"""End-to-end + negative + replay + OTEL + matrix tests for the L2 pipeline
resolution-consistency invariant (04.5a INV-RC-1..8).

Exercises the REAL `L2PhasePipeline.run()` chokepoint with adapter functions
that each independently compute their own L2ResolutionContext and digest.
No mocks of the gate or the digest function — match emerges from real
canonical-JSON SHA-256 hashing.

Test classes map to user prompt sections:
  TestE2EHappyPath              — section 5
  TestNegativeScenarios         — section 6 (A..J, 10 scenarios)
  TestOtelEvidence              — section 7
  TestReplayDeterminism         — section 8
  TestL2CapableAgentMatrix      — section 4 + 5 matrix coverage
"""

from __future__ import annotations

import dataclasses
from typing import Any

import pytest

from agentic_core.L2_execution.observability.l2_resolution_spans import (
    clear_recorded_spans,
    recorded_spans,
)
from agentic_core.L2_execution.orchestration.l2_phase_pipeline import (
    ExecutorResult,
    HealerResult,
    L2PhasePipeline,
    PipelineConfig,
    ValidatorResult,
)
from agentic_core.L2_execution.types.l2_resolution_context import (
    L2ResolutionContext,
    RepairAuthorityClass,
    compute_resolution_digest,
)
from agentic_core.L2_execution.types.l2_v3_receipts import (
    AttemptReceipt,
    DeterminismBundle,
    HealOutcomeStamp,
    LineageRoot,
    PrepReceipt,
    ResultClass,
    TerminalStamp,
    ValidationOutcome,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _build_context(
    *,
    agent_id: str = "agent-A",
    agent_version: str = "1.0.0",
    validator_id: str = "validator-A",
    validator_version: str = "1.0.0",
    policy_hash: str = "p" * 64,
    blueprint_hash: str = "b" * 64,
    capability_scope_hash: str = "c" * 64,
    sandbox_envelope_hash: str = "s" * 64,
    replay_key: str = "r" * 64,
    snapshot_manifest_hash: str = "m" * 64,
    provider_lane: str = "deterministic",
    repair_authority_class: RepairAuthorityClass = RepairAuthorityClass.LOCAL_SAFE_ONLY,
    allowed_repair_types: tuple[str, ...] = ("retry_same_call",),
    trace_id: str = "trace-1",
) -> L2ResolutionContext:
    return L2ResolutionContext(
        request_id="req-1",
        run_id="run-1",
        trace_id=trace_id,
        route_id="route-1",
        step_id="step-1",
        agent_id=agent_id,
        agent_type="executor",
        agent_version=agent_version,
        agent_profile_hash="ah" + "0" * 62,
        validator_id=validator_id,
        validator_version=validator_version,
        capability_token="cap-1",
        capability_scope_hash=capability_scope_hash,
        sandbox_envelope_hash=sandbox_envelope_hash,
        policy_hash=policy_hash,
        blueprint_hash=blueprint_hash,
        replay_key=replay_key,
        snapshot_manifest_hash=snapshot_manifest_hash,
        tool_registry_digest="td" + "0" * 62,
        model_registry_digest="md" + "0" * 62,
        provider_lane=provider_lane,
        repair_authority_class=repair_authority_class,
        allowed_repair_types=allowed_repair_types,
        max_repair_count=3,
        frozen_execution_context_hash="fe" + "0" * 62,
        resolver_digest="rs" + "0" * 62,
    )


def _determinism() -> DeterminismBundle:
    return DeterminismBundle(
        blueprint_hash="b" * 64,
        policy_hash="p" * 64,
        prompt_hash="ph" + "0" * 62,
        input_hash="ih" + "0" * 62,
        replay_key="r" * 64,
        attempt_seed="seed-1",
    )


def _lineage() -> LineageRoot:
    return LineageRoot(
        parent_route_id="route-parent",
        parent_plan_id="plan-1",
        parent_step_id=None,
        ancestry_chain=("root",),
    )


# Counters across each test that decorate validator/executor/healer
# adapter funcs so we can assert "exactly N calls".
class _Counters:
    def __init__(self) -> None:
        self.executor_calls = 0
        self.healer_calls = 0


def _make_validator(
    ctx: L2ResolutionContext,
) -> Any:
    """Return a real validator_fn that ALWAYS computes its own digest."""

    def _validator(prep: PrepReceipt) -> ValidatorResult:
        digest = compute_resolution_digest(ctx)
        return ValidatorResult(
            outcome=ValidationOutcome.PASS,
            rules_passed=("e2.signature", "e2.capability_scope"),
            classified_side_effect="read_only",
            validator_resolution_context=ctx,
            validator_resolution_digest=digest,
        )

    return _validator


def _make_executor(
    counters: _Counters,
    *,
    fail_then_succeed: bool = True,
) -> Any:
    """First attempt returns SOFT_REPAIRABLE, second returns SUCCESS.

    When fail_then_succeed=False, every attempt SUCCEEDs (no heal needed).
    """

    def _executor(
        prep: PrepReceipt,
        validation: Any,
        attempt_count: int,
    ) -> ExecutorResult:
        counters.executor_calls += 1
        if fail_then_succeed and attempt_count == 1:
            return ExecutorResult(
                result_class=ResultClass.SOFT_REPAIRABLE,
                trace_id="trace-exec-1",
                error_summary="schema_parse_error",
            )
        return ExecutorResult(
            result_class=ResultClass.SUCCESS,
            trace_id="trace-exec-2",
            output_digest="ok-digest",
        )

    return _executor


def _make_healer(
    counters: _Counters,
    ctx: L2ResolutionContext,
    *,
    override_ctx: L2ResolutionContext | None = None,
    forge_digest: str | None = None,
    omit_resolution: bool = False,
) -> Any:
    """Healer that returns its own resolution context + digest.

    `override_ctx`: pretend to resolve a DIFFERENT context (negative tests).
    `forge_digest`: force a digest that doesn't match the override_ctx
                    (defense-in-depth test).
    `omit_resolution`: simulate a legacy healer that returns no v5 fields.
    """

    def _healer(attempt: AttemptReceipt) -> HealerResult:
        counters.healer_calls += 1
        if omit_resolution:
            return HealerResult(
                outcome=HealOutcomeStamp.PASS,
                reason_code="json_repair",
                delta_summary="repaired schema",
            )
        used_ctx = override_ctx if override_ctx is not None else ctx
        digest = forge_digest if forge_digest is not None else compute_resolution_digest(used_ctx)
        return HealerResult(
            outcome=HealOutcomeStamp.PASS,
            reason_code="json_repair",
            delta_summary="repaired schema",
            heal_resolution_context=used_ctx,
            heal_resolution_digest=digest,
        )

    return _healer


@pytest.fixture(autouse=True)
def _clear_spans() -> None:
    """Every test starts with a clean OTEL recorder."""
    clear_recorded_spans()


def _run_pipeline(
    validator: Any,
    executor: Any,
    healer: Any,
    *,
    enforce: bool = True,
    max_repairs: int = 3,
) -> Any:
    pipe = L2PhasePipeline(
        validator_fn=validator,
        executor_fn=executor,
        healer_fn=healer,
        config=PipelineConfig(
            max_attempts=2,
            max_repairs=max_repairs,
            enforce_resolution_consistency=enforce,
        ),
    )
    return pipe.run(
        route_id="route-1",
        step_id="step-1",
        determinism=_determinism(),
        lineage=_lineage(),
    )


# ---------------------------------------------------------------------------
# Section 5 — End-to-end happy path
# ---------------------------------------------------------------------------


class TestE2EHappyPath:
    def test_matching_resolution_executes_one_heal_and_seals_success(self) -> None:
        ctx = _build_context()
        counters = _Counters()
        result = _run_pipeline(
            _make_validator(ctx),
            _make_executor(counters, fail_then_succeed=True),
            _make_healer(counters, ctx),
        )

        # E4 ran exactly once.
        assert len(result.heals) == 1
        assert result.heals[0].repair_count == 1
        # E3 ran twice (fail, then SUCCESS after heal).
        assert len(result.attempts) == 2
        # Same blueprint/policy/replay across heal + prep.
        for r in (*result.attempts, *result.heals):
            assert r.determinism.blueprint_hash == "b" * 64
            assert r.determinism.policy_hash == "p" * 64
            assert r.determinism.replay_key == "r" * 64
        # Sealed terminal.
        assert result.terminal_stamp is TerminalStamp.SUCCESS
        assert result.dispatch is not None
        assert result.dispatch.has_commit_payload is False  # invariant
        assert result.dispatch.user_visible_safe is True


# ---------------------------------------------------------------------------
# Section 6 — Negative tests (A..J)
# ---------------------------------------------------------------------------


class TestNegativeScenarios:
    @pytest.mark.parametrize(
        ("scenario", "override_kwargs", "expected_field"),
        [
            ("A_validator_agent_mismatch", {"agent_id": "agent-B"}, "agent_id"),
            ("B_policy_hash_mismatch", {"policy_hash": "x" * 64}, "policy_hash"),
            ("C_blueprint_hash_mismatch", {"blueprint_hash": "x" * 64}, "blueprint_hash"),
            (
                "D_sandbox_widening",
                {"sandbox_envelope_hash": "x" * 64},
                "sandbox_envelope_hash",
            ),
            (
                "E_capability_widening",
                {"capability_scope_hash": "x" * 64},
                "capability_scope_hash",
            ),
            ("F_replay_snapshot_mismatch", {"replay_key": "x" * 64}, "replay_key"),
        ],
    )
    def test_resolution_field_mismatch_fails_closed(
        self,
        scenario: str,
        override_kwargs: dict[str, Any],
        expected_field: str,
    ) -> None:
        validator_ctx = _build_context()
        heal_ctx = _build_context(**override_kwargs)
        counters = _Counters()
        result = _run_pipeline(
            _make_validator(validator_ctx),
            _make_executor(counters, fail_then_succeed=True),
            _make_healer(counters, heal_ctx, override_ctx=heal_ctx),
        )

        # Heal MUST NOT have produced a HealReceipt.
        assert result.heals == ()
        # Terminal class is the new mismatch terminal.
        assert (
            result.terminal_stamp
            is TerminalStamp.VALIDATOR_AGENT_RESOLUTION_MISMATCH
        ), f"scenario {scenario}: unexpected terminal {result.terminal_stamp}"
        # Sealed dispatch is present, no commit, not user-visible-safe.
        assert result.dispatch is not None
        assert result.dispatch.has_commit_payload is False
        assert result.dispatch.user_visible_safe is False
        assert result.dispatch.downstream_recommendation == "deny"
        # Decisive reason names the mismatched field.
        assert expected_field in result.dispatch.decisive_reason
        # No proposed_state_diff (last attempt's must be empty/inert).
        for a in result.attempts:
            assert a.proposed_state_diff == {}

    def test_G_default_agent_fallback_fails_closed(self) -> None:
        validator_ctx = _build_context()
        heal_ctx = _build_context(agent_id="default")  # sentinel
        counters = _Counters()
        result = _run_pipeline(
            _make_validator(validator_ctx),
            _make_executor(counters, fail_then_succeed=True),
            _make_healer(counters, heal_ctx, override_ctx=heal_ctx),
        )
        assert result.heals == ()
        assert (
            result.terminal_stamp
            is TerminalStamp.VALIDATOR_AGENT_RESOLUTION_MISMATCH
        )

    def test_H_direct_heal_without_validation_attempt_fails_closed(self) -> None:
        """Healer that returns no v5 fields under enforcement is treated as
        the 'heal-without-validation' equivalent."""
        ctx = _build_context()
        counters = _Counters()
        result = _run_pipeline(
            _make_validator(ctx),
            _make_executor(counters, fail_then_succeed=True),
            _make_healer(counters, ctx, omit_resolution=True),
        )
        # Healer DID run (we let it run for legacy compat) but the gate
        # caught the missing digest and sealed REJECTED.
        assert result.heals == ()
        assert (
            result.terminal_stamp
            is TerminalStamp.VALIDATOR_AGENT_RESOLUTION_MISMATCH
        )
        assert "heal_resolution_digest" in result.dispatch.decisive_reason

    def test_I_direct_l4_write_during_heal_blocked_by_invariant(self) -> None:
        """DispatchReceipt.has_commit_payload=False is structurally enforced.

        The pipeline never sets it True. Confirm even on the mismatch path
        the seal carries no commit payload — INV-RC-5 + L2 invariant [7].
        """
        validator_ctx = _build_context()
        heal_ctx = _build_context(agent_id="agent-B")
        counters = _Counters()
        result = _run_pipeline(
            _make_validator(validator_ctx),
            _make_executor(counters, fail_then_succeed=True),
            _make_healer(counters, heal_ctx, override_ctx=heal_ctx),
        )
        assert result.dispatch is not None
        assert result.dispatch.has_commit_payload is False
        # commit_requested is False because executor never proposed a diff.
        assert result.dispatch.commit_requested is False

    def test_J_inconsistent_agent_specific_behavior_uniform_under_invariant(self) -> None:
        """Same repair class across multiple agents must produce uniform
        terminal classification when validator/heal disagree."""
        agents = ["agent-A", "agent-B", "agent-C", "agent-D"]
        terminals: list[TerminalStamp] = []
        for agent in agents:
            validator_ctx = _build_context(agent_id=agent)
            heal_ctx = _build_context(agent_id=agent + "-MISMATCH")
            counters = _Counters()
            result = _run_pipeline(
                _make_validator(validator_ctx),
                _make_executor(counters, fail_then_succeed=True),
                _make_healer(counters, heal_ctx, override_ctx=heal_ctx),
            )
            terminals.append(result.terminal_stamp)
        # All four agents fail closed identically.
        assert all(
            t is TerminalStamp.VALIDATOR_AGENT_RESOLUTION_MISMATCH for t in terminals
        )


# ---------------------------------------------------------------------------
# Section 7 — OTEL evidence
# ---------------------------------------------------------------------------


class TestOtelEvidence:
    def test_happy_path_emits_validate_heal_compare_executed_spans(self) -> None:
        ctx = _build_context()
        counters = _Counters()
        _run_pipeline(
            _make_validator(ctx),
            _make_executor(counters, fail_then_succeed=True),
            _make_healer(counters, ctx),
        )
        names = [s.name for s in recorded_spans()]
        assert "l2.resolution.validate" in names
        assert "l2.resolution.heal" in names
        # compare appears once with resolution_match=True.
        compare_spans = [s for s in recorded_spans() if s.name == "l2.resolution.compare"]
        assert len(compare_spans) == 1
        assert compare_spans[0].attributes["resolution_match"] is True
        # No blocked span on happy path.
        assert "l2.heal.blocked" not in names

    def test_mismatch_emits_compare_false_then_blocked_span(self) -> None:
        validator_ctx = _build_context()
        heal_ctx = _build_context(agent_id="agent-B")
        counters = _Counters()
        _run_pipeline(
            _make_validator(validator_ctx),
            _make_executor(counters, fail_then_succeed=True),
            _make_healer(counters, heal_ctx, override_ctx=heal_ctx),
        )
        names = [s.name for s in recorded_spans()]
        assert "l2.resolution.validate" in names
        assert "l2.resolution.heal" in names
        compare_spans = [s for s in recorded_spans() if s.name == "l2.resolution.compare"]
        assert len(compare_spans) == 1
        assert compare_spans[0].attributes["resolution_match"] is False
        assert compare_spans[0].attributes["first_mismatched_field"] == "agent_id"
        # Blocked span carries decisive_rule_id + sealed_artifact_id.
        blocked_spans = [s for s in recorded_spans() if s.name == "l2.heal.blocked"]
        assert len(blocked_spans) == 1
        attrs = blocked_spans[0].attributes
        assert attrs["decisive_rule_id"] == "VALIDATOR_AGENT_RESOLUTION_MISMATCH"
        assert attrs["first_mismatched_field"] == "agent_id"
        assert attrs["sealed_artifact_id"].startswith("sealed-")
        assert attrs["terminal_class"] == "VALIDATOR_AGENT_RESOLUTION_MISMATCH"

    def test_validate_span_carries_required_attributes(self) -> None:
        ctx = _build_context()
        counters = _Counters()
        _run_pipeline(
            _make_validator(ctx),
            _make_executor(counters, fail_then_succeed=False),
            _make_healer(counters, ctx),
        )
        validate = next(
            s for s in recorded_spans() if s.name == "l2.resolution.validate"
        )
        required = {
            "request_id",
            "run_id",
            "route_id",
            "step_id",
            "trace_id",
            "agent_id",
            "agent_type",
            "agent_version",
            "validator_id",
            "validator_version",
            "policy_hash",
            "blueprint_hash",
            "replay_key",
            "capability_scope_hash",
            "sandbox_envelope_hash",
            "snapshot_manifest_hash",
            "provider_lane",
            "repair_authority_class",
            "validator_resolution_digest",
        }
        missing = required - validate.attributes.keys()
        assert missing == set(), f"missing attrs: {missing}"


# ---------------------------------------------------------------------------
# Section 8 — Replay determinism
# ---------------------------------------------------------------------------


class TestReplayDeterminism:
    def test_same_inputs_yield_same_digests_and_same_terminal(self) -> None:
        ctx = _build_context()
        # Run twice; capture digests + terminal_stamp.
        runs: list[Any] = []
        for _ in range(2):
            clear_recorded_spans()
            counters = _Counters()
            r = _run_pipeline(
                _make_validator(ctx),
                _make_executor(counters, fail_then_succeed=True),
                _make_healer(counters, ctx),
            )
            v_span = next(
                s for s in recorded_spans() if s.name == "l2.resolution.validate"
            )
            h_span = next(
                s for s in recorded_spans() if s.name == "l2.resolution.heal"
            )
            runs.append(
                {
                    "validator_digest": v_span.attributes["validator_resolution_digest"],
                    "heal_digest": h_span.attributes["heal_resolution_digest"],
                    "terminal": r.terminal_stamp,
                    "decisive": r.dispatch.decisive_reason if r.dispatch else "",
                    "blueprint_hash": r.prep.determinism.blueprint_hash,
                    "policy_hash": r.prep.determinism.policy_hash,
                    "replay_key": r.prep.determinism.replay_key,
                }
            )
        # Digests, terminal, and replay refs all stable across runs.
        assert runs[0]["validator_digest"] == runs[1]["validator_digest"]
        assert runs[0]["heal_digest"] == runs[1]["heal_digest"]
        assert runs[0]["validator_digest"] == runs[0]["heal_digest"]
        assert runs[0]["terminal"] is runs[1]["terminal"]
        assert runs[0]["decisive"] == runs[1]["decisive"]
        assert runs[0]["blueprint_hash"] == runs[1]["blueprint_hash"]
        assert runs[0]["policy_hash"] == runs[1]["policy_hash"]
        assert runs[0]["replay_key"] == runs[1]["replay_key"]


# ---------------------------------------------------------------------------
# Section 4 + 5 — L2-capable agent matrix
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class _AgentMatrixEntry:
    agent_id: str
    agent_type: str
    provider_lane: str
    repair_authority_class: RepairAuthorityClass


# Representative L2-capable agent identities covering each routing lane
# from agentic_core.L2_execution.healers.healing_router HealTier. If new
# lanes are added, this list MUST grow — fail-closed by design.
_L2_AGENT_MATRIX: tuple[_AgentMatrixEntry, ...] = (
    _AgentMatrixEntry("LocalDeterministicAgent-1", "deterministic", "deterministic", RepairAuthorityClass.LOCAL_SAFE_ONLY),
    _AgentMatrixEntry("QwenLocalAgent-1", "qwen_vllm", "qwen_local", RepairAuthorityClass.LOCAL_SAFE_ONLY),
    _AgentMatrixEntry("GeminiFlashAgent-1", "gemini_flash", "google", RepairAuthorityClass.LOCAL_SAFE_ONLY),
    _AgentMatrixEntry("GeminiProAgent-1", "gemini_pro", "google", RepairAuthorityClass.ESCALATE_REQUIRED),
    _AgentMatrixEntry("AnthropicSonnetAgent-1", "anthropic_sonnet", "anthropic", RepairAuthorityClass.LOCAL_SAFE_ONLY),
    _AgentMatrixEntry("HitlAgent-1", "human_review", "hitl", RepairAuthorityClass.ESCALATE_REQUIRED),
)


class TestL2CapableAgentMatrix:
    def test_matrix_is_non_empty(self) -> None:
        """Fail-closed if no L2-capable agent is registered."""
        assert len(_L2_AGENT_MATRIX) > 0, "no L2-capable agents in matrix"

    @pytest.mark.parametrize("entry", _L2_AGENT_MATRIX, ids=lambda e: e.agent_id)
    def test_each_agent_passes_with_matching_resolution(
        self, entry: _AgentMatrixEntry
    ) -> None:
        ctx = _build_context(
            agent_id=entry.agent_id,
            provider_lane=entry.provider_lane,
            repair_authority_class=entry.repair_authority_class,
        )
        counters = _Counters()
        result = _run_pipeline(
            _make_validator(ctx),
            _make_executor(counters, fail_then_succeed=True),
            _make_healer(counters, ctx),
        )
        assert result.terminal_stamp is TerminalStamp.SUCCESS
        assert len(result.heals) == 1

    @pytest.mark.parametrize("entry", _L2_AGENT_MATRIX, ids=lambda e: e.agent_id)
    def test_each_agent_fails_closed_on_mismatch(
        self, entry: _AgentMatrixEntry
    ) -> None:
        validator_ctx = _build_context(
            agent_id=entry.agent_id,
            provider_lane=entry.provider_lane,
            repair_authority_class=entry.repair_authority_class,
        )
        heal_ctx = _build_context(
            agent_id=entry.agent_id + "-MISMATCH",
            provider_lane=entry.provider_lane,
            repair_authority_class=entry.repair_authority_class,
        )
        counters = _Counters()
        result = _run_pipeline(
            _make_validator(validator_ctx),
            _make_executor(counters, fail_then_succeed=True),
            _make_healer(counters, heal_ctx, override_ctx=heal_ctx),
        )
        assert (
            result.terminal_stamp
            is TerminalStamp.VALIDATOR_AGENT_RESOLUTION_MISMATCH
        )
        assert result.heals == ()


# ---------------------------------------------------------------------------
# Backward-compat: legacy callers (enforcement off) unaffected
# ---------------------------------------------------------------------------


class TestLegacyBackwardCompat:
    def test_legacy_validator_and_healer_no_v5_fields_off_path(self) -> None:
        """When enforce_resolution_consistency=False and validators/healers
        don't surface v5 fields, pipeline behaves exactly like v4."""

        def legacy_validator(prep: PrepReceipt) -> ValidatorResult:
            return ValidatorResult(outcome=ValidationOutcome.PASS)

        def legacy_executor(
            prep: PrepReceipt, validation: Any, attempt_count: int
        ) -> ExecutorResult:
            if attempt_count == 1:
                return ExecutorResult(
                    result_class=ResultClass.SOFT_REPAIRABLE,
                    trace_id="t",
                    error_summary="x",
                )
            return ExecutorResult(
                result_class=ResultClass.SUCCESS,
                trace_id="t",
                output_digest="ok",
            )

        def legacy_healer(attempt: AttemptReceipt) -> HealerResult:
            return HealerResult(outcome=HealOutcomeStamp.PASS, reason_code="ok")

        result = _run_pipeline(
            legacy_validator, legacy_executor, legacy_healer, enforce=False
        )
        assert result.terminal_stamp is TerminalStamp.SUCCESS
        # No resolution spans recorded when enforcement is off.
        names = [s.name for s in recorded_spans()]
        assert "l2.resolution.validate" not in names
        assert "l2.resolution.heal" not in names
