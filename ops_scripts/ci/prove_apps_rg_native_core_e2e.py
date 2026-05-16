#!/usr/bin/env python3
"""Native apps_rg core E2E certification proof gate (opt-in harness).

Bypass: APPS_RG_NATIVE_CORE_E2E_BYPASS=1
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))


def _bindings_apps_import_scan() -> list[str]:
    from agentic_core.runtime.bindings.app_binding_validation import (
        scan_generic_bindings_tree_for_apps_imports,
    )

    return scan_generic_bindings_tree_for_apps_imports()


def main() -> int:
    if os.environ.get("APPS_RG_NATIVE_CORE_E2E_BYPASS", "").strip() in ("1", "true", "yes"):
        print("[APPS-RG-NATIVE-CORE-E2E] BYPASS=1")
        return 0

    errors: list[str] = []
    hits = _bindings_apps_import_scan()
    if hits:
        errors.append("apps_* import(s) under agentic_core/runtime/bindings: " + "; ".join(hits))

    try:
        from agentic_core.runtime.bindings.native_contract_chain import (
            build_native_core_contract_chain_from_binding,
        )

        assert callable(build_native_core_contract_chain_from_binding)
    except ImportError as exc:
        errors.append(f"native_contract_chain_import:{exc}")

    tests = [
        "tests/_apps_contract/test_apps_rg_native_core_e2e_entry.py",
        "tests/_apps_contract/test_apps_rg_native_core_u0_l1_l0_chain.py",
        "tests/_apps_contract/test_apps_rg_native_core_evidence_pa_l2_chain.py",
        "tests/_apps_contract/test_apps_rg_native_core_ag5_exit_chain.py",
        "tests/_apps_contract/test_apps_rg_native_core_runtime_exhaust_l6_handoff.py",
        "tests/_apps_contract/test_apps_rg_native_core_e2e_certification.py",
    ]
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "--override-ini=addopts=-q",
        *[str(_REPO / t) for t in tests],
        "-q",
    ]
    proc = subprocess.run(cmd, cwd=str(_REPO), check=False)
    if proc.returncode != 0:
        errors.append("pytest_native_core_e2e_suite_nonzero_exit")

    if errors:
        print("[APPS-RG-NATIVE-CORE-E2E] FAIL:", "; ".join(errors))
        return 1

    print("[APPS-RG-NATIVE-CORE-E2E] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
