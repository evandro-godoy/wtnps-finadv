---
name: 03_padronizar_schema_ohlcv
about: Template for Sprint 2 Integration tasks
title: '[ARCH] Padronizar schema OHLCV (Open/High/Low/Close/Volume)'
labels: sprint-2, integration
assignees: ''
---

## 🎯 Objetivo
Padronizar o schema de dados de mercado para evitar conflitos entre lowercase e uppercase.

## 📂 Contexto & Arquivos
- **Alvo:** src/data_handler/mt5_provider.py, src/data_handler/provider.py, src/live/monitor_engine.py, src/strategies/*
- **Dependências:** Strategy define_features, Model inputs

## 🛠️ Especificações Técnicas
1. Definir schema canonico (Open/High/Low/Close/Volume) ou (open/high/low/close/volume).
2. Normalizar o retorno de todos os providers para o schema definido.
3. Atualizar estrategias e consumidores para o schema unico.
4. Incluir validacao de colunas obrigatorias no pipeline.

## 🔗 Dependências & Bloqueios
- [ ] Mapear consumidores que assumem uppercase/lowercase
- [ ] Ajustar testes de feature engineering

## 📦 Definition of Done (DoD)
- [ ] Todos os providers retornam schema unico
- [ ] Estrategias e engines compatibilizadas
- [ ] Testes atualizados
- [ ] Documentacao de schema revisada

## 📊 Estimativa
- **Story Points:** 3
- **Horas:** 6h
- **Prioridade:** 🔴 ALTA
