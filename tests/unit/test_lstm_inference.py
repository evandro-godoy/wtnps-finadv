"""
Teste de validação de inferência LSTM Volatility.

Valida:
1. Carregamento correto de modelos .keras e .joblib
2. Shape de entrada/saída
3. Consistência de features entre training e inference
4. Performance de inferência
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path
import time
import logging
from datetime import datetime, timedelta

from src.strategies.lstm_volatility import LSTMVolatilityStrategy, LSTMVolatilityWrapper
from src.data_handler.mt5_provider import MetaTraderProvider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestLSTMInference:
    """Suite de testes para validação de inferência LSTM."""
    
    @pytest.fixture(scope="class")
    def model_artifacts_wdo(self):
        """Fixture para carregar artefatos do modelo WDO$."""
        model_prefix = "models/WDO$_LSTMVolatilityStrategy_M5_prod"
        
        # Verifica se os artefatos existem
        model_path = f"{model_prefix}_lstm.keras"
        scaler_path = f"{model_prefix}_scaler.joblib"
        params_path = f"{model_prefix}_params.joblib"
        
        assert Path(model_path).exists(), f"Modelo não encontrado: {model_path}"
        assert Path(scaler_path).exists(), f"Scaler não encontrado: {scaler_path}"
        assert Path(params_path).exists(), f"Params não encontrado: {params_path}"
        
        return model_prefix
    
    @pytest.fixture(scope="class")
    def loaded_model_wdo(self, model_artifacts_wdo):
        """Fixture para carregar o modelo WDO$."""
        model = LSTMVolatilityWrapper.load(model_artifacts_wdo)
        return model
    
    @pytest.fixture(scope="class")
    def strategy_instance(self):
        """Fixture para instância de estratégia."""
        return LSTMVolatilityStrategy(lookback=96)
    
    @pytest.fixture(scope="class")
    def historical_data(self):
        """Fixture para dados históricos de teste (último mês)."""
        try:
            provider = MetaTraderProvider()
            data = provider.get_latest_candles(
                symbol="WDO$",
                timeframe="M5",
                n=2000
            )
            
            assert isinstance(data, pd.DataFrame), "Provider deve retornar DataFrame"
            assert len(data) > 0, "DataFrame de dados históricos está vazio"
            
            return data
        except Exception as e:
            pytest.skip(f"MT5 não disponível ou erro ao carregar dados: {e}")
    
    def test_model_loading(self, loaded_model_wdo):
        """Testa se o modelo carrega corretamente."""
        assert loaded_model_wdo is not None, "Modelo não foi carregado"
        assert hasattr(loaded_model_wdo, 'model'), "Modelo não tem atributo 'model'"
        assert hasattr(loaded_model_wdo, 'scaler'), "Modelo não tem atributo 'scaler'"
        assert loaded_model_wdo.lookback == 96, f"Lookback esperado: 96, obtido: {loaded_model_wdo.lookback}"
        
        logger.info(f"✓ Modelo carregado com sucesso")
        logger.info(f"  Lookback: {loaded_model_wdo.lookback}")
        logger.info(f"  Features: {loaded_model_wdo.n_features}")
        logger.info(f"  Scaler features_in: {loaded_model_wdo.scaler.n_features_in_}")
    
    def test_model_input_shape(self, loaded_model_wdo):
        """Valida shape de entrada do modelo."""
        # Shape esperado: (batch_size, lookback=96, n_features)
        expected_input_shape = (None, 96, loaded_model_wdo.n_features)
        actual_input_shape = loaded_model_wdo.model.input_shape
        
        assert actual_input_shape[1] == expected_input_shape[1], \
            f"Lookback esperado: {expected_input_shape[1]}, obtido: {actual_input_shape[1]}"
        assert actual_input_shape[2] == expected_input_shape[2], \
            f"Features esperadas: {expected_input_shape[2]}, obtidas: {actual_input_shape[2]}"
        
        logger.info(f"✓ Input shape validado: {actual_input_shape}")
    
    def test_model_output_shape(self, loaded_model_wdo):
        """Valida shape de saída do modelo."""
        # Shape esperado: (batch_size, 1) - classificação binária
        expected_output_shape = (None, 1)
        actual_output_shape = loaded_model_wdo.model.output_shape
        
        assert actual_output_shape == expected_output_shape, \
            f"Output shape esperado: {expected_output_shape}, obtido: {actual_output_shape}"
        
        logger.info(f"✓ Output shape validado: {actual_output_shape}")
    
    def test_feature_consistency(self, strategy_instance, historical_data):
        """Valida consistência de features entre training e inference."""
        # Gera features usando a estratégia
        df_with_features = strategy_instance.define_features(historical_data)
        
        # Verifica se todas as features esperadas foram criadas
        expected_features = strategy_instance.get_feature_names()
        
        for feature in expected_features:
            assert feature in df_with_features.columns, \
                f"Feature '{feature}' não encontrada no DataFrame gerado"
        
        # Verifica se não há NaN/Inf nas features
        feature_df = df_with_features[expected_features]
        
        # Verifica NaN
        nan_count = feature_df.isna().sum().sum()
        assert nan_count == 0, f"Encontrados {nan_count} valores NaN nas features"
        
        # Verifica Inf
        inf_count = np.isinf(feature_df.values).sum()
        assert inf_count == 0, f"Encontrados {inf_count} valores Inf nas features"
        
        logger.info(f"✓ Features consistentes: {len(expected_features)} features validadas")
        logger.info(f"  Features: {expected_features}")
    
    def test_scaler_normalization(self, loaded_model_wdo, strategy_instance, historical_data):
        """Valida normalização do scaler."""
        # Gera features
        df_with_features = strategy_instance.define_features(historical_data)
        features = strategy_instance.get_feature_names()
        X = df_with_features[features].values
        
        # Aplica scaler
        X_scaled = loaded_model_wdo.scaler.transform(X)
        
        # Verifica range [0, 1] (MinMaxScaler)
        min_val = X_scaled.min()
        max_val = X_scaled.max()
        
        assert min_val >= 0.0, f"Valor mínimo após scaling < 0: {min_val}"
        assert max_val <= 1.0, f"Valor máximo após scaling > 1: {max_val}"
        
        logger.info(f"✓ Scaler normalização validada: range [{min_val:.4f}, {max_val:.4f}]")
    
    def test_inference_with_real_data(self, loaded_model_wdo, strategy_instance, historical_data):
        """Testa inferência com dados reais."""
        # Gera features
        df_with_features = strategy_instance.define_features(historical_data)
        features = strategy_instance.get_feature_names()
        X = df_with_features[features]
        
        # Faz predição
        predictions = loaded_model_wdo.predict(X)
        
        # Validações
        assert isinstance(predictions, np.ndarray), "Predições devem ser numpy array"
        assert len(predictions) > 0, "Array de predições está vazio"
        assert set(predictions).issubset({0, 1}), "Predições devem ser 0 ou 1 (classificação binária)"
        
        # Predição de probabilidades
        proba = loaded_model_wdo.predict_proba(X)
        
        assert proba.shape[1] == 2, f"Shape de probabilidades esperado: (n, 2), obtido: {proba.shape}"
        assert np.allclose(proba.sum(axis=1), 1.0), "Probabilidades devem somar 1.0"
        
        logger.info(f"✓ Inferência com dados reais validada")
        logger.info(f"  Samples processados: {len(predictions)}")
        logger.info(f"  Classe 1 (volatilidade): {predictions.sum()} ({predictions.mean()*100:.1f}%)")
        logger.info(f"  Classe 0 (normal): {(1-predictions).sum()} ({(1-predictions.mean())*100:.1f}%)")
    
    def test_inference_with_synthetic_data(self, loaded_model_wdo):
        """Testa inferência com dados sintéticos."""
        n_features = loaded_model_wdo.n_features
        n_samples = 200  # Precisa > lookback para criar sequências
        
        # Dados sintéticos aleatórios no range [0, 1]
        X_synthetic = np.random.rand(n_samples, n_features)
        X_df = pd.DataFrame(X_synthetic)
        
        # Predição
        predictions = loaded_model_wdo.predict(X_df)
        
        assert len(predictions) > 0, "Predições com dados sintéticos estão vazias"
        assert predictions.dtype in [np.int32, np.int64], f"Dtype esperado: int, obtido: {predictions.dtype}"
        
        logger.info(f"✓ Inferência com dados sintéticos validada")
        logger.info(f"  Samples gerados: {n_samples}")
        logger.info(f"  Predições: {len(predictions)}")
    
    def test_inference_performance(self, loaded_model_wdo, strategy_instance, historical_data):
        """Testa performance de inferência (<100ms target)."""
        # Simula inferência de 1 candle (último do histórico)
        df_with_features = strategy_instance.define_features(historical_data)
        features = strategy_instance.get_feature_names()
        
        # Pega últimos 200 candles (suficiente para lookback=96)
        X_window = df_with_features[features].tail(200)
        
        # Mede tempo de inferência
        start_time = time.time()
        predictions = loaded_model_wdo.predict(X_window)
        inference_time_ms = (time.time() - start_time) * 1000
        
        # Target: <100ms por inferência
        assert inference_time_ms < 100, \
            f"Tempo de inferência muito alto: {inference_time_ms:.2f}ms (target: <100ms)"
        
        logger.info(f"✓ Performance validada")
        logger.info(f"  Tempo de inferência: {inference_time_ms:.2f}ms")
        logger.info(f"  Target: <100ms ✓")
    
    def test_memory_footprint(self, loaded_model_wdo, strategy_instance, historical_data):
        """Valida memory footprint com buffer de 500 candles."""
        import sys
        
        # Gera features para 500 candles
        df_with_features = strategy_instance.define_features(historical_data.tail(500))
        features = strategy_instance.get_feature_names()
        X = df_with_features[features]
        
        # Estima tamanho em memória
        memory_bytes = X.memory_usage(deep=True).sum()
        memory_mb = memory_bytes / (1024 ** 2)
        
        # Target: <500MB para buffer
        assert memory_mb < 500, f"Memory footprint muito alto: {memory_mb:.2f}MB (target: <500MB)"
        
        logger.info(f"✓ Memory footprint validado")
        logger.info(f"  Buffer 500 candles: {memory_mb:.2f}MB")
        logger.info(f"  Target: <500MB ✓")
    
    def test_batch_predictions(self, loaded_model_wdo, strategy_instance, historical_data):
        """Testa predições em lote (múltiplos candles)."""
        df_with_features = strategy_instance.define_features(historical_data)
        features = strategy_instance.get_feature_names()
        X = df_with_features[features]
        
        # Predição em lote
        start_time = time.time()
        predictions = loaded_model_wdo.predict(X)
        proba = loaded_model_wdo.predict_proba(X)
        batch_time_ms = (time.time() - start_time) * 1000
        
        # Validações
        assert len(predictions) > 0, "Predições em lote vazias"
        assert len(predictions) == len(proba), "Predições e probabilidades com tamanhos diferentes"
        
        # Performance por candle
        time_per_candle = batch_time_ms / len(predictions) if len(predictions) > 0 else 0
        
        logger.info(f"✓ Batch predictions validadas")
        logger.info(f"  Total samples: {len(predictions)}")
        logger.info(f"  Tempo total: {batch_time_ms:.2f}ms")
        logger.info(f"  Tempo/candle: {time_per_candle:.2f}ms")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
