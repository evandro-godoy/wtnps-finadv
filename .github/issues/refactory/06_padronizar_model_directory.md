---
name: 06_padronizar_model_directory
about: Template for Sprint 2 Integration tasks
title: '[ARCH] Padronizar chave model_directory nos configs'
labels: sprint-2, integration
assignees: ''
---

## 🎯 Objetivo
Eliminar divergencia entre `model_directory` e `models_directory` nos modulos e configs.

## 📂 Contexto & Arquivos
- **Alvo:** src/live_trader.py, src/simulation/engine.py, src/live/monitor_engine.py, src/setups/setup_scanner.py
- **Dependências:** configs/main.yaml

## 🛠️ Especificações Técnicas
1. Definir chave canonica `model_directory` no YAML.
2. Garantir fallback seguro para legado apenas onde necessario.
3. Atualizar leitura em todos os modulos para a chave canonica.

## 🔗 Dependências & Bloqueios
- [ ] Validar impacto nos artefatos existentes em models/

## 📦 Definition of Done (DoD)
- [ ] Leitura unica da chave `model_directory`
- [ ] Sem uso de `models_directory` no codebase
- [ ] Documentacao atualizada

## 📊 Estimativa
- **Story Points:** 2
- **Horas:** 4h
- **Prioridade:** 🟡 MEDIA
