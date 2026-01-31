"""Testes unitários para MetaTraderProvider - Fail Fast Connection Strategy."""

import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import sys

from src.data_handler.mt5_provider import MetaTraderProvider
from src.events import MarketDataEvent


class TestMetaTraderProvider(unittest.TestCase):
    """Testes da estratégia Fail Fast e interface de dados."""
    
    @patch('src.data_handler.mt5_provider.mt5')
    def test_fail_fast_on_init_failure(self, mock_mt5):
        """Requisito 2: Fail Fast - Se MT5 não inicializar, deve fazer exit(1)."""
        mock_mt5.initialize.return_value = False
        mock_mt5.last_error.return_value = "Terminal not found"
        
        with self.assertRaises(SystemExit) as context:
            MetaTraderProvider()
        
        self.assertEqual(context.exception.code, 1)
        mock_mt5.initialize.assert_called_once()
    
    @patch('src.data_handler.mt5_provider.mt5')
    def test_successful_initialization(self, mock_mt5):
        """Requisito 1: Conexão bem-sucedida ao MT5."""
        mock_mt5.initialize.return_value = True
        mock_mt5.version.return_value = (5, 0, 45)
        mock_mt5.terminal_info.return_value = MagicMock(name="MetaTrader 5")
        
        provider = MetaTraderProvider()
        
        # Verifica que inicialização foi chamada
        mock_mt5.initialize.assert_called_once()
        self.assertIsNotNone(provider)
    
    @patch('src.data_handler.mt5_provider.mt5')
    def test_get_latest_candles_returns_dataframe(self, mock_mt5):
        """Requisito 3: Interface retorna DataFrame com colunas esperadas."""
        # Setup
        mock_mt5.initialize.return_value = True
        mock_mt5.terminal_info.return_value = MagicMock()
        mock_mt5.TIMEFRAME_M5 = 5
        
        # Mock dos candles retornados pelo MT5
        mock_rates = [
            {
                'time': 1672531200,  # 2023-01-01 00:00:00
                'open': 100.0,
                'high': 102.0,
                'low': 99.0,
                'close': 101.5,
                'tick_volume': 1000,
            },
            {
                'time': 1672531500,  # 5 minutos depois
                'open': 101.5,
                'high': 103.0,
                'low': 101.0,
                'close': 102.0,
                'tick_volume': 1200,
            }
        ]
        mock_mt5.copy_rates_from_pos.return_value = mock_rates
        
        provider = MetaTraderProvider()
        df = provider.get_latest_candles('WDO$', 'M5', n=2)
        
        # Validar formato do DataFrame
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)
        
        # Validar colunas esperadas (Open, High, Low, Close, Volume)
        expected_cols = {'Open', 'High', 'Low', 'Close', 'Volume'}
        self.assertEqual(set(df.columns), expected_cols)
        
        # Validar tipos de dados
        self.assertTrue(df['Open'].dtype == float)
        self.assertTrue(df['High'].dtype == float)
        self.assertTrue(df['Low'].dtype == float)
        self.assertTrue(df['Close'].dtype == float)
        self.assertTrue(df['Volume'].dtype in [int, 'int64'])
        
        # Validar valores
        self.assertEqual(df.iloc[0]['Open'], 100.0)
        self.assertEqual(df.iloc[0]['Close'], 101.5)
        self.assertEqual(df.iloc[0]['Volume'], 1000)
    
    @patch('src.data_handler.mt5_provider.mt5')
    def test_invalid_timeframe_raises_error(self, mock_mt5):
        """Requisito 3: Timeframe inválido levanta ValueError."""
        mock_mt5.initialize.return_value = True
        mock_mt5.terminal_info.return_value = MagicMock()
        
        provider = MetaTraderProvider()
        
        with self.assertRaises(ValueError) as context:
            provider.get_latest_candles('WDO$', 'INVALID_TF', n=100)
        
        self.assertIn("Timeframe inválido", str(context.exception))
    
    @patch('src.data_handler.mt5_provider.mt5')
    def test_no_data_returned_raises_error(self, mock_mt5):
        """Requisito 3: MT5 retornando dados vazios levanta ValueError."""
        mock_mt5.initialize.return_value = True
        mock_mt5.terminal_info.return_value = MagicMock()
        mock_mt5.TIMEFRAME_M5 = 5
        mock_mt5.copy_rates_from_pos.return_value = None
        mock_mt5.last_error.return_value = "No data"
        
        provider = MetaTraderProvider()
        
        with self.assertRaises(ValueError) as context:
            provider.get_latest_candles('INVALID$', 'M5', n=100)
        
        self.assertIn("Nenhum dado retornado", str(context.exception))
    
    @patch('src.data_handler.mt5_provider.mt5')
    def test_get_latest_candles_as_events(self, mock_mt5):
        """Teste método auxiliar que retorna MarketDataEvent (para EventBus)."""
        mock_mt5.initialize.return_value = True
        mock_mt5.terminal_info.return_value = MagicMock()
        mock_mt5.TIMEFRAME_M5 = 5
        
        mock_rates = [
            {
                'time': 1672531200,
                'open': 100.0,
                'high': 102.0,
                'low': 99.0,
                'close': 101.5,
                'tick_volume': 1000,
            }
        ]
        mock_mt5.copy_rates_from_pos.return_value = mock_rates
        
        provider = MetaTraderProvider()
        events = provider.get_latest_candles_as_events('WDO$', 'M5', n=1)
        
        self.assertEqual(len(events), 1)
        self.assertIsInstance(events[0], MarketDataEvent)
        self.assertEqual(events[0].symbol, 'WDO$')
        self.assertEqual(events[0].close, 101.5)
        self.assertEqual(events[0].volume, 1000)
    
    @patch('src.data_handler.mt5_provider.mt5')
    def test_shutdown(self, mock_mt5):
        """Teste shutdown gracioso."""
        mock_mt5.initialize.return_value = True
        mock_mt5.terminal_info.return_value = MagicMock()
        mock_mt5.shutdown.return_value = None
        
        provider = MetaTraderProvider()
        provider.shutdown()
        
        mock_mt5.shutdown.assert_called_once()


if __name__ == '__main__':
    unittest.main(verbosity=2)
