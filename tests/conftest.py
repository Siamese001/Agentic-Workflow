import sys
import os
import warnings
from pathlib import Path
import pytest

# Sovereignty Injection: Ensure project root and stubs are at the top of the path
project_root = Path(__file__).parent.parent
stubs_path = project_root / "stubs"

# Insert project root first, then stubs as a fallback
sys.path.insert(0, str(project_root))
sys.path.insert(1, str(stubs_path))

@pytest.fixture(autouse=True)
def stub_environment_warning():
    """Warns the user that the system is running in a Sovereign Stubbed state."""
    warnings.warn(
        "\n[SOVEREIGNTY ALERT] Tests are running with Import Stubs. \n"
        "Collection is unblocked, but runtime behavior is simulated.",
        UserWarning
    )

def pytest_configure(config):
    """Register custom markers for the sovereign suite."""
    config.addinivalue_line("markers", "sovereign: marks tests as part of the core sovereignty suite")
