"""conftest for tests/unit/apps/apps_lic/ — ensure apps_lic resolves to source, not test shadow."""
import sys
from pathlib import Path

_REPO_ROOT = str(Path(__file__).resolve().parents[5])
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

# If apps_lic.utils was cached as a non-package by an earlier collector, purge it.
_mod = sys.modules.get("apps_lic.utils")
if _mod is not None and not hasattr(_mod, "__path__"):
    _doomed = [k for k in list(sys.modules) if k == "apps_lic.utils" or k.startswith("apps_lic.utils.")]
    for _k in _doomed:
        del sys.modules[_k]
