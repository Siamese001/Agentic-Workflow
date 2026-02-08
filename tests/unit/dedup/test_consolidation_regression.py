"""
Regression tests for Phase 3 agent consolidations.

AST-based structural validation (no runtime imports of agents needed).
Validates:
- Cluster 6: CodeFormatterAgent + UnusedCleanupAgent share CodeToolRunnerCapability
- Cluster 7: ContentStrategyAgent is retired as deprecation shim
- All consolidated agents preserve their MRO, methods, and import paths
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent


def _parse_class_ast(filepath: Path) -> dict:
    """Parse a file and extract the first class's bases, methods, and body info."""
    source = filepath.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(filepath))
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            bases = []
            for base in node.bases:
                if isinstance(base, ast.Name):
                    bases.append(base.id)
                elif isinstance(base, ast.Attribute):
                    bases.append(base.attr)
            methods = [
                item.name
                for item in node.body
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]
            # Check for deprecation warning in __post_init__
            has_deprecation_warning = False
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__post_init__":
                    for sub in ast.walk(item):
                        if isinstance(sub, ast.Call):
                            func = sub.func
                            if isinstance(func, ast.Attribute) and func.attr == "warn":
                                has_deprecation_warning = True
                            elif isinstance(func, ast.Name) and func.id == "warn":
                                has_deprecation_warning = True
            return {
                "class_name": node.name,
                "bases": bases,
                "methods": methods,
                "has_deprecation_warning": has_deprecation_warning,
            }
    return {}


def _extract_imports(filepath: Path) -> list[str]:
    """Extract all import-from module paths from a file."""
    source = filepath.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(filepath))
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
    return imports


# ---------------------------------------------------------------------------
# Cluster 6: CodeToolRunnerCapability extraction (AST-based)
# ---------------------------------------------------------------------------

CODE_FORMATTER_PATH = PROJECT_ROOT / "agentic_core" / "L5_safety" / "reasoning" / "CodeFormatterAgent.py"
UNUSED_CLEANUP_PATH = PROJECT_ROOT / "agentic_core" / "L5_safety" / "reasoning" / "UnusedCleanupAgent.py"
CODE_TOOL_RUNNER_PATH = PROJECT_ROOT / "agentic_core" / "L5_safety" / "reasoning" / "code_tool_runner_core.py"


class TestCodeToolRunnerMixinExtraction:
    """Verify CodeFormatterAgent and UnusedCleanupAgent share CodeToolRunnerCapability."""

    def test_capability_file_exists(self):
        """CodeToolRunnerCapability source file must exist."""
        assert CODE_TOOL_RUNNER_PATH.exists(), f"Missing: {CODE_TOOL_RUNNER_PATH}"

    def test_capability_class_defined(self):
        """code_tool_runner_core must define CodeToolRunnerCapability class."""
        info = _parse_class_ast(CODE_TOOL_RUNNER_PATH)
        assert info, "No class found in code_tool_runner_core.py"

    def test_capability_is_pure_mixin(self):
        """CodeToolRunnerCapability must NOT inherit from SovereignBaseAgent."""
        info = _parse_class_ast(CODE_TOOL_RUNNER_PATH)
        assert "SovereignBaseAgent" not in info["bases"], (
            "Capability must be agent-agnostic (pure mixin) to avoid Diamond Problem"
        )

    @pytest.mark.parametrize("filepath,agent_name", [
        (CODE_FORMATTER_PATH, "CodeFormatterAgent"),
        (UNUSED_CLEANUP_PATH, "UnusedCleanupAgent"),
    ])
    def test_agent_inherits_capability(self, filepath, agent_name):
        """Agent must list CodeToolRunnerCapability in its bases."""
        assert filepath.exists(), f"Missing: {filepath}"
        info = _parse_class_ast(filepath)
        assert info, f"No class found in {filepath.name}"
        assert "CodeToolRunnerCapability" in info["bases"], (
            f"{agent_name} must inherit from CodeToolRunnerCapability, got: {info['bases']}"
        )

    @pytest.mark.parametrize("filepath,agent_name", [
        (CODE_FORMATTER_PATH, "CodeFormatterAgent"),
        (UNUSED_CLEANUP_PATH, "UnusedCleanupAgent"),
    ])
    def test_agent_preserves_sovereign_base(self, filepath, agent_name):
        """Agent must still have SovereignBaseAgent in its base chain."""
        info = _parse_class_ast(filepath)
        assert "SovereignBaseAgent" in info["bases"], (
            f"{agent_name} must inherit SovereignBaseAgent, got: {info['bases']}"
        )

    @pytest.mark.parametrize("filepath,agent_name", [
        (CODE_FORMATTER_PATH, "CodeFormatterAgent"),
        (UNUSED_CLEANUP_PATH, "UnusedCleanupAgent"),
    ])
    def test_capability_precedes_sovereign_base(self, filepath, agent_name):
        """CodeToolRunnerCapability must precede SovereignBaseAgent in MRO to avoid diamond."""
        info = _parse_class_ast(filepath)
        bases = info["bases"]
        if "CodeToolRunnerCapability" in bases and "SovereignBaseAgent" in bases:
            cap_idx = bases.index("CodeToolRunnerCapability")
            sov_idx = bases.index("SovereignBaseAgent")
            assert cap_idx < sov_idx, (
                f"{agent_name}: CodeToolRunnerCapability ({cap_idx}) must precede "
                f"SovereignBaseAgent ({sov_idx}) in MRO"
            )

    @pytest.mark.parametrize("filepath,agent_name", [
        (CODE_FORMATTER_PATH, "CodeFormatterAgent"),
        (UNUSED_CLEANUP_PATH, "UnusedCleanupAgent"),
    ])
    def test_agent_has_execute(self, filepath, agent_name):
        """Agent must define execute method."""
        info = _parse_class_ast(filepath)
        assert "execute" in info["methods"], (
            f"{agent_name} must define execute(), got methods: {info['methods']}"
        )

    def test_backward_compat_alias_in_source(self):
        """code_tool_runner_core must define CodeToolRunnerMixin alias."""
        source = CODE_TOOL_RUNNER_PATH.read_text(encoding="utf-8")
        assert "CodeToolRunnerMixin" in source, (
            "Backward-compat alias CodeToolRunnerMixin missing from code_tool_runner_core.py"
        )


