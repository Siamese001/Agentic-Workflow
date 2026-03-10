"""Unit tests for runtime_state_digest deterministic digest."""

from __future__ import annotations

import copy

import pytest

from agentic_core.L0_routing.scripts.runtime_state_digest import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    EXCLUDE_PATHS,
    compute_runtime_state_digest,
    runtime_state_digest_view,
)

pytestmark = pytest.mark.unit

# ── Fixtures ────────────────────────────────────────────────────────

_BASE_STATE: dict = {
    "status": "completed",
    "start_time": "2026-02-19T19:00:00",
    "end_time": "2026-02-19T19:01:00",
    "current_agent": None,
    "current_layer": None,
    "agents_order": ["location", "classification"],
    "completed_agents": [
        {
            "agent": "location",
            "time": "2026-02-19T19:00:10",
            "success": True,
            "details": "",
        },
        {
            "agent": "classification",
            "time": "2026-02-19T19:00:30",
            "success": True,
            "details": "",
        },
    ],
    "events": [
        {
            "time": "2026-02-19T19:00:00",
            "type": "info",
            "message": "Mission started",
        },
        {
            "time": "2026-02-19T19:00:10",
            "type": "agent_start",
            "message": "location",
        },
    ],
    "meta_learning": {"enabled": False},
    "compliance_scores": {},
    "decisions_made": [],
    "compliance_report": {},
    "gravity_violations": [{"type": "GRAVITY", "violations_found": 384}],
}


# ── Test 1: timestamp variance does not change digest ───────────────


def test_timestamp_variance_same_digest():
    """Two states identical except for excluded timestamp fields
    must produce the same digest."""
    state_a = copy.deepcopy(_BASE_STATE)
    state_b = copy.deepcopy(_BASE_STATE)

    # Vary every excluded timestamp
    state_b["start_time"] = "2099-12-31T23:59:59"
    state_b["end_time"] = "2099-12-31T23:59:59"
    state_b["events"][0]["time"] = "2099-12-31T23:59:59"
    state_b["events"][1]["time"] = "2099-12-31T23:59:59"
    state_b["completed_agents"][0]["time"] = "2099-12-31T23:59:59"
    state_b["completed_agents"][1]["time"] = "2099-12-31T23:59:59"

    assert compute_runtime_state_digest(state_a) == (compute_runtime_state_digest(state_b))


# ── Test 2: semantic variance changes digest ────────────────────────


def test_semantic_variance_changes_digest():
    """Changing a meaningful field must produce a different digest."""
    state_a = copy.deepcopy(_BASE_STATE)
    state_b = copy.deepcopy(_BASE_STATE)

    state_b["gravity_violations"][0]["violations_found"] = 0

    assert compute_runtime_state_digest(state_a) != (compute_runtime_state_digest(state_b))


# ── Test 3: input immutability ──────────────────────────────────────


def test_digest_view_does_not_mutate_input():
    """runtime_state_digest_view must not mutate the input dict."""
    original = copy.deepcopy(_BASE_STATE)
    frozen = copy.deepcopy(original)

    runtime_state_digest_view(original)

    assert original == frozen


# ── Test 4: digest field self-exclusion ─────────────────────────────


def test_digest_field_excluded_from_own_computation():
    """Adding runtime_state_digest_sha256 to state must not
    change the digest value."""
    state_a = copy.deepcopy(_BASE_STATE)
    digest_without = compute_runtime_state_digest(state_a)

    state_a["runtime_state_digest_sha256"] = "bogus_old_value"
    digest_with = compute_runtime_state_digest(state_a)

    assert digest_without == digest_with


# ── Test 5: EXCLUDE_PATHS completeness ──────────────────────────────


def test_exclude_paths_contains_expected_entries():
    """Sanity check that EXCLUDE_PATHS has the required entries."""
    assert "start_time" in EXCLUDE_PATHS
    assert "end_time" in EXCLUDE_PATHS
    assert "events[*].time" in EXCLUDE_PATHS
    assert "completed_agents[*].time" in EXCLUDE_PATHS
    assert "runtime_state_digest_sha256" in EXCLUDE_PATHS
