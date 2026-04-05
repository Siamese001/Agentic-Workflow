"""conftest for apps_rg tests - handles Pydantic V2 deprecation warnings and package shadowing."""

import sys
import warnings
from pathlib import Path

# Ensure repo root is on sys.path BEFORE any test module import
_REPO_ROOT = str(Path(__file__).resolve().parents[3])
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

# Purge any apps_rg shadow registered from tests/unit/apps_rg/__init__.py
# so imports like `from apps_rg.config.X import Y` resolve to the real package
_TESTS_ROOT = str(Path(__file__).resolve().parents[2])
_to_purge = [
    k for k, m in sys.modules.items()
    if (k == "apps_rg" or k.startswith("apps_rg."))
    and _TESTS_ROOT in (getattr(m, "__file__", "") or "")
]
for _k in _to_purge:
    del sys.modules[_k]

# Filter Pydantic V2 deprecation warnings to prevent collection errors
warnings.filterwarnings(
    "ignore",
    message=".*PydanticDeprecatedSince20.*",
    category=DeprecationWarning,
)
warnings.filterwarnings(
    "ignore",
    message=".*Pydantic V1 style.*",
    category=DeprecationWarning,
)
warnings.filterwarnings(
    "ignore",
    message=".*Support for class-based.*",
    category=DeprecationWarning,
)
