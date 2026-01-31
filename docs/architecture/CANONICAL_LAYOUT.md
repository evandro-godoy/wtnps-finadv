# Canonical Src Layout - wtnps-finadv

## Estrutura Adotada
- **src/**: Código fonte principal (imports como `from src.core.event_bus import EventBus`)
- **tests/**: Testes unitários e integração (imports como `from src.events import SignalEvent`)
- **docs/**: Documentação (planning, architecture, user)
- **models/**: Artefatos treinados (.keras, .joblib)
- **notebooks/**: Análises e testes jupyter
- **configs/**: YAML configs e .env
- **reports/**: Saídas de análise

## Benefícios
1. **Isolamento**: Testes não importam código não-packaged
2. **Instalação**: `pip install -e .` funciona corretamente
3. **CI/CD**: Workflows sabem onde procurar
4. **Escalabilidade**: Fácil adicionar novos packages

## Referência
https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/
