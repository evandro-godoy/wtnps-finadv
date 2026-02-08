# 🏛️ PROJECT HANDOVER & ARCHITECTURAL AUDIT
> **Para:** Agente ARCHITECT
> **De:** Tech Lead / Context Manager
> **Data:** 07/02/2026
> **Contexto:** Encerramento da fase de Migração (Sprint 3) e Preparação para Demo (Sprint 4).

---

## 1. O Objetivo Original (North Star) 🌟
O projeto **WTNPS-FINADV** é um sistema de trading algorítmico de nível institucional ("Obra de Arte"), desenhado para operar no mercado brasileiro (B3) via MetaTrader 5 (MT5).

### Pilares de Negócio
1.  **Monitoramento Passivo:** O sistema observa o mercado em tempo real (candles M5).
2.  **Inferência ML:** Utiliza modelos LSTM pré-treinados para prever volatilidade/direção.
3.  **Visualização Limpa:** Fornece feedback visual imediato via Interface Web (`charts_clean`), sem poluição visual.
4.  **Segurança (Fail-Fast):** Se o dado não é confiável ou a conexão cai, o sistema para imediatamente. Nada de operar "cego".

### Pilares Técnicos (A "Constituição")
1.  **Monólito Modular:** Um único repositório, mas com módulos desacoplados.
2.  **Event-Driven:** A comunicação entre módulos (Data -> Strategy -> UI) ocorre **exclusivamente** via `EventBus`.
3.  **Canonical Layout:** Código fonte estritamente em `src/`. Testes em `tests/`. Docs em `docs/`.
4.  **Type Safety:** Uso extensivo de Pydantic e Type Hints.

---

## 2. Estado Atual: O "Grande Merge" Incompleto 🚧

A análise do repositório `wtnps-finadv` revela que a migração do código legado (`newapp`) para a estrutura canônica foi iniciada, mas **não finalizada com limpeza**. Temos um cenário de "Esquizofrenia Arquitetural": o corpo novo (`src/`) convive com o corpo antigo (`newapp/`) dentro do mesmo repo.

### 🕵️‍♂️ Diagnóstico de Integridade

| Componente | Status | Localização Atual | Observação Crítica |
| :--- | :--- | :--- | :--- |
| **Data Provider** | ⚠️ Duplicado | `src/data_handler/mt5_provider.py` (Novo) <br> `newapp/src/data_handler/` (Antigo) | Precisamos garantir que o `MonitorEngine` use APENAS o novo provider. |
| **Strategy Engine** | ⚠️ Duplicado | `src/modules/strategy/lstm_adapter.py` <br> `src/strategies/lstm_volatility.py` | Lógica de negócio espalhada. O Adapter deve encapsular a Estratégia, não competir com ela. |
| **Frontend Assets** | ❌ Disperso | `templates/` (Raiz) <br> `newapp/templates/` <br> `newapp/static/` | O `launch.json` e o `main.py` podem estar apontando para lugares diferentes. |
| **Models ML** | ⚠️ Risco | `models/` (Raiz) <br> `newapp/models/others/` | Risco de carregar binários desatualizados se o PATH não for absoluto e validado. |
| **Config** | ✅ Estável | `src/core/config.py` + `.env` | O sistema de configuração parece sólido e centralizado. |

---

## 3. Ações Críticas Pendentes (Gap Analysis) 📉

Para viabilizar a demonstração e estabilizar o projeto, as seguintes anomalias devem ser resolvidas IMEDIATAMENTE:

### 🔴 Prioridade Crítica (Showstoppers)
1.  **Exorcismo do `newapp`:** A pasta `newapp/` ainda existe na raiz. Isso causa confusão nos imports.
    * *Ação:* Todo código útil deve ser movido para `src/` e a pasta `newapp/` deletada.
2.  **Conflito de Entrypoints:** Temos `src/main.py` (Orquestrador Novo) e `newapp/main.py` (Legado).
    * *Ação:* Garantir que `src/main.py` seja o único ponto de entrada e que ele suba o servidor Web (Uvicorn) E o Monitor em background.
3.  **Falta de Rotas de UI no Core:** O arquivo `src/api/routes` precisa servir o template `charts_clean.html`. Atualmente, essa lógica pode estar presa no `main.py` antigo.

### 🟡 Prioridade Alta (Qualidade)
1.  **Padronização de Indicadores:** O roteiro da demo exige SMA21 (Azul), SMA200 (Preta), EMA9 (Vermelha).
    * *Ação:* Verificar se `src/utils/indicators.py` calcula isso e se o JSON de resposta da API inclui esses campos.
2.  **Limpeza de Estratégias:** Consolidação dos arquivos em `src/modules/strategy`. Decidir se usamos a classe `LSTMVolatilityStrategy` ou se a lógica fica dentro do `Adapter`. (Recomendação: Mantenha a Strategy pura e o Adapter como wrapper).

---

## 4. Diretrizes para o Agente ARCHITECT (Próximos Passos) 🗺️

**Ao planejar as próximas Issues, siga esta ordem de batalha:**

1.  **Fase 1: Saneamento (Cleanup):**
    * Identificar arquivos órfãos em `newapp/`.
    * Mover templates HTML/CSS/JS para `src/interface/templates` e `src/interface/static` (ou manter na raiz se o framework exigir, mas sem duplicatas).
    * **DELETAR** a pasta `newapp/`.

2.  **Fase 2: Wiring (Integração):**
    * Refatorar `src/main.py` para injetar as dependências: `Config` -> `EventBus` -> `MT5Provider` -> `MonitorEngine`.
    * Conectar o `MonitorEngine` ao `EventBus` para que os eventos de mercado cheguem ao Frontend via WebSocket/Polling.

3.  **Fase 3: Demo Prep:**
    * Validar se o endpoint `/charts` entrega o JSON com OHLCV + Médias Móveis.
    * Testar a execução via VS Code (`F5`).

---

**Nota Final:** Não escreva código novo ("features") até que a estrutura de pastas esteja unificada. A existência de dois diretórios de código fonte (`src` e `newapp`) é a maior ameaça técnica atual.