"""Signal-related API routes."""

from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/signals", tags=["Signals"])


class SignalResponse(BaseModel):
    """Signal data response model."""
    ticker: str
    timestamp: str
    ai_signal: str
    probability: float
    price: float
    indicators: dict
    timeframe: str


# This module can be extended with additional signal-related endpoints
# Currently, signal endpoints are in main.py for simplicity
