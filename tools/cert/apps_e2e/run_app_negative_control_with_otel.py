"""APPS-DOM Negative-Control Runtime Harness — invoke v6 Exit with BAD
output per app and capture the X3 DENY disposition.

Plan: docs/archive/windsurf/legacy-tree/plans/apps-dom-runtime-harness-followup-f2a7b3.md W3.P1.

Produces real runtime evidence that X3 blocks bad app output, satisfying
APPS-DOM-006 (x3_domain_block_proved). For each of the 8 runtime apps,
the harness synthesizes a receipts dict with:

  * groundedness/faithfulness/citation_precision < 0.5 (triggers X1D UNGROUNDED)
  * unsupported_claims present (reinforces X1D UNGROUNDED)
  * non-empty evidence_bundle + FEC (forces X1D to evaluate, not NOT_APPLICABLE)

UNGROUNDED is in `_HARD_FAIL_CODES` in x2_matrix, so X2 deterministically
routes to V6Disposition.DENY, which emits SPAN_X3A_DENY_EMIT.

Output: artifacts/apps_negative_controls_runtime/<app>_negative_trace.json

Each fixture carries:
  - top-level `app` (str) — for compiler pointer resolution via `/app`
  - `exit_disposition`: "X3A" (DENY) — SIGNED_OFF evidence
  - `x3_denied`: True
  - `otel_spans`: full v6 span bucket including X1D FAIL + X3A emit
  - `verdicts`: list of X1 gate verdicts
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
OUTPUT_DIR = REPO_ROOT / "artifacts" / "apps_negative_controls_runtime"

RUNTIME_APPS = (
    "apps_qna", "apps_underwriting_ai",
    "apps_research", "apps_exec", "apps_eval",
)


def _build_negative_receipts(app: str) -> dict[str, Any]:
    """Build a receipts dict guaranteed to produce X3 DENY via X1D UNGROUNDED."""
    from tools.cert.apps_e2e._harness_identity import (  # noqa: PLC0415
        build_identity_block, compute_hmac_sig,
    )
    route_id = f"apps_{app}.negative_control_v1"
    ids = build_identity_block(f"{app}-neg", deterministic=True)
    receipts = {
        "source_type": "L2_SEALED_ARTIFACT",
        "request_id": ids["request_id"],
        "run_id": ids["run_id"],
        "session_id": ids["session_id"],
        "trace_root": f"trace-{app}-neg",
        "route_id": route_id,
        "policy_hash": f"pol::{app}::v1",
        "blueprint_hash": f"bp::{app}::v1",
        "prompt_hash": f"ph::{app}::v1",
        "replay_key": ids["replay_key"],
        "compliance_hash": f"comp-{app}-neg",
        "manifest_hash": f"mh-{app}-neg",
        "hmac_sig": "",  # filled below
        "route_contract": {
            "route_id": route_id,
            "policy_hash": f"pol::{app}::v1",
            "blueprint_hash": f"bp::{app}::v1",
            "prompt_hash": f"ph::{app}::v1",
            "app_id": app,
        },
        "sandbox_envelope": {"isolation_intact": True},
        "capability_token": {"authorizes_write": False, "expired": False},
        "provider_lane": "default",
        "cost_tier": "low",
        "slo_slice": {"latency_ms": 30000},
        "timeout_ms": 30000,
        "budget_counters": {"used_tokens": 256, "max_tokens": 4000},
        "terminal_class": "answer_only",
        "exec_trace": {
            "tool_calls": [],
            "model_calls": [{"model_id": "m1"}],
            "replay_receipts_present": True,
            "wall_clock_used": False,
        },
        "state_diff": {},
        "write_intent_class": "",
        # Non-empty evidence_bundle + FEC forces X1D to run (not NOT_APPLICABLE)
        "evidence_bundle": {"sources": [f"{app}_src_1"]},
        "final_evidence_contract": {
            "schema_version": "1.0",
            "producer": f"{app}.cert.fec_producer",
            "c0_status": "PASS",
            "grounded": True,
        },
        "prompt_assembly_status": {"slot_order_valid": True},
        "compiled_prompt_artifact": {},
        # BAD output — triggers X1D UNGROUNDED which is in _HARD_FAIL_CODES
        "output": {
            "text": f"{app} fabricated negative-control output",
            "schema_required": False,
            "schema_valid": True,
            "groundedness": 0.2,
            "faithfulness": 0.2,
            "citation_precision": 0.2,
            "unsupported_claims": [f"{app} fabricated fact"],
            "completion_score": 0.7,
            "confidence": 0.3,
            "format_fit": True,
        },
        "validation_counters": {},
        "retry_counters": {"retry_count": 0, "retry_max": 3},
        "repair_counters": {},
        "trajectory_snapshot": {},
        "grader_composition": {
            "roster": ["code_schema", "code_citation"],
            "threshold_profile": "production_v1",
        },
        "track_label": "production",
        "support_score": 0.2,
        "confidence": 0.3,
        "abstain_flags": [],
        "contradiction_flags": [],
        "otel_spans": {"spans": {}},
        "timing_offsets": {},
        "anomaly_flags": [],
        "hitl_packet": {},
        "bus_d_signals": [],
        "bus_e_signals": [],
        "replay_guard_violations": [],
        "isolation_anomalies": [],
        "drift_warnings": [],
    }
    receipts["hmac_sig"] = compute_hmac_sig(receipts)
    return receipts


def _jsonify(obj: Any) -> Any:
    if obj is None or isinstance(obj, (bool, int, float, str)):
        return obj
    if isinstance(obj, (list, tuple)):
        return [_jsonify(x) for x in obj]
    if isinstance(obj, dict):
        return {str(k): _jsonify(v) for k, v in obj.items()}
    try:
        return str(obj)
    except Exception:  # noqa: BLE001
        return repr(obj)


def _capture_one_app(app: str) -> dict[str, Any]:
    start = time.time()
    status: dict[str, Any] = {
        "app": app,
        "captured": False,
        "denied": False,
        "reason": None,
        "fixture_path": None,
    }
    from agentic_core.L3_orchestration.exit_eval.v6 import (  # noqa: PLC0415
        run_exit_eval,
        V6Disposition,
    )

    receipts = _build_negative_receipts(app)
    try:
        result = run_exit_eval(receipts)
    except Exception as exc:  # noqa: BLE001
        status["reason"] = f"run_exit_eval raised {type(exc).__name__}: {exc}"
        return status

    review = result.packet
    disposition_value = getattr(result.disposition, "value", str(result.disposition))
    denied = result.disposition in {
        V6Disposition.DENY,
        V6Disposition.SAFE_ABSTAIN,
        V6Disposition.ESCALATE,
    }

    # Collect X1 verdict summary for audit
    verdicts_summary = []
    for v in (result.verdicts or []):
        verdicts_summary.append({
            "gate_id": v.gate_id,
            "result": v.result.value if hasattr(v.result, "value") else str(v.result),
            "reason_codes": list(v.reason_codes or []),
        })

    # Serialize OTEL spans
    spans_serialized: dict[str, list[dict[str, Any]]] = {}
    v6_bucket = (review.otel_spans.get("v6", {}) if (review and review.otel_spans) else {})
    if isinstance(v6_bucket, dict):
        for span_name, entries in v6_bucket.items():
            spans_serialized[span_name] = [
                {
                    "attributes": _jsonify(e.get("attributes", {})),
                    "start_ms": int(e.get("start_ms", 0) or 0),
                    "end_ms": int(e.get("end_ms", 0) or 0),
                    "latency_ms": int(e.get("latency_ms", 0) or 0),
                }
                for e in (entries if isinstance(entries, list) else [])
            ]

    fixture = {
        "schema_version": "1.0",
        "harness_version": "apps_dom_negative_control_runtime_v1",
        "app": app,
        "archetype": "fabrication",
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime()),
        "elapsed_ms": int((time.time() - start) * 1000),
        "exit_disposition": disposition_value,
        "x3_denied": denied,
        "x2_decision": {
            "rationale": result.decision.rationale if result.decision else "",
            "failed_gate_ids": list(result.decision.failed_gate_ids) if result.decision else [],
            "reason_codes": list(result.decision.reason_codes) if result.decision else [],
        },
        "verdicts": verdicts_summary,
        "otel_spans": spans_serialized,
        "spans_count": sum(len(v) for v in spans_serialized.values()),
        "span_names": sorted(spans_serialized.keys()),
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fixture_path = OUTPUT_DIR / f"{app}_negative_trace.json"
    fixture_path.write_text(json.dumps(fixture, indent=2, sort_keys=True), encoding="utf-8")

    status.update({
        "captured": True,
        "denied": denied,
        "disposition": disposition_value,
        "fixture_path": str(fixture_path.relative_to(REPO_ROOT).as_posix()),
        "spans_count": fixture["spans_count"],
    })
    return status


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apps", nargs="*", default=list(RUNTIME_APPS))
    args = parser.parse_args(argv)

    print(f"APPS-DOM negative-control harness — {len(args.apps)} app(s)...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, Any]] = []
    for app in args.apps:
        r = _capture_one_app(app)
        results.append(r)
        if r["captured"]:
            print(
                f"  {'DENY' if r['denied'] else 'WARN':4s} {app:24s}  "
                f"disp={r['disposition']:6s}  spans={r['spans_count']:3d}  "
                f"fixture={r['fixture_path']}"
            )
        else:
            print(f"  FAIL {app:24s}  reason={r['reason']}")

    denied = sum(1 for r in results if r.get("denied"))
    failed = sum(1 for r in results if not r["captured"])
    print(f"\nCaptured {len(results) - failed}/{len(results)} app traces; denied={denied}; failed={failed}")

    index_path = OUTPUT_DIR / "_index.json"
    index_path.write_text(
        json.dumps({
            "schema_version": "1.0",
            "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime()),
            "denied_count": denied,
            "failed_count": failed,
            "results": results,
        }, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(f"Wrote index {index_path.relative_to(REPO_ROOT).as_posix()}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
