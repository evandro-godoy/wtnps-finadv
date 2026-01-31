#!/usr/bin/env python3
"""
Exemplo de uso do MT5 Provider com configurações via .env
Demonstra os principais uso cases.
"""

import sys
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(name)s] %(message)s'
)
logger = logging.getLogger(__name__)

def example_1_basic_initialization():
    """Exemplo 1: Inicialização básica do provider."""
    print("\n" + "=" * 70)
    print("EXEMPLO 1: Inicialização Básica")
    print("=" * 70)
    
    try:
        from src.data_handler.mt5_provider import MetaTraderProvider
        
        # Inicializa provider (usa configurações de .env automaticamente)
        provider = MetaTraderProvider()
        print("✅ Provider inicializado com sucesso!")
        
        # Cleanup
        provider.shutdown()
        
    except ConnectionError as e:
        print(f"❌ Erro de conexão: {e}")
        print("   Verifique se o terminal MetaTrader 5 está rodando")


def example_2_fetch_candles():
    """Exemplo 2: Buscar candles do MT5."""
    print("\n" + "=" * 70)
    print("EXEMPLO 2: Buscar Candles")
    print("=" * 70)
    
    try:
        from src.data_handler.mt5_provider import MetaTraderProvider
        
        provider = MetaTraderProvider()
        
        # Buscar últimos 10 candles de WDO$ no timeframe M5
        df = provider.get_latest_candles('WDO$', 'M5', n=10)
        
        print(f"✅ Buscados {len(df)} candles:")
        print("\nPrimeiras 5 linhas:")
        print(df.head())
        
        print(f"\nÚltimas 5 linhas:")
        print(df.tail())
        
        # Estatísticas básicas
        print(f"\nEstatísticas de Preço:")
        print(f"  Mínima:  {df['Low'].min():.2f}")
        print(f"  Máxima:  {df['High'].max():.2f}")
        print(f"  Fechamento Último: {df['Close'].iloc[-1]:.2f}")
        
        provider.shutdown()
        
    except ConnectionError as e:
        print(f"❌ Erro de conexão: {e}")
    except ValueError as e:
        print(f"❌ Erro de validação: {e}")


def example_3_multiple_assets():
    """Exemplo 3: Buscar dados de múltiplos ativos."""
    print("\n" + "=" * 70)
    print("EXEMPLO 3: Múltiplos Ativos")
    print("=" * 70)
    
    try:
        from src.data_handler.mt5_provider import MetaTraderProvider
        
        provider = MetaTraderProvider()
        
        assets = ['WDO$', 'WIN$']
        timeframe = 'M5'
        
        for asset in assets:
            try:
                df = provider.get_latest_candles(asset, timeframe, n=5)
                print(f"\n✅ {asset} ({timeframe}):")
                print(f"   Último Preço: {df['Close'].iloc[-1]:.2f}")
                print(f"   Variação: {((df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0] * 100):.2f}%")
            except Exception as e:
                print(f"⚠️  {asset}: {e}")
        
        provider.shutdown()
        
    except ConnectionError as e:
        print(f"❌ Erro de conexão: {e}")


def example_4_check_config():
    """Exemplo 4: Inspecionar configuração carregada."""
    print("\n" + "=" * 70)
    print("EXEMPLO 4: Inspeção de Configuração")
    print("=" * 70)
    
    from src.core.config import settings
    
    print("\n📋 Configurações do Sistema:")
    print(f"  Project: {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"  Base Dir: {settings.BASE_DIR}")
    print(f"  Models Dir: {settings.MODELS_DIR}")
    print(f"  Logs Dir: {settings.LOGS_DIR}")
    
    print("\n📋 Configurações do MT5:")
    mt5_config = settings.get_mt5_config()
    print(f"  Path: {mt5_config['path']}")
    print(f"  Timeout: {mt5_config['timeout']}ms")
    print(f"  Requer Auth: {settings.mt5_needs_auth()}")
    
    if settings.mt5_needs_auth():
        print(f"  Login: {mt5_config['login']}")
        print(f"  Server: {mt5_config['server']}")
    else:
        print(f"  ✅ Modo Terminal Aberto (sem credenciais)")


def example_5_event_bus():
    """Exemplo 5: Publicar dados no EventBus."""
    print("\n" + "=" * 70)
    print("EXEMPLO 5: Integração com EventBus")
    print("=" * 70)
    
    try:
        from src.data_handler.mt5_provider import MetaTraderProvider
        from src.core.event_bus import event_bus
        
        # Criar subscriber de teste
        events_received = []
        
        def test_subscriber(event):
            events_received.append(event)
            print(f"  📊 Evento recebido: {event.symbol} @ {event.timestamp}")
        
        # Subscribe
        from src.events import MarketDataEvent
        event_bus.subscribe(MarketDataEvent, test_subscriber)
        
        # Buscar e publicar
        provider = MetaTraderProvider()
        provider.publish_to_eventbus('WDO$', 'M5', n=3)
        
        print(f"\n✅ Publicados {len(events_received)} eventos no EventBus")
        
        provider.shutdown()
        
    except ConnectionError as e:
        print(f"❌ Erro de conexão: {e}")
    except Exception as e:
        print(f"❌ Erro: {e}")


def main():
    """Menu principal."""
    print("\n" + "=" * 70)
    print("🎯 EXEMPLOS DE USO - MT5 PROVIDER COM CONFIGURAÇÃO .env")
    print("=" * 70)
    
    examples = {
        "1": ("Verificar Configuração", example_4_check_config),
        "2": ("Inicialização Básica", example_1_basic_initialization),
        "3": ("Buscar Candles", example_2_fetch_candles),
        "4": ("Múltiplos Ativos", example_3_multiple_assets),
        "5": ("Integração com EventBus", example_5_event_bus),
        "t": ("Executar Todos (requer MT5 rodando)", lambda: [
            example_4_check_config(),
            example_1_basic_initialization(),
        ]),
    }
    
    print("\nSelecione um exemplo:")
    for key, (desc, _) in examples.items():
        print(f"  [{key}] {desc}")
    print("  [q] Sair")
    
    choice = input("\nOpção: ").strip().lower()
    
    if choice == 'q':
        print("👋 Até logo!")
        return
    
    if choice in examples:
        _, func = examples[choice]
        try:
            func()
        except KeyboardInterrupt:
            print("\n⚠️  Interrompido pelo usuário")
        except Exception as e:
            logger.exception(f"Erro: {e}")
    else:
        print("❌ Opção inválida")


if __name__ == "__main__":
    # Se executado com argumento, rodar exemplo específico
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "config":
            example_4_check_config()
        elif arg == "init":
            example_1_basic_initialization()
        elif arg == "candles":
            example_2_fetch_candles()
        elif arg == "multi":
            example_3_multiple_assets()
        elif arg == "events":
            example_5_event_bus()
        else:
            print(f"Uso: python {sys.argv[0]} [config|init|candles|multi|events]")
    else:
        # Modo interativo
        main()
