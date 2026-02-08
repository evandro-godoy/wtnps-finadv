# Copilot Instructions for WTNPS FinAdv

## Big Picture
- Config-driven trading system; `configs/main.yaml` is the source of truth for assets, strategies, setup rules, backtesting, and live trading.
- Two execution engines share the same AI + setup decision flow: SimulationEngine and LiveTrader.
- Strategy plugins live under `src/strategies/` and are dynamically loaded by module/class name.
- Real-time monitor and GUI are separate from LiveTrader (see `src/live/README.md` and `src/gui/README.md`).

## Architecture Patterns (examples)
- Strategy interface: `BaseStrategy` in `src/strategies/base.py` with `define_features()`, `define_target()`, `define_model()`, `get_feature_names()`, `save()/load()`.
- AI + setup gating: `SetupAnalyzer.evaluate_setups()` in `src/setups/analyzer.py` validates rules after AI signal.
- Engine entry points: `src/simulation/engine.py` (simulation/backtest) and `src/live_trader.py` (live trading).
- Data providers: `src/data_handler/provider.py` with `MetaTraderProvider` and `YFinanceProvider`, plus `.cache_data/` parquet caching.

## Project-Specific Conventions
- AI signals are uppercase Portuguese: `COMPRA`, `VENDA`, `HOLD`.
- Timeframes are limited to `M1, M5, M15, M30, H1, H4, D1, W1, MN1` and are mapped in engine/provider helpers.
- Model artifacts use prefix `{TICKER}_{STRATEGY}_{TIMEFRAME}_prod_` (e.g., models/WDO$_LSTMVolatilityStrategy_M5_prod_lstm.keras).
- YAML key is `model_directory` (legacy code may read `models_directory` with fallback).

## Developer Workflows (from README)
- Install: `poetry install` (requires MT5 terminal for live data).
- Train supervised models: `poetry run python train_model.py`.
- Train DRL: `poetry run python train_drl_model.py`.
- Run live trading: `poetry run python src/live_trader.py`.
- Run GUI monitor: `poetry run python run_monitor_gui.py --mode live`.
- Tests: `poetry run pytest tests/ -v` (integration tests need MT5 running).

## Integration Points
- MetaTrader 5 must be initialized and logged in before fetching data or placing orders.
- Live trading uses `ticker_order` for order routing and `ticker` for historical data in config.
- TensorFlow/Keras models (`.keras`) and scikit-learn scalers (`.joblib`) are loaded by strategies.

## Codebase Boundaries
- Active code is under `src/`, configs in `configs/`, models in `models/`, reports in `reports/`.
- Ignore deprecated code under `archive/`, `bkp/`, and `*old*` paths when giving examples.
