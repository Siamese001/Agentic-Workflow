"""P0.1 Governance tests — apps_underwriting_ai provider boundary.

Enforces that provider SDK calls (LLM invocations, embedding APIs, external
HTTP) are never made directly from __main__.py or from the capability registry.
Provider calls belong inside the PA compiler and L2 step adapters, behind
the LLM rationale firewall.

Plan: apps-underwriting-ai-spine-hardening-d7f3b2 P0.1 / P0.4.

Tests 20–21 (provider boundary group). Tests 20 passes immediately
(checking the capability registry). Test 21 is xfail(strict=True) until
W1 cleans up __main__.py.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
APP_DIR = REPO_ROOT / "apps_underwriting_ai"
MAIN_PY = APP_DIR / "__main__.py"
CAPABILITY_REGISTRY = APP_DIR / "integrations" / "underwriting_capability_registry.py"

_PROVIDER_PATTERNS = [
    "openai",
    "anthropic",
    "cohere",
    "together",
    "litellm",
    "groq",
    "mistral",
    "vertexai",
    "boto3",
    "requests.post",
    "httpx.post",
]


def _check_no_provider_calls(path: Path, label: str) -> None:
    """Assert that no provider SDK symbols appear in the source file."""
    assert path.exists(), f"{label} missing: {path}"
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                for p in _PROVIDER_PATTERNS:
                    if alias.name.startswith(p):
                        pytest.fail(
                            f"{label} imports provider SDK '{p}' at line {node.lineno}. "
                            "Provider calls must go through the LLM rationale firewall "
                            "inside the PA compiler or L2 step adapters."
                        )
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            for p in _PROVIDER_PATTERNS:
                if mod.startswith(p):
                    pytest.fail(
                        f"{label} imports from provider SDK '{p}' (module: {mod}) "
                        f"at line {node.lineno}. Provider imports forbidden here."
                    )


# ---------------------------------------------------------------------------
# 20. Capability registry contains no provider calls
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_underwriting_ai_capability_registry_has_no_provider_calls() -> None:
    """underwriting_capability_registry.py must not import or call provider SDKs.

    The registry is pure metadata — it declares capability contracts without
    invoking any provider or external API.
    """
    _check_no_provider_calls(
        CAPABILITY_REGISTRY,
        "underwriting_capability_registry.py",
    )


# ---------------------------------------------------------------------------
# 21. __main__.py must not call provider SDKs at module level
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_underwriting_ai_main_has_no_top_level_provider_calls() -> None:
    """__main__.py must not import provider SDKs at the top level.

    After W1, the shim only imports argparse, sys, and the agentic_core runner.
    Any provider SDK import anywhere in __main__.py is a boundary violation.
    """
    _check_no_provider_calls(MAIN_PY, "apps_underwriting_ai/__main__.py")
