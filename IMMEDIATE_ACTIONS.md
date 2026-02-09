# 🚨 IMMEDIATE ACTIONS REQUIRED

**Date**: February 9, 2025  
**Priority**: CRITICAL - Start TODAY

---

## ⏰ 5-Minute Action: Create .gitignore

**WHY**: Your .env file is NOT protected and could expose credentials

**DO NOW**:

```bash
# Step 1: Create branch
git checkout -b security/add-gitignore

# Step 2: Create .gitignore file
cat > .gitignore << 'END'
# Environment variables
.env
.env.local
*.env.backup

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Logs
*.log
logs/
*.out
*.err

# Models & Data Cache
models/*.keras
models/*.h5
models/*.joblib
models/*.pkl
.cache_data/
*.parquet

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Jupyter
.ipynb_checkpoints/
*.ipynb

# Database
*.db
*.sqlite3

# Backup files
*.bak
*.backup
END

# Step 3: Remove .env from git tracking (if it was committed)
git rm --cached .env 2>/dev/null || echo ".env not in repo"

# Step 4: Commit
git add .gitignore
git commit -m "feat(security): Add .gitignore to prevent credential leaks

- Protect .env files
- Ignore Python artifacts
- Ignore model files
- Ignore logs and cache

Fixes: Critical security vulnerability"

# Step 5: Push
git push origin security/add-gitignore

# Step 6: Create Pull Request on GitHub
echo "✅ Now create PR on GitHub with title: '[CRITICAL] Add .gitignore'"
```

---

## 🔍 30-Minute Action: Audit Git History

**WHY**: Check if credentials were ever committed

**DO NEXT**:

```bash
# Check if .env was ever in git history
echo "Checking git history for .env..."
git log --all --full-history --source -- ".env"

# Check for password patterns
echo "Checking for password patterns..."
git log -p --all | grep -i "password\|secret\|key" | head -20

# If you find exposed credentials:
echo "⚠️  FOUND CREDENTIALS IN HISTORY?"
echo "1. Rotate ALL credentials immediately"
echo "2. Consider using git-filter-repo to clean history"
echo "3. Force push (destructive - coordinate with team)"
```

---

## 🧪 2-Hour Action: Setup CI/CD with pytest

**WHY**: Tests exist but never run - no quality gates

**DO THIS WEEK**:

### Step 1: Configure pytest in pyproject.toml

```bash
# Edit pyproject.toml and add:
cat >> pyproject.toml << 'PYTEST'

[tool.pytest.ini_options]
minversion = "9.0"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--strict-markers",
    "--cov=src",
    "--cov-report=html",
    "--cov-report=term-missing",
    "--cov-fail-under=50"  # Start at 50%, increase gradually
]
markers = [
    "unit: Unit tests (fast, no external dependencies)",
    "integration: Integration tests (requires MT5)",
    "slow: Slow running tests"
]

[tool.coverage.run]
source = ["src"]
omit = [
    "*/tests/*",
    "*/test_*.py",
    "*/__pycache__/*",
    "*/venv/*"
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "class .*\\bProtocol\\):",
    "@(abc\\.)?abstractmethod"
]
PYTEST
```

### Step 2: Create GitHub Actions workflow

```bash
mkdir -p .github/workflows

cat > .github/workflows/tests.yml << 'WORKFLOW'
name: Tests and Quality

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.12']
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Setup Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install Poetry
        uses: snok/install-poetry@v1
        with:
          version: 1.7.1
          virtualenvs-create: true
          virtualenvs-in-project: true
      
      - name: Load cached venv
        id: cached-poetry-dependencies
        uses: actions/cache@v3
        with:
          path: .venv
          key: venv-${{ runner.os }}-${{ matrix.python-version }}-${{ hashFiles('**/poetry.lock') }}
      
      - name: Install dependencies
        if: steps.cached-poetry-dependencies.outputs.cache-hit != 'true'
        run: poetry install --no-interaction --no-root
      
      - name: Install project
        run: poetry install --no-interaction
      
      - name: Run unit tests
        run: |
          poetry run pytest tests/unit/ -v --cov=src --cov-report=xml --cov-report=term-missing -m "not slow"
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          flags: unittests
          name: codecov-umbrella
          fail_ci_if_error: false

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install Poetry
        uses: snok/install-poetry@v1
      - name: Install dependencies
        run: poetry install --no-interaction
      - name: Run flake8
        run: poetry run flake8 src/ --max-line-length=120 --extend-ignore=E203,W503
      - name: Run black check
        run: poetry run black src/ tests/ --check
WORKFLOW

# Commit workflow
git add .github/workflows/tests.yml pyproject.toml
git commit -m "feat(ci): Add CI/CD pipeline with pytest and coverage"
git push
```

### Step 3: Add badges to README.md

```markdown
# Add to top of README.md after title:
[![Tests](https://github.com/YOUR_USERNAME/wtnps-finadv/actions/workflows/tests.yml/badge.svg)](https://github.com/YOUR_USERNAME/wtnps-finadv/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/YOUR_USERNAME/wtnps-finadv/branch/main/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/wtnps-finadv)
```

---

## 📝 Create GitHub Issues

**DO AFTER ABOVE**:

```bash
# Use GitHub CLI to create issues
gh issue create --title "[P0] Add .gitignore to prevent credential leaks" \
  --body "See IMMEDIATE_ACTIONS.md - 5 minute fix" \
  --label "security,critical,quick-win" \
  --assignee @me

gh issue create --title "[P0] Setup CI/CD pipeline with pytest" \
  --body "See IMMEDIATE_ACTIONS.md - 2 hour implementation" \
  --label "testing,ci-cd,quality" \
  --assignee @me

gh issue create --title "[P0] Consolidate dual MT5 provider implementations" \
  --body "Two separate MT5 providers exist - see ARCHITECTURE_REVIEW.md Section 1.2" \
  --label "architecture,technical-debt,p0" \
  --assignee @me
```

---

## ✅ Verification Checklist

After completing the above, verify:

- [ ] .gitignore file exists and is committed
- [ ] .env is NOT tracked by git (`git ls-files | grep .env` returns nothing)
- [ ] Git history audited for credentials
- [ ] pytest runs locally: `poetry run pytest tests/unit/ -v`
- [ ] GitHub Actions workflow file exists
- [ ] CI pipeline runs on next push
- [ ] Issues created on GitHub

---

## 📞 Need Help?

If you encounter issues:

1. **Git History Cleanup**: Consider using `git-filter-repo` (destructive!)
2. **Poetry Issues**: Run `poetry install --no-cache`
3. **Test Failures**: Start with `pytest tests/unit/ -v -x` to stop on first failure
4. **CI Issues**: Check GitHub Actions logs for details

---

## 🎯 Success Criteria

You'll know you're done when:

1. ✅ `.env` is protected by .gitignore
2. ✅ No credentials in git history
3. ✅ Tests run automatically on every PR
4. ✅ Coverage report generated
5. ✅ Team can see test results in PR checks

---

**STOP READING. START DOING. 🚀**

Begin with the 5-minute .gitignore fix RIGHT NOW.
