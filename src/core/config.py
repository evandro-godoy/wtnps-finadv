# src/core/config.py
"""
Configurações globais do sistema com suporte a MT5.
Usa pydantic-settings para validação e .env para variáveis de ambiente.
"""

import os
import logging
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field

logger = logging.getLogger(__name__)


class MT5Settings(BaseSettings):
    """Configurações específicas do MetaTrader 5."""
    
    # Terminal path
    path: str = Field(
        default=r"C:\Program Files\MetaTrader 5\terminal64.exe",
        description="Caminho para o executável do MT5 terminal"
    )
    
    # Credenciais (opcionais - pode usar apenas terminal aberto)
    login: Optional[str] = Field(
        default=None,
        description="Login MT5 (deixar vazio para usar apenas terminal aberto)"
    )
    password: Optional[str] = Field(
        default=None,
        description="Senha MT5 (deixar vazio para usar apenas terminal aberto)"
    )
    server: Optional[str] = Field(
        default=None,
        description="Servidor MT5 (deixar vazio para usar padrão)"
    )
    
    # Operações
    timeout: int = Field(
        default=5000,
        description="Timeout para operações MT5 em ms"
    )
    
    class Config:
        env_prefix = "MT5_"
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignorar variáveis que não pertencem a este model


class Settings(BaseSettings):
    """
    Configurações globais validadas via Pydantic.
    Lê variáveis de ambiente do arquivo .env.
    """
    
    # ========== Identificação ==========
    PROJECT_NAME: str = Field(
        default="wtnps-finadv",
        description="Nome do projeto"
    )
    VERSION: str = Field(
        default="0.2.0-sprint3",
        description="Versão do sistema"
    )
    
    # ========== Caminhos (Baseados na estrutura do repo) ==========
    BASE_DIR: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent.parent.parent,
        description="Diretório raiz do projeto"
    )
    MODELS_DIR: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent.parent.parent / "models",
        description="Diretório de modelos treinados"
    )
    LOGS_DIR: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent.parent.parent / "logs",
        description="Diretório de logs"
    )
    CACHE_DIR: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent.parent.parent / ".cache_data",
        description="Diretório de cache de dados"
    )
    
    # ========== Trading ==========
    TRADING_ENABLED: bool = Field(
        default=False,
        description="Trava de segurança: habilita execução de trades"
    )
    TICKER_TARGET: str = Field(
        default="WDO$",
        description="Ativo padrão para o MVP"
    )
    
    # ========== Logging ==========
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Nível de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    
    # ========== MetaTrader 5 ==========
    MT5: MT5Settings = Field(
        default_factory=MT5Settings,
        description="Configurações do MetaTrader 5"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        # Permite configurações aninhadas via prefixo
        env_nested_delimiter = "__"
        extra = "ignore"  # Ignorar variáveis de ambiente não mapeadas

    def get_mt5_config(self) -> dict:
        """
        Retorna configurações do MT5 em formato de dicionário.
        Remove valores None/vazios para deixar MT5 usar defaults.
        """
        return {
            "path": self.MT5.path,
            "login": self.MT5.login if self.MT5.login else None,
            "password": self.MT5.password if self.MT5.password else None,
            "server": self.MT5.server if self.MT5.server else None,
            "timeout": self.MT5.timeout,
        }

    def mt5_needs_auth(self) -> bool:
        """
        Verifica se MT5 requer autenticação.
        Retorna False se qualquer credencial essencial está vazia.
        """
        return bool(self.MT5.login and self.MT5.password)


# ============== Singleton de configuração ==============
settings = Settings()

# Garante que diretórios essenciais existam
os.makedirs(settings.LOGS_DIR, exist_ok=True)
os.makedirs(settings.CACHE_DIR, exist_ok=True)
os.makedirs(settings.MODELS_DIR, exist_ok=True)

logger.debug(f"✅ Configurações carregadas de .env")
logger.debug(f"   MT5 Path: {settings.MT5.path}")
logger.debug(f"   MT5 Requer Auth: {settings.mt5_needs_auth()}")
logger.debug(f"   Base Dir: {settings.BASE_DIR}")