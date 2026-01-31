# MT5 Configuration & Provider - Guia de Implementação

## 📋 Resumo das Alterações

### 1. **src/core/config.py** - Configurações Robustas
- ✅ Adicionado `MT5Settings` class para validar configurações do MT5
- ✅ Suporte a variáveis de ambiente via `.env` usando `pydantic-settings`
- ✅ Três modos de operação:
  - **Terminal Aberto** (padrão, recomendado): Deixar `MT5_LOGIN`, `MT5_PASSWORD` vazios
  - **Com Autenticação**: Fornecer `MT5_LOGIN`, `MT5_PASSWORD`, `MT5_SERVER`
  - **Customizado**: Editar `.env` para seus valores

**Configurações disponíveis:**
```bash
MT5_PATH=C:\Program Files\MetaTrader 5\terminal64.exe
MT5_LOGIN=                    # Deixar vazio para terminal aberto
MT5_PASSWORD=                 # Deixar vazio para terminal aberto
MT5_SERVER=                   # Deixar vazio para usar padrão
MT5_TIMEOUT=5000              # em ms
```

**Métodos de acesso:**
```python
from src.core.config import settings

# Obter config como dicionário
mt5_config = settings.get_mt5_config()

# Verificar se requer autenticação
if settings.mt5_needs_auth():
    print("Usando credenciais")
else:
    print("Usando terminal aberto")
```

---

### 2. **src/data_handler/mt5_provider.py** - Provider Melhorado
- ✅ Integração com `settings` para carregar configurações
- ✅ Suporte a autenticação opcional
- ✅ Singleton pattern para evitar múltiplas conexões
- ✅ Logging detalhado com emojis para melhor visualização
- ✅ Tratamento robusto de erros

**Uso básico:**
```python
from src.data_handler.mt5_provider import MetaTraderProvider

# Inicializar (usa .env automaticamente)
provider = MetaTraderProvider()

# Buscar candles
df = provider.get_latest_candles('WDO$', 'M5', n=100)

# Limpar conexão
provider.shutdown()
```

**Métodos principais:**
- `get_latest_candles(symbol, timeframe, n)` → DataFrame com OHLCV
- `get_latest_candles_as_events(symbol, timeframe, n)` → Lista de MarketDataEvent
- `publish_to_eventbus(symbol, timeframe, n)` → Publica eventos no EventBus
- `shutdown()` → Encerra conexão MT5

---

### 3. **.env** - Arquivo de Configuração
Arquivo criado automaticamente com defaults seguros.

**Variedades de uso:**

#### Opção A: Terminal Aberto (Recomendado para Dev)
```bash
MT5_PATH=C:\Program Files\MetaTrader 5\terminal64.exe
MT5_LOGIN=
MT5_PASSWORD=
MT5_SERVER=
MT5_TIMEOUT=5000
```
✅ Mais rápido
✅ Sem senha em texto
✅ Requer apenas terminal aberto

#### Opção B: Com Credenciais
```bash
MT5_PATH=C:\Program Files\MetaTrader 5\terminal64.exe
MT5_LOGIN=123456
MT5_PASSWORD=MinhaSeha123
MT5_SERVER=MyBrokerServer
MT5_TIMEOUT=5000
```
✅ Automático
⚠️ Requer segurança do .env (nunca commit)

---

## 🧪 Teste de Configuração

Execute para validar:
```bash
poetry run python test_config.py
```

Saída esperada:
```
✅ TESTE DE CONFIGURAÇÃO CONCLUÍDO
   MT5 requer autenticação: False
   ✅ Usando modo terminal aberto
   ✅ MetaTraderProvider importado com sucesso
```

---

## 🚀 Próximos Passos

1. **Abrir Terminal MT5:**
   ```
   C:\Program Files\MetaTrader 5\terminal64.exe
   ```

2. **Testar Conexão:**
   ```bash
   poetry run python -c "
   from src.data_handler.mt5_provider import MetaTraderProvider
   p = MetaTraderProvider()
   print('✅ MT5 conectado!')
   "
   ```

3. **Testar Provider:**
   ```bash
   poetry run python -c "
   from src.data_handler.mt5_provider import MetaTraderProvider
   p = MetaTraderProvider()
   df = p.get_latest_candles('WDO\$', 'M5', n=10)
   print(df.head())
   "
   ```

---

## 📝 Hierarquia de Configuração

```
1. Variáveis de Ambiente (.env)     [Máxima Prioridade]
   ↓
2. Valores em MT5Settings
   ↓
3. Defaults em src/core/config.py   [Mínima Prioridade]
```

**Exemplo:**
- `.env` define `MT5_TIMEOUT=3000` → Usa 3000ms
- `.env` vazio → Usa default 5000ms
- Código pode sobrescrever via `settings.MT5.timeout = 2000`

---

## ⚠️ Segurança

- **Nunca commitar `.env`** com credenciais reais
- Usar `.env.example` como template
- Adicionar `.env` ao `.gitignore`
- Para produção: usar variáveis de ambiente do sistema

---

## 🔧 Troubleshooting

| Problema | Causa | Solução |
|----------|-------|--------|
| `ModuleNotFoundError: pydantic_settings` | Dependência não instalada | `poetry install` |
| `MT5 não está conectado` | Terminal não aberto | Abrir `terminal64.exe` |
| `FileNotFoundError` no MT5_PATH | Caminho incorreto | Editar `.env` com caminho correto |
| `Login inválido` | Credenciais erradas | Verificar `MT5_LOGIN` e `MT5_PASSWORD` |

---

## 📚 Referências

- **Config System:** `src/core/config.py`
- **MT5 Provider:** `src/data_handler/mt5_provider.py`
- **Test Script:** `test_config.py`
- **Pydantic Settings:** https://docs.pydantic.dev/latest/concepts/pydantic_settings/
