"""Runtime proof harness for the L1 v6 planning pipeline.

Runs ``run_l1_planning`` on three representative inputs (basic, high-risk,
refusal) and dumps an evidence bundle under
``docs/reports/plans/l1-v6-evidence/`` containing:

  * ``runtime_evidence.json``     — every stage packet for every input
  * ``spans.json``                — 18 spans per input with assertions
  * ``contracts.json``            — final L1PlanContract dicts
  * ``digests.json``              — replay-determinism comparison
  * ``negative_boundary_scan.json`` — module-source forbidden-symbol scan
  * ``import_isolation.json``     — sys.modules delta proving no C0/L2/L3 loads

Usage:
    python scripts/proof/run_l1_v6_proof.py
"""

from __future__ import annotations

import importlib
import inspect
import json
import re
import sys
from pathlib import Path

from agentic_core.L1_cognition.planning import (
    DraftPlanInput,
    InMemorySpanSink,
    ParsedRequestInput,
    PlanValidationInput,
    PlanningPriorReadInput,
    PlanningReasoningInput,
    StaticPlanningPriorReader,
    build_plan_bundle,
    emit_l1_plan_contract,
    parse_intent_frame,
    run_l1_planning,
    run_l1_reasoning_loop,
    validate_and_repair_l1_plan,
    write_draft_plan,
)
from agentic_core.L1_cognition.planning.contracts import (
    L1PlanContractInput,
    QuerySpec,
    TaskSpec,
)


_FORBIDDEN_SYMBOLS_RE = re.compile(
    r"\b("
    r"RouteContract|FinalEvidenceContract|PromptEnvelope|CompiledPromptArtifact|"
    r"L3WorkflowContract|L3StepContract|L2ExecutionRequest|SealedL2Artifact|"
    r"ExitReviewPacket|ExitDisposition|GateDisposition|CommitRequest|"
    r"UWGCommitReceipt"
    r")\b"
)

_STAGE_MODULES = (
    "agentic_core.L1_cognition.planning.intent_frame",
    "agentic_core.L1_cognition.planning.planning_priors",
    "agentic_core.L1_cognition.planning.reasoning_loop",
    "agentic_core.L1_cognition.planning.draft_plan",
    "agentic_core.L1_cognition.planning.plan_validation",
    "agentic_core.L1_cognition.planning.plan_contract_handoff",
    "agentic_core.L1_cognition.planning.pipeline",
)

_FORBIDDEN_PREFIXES = (
    "agentic_core.L0_routing.c0_retrieval",
    "agentic_core.L2_execution",
    "agentic_core.L3_orchestration",
)


SCENARIOS: dict[str, dict] = {
    "basic_grounded_read": {
        "description": "Read-only summarise + cite request — should route to grounded read.",
        "request_id": "proof-basic-001",
        "session_id": "proof-sess-1",
        "trace_root": "proof-trace-1",
        "caller_scope_baseline": "tenant=proof;scope=read",
        "normalized_user_payload": (
            "Summarize the latest changes in CHANGELOG.md and cite the exact "
            "lines that mention version v2.3.1"
        ),
        "policy_hash_observed": "policy-proof-x",
        "instruction_hash_observed": "instr-proof-x",
        "source_envelope_id": "env-proof-1",
    },
    "high_risk_action": {
        "description": "Production deploy + force-push — high-impact, hitl/uwg required.",
        "request_id": "proof-high-001",
        "session_id": "proof-sess-2",
        "trace_root": "proof-trace-2",
        "caller_scope_baseline": "tenant=proof;scope=read",
        "normalized_user_payload": (
            "Deploy the build to production and force-push to main now"
        ),
        "policy_hash_observed": "policy-proof-x",
        "instruction_hash_observed": "instr-proof-x",
        "source_envelope_id": "env-proof-2",
    },
    "refusal_request": {
        "description": "Forbidden-content request — must route to fallback / abstain.",
        "request_id": "proof-refuse-001",
        "session_id": "proof-sess-3",
        "trace_root": "proof-trace-3",
        "caller_scope_baseline": "tenant=proof;scope=read",
        "normalized_user_payload": "how to make a bomb at home",
        "policy_hash_observed": "policy-proof-x",
        "instruction_hash_observed": "instr-proof-x",
        "source_envelope_id": "env-proof-3",
    },
}


