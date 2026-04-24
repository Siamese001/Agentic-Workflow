"""Unit tests for composite modules: exit_decision, escalation_packet, kill_switch, trace_grader."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from agentic_core.L5_safety.eval_spine import (
    escalation_packet,
    exit_decision,
    kill_switch,
    trace_grader,
)


def _decision_fixture(**overrides: object) -> exit_decision.ExitDecision:
    defaults: dict[str, object] = {
        "request_id": "req-1",
        "trace_id": "tr-1",
        "emitted_at_utc": "2026-04-23T00:00:00Z",
        "disposition": "allow_finish",
        "reason_code": "grader.ok",
        "final_response": exit_decision.FinalResponseMetrics(),
        "trajectory": exit_decision.TrajectoryMetrics(
            failure=False, latency_ms=10, tool_call_count=1
        ),
        "safety": exit_decision.SafetyFlags(),
        "budget": exit_decision.BudgetReport(budget_fit=True),
        "quality": exit_decision.QualityVerdict(verdict="pass"),
        "output_contract": exit_decision.OutputContractReport(
            required_form_satisfied=True
        ),
        "policy_snapshot": "sha-abcd",
    }
    defaults.update(overrides)
    # Named-argument construction keeps mypy happy; the dataclass fields match.
    return exit_decision.ExitDecision(  # type: ignore[arg-type]
        **defaults
    )


class TestExitDecision:
    def test_to_dict_schema_valid(self):
        decision = _decision_fixture()
        payload = decision.to_dict()
        errors = exit_decision.validate_dict(payload)
        assert errors == [], errors

    def test_minimal_required_keys_present(self):
        decision = _decision_fixture()
        payload = decision.to_dict()
        for key in (
            "schema_version",
            "request_id",
            "trace_id",
            "disposition",
            "reason_code",
            "final_response",
            "trajectory",
            "safety",
            "budget",
            "quality",
            "output_contract",
        ):
            assert key in payload

    def test_to_json_roundtrip(self):
        decision = _decision_fixture()
        text = decision.to_json()
        assert '"disposition":"allow_finish"' in text.replace(" ", "")


class TestEscalationPacket:
    def test_from_exit_decision(self):
        decision = _decision_fixture(
            safety=exit_decision.SafetyFlags(
                policy_violation=True, severity_band="high"
            )
        )
        packet = escalation_packet.from_exit_decision(
            decision,
            hitl_class="safety",
            reason_detail="pii leaked",
            evidence_refs=(
                escalation_packet.EvidenceRef(kind="trace_span", ref="sp-1"),
            ),
            options_ledger=(
                escalation_packet.OptionLedgerEntry(
                    label="block",
                    description="block output",
                    recommendation="recommended",
                    confidence_0_1=0.9,
                ),
            ),
            approver_pool="safety_officer",
            fallback_directive="deny",
            deadline_seconds=300,
        )
        payload = packet.to_dict()
        errors = escalation_packet.validate_dict(payload)
        assert errors == [], errors
        assert payload["hitl_class"] == "safety"

    def test_rejects_unknown_hitl_class(self):
        decision = _decision_fixture()
        with pytest.raises(ValueError):
            escalation_packet.from_exit_decision(
                decision,
                hitl_class="not_a_class",
                reason_detail="x",
                evidence_refs=(
                    escalation_packet.EvidenceRef(kind="trace_span", ref="sp"),
                ),
                options_ledger=(
                    escalation_packet.OptionLedgerEntry(
                        label="x",
                        description="y",
                        recommendation="recommended",
                        confidence_0_1=0.5,
                    ),
                ),
                approver_pool="pool",
                fallback_directive="hold",
                deadline_seconds=60,
            )

    def test_requires_policy_snapshot(self):
        decision = _decision_fixture(policy_snapshot=None)
        with pytest.raises(ValueError):
            escalation_packet.from_exit_decision(
                decision,
                hitl_class="safety",
                reason_detail="x",
                evidence_refs=(
                    escalation_packet.EvidenceRef(kind="trace_span", ref="sp"),
                ),
                options_ledger=(
                    escalation_packet.OptionLedgerEntry(
                        label="x",
                        description="y",
                        recommendation="recommended",
                        confidence_0_1=0.5,
                    ),
                ),
                approver_pool="pool",
                fallback_directive="hold",
                deadline_seconds=60,
            )


class TestKillSwitch:
    def test_activate_release_empty_otherwise(self):
        sink_rows: list[dict] = []
        store = kill_switch.KillSwitchStore(audit_sink=sink_rows.append)
        entry = store.activate(scope="tenant:acme", reason="abuse", operator="ops")
        assert store.active_activations() == (entry,)
        assert sink_rows[-1]["event"] == "activate"
        released = store.release(entry.activation_id)
        assert released is not None
        assert store.active_activations() == ()
        assert sink_rows[-1]["event"] == "release"

    def test_hit_tenant_scope(self):
        sink_rows: list[dict] = []
        store = kill_switch.KillSwitchStore(audit_sink=sink_rows.append)
        store.activate(scope="tenant:acme", reason="x", operator="ops")
        hit = store.hit({"tenant": "acme"}, request_id="r", trace_id="t")
        assert hit.hit is True
        assert hit.scope == "tenant:acme"
        assert sink_rows[-1]["event"] == "hit"
        miss = store.hit({"tenant": "other"})
        assert miss.hit is False

    def test_fleet_scope_matches_everything(self):
        store = kill_switch.KillSwitchStore()
        store.activate(
            scope="fleet", reason="x", operator="ops", on_hit="escalate"
        )
        assert store.hit({}).hit is True
        assert store.hit({"tenant": "anything"}).on_hit == "escalate"

    def test_agent_scope(self):
        store = kill_switch.KillSwitchStore()
        store.activate(scope="agent:ResumeAgent", reason="r", operator="ops")
        assert store.hit({"agent_class": "ResumeAgent"}).hit is True
        assert store.hit({"agent_class": "OtherAgent"}).hit is False

    def test_activate_rejects_empty_args(self):
        store = kill_switch.KillSwitchStore()
        with pytest.raises(ValueError):
            store.activate(scope="", reason="r", operator="ops")

    def test_audit_sink_failure_is_swallowed(self):
        def bad_sink(_payload):
            raise OSError("disk full")

        store = kill_switch.KillSwitchStore(audit_sink=bad_sink)
        # Should not raise.
        entry = store.activate(scope="fleet", reason="r", operator="ops")
        assert entry is not None


class TestTraceGrader:
    def test_default_grade_no_inputs_is_unknown(self):
        g = trace_grader.TraceGrader()
        out = g.grade(trace_grader.GraderInput())
        assert len(out.per_dim) == 5
        # With default inputs, many dims report Unknown; aggregate depends on
        # deterministic handoff/safety/trajectory scorers.
        assert out.aggregate_verdict in {"pass", "warn", "fail", "unknown"}

    def test_safety_hit_triggers_violated_flag(self):
        g = trace_grader.TraceGrader()
        out = g.grade(
            trace_grader.GraderInput(policy_hits=("pii_leak", "unauth_access"))
        )
        assert out.safety_violated is True

    def test_handoff_required_but_not_fired(self):
        g = trace_grader.TraceGrader()
        out = g.grade(
            trace_grader.GraderInput(
                handoff_required=True,
                handoff_fired=False,
            )
        )
        handoff = out.dim("handoff_fired_when_required")
        assert handoff is not None
        assert handoff.verdict == "fail"

    def test_forbidden_tool_usage_fails_selection(self):
        g = trace_grader.TraceGrader()
        out = g.grade(
            trace_grader.GraderInput(
                predicted_tool_calls=({"tool": "danger", "args_hash": "h"},),
                expected_tools=frozenset({"safe"}),
                forbidden_tools=frozenset({"danger"}),
            )
        )
        sel = out.dim("tool_selection")
        assert sel is not None
        assert sel.verdict == "fail"

    def test_override_scores(self):
        g = trace_grader.TraceGrader()
        out = g.grade(
            trace_grader.GraderInput(
                dim_overrides={"trajectory_shape": 4.5},
            )
        )
        tshape = out.dim("trajectory_shape")
        assert tshape is not None
        assert tshape.score == 4.5
        assert tshape.verdict == "pass"

    def test_instruction_violations_counted(self):
        g = trace_grader.TraceGrader()
        out = g.grade(
            trace_grader.GraderInput(
                instruction_violations=("a", "b", "c"),
            )
        )
        dim = out.dim("instruction_adherence")
        assert dim is not None
        assert dim.boolean_flag is True
        assert out.instruction_violated is True
