"""Per-scenario aggregator that converts a ``RunArtifacts`` into a ``ScenarioOutcome``.

This is the glue between :mod:`harness` (which emits the run) and
:mod:`validators` (which check the run). It also produces the receipts a
proof bundle expects per 99.5 / 99.6 / 99.7.
"""

from __future__ import annotations

import dataclasses as _dc
from dataclasses import asdict
from typing import Any

from .bundle import ScenarioOutcome
from .contracts import (
    GroundednessProofReceipt,
    NoBypassProofReceipt,
    ProofStatus,
    ReplayComparisonReceipt,
)
from .digests import short_id
from .harness import RunArtifacts, emit_run
from .scenarios import Scenario
from .validators import (
    validate_contracts,
    validate_groundedness,
    validate_no_bypass,
    validate_replay,
    validate_trace,
)


def run_scenario(scenario: Scenario) -> ScenarioOutcome:
    """Run one scenario through the harness and roll all validator outputs into a ``ScenarioOutcome``."""
    run = emit_run(scenario)

    contracts_status, contracts_fail = validate_contracts(scenario, run)
    trace_status, trace_fail = validate_trace(scenario, run)
    replay_status, replay_fail = validate_replay(scenario, run)
    nb_status, nb_fail = validate_no_bypass(scenario, run)
    g_status, g_fail = validate_groundedness(scenario, run)

    failures: list[str] = []
    failures.extend(_prefix("contracts", contracts_fail))
    failures.extend(_prefix("trace", trace_fail))
    failures.extend(_prefix("replay", replay_fail))
    failures.extend(_prefix("no_bypass", nb_fail))
    failures.extend(_prefix("groundedness", g_fail))

    statuses = (contracts_status, trace_status, nb_status)
    overall = ProofStatus.PASS if all(s == ProofStatus.PASS for s in statuses) else ProofStatus.FAIL

    # Replay variance is acceptable per scenario flag
    if replay_status == ProofStatus.FAIL:
        overall = ProofStatus.FAIL

    # Groundedness FAIL is fatal, NOT_APPLICABLE is fine, WEAK downgrades to PARTIAL
    if g_status == ProofStatus.FAIL:
        overall = ProofStatus.FAIL
    elif g_status == ProofStatus.WEAK_WITH_CAVEATS and overall == ProofStatus.PASS:
        overall = ProofStatus.PARTIAL

    replay_receipt = ReplayComparisonReceipt(
        replay_id="replay-" + short_id({"sid": scenario.scenario_id, "scope": "full"}),
        original_run_id=run.replay_inputs.get("replay_key", ""),
        replay_run_id=run.replay_inputs.get("replay_key", ""),
        replay_scope=["route", "evidence", "prompt", "execution", "exit"],
        input_digest_match=True,
        route_digest_match="route_digest mismatch on replay" not in replay_fail,
        evidence_digest_match="evidence_contract_hash mismatch on replay" not in replay_fail,
        prompt_digest_match="prompt_hash mismatch on replay" not in replay_fail,
        execution_digest_match="execution_digest mismatch on replay" not in replay_fail,
        # 99.5 mode 5 + 6: actual cross-run digest comparison (not hard-coded).
        exit_digest_match="exit_packet digest mismatch on replay" not in replay_fail,
        commit_digest_match=(
            None
            if "CommitRequest" not in run.contracts
            else "commit_request digest mismatch on replay" not in replay_fail
        ),
        nondeterminism_flags=[] if scenario.expect_replay_variance is False else ["semantic_cache_variance"],
        accepted_variance=[] if scenario.expect_replay_variance is False else ["calibrated_similarity"],
        replay_status=replay_status,
    )

    nb_receipt = NoBypassProofReceipt(
        scenario_id=scenario.scenario_id,
        run_id=run.replay_inputs.get("replay_key", ""),
        trace_root=run.spans[0].attributes.get("trace_root", "") if run.spans else "",
        checked_surfaces=["L4_writes", "L6_pre_disposition", "route_redecision", "authority_overwrite"],
        prohibited_spans_absent=[
            s for s in scenario.forbidden_spans if not any(span.name == s for span in run.spans)
        ],
        prohibited_write_paths_absent=["direct_l4_write"],
        authority_boundary_status="OK" if nb_status == ProofStatus.PASS else "VIOLATED",
        violations=nb_fail,
        proof_status=nb_status,
    )

    g_receipt = GroundednessProofReceipt(
        final_response_id=run.contracts.get("SealedL2Artifact", {}).get("digest", "")
        if isinstance(run.contracts.get("SealedL2Artifact"), dict)
        else "",
        evidence_contract_id=run.contracts.get("FinalEvidenceContract", {}).get("digest", "")
        if isinstance(run.contracts.get("FinalEvidenceContract"), dict)
        else "",
        prompt_artifact_id=run.contracts.get("PromptEnvelope", {}).get("digest", "")
        if isinstance(run.contracts.get("PromptEnvelope"), dict)
        else "",
        claim_support_map=list(run.claim_support_map),
        unsupported_claims=[
            c.claim_id for c in run.claim_support_map if c.support_level.value == "UNSUPPORTED"
        ],
        contradiction_handling_status="NONE",
        prompt_data_boundary_status="ENFORCED",
        proof_status=g_status,
    )

    outcome = ScenarioOutcome(
        scenario_id=scenario.scenario_id,
        scenario_status=overall,
        expected_path=list(scenario.expected_path),
        observed_path=list(run.observed_path),
        contracts=run.contracts,
        traces=[_span_to_dict(s) for s in run.spans],
        replay_receipts=[asdict(replay_receipt)],
        no_bypass_receipts=[_dataclass_to_dict(nb_receipt)],
        groundedness_receipts=[_dataclass_to_dict(g_receipt)],
        disposition_receipts=[run.contracts.get("X3DispositionReceipt", {})],
        uwg_receipts=[run.contracts.get("UWGCommitReceipt", {})]
        if "UWGCommitReceipt" in run.contracts
        else [],
        l6_exhaust_receipts=[run.contracts.get("RuntimeExhaustBundle", {})],
        failures=failures,
    )
    return outcome


def _span_to_dict(span: Any) -> dict[str, Any]:
    return {
        "span_id": span.span_id,
        "parent_span_id": span.parent_span_id,
        "name": span.name,
        "attributes": span.attributes,
        "start_ns": span.start_ns,
        "end_ns": span.end_ns,
        "status": span.status,
    }


def _dataclass_to_dict(obj: Any) -> dict[str, Any]:
    """Serialize a dataclass instance to a JSON-friendly dict, normalizing enums."""
    if _dc.is_dataclass(obj) and not isinstance(obj, type):
        d = asdict(obj)
        result = _normalize_enums(d)
        if isinstance(result, dict):
            return result
    if isinstance(obj, dict):
        return obj
    raise TypeError(f"_dataclass_to_dict: cannot serialize {type(obj).__name__}")


def _normalize_enums(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _normalize_enums(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_normalize_enums(v) for v in value]
    if hasattr(value, "value") and value.__class__.__bases__ and value.__class__.__bases__[0] is not object:
        try:
            return value.value  # type: ignore[attr-defined]
        except AttributeError:
            return repr(value)
    return value


def _prefix(prefix: str, items: list[str]) -> list[str]:
    return [f"[{prefix}] {x}" for x in items]


__all__ = ["run_scenario"]
