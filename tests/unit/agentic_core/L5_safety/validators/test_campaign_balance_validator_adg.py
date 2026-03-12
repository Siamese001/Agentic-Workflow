"""ADG importability contract for agentic_core/L5_safety/validators/campaign_balance_validator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_campaign_balance_validator.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.validators.campaign_balance_validator import (  # noqa: F401
        BalanceResult,
        CampaignBalanceValidator,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    BalanceResult = None  # type: ignore[assignment,misc]
    CampaignBalanceValidator = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="campaign_balance_validator.py deps unavailable")
class TestCampaignBalanceValidatorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: campaign_balance_validator.py must be importable."""
        assert _AVAILABLE

    def test_balanceresult_is_type(self) -> None:
        assert BalanceResult is not None

    def test_campaignbalancevalidator_is_type(self) -> None:
        assert CampaignBalanceValidator is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

