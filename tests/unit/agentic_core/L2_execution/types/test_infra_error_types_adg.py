"""ADG-driven tests for L2_execution/types/infra_error_types.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.types.infra_error_types import InfrastructureDependencyError


class TestInfrastructureDependencyError:
    def test_is_runtime_error(self):
        assert issubclass(InfrastructureDependencyError, RuntimeError)

    def test_raises(self):
        with pytest.raises(InfrastructureDependencyError):
            raise InfrastructureDependencyError("Redis unavailable")

    def test_message_preserved(self):
        err = InfrastructureDependencyError("FAISS missing")
        assert "FAISS missing" in str(err)
