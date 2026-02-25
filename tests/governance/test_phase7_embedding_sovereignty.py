"""Phase 7: Embedding Sovereignty & Kill-Switch Enforcement

Tests for:
- Single embedding factory seam enforcement
- EMBEDDING_ENABLED kill-switch (fail-closed)
- AST bypass scanner for embedding SDK imports
- W7-EMBEDDING-SOVEREIGNTY-DIGEST determinism
- W7_NEGCTRL_TAMPER negative control
"""

import ast
import hashlib
import json
import os
import pathlib
import pytest
from typing import Any, Dict, List, Set

pytestmark = pytest.mark.unit_min_deps

# Test infrastructure
REPO_ROOT = pathlib.Path(__file__).parent.parent.parent
SCAN_ROOTS = [
    REPO_ROOT / "agentic_core",
    REPO_ROOT / "apps_lic",
    REPO_ROOT / "apps_rg",
    REPO_ROOT / "apps_shared",
    REPO_ROOT / "system_learning",
]

# Forbidden embedding SDK imports
FORBIDDEN_EMBEDDING_IMPORTS = {
    # Direct SDK imports
    "openai",
    "anthropic", 
    "google.generativeai",
    "sentence_transformers",
    "transformers",
    "vllm",
    # Embedding-specific imports
    "sentence_transformers.SentenceTransformer",
    "transformers.AutoModel",
    "transformers.AutoTokenizer",
    "openai.embeddings",
    "anthropic.embeddings",
    "google.generativeai.embeddings",
}

# Allowlisted modules that can import embedding SDKs
ALLOWLISTED_EMBEDDING_MODULES = {
    "agentic_core.embeddings.embedding_factory",
    "data.sdks_mcps.client_wrappers",
    "agentic_core.L2_execution.reasoning.EmbeddingSovereignAgent",
    "system_learning.engines.embedding_service_factory",
}

# Known embedding debt (baseline)
KNOWN_EMBEDDING_DEBT = {
    "tests/unit_min_deps/system_learning/test_openai_embedder_stub_b5.py",
    "tests/integration_full_deps/system_learning/test_seed_pack_full_build_b5.py",
    "system_learning/engines/openai_embedder.py",
    "system_learning/engines/seed_pack_build_cli.py",
    "ops_scripts/ci/audit_embedding_surface.py",
    "ops_scripts/general/ast_import_audit.py",
    "data/sdks_mcps/reference_clients/minimal_anthropic.py",
    "data/sdks_mcps/client_wrappers/openai_client.py",
    "apps_shared/utils/late_interaction_reranker_util.py",
    "apps_shared/utils/providers_google_genai_client_util.py",
    "agentic_core/L2_execution/healers/healing_provider_adapters.py",
    "apps_rg/utils/providers_anthropic_client_util.py",
    "apps_rg/utils/deep_brain_harvester_util.py",
    "apps_rg/tools/ResumeGenerator.py",
    "apps_rg/reasoning/HardenedopenaiexecutorStrategy.py",
    "apps_rg/enforcement/HardenedanthropicexecutorStrategy.py",
    "agentic_core/architecture/embedding_allowlist.py",
}

KNOWN_EMBEDDING_DEBT_CEILING = len(KNOWN_EMBEDDING_DEBT)


def _canonical_path(filepath: pathlib.Path) -> str:
    """Convert absolute path to canonical repo-relative path."""
    try:
        rel = filepath.relative_to(REPO_ROOT)
        return str(rel).replace("\\", "/")
    except ValueError:
        return str(filepath).replace("\\", "/")


def _collect_py_files(roots: List[pathlib.Path]) -> List[pathlib.Path]:
    """Collect all Python files from scan roots."""
    py_files = []
    for root in roots:
        if root.exists():
            py_files.extend(root.rglob("*.py"))
    return py_files


