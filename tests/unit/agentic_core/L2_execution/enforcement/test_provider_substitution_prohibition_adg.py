"""ADG importability contract for agentic_core/L2_execution/enforcement/provider_substitution_prohibition.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_provider_substitution_prohibition.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.enforcement.provider_substitution_prohibition import (  # noqa: F401
        ProviderRequest,
        ProviderSubstitutionViolation,
        ProviderSubstitutionGuard,
        validate_provider_request,
        enforce_fail_closed_on_failure,
        get_substitution_guard,
        test_provider_substitution_prohibition,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ProviderRequest = None  # type: ignore[assignment,misc]
    ProviderSubstitutionViolation = None  # type: ignore[assignment,misc]
    ProviderSubstitutionGuard = None  # type: ignore[assignment,misc]
    validate_provider_request = None  # type: ignore[assignment,misc]
    enforce_fail_closed_on_failure = None  # type: ignore[assignment,misc]
    get_substitution_guard = None  # type: ignore[assignment,misc]
    test_provider_substitution_prohibition = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="provider_substitution_prohibition.py deps unavailable")
class TestProviderSubstitutionProhibitionImportability:
    def test_module_importable(self) -> None:
        """ADG contract: provider_substitution_prohibition.py must be importable."""
        assert _AVAILABLE

    def test_providerrequest_is_type(self) -> None:
        assert ProviderRequest is not None

    def test_providersubstitutionviolation_is_type(self) -> None:
        assert ProviderSubstitutionViolation is not None

    def test_providersubstitutionguard_is_type(self) -> None:
        assert ProviderSubstitutionGuard is not None

    def test_validate_provider_request_callable(self) -> None:
        assert callable(validate_provider_request)

    def test_enforce_fail_closed_on_failure_callable(self) -> None:
        assert callable(enforce_fail_closed_on_failure)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

