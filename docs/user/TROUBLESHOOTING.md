# TROUBLESHOOTING GUIDE - WTNPS Trade

## Common Issues and Solutions

### MT5 Connection Issues

#### Problem: `mt5.initialize() returned False`

**Possible Causes:**
1. MT5 terminal is not running
2. MT5 terminal is not logged in
3. Incorrect MT5_PATH in .env
4. Firewall blocking connection

**Solutions:**

1. **Check if MT5 is running:**
   ```powershell
   Get-Process -Name "terminal64" -ErrorAction SilentlyContinue
   ```
   If not running, start MetaTrader 5 terminal manually

2. **Verify MT5 login:**
   - Open MT5 terminal
   - Check if account is logged in (top-left corner should show account number)
   - If not logged in, go to File → Login to Trade Account

3. **Verify MT5_PATH:**
   ```powershell
   # Check your .env file
   Get-Content .env | Select-String "MT5_PATH"
   
   # Default path
   Test-Path "C:\Program Files\MetaTrader 5\terminal64.exe"
   ```

4. **Run environment validation:**
   ```powershell
   poetry run python scripts/validate_environment.py
   ```

---

#### Problem: `Symbol 'WDO$' not available`

**Possible Causes:**
1. Symbol not in Market Watch
2. Incorrect symbol name for your broker

**Solutions:**

1. **Add symbol to Market Watch:**
   - Open MT5 terminal
   - Press Ctrl+U (Market Watch)
   - Right-click → Symbols → Find "WDO" or "WIN"
   - Select symbol → Show

2. **Check symbol name:**
   - Different brokers may use different symbol names
   - Common alternatives: "WDOZ24", "WDOX25", "WDO-USD"
   - Update `ticker` in configs/main.yaml

3. **List available symbols:**
   ```python
   import MetaTrader5 as mt5
   mt5.initialize()
   symbols = mt5.symbols_get()
   for s in symbols[:20]:  # First 20 symbols
       print(s.name)
   ```

---

### Model Loading Errors

#### Problem: `FileNotFoundError: models/WDO$_LSTMVolatilityStrategy_M5_prod_lstm.keras`

**Cause:** Model files not trained/generated

**Solution:**

1. **Train models:**
   ```powershell
   poetry run python train_model.py
   ```

2. **Verify model artifacts exist:**
   ```powershell
   ls models/*.keras
   ls models/*.joblib
   ```

3. **Expected files for each ticker:**
   - `{TICKER}_LSTMVolatilityStrategy_M5_prod_lstm.keras`
   - `{TICKER}_LSTMVolatilityStrategy_M5_prod_scaler.joblib`
   - `{TICKER}_LSTMVolatilityStrategy_M5_prod_params.joblib`

---

#### Problem: `ValueError: X has N features, but scaler expects M`

**Cause:** Feature mismatch between training and inference

**Solutions:**

1. **Retrain model with current strategy definition:**
   ```powershell
   poetry run python train_model.py
   ```

2. **Verify feature consistency:**
   ```powershell
   poetry run pytest tests/unit/test_lstm_inference.py::TestLSTMInference::test_feature_consistency -v
   ```

3. **Check strategy features:**
   ```python
   from src.strategies.lstm_volatility import LSTMVolatilityStrategy
   strategy = LSTMVolatilityStrategy()
   print(strategy.get_feature_names())
   # Should match scaler.n_features_in_
   ```

---

### WebSocket Connection Failed

#### Problem: Browser cannot connect to `ws://localhost:8000/ws/live-signals`

**Possible Causes:**
1. FastAPI server not running
2. Port 8000 already in use
3. CORS issues
4. Firewall blocking connection

**Solutions:**

1. **Check if FastAPI is running:**
   ```powershell
   # Test API endpoint
   Invoke-WebRequest -Uri "http://localhost:8000/health"
   ```