def _ast_has_forbidden_embedding_imports(source: str, filepath: str) -> List[str]:
    """Check if AST contains forbidden embedding imports."""
    violations = []
    
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return ["SYNTAX_ERROR"]
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in FORBIDDEN_EMBEDDING_IMPORTS:
                    violations.append(f"line {node.lineno}: import {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                module = node.module
                # Check for partial matches
                for forbidden in FORBIDDEN_EMBEDDING_IMPORTS:
                    if module == forbidden or module.startswith(forbidden + "."):
                        violations.append(f"line {node.lineno}: from {module}")
                        break
                    # Check if any imported name matches
                    for alias in node.names:
                        full_name = f"{module}.{alias.name}" if module else alias.name
                        if full_name in FORBIDDEN_EMBEDDING_IMPORTS:
                            violations.append(f"line {node.lineno}: from {full_name}")
                            break
    
    return violations


# ---------------------------------------------------------------------------
# T1: Single Embedding Factory Enforcement
# ---------------------------------------------------------------------------

def test_embedding_factory_exists_and_is_importable():
    """Verify embedding factory exists and can be imported."""
    from agentic_core.embeddings.embedding_factory import (
        create_embedding_client,
        get_embedding_client,
        EMBEDDING_ENABLED,
        EmbeddingDisabledError,
        EmbeddingSovereigntyViolationError,
    )
    
    # Verify module structure
    assert callable(create_embedding_client)
    assert callable(get_embedding_client)
    assert isinstance(EMBEDDING_ENABLED, bool)
    assert EmbeddingDisabledError is not None
    assert EmbeddingSovereigntyViolationError is not None


def test_embedding_factory_kill_switch_fails_closed():
    """EMBEDDING_ENABLED=false must raise EmbeddingDisabledError."""
    # Save original state
    original_enabled = os.environ.get("EMBEDDING_ENABLED", "true")
    
    try:
        # Set kill-switch
        os.environ["EMBEDDING_ENABLED"] = "false"
        
        # Clear module cache to reload
        import importlib
        import agentic_core.embeddings.embedding_factory
        importlib.reload(agentic_core.embeddings.embedding_factory)
        
        from agentic_core.embeddings.embedding_factory import (
            create_embedding_client,
            EmbeddingDisabledError,
        )
        
        # Should raise
        with pytest.raises(EmbeddingDisabledError, match="EMBEDDING_ENABLED=false"):
            create_embedding_client("openai")
            
    finally:
        # Restore original state
        os.environ["EMBEDDING_ENABLED"] = original_enabled
        # Clear module cache again
        importlib.reload(agentic_core.embeddings.embedding_factory)


def test_embedding_factory_registration_tracking():
    """Factory must track registered clients."""
    from agentic_core.embeddings.embedding_factory import (
        create_embedding_client,
        get_embedding_client,
        _embedding_client_registry,
    )
    
    # Clear registry
    _embedding_client_registry.clear()
    
    # Create client (should register)
    client = create_embedding_client("openai", "text-embedding-ada-002")
    assert "openai_text-embedding-ada-002" in _embedding_client_registry
    
    # Retrieve client
    retrieved = get_embedding_client("openai_text-embedding-ada-002")
    assert retrieved is client


# ---------------------------------------------------------------------------
# T2: AST Bypass Scanner
# ---------------------------------------------------------------------------

def test_embedding_ast_bypass_scanner_finds_known_debt():
    """AST scan must find known embedding debt violations."""
    py_files = _collect_py_files(SCAN_ROOTS)
    violations_by_file: Dict[str, List[str]] = {}
    
    for filepath in py_files:
        canon = _canonical_path(filepath)
        
        # Skip allowlisted paths
        if any(canon.startswith(allowed) for allowed in ALLOWLISTED_EMBEDDING_MODULES):
            continue
        
        try:
            source = filepath.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        
        violations = _ast_has_forbidden_embedding_imports(source, canon)
        if violations:
            violations_by_file[canon] = violations
    
    # Check known debt
    found_count = len(violations_by_file)
    ceiling = KNOWN_EMBEDDING_DEBT_CEILING
    delta = found_count - ceiling
    
    # Print governance signal
    print(
        f"\nEMBEDDING-DEBT: found={found_count}, ceiling={ceiling}, delta={delta}"
    )
    for path, viols in sorted(violations_by_file.items()):
        for v in viols:
            print(f"  {'[KNOWN]' if path in KNOWN_EMBEDDING_DEBT else '[NEW!]'} {path}: {v}")
    
    # Detect unknown violations
    unknown_violations = sorted(
        path for path in violations_by_file if path not in KNOWN_EMBEDDING_DEBT
    )
    if unknown_violations:
        lines = ["NEW EMBEDDING VIOLATIONS:"]
        for path in unknown_violations:
            for v in violations_by_file[path]:
                lines.append(f"  {path}: {v}")
        pytest.fail("\n".join(lines))
    
    # Enforce non-growing ceiling
    assert found_count <= ceiling, (
        f"EMBEDDING-DEBT ceiling exceeded: found={found_count}, ceiling={ceiling}, delta={delta}"
    )


def test_embedding_allowlisted_modules_exist():
    """All allowlisted embedding modules must exist."""
    missing = []
    for module_path in ALLOWLISTED_EMBEDDING_MODULES:
        # Convert module path to file path
        file_path = REPO_ROOT / module_path.replace(".", "/")
        if not file_path.exists():
            # Try with .py extension
            if not (file_path.with_suffix(".py")).exists():
                missing.append(module_path)
    
    assert not missing, f"Missing allowlisted modules: {missing}"


# ---------------------------------------------------------------------------
# T3: W7 Digest Determinism
# ---------------------------------------------------------------------------

def test_w7_digest_is_computed_and_stable():
    """W7-EMBEDDING-SOVEREIGNTY-DIGEST must be computable and stable."""
    from agentic_core.embeddings.embedding_factory import compute_w7_sovereignty_digest
    
    # Compute digest
    digest1 = compute_w7_sovereignty_digest()
    
    # Verify format (hex string)
    assert len(digest1) == 64
    assert all(c in "0123456789abcdef" for c in digest1)
    
    # Compute again (should be identical)
    digest2 = compute_w7_sovereignty_digest()
    assert digest1 == digest2, "W7 digest must be stable across calls"


def test_w7_digest_changes_with_factory_state():
    """W7 digest must change when factory state changes."""
    from agentic_core.embeddings.embedding_factory import (
        compute_w7_sovereignty_digest,
        _embedding_client_registry,
    )
    
    # Clear registry and compute baseline
    _embedding_client_registry.clear()
    baseline_digest = compute_w7_sovereignty_digest()
    
    # Register a client and compute new digest
    _embedding_client_registry["test_client"] = "mock_client"
    new_digest = compute_w7_sovereignty_digest()
    
    # Digests must differ
    assert baseline_digest != new_digest, "W7 digest must change with factory state"
    
    # Clean up
    _embedding_client_registry.clear()


# ---------------------------------------------------------------------------
# T4: Negative Control (W7_NEGCTRL_TAMPER)
# ---------------------------------------------------------------------------

@pytest.mark.xfail(strict=True, reason="W7_NEGCTRL_TAMPER=1 must xfail; restore run must pass")
def test_w7_negative_control_tamper_detection():
    """When W7_NEGCTRL_TAMPER=1, injecting bypass must trigger guard."""
    tamper = os.environ.get("W7_NEGCTRL_TAMPER", "0")
    
    if tamper != "1":
        pytest.skip("W7_NEGCTRL_TAMPER not set — restore run, skipping tamper body")
    
    # Tamper: attempt to create embedding client outside factory
    from agentic_core.embeddings.embedding_factory import guard_embedding_instantiation
    
    caught = False
    try:
        guard_embedding_instantiation("forbidden.module", "EmbeddingClient")
    except EmbeddingSovereigntyViolationError:
        caught = True
    
    # Guard triggered as expected - now deliberately fail to produce xfail
    assert not caught, "NEGCTRL: guard triggered as expected (intentional fail)"


@pytest.mark.xfail(strict=True, reason="W7_NEGCTRL_TAMPER=1 must xfail; restore run must pass")
def test_w7_full_embedding_sovereignty_system():
    """Full embedding sovereignty system test."""
    tamper = os.environ.get("W7_NEGCTRL_TAMPER", "0")
    
    if tamper != "1":
        pytest.skip("W7_NEGCTRL_TAMPER not set — restore run, skipping tamper body")
    
    # Tamper: simulate embedding operation while disabled
    # Clear module cache to ensure new EMBEDDING_ENABLED value is read
    import importlib
    import agentic_core.embeddings.embedding_factory
    importlib.reload(agentic_core.embeddings.embedding_factory)
    
    original_enabled = os.environ.get("EMBEDDING_ENABLED", "true")
    os.environ["EMBEDDING_ENABLED"] = "false"
    
    # Reload module again to pick up new env var
    importlib.reload(agentic_core.embeddings.embedding_factory)
    
    caught = False
    try:
        from agentic_core.embeddings.embedding_factory import create_embedding_client, EmbeddingDisabledError
        create_embedding_client("openai")
    except EmbeddingDisabledError:
        caught = True
    finally:
        os.environ["EMBEDDING_ENABLED"] = original_enabled
        importlib.reload(agentic_core.embeddings.embedding_factory)
    
    assert not caught, "NEGCTRL: kill-switch triggered as expected (intentional fail)"


# ---------------------------------------------------------------------------
# T5: Integration Tests
# ---------------------------------------------------------------------------

def test_embedding_factory_integration_with_sovereign_agent():
    """Embedding factory must integrate with EmbeddingSovereignAgent."""
    try:
        from agentic_core.L2_execution.reasoning.EmbeddingSovereignAgent import (
            get_embedding_gateway,
        )
        from agentic_core.embeddings.embedding_factory import EMBEDDING_ENABLED
        
        # Should be able to get gateway when enabled
        if EMBEDDING_ENABLED:
            gateway = get_embedding_gateway()
            assert gateway is not None
        else:
            # Should raise when disabled
            with pytest.raises(Exception):
                get_embedding_gateway()
                
    except ImportError:
        pytest.skip("EmbeddingSovereignAgent not available")


def test_no_direct_embedding_sdk_instantiation():
    """Runtime guard must prevent direct SDK instantiation."""
    from agentic_core.embeddings.embedding_factory import (
        guard_embedding_instantiation,
        EmbeddingSovereigntyViolationError,
    )
    
    # Test that truly forbidden modules raise
    with pytest.raises(EmbeddingSovereigntyViolationError, match="EMBEDDING_SOVEREIGNTY_VIOLATION"):
        guard_embedding_instantiation("forbidden.embedding.module", "EmbeddingClient")
    
    # Test specific allowlisted modules that should not raise
    truly_allowlisted = {
        "agentic_core.embeddings.embedding_factory",
        "data.sdks_mcps.client_wrappers",
        "agentic_core.L2_execution.reasoning.EmbeddingSovereignAgent",
        "system_learning.engines.embedding_service_factory",
    }
    
    for allowed in truly_allowlisted:
        try:
            guard_embedding_instantiation(allowed, "SomeClass")
        except EmbeddingSovereigntyViolationError:
            pytest.fail(f"Allowlisted module {allowed} should not raise violation")
