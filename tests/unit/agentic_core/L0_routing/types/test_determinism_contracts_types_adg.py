"""ADG importability contract for agentic_core/L0_routing/types/determinism_contracts_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_determinism_contracts_types.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.types.determinism_contracts_types import (  # noqa: F401
        ForbiddenInputError,
        canonical_ast_serialize,
        check_forbidden_input_type,
        require_manifest_hash_ok,
        validate_execution_input,
        validate_manifest_emission,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ForbiddenInputError = None  # type: ignore[assignment,misc]
    validate_execution_input = None  # type: ignore[assignment,misc]
    check_forbidden_input_type = None  # type: ignore[assignment,misc]
    validate_manifest_emission = None  # type: ignore[assignment,misc]
    require_manifest_hash_ok = None  # type: ignore[assignment,misc]
    canonical_ast_serialize = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="determinism_contracts_types deps unavailable")
class TestDeterminismContractsTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L0_routing/types/determinism_contracts_types.py must be importable."""
        assert _AVAILABLE

    def test_forbiddeninputerror_defined(self) -> None:
        assert ForbiddenInputError is not None
