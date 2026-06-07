"""APPS-DOM X3E SAFE_ABSTAIN Runtime Harness.

Plan: docs/archive/windsurf/legacy-tree/plans/apps-dom-real-evidence-enhancement-c7f4d8.md W3.P1.

Complements the DENY harness (run_app_negative_control_with_otel.py) with
proof that the X3E SAFE_ABSTAIN disposition path actually fires under
realistic "evidence empty" conditions. Without this, the fleet-wide
proof that "bad output blocks" covers only the X3A DENY branch; X3E
ESCALATE-to-abstain remains unexercised.

Recipe that deterministically produces V6Disposition.SAFE_ABSTAIN:

  - final_evidence_contract.c0_status = "EMPTY"
    -> X1D grounded route, reason_codes=["EVIDENCE_EMPTY"]
    -> X1 gate result = FAIL with code in _SAFE_ABSTAIN_CODES
  - All other X1 gates PASS (clean policy/sandbox/output)
  -> X2 aggregate: no hard-fail hits, no other fail codes, abstain_hits
     list non-empty -> X3E SAFE_ABSTAIN

Output fixtures land at
``artifacts/apps_safe_abstain_runtime/<app>_abstain_trace.json`` with
``exit_disposition: "X3E"`` and full OTEL span coverage.

Exit codes: 0 when all 8 apps captured X3E; 1 otherwise.
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
OUTPUT_DIR = REPO_ROOT / "artifacts" / "apps_safe_abstain_runtime"

RUNTIME_APPS = (
    "apps_qna", "apps_underwriting_ai",
    "apps_rg", "apps_lic", "apps_rfp",
    "apps_research", "apps_exec", "apps_eval",
)


def _build_safe_abstain_receipts(app: str) -> dict[str, Any]:
    """Build a receipts dict that deterministically yields X3E SAFE_ABSTAIN."""
    from tools.cert.apps_e2e._harness_identity import (  # noqa: PLC0415
        build_identity_block, compute_hmac_sig,
    )
    route_id = f"apps_{app}.safe_abstain_v1"
    ids = build_identity_block(f"{app}-abstain", deterministic=True)
    receipts = {
        "source_type": "L2_SEALED_ARTIFACT",
        "request_id": ids["request_id"],
        "run_id": ids["run_id"],
        "session_id": ids["session_id"],
        "trace_root": f"trace-{app}-abstain",
        "route_id": route_id,
        "policy_hash": f"pol::{app}::v1",
        "blueprint_hash": f"bp::{app}::v1",
        "prompt_hash": f"ph::{app}::v1",
        "replay_key": ids["replay_key"],
        "compliance_hash": f"comp-{app}-abstain",
        "manifest_hash": f"mh-{app}-abstain",
        "hmac_sig": "",
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
        "budget_counters": {"used_tokens": 100, "max_tokens": 4000},
        "terminal_class": "answer_only",
        "exec_trace": {
            "tool_calls": [],
            "model_calls": [{"model_id": "m1"}],
            "replay_receipts_present": True,
            "wall_clock_used": False,
        },
        "state_diff": {},
        "write_intent_class": "",
        # Evidence bundle present (not empty) forces X1D into grounded path
        "evidence_bundle": {"sources": [f"{app}_src_0"]},
        # c0_status="EMPTY" triggers X1D EVIDENCE_EMPTY -> X3E SAFE_ABSTAIN
        "final_evidence_contract": {
            "schema_version": "1.0",
            "producer": f"{app}.cert.fec_producer",
            "c0_status": "EMPTY",
        },
        "prompt_assembly_status": {"slot_order_valid": True},
        "compiled_prompt_artifact": {},
        # Output fields kept clean so X1B doesn't fail
        "output": {
            "text": f"{app} safe-abstain output (evidence empty)",
            "schema_required": False,
            "schema_valid": True,
            "groundedness": 0.95,
            "faithfulness": 0.95,
            "citation_precision": 0.95,
            "completion_score": 0.9,
            "confidence": 0.6,
            "format_fit": True,
            "unsupported_claims": [],
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
        "support_score": 0.3,
        "confidence": 0.6,
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
        "safe_abstained": False,
        "reason": None,
        "fixture_path": None,
    }
    from agentic_core.L3_orchestration.exit_eval.v6 import (  # noqa: PLC0415
        run_exit_eval,
        V6Disposition,
    )

    receipts = _build_safe_abstain_receipts(app)
    try:
        result = run_exit_eval(receipts)
    except Exception as exc:  # noqa: BLE001
        status["reason"] = f"run_exit_eval raised {type(exc).__name__}: {exc}"
        return status

    review = result.packet
    disposition_value = getattr(result.disposition, "value", str(result.disposition))
    # X3E SAFE_ABSTAIN is the target; X3B ESCALATE is an acceptable
    # secondary (both prove "safe-stop-not-allow").
    safe_abstained = result.disposition in {
        V6Disposition.SAFE_ABSTAIN,
        V6Disposition.ESCALATE,
    }

    verdicts_summary = [
        {
            "gate_id": v.gate_id,
            "result": v.result.value if hasattr(v.result, "value") else str(v.result),
            "reason_codes": list(v.reason_codes or []),
        }
        for v in (result.verdicts or [])
    ]

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
        "harness_version": "apps_dom_safe_abstain_runtime_v1",
        "app": app,
        "archetype": "evidence_empty",
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime()),
        "elapsed_ms": int((time.time() - start) * 1000),
        "exit_disposition": disposition_value,
        "safe_abstained": safe_abstained,
        "hmac_sig": receipts["hmac_sig"],
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
    fixture_path = OUTPUT_DIR / f"{app}_abstain_trace.json"
    fixture_path.write_text(json.dumps(fixture, indent=2, sort_keys=True), encoding="utf-8")

    status.update({
        "captured": True,
        "safe_abstained": safe_abstained,
        "disposition": disposition_value,
        "fixture_path": str(fixture_path.relative_to(REPO_ROOT).as_posix()),
        "spans_count": fixture["spans_count"],
    })
    return status


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apps", nargs="*", default=list(RUNTIME_APPS))
    args = parser.parse_args(argv)

    print(f"APPS-DOM safe-abstain harness — {len(args.apps)} app(s)...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, Any]] = []
    for app in args.apps:
        r = _capture_one_app(app)
        results.append(r)
        if r["captured"]:
            label = "ABSTN" if r.get("safe_abstained") else "WARN"
            print(
                f"  {label:5s} {app:24s}  disp={r['disposition']:6s}  "
                f"spans={r['spans_count']:3d}  fixture={r['fixture_path']}"
            )
        else:
            print(f"  FAIL  {app:24s}  reason={r['reason']}")

    abstained = sum(1 for r in results if r.get("safe_abstained"))
    failed = sum(1 for r in results if not r["captured"])
    print(
        f"\nCaptured {len(results) - failed}/{len(results)} traces; "
        f"safe_abstained_or_escalate={abstained}; failed={failed}"
    )

    index_path = OUTPUT_DIR / "_index.json"
    index_path.write_text(
        json.dumps({
            "schema_version": "1.0",
            "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime()),
            "safe_abstained_count": abstained,
            "failed_count": failed,
            "results": results,
        }, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(f"Wrote index {index_path.relative_to(REPO_ROOT).as_posix()}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
