"""Tests for v4 invariants module.

Coverage:
    - SealedL2ArtifactContents builds correctly from receipt chain
    - All 7 sections populated (identity/governance/execution/evidence/
      replay/observability/terminal)
    - check_invariants returns no violations on a healthy SUCCESS run
    - check_invariants flags missing replay metadata
    - check_invariants flags REJECTED with user_visible_safe=True
    - check_invariants flags commit_requested=True without state diff
    - L2_INVARIANTS registry is non-empty
"""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.orchestration.l2_phase_pipeline import (
    ExecutorResult,
    HealerResult,
    L2PhasePipeline,
    ValidatorResult,
)
from agentic_core.L2_execution.types.l2_v3_receipts import (
    DeterminismBundle,
    HealOutcomeStamp,
    LineageRoot,
    ResultClass,
    TerminalStamp,
    ValidationOutcome,
)
from agentic_core.L2_execution.types.l2_v4_invariants import (
    L2_INVARIANTS,
    InvariantViolation,
    SealedL2ArtifactContents,
    check_invariants,
)

# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def determinism() -> DeterminismBundle:
    return DeterminismBundle(
        blueprint_hash="bp-1",
        policy_hash="pol-1",
        prompt_hash="pr-1",
        input_hash="in-1",
        replay_key="rk-1",
        attempt_seed="seed-1",
    )


@pytest.fixture
def lineage() -> LineageRoot:
    return LineageRoot(
        parent_route_id="route-1",
        parent_plan_id="plan-1",
        parent_step_id="step-1",
    )


def _approve(_p) -> ValidatorResult:  # type: ignore[no-untyped-def]
    return ValidatorResult(
        outcome=ValidationOutcome.PASS, classified_side_effect="READ"
    )


def _success(_p, _v, n) -> ExecutorResult:  # type: ignore[no-untyped-def]
    return ExecutorResult(
        result_class=ResultClass.SUCCESS,
        trace_id=f"t-{n}",
        span_id=f"s-{n}",
        latency_ms=1.0,
        tokens_used=10,
        return_code=0,
        output_digest="ok",
    )


def _no_heal(_a) -> HealerResult:  # type: ignore[no-untyped-def]
    return HealerResult(
        outcome=HealOutcomeStamp.NEEDS_HELP, reason_code="unhealable"
    )


# ---------------------------------------------------------------------------
# SealedL2ArtifactContents.from_receipts
# ---------------------------------------------------------------------------


