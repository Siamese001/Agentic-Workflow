"""
Guardian Semantic Coverage Assertions.

Provides test helper functions that:
1. Assert check_id presence/status in GuardianResult
2. Log assertions to a global registry for coverage tracking

Usage in tests:
    from tests.guardian._assertions import assert_check, get_asserted_check_ids

    def test_hygiene_pass(clean_repo):
        result = run_hygiene_guardian(repo_root=clean_repo)
        assert_check(result, "temp_artifacts", status="PASS")
        assert_check(result, "empty_folders", status="PASS")
"""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agentic_core.L0_routing.types.guardian_contract_types import GuardianResult

# Thread-safe global registry of asserted check_ids
_ASSERTED_CHECK_IDS: dict[str, set[str]] = {}  # guardian_id -> {check_ids}
_ASSERTED_SCENARIOS: dict[str, set[str]] = {}  # guardian_id -> {"PASS", "FAIL"}
_LOCK = threading.Lock()


def _register_assertion(guardian_id: str, check_id: str, scenario: str | None) -> None:
    """Record an assertion for coverage tracking."""
    with _LOCK:
        if guardian_id not in _ASSERTED_CHECK_IDS:
            _ASSERTED_CHECK_IDS[guardian_id] = set()
        _ASSERTED_CHECK_IDS[guardian_id].add(check_id)

        if scenario:
            if guardian_id not in _ASSERTED_SCENARIOS:
                _ASSERTED_SCENARIOS[guardian_id] = set()
            _ASSERTED_SCENARIOS[guardian_id].add(scenario)


def assert_check(
    result: GuardianResult,
    check_id: str,
    *,
    status: str | None = None,
    details_contains: str | None = None,
    evidence_predicate: callable | None = None,
) -> None:
    """
    Assert that a check_id exists in the result and optionally matches criteria.

    Args:
        result: The GuardianResult to inspect.
        check_id: The check_id to find.
        status: If provided, assert the check has this status (PASS/FAIL/SKIP).
        details_contains: If provided, assert details contain this substring.
        evidence_predicate: If provided, callable that takes evidence dict and returns bool.

    Raises:
        AssertionError: If the check is not found or criteria not met.

    Note:
        Coverage is only recorded if status is asserted AND at least one semantic
        property is verified (details_contains or evidence_predicate).
        This prevents "empty assertions" from satisfying the coverage ratchet.
    """
    # Find the check first
    matching = [c for c in result.checks if c.check_id == check_id]
    assert matching, (
        f"check_id '{check_id}' not found in guardian '{result.guardian_id}'. "
        f"Available: {[c.check_id for c in result.checks]}"
    )

    check = matching[0]

    # Validate status
    if status is not None:
        assert check.status == status, (
            f"check_id '{check_id}' status: expected '{status}', got '{check.status}'"
        )

    # Validate semantic properties
    semantic_verified = False
    if details_contains is not None:
        assert details_contains in check.details, (
            f"check_id '{check_id}' details: expected to contain '{details_contains}', got '{check.details}'"
        )
        semantic_verified = True

    if evidence_predicate is not None:
        assert evidence_predicate(check.evidence), (
            f"check_id '{check_id}' evidence predicate failed for {check.evidence}"
        )
        semantic_verified = True

    # Register for coverage tracking ONLY if quality assertion
    # (status + at least one semantic property)
    if status is not None and semantic_verified:
        scenario = status if status in ("PASS", "FAIL") else None
        _register_assertion(result.guardian_id, check_id, scenario)


def assert_guardian_status(result: GuardianResult, expected: str) -> None:
    """
    Assert the overall guardian status and register the scenario.

    Args:
        result: The GuardianResult to inspect.
        expected: Expected status (PASS/FAIL/ERROR).
    """
    _register_assertion(result.guardian_id, "__guardian_status__", expected)
    assert result.status == expected, (
        f"Guardian '{result.guardian_id}' status: expected '{expected}', got '{result.status}'"
    )


def get_asserted_check_ids() -> dict[str, set[str]]:
    """Return a copy of all asserted check_ids by guardian."""
    with _LOCK:
        return {k: v.copy() for k, v in _ASSERTED_CHECK_IDS.items()}


def get_asserted_scenarios() -> dict[str, set[str]]:
    """Return a copy of all asserted scenarios (PASS/FAIL) by guardian."""
    with _LOCK:
        return {k: v.copy() for k, v in _ASSERTED_SCENARIOS.items()}


def clear_assertion_registry() -> None:
    """Clear all recorded assertions (for test isolation)."""
    with _LOCK:
        _ASSERTED_CHECK_IDS.clear()
        _ASSERTED_SCENARIOS.clear()
