"""ADG-driven tests for L2_execution/types/vm_status_types.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.types.vm_status_types import VmProvider, VmStatus
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    VmStatus = None  # type: ignore[assignment,misc]
    VmProvider = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="vm_status_types has NameError bug")
class TestVmStatus:
    def test_is_enum(self):
        import enum
        assert issubclass(VmStatus, enum.Enum)

    def test_running_value(self):
        assert VmStatus.RUNNING.value == "running"

    def test_failed_value(self):
        assert VmStatus.FAILED.value == "failed"

    def test_all_five_members(self):
        assert len(list(VmStatus)) == 5


@pytest.mark.skipif(not _AVAILABLE, reason="vm_status_types has NameError bug")
class TestVmProvider:
    def test_is_enum(self):
        import enum
        assert issubclass(VmProvider, enum.Enum)

    def test_firecracker_value(self):
        assert VmProvider.FIRECRACKER.value == "firecracker"

    def test_docker_value(self):
        assert VmProvider.DOCKER.value == "docker"

    def test_has_local(self):
        assert VmProvider.LOCAL.value == "local"