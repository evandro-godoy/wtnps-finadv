---
name: 01_eventbus_centralizacao
about: Template for Sprint 2 Integration tasks
title: '[ARCH] Centralizar EventBus e remover acoplamento direto'
labels: sprint-2, integration
assignees: ''
---

## 🎯 Objetivo
Restaurar o fluxo event-driven como via exclusiva de comunicacao entre modulos, eliminando acoplamento direto de UI e buffer.

## 📂 Contexto & Arquivos
- **Alvo:** src/live/monitor_engine.py, src/core/event_bus.py, src/gui/monitor_ui.py, src/api/main.py
- **Dependências:** EventBus, InferenceSignalEvent, WebSocketManager

## 🛠️ Especificações Técnicas
1. Usar o singleton `event_bus` como barramento central.
2. Substituir `ui_callback` e acesso direto a `buffer_df` por eventos publicados e consumidos.
3. Garantir que API e GUI consumam apenas eventos (ex.: `INFERENCE_SIGNAL`).
4. Manter compatibilidade de payloads para UI e WebSocket.

## 🔗 Dependências & Bloqueios
- [ ] Mapear pontos que leem `buffer_df` diretamente
- [ ] Definir evento padrao para dados de candle (se necessario)

## 📦 Definition of Done (DoD)
- [ ] Comunicacao entre modulos via EventBus apenas
- [ ] UI e API sem acesso direto a `buffer_df`
- [ ] Testes de integracao atualizados
- [ ] Documentacao de fluxo event-driven atualizada

## 📊 Estimativa
- **Story Points:** 5
- **Horas:** 12h
- **Prioridade:** 🔴 ALTA
