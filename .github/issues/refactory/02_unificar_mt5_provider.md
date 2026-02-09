---
name: 02_unificar_mt5_provider
about: Unificar o MetaTraderProvider e padronizar imports e factory.
title: '[ARCH] Unificar MetaTraderProvider e imports'
labels: sprint-refactory, refactory, data, mt5
assignees: 'Engineer'
---

## 🎯 Objetivo
Eliminar duplicidade de providers MT5 e padronizar imports para uma unica implementacao canonica.

## 📌 Status (2026-02-08)
**Estado:** Parcial.

**Evidencias (codigo):**
- Existem duas implementacoes `MetaTraderProvider`: em `src/data_handler/mt5_provider.py` e em `src/data_handler/provider.py`.
- `SimulationEngine` e `LiveTrader` usam `get_provider_instance` de `provider.py`, que referencia a implementacao duplicada.
- `ReplayEngine` instancia `MetaTraderProvider` do modulo `provider.py`.

**Arquivos verificados:**
- src/data_handler/mt5_provider.py
- src/data_handler/provider.py
- src/simulation/engine.py
- src/live_trader.py
- src/live/replay_engine.py

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

## 🧭 Escopo detalhado
- Unificar a classe `MetaTraderProvider` na implementacao canonica em `src/data_handler/mt5_provider.py`.
- Ajustar `get_provider_instance` para retornar somente o provider canonico.
- Atualizar imports diretos em monitor, simulacao, live_trader, replay e setup_scanner.
- Remover a duplicata de `provider.py` ou mantela apenas como alias temporario.

## 🔧 Passos de implementacao
1. Atualizar `provider.py` para importar o provider canonico e expor via factory.
2. Substituir imports diretos da classe duplicada nos arquivos listados.
3. Remover/encapsular a classe duplicada em `provider.py`.
4. Revisar testes unitarios e docs que citam o provider antigo.

## 🧪 Plano de verificacao
- Buscar por `class MetaTraderProvider` e confirmar apenas a classe canonica.
- Confirmar que `get_provider_instance` retorna a classe canonica.
- Smoke test de `SimulationEngine` e `LiveTrader` sem erros de importacao.

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
