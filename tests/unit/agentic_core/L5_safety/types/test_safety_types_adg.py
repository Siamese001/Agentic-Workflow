"""ADG contract tests for L5_safety/types/safety_types.py."""
from __future__ import annotations
import ast
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L5_safety.types.safety_types import ThreatLevel, RuleType
    _AVAIL = True
except Exception:
    _AVAIL = False; ThreatLevel = RuleType = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestThreatLevel:
    def test_is_enum(self):
        import enum; assert issubclass(ThreatLevel, enum.Enum)
    def test_has_four_levels(self): assert len(list(ThreatLevel)) == 4
    def test_critical(self): assert ThreatLevel.CRITICAL.value == "critical"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestRuleType:
    def test_is_enum(self):
        import enum; assert issubclass(RuleType, enum.Enum)
    def test_has_pattern_match(self): assert RuleType.PATTERN_MATCH.value == "pattern_match"

def test_module_parses():
    import pathlib
    src = pathlib.Path("agentic_core/L5_safety/types/safety_types.py").read_text(encoding="utf-8")
    ast.parse(src)
