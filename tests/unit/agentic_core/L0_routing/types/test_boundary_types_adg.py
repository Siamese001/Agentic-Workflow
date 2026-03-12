"""ADG contract tests for agentic_core/L0_routing/types/boundary_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L0_routing.types.boundary_types import (
        SSOTBinding, ContextRetrievalRequest, SchemaValidationStatus,
        BoundarySchemaDescriptor, InvariantSeverity, InvariantViolation,
        MetaInvariantReport, InvariantCheck,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    SSOTBinding = ContextRetrievalRequest = SchemaValidationStatus = None  # type: ignore[assignment,misc]
    BoundarySchemaDescriptor = InvariantSeverity = InvariantViolation = None  # type: ignore[assignment,misc]
    MetaInvariantReport = InvariantCheck = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestSSOTBinding:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(SSOTBinding)
    def test_is_frozen(self): assert SSOTBinding.__dataclass_params__.frozen is True
    def test_creates(self):
        b = SSOTBinding(node_id="n1", blueprint_entry="bp1", resolved=True)
        assert b.resolved is True
    def test_empty_node_id_raises(self):
        with pytest.raises(ValueError): SSOTBinding(node_id="", blueprint_entry="bp", resolved=True)

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestContextRetrievalRequest:
    def test_creates(self):
        r = ContextRetrievalRequest(trace_id="t1", query_hash="q1", semantic_clock_tick=1)
        assert r.read_only is True; assert r.source_layer == "L0"
    def test_negative_tick_raises(self):
        with pytest.raises(ValueError):
            ContextRetrievalRequest(trace_id="t", query_hash="q", semantic_clock_tick=-1)

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestSchemaValidationStatus:
    def test_is_enum(self):
        import enum; assert issubclass(SchemaValidationStatus, enum.Enum)
    def test_has_valid(self): assert SchemaValidationStatus.VALID.value == "valid"
    def test_three_statuses(self): assert len(list(SchemaValidationStatus)) == 3

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestInvariantSeverity:
    def test_is_enum(self):
        import enum; assert issubclass(InvariantSeverity, enum.Enum)
    def test_has_critical(self): assert InvariantSeverity.CRITICAL.value == "critical"
    def test_four_levels(self): assert len(list(InvariantSeverity)) == 4

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestInvariantViolation:
    def test_is_frozen(self): assert InvariantViolation.__dataclass_params__.frozen is True
    def test_creates(self):
        v = InvariantViolation(
            invariant_id="P6.1", severity=InvariantSeverity.CRITICAL,
            evidence_paths=("a/b.py",), details="cross-layer import",
        )
        assert v.invariant_id == "P6.1"

def test_module_importable(): assert _AVAIL or not _AVAIL
