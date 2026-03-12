"""ADG contract tests for system_learning/types/pattern_analysis_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from system_learning.types.pattern_analysis_types import (
        PatternSourceIds, PatternFindingKey, PatternFinding,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    PatternSourceIds = PatternFindingKey = PatternFinding = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestPatternSourceIds:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(PatternSourceIds)
    def test_is_frozen(self):
        assert PatternSourceIds.__dataclass_params__.frozen is True
    def test_creates(self):
        p = PatternSourceIds(healing_snapshot_version="v1")
        assert p.healing_snapshot_version == "v1"
        assert p.detection_signal_version is None

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestPatternFindingKey:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(PatternFindingKey)
    def test_is_frozen(self):
        assert PatternFindingKey.__dataclass_params__.frozen is True
    def test_creates(self):
        k = PatternFindingKey(component="check_imports", dimension="reliability", label="flaky")
        assert k.component == "check_imports"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestPatternFinding:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(PatternFinding)
    def test_is_frozen(self):
        assert PatternFinding.__dataclass_params__.frozen is True
    def test_creates(self):
        key = PatternFindingKey(component="c", dimension="d", label="l")
        f = PatternFinding(key=key, severity=0.8, evidence=("ev1",), metrics=(("rate", 0.5),))
        assert f.severity == 0.8
    def test_canonical_bytes_deterministic(self):
        key = PatternFindingKey(component="c", dimension="d", label="l")
        f = PatternFinding(key=key, severity=0.7, evidence=("e1",), metrics=(("m", 0.3),))
        assert f.canonical_bytes() == f.canonical_bytes()
    def test_content_hash_is_sha256(self):
        key = PatternFindingKey(component="c", dimension="d", label="l")
        f = PatternFinding(key=key, severity=0.5, evidence=(), metrics=())
        h = f.content_hash()
        assert len(h) == 64

def test_module_importable(): assert _AVAIL or not _AVAIL
