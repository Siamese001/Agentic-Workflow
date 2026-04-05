"""conftest for apps_lic/reasoning tests — diagnoses apps_lic.utils shadow."""
import sys
from pathlib import Path

_REPO_ROOT = str(Path(__file__).resolve().parents[4])
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

# Diagnostic: check apps_lic.utils state at conftest load time
_mod = sys.modules.get("apps_lic.utils")
if _mod is not None and not hasattr(_mod, "__path__"):
    # It's a non-package — log and purge
    import warnings
    warnings.warn(
        f"[SHADOW DETECTED] apps_lic.utils is non-package at conftest load: "
        f"file={getattr(_mod,'__file__',None)}",
        stacklevel=1,
    )
    _doomed = [k for k in list(sys.modules) if k == "apps_lic.utils" or k.startswith("apps_lic.utils.")]
    for _k in _doomed:
        del sys.modules[_k]
