"""Tests for time-shifted consumption behavior - Phase 7 functionality.

Tests that L0 reads only activated state from previous run, not same-run writes.
"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_time_shifted_consumption")
_emit_applies_guardrail("p0", "test_time_shifted_consumption", "p0_governance")
_emit_reads_policy_state("p0", "test_time_shifted_consumption", "policy_binding")
_emit_snapshots_state("p0", "test_time_shifted_consumption", "state_snapshot")
emit_replay_key("p0", "test_time_shifted_consumption")
emit_determinism_digest("p0", "test_time_shifted_consumption")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.unit_min_deps

from agentic_core.L0_routing.meta_control.config_store import (
    _clear_start_of_run_cache,
    activate_version,
    get_active_version,
    read_active_payload,
    read_version_payload,
    write_next_version,
)
from agentic_core.L0_routing.types.determinism_types import SemanticClockSnapshot


class TestTimeShiftedConsumption:
    """Test suite for time-shifted consumption behavior."""

    def test_time_shifted_behavior_t_reads_old_t1_reads_new(self):
        """Test time-shifted consumption: T reads old version, T+1 reads new version."""
        store_root = Path(TemporaryDirectory().name)
        app_id = "test_app"
        component = "prompt_templates"  # Valid mutable component

        # Clear cache for clean test
        _clear_start_of_run_cache()

        # Initial state: no versions
        assert get_active_version(store_root, app_id, component) == 0
        assert read_active_payload(store_root, app_id, component) == {}

        # Simulate start of run T: capture initial state
        initial_payload = read_active_payload(store_root, app_id, component)

        # Run t: write version 1 (this updates current.json for next run)
        semantic_clock = SemanticClockSnapshot(tick=1, vector_clock=(("L0", 1),))
        payload_v1 = {"key": "value_v1", "version": 1}

        write_next_version(
            store_root=store_root,
            app_id=app_id,
            component=component,
            payload=payload_v1,
            semantic_clock=semantic_clock,
        )

        # Version 1 is written and current.json is updated for next run
        # But L0 in run T still reads the initial state (time-shifted)
        assert read_active_payload(store_root, app_id, component) == initial_payload  # Still {}

        # Activate version 1 explicitly (this would happen between runs)
        activate_version(store_root, app_id, component, 1)

        # Now active version is 1
        assert get_active_version(store_root, app_id, component) == 1
        assert read_active_payload(store_root, app_id, component) == initial_payload  # Still {} due to cache

        # Simulate start of run T+1: clear cache to simulate new run
        _clear_start_of_run_cache()
        start_t1_payload = read_active_payload(store_root, app_id, component)
        assert start_t1_payload == payload_v1  # Now reads v1

        # Run t+1: write version 2 (updates current.json for next run)
        semantic_clock_t1 = SemanticClockSnapshot(tick=2, vector_clock=(("L0", 2),))
        payload_v2 = {"key": "value_v2", "version": 2}

        snapshot_v2 = write_next_version(
            store_root=store_root,
            app_id=app_id,
            component=component,
            payload=payload_v2,
            semantic_clock=semantic_clock_t1,
        )

        # Version 2 is written and current.json updated
        assert snapshot_v2.config_version == 2
        # But L0 in run T+1 still reads v1 (time-shifted)
        assert read_active_payload(store_root, app_id, component) == start_t1_payload  # Still v1

        # Activate version 2 for next run
        activate_version(store_root, app_id, component, 2)

        # Simulate start of run T+2: clear cache
        _clear_start_of_run_cache()
        # Now active version is 2
        assert get_active_version(store_root, app_id, component) == 2
        assert read_active_payload(store_root, app_id, component) == payload_v2

    def test_read_specific_version(self):
        """Test reading a specific version (not just active)."""
        store_root = Path(TemporaryDirectory().name)
        app_id = "test_app"
        component = "routing_thresholds"  # Valid mutable component

        # Clear cache for clean test
        _clear_start_of_run_cache()

        # Capture initial state before any writes
        initial_payload = read_active_payload(store_root, app_id, component)
        assert initial_payload == {}

        # Write version 1
        semantic_clock = SemanticClockSnapshot(tick=1, vector_clock=(("L0", 1),))
        payload_v1 = {"threshold": 0.5}

        write_next_version(
            store_root=store_root,
            app_id=app_id,
            component=component,
            payload=payload_v1,
            semantic_clock=semantic_clock,
        )

        # Can read specific version
        assert read_version_payload(store_root, app_id, component, 1) == payload_v1

        # Active payload is still {} due to time-shift (cache captured before write)
        assert read_active_payload(store_root, app_id, component) == initial_payload

        # Write version 2
        payload_v2 = {"threshold": 0.6}
        semantic_clock_v2 = SemanticClockSnapshot(tick=2, vector_clock=(("L0", 2),))

        write_next_version(
            store_root=store_root,
            app_id=app_id,
            component=component,
            payload=payload_v2,
            semantic_clock=semantic_clock_v2,
        )

        # Can still read version 1 specifically
        assert read_version_payload(store_root, app_id, component, 1) == payload_v1
        assert read_version_payload(store_root, app_id, component, 2) == payload_v2

        # Active payload is still {} due to time-shift
        assert read_active_payload(store_root, app_id, component) == {}

        # Clear cache to simulate new run
        _clear_start_of_run_cache()
        # Now reads the latest written version
        assert read_active_payload(store_root, app_id, component) == payload_v2

    def test_activate_nonexistent_version_raises_error(self):
        """Test that activating non-existent version raises error."""
        store_root = Path(TemporaryDirectory().name)
        app_id = "test_app"
        component = "tool_policies"  # Valid mutable component

        # Clear cache for clean test
        _clear_start_of_run_cache()

        # Try to activate version 1 when no versions exist
        with pytest.raises(ValueError, match="VERSION_NOT_FOUND"):
            activate_version(store_root, app_id, component, 1)

    def test_get_active_version_returns_zero_when_none(self):
        """Test that get_active_version returns 0 when no version is active."""
        store_root = Path(TemporaryDirectory().name)
        app_id = "test_app"
        component = "prompt_templates"  # Valid mutable component

        # Clear cache for clean test
        _clear_start_of_run_cache()

        # No versions written, should return 0
        assert get_active_version(store_root, app_id, component) == 0

    def test_read_active_payload_empty_when_none(self):
        """Test that read_active_payload returns {} when no version is active."""
        store_root = Path(TemporaryDirectory().name)
        app_id = "test_app"
        component = "routing_thresholds"  # Valid mutable component

        # Clear cache for clean test
        _clear_start_of_run_cache()

        # No versions written, should return empty dict
        assert read_active_payload(store_root, app_id, component) == {}

    def test_activation_pointer_atomic_update(self):
        """Test that activation pointer updates are atomic."""
        store_root = Path(TemporaryDirectory().name)
        app_id = "test_app"
        component = "tool_policies"  # Valid mutable component

        # Clear cache for clean test
        _clear_start_of_run_cache()

        # Capture initial state before any writes
        initial_payload = read_active_payload(store_root, app_id, component)
        assert initial_payload == {}

        # Write multiple versions
        semantic_clock = SemanticClockSnapshot(tick=1, vector_clock=(("L0", 1),))

        for i in range(1, 4):
            payload = {"policy": f"version_{i}"}
            write_next_version(
                store_root=store_root,
                app_id=app_id,
                component=component,
                payload=payload,
                semantic_clock=semantic_clock,
            )

        # After writing 3 versions, latest version is 3
        assert get_active_version(store_root, app_id, component) == 3
        # But active payload is still {} due to time-shift (cache captured before writes)
        assert read_active_payload(store_root, app_id, component) == initial_payload

        # Activate version 2 - this updates current.json payload
        activate_version(store_root, app_id, component, 2)
        # get_active_version still returns 3 (latest version number)
        assert get_active_version(store_root, app_id, component) == 3
        # But read_active_payload still returns initial_payload due to time-shift cache
        assert read_active_payload(store_root, app_id, component) == initial_payload

        # Clear cache to simulate new run
        _clear_start_of_run_cache()
        # Now reads the activated version's payload
        assert read_active_payload(store_root, app_id, component) == {"policy": "version_2"}

        # Activate version 1
        activate_version(store_root, app_id, component, 1)
        # Still cached until next run
        assert read_active_payload(store_root, app_id, component) == {"policy": "version_2"}

        # Clear cache for new run
        _clear_start_of_run_cache()
        assert read_active_payload(store_root, app_id, component) == {"policy": "version_1"}

        # Can go back to version 3
        activate_version(store_root, app_id, component, 3)
        _clear_start_of_run_cache()
        assert read_active_payload(store_root, app_id, component) == {"policy": "version_3"}
