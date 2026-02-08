---
name: 07_assets_ui_canonical
about: Template for Sprint 2 Integration tasks
title: '[ARCH] Consolidar assets de UI no layout canonico'
labels: sprint-2, integration
assignees: ''
---

## 🎯 Objetivo
Alinhar templates e static files ao layout canonico para evitar caminhos alternativos.

## 📂 Contexto & Arquivos
- **Alvo:** src/api/main.py, templates/, src/interface (se criado)
- **Dependências:** charts_clean.html, home.html, static assets

## 🛠️ Especificações Técnicas
1. Definir local canonico para templates e static (ex.: src/interface/templates).
2. Atualizar FastAPI para usar apenas o local canonico.
3. Remover logica de fallback para caminhos alternativos.

## 🔗 Dependências & Bloqueios
- [ ] Verificar referencia de templates na API e UI

## 📦 Definition of Done (DoD)
- [ ] Templates e static em local unico
- [ ] API aponta apenas para local canonico
- [ ] Documentacao atualizada

## 📊 Estimativa
- **Story Points:** 3
- **Horas:** 6h
- **Prioridade:** 🟢 BAIXA
