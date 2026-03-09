"""
Contract tests for decorator canonical locations and backward-compat shims.

Architecture (after layer inversion fix):
    CANONICAL (SSOT):
        - agentic_core/base_agents/decorators.py  (standard_heal, HEAL_RESULT_SCHEMA)
        - agentic_core/base_agents/timeout_decorator.py  (timeout)

    BACKWARD-COMPAT SHIMS:
        - agentic_core/L5_safety/utils/decorators_util.py  (re-exports from base_agents)
        - agentic_core/L0_routing/utils/timeout_decorator_util.py  (re-exports from base_agents)

These tests verify:
    1. Canonical modules export required symbols
    2. Shims re-export the exact same objects (identity check)
    3. No agentic_core module imports from shim locations (enforcement)
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
)

ROOT = Path(__file__).resolve().parents[2]

pytestmark = pytest.mark.unit_min_deps


class TestCanonicalDecoratorsContract:
    """Verify base_agents.decorators is the canonical SSOT."""

    def test_standard_heal_importable(self) -> None:
        from agentic_core.utils.decorators_base_util import standard_heal

        assert callable(standard_heal)

    def test_standard_heal_async_importable(self) -> None:
        from agentic_core.utils.decorators_base_util import standard_heal_async

        assert callable(standard_heal_async)

    def test_heal_result_schema_importable(self) -> None:
        from agentic_core.utils.decorators_base_util import HEAL_RESULT_SCHEMA

        assert isinstance(HEAL_RESULT_SCHEMA, dict)
        assert "violations_found" in HEAL_RESULT_SCHEMA
        assert "violations_fixed" in HEAL_RESULT_SCHEMA
        assert "status" in HEAL_RESULT_SCHEMA

    def test_dunder_all_matches_exports(self) -> None:
        import agentic_core.utils.decorators_base_util as mod

        assert hasattr(mod, "__all__")
        for name in mod.__all__:
            assert hasattr(mod, name), f"__all__ lists '{name}' but it is not exported"


class TestCanonicalTimeoutContract:
    """Verify base_agents.timeout_decorator is the canonical SSOT."""

    def test_timeout_importable(self) -> None:
        from agentic_core.utils.timeout_decorator_util import timeout

        assert callable(timeout)

    def test_timeout_returns_decorator(self) -> None:
        from agentic_core.utils.timeout_decorator_util import timeout

        decorator = timeout(30)
        assert callable(decorator)

    def test_timeout_decorator_wraps_function(self) -> None:
        from agentic_core.utils.timeout_decorator_util import timeout

        def sample_func():
            return 42

        decorated = timeout(10)(sample_func)
        # Decorated function should be callable and return same result
        assert callable(decorated)
        assert decorated() == 42

    def test_dunder_all_matches_exports(self) -> None:
        import agentic_core.utils.timeout_decorator_util as mod

        assert hasattr(mod, "__all__")
        for name in mod.__all__:
            assert hasattr(mod, name), f"__all__ lists '{name}' but it is not exported"


class TestBackwardCompatShimIdentity:
    """Verify shims re-export the exact same objects from canonical locations."""

    def test_l5_shim_standard_heal_is_canonical(self) -> None:
        """L5 shim must re-export base_agents.decorators.standard_heal."""
        from agentic_core.L5_safety.utils.decorators_util import standard_heal as shim
        from agentic_core.utils.decorators_base_util import standard_heal as canonical

        assert shim is canonical, "L5 shim must re-export canonical object"

    def test_l5_shim_heal_result_schema_is_canonical(self) -> None:
        from agentic_core.L5_safety.utils.decorators_util import (
            HEAL_RESULT_SCHEMA as shim,
        )
        from agentic_core.utils.decorators_base_util import HEAL_RESULT_SCHEMA as canonical

        assert shim is canonical

    def test_l0_shim_timeout_is_canonical(self) -> None:
        """L0 shim must re-export base_agents.timeout_decorator.timeout."""
        from agentic_core.L0_routing.utils.timeout_decorator_util import (
            timeout as shim,
        )
        from agentic_core.utils.timeout_decorator_util import timeout as canonical

        assert shim is canonical, "L0 shim must re-export canonical object"


class TestNoShimImportsEnforcement:
    """AST enforcement: no agentic_core module may import from shim locations."""

    SHIM_FILES = {"decorators_util.py", "timeout_decorator_util.py"}
    FORBIDDEN_IMPORTS = [
        "agentic_core.L5_safety.utils.decorators_util",
        "agentic_core.L0_routing.utils.timeout_decorator_util",
    ]

    def test_no_imports_from_shim_locations(self) -> None:
        """No agentic_core module (except shims) may import from shim locations."""
        violations = self._find_forbidden_imports()
        assert not violations, (
            f"Found {len(violations)} forbidden imports from shim locations:\n"
            + "\n".join(f"  {v}" for v in violations[:20])
        )

    def _find_forbidden_imports(self) -> list[str]:
        violations = []
        agentic_core = ROOT / AGENTIC_CORE_DIR

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


class TestBaseAgentsDecoratorImports:
    """AST enforcement: base_agents/decorators.py and timeout_decorator.py must not import from shim locations."""

    DECORATOR_FILES = {"decorators.py", "timeout_decorator.py"}
    FORBIDDEN_SHIM_IMPORTS = [
        "agentic_core.L5_safety.utils.decorators_util",
        "agentic_core.L0_routing.utils.timeout_decorator_util",
    ]

    def test_base_agents_decorators_no_shim_imports(self) -> None:
        """base_agents decorator modules must not import from their shim locations (no circular deps)."""
        violations = []
        base_agents = ROOT / AGENTIC_CORE_DIR / "base_agents"

        for py_file in base_agents.glob("*.py"):
            if py_file.name not in self.DECORATOR_FILES:
                continue

            try:
                source = py_file.read_text(encoding="utf-8")
                tree = ast.parse(source)
            except (SyntaxError, UnicodeDecodeError):
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    for forbidden in self.FORBIDDEN_SHIM_IMPORTS:
                        if node.module == forbidden or node.module.startswith(forbidden + "."):
                            violations.append(
                                f"{py_file.name}:{node.lineno} imports from {node.module}",
                            )

        assert not violations, (
            "base_agents decorator modules import from shim locations (layer inversion):\n"
            + "\n".join(f"  {v}" for v in violations)
        )


class TestShimAllowlist:
    """AST enforcement: shims must import ONLY from base_agents canonical locations."""

    DECORATORS_SHIM = ROOT / "agentic_core/L5_safety/utils/decorators_util.py"
    TIMEOUT_SHIM = ROOT / "agentic_core/L0_routing/utils/timeout_decorator_util.py"

    def test_decorators_shim_imports_only_base_agents(self) -> None:
        """decorators_util.py must import ONLY from utils.decorators_util (canonical)."""
        violations = self._check_shim_imports(
            self.DECORATORS_SHIM,
            allowed="agentic_core.utils.decorators_util",
        )
        assert not violations, "decorators_util.py imports from non-canonical locations:\n" + "\n".join(
            f"  {v}" for v in violations
        )

    def test_timeout_shim_imports_only_base_agents(self) -> None:
        """timeout_decorator_util.py must import ONLY from base_agents.timeout_decorator."""
        violations = self._check_shim_imports(
            self.TIMEOUT_SHIM,
            allowed="agentic_core.utils.timeout_decorator_util",
        )
        assert not violations, (
            "timeout_decorator_util.py imports from non-canonical locations:\n"
            + "\n".join(f"  {v}" for v in violations)
        )

    def _check_shim_imports(self, shim_path: Path, allowed: str) -> list[str]:
        """Check that shim imports ONLY from allowed module (plus __future__)."""
        violations = []
        try:
            source = shim_path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except (SyntaxError, UnicodeDecodeError, FileNotFoundError) as e:
            return [f"Cannot parse {shim_path.name}: {e}"]

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                if node.module == "__future__":
                    continue
                if node.module != allowed:
                    violations.append(
                        f"line {node.lineno}: imports from {node.module} (allowed: {allowed})",
                    )

        return violations


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
