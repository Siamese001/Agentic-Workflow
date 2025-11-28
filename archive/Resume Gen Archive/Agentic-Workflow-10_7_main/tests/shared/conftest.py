import sys
from pathlib import Path

import pytest

from tests.shared import fixtures as shared_fixtures
from tests.shared.test_utils import (
    install_langgraph_stub,
    pytest_addoption,
    pytest_collection_modifyitems,
    pytest_configure,
    pytest_pyfunc_call,
)

# Ensure repository root is importable when pytest rootdir resolves to tests/
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

install_langgraph_stub()

# Re-export fixtures for pytest discovery
globals().update(vars(shared_fixtures))

__all__ = list(shared_fixtures.__all__) if hasattr(shared_fixtures, "__all__") else []
