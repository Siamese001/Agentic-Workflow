"""Reindex L_PG drift source files on a shadow ADG snapshot and run the ratchet gate.

Avoids full ``generate_full_adg`` while proving import-surface fixes against the
current graph.

Usage:
  python tools/analysis/p0_incremental_lpg_proof.py
  ADG_SNAPSHOT=artifacts/adg/shadow_lpg_proof.sqlite python ops_scripts/ci/check_lpg_drift_ratchet.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

# Source files from artifacts/adg/p0_slices/L2_lpg_drift_ratchet.json (2026-05-25).
LPG_DRIFT_SOURCES = [
    "agentic_core/L0_routing/c0_retrieval/dispatcher.py",
    "agentic_core/L0_routing/reasoning/assembly_stage.py",
    "agentic_core/L0_routing/reasoning/prompt_bom_builder.py",
    "agentic_core/L2_execution/apps_research_l2_binding.py",
    "agentic_core/L2_execution/bounded_executor.py",
    "agentic_core/L2_execution/l2_package_driven_executor.py",
    "agentic_core/L2_execution/prompt_envelope_validator.py",
    "agentic_core/L3_orchestration/managed_workflow_runner.py",
    "agentic_core/L3_orchestration/reasoning/engines/context_compaction.py",
    "agentic_core/L3_orchestration/reasoning/engines/graph_aware_indexer.py",
    "agentic_core/L3_orchestration/reasoning/engines/sub_atomic_engine_impl.py",
    "agentic_core/L4_state/utils/memory/template_registry.py",
    "agentic_core/L5_safety/enforcement/canary_token_defense_strategy.py",
    "agentic_core/L6_system_learning/pipelines/meta_learning_pipeline.py",
    "agentic_core/mixins/instructional_injection_mixin.py",
    "agentic_core/mixins/prompt_rendering_mixin.py",
    "apps_research/runtime/profile_builder_adapter.py",
    "apps_rg/runtime/bindings/c0_binding.py",
    "apps_rg/runtime/spine/governed_pa_compose.py",
    "apps_rg/runtime/spine/l2_handoff_receipt.py",
    "apps_shared/proof/scenario_base.py",
    "apps_shared/validators/proof/scenario_base.py",
    "ops_scripts/ci/check_exemplar_coverage.py",
]


def main() -> int:
    from importlib import import_module

    from ops_scripts.ci._adg_wiring_gate_base import (  # guardian: allow-layer-violation -- L_TOOLS->L_OPS ADG proof harness
        connect_snapshot,
        latest_snapshot,
    )

    from tools.adg.incremental_reindex import IncrementalReindexer

    source = latest_snapshot()
    shadow = ROOT / "artifacts" / "adg" / "shadow_lpg_proof.sqlite"
    reindexer = IncrementalReindexer(source_snapshot=source, shadow_snapshot=shadow, repo_root=ROOT)
    reindexer.initialize_shadow(overwrite=True)

    deltas = []
    for rel in LPG_DRIFT_SOURCES:
        delta = reindexer.reindex_file(rel)
        deltas.append(delta.to_dict())

    mod = import_module("ops_scripts.ci.check_lpg_drift_ratchet")
    conn = connect_snapshot(shadow)
    try:
        violations = mod.LpgDriftRatchetGate().run(conn)
    finally:
        conn.close()

    out_dir = ROOT / "artifacts" / "adg" / "p0_slices"
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "gate_id": "L2_lpg_drift_ratchet",
        "snapshot": shadow.relative_to(ROOT).as_posix(),
        "count": len(violations),
        "violations": [
            {
                "subject": v.subject,
                "rule": v.rule,
                "detail": v.detail,
                "extra": v.extra,
            }
            for v in violations
        ],
    }
    proof_path = out_dir / "L2_lpg_drift_ratchet_shadow_proof.json"
    proof_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"[p0_incremental_lpg] shadow={shadow.relative_to(ROOT).as_posix()}")
    print(f"[p0_incremental_lpg] reindexed_files={len(LPG_DRIFT_SOURCES)}")
    print(f"[p0_incremental_lpg] L2_lpg_drift_ratchet count={len(violations)}")
    print(f"[p0_incremental_lpg] proof={proof_path.relative_to(ROOT).as_posix()}")
    return 0 if len(violations) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
