"""Unit tests for BacktestEngine day-trade logic and schema validation."""

from typing import Dict, List

import numpy as np
import pandas as pd
import pytest

from src.backtest_engine.backtest_lstm_volatility import BacktestEngine


def _utc_index(timestamps: List[str]) -> pd.DatetimeIndex:
    """Create a UTC DatetimeIndex from ISO timestamp strings."""
    return pd.DatetimeIndex(timestamps, tz="UTC")


def _build_prices(
    index: pd.DatetimeIndex,
    rows: List[Dict[str, float]],
) -> pd.DataFrame:
    """Build an OHLCV DataFrame with canonical columns."""
    frame = pd.DataFrame(rows, index=index)
    return frame[["Open", "High", "Low", "Close", "Volume"]]


def test_stop_priority_over_take_profit() -> None:
    """Stop loss exits take priority over take profit."""
    engine = BacktestEngine()
    index = _utc_index(
        ["2024-01-01 10:00", "2024-01-01 10:05"]
    )
    prices = _build_prices(
        index,
        [
            {
                "Open": 100.0,
                "High": 100.0,
                "Low": 100.0,
                "Close": 100.0,
                "Volume": 1.0,
            },
            {
                "Open": 100.0,
                "High": 102.0,
                "Low": 98.0,
                "Close": 100.0,
                "Volume": 1.0,
            },
        ],
    )
    signals = np.array([1, 0], dtype=int)

    results = engine._simulate_daytrade_positions(
        signals=signals,
        prices=prices,
        stop_loss_pct=0.01,
        take_profit_pct=0.01,
    )

    assert results["full_trades"][0]["exit_reason"] == "STOP"


def test_take_profit_exit() -> None:
    """Take profit exits when the high reaches the target."""
    engine = BacktestEngine()
    index = _utc_index(
        ["2024-01-01 10:00", "2024-01-01 10:05"]
    )
    prices = _build_prices(
        index,
        [
            {
                "Open": 100.0,
                "High": 100.0,
                "Low": 100.0,
                "Close": 100.0,
                "Volume": 1.0,
            },
            {
                "Open": 100.0,
                "High": 101.5,
                "Low": 99.5,
                "Close": 101.0,
                "Volume": 1.0,
            },
        ],
    )
    signals = np.array([1, 0], dtype=int)

    results = engine._simulate_daytrade_positions(
        signals=signals,
        prices=prices,
        stop_loss_pct=0.01,
        take_profit_pct=0.01,
    )

    assert results["full_trades"][0]["exit_reason"] == "TAKE_PROFIT"


def test_market_close_exit() -> None:
    """Market close forces exit at or after the close hour."""
    engine = BacktestEngine()
    index = _utc_index(
        ["2024-01-01 16:55", "2024-01-01 17:00"]
    )
    prices = _build_prices(
        index,
        [
            {
                "Open": 100.0,
                "High": 100.0,
                "Low": 100.0,
                "Close": 100.0,
                "Volume": 1.0,
            },
            {
                "Open": 100.0,
                "High": 100.5,
                "Low": 99.5,
                "Close": 100.2,
                "Volume": 1.0,
            },
        ],
    )
    signals = np.array([1, 0], dtype=int)

    results = engine._simulate_daytrade_positions(
        signals=signals,
        prices=prices,
        stop_loss_pct=0.01,
        market_close_hour=17,
    )

    assert results["full_trades"][0]["exit_reason"] == "MARKET_CLOSE"


def test_overnight_force_exit() -> None:
    """Overnight force closes at the last candle of the prior day."""
    engine = BacktestEngine()
    index = _utc_index(
        ["2024-01-01 16:55", "2024-01-02 00:05"]
    )
    prices = _build_prices(
        index,
        [
            {
                "Open": 100.0,
                "High": 100.0,
                "Low": 100.0,
                "Close": 100.0,
                "Volume": 1.0,
            },
            {
                "Open": 100.0,
                "High": 100.5,
                "Low": 99.5,
                "Close": 100.2,
                "Volume": 1.0,
            },
        ],
    )
    signals = np.array([1, 0], dtype=int)

    results = engine._simulate_daytrade_positions(
        signals=signals,
        prices=prices,
        stop_loss_pct=0.01,
        market_close_hour=17,
    )

    assert results["full_trades"][0]["exit_reason"] == "OVERNIGHT_FORCE"


def test_max_holding_exit() -> None:
    """Max holding triggers exit after the configured candle count."""
    engine = BacktestEngine()
    index = _utc_index(
        ["2024-01-01 10:00", "2024-01-01 10:05"]
    )
    prices = _build_prices(
        index,
        [
            {
                "Open": 100.0,
                "High": 100.0,
                "Low": 100.0,
                "Close": 100.0,
                "Volume": 1.0,
            },
            {
                "Open": 100.0,
                "High": 100.5,
                "Low": 99.5,
                "Close": 100.2,
                "Volume": 1.0,
            },
        ],
    )
    signals = np.array([1, 0], dtype=int)

    results = engine._simulate_daytrade_positions(
        signals=signals,
        prices=prices,
        max_holding_candles=2,
    )

    assert results["full_trades"][0]["exit_reason"] == "MAX_HOLDING"


def test_data_end_exit() -> None:
    """Data end closes any remaining open position."""
    engine = BacktestEngine()
    index = _utc_index(["2024-01-01 10:00"])
    prices = _build_prices(
        index,
        [
            {
                "Open": 100.0,
                "High": 100.0,
                "Low": 100.0,
                "Close": 100.0,
                "Volume": 1.0,
            }
        ],
    )
    signals = np.array([1], dtype=int)

    results = engine._simulate_daytrade_positions(
        signals=signals,
        prices=prices,
    )

    assert results["full_trades"][0]["exit_reason"] == "DATA_END"


def test_schema_validation_missing_columns() -> None:
    """Missing canonical columns raises a clear error."""
    engine = BacktestEngine()
    index = _utc_index(["2024-01-01 10:00"])
    prices = pd.DataFrame(
        [{"Open": 100.0, "High": 101.0, "Low": 99.0, "Volume": 1.0}],
        index=index,
    )
    signals = np.array([0], dtype=int)

    with pytest.raises(ValueError, match="missing required columns"):
        engine._simulate_daytrade_positions(
            signals=signals,
            prices=prices,
        )


def test_schema_validation_empty_prices() -> None:
    """Empty price data raises a clear error."""
    engine = BacktestEngine()
    empty_index = pd.DatetimeIndex([], tz="UTC")
    prices = pd.DataFrame(
        columns=["Open", "High", "Low", "Close", "Volume"],
        index=empty_index,
    )
    signals = np.array([], dtype=int)

    with pytest.raises(ValueError, match="prices is empty"):
        engine._simulate_daytrade_positions(
            signals=signals,
            prices=prices,
        )


def test_run_backtest_empty_prices() -> None:
    """Run backtest fails fast when prices are empty."""
    engine = BacktestEngine()
    empty_index = pd.DatetimeIndex([], tz="UTC")
    prices = pd.DataFrame(
        columns=["Open", "High", "Low", "Close", "Volume"],
        index=empty_index,
    )

    with pytest.raises(ValueError, match="prices is empty"):
        engine.run_backtest(
            ticker="TEST",
            predictions=np.array([]),
            probabilities=np.array([]),
            actual_targets=np.array([]),
            prices=prices,
        )