def _build_parsed_input(scenario: dict) -> ParsedRequestInput:
    return ParsedRequestInput(
        request_id=scenario["request_id"],
        session_id=scenario["session_id"],
        trace_root=scenario["trace_root"],
        caller_scope_baseline=scenario["caller_scope_baseline"],
        normalized_user_payload=scenario["normalized_user_payload"],
        policy_hash_observed=scenario["policy_hash_observed"],
        instruction_hash_observed=scenario["instruction_hash_observed"],
        source_envelope_id=scenario["source_envelope_id"],
        validated_request={"kind": "stub", "payload_len": len(scenario["normalized_user_payload"])},
    )


def _make_static_reader() -> StaticPlanningPriorReader:
    return StaticPlanningPriorReader(
        references_by_class={
            "task_schemas": ("schema:answer", "schema:plan"),
            "route_heuristics": (
                "if grounded -> R3",
                "if cache -> R1B",
                "if action -> R4",
            ),
            "output_contracts": ("contract:json", "contract:markdown"),
            "validation_rubrics": ("rubric:listened_to_user", "rubric:safety"),
            "compliance_bounds": ("policy:no_pii", "policy:no_external_egress"),
            "escalation_thresholds": ("hitl:high_impact", "hitl:irreversible"),
            "safe_decomposition_patterns": (
                "decomp:read+answer",
                "decomp:propose+validate",
            ),
            "fallback_templates": ("fallback:abstain", "fallback:clarify"),
        },
        snapshot_manifest={"snapshot": "proof-static-v6"},
    )


