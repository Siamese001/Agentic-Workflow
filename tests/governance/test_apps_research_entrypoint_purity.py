"""P0.1 Governance tests — apps_research entrypoint purity.

Enforces that apps_research/__main__.py is a pure shim: no engine imports,
no C0 adapter imports, no PA compiler imports, no L2 adapter imports, no
provider SDK imports, no L4 write surfaces, no l2_callable construction,
no inline research closure.

Plan: apps-research-spine-alignment-d4e8f2 P0.1.

The active CLI may call the canonical spine handoff, but it must not delegate
to the retired apps_research.scripts.run_research entrypoint or import engines.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
APP_DIR = REPO_ROOT / "apps_research"
MAIN_PY = APP_DIR / "__main__.py"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _src() -> str:
    assert MAIN_PY.exists(), f"apps_research/__main__.py missing: {MAIN_PY}"
    return MAIN_PY.read_text(encoding="utf-8")


def _tree() -> ast.Module:
    return ast.parse(_src())


def _all_imports(tree: ast.Module) -> list[tuple[str | None, str, int]]:
    """Return (module, name_or_alias, lineno) for every import in the tree."""
    results: list[tuple[str | None, str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                results.append((None, alias.name, node.lineno))
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            for alias in node.names:
                results.append((mod, alias.name, node.lineno))
    return results


# ---------------------------------------------------------------------------
# 1. Pure shim: __main__.py must call agentic_core runner, not run research itself
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_research_main_is_pure_shim() -> None:
    """__main__.py must delegate to agentic_core runner, not run research inline.

    Violations: calling run_research.main, instantiating engine classes, calling
    query_decomposer, or containing synthesis logic directly.
    """
    src = _src()
    forbidden_patterns = [
        "apps_research.scripts.run_research",  # legacy script delegation
        "run_research.main",
        "company_brief_engine",  # direct engine import/use
        "research_assembly_engine",
        "query_decomposer",
        "synthesis_engine",
        "ResearchHopOrchestrator",  # orchestrator belongs inside governed substrate
    ]
    violations = [p for p in forbidden_patterns if p in src]
    assert not violations, (
        f"apps_research/__main__.py is NOT a pure shim. Found forbidden patterns: "
        f"{violations}. __main__.py must only parse CLI args, build the request "
        f"envelope, and call the agentic_core canonical runner with "
        f"app_name='apps_research'."
    )


# ---------------------------------------------------------------------------
# 2. No research engine imports
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_research_main_does_not_import_research_engines() -> None:
    """__main__.py must not import any apps_research.engines module."""
    tree = _tree()
    for mod, name, lineno in _all_imports(tree):
        full = f"{mod}.{name}" if mod else name
        if "apps_research.engines" in full or (mod and mod.startswith("apps_research.engines")):
            pytest.fail(
                f"apps_research/__main__.py imports engine at line {lineno}: "
                f"from {mod} import {name}. "
                "Engine imports are forbidden in __main__.py — delegate to agentic_core runner."
            )
        if mod and "engines" in mod and "apps_research" in mod:
            pytest.fail(
                f"apps_research/__main__.py imports from engines namespace at line {lineno}: "
                f"from {mod} import {name}."
            )


# ---------------------------------------------------------------------------
# 3. No C0 adapter imports
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_research_main_does_not_import_c0_adapters() -> None:
    """__main__.py must not import C0 retrieval adapters directly."""
    tree = _tree()
    c0_forbidden = [
        "research_c0_adapter",
        "tavily_retrieval",
        "reranker_adapter",
        "pdf_ingest",
        "llm_client",
        "c0_context",
        "c0_retrieval",
        "retrieval_engine",
        "research_retrieval_engine",
    ]
    for mod, name, lineno in _all_imports(tree):
        full_mod = mod or ""
        full_name = name or ""
        for forbidden in c0_forbidden:
            if forbidden in full_mod or forbidden in full_name:
                pytest.fail(
                    f"apps_research/__main__.py imports C0 adapter '{forbidden}' at "
                    f"line {lineno}: from {mod} import {name}. "
                    "C0 adapter imports are forbidden in __main__.py."
                )


# ---------------------------------------------------------------------------
# 4. No PA compiler imports
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_research_main_does_not_import_pa_compiler() -> None:
    """__main__.py must not import the Prompt Assembly compiler."""
    tree = _tree()
    pa_forbidden = [
        "research_pa_compiler",
        "prompt_assembly",
        "PromptBOM",
        "CompiledPromptArtifact",
        "prompt_registry",
    ]
    for mod, name, lineno in _all_imports(tree):
        full_mod = mod or ""
        full_name = name or ""
        for forbidden in pa_forbidden:
            if forbidden in full_mod or forbidden in full_name:
                pytest.fail(
                    f"apps_research/__main__.py imports PA component '{forbidden}' at "
                    f"line {lineno}: from {mod} import {name}. "
                    "PA compiler must not be imported in __main__.py."
                )


# ---------------------------------------------------------------------------
# 5. No L2 adapter imports
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_research_main_does_not_import_l2_adapters() -> None:
    """__main__.py must not import L2 step adapters directly."""
    tree = _tree()
    l2_forbidden = [
        "research_l2_step_adapters",
        "execution_adapter",
        "research_ingress_runner",
        "governed_research_run",
    ]
    src = _src()
    # governed_run (the shared spine helper) is permitted; governed_research_run (app-owned) is not
    for mod, name, lineno in _all_imports(tree):
        full_mod = mod or ""
        full_name = name or ""
        for forbidden in l2_forbidden:
            if forbidden in full_mod or forbidden in full_name:
                pytest.fail(
                    f"apps_research/__main__.py imports L2 adapter '{forbidden}' at "
                    f"line {lineno}: from {mod} import {name}. "
                    "L2 adapters must not be imported in __main__.py — they are "
                    "invoked by the agentic_core runner via the registered capability."
                )


# ---------------------------------------------------------------------------
# 6. No provider SDK imports
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_research_main_does_not_import_provider_sdks() -> None:
    """__main__.py must not import provider SDKs (openai, anthropic, etc.)."""
    tree = _tree()
    provider_forbidden = [
        "openai",
        "anthropic",
        "cohere",
        "together",
        "litellm",
        "groq",
        "mistral",
        "google.generativeai",
        "vertexai",
        "boto3",  # Bedrock
    ]
    for mod, name, lineno in _all_imports(tree):
        full_mod = mod or ""
        full_name = name or ""
        for forbidden in provider_forbidden:
            if full_mod.startswith(forbidden) or full_name == forbidden:
                pytest.fail(
                    f"apps_research/__main__.py imports provider SDK '{forbidden}' at "
                    f"line {lineno}: from {mod} import {name}. "
                    "Provider SDK imports are forbidden in __main__.py."
                )


# ---------------------------------------------------------------------------
# 7. No L4 write surface imports
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_research_main_does_not_import_l4_write_surfaces() -> None:
    """__main__.py must not import L4 write surfaces directly."""
    tree = _tree()
    l4_forbidden = [
        "research_brief_uwg_writer",
        "L4_state",
        "durable_write",
        "write_gateway",
        "uwg_writer",
        "canonical_store",
    ]
    for mod, name, lineno in _all_imports(tree):
        full_mod = mod or ""
        full_name = name or ""
        for forbidden in l4_forbidden:
            if forbidden in full_mod or forbidden in full_name:
                pytest.fail(
                    f"apps_research/__main__.py imports L4 write surface '{forbidden}' at "
                    f"line {lineno}: from {mod} import {name}. "
                    "L4 writes must go through UWG, never directly from __main__.py."
                )


# ---------------------------------------------------------------------------
# 8. No l2_callable construction
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_research_main_contains_no_l2_callable_construction() -> None:
    """__main__.py must not build, assign, or pass an l2_callable closure."""
    tree = _tree()
    for node in ast.walk(tree):
        # Variable named l2_callable or recipe_callable
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in (
                    "l2_callable", "recipe_callable", "_l2_callable"
                ):
                    pytest.fail(
                        f"apps_research/__main__.py assigns l2_callable at line "
                        f"{node.lineno}. __main__.py must not build callable closures — "
                        "pass app_name to the agentic_core runner instead."
                    )
        # Function calls named build_l2_callable or similar
        if isinstance(node, ast.Call):
            func = node.func
            name = None
            if isinstance(func, ast.Name):
                name = func.id
            elif isinstance(func, ast.Attribute):
                name = func.attr
            if name and "l2_callable" in name.lower():
                pytest.fail(
                    f"apps_research/__main__.py calls l2_callable factory at line "
                    f"{getattr(node, 'lineno', '?')}."
                )
        # Name reference to l2_callable
        if isinstance(node, ast.Name) and node.id == "l2_callable":
            pytest.fail(
                f"apps_research/__main__.py references 'l2_callable' at line "
                f"{node.lineno}."
            )


# ---------------------------------------------------------------------------
# 9. Default --topic path must not use legacy capability registry / GovernedResearchRun
# ---------------------------------------------------------------------------

_LEGACY_DEFAULT_PATH_FORBIDDEN = (
    "research_capability_registry",
    "resolve_company_brief_capability",
    "GovernedResearchRun",
    "_run_canonical",
)


@pytest.mark.governance
def test_apps_research_main_default_path_no_legacy_capability_registry() -> None:
    """Default product CLI must not import or call the legacy registry bypass path.

    Phase 3 may still keep research_capability_registry.py and GovernedResearchRun
    on disk for substrate/handoff — they must not be wired from __main__.py.
    """
    src = _src()
    tree = _tree()

    for mod, name, lineno in _all_imports(tree):
        full = f"{mod}.{name}" if mod else name
        if "research_capability_registry" in full:
            pytest.fail(
                f"apps_research/__main__.py imports capability registry at line {lineno}: "
                f"{full}"
            )
        if mod == "apps_research.integrations.governed_research_run" or name == "GovernedResearchRun":
            pytest.fail(
                f"apps_research/__main__.py imports GovernedResearchRun at line {lineno}."
            )

    for pattern in _LEGACY_DEFAULT_PATH_FORBIDDEN:
        if pattern in src and pattern == "GovernedResearchRun":
            # Allow docstring/comment mention only when not an import or call
            if "import GovernedResearchRun" in src or "GovernedResearchRun(" in src:
                pytest.fail(
                    "apps_research/__main__.py must not import or instantiate "
                    "GovernedResearchRun on the default path."
                )
            continue
        if pattern in src:
            if pattern == "GovernedResearchRun":
                continue
            pytest.fail(
                f"apps_research/__main__.py references forbidden legacy path '{pattern}'."
            )

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            call_name = ""
            if isinstance(func, ast.Name):
                call_name = func.id
            elif isinstance(func, ast.Attribute):
                call_name = func.attr
            if call_name in (
                "resolve_company_brief_capability",
                "_run_canonical",
            ):
                pytest.fail(
                    f"apps_research/__main__.py calls {call_name} at line {node.lineno}."
                )


@pytest.mark.governance
def test_apps_research_main_default_path_uses_profile_spine_call_chain() -> None:
    """main() must delegate product runs to the non-stub spine handoff."""
    tree = _tree()
    has_run_profile_spine = False
    main_calls_product = False
    product_calls_profile = False
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == "_run_profile_spine":
                has_run_profile_spine = True
            if node.name == "_run_product_research":
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        func = child.func
                        if isinstance(func, ast.Name) and func.id == "_run_profile_spine":
                            main_calls_product = True
            if node.name == "_run_research_record":
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        func = child.func
                        if isinstance(func, ast.Name) and func.id == "run_research_via_spine":
                            product_calls_profile = True
        if isinstance(node, ast.FunctionDef) and node.name == "main":
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    func = child.func
                    if isinstance(func, ast.Name) and func.id == "_run_product_research":
                        main_calls_product = True
    assert has_run_profile_spine, "_run_profile_spine missing from __main__.py"
    assert main_calls_product, (
        "main() must call _run_product_research which calls _run_profile_spine"
    )
    assert product_calls_profile, (
        "_run_research_record() must call run_research_via_spine, not the deleted L2 stub"
    )


# ---------------------------------------------------------------------------
# 10. No inline research closure
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_research_main_contains_no_inline_research_closure() -> None:
    """__main__.py must not define a function that performs research/synthesis inline.

    Permitted inner functions: _adg_bootstrap, _is_live_cert_mode, _run_live_cert,
    _load_cert_route_entry, _build_exit_receipts, _maybe_run_exit_hook, main.
    Any function that references retrieval, synthesis, or provider calls inline is forbidden.
    """
    tree = _tree()
    synthesis_markers = {
        "retrieve", "synthesize", "brief", "query_decompose",
        "company_brief", "research_run", "run_main",
    }
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            func_src_nodes = list(ast.walk(node))
            for child in func_src_nodes:
                if isinstance(child, ast.Call):
                    func = child.func
                    call_name = ""
                    if isinstance(func, ast.Name):
                        call_name = func.id
                    elif isinstance(func, ast.Attribute):
                        call_name = func.attr
                    if call_name == "run_main":
                        pytest.fail(
                            f"apps_research/__main__.py function '{node.name}' at line "
                            f"{node.lineno} calls 'run_main' — the legacy runner call. "
                            "Remove this; wire to agentic_core canonical runner instead."
                        )
