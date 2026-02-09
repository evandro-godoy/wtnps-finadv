---
name: 03_padronizar_schema_ohlcv
about: Padronizar schema OHLCV e garantir consistencia em providers e estrategias.
title: '[ARCH] Padronizar schema OHLCV (Open/High/Low/Close/Volume)'
labels: sprint-refactory, refactory, data, schema
assignees: 'Quant'
---

## 🎯 Objetivo
Padronizar o schema de dados de mercado para evitar conflitos entre lowercase e uppercase.

## 📌 Status (2026-02-08)
**Estado:** Parcial.

**Evidencias (codigo):**
- Helper canonico em `src/data_handler/ohlcv_schema.py` existe e e usado em providers.
- `MetaTraderProvider` (mt5_provider.py) retorna `Open/High/Low/Close/Volume` e index UTC.
- Ainda existem consumidores com uso de chaves lowercase (`close`) em API/UI/Replay/GUI e outros modulos.

**Arquivos verificados:**
- src/data_handler/ohlcv_schema.py
- src/data_handler/mt5_provider.py
- src/data_handler/provider.py
- src/api/routes/chart_data.py
- src/gui/monitor_ui.py
- src/live/replay_engine.py
- src/run.py

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

## 🧭 Escopo detalhado
- Remover uso de chaves lowercase (`open/high/low/close/volume`) em consumidores.
- Garantir `DatetimeIndex` UTC em todos os datasets que entram no pipeline.
- Aplicar `validate_ohlcv_schema` na entrada de consumidores criticos.
- Atualizar pontos de UI/API/Replay que ainda transformam dados para lowercase.

## 🔧 Passos de implementacao
1. Mapear ocorrencias de lowercase em estrategias, engines, API e GUI.
2. Substituir acessos por colunas canonicas e remover fallbacks.
3. Aplicar validacao centralizada do schema nos consumidores principais.
4. Ajustar testes de feature engineering e pipelines afetados.

## 🧪 Plano de verificacao
- Providers retornam `Open/High/Low/Close/Volume` com index UTC.
- Nenhuma referencia a `close`/`open` lowercase em estrategias/engines.
- Validacao falha cedo quando o schema esta incorreto.

## 🔗 Dependências & Bloqueios
- [ ] Mapear consumidores que assumem uppercase/lowercase
- [ ] Ajustar testes de feature engineering
- [ ] Coordenar com 02_unificar_mt5_provider para reduzir duplicidade

## 📦 Definition of Done (DoD)
- [x] Todos os providers retornam schema unico
- [ ] Estrategias e engines compatibilizadas
- [ ] Validacao de colunas obrigatorias aplicada no pipeline
- [x] Testes atualizados
- [ ] Documentacao de schema revisada

## ✅ Verificacao
- [ ] Provedores retornam colunas `Open/High/Low/Close/Volume`
- [ ] Nao ha referencias a colunas lowercase em estrategias/engines

## 📊 Estimativa
- **Story Points:** 3
- **Horas:** 6h
- **Prioridade:** 🔴 ALTA
