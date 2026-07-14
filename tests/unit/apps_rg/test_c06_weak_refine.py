"""Focused C0.6 bounded-refinement and invariant tests."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from pathlib import Path

from apps_rg.runtime.c0 import c06_weak_refine as c06_module
from apps_rg.runtime.c0.c03_resume_graph_contracts import (
    TraversalRecorder,
    build_candidate_decision,
    build_candidate_receipt,
    finalize_canonical_section_plan,
    stable_digest,
)
from apps_rg.runtime.c0.c06_weak_refine import (
    C06_RECEIPT_ARTIFACT,
    finalize_c06_after_c05,
    maybe_c06_weak_refine,
)
from apps_rg.runtime.c0.c05_fec_packet import build_c05_final_evidence_contract
from apps_rg.runtime.c0.c07_handoff_audit import audit_c07_handoff

REPO = Path(__file__).resolve().parents[3]
SECTION = "competencies"
ROLE_FAMILY = "SVP_ENGINEERING_AI_PLATFORM"
GRAPH_DIGEST = "graph-digest-1"


def _atoms() -> list[dict]:
    return [
        {
            "fact_id": "fact-1",
            "text_to_embed": "Led a governed platform change with measurable impact.",
            "proof_status": "proof_eligible",
            "source_type": "proof_pool",
            "source_span_ref": "ledger:fact-1",
            "allowed_sections": [SECTION],
            "blocked_sections": [],
        }
    ]


def _c03(*, direct: bool, graph_digest: str = GRAPH_DIGEST) -> dict:
    return {
        "schema_version": "c03_skills_graph_v1",
        "section_id": SECTION,
        "role_family_key": ROLE_FAMILY,
        "bindings": [
            {
                "fact_id": "fact-1",
                "graph_support_strength": "DIRECT" if direct else "NONE",
                "claim_support_allowed": direct,
            }
        ],
        "graph_candidate_decision_ledger": [
            {
                "candidate_path_id": "fact:fact-1/skill:skill-1",
                "decision": "selected",
                "authority": {"authority_pass": True},
            }
        ],
        "graph_candidate_receipt": {"candidate_conservation_pass": True},
        "graph_traversal_receipt": {"pass": True, "events_digest": "events-1"},
        "pretarget_authority_receipt": {"authority_before_targeting_pass": True},
        "selected_graph_plan_receipt": {"graph_hash": graph_digest},
        "new_atoms_created": 0,
        "broad_fact_link_fallback_used": False,
        "label_tag_proof_fallback_used": False,
    }


def _plan(
    *,
    graph_digest: str = GRAPH_DIGEST,
    fact_skill_id: str = "skill-1",
    decision_skill_id: str = "skill-1",
) -> dict:
    path_id = f"root:fact-1/skill:{decision_skill_id}"
    authority = {
        "authority_pass": True,
        "targeting_consulted": False,
        "authority_evaluated_before_targeting": True,
    }
    decision = build_candidate_decision(
        section_id=SECTION,
        candidate_id=decision_skill_id,
        candidate_type="leaf_skill",
        candidate_path_id=path_id,
        decision="selected",
        reason_codes=["selected_by_authority_then_rank"],
        authority=authority,
        hop_depth=1,
        parent_id="fact-1",
        root_id="fact-1",
    )
    recorder = TraversalRecorder(section_id=SECTION, max_hop_depth=1)
    recorder.record(
        event_type="edge_traversed",
        hop_depth=1,
        source_node_id="fact-1",
        target_node_id=decision_skill_id,
        edge_type="role_episode_contains_skill",
        candidate_path_id=path_id,
    )
    recorder.record(
        event_type="authority_evaluated",
        hop_depth=1,
        source_node_id="fact-1",
        target_node_id=decision_skill_id,
        edge_type="role_episode_contains_skill",
        candidate_path_id=path_id,
        authority_pass=True,
    )
    recorder.record(
        event_type="candidate_terminal",
        hop_depth=1,
        source_node_id="fact-1",
        target_node_id=decision_skill_id,
        edge_type="role_episode_contains_skill",
        candidate_path_id=path_id,
        authority_pass=True,
        decision="selected",
        reason_codes=["selected_by_authority_then_rank"],
    )
    raw = {
        "section_id": SECTION,
        "source_authority_contract": {
            "graph_digest": graph_digest,
            "targeting_inputs_are_non_authority": True,
        },
        "facts": [
            {"fact_id": "fact-1", "graph_skill_node_ids": [fact_skill_id]}
        ],
        "graph_candidate_decision_ledger": [decision],
        "graph_candidate_receipt": build_candidate_receipt(
            section_id=SECTION, decisions=[decision]
        ),
        "graph_traversal_receipt": recorder.build_receipt(decisions=[decision]),
    }
    return finalize_canonical_section_plan(raw)


def _run(initial: dict, *, c05_status: str = "PASS") -> tuple[dict, dict]:
    return maybe_c06_weak_refine(
        section_id=SECTION,
        role_family_key=ROLE_FAMILY,
        route_ref="route_contract.json",
        run_id="run-1",
        atoms=_atoms(),
        initial_c03=initial,
        initial_c05_receipt={"support_status": c05_status},
        selected_graph_plan=_plan(),
        repo_root=REPO,
    )


def test_weak_coverage_retries_exactly_once_with_frozen_plan(monkeypatch) -> None:
    calls: list[dict] = []
    refined = _c03(direct=True)

    def _fake_expand(**kwargs):
        calls.append(kwargs)
        return deepcopy(refined)

    monkeypatch.setattr(c06_module, "expand_c03_graph_bindings", _fake_expand)
    adopted, receipt = _run(_c03(direct=False), c05_status="WEAK")
    receipt = finalize_c06_after_c05(
        receipt, final_c05_receipt={"support_status": "PASS"}
    )

    assert adopted == refined
    assert len(calls) == 1
    assert calls[0]["strict_ranked_selection"] is False
    assert calls[0]["selected_graph_plan"] == _plan()
    assert calls[0]["atoms"] == _atoms()
    assert receipt["attempted"] is True
    assert receipt["attempt_count"] == receipt["max_attempts"] == 1
    assert receipt["outcome"] == "PASS"
    assert receipt["pass"] is True
    assert receipt["graph_digest_before"] == GRAPH_DIGEST
    assert receipt["frozen_graph_digest"] == GRAPH_DIGEST
    assert receipt["graph_digest_after"] == GRAPH_DIGEST
    assert receipt["binding_fact_ids_before"] == ["fact-1"]
    assert receipt["binding_fact_ids_after"] == ["fact-1"]
    assert receipt["final_coverage"]["direct_supported_fact_ids"] == ["fact-1"]
    assert receipt["final_coverage"]["proof_fact_ids"] == ["fact-1"]
    digest_payload = dict(receipt)
    digest_payload.pop("receipt_digest")
    assert receipt["receipt_digest"] == stable_digest(digest_payload)


def test_graph_snapshot_mismatch_blocks_before_retry(monkeypatch) -> None:
    calls = 0

    def _fake_expand(**_kwargs):
        nonlocal calls
        calls += 1
        return _c03(direct=True)

    monkeypatch.setattr(c06_module, "expand_c03_graph_bindings", _fake_expand)
    adopted, receipt = _run(_c03(direct=False, graph_digest="other-graph"))

    assert calls == 0
    assert adopted["bindings"][0]["claim_support_allowed"] is False
    assert receipt["attempted"] is False
    assert receipt["attempt_count"] == 0
    assert receipt["outcome"] == "BLOCKED"
    assert "initial_graph_snapshot_digest_changed" in receipt["failure_reasons"]


def test_stale_plan_digest_and_cross_fact_skill_path_block_before_retry(
    monkeypatch,
) -> None:
    calls = 0

    def _unexpected(**_kwargs):
        nonlocal calls
        calls += 1
        return _c03(direct=True)

    monkeypatch.setattr(c06_module, "expand_c03_graph_bindings", _unexpected)
    stale = _plan()
    stale["facts"][0]["graph_skill_node_ids"] = ["skill-2"]
    _, stale_receipt = maybe_c06_weak_refine(
        section_id=SECTION,
        role_family_key=ROLE_FAMILY,
        route_ref="route_contract.json",
        run_id="run-1",
        atoms=_atoms(),
        initial_c03=_c03(direct=False),
        initial_c05_receipt={"support_status": "WEAK"},
        selected_graph_plan=stale,
        repo_root=REPO,
    )
    assert calls == 0
    assert stale_receipt["pass"] is False
    assert "selected_graph_plan_digest_invalid" in stale_receipt["failure_reasons"]

    # This plan has a fresh, internally valid seal, but its fact projection and
    # selected leaf path disagree. The exact fact->skill->path check must still
    # reject it before C0.3 executes.
    cross_path = _plan(fact_skill_id="skill-2", decision_skill_id="skill-1")
    _, cross_receipt = maybe_c06_weak_refine(
        section_id=SECTION,
        role_family_key=ROLE_FAMILY,
        route_ref="route_contract.json",
        run_id="run-1",
        atoms=_atoms(),
        initial_c03=_c03(direct=False),
        initial_c05_receipt={"support_status": "WEAK"},
        selected_graph_plan=cross_path,
        repo_root=REPO,
    )
    assert calls == 0
    assert cross_receipt["pass"] is False
    assert any(
        reason.startswith("selected_graph_plan_fact_skill_path_mismatch:")
        for reason in cross_receipt["failure_reasons"]
    )


def test_refinement_cannot_mutate_atom_content_or_provenance(monkeypatch) -> None:
    original_atoms = _atoms()

    def _mutating_expand(**kwargs):
        kwargs["atoms"][0]["text_to_embed"] = "INJECTED"
        kwargs["atoms"][0]["source_span_ref"] = "untrusted:replacement"
        return _c03(direct=True)

    monkeypatch.setattr(c06_module, "expand_c03_graph_bindings", _mutating_expand)
    adopted, receipt = maybe_c06_weak_refine(
        section_id=SECTION,
        role_family_key=ROLE_FAMILY,
        route_ref="route_contract.json",
        run_id="run-1",
        atoms=original_atoms,
        initial_c03=_c03(direct=False),
        initial_c05_receipt={"support_status": "WEAK"},
        selected_graph_plan=_plan(),
        repo_root=REPO,
    )

    assert original_atoms == _atoms()
    assert adopted["bindings"][0]["claim_support_allowed"] is False
    assert receipt["pass"] is False
    assert "atom_payload_changed_during_refinement" in receipt["failure_reasons"]
    assert receipt["atom_payload_digest_before"] != receipt["atom_payload_digest_after"]


def test_initial_c03_route_drift_blocks_before_retry(monkeypatch) -> None:
    initial = _c03(direct=False)
    initial["role_family_key"] = "DIFFERENT_ROLE"

    def _unexpected(**_kwargs):
        raise AssertionError("route-drifted C0.3 must not be retried")

    monkeypatch.setattr(c06_module, "expand_c03_graph_bindings", _unexpected)
    adopted, receipt = _run(initial, c05_status="WEAK")

    assert adopted == initial
    assert receipt["attempted"] is False
    assert receipt["pass"] is False
    assert "initial_c03_route_scope_mismatch" in receipt["failure_reasons"]
    assert receipt["route_scope"]["role_family_key"] == "DIFFERENT_ROLE"
    assert receipt["requested_route_scope"]["role_family_key"] == ROLE_FAMILY


def test_refined_route_or_fact_scope_drift_is_rejected(monkeypatch) -> None:
    route_drift = _c03(direct=True)
    route_drift["role_family_key"] = "DIFFERENT_ROLE"
    monkeypatch.setattr(
        c06_module,
        "expand_c03_graph_bindings",
        lambda **_kwargs: deepcopy(route_drift),
    )
    adopted, receipt = _run(_c03(direct=False))
    assert adopted["bindings"][0]["claim_support_allowed"] is False
    assert receipt["outcome"] == "BLOCKED"
    assert "route_scope_changed" in receipt["failure_reasons"]

    fact_drift = _c03(direct=True)
    fact_drift["bindings"][0]["fact_id"] = "fact-2"
    monkeypatch.setattr(
        c06_module,
        "expand_c03_graph_bindings",
        lambda **_kwargs: deepcopy(fact_drift),
    )
    _, receipt = _run(_c03(direct=False))
    assert "atom_or_fact_scope_changed" in receipt["failure_reasons"]
    assert "direct_coverage_scope_mismatch" in receipt["failure_reasons"]


def test_unresolved_weakness_and_final_c05_weakness_fail_closed(monkeypatch) -> None:
    monkeypatch.setattr(
        c06_module,
        "expand_c03_graph_bindings",
        lambda **_kwargs: _c03(direct=False),
    )
    initial = _c03(direct=False)
    adopted, receipt = _run(initial)
    assert adopted == initial
    assert receipt["attempt_count"] == 1
    assert receipt["outcome"] == "BLOCKED"
    assert "refinement_did_not_restore_full_direct_coverage" in receipt["failure_reasons"]

    successful = _c03(direct=True)
    monkeypatch.setattr(
        c06_module,
        "expand_c03_graph_bindings",
        lambda **_kwargs: successful,
    )
    _, receipt = _run(initial, c05_status="WEAK")
    receipt = finalize_c06_after_c05(
        receipt, final_c05_receipt={"support_status": "WEAK"}
    )
    assert receipt["outcome"] == "BLOCKED"
    assert receipt["pass"] is False
    assert "final_c05_support_not_pass" in receipt["failure_reasons"]


def test_refinement_exception_is_sealed_and_initial_result_is_retained(monkeypatch) -> None:
    initial = _c03(direct=False)

    def _failed_expand(**_kwargs):
        raise RuntimeError("projection unavailable")

    monkeypatch.setattr(c06_module, "expand_c03_graph_bindings", _failed_expand)
    adopted, receipt = _run(initial, c05_status="WEAK")

    assert adopted == initial
    assert receipt["attempted"] is True
    assert receipt["attempt_count"] == 1
    assert receipt["outcome"] == "BLOCKED"
    assert receipt["pass"] is False
    assert receipt["failure_reasons"] == [
        "refinement_execution_failed:RuntimeError"
    ]
    assert "projection unavailable" not in str(receipt)
    digest_payload = dict(receipt)
    digest_payload.pop("receipt_digest")
    assert receipt["receipt_digest"] == stable_digest(digest_payload)


def test_blocked_initial_c03_is_not_retried(monkeypatch) -> None:
    initial = _c03(direct=False)
    initial["graph_traversal_receipt"]["pass"] = False

    def _unexpected(**_kwargs):
        raise AssertionError("blocked C0.3 must not be retried")

    monkeypatch.setattr(c06_module, "expand_c03_graph_bindings", _unexpected)
    _, receipt = _run(initial)
    assert receipt["attempted"] is False
    assert receipt["outcome"] == "BLOCKED"
    assert "initial_c03_contract_blocked" in receipt["failure_reasons"]


def test_c07_accepts_valid_c06_receipt_and_rejects_tampering(monkeypatch) -> None:
    atoms = _atoms()
    initial = _c03(direct=True)
    _, receipt = _run(initial)
    receipt = finalize_c06_after_c05(
        receipt, final_c05_receipt={"support_status": "PASS"}
    )
    fec, c05 = build_c05_final_evidence_contract(
        section_id=SECTION,
        atoms=atoms,
        strata={},
        graph_bindings=initial["bindings"],
        front_spine=None,
        allowed_fact_ids=["fact-1"],
    )
    c07 = audit_c07_handoff(
        fec=fec,
        c02_receipt={"graph_inference_performed": False},
        c03_receipt=initial,
        graph_bindings=initial["bindings"],
        allowed_fact_ids=["fact-1"],
        c05_receipt=c05,
        c06_receipt=receipt,
    )
    assert c07["handoff_safe"] is True, c07
    assert c07["checks"]["c06_bounded_refinement_pass"] is True

    missing_c06 = audit_c07_handoff(
        fec=fec,
        c02_receipt={"graph_inference_performed": False},
        c03_receipt=initial,
        graph_bindings=initial["bindings"],
        allowed_fact_ids=["fact-1"],
        c05_receipt=c05,
    )
    assert missing_c06["handoff_safe"] is False
    assert missing_c06["checks"]["c06_receipt_present"] is False
    assert missing_c06["checks"]["c06_bounded_refinement_pass"] is False
    assert "c06_receipt_missing" in missing_c06["violations"]

    substituted_c03 = dict(initial)
    substituted_c03["role_family_projection"] = {"tampered_after_c06": True}
    stale_receipt_handoff = audit_c07_handoff(
        fec=fec,
        c02_receipt={"graph_inference_performed": False},
        c03_receipt=substituted_c03,
        graph_bindings=initial["bindings"],
        allowed_fact_ids=["fact-1"],
        c05_receipt=c05,
        c06_receipt=receipt,
    )
    assert stale_receipt_handoff["handoff_safe"] is False
    assert (
        "c06_adopted_c03_digest_mismatch"
        in stale_receipt_handoff["violations"]
    )

    tampered = dict(receipt)
    tampered["route_changed"] = True
    c07 = audit_c07_handoff(
        fec=fec,
        c02_receipt={"graph_inference_performed": False},
        c03_receipt=initial,
        graph_bindings=initial["bindings"],
        allowed_fact_ids=["fact-1"],
        c05_receipt=c05,
        c06_receipt=tampered,
    )
    assert c07["handoff_safe"] is False
    assert "c06_route_scope_changed" in c07["violations"]
    assert "c06_receipt_digest_invalid" in c07["violations"]

    monkeypatch.setattr(
        c06_module,
        "expand_c03_graph_bindings",
        lambda **_kwargs: _c03(direct=True),
    )
    _, attempted = _run(_c03(direct=False), c05_status="WEAK")
    attempted = finalize_c06_after_c05(
        attempted, final_c05_receipt={"support_status": "PASS"}
    )
    attempted_fec = replace(
        fec,
        weak_support_refinement_attempts=(
            f"{C06_RECEIPT_ARTIFACT}#{attempted['receipt_digest']}",
        ),
    )
    attempted_c07 = audit_c07_handoff(
        fec=attempted_fec,
        c02_receipt={"graph_inference_performed": False},
        c03_receipt=initial,
        graph_bindings=initial["bindings"],
        allowed_fact_ids=["fact-1"],
        c05_receipt=c05,
        c06_receipt=attempted,
    )
    assert attempted_c07["handoff_safe"] is True

    stale_ref_fec = replace(
        attempted_fec,
        weak_support_refinement_attempts=(
            f"{C06_RECEIPT_ARTIFACT}#stale-digest",
        ),
    )
    stale_ref_c07 = audit_c07_handoff(
        fec=stale_ref_fec,
        c02_receipt={"graph_inference_performed": False},
        c03_receipt=initial,
        graph_bindings=initial["bindings"],
        allowed_fact_ids=["fact-1"],
        c05_receipt=c05,
        c06_receipt=attempted,
    )
    assert stale_ref_c07["handoff_safe"] is False
    assert "c06_fec_attempt_ref_digest_mismatch" in stale_ref_c07["violations"]
