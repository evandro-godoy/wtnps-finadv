"""
Exemplo Prático: MetaTraderProvider - Fail Fast Connection Strategy

Este script demonstra como usar a classe MetaTraderProvider para:
1. Conectar ao MT5 com estratégia Fail Fast
2. Buscar candles em formato DataFrame
3. Integrar com EventBus
4. Tratar erros apropriadamente
"""

import logging
from datetime import datetime
from src.data_handler.mt5_provider import MetaTraderProvider

# Configurar logging para ver as mensagens de status
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(name)s] %(message)s'
)

logger = logging.getLogger(__name__)


def exemplo_basico():
    """Exemplo 1: Uso básico - buscar candles como DataFrame."""
    
    print("\n" + "="*60)
    print("EXEMPLO 1: Buscar Candles como DataFrame")
    print("="*60)
    
    try:
        # 1. Inicializar provider (Fail Fast aqui)
        provider = MetaTraderProvider()
        
        # 2. Buscar candles como DataFrame
        df = provider.get_latest_candles(
            symbol='WDO$',
            timeframe='M5',
            n=10  # Apenas 10 candles para exemplo
        )
        
        # 3. Explorar o DataFrame
        print(f"\n✅ Obtidos {len(df)} candles")
        print(f"\nColunas: {df.columns.tolist()}")
        print(f"Tipos:\n{df.dtypes}\n")
        
        print("Primeiras 5 linhas:")
        print(df.head())
        
        print("\nÚltimas 2 linhas:")
        print(df.tail(2))
        
        # 4. Acessar dados específicos
        last_close = df.iloc[-1]['Close']
        last_volume = df.iloc[-1]['Volume']
        print(f"\nÚltimo Close: {last_close}")
        print(f"Último Volume: {last_volume}")
        
    except (ValueError, ConnectionError) as e:
        logger.error(f"Erro: {e}")
    finally:
        provider.shutdown()


def exemplo_tratamento_erro():
    """Exemplo 2: Tratamento de erros comuns."""
    
    print("\n" + "="*60)
    print("EXEMPLO 2: Tratamento de Erros")
    print("="*60)
    
    try:
        provider = MetaTraderProvider()
        
        # Testando timeframe inválido
        print("\n1. Tentando timeframe inválido...")
        try:
            df = provider.get_latest_candles('WDO$', 'INVALID_TF', n=100)
        except ValueError as e:
            print(f"   ❌ Erro capturado: {e}")
        
        # Testando símbolo inválido
        print("\n2. Tentando símbolo inválido...")
        try:
            df = provider.get_latest_candles('FAKE$', 'M5', n=100)
        except ValueError as e:
            print(f"   ❌ Erro capturado: {e}")
        
        # Timeframe válido com símbolo válido
        print("\n3. Tentando com parâmetros válidos...")
        df = provider.get_latest_candles('WDO$', 'M5', n=5)
        print(f"   ✅ Sucesso: {len(df)} candles obtidos")
        
    except ConnectionError as e:
        logger.error(f"Erro de conexão: {e}")
    finally:
        provider.shutdown()


def exemplo_processamento_dados():
    """Exemplo 3: Processar e analisar dados."""
    
    print("\n" + "="*60)
    print("EXEMPLO 3: Processamento de Dados")
    print("="*60)
    
    try:
        provider = MetaTraderProvider()
        
        # Buscar 50 candles
        df = provider.get_latest_candles('WDO$', 'M15', n=50)
        
        # Calcular alguns indicadores simples
        print("\n📊 Análise dos candles:")
        print(f"Total de candles: {len(df)}")
        
        # Estatísticas
        print(f"\nPreço de Fechamento (Close):")
        print(f"  Mínimo: {df['Close'].min():.2f}")
        print(f"  Máximo: {df['Close'].max():.2f}")
        print(f"  Médio:  {df['Close'].mean():.2f}")
        print(f"  Desvio: {df['Close'].std():.2f}")
        
        print(f"\nVolume:")
        print(f"  Total:  {df['Volume'].sum()}")
        print(f"  Médio:  {df['Volume'].mean():.0f}")
        
        # Detecção de candles grandes
        df['Range'] = df['High'] - df['Low']
        df['BodySize'] = abs(df['Close'] - df['Open'])
        
        big_candles = df[df['Range'] > df['Range'].quantile(0.75)]
        print(f"\nCandles grandes (top 25%): {len(big_candles)}")
        
        # Calcular média móvel
        df['SMA_10'] = df['Close'].rolling(window=10).mean()
        
        print(f"\nMédia móvel (SMA_10) dos últimos 3 candles:")
        print(df[['Close', 'SMA_10']].tail(3))
        
    except (ValueError, ConnectionError) as e:
        logger.error(f"Erro: {e}")
    finally:
        provider.shutdown()


def exemplo_eventbus_integration():
    """Exemplo 4: Integração com EventBus."""
    
    print("\n" + "="*60)
    print("EXEMPLO 4: Integração com EventBus")
    print("="*60)
    
    try:
        provider = MetaTraderProvider()
        
        # Opção 1: Obter eventos
        print("\n1. Obtendo eventos:")
        events = provider.get_latest_candles_as_events('WDO$', 'M5', n=3)
        
        print(f"   Total de eventos: {len(events)}")
        for i, event in enumerate(events, 1):
            print(f"   Evento {i}: {event.symbol} {event.timeframe} Close={event.close:.2f}")
        
        # Opção 2: Publicar direto no EventBus
        print("\n2. Publicando no EventBus:")
        provider.publish_to_eventbus('WDO$', 'M5', n=5)
        print("   ✅ 5 eventos publicados no barramento")
        
    except (ValueError, ConnectionError) as e:
        logger.error(f"Erro: {e}")
    finally:
        provider.shutdown()


def exemplo_fail_fast():
    """Exemplo 5: Demonstrar Fail Fast (conceptual)."""
    
    print("\n" + "="*60)
    print("EXEMPLO 5: Estratégia Fail Fast (Conceitual)")
    print("="*60)
    
    print("""
    ⚡ Estratégia Fail Fast em ação:
    
    Se MT5 não estiver conectado/instalado:
    
    1. MetaTraderProvider() é chamado
    2. mt5.initialize() retorna False
    3. Logger imprime CRÍTICO com detalhes
    4. sys.exit(1) encerra o programa imediatamente
    
    ✅ Benefício: Sistema não funciona "cego" sem dados reais
    
    ❌ Sem Fail Fast (ruim):
       - Programa continua rodando
       - Estratégias ficam em HOLD indefinidamente
       - Operador não percebe o problema
    
    ✅ Com Fail Fast (bom):
       - Log crítico avisa imediatamente
       - Programa encerra
       - Operador identifica e resolve problema
       - Depois reinicia o sistema
    """)


def main():
    """Executar todos os exemplos."""
    
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║     MetaTraderProvider - Exemplos de Uso                  ║
    ║     Fail Fast Connection Strategy                         ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    # AVISO
    print("\n⚠️  AVISO: Estes exemplos requerem MT5 conectado e símbolos disponíveis")
    print("   Alguns exemplos podem falhar se MT5 não estiver ativo\n")
    
    # Executar exemplos (comentar/descomentar conforme necessário)
    
    # exemplo_basico()
    # exemplo_tratamento_erro()
    # exemplo_processamento_dados()
    # exemplo_eventbus_integration()
    exemplo_fail_fast()  # Este pode ser executado sempre
    
    print("\n" + "="*60)
    print("Exemplos concluídos!")
    print("="*60)


if __name__ == '__main__':
    main()
