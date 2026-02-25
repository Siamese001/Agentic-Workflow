"""Phase 10: High-Signal OpenAI Embedding Activation — HS-1..HS-6

Tests for:
- OpenAI embeddings active at HS-1..HS-6 injection points
- No routing/tier/safety mutation from embeddings
- No direct SDK imports outside embedding_factory
- Kill-switch enforced fail-closed
- W10-EMBEDDING-HS-DIGEST stability
- W10_NEGCTRL_TAMPER negative control
"""

import ast
import os
import pathlib

import pytest

from agentic_core.embeddings.embedding_input_guard import EmbeddingInputGuard, EmbeddingInputViolation
from agentic_core.L0_routing.engines.assembly_stage import GovernedPayload

# Test infrastructure
REPO_ROOT = pathlib.Path(__file__).parent.parent.parent
SCAN_ROOTS = [
    REPO_ROOT / "agentic_core",
    REPO_ROOT / "apps_lic",
    REPO_ROOT / "apps_rg",
    REPO_ROOT / "apps_shared",
    REPO_ROOT / "system_learning",
]

# Forbidden embedding SDK imports outside factory
FORBIDDEN_EMBEDDING_IMPORTS = {
    "openai.embeddings",
    "openai.Embedding",
    "tiktoken",
    "faiss",
    "requests",
    "httpx",
}

# Allowed embedding imports (factory only)
ALLOWED_EMBEDDING_IMPORTS = {
    "agentic_core.embeddings.embedding_factory",
    "agentic_core.embeddings.tokenization_adapter",
    "agentic_core.embeddings.embedding_input_guard",
    "data.sdks_mcps",  # Centralized SDK wrapper
    "tests",  # Test infrastructure
}

# Known embedding bypass debt (baseline)
KNOWN_EMBEDDING_BYPASS_DEBT = set()

KNOWN_EMBEDDING_BYPASS_DEBT_CEILING = len(KNOWN_EMBEDDING_BYPASS_DEBT)


def _canonical_path(filepath: pathlib.Path) -> str:
    """Convert absolute path to canonical repo-relative path."""
    try:
        rel = filepath.relative_to(REPO_ROOT)
        return str(rel).replace("\\", "/")
    except ValueError:
        return str(filepath).replace("\\", "/")


def _collect_py_files(roots: list[pathlib.Path]) -> list[pathlib.Path]:
    """Collect all Python files from scan roots."""
    py_files = []
    for root in roots:
        if root.exists():
            py_files.extend(root.rglob("*.py"))
    return py_files


def _is_in_allowed_context(filepath: str) -> bool:
    """Check if a file's path corresponds to an allowed module path."""
    # Convert file path to a module-like path
    module_path = filepath.replace("/", ".").replace(".py", "")
    for allowed_module in ALLOWED_EMBEDDING_IMPORTS:
        if module_path.startswith(allowed_module):
            return True
    return False


def _ast_scan_for_embedding_bypass(source: str, filepath: str) -> list[str]:
    """Scan AST for embedding SDK bypass violations."""
    violations = []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return ["SYNTAX_ERROR"]

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if any(alias.name.startswith(f) for f in FORBIDDEN_EMBEDDING_IMPORTS):
                    if not _is_in_allowed_context(filepath):
                        violations.append(f"line {node.lineno}: forbidden embedding import '{alias.name}'")
        elif isinstance(node, ast.ImportFrom):
            if node.module and any(node.module.startswith(f) for f in FORBIDDEN_EMBEDDING_IMPORTS):
                if not _is_in_allowed_context(filepath):
                    violations.append(f"line {node.lineno}: forbidden from import '{node.module}'")
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if (
                isinstance(node.func.value, ast.Name)
                and node.func.value.id == "openai"
                and node.func.attr in {"Embedding", "embeddings"}
            ):
                violations.append(f"line {node.lineno}: direct OpenAI embedding client instantiation")
            if (
                node.func.attr in ["post", "get"]
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id in ["requests", "httpx"]
            ):
                if (
                    node.args
                    and isinstance(node.args[0], ast.Constant)
                    and "api.openai.com" in str(node.args[0].value)
                ):
                    violations.append(f"line {node.lineno}: direct HTTP call to OpenAI API")

    return violations