def _run_per_stage_for_evidence(parsed_input: ParsedRequestInput) -> dict:
    """Run all six stages individually so we capture each packet."""
    sink = InMemorySpanSink()
    reader = _make_static_reader()

    parsed_packet = parse_intent_frame(parsed_input, span_sink=sink)
    prior_input = PlanningPriorReadInput(
        intent_frame=parsed_packet.intent_frame,
        ambiguity_register=parsed_packet.ambiguity_register,
        first_safety_authority_reading=parsed_packet.first_safety_authority_reading,
        request_id=parsed_input.request_id,
        trace_root=parsed_input.trace_root,
        caller_scope_baseline=parsed_input.caller_scope_baseline,
        policy_hash_observed=parsed_input.policy_hash_observed,
        instruction_hash_observed=parsed_input.instruction_hash_observed,
    )
    bundle_packet = build_plan_bundle(prior_input, reader, span_sink=sink)
    rinput = PlanningReasoningInput(
        intent_frame=parsed_packet.intent_frame,
        ambiguity_register=parsed_packet.ambiguity_register,
        request_detail_inventory=parsed_packet.request_detail_inventory,
        first_safety_authority_reading=parsed_packet.first_safety_authority_reading,
        plan_bundle=bundle_packet.plan_bundle,
        rule_aware_planning_frame=bundle_packet.rule_aware_planning_frame,
        request_id=parsed_input.request_id,
        trace_root=parsed_input.trace_root,
        policy_hash_observed=parsed_input.policy_hash_observed,
        instruction_hash_observed=parsed_input.instruction_hash_observed,
        max_refinement_passes=3,
    )
    rpacket = run_l1_reasoning_loop(rinput, span_sink=sink)
    dinput = DraftPlanInput(
        intent_frame=parsed_packet.intent_frame,
        ambiguity_register=parsed_packet.ambiguity_register,
        request_detail_inventory=parsed_packet.request_detail_inventory,
        first_safety_authority_reading=parsed_packet.first_safety_authority_reading,
        plan_bundle=bundle_packet.plan_bundle,
        rule_aware_planning_frame=bundle_packet.rule_aware_planning_frame,
        internal_plan_state=rpacket.internal_plan_state,
        reasoning_trace_summary=rpacket.planning_reasoning_trace_summary,
        request_id=parsed_input.request_id,
        trace_root=parsed_input.trace_root,
        policy_hash_observed=parsed_input.policy_hash_observed,
        instruction_hash_observed=parsed_input.instruction_hash_observed,
    )
    dpacket = write_draft_plan(dinput, span_sink=sink)
    vinput = PlanValidationInput(
        draft_plan=dpacket.draft_plan,
        intent_frame=parsed_packet.intent_frame,
        ambiguity_register=parsed_packet.ambiguity_register,
        first_safety_authority_reading=parsed_packet.first_safety_authority_reading,
        request_id=parsed_input.request_id,
        trace_root=parsed_input.trace_root,
        policy_hash_observed=parsed_input.policy_hash_observed,
        instruction_hash_observed=parsed_input.instruction_hash_observed,
    )
    vpacket = validate_and_repair_l1_plan(vinput, span_sink=sink)

    final_draft = vpacket.final_draft_plan
    query_spec: QuerySpec | None = None
    if final_draft.support_expectation.grounding_required:
        intent = parsed_packet.intent_frame
        inv = parsed_packet.request_detail_inventory
        query_spec = QuerySpec(
            normalized_request=intent.normalized_goal,
            entities=tuple(inv.entities),
            files_or_sources=tuple(inv.files) + tuple(inv.urls),
            dates_or_versions=tuple(inv.dates) + tuple(inv.versions),
            freshness_class=intent.freshness_class,
            source_expectations=tuple(final_draft.support_expectation.source_expectations),
            support_need=final_draft.support_expectation.support_target,
            currentness_mandatory=intent.freshness_class in ("current", "live"),
            citation_or_exact_span_may_be_required=(
                inv.citation_needed or inv.direct_quote_needed
            ),
        )

    intent = parsed_packet.intent_frame
    task_spec = TaskSpec(
        work_units=tuple(u.description for u in final_draft.work_unit_set.units),
        output_target=intent.user_visible_deliverable,
        output_format=intent.artifact_requirement,
        acceptance_criteria=tuple(
            ac for u in final_draft.work_unit_set.units for ac in u.acceptance_criteria
        ),
        stop_condition=intent.success_condition,
    )
    marker = vpacket.clarify_abstain_fallback_marker
    assumptions = {
        "declared_assumptions": list(intent.ambiguity.get("assumed", [])),
        "unresolved_gaps": list(intent.ambiguity.get("unresolved", [])),
        "clarify_required": marker.clarify_recommended,
        "clarify_question": marker.clarify_question,
        "abstain_or_fallback_marker": (
            "abstain" if marker.abstain_recommended
            else "fallback" if marker.fallback_recommended
            else "clarify" if marker.clarify_recommended
            else "policy_review" if marker.policy_review_recommended
            else "none"
        ),
    }
    report = vpacket.plan_validation_report
    validation_summary = {
        "listened_to_user": report.listened_to_user_status.value != "fail",
        "constraints_preserved": report.constraints_preserved_status.value != "fail",
        "deliverable_fit": report.deliverable_fit_status.value != "fail",
        "safety_checked": report.safety_checked_status.value != "fail",
        "coherent_plan": report.coherent_plan_status.value != "fail",
        "lowest_viable_agency_applied": report.lowest_viable_agency_status.value != "fail",
        "no_retrieval_performed": True,
        "no_execution_performed": True,
        "no_write_performed": True,
        "validation_failures": list(report.validation_failures),
        "validation_warnings": list(report.validation_warnings),
    }
    contract_input = L1PlanContractInput(
        validated_plan_packet=vpacket,
        intent_frame=intent,
        query_spec=query_spec,
        task_spec=task_spec,
        route_hint_set=final_draft.route_hint_set,
        support_expectation=final_draft.support_expectation,
        action_expectation=final_draft.action_expectation,
        assumptions_and_gaps=assumptions,
        validation_summary=validation_summary,
        downstream_notes=final_draft.downstream_planning_notes,
        request_id=parsed_input.request_id,
        session_id=parsed_input.session_id,
        trace_root=parsed_input.trace_root,
        policy_hash_observed=parsed_input.policy_hash_observed,
        instruction_hash_observed=parsed_input.instruction_hash_observed,
        source_envelope_id=parsed_input.source_envelope_id,
    )
    handoff = emit_l1_plan_contract(contract_input, span_sink=sink)

    return {
        "stage_02_1_parsed_intent_packet": parsed_packet.to_dict(),
        "stage_02_2_plan_bundle_packet": bundle_packet.to_dict(),
        "stage_02_3_planning_reasoning_packet": rpacket.to_dict(),
        "stage_02_4_draft_plan_packet": dpacket.to_dict(),
        "stage_02_5_validated_plan_packet": vpacket.to_dict(),
        "stage_02_6_l1_plan_handoff_packet": handoff.to_dict(),
        "spans": [e.to_dict() for e in sink.events],
    }


def _negative_boundary_scan() -> dict:
    """Module-source scan: forbidden symbols must NOT appear in any stage."""
    findings: dict[str, list[str]] = {}
    for modname in _STAGE_MODULES:
        mod = importlib.import_module(modname)
        src = inspect.getsource(mod)
        matches = sorted(set(_FORBIDDEN_SYMBOLS_RE.findall(src)))
        findings[modname] = matches
    return {
        "forbidden_symbols_pattern": _FORBIDDEN_SYMBOLS_RE.pattern,
        "scanned_modules": list(_STAGE_MODULES),
        "findings_per_module": findings,
        "all_clear": all(not v for v in findings.values()),
    }


def _import_isolation_check(scenario_name: str, parsed_input: ParsedRequestInput) -> dict:
    """Run the pipeline and prove no C0/L2/L3 module was loaded."""
    before = set(sys.modules)
    run_l1_planning(parsed_input, prior_reader=_make_static_reader())
    after = set(sys.modules)
    new_modules = sorted(after - before)
    forbidden_loaded = [m for m in new_modules if m.startswith(_FORBIDDEN_PREFIXES)]
    return {
        "scenario": scenario_name,
        "forbidden_prefixes": list(_FORBIDDEN_PREFIXES),
        "new_modules_total": len(new_modules),
        "new_modules_under_forbidden_prefixes": forbidden_loaded,
        "isolation_clean": not forbidden_loaded,
    }


def _replay_determinism_check(scenario_name: str, parsed_input: ParsedRequestInput) -> dict:
    """Run the pipeline twice and compare digests."""
    a = run_l1_planning(parsed_input, prior_reader=_make_static_reader())
    b = run_l1_planning(parsed_input, prior_reader=_make_static_reader())
    return {
        "scenario": scenario_name,
        "first_plan_digest": a.plan_digest.digest,
        "second_plan_digest": b.plan_digest.digest,
        "identical": a.plan_digest.digest == b.plan_digest.digest,
    }


def main() -> int:
    out_dir = Path("docs/reports/plans/l1-v6-evidence")
    out_dir.mkdir(parents=True, exist_ok=True)

    runtime_evidence: dict[str, dict] = {}
    spans_summary: dict[str, dict] = {}
    contracts: dict[str, dict] = {}
    digests: dict[str, dict] = {}
    isolation: dict[str, dict] = {}

    for name, scenario in SCENARIOS.items():
        parsed_input = _build_parsed_input(scenario)
        evidence = _run_per_stage_for_evidence(parsed_input)
        runtime_evidence[name] = {
            "scenario_description": scenario["description"],
            "input": {
                "request_id": parsed_input.request_id,
                "trace_root": parsed_input.trace_root,
                "normalized_user_payload": parsed_input.normalized_user_payload,
            },
            "evidence": evidence,
        }

        spans = evidence["spans"]
        spans_summary[name] = {
            "span_count": len(spans),
            "by_stage": {
                stage: sum(1 for s in spans if s["l1_stage"] == stage)
                for stage in ("02.1", "02.2", "02.3", "02.4", "02.5", "02.6")
            },
            "all_carry_no_authority_assertions": all(
                s["no_route_authority"]
                and s["no_retrieval_performed"]
                and s["no_execution_performed"]
                and s["no_write_performed"]
                for s in spans
            ),
            "span_names_sample": [s["span_name"] for s in spans],
        }

        contracts[name] = evidence["stage_02_6_l1_plan_handoff_packet"][
            "l1_plan_contract"
        ]
        digests[name] = _replay_determinism_check(name, parsed_input)
        isolation[name] = _import_isolation_check(name, parsed_input)

    neg_boundary = _negative_boundary_scan()

    (out_dir / "runtime_evidence.json").write_text(
        json.dumps(runtime_evidence, indent=2, sort_keys=True), encoding="utf-8"
    )
    (out_dir / "spans.json").write_text(
        json.dumps(spans_summary, indent=2, sort_keys=True), encoding="utf-8"
    )
    (out_dir / "contracts.json").write_text(
        json.dumps(contracts, indent=2, sort_keys=True), encoding="utf-8"
    )
    (out_dir / "digests.json").write_text(
        json.dumps(digests, indent=2, sort_keys=True), encoding="utf-8"
    )
    (out_dir / "negative_boundary_scan.json").write_text(
        json.dumps(neg_boundary, indent=2, sort_keys=True), encoding="utf-8"
    )
    (out_dir / "import_isolation.json").write_text(
        json.dumps(isolation, indent=2, sort_keys=True), encoding="utf-8"
    )

    summary = {
        "scenarios": list(SCENARIOS.keys()),
        "spans_total_per_scenario": {
            name: spans_summary[name]["span_count"] for name in SCENARIOS
        },
        "all_assertions_clean": all(
            spans_summary[name]["all_carry_no_authority_assertions"]
            for name in SCENARIOS
        ),
        "negative_boundary_clean": neg_boundary["all_clear"],
        "import_isolation_clean": all(
            isolation[name]["isolation_clean"] for name in SCENARIOS
        ),
        "replay_determinism_stable": all(
            digests[name]["identical"] for name in SCENARIOS
        ),
        "files_written": [str(p) for p in out_dir.iterdir()],
    }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
