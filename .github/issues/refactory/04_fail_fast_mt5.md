---
name: 04_fail_fast_mt5
about: Template for Sprint 2 Integration tasks
title: '[ARCH] Aplicar fail-fast consistente no MT5'
labels: sprint-2, integration
assignees: ''
---

## 🎯 Objetivo
Garantir comportamento fail-fast consistente em todas as inicializacoes do MT5.

## 📂 Contexto & Arquivos
- **Alvo:** src/data_handler/mt5_provider.py, src/data_handler/provider.py, src/live_trader.py, src/simulation/engine.py
- **Dependências:** settings.mt5 config, logging

## 🛠️ Especificações Técnicas
1. Definir politica unica de falha (ConnectionError e encerramento controlado).
2. Remover inicializacoes silenciosas que apenas logam erro.
3. Padronizar mensagens e tratamento em pontos de entrada.

## 🔗 Dependências & Bloqueios
- [ ] Confirmar comportamento desejado para ambiente de simulacao
- [ ] Revisar impacto em testes

## 📦 Definition of Done (DoD)
- [ ] Falha do MT5 interrompe fluxo de forma previsivel
- [ ] Logs consistentes em todos os modulos
- [ ] Testes atualizados
- [ ] Documentacao de operacao atualizada

## 📊 Estimativa
- **Story Points:** 3
- **Horas:** 6h
- **Prioridade:** 🟡 MEDIA
