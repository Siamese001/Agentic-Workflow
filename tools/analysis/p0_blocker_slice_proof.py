"""Prove P0 pipeline blockers after authority + J1 slice (shadow J1 optional)."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

CANONICAL = ROOT / "artifacts" / "adg" / "adg_indexed_05252026_1012.sqlite"
DISPATCHER = "agentic_core/L0_routing/c0_retrieval/dispatcher.py"


def main() -> int:
    from importlib import import_module

    from ops_scripts.ci._adg_wiring_gate_base import connect_snapshot  # guardian: allow-layer-violation -- L_TOOLS->L_OPS ADG proof harness
    from ops_scripts.ci.check_authority_boundary_breaches import (  # guardian: allow-layer-violation -- L_TOOLS->L_OPS ADG proof harness
        authority_breaches_fail_adr071,
    )
    from tools.adg.incremental_reindex import IncrementalReindexer

    auth_conn = connect_snapshot(CANONICAL)
    try:
        failed, per_src, reasons = authority_breaches_fail_adr071(auth_conn)
    finally:
        auth_conn.close()

    shadow = ROOT / "artifacts" / "adg" / "shadow_j1_wiring.sqlite"
    if shadow.is_file():
        shadow.unlink()
    shutil.copy2(CANONICAL, shadow)
    reindexer = IncrementalReindexer(
        source_snapshot=CANONICAL, shadow_snapshot=shadow, repo_root=ROOT
    )
    reindexer.initialize_shadow(overwrite=True)
    reindexer.reindex_file(DISPATCHER)

    j1 = import_module("ops_scripts.ci.check_canonical_pipeline_wiring")
    j1_conn = connect_snapshot(shadow)
    try:
        j1_violations = j1.CanonicalPipelineWiringGate().run(j1_conn)
    finally:
        j1_conn.close()

    j1_fail = [v for v in j1_violations if getattr(v, "severity", "fail") != "warn"]

    payload = {
        "authority_boundary": {
            "snapshot": CANONICAL.name,
            "pass": not failed,
            "total": sum(per_src.values()),
            "reasons": reasons,
            "per_src": per_src,
        },
        "J1_canonical_pipeline_wiring": {
            "snapshot": shadow.name,
            "pass": len(j1_fail) == 0,
            "fail_count": len(j1_fail),
            "warn_count": len(j1_violations) - len(j1_fail),
            "failures": [{"subject": v.subject, "rule": v.rule, "detail": v.detail} for v in j1_fail],
        },
    }
    out = ROOT / "artifacts" / "adg" / "p0_slices" / "p0_blocker_slice_proof.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"[p0_blocker_slice] authority pass={not failed} total={sum(per_src.values())}")
    print(f"[p0_blocker_slice] J1 shadow pass={len(j1_fail)==0} fail={len(j1_fail)} warn={payload['J1_canonical_pipeline_wiring']['warn_count']}")
    print(f"[p0_blocker_slice] proof={out.relative_to(ROOT).as_posix()}")
    return 0 if (not failed and len(j1_fail) == 0) else 1


if __name__ == "__main__":
    raise SystemExit(main())
