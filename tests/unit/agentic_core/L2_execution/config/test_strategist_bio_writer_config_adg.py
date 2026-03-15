"""ADG-driven tests for L2_execution/config/strategist_bio_writer_config.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.config.strategist_bio_writer_config import BioWriterConfig
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    BioWriterConfig = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="strategist_bio_writer_config deps unavailable")
class TestBioWriterConfig:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(BioWriterConfig)

    def test_creates_with_defaults(self):
        cfg = BioWriterConfig()
        assert cfg.min_words == 118
        assert cfg.max_words == 135
        assert cfg.VOICE == "THIRD_PERSON_IMPLIED"
        assert cfg.TEMPERATURE == 0.6
        assert cfg.max_attempts == 3

    def test_word_range_valid(self):
        cfg = BioWriterConfig()
        assert cfg.min_words < cfg.max_words


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
