"""W5 Ingress-Only Verification Tests — AG-RGGOV-W5 Compliance.

Validates that apps_rg/__main__.py is pure ingress shim with NO runtime authority.

Tests:
- No planner/router/orchestrator imports
- No prompt assembly/executor/provider calls
- No get_llm_gateway/SovereignLLMGateway usage
- No quarantine imports
- No core runtime contract emission
- Ingress payload types exist
- Main function delegates to AppIngressRunner
"""

import ast
import inspect
import sys
from pathlib import Path

import pytest


def _get_main_module_source() -> str:
    """Read apps_rg/__main__.py source."""
    main_path = Path(__file__).parent.parent.parent / "apps_rg" / "__main__.py"
    return main_path.read_text(encoding="utf-8")


def _parse_main_ast() -> ast.Module:
    """Parse apps_rg/__main__.py into AST."""
    source = _get_main_module_source()
    return ast.parse(source)


class TestW5IngressOnlyConstraints:
    """Verify hard constraints from AG-RGGOV-W5."""

    def test_no_planner_import(self) -> None:
        """AG-RGGOV-W5: NO planner imports allowed."""
        tree = _parse_main_ast()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import | ast.ImportFrom):
                names = []
                if isinstance(node, ast.Import):
                    names = [alias.name for alias in node.names]
                elif node.module:
                    names = [node.module]
                for name in names:
                    assert "planner" not in name.lower(), f"Forbidden planner import: {name}"

    def test_no_router_import(self) -> None:
        """AG-RGGOV-W5: NO router imports allowed."""
        tree = _parse_main_ast()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import | ast.ImportFrom):
                names = []
                if isinstance(node, ast.Import):
                    names = [alias.name for alias in node.names]
                elif node.module:
                    names = [node.module]
                for name in names:
                    assert "router" not in name.lower(), f"Forbidden router import: {name}"

    def test_no_orchestrator_import(self) -> None:
        """AG-RGGOV-W5: NO orchestrator imports allowed."""
        tree = _parse_main_ast()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import | ast.ImportFrom):
                names = []
                if isinstance(node, ast.Import):
                    names = [alias.name for alias in node.names]
                elif node.module:
                    names = [node.module]
                for name in names:
                    assert "orchestrator" not in name.lower(), f"Forbidden orchestrator import: {name}"

    def test_no_prompt_assembly_import(self) -> None:
        """AG-RGGOV-W5: NO prompt_assembly imports allowed."""
        tree = _parse_main_ast()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import | ast.ImportFrom):
                names = []
                if isinstance(node, ast.Import):
                    names = [alias.name for alias in node.names]
                elif node.module:
                    names = [node.module]
                for name in names:
                    assert "prompt_assembly" not in name.lower(), f"Forbidden prompt_assembly import: {name}"

    def test_no_executor_import(self) -> None:
        """AG-RGGOV-W5: NO executor imports allowed."""
        tree = _parse_main_ast()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import | ast.ImportFrom):
                names = []
                if isinstance(node, ast.Import):
                    names = [alias.name for alias in node.names]
                elif node.module:
                    names = [node.module]
                for name in names:
                    assert "executor" not in name.lower(), f"Forbidden executor import: {name}"

    def test_no_provider_call_patterns(self) -> None:
        """AG-RGGOV-W5: NO get_llm_gateway or SovereignLLMGateway usage."""
        source = _get_main_module_source()
        # Check for actual call patterns (not just docstring mentions)
        forbidden_calls = [
            "get_llm_gateway(",  # function call
            "SovereignLLMGateway(",  # class instantiation
            "SovereignBaseAgent(",  # class instantiation
            "= get_llm_gateway",  # assignment
        ]
        for pattern in forbidden_calls:
            assert pattern not in source, f"Forbidden provider call pattern: {pattern}"

    def test_no_quarantine_import(self) -> None:
        """AG-RGGOV-W5: NO quarantine module imports allowed."""
        tree = _parse_main_ast()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import | ast.ImportFrom):
                names = []
                if isinstance(node, ast.Import):
                    names = [alias.name for alias in node.names]
                elif node.module:
                    names = [node.module]
                for name in names:
                    assert "quarantine" not in name.lower(), f"Forbidden quarantine import: {name}"

    def test_apps_rg_runtime_symbols_not_in_main(self) -> None:
        """AG-RGGOV-W5: No apps_rg runtime symbols in __main__.py"""
        tree = _parse_main_ast()
        # Check for function definitions that would indicate runtime logic
        runtime_indicators = [
            "generate_", "run_", "execute_", "call_", "invoke_",
            "plan_", "route_", "assemble_", "emit_"
        ]
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                for indicator in runtime_indicators:
                    assert not node.name.startswith(indicator), (
                        f"Runtime indicator '{indicator}' found in function: {node.name}"
                    )


class TestW5IngressPayloadTypes:
    """Verify ingress payload dataclasses exist."""

    def test_apps_rg_ingress_payload_imported_from_core(self) -> None:
        """Verify AppsRgIngressPayload is imported from agentic_core, not locally defined."""
        source = _get_main_module_source()
        # Should import from core, not define locally
        assert "from agentic_core.runtime.contracts.apps_rg_ingress_payload import" in source
        assert "AppsRgIngressPayload" in source
        # Should NOT define class locally
        assert "class AppsRgIngressPayload" not in source
        # Should use the imported class
        assert "target_company" in source
        assert "target_role" in source

    def test_request_envelope_imported_from_core(self) -> None:
        """Verify RequestEnvelope is imported from agentic_core, not locally defined."""
        source = _get_main_module_source()
        # Should import from core
        assert "RequestEnvelope" in source
        # Should NOT define class locally
        assert "class RequestEnvelope" not in source
        # Should use the imported class
        assert "app_id" in source or "payload" in source


class TestW5IngressFlow:
    """Verify ingress flow delegates to agentic_core."""

    def test_main_function_delegates_to_runner(self) -> None:
        """Verify main() calls AppIngressRunner."""
        source = _get_main_module_source()
        assert "AppIngressRunner" in source, "AppIngressRunner import/delegation missing"
        assert "runner.run" in source or "runner.run(" in source, "runner.run() call missing"

    def test_no_direct_model_calls(self) -> None:
        """Verify no direct LLM model calls in main."""
        source = _get_main_module_source()
        # Check for actual import/call patterns, not generic words
        forbidden_patterns = [
            "import anthropic",  # direct import
            "import openai",  # direct import
            "llm_gateway(",  # function call
            "gateway.call(",  # method call
            "client.chat.completions.create(",  # API call
            "anthropic.Anthropic(",  # client instantiation
            "openai.OpenAI(",  # client instantiation
        ]
        source_lower = source.lower()
        for pattern in forbidden_patterns:
            assert pattern not in source_lower, f"Direct model call found: {pattern}"

    def test_cli_argument_parsing_exists(self) -> None:
        """Verify CLI argument parsing is present."""
        source = _get_main_module_source()
        assert "argparse" in source or "ArgumentParser" in source
        assert "--target-company" in source
        assert "--target-role" in source

    def test_interactive_wizard_option_exists(self) -> None:
        """Verify --interactive flag exists for wizard mode."""
        source = _get_main_module_source()
        assert "--interactive" in source or "interactive" in source.lower()


class TestW5FailClosedBehavior:
    """Verify fail-closed behavior when runner unavailable."""

    def test_runner_import_guard_exists(self) -> None:
        """Verify AppIngressRunner import has fail-closed guard."""
        source = _get_main_module_source()
        assert "_RUNNER_AVAILABLE" in source or "ImportError" in source
        assert "RuntimeError" in source, "Fail-closed RuntimeError missing"
