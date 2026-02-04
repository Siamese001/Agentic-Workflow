"""
Deterministic Behavioral Test Harness.

v3.0: All behavioral/golden tests MUST use this fixture to ensure
deterministic, reproducible outputs.

This module provides:
1. Frozen timestamps (datetime.utcnow() returns 2026-01-01T00:00:00Z)
2. Deterministic UUID sequence (uuid.uuid4() returns predictable values)
3. Volatile field stripping for JSON comparison

Usage:
    def test_my_agent(deterministic_harness):
        with deterministic_harness:
            result = my_agent.execute(input)
            clean = deterministic_harness.strip_volatile(result)
            assert clean == expected_golden
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from typing import Any, List
from pathlib import Path
import uuid


# Frozen timestamp for all tests
FROZEN_TIMESTAMP = datetime(2026, 1, 1, 0, 0, 0)
FROZEN_TIMESTAMP_ISO = "2026-01-01T00:00:00Z"

# Deterministic UUID sequence
UUID_SEQUENCE = [
    "00000000-0000-0000-0000-000000000001",
    "00000000-0000-0000-0000-000000000002",
    "00000000-0000-0000-0000-000000000003",
    "00000000-0000-0000-0000-000000000004",
    "00000000-0000-0000-0000-000000000005",
    "00000000-0000-0000-0000-000000000006",
    "00000000-0000-0000-0000-000000000007",
    "00000000-0000-0000-0000-000000000008",
    "00000000-0000-0000-0000-000000000009",
    "00000000-0000-0000-0000-000000000010",
]

# Fields to strip from output before comparison
VOLATILE_FIELDS = [
    "created_at",
    "updated_at",
    "timestamp",
    "elapsed_time",
    "execution_time",
    "duration",
    "trace_id",
    "request_id",
    "session_id",
    "correlation_id",
    "span_id",
    "start_time",
    "end_time",
]


class DeterministicUUIDGenerator:
    """Generates UUIDs in a deterministic sequence."""

    def __init__(self):
        self.index = 0

    def __call__(self) -> uuid.UUID:
        if self.index >= len(UUID_SEQUENCE):
            self.index = 0  # Wrap around
        result = uuid.UUID(UUID_SEQUENCE[self.index])
        self.index += 1
        return result

    def reset(self):
        self.index = 0


def strip_volatile_fields(obj: Any, fields: List[str] = None) -> Any:
    """
    Recursively strip volatile fields from a dictionary or list.

    Args:
        obj: The object to strip fields from
        fields: List of field names to strip (defaults to VOLATILE_FIELDS)

    Returns:
        A copy of the object with volatile fields removed
    """
    if fields is None:
        fields = VOLATILE_FIELDS

    if isinstance(obj, dict):
        return {k: strip_volatile_fields(v, fields) for k, v in obj.items() if k not in fields}
    elif isinstance(obj, list):
        return [strip_volatile_fields(item, fields) for item in obj]
    else:
        return obj


class DeterministicContext:
    """
    Context manager that provides a deterministic test environment.

    Freezes time and seeds UUID generation for reproducible tests.
    """

    def __init__(self):
        self.uuid_generator = DeterministicUUIDGenerator()
        self.patches = []
        self._original_datetime = None

    def __enter__(self):
        # Create a mock datetime class
        mock_datetime = MagicMock(wraps=datetime)
        mock_datetime.utcnow.return_value = FROZEN_TIMESTAMP
        mock_datetime.now.return_value = FROZEN_TIMESTAMP

        # Preserve the ability to create datetime objects
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        # Patch datetime in common locations
        datetime_modules = [
            "datetime.datetime",
        ]

        for module in datetime_modules:
            try:
                p = patch(module, mock_datetime)
                p.start()
                self.patches.append(p)
            except Exception:
                pass

        # Seed UUID
        uuid_patch = patch("uuid.uuid4", self.uuid_generator)
        uuid_patch.start()
        self.patches.append(uuid_patch)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for p in reversed(self.patches):
            try:
                p.stop()
            except Exception:
                pass
        self.uuid_generator.reset()
        return False

    def strip_volatile(self, obj: Any) -> Any:
        """Strip volatile fields from output for comparison."""
        return strip_volatile_fields(obj)

    @property
    def frozen_timestamp(self) -> datetime:
        return FROZEN_TIMESTAMP

    @property
    def frozen_timestamp_iso(self) -> str:
        return FROZEN_TIMESTAMP_ISO

    def get_next_uuid(self) -> str:
        """Get the next UUID in the sequence without consuming it."""
        idx = self.uuid_generator.index
        if idx >= len(UUID_SEQUENCE):
            idx = 0
        return UUID_SEQUENCE[idx]


@pytest.fixture
def deterministic_harness():
    """
    Pytest fixture that provides a deterministic test environment.

    Usage:
        def test_my_agent(deterministic_harness):
            with deterministic_harness:
                result = my_agent.execute(input)
                # result will have frozen timestamps and deterministic UUIDs

    The harness:
    1. Freezes datetime.utcnow() to 2026-01-01T00:00:00Z
    2. Seeds uuid.uuid4() to return deterministic sequence
    3. Provides strip_volatile() for output comparison
    """
    return DeterministicContext()


@pytest.fixture
def golden_snapshot_dir():
    """Fixture that provides the path to the golden snapshots directory."""
    return Path(__file__).parent.parent / "snapshots"


@pytest.fixture
def standard_test_input():
    """Standard test input for behavioral tests."""
    return {"task": "test_operation", "context": {"layer": "L5", "mode": "test"}}
