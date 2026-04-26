"""Validators for the E2E proof harness.

One validator per 99-series sibling document:
- ``validate_contracts`` (99.3 contract emission and handoff)
- ``validate_trace`` (99.4 OTEL trace tree)
- ``validate_replay`` (99.5 deterministic replay)
- ``validate_no_bypass`` (99.6 no-bypass and sovereignty)
- ``validate_groundedness`` (99.7 evidence-prompt-output groundedness)
- ``validate_route_coverage`` (99.2 route path coverage)

Each returns a tuple ``(ProofStatus, list[str] failures)`` so callers can roll
multiple validators into a per-scenario ``ScenarioOutcome``.
"""

from __future__ import annotations

from typing import Any

from .contracts import (
    OutputAction,
    ProofStatus,
    RouteId,
    SupportLevel,
    XDisposition,
)
from .digests import digest
from .harness import RunArtifacts, emit_run
from .scenarios import Scenario


# ---------------------------------------------------------------------------
# 99.3 contract emission and handoff
# ---------------------------------------------------------------------------


def validate_contracts(scenario: Scenario, run: RunArtifacts) -> tuple[ProofStatus, list[str]]:
    failures: list[str] = []

    required = [
        "ValidatedRequest",
        "L1PlanContract",
        "RouteContract",
        "ExitReviewPacket",
        "X3DispositionReceipt",
        "RuntimeExhaustBundle",
    ]
    if scenario.grounding_required and scenario.route_id not in {
        RouteId.R1A_EXACT_CACHE,
        RouteId.R1B_SEMANTIC_CACHE,
        RouteId.R5_FALLBACK,
        RouteId.HITL_POSTURE,
    }:
        required.append("FinalEvidenceContract")
        required.append("PromptEnvelope")
    if scenario.route_id == RouteId.R3R4_MANAGED_WORKFLOW:
        required.append("L3WorkflowContract")
    if scenario.route_id == RouteId.UWG_COMMIT_PATH:
        required.extend(["CommitRequest", "UWGCommitReceipt"])

    for name in required:
        if name not in run.contracts:
            failures.append(f"missing required contract: {name}")

    # Authority field continuity
    expected_root_keys = {"request_id", "run_id", "trace_root", "policy_hash", "blueprint_hash", "replay_key"}
    canonical_root: dict[str, Any] | None = None
    for cname, payload in run.contracts.items():
        canonical_root = _check_authority_root(cname, payload, expected_root_keys, canonical_root, failures)

    # Lineage references resolve
    digests_by_name = {n: p.get("digest") for n, p in run.contracts.items() if isinstance(p, dict)}
    # (downstream, upstream, ref_field). PromptEnvelope and L2ExecutionRequest carry
    # two upstream refs; we check the route-bound one for both.
    chain: list[tuple[str, str, str]] = [
        ("L1PlanContract", "ValidatedRequest", "upstream_ref"),
        ("RouteContract", "L1PlanContract", "upstream_ref"),
        ("FinalEvidenceContract", "RouteContract", "upstream_ref"),
        ("L3WorkflowContract", "RouteContract", "upstream_ref"),
        ("PromptEnvelope", "RouteContract", "upstream_route_ref"),
        ("L2ExecutionRequest", "RouteContract", "upstream_route_ref"),
        ("SealedL2Artifact", "L2ExecutionRequest", "upstream_ref"),
        ("ExitReviewPacket", "SealedL2Artifact", "upstream_ref"),
        ("X3DispositionReceipt", "ExitReviewPacket", "upstream_ref"),
        ("CommitRequest", "X3DispositionReceipt", "upstream_ref"),
        ("UWGCommitReceipt", "CommitRequest", "upstream_ref"),
        ("RuntimeExhaustBundle", "X3DispositionReceipt", "upstream_ref"),
    ]
    for downstream, upstream, ref_field in chain:
        if downstream in run.contracts and upstream in run.contracts:
            payload = run.contracts[downstream]
            ref = payload.get(ref_field, "")
            expected = digests_by_name.get(upstream, "")
            if ref != expected:
                failures.append(f"{downstream}.{ref_field} does not point to {upstream}.digest")

    # No layer emitted another layer's contract: enforced structurally because
    # only the harness emits and each contract carries its declared contract_type.
    for cname, payload in run.contracts.items():
        if not isinstance(payload, dict):
            failures.append(f"{cname}: not serialized as dict")
            continue
        if payload.get("contract_type") != cname:
            failures.append(f"{cname}: contract_type field {payload.get('contract_type')!r} does not match")

    # Direct-write rule: SealedL2Artifact must not have direct_l4_write True.
    sealed = run.contracts.get("SealedL2Artifact")
    if isinstance(sealed, dict) and sealed.get("direct_l4_write"):
        failures.append("SealedL2Artifact.direct_l4_write is True — only UWG may write L4")

    return (ProofStatus.PASS if not failures else ProofStatus.FAIL, failures)


