# 🚀 WTNPS FinAdv - Algorithmic Trading Framework

Production-ready **ML/DRL trading system** with MetaTrader5 integration.

**Status**: Sprint 3 - Migration & Clean Up  
**Branch**: main  
**Python**: 3.12+

---

## 📖 Quick Navigation

### 🏗️ Architecture & Setup
- [Canonical Src Layout](docs/architecture/CANONICAL_LAYOUT.md) - Project structure
- [Migration Guide](docs/architecture/MIGRATION_GUIDE.md) - From wtnps-trade to wtnps-finadv

### 📋 Planning & Status
- [Implementation Plan](docs/planning/IMPLEMENTATION_PLAN.md) - Master roadmap
- [Sprint 3 Plan](docs/planning/PLANO_SPRINT_3.md) - Current sprint

### 👤 User Documentation
- [GUI User Guide](docs/user/GUIA_USUARIO_CHARTS.md) - Using dashboards
- [DRL Documentation](docs/user/DRL_README.md) - Deep Reinforcement Learning

---

## ⚡ Quick Start

### 1. Environment Setup
```bash
# Clone repository
git clone https://github.com/evandro-godoy/wtnps-finadv.git
cd wtnps-finadv

# Install dependencies
poetry install

# Setup environment
cp .env.example .env
# Edit .env: configure MT5_PATH, MT5_LOGIN, MT5_SERVER, MT5_PASSWORD
```

### 2. Run Tests
```bash
# All tests
poetry run pytest tests/ -v

# Unit only
poetry run pytest tests/unit/ -v

# Integration (requires MT5 running)
poetry run pytest tests/integration/ -v
```

### 3. Live Trading
```bash
poetry run python src/live_trader.py
```

### 4. View Dashboards
```bash
poetry run python run_monitor_gui.py --mode live
```

---

## 🏛️ Architecture Overview

### Core Components
- **EventBus** (`src/core/event_bus.py`) - Publish/subscribe event dispatcher
- **Strategies** (`src/strategies/`) - ML models (LSTM, RandomForest, DRL)
- **Data Providers** (`src/data_handler/`) - MT5, YFinance
- **Execution** (`src/live_trader.py`, `src/simulation/`) - Live and simulation engines

---

## 🧭 Project Structure
```
.
├── docs/
│   ├── planning/
│   ├── architecture/
│   └── user/
├── src/
├── tests/
├── models/
├── notebooks/
├── configs/
├── reports/
└── logs/
```
