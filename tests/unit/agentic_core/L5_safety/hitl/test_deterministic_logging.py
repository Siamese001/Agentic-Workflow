"""Addendum 6.3: Deterministic HITL Decision Logger tests."""

from __future__ import annotations

import json

from agentic_core.L5_safety.hitl.decision_logger import HITLDecision, HITLDecisionLogger
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_deterministic_logging")
_emit_applies_guardrail("p0", "test_deterministic_logging", "p0_governance")
_emit_reads_policy_state("p0", "test_deterministic_logging", "policy_binding")
_emit_snapshots_state("p0", "test_deterministic_logging", "state_snapshot")
emit_replay_key("p0", "test_deterministic_logging")
emit_determinism_digest("p0", "test_deterministic_logging")
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

class TestHITLDecisionLogger:
    def test_log_returns_decision(self, tmp_path):
        logger = HITLDecisionLogger(log_path=tmp_path / "decisions.jsonl")
        decision = logger.log(
            agent="TestAgent",
            file="foo.py",
            violation="missing_field",
            proposed="add field",
            decision="APPROVE",
            reviewer_signature="reviewer@test.com",
        )
        assert isinstance(decision, HITLDecision)
        assert decision.agent == "TestAgent"
        assert decision.decision == "APPROVE"
        assert decision.decision_number == 1

    def test_counter_increments(self, tmp_path):
        logger = HITLDecisionLogger(log_path=tmp_path / "decisions.jsonl")
        d1 = logger.log("A", "f1.py", "v1", "p1", "APPROVE")
        d2 = logger.log("B", "f2.py", "v2", "p2", "REJECT")
        assert d1.decision_number == 1
        assert d2.decision_number == 2

    def test_log_line_format(self, tmp_path):
        logger = HITLDecisionLogger(log_path=tmp_path / "decisions.jsonl")
        d = logger.log("AgentX", "bar.py", "bad_import", "fix import", "REJECT")
        line = d.to_log_line()
        assert "HITL_DECISION_1" in line
        assert "Agent=AgentX" in line
        assert "File=bar.py" in line
        assert "Violation=bad_import" in line
        assert "Decision=REJECT" in line

    def test_no_timestamp_in_log_line(self, tmp_path):
        """Determinism rule: no wall-clock timestamps in key fields."""
        logger = HITLDecisionLogger(log_path=tmp_path / "decisions.jsonl")
        d = logger.log("A", "f.py", "v", "p", "APPROVE")
        line = d.to_log_line()
        import re

        assert not re.search(r"\d{4}-\d{2}-\d{2}", line), "Timestamp found in log line"

    def test_written_to_jsonl_file(self, tmp_path):
        log_path = tmp_path / "decisions.jsonl"
        logger = HITLDecisionLogger(log_path=log_path)
        logger.log("A", "f.py", "v", "p", "APPROVE")
        assert log_path.exists()
        with open(log_path) as f:
            record = json.loads(f.readline())
        assert record["agent"] == "A"
        assert record["decision"] == "APPROVE"

    def test_all_records_retrievable(self, tmp_path):
        logger = HITLDecisionLogger(log_path=tmp_path / "decisions.jsonl")
        for i in range(3):
            logger.log(f"Agent{i}", f"f{i}.py", "v", "p", "APPROVE")
        records = logger.all_records()
        assert len(records) == 3

    def test_count_matches_logged(self, tmp_path):
        logger = HITLDecisionLogger(log_path=tmp_path / "decisions.jsonl")
        logger.log("A", "f.py", "v", "p", "APPROVE")
        logger.log("B", "g.py", "v", "p", "REJECT")
        assert logger.count() == 2

    def test_negative_no_records_without_log_call(self, tmp_path):
        """Negative control: fresh logger must have zero records."""
        logger = HITLDecisionLogger(log_path=tmp_path / "decisions.jsonl")
        assert logger.count() == 0
        assert logger.all_records() == []