2. **Start API server:**
   ```powershell
   poetry run uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Check port availability:**
   ```powershell
   # Find process using port 8000
   Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
   
   # Kill process if needed
   Stop-Process -Id <PID>
   ```

4. **Test WebSocket from browser console:**
   ```javascript
   const ws = new WebSocket('ws://localhost:8000/ws/live-signals');
   ws.onopen = () => console.log('Connected');
   ws.onerror = (e) => console.error('Error:', e);
   ws.onmessage = (e) => console.log('Message:', e.data);
   ```

5. **Check browser network tab:**
   - Open DevTools (F12)
   - Go to Network tab → WS filter
   - Look for connection attempts and errors

---

### Performance Issues

#### Problem: Inference taking >100ms per candle

**Possible Causes:**
1. GPU not being used by TensorFlow
2. Too many features
3. Large lookback window

**Solutions:**

1. **Check TensorFlow GPU usage:**
   ```python
   import tensorflow as tf
   print("GPU Available:", tf.config.list_physical_devices('GPU'))
   ```

2. **Profile inference time:**
   ```powershell
   poetry run pytest tests/unit/test_lstm_inference.py::TestLSTMInference::test_inference_performance -v -s
   ```

3. **Reduce model complexity (if needed):**
   - Decrease `lookback` parameter (default: 96)
   - Reduce number of features in `define_features()`
   - Use smaller `lstm_units` (default: 64)

---

#### Problem: Memory usage >500MB

**Possible Causes:**
1. Buffer size too large
2. Memory leak in monitoring loop
3. Too many candles stored

**Solutions:**

1. **Run memory profiling:**
   ```powershell
   poetry run python scripts/dry_run.py --duration 10
   # Check max memory in report
   ```

2. **Reduce buffer size:**
   - In MonitorEngine: `buffer_size=500` → `buffer_size=300`

3. **Check for memory leaks:**
   ```python
   import tracemalloc
   tracemalloc.start()
   # Run monitoring
   # ...
   snapshot = tracemalloc.take_snapshot()
   top_stats = snapshot.statistics('lineno')
   for stat in top_stats[:10]:
       print(stat)
   ```

---

### Data Issues

#### Problem: Empty DataFrame returned by provider

**Possible Causes:**
1. Date range outside available data
2. Market closed (no data for recent dates)
3. Ticker not available for provider

**Solutions:**

1. **Check date range:**
   ```python
   from datetime import datetime, timedelta
   from src.data_handler.provider import MetaTraderProvider
   
   provider = MetaTraderProvider()
   start = datetime.now() - timedelta(days=30)
   end = datetime.now()
   
   data = provider.get_data("WDO$", start, end, "M5")
   print(f"Rows: {len(data)}")
   print(f"Date range: {data.index[0]} to {data.index[-1]}")
   ```

2. **Verify market hours:**
   - Brazilian futures: Mon-Fri 9:00-18:00 BRT
   - Check if current time is within trading hours

3. **Use cached data for testing:**
   ```powershell
   # Check cache
   ls .cache_data/*.parquet
   ```

---

### Configuration Issues

#### Problem: `FileNotFoundError: configs/main.yaml`

**Solution:**

1. **Create config from example:**
   ```powershell
   Copy-Item configs/main.yaml.example configs/main.yaml
   ```

2. **Verify config structure:**
   ```powershell
   poetry run python test_config.py
   ```

---

#### Problem: `KeyError: 'global_settings'` or `'model_directory'`

**Cause:** Legacy config format

**Solution:**

Update configs/main.yaml to include:
```yaml
global_settings:
  model_directory: "models"  # Not models_directory!
```

---

## Diagnostic Commands

### Quick Health Check
```powershell
# 1. Validate environment
poetry run python scripts/validate_environment.py

# 2. Run LSTM tests
poetry run pytest tests/unit/test_lstm_inference.py -v

# 3. Dry-run for 5 minutes
poetry run python scripts/dry_run.py --ticker WDO$ --duration 5
```

### Check Logs
```powershell
# Live signal logs (JSON Lines)
Get-Content logs/live_signals_20260202.jsonl | Select-Object -Last 10

# CSV report
Import-Csv reports/live_signals/signals_20260202.csv | Select-Object -Last 10

# Dry-run logs
Get-Content reports/dry_run_*.log | Select-Object -Last 50
```

### Test API Endpoints
```powershell
# Health check
Invoke-WebRequest -Uri "http://localhost:8000/health"

# Get status
Invoke-WebRequest -Uri "http://localhost:8000/api/status"

# Get latest signals
Invoke-WebRequest -Uri "http://localhost:8000/api/signals/latest?limit=10"
```

---

## Getting Help

If issues persist after trying solutions above:

1. **Check logs:**
   - `logs/live_signals_*.jsonl` - Signal generation logs
   - `reports/dry_run_*.log` - Dry-run test logs
   - Console output for real-time errors

2. **Run validation:**
   ```powershell
   poetry run python scripts/validate_environment.py
   ```

3. **Create a GitHub issue** with:
   - Output of `validate_environment.py`
   - Relevant error messages from logs
   - Steps to reproduce the issue
   - Environment details (Windows version, Python version)

4. **Common log locations:**
   - Environment validation: `reports/environment_validation.json`
   - Dry-run reports: `reports/dry_run_*.log`
   - Signal logs: `logs/live_signals_*.jsonl`
   - CSV reports: `reports/live_signals/signals_*.csv`
