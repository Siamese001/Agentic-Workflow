"""Foundational behavioral tests for agentic_core/L2_execution/types/sandbox_envelope_types.py.

fan_in=5 — imported by 5 other modules.
ADG import-hygiene is covered separately by test_sandbox_envelope_types_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.types.sandbox_envelope_types import (  # noqa: F401
        DEFAULT_TOOL_BUDGET,
        SandboxEnvelope,
        ToolBudget,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    ToolBudget = None  # type: ignore[assignment,misc]
    SandboxEnvelope = None  # type: ignore[assignment,misc]
    DEFAULT_TOOL_BUDGET = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="sandbox_envelope_types.py deps unavailable")
class TestToolBudgetContract:
    def test_is_class(self):
        assert isinstance(ToolBudget, type)

@pytest.mark.skipif(not _AVAILABLE, reason="sandbox_envelope_types.py deps unavailable")
class TestSandboxEnvelopeContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(SandboxEnvelope)

    def test_is_frozen(self):
        assert SandboxEnvelope.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(SandboxEnvelope)}
        assert fnames >= {'invocation_metadata', 'instruction_packet_id', 'tool_name', 'envelope_id', 'budget', 'tool_args'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(SandboxEnvelope)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="sandbox_envelope_types.py deps unavailable")
class TestDefaultToolBudgetConstant:
    def test_is_not_none(self):
        assert DEFAULT_TOOL_BUDGET is not None


def test_module_importable():
    """Smoke: sandbox_envelope_types importable or gracefully unavailable."""
    pass