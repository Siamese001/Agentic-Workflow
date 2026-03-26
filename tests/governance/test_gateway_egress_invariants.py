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

#  # MOVED: from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    L0_ROUTING_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    OPS_SCRIPTS_DIR,
    TESTS_DIR,
    TOOLS_DIR,
)

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
    L2_EXECUTION_DIR,
    "data/sdks_mcps",
    TESTS_DIR,
    OPS_SCRIPTS_DIR,
    TOOLS_DIR,
)

_KNOWN_BYPASS_DEBT: frozenset[str] = frozenset(
    {
        "apps_rg/tools/ResumeGenerator.py",
        "apps_shared/utils/providers_google_genai_client_util.py",
        # Lazy inline import inside invoke_prompt() with try/except ImportError guard.
        # This is the hardened executor implementation for the sync healing path.
        # Remediation: move import to L2 gateway; tracked as gateway-migration debt.
        "apps_shared/types/hardened_gemini_executor_types.py",
    }
)

_NON_GATEWAY_SCAN_ROOTS = [
    REPO_ROOT / L0_ROUTING_DIR,
    REPO_ROOT / L1_COGNITION_DIR,
    REPO_ROOT / L3_ORCHESTRATION_DIR,
    REPO_ROOT / AGENTIC_CORE_DIR / "L5_safety",
    REPO_ROOT / APPS_LIC_DIR,
    REPO_ROOT / APPS_RG_DIR,
    REPO_ROOT / APPS_SHARED_DIR,
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
        from agentic_core.L0_routing.config.path_constants import (
        """INV-GW-1: Zero direct SDK imports outside L2 gateway (AST scan of non-gateway layers)."""
        tamper = os.environ.get("SPRAWL_NEGCTRL_TAMPER", "0")

    tamper = os.environ.get("SPRAWL_NEGCTRL_TAMPER", "0")

    violations: dict[str, list[str]] = {}
    for root in _NON_GATEWAY_SCAN_ROOTS:
        if not root.exists():
            continue
        for py in root.rglob("*.py"):
            canon = _canonical(py)
            if _in_allowed(canon) or canon in _KNOWN_BYPASS_DEBT:
                continue
            source = py.read_text(encoding="utf-8", errors="replace")
            hits = _ast_scan_sdk_imports(source, canon)
            if hits:
                violations[canon] = hits

    if tamper == "1":
        pytest.xfail(reason="SPRAWL_NEGCTRL_TAMPER=1: INV-GW-1 xfail — tamper mode active")

    assert not violations, "INV-GW-1 VIOLATION — direct SDK imports outside sovereign gateway:\n" + "\n".join(
        f"  {p}: {v}" for p, vs in violations.items() for v in vs
    )
