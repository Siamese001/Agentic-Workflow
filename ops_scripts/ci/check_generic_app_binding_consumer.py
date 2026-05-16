#!/usr/bin/env python3
"""CI smoke: generic binding consumer validates the native-core fixture package."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]


def main() -> int:
    import sys

    if str(_REPO) not in sys.path:
        sys.path.insert(0, str(_REPO))

    # Imports after sys.path not needed when run as module from repo root
    from agentic_core.runtime.bindings.app_binding_loader import load_app_binding_package
    from agentic_core.runtime.bindings.app_binding_validation import validate_app_binding_package

    pkg = load_app_binding_package(_REPO / "tests/_core_contract/fixtures/apps_rg_binding_package")
    result = validate_app_binding_package(pkg)
    if result.status != "PASS":
        print("[GENERIC-APP-BINDING-CONSUMER] FAIL:", "; ".join(result.errors[:12]))
        return 1
    print("[GENERIC-APP-BINDING-CONSUMER] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
