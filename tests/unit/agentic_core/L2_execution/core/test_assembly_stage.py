"""Smoke tests for assembly_stage exports."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution._agentic_core_smoke import import_attr_or_skip, import_module_or_skip


@pytest.mark.unit
class TestAssemblyStage:
    """Smoke tests for assembly_stage exports."""

    def test_assembly_stage_imports(self) -> None:
        """Import submodule."""
        module = import_module_or_skip("agentic_core.assembly_stage")
        assert module is not None

    def test_assembly_stage_class(self) -> None:
        """Import AssemblyStage."""
        klass = import_attr_or_skip("agentic_core.assembly_stage", "AssemblyStage")
        assert klass is not None

    def test_validate_stage(self) -> None:
        """Import validate_stage."""
        validator = import_attr_or_skip("agentic_core.assembly_stage", "validate_stage")
        assert callable(validator)
