"""Embedding invariant contract tests.

Invariants asserted:
  INV-EMB-1: Embedding outputs are informational only and cannot mutate routing/safety state.
  INV-EMB-2: No direct embedding SDK instantiation occurs outside the factory entrypoint.
"""

from __future__ import annotations

import ast
import os
import pathlib

import pytest

pytestmark = pytest.mark.governance

REPO_ROOT = pathlib.Path(__file__).parent.parent.parent
SCAN_ROOTS = [
    REPO_ROOT / "agentic_core",
    REPO_ROOT / "apps_lic",
    REPO_ROOT / "apps_rg",
    REPO_ROOT / "apps_shared",
    REPO_ROOT / "system_learning",
]

_FORBIDDEN_SDK_MODULES = frozenset(
    {
        "openai.embeddings",
        "openai.Embedding",
        "tiktoken",
        "faiss",
        "sentence_transformers",
        "transformers",
    }
)

_FACTORY_ALLOWED_PREFIXES = frozenset(
    {
        "agentic_core/embeddings",
        "system_learning/engines/embedding_service_factory",
        "system_learning/engines/openai_embedder",
        "data/sdks_mcps",
        "tests",
        "ops_scripts",
    }
)

_KNOWN_BYPASS_DEBT = frozenset(
    {
        "agentic_core/L2_execution/healers/vllm_process_manager.py",
        "agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py",
        "apps_shared/utils/late_interaction_reranker_util.py",
    }
)


def _canonical(filepath: pathlib.Path) -> str:
    try:
        return str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(filepath).replace("\\", "/")


def _in_allowed_context(canon: str) -> bool:
    return any(canon.startswith(p) for p in _FACTORY_ALLOWED_PREFIXES)


def _ast_scan_direct_instantiation(source: str, canon: str) -> list[str]:
    if _in_allowed_context(canon):
        return []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    hits: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if any(alias.name == m or alias.name.startswith(m + ".") for m in _FORBIDDEN_SDK_MODULES):
                    hits.append(f"line {node.lineno}: direct SDK import '{alias.name}'")
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if any(mod == m or mod.startswith(m + ".") for m in _FORBIDDEN_SDK_MODULES):
                hits.append(f"line {node.lineno}: direct SDK from-import '{mod}'")
    return hits


def test_embedding_outputs_are_informational_only_non_mutation():
    """INV-EMB-1: EmbeddingResult fields must be informational; no control fields allowed."""
    from system_learning.engines.embedding_service_factory import EmbeddingResult

    result = EmbeddingResult(
        content_hash="abc123",
        score_round6=0.987654,
        row_idx=42,
        embedding_artifact_hash="def456",
    )
    assert hasattr(result, "content_hash"), "content_hash must exist"
    assert hasattr(result, "score_round6"), "score_round6 must exist"
    assert hasattr(result, "embedding_artifact_hash"), "embedding_artifact_hash must exist"

    _CONTROL_FIELDS = (
        "tier_threshold",
        "route_override",
        "safety_bypass",
        "execution_authority",
        "routing_weight",
    )
    for field in _CONTROL_FIELDS:
        assert not hasattr(result, field), f"EmbeddingResult must not have control field '{field}'"

    with pytest.raises(AttributeError):
        result.content_hash = "tampered"  # type: ignore[misc]


def test_no_direct_embedding_client_instantiation_outside_factory():
    """INV-EMB-2: AST scan — no direct SDK embedding imports outside factory."""
    tamper = os.environ.get("SPRAWL_NEGCTRL_TAMPER", "0")

    violations: dict[str, list[str]] = {}
    for root in SCAN_ROOTS:
        if not root.exists():
            continue
        for py in root.rglob("*.py"):
            canon = _canonical(py)
            if canon in _KNOWN_BYPASS_DEBT:
                continue
            try:
                source = py.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            hits = _ast_scan_direct_instantiation(source, canon)
            if hits:
                violations[canon] = hits

    if tamper == "1":
        pytest.xfail(
            strict=True,
            reason="SPRAWL_NEGCTRL_TAMPER=1: INV-EMB-2 xfail — tamper mode active",
        )

    assert not violations, "INV-EMB-2 VIOLATION — direct SDK instantiation outside factory:\n" + "\n".join(
        f"  {p}: {v}" for p, vs in violations.items() for v in vs
    )
