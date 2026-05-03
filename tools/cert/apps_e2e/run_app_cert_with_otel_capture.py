"""APPS-DOM Runtime Harness — invoke v6 Exit pipeline per app + capture OTEL.

Plan: .windsurf/plans/apps-dom-runtime-harness-followup-f2a7b3.md W1.P1.

For each of the 8 runtime apps, this harness:

  1. Loads the app's active eval_rubrics.yaml + threshold_profiles.yaml
  2. Discovers app_id, task_class, rubric_ref, threshold_profile_ref
  3. Builds a run_context with dim_scores satisfying the rubric (PASS path)
  4. Invokes AppSpecificEvaluator.evaluate() directly -> real domain verdict
  5. Builds a base receipts dict, invokes run_exit_eval() -> real X1-X3 spans
  6. Post-hoc enriches the returned packet with the app_specific_eval span
     (deterministic equivalent to what pipeline.py emits internally; its own
     emit path is unreachable without normalize_to_packet populating app_id
     on the packet, which is a separate runtime fix)
  7. Writes the captured OTEL spans + app_specific_eval result to
     artifacts/apps_otel_traces/<app>_cert_trace.json

The resulting fixtures ARE real runtime evidence:
  - AppSpecificEvaluator ran against the app's real rubric + threshold YAML
  - run_exit_eval produced real X1-X3 gate verdicts + spans
  - The exit.app_specific_eval span attrs are computed from the real eval result

What's synthesized vs real:
  - dim_scores in run_context: synthesized to pass the rubric (documented)
  - route_contract metadata: synthesized (no cert run exists yet to borrow)
  - replay hashes: synthesized (deterministic per-app strings)

Exit codes:
  0 — all 8 apps captured successfully
  1 — 1..N apps failed capture (non-fatal, other apps still captured)
  2 — fatal setup error
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
# Ensure REPO_ROOT is on sys.path so `agentic_core.*` resolves when the
# harness is invoked as a script rather than as `python -m`.
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
OUTPUT_DIR = REPO_ROOT / "artifacts" / "apps_otel_traces"

RUNTIME_APPS = (
    "apps_qna", "apps_underwriting_ai",
    "apps_rg", "apps_lic", "apps_rfp",
    "apps_research", "apps_exec", "apps_eval",
)


def _load_yaml(path: Path) -> Any:
    import yaml  # noqa: PLC0415
    if not path.exists():
        return None
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return None


def _discover_app_contract(app: str) -> dict[str, Any] | None:
    """Return {app_id, task_class, rubric_ref, threshold_profile_ref, rubric, threshold}
    or None if the app's contract cannot be resolved."""
    rubric_path = REPO_ROOT / app / "config" / "domain_contract" / "eval_rubrics.yaml"
    thresh_path = REPO_ROOT / app / "config" / "domain_contract" / "threshold_profiles.yaml"
    rubrics = _load_yaml(rubric_path)
    thresholds = _load_yaml(thresh_path)
    if not rubrics or not thresholds:
        return None
    rubric = rubrics[0] if isinstance(rubrics, list) else rubrics
    threshold = thresholds[0] if isinstance(thresholds, list) else thresholds
    if not isinstance(rubric, dict) or not isinstance(threshold, dict):
        return None
    return {
        "app_id": rubric.get("app_id", app),
        "task_class": rubric.get("task_class", ""),
        "rubric_ref": rubric.get("eval_rubric_id", rubric.get("rubric_id", "")),
        "threshold_profile_ref": threshold.get("threshold_profile_id", ""),
        "rubric": rubric,
        "threshold": threshold,
    }


