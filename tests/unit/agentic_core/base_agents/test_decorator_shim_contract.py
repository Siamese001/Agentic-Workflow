"""
Contract tests for base_agents decorator shim modules.

These tests verify that the shim re-export modules at
``agentic_core.base_agents.decorators`` and
``agentic_core.base_agents.timeout_decorator`` correctly resolve
to their canonical implementations.

Background (Issue #5):
    54 files import ``standard_heal`` from ``base_agents.decorators``
    67 files import ``timeout`` from ``base_agents.timeout_decorator``
    Neither module existed — they were phantom imports.
    Shim modules were created 2026-02-08 to resolve this.

Canonical sources:
    - agentic_core/L5_safety/utils/decorators_util.py  (standard_heal, HEAL_RESULT_SCHEMA)
    - agentic_core/L0_maintenance/utils/timeout_decorator_util.py  (timeout)
"""

from __future__ import annotations

import pytest


class TestDecoratorsShimContract:
    """Verify base_agents.decorators shim resolves to canonical implementation."""

    def test_standard_heal_importable(self) -> None:
        from agentic_core.base_agents.decorators import standard_heal

        assert callable(standard_heal)

    def test_standard_heal_async_importable(self) -> None:
        from agentic_core.base_agents.decorators import standard_heal_async

        assert callable(standard_heal_async)

    def test_heal_result_schema_importable(self) -> None:
        from agentic_core.base_agents.decorators import HEAL_RESULT_SCHEMA

        assert isinstance(HEAL_RESULT_SCHEMA, dict)
        assert "violations_found" in HEAL_RESULT_SCHEMA
        assert "violations_fixed" in HEAL_RESULT_SCHEMA
        assert "status" in HEAL_RESULT_SCHEMA

    def test_standard_heal_is_canonical_instance(self) -> None:
        """Shim must re-export the exact same function object, not a copy."""
        from agentic_core.base_agents.decorators import standard_heal as shim_heal
        from agentic_core.L5_safety.utils.decorators_util import (
            standard_heal as canonical_heal,
        )

        assert shim_heal is canonical_heal, "Shim must re-export the canonical function object, not a wrapper"

    def test_heal_result_schema_is_canonical_instance(self) -> None:
        from agentic_core.base_agents.decorators import (
            HEAL_RESULT_SCHEMA as shim_schema,
        )
        from agentic_core.L5_safety.utils.decorators_util import (
            HEAL_RESULT_SCHEMA as canonical_schema,
        )

        assert shim_schema is canonical_schema

    def test_dunder_all_matches_exports(self) -> None:
        import agentic_core.base_agents.decorators as mod

        assert hasattr(mod, "__all__")
        for name in mod.__all__:
            assert hasattr(mod, name), f"__all__ lists '{name}' but it is not exported"


class TestTimeoutDecoratorShimContract:
    """Verify base_agents.timeout_decorator shim resolves to canonical implementation."""

    def test_timeout_importable(self) -> None:
        from agentic_core.base_agents.timeout_decorator import timeout

        assert callable(timeout)

    def test_timeout_is_canonical_instance(self) -> None:
        """Shim must re-export the exact same function object."""
        from agentic_core.base_agents.timeout_decorator import timeout as shim_timeout
        from agentic_core.L0_maintenance.utils.timeout_decorator_util import (
            timeout as canonical_timeout,
        )

        assert shim_timeout is canonical_timeout

    def test_timeout_returns_decorator(self) -> None:
        """timeout(N) must return a callable decorator."""
        from agentic_core.base_agents.timeout_decorator import timeout

        decorator = timeout(30)
        assert callable(decorator)

    def test_timeout_decorator_is_passthrough(self) -> None:
        """Current impl is a placeholder — decorated func must be returned unchanged."""
        from agentic_core.base_agents.timeout_decorator import timeout

        def sample_func():
            return 42

        decorated = timeout(10)(sample_func)
        assert decorated is sample_func

    def test_dunder_all_matches_exports(self) -> None:
        import agentic_core.base_agents.timeout_decorator as mod

        assert hasattr(mod, "__all__")
        for name in mod.__all__:
            assert hasattr(mod, name), f"__all__ lists '{name}' but it is not exported"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
