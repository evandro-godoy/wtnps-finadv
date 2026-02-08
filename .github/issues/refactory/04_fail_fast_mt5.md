---
name: 04_fail_fast_mt5
about: Aplicar fail-fast consistente no MT5 em fluxos live e simulacao.
title: '[ARCH] Aplicar fail-fast consistente no MT5'
labels: sprint-refactory, refactory, reliability, mt5
assignees: 'Guardian'
---

## 🎯 Objetivo
Garantir comportamento fail-fast consistente em todas as inicializacoes do MT5.

## 📂 Contexto & Arquivos
- **Alvo:** src/data_handler/mt5_provider.py, src/data_handler/provider.py, src/live_trader.py, src/simulation/engine.py, src/api/main.py
- **Dependências:** settings.mt5 config, logging

## 🛠️ Especificações Técnicas
1. Politica unica: falha de inicializacao do MT5 gera `ConnectionError` com log critico.
2. Em fluxos live (API/monitor/live_trader), falha deve interromper a inicializacao do servico.
3. Em fluxos de simulacao, falha deve retornar erro explicito (sem continuar em estado incompleto).
4. Remover inicializacoes silenciosas que apenas logam erro.
5. Padronizar mensagens e tratamento em pontos de entrada (prefixo consistente para logs criticos).

## 🔗 Dependências & Bloqueios
- [ ] Confirmar comportamento desejado para ambiente de simulacao
- [ ] Revisar impacto em testes
- [ ] Alinhar com 02_unificar_mt5_provider

## 📦 Definition of Done (DoD)
- [ ] Falha do MT5 interrompe fluxo de forma previsivel
- [ ] Logs consistentes em todos os modulos
- [ ] Erros propagados de forma explicita nos entrypoints
- [ ] Testes atualizados
- [ ] Documentacao de operacao atualizada

## ✅ Verificacao
- [ ] Simular falha de MT5 e confirmar interrupcao do startup
- [ ] Confirmar mensagens criticas padronizadas

## 📊 Estimativa
- **Story Points:** 3
- **Horas:** 6h
- **Prioridade:** 🟡 MEDIA