def _synthesize_l2_receipt(app: str, contract: dict[str, Any]) -> dict[str, Any]:
    """Build an L2-receipt-shaped dict that the app's rubric_output_mapper
    can extract real dim_scores from.

    Populates keys that every known `rubric_output_map.yaml` extractor reads:
    output.text / output.citations / output.grounded / output.sections /
    evidence_bundle.sources / template_ids / route_id / etc.
    """
    return {
        "output": {
            "text": f"{app} pass-path synthesized output for runtime harness",
            "schema_valid": True,
            "schema_required": False,
            "format_fit": True,
            "citations": [f"{app}_cite_1", f"{app}_cite_2"],
            "grounded": True,
            "sections": ["intro", "body", "conclusion"],
            "groundedness": 0.95,
            "faithfulness": 0.95,
            "citation_precision": 0.95,
            "completion_score": 0.9,
            "confidence": 0.8,
            "unsupported_claims": [],
            "tracked_metrics": {
                "ttft_ms": 120,
                "ttlt_ms": 840,
                "output_tokens_per_sec": 45.0,
                "n_total_tokens": 256,
                "cost_usd": 0.0012,
            },
        },
        "evidence_bundle": {"sources": [f"{app}_src_a", f"{app}_src_b"]},
        "final_evidence_contract": {
            "schema_version": "1.0",
            "producer": f"{app}.cert.fec_producer",
            "grounded": True,
            "retrieval_sources": [f"{app}_src_a", f"{app}_src_b"],
            "template_ids": [f"{app}_tmpl_1"],
            "route_id": f"{contract['app_id']}.runtime_harness_v1",
            "evidence_sufficiency": "grounded",
        },
        "state_diff": {},
        "route_id": f"{contract['app_id']}.runtime_harness_v1",
        "template_ids": [f"{app}_tmpl_1"],
    }


def _build_pass_run_context(app: str, contract: dict[str, Any]) -> dict[str, Any]:
    """Build a run_context with dim_scores derived from the real mapper when
    the app has a `rubric_output_map.yaml`; otherwise fall back to synthesized
    above-threshold scores.

    The run_context records its dim_scores source so the captured fixture
    can surface `dim_scores_source` for auditability.
    """
    rubric = contract["rubric"]
    threshold = contract["threshold"]
    dim_minimums: dict[str, float] = dict(threshold.get("dimension_minimums", {}) or {})
    intentional_failopen = set(threshold.get("intentional_failopen_dims", []) or [])

    # Build the underlying L2 receipt — same payload the mapper consumes.
    l2_receipt = _synthesize_l2_receipt(app, contract)
    l2_output = l2_receipt["output"]

    # Try the real rubric_output_mapper first.
    mapper_yaml_path = (
        REPO_ROOT / app / "config" / "domain_contract" / "rubric_output_map.yaml"
    )
    dim_scores: dict[str, float] = {}
    dim_evidence: dict[str, list[str]] = {}
    dim_scores_source = "synthetic_fallback"

    if mapper_yaml_path.exists():
        try:
            from apps_shared.cert.rubric_output_mapper import (  # noqa: PLC0415
                map_l2_receipt_to_dim_scores,
            )
            projected = map_l2_receipt_to_dim_scores(l2_receipt, mapper_yaml_path)
            if isinstance(projected, dict):
                mapped_scores = projected.get("dim_scores") or {}
                mapped_evidence = projected.get("dim_evidence") or {}
                if isinstance(mapped_scores, dict) and mapped_scores:
                    dim_scores = {str(k): float(v) for k, v in mapped_scores.items()}
                    if isinstance(mapped_evidence, dict):
                        dim_evidence = {
                            str(k): [str(x) for x in (v if isinstance(v, (list, tuple)) else [])]
                            for k, v in mapped_evidence.items()
                        }
                    dim_scores_source = "mapper"
        except Exception:  # noqa: BLE001
            # guardian: allow-broad-except -- mapper is fail-soft; fall back
            dim_scores = {}

    # Synthesized above-threshold fallback (also fills gaps when mapper
    # only covers a subset of dims).
    for dim in rubric.get("score_dimensions", []):
        if not isinstance(dim, dict):
            continue
        dim_id = dim.get("dimension_id")
        if not isinstance(dim_id, str):
            continue
        if dim_id in dim_scores:
            continue
        if dim_id in intentional_failopen:
            continue
        min_score = float(dim_minimums.get(dim_id, 0.7))
        dim_scores[dim_id] = min(1.0, min_score + 0.05)
        if dim_id not in dim_evidence:
            dim_evidence[dim_id] = [f"{app}_ev_{dim_id}"]

    # Attach dim_scores + dim_evidence to the L2 output so the evaluator
    # reads them through read_dim_score_from_output.
    l2_output["dim_scores"] = dim_scores
    l2_output["dim_evidence"] = dim_evidence

    run_context = {
        **l2_receipt,
        "route_contract": {
            "route_id": f"{contract['app_id']}.runtime_harness_v1",
            "app_id": contract["app_id"],
        },
        "trace_root": f"trace-{app}-cert-harness",
    }
    # Breadcrumb for fixture capture (stripped before v6 pipeline consumes it).
    run_context["_dim_scores_source"] = dim_scores_source
    return run_context


def _sha256_file_short(path: Path) -> str:
    """Return `sha256://<16hex>` of a file's contents, or empty string if absent."""
    if not path.exists():
        return ""
    import hashlib  # noqa: PLC0415
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return f"sha256://{h.hexdigest()[:16]}"


def _resolve_real_hashes(app: str) -> dict[str, str]:
    """W4.P1 — bind policy/blueprint/prompt hashes to real on-disk artifacts.

    Returns a dict with keys policy_hash, blueprint_hash, prompt_hash,
    compliance_hash, manifest_hash. Each value is `sha256://<16hex>` when
    the canonical source file exists; empty string otherwise (harness
    uses that as a hint to fall back to the prior synthetic value).

    Sources:
      - policy_hash      → apps_<x>/config/cert_route_registry.yaml
      - blueprint_hash   → apps_<x>/config/domain_contract/eval_rubrics.yaml
      - prompt_hash      → first file under apps_<x>/config/prompts/ if any
      - compliance_hash  → apps_<x>/config/domain_contract/threshold_profiles.yaml
      - manifest_hash    → apps_<x>/config/domain_contract/app_domain_manifest.yaml
    """
    app_root = REPO_ROOT / app
    prompts_dir = app_root / "config" / "prompts"
    prompt_file = ""
    if prompts_dir.exists():
        for cand in sorted(prompts_dir.glob("*.yaml")):
            prompt_file = _sha256_file_short(cand)
            break
        if not prompt_file:
            for cand in sorted(prompts_dir.glob("*.yml")):
                prompt_file = _sha256_file_short(cand)
                break
    return {
        "policy_hash": _sha256_file_short(app_root / "config" / "cert_route_registry.yaml"),
        "blueprint_hash": _sha256_file_short(
            app_root / "config" / "domain_contract" / "eval_rubrics.yaml"
        ),
        "prompt_hash": prompt_file,
        "compliance_hash": _sha256_file_short(
            app_root / "config" / "domain_contract" / "threshold_profiles.yaml"
        ),
        "manifest_hash": _sha256_file_short(
            app_root / "config" / "domain_contract" / "app_domain_manifest.yaml"
        ),
    }


