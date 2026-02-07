# src/api/routes/chart_data.py
"""
Endpoint de dados para o gráfico da demo.

Retorna candles OHLCV + indicadores (SMA21, SMA200, EMA9) e, opcionalmente,
o sinal de inferência da LSTMVolatilityStrategy para o último candle.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import yaml
from fastapi import APIRouter, HTTPException, Query

from src.utils.indicators import add_demo_indicators

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Chart Data"])

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_CONFIG_PATH = Path(__file__).resolve().parents[3] / "configs" / "main.yaml"


def _load_yaml_config() -> dict:
    with open(_CONFIG_PATH, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _get_asset_config(config: dict, ticker: str) -> Optional[dict]:
    for asset in config.get("assets", []):
        if asset.get("ticker") == ticker:
            return asset
    return None


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Garante colunas lowercase (open, high, low, close, volume)."""
    col_map = {"Open": "open", "High": "high", "Low": "low",
               "Close": "close", "Volume": "volume"}
    if any(c in df.columns for c in col_map):
        df = df.rename(columns=col_map)
    return df


def _run_prediction(
    ticker: str,
    config: dict,
    asset_config: dict,
    df_features: pd.DataFrame,
) -> Optional[dict]:
    """
    Executa a predição da LSTMVolatilityStrategy sobre os dados já com features.

    Retorna dict com ai_signal, probability, etc. ou None em caso de falha.
    """
    from src.strategies.lstm_volatility import LSTMVolatilityStrategy, LSTMVolatilityWrapper

    # Busca config da estratégia
    strat_cfg = None
    for s in asset_config.get("strategies", []):
        if s.get("name") == "LSTMVolatilityStrategy":
            strat_cfg = s
            break

    if strat_cfg is None:
        logger.warning("LSTMVolatilityStrategy não encontrada no config para %s", ticker)
        return None

    params = strat_cfg.get("strategy_params", {})
    strategy = LSTMVolatilityStrategy(
        lookback=params.get("lookback", 108),
        lstm_units=params.get("lstm_units", 64),
        dropout_rate=params.get("dropout_rate", 0.2),
        epochs=params.get("epochs", 30),
        batch_size=params.get("batch_size", 128),
        target_period=params.get("target_period", 5),
        volatility_multiplier=params.get("volatility_multiplier", 3.0),
    )

    # Resolve caminho do modelo
    model_dir = config.get("global_settings", {}).get("model_directory", "models")
    model_dir_path = Path(model_dir)
    if not model_dir_path.is_absolute():
        project_root = Path(__file__).resolve().parents[3]
        model_dir_path = (project_root / model_dir_path).resolve()

    timeframe_model = strat_cfg.get("data", {}).get("timeframe_model", "M5")
    prefix = str(model_dir_path / f"{ticker}_LSTMVolatilityStrategy_{timeframe_model}_prod")

    try:
        model: LSTMVolatilityWrapper = LSTMVolatilityStrategy.load(prefix)
    except FileNotFoundError:
        logger.error("Modelo não encontrado: %s", prefix)
        return None
    except Exception as exc:
        logger.error("Erro ao carregar modelo: %s", exc)
        return None

    # Prepara input
    lookback = getattr(model, "lookback", params.get("lookback", 108))
    feature_names = strategy.get_feature_names()

    if len(df_features) < lookback + 10:
        logger.warning("Dados insuficientes para predição (%d < %d)", len(df_features), lookback)
        return None

    tail = df_features.tail(lookback + 20)
    missing = [f for f in feature_names if f not in tail.columns]
    if missing:
        logger.error("Features faltando para predição: %s", missing)
        return None

    X = tail[feature_names]
    if X.isnull().values.any():
        logger.warning("NaNs encontrados nas features — predição pode ser imprecisa.")

    try:
        proba = model.predict_proba(X)
        if proba is None or len(proba) == 0:
            return None
        prob_class1 = float(proba[-1, 1])
    except Exception as exc:
        logger.error("Erro na predição: %s", exc)
        return None

    # Determina sinal
    last_close = float(df_features["close"].iloc[-1])
    ema_20 = float(df_features["close"].ewm(span=20, adjust=False).mean().iloc[-1])
    direction = "CALL" if last_close > ema_20 else "PUT"

    if prob_class1 >= 0.5:
        ai_signal = "COMPRA" if direction == "CALL" else "VENDA"
    else:
        ai_signal = "HOLD"

    return {
        "ai_signal": ai_signal,
        "probability": round(prob_class1, 4),
        "direction": direction,
        "price": round(last_close, 2),
    }


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------


