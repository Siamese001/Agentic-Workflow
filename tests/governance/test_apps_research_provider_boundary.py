"""P0.1 Governance tests — apps_research provider gateway boundary.

Enforces that:
- Provider calls go only through the governed gateway (not raw SDK calls)
- Exit emits X3 disposition but does not write L4 directly

Plan: apps-research-spine-alignment-d4e8f2 P0.1.

Tests 19-20 in the P0 test suite.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
APP_DIR = REPO_ROOT / "apps_research"
MAIN_PY = APP_DIR / "__main__.py"
ENGINES_DIR = APP_DIR / "engines"
INTEGRATIONS_DIR = APP_DIR / "integrations"

# Provider SDK top-level modules — any direct import is a boundary violation
PROVIDER_SDK_MODULES = frozenset([
    "openai",
    "anthropic",
    "cohere",
    "together",
    "litellm",
    "groq",
    "mistral",
    "google.generativeai",
    "vertexai",
    "boto3",
    "botocore",
    "azureml",
    "huggingface_hub",
    "transformers",
])

# Files that ARE the governed gateway — raw SDK calls are expected here
GATEWAY_FILES = frozenset([
    "llm_client.py",
    "provider_gateway.py",
    "governed_provider_gateway.py",
])


def _scan_file_for_provider_imports(path: Path) -> list[tuple[str, int]]:
    """Return (import_name, lineno) for any raw provider SDK import in path."""
    if not path.exists():
        return []
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src)
    violations: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".")[0]
                if top in PROVIDER_SDK_MODULES:
                    violations.append((alias.name, node.lineno))
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            top = mod.split(".")[0]
            if top in PROVIDER_SDK_MODULES:
                violations.append((mod, node.lineno))
    return violations


# ---------------------------------------------------------------------------
# 19. Provider calls only through governed gateway
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_research_provider_calls_only_through_governed_gateway() -> None:
    """No apps_research module outside the governed gateway may import provider SDKs.

    Allowed: apps_research/integrations/llm_client.py (the gateway itself).
    Forbidden everywhere else: direct openai, anthropic, cohere, litellm, etc. imports.
    """
    scan_dirs = [ENGINES_DIR, INTEGRATIONS_DIR]
    all_violations: list[str] = []

    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for py_file in scan_dir.rglob("*.py"):
            if py_file.name in GATEWAY_FILES:
                continue  # gateway itself is allowed
            violations = _scan_file_for_provider_imports(py_file)
            for imp, lineno in violations:
                rel = py_file.relative_to(REPO_ROOT)
                all_violations.append(f"{rel}:{lineno} — import {imp}")

    # Also check __main__.py
    main_violations = _scan_file_for_provider_imports(MAIN_PY)
    for imp, lineno in main_violations:
        all_violations.append(f"apps_research/__main__.py:{lineno} — import {imp}")

    assert not all_violations, (
        "Raw provider SDK imports detected outside the governed gateway. "
        "All provider calls must go through the governed gateway "
        "(apps_research/integrations/llm_client.py or equivalent). "
        "Violations:\n" + "\n".join(f"  {v}" for v in all_violations)
    )


# ---------------------------------------------------------------------------
# 20. Exit emits X3 but does not write L4
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_research_exit_emits_x3_but_does_not_write_l4() -> None:
    """Exit v6 must emit exactly one X3 disposition; it must not write L4 directly.

    Checked via the cert_route_registry which confirms Exit is invoked,
    and by ensuring no module in apps_research/integrations/ performs
    direct L4 writes (only UWG writes are permitted).
    """
    cert_registry = APP_DIR / "config" / "cert_route_registry.yaml"
    assert cert_registry.exists(), f"cert_route_registry.yaml missing: {cert_registry}"

    import yaml  # local import — governance test only
    doc = yaml.safe_load(cert_registry.read_text(encoding="utf-8"))
    routes = doc.get("routes", [])
    assert routes, "cert_route_registry.yaml has no routes"

    # Exit must be invoked
    assert any(r.get("invoke_exit_eval") for r in routes), (
        "cert_route_registry.yaml must declare invoke_exit_eval: true. "
        "Exit v6 must be invoked on every execution path."
    )

    # Scan integrations for direct L4 write patterns (outside UWG writer)
    l4_write_patterns = [
        "L4_state.write",
        "canonical_store.write",
        "durable_write(",
        "write_to_l4(",
        ".write_l4(",
        "StateStore().write",
    ]
    violations: list[str] = []
    if INTEGRATIONS_DIR.exists():
        for py_file in INTEGRATIONS_DIR.rglob("*.py"):
            if py_file.name in ("research_brief_uwg_writer.py",):
                continue  # UWG writer is the approved write path
            src = py_file.read_text(encoding="utf-8")
            for pattern in l4_write_patterns:
                if pattern in src:
                    rel = py_file.relative_to(REPO_ROOT)
                    violations.append(f"{rel} — pattern '{pattern}'")

    assert not violations, (
        "Direct L4 write patterns detected in apps_research integrations (outside UWG). "
        "Exit emits X3 disposition only; L4 writes must go through UWG. "
        "Violations:\n" + "\n".join(f"  {v}" for v in violations)
    )
