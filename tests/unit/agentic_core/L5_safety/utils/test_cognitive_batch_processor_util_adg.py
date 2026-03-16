"""ADG-driven tests for L5_safety/utils/cognitive_batch_processor_util.py — fan_in=1."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_cognitive_batch_processor_util_adg")
_emit_applies_guardrail("p0", "test_cognitive_batch_processor_util_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_cognitive_batch_processor_util_adg", "policy_binding")
_emit_snapshots_state("p0", "test_cognitive_batch_processor_util_adg", "state_snapshot")
emit_replay_key("p0", "test_cognitive_batch_processor_util_adg")
emit_determinism_digest("p0", "test_cognitive_batch_processor_util_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.utils.cognitive_batch_processor_util import CognitiveBatchProcessor


class TestCognitiveBatchProcessor:
    def test_creates(self, tmp_path):
        agent = MagicMock()
        processor = CognitiveBatchProcessor(
            agent=agent,
            checkpoint_file=tmp_path / "ckpt.json",
        )
        assert processor is not None

    def test_rate_limit_delay_default(self, tmp_path):
        agent = MagicMock()
        processor = CognitiveBatchProcessor(
            agent=agent,
            checkpoint_file=tmp_path / "ckpt.json",
        )
        assert processor.rate_limit_delay == pytest.approx(1.0)

    def test_checkpoint_interval_default(self, tmp_path):
        agent = MagicMock()
        processor = CognitiveBatchProcessor(
            agent=agent,
            checkpoint_file=tmp_path / "ckpt.json",
        )
        assert processor.checkpoint_interval == 10

    def test_max_retries_default(self, tmp_path):
        agent = MagicMock()
        processor = CognitiveBatchProcessor(
            agent=agent,
            checkpoint_file=tmp_path / "ckpt.json",
        )
        assert processor.max_retries == 3

    def test_results_start_empty_no_checkpoint(self, tmp_path):
        agent = MagicMock()
        processor = CognitiveBatchProcessor(
            agent=agent,
            checkpoint_file=tmp_path / "ckpt.json",
        )
        assert processor.results == {}

    def test_has_process_batch(self):
        assert hasattr(CognitiveBatchProcessor, "process_batch")
