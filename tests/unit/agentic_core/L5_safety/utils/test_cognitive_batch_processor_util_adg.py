"""ADG-driven tests for L5_safety/utils/cognitive_batch_processor_util.py — fan_in=1."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

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
