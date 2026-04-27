"""
Phase 5 / Phase 8 -- canonical trace harness.

Runs each E2E scenario from the user spec, emitting all required runtime
spans through RuntimeSpanRecorder. Output traces are written to
artifacts/runtime/requirements_proof/traces/scenario_<id>.json.

Scenario A: simple grounded read (R3, no L3, no UWG)
Scenario B: managed workflow with L3 and StateDiff proposal (no commit)
Scenario C: weak evidence triggers C0.6 refinement
Scenario D: prompt-injection bypass attack (HITL packetization, no UWG)

Each scenario is wrapped in a single ``runtime.request`` root span so the
trace is a tree (one root, every other span reachable). The scenario body
is a plain callable that emits stage spans as siblings under the root.

These traces are EVIDENCE OF THE CONTRACT, not evidence of full runtime.
They prove the OTEL schema is well-formed and a complete tree can be
constructed for every scenario the spec requires. Wiring the recorder into
real runtime code is a future Phase-4 task gated by per-stage Author-Gate.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Callable, Dict

from agentic_core.runtime.prove_requirements.otel_contract import (
    RuntimeSpanRecorder,
    RuntimeTrace,
    write_trace,
)


def _digest(label: str) -> str:
    return hashlib.sha1(label.encode("utf-8")).hexdigest()[:16]


def _emit_under_request(
    scenario: str,
    route_id: str,
    policy_hash: str,
    blueprint_hash: str,
    replay_key: str,
    body_fn: Callable[[RuntimeSpanRecorder, str, str, str], None],
) -> RuntimeTrace:
    """Emit a runtime.request root then delegate to body_fn for stage spans."""
    rec = RuntimeSpanRecorder(scenario=scenario)
    with rec.span(
        "runtime.request",
        route_id=route_id,
        policy_hash=policy_hash,
        blueprint_hash=blueprint_hash,
        replay_key=replay_key,
    ):
        body_fn(rec, policy_hash, blueprint_hash, replay_key)
    return rec.finalize()


# ---------------------------------------------------------------------------
# Scenario A -- simple grounded read (no L3, no UWG)
# ---------------------------------------------------------------------------

def _body_scenario_a(
    rec: RuntimeSpanRecorder,
    policy_hash: str,
    blueprint_hash: str,
    replay_key: str,
) -> None:
    route = "R3_SIMPLE_GROUNDED_READ"
    with rec.span("u0.intake", policy_hash=policy_hash, contract_digest=_digest("intake_envelope_v1")):
        pass
    with rec.span("l1.plan", policy_hash=policy_hash, contract_digest=_digest("L1PlanContract_v1")):
        pass
    with rec.span(
        "l0.route_decision",
        route_id=route,
        policy_hash=policy_hash,
        blueprint_hash=blueprint_hash,
        replay_key=replay_key,
        contract_digest=_digest("RouteContract_v1"),
        reason_codes=["grounding_required=true", "L3_required=false"],
    ):
        pass
    with rec.span(
        "c0.0.preflight",
        route_id=route,
        policy_hash=policy_hash,
        replay_key=replay_key,
        reason_codes=["grounding_eligible"],
    ):
        with rec.span("c0.1.retrieval_plan", route_id=route):
            pass
        with rec.span("c0.2.fetch", route_id=route, artifact_refs=["chunk:42", "chunk:73"]):
            with rec.span("c0.2a.hydrate", route_id=route):
                pass
            with rec.span("c0.3.graph_traverse", route_id=route):
                pass
            with rec.span("c0.4.shape_rerank_stratify", route_id=route):
                pass
        with rec.span(
            "c0.5.final_evidence_contract",
            route_id=route,
            policy_hash=policy_hash,
            blueprint_hash=blueprint_hash,
            replay_key=replay_key,
            contract_digest=_digest("FinalEvidenceContract_v1"),
            reason_codes=["support_target_met"],
        ):
            pass
    with rec.span(
        "prompt_assembly.compile",
        route_id=route,
        policy_hash=policy_hash,
        contract_digest=_digest("CompiledPromptArtifact_v1"),
    ):
        pass
    with rec.span("l2.e1.prep", route_id=route, step_id="e1", policy_hash=policy_hash):
        with rec.span("l2.e2.valid", step_id="e2", route_id=route):
            pass
        with rec.span(
            "l2.e3.exec",
            step_id="e3",
            route_id=route,
            tokens_in=420,
            tokens_out=180,
            cost_usd=0.002,
        ):
            pass
        with rec.span(
            "l2.e5.seal",
            step_id="e5",
            route_id=route,
            contract_digest=_digest("SealedL2Artifact_v1"),
        ):
            pass
    with rec.span("exit.preflight", route_id=route):
        with rec.span(
            "exit.x1.gates",
            gate_id="X1A..X1I",
            policy_hash=policy_hash,
            reason_codes=["all_gates_passed"],
        ):
            pass
        with rec.span("exit.x2.aggregate", route_id=route):
            pass
        with rec.span(
            "exit.x3.disposition",
            route_id=route,
            replay_key=replay_key,
            reason_codes=["ALLOW_FINISH"],
        ):
            pass
    with rec.span("l6.ingest", route_id=route):
        with rec.span("l6.evaluate", route_id=route):
            pass


def run_scenario_a_grounded_read() -> RuntimeTrace:
    return _emit_under_request(
        "A_grounded_read",
        "R3_SIMPLE_GROUNDED_READ",
        _digest("policy:v1"),
        _digest("blueprint:v1"),
        _digest("replay:scenario_a"),
        _body_scenario_a,
    )


# ---------------------------------------------------------------------------
# Scenario B -- managed workflow with L3 and StateDiff proposal (no commit)
# ---------------------------------------------------------------------------

def _body_scenario_b(
    rec: RuntimeSpanRecorder,
    policy_hash: str,
    blueprint_hash: str,
    replay_key: str,
) -> None:
    route = "R5_MANAGED_WORKFLOW"
    with rec.span("u0.intake", policy_hash=policy_hash):
        pass
    with rec.span("l1.plan", policy_hash=policy_hash, contract_digest=_digest("L1PlanContract_v1")):
        pass
    with rec.span(
        "l0.route_decision",
        route_id=route,
        policy_hash=policy_hash,
        blueprint_hash=blueprint_hash,
        replay_key=replay_key,
        contract_digest=_digest("RouteContract_v1"),
        reason_codes=["L3_required=true"],
    ):
        pass
    with rec.span("c0.0.preflight", route_id=route):
        with rec.span("c0.1.retrieval_plan", route_id=route):
            pass
        with rec.span("c0.2.fetch", route_id=route):
            with rec.span("c0.2a.hydrate", route_id=route):
                pass
            with rec.span("c0.3.graph_traverse", route_id=route):
                pass
            with rec.span("c0.4.shape_rerank_stratify", route_id=route):
                pass
        with rec.span(
            "c0.5.final_evidence_contract",
            route_id=route,
            contract_digest=_digest("FinalEvidenceContract_v1"),
            reason_codes=["support_target_met"],
        ):
            pass
    with rec.span("l3.workflow_start", route_id=route, blueprint_hash=blueprint_hash):
        with rec.span(
            "l3.step_dispatch",
            route_id=route,
            step_id="step-1",
            contract_digest=_digest("L3StepContract_v1"),
        ):
            pass
    with rec.span("prompt_assembly.compile", route_id=route):
        pass
    with rec.span("l2.e1.prep", route_id=route, step_id="step-1"):
        with rec.span("l2.e2.valid", step_id="step-1"):
            pass
        with rec.span(
            "l2.e3.exec",
            step_id="step-1",
            tokens_in=600,
            tokens_out=240,
            artifact_refs=["StateDiffCandidate:proposed"],
        ):
            pass
        with rec.span(
            "l2.e5.seal",
            step_id="step-1",
            contract_digest=_digest("SealedL2Artifact_v1"),
            reason_codes=["proposed_state_diff_only"],
        ):
            pass
    with rec.span("exit.preflight", route_id=route):
        with rec.span(
            "exit.x1.gates",
            gate_id="X1A..X3C",
            reason_codes=["write_eligibility_failed_no_user_authority"],
        ):
            pass
        with rec.span("exit.x2.aggregate", route_id=route):
            pass
        with rec.span(
            "exit.x3.disposition",
            route_id=route,
            replay_key=replay_key,
            reason_codes=["ALLOW_FINISH_PROPOSAL_ONLY"],
        ):
            pass
    with rec.span("l6.ingest", route_id=route):
        with rec.span("l6.evaluate", route_id=route):
            pass
        with rec.span("l6.rca_or_proposal", route_id=route):
            pass


def run_scenario_b_managed_workflow() -> RuntimeTrace:
    return _emit_under_request(
        "B_managed_workflow",
        "R5_MANAGED_WORKFLOW",
        _digest("policy:v1"),
        _digest("blueprint:v1_managed"),
        _digest("replay:scenario_b"),
        _body_scenario_b,
    )


# ---------------------------------------------------------------------------
# Scenario C -- weak evidence triggers C0.6 refinement
# ---------------------------------------------------------------------------

def _body_scenario_c(
    rec: RuntimeSpanRecorder,
    policy_hash: str,
    blueprint_hash: str,
    replay_key: str,
) -> None:
    route = "R3_SIMPLE_GROUNDED_READ"
    with rec.span("u0.intake", policy_hash=policy_hash):
        pass
    with rec.span("l1.plan"):
        pass
    with rec.span(
        "l0.route_decision",
        route_id=route,
        policy_hash=policy_hash,
        blueprint_hash=blueprint_hash,
        replay_key=replay_key,
        contract_digest=_digest("RouteContract_v1"),
    ):
        pass
    with rec.span("c0.0.preflight", route_id=route):
        with rec.span("c0.1.retrieval_plan", route_id=route):
            pass
        with rec.span("c0.2.fetch", route_id=route):
            with rec.span("c0.2a.hydrate", route_id=route):
                pass
            with rec.span("c0.3.graph_traverse", route_id=route):
                pass
            with rec.span("c0.4.shape_rerank_stratify", route_id=route, reason_codes=["contradictions_kept"]):
                pass
        with rec.span(
            "c0.5.final_evidence_contract",
            route_id=route,
            contract_digest=_digest("FinalEvidenceContract_weak"),
            reason_codes=["WEAK_WITH_CAVEATS", "support_target_partial"],
        ):
            with rec.span(
                "c0.6.weak_support_refinement",
                reason_codes=["budget_remaining", "scope_unchanged"],
            ):
                pass
    with rec.span("prompt_assembly.compile", route_id=route):
        pass
    with rec.span("l2.e1.prep", route_id=route, step_id="e1"):
        with rec.span("l2.e2.valid", step_id="e2"):
            pass
        with rec.span(
            "l2.e3.exec",
            step_id="e3",
            tokens_in=380,
            tokens_out=120,
            reason_codes=["caveated_answer"],
        ):
            pass
        with rec.span(
            "l2.e5.seal",
            step_id="e5",
            contract_digest=_digest("SealedL2Artifact_v1"),
        ):
            pass
    with rec.span("exit.preflight", route_id=route):
        with rec.span(
            "exit.x1.gates",
            gate_id="X1A..X1I",
            reason_codes=["abstain_eligible_due_to_weak_evidence"],
        ):
            pass
        with rec.span("exit.x2.aggregate"):
            pass
        with rec.span(
            "exit.x3.disposition",
            replay_key=replay_key,
            reason_codes=["ALLOW_FINISH_WITH_CAVEAT"],
        ):
            pass
    with rec.span("l6.ingest"):
        with rec.span("l6.evaluate"):
            pass


def run_scenario_c_weak_evidence() -> RuntimeTrace:
    return _emit_under_request(
        "C_weak_evidence",
        "R3_SIMPLE_GROUNDED_READ",
        _digest("policy:v1"),
        _digest("blueprint:v1"),
        _digest("replay:scenario_c"),
        _body_scenario_c,
    )


# ---------------------------------------------------------------------------
# Scenario D -- prompt-injection bypass attempt
# ---------------------------------------------------------------------------

def _body_scenario_d(
    rec: RuntimeSpanRecorder,
    policy_hash: str,
    blueprint_hash: str,
    replay_key: str,
) -> None:
    with rec.span("u0.intake", policy_hash=policy_hash):
        pass
    with rec.span("l1.plan"):
        pass
    with rec.span(
        "l0.route_decision",
        route_id="R3_SIMPLE_GROUNDED_READ",
        policy_hash=policy_hash,
        blueprint_hash=blueprint_hash,
        replay_key=replay_key,
    ):
        pass
    with rec.span("c0.0.preflight"):
        with rec.span("c0.1.retrieval_plan"):
            pass
        with rec.span("c0.2.fetch", artifact_refs=["chunk:adversarial"]):
            with rec.span("c0.2a.hydrate"):
                pass
            with rec.span("c0.3.graph_traverse"):
                pass
            with rec.span(
                "c0.4.shape_rerank_stratify",
                reason_codes=["airlock_quoted", "treated_as_data"],
            ):
                pass
        with rec.span(
            "c0.5.final_evidence_contract",
            contract_digest=_digest("FinalEvidenceContract_adversarial"),
            reason_codes=["adversarial_content_fenced"],
        ):
            pass
    with rec.span(
        "prompt_assembly.compile",
        reason_codes=["airlock_pass", "data_only_treatment"],
    ):
        pass
    with rec.span("l2.e1.prep"):
        with rec.span("l2.e2.valid"):
            pass
        with rec.span("l2.e3.exec", reason_codes=["instruction_injection_neutralized"]):
            pass
        with rec.span(
            "l2.e5.seal",
            contract_digest=_digest("SealedL2Artifact_v1"),
            reason_codes=["no_proposed_state_diff"],
        ):
            pass
    with rec.span("exit.preflight"):
        with rec.span(
            "exit.x1.gates",
            gate_id="X1A..X1I+X3C",
            reason_codes=["write_eligibility_blocked"],
        ):
            pass
        with rec.span("exit.x2.aggregate"):
            pass
        with rec.span(
            "exit.x3.disposition",
            replay_key=replay_key,
            reason_codes=["BLOCK_WRITE", "ALLOW_FINISH_READONLY"],
            status="BLOCKED",
        ):
            pass
    with rec.span(
        "hitl.packetization",
        reason_codes=["adversarial_pattern_review_optional"],
    ):
        pass
    with rec.span("l6.ingest"):
        with rec.span("l6.evaluate"):
            pass
        with rec.span(
            "l6.rca_or_proposal",
            reason_codes=["adversarial_pattern_recorded_for_future_run"],
        ):
            pass


def run_scenario_d_anti_bypass() -> RuntimeTrace:
    return _emit_under_request(
        "D_anti_bypass",
        "R3_SIMPLE_GROUNDED_READ",
        _digest("policy:v1"),
        _digest("blueprint:v1"),
        _digest("replay:scenario_d"),
        _body_scenario_d,
    )


# ---------------------------------------------------------------------------
# Scenario E -- authorized write commit (W6 positive UWG evidence)
# ---------------------------------------------------------------------------

def _body_scenario_e(
    rec: RuntimeSpanRecorder,
    policy_hash: str,
    blueprint_hash: str,
    replay_key: str,
) -> None:
    """The happy-path managed workflow that DOES commit.

    Differs from Scenario B in three ways:
      1. exit.x1.gates passes write-eligibility (X3A..X3C)
      2. exit.x3.disposition emits ALLOW_COMMIT (the authorization marker)
      3. uwg.commit_request -> uwg.commit_receipt actually fire
      4. l6.promotion_attempt fires after a successful commit
    """
    route = "R5_MANAGED_WORKFLOW"
    with rec.span("u0.intake", policy_hash=policy_hash):
        pass
    with rec.span("l1.plan", policy_hash=policy_hash, contract_digest=_digest("L1PlanContract_v1")):
        pass
    with rec.span(
        "l0.route_decision",
        route_id=route,
        policy_hash=policy_hash,
        blueprint_hash=blueprint_hash,
        replay_key=replay_key,
        contract_digest=_digest("RouteContract_v1"),
        reason_codes=["L3_required=true", "write_authority_present"],
    ):
        pass
    with rec.span("c0.0.preflight", route_id=route):
        with rec.span("c0.1.retrieval_plan", route_id=route):
            pass
        with rec.span("c0.2.fetch", route_id=route):
            with rec.span("c0.2a.hydrate", route_id=route):
                pass
            with rec.span("c0.3.graph_traverse", route_id=route):
                pass
            with rec.span("c0.4.shape_rerank_stratify", route_id=route):
                pass
        with rec.span(
            "c0.5.final_evidence_contract",
            route_id=route,
            contract_digest=_digest("FinalEvidenceContract_v1"),
            reason_codes=["support_target_met"],
        ):
            pass
    with rec.span("l3.workflow_start", route_id=route, blueprint_hash=blueprint_hash):
        with rec.span(
            "l3.step_dispatch",
            route_id=route,
            step_id="step-1",
            contract_digest=_digest("L3StepContract_v1"),
        ):
            pass
    with rec.span("prompt_assembly.compile", route_id=route):
        pass
    with rec.span("l2.e1.prep", route_id=route, step_id="step-1"):
        with rec.span("l2.e2.valid", step_id="step-1"):
            pass
        with rec.span(
            "l2.e3.exec",
            step_id="step-1",
            tokens_in=600,
            tokens_out=240,
            cost_usd=0.003,
            artifact_refs=["StateDiffCandidate:authorized"],
        ):
            pass
        with rec.span(
            "l2.e5.seal",
            step_id="step-1",
            contract_digest=_digest("SealedL2Artifact_v1"),
            reason_codes=["state_diff_authorized"],
        ):
            pass
    with rec.span("exit.preflight", route_id=route):
        with rec.span(
            "exit.x1.gates",
            gate_id="X1A..X3C",
            reason_codes=["all_gates_passed", "write_eligibility_passed"],
        ):
            pass
        with rec.span("exit.x2.aggregate", route_id=route):
            pass
        with rec.span(
            "exit.x3.disposition",
            route_id=route,
            replay_key=replay_key,
            reason_codes=["ALLOW_FINISH", "ALLOW_COMMIT"],
        ):
            pass
    # The actual commit -- only fires when x3 authorizes it.
    with rec.span(
        "uwg.commit_request",
        route_id=route,
        policy_hash=policy_hash,
        blueprint_hash=blueprint_hash,
        contract_digest=_digest("UWGCommitContract_v1"),
        reason_codes=["authorized_by_x3"],
        artifact_refs=["StateDiffCandidate:authorized"],
    ):
        with rec.span(
            "uwg.commit_receipt",
            route_id=route,
            replay_key=replay_key,
            contract_digest=_digest("UWGCommitReceipt_v1"),
            reason_codes=["commit_durable"],
        ):
            pass
    with rec.span("l6.ingest", route_id=route):
        with rec.span("l6.evaluate", route_id=route):
            pass
        with rec.span(
            "l6.rca_or_proposal",
            route_id=route,
            reason_codes=["successful_commit_observed"],
        ):
            with rec.span(
                "l6.promotion_attempt",
                route_id=route,
                reason_codes=["promotion_candidate_logged"],
            ):
                pass


def run_scenario_e_authorized_commit() -> RuntimeTrace:
    return _emit_under_request(
        "E_authorized_commit",
        "R5_MANAGED_WORKFLOW",
        _digest("policy:v1"),
        _digest("blueprint:v1_authorized"),
        _digest("replay:scenario_e"),
        _body_scenario_e,
    )


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

SCENARIO_FNS = (
    ("A_grounded_read", run_scenario_a_grounded_read),
    ("B_managed_workflow", run_scenario_b_managed_workflow),
    ("C_weak_evidence", run_scenario_c_weak_evidence),
    ("D_anti_bypass", run_scenario_d_anti_bypass),
    ("E_authorized_commit", run_scenario_e_authorized_commit),
)


def run_all_scenarios(traces_dir: Path) -> Dict[str, str]:
    out: Dict[str, str] = {}
    traces_dir.mkdir(parents=True, exist_ok=True)
    for name, fn in SCENARIO_FNS:
        trace = fn()
        path = traces_dir / f"scenario_{name}.json"
        write_trace(trace, path)
        out[name] = str(path)
    return out
