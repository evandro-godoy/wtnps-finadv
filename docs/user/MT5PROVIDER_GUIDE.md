# MetaTraderProvider - Guia de Uso

## Overview

`MetaTraderProvider` é a classe responsável por conectar ao MetaTrader 5 e buscar dados OHLCV de forma segura usando a estratégia **Fail Fast**.

### Requisitos Implementados

✅ **Requisito 1 (Conexão):** No `__init__`, tenta conectar ao MT5 via `mt5.initialize()`

✅ **Requisito 2 (Fail Fast):** Se a conexão falhar, loga criticamente e executa `sys.exit(1)`, impedindo que o sistema continue "cego"

✅ **Requisito 3 (Interface):** Método `get_latest_candles(symbol, timeframe, n=100)` retorna um **DataFrame Pandas** com colunas padronizadas (Open, High, Low, Close, Volume)

## Instalação

O arquivo já está localizado em:
```
src/data_handler/mt5_provider.py
```

## Uso Básico

### 1. Inicialização (Fail Fast)

```python
from src.data_handler.mt5_provider import MetaTraderProvider

# Se MT5 não estiver disponível, o programa encerra com mensagem crítica
# Não há retry ou fallback - garante que o sistema não funcione sem MT5
try:
    provider = MetaTraderProvider()
    print("✅ MT5 conectado com sucesso")
except SystemExit:
    # Já foi logado criticamente, apenas para tratamento se necessário
    print("MT5 não disponível - encerrando")
```

### 2. Buscar Candles como DataFrame

```python
import pandas as pd

# Busca os últimos 100 candles de WDO$ em M5
df = provider.get_latest_candles(
    symbol='WDO$',
    timeframe='M5',
    n=100
)

print(df.head())
# Output:
#                     Open    High     Low   Close  Volume
# time                                                      
# 2025-01-31 10:00:00 100.0  102.0   99.0  101.5    1000
# 2025-01-31 10:05:00 101.5  103.0  101.0  102.0    1200
```

**Características do DataFrame:**
- **Index:** timestamp (datetime, UTC)
- **Colunas:** Open, High, Low, Close, Volume (capitalizadas)
- **Tipos:** Open/High/Low/Close como float64, Volume como int64
- **Pronto para:** LSTMAdapter, features engineering, backtesting

### 3. Timeframes Suportados

```python
# M5 = 5 minutos
df = provider.get_latest_candles('WDO$', 'M5', n=100)

# Outros timeframes válidos:
# M1, M15, M30, H1, H4, D1, W1, MN1
```

### 4. Integração com EventBus (Opcional)

Se você precisa publicar candles como eventos:

```python
# Opção A: Buscar como MarketDataEvent
events = provider.get_latest_candles_as_events('WDO$', 'M5', n=50)
for event in events:
    print(f"Event: {event.symbol} Close={event.close} @ {event.timestamp}")

# Opção B: Publicar diretamente no EventBus
provider.publish_to_eventbus('WDO$', 'M5', n=50)
```

## Tratamento de Erros

### Erro 1: MT5 não inicializado (Fail Fast)

```
CRÍTICO: Falha ao inicializar MT5. Error: ... 
Sistema encerrando - MT5 é uma dependência crítica
```

**Solução:** Certifique-se de que:
1. MetaTrader 5 está instalado no computador
2. Terminal MT5 está aberto e logado
3. Permissões de acesso à DLL do MT5 estão corretas

### Erro 2: Timeframe inválido

```python
try:
    df = provider.get_latest_candles('WDO$', 'INVALID', n=100)
except ValueError as e:
    print(e)
    # Output: Timeframe inválido: 'INVALID'. Válidos: ['M1', 'M5', ...]
```

### Erro 3: Símbolo não encontrado

```python
try:
    df = provider.get_latest_candles('FAKE$', 'M5', n=100)
except ValueError as e:
    print(e)
    # Output: Nenhum dado retornado para FAKE$ M5. Error: ...
```

**Solução:** Verifique se o símbolo existe no seu terminal MT5

### Erro 4: MT5 desconectado

```python
try:
    df = provider.get_latest_candles('WDO$', 'M5', n=100)
except ConnectionError as e:
    print(e)
    # Output: MT5 não está conectado
```

**Solução:** Reconecte ao terminal MT5 e reinicie o programa

## Encerramento Gracioso

```python
# Sempre encerre a conexão quando não usar mais
provider.shutdown()
# Output: ✅ MT5 desconectado com sucesso
```

## Exemplo Completo

```python
from src.data_handler.mt5_provider import MetaTraderProvider
import pandas as pd

def main():
    # 1. Inicializa (Fail Fast)
    provider = MetaTraderProvider()
    
    # 2. Busca dados
    try:
        df = provider.get_latest_candles('WDO$', 'M5', n=100)
        print(f"Candles obtidos: {len(df)}")
        print(f"Últimas 5 linhas:\n{df.tail()}")
        
        # 3. Processa como quiser
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        print(f"\nMédia móvel calculada")
        
    except (ValueError, ConnectionError) as e:
        print(f"Erro ao buscar dados: {e}")
    finally:
        # 4. Encerra
        provider.shutdown()

if __name__ == '__main__':
    main()
```

## Logging

Os logs são enviados automaticamente para o logger do módulo. Configure conforme necessário:

```python
import logging

# Ver logs de DEBUG (mais detalhado)
logging.getLogger('src.data_handler.mt5_provider').setLevel(logging.DEBUG)

# Exemplo de output:
# INFO: ✅ MT5 inicializado com sucesso
# INFO:    Versão: (5, 0, 45)
# INFO:    Terminal: MetaTrader 5
# INFO: ✅ Buscados 100 candles de WDO$ M5
```

## Arquitetura

```
MetaTraderProvider
├── __init__()
│   └─ mt5.initialize() [Fail Fast: exit(1) se falhar]
│
├── get_latest_candles(symbol, timeframe, n=100) → DataFrame
│   └─ Retorna: [Open, High, Low, Close, Volume] (capitalizados)
│
├── get_latest_candles_as_events(symbol, timeframe, n=100) → List[MarketDataEvent]
│   └─ Para integração com EventBus
│
├── publish_to_eventbus(symbol, timeframe, n=100)
│   └─ Publica eventos direto no barramento
│
└── shutdown()
    └─ mt5.shutdown() gracioso
```

## Testes

Execute os testes unitários:

```bash
poetry run pytest tests/unit/test_mt5_provider.py -v
```

Testes cobrindo:
- ✅ Fail Fast on init
- ✅ Successful initialization
- ✅ DataFrame format (colunas, tipos)
- ✅ Invalid timeframe handling
- ✅ Empty data handling
- ✅ EventBus integration
- ✅ Graceful shutdown
