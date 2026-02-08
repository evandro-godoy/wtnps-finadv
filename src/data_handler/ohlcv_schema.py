"""Utilities for OHLCV schema standardization and validation."""

from __future__ import annotations

from typing import Iterable
import pandas as pd


OHLCV_COLUMNS = ["Open", "High", "Low", "Close", "Volume"]

_CANONICAL_COLUMN_MAP = {
    "open": "Open",
    "high": "High",
    "low": "Low",
    "close": "Close",
    "volume": "Volume",
    "tick_volume": "Volume",
    "real_volume": "Volume",
    "Open": "Open",
    "High": "High",
    "Low": "Low",
    "Close": "Close",
    "Volume": "Volume",
}


def standardize_ohlcv_schema(
    data: pd.DataFrame,
    *,
    source: str,
) -> pd.DataFrame:
    """
    Standardize a DataFrame to the canonical OHLCV schema.

    Args:
        data: Raw market data.
        source: Caller identifier for error messages.

    Returns:
        DataFrame with columns [Open, High, Low, Close, Volume] and UTC index.
    """
    if not isinstance(data, pd.DataFrame):
        raise TypeError(
            f"{source}: expected DataFrame, received {type(data)}"
        )

    data = data.copy()
    data = data.rename(columns=_CANONICAL_COLUMN_MAP)
    _ensure_required_columns(data.columns, source=source)

    if not isinstance(data.index, pd.DatetimeIndex):
        raise ValueError(
            f"{source}: expected DatetimeIndex, received {type(data.index)}"
        )

    if data.index.tz is None:
        data.index = data.index.tz_localize("UTC")
    else:
        data.index = data.index.tz_convert("UTC")

    data = data[OHLCV_COLUMNS]

    data["Open"] = data["Open"].astype(float)
    data["High"] = data["High"].astype(float)
    data["Low"] = data["Low"].astype(float)
    data["Close"] = data["Close"].astype(float)
    data["Volume"] = data["Volume"].fillna(0).astype("int64")

    return data


def validate_ohlcv_schema(
    data: pd.DataFrame,
    *,
    source: str,
) -> None:
    """
    Validate that the DataFrame matches the canonical OHLCV schema.

    Args:
        data: Market data to validate.
        source: Caller identifier for error messages.

    Raises:
        ValueError: If columns or index are not compliant.
    """
    if not isinstance(data, pd.DataFrame):
        raise TypeError(
            f"{source}: expected DataFrame, received {type(data)}"
        )

    _ensure_required_columns(data.columns, source=source)

    if not isinstance(data.index, pd.DatetimeIndex):
        raise ValueError(
            f"{source}: expected DatetimeIndex, received {type(data.index)}"
        )

    if data.index.tz is None:
        raise ValueError(f"{source}: DatetimeIndex must be UTC-aware")

    if str(data.index.tz) != "UTC":
        raise ValueError(
            f"{source}: DatetimeIndex must be UTC, received {data.index.tz}"
        )


def _ensure_required_columns(columns: Iterable[str], *, source: str) -> None:
    missing = [name for name in OHLCV_COLUMNS if name not in columns]
    if missing:
        raise ValueError(
            f"{source}: missing required columns {missing}"
        )
