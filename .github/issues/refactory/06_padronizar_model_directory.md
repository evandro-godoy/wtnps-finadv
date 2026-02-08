---
name: 06_padronizar_model_directory
about: Padronizar chave model_directory nos configs e consumidores.
title: '[ARCH] Padronizar chave model_directory nos configs'
labels: sprint-refactory, refactory, config
assignees: 'Devops'
---

## 🎯 Objetivo
Eliminar divergencia entre `model_directory` e `models_directory` nos modulos e configs.

## 📂 Contexto & Arquivos
- **Alvo:** src/live_trader.py, src/simulation/engine.py, src/live/monitor_engine.py, src/setups/setup_scanner.py, configs/main.yaml
- **Dependências:** configs/main.yaml

## 🛠️ Especificações Técnicas
1. Definir chave canonica `model_directory` no YAML.
2. Atualizar leitura em todos os modulos para a chave canonica.
3. Manter fallback temporario para `models_directory` com warning (janela de migracao).
4. Remover fallback apos validacao do config atualizado.

## 🔗 Dependências & Bloqueios
- [ ] Validar impacto nos artefatos existentes em models/
- [ ] Coordenar com task 02 para compatibilidade do provider

## 📦 Definition of Done (DoD)
- [ ] Leitura unica da chave `model_directory`
- [ ] Sem uso de `models_directory` no codebase
- [ ] Configs atualizados
- [ ] Documentacao atualizada

## ✅ Verificacao
- [ ] Busca por `models_directory` nao retorna ocorrencias
- [ ] Carregamento de modelos funciona com `model_directory`

## 📊 Estimativa
- **Story Points:** 2
- **Horas:** 4h
- **Prioridade:** 🟡 MEDIA
