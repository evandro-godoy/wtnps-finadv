# Migration Guide: wtnps-trade → wtnps-finadv

## Histórico
- **wtnps-trade**: Desenvolvimento iterativo (Sprint 1-3)
- **wtnps-finadv**: Repositório oficial final (Canonical Layout)

## Documentação Movida
- Sprint plans → `docs/planning/`
- User guides → `docs/user/`
- Architecture specs → `docs/architecture/`

## Código Movido
- `src/` inteiro copiado preservando estrutura
- `tests/` inteiro copiado
- `models/` com artefatos treinados
- Scripts soltos (train_model.py, etc) mantidos em wtnps-trade como histórico

## Dependências Resolvidas
- `pyproject.toml` com Python ^3.12
- `poetry.lock` com todas as transitive dependencies

## Status
- [x] Infrastructure setup
- [x] Documentation centralized
- [ ] Code migrated
- [ ] Dependencies resolved
- [ ] Tests passing (próximo: CI validation)
