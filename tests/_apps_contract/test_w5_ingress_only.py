"""W5 Ingress-Only Verification Tests — AG-RGGOV-W5 Compliance.

Validates that apps_rg/__main__.py is pure ingress shim with NO runtime authority.

Tests:
- No planner/router/orchestrator imports
- No prompt assembly/executor/provider calls
- No get_llm_gateway/SovereignLLMGateway usage
- No quarantine imports
- No core runtime contract emission
- Main delegates to ``dispatch_apps_rg_run`` (canonical CLI entry), not inline spine logic
"""

import ast
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


class TestW5CanonicalDispatchEntry:
    """``__main__`` wires CLI primitives to the app-owned full-run seam."""

    def test_imports_full_run_governance_seam(self) -> None:
        tree = _parse_main_ast()
        has_import = False
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.ImportFrom)
                and node.module == "apps_rg.runtime.orchestration.r3r4_whole_run_orchestration"
            ):
                for alias in node.names:
                    if alias.name == "run_whole_run_with_route_governance":
                        has_import = True
                        break
        assert has_import, "__main__ must import run_whole_run_with_route_governance"

    def test_main_function_body_calls_full_run_governance_seam(self) -> None:
        tree = _parse_main_ast()
        main_fn: ast.FunctionDef | None = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "main":
                main_fn = node
                break
        assert main_fn is not None
        found = False
        for node in ast.walk(main_fn):
            if isinstance(node, ast.Call):
                fn = node.func
                if isinstance(fn, ast.Name) and fn.id == "run_whole_run_with_route_governance":
                    found = True
                    break
                if isinstance(fn, ast.Attribute) and fn.attr == "run_whole_run_with_route_governance":
                    found = True
                    break
        assert found, "main() must call run_whole_run_with_route_governance(...)"

    def test_no_local_request_envelope_definition(self) -> None:
        """Ingress envelope construction happens inside dispatch / U0 — not in __main__."""
        source = _get_main_module_source()
        assert "class RequestEnvelope" not in source


class TestW5IngressFlow:
    """Verify ingress flow delegates to agentic_core."""

    def test_main_invokes_full_run_governance_at_runtime(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Behavior: main() calls the app-owned full-run seam with CLI-derived primitives."""
        calls: list[dict[str, object]] = []

        def _fake_dispatch(**kwargs: object) -> dict[str, object]:
            calls.append(kwargs)
            return {
                "exit_status": "success",
                "execution_status": "completed",
                "outcome_authorized": True,
                "artifact_dir": "",
            }

        monkeypatch.setenv("APPS_RG_TEST_HARNESS", "1")
        monkeypatch.setattr(
            "apps_rg.runtime.orchestration.r3r4_whole_run_orchestration.run_whole_run_with_route_governance",
            _fake_dispatch,
        )
        import apps_rg.__main__ as rg_main

        code = rg_main.main(["--target-company", "AcmeCo", "--target-role", "Engineer"])
        assert code == 0
        assert len(calls) == 1
        assert calls[0].get("target_company") == "AcmeCo"
        assert calls[0].get("target_role") == "Engineer"

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
    """Verify fail-closed CLI exit when the dispatch seam fails."""

    def test_dispatch_failure_returns_exit_1(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """When dispatch raises, main catches and returns 1 (no successful CLI outcome)."""

        def _boom(**_kwargs: object) -> dict[str, object]:
            raise RuntimeError("dispatch simulated failure")

        monkeypatch.setenv("APPS_RG_TEST_HARNESS", "1")
        monkeypatch.setattr(
            "apps_rg.runtime.orchestration.r3r4_whole_run_orchestration.run_whole_run_with_route_governance",
            _boom,
        )
        import apps_rg.__main__ as rg_main

        code = rg_main.main(["--target-company", "AcmeCo", "--target-role", "Engineer"])
        assert code == 1
