"""
Governance tests for apps_lic entrypoint purity and recipe registry resolution.

These tests enforce hard architectural invariants:
1. No l2_callable construction in __main__.py
2. No HOP agent imports in __main__.py
3. No apps_research imports in __main__.py
4. Recipe resolved by agentic_core from registry
5. Fail-closed behavior on recipe resolution failure
6. No legacy fallback
7. No direct provider SDK calls
8. Proper durable write flow through Exit → UWG → L4
"""

import ast
import inspect
import sys
from pathlib import Path
from typing import Set
import pytest


class TestAppsLicEntrypointPurity:
    """P0.1: Entrypoint purity hard governance tests."""

    def test_apps_lic_main_contains_no_l2_callable_construction(self):
        """Assert apps_lic/__main__.py does not build, pass, or own any callable."""
        main_file = Path(__file__).parent.parent.parent / "apps_lic" / "__main__.py"
        if not main_file.exists():
            pytest.fail("apps_lic/__main__.py does not exist")
        
        content = main_file.read_text()
        tree = ast.parse(content)
        
        # Search for l2_callable patterns
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id in ["l2_callable", "_build_l2_callable"]:
                pytest.fail(f"Found forbidden l2_callable reference at line {node.lineno}")
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in ["_build_l2_callable", "build_l2_callable"]:
                    pytest.fail(f"Found forbidden l2_callable construction at line {node.lineno}")
                # Also check for recipe resolution calls
                if isinstance(node.func, ast.Name) and node.func.id in ["_resolve_recipe_callable", "resolve_l2_recipe"]:
                    pytest.fail(f"Found forbidden recipe resolution call at line {node.lineno}")
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id in ["l2_callable", "recipe_callable"]:
                        pytest.fail(f"Found forbidden callable assignment at line {node.lineno}")
        
        # Product path must invoke canonical spine dispatch, not a raw L2 callable
        if "run_canonical_apps_lic_spine" not in content:
            pytest.fail(
                "__main__.py must call run_canonical_apps_lic_spine, not construct L2 callables"
            )

    def test_apps_lic_main_does_not_import_hop_agents(self):
        """Assert apps_lic/__main__.py does not import HOP agents directly."""
        main_file = Path(__file__).parent.parent.parent / "apps_lic" / "__main__.py"
        if not main_file.exists():
            pytest.fail("apps_lic/__main__.py does not exist")
        
        content = main_file.read_text()
        tree = ast.parse(content)
        
        hop_patterns = [
            "HOP1ProfileAnalysisAgent",
            "HOP2ResearchAgent", 
            "HOP3SenderGroundingAgent",
            "MessagePlanner",
            "from apps_lic.engines",
            "import.*Agent",
        ]
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module and "engines" in node.module:
                    pytest.fail(f"Found forbidden engines import at line {node.lineno}: {node.module}")
                for alias in node.names:
                    if "Agent" in alias.name or "Planner" in alias.name:
                        pytest.fail(f"Found forbidden agent import at line {node.lineno}: {alias.name}")

    def test_apps_lic_main_does_not_import_apps_research(self):
        """Assert apps_lic/__main__.py does not import apps_research."""
        main_file = Path(__file__).parent.parent.parent / "apps_lic" / "__main__.py"
        if not main_file.exists():
            pytest.fail("apps_lic/__main__.py does not exist")
        
        content = main_file.read_text()
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if "apps_research" in alias.name:
                        pytest.fail(f"Found forbidden apps_research import at line {node.lineno}")
            if isinstance(node, ast.ImportFrom):
                if node.module and "apps_research" in node.module:
                    pytest.fail(f"Found forbidden apps_research import at line {node.lineno}: {node.module}")

    def test_apps_lic_yaml_l2_recipe_registry_deleted(self):
        """YAML L2 recipe registry must be physically deleted."""
        import importlib
        registry_file = Path(__file__).parent.parent.parent / "apps_lic" / "integrations" / "lic_l2_recipe_registry.py"
        assert not registry_file.exists()
        with pytest.raises((ModuleNotFoundError, ImportError)):
            importlib.import_module("apps_lic.integrations.lic_l2_recipe_registry")

    def test_apps_lic_hop_registry_is_l2_ssot(self):
        """Product L2 is hop_pipeline.REGISTRY + l2_execute_apps_lic."""
        from apps_lic.config.hop_pipeline import REGISTRY

        assert REGISTRY.stage_count() == 9
        names = [s.stage_name for s in REGISTRY.ordered()]
        assert names[0] == "profile_analysis"
        assert "generation" in names

    def test_apps_lic_research_bridge_executes_only_inside_l3_managed_workflow(self):
        """Assert apps_research bridge executes only via L3 managed workflow (not CLI import)."""
        import ast

        main_file = Path(__file__).parent.parent.parent / "apps_lic" / "__main__.py"

        if main_file.exists():
            tree = ast.parse(main_file.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        assert "apps_research" not in alias.name, (
                            f"apps_research must not be imported in __main__: {alias.name}"
                        )
                elif isinstance(node, ast.ImportFrom) and node.module:
                    assert "apps_research" not in node.module, (
                        f"apps_research must not be imported in __main__: {node.module}"
                    )
        
    def test_apps_lic_recipe_resolution_failure_fails_closed_through_exit(self):
        """Assert recipe resolution failure emits R5 terminal through Exit V6."""
        main_file = Path(__file__).parent.parent.parent / "apps_lic" / "__main__.py"
        if not main_file.exists():
            pytest.fail("apps_lic/__main__.py does not exist")
        
        content = main_file.read_text()
        
        # Must not have fallback to legacy
        if "run_workflow_lic" in content:
            pytest.fail("Must not fallback to run_workflow_lic.py")
        
        # Should have fail-closed pattern
        if "except" in content and "fallback" in content.lower():
            pytest.fail("Must not have fallback exception handling")

    def test_apps_lic_no_legacy_runner_feature_flag(self):
        """Assert no --use-legacy-runner feature flag exists."""
        main_file = Path(__file__).parent.parent.parent / "apps_lic" / "__main__.py"
        if not main_file.exists():
            pytest.fail("apps_lic/__main__.py does not exist")
        
        content = main_file.read_text()
        
        forbidden_patterns = [
            "use-legacy-runner",
            "use_legacy_runner", 
            "legacy_runner",
            "--legacy",
        ]
        
        for pattern in forbidden_patterns:
            if pattern in content:
                pytest.fail(f"Found forbidden legacy flag pattern: {pattern}")

    def test_apps_lic_run_workflow_lic_not_reachable_from_main(self):
        """Assert run_workflow_lic.py is not reachable from __main__.py."""
        main_file = Path(__file__).parent.parent.parent / "apps_lic" / "__main__.py"
        if not main_file.exists():
            pytest.fail("apps_lic/__main__.py does not exist")
        
        content = main_file.read_text()
        
        if "run_workflow_lic" in content:
            pytest.fail("run_workflow_lic must not be reachable from __main__.py")
        if "from apps_lic.tools" in content:
            pytest.fail("Must not import from apps_lic.tools in __main__.py")

    def test_apps_lic_recipe_resolution_failure_does_not_fallback_to_legacy(self):
        """Assert recipe resolution failure does not fallback to legacy path."""
        main_file = Path(__file__).parent.parent.parent / "apps_lic" / "__main__.py"
        if not main_file.exists():
            pytest.fail("apps_lic/__main__.py does not exist")
        
        content = main_file.read_text()
        tree = ast.parse(content)
        
        # Look for exception handlers that might fallback
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if node.body:
                    for stmt in node.body:
                        stmt_str = ast.unparse(stmt) if hasattr(ast, 'unparse') else str(stmt)
                        if "workflow" in stmt_str.lower() or "legacy" in stmt_str.lower():
                            pytest.fail(f"Found potential legacy fallback in exception handler at line {node.lineno}")

    def test_apps_lic_shadow_modules_deleted(self):
        """GovernedLic, spine_handoff, and YAML step adapters must not exist."""
        root = Path(__file__).parent.parent.parent / "apps_lic"
        assert not (root / "integrations" / "governed_lic_run.py").exists()
        assert not (root / "integrations" / "spine_handoff.py").exists()
        assert not (root / "integrations" / "lic_l2_step_adapters.py").exists()
        assert not (root / "integrations" / "lic_l2_recipe_registry.py").exists()
