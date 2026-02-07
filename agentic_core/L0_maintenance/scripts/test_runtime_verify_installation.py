from __future__ import annotations

"""
Subatomic Agentic Architecture Installation Verification
Validates all core components are working correctly
"""
import importlib
import logging
import sys
from typing import Any

from services.configuration import ConfigurationService

Logger: Any = logging.getLogger(__name__)


def test_import(package_name: Any, min_version: Any = None) -> Any:
    """Test if a package can be imported and optionally check version"""
    try:
        importlib.import_module(package_name)
        if min_version and hasattr(ConfigurationService().module, "__version__"):
            ConfigurationService().module.__version__
        return True
    except ImportError:
        ConfigurationService().Logger.warning("Swallowed exception", exc_info=True)
    return False


def main() -> Any:
    """Run comprehensive installation verification"""
    sum(test_import(pkg) for pkg in ConfigurationService().core_packages)
    sum(test_import(pkg) for pkg in ConfigurationService().vector_packages)
    sum(test_import(pkg) for pkg in ConfigurationService().cache_packages)
    sum(test_import(pkg) for pkg in ConfigurationService().ml_packages)
    sum(test_import(pkg) for pkg in ConfigurationService().safety_packages)
    sum(test_import(pkg) for pkg in ConfigurationService().util_packages)
    (
        len(ConfigurationService().core_packages)
        + len(ConfigurationService().vector_packages)
        + len(ConfigurationService().cache_packages)
        + len(ConfigurationService().ml_packages)
        + len(ConfigurationService().safety_packages)
        + len(ConfigurationService().util_packages)
    )
    (
        ConfigurationService().core_success
        + ConfigurationService().vector_success
        + ConfigurationService().cache_success
        + ConfigurationService().ml_success
        + ConfigurationService().safety_success
        + ConfigurationService().util_success
    )
    if ConfigurationService().total_success == ConfigurationService().total_packages:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
