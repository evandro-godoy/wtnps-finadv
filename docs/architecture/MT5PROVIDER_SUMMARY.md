# MetaTraderProvider - Resumo da Implementação

## 📋 Checklist de Requisitos

| # | Requisito | Status | Detalhes |
|---|-----------|--------|----------|
| 1 | **Conexão**: No `__init__`, tenta `mt5.initialize()` | ✅ | Linhas 31-37 de `mt5_provider.py` |
| 2 | **Fail Fast**: Se inicialização falha, `sys.exit(1)` | ✅ | Dispara `sys.exit(1)` após log crítico |
| 3 | **Interface**: `get_latest_candles()` retorna DataFrame | ✅ | Colunas: Open, High, Low, Close, Volume |

---

## 🏗️ Arquitetura da Classe

```
┌─────────────────────────────────────────────────────────────┐
│              MetaTraderProvider                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  __init__()                                                  │
│  ├─ mt5.initialize()                                        │
│  ├─ ✅ OK  → Log info + continua                           │
│  └─ ❌ FAIL → Log crítico + sys.exit(1) [FAIL FAST]        │
│                                                              │
│  get_latest_candles(symbol, timeframe, n=100)              │
│  ├─ Valida conexão MT5                                     │
│  ├─ Mapeia timeframe string → constante MT5                │
│  ├─ Busca rates via mt5.copy_rates_from_pos()             │
│  ├─ Converte para DataFrame Pandas                         │
│  ├─ Renomeia colunas: (open→Open, close→Close, etc)      │
│  └─ Retorna: pd.DataFrame[Open, High, Low, Close, Volume] │
│                                                              │
│  get_latest_candles_as_events(symbol, timeframe, n=100)   │
│  ├─ Chama get_latest_candles()                            │
│  ├─ Converte cada linha em MarketDataEvent                │
│  └─ Retorna: List[MarketDataEvent]                        │
│                                                              │
│  publish_to_eventbus(symbol, timeframe, n=100)            │
│  ├─ Chama get_latest_candles_as_events()                 │
│  ├─ Para cada evento, event_bus.publish(event)           │
│  └─ Log: Publicados N eventos                             │
│                                                              │
│  shutdown()                                                  │
│  ├─ Chama mt5.shutdown()                                  │
│  ├─ Log sucesso ou erro                                  │
│  └─ Graceful disconnect                                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Fluxo de Dados

### Caso 1: Conexão bem-sucedida

```
programa.py
    ↓
MetaTraderProvider()  ← __init__
    ↓
mt5.initialize() → True
    ↓
✅ Log: MT5 inicializado com sucesso
    ↓
(Sistema continua normalmente)
    ↓
get_latest_candles('WDO$', 'M5', 100)
    ↓
DataFrame[Open, High, Low, Close, Volume]
```

### Caso 2: Falha na conexão (FAIL FAST)

```
programa.py
    ↓
MetaTraderProvider()  ← __init__
    ↓
mt5.initialize() → False
    ↓
❌ logger.critical("Falha ao inicializar MT5")
❌ logger.critical("Sistema encerrando...")
    ↓
sys.exit(1)  ← ENCERRA O PROGRAMA
    ↓
[Programa termina imediatamente]
```

---

## 📈 Exemplo de Output

### Inicialização bem-sucedida:
```
INFO: ✅ MT5 inicializado com sucesso
INFO:    Versão: (5, 0, 45)
INFO:    Terminal: MetaTrader 5
```

### Buscando candles:
```
INFO: ✅ Buscados 100 candles de WDO$ M5
```

### DataFrame resultado:
```
                     Open    High     Low   Close  Volume
time                                                      
2025-01-31 09:00:00 100.50 101.20  100.00 100.80   5000
2025-01-31 09:05:00 100.80 101.50  100.50 101.20   4800
2025-01-31 09:10:00 101.20 102.00  101.00 101.80   5200
...
```

---

## 🔍 Validações Implementadas

| Validação | Erro | Mensagem |
|-----------|------|----------|
| Timeframe inválido | `ValueError` | "Timeframe inválido: '...'. Válidos: [...]" |
| MT5 desconectado | `ConnectionError` | "MT5 não está conectado" |
| Sem dados retornados | `ValueError` | "Nenhum dado retornado para ... Error: ..." |
| Colunas faltando | `ValueError` | "Dados do MT5 faltando colunas: ..." |
| Erro na busca | `ConnectionError` | "Erro ao buscar candles de ...: ..." |

---

## 🎯 Tipos de Retorno

### `get_latest_candles()` → `pd.DataFrame`
```python
Index: DatetimeIndex (timestamp em UTC)
Colunas:
  - Open: float64
  - High: float64
  - Low: float64
  - Close: float64
  - Volume: int64
