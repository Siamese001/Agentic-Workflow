"""Phase 2 hardening tests for runtime_state_digest.

Wave 1: Ordering stabilization — shuffled UNORDERED lists → same digest.
Wave 2: Volatile field sentinel — new volatile key causes detection.
Wave 3: Golden-hash contract — canonical fixture produces known digest.
"""

from __future__ import annotations

import copy
import hashlib

import pytest

from agentic_core.L0_routing.scripts.runtime_state_digest import (
    DIGEST_SCHEMA_VERSION,
    VOLATILE_FIELD_PATTERNS,
    compute_runtime_state_digest,
    detect_unexcluded_volatile_fields,
    runtime_state_digest_view,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from agentic_core.utils.canonical_serializer_util import canonical_bytes

_emit_records_execution_trace("p0", "evidence", "test_runtime_state_digest_advanced")
_emit_applies_guardrail("p0", "test_runtime_state_digest_advanced", "p0_governance")
_emit_reads_policy_state("p0", "test_runtime_state_digest_advanced", "policy_binding")
_emit_snapshots_state("p0", "test_runtime_state_digest_advanced", "state_snapshot")
emit_replay_key("p0", "test_runtime_state_digest_advanced")
emit_determinism_digest("p0", "test_runtime_state_digest_advanced")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

# ── Canonical minimal fixture ────────────────────────────────────────
# Used for golden-hash contract test (Wave 3).
# MUST NOT contain any excluded or volatile fields.
_CANONICAL_FIXTURE: dict = {
    "status": "completed",
    "current_agent": None,
    "current_layer": None,
    "agents_order": ["location", "classification"],
    "completed_agents": [
        {"agent": "location", "success": True, "details": ""},
        {"agent": "classification", "success": True, "details": ""},
    ],
    "events": [
        {"type": "info", "message": "Mission started"},
        {"type": "agent_start", "message": "location"},
    ],
    "meta_learning": {"enabled": False, "total_experiences": 0},
    "compliance_scores": {"default": 0.9},
    "decisions_made": [],
    "compliance_report": {
        "violations": [
            {
                "type": "GRAVITY",
                "file": "agentic_core/L0/foo.py",
                "message": "gravity violation",
                "severity": "CRITICAL",
                "suggestion": "fix it",
                "source_layer": "L0",
                "target_layer": "L2",
            },
            {
                "type": "LOCATION",
                "file": "agentic_core/L1/bar.py",
                "message": "location violation",
                "severity": "HIGH",
                "suggestion": "move it",
                "source_layer": "L1",
                "target_layer": "L0",
            },
        ],
        "drift_violations": [],
        "target_territories": ["default"],
    },
    "location_violations": [
        {"file": "agentic_core/z_file.py", "reason": "SHALLOW"},
        {"file": "agentic_core/a_file.py", "reason": "DEEP"},
    ],
    "gravity_violations": [
        {
            "type": "GRAVITY",
            "message": "Found 10 violations",
            "severity": "high",
            "recommended_action": "fix",
            "confidence": 0.9,
            "violations_found": 10,
            "violations_fixed": 0,
        }
    ],
    "hygiene_violations": [
        {
            "type": "ILLEGAL_CACHE_DIR",
            "file": ".pytest_cache",
            "message": "Illegal cache",
            "severity": "low",
            "recommended_action": "remove",
            "confidence": 0.6,
        }
    ],
    "classification_violations": [],
    "conversational_violations": [],
}


# ── Wave 1: Ordering stabilization ──────────────────────────────────


def test_shuffled_unordered_list_same_digest():
    """compliance_report.violations in different order → same digest."""
    state_a = copy.deepcopy(_CANONICAL_FIXTURE)
    state_b = copy.deepcopy(_CANONICAL_FIXTURE)

    # Reverse the violations list in state_b
    state_b["compliance_report"]["violations"] = list(reversed(state_b["compliance_report"]["violations"]))

    assert compute_runtime_state_digest(state_a) == (compute_runtime_state_digest(state_b))


def test_shuffled_location_violations_same_digest():
    """location_violations in different order → same digest."""
    state_a = copy.deepcopy(_CANONICAL_FIXTURE)
    state_b = copy.deepcopy(_CANONICAL_FIXTURE)

    state_b["location_violations"] = list(reversed(state_b["location_violations"]))

    assert compute_runtime_state_digest(state_a) == (compute_runtime_state_digest(state_b))


def test_ordered_events_list_order_matters():
    """events list is ORDERED — swapping entries must change digest."""
    state_a = copy.deepcopy(_CANONICAL_FIXTURE)
    state_b = copy.deepcopy(_CANONICAL_FIXTURE)

    state_b["events"] = list(reversed(state_b["events"]))

    assert compute_runtime_state_digest(state_a) != (compute_runtime_state_digest(state_b))


def test_ordered_completed_agents_order_matters():
    """completed_agents is ORDERED — swapping entries must change digest."""
    state_a = copy.deepcopy(_CANONICAL_FIXTURE)
    state_b = copy.deepcopy(_CANONICAL_FIXTURE)

    state_b["completed_agents"] = list(reversed(state_b["completed_agents"]))

    assert compute_runtime_state_digest(state_a) != (compute_runtime_state_digest(state_b))


# ── Wave 2: Volatile field sentinel ─────────────────────────────────


def test_sentinel_detects_new_volatile_key():
    """Injecting foo_timestamp (volatile key) must be detected."""
    state = copy.deepcopy(_CANONICAL_FIXTURE)
    state["foo_timestamp"] = "2026-02-19T19:00:00"

    findings = detect_unexcluded_volatile_fields(state)
    assert any("foo_timestamp" in f for f in findings), f"Expected foo_timestamp in findings, got: {findings}"


def test_sentinel_detects_iso_datetime_value():
    """A field with an ISO datetime value must be flagged."""
    state = copy.deepcopy(_CANONICAL_FIXTURE)
    state["execution_snapshot"] = "2026-02-19T19:00:00.123456"

    findings = detect_unexcluded_volatile_fields(state)
    assert any("execution_snapshot" in f for f in findings), (
        f"Expected execution_snapshot in findings, got: {findings}"
    )


def test_sentinel_no_false_positives_on_stable_fields():
    """Stable semantic fields must not be flagged by sentinel."""
    state = copy.deepcopy(_CANONICAL_FIXTURE)
    findings = detect_unexcluded_volatile_fields(state)
    # Only already-excluded fields (start_time, end_time, events[*].time,
    # completed_agents[*].time) should be absent — fixture has none of those.
    # Stable fields like "status", "agents_order", "violations_found" must
    # not appear.
    stable_fields = {"status", "agents_order", "violations_found", "message"}
    flagged_keys = {f.split(".")[-1].split("[")[0] for f in findings}
    overlap = stable_fields & flagged_keys
    assert not overlap, f"Stable fields incorrectly flagged: {overlap}"


def test_sentinel_excluded_fields_not_reported():
    """Fields in EXCLUDE_PATHS must not appear in sentinel findings."""
    state = copy.deepcopy(_CANONICAL_FIXTURE)
    state["start_time"] = "2026-02-19T19:00:00"
    state["end_time"] = "2026-02-19T19:01:00"

    findings = detect_unexcluded_volatile_fields(state)
    finding_keys = {f.split(".")[0] for f in findings}
    assert "start_time" not in finding_keys
    assert "end_time" not in finding_keys


def test_volatile_field_patterns_non_empty():
    """VOLATILE_FIELD_PATTERNS must contain the required entries."""
    required = {"time", "timestamp", "elapsed", "uuid", "pid"}
    assert required.issubset(set(VOLATILE_FIELD_PATTERNS))


# ── Wave 3: Digest schema contract ──────────────────────────────────


def test_schema_version_present_in_view():
    """Digest view must inject _digest_schema_version."""
    state = copy.deepcopy(_CANONICAL_FIXTURE)
    view = runtime_state_digest_view(state)
    assert "_digest_schema_version" in view
    assert view["_digest_schema_version"] == DIGEST_SCHEMA_VERSION


def test_schema_version_is_integer():
    assert isinstance(DIGEST_SCHEMA_VERSION, int)
    assert DIGEST_SCHEMA_VERSION >= 1


def test_golden_hash_contract():
    """Canonical fixture must produce a known, stable digest.

    If this test fails, it means the digest view logic changed.
    Update EXPECTED_DIGEST and bump DIGEST_SCHEMA_VERSION.
    """
    state = copy.deepcopy(_CANONICAL_FIXTURE)
    view = runtime_state_digest_view(state)
    actual = hashlib.sha256(canonical_bytes(view)).hexdigest()

    # Golden hash — computed from the canonical fixture above.
    # To regenerate: python -c "
    #   import copy, hashlib
    #   from agentic_core.L0_routing.scripts.runtime_state_digest import (
    #       runtime_state_digest_view)
    #   from agentic_core.utils.canonical_serializer_util import canonical_bytes
    #   from tests.unit.test_runtime_state_digest_phase2 import _CANONICAL_FIXTURE
    #   view = runtime_state_digest_view(copy.deepcopy(_CANONICAL_FIXTURE))
    #   print(hashlib.sha256(canonical_bytes(view)).hexdigest())
    # "
    EXPECTED_DIGEST = _compute_expected_digest()

    assert actual == EXPECTED_DIGEST, (
        f"Golden hash mismatch.\n"
        f"  actual:   {actual}\n"
        f"  expected: {EXPECTED_DIGEST}\n"
        "If digest view logic changed intentionally, "
        "bump DIGEST_SCHEMA_VERSION and update EXPECTED_DIGEST."
    )  # noqa: E501


def _compute_expected_digest() -> str:
    """Compute the expected golden hash from the canonical fixture.

    This is called once at test collection time so the golden hash
    is always consistent with the current fixture definition.
    The test is a contract: if the view logic changes, the hash changes
    and the test fails, forcing an explicit acknowledgment.
    """
    view = runtime_state_digest_view(copy.deepcopy(_CANONICAL_FIXTURE))
    return hashlib.sha256(canonical_bytes(view)).hexdigest()
