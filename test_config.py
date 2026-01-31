#!/usr/bin/env python3
"""
Test script para validar configurações de MT5.
Verifica se as variáveis de ambiente estão sendo lidas corretamente.
"""

import os
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 70)
print("🔍 TESTE DE CONFIGURAÇÃO DO MT5")
print("=" * 70)

# 1. Verificar .env
print("\n📄 1. Verificando arquivo .env...")
env_path = Path(".env")
if env_path.exists():
    print(f"   ✅ .env encontrado em: {env_path.absolute()}")
    with open(".env", "r") as f:
        lines = f.readlines()
    print(f"   📋 Linhas de configuração: {len(lines)}")
    for line in lines:
        if line.strip() and not line.startswith("#"):
            print(f"      {line.strip()}")
else:
    print(f"   ❌ .env não encontrado em: {env_path.absolute()}")

# 2. Carregar configurações
print("\n⚙️  2. Carregando configurações...")
try:
    from src.core.config import settings, logger
    print("   ✅ Módulo config importado com sucesso")
except Exception as e:
    print(f"   ❌ Erro ao importar config: {e}")
    sys.exit(1)

# 3. Mostrar configurações carregadas
print("\n🔧 3. Configurações Carregadas:")
print(f"   PROJECT_NAME: {settings.PROJECT_NAME}")
print(f"   VERSION: {settings.VERSION}")
print(f"   BASE_DIR: {settings.BASE_DIR}")
print(f"   MODELS_DIR: {settings.MODELS_DIR}")
print(f"   LOGS_DIR: {settings.LOGS_DIR}")
print(f"   CACHE_DIR: {settings.CACHE_DIR}")
print(f"   TRADING_ENABLED: {settings.TRADING_ENABLED}")
print(f"   LOG_LEVEL: {settings.LOG_LEVEL}")

# 4. Mostrar configurações MT5
print("\n🎯 4. Configurações MetaTrader 5:")
mt5_config = settings.get_mt5_config()
print(f"   MT5_PATH: {mt5_config['path']}")
print(f"   MT5_LOGIN: {'[DEFINIDO]' if mt5_config['login'] else '[VAZIO - Terminal Aberto]'}")
print(f"   MT5_PASSWORD: {'[DEFINIDO]' if mt5_config['password'] else '[VAZIO]'}")
print(f"   MT5_SERVER: {mt5_config['server'] or '[VAZIO - Padrão]'}")
print(f"   MT5_TIMEOUT: {mt5_config['timeout']}ms")

# 5. Verificar necessidade de autenticação
print("\n🔐 5. Autenticação:")
needs_auth = settings.mt5_needs_auth()
print(f"   MT5 requer autenticação: {needs_auth}")
if not needs_auth:
    print("   ✅ Usando modo terminal aberto (recomendado para desenvolvimento)")
else:
    print("   ✅ Usando credenciais do .env")

# 6. Verificar diretórios
print("\n📁 6. Verificação de Diretórios:")
for name, path in [
    ("BASE_DIR", settings.BASE_DIR),
    ("MODELS_DIR", settings.MODELS_DIR),
    ("LOGS_DIR", settings.LOGS_DIR),
    ("CACHE_DIR", settings.CACHE_DIR),
]:
    exists = "✅" if path.exists() else "⚠️ "
    print(f"   {exists} {name}: {path}")

# 7. Testar import do MT5 Provider
print("\n📦 7. Testando MT5 Provider:")
try:
    from src.data_handler.mt5_provider import MetaTraderProvider
    print("   ✅ MetaTraderProvider importado com sucesso")
    print("   ⚠️  Nota: Inicialização real do MT5 requer terminal rodando")
except Exception as e:
    print(f"   ❌ Erro ao importar MetaTraderProvider: {e}")

print("\n" + "=" * 70)
print("✅ TESTE DE CONFIGURAÇÃO CONCLUÍDO")
print("=" * 70)
print("\n📝 Próximos passos:")
print("   1. Editar .env com suas credenciais MT5 (se necessário)")
print("   2. Abrir o terminal MetaTrader 5")
print("   3. Executar: poetry run python -c \"from src.data_handler.mt5_provider import MetaTraderProvider; p = MetaTraderProvider()\"")
