# Agentic Workflow Testing Architecture

**Status:** Strict Scope Mirroring (Enforced)

## The Golden Rule
Tests are **NOT** colocated. They are **Mirrored**.

The `tests/` directory strictly mimics the source code structure under specific "Test Types".

### Directory Structure
```text
tests/
 ├── unit/                  # Mocked, fast, isolated tests
 │    ├── agentic_core/     # Mirrors root agentic_core/
 │    │    └── L5_safety/   # Mirrors agentic_core/L5_safety/
 │    └── apps_rg/          # Mirrors apps_rg/
 ├── integration/           # DB/API interaction tests
 │    └── agentic_core/
 ├── e2e/                   # Full system/browser tests
 └── fixtures/              # Shared conftest.py and data

```

### Rules

1. **No `sys.path` Hacks:** `pytest.ini` sets `pythonpath = .`. Import `agentic_core` directly.
2. **No Root Tests:** Do not put `test_foo.py` in `tests/`. Put it in `tests/unit/domain/...`.
3. **Strict Mirroring:** If source is `agentic_core/utils/foo.py`, test is `tests/unit/agentic_core/utils/test_foo.py`.

### Running Tests

```bash
# Run everything
pytest

# Run specific domain
pytest tests/unit/agentic_core/L5_safety

# Run Governance Check
python ops_scripts/governance/check_test_structure.py

```