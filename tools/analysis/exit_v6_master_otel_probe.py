"""Master OTEL evidence probe for Exit Eval v6.

Reads requirements registry YAML, runs runtime probes, emits one OTEL-shaped
span per requirement, writes JSON evidence file.

Run:
    python tools/analysis/exit_v6_master_otel_probe.py
"""

from __future__ import annotations

import hashlib
import json
import secrets
import sys
from pathlib import Path
from typing import Any

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from agentic_core.L3_orchestration.exit_eval.v6 import (
    EXIT_V6_SPAN_CATALOG,
    ExitEvalPipeline,
    ExitReviewPacket,
    HITLDecision,
    HITLVerdict,
    SourceType,
    UwgOutcome,
    V6Disposition,
    build_freeze_receipt,
    build_human_decision_receipt,
    build_human_review_packet,
    build_l5_reclearance_request,
    classify_source,
    default_backends,
    enqueue_l6_handoff,
    eval_x1a,
    eval_x1b,
    eval_x1c,
    eval_x1f,
    eval_x1j,
    normalize_to_packet,
    validate_required_receipts,
)
from agentic_core.L3_orchestration.exit_eval.v6 import otel as v6_otel
from agentic_core.L3_orchestration.exit_eval.v6.return_payload import (
    RETURN_PAYLOAD_FAILURE_CODES,
)
from tests.unit.agentic_core.L3_orchestration.exit_eval.v6._fixtures import (
    base_packet,
    base_receipts,
)

_TRACE_ID = secrets.token_hex(16)
_REGISTRY = _REPO_ROOT / "tools/analysis/exit_v6_requirements_registry.yaml"
_OUT = _REPO_ROOT / "docs/reports/plans/exit_v6_MASTER_otel_evidence.json"


def _span_id(req_id: str) -> str:
    return hashlib.sha256(req_id.encode()).hexdigest()[:16]


def _extract_spans(pkt: ExitReviewPacket | None) -> list[str]:
    if not pkt or not isinstance(pkt.otel_spans, dict):
        return []
    b = pkt.otel_spans.get("v6", {})
    return list(b.keys()) if isinstance(b, dict) else []


def _observe() -> dict[str, Any]:
    """Capture all runtime observations referenced by validators."""
    o: dict[str, Any] = {}
    pipe = ExitEvalPipeline()

    # Baseline X3D
    base = pipe.run(base_receipts())
    o["x3d_disposition"] = base.disposition.name
    o["x3d_spans"] = sorted(_extract_spans(base.packet))
    o["x3d_unique_count"] = len(o["x3d_spans"])

    # X3C COMMIT
    co = dict(
        terminal_class="with_state_diff",
        write_intent_class="memory_promotion",
        capability_token={"authorizes_write": True},
        state_diff={
            "complete": True,
            "bounded": True,
            "uwg_routed": True,
            "blast_radius": "low",
            "rollback_plan": {"steps": []},
        },
        grader_composition={
            "roster": ["code_schema"],
            "threshold_profile": "production_v1",
            "consistency": {"pass_power_estimate": 0.99, "theta": 0.95, "sample_quality": "ok"},
        },
    )
    commit = ExitEvalPipeline(uwg_backends=default_backends()).run(base_receipts(**co))
    o["x3c_disposition"] = commit.disposition.name

    # X3B
    high = {
        **co,
        "state_diff": {
            **co["state_diff"],
            "blast_radius": "high",
            "rollback_plan": {"steps": [{"kind": "noop"}]},
        },
    }
    o["x3b_disposition"] = ExitEvalPipeline().run(base_receipts(**high)).disposition.name

    # X3A
    deny_rec = base_receipts(
        exec_trace={
            "tool_calls": [],
            "model_calls": [{"model_id": "m1"}],
            "replay_receipts_present": True,
            "wall_clock_used": False,
            "learning_bus_contamination": True,
        }
    )
    o["x3a_disposition"] = ExitEvalPipeline().run(deny_rec).disposition.name

    # Empty fail-closed
    empty = pipe.run({})
    o["empty_disposition"] = empty.disposition.name
    o["empty_codes"] = [f.reason_code for f in (empty.preflight_failures or [])]

    # Determinism
    d1 = pipe.run(base_receipts()).exhaust_manifest.deterministic_digest or ""
    d2 = pipe.run(base_receipts()).exhaust_manifest.deterministic_digest or ""
    o["det_d1"] = d1[:16]
    o["det_d2"] = d2[:16]
    o["det_equal"] = d1 == d2
    rec_a = base_receipts()
    rec_b = {k: rec_a[k] for k in reversed(list(rec_a))}
    pa = pipe.run(rec_a).exhaust_manifest.deterministic_digest
    pb = pipe.run(rec_b).exhaust_manifest.deterministic_digest
    o["perm_equal"] = pa == pb
    o["perm_d"] = pa[:16]

    # Source classify round-trip
    cs = {}
    for s in SourceType:
        rec = base_receipts(source_type=s.value)
        if s is SourceType.HITL_RECLEARED_PACKET:
            rec.update(hitl_recleared=True, hitl_packet={"l5_cleared": True})
        if s is SourceType.RET_CACHE_EXACT:
            rec["cache_hit_kind"] = "exact"
        if s is SourceType.RET_CACHE_SEMANTIC:
            rec["cache_hit_kind"] = "semantic"
        cs[s.value] = classify_source(rec).value
    o["classify_source"] = cs

    # Catalogs
    import agentic_core.L3_orchestration.exit_eval.v6 as _v6

    o["span_catalog"] = sorted(EXIT_V6_SPAN_CATALOG)
    o["span_count"] = len(o["span_catalog"])
    o["required_attrs"] = sorted(v6_otel.REQUIRED_ATTRIBUTES)
    o["required_attrs_count"] = len(o["required_attrs"])
    o["v6_all"] = sorted(getattr(_v6, "__all__", []))
    o["v6_all_count"] = len(o["v6_all"])
    o["return_codes"] = sorted(RETURN_PAYLOAD_FAILURE_CODES)
    o["return_codes_count"] = len(o["return_codes"])
    o["disp_enum"] = [(d.name, d.value) for d in V6Disposition]
    o["disp_names"] = [d.name for d in V6Disposition]
    o["source_enum"] = [s.value for s in SourceType]
    o["uwg_enum"] = [u.name for u in UwgOutcome]
    o["verdict_enum"] = [v.name for v in HITLVerdict]
    o["erp_fields"] = list(ExitReviewPacket.__dataclass_fields__.keys())

    # HITL contracts
    pkt = base_packet()
    f1 = build_freeze_receipt(pkt, reason_codes=["R1"], frozen_artifact_refs=["a"])
    f2 = build_freeze_receipt(pkt, reason_codes=["R2"], frozen_artifact_refs=["b"])
    rp1 = build_human_review_packet(pkt, f1, review_packet_id="rp-1", escalation_reason_codes=["R1"])
    dec1 = build_human_decision_receipt(
        rp1.review_packet_id,
        HITLDecision(
            verdict=HITLVerdict.APPROVE,
            modified_packet=None,
            rationale="r",
            reviewer_id="u1",
            decision_at_ms=0,
        ),
        reviewer_id_ref="u1",
    )
    rc1 = build_l5_reclearance_request(pkt, dec1)
    o["freeze_fields"] = list(f1.__dataclass_fields__.keys())
    o["freeze_distinct"] = f1.freeze_digest != f2.freeze_digest
    o["review_fields"] = list(rp1.__dataclass_fields__.keys())
    o["decision_fields"] = list(dec1.__dataclass_fields__.keys())
    o["reclear_fields"] = list(rc1.__dataclass_fields__.keys())
    o["data_not_authority"] = dec1.data_not_authority_assertion

    from agentic_core.L3_orchestration.exit_eval.v6.hitl import _RECLEAR_GATES

    o["reclear_gates"] = {k.name: list(v) for k, v in _RECLEAR_GATES.items()}

    # L6 handoff
    handoff = enqueue_l6_handoff(base.exhaust_manifest)
    o["l6_allowed"] = handoff.get("l6_mutation_allowed")
    o["boundary_status"] = (
        base.exhaust_manifest.runtime_boundary_status.value if base.exhaust_manifest else None
    )

    # Preflight isolated
    pf = {}

    def _pf(label, mut):
        rec = base_receipts()
        mut(rec)
        pf[label] = [f.reason_code for f in validate_required_receipts(rec)]

    _pf("policy_hash_missing", lambda r: r.update(policy_hash=""))
    _pf("replay_key_missing", lambda r: r.update(replay_key=""))
    _pf("route_contract_missing", lambda r: r.pop("route_contract", None))
    _pf("terminal_class_missing", lambda r: r.update(terminal_class=""))
    _pf(
        "action_missing_sandbox",
        lambda r: (r.update(terminal_class="external_action"), r.pop("sandbox_envelope", None)),
    )
    _pf(
        "tool_missing_capability",
        lambda r: (
            r.__setitem__("exec_trace", dict(r["exec_trace"], tool_calls=[{"id": "t1"}])),
            r.pop("capability_token", None),
        ),
    )
    _pf(
        "grounded_missing_contract",
        lambda r: (
            r.update(grounding_required=True, evidence_bundle={"e": 1}),
            r.update(final_evidence_contract={}),
        ),
    )
    _pf(
        "hitl_recleared_missing_l5",
        lambda r: r.update(
            source_type="HITL_RECLEARED_PACKET", hitl_recleared=True, hitl_packet={"l5_cleared": False}
        ),
    )
    o["preflight"] = pf

    # All preflight codes union
    o["all_pf_codes"] = sorted({c for codes in pf.values() for c in codes})

    return o


_VALIDATOR_FNS = {
    # Each validator: takes obs dict + req metadata, returns (status, evidence, attrs)
}


def _validate(req: dict, obs: dict[str, Any]) -> tuple[str, str, dict]:
    """Apply validator named in req['check'] against observations."""
    chk = req.get("check", "always_design")
    args = req.get("args", {})

    if chk == "ok_static":
        return "OK", req.get("evidence", "asserted by spec contract"), args

    if chk == "design":
        return "DESIGN", req.get("evidence", "design-only, no runtime binding"), args

    if chk == "gap":
        return "GAP", req.get("evidence", "known gap"), args

    if chk == "source_type_in_enum":
        target = args["value"]
        present = target in obs["source_enum"]
        return (
            ("OK", f"SourceType.{target} in enum", {"source_enum": obs["source_enum"], "target": target})
            if present
            else ("GAP", f"{target} missing from {obs['source_enum']}", {"target": target})
        )

    if chk == "preflight_emits":
        case = args["case"]
        code = args["code"]
        codes = obs["preflight"].get(case, [])
        present = code in codes
        return (
            ("OK", f"preflight[{case}] emitted {code}", {"case": case, "code": code, "observed_codes": codes})
            if present
            else (
                "GAP",
                f"expected {code} in preflight[{case}]={codes}",
                {"case": case, "code": code, "observed_codes": codes},
            )
        )

    if chk == "v6_export":
        name = args["name"]
        present = name in obs["v6_all"]
        return (
            ("OK", f"{name} in v6.__all__", {"export": name})
            if present
            else ("GAP", f"{name} not exported", {"export": name})
        )

    if chk == "v6_internal":
        # exists inside a v6 submodule but not necessarily in __all__
        import importlib

        mod_path = args["module"]
        name = args["name"]
        try:
            mod = importlib.import_module(mod_path)
            present = hasattr(mod, name)
            return (
                ("OK", f"{mod_path}.{name} present", {"module": mod_path, "name": name})
                if present
                else ("GAP", f"{name} not in {mod_path}", {"module": mod_path, "name": name})
            )
        except ImportError as e:
            return "GAP", f"cannot import {mod_path}: {e}", {"module": mod_path}

    if chk == "preflight_emits_alias":
        # Spec uses a long code; v6 emits a short alias. Pass if EITHER is present.
        case = args["case"]
        spec_code = args["spec_code"]
        v6_alias = args["v6_alias"]
        codes = obs["preflight"].get(case, [])
        if v6_alias in codes:
            return (
                "OK",
                f"v6 emits alias {v6_alias} (spec wants {spec_code}); semantic match",
                {
                    "case": case,
                    "spec_code": spec_code,
                    "v6_alias": v6_alias,
                    "observed_codes": codes,
                    "naming_drift": True,
                },
            )
        if spec_code in codes:
            return (
                "OK",
                f"exact match {spec_code}",
                {"case": case, "code": spec_code, "observed_codes": codes},
            )
        return (
            "GAP",
            f"neither {spec_code} nor {v6_alias} in {codes}",
            {"case": case, "spec_code": spec_code, "v6_alias": v6_alias, "observed_codes": codes},
        )

    if chk == "span_in_catalog":
        s = args["span"]
        present = s in obs["span_catalog"]
        return (
            ("OK", f"{s} in EXIT_V6_SPAN_CATALOG", {"span": s})
            if present
            else ("GAP", f"{s} missing from catalog", {"span": s})
        )

    if chk == "span_in_catalog_alias":
        spec = args["spec_span"]
        v6 = args["v6_span"]
        if v6 in obs["span_catalog"]:
            return (
                "OK",
                f"v6 emits alias {v6} (spec wants {spec}); semantic match",
                {"spec_span": spec, "v6_span": v6, "naming_drift": True},
            )
        if spec in obs["span_catalog"]:
            return ("OK", f"exact match {spec}", {"span": spec})
        return ("GAP", f"neither {spec} nor {v6} in catalog", {"spec_span": spec, "v6_span": v6})

    if chk == "uwg_outcome_alias":
        spec = args["spec_outcome"]
        v6 = args["v6_outcome"]
        if v6 in obs["uwg_enum"]:
            return (
                "OK",
                f"v6 alias {v6} maps to spec {spec}",
                {"spec_outcome": spec, "v6_outcome": v6, "naming_drift": True},
            )
        return ("GAP", f"v6 alias {v6} not in {obs['uwg_enum']}", {"spec_outcome": spec, "v6_outcome": v6})

    if chk == "attr_in_required":
        a = args["attribute"]
        present = a in obs["required_attrs"]
        return (
            ("OK", f"{a} in REQUIRED_ATTRIBUTES", {"attribute": a})
            if present
            else ("GAP", f"{a} missing from required attrs", {"attribute": a})
        )

    if chk == "disposition_name":
        key = args["obs_key"]
        expected = args["expected"]
        actual = obs[key]
        return (
            ("OK", f"{key}={actual}", {"observed": actual, "expected": expected})
            if actual == expected
            else ("GAP", f"{key}={actual} != {expected}", {"observed": actual, "expected": expected})
        )

    if chk == "disposition_in_enum":
        d = args["disposition"]
        present = d in obs["disp_names"] or any(d == n for n, _ in obs["disp_enum"])
        return (
            ("OK", f"V6Disposition.{d} present", {"disposition": d})
            if present
            else ("GAP", f"{d} not in {obs['disp_names']}", {"disposition": d})
        )

    if chk == "uwg_outcome_in_enum":
        u = args["outcome"]
        present = u in obs["uwg_enum"]
        return (
            ("OK", f"UwgOutcome.{u} present", {"outcome": u})
            if present
            else ("GAP", f"{u} not in {obs['uwg_enum']}", {"outcome": u})
        )

    if chk == "return_code_present":
        c = args["code"]
        present = c in obs["return_codes"]
        return (
            ("OK", f"{c} in RETURN_PAYLOAD_FAILURE_CODES", {"code": c})
            if present
            else ("GAP", f"{c} not in return codes", {"code": c})
        )

    if chk == "obs_eq":
        key = args["key"]
        expected = args["expected"]
        actual = obs.get(key)
        return (
            ("OK", f"{key}={actual}", {"key": key, "value": actual})
            if actual == expected
            else ("GAP", f"{key}={actual} != {expected}", {"key": key, "value": actual, "expected": expected})
        )

    if chk == "obs_truthy":
        key = args["key"]
        v = obs.get(key)
        return (
            ("OK", f"{key}={v}", {"key": key, "value": v})
            if v
            else ("GAP", f"{key} not truthy: {v}", {"key": key, "value": v})
        )

    if chk == "field_in_dataclass":
        list_key = args["list_key"]
        f = args["field"]
        fields = obs.get(list_key, [])
        present = f in fields
        return (
            ("OK", f"{f} in {list_key}", {"field": f})
            if present
            else ("GAP", f"{f} not in {fields}", {"field": f, "fields": fields})
        )

    if chk == "verdict_in_enum":
        v = args["verdict"]
        present = v in obs["verdict_enum"]
        return (
            (
                "OK",
                f"HITLVerdict.{v} present",
                {"verdict": v, "reclear_gates": obs["reclear_gates"].get(v, [])},
            )
            if present
            else ("GAP", f"{v} not in {obs['verdict_enum']}", {"verdict": v})
        )

    return "DESIGN", f"unknown check '{chk}' — defaulting to DESIGN", args


def main() -> None:
    obs = _observe()
    with _REGISTRY.open("r", encoding="utf-8") as f:
        registry = yaml.safe_load(f)

    spans: list[dict] = []
    counts = {"OK": 0, "DESIGN": 0, "GAP": 0}

    for req in registry["requirements"]:
        rid = req["id"]
        status, evidence, attrs = _validate(req, obs)
        spans.append(
            {
                "req_id": rid,
                "trace_id": _TRACE_ID,
                "span_id": _span_id(rid),
                "name": f"exit.req.{rid}",
                "kind": "INTERNAL",
                "source": f"{req['source']}:{req.get('line', '?')}",
                "requirement": req["text"],
                "status": status,
                "evidence": evidence,
                "attributes": {**(req.get("attributes") or {}), **attrs},
            }
        )
        counts[status] += 1

    out = {
        "trace_id": _TRACE_ID,
        "summary": {
            "total": len(spans),
            "ok": counts["OK"],
            "design": counts["DESIGN"],
            "gap": counts["GAP"],
        },
        "observations_summary": {
            "x3d_disposition": obs["x3d_disposition"],
            "x3c_disposition": obs["x3c_disposition"],
            "x3b_disposition": obs["x3b_disposition"],
            "x3a_disposition": obs["x3a_disposition"],
            "empty_disposition": obs["empty_disposition"],
            "span_catalog_count": obs["span_count"],
            "required_attributes_count": obs["required_attrs_count"],
            "v6_module_all_count": obs["v6_all_count"],
            "return_payload_failure_codes_count": obs["return_codes_count"],
            "determinism_equal": obs["det_equal"],
            "permutation_equal": obs["perm_equal"],
            "l6_handoff_allowed": obs["l6_allowed"],
            "runtime_boundary_status": obs["boundary_status"],
            "freeze_digest_distinct": obs["freeze_distinct"],
            "data_not_authority_assertion": obs["data_not_authority"],
        },
        "spans": spans,
    }
    _OUT.parent.mkdir(parents=True, exist_ok=True)
    _OUT.write_text(json.dumps(out, indent=2, default=str))
    print(f"Wrote {len(spans)} spans -> {_OUT}")
    print(f"  OK={counts['OK']}  DESIGN={counts['DESIGN']}  GAP={counts['GAP']}")
    print(f"  trace_id={_TRACE_ID}")


if __name__ == "__main__":
    main()
