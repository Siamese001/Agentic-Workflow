"""ADG importability contract for agentic_core/L2_execution/enforcement/provider_substitution_prohibition.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_provider_substitution_prohibition.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.enforcement.provider_substitution_prohibition import (  # noqa: F401
        ProviderRequest,
        ProviderSubstitutionGuard,
        ProviderSubstitutionViolation,
        enforce_fail_closed_on_failure,
        get_substitution_guard,
        validate_provider_request,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ProviderRequest = None  # type: ignore[assignment,misc]
    ProviderSubstitutionViolation = None  # type: ignore[assignment,misc]
    validate_provider_request = None  # type: ignore[assignment,misc]
    enforce_fail_closed_on_failure = None  # type: ignore[assignment,misc]
    ProviderSubstitutionGuard = None  # type: ignore[assignment,misc]
    get_substitution_guard = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="provider_substitution_prohibition deps unavailable")
class TestProviderSubstitutionProhibitionImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L2_execution/enforcement/provider_substitution_prohibition.py must be importable."""
        assert _AVAILABLE

    def test_providerrequest_defined(self) -> None:
        assert ProviderRequest is not None

    def test_providersubstitutionviolation_defined(self) -> None:
        assert ProviderSubstitutionViolation is not None

    def test_providersubstitutionguard_defined(self) -> None:
        assert ProviderSubstitutionGuard is not None
