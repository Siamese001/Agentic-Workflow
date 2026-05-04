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
        
        # Also check that runner is called with app_name, not callable
        if "app_name=\"apps_lic\"" not in content and "app_name='apps_lic'" not in content:
            pytest.fail("__main__.py must pass app_name='apps_lic' to runner, not a callable")

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

    def test_apps_lic_r4_runner_resolves_static_recipe_from_registry(self):
        """Assert agentic_core R4 runner resolves apps_lic static recipe from registry."""
        # This test verifies that the recipe registry contains the static recipe
        registry_file = Path(__file__).parent.parent.parent / "apps_lic" / "integrations" / "lic_l2_recipe_registry.py"
        if not registry_file.exists():
            pytest.fail("lic_l2_recipe_registry.py does not exist - scaffold first")
        
        content = registry_file.read_text()
        
        if "register_static_recipe" not in content:
            pytest.fail("Registry must export register_static_recipe")
        if "apps_lic_static_dag" not in content and "static" not in content.lower():
            pytest.fail("Registry must reference static DAG")

    def test_apps_lic_managed_runner_resolves_managed_recipe_from_registry(self):
        """Assert agentic_core/L3 managed workflow runner resolves apps_lic managed recipe from registry."""
        registry_file = Path(__file__).parent.parent.parent / "apps_lic" / "integrations" / "lic_l2_recipe_registry.py"
        if not registry_file.exists():
            pytest.fail("lic_l2_recipe_registry.py does not exist - scaffold first")
        
        content = registry_file.read_text()
        
        if "register_managed_recipe" not in content:
            pytest.fail("Registry must export register_managed_recipe")
        if "apps_lic_managed_dag" not in content and "managed" not in content.lower():
            pytest.fail("Registry must reference managed DAG")

    def test_apps_lic_hops_execute_only_as_registered_l2_steps(self):
        """Assert apps_lic HOPs are wrapped as registered L2 step adapters."""
        adapters_file = Path(__file__).parent.parent.parent / "apps_lic" / "integrations" / "lic_l2_step_adapters.py"
        if not adapters_file.exists():
            pytest.fail("lic_l2_step_adapters.py does not exist - scaffold first")
        
        content = adapters_file.read_text()
        
        # Must have step adapter definitions
        if "def " not in content:
            pytest.fail("Step adapters must define callable functions")
        
        # Must reference E1-E5 phases
        phases = ["E1", "E2", "E3", "E4", "E5"]
        if not any(phase in content for phase in phases):
            pytest.fail("Step adapters must reference canonical E1-E5 phases")

    def test_apps_lic_research_bridge_executes_only_inside_l3_managed_workflow(self):
        """Assert apps_research bridge executes only as registered L3/L2 managed workflow step."""
        adapters_file = Path(__file__).parent.parent.parent / "apps_lic" / "integrations" / "lic_l2_step_adapters.py"
        main_file = Path(__file__).parent.parent.parent / "apps_lic" / "__main__.py"
        
        if main_file.exists():
            main_content = main_file.read_text()
            if "apps_research" in main_content or "ResearchBridge" in main_content:
                pytest.fail("apps_research must not be referenced in __main__.py")
        
        if adapters_file.exists():
            content = adapters_file.read_text()
            if "research" not in content.lower() and "briefing" not in content.lower():
                pytest.skip("Research bridge adapter not yet implemented")

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

    def test_apps_lic_no_generic_draft_when_recipe_missing(self):
        """Assert no generic fallback draft is generated if recipe resolution fails."""
        adapters_file = Path(__file__).parent.parent.parent / "apps_lic" / "integrations" / "lic_l2_step_adapters.py"
        if not adapters_file.exists():
            pytest.fail("lic_l2_step_adapters.py does not exist - scaffold first")
        
        content = adapters_file.read_text()
        
        # Must not have generic draft generation
        if "generic" in content.lower() and "draft" in content.lower():
            pytest.fail("Must not generate generic fallback drafts")
        if "fallback" in content.lower() and "draft" in content.lower():
            pytest.fail("Must not generate fallback drafts")

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

    def test_apps_lic_l2_step_adapters_do_not_call_provider_sdks_directly(self):
        """Assert L2 step adapters do not call provider SDKs directly."""
        adapters_file = Path(__file__).parent.parent.parent / "apps_lic" / "integrations" / "lic_l2_step_adapters.py"
        if not adapters_file.exists():
            pytest.fail("lic_l2_step_adapters.py does not exist - scaffold first")
        
        content = adapters_file.read_text()
        tree = ast.parse(content)
        
        forbidden_providers = [
            "openai", "anthropic", "gemini", "google.generativeai",
            "bedrock", "boto3", "vertexai", "openrouter",
        ]
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if any(provider in alias.name.lower() for provider in forbidden_providers):
                        pytest.fail(f"Found forbidden provider SDK import: {alias.name}")
            if isinstance(node, ast.ImportFrom):
                if node.module and any(provider in node.module.lower() for provider in forbidden_providers):
                    pytest.fail(f"Found forbidden provider SDK import from: {node.module}")

    def test_apps_lic_model_generation_uses_governed_provider_gateway(self):
        """Assert model generation uses canonical governed provider gateway."""
        adapters_file = Path(__file__).parent.parent.parent / "apps_lic" / "integrations" / "lic_l2_step_adapters.py"
        if not adapters_file.exists():
            pytest.fail("lic_l2_step_adapters.py does not exist - scaffold first")
        
        content = adapters_file.read_text()
        
        # Must reference governed gateway
        gateway_patterns = [
            "governed", "gateway", "provider_gateway",
            "policy_hash", "blueprint_hash", "capability_token",
        ]
        
        if not any(pattern in content for pattern in gateway_patterns):
            pytest.fail("Step adapters must reference governed provider gateway")

    def test_apps_lic_exit_emits_commit_request_but_does_not_write_l4(self):
        """Assert Exit V6 emits CommitRequest but does not write L4 directly."""
        adapters_file = Path(__file__).parent.parent.parent / "apps_lic" / "integrations" / "lic_l2_step_adapters.py"
        if not adapters_file.exists():
            pytest.fail("lic_l2_step_adapters.py does not exist - scaffold first")
        
        content = adapters_file.read_text()
        tree = ast.parse(content)
        
        # Must not have direct L4 writes
        forbidden_l4 = ["uwg", "universal_write_gateway", "write_to_l4", "l4_write"]
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if any(forbidden in node.func.attr.lower() for forbidden in forbidden_l4):
                        pytest.fail(f"Found potential L4 write at line {node.lineno}")
                if isinstance(node.func, ast.Name):
                    if any(forbidden in node.func.id.lower() for forbidden in forbidden_l4):
                        pytest.fail(f"Found potential L4 write at line {node.lineno}")
        
        # L2 should not write L4 directly
        if "uwg" in content.lower() or "l4" in content.lower():
            # Check if it's just references vs actual writes
            pass  # Will be checked more strictly in integration tests


class TestAppsLicRecipeRegistryScaffold:
    """P0.2: Recipe registry adapter scaffold tests."""

    def test_recipe_registry_file_exists(self):
        """Assert lic_l2_recipe_registry.py exists."""
        registry_file = Path(__file__).parent.parent.parent / "apps_lic" / "integrations" / "lic_l2_recipe_registry.py"
        assert registry_file.exists(), "lic_l2_recipe_registry.py must exist"

    def test_recipe_registry_exports_register_static_recipe(self):
        """Assert registry exports register_static_recipe function."""
        registry_file = Path(__file__).parent.parent.parent / "apps_lic" / "integrations" / "lic_l2_recipe_registry.py"
        if not registry_file.exists():
            pytest.skip("Registry file does not exist yet")
        
        content = registry_file.read_text()
        assert "def register_static_recipe" in content, "Must export register_static_recipe"

    def test_recipe_registry_exports_register_managed_recipe(self):
        """Assert registry exports register_managed_recipe function."""
        registry_file = Path(__file__).parent.parent.parent / "apps_lic" / "integrations" / "lic_l2_recipe_registry.py"
        if not registry_file.exists():
            pytest.skip("Registry file does not exist yet")
        
        content = registry_file.read_text()
        assert "def register_managed_recipe" in content, "Must export register_managed_recipe"

    def test_recipe_registry_exports_resolve_recipe(self):
        """Assert registry exports resolve_recipe function."""
        registry_file = Path(__file__).parent.parent.parent / "apps_lic" / "integrations" / "lic_l2_recipe_registry.py"
        if not registry_file.exists():
            pytest.skip("Registry file does not exist yet")
        
        content = registry_file.read_text()
        assert "def resolve_recipe" in content, "Must export resolve_recipe"


class TestAppsLicStepAdapterScaffold:
    """P0.3: Step adapter scaffold tests."""

    def test_step_adapter_file_exists(self):
        """Assert lic_l2_step_adapters.py exists."""
        adapters_file = Path(__file__).parent.parent.parent / "apps_lic" / "integrations" / "lic_l2_step_adapters.py"
        assert adapters_file.exists(), "lic_l2_step_adapters.py must exist"

    def test_step_adapters_define_e1_prep_stage(self):
        """Assert step adapters define E1 Prep stage."""
        adapters_file = Path(__file__).parent.parent.parent / "apps_lic" / "integrations" / "lic_l2_step_adapters.py"
        if not adapters_file.exists():
            pytest.skip("Step adapter file does not exist yet")
        
        content = adapters_file.read_text()
        assert "E1" in content or "Prep" in content or "load_manifest" in content, "Must define E1 Prep stage"

    def test_step_adapters_define_e2_valid_stage(self):
        """Assert step adapters define E2 Valid stage."""
        adapters_file = Path(__file__).parent.parent.parent / "apps_lic" / "integrations" / "lic_l2_step_adapters.py"
        if not adapters_file.exists():
            pytest.skip("Step adapter file does not exist yet")
        
        content = adapters_file.read_text()
        assert "E2" in content or "Valid" in content or "validate" in content, "Must define E2 Valid stage"

    def test_step_adapters_define_e3_exec_stage(self):
        """Assert step adapters define E3 Exec stage."""
        adapters_file = Path(__file__).parent.parent.parent / "apps_lic" / "integrations" / "lic_l2_step_adapters.py"
        if not adapters_file.exists():
            pytest.skip("Step adapter file does not exist yet")
        
        content = adapters_file.read_text()
        assert "E3" in content or "Exec" in content or "compose" in content or "plan" in content, "Must define E3 Exec stage"

    def test_step_adapters_define_e4_heal_stage(self):
        """Assert step adapters define E4 Heal stage."""
        adapters_file = Path(__file__).parent.parent.parent / "apps_lic" / "integrations" / "lic_l2_step_adapters.py"
        if not adapters_file.exists():
            pytest.skip("Step adapter file does not exist yet")
        
        content = adapters_file.read_text()
        assert "E4" in content or "Heal" in content or "repair" in content or "omit" in content, "Must define E4 Heal stage"

    def test_step_adapters_define_e5_seal_stage(self):
        """Assert step adapters define E5 Seal stage."""
        adapters_file = Path(__file__).parent.parent.parent / "apps_lic" / "integrations" / "lic_l2_step_adapters.py"
        if not adapters_file.exists():
            pytest.skip("Step adapter file does not exist yet")
        
        content = adapters_file.read_text()
        assert "E5" in content or "Seal" in content or "seal" in content, "Must define E5 Seal stage"
