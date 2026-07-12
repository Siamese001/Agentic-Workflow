"""Shadow-reindex L0 ingress + run G_REACH without full ADG regen.

Usage:
  python tools/analysis/p0_incremental_reach_proof.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

REACH_INGRESS_FILES = [
    "agentic_core/L0_routing/package_driven_l0_binding.py",
    "agentic_core/L0_routing/c0_retrieval/__init__.py",
    "agentic_core/L0_routing/c0_retrieval/dispatcher.py",
    "agentic_core/knowledge/__init__.py",
    "agentic_core/knowledge/gates/__init__.py",
    "agentic_core/knowledge/retrieval/__init__.py",
    "agentic_core/knowledge/enrichment/__init__.py",
    "agentic_core/prompt_governance/__init__.py",
    "agentic_core/prompt_governance/validation/__init__.py",
    "agentic_core/prompt_governance/contracts/__init__.py",
    "agentic_core/prompt_governance/security/__init__.py",
    "agentic_core/prompt_governance/core/__init__.py",
    "agentic_core/prompt_governance/prompt_assembly/__init__.py",
]


def main() -> int:
    from importlib import import_module

    from ops_scripts.ci._adg_wiring_gate_base import (  # guardian: allow-layer-violation -- L_TOOLS->L_OPS ADG proof harness
        connect_snapshot,
        latest_snapshot,
    )

    from tools.adg.incremental_reindex import IncrementalReindexer

    source = latest_snapshot()
    shadow = ROOT / "artifacts" / "adg" / "shadow_reach_proof.sqlite"
    reindexer = IncrementalReindexer(source_snapshot=source, shadow_snapshot=shadow, repo_root=ROOT)
    reindexer.initialize_shadow(overwrite=True)
    for rel in REACH_INGRESS_FILES:
        reindexer.reindex_file(rel)

    mod = import_module("ops_scripts.ci.check_graph_reach")
    conn = connect_snapshot(shadow)
    try:
        violations = mod.GraphReachGate().run(conn)
    finally:
        conn.close()

    out_dir = ROOT / "artifacts" / "adg" / "p0_slices"
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "gate_id": "G_REACH_l0_reachability",
        "snapshot": shadow.relative_to(ROOT).as_posix(),
        "count": len(violations),
        "violations": [
            {
                "subject": v.subject,
                "rule": v.rule,
                "detail": v.detail,
                "extra": v.extra,
            }
            for v in violations[:200]
        ],
        "truncated": len(violations) > 200,
    }
    proof = out_dir / "G_REACH_l0_reachability_shadow_proof.json"
    proof.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"[p0_incremental_reach] shadow={shadow.relative_to(ROOT).as_posix()}")
    print(f"[p0_incremental_reach] G_REACH count={len(violations)}")
    print(f"[p0_incremental_reach] proof={proof.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
