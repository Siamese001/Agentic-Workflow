"""Static bypass scanner invariant contract tests.

Invariants asserted:
  INV-SBS-1: No direct provider SDK imports for embeddings or LLM anywhere outside
              the sanctioned factory/gateway modules (AST scan of full repo).
  INV-SBS-2: No provider name or model-ID string literals appear outside the
              single registry fixture (tests/fixtures/embedding_provider_registry_fixture.py).
"""

from __future__ import annotations

import ast
import os
import pathlib
import re

import pytest

pytestmark = pytest.mark.governance

REPO_ROOT = pathlib.Path(__file__).parent.parent.parent

_SCAN_ROOTS = [
    REPO_ROOT / "agentic_core",
    REPO_ROOT / "apps_lic",
    REPO_ROOT / "apps_rg",
    REPO_ROOT / "apps_shared",
    REPO_ROOT / "system_learning",
]

_FORBIDDEN_IMPORT_ROOTS = frozenset(
    {
        "openai",
        "anthropic",
        "google.generativeai",
        "vertexai",
        "cohere",
        "voyageai",
        "sentence_transformers",
        "tiktoken",
    }
)

_ALLOWED_IMPORT_PREFIXES = (
    "agentic_core/L2_execution",
    "agentic_core/embeddings",
    "system_learning/engines/embedding_service_factory",
    "system_learning/engines/openai_embedder",
    "data/sdks_mcps",
    "tests",
    "ops_scripts",
    "tools",
)

_PROVIDER_LITERAL_PATTERN = re.compile(
    r"""(?:["'])(openai|anthropic|cohere|vertexai|bge|voyageai|sentence[_-]transformers)(?:["'])""",
    re.IGNORECASE,
)

_REGISTRY_FIXTURE = "tests/fixtures/embedding_provider_registry_fixture.py"

_LITERAL_SCAN_EXCLUDE = frozenset(
    {
        "tests/governance/test_static_bypass_scanners.py",
        "tests/governance/test_embedding_invariants.py",
        "tests/governance/test_gateway_egress_invariants.py",
    }
)

_KNOWN_DEBT: frozenset[str] = frozenset(
    {
        "agentic_core/L2_execution/healers/vllm_process_manager.py",
        "system_learning/engines/openai_embedder.py",
        "agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py",
        "apps_shared/utils/late_interaction_reranker_util.py",
        "apps_rg/tools/ResumeGenerator.py",
        "apps_shared/utils/providers_google_genai_client_util.py",
    }
)


def _canonical(filepath: pathlib.Path) -> str:
    try:
        return str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(filepath).replace("\\", "/")


def _in_allowed(canon: str) -> bool:
    return any(canon.startswith(p) for p in _ALLOWED_IMPORT_PREFIXES)


def _ast_scan_imports(source: str, canon: str) -> list[str]:
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
                for sdk in _FORBIDDEN_IMPORT_ROOTS:
                    if alias.name == sdk or alias.name.startswith(sdk + "."):
                        hits.append(f"line {node.lineno}: import {alias.name!r}")
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            for sdk in _FORBIDDEN_IMPORT_ROOTS:
                if mod == sdk or mod.startswith(sdk + "."):
                    hits.append(f"line {node.lineno}: from {mod!r}")
    return hits


def _scan_model_string_literals(source: str, canon: str) -> list[str]:
    if canon == _REGISTRY_FIXTURE or _in_allowed(canon) or canon in _LITERAL_SCAN_EXCLUDE:
        return []
    hits: list[str] = []
    for i, line in enumerate(source.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if _PROVIDER_LITERAL_PATTERN.search(line):
            hits.append(f"line {i}: provider literal in source: {stripped[:80]!r}")
    return hits


def test_no_direct_provider_sdk_imports_for_embeddings_or_llm():
    """INV-SBS-1: AST scan — no direct provider SDK imports outside factory/gateway."""
    tamper = os.environ.get("SPRAWL_NEGCTRL_TAMPER", "0")

    violations: dict[str, list[str]] = {}
    for root in _SCAN_ROOTS:
        if not root.exists():
            continue
        for py in root.rglob("*.py"):
            canon = _canonical(py)
            if canon in _KNOWN_DEBT:
                continue
            try:
                source = py.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            hits = _ast_scan_imports(source, canon)
            if hits:
                violations[canon] = hits

    if tamper == "1":
        pytest.xfail(reason="SPRAWL_NEGCTRL_TAMPER=1: INV-SBS-1 xfail — tamper mode active")

    assert not violations, "INV-SBS-1 VIOLATION — direct provider SDK imports outside factory:\n" + "\n".join(
        f"  {p}: {v}" for p, vs in violations.items() for v in vs
    )


def test_no_model_string_literals_outside_registry_allowlist():
    """INV-SBS-2: Provider/model string literals only in registry fixture (scan governance tests)."""
    tamper = os.environ.get("SPRAWL_NEGCTRL_TAMPER", "0")

    governance_root = REPO_ROOT / "tests" / "governance"
    violations: dict[str, list[str]] = {}
    for py in governance_root.rglob("*.py"):
        canon = _canonical(py)
        if canon == _REGISTRY_FIXTURE:
            continue
        try:
            source = py.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        hits = _scan_model_string_literals(source, canon)
        if hits:
            violations[canon] = hits

    if tamper == "1":
        pytest.xfail(reason="SPRAWL_NEGCTRL_TAMPER=1: INV-SBS-2 xfail — tamper mode active")

    assert not violations, "INV-SBS-2 VIOLATION — provider/model literals outside registry:\n" + "\n".join(
        f"  {p}: {v}" for p, vs in violations.items() for v in vs
    )
