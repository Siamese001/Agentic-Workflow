"""Addendum 1.3: Healing Visibility Enforcement tests."""

from __future__ import annotations

from agentic_core.L2_execution.healers.healing_event_emitter import (
    HealingAttemptEvent,
    HealingEventEmitter,
)


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
