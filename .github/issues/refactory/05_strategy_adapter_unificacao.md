---
name: 05_strategy_adapter_unificacao
about: Unificar adapter e carregamento dinamico de estrategias via config.
title: '[ARCH] Unificar Strategy Adapter e carregamento dinamico'
labels: sprint-refactory, refactory, ml, strategy
assignees: 'Quant'
---

## 🎯 Objetivo
Remover caminhos paralelos de estrategia e garantir carregamento dinamico a partir do config.

## 📌 Status (2026-02-08)
**Estado:** Parcial.

**Evidencias (codigo):**
- `RealTimeMonitor` instancia `LSTMVolatilityStrategy` diretamente.
- `LSTMVolatilityAdapter` existe, mas nao e o caminho unico de inferencia.
- API `/chart-data` instancia `LSTMVolatilityStrategy` diretamente.

**Arquivos verificados:**
- src/live/monitor_engine.py
- src/modules/strategy/lstm_adapter.py
- src/api/routes/chart_data.py
- configs/main.yaml

## 📂 Contexto & Arquivos
- **Alvo:** src/live/monitor_engine.py, src/modules/strategy/lstm_adapter.py, src/strategies/*, configs/main.yaml
- **Dependências:** BaseStrategy, config YAML

## 🛠️ Especificações Técnicas
1. Evitar instanciacao direta de `LSTMVolatilityStrategy` no monitor.
2. Adapter deve envolver a Strategy, nao competir com ela.
3. Carregamento de estrategia deve seguir config (`assets[].strategies[]`) e modulo/class name.
4. Definir um unico caminho de inferencia: config -> Strategy -> Adapter -> EventBus.
5. Remover qualquer construcao direta de Strategy fora do loader dinamico.

## 🧭 Escopo detalhado
- Centralizar carregamento dinamico de estrategias via config.
- Garantir que o adapter encapsula a Strategy (sem logica duplicada).
- Remover instanciacoes diretas de `LSTMVolatilityStrategy` fora do loader.
- Alinhar API de chart-data e monitor ao caminho unico.

## 🔧 Passos de implementacao
1. Mapear instanciacoes diretas da Strategy (monitor, API, GUI).
2. Introduzir ou ajustar loader para sempre envolver Strategy com Adapter.
3. Atualizar consumidores para usar o caminho config -> Strategy -> Adapter.
4. Ajustar testes de inferencia para o novo fluxo.

## 🧪 Plano de verificacao
- Monitor usa estrategia definida no YAML via loader dinamico.
- Adapter publica eventos e Strategy permanece pura.
- Nenhuma instanciacao direta de `LSTMVolatilityStrategy` fora do loader.

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
