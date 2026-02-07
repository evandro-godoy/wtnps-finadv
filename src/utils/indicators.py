# src/utils/indicators.py
"""
Funções utilitárias para cálculo de indicadores técnicos.

Fornece funções reutilizáveis para SMA, EMA e outros indicadores,
desacopladas das estratégias específicas.
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


def calculate_sma(series: pd.Series, period: int) -> pd.Series:
    """
    Calcula a Média Móvel Simples (SMA).

    Args:
        series: Série de preços (geralmente 'close').
        period: Número de períodos para a média.

    Returns:
        pd.Series com a SMA calculada.
    """
    if len(series) < period:
        logger.warning(
            f"Dados insuficientes para SMA({period}): {len(series)} barras disponíveis."
        )
    return series.rolling(window=period, min_periods=period).mean()


def calculate_ema(series: pd.Series, span: int) -> pd.Series:
    """
    Calcula a Média Móvel Exponencial (EMA).

    Args:
        series: Série de preços (geralmente 'close').
        span: Período (span) da EMA.

    Returns:
        pd.Series com a EMA calculada.
    """
    if len(series) < span:
        logger.warning(
            f"Dados insuficientes para EMA({span}): {len(series)} barras disponíveis."
        )
    return series.ewm(span=span, adjust=False).mean()


def add_demo_indicators(df: pd.DataFrame, close_col: str = "close") -> pd.DataFrame:
    """
    Adiciona os indicadores da demo (SMA21, SMA200, EMA9) ao DataFrame.

    Modifica o DataFrame *in-place* e também o retorna por conveniência.

    Args:
        df: DataFrame com pelo menos a coluna de fechamento.
        close_col: Nome da coluna de preço de fechamento.

    Returns:
        O mesmo DataFrame com colunas ``sma_21``, ``sma_200`` e ``ema_9``.
    """
    df["sma_21"] = calculate_sma(df[close_col], 21)
    df["sma_200"] = calculate_sma(df[close_col], 200)
    df["ema_9"] = calculate_ema(df[close_col], 9)
    return df
