"""
Contract tests for decorator canonical locations and backward-compat shims.

Architecture (after layer inversion fix):
    CANONICAL (SSOT):
        - agentic_core/base_agents/decorators.py  (standard_heal, HEAL_RESULT_SCHEMA)
        - agentic_core/base_agents/timeout_decorator.py  (timeout)

    BACKWARD-COMPAT SHIMS:
        - agentic_core/L5_safety/utils/decorators_util.py  (re-exports from base_agents)
        - agentic_core/L0_maintenance/utils/timeout_decorator_util.py  (re-exports from base_agents)

These tests verify:
    1. Canonical modules export required symbols
    2. Shims re-export the exact same objects (identity check)
    3. No agentic_core module imports from shim locations (enforcement)
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[4]

pytestmark = pytest.mark.unit_min_deps


class TestCanonicalDecoratorsContract:
    """Verify base_agents.decorators is the canonical SSOT."""

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

    def test_dunder_all_matches_exports(self) -> None:
        import agentic_core.base_agents.decorators as mod

        assert hasattr(mod, "__all__")
        for name in mod.__all__:
            assert hasattr(mod, name), f"__all__ lists '{name}' but it is not exported"


class TestCanonicalTimeoutContract:
    """Verify base_agents.timeout_decorator is the canonical SSOT."""

    def test_timeout_importable(self) -> None:
        from agentic_core.base_agents.timeout_decorator import timeout

        assert callable(timeout)

    def test_timeout_returns_decorator(self) -> None:
        from agentic_core.base_agents.timeout_decorator import timeout

        decorator = timeout(30)
        assert callable(decorator)

    def test_timeout_decorator_is_passthrough(self) -> None:
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


class TestBackwardCompatShimIdentity:
    """Verify shims re-export the exact same objects from canonical locations."""

    def test_l5_shim_standard_heal_is_canonical(self) -> None:
        """L5 shim must re-export base_agents.decorators.standard_heal."""
        from agentic_core.base_agents.decorators import standard_heal as canonical
        from agentic_core.L5_safety.utils.decorators_util import standard_heal as shim

        assert shim is canonical, "L5 shim must re-export canonical object"

    def test_l5_shim_heal_result_schema_is_canonical(self) -> None:
        from agentic_core.base_agents.decorators import HEAL_RESULT_SCHEMA as canonical
        from agentic_core.L5_safety.utils.decorators_util import (
            HEAL_RESULT_SCHEMA as shim,
        )

        assert shim is canonical

    def test_l0_shim_timeout_is_canonical(self) -> None:
        """L0 shim must re-export base_agents.timeout_decorator.timeout."""
        from agentic_core.base_agents.timeout_decorator import timeout as canonical
        from agentic_core.L0_maintenance.utils.timeout_decorator_util import (
            timeout as shim,
        )

        assert shim is canonical, "L0 shim must re-export canonical object"


class TestNoShimImportsEnforcement:
    """AST enforcement: no agentic_core module may import from shim locations."""

    SHIM_FILES = {"decorators_util.py", "timeout_decorator_util.py"}
    FORBIDDEN_IMPORTS = [
        "agentic_core.L5_safety.utils.decorators_util",
        "agentic_core.L0_maintenance.utils.timeout_decorator_util",
    ]

    def test_no_imports_from_l5_decorators_shim(self) -> None:
        """No agentic_core module may import from L5 decorators shim."""
        violations = self._find_forbidden_imports()
        assert not violations, (
            f"Found {len(violations)} forbidden imports from shim locations:\n"
            + "\n".join(f"  {v}" for v in violations[:20])
        )

    def _find_forbidden_imports(self) -> list[str]:
        violations = []
        agentic_core = ROOT / "agentic_core"

        for py_file in agentic_core.rglob("*.py"):
            if py_file.name in self.SHIM_FILES:
                continue

            try:
                source = py_file.read_text(encoding="utf-8")
                tree = ast.parse(source)
            except (SyntaxError, UnicodeDecodeError):
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    for forbidden in self.FORBIDDEN_IMPORTS:
                        if node.module == forbidden or node.module.startswith(
                            forbidden + ".",
                        ):
                            rel_path = py_file.relative_to(ROOT)
                            violations.append(
                                f"{rel_path}:{node.lineno} imports from {node.module}",
                            )

        return violations


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
