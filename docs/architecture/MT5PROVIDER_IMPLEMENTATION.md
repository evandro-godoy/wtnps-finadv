# Implementação: MetaTraderProvider - Fail Fast Connection Strategy

## Data: 31/01/2026
## Status: ✅ CONCLUÍDO

---

## Resumo Executivo

Implementação da classe `MetaTraderProvider` em `src/data_handler/mt5_provider.py` com estratégia **Fail Fast** e interface padronizada para retornar dados em formato DataFrame Pandas.

## Requisitos Atendidos

### ✅ Requisito 1: Conexão ao MT5
**O quê:** No `__init__`, tentar conectar ao MT5 via `mt5.initialize()`

**Implementação:**
```python
def __init__(self):
    if not mt5.initialize():
        error_msg = f"CRÍTICO: Falha ao inicializar MT5. Error: {mt5.last_error()}"
        logger.critical(error_msg)
        logger.critical("Sistema encerrando - MT5 é uma dependência crítica")
        sys.exit(1)
    
    logger.info(f"✅ MT5 inicializado com sucesso")
    logger.info(f"   Versão: {mt5.version()}")
    logger.info(f"   Terminal: {mt5.terminal_info()}")
```

**Evidência:**
- Linhas 31-40 de `src/data_handler/mt5_provider.py`

---

### ✅ Requisito 2: Fail Fast
**O quê:** Se inicialização falhar, logar erro e disparar `sys.exit(1)` impedindo que o sistema continue

**Implementação:**
- Se `mt5.initialize()` retorna `False`:
  1. Log crítico com mensagem de erro do MT5
  2. Log crítico informando encerramento
  3. `sys.exit(1)` - interrompe a execução do programa

**Benefício:** 
- Evita que o sistema continue funcionando "cego" sem dados reais
- Força o operador a resolver problemas com MT5 antes de usar o sistema

**Evidência:**
- Linhas 32-37 de `src/data_handler/mt5_provider.py`

---

### ✅ Requisito 3: Interface de Dados
**O quê:** Método `get_latest_candles(symbol, timeframe, n=100)` retorna DataFrame com colunas esperadas (Open, High, Low, Close, Volume)

**Assinatura:**
```python
def get_latest_candles(
    self, 
    symbol: str, 
    timeframe: str, 
    n: int = 100
) -> pd.DataFrame:
```

**Retorno:**
```
DataFrame com:
- Index: timestamp (datetime, UTC)
- Colunas: Open, High, Low, Close, Volume (capitalizadas)
- Tipos: Open/High/Low/Close → float64, Volume → int64
```

**Exemplo:**
```
                     Open    High     Low   Close  Volume
time                                                      
2025-01-31 10:00:00 100.0  102.0   99.0  101.5    1000
2025-01-31 10:05:00 101.5  103.0  101.0  102.0    1200
```

**Timeframes Suportados:**
- M1, M5, M15, M30, H1, H4, D1, W1, MN1

**Tratamento de Erros:**
1. **Timeframe inválido** → `ValueError` com lista de válidos
2. **MT5 desconectado** → `ConnectionError`
3. **Sem dados** → `ValueError` com mensagem

**Evidência:**
- Linhas 43-145 de `src/data_handler/mt5_provider.py`

---

## Métodos Adicionais (Bônus)

### `get_latest_candles_as_events(symbol, timeframe, n=100)`
Converte o DataFrame para lista de `MarketDataEvent` para integração com EventBus.

```python
events = provider.get_latest_candles_as_events('WDO$', 'M5', n=100)
# → List[MarketDataEvent]
```

### `publish_to_eventbus(symbol, timeframe, n=100)`
Busca candles e publica direto no barramento de eventos.

```python
provider.publish_to_eventbus('WDO$', 'M5')
# → Publica eventos no EventBus automaticamente
```

### `shutdown()`
Encerra conexão com MT5 de forma segura.

```python
provider.shutdown()
# → ✅ MT5 desconectado com sucesso
```

---

## Testes Unitários

Arquivo: `tests/unit/test_mt5_provider.py`

