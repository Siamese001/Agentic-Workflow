"""ADG-driven tests for L2_execution/enforcement/manifest_hash_validator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.enforcement.manifest_hash_validator import (
    ManifestHashError,
    REQUIRED_HASH_FIELDS,
)


class TestManifestHashError:
    def test_is_exception(self):
        assert issubclass(ManifestHashError, Exception)

    def test_raises(self):
        with pytest.raises(ManifestHashError):
            raise ManifestHashError("missing policy_hash")


class TestRequiredHashFields:
    def test_is_tuple(self):
        assert isinstance(REQUIRED_HASH_FIELDS, tuple)

    def test_has_four_fields(self):
        assert len(REQUIRED_HASH_FIELDS) == 4

    def test_contains_policy_hash(self):
        assert "policy_hash" in REQUIRED_HASH_FIELDS

    def test_contains_routing_hash(self):
        assert "routing_hash" in REQUIRED_HASH_FIELDS
