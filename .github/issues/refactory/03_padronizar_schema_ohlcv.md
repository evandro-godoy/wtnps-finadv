---
name: 03_padronizar_schema_ohlcv
about: Padronizar schema OHLCV e garantir consistencia em providers e estrategias.
title: '[ARCH] Padronizar schema OHLCV (Open/High/Low/Close/Volume)'
labels: sprint-refactory, refactory, data, schema
assignees: 'Quant'
---

## 🎯 Objetivo
Padronizar o schema de dados de mercado para evitar conflitos entre lowercase e uppercase.

## 📂 Contexto & Arquivos
- **Alvo:** src/data_handler/mt5_provider.py, src/data_handler/provider.py, src/live/monitor_engine.py, src/strategies/*, src/modules/*
- **Dependências:** Strategy define_features, Model inputs

## 🛠️ Especificações Técnicas
1. Schema canonico definido: `Open`, `High`, `Low`, `Close`, `Volume`.
2. Index obrigatorio: `DatetimeIndex` em UTC.
3. Tipos esperados: OHLC como float, Volume como int.
4. Normalizar retorno de todos os providers para o schema canonico.
5. Atualizar estrategias e consumidores para o schema unico (sem fallback lowercase).
6. Incluir validacao de colunas obrigatorias no pipeline (falhar cedo com mensagem clara).

## 🔗 Dependências & Bloqueios
- [ ] Mapear consumidores que assumem uppercase/lowercase
- [ ] Ajustar testes de feature engineering
- [ ] Coordenar com 02_unificar_mt5_provider para reduzir duplicidade

## 📦 Definition of Done (DoD)
- [ ] Todos os providers retornam schema unico
- [ ] Estrategias e engines compatibilizadas
- [ ] Validacao de colunas obrigatorias aplicada no pipeline
- [ ] Testes atualizados
- [ ] Documentacao de schema revisada

## ✅ Verificacao
- [ ] Provedores retornam colunas `Open/High/Low/Close/Volume`
- [ ] Nao ha referencias a colunas lowercase em estrategias/engines

## 📊 Estimativa
- **Story Points:** 3
- **Horas:** 6h
- **Prioridade:** 🔴 ALTA