class TestSealedContentsFromReceipts:
    def test_builds_all_seven_sections(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        pipe = L2PhasePipeline(
            validator_fn=_approve, executor_fn=_success, healer_fn=_no_heal
        )
        r = pipe.run("route-1", "step-1", determinism, lineage)
        assert r.dispatch is not None
        contents = SealedL2ArtifactContents.from_receipts(
            prep=r.prep,
            validation=r.validation,
            attempts=r.attempts,
            heals=r.heals,
            dispatch=r.dispatch,
            payload={"answer": "yes"},
            evidence_refs=("doc-1",),
        )
        assert contents.identity.run_id == r.prep.run_id
        assert contents.identity.parent_route_id == "route-1"
        assert contents.governance.policy_hash == "pol-1"
        assert contents.governance.blueprint_hash == "bp-1"
        assert contents.governance.side_effect_class == "READ"
        assert contents.execution.attempt_count == 1
        assert contents.execution.repair_count == 0
        assert contents.evidence.source_refs == ("doc-1",)
        assert contents.replay.replay_key == "rk-1"
        assert contents.observability.trace_id == "t-1"
        assert contents.terminal.terminal_class is TerminalStamp.SUCCESS
        assert contents.terminal.user_visible_safe is True


# ---------------------------------------------------------------------------
# check_invariants
# ---------------------------------------------------------------------------


class TestCheckInvariants:
    def test_healthy_success_run_no_violations(
        self, determinism: DeterminismBundle, lineage: LineageRoot
    ) -> None:
        pipe = L2PhasePipeline(
            validator_fn=_approve, executor_fn=_success, healer_fn=_no_heal
        )
        r = pipe.run("route-1", "step-1", determinism, lineage)
        assert r.dispatch is not None
        contents = SealedL2ArtifactContents.from_receipts(
            prep=r.prep,
            validation=r.validation,
            attempts=r.attempts,
            heals=r.heals,
            dispatch=r.dispatch,
        )
        violations = check_invariants(contents)
        assert violations == ()

    def test_rejected_with_user_visible_safe_flagged(
        self,
        determinism: DeterminismBundle,
        lineage: LineageRoot,
    ) -> None:
        pipe = L2PhasePipeline(
            validator_fn=_approve, executor_fn=_success, healer_fn=_no_heal
        )
        r = pipe.run("route-1", "step-1", determinism, lineage)
        assert r.dispatch is not None
        # Build sealed contents but tamper with terminal section to force
        # REJECTED + user_visible_safe=True (should violate).
        from agentic_core.L2_execution.types.l2_v4_invariants import (
            TerminalSection,
        )

        good = SealedL2ArtifactContents.from_receipts(
            prep=r.prep,
            validation=r.validation,
            attempts=r.attempts,
            heals=r.heals,
            dispatch=r.dispatch,
        )
        bad_terminal = TerminalSection(
            terminal_class=TerminalStamp.REJECTED,
            reason_code="injection_breach",
            user_visible_safe=True,  # WRONG: rejected MUST be unsafe
        )
        bad_contents = SealedL2ArtifactContents(
            identity=good.identity,
            governance=good.governance,
            execution=good.execution,
            evidence=good.evidence,
            replay=good.replay,
            observability=good.observability,
            terminal=bad_terminal,
        )
        violations = check_invariants(bad_contents)
        titles = {v.title for v in violations}
        assert "quarantine_marked_unsafe" in titles

    def test_commit_requested_without_diff_flagged(
        self,
        determinism: DeterminismBundle,
        lineage: LineageRoot,
    ) -> None:
        pipe = L2PhasePipeline(
            validator_fn=_approve, executor_fn=_success, healer_fn=_no_heal
        )
        r = pipe.run("route-1", "step-1", determinism, lineage)
        assert r.dispatch is not None
        from agentic_core.L2_execution.types.l2_v4_invariants import (
            ExecutionSection,
            TerminalSection,
        )

        good = SealedL2ArtifactContents.from_receipts(
            prep=r.prep,
            validation=r.validation,
            attempts=r.attempts,
            heals=r.heals,
            dispatch=r.dispatch,
        )
        bad_contents = SealedL2ArtifactContents(
            identity=good.identity,
            governance=good.governance,
            execution=ExecutionSection(
                payload=None,
                proposed_state_diff={},  # empty diff
                attempt_count=1,
            ),
            evidence=good.evidence,
            replay=good.replay,
            observability=good.observability,
            terminal=TerminalSection(
                terminal_class=TerminalStamp.SUCCESS,
                reason_code="ok",
                commit_requested=True,  # but no diff to back it up
            ),
        )
        violations = check_invariants(bad_contents)
        titles = {v.title for v in violations}
        assert "commit_only_when_proposing" in titles

    def test_missing_replay_metadata_flagged(
        self,
        determinism: DeterminismBundle,
        lineage: LineageRoot,
    ) -> None:
        from agentic_core.L2_execution.types.l2_v4_invariants import (
            EvidenceSection,
            ExecutionSection,
            GovernanceSection,
            IdentitySection,
            ObservabilitySection,
            ReplaySection,
            TerminalSection,
        )

        bad = SealedL2ArtifactContents(
            identity=IdentitySection(
                sealed_l2_artifact_id="x",
                run_id="r",
                route_id="rt",
                parent_route_id="parent",
            ),
            governance=GovernanceSection(
                compliance_hash="ch",
                policy_hash="",  # MISSING
                blueprint_hash="",  # MISSING
                capability_token_ref="ct",
                sandbox_envelope_ref="se",
            ),
            execution=ExecutionSection(),
            evidence=EvidenceSection(),
            replay=ReplaySection(
                replay_key="",  # MISSING
                input_hash="",  # MISSING
                prompt_hash="",
            ),
            observability=ObservabilitySection(trace_id="t"),
            terminal=TerminalSection(
                terminal_class=TerminalStamp.SUCCESS, reason_code="ok"
            ),
        )
        violations = check_invariants(bad)
        titles = {v.title for v in violations}
        assert "replay_lineage_preserved" in titles


class TestL2InvariantsRegistry:
    def test_registry_populated(self) -> None:
        assert len(L2_INVARIANTS) >= 5
        ids = {inv.invariant_id for inv in L2_INVARIANTS}
        # v4 numbers 1, 2, 6, 7, 8, 12, 13 covered by current check fns.
        assert 1 in ids
        assert 8 in ids
        assert 13 in ids

    def test_violations_are_typed(self) -> None:
        # No fixtures needed — building synthetic contents to trip multiple
        # invariants at once.
        from agentic_core.L2_execution.types.l2_v4_invariants import (
            EvidenceSection,
            ExecutionSection,
            GovernanceSection,
            IdentitySection,
            ObservabilitySection,
            ReplaySection,
            TerminalSection,
        )

        bad = SealedL2ArtifactContents(
            identity=IdentitySection(
                sealed_l2_artifact_id="",
                run_id="",  # MISSING
                route_id="",  # MISSING
                parent_route_id="",  # MISSING
            ),
            governance=GovernanceSection(
                compliance_hash="",
                policy_hash="",
                blueprint_hash="",
                capability_token_ref="",
                sandbox_envelope_ref="",
            ),
            execution=ExecutionSection(),
            evidence=EvidenceSection(),
            replay=ReplaySection(
                replay_key="", input_hash="", prompt_hash=""
            ),
            observability=ObservabilitySection(trace_id=""),
            terminal=TerminalSection(
                terminal_class=TerminalStamp.SUCCESS, reason_code=""
            ),
        )
        v = check_invariants(bad)
        assert all(isinstance(x, InvariantViolation) for x in v)
        assert len(v) >= 3  # multiple invariants violated
