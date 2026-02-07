## Plan: Sprint 3 — The Great Merge

**TL;DR:** O `newapp/` já foi parcialmente migrado para o `src/` canônico. A Sprint 3 foca em **consolidar** o que já existe, resolver conflitos estruturais (dual providers, dual UI stacks, `src/main` sem extensão .py), unificar imports, e garantir que o sistema rode end-to-end sem `ModuleNotFoundError`. São 5 issues independentes, executáveis em paralelo.

**Decisões-chave incorporadas:**
- **UI**: Híbrido — Plotly.js (base) + portar virtual-scroll.js, CSS Grid
- **Provider**: `mt5_provider.py` (Sprint 2) como canônico
- **Config**: `configs/main.yaml` existe e está atualizado (path absoluto para models)

---

### Descobertas Críticas da Pesquisa

| Achado | Impacto | Ação |
|--------|---------|------|
| `src/main` sem extensão `.py` | Não é importável | Renomear para `src/main.py` |
| Duas classes `MetaTraderProvider` com column-naming diferente (`Open` vs `open`) | Quebra de inferência se trocar provider | Migrar monitor_engine + testes para `mt5_provider.py` + adapter de columns |
| `src/live/monitor_engine.py` importa da `provider.py` (legacy) | Conflito direto com decisão de usar `mt5_provider.py` | Issue 1 resolve isso |
| `configs/main.yaml` usa path absoluto `c:/projects/wtnps-trade/models` | Path provavelmente incorreto para `wtnps-finadv` | Corrigir para `models` (relativo) |
| `test_lstm_inference.py` importa `MetaTraderProvider` de `provider.py` | Teste quebrará ao deprecar provider.py | Issue 5 corrige |
| `templates/` usa Plotly; nenhum virtual-scroll ou CSS Grid existe | UI do newapp não foi migrada | Issue 2 porta esses assets |
| `src/modules/execution/` vazio, `src/data_handler/hybrid_data_loader.py` não existe | Referências do user inexistentes | Remover das issues ou criar stubs |
| Não existe `static/` na raiz nem `.github/issues/sprint3/` | Precisam ser criados | Issue 2 cria `static/`, Issue meta cria sprint3/ |

---

### Steps — Issues da Sprint

#### Issue 1: [CORE] Migrar MonitorEngine para mt5_provider.py
**Responsável:** @ARCHITECT — Sem dependências externas

