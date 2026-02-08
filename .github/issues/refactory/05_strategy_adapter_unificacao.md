---
name: 05_strategy_adapter_unificacao
about: Template for Sprint 2 Integration tasks
title: '[ARCH] Unificar Strategy Adapter e carregamento dinamico'
labels: sprint-2, integration
assignees: ''
---

## 🎯 Objetivo
Remover caminhos paralelos de estrategia e garantir carregamento dinamico a partir do config.

## 📂 Contexto & Arquivos
- **Alvo:** src/live/monitor_engine.py, src/modules/strategy/lstm_adapter.py, src/strategies/*
- **Dependências:** BaseStrategy, config YAML

## 🛠️ Especificações Técnicas
1. Evitar instanciacao direta de `LSTMVolatilityStrategy` no monitor.
2. Adapter deve envolver a Strategy, nao competir com ela.
3. Carregamento de estrategia deve seguir config (`assets[].strategies[]`).
4. Definir um unico caminho de inferencia.

## 🔗 Dependências & Bloqueios
- [ ] Validar compatibilidade com modelos existentes
- [ ] Ajustar testes de inferencia

## 📦 Definition of Done (DoD)
- [ ] Uma unica trilha de estrategia/adapter
- [ ] Monitor e engines usam carregamento dinamico
- [ ] Testes ajustados
- [ ] Documentacao de estrategia revisada

## 📊 Estimativa
- **Story Points:** 5
- **Horas:** 10h
- **Prioridade:** 🟡 MEDIA
