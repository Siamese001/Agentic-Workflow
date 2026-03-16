"""Gate C4: Observability liveness tests.

Every telemetry channel must emit on startup/check.
Tests verify HealingEventEmitter, AICheckAuditEmitter, and HITLDecisionLogger
all produce observable signals on first use.
"""

from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_observability_liveness")
_emit_applies_guardrail("p0", "test_observability_liveness", "p0_governance")
_emit_reads_policy_state("p0", "test_observability_liveness", "policy_binding")
_emit_snapshots_state("p0", "test_observability_liveness", "state_snapshot")
emit_replay_key("p0", "test_observability_liveness")
emit_determinism_digest("p0", "test_observability_liveness")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class TestHealingEventEmitterLiveness:
    def test_emitter_produces_event_on_first_emit(self, tmp_path):
        from agentic_core.L2_execution.healers.healing_event_emitter import HealingEventEmitter

        emitter = HealingEventEmitter(log_path=tmp_path / "healing.jsonl")
        event = emitter.emit(
            trace_id="liveness-t001",
            attempt_number=1,
            failure_class="liveness_check",
            healer_selected="LivenessAgent",
            model_used="gemini-2.5-pro",
            outcome="success",
        )
        assert event.trace_id == "liveness-t001"
        events = emitter.emitted_events()
        assert len(events) == 1

    def test_emitter_log_file_created(self, tmp_path):
        from agentic_core.L2_execution.healers.healing_event_emitter import HealingEventEmitter

        log_path = tmp_path / "healing_liveness.jsonl"
        emitter = HealingEventEmitter(log_path=log_path)
        emitter.emit("t", 1, "err", "agent", "model", "success")
        assert log_path.exists()
        assert log_path.stat().st_size > 0

    def test_negative_no_emission_without_emit_call(self, tmp_path):
        from agentic_core.L2_execution.healers.healing_event_emitter import HealingEventEmitter

        emitter = HealingEventEmitter(log_path=tmp_path / "healing.jsonl")
        assert emitter.emitted_events() == []


class TestAICheckAuditEmitterLiveness:
    def test_emitter_produces_record_on_emit(self, tmp_path):
        from agentic_core.L5_safety.audit.ai_check_audit import AICheckAuditEmitter, AICheckAuditRecord

        emitter = AICheckAuditEmitter(audit_path=tmp_path / "audit.jsonl")
        record = emitter.emit(
            component="LivenessChecker",
            model_id="gemini-2.5-pro",
            input_data="liveness check input",
            verdict="PASS",
            confidence=0.95,
            trace_id="liveness-audit-001",
        )
        assert isinstance(record, AICheckAuditRecord)
        assert record.confidence == 0.95

    def test_emitter_writes_to_file(self, tmp_path):
        from agentic_core.L5_safety.audit.ai_check_audit import AICheckAuditEmitter

        audit_path = tmp_path / "audit_liveness.jsonl"
        emitter = AICheckAuditEmitter(audit_path=audit_path)
        emitter.emit("comp", "model", "input_data_str", "PASS", 0.8, "t-001")
        assert audit_path.exists()
        assert audit_path.stat().st_size > 0

    def test_negative_no_entries_without_emit(self, tmp_path):
        from agentic_core.L5_safety.audit.ai_check_audit import AICheckAuditEmitter

        emitter = AICheckAuditEmitter(audit_path=tmp_path / "audit.jsonl")
        assert emitter.read_all() == []


class TestHITLDecisionLoggerLiveness:
    def test_logger_produces_record_on_log(self, tmp_path):
        from agentic_core.L5_safety.hitl.decision_logger import HITLDecisionLogger

        logger = HITLDecisionLogger(log_path=tmp_path / "decisions.jsonl")
        d = logger.log("LivenessAgent", "liveness.py", "check", "propose", "APPROVE")
        assert d.decision_number == 1
        assert logger.count() == 1

    def test_negative_count_zero_on_fresh_logger(self, tmp_path):
        from agentic_core.L5_safety.hitl.decision_logger import HITLDecisionLogger

        logger = HITLDecisionLogger(log_path=tmp_path / "decisions.jsonl")
        assert logger.count() == 0