- **Problema:** [src/live/monitor_engine.py](src/live/monitor_engine.py#L13) importa `MetaTraderProvider` de `src.data_handler.provider` (legacy, lowercase columns). Precisa migrar para `src.data_handler.mt5_provider` (config-driven, Capitalized columns).
- **Ações:**
  1. Em [src/live/monitor_engine.py](src/live/monitor_engine.py), trocar import de `src.data_handler.provider.MetaTraderProvider` para `src.data_handler.mt5_provider.MetaTraderProvider`
  2. Adaptar todas as referências de colunas no RealTimeMonitor: `df['close']` → `df['Close']`, `df['open']` → `df['Open']`, etc. (afeta `_process_new_candle`, `define_features`, buffer operations)
  3. Remover `yaml.safe_load` e `_load_config` (usar `src.core.config.settings` ao invés de ler YAML direto)
  4. Renomear `src/main` → `src/main.py` (extensão faltante)
  5. Corrigir `configs/main.yaml`: `model_directory: "c:/projects/wtnps-trade/models"` → `model_directory: "models"`
  6. Integrar `MonitorEngine` com `TradingSystem` de [src/main.py](src/main) — o `TradingSystem.start()` deve instanciar `RealTimeMonitor` ao invés de ter loop próprio
- **Arquivos:** [src/live/monitor_engine.py](src/live/monitor_engine.py), [src/main](src/main), [configs/main.yaml](configs/main.yaml)
- **DoD:** MonitorEngine usa `mt5_provider.MetaTraderProvider`, `src/main.py` existe com extensão, import `python -c "from src.live.monitor_engine import RealTimeMonitor"` não dá erro

#### Issue 2: [UI] Migrar Templates + Static (Híbrido Plotly+newapp)
**Responsável:** @FULLSTACK — Independente das outras

- **Problema:** O frontend Plotly.js existe em [templates/](templates/) mas faltam assets do newapp: virtual-scroll.js, CSS Grid responsivo, Split.js integration
- **Ações:**
  1. Criar `static/` na raiz do projeto (para servir assets de forma padrão, paralelo ao `templates/static/`)
  2. Portar `virtual-scroll.js` — criar `templates/static/js/virtual-scroll.js` com `VirtualScroll` e `PredictionVirtualScroll` classes para tabelas de sinais performáticas
  3. Adicionar CSS Grid ao [templates/static/css/charts_clean.css](templates/static/css/charts_clean.css) — merge do layout responsivo (gutter, split panes) do newapp com o dark theme existente
  4. Integrar Split.js via CDN no [templates/charts_clean.html](templates/charts_clean.html) — painel de chart redimensionável
  5. Atualizar [src/api/main.py](src/api/main.py) para montar `static/` na raiz se o diretório existir
  6. Manter GUI Tkinter [src/gui/monitor_ui.py](src/gui/monitor_ui.py) inalterado (não alterar lógica de backend)
- **Arquivos:** `templates/charts_clean.html`, `templates/static/css/charts_clean.css`, `templates/static/js/virtual-scroll.js` (novo), `src/api/main.py`
- **DoD:** `http://localhost:8000/` mostra chart com split panes e tabela de sinais com virtual scroll

#### Issue 3: [STRATEGY] Consolidar LSTM + Adapter
**Responsável:** @QUANT — Independente das outras

- **Problema:** A estratégia LSTM existe em dois locais: [src/strategies/lstm_volatility.py](src/strategies/lstm_volatility.py) (strategy completa, 465 linhas) e [src/modules/strategy/lstm_adapter.py](src/modules/strategy/lstm_adapter.py) (adapter event-driven, 213 linhas). O adapter usa `define_features()` da strategy mas tem seu próprio buffer e normalização.
- **Ações:**
  1. Validar que `LSTMVolatilityAdapter.on_market_data()` gera features idênticas ao `LSTMVolatilityStrategy.define_features()` — atenção ao column naming (`Open` vs `open`) que mudará com Issue 1
  2. No adapter, adaptar input columns para Capitalized (`Open`, `High`, `Low`, `Close`, `Volume`) conforme `mt5_provider.py`
  3. Verificar lookback: adapter usa 108, strategy usa 96 — reconciliar (adapter auto-ajusta via `model.input_shape`, mas confirmar)
  4. Criar `tests/unit/test_lstm_adapter.py` com teste de shape consistency: dados sintéticos → `on_market_data()` → `SignalEvent` publicado
  5. Verificar `.keras` models em [models/](models/) — confirmar que são carregáveis pelo adapter (artifact naming: `{TICKER}_LSTMVolatilityStrategy_M5_prod_lstm.keras`)
  6. NÃO criar `hybrid_data_loader.py` — não existe base para isso; remover referências dos docs
- **Arquivos:** [src/modules/strategy/lstm_adapter.py](src/modules/strategy/lstm_adapter.py), `tests/unit/test_lstm_adapter.py` (novo)
- **DoD:** `pytest tests/unit/test_lstm_adapter.py -v` passa 100%, adapter carrega modelo `.keras` existente

#### Issue 4: [OPS] Atualizar Ambiente (Poetry)
**Responsável:** @DEVOPS — Blocker parcial (rodar primeiro ou em paralelo)

- **Problema:** Dependências inconsistentes: `yfinance` importado em [src/data_handler/provider.py](src/data_handler/provider.py) mas não está no `pyproject.toml`. `tkcalendar` mencionado mas ausente. `psutil` usado por [scripts/dry_run.py](scripts/dry_run.py) mas não declarado.
- **Ações:**
  1. Adicionar ao `pyproject.toml`: `yfinance`, `tkcalendar`, `psutil`
  2. Verificar se `talib` é necessário (pesquisa mostra que NÃO, confirm)
  3. Verificar se `flask` é necessário (pesquisa mostra que NÃO — projeto usa FastAPI)
  4. Rodar `poetry lock` e `poetry install`
  5. Checar se `bokeh` ainda é necessário ou se pode ser removido (se decisão UI é Plotly-first)
  6. Validar versões: `tensorflow>=2.15`, `keras>=3.0` compatibilidade com `.keras` format
- **Arquivos:** [pyproject.toml](pyproject.toml), `poetry.lock`
- **DoD:** `poetry install` sem erros, `poetry run python -c "import yfinance; import psutil; import tkcalendar"` OK

#### Issue 5: [QA] Varredura de Integridade Pós-Merge
**Responsável:** @GUARDIAN — Executar APÓS Issues 1-4

- **Problema:** Trocar provider causa cascade de `ImportError` e column name mismatches nos testes
- **Ações:**
  1. Corrigir [tests/unit/test_lstm_inference.py](tests/unit/test_lstm_inference.py) — trocar import de `src.data_handler.provider.MetaTraderProvider` para `src.data_handler.mt5_provider.MetaTraderProvider` + adaptar column names
  2. Rodar `poetry run pytest tests/ -v --tb=short` e corrigir todos os `ModuleNotFoundError`
  3. Rodar `poetry run python -c "from src.main import TradingSystem"` (renomeado na Issue 1)
  4. Rodar `poetry run python -c "from src.live.monitor_engine import RealTimeMonitor"`
  5. Rodar `poetry run python -c "from src.api.main import app"`
  6. Validar que [src/api/main.py](src/api/main.py) → `RealTimeMonitor` → `mt5_provider.MetaTraderProvider` chain funciona (sem MT5: mock)
  7. Limpar dead code: `src/gui/monitor_ui_backup.py` (backup desnecessário), verificar se `provider.py` ainda é necessário (manter para YFinanceProvider, marcar MetaTraderProvider como deprecated)
- **Arquivos:** Todos os que foram modificados nas Issues 1-4 + `tests/`
- **DoD:** `pytest` 100% pass (com mocks para MT5), `flake8 src/` sem erros críticos, sistema inicia sem crashes de import

---

### Verification

```powershell
# 1. Import validation (Issue 5 final check)
poetry run python -c "from src.main import TradingSystem; print('OK')"
poetry run python -c "from src.live.monitor_engine import RealTimeMonitor; print('OK')"
poetry run python -c "from src.api.main import app; print('OK')"

# 2. Test suite
poetry run pytest tests/ -v --tb=short

# 3. API smoke test
poetry run uvicorn src.api.main:app --host 0.0.0.0 --port 8000 &
# Em outro terminal:
curl http://localhost:8000/health

# 4. Dependency validation
poetry install
poetry run python scripts/validate_environment.py
```

### Decisions

- **Provider canônico:** `mt5_provider.py` — `provider.py` mantido apenas para `YFinanceProvider`, com `MetaTraderProvider` marcado como `@deprecated`
- **UI stack:** Plotly.js (base) + virtual-scroll.js + Split.js + CSS Grid (porte híbrido do newapp)
- **`hybrid_data_loader.py`:** Não existe e não será criado nesta Sprint (removido do escopo)
- **Ordem de execução:** Issues 1-4 em paralelo → Issue 5 (pós-merge)
- **Column naming:** Padronizar para Capitalized (`Open`, `High`, `Low`, `Close`, `Volume`) em todo o codebase, consistente com `mt5_provider.py`
