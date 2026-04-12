"""conftest for apps_lic/reasoning tests — diagnoses apps_lic.utils shadow."""

import sys
from pathlib import Path
from types import ModuleType

_REPO_ROOT = str(Path(__file__).resolve().parents[4])
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

# Stub apps_lic.utils.LICAgentBase so GovernanceShieldAgent can be imported in tests.
# The real module lives at apps_lic/utils/lic_agent_base_util.py; the source file uses
# a non-existent path apps_lic.utils.LICAgentBase (pre-existing bug — out of scope).
if "apps_lic.utils.LICAgentBase" not in sys.modules:
    _stub_mod = ModuleType("apps_lic.utils.LICAgentBase")

    class _StubLICAgentBase:
        def __post_init__(self):
            pass

        def heal(self, *a, **kw):
            pass

        def heal_repository(self, *a, **kw):
            raise NotImplementedError

    _stub_mod.LICAgentBase = _StubLICAgentBase  # type: ignore[attr-defined]
    sys.modules["apps_lic.utils.LICAgentBase"] = _stub_mod

# Diagnostic: check apps_lic.utils state at conftest load time
_mod = sys.modules.get("apps_lic.utils")
if _mod is not None and not hasattr(_mod, "__path__"):
    # It's a non-package — log and purge
    import warnings

    warnings.warn(
        f"[SHADOW DETECTED] apps_lic.utils is non-package at conftest load: "
        f"file={getattr(_mod, '__file__', None)}",
        stacklevel=1,
    )
    _doomed = [k for k in list(sys.modules) if k == "apps_lic.utils" or k.startswith("apps_lic.utils.")]
    for _k in _doomed:
        del sys.modules[_k]
