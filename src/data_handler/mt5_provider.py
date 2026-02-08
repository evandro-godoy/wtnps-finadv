"""MetaTrader 5 Data Provider with Config-based Initialization."""

import logging
import sys
from datetime import datetime
from typing import Optional
import MetaTrader5 as mt5
import pandas as pd

from src.core.config import settings
from src.core.event_bus import event_bus
from src.events import MarketDataEvent

logger = logging.getLogger(__name__)


class MetaTraderProvider:
    """
    Provider para dados do MetaTrader 5 com suporte a configuração via .env.
    
    Estratégia Fail Fast: Se MT5 não conectar, lança ConnectionError.
    Sem retry loops nesta versão (Sprint 2 MVP).
    
    Configuração:
        - Lê MT5_PATH do .env (padrão: C:\\Program Files\\MetaTrader 5\\terminal64.exe)
        - Credenciais opcionais: MT5_LOGIN, MT5_PASSWORD, MT5_SERVER
        - Timeout: MT5_TIMEOUT (padrão: 5000ms)
    
    Raises:
        ConnectionError: Se mt5.initialize() falhar
        ValueError: Se symbol não for encontrado
    """
    
    # Classe estática para gerenciar estado global do MT5
    _initialized = False
    _lock = None
    
    def __init__(self):
        """
        Inicializa conexão com MT5 usando configurações do settings.
        
        Se credenciais forem fornecidas, realiza login.
        Caso contrário, usa apenas o terminal aberto.
        
        Fail Fast: Se a conexão falhar, loga e encerra o processo.
        """
        # Verificar se já foi inicializado (singleton)
        if MetaTraderProvider._initialized and mt5.terminal_info():
            logger.debug("MT5 já estava inicializado - reutilizando conexão")
            return
        
        # Obter config
        mt5_config = settings.get_mt5_config()
        needs_auth = settings.mt5_needs_auth()
        
        logger.info("=" * 60)
        logger.info("Inicializando MetaTrader 5...")
        logger.info(f"  Caminho: {mt5_config['path']}")
        logger.info(f"  Requer autenticação: {needs_auth}")
        logger.info(f"  Timeout: {mt5_config['timeout']}ms")
        logger.info("=" * 60)
        
        # Tentar inicializar
        try:
            init_kwargs = {
                "path": mt5_config['path'],
                "timeout": mt5_config['timeout'],
            }
            
            # Se temos credenciais, adicionar ao init
            if needs_auth:
                init_kwargs.update({
                    "login": int(mt5_config['login']),
                    "password": mt5_config['password'],
                    "server": mt5_config['server'],
                })
            
            if not mt5.initialize(**init_kwargs):
                error_msg = (
                    f"❌ CRÍTICO: Falha ao inicializar MT5\n"
                    f"   Erro: {mt5.last_error()}\n"
                    f"   Verifique:\n"
                    f"     - Caminho MT5: {mt5_config['path']}\n"
                    f"     - Terminal está rodando\n"
                    f"     - Credenciais (se aplicável)\n"
                )
                logger.critical(error_msg)
                logger.critical("❌ MT5 é uma dependência crítica — levantando ConnectionError")
                raise ConnectionError(error_msg)
            
            MetaTraderProvider._initialized = True
            
            # Log de sucesso
            version = mt5.version()
            terminal_info = mt5.terminal_info()
            logger.info("✅ MT5 inicializado com sucesso!")
            logger.info(f"   Versão: {version}")
            logger.info(f"   Terminal: {terminal_info.name if terminal_info else 'Unknown'}")
            
            if needs_auth:
                acc = mt5.account_info()
                if acc:
                    logger.info(f"   Conta: {acc.name} ({acc.login})")
            
        except Exception as e:
            error_msg = f"❌ Erro ao inicializar MT5: {type(e).__name__}: {e}"
            logger.critical(error_msg)
            raise ConnectionError(error_msg) from e

    def is_connected(self) -> bool:
        """Compat method for legacy provider interface."""
        return self._validate_connection()
    
    @staticmethod
    def _validate_connection() -> bool:
        """
        Valida se MT5 ainda está conectado.
        
        Returns:
            True se conectado, False caso contrário
        """
        try:
            return mt5.terminal_info() is not None
        except:
            return False
    
    def get_latest_candles(
        self, 
        symbol: str, 
        timeframe: str, 
        n: int = 100
    ) -> pd.DataFrame:
        """
        Busca últimos N candles do MT5 e retorna como DataFrame Pandas.
        
        O DataFrame possui as colunas esperadas pelo LSTMAdapter:
        - Open (float)
        - High (float)
        - Low (float)
        - Close (float)
        - Volume (int)
        
        Args:
            symbol: Símbolo do ativo (ex: "WIN$", "WDO$")
            timeframe: Timeframe (ex: "M5", "M15", "H1", "D1", etc.)
            n: Número de candles a retornar (padrão: 100)
        
        Returns:
            pd.DataFrame com colunas [Open, High, Low, Close, Volume]
            Index: timestamp (datetime)
        
        Raises:
            ConnectionError: Se MT5 não estiver conectado
            ValueError: Se timeframe for inválido ou nenhum dado retornado
        """
        # Validar conexão
        if not self._validate_connection():
            error_msg = "❌ MT5 não está conectado"
            logger.critical(error_msg)
            raise ConnectionError(error_msg)
        
        # Mapear timeframe string para constante MT5
        timeframe_map = {
            "M1": mt5.TIMEFRAME_M1,
            "M5": mt5.TIMEFRAME_M5,
            "M15": mt5.TIMEFRAME_M15,
            "M30": mt5.TIMEFRAME_M30,
            "H1": mt5.TIMEFRAME_H1,
            "H4": mt5.TIMEFRAME_H4,
            "D1": mt5.TIMEFRAME_D1,
            "W1": mt5.TIMEFRAME_W1,
            "MN1": mt5.TIMEFRAME_MN1,
        }
        
        mt5_timeframe = timeframe_map.get(timeframe)
        if mt5_timeframe is None:
            error_msg = f"❌ Timeframe inválido: '{timeframe}'. Válidos: {list(timeframe_map.keys())}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Buscar candles (posição 0 é o mais recente)
        try:
            rates = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, n)
        except Exception as e:
            error_msg = f"❌ Erro ao buscar candles de {symbol}: {e}"
            logger.error(error_msg)
            raise ConnectionError(error_msg)
        
        if rates is None or len(rates) == 0:
            error_msg = f"❌ Nenhum dado retornado para {symbol} {timeframe}. Error: {mt5.last_error()}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Converter para DataFrame
        df = pd.DataFrame(rates)
        
        # Validar colunas esperadas do MT5
        required_cols = ['time', 'open', 'high', 'low', 'close', 'tick_volume']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            error_msg = f"❌ Dados do MT5 faltando colunas: {missing_cols}. Colunas: {df.columns.tolist()}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Converter timestamp e definir como index
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        
        # Padronizar nomes: MT5 usa lowercase, esperamos capitalizados
        df_output = pd.DataFrame({
            'Open': df['open'].astype(float),
            'High': df['high'].astype(float),
            'Low': df['low'].astype(float),
            'Close': df['close'].astype(float),
            'Volume': df['tick_volume'].astype(int),
        })
        
        logger.debug(f"✅ Buscados {len(df_output)} candles: {symbol} {timeframe}")
        return df_output
    
    def get_latest_candles_as_events(
        self,
        symbol: str,
        timeframe: str,
        n: int = 100
    ) -> list[MarketDataEvent]:
        """
        Busca candles e retorna como lista de MarketDataEvent (uso com EventBus).
        
        Args:
            symbol: Símbolo do ativo
            timeframe: Timeframe válido
            n: Número de candles
        
        Returns:
            Lista de MarketDataEvent
        """
        df = self.get_latest_candles(symbol, timeframe, n)
        
        events = []
        for timestamp, row in df.iterrows():
            event = MarketDataEvent(
                symbol=symbol,
                timeframe=timeframe,
                open=float(row['Open']),
                high=float(row['High']),
                low=float(row['Low']),
                close=float(row['Close']),
                volume=int(row['Volume']),
                timestamp=timestamp
            )
            events.append(event)
        
        return events
    
    def publish_to_eventbus(self, symbol: str, timeframe: str, n: int = 100):
        """
        Busca candles e publica no EventBus como MarketDataEvents.
        
        Args:
            symbol: Símbolo do ativo
            timeframe: Timeframe
            n: Número de candles
        """
        events = self.get_latest_candles_as_events(symbol, timeframe, n)
        for event in events:
            event_bus.publish(event)
        logger.debug(f"✅ Publicados {len(events)} eventos no EventBus")
    
    def shutdown(self):
        """Encerra conexão com MT5."""
        try:
            mt5.shutdown()
            MetaTraderProvider._initialized = False
            logger.info("✅ MT5 desconectado com sucesso")
        except Exception as e:
            logger.error(f"⚠️  Erro ao desconectar MT5: {e}")

    def close_connection(self):
        """Alias para shutdown (compatibilidade com legado)."""
        self.shutdown()
    
    def __del__(self):
        """Destrutor - garante shutdown ao destruir objeto."""
        try:
            if MetaTraderProvider._initialized and mt5.terminal_info() is not None:
                mt5.shutdown()
                MetaTraderProvider._initialized = False
        except:
            pass





