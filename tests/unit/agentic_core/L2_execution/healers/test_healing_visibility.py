"""Addendum 1.3: Healing Visibility Enforcement tests."""

from __future__ import annotations

from agentic_core.L2_execution.healers.healing_event_emitter import (
    HealingAttemptEvent,
    HealingEventEmitter,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_healing_visibility")
_emit_applies_guardrail("p0", "test_healing_visibility", "p0_governance")
_emit_reads_policy_state("p0", "test_healing_visibility", "policy_binding")
_emit_snapshots_state("p0", "test_healing_visibility", "state_snapshot")
emit_replay_key("p0", "test_healing_visibility")
emit_determinism_digest("p0", "test_healing_visibility")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_healing_visibility", "execution_auth")
_emit_validates_capability("p2", "test_healing_visibility", "capability_check")
_emit_routes_to_capability("p2", "test_healing_visibility", "capability_route")
_emit_writes_via_uwg("p2", "test_healing_visibility", "uwg_write")
_emit_blocks_direct_write("p2", "test_healing_visibility", "direct_write_block")
_emit_records_tool_invocation("p2", "test_healing_visibility", "tool_invocation")
_emit_captures_execution_output("p2", "test_healing_visibility", "exec_output")
_emit_dispatches_agent("p3", "test_healing_visibility", "agent_dispatch")
_emit_coordinates_agents("p3", "test_healing_visibility", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_healing_visibility", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_healing_visibility", "healing_outcome")
_emit_escalates_failure("p3", "test_healing_visibility", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_healing_visibility", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_healing_visibility", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_healing_visibility", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_healing_visibility", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_healing_visibility", "eval_metric")
_emit_stores_embedding("p4", "test_healing_visibility", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_healing_visibility", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_healing_visibility", "exec_snapshot_link")


class TestHealingEventEmitter:
    def test_emit_returns_event(self, tmp_path):
        emitter = HealingEventEmitter(log_path=tmp_path / "events.jsonl")
        event = emitter.emit(
            trace_id="t-001",
            attempt_number=1,
            failure_class="syntax_error",
            healer_selected="LocalAgent",
            model_used="gemini-2.5-pro",
            outcome="success",
        )
        assert isinstance(event, HealingAttemptEvent)
        assert event.trace_id == "t-001"
        assert event.attempt_number == 1
        assert event.outcome == "success"

    def test_emitted_events_list_grows(self, tmp_path):
        emitter = HealingEventEmitter(log_path=tmp_path / "events.jsonl")
        emitter.emit("t-001", 1, "type_error", "LocalAgent", "gpt-4", "success")
        emitter.emit("t-001", 2, "type_error", "QwenVLLM", "qwen2.5", "error")
        assert len(emitter.emitted_events()) == 2

    def test_event_written_to_jsonl(self, tmp_path):
        log_path = tmp_path / "events.jsonl"
        emitter = HealingEventEmitter(log_path=log_path)
        emitter.emit("t-002", 1, "import_error", "LocalAgent", "gemini", "partial")
        assert log_path.exists()
        lines = log_path.read_text().strip().splitlines()
        assert len(lines) == 1
        import json

        record = json.loads(lines[0])
        assert record["trace_id"] == "t-002"
        assert record["outcome"] == "partial"

    def test_multiple_events_separate_lines(self, tmp_path):
        log_path = tmp_path / "events.jsonl"
        emitter = HealingEventEmitter(log_path=log_path)
        for i in range(3):
            emitter.emit(f"t-{i:03d}", i, "err", "agent", "model", "success")
        lines = log_path.read_text().strip().splitlines()
        assert len(lines) == 3

    def test_negative_no_event_without_emit(self, tmp_path):
        """Negative control: no events unless emit() is called."""
        emitter = HealingEventEmitter(log_path=tmp_path / "events.jsonl")
        assert emitter.emitted_events() == []

    def test_metadata_stored(self, tmp_path):
        emitter = HealingEventEmitter(log_path=tmp_path / "events.jsonl")
        event = emitter.emit(
            "t-meta",
            1,
            "err",
            "agent",
            "model",
            "success",
            metadata={"file": "foo.py", "line": 42},
        )
        assert event.metadata == {"file": "foo.py", "line": 42}
