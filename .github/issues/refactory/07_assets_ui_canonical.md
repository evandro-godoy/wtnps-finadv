---
name: 07_assets_ui_canonical
about: Consolidar templates e static em layout canonico para a UI.
title: '[ARCH] Consolidar assets de UI no layout canonico'
labels: sprint-refactory, refactory, ui
assignees: 'Fullstack'
---

## 🎯 Objetivo
Alinhar templates e static files ao layout canonico para evitar caminhos alternativos.

## 📌 Status (2026-02-08)
**Estado:** Pendente.

**Evidencias (codigo):**
- API monta `TEMPLATES_DIR` e `STATIC_DIR` a partir da raiz (`/templates` e `/static`).
- Nao ha consolidacao para `src/interface/templates` + `src/interface/static` no runtime principal.

**Arquivos verificados:**
- src/api/main.py
- docs/architecture/PROJECT_ARCHITECT_HANDOVER.md
- docs/architecture/CANONICAL_LAYOUT.md

## 📂 Contexto & Arquivos
- **Alvo:** src/api/main.py, templates/, src/interface (se criado)
- **Dependências:** charts_clean.html, home.html, static assets
- **Decisao canonica:** mover templates/static para um unico local (ex.: src/interface/templates e src/interface/static).

## 🛠️ Especificações Técnicas
1. Definir local canonico para templates e static (ex.: src/interface/templates).
2. Mover assets do diretorio raiz para o local canonico.
3. Atualizar FastAPI para usar apenas o local canonico.
4. Remover logica de fallback para caminhos alternativos.

## 🧭 Escopo detalhado
- Consolidar templates e static no layout canonico indicado em docs.
- Atualizar FastAPI para apontar apenas ao local canonico.
- Remover duplicatas de templates/static na raiz.

## 🔧 Passos de implementacao
1. Definir o caminho canonico (ex.: `src/interface/templates` e `src/interface/static`).
2. Mover assets da raiz para o local canonico.
3. Atualizar `TEMPLATES_DIR`/`STATIC_DIR` na API para usar apenas o local canonico.
4. Remover fallbacks e caminhos alternativos.

## 🧪 Plano de verificacao
- Smoke test: `/` e `/charts` servem HTML e assets corretamente.
- Confirmar inexistencia de templates/static fora do local canonico.

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
