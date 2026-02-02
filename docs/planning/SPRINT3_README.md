# Sprint 3: Live Inference & Monitoring Integration

## Quick Start Guide

### 1. Environment Validation

Antes de executar o sistema, valide seu ambiente:

```powershell
poetry run python scripts/validate_environment.py
```

**Checks realizados:**
- ✅ .env file e variáveis de ambiente
- ✅ MT5 installation e connection
- ✅ Model artifacts (WDO$, WIN$)
- ✅ Python dependencies

---

### 2. Start API Server

Inicie o servidor FastAPI com WebSocket:

```powershell
poetry run uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

**Endpoints disponíveis:**
- `http://localhost:8000/` - Frontend HTML (charts_clean.html)
- `http://localhost:8000/docs` - API documentation (Swagger UI)
- `http://localhost:8000/health` - Health check
- `http://localhost:8000/api/status` - Monitor engine status
- `http://localhost:8000/api/signals/latest` - Latest signals (REST)
- `ws://localhost:8000/ws/live-signals` - Real-time signals (WebSocket)

---

### 3. Start Monitor Engine

**Opção A: Via API (Recommended)**

```powershell
# Start via POST request
Invoke-WebRequest -Uri "http://localhost:8000/api/monitor/start?ticker=WDO$&timeframe=M5" -Method POST
```

**Opção B: Direct Execution (for testing)**

```python
from src.live.monitor_engine import RealTimeMonitor

monitor = RealTimeMonitor(ticker="WDO$", timeframe_str="M5")
monitor.run()
```

---

### 4. Access Frontend

Abra o navegador em:

```
http://localhost:8000/
```

**Features:**
- 📈 Candlestick chart em tempo real (Plotly.js)
- 🎯 Último sinal com probabilidade e indicadores
- 📊 Histórico de sinais (últimos 10)
- ℹ️ Estatísticas (candles, sinais, uptime)
- 🔌 Status de conexão WebSocket

---

### 5. Run Dry-Run Test

Teste o sistema por 5 minutos:

```powershell
poetry run python scripts/dry_run.py --ticker WDO$ --duration 5
```

**Métricas coletadas:**
- Sinais gerados
- Exceções (deve ser 0)
- Uso de memória (target: <500MB)
- Tempo de execução

**Report gerado em:** `reports/dry_run_{timestamp}.log`

---

## Workflow Completo

```
┌─────────────────┐
│  MT5 Terminal   │ (Dados em tempo real)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ MonitorEngine   │ (Inferência LSTM)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   EventBus      │ (Publish InferenceSignalEvent)
└────────┬────────┘
         │
    ┌────┴────┬──────────┐
    ▼         ▼          ▼
┌────────┐ ┌────────┐ ┌──────────┐
│ Logger │ │CSV File│ │APIServer │ (WebSocket)
└────────┘ └────────┘ └────┬─────┘
                           │
                           ▼
                    ┌──────────────┐
                    │charts_clean  │ (Browser)
                    └──────────────┘
```

---

## Logs & Reports

### Signal Logs (JSON Lines)
```powershell
# View latest signals
Get-Content logs/live_signals_20260202.jsonl | Select-Object -Last 10
```

**Formato:**
```json
{
  "timestamp": "2026-02-02T14:35:00Z",
  "ticker": "WDO$",
  "timeframe": "M5",
  "ai_signal": "COMPRA",
  "probability": 0.78,
  "price": 125850,
  "indicators": {
    "atr": 450.5,
    "ema_9": 125800,
    "rsi": 62.3,
    "trend": "ALTA"
  }
}
```

### CSV Reports
```powershell
# Import and analyze
Import-Csv reports/live_signals/signals_20260202.csv | 
  Where-Object { $_.ai_signal -ne "HOLD" } | 
  Select-Object timestamp, ai_signal, probability, price
```

---

## Testing

### Run LSTM Tests
```powershell
# Full test suite
poetry run pytest tests/unit/test_lstm_inference.py -v

# Specific tests
poetry run pytest tests/unit/test_lstm_inference.py::TestLSTMInference::test_model_loading -v
poetry run pytest tests/unit/test_lstm_inference.py::TestLSTMInference::test_inference_performance -v
```

### Test WebSocket Connection (Browser Console)
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/live-signals');

ws.onopen = () => console.log('✅ Connected');
ws.onerror = (e) => console.error('❌ Error:', e);
ws.onmessage = (e) => {
  const data = JSON.parse(e.data);
  console.log('📊 Signal:', data);
};
```

---

## Troubleshooting

### MT5 Connection Issues

**Error:** `mt5.initialize() returned False`

**Solution:**
1. Verify MT5 terminal is running and logged in
2. Check `MT5_PATH` in `.env`
3. Run: `poetry run python scripts/validate_environment.py`

### Model Not Found

**Error:** `FileNotFoundError: models/WDO$_..._prod_lstm.keras`

**Solution:**
```powershell
# Train models first
poetry run python train_model.py
```

### WebSocket Connection Failed

**Error:** Browser console shows `WebSocket connection failed`

**Solution:**
1. Verify FastAPI is running: `http://localhost:8000/health`
2. Check CORS settings in `src/api/main.py`
3. Try different browser (Chrome recommended)

**More solutions:** See [docs/user/TROUBLESHOOTING.md](../user/TROUBLESHOOTING.md)

---

## Performance Targets

| Metric | Target | Validation |
|--------|--------|------------|
| LSTM Inference | <100ms | `pytest test_lstm_inference.py::test_inference_performance` |
| WebSocket Latency | <200ms | Browser DevTools Network tab |
| Memory Usage (500 candles) | <500MB | `python scripts/dry_run.py --duration 10` |
| API Response | <50ms | `Measure-Command { Invoke-WebRequest ... }` |

---

## Architecture Notes

### No Order Execution (Sprint 3 Scope)

⚠️ **IMPORTANTE:** Esta sprint NÃO inclui execução de ordens. O sistema é puramente analítico:

- ✅ Conexão MT5 (leitura de dados)
- ✅ Inferência LSTM
- ✅ Geração de sinais
- ✅ Visualização via WebSocket
- ❌ Envio de ordens (será Sprint 4)

### EventBus Pattern

Todos os sinais são publicados via `EventBus` para desacoplamento:

```python
# MonitorEngine publica
event = InferenceSignalEvent(...)
self.event_bus.publish(event)

# Subscribers recebem
def handle_signal(event: InferenceSignalEvent):
    # Process signal
    ...

event_bus.subscribe("INFERENCE_SIGNAL", handle_signal)
```

### Signal Cache

API mantém cache dos últimos 100 sinais em memória para endpoint REST `/api/signals/latest`.

---

## Next Steps (Sprint 4 - Future)

1. **Execution Engine** - MT5 order sending
2. **Setup Rules** - Integrate SetupAnalyzer
3. **Risk Management** - Position sizing, SL/TP
4. **Enhanced Frontend** - More indicators, filters
5. **Notifications** - Email, Telegram, SMS

---

## Documentation

- [SPRINT3_CHECKLIST.md](SPRINT3_CHECKLIST.md) - Detailed checklist
- [TROUBLESHOOTING.md](../user/TROUBLESHOOTING.md) - Common issues
- [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) - Full implementation plan
- [DRL_README.md](../user/DRL_README.md) - DRL training guide

---

**Sprint 3 Status:** ✅ COMPLETE  
**Date:** 02/02/2026  
**Issues:** 4/4 implemented  
**Tests:** PASS (100%)
