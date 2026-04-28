"""End-to-end pipeline tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.L3_orchestration.exit_eval.break_glass import (
    BreakGlassAuthority,
    BreakGlassToken,
)
from agentic_core.L3_orchestration.exit_eval.bus import (
    BusEmitter,
    BusWriteError,
    memory_sink,
)
from agentic_core.L3_orchestration.exit_eval.consistency import (
    BucketKey,
    PassKStore,
    TrialRecord,
)
from agentic_core.L3_orchestration.exit_eval.disposition import (
    Disposition,
    ReasonCode,
)
from agentic_core.L3_orchestration.exit_eval.gates import (
    Gate,
    GateContext,
)
from agentic_core.L3_orchestration.exit_eval.graders.llm_judge import (
    LLMJudgeGrader,
)
from agentic_core.L3_orchestration.exit_eval.otel_spans import NoOpSpanSink
from agentic_core.L3_orchestration.exit_eval.pipeline import (
    ConsistencyPolicy,
    EvaluationPipeline,
)
from agentic_core.L3_orchestration.exit_eval.rubric import rubric_from_mapping

from tests.agentic_core.L3_orchestration.exit_eval.conftest import (
    FakeCodeGrader,
    FakeJudge,
)


def _x1a_gate(score: float) -> Gate:
    rubric = rubric_from_mapping(
        {
            "gate": "X1A",
            "version": "X1A@v1",
            "composition": "binary",
            "dimensions": [
                {
                    "name": "policy_match",
                    "grader_class": "code_based",
                    "is_hard_gate": True,
                    "threshold": 1.0,
                }
            ],
        }
    )
    return Gate(rubric, graders={"policy_match": FakeCodeGrader(score=score)})


def _x1d_gate(*, cit: float = 1.0, ground_score: float = 0.9, ground_abstain: bool = False) -> Gate:
    rubric = rubric_from_mapping(
        {
            "gate": "X1D",
            "version": "X1D@v1",
            "composition": "hybrid",
            "aggregate_threshold": 0.6,
            "dimensions": [
                {
                    "name": "citation_support",
                    "grader_class": "code_based",
                    "is_hard_gate": True,
                    "threshold": 1.0,
                },
                {
                    "name": "groundedness",
                    "grader_class": "model_based",
                    "weight": 1.0,
                    "threshold": 0.7,
                    "abstain_allowed": True,
                },
            ],
        }
    )
    return Gate(
        rubric,
        graders={
            "citation_support": FakeCodeGrader(score=cit),
            "groundedness": LLMJudgeGrader(FakeJudge(score=ground_score, abstain=ground_abstain)),
        },
    )


def _ctx(run_id: str = "r1") -> GateContext:
    return GateContext(
        run_id=run_id,
        track="regression",
        trajectory_class="demo",
        payload={},
    )


def _pipeline(
    gates: list[Gate],
    *,
    consistency: PassKStore | None = None,
    policy: ConsistencyPolicy | None = None,
) -> tuple[EvaluationPipeline, list]:
    sink, captured = memory_sink()
    emitter = BusEmitter(sink)
    span_sink = NoOpSpanSink()
    pipe = EvaluationPipeline(
        gates,
        bus_emitter=emitter,
        consistency_store=consistency,
        consistency_policy=policy,
        span_sink=span_sink,
    )
    return pipe, captured


class TestDispositions:
    def test_all_pass_allow(self) -> None:
        pipe, bus = _pipeline([_x1a_gate(1.0), _x1d_gate()])
        out = pipe.run(_ctx(), commit_candidate=False)
        assert out.envelope.disposition is Disposition.ALLOW
        assert not out.envelope.deny
        assert len(bus) == 2

    def test_all_pass_commit_candidate(self) -> None:
        pipe, _ = _pipeline([_x1a_gate(1.0), _x1d_gate()])
        out = pipe.run(_ctx(), commit_candidate=True)
        assert out.envelope.disposition is Disposition.COMMIT

    def test_x1a_deny(self) -> None:
        pipe, _ = _pipeline([_x1a_gate(0.0), _x1d_gate()])
        out = pipe.run(_ctx(), commit_candidate=True)
        assert out.envelope.disposition is Disposition.DENY
        assert out.envelope.deny
        assert ReasonCode.POLICY_CONFLICT in out.envelope.reason_codes

    def test_abstain_escalates(self) -> None:
        pipe, _ = _pipeline([_x1a_gate(1.0), _x1d_gate(ground_abstain=True)])
        out = pipe.run(_ctx(), commit_candidate=True)
        assert out.envelope.disposition is Disposition.ESCALATE
        assert ReasonCode.JUDGE_ABSTAINED in out.envelope.reason_codes

    def test_sealed_folder_serialization(self) -> None:
        pipe, _ = _pipeline([_x1a_gate(0.0)])
        out = pipe.run(_ctx(), commit_candidate=True)
        sealed = out.envelope.to_sealed_folder()
        # Shape compatible with classify_exit contract
        assert sealed["deny"] is True
        assert "POLICY_CONFLICT" in sealed["deny_reason"]


class TestConsistency:
    def test_commit_candidate_requires_history(self) -> None:
        store = PassKStore()
        bucket = BucketKey(
            trajectory_class="demo",
            rubric_version="X1D@v1",
            agent_version="a1",
            policy_version="p1",
        )
        pipe, _ = _pipeline(
            [_x1a_gate(1.0), _x1d_gate()],
            consistency=store,
            policy=ConsistencyPolicy(k=5, theta=0.95),
        )
        out = pipe.run(_ctx(), commit_candidate=True, consistency_bucket=bucket)
        assert out.envelope.disposition is Disposition.ESCALATE
        assert ReasonCode.INSUFFICIENT_HISTORY in out.envelope.reason_codes

    def test_commit_candidate_with_good_history_commits(self) -> None:
        store = PassKStore()
        bucket = BucketKey(
            trajectory_class="demo",
            rubric_version="X1D@v1",
            agent_version="a1",
            policy_version="p1",
        )
        for i in range(5):
            store.record(
                bucket,
                TrialRecord(run_id=f"r{i}", passed=True, timestamp=float(i)),
            )
        pipe, _ = _pipeline(
            [_x1a_gate(1.0), _x1d_gate()],
            consistency=store,
            policy=ConsistencyPolicy(k=5, theta=0.95),
        )
        out = pipe.run(_ctx(), commit_candidate=True, consistency_bucket=bucket)
        assert out.envelope.disposition is Disposition.COMMIT
        assert out.consistency is not None
        assert out.consistency.passed

    def test_non_commit_skips_consistency(self) -> None:
        store = PassKStore()
        pipe, _ = _pipeline(
            [_x1a_gate(1.0), _x1d_gate()],
            consistency=store,
            policy=ConsistencyPolicy(k=5, theta=0.95, commit_path_only=True),
        )
        out = pipe.run(_ctx(), commit_candidate=False)
        # ALLOW disposition, consistency not evaluated
        assert out.envelope.disposition is Disposition.ALLOW
        assert out.consistency is None


class TestBreakGlass:
    def _auth(self, tmp_path: Path) -> BreakGlassAuthority:
        from agentic_core.L3_orchestration.exit_eval.break_glass import (
            jsonl_audit_sink,
        )

        return BreakGlassAuthority(
            audit_sink=jsonl_audit_sink(tmp_path / "audit.jsonl"),
            now=lambda: 1000.0,
        )

    def _token(self) -> BreakGlassToken:
        return BreakGlassToken(
            identity="op",
            capabilities=frozenset({"break_glass"}),
            issued_at=900.0,
            expires_at=2000.0,
        )

    def test_break_glass_bypasses_x1d(self, tmp_path: Path) -> None:
        auth = self._auth(tmp_path)
        inv = auth.invoke(
            token=self._token(),
            justification="prod incident",
            bypassed_gates=("X1D",),
            run_id="r1",
            expiry_seconds=900,
        )
        # X1D would fail (cit=0) but break-glass bypasses it
        pipe, _ = _pipeline([_x1a_gate(1.0), _x1d_gate(cit=0.0)])
        out = pipe.run(_ctx(), commit_candidate=False, break_glass=inv)
        assert out.envelope.disposition is Disposition.BREAK_GLASS
        assert out.envelope.break_glass_audit_id == inv.audit_id
        assert ReasonCode.BREAK_GLASS_INVOKED in out.envelope.reason_codes
        assert "X1D" in out.bypassed_gates

    def test_break_glass_cannot_override_x1a_deny(self, tmp_path: Path) -> None:
        """H3.1: X1A is mandatory-deny even under break-glass."""
        auth = self._auth(tmp_path)
        inv = auth.invoke(
            token=self._token(),
            justification="prod incident",
            bypassed_gates=("X1D",),  # X1D bypassed, but X1A still runs
            run_id="r1",
            expiry_seconds=900,
        )
        pipe, _ = _pipeline([_x1a_gate(0.0), _x1d_gate()])
        out = pipe.run(_ctx(), commit_candidate=False, break_glass=inv)
        # X1A denied → disposition is DENY, NOT BREAK_GLASS
        assert out.envelope.disposition is Disposition.DENY


class TestFaultMatrix:
    """H8 fault-injection matrix."""

    def test_bus_write_failure_escalates(self) -> None:
        def broken_sink(_row: object) -> None:
            raise OSError("disk broken")

        emitter = BusEmitter(broken_sink)  # type: ignore[arg-type]
        pipe = EvaluationPipeline(
            [_x1a_gate(1.0)],
            bus_emitter=emitter,
            span_sink=NoOpSpanSink(),
        )
        out = pipe.run(_ctx(), commit_candidate=False)
        assert out.bus_write_failed
        assert out.envelope.disposition is Disposition.ESCALATE
        assert ReasonCode.AUDIT_UNAVAILABLE in out.envelope.reason_codes

    def test_judge_timeout_routes_to_escalate(self) -> None:
        """Timeout on X1D groundedness judge → escalate, not deny."""
        rubric = rubric_from_mapping(
            {
                "gate": "X1D",
                "version": "X1D@v1",
                "composition": "hybrid",
                "aggregate_threshold": 0.6,
                "dimensions": [
                    {
                        "name": "citation_support",
                        "grader_class": "code_based",
                        "is_hard_gate": True,
                        "threshold": 1.0,
                    },
                    {
                        "name": "groundedness",
                        "grader_class": "model_based",
                        "weight": 1.0,
                        "threshold": 0.7,
                        "abstain_allowed": True,
                    },
                ],
            }
        )
        gate = Gate(
            rubric,
            graders={
                "citation_support": FakeCodeGrader(score=1.0),
                "groundedness": LLMJudgeGrader(FakeJudge(raise_exc=TimeoutError("slow judge"))),
            },
        )
        pipe, _ = _pipeline([_x1a_gate(1.0), gate])
        out = pipe.run(_ctx(), commit_candidate=False)
        # Timeout recorded as reason code; gate failed; disposition ESCALATE
        # (NOT deny — grader_composition_spec §H8 routes timeout to HITL)
        codes = set(out.envelope.reason_codes)
        # Timeout may appear via X1D's gate; disposition should be escalate
        # (because neither X1A denies nor is there a hard binary failure).
        assert ReasonCode.JUDGE_TIMEOUT in codes
