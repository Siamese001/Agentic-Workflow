"""P0.1 Governance tests — apps_underwriting_ai entrypoint purity.

Enforces that apps_underwriting_ai/__main__.py is a pure shim: no direct
engine instantiation, no C0 adapter imports, no PA compiler imports, no
L2 adapter imports, no provider SDK imports, no l2_callable construction,
no inline underwriting closure.

Plan: apps-underwriting-ai-spine-hardening-d7f3b2 P0.1 / P0.4.

Tests 1–11 (entrypoint group). The entrypoint purity tests (1–9) are
xfail(strict=True) on the current codebase because __main__.py still
imports governed_underwriting_run / UnderwritingIngressRunner / engines.
They become GREEN after W1 rewrites __main__.py into a pure shim.

Tests 10–11 (scaffold presence) pass immediately after P0 stubs land.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
APP_DIR = REPO_ROOT / "apps_underwriting_ai"
MAIN_PY = APP_DIR / "__main__.py"
INTEGRATIONS_DIR = APP_DIR / "integrations"


def _src() -> str:
    assert MAIN_PY.exists(), f"apps_underwriting_ai/__main__.py missing: {MAIN_PY}"
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
# 1. Pure shim: __main__.py must not instantiate underwriting engines inline
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_underwriting_ai_main_does_not_import_governed_underwriting_run() -> None:
    """__main__.py must not import governed_underwriting_run (app-owned runner).

    After W1, __main__.py delegates all execution to the agentic_core runner
    via the registered capability. governed_underwriting_run is an app-internal
    helper; it must not appear in the shim.
    """
    src = _src()
    assert "governed_underwriting_run" not in src, (
        "apps_underwriting_ai/__main__.py imports governed_underwriting_run. "
        "After W1, __main__.py must only parse CLI args and call the agentic_core "
        "canonical runner with app_name='apps_underwriting_ai'."
    )


# ---------------------------------------------------------------------------
# 2. No direct engine imports in __main__.py
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_underwriting_ai_main_does_not_import_engines() -> None:
    """__main__.py must not import any apps_underwriting_ai.engines module."""
    tree = _tree()
    for mod, name, lineno in _all_imports(tree):
        full = f"{mod}.{name}" if mod else name
        if "apps_underwriting_ai.engines" in full or (
            mod and mod.startswith("apps_underwriting_ai.engines")
        ):
            pytest.fail(
                f"apps_underwriting_ai/__main__.py imports engine at line {lineno}: "
                f"from {mod} import {name}. "
                "Engine imports are forbidden in __main__.py."
            )
        if mod and "engines" in mod and "apps_underwriting_ai" in mod:
            pytest.fail(
                f"apps_underwriting_ai/__main__.py imports from engines namespace at "
                f"line {lineno}: from {mod} import {name}."
            )


# ---------------------------------------------------------------------------
# 3. No UnderwritingIngressRunner in __main__.py
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_underwriting_ai_main_does_not_import_ingress_runner() -> None:
    """__main__.py must not import UnderwritingIngressRunner directly."""
    src = _src()
    assert "UnderwritingIngressRunner" not in src, (
        "apps_underwriting_ai/__main__.py imports UnderwritingIngressRunner. "
        "The ingress runner is an internal integration component; __main__.py "
        "must not reference it after W1."
    )


# ---------------------------------------------------------------------------
# 4. No C0 adapter imports in __main__.py
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_underwriting_ai_main_does_not_import_c0_adapters() -> None:
    """__main__.py must not import C0 retrieval adapters directly."""
    tree = _tree()
    c0_forbidden = [
        "underwriting_c0_adapter",
        "C0_MODE",
        "FinalEvidenceContract",
        "llm_client",
        "c0_retrieval",
    ]
    for mod, name, lineno in _all_imports(tree):
        full_mod = mod or ""
        full_name = name or ""
        for forbidden in c0_forbidden:
            if forbidden in full_mod or forbidden in full_name:
                pytest.fail(
                    f"apps_underwriting_ai/__main__.py imports C0 adapter '{forbidden}' at "
                    f"line {lineno}: from {mod} import {name}. "
                    "C0 adapter imports are forbidden in __main__.py."
                )


# ---------------------------------------------------------------------------
# 5. No PA compiler imports in __main__.py
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_underwriting_ai_main_does_not_import_pa_compiler() -> None:
    """__main__.py must not import the Prompt Assembly compiler."""
    tree = _tree()
    pa_forbidden = [
        "underwriting_pa_compiler",
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
                    f"apps_underwriting_ai/__main__.py imports PA component '{forbidden}' at "
                    f"line {lineno}: from {mod} import {name}. "
                    "PA compiler must not be imported in __main__.py."
                )


# ---------------------------------------------------------------------------
# 6. No provider SDK imports in __main__.py
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_underwriting_ai_main_does_not_import_provider_sdks() -> None:
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
        "vertexai",
        "boto3",
    ]
    for mod, name, lineno in _all_imports(tree):
        full_mod = mod or ""
        full_name = name or ""
        for forbidden in provider_forbidden:
            if full_mod.startswith(forbidden) or full_name == forbidden:
                pytest.fail(
                    f"apps_underwriting_ai/__main__.py imports provider SDK '{forbidden}' at "
                    f"line {lineno}: from {mod} import {name}. "
                    "Provider SDK imports are forbidden in __main__.py."
                )


# ---------------------------------------------------------------------------
# 7. No l2_callable construction in __main__.py
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_underwriting_ai_main_contains_no_l2_callable_construction() -> None:
    """__main__.py must not build, assign, or pass an l2_callable closure."""
    tree = _tree()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in (
                    "l2_callable", "recipe_callable", "_l2_callable"
                ):
                    pytest.fail(
                        f"apps_underwriting_ai/__main__.py assigns l2_callable at line "
                        f"{node.lineno}. __main__.py must not build callable closures."
                    )
        if isinstance(node, ast.Call):
            func = node.func
            name = None
            if isinstance(func, ast.Name):
                name = func.id
            elif isinstance(func, ast.Attribute):
                name = func.attr
            if name and "l2_callable" in name.lower():
                pytest.fail(
                    f"apps_underwriting_ai/__main__.py calls l2_callable factory at line "
                    f"{getattr(node, 'lineno', '?')}."
                )


# ---------------------------------------------------------------------------
# 8. No DeterministicRiskScorer import in __main__.py
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_underwriting_ai_main_does_not_import_deterministic_risk_scorer() -> None:
    """__main__.py must not import DeterministicRiskScorer.

    The scorer belongs inside the governed engine substrate, not in the
    CLI shim. All scoring executes inside the managed workflow stages.
    """
    src = _src()
    assert "DeterministicRiskScorer" not in src, (
        "apps_underwriting_ai/__main__.py references DeterministicRiskScorer. "
        "The scorer must not be imported or called from the CLI shim. "
        "Scoring executes inside the managed workflow stage adapters."
    )


# ---------------------------------------------------------------------------
# 9. No DecisionRenderer / EnterpriseUnderwritingRenderer in __main__.py
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_underwriting_ai_main_does_not_import_output_renderers() -> None:
    """__main__.py must not import output renderer classes directly.

    The pure shim delegates rendering to the agentic_core runner's output
    contract. Direct renderer imports indicate the shim is doing too much.
    """
    src = _src()
    forbidden = ["DecisionRenderer", "EnterpriseUnderwritingRenderer"]
    found = [f for f in forbidden if f in src]
    assert not found, (
        f"apps_underwriting_ai/__main__.py imports output renderers: {found}. "
        "After W1, output rendering is delegated to the agentic_core runner."
    )


# ---------------------------------------------------------------------------
# 10. Scaffold: capability registry file exists
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_underwriting_ai_capability_registry_file_exists() -> None:
    """underwriting_capability_registry.py must exist (created in P0.2)."""
    registry = INTEGRATIONS_DIR / "underwriting_capability_registry.py"
    assert registry.exists(), (
        f"apps_underwriting_ai/integrations/underwriting_capability_registry.py "
        f"is missing at {registry}. "
        "P0.2 must create this file before W1 wires agentic_core capability resolution."
    )


# ---------------------------------------------------------------------------
# 11. Scaffold: integration stub files exist
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_underwriting_ai_integration_stubs_exist() -> None:
    """All four P0.3 integration stub files must exist."""
    stubs = [
        "underwriting_c0_adapter.py",
        "underwriting_l3_workflow_adapter.py",
        "underwriting_l2_step_adapters.py",
        "underwriting_exit_fec_producer.py",
    ]
    missing = [s for s in stubs if not (INTEGRATIONS_DIR / s).exists()]
    assert not missing, (
        f"Missing P0.3 integration stub files: {missing}. "
        f"Expected at apps_underwriting_ai/integrations/. "
        "P0.3 must create all stubs before W2/W3/W4/W5 implement them."
    )
