"""Local conftest for tests/enforcement to bypass testpaths restriction."""

import os
from pathlib import Path


def pytest_configure(config):
    """Bypass testpaths restriction for enforcement tests."""
    # Only bypass if explicitly requested (default OFF)
    if os.environ.get("PYTEST_BYPASS_RUNLOOP") == "1":
        return

    # Completely override testpaths to allow enforcement tests
    enforcement_dir = str(Path(__file__).parent)

    # Override the iniconfig values
    if hasattr(config, "_inicache"):
        config._inicache["testpaths"] = [enforcement_dir]

    # Override the option values
    if hasattr(config, "option"):
        config.option.testpaths = [enforcement_dir]
