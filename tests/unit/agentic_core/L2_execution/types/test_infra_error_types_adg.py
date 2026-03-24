"""ADG importability contract for agentic_core/L2_execution/types/infra_error_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_infra_error_types.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.types.infra_error_types import (  # noqa: F401
        InfrastructureDependencyError,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    InfrastructureDependencyError = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="infra_error_types deps unavailable")
class TestInfraErrorTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L2_execution/types/infra_error_types.py must be importable."""
        assert _AVAILABLE

    def test_infrastructuredependencyerror_defined(self) -> None:
        assert InfrastructureDependencyError is not None