---
name: 05_strategy_adapter_unificacao
about: Unificar adapter e carregamento dinamico de estrategias via config.
title: '[ARCH] Unificar Strategy Adapter e carregamento dinamico'
labels: sprint-refactory, refactory, ml, strategy
assignees: 'Quant'
---

## 🎯 Objetivo
Remover caminhos paralelos de estrategia e garantir carregamento dinamico a partir do config.

## 📂 Contexto & Arquivos
- **Alvo:** src/live/monitor_engine.py, src/modules/strategy/lstm_adapter.py, src/strategies/*, configs/main.yaml
- **Dependências:** BaseStrategy, config YAML

## 🛠️ Especificações Técnicas
1. Evitar instanciacao direta de `LSTMVolatilityStrategy` no monitor.
2. Adapter deve envolver a Strategy, nao competir com ela.
3. Carregamento de estrategia deve seguir config (`assets[].strategies[]`) e modulo/class name.
4. Definir um unico caminho de inferencia: config -> Strategy -> Adapter -> EventBus.
5. Remover qualquer construcao direta de Strategy fora do loader dinamico.

## 🔗 Dependências & Bloqueios
- [ ] Validar compatibilidade com modelos existentes
- [ ] Ajustar testes de inferencia
- [ ] Depende da padronizacao de schema (task 03)

## 📦 Definition of Done (DoD)
- [ ] Uma unica trilha de estrategia/adapter
- [ ] Monitor e engines usam carregamento dinamico
- [ ] Nenhuma instanciacao direta de `LSTMVolatilityStrategy` fora do loader
- [ ] Testes ajustados
- [ ] Documentacao de estrategia revisada

## ✅ Verificacao
- [ ] Execucao do monitor usa estrategia definida no YAML
- [ ] Eventos de sinal publicados via adapter

## 📊 Estimativa
- **Story Points:** 5
- **Horas:** 10h
- **Prioridade:** 🟡 MEDIA