# ---------------------------------------------------------------------------
# 99.4 OTEL trace tree validation
# ---------------------------------------------------------------------------


def validate_trace(scenario: Scenario, run: RunArtifacts) -> tuple[ProofStatus, list[str]]:
    failures: list[str] = []

    if not run.spans:
        failures.append("no spans emitted")
        return (ProofStatus.FAIL, failures)

    span_names = {s.name for s in run.spans}

    # All expected spans present
    for name in scenario.expected_spans:
        if name not in span_names:
            failures.append(f"expected span missing: {name}")

    # No forbidden spans
    for name in scenario.forbidden_spans:
        if name in span_names:
            failures.append(f"forbidden span present: {name}")

    # Required root attributes on every span
    required_attrs = ("request_id", "run_id", "trace_root", "policy_hash", "blueprint_hash", "replay_key")
    for span in run.spans:
        missing = [k for k in required_attrs if not span.attributes.get(k)]
        if missing:
            failures.append(f"span {span.name!r} missing attrs {missing}")

    # Parent ids form a valid tree (every non-root parent must exist)
    span_ids = {s.span_id for s in run.spans}
    for span in run.spans:
        if span.parent_span_id and span.parent_span_id not in span_ids:
            failures.append(f"span {span.name!r} has dangling parent {span.parent_span_id}")

    # L6 must not appear before exit.disposition
    order = {s.name: i for i, s in enumerate(run.spans)}
    if (
        "l6.ingest" in order
        and "exit.disposition" in order
        and order["l6.ingest"] <= order["exit.disposition"]
    ):
        failures.append("l6.ingest span appears before exit.disposition")

    # uwg.commit only allowed when route is UWG_COMMIT_PATH
    if "uwg.commit" in span_names and scenario.route_id != RouteId.UWG_COMMIT_PATH:
        failures.append("uwg.commit span emitted on non-commit route")

    # 99.4 §VALIDATION RULE: tool/model spans must carry provider, model/tool id,
    # latency, tokens, cost, status. Side-effect spans must carry capability_token_ref
    # and sandbox_envelope_ref.
    for span in run.spans:
        _check_l2_exec_attributes(scenario, span, failures)

    return (ProofStatus.PASS if not failures else ProofStatus.FAIL, failures)


_MODEL_SPAN_REQUIRED = ("provider", "model_id", "latency_ms", "tokens_in", "tokens_out", "cost_usd", "status")
_SIDE_EFFECT_REQUIRED = ("capability_token_ref", "sandbox_envelope_ref")
_SIDE_EFFECT_ROUTES = {RouteId.R4_SINGLE_ACTION, RouteId.R3_PLUS_R4_SINGLE_STEP, RouteId.UWG_COMMIT_PATH}


def _check_l2_exec_attributes(scenario: Scenario, span: Any, failures: list[str]) -> None:
    """Per-span 99.4 attribute enforcement. Helper keeps validate_trace tight."""
    if span.name == "l2.e3.exec":
        missing = [k for k in _MODEL_SPAN_REQUIRED if span.attributes.get(k) in (None, "")]
        if missing:
            failures.append(f"l2.e3.exec span missing model attrs {missing}")
        if scenario.route_id in _SIDE_EFFECT_ROUTES:
            se_missing = [k for k in _SIDE_EFFECT_REQUIRED if not span.attributes.get(k)]
            if se_missing:
                failures.append(f"l2.e3.exec side-effect span missing {se_missing}")
    if span.name == "uwg.commit" and not span.attributes.get("commit_request_id"):
        failures.append("uwg.commit span missing commit_request_id")


# ---------------------------------------------------------------------------
# 99.5 deterministic replay
# ---------------------------------------------------------------------------


