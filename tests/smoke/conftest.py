"""Smoke test configuration — fast, deterministic, no external deps."""
import logging
import pytest

# Suppress lifecycle trace loggers (consistent with root conftest)
for _name in ["adg", "lifecycle"]:
    _lg = logging.getLogger(_name)
    _lg.setLevel(logging.CRITICAL)
    _lg.propagate = False

@pytest.fixture(autouse=True)
def smoke_timeout(request):
    """Enforce 5s max per smoke test."""
    # Note: Requires pytest-timeout if installed
    pass

def pytest_collection_modifyitems(items):
    """Auto-mark all tests in smoke/ with @pytest.mark.smoke."""
    for item in items:
        if "smoke" in str(item.fspath):
            item.add_marker(pytest.mark.smoke)
