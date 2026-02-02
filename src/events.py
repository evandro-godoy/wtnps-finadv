"""Módulo de definição de eventos do sistema."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional
import pandas as pd


@dataclass
class BaseEvent:
    """Classe base para todos os eventos do sistema."""
    event_type: str
    timestamp: datetime


@dataclass
class MarketDataEvent(BaseEvent):
    """Evento de dados de mercado (OHLCV)."""
    symbol: str
    timeframe: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    
    def __init__(self, symbol: str, timeframe: str, open: float, high: float, 
                 low: float, close: float, volume: float, timestamp: Optional[datetime] = None):
        self.symbol = symbol
        self.timeframe = timeframe
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.timestamp = timestamp or datetime.now()
        self.event_type = "MARKET_DATA"


@dataclass
class SignalEvent(BaseEvent):
    """Evento de sinal de trading."""
    symbol: str
    signal: str  # COMPRA, VENDA, HOLD
    confidence: float
    price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __init__(self, symbol: str, signal: str, confidence: float, price: float,
                 stop_loss: Optional[float] = None, take_profit: Optional[float] = None,
                 metadata: Optional[Dict[str, Any]] = None, timestamp: Optional[datetime] = None):
        self.symbol = symbol
        self.signal = signal
        self.confidence = confidence
        self.price = price
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.metadata = metadata or {}
        self.timestamp = timestamp or datetime.now()
        self.event_type = "SIGNAL"


@dataclass
class OrderEvent(BaseEvent):
    """Evento de ordem de execução."""
    symbol: str
    order_type: str  # MARKET, LIMIT
    side: str  # BUY, SELL
    quantity: float
    price: Optional[float] = None
    
    def __init__(self, symbol: str, order_type: str, side: str, quantity: float,
                 price: Optional[float] = None, timestamp: Optional[datetime] = None):
        self.symbol = symbol
        self.order_type = order_type
        self.side = side
        self.quantity = quantity
        self.price = price
        self.timestamp = timestamp or datetime.now()
        self.event_type = "ORDER"


@dataclass
class InferenceSignalEvent(BaseEvent):
    """Evento de sinal de inferência ML (sem execução de ordem).
    
    Usado para monitoramento analítico e visualização em tempo real.
    Contém predição do modelo, probabilidade e indicadores técnicos.
    """
    ticker: str
    ai_signal: str  # COMPRA, VENDA, HOLD
    probability: float  # 0.0 - 1.0
    price: float
    indicators: Dict[str, Any]  # ATR, EMAs, RSI, etc
    timeframe: Optional[str] = None
    
    def __init__(self, ticker: str, ai_signal: str, probability: float, price: float,
                 indicators: Dict[str, Any], timeframe: Optional[str] = None,
                 timestamp: Optional[datetime] = None):
        self.ticker = ticker
        self.ai_signal = ai_signal
        self.probability = probability
        self.price = price
        self.indicators = indicators
        self.timeframe = timeframe
        self.timestamp = timestamp or datetime.now()
        self.event_type = "INFERENCE_SIGNAL"
