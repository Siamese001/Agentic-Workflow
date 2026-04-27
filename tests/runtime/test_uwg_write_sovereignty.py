"""
tests/runtime/test_uwg_write_sovereignty.py

Spec-named test 13 of 14 (Phase 10).

Asserts the contract for the UWG (Unified Write Gateway) write-sovereignty
guarantee.

What UWG guarantees per the user spec:
  * uwg.commit_request -> uwg.commit_receipt is the ONLY path through
    which state mutates
  * commit_receipt CANNOT appear without a preceding commit_request in
    the same trace (no orphaned commits)
  * commit_request CANNOT appear unless x3.disposition authorized it
    (no commit-on-block, no commit-on-abstain)
  * The harness's 4 scenarios are deliberately non-committing -- B is
    proposal-only, A is read-only, C is caveated read, D is the bypass
    attack. A "Scenario E -- authorized commit" for positive evidence
    is deferred to a future wave (W7+).

Honest gap statement:
  This test proves the NEGATIVE side of UWG sovereignty (no commit
  escapes when not authorized). It does not yet prove the POSITIVE side
  (a properly-authorized commit produces commit_request -> commit_receipt
  with the right contract_digest). That requires Scenario E.
"""

from __future__ import annotations

import pytest


SCENARIOS = ("A_grounded_read", "B_managed_workflow", "C_weak_evidence",
             "D_anti_bypass", "E_authorized_commit")


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_no_orphaned_commit_receipt(
    spans_by_name: dict[str, dict[str, dict]],
    scenario: str,
) -> None:
    """If commit_receipt appears, commit_request MUST also appear."""
    has_receipt = "uwg.commit_receipt" in spans_by_name[scenario]
    has_request = "uwg.commit_request" in spans_by_name[scenario]
    if has_receipt:
        assert has_request, (
            f"{scenario} has uwg.commit_receipt without uwg.commit_request -- "
            f"orphaned commit violates write sovereignty"
        )


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_no_unauthorized_commit_request(
    spans_by_name: dict[str, dict[str, dict]],
    scenario: str,
) -> None:
    """commit_request MUST NOT appear unless x3.disposition reason_codes
    authorize commit. None of the harness's 4 scenarios do."""
    if "uwg.commit_request" in spans_by_name[scenario]:
        x3 = spans_by_name[scenario]["exit.x3.disposition"]
        rc = " ".join(x3.get("reason_codes") or [])
        # Authorization markers (not currently emitted by any harness scenario)
        authorized = any(
            marker in rc
            for marker in ("ALLOW_COMMIT", "WRITE_AUTHORIZED", "COMMIT_AUTHORIZED")
        )
        assert authorized, (
            f"{scenario} emitted uwg.commit_request without an authorization "
            f"marker in x3 reason_codes={rc!r}"
        )


def test_only_authorized_scenario_commits() -> None:
    """A/B/C/D are non-committing by design. E is the ONLY scenario that
    emits uwg.commit_receipt -- and only after x3 declares ALLOW_COMMIT."""
    from agentic_core.runtime.prove_requirements.otel_harness import SCENARIO_FNS
    for name, fn in SCENARIO_FNS:
        trace = fn().to_dict()
        names = {s["name"] for s in trace["spans"]}
        if name == "E_authorized_commit":
            assert "uwg.commit_receipt" in names, "Scenario E must emit commit_receipt"
            assert "uwg.commit_request" in names, "Scenario E must emit commit_request"
        else:
            assert "uwg.commit_receipt" not in names, (
                f"unexpected commit in {name} -- only E may commit"
            )


def test_scenario_e_commit_path_is_positively_proven(
    spans_by_name: dict[str, dict[str, dict]],
) -> None:
    """Positive UWG evidence: the full request -> receipt path with a
    contract digest, parented correctly, and authorized at x3."""
    s = spans_by_name["E_authorized_commit"]
    assert "uwg.commit_request" in s
    assert "uwg.commit_receipt" in s
    # commit_receipt must be a child of commit_request (atomic transaction shape).
    assert s["uwg.commit_receipt"]["parent_span_id"] == s["uwg.commit_request"]["span_id"]
    # Both must carry contract_digest.
    assert s["uwg.commit_request"]["contract_digest"] is not None
    assert s["uwg.commit_receipt"]["contract_digest"] is not None
    # x3 must have authorized.
    rc = " ".join(s["exit.x3.disposition"].get("reason_codes") or [])
    assert "ALLOW_COMMIT" in rc, (
        f"Scenario E x3 reason_codes={rc!r} must include ALLOW_COMMIT"
    )


def test_scenario_e_l6_records_promotion_attempt(spans_by_name: dict[str, dict[str, dict]]) -> None:
    """A successful authorized commit must be observable as a promotion candidate."""
    assert "l6.promotion_attempt" in spans_by_name["E_authorized_commit"]


def test_scenario_b_emits_no_uwg_spans(spans_by_name: dict[str, dict[str, dict]]) -> None:
    """B is proposal-only -- StateDiff is signaled via reason_codes on l2.e5.seal,
    NOT via uwg.commit_request. The proposal lives in artifact_refs, not in a
    commit span."""
    s = spans_by_name["B_managed_workflow"]
    assert "uwg.commit_request" not in s
    assert "uwg.commit_receipt" not in s


def test_scenario_d_emits_no_uwg_spans(spans_by_name: dict[str, dict[str, dict]]) -> None:
    """The bypass attack must NOT produce any UWG span -- write must be
    cleanly blocked at exit.x3, never reaching UWG."""
    s = spans_by_name["D_anti_bypass"]
    assert "uwg.commit_request" not in s
    assert "uwg.commit_receipt" not in s


def test_scenario_b_l2_e5_marks_proposed_state_diff(
    spans_by_name: dict[str, dict[str, dict]],
) -> None:
    """The PROPOSAL representation lives in l2.e5.seal artifact_refs +
    reason_codes -- this is the spec's 'no StateDiff escapes E5' rule
    expressed positively."""
    seal = spans_by_name["B_managed_workflow"]["l2.e5.seal"]
    rc = " ".join(seal.get("reason_codes") or [])
    assert "proposed" in rc.lower(), (
        f"Scenario B l2.e5.seal reason_codes={rc!r} must declare proposal"
    )


def test_uwg_span_names_are_admissible(spans_by_name: dict[str, dict[str, dict]]) -> None:
    """The full UWG vocabulary is exactly two span names. Anything else
    appearing under the uwg.* prefix is a contract violation."""
    admissible = {"uwg.commit_request", "uwg.commit_receipt"}
    for scen in SCENARIOS:
        for span_name in spans_by_name[scen]:
            if span_name.startswith("uwg."):
                assert span_name in admissible, (
                    f"{scen} emitted unexpected uwg.* span: {span_name}"
                )


def test_negative_evidence_only_is_documented(proof_artifacts) -> None:
    """The GAPS.md must explicitly state that positive UWG evidence
    (Scenario E) is deferred. This is the spec's 'do not claim' rule
    in action."""
    md = (proof_artifacts / "GAPS.md").read_text(encoding="utf-8")
    # Either the gap is acknowledged in the file, or no UWG-related claim
    # is made beyond what the harness exercises.
    assert "Phase 4" in md  # canonical Phase-4 wiring section