def _build_receipts(app: str, contract: dict[str, Any]) -> dict[str, Any]:
    """Build a receipts dict for run_exit_eval. Mirrors tests/_fixtures.base_receipts."""
    from tools.cert.apps_e2e._harness_identity import (  # noqa: PLC0415
        build_identity_block, compute_hmac_sig,
    )
    route_id = f"{contract['app_id']}.runtime_harness_v1"
    hashes = _resolve_real_hashes(app)
    # Fall back to prior deterministic strings only when the on-disk file
    # doesn't exist — documented in the fixture as a residual gap.
    policy_hash = hashes["policy_hash"] or f"pol::{app}::v1"
    blueprint_hash = hashes["blueprint_hash"] or f"bp::{app}::v1"
    prompt_hash = hashes["prompt_hash"] or f"ph::{app}::v1"
    compliance_hash = hashes["compliance_hash"] or f"comp-{app}-1"
    manifest_hash = hashes["manifest_hash"] or f"mh-{app}-1"
    # W1 — real uuid4-shaped identifiers (deterministic for reproducibility)
    ids = build_identity_block(app, deterministic=True)
    receipts = {
        "source_type": "L2_SEALED_ARTIFACT",
        "request_id": ids["request_id"],
        "run_id": ids["run_id"],
        "session_id": ids["session_id"],
        "trace_root": f"trace-{app}-cert-harness",
        "route_id": route_id,
        "policy_hash": policy_hash,
        "blueprint_hash": blueprint_hash,
        "prompt_hash": prompt_hash,
        "replay_key": ids["replay_key"],
        "compliance_hash": compliance_hash,
        "manifest_hash": manifest_hash,
        # hmac_sig computed after the rest is built (W2)
        "hmac_sig": "",
        # APPS-DOM runtime binding — fields read by normalize_to_packet
        # (post W1.P1) so the pipeline emits exit.app_specific_eval natively.
        "app_id": contract["app_id"],
        "task_class": contract["task_class"],
        "rubric_ref": contract["rubric_ref"],
        "threshold_profile_ref": contract["threshold_profile_ref"],
        "route_contract": {
            "route_id": route_id,
            "policy_hash": policy_hash,
            "blueprint_hash": blueprint_hash,
            "prompt_hash": prompt_hash,
            "app_id": contract["app_id"],
            "task_class": contract["task_class"],
            "rubric_ref": contract["rubric_ref"],
            "threshold_profile_ref": contract["threshold_profile_ref"],
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
        "evidence_bundle": {"sources": [f"{app}_synthetic_source_1"]},
        "final_evidence_contract": {
            "schema_version": "1.0",
            "producer": f"{app}.cert.fec_producer",
            "grounded": True,
            "route_id": route_id,
            "evidence_sufficiency": "grounded",
        },
        "prompt_assembly_status": {"slot_order_valid": True},
        "compiled_prompt_artifact": {},
        "output": {
            "text": f"{app} synthetic pass-path output",
            "schema_required": False,
            "schema_valid": True,
            "groundedness": 0.95,
            "faithfulness": 0.95,
            "citation_precision": 0.95,
            "completion_score": 0.9,
            "confidence": 0.75,
            "format_fit": True,
        },
        "validation_counters": {},
        "retry_counters": {"retry_count": 0, "retry_max": 3},
        "repair_counters": {},
        "trajectory_snapshot": {},
        "grader_composition": {
            "roster": ["code_schema", "code_citation"],
            "threshold_profile": contract["threshold_profile_ref"],
        },
        "track_label": "production",
        "support_score": 0.9,
        "confidence": 0.75,
        "abstain_flags": [],
        "contradiction_flags": [],
        "otel_spans": {
            "spans": {
                "trace_root": f"t-{app}",
                "route_contract": f"rc-{app}",
                "tool_invocations": [f"i-{app}"],
                "evidence_contracts": [f"e-{app}"],
                "step_outputs": [f"s-{app}"],
                "exit_disposition": "ALLOW",
            },
        },
        "timing_offsets": {},
        "anomaly_flags": [],
        "hitl_packet": {},
        "bus_d_signals": [],
        "bus_e_signals": [],
        "replay_guard_violations": [],
        "isolation_anomalies": [],
        "drift_warnings": [],
    }
    # W2 — real HMAC-SHA256 over canonical-JSON receipt form (excludes
    # hmac_sig + non-deterministic identity fields so the sig is content-bound).
    receipts["hmac_sig"] = compute_hmac_sig(receipts)
    return receipts


_HARNESS_EVALUATOR_CACHE: Any = None


def _get_harness_evaluator() -> Any:
    """Lazily build a harness-scoped evaluator with a preloaded store.

    Cached across apps within a single run so the store is built once.
    """
    global _HARNESS_EVALUATOR_CACHE
    if _HARNESS_EVALUATOR_CACHE is not None:
        return _HARNESS_EVALUATOR_CACHE
    from tools.cert.apps_e2e._harness_store_loader import (  # noqa: PLC0415
        build_harness_evaluator,
    )
    evaluator, _reports = build_harness_evaluator(RUNTIME_APPS)
    _HARNESS_EVALUATOR_CACHE = evaluator
    return evaluator


def _capture_one_app(app: str) -> dict[str, Any]:
    """Execute the harness for a single app. Returns a status record."""
    start = time.time()
    status: dict[str, Any] = {
        "app": app,
        "captured": False,
        "reason": None,
        "generated_at_utc": None,
        "fixture_path": None,
    }
    from agentic_core.L3_orchestration.exit_eval.v6.pipeline import (  # noqa: PLC0415
        ExitEvalPipeline,
    )

    contract = _discover_app_contract(app)
    if contract is None:
        status["reason"] = "could not resolve app contract from YAML"
        return status

    run_context = _build_pass_run_context(app, contract)
    receipts = _build_receipts(app, contract)

    # Thread dim_scores + dim_evidence from run_context into receipts.output
    # so the pipeline's internal normalize_to_packet → evaluate_from_packet
    # path reads them. The evaluator's run_context is built from
    # review.output inside the pipeline.
    ro = dict(receipts.get("output") or {})
    rc_output = run_context.get("output") or {}
    if isinstance(rc_output, dict):
        if "dim_scores" in rc_output:
            ro["dim_scores"] = rc_output["dim_scores"]
        if "dim_evidence" in rc_output:
            ro["dim_evidence"] = rc_output["dim_evidence"]
        if "tracked_metrics" in rc_output:
            ro["tracked_metrics"] = rc_output["tracked_metrics"]
    receipts["output"] = ro

    # Step A — real Exit pipeline run with harness-scoped evaluator.
    # The pipeline's own `exit.app_specific_eval` emit path now fires
    # natively because:
    #   (a) W1.P1 patched normalize_to_packet to populate app_id/rubric_ref.
    #   (b) W2.P1 preloads the store so rubric lookups resolve.
    #   (c) W3.P1 populates receipts.output.dim_scores via the real mapper.
    # No post-hoc record_span enrichment needed.
    try:
        evaluator = _get_harness_evaluator()
        pipeline = ExitEvalPipeline(app_evaluator=evaluator)
        result = pipeline.run(receipts)
    except Exception as exc:  # noqa: BLE001
        status["reason"] = f"ExitEvalPipeline.run raised {type(exc).__name__}: {exc}"
        return status

    review = result.packet
    if review is None:
        status["reason"] = "pipeline returned no review packet"
        return status

    # Extract app_eval from the packet (populated by the pipeline itself).
    ase_from_packet = review.app_specific_eval or {}
    app_eval_bound = bool(ase_from_packet.get("bound"))
    app_eval_passed = bool(ase_from_packet.get("passed"))
    app_eval_dims = ase_from_packet.get("dimensions") or []
    _dim_pass = sum(1 for d in app_eval_dims if isinstance(d, dict) and d.get("status") == "PASS")
    _dim_fail = sum(1 for d in app_eval_dims if isinstance(d, dict) and d.get("status") == "FAIL")
    _dim_unknown = sum(1 for d in app_eval_dims if isinstance(d, dict) and d.get("status") == "UNKNOWN")

    # Step D — serialize captured spans + decision + app_eval to fixture
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fixture_path = OUTPUT_DIR / f"{app}_cert_trace.json"

    # Extract v6 span bucket, convert to a JSON-friendly shape
    v6_bucket = review.otel_spans.get("v6", {}) if review.otel_spans else {}
    spans_serialized: dict[str, list[dict[str, Any]]] = {}
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

    # Resolve disposition string
    disposition = ""
    if result.decision is not None:
        disposition = getattr(result.decision.disposition, "value", str(result.decision.disposition))
    else:
        disposition = getattr(result.disposition, "value", str(result.disposition))

    hashes_report = _resolve_real_hashes(app)
    fixture = {
        "schema_version": "1.0",
        "harness_version": "apps_dom_runtime_harness_v2_real_evidence",
        "app": app,
        "app_id": contract["app_id"],
        "task_class": contract["task_class"],
        "rubric_ref": contract["rubric_ref"],
        "threshold_profile_ref": contract["threshold_profile_ref"],
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime()),
        "elapsed_ms": int((time.time() - start) * 1000),
        "exit_disposition": disposition,
        "dim_scores_source": run_context.get("_dim_scores_source", "synthetic_fallback"),
        "real_hashes": {
            "policy_hash": hashes_report["policy_hash"],
            "blueprint_hash": hashes_report["blueprint_hash"],
            "prompt_hash": hashes_report["prompt_hash"],
            "compliance_hash": hashes_report["compliance_hash"],
            "manifest_hash": hashes_report["manifest_hash"],
        },
        "app_specific_eval": {
            **ase_from_packet,
            "dim_pass_count": _dim_pass,
            "dim_fail_count": _dim_fail,
            "dim_unknown_count": _dim_unknown,
        },
        "otel_spans": spans_serialized,
        "spans_count": sum(len(v) for v in spans_serialized.values()),
        "span_names": sorted(spans_serialized.keys()),
        "x1_verdict_count": len(result.verdicts or []),
    }
    fixture_path.write_text(json.dumps(fixture, indent=2, sort_keys=True), encoding="utf-8")

    status.update({
        "captured": True,
        "generated_at_utc": fixture["generated_at_utc"],
        "fixture_path": str(fixture_path.relative_to(REPO_ROOT).as_posix()),
        "disposition": disposition,
        "app_eval_bound": app_eval_bound,
        "app_eval_passed": app_eval_passed,
        "dim_pass_count": _dim_pass,
        "dim_fail_count": _dim_fail,
        "spans_count": fixture["spans_count"],
        "app_specific_eval_span_present": "exit.app_specific_eval" in spans_serialized,
        "dim_scores_source": fixture["dim_scores_source"],
    })
    return status


def _jsonify(obj: Any) -> Any:
    """Recursively coerce non-JSON-serializable values."""
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apps", nargs="*", default=list(RUNTIME_APPS),
                        help="Subset of apps to capture (default: all 8)")
    args = parser.parse_args(argv)

    print(f"APPS-DOM runtime harness — capturing OTEL for {len(args.apps)} app(s)...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, Any]] = []
    for app in args.apps:
        r = _capture_one_app(app)
        results.append(r)
        if r["captured"]:
            print(
                f"  OK  {app:24s}  spans={r['spans_count']:3d}  "
                f"app_eval_bound={r['app_eval_bound']}  passed={r['app_eval_passed']}  "
                f"disp={r['disposition']}  fixture={r['fixture_path']}"
            )
        else:
            print(f"  FAIL {app:24s}  reason={r['reason']}")

    captured = sum(1 for r in results if r["captured"])
    failed = len(results) - captured
    print(f"\nCaptured {captured}/{len(results)} app traces; failures={failed}")

    # Summary index
    index_path = OUTPUT_DIR / "_index.json"
    index = {
        "schema_version": "1.0",
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime()),
        "captured_count": captured,
        "failed_count": failed,
        "results": results,
    }
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote index {index_path.relative_to(REPO_ROOT).as_posix()}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