def validate_replay(scenario: Scenario, run: RunArtifacts) -> tuple[ProofStatus, list[str]]:
    failures: list[str] = []

    if not run.replay_inputs.get("replay_key"):
        failures.append("missing replay_key")
    if not run.replay_inputs.get("snapshot_manifest"):
        failures.append("missing snapshot_manifest")

    # Per 99.5: same inputs (snapshot, policy, blueprint, intent) MUST produce
    # the same digests. Re-run the harness with the SAME seed: every replay-
    # bound surface must match exactly. (Seed is the simulator's stand-in for
    # the canonical request; identical seed = identical input.)
    second = emit_run(scenario, seed=0)

    same_route = run.replay_inputs.get("route_digest") == second.replay_inputs.get("route_digest")
    same_evidence = run.replay_inputs.get("evidence_contract_hash") == second.replay_inputs.get(
        "evidence_contract_hash"
    )
    same_prompt = run.replay_inputs.get("prompt_hash") == second.replay_inputs.get("prompt_hash")
    same_exec = run.replay_inputs.get("execution_digest") == second.replay_inputs.get("execution_digest")

    if not same_route:
        failures.append("route_digest mismatch on replay")
    if (
        not same_evidence
        and scenario.grounding_required
        and scenario.route_id
        not in {
            RouteId.R1A_EXACT_CACHE,
            RouteId.R1B_SEMANTIC_CACHE,
            RouteId.R5_FALLBACK,
            RouteId.HITL_POSTURE,
        }
    ):
        failures.append("evidence_contract_hash mismatch on replay")
    if not same_prompt and scenario.route_id not in {
        RouteId.R1A_EXACT_CACHE,
        RouteId.R1B_SEMANTIC_CACHE,
        RouteId.R5_FALLBACK,
        RouteId.HITL_POSTURE,
    }:
        failures.append("prompt_hash mismatch on replay")
    if not same_exec:
        failures.append("execution_digest mismatch on replay")

    if scenario.expect_replay_variance:
        # Variance is acceptable; harness itself is deterministic, so we mark this PASS.
        return (ProofStatus.EXPLAINED_VARIANCE, failures)

    return (ProofStatus.PASS if not failures else ProofStatus.FAIL, failures)


# ---------------------------------------------------------------------------
# 99.6 no-bypass + sovereignty
# ---------------------------------------------------------------------------


_PROHIBITED_SPANS_BY_ROUTE: dict[RouteId, tuple[str, ...]] = {
    RouteId.R1A_EXACT_CACHE: ("l2.e3.exec", "l3.workflow.build", "uwg.commit"),
    RouteId.R1B_SEMANTIC_CACHE: ("l2.e3.exec", "l3.workflow.build", "uwg.commit"),
    RouteId.R5_FALLBACK: ("l2.e3.exec", "uwg.commit"),
    RouteId.R3_SIMPLE_GROUNDED_READ: ("l3.workflow.build", "l3.step.dispatch", "uwg.commit"),
    RouteId.R4_SINGLE_ACTION: ("l3.workflow.build", "uwg.commit"),
    RouteId.R3_PLUS_R4_SINGLE_STEP: ("l3.workflow.build", "uwg.commit"),
    RouteId.R3R4_MANAGED_WORKFLOW: ("uwg.commit",),
    RouteId.HITL_POSTURE: ("l2.e3.exec", "uwg.commit"),
    RouteId.UWG_COMMIT_PATH: (),
}


def validate_no_bypass(scenario: Scenario, run: RunArtifacts) -> tuple[ProofStatus, list[str]]:
    failures: list[str] = []
    span_names = {s.name for s in run.spans}

    # 99.6: only UWG writes L4
    sealed = run.contracts.get("SealedL2Artifact")
    if isinstance(sealed, dict) and sealed.get("direct_l4_write"):
        failures.append("L4 write attempted outside UWG (SealedL2Artifact.direct_l4_write=True)")

    # 99.6: L6 ingest must come AFTER exit.disposition
    order = [s.name for s in run.spans]
    if "l6.ingest" in order and "exit.disposition" in order:
        if order.index("l6.ingest") <= order.index("exit.disposition"):
            failures.append("L6 influence before Exit disposition")

    # Route-specific prohibited spans (anti-bypass tests from 99.6)
    for forbidden in _PROHIBITED_SPANS_BY_ROUTE.get(scenario.route_id, ()):
        if forbidden in span_names:
            failures.append(f"prohibited span for route {scenario.route_id.value}: {forbidden}")

    # Authority fields cannot be overwritten by lower-authority content:
    # validated by digest stability across the chain (re-digesting a contract
    # whose root has been tampered would shift its declared digest).
    for name, payload in run.contracts.items():
        if not isinstance(payload, dict):
            continue
        declared = payload.get("digest")
        # Recompute the digest, masking the digest field to avoid recursion
        recompute = {k: v for k, v in payload.items() if k != "digest"}
        recomputed = digest(recompute)
        if declared != recomputed:
            failures.append(f"{name}: declared digest does not match recomputed (tamper detected)")

    # CommitRequest only valid when X3 disposition is X3C_COMMIT_ELIGIBLE
    commit_req = run.contracts.get("CommitRequest")
    disposition = run.contracts.get("X3DispositionReceipt")
    if commit_req is not None:
        if (
            not isinstance(disposition, dict)
            or disposition.get("disposition") != XDisposition.X3C_COMMIT_ELIGIBLE.value
        ):
            failures.append("CommitRequest emitted without X3C_COMMIT_ELIGIBLE disposition")

    # 99 owns no runtime side effects: nothing to check on this side because
    # the harness emits inert dataclasses only.

    return (ProofStatus.PASS if not failures else ProofStatus.FAIL, failures)


