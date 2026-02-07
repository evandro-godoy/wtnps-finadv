"""Tests for LSTMVolatilityAdapter event handling and signal emission."""

from datetime import datetime, timedelta

import numpy as np
from sklearn.preprocessing import MinMaxScaler

from src.events import MarketDataEvent, SignalEvent
from src.modules.strategy.lstm_adapter import LSTMVolatilityAdapter
from src.strategies.lstm_volatility import LSTMVolatilityStrategy


class DummyEventBus:
    def __init__(self):
        self.events = []

    def publish(self, event):
        self.events.append(event)


class DummyModel:
    def __init__(self, lookback: int, n_features: int):
        self.input_shape = (None, lookback, n_features)

    def predict(self, X, verbose=0):
        return np.array([[0.1, 0.9]], dtype=np.float32)


def _make_event(index: int, base_time: datetime) -> MarketDataEvent:
    price = 100.0 + index * 0.1
    return MarketDataEvent(
        symbol="WDO$",
        timeframe="M5",
        open=price - 0.05,
        high=price + 0.1,
        low=price - 0.1,
        close=price,
        volume=1000 + index,
        timestamp=base_time + timedelta(minutes=5 * index)
    )


def test_adapter_emits_signal_with_synthetic_events():
    strategy = LSTMVolatilityStrategy()
    n_features = len(strategy.get_feature_names())

    event_bus = DummyEventBus()
    adapter = LSTMVolatilityAdapter(event_bus=event_bus, lookback=20)

    adapter.model = DummyModel(adapter.lookback, n_features)

    scaler = MinMaxScaler()
    scaler.fit(np.random.rand(300, n_features))
    adapter.scaler = scaler

    base_time = datetime.utcnow()
    for i in range(210):
        adapter.on_market_data(_make_event(i, base_time))

    assert adapter.processed_count == 210
    assert adapter.buffer.shape[0] >= adapter.lookback
    assert len(event_bus.events) >= 1
    assert isinstance(event_bus.events[-1], SignalEvent)
