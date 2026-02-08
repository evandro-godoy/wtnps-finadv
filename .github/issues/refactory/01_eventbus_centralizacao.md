---
name: 01_eventbus_centralizacao
about: Centralizar EventBus e remover acoplamento direto entre monitor, API e UI.
title: '[ARCH] Centralizar EventBus e remover acoplamento direto'
labels: sprint-refactory, refactory, architecture, eventbus
assignees: 'Architect'
---

## 🎯 Objetivo
Restaurar o fluxo event-driven como via exclusiva de comunicacao entre modulos, eliminando acoplamento direto de UI e acesso direto a dados internos do monitor.

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

## 🔗 Dependências & Bloqueios
- [ ] Mapear pontos que leem `buffer_df` diretamente
- [ ] Definir evento padrao para dados de candle (se necessario)
- [ ] Alinhar schema OHLCV com a task 03_padronizar_schema_ohlcv

## 📦 Definition of Done (DoD)
- [ ] Comunicacao entre modulos via EventBus apenas
- [ ] UI e API sem acesso direto a `buffer_df`
- [ ] `event_bus` singleton usado no monitor e consumidores
- [ ] Eventos `MARKET_DATA_CANDLE` e `INFERENCE_SIGNAL` definidos e publicados
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
