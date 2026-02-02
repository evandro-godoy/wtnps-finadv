"""
Environment validation script for WTNPS Trade.

Validates:
- .env configuration
- MT5 installation and connection
- Model artifacts existence
- Python environment dependencies

Usage:
    poetry run python scripts/validate_environment.py
"""

import sys
import json
from pathlib import Path
from datetime import datetime
import logging

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

import MetaTrader5 as mt5
from dotenv import load_dotenv
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EnvironmentValidator:
    """Validates environment configuration for WTNPS Trade."""
    
    def __init__(self):
        """Initialize validator."""
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "checks": {}
        }
        self.all_passed = True
    
    def run_all_checks(self):
        """Run all validation checks."""
        logger.info("=" * 80)
        logger.info("WTNPS TRADE - ENVIRONMENT VALIDATION")
        logger.info("=" * 80)
        
        self.check_env_file()
        self.check_mt5_path()
        self.check_mt5_connection()
        self.check_model_artifacts()
        self.check_python_dependencies()
        
        self.generate_report()
        
        logger.info("=" * 80)
        if self.all_passed:
            logger.info("✅ ALL CHECKS PASSED - Environment is ready!")
        else:
            logger.error("❌ SOME CHECKS FAILED - Please fix issues above")
        logger.info("=" * 80)
        
        return self.all_passed
    
    def check_env_file(self):
        """Check if .env file exists and contains required variables."""
        logger.info("\n📄 Checking .env file...")
        
        env_path = Path(".env")
        
        if not env_path.exists():
            self._fail("env_file", "File not found", ".env file does not exist")
            logger.warning("⚠️  .env file not found. Copy .env.example to .env")
            return
        
        # Load .env
        load_dotenv()
        
        # Check required variables
        required_vars = ["MT5_PATH"]
        optional_vars = ["MT5_LOGIN", "MT5_PASSWORD", "MT5_SERVER", "MT5_TIMEOUT"]
        
        missing_required = []
        missing_optional = []
        
        for var in required_vars:
            value = os.getenv(var)
            if not value:
                missing_required.append(var)
        
        for var in optional_vars:
            value = os.getenv(var)
            if not value:
                missing_optional.append(var)
        
        if missing_required:
            self._fail(
                "env_variables",
                "Missing required variables",
                f"Missing: {', '.join(missing_required)}"
            )
            logger.error(f"❌ Missing required variables: {', '.join(missing_required)}")
        else:
            self._pass("env_variables", "All required variables present")
            logger.info("✅ .env file valid")
        
        if missing_optional:
            logger.warning(f"⚠️  Optional variables not set: {', '.join(missing_optional)}")
            logger.info("   This is OK if using default values or anonymous connection")
    
    def check_mt5_path(self):
        """Check if MT5 executable exists at specified path."""
        logger.info("\n🔧 Checking MetaTrader 5 installation...")
        
        mt5_path = os.getenv("MT5_PATH", "C:\\Program Files\\MetaTrader 5\\terminal64.exe")
        mt5_path_obj = Path(mt5_path)
        
        if not mt5_path_obj.exists():
            self._fail(
                "mt5_path",
                "MT5 executable not found",
                f"Path does not exist: {mt5_path}"
            )
            logger.error(f"❌ MT5 not found at: {mt5_path}")
            logger.info("   Please install MetaTrader 5 or update MT5_PATH in .env")
        else:
            self._pass("mt5_path", f"MT5 found at {mt5_path}")
            logger.info(f"✅ MT5 found: {mt5_path}")
    
    def check_mt5_connection(self):
        """Test MT5 connection."""
        logger.info("\n🔌 Testing MetaTrader 5 connection...")
        
        # Try to initialize MT5
        if not mt5.initialize():
            error_code = mt5.last_error()
            self._fail(
                "mt5_connection",
                "Failed to connect to MT5",
                f"Error code: {error_code}"
            )
            logger.error(f"❌ MT5 connection failed. Error: {error_code}")
            logger.info("   Make sure MT5 terminal is running and logged in")
            return
        
        # Get account info
        account_info = mt5.account_info()
        if account_info is None:
            self._fail(
                "mt5_account",
                "Failed to get account info",
                "MT5 may not be logged in"
            )
            logger.warning("⚠️  Could not get account info. MT5 may not be logged in")
        else:
            self._pass(
                "mt5_account",
                f"Connected to account {account_info.login}"
            )
            logger.info(f"✅ MT5 connected successfully")
            logger.info(f"   Account: {account_info.login}")
            logger.info(f"   Server: {account_info.server}")
        
        # Test symbol access
        test_symbols = ["WDO$", "WIN$"]
        for symbol in test_symbols:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                logger.warning(f"⚠️  Symbol {symbol} not available")
            else:
                logger.info(f"   Symbol {symbol}: Available ✓")
        
        # Shutdown MT5
        mt5.shutdown()
        
        self._pass("mt5_connection", "MT5 connection test passed")
    
    def check_model_artifacts(self):
        """Check if model artifacts exist."""
        logger.info("\n🤖 Checking model artifacts...")
        
        models_dir = Path("models")
        
        if not models_dir.exists():
            self._fail(
                "models_directory",
                "Models directory not found",
                "models/ directory does not exist"
            )
            logger.error("❌ models/ directory not found")
            return
        
        # Expected model files
        expected_models = [
            "WDO$_LSTMVolatilityStrategy_M5_prod_lstm.keras",
            "WDO$_LSTMVolatilityStrategy_M5_prod_scaler.joblib",
            "WDO$_LSTMVolatilityStrategy_M5_prod_params.joblib",
        ]
        
        optional_models = [
            "WIN$_LSTMVolatilityStrategy_M5_prod_lstm.keras",
            "WIN$_LSTMVolatilityStrategy_M5_prod_scaler.joblib",
            "WIN$_LSTMVolatilityStrategy_M5_prod_params.joblib",
        ]
        
        missing_required = []
        missing_optional = []
        
        for model_file in expected_models:
            model_path = models_dir / model_file
            if not model_path.exists():
                missing_required.append(model_file)
        
        for model_file in optional_models:
            model_path = models_dir / model_file
            if not model_path.exists():
                missing_optional.append(model_file)
        
        if missing_required:
            self._fail(
                "model_artifacts",
                "Required model files missing",
                f"Missing: {', '.join(missing_required)}"
            )
            logger.error(f"❌ Missing model files: {', '.join(missing_required)}")
            logger.info("   Run: poetry run python train_model.py")
        else:
            self._pass("model_artifacts", "All required model artifacts found")
            logger.info("✅ WDO$ model artifacts found")
        
        if missing_optional:
            logger.warning(f"⚠️  Optional models not found: {', '.join(missing_optional)}")
        else:
            logger.info("✅ WIN$ model artifacts found")
    
    def check_python_dependencies(self):
        """Check if required Python packages are installed."""
        logger.info("\n📦 Checking Python dependencies...")
        
        required_packages = [
            "fastapi",
            "uvicorn",
            "websockets",
            "MetaTrader5",
            "pandas",
            "numpy",
            "tensorflow",
            "scikit-learn",
            "plotly",
            "pydantic",
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            self._fail(
                "python_dependencies",
                "Missing Python packages",
                f"Missing: {', '.join(missing_packages)}"
            )
            logger.error(f"❌ Missing packages: {', '.join(missing_packages)}")
            logger.info("   Run: poetry install")
        else:
            self._pass("python_dependencies", "All required packages installed")
            logger.info("✅ All required packages installed")
    
    def generate_report(self):
        """Generate JSON report."""
        report_dir = Path("reports")
        report_dir.mkdir(exist_ok=True)
        
        report_path = report_dir / "environment_validation.json"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)
        
        logger.info(f"\n📊 Report saved to: {report_path}")
    
    def _pass(self, check_name, message):
        """Mark a check as passed."""
        self.results["checks"][check_name] = {
            "status": "PASS",
            "message": message
        }
    
    def _fail(self, check_name, error, details):
        """Mark a check as failed."""
        self.results["checks"][check_name] = {
            "status": "FAIL",
            "error": error,
            "details": details
        }
        self.all_passed = False


def main():
    """Main entry point."""
    validator = EnvironmentValidator()
    success = validator.run_all_checks()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
