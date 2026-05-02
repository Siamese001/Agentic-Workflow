"""All-apps matrix builder.

Reads every per-app proof bundle under artifacts/certification/apps_e2e/
and produces apps_e2e_matrix.json. The matrix MUST be derived from
bundles, never hand-authored.

Usage:
    python -m tools.certification.apps_e2e.matrix_builder
    python -m tools.certification.apps_e2e.matrix_builder --print-table
"""
from __future__ import annotations

import argparse
import json
import sys
import uuid
from typing import Any

from tools.certification.apps_e2e import MATRIX_SCHEMA_VERSION
from tools.certification.apps_e2e.app_specs import APP_SPECS, AppSpec
from tools.certification.apps_e2e.hash_utils import (
    REPO_ROOT, git_head, relative_to_repo, utc_now_iso, write_json,
)
from tools.certification.apps_e2e.paths import MATRIX_PATH, AppCertPaths


def _row_for(spec: AppSpec) -> dict[str, Any]:
    paths = AppCertPaths(spec.app_name)
    bundle: dict[str, Any] | None = None
    if paths.proof_bundle.exists():
        try:
            bundle = json.loads(paths.proof_bundle.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            bundle = None

    discovered = True
    runnable = spec.runnable
    proof_ref = relative_to_repo(paths.proof_bundle) if paths.proof_bundle.exists() else None

    # Compute certification_level for this row. ALWAYS recomputed by the
    # matrix builder — bundle-declared certification_level is never trusted
    # (amendment 4). Imported lazily to avoid circular dependencies.
    from tools.certification.apps_e2e.certification_levels import (
        compute_level as _compute_cert_level,
    )
    _row_level = str(_compute_cert_level(bundle, spec, violations=()).value)

    # Default fields when bundle missing
    if bundle is None:
        return {
            "app_name": spec.app_name,
            "certification_level": _row_level,  # W1.3 — verifier-recomputed
            "discovered": discovered,
            "entrypoint_command": spec.entrypoint_command if runnable else None,
            "entrypoint_runnable": runnable,
            "proof_bundle_ref": None,
            "success": False,
            "blocking_gaps": ["proof_bundle_not_emitted"],
            "agentic_core_spine_status": "spine_unverified",
            "app_overlay_authority_status": "overlay_unknown",
            "static_dag_status": "unknown" if spec.expects_static_dag else "not_applicable",
            "l3_runtime_status": "missing",
            "c0_status": "missing" if spec.expects_c0_grounding else "not_applicable",
            "prompt_assembly_status": "missing" if spec.expects_prompt_assembly else "not_applicable",
            "l2_status": "missing" if spec.expects_l2_execution else "not_applicable",
            "exit_status": "missing",
            "uwg_l4_status": "missing" if spec.expects_durable_mutation else "not_applicable",
            "l6_status": "missing",
            "otel_status": "missing",
            "verifier_status": "skipped",
        }

    static_dag_present = bool((bundle.get("static_dag_proof_inline_summary") or {}).get("present"))
    static_dag_status = (
        "not_applicable" if not spec.expects_static_dag and not static_dag_present
        else ("present" if static_dag_present else "missing")
    )

    l3_recv = bundle.get("runtime_l3_receipt_ref")
    l3_bypass = bundle.get("runtime_l3_bypass_ref")
    if l3_recv:
        l3_status = "ran"
    elif l3_bypass:
        l3_status = "bypassed"
    else:
        l3_status = "missing"

    def _stage_status(present_ref: str | None, expected: bool) -> str:
        if present_ref:
            return "present"
        return "missing" if expected else "not_applicable"

    return {
        "app_name": spec.app_name,
        "certification_level": _row_level,  # W1.3 — verifier-recomputed
        "discovered": discovered,
        "entrypoint_command": bundle.get("entrypoint_command"),
        "entrypoint_runnable": runnable,
        "proof_bundle_ref": proof_ref,
        "success": bool(bundle.get("success")),
        "blocking_gaps": list(bundle.get("blocking_gaps") or []),
        "agentic_core_spine_status": bundle.get("agentic_core_spine_status", "spine_unverified"),
        "app_overlay_authority_status": bundle.get("app_overlay_authority_status", "overlay_unknown"),
        "static_dag_status": static_dag_status,
        "l3_runtime_status": l3_status,
        "c0_status": _stage_status(bundle.get("runtime_c0_receipt_ref"), spec.expects_c0_grounding),
        "prompt_assembly_status": _stage_status(bundle.get("runtime_prompt_assembly_ref"), spec.expects_prompt_assembly),
        "l2_status": _stage_status(bundle.get("runtime_l2_artifact_ref"), spec.expects_l2_execution),
        "exit_status": "present" if bundle.get("runtime_exit_disposition_ref") else "missing",
        "uwg_l4_status": _stage_status(bundle.get("runtime_uwg_receipt_ref"), spec.expects_durable_mutation),
        "l6_status": "present" if bundle.get("runtime_exhaust_ref") else "missing",
        "otel_status": (
            "synthetic" if bundle.get("synthetic_trace_detected")
            else ("present" if bundle.get("otel_or_runtime_trace_ref") else "missing")
        ),
        "verifier_status": "pass" if bundle.get("success") else "fail",
    }


def build_matrix() -> dict[str, Any]:
    rows = [_row_for(spec) for spec in APP_SPECS]
    commit, _ = git_head()
    # Standard totals
    totals = {
        "discovered": sum(1 for r in rows if r["discovered"]),
        "runnable": sum(1 for r in rows if r["entrypoint_runnable"]),
        "succeeded": sum(1 for r in rows if r["success"]),
        "failed": sum(1 for r in rows if not r["success"] and r["proof_bundle_ref"]),
        "not_run": sum(1 for r in rows if not r["proof_bundle_ref"]),
    }
    # W1.3 — certification-level breakdown. Sum MUST equal discovered.
    from tools.certification.apps_e2e.certification_levels import CertificationLevel
    level_breakdown = {lvl.value: 0 for lvl in CertificationLevel}
    for r in rows:
        lvl = r.get("certification_level") or "EMITS_BUNDLE"
        if lvl in level_breakdown:
            level_breakdown[lvl] += 1
        else:
            level_breakdown[lvl] = 1
    totals["certification_level_breakdown"] = level_breakdown
    return {
        "matrix_schema_version": MATRIX_SCHEMA_VERSION,
        "generated_at_utc": utc_now_iso(),
        "git_commit": commit,
        "harness_run_id": f"matrix-{uuid.uuid4().hex[:16]}",
        "apps": rows,
        "totals": totals,
    }


def print_table(matrix: dict[str, Any]) -> None:
    rows = matrix["apps"]
    cols = (
        ("App", "app_name", 22),
        ("CertLevel", "certification_level", 26),  # W1.3
        ("Entry", "entrypoint_runnable", 5),
        ("L3", "l3_runtime_status", 10),
        ("Spine", "agentic_core_spine_status", 16),
        ("OTEL", "otel_status", 9),
        ("Exit", "exit_status", 8),
        ("Exhaust", "l6_status", 8),
        ("Success", "success", 7),
        ("Gap", "blocking_gaps", 30),
    )
    header = "  ".join(f"{name:<{w}}" for name, _, w in cols)
    print(header)
    print("-" * len(header))
    for r in rows:
        cells = []
        for _, key, w in cols:
            v = r.get(key)
            if isinstance(v, list):
                v = ",".join(v[:2])[:w]
            elif isinstance(v, bool):
                v = "true" if v else "false"
            else:
                v = "" if v is None else str(v)
            cells.append(f"{v[:w]:<{w}}")
        print("  ".join(cells))
    t = matrix["totals"]
    print("-" * len(header))
    print(f"TOTALS: discovered={t['discovered']} runnable={t['runnable']} "
          f"succeeded={t['succeeded']} failed={t['failed']} not_run={t['not_run']}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="matrix_builder", add_help=True)
    p.add_argument("--print-table", action="store_true")
    args = p.parse_args(argv)

    matrix = build_matrix()
    digest, size = write_json(MATRIX_PATH, matrix)
    print(f"[matrix] wrote {relative_to_repo(MATRIX_PATH)} ({size} B, sha256={digest[:12]}…)")
    if args.print_table:
        print()
        print_table(matrix)
    return 0


if __name__ == "__main__":
    sys.exit(main())
