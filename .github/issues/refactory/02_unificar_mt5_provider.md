---
name: 02_unificar_mt5_provider
about: Unificar o MetaTraderProvider e padronizar imports e factory.
title: '[ARCH] Unificar MetaTraderProvider e imports'
labels: sprint-refactory, refactory, data, mt5
assignees: 'Engineer'
---

## 🎯 Objetivo
Eliminar duplicidade de providers MT5 e padronizar imports para uma unica implementacao canonica.

## 📂 Contexto & Arquivos
- **Alvo:** src/data_handler/mt5_provider.py, src/data_handler/provider.py, src/live/monitor_engine.py, src/simulation/engine.py, src/live_trader.py
- **Dependências:** BaseDataProvider, get_provider_instance
- **Decisao canonica:** manter `src/data_handler/mt5_provider.py` como unica implementacao de MetaTraderProvider.

## 🛠️ Especificações Técnicas
1. Definir `src/data_handler/mt5_provider.py` como implementacao unica.
2. Remover ou encapsular a classe duplicada em `src/data_handler/provider.py`.
3. Atualizar imports para usar apenas a implementacao canonica nos seguintes pontos:
	- src/live/monitor_engine.py
	- src/simulation/engine.py
	- src/live_trader.py
	- src/setups/setup_scanner.py
	- src/live/replay_engine.py
4. Manter interface minima esperada por `get_provider_instance` (factory deve retornar a classe canonica).
5. Garantir que o provider canonico implementa `is_connected()` para compatibilidade.

## 🔗 Dependências & Bloqueios
- [ ] Checar referencias em docs e testes
- [ ] Validar compatibilidade com SimulationEngine e LiveTrader
- [ ] Alinhar comportamento de fail-fast com a task 04_fail_fast_mt5

## 📦 Definition of Done (DoD)
- [ ] Apenas um MetaTraderProvider ativo no codebase
- [ ] Imports consolidados para a implementacao canonica
- [ ] `get_provider_instance` retorna apenas a implementacao canonica
- [ ] Testes relevantes ajustados (unitarios do provider, smoke em live/simulacao)
- [ ] Documentacao atualizada

## ✅ Verificacao
- [ ] Busca por `class MetaTraderProvider` retorna somente a classe canonica
- [ ] Imports atualizados nos arquivos listados

## 📊 Estimativa
- **Story Points:** 5
- **Horas:** 10h
- **Prioridade:** 🔴 ALTA