# ---------------------------------------------------------------------------
# Cluster 7: ContentStrategyAgent deprecation shim (AST-based)
# ---------------------------------------------------------------------------

CSA_REASONING_PATH = PROJECT_ROOT / "apps_rg" / "reasoning" / "ContentStrategyAgent.py"
CSA_ENGINES_PATH = PROJECT_ROOT / "apps_rg" / "engines" / "ContentStrategyAgent.py"


class TestContentStrategyAgentRetirement:
    """Verify ContentStrategyAgent is properly retired as a deprecation shim."""

    def test_reasoning_file_exists(self):
        """ContentStrategyAgent must exist in apps_rg/reasoning/."""
        assert CSA_REASONING_PATH.exists()

    def test_engines_shim_exists(self):
        """ContentStrategyAgent re-export shim must exist in apps_rg/engines/."""
        assert CSA_ENGINES_PATH.exists()

    def test_reasoning_inherits_rg_agent_base(self):
        """ContentStrategyAgent (reasoning) must inherit from RGAgentBase."""
        info = _parse_class_ast(CSA_REASONING_PATH)
        assert "RGAgentBase" in info["bases"], (
            f"ContentStrategyAgent must inherit RGAgentBase, got: {info['bases']}"
        )

    def test_reasoning_has_analyze_topic(self):
        """ContentStrategyAgent must retain analyze_topic for backward compat."""
        info = _parse_class_ast(CSA_REASONING_PATH)
        assert "analyze_topic" in info["methods"], (
            f"ContentStrategyAgent must have analyze_topic(), got: {info['methods']}"
        )

    def test_reasoning_emits_deprecation_warning(self):
        """ContentStrategyAgent.__post_init__ must call warnings.warn."""
        info = _parse_class_ast(CSA_REASONING_PATH)
        assert info["has_deprecation_warning"], (
            "ContentStrategyAgent.__post_init__ must emit DeprecationWarning"
        )

    def test_engines_shim_re_exports_from_reasoning(self):
        """Engines shim must import from apps_rg.reasoning.ContentStrategyAgent."""
        imports = _extract_imports(CSA_ENGINES_PATH)
        assert "apps_rg.reasoning.ContentStrategyAgent" in imports, (
            f"Engines shim must re-export from reasoning, got imports: {imports}"
        )

    def test_reasoning_has_post_init(self):
        """ContentStrategyAgent must define __post_init__ for deprecation warning."""
        info = _parse_class_ast(CSA_REASONING_PATH)
        assert "__post_init__" in info["methods"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
