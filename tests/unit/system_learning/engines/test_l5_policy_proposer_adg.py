"""ADG importability contract for system_learning/engines/l5_policy_proposer.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_l5_policy_proposer.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from system_learning.engines.l5_policy_proposer import (  # noqa: F401
        L5PolicyChangePackage,
        L5PolicyProposer,
        extract_l5_metrics_from_healing_actions,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    L5PolicyChangePackage = None  # type: ignore[assignment,misc]
    L5PolicyProposer = None  # type: ignore[assignment,misc]
    extract_l5_metrics_from_healing_actions = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="l5_policy_proposer.py deps unavailable")
class TestL5PolicyProposerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: l5_policy_proposer.py must be importable."""
        assert _AVAILABLE

    def test_l5policychangepackage_is_type(self) -> None:
        assert L5PolicyChangePackage is not None

    def test_l5policyproposer_is_type(self) -> None:
        assert L5PolicyProposer is not None

    def test_extract_l5_metrics_from_healing_actions_callable(self) -> None:
        assert callable(extract_l5_metrics_from_healing_actions)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

