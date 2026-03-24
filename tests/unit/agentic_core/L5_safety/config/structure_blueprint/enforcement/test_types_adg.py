"""ADG importability contract for agentic_core/L5_safety/config/structure_blueprint/enforcement/types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.config.structure_blueprint.enforcement.types import (  # noqa: F401
        VERIFIER_VERSION,
        EnforcementReport,
        EnforcementResult,
        Violation,
        emit_report_json,
        make_report,
        make_result,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    Violation = None  # type: ignore[assignment,misc]
    EnforcementResult = None  # type: ignore[assignment,misc]
    EnforcementReport = None  # type: ignore[assignment,misc]
    make_result = None  # type: ignore[assignment,misc]
    make_report = None  # type: ignore[assignment,misc]
    emit_report_json = None  # type: ignore[assignment,misc]
    VERIFIER_VERSION = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="types.py deps unavailable")
class TestTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: types.py must be importable."""
        assert _AVAILABLE

    def test_violation_is_type(self) -> None:
        assert Violation is not None

    def test_enforcementresult_is_type(self) -> None:
        assert EnforcementResult is not None

    def test_enforcementreport_is_type(self) -> None:
        assert EnforcementReport is not None

    def test_make_result_callable(self) -> None:
        assert callable(make_result)

    def test_make_report_callable(self) -> None:
        assert callable(make_report)

    def test_verifier_version_defined(self) -> None:
        assert VERIFIER_VERSION is not None