#!/usr/bin/env python3
"""Advisory L0/L3 parent invariant pack (plan l0-l3-parent-gap-remediation W2.1)."""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

_CHECKS: list[tuple[str, bool, str]] = []


def _record(name: str, ok: bool, detail: str) -> None:
    _CHECKS.append((name, ok, detail))


def main() -> int:
    # NC-L0-001: apps_rg route evidence module present
    p = _REPO / "apps_rg" / "runtime" / "bindings" / "l0_route_evidence.py"
    _record("NC-L0-001_route_evidence_module", p.is_file(), str(p))

    # NC-L0-002: apps_rg l3_binding present
    p3 = _REPO / "apps_rg" / "runtime" / "bindings" / "l3_binding.py"
    _record("NC-L0-002_apps_rg_l3_binding", p3.is_file(), str(p3))

    try:
        from agentic_core.runtime.contracts.route_contract import RouteContract

        fields = {f.name for f in RouteContract.__dataclass_fields__.values()}
        _record(
            "NC-L0-003_route_digest_field",
            "route_digest" in fields,
            "route_digest on RouteContract",
        )
        _record(
            "NC-L0-004_route_policy_ref_field",
            "route_policy_ref" in fields,
            "route_policy_ref on RouteContract",
        )
        _record(
            "NC-L0-005_hmac_sig_field",
            "hmac_sig" in fields,
            "hmac_sig on RouteContract",
        )
    except Exception as exc:  # guardian: allow-broad-exception -- gate must report
        _record("NC-L0-003_route_contract_import", False, str(exc))

    try:
        mod = importlib.import_module("apps_rg.runtime.bindings.l3_binding")
        _record(
            "NC-L3-001_l3_orchestrate_apps_rg",
            hasattr(mod, "l3_orchestrate_apps_rg"),
            "callable exported",
        )
    except Exception as exc:  # guardian: allow-broad-exception -- gate must report
        _record("NC-L3-001_l3_import", False, str(exc))

    v12_arch = _REPO / "agentic_core" / "L0_routing" / "_archive" / "v12" / "reasoning" / "v12_route_selector.py"
    v15_yaml = _REPO / "config" / "routing" / "fallback_chains_v15.yaml"
    _record(
        "NC-L0-V15-001_v12_archived",
        v12_arch.is_file(),
        str(v12_arch),
    )
    _record(
        "NC-L0-V15-002_v15_fallback_yaml",
        v15_yaml.is_file(),
        str(v15_yaml),
    )

    failed = [c for c in _CHECKS if not c[1] and not c[0].startswith("INFO")]
    for name, ok, detail in _CHECKS:
        tag = "PASS" if ok else "FAIL"
        print(f"  {name:40} {tag}  {detail}")
    if failed:
        print(f"\nFAIL {len(failed)} required check(s)")
        return 1
    print(f"\nOK {len(_CHECKS)} checks ({sum(1 for c in _CHECKS if c[0].startswith('INFO'))} informational)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