Cobertura de testes:
- ✅ Fail Fast on init failure (`test_fail_fast_on_init_failure`)
- ✅ Successful initialization (`test_successful_initialization`)
- ✅ DataFrame format validation (`test_get_latest_candles_returns_dataframe`)
- ✅ Invalid timeframe handling (`test_invalid_timeframe_raises_error`)
- ✅ Empty data handling (`test_no_data_returned_raises_error`)
- ✅ EventBus integration (`test_get_latest_candles_as_events`)
- ✅ Graceful shutdown (`test_shutdown`)

**Executar testes:**
```bash
poetry run pytest tests/unit/test_mt5_provider.py -v
```

---

## Documentação

Arquivo: `docs/user/MT5PROVIDER_GUIDE.md`

Conteúdo:
- Overview e requisitos
- Guia de uso com exemplos
- Tratamento de erros
- Logging
- Arquitetura
- Instruções para testes

---

## Integração com Sistema

### Fluxo de Inicialização
```
programa.py
  ↓
MetaTraderProvider() [Fail Fast aqui]
  ├─ mt5.initialize() = True → OK
  └─ mt5.initialize() = False → sys.exit(1) [PARADA]
  ↓
get_latest_candles('WDO$', 'M5', n=100) → DataFrame
  ↓
LSTMAdapter, Features Engineering, etc.
```

### Compatibilidade
- ✅ DataFrames no formato esperado por `LSTMAdapter`
- ✅ Colunas capitalizadas: Open, High, Low, Close, Volume
- ✅ Index como timestamp (datetime)
- ✅ Tipos numéricos corretos (float64 para OHLC, int64 para Volume)

---

## Checklist de Entrega

- [x] Classe `MetaTraderProvider` implementada em `src/data_handler/mt5_provider.py`
- [x] Requisito 1: Conexão MT5 no `__init__`
- [x] Requisito 2: Fail Fast com `sys.exit(1)`
- [x] Requisito 3: `get_latest_candles()` retornando DataFrame
- [x] Validação de timeframes
- [x] Validação de dados retornados
- [x] Métodos auxiliares (events, eventbus, shutdown)
- [x] Testes unitários (`test_mt5_provider.py`)
- [x] Documentação de uso (`MT5PROVIDER_GUIDE.md`)
- [x] Verificação de sintaxe Python (`py_compile`)
- [x] Logging estruturado com níveis apropriados

---

## Notas de Desenvolvimento

### Importações
```python
import logging
import sys                                    # Para Fail Fast
from datetime import datetime
from typing import Optional
import MetaTrader5 as mt5                    # Requer terminal MT5
import pandas as pd                          # Para retorno DataFrame

from src.core.event_bus import event_bus    # Para EventBus (opcional)
from src.events import MarketDataEvent      # Para conversão de eventos
```

### Logging Estruturado
- `logger.critical()` para Fail Fast
- `logger.error()` para erros recuperáveis
- `logger.info()` para operações bem-sucedidas
- `logger.debug()` para detalhes de publi no eventbus

### Type Hints
- Completos em assinatura de métodos
- Retorno explícito: `→ pd.DataFrame`, `→ list[MarketDataEvent]`

### Convenção de Nomes
- Snake_case para parâmetros: `symbol`, `timeframe`, `n`
- Capitalizados para colunas: `Open`, `High`, `Low`, `Close`, `Volume`

---

## Próximos Passos (Sugestões)

1. Testar com MT5 real para validar:
   - Conexão efetiva
   - Retorno de dados corretos
   - Timeout behavior

2. Adicionar cache de candles (se necessário):
   - `.cache_data/` para histórico
   - Invalidação de cache temporal

3. Integração com `SimulationEngine`:
   - Usar `get_latest_candles()` para simulations
   - Usar `get_latest_candles_as_events()` para event-driven

4. Monitoramento:
   - Alertas se MT5 desconectar durante operação
   - Reconexão automática (Sprint 3)

---

## Referências

- **Arquivo Principal:** `src/data_handler/mt5_provider.py`
- **Testes:** `tests/unit/test_mt5_provider.py`
- **Documentação:** `docs/user/MT5PROVIDER_GUIDE.md`
- **Eventos:** `src/events.py` (MarketDataEvent)
- **EventBus:** `src/core/event_bus.py`

---

**Status:** ✅ Pronto para integração
**Complexidade:** Baixa (3 requisitos = 1 classe)
**Cobertura:** 100% dos requisitos + bônus
