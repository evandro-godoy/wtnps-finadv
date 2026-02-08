---
name: 07_assets_ui_canonical
about: Consolidar templates e static em layout canonico para a UI.
title: '[ARCH] Consolidar assets de UI no layout canonico'
labels: sprint-refactory, refactory, ui
assignees: 'Fullstack'
---

## 🎯 Objetivo
Alinhar templates e static files ao layout canonico para evitar caminhos alternativos.

## 📂 Contexto & Arquivos
- **Alvo:** src/api/main.py, templates/, src/interface (se criado)
- **Dependências:** charts_clean.html, home.html, static assets
- **Decisao canonica:** mover templates/static para um unico local (ex.: src/interface/templates e src/interface/static).

## 🛠️ Especificações Técnicas
1. Definir local canonico para templates e static (ex.: src/interface/templates).
2. Mover assets do diretorio raiz para o local canonico.
3. Atualizar FastAPI para usar apenas o local canonico.
4. Remover logica de fallback para caminhos alternativos.

## 🔗 Dependências & Bloqueios
- [ ] Verificar referencia de templates na API e UI
- [ ] Alinhar com o layout canonico de docs/architecture

## 📦 Definition of Done (DoD)
- [ ] Templates e static em local unico
- [ ] API aponta apenas para local canonico
- [ ] Endpoints / e /charts servem HTML corretamente
- [ ] Documentacao atualizada

## ✅ Verificacao
- [ ] Smoke test: acessar / e /charts com assets carregando

## 📊 Estimativa
- **Story Points:** 3
- **Horas:** 6h
- **Prioridade:** 🟢 BAIXA