# ---------------------------------------------------------------------------
# 99.7 groundedness
# ---------------------------------------------------------------------------


def validate_groundedness(scenario: Scenario, run: RunArtifacts) -> tuple[ProofStatus, list[str]]:
    failures: list[str] = []

    if not scenario.grounding_required or scenario.route_id in {
        RouteId.R1A_EXACT_CACHE,
        RouteId.R1B_SEMANTIC_CACHE,
        RouteId.R5_FALLBACK,
        RouteId.HITL_POSTURE,
    }:
        return (ProofStatus.NOT_APPLICABLE, failures)

    sealed = run.contracts.get("SealedL2Artifact")
    evidence = run.contracts.get("FinalEvidenceContract")
    prompt = run.contracts.get("PromptEnvelope")

    if evidence is None:
        failures.append("grounding required but FinalEvidenceContract missing")
    if prompt is None:
        failures.append("grounding required but PromptEnvelope missing")

    if isinstance(sealed, dict):
        cited = sealed.get("cited_evidence_refs") or []
        if not cited:
            failures.append("sealed artifact cites zero evidence on grounded route")

    # Every claim must have a support map entry
    if not run.claim_support_map:
        failures.append("claim_support_map empty on grounded route")

    for cs in run.claim_support_map:
        if cs.support_level == SupportLevel.UNSUPPORTED and cs.output_action == OutputAction.INCLUDE:
            failures.append(f"unsupported claim {cs.claim_id!r} would be INCLUDEd")
        if cs.citation_anchor_status not in {"RESOLVED", "NOT_REQUIRED"}:
            failures.append(f"claim {cs.claim_id!r} citation anchor unresolved")

    # Prompt evidence references match C0 evidence (data boundary check)
    if isinstance(prompt, dict) and isinstance(evidence, dict):
        if prompt.get("upstream_evidence_ref") != evidence.get("digest"):
            failures.append(
                "PromptEnvelope.upstream_evidence_ref does not match FinalEvidenceContract.digest"
            )

    return (ProofStatus.PASS if not failures else ProofStatus.FAIL, failures)


# ---------------------------------------------------------------------------
# 99.2 route coverage
# ---------------------------------------------------------------------------


def validate_route_coverage(
    scenarios_run: list[tuple[Scenario, RunArtifacts]],
) -> tuple[ProofStatus, list[str]]:
    """Validate that every required route family has at least one passing scenario."""
    failures: list[str] = []
    seen: set[RouteId] = set()
    for scenario, run in scenarios_run:
        # A scenario contributes to coverage iff its observed_path includes
        # the expected route emission span and contracts exist.
        if "l0.route.emit_contract" in run.observed_path and "RouteContract" in run.contracts:
            seen.add(scenario.route_id)
    required = set(RouteId)
    missing = required - seen
    if missing:
        failures.append(f"missing route coverage for: {sorted(m.value for m in missing)}")
    return (ProofStatus.PASS if not failures else ProofStatus.FAIL, failures)


def _check_authority_root(
    cname: str,
    payload: Any,
    expected_keys: set[str],
    canonical: dict[str, Any] | None,
    failures: list[str],
) -> dict[str, Any] | None:
    """Validate the authority root of one contract; return updated canonical root."""
    raw_root = payload.get("root") if isinstance(payload, dict) else None
    if not isinstance(raw_root, dict):
        failures.append(f"{cname}: missing root authority block")
        return canonical
    root: dict[str, Any] = raw_root
    missing = [k for k in expected_keys if not root.get(k)]
    if missing:
        failures.append(f"{cname}: empty authority field(s) {missing}")
    if canonical is None:
        return root
    for key in expected_keys:
        if root.get(key) != canonical.get(key):
            failures.append(f"{cname}: authority field {key!r} differs from canonical root")
    return canonical


__all__ = [
    "validate_contracts",
    "validate_trace",
    "validate_replay",
    "validate_no_bypass",
    "validate_groundedness",
    "validate_route_coverage",
]
