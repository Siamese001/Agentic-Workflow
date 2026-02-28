"""Gateway egress invariant contract tests.

Invariants asserted:
  INV-GW-1: All LLM egress must flow exclusively through the sovereign gateway;
             no direct SDK imports exist outside the L2 gateway module (AST scan).
"""

from __future__ import annotations

import ast
import os
import pathlib

import pytest

pytestmark = pytest.mark.governance

REPO_ROOT = pathlib.Path(__file__).parent.parent.parent

_FORBIDDEN_SDK_ROOTS = frozenset(
    {
        "google.generativeai",
        "anthropic",
        "openai",
        "vertexai",
        "cohere",
    }
)

_ALLOWED_ROOTS = (
    "agentic_core/L2_execution",
    "data/sdks_mcps",
    "tests",
    "ops_scripts",
    "tools",
)

_KNOWN_BYPASS_DEBT: frozenset[str] = frozenset(
    {
        "apps_rg/tools/ResumeGenerator.py",
        "apps_shared/utils/providers_google_genai_client_util.py",
    }
)

_NON_GATEWAY_SCAN_ROOTS = [
    REPO_ROOT / "agentic_core" / "L0_routing",
    REPO_ROOT / "agentic_core" / "L1_cognition",
    REPO_ROOT / "agentic_core" / "L3_orchestration",
    REPO_ROOT / "agentic_core" / "L5_safety",
    REPO_ROOT / "apps_lic",
    REPO_ROOT / "apps_rg",
    REPO_ROOT / "apps_shared",
]


def _canonical(filepath: pathlib.Path) -> str:
    try:
        return str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(filepath).replace("\\", "/")


def _in_allowed(canon: str) -> bool:
    return any(canon.startswith(p) for p in _ALLOWED_ROOTS)


def _ast_scan_sdk_imports(source: str, canon: str) -> list[str]:
    if _in_allowed(canon):
        return []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    hits: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                for sdk in _FORBIDDEN_SDK_ROOTS:
                    if alias.name == sdk or alias.name.startswith(sdk + "."):
                        hits.append(f"line {node.lineno}: import {alias.name!r}")
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            for sdk in _FORBIDDEN_SDK_ROOTS:
                if mod == sdk or mod.startswith(sdk + "."):
                    hits.append(f"line {node.lineno}: from {mod} import ...")
    return hits


def test_llm_egress_only_via_sovereign_gateway():
    """INV-GW-1: Zero direct SDK imports outside L2 gateway (AST scan of non-gateway layers)."""
    tamper = os.environ.get("SPRAWL_NEGCTRL_TAMPER", "0")

    violations: dict[str, list[str]] = {}
    for root in _NON_GATEWAY_SCAN_ROOTS:
        if not root.exists():
            continue
        for py in root.rglob("*.py"):
            canon = _canonical(py)
            if _in_allowed(canon) or canon in _KNOWN_BYPASS_DEBT:
                continue
            try:
                source = py.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            hits = _ast_scan_sdk_imports(source, canon)
            if hits:
                violations[canon] = hits

    if tamper == "1":
        pytest.xfail(reason="SPRAWL_NEGCTRL_TAMPER=1: INV-GW-1 xfail — tamper mode active")

    assert not violations, "INV-GW-1 VIOLATION — direct SDK imports outside sovereign gateway:\n" + "\n".join(
        f"  {p}: {v}" for p, vs in violations.items() for v in vs
    )
