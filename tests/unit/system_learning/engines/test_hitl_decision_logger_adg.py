"""ADG-driven tests for system_learning/engines/hitl_decision_logger.py — fan_in=2.

Contract tests: log_hitl_decision, _get_evidence_path, counter behavior.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

from system_learning.engines.hitl_decision_logger import (
    _get_evidence_path,
    log_hitl_decision,
)


class TestGetEvidencePath:
    def test_returns_path_object(self):
        result = _get_evidence_path()
        assert isinstance(result, Path)

    def test_env_override_used(self):
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
            tmp = f.name
        try:
            os.environ["HITL_EVIDENCE_FILE"] = tmp
            result = _get_evidence_path()
            assert str(result) == tmp
        finally:
            os.environ.pop("HITL_EVIDENCE_FILE", None)
            Path(tmp).unlink(missing_ok=True)

    def test_default_path_when_no_env(self):
        os.environ.pop("HITL_EVIDENCE_FILE", None)
        result = _get_evidence_path()
        assert "evidence" in str(result).lower() or "docs" in str(result).lower()


class TestLogHitlDecision:
    def test_returns_positive_int(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            tmp = f.name
        try:
            os.environ["HITL_EVIDENCE_FILE"] = tmp
            result = log_hitl_decision(
                agent="TestAgent",
                file_path="foo/bar.py",
                violation="EMPTY_FILE",
                proposed="ARCHIVE",
                decision="APPROVED",
            )
            assert isinstance(result, int)
            assert result > 0
        finally:
            os.environ.pop("HITL_EVIDENCE_FILE", None)
            Path(tmp).unlink(missing_ok=True)

    def test_counter_increments(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            tmp = f.name
        try:
            os.environ["HITL_EVIDENCE_FILE"] = tmp
            n1 = log_hitl_decision(
                agent="AgentA", file_path="a.py",
                violation="V1", proposed="P1", decision="APPROVED",
            )
            n2 = log_hitl_decision(
                agent="AgentB", file_path="b.py",
                violation="V2", proposed="P2", decision="SKIPPED",
            )
            assert n2 == n1 + 1
        finally:
            os.environ.pop("HITL_EVIDENCE_FILE", None)
            Path(tmp).unlink(missing_ok=True)

    def test_appends_to_file(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            tmp = f.name
        try:
            os.environ["HITL_EVIDENCE_FILE"] = tmp
            log_hitl_decision(
                agent="TestAgent", file_path="x.py",
                violation="TEST_V", proposed="MOVE", decision="APPROVED",
                extra={"note": "test_run"},
            )
            content = Path(tmp).read_text(encoding="utf-8")
            assert "TestAgent" in content or len(content) > 0
        finally:
            os.environ.pop("HITL_EVIDENCE_FILE", None)
            Path(tmp).unlink(missing_ok=True)

    def test_accepts_extra_dict(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            tmp = f.name
        try:
            os.environ["HITL_EVIDENCE_FILE"] = tmp
            result = log_hitl_decision(
                agent="AgentExtra",
                file_path="extra.py",
                violation="EXTRA_V",
                proposed="RENAME",
                decision="MANUAL",
                extra={"reason": "needs review", "priority": "high"},
            )
            assert isinstance(result, int)
        finally:
            os.environ.pop("HITL_EVIDENCE_FILE", None)
            Path(tmp).unlink(missing_ok=True)