```

### `get_latest_candles_as_events()` → `list[MarketDataEvent]`
```python
[
  MarketDataEvent(
    symbol='WDO$',
    timeframe='M5',
    open=100.5,
    high=101.2,
    low=100.0,
    close=100.8,
    volume=5000,
    timestamp=datetime(...)
  ),
  ...
]
```

---

## 🚀 Timeframes Suportados

```
Intraday:           Day & Higher:
├─ M1  (1 min)      ├─ D1  (1 dia)
├─ M5  (5 min)      ├─ W1  (1 semana)
├─ M15 (15 min)     └─ MN1 (1 mês)
├─ M30 (30 min)
└─ H1, H4 (horas)
```

---

## 📦 Dependências

### Imports Internos
```python
from src.core.event_bus import event_bus
from src.events import MarketDataEvent
```

### Imports Externos (requeridos)
```python
import logging
import sys
import MetaTrader5 as mt5          # Terminal MT5 necessário
import pandas as pd
```

---

## 🔧 Modo de Uso

### 1. Inicializar
```python
from src.data_handler.mt5_provider import MetaTraderProvider

provider = MetaTraderProvider()  # Fail Fast aqui se MT5 não conectar
```

### 2. Buscar dados
```python
# Como DataFrame
df = provider.get_latest_candles('WDO$', 'M5', n=100)

# Como eventos
events = provider.get_latest_candles_as_events('WDO$', 'M5', n=100)

# Publicar direto
provider.publish_to_eventbus('WDO$', 'M5', n=100)
```

### 3. Encerrar
```python
provider.shutdown()  # Graceful disconnect
```

---

## 📝 Logging Estruturado

| Nível | Quando | Exemplo |
|-------|--------|---------|
| `CRITICAL` | Fail Fast na init | "CRÍTICO: Falha ao inicializar MT5" |
| `ERROR` | Timeframe inválido | "Timeframe inválido: 'ABC'" |
| `ERROR` | Sem dados | "Nenhum dado retornado para WDO$" |
| `INFO` | Sucesso na init | "✅ MT5 inicializado com sucesso" |
| `INFO` | Candles buscados | "✅ Buscados 100 candles de WDO$ M5" |
| `DEBUG` | EventBus pub | "Publicados 100 eventos no EventBus" |

---

## ✅ Testes Cobrindo

```
tests/unit/test_mt5_provider.py
├─ test_fail_fast_on_init_failure
├─ test_successful_initialization
├─ test_get_latest_candles_returns_dataframe
├─ test_invalid_timeframe_raises_error
├─ test_no_data_returned_raises_error
├─ test_get_latest_candles_as_events
└─ test_shutdown
```

---

## 🎓 Documentação

| Arquivo | Conteúdo |
|---------|----------|
| `MT5PROVIDER_GUIDE.md` | Guia completo de uso |
| `MT5PROVIDER_IMPLEMENTATION.md` | Detalhes técnicos |
| `example_mt5provider.py` | 5 exemplos práticos |

---

## 🔐 Estratégia Fail Fast - Por Quê?

**Problema:** Sem MT5, o sistema fica em HOLD indefinidamente
```
Sistema inicia
  ↓
Tenta buscar dados
  ↓
Erro (retorna None/vazio)
  ↓
Sistema continua operando "cego"
  ↓
❌ RUIM: Operador não percebe o problema
```

**Solução Fail Fast:**
```
Sistema inicia
  ↓
MetaTraderProvider() falha
  ↓
Log crítico
  ↓
sys.exit(1)
  ↓
✅ BOM: Operador vê problema imediatamente
✅ BOM: Força solução antes de reiniciar
```

---

## 📌 Notas Importantes

1. **MT5 é obrigatório**: Terminal precisa estar aberto e logado
2. **Fail Fast**: Não há retry automático - é proposital
3. **Timezone**: Timestamps retornados em UTC
4. **Colunas capitalizadas**: Open, High, Low, Close, Volume (não open, close...)
5. **Index é DatetimeIndex**: Facilita operações de série temporal
6. **Volume é int64**: Compatível com cálculos de ML

---

## 🎯 Status Final

```
✅ Requisito 1 (Conexão)  - Implementado
✅ Requisito 2 (Fail Fast) - Implementado
✅ Requisito 3 (Interface) - Implementado
✅ Testes Unitários       - Criados
✅ Documentação           - Completa
✅ Exemplos de Uso        - Fornecidos
```

**Pronto para integração e uso em produção! 🚀**
