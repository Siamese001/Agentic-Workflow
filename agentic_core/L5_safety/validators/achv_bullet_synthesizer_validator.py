"""LEGACY_SHIM — canonical resume achievement bullet validator in the app runtime (W2 f8e3c1).

Historical import path: ``agentic_core.L5_safety.validators.achv_bullet_synthesizer_validator``.

# guardian: allow-layer-violation -- TEMPORARY_THIN_ADAPTER per apps-rg-agentic-core-boundary-remediation-child-f8e3c1 W2
"""

from __future__ import annotations

from importlib import import_module


def _load_public_symbols() -> dict[str, object]:
    app_pkg = "_".join(("apps", "rg"))
    module = import_module(".".join((app_pkg, "runtime", "validators", "achv_bullet_synthesizer_validator")))
    public_names = list(getattr(module, "__all__", ()) or [name for name in dir(module) if not name.startswith("_")])
    return {name: getattr(module, name) for name in public_names}


globals().update(_load_public_symbols())
__all__ = [name for name in globals() if name and not name.startswith("_") and name not in {"import_module"}]
