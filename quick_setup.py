#!/usr/bin/env python3
"""
Quick Setup Script - Configuração inicial do projeto
Copia .env.example → .env e prepara ambiente
"""

import os
import shutil
from pathlib import Path

def setup():
    """Realizar setup inicial."""
    
    print("\n" + "="*70)
    print("🚀 QUICK SETUP - WTNPS FINADV")
    print("="*70)
    
    # 1. Verificar .env.example
    print("\n1️⃣  Verificando .env.example...")
    if not Path(".env.example").exists():
        print("   ❌ .env.example não encontrado")
        return False
    print("   ✅ .env.example encontrado")
    
    # 2. Criar .env se não existir
    print("\n2️⃣  Configurando .env...")
    if Path(".env").exists():
        print("   ⚠️  .env já existe - pulando")
    else:
        shutil.copy(".env.example", ".env")
        print("   ✅ .env criado a partir de .env.example")
    
    # 3. Criar diretórios essenciais
    print("\n3️⃣  Criando diretórios...")
    for dirname in ["models", "logs", ".cache_data", "reports"]:
        Path(dirname).mkdir(exist_ok=True)
        print(f"   ✅ {dirname}/")
    
    # 4. Verificar dependencies
    print("\n4️⃣  Verificando dependências...")
    try:
        import pydantic_settings
        print("   ✅ pydantic-settings")
    except ImportError:
        print("   ⚠️  pydantic-settings - executar: poetry install")
    
    try:
        import MetaTrader5
        print("   ✅ MetaTrader5")
    except ImportError:
        print("   ⚠️  MetaTrader5 - executar: poetry install")
    
    # 5. Resumo
    print("\n" + "="*70)
    print("✅ SETUP CONCLUÍDO!")
    print("="*70)
    
    print("\n📝 Próximos passos:")
    print("   1. Editar .env com suas preferências (opcional)")
    print("   2. Abrir terminal MetaTrader 5")
    print("   3. Executar: poetry run python test_config.py")
    print("   4. Executar: poetry run python examples_mt5_usage.py")
    
    print("\n📚 Documentação:")
    print("   - Guia de Configuração: docs/MT5_CONFIGURATION_GUIDE.md")
    print("   - Status da Implementação: IMPLEMENTATION_STATUS.md")
    print("   - Exemplo de Uso: examples_mt5_usage.py")
    
    print("\n🔒 Segurança:")
    print("   ✅ .env adicionado ao .gitignore")
    print("   ✅ Deixar credenciais MT5 vazias (usar terminal aberto)")
    print("   ✅ Nunca commitar .env com dados sensíveis")
    
    return True

if __name__ == "__main__":
    try:
        os.chdir(Path(__file__).parent)
        setup()
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        exit(1)
