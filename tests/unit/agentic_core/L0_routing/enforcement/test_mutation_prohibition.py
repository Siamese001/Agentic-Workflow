"""Runtime-hardened tests for protected-root mutation prohibition contracts."""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def enforcement_package():
    return pytest.importorskip("agentic_core.L0_routing.enforcement")


class TestMutationProhibitionContracts:
    def test_get_default_protected_root_policy_returns_value(self, enforcement_package):
        assert enforcement_package.get_default_protected_root_policy() is not None

    def test_enforce_protected_root_public_surface(self, enforcement_package):
        assert callable(enforcement_package.enforce_protected_root)

    def test_source_mutation_blocked_initialization(self, enforcement_package):
        assert isinstance(enforcement_package.SourceMutationBlocked(), Exception)

    def test_protected_root_block_event_initialization(self, enforcement_package):
        instance = enforcement_package.ProtectedRootBlockEvent(
            "2023-01-01T00:00:00Z",
            str(Path("/test/path")),
            "root123",
            "caller",
        )

        assert instance is not None
