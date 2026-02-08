## Plan: Detalhar Backlog Refactory

Vou atualizar cada issue em .github/issues/refactory com escopo, passos, dependencias e criterios de aceite alinhados ao handover e aos docs do provider. O foco e tornar cada task executavel sem ambiguidade, mantendo o template e a prioridade existente. Isso inclui especificar arquivos-alvo, padrao de schema OHLCV, evento/payload esperado, comportamento fail-fast por entrypoint e padrao de chave model_directory. Tambem vou adicionar plano de verificacao simples por task.

**Steps**
1. Revisar e enriquecer 01_eventbus_centralizacao com inventario de acessos diretos, definicao de evento/payload e criterios de aceite de UI/WebSocket; atualizar [.github/issues/refactory/01_eventbus_centralizacao.md](.github/issues/refactory/01_eventbus_centralizacao.md) com referencias a [src/live/monitor_engine.py](src/live/monitor_engine.py), [src/api/main.py](src/api/main.py), [src/gui/monitor_ui.py](src/gui/monitor_ui.py) e [src/core/event_bus.py](src/core/event_bus.py).
2. Especificar a unificacao do provider em 02_unificar_mt5_provider com decisao canonica, lista de imports a ajustar e impacto em factories; atualizar [.github/issues/refactory/02_unificar_mt5_provider.md](.github/issues/refactory/02_unificar_mt5_provider.md) com referencias a [src/data_handler/mt5_provider.py](src/data_handler/mt5_provider.py) e [src/data_handler/provider.py](src/data_handler/provider.py).
3. Fixar schema canonico OHLCV e consumidores em 03_padronizar_schema_ohlcv; atualizar [.github/issues/refactory/03_padronizar_schema_ohlcv.md](.github/issues/refactory/03_padronizar_schema_ohlcv.md) com pontos de adaptacao em [src/strategies/](src/strategies/) e [src/modules/](src/modules/).
4. Detalhar politica fail-fast por contexto (live vs simulacao) em 04_fail_fast_mt5; atualizar [.github/issues/refactory/04_fail_fast_mt5.md](.github/issues/refactory/04_fail_fast_mt5.md) com comportamento esperado e logs padrao.
5. Consolidar fluxo de estrategia/adapter em 05_strategy_adapter_unificacao; atualizar [.github/issues/refactory/05_strategy_adapter_unificacao.md](.github/issues/refactory/05_strategy_adapter_unificacao.md) com carregamento dinamico via config e eliminacao de instanciacao direta.
6. Padronizar leitura de model_directory em 06_padronizar_model_directory; atualizar [.github/issues/refactory/06_padronizar_model_directory.md](.github/issues/refactory/06_padronizar_model_directory.md) com migration steps e referencias a [configs/main.yaml](configs/main.yaml).
7. Definir local canonico de templates/static e ajustes no FastAPI em 07_assets_ui_canonical; atualizar [.github/issues/refactory/07_assets_ui_canonical.md](.github/issues/refactory/07_assets_ui_canonical.md) com passos e criterios de aceite.

**Verification**
- Revisar cada issue para garantir: escopo com caminhos, passos ordenados, dependencias e DoD verificavel; leitura rapida dos sete arquivos em .github/issues/refactory.

**Decisions**
- Usar o schema canonico Open/High/Low/Close/Volume com DatetimeIndex UTC.
- Tratar event-driven como via exclusiva para UI/API.
- Definir model_directory como chave unica de configuracao.