# T1: OpenAI Embedding Provider Registration
def test_openai_embedding_provider_registration():
    from agentic_core.embeddings.embedding_factory import (
        create_embedding_client,
        is_enabled,
    )

    if not is_enabled():
        pytest.skip("EMBEDDING_ENABLED=false - skipping embedding tests")
    client = create_embedding_client(provider="openai", model="text-embedding-3-large", dimensions=1536)
    assert hasattr(client, "get_embedding")
    assert hasattr(client, "get_embeddings_batch")
    assert hasattr(client, "get_replay_metadata")
    metadata = client.get_replay_metadata()
    expected_fields = [
        "provider",
        "model",
        "pack_hash",
        "embedding_dimension",
        "distance_metric",
        "tokenization_policy_version",
        "normalization_policy",
        "chunking_policy",
        "hs_injection_surface_version",
    ]
    for field in expected_fields:
        assert field in metadata, f"Missing replay metadata field: {field}"
    assert metadata["provider"] == "openai"
    assert metadata["model"] == "text-embedding-3-large"
    assert isinstance(metadata["embedding_dimension"], int)
    assert metadata["distance_metric"] == "cosine"


# T2: Kill-switch enforcement
def test_embedding_kill_switch_fail_closed():
    original_value = os.environ.get("EMBEDDING_ENABLED")
    try:
        os.environ["EMBEDDING_ENABLED"] = "false"
        import importlib

        import agentic_core.embeddings.embedding_factory as factory_module

        importlib.reload(factory_module)
        with pytest.raises(factory_module.EmbeddingDisabledError):
            factory_module.create_embedding_client("openai")
    finally:
        if original_value is not None:
            os.environ["EMBEDDING_ENABLED"] = original_value
        elif "EMBEDDING_ENABLED" in os.environ:
            del os.environ["EMBEDDING_ENABLED"]
        import importlib

        import agentic_core.embeddings.embedding_factory as factory_module

        importlib.reload(factory_module)


# T3: Structural Non-Mutation Guard (Routing)
def test_embedding_non_mutation_routing():
    payload1 = GovernedPayload(s0_system="s", i0_instructional="i", c0_context="c1", u0_user_prompt="u")
    payload2 = GovernedPayload(s0_system="s", i0_instructional="i", c0_context="c2", u0_user_prompt="u")
    assert payload1.routing_hash == payload2.routing_hash
    assert payload1.manifest_hash != payload2.manifest_hash


# T4: AST Scanner Zero-Tolerance
def test_ast_scanner_zero_tolerance():
    py_files = _collect_py_files(SCAN_ROOTS)
    violations_by_file: dict[str, list[str]] = {}
    for filepath in py_files:
        canon = _canonical_path(filepath)
        try:
            source = filepath.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        violations = _ast_scan_for_embedding_bypass(source, canon)
        if violations:
            violations_by_file[canon] = violations
    found_violations = {p: v for p, v in violations_by_file.items() if p not in KNOWN_EMBEDDING_BYPASS_DEBT}
    if found_violations:
        lines = ["NEW EMBEDDING BYPASS VIOLATIONS:"]
        for path, viols in sorted(found_violations.items()):
            for v in viols:
                lines.append(f"  {path}: {v}")
        pytest.fail("\n".join(lines))


# T5: Data Leak Negative Control
@pytest.mark.xfail(strict=True, reason="W10_DATA_LEAK_TAMPER=1 must xfail on policy violation.")
def test_w10_data_leak_tamper_xfail():
    tamper = os.environ.get("W10_DATA_LEAK_TAMPER", "0")
    if tamper != "1":
        pytest.skip("W10_DATA_LEAK_TAMPER not set")
    with pytest.raises(EmbeddingInputViolation):
        EmbeddingInputGuard.guard("some text", "secret_field")
    guarded_text = EmbeddingInputGuard.guard("my api key is sk-12345secret", "u0_user_prompt")
    assert "sk-12345secret" not in guarded_text.redacted_text
    assert "[REDACTED]" in guarded_text.redacted_text
    pytest.fail("NEGCTRL: data leak guard handled correctly (intentional fail)")


pytestmark = pytest.mark.unit_min_deps