@router.get("/chart-data")
async def get_chart_data(
    ticker: str = Query(default=None, description="Ticker do ativo (default: primeiro habilitado do main.yaml)"),
    bars: int = Query(default=1000, ge=100, le=5000, description="Número de barras M5"),
):
    """
    Retorna candles OHLCV + indicadores demo para o gráfico.

    Response JSON::

        {
            "ticker": "WDO$",
            "timeframe": "M5",
            "bars": 1000,
            "candles": [
                {
                    "time": "2025-02-07T10:00:00",
                    "open": 5870.0,
                    "high": 5875.0,
                    "low": 5868.0,
                    "close": 5872.0,
                    "volume": 1234,
                    "sma_21": 5865.3,
                    "sma_200": 5810.1,
                    "ema_9": 5870.5
                },
                ...
            ],
            "prediction": {
                "ai_signal": "COMPRA",
                "probability": 0.7123,
                "direction": "CALL",
                "price": 5872.0
            }
        }
    """
    # 1 — Carrega config e resolve ticker
    try:
        config = _load_yaml_config()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao carregar configuração: {exc}")

    if ticker is None:
        # Usa o primeiro ativo habilitado
        for asset in config.get("assets", []):
            if asset.get("enabled", True):
                ticker = asset["ticker"]
                break
        if ticker is None:
            raise HTTPException(status_code=400, detail="Nenhum ativo habilitado no config.")

    asset_config = _get_asset_config(config, ticker)
    if asset_config is None:
        raise HTTPException(status_code=404, detail=f"Ativo '{ticker}' não encontrado no config.")

    # 2 — Busca dados do MT5
    try:
        from src.data_handler.mt5_provider import MetaTraderProvider as MT5Prov

        provider = MT5Prov()
        raw_df = provider.get_latest_candles(symbol=ticker, timeframe="M5", n=bars)
    except ConnectionError as exc:
        raise HTTPException(status_code=503, detail=f"MT5 não conectado: {exc}")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Erro ao buscar dados do MT5")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar dados: {exc}")

    if raw_df.empty:
        raise HTTPException(status_code=404, detail=f"Nenhum dado retornado para {ticker} M5.")

    # 3 — Normaliza colunas → lowercase
    df = _normalize_columns(raw_df.copy())

    # 4 — Calcula indicadores demo
    add_demo_indicators(df, close_col="close")

    # 5 — Executa predição da LSTMVolatilityStrategy
    #     (precisa de todas as features, então usamos define_features)
    prediction = None
    try:
        from src.strategies.lstm_volatility import LSTMVolatilityStrategy

        strat_cfg = None
        for s in asset_config.get("strategies", []):
            if s.get("name") == "LSTMVolatilityStrategy":
                strat_cfg = s
                break

        if strat_cfg:
            params = strat_cfg.get("strategy_params", {})
            strategy = LSTMVolatilityStrategy(**params)
            df_features = strategy.define_features(df.copy())
            prediction = _run_prediction(ticker, config, asset_config, df_features)
    except Exception as exc:
        logger.warning("Predição falhou (não-fatal): %s", exc)

    # 6 — Monta resposta JSON
    records = []
    for ts, row in df.iterrows():
        rec = {
            "time": ts.isoformat() if hasattr(ts, "isoformat") else str(ts),
            "open": _safe_float(row.get("open")),
            "high": _safe_float(row.get("high")),
            "low": _safe_float(row.get("low")),
            "close": _safe_float(row.get("close")),
            "volume": int(row.get("volume", 0)),
            "sma_21": _safe_float(row.get("sma_21")),
            "sma_200": _safe_float(row.get("sma_200")),
            "ema_9": _safe_float(row.get("ema_9")),
        }
        records.append(rec)

    return {
        "ticker": ticker,
        "timeframe": "M5",
        "bars": len(records),
        "candles": records,
        "prediction": prediction,
    }


def _safe_float(val) -> Optional[float]:
    """Converte para float, retornando None para NaN/inf."""
    if val is None:
        return None
    try:
        f = float(val)
        if np.isnan(f) or np.isinf(f):
            return None
        return round(f, 5)
    except (TypeError, ValueError):
        return None
