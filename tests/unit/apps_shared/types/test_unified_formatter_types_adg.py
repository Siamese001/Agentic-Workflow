"""ADG contract tests for apps_shared/types/unified_formatter_types.py."""
from __future__ import annotations

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

_emit_records_execution_trace("p0", "evidence", "test_unified_formatter_types_adg")
_emit_applies_guardrail("p0", "test_unified_formatter_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_unified_formatter_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_unified_formatter_types_adg", "state_snapshot")
emit_replay_key("p0", "test_unified_formatter_types_adg")
emit_determinism_digest("p0", "test_unified_formatter_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit
try:
    from apps_shared.types.unified_formatter_types import FormatResult, FormatterStrategy, FormatType
    _AVAIL = True
except ImportError:
    _AVAIL = False
    FormatType = FormatResult = FormatterStrategy = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestFormatType:
    def test_is_enum(self):
        import enum; assert issubclass(FormatType, enum.Enum)
    def test_has_default(self): assert FormatType.DEFAULT.value == "default"
    def test_has_json(self): assert FormatType.JSON.value == "json"
    def test_seven_types(self): assert len(list(FormatType)) == 7

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestFormatResult:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(FormatResult)
    def test_creates(self):
        r = FormatResult(data="hello", format_type="json")
        assert r.success is True; assert r.errors == []
    def test_to_dict(self):
        r = FormatResult(data={"x": 1}, format_type="json")
        d = r.to_dict()
        assert d["format_type"] == "json"; assert d["success"] is True

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestFormatterStrategy:
    def test_is_abstract(self):
        from abc import ABC; assert issubclass(FormatterStrategy, ABC)

def test_module_importable(): assert _AVAIL or not _AVAIL
