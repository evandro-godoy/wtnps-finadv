---
name: 02_unificar_mt5_provider
about: Template for Sprint 2 Integration tasks
title: '[ARCH] Unificar MetaTraderProvider e imports'
labels: sprint-2, integration
assignees: ''
---

## 🎯 Objetivo
Eliminar duplicidade de providers MT5 e padronizar imports para uma unica implementacao.

## 📂 Contexto & Arquivos
- **Alvo:** src/data_handler/mt5_provider.py, src/data_handler/provider.py, src/live/monitor_engine.py, src/simulation/engine.py, src/live_trader.py
- **Dependências:** BaseDataProvider, get_provider_instance

## 🛠️ Especificações Técnicas
1. Definir `src/data_handler/mt5_provider.py` como implementacao unica.
2. Remover/encapsular `MetaTraderProvider` duplicado de provider.py.
3. Atualizar imports para usar apenas a implementacao canonica.
4. Manter interface minima esperada por `get_provider_instance`.

## 🔗 Dependências & Bloqueios
- [ ] Checar referencias em docs e testes
- [ ] Validar compatibilidade com SimulationEngine e LiveTrader

## 📦 Definition of Done (DoD)
- [ ] Apenas um MetaTraderProvider ativo no codebase
- [ ] Imports consolidados
- [ ] Testes relevantes ajustados
- [ ] Documentacao atualizada

## 📊 Estimativa
- **Story Points:** 5
- **Horas:** 10h
- **Prioridade:** 🔴 ALTA
