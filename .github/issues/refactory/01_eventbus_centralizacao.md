---
name: 01_eventbus_centralizacao
about: Centralizar EventBus e remover acoplamento direto entre monitor, API e UI.
title: '[ARCH] Centralizar EventBus e remover acoplamento direto'
labels: sprint-refactory, refactory, architecture, eventbus
assignees: 'Architect'
---

## 🎯 Objetivo
Restaurar o fluxo event-driven como via exclusiva de comunicacao entre modulos, eliminando acoplamento direto de UI e acesso direto a dados internos do monitor.

## 📌 Status (2026-02-08)
**Estado:** Parcial.

**Evidencias (codigo):**
- Monitor publica eventos via singleton `event_bus` e usa `MarketDataCandleEvent`/`InferenceSignalEvent`.
- API e GUI se inscrevem no `event_bus` (sem leitura direta de `buffer_df`).
- `RealTimeMonitor` ainda mantem `buffer_df` interno (necessario para inferencia), mas o contrato canonico `MARKET_DATA_CANDLE` ainda nao esta validado com schema/DTO no producer/consumer.
- Existe logica paralela de UI em backup que ainda usa `buffer_df` (arquivo de backup, nao usado em runtime principal).

**Arquivos verificados:**
- src/live/monitor_engine.py
- src/api/main.py
- src/gui/monitor_ui.py
- src/core/event_bus.py

## 🧭 Escopo detalhado
- Centralizar a comunicacao entre monitor, API e GUI exclusivamente via `event_bus`.
- Eliminar qualquer dependencia de leitura direta de `buffer_df` e callbacks diretos.
- Garantir o contrato canonico de `MARKET_DATA_CANDLE` e `INFERENCE_SIGNAL` com payload completo.
- Manter `buffer_df` apenas como estado interno do monitor (nao exposto).

## 🔧 Passos de implementacao
1. Inventariar acessos diretos a `buffer_df`/`ui_callback` em monitor, API e GUI.
2. Ajustar produtores para publicar eventos canonicos com todos os campos obrigatorios.
3. Ajustar consumidores para usar apenas eventos (sem leitura de buffers internos).
4. Atualizar checklist de smoke test e contrato no issue.

## 🧪 Plano de verificacao
- Confirmar publish/subscribe dos eventos `MARKET_DATA_CANDLE` e `INFERENCE_SIGNAL`.
- Acessar `/charts` e validar atualizacao via eventos.
- Garantir ausencia de acessos diretos a `buffer_df` fora do monitor.

## 📂 Contexto & Arquivos
- **Alvo:** src/live/monitor_engine.py, src/core/event_bus.py, src/gui/monitor_ui.py, src/api/main.py
- **Dependências:** EventBus, InferenceSignalEvent, WebSocketManager
- **Pontos atuais a eliminar:**
	- Leitura direta de `buffer_df` e `ui_callback` em monitor/UI/API.
	- EventBus local em monitor (preferir singleton `event_bus`).

## 🛠️ Especificações Técnicas
1. Usar o singleton `event_bus` como barramento central (nao instanciar EventBus local no monitor).
2. Substituir `ui_callback` e acesso direto a `buffer_df` por eventos publicados e consumidos.
3. Definir evento canonico para candles (ex.: `MARKET_DATA_CANDLE`) com payload minimo:
	- `timestamp`, `ticker`, `timeframe`, `open`, `high`, `low`, `close`, `volume`.
4. Manter `INFERENCE_SIGNAL` com payload compatível com UI e WebSocket.
5. Atualizar API e GUI para consumir apenas eventos (sem leitura direta de buffer).
6. Documentar contrato de eventos (tipos e campos) no proprio issue.

## 📜 Contrato de Eventos (Canonico)

### MARKET_DATA_CANDLE

| Campo | Tipo | Obrigatorio | Observacoes |
| --- | --- | --- | --- |
| event_type | string | sim | Valor fixo: `MARKET_DATA_CANDLE`. |
| timestamp | datetime | sim | ISO-8601 em UTC. |
| ticker | string | sim | Ex: `WDO$`. |
| timeframe | string | sim | Ex: `M5`, `H1`. |
| Open | float | sim | Schema canonico OHLCV. |
| High | float | sim | Schema canonico OHLCV. |
| Low | float | sim | Schema canonico OHLCV. |
| Close | float | sim | Schema canonico OHLCV. |
| Volume | int | sim | Schema canonico OHLCV. |

### INFERENCE_SIGNAL

| Campo | Tipo | Obrigatorio | Observacoes |
| --- | --- | --- | --- |
| event_type | string | sim | Valor fixo: `INFERENCE_SIGNAL`. |
| timestamp | datetime | sim | ISO-8601 em UTC. |
| ticker | string | sim | Ex: `WDO$`. |
| timeframe | string | sim | Ex: `M5`, `H1`. |
| ai_signal | string | sim | `COMPRA`, `VENDA`, `HOLD`. |
| probability | float | sim | 0.0 a 1.0. |
| price | float | sim | Preco do ultimo candle. |
| indicators | object | sim | Ex: `atr`, `ema_9`, `ema_20`, `rsi`, `trend`, `pattern`, `support`, `resistance`, `signal_valid`, `validation_reason`. |

## 🔗 Dependências & Bloqueios
- [ ] Mapear pontos que leem `buffer_df` diretamente
- [ ] Definir evento padrao para dados de candle (se necessario)
- [ ] Alinhar schema OHLCV com a task 03_padronizar_schema_ohlcv

## 📦 Definition of Done (DoD)
- [ ] Comunicacao entre modulos via EventBus apenas
- [x] UI e API sem acesso direto a `buffer_df`
- [x] `event_bus` singleton usado no monitor e consumidores
- [x] Eventos `MARKET_DATA_CANDLE` e `INFERENCE_SIGNAL` definidos e publicados
- [ ] UI e WebSocket recebem payloads via eventos sem regressao visual
- [ ] Testes de integracao atualizados ou checklist de smoke test adicionado
- [ ] Documentacao de fluxo event-driven atualizada

## ✅ Verificacao
- [ ] Abrir /charts e confirmar renderizacao com dados via eventos
- [ ] Conferir logs de publicacao e consumo de eventos

## 📊 Estimativa
- **Story Points:** 5
- **Horas:** 12h
- **Prioridade:** 🔴 ALTA
