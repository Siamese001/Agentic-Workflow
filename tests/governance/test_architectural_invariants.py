"""
Architectural Invariants Governance Tests

Phase 0: Architectural Invariants & Topology Lock -- HF Embeddings Edition

Acceptance command SSOT:
    python -m pytest -q tests/governance/test_architectural_invariants.py
"""

import ast
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from agentic_core.architecture.architectural_invariants import (
    INVARIANT_C0_ONLY_EMBEDDINGS,
    INVARIANT_EMBEDDING_KILLSWITCH_GLOBAL,
    INVARIANT_EMBEDDING_PROVIDER_PIN,
    INVARIANT_GATEWAY_TOPOLOGY,
    INVARIANT_LAYER_SOVEREIGNTY,
    INVARIANT_REPLAY_KEY_SCHEMA,
    compute_invariant_digest,
    validate_hf_embedder_config,
    validate_replay_key_completeness,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).parent.parent.parent

# L0-L6 layer directories -- the scope of the architectural invariants.
# Provider SDK usage in apps_*, data/, tools/, system_learning/ is handled by
# their own governance; these tests enforce L0-L6 layer sovereignty only.
_LAYER_DIRS = [
    _REPO_ROOT / "agentic_core" / f"L{i}_{name}"
    for i, name in enumerate(
        [
            "routing",
            "cognition",
            "execution",
            "orchestration",
            "state",
            "safety",
            "observability",
        ]
    )
]


def _py_files_in(dirs: list[Path]) -> list[Path]:
    out: list[Path] = []
    for base in dirs:
        if not base.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if not d.startswith(".") and d != "__pycache__"]
            for fn in filenames:
                if fn.endswith(".py"):
                    out.append(Path(dirpath) / fn)
    return out


def _ast_imports(path: Path) -> set[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return set()
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                found.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module)
    return found


def _ast_string_literals(path: Path) -> set[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return set()
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            found.add(node.value)
    return found


# ---------------------------------------------------------------------------
# Digest -- printed once, first test that emits it
# ---------------------------------------------------------------------------

_DIGEST_PRINTED = False


def _print_digest_once() -> str:
    global _DIGEST_PRINTED
    d = compute_invariant_digest()
    if not _DIGEST_PRINTED:
        print(f"\nW0-INVARIANT-DIGEST: {d}", flush=True)
        _DIGEST_PRINTED = True
    return d


# ===========================================================================
# Layer Sovereignty
# ===========================================================================


@pytest.mark.governance
def test_layer_sovereignty_defined():
    assert INVARIANT_LAYER_SOVEREIGNTY is not None
    assert "description" in INVARIANT_LAYER_SOVEREIGNTY
    assert "rules" in INVARIANT_LAYER_SOVEREIGNTY
    assert len(INVARIANT_LAYER_SOVEREIGNTY["rules"]) > 0


@pytest.mark.governance
def test_layer_sovereignty_no_upward_mutation_rule():
    rules = INVARIANT_LAYER_SOVEREIGNTY["rules"]
    assert any("upward mutation" in r.lower() for r in rules)


@pytest.mark.governance
def test_layer_sovereignty_enforcement_defined():
    assert "enforcement" in INVARIANT_LAYER_SOVEREIGNTY


# ===========================================================================
# Gateway Topology
# ===========================================================================


@pytest.mark.governance
def test_gateway_topology_defined():
    assert INVARIANT_GATEWAY_TOPOLOGY is not None
    assert "description" in INVARIANT_GATEWAY_TOPOLOGY
    assert "rules" in INVARIANT_GATEWAY_TOPOLOGY


@pytest.mark.governance
def test_gateway_topology_sole_seam_rule():
    rules = INVARIANT_GATEWAY_TOPOLOGY["rules"]
    assert any("sovereign" in r.lower() or "sole" in r.lower() for r in rules)


@pytest.mark.governance
def test_no_direct_provider_sdk_imports_in_l0_l6():
    """
    L0-L6 layer files must not import provider SDKs (openai, anthropic,
    transformers, torch, tensorflow) directly.
    healing_provider_adapters is the explicitly sanctioned seam file and is
    excluded from this scan.
    """
    forbidden_top = {"openai", "anthropic", "transformers", "torch", "tensorflow"}
    # Sanctioned seam files that are allowed to hold provider SDK imports
    sanctioned_seam_names = {"healing_provider_adapters.py"}
    layer_files = _py_files_in(_LAYER_DIRS)
    violations: list[str] = []
    for fp in layer_files:
        if fp.name in sanctioned_seam_names:
            continue
        for imp in _ast_imports(fp):
            top = imp.split(".")[0]
            if top in forbidden_top:
                violations.append(f"{fp.relative_to(_REPO_ROOT)}: {imp}")
    assert not violations, "Direct provider SDK imports in L0-L6 layers detected:\n" + "\n".join(violations)


@pytest.mark.governance
def test_no_model_literals_in_l0_l6():
    """
    L0-L6 layer files must not contain ad-hoc model string literals.
    Pre-existing sanctioned files (config, types, scripts, gateway agents) that
    reference model IDs for cost/resource purposes are excluded by path fragment.
    """
    forbidden_lits = {"gpt-4", "gpt-3.5-turbo", "claude-3", "text-davinci-003"}
    # Sanctioned path fragments: config layers, type registries, scripts, and
    # gateway agents that legitimately hold model ID constants.
    sanctioned_path_fragments = {
        "config",
        "types",
        "scripts",
        "SovereignMCPGatewayAgent",
        "SubatomicHopAgent",
    }
    layer_files = _py_files_in(_LAYER_DIRS)
    violations: list[str] = []
    for fp in layer_files:
        rel = str(fp.relative_to(_REPO_ROOT)).replace("\\", "/")
        if any(frag in rel for frag in sanctioned_path_fragments):
            continue
        for lit in _ast_string_literals(fp):
            if lit.lower() in forbidden_lits:
                violations.append(f"{rel}: '{lit}'")
    assert not violations, "Model literals in L0-L6 layers:\n" + "\n".join(violations)


# ===========================================================================
# C0-Only Embedding Doctrine
# ===========================================================================


@pytest.mark.governance
def test_c0_only_embeddings_defined():
    assert INVARIANT_C0_ONLY_EMBEDDINGS is not None
    assert "description" in INVARIANT_C0_ONLY_EMBEDDINGS
    assert "rules" in INVARIANT_C0_ONLY_EMBEDDINGS


@pytest.mark.governance
def test_c0_only_no_tier_alteration_rule():
    rules = INVARIANT_C0_ONLY_EMBEDDINGS["rules"]
    assert any("tier" in r.lower() for r in rules)


@pytest.mark.governance
def test_no_openai_embedding_imports_in_l0_l6():
    """L0-L6 layers must not import OpenAI embedding APIs."""
    forbidden = {"openai.embeddings", "openai.Embedding", "openai.EmbeddingAPI"}
    layer_files = _py_files_in(_LAYER_DIRS)
    violations: list[str] = []
    for fp in layer_files:
        for imp in _ast_imports(fp):
            if imp in forbidden:
                violations.append(f"{fp.relative_to(_REPO_ROOT)}: {imp}")
    assert not violations, "OpenAI embedding imports in L0-L6:\n" + "\n".join(violations)


@pytest.mark.governance
def test_routing_l0_l6_no_embedding_metadata_imports():
    """
    Routing/tiering files within L0-L6 must not import embedding *metadata* types.
    (Importing an EmbeddingSovereignAgent class for orchestration is distinct from
    importing raw embedding vector metadata types like EmbeddingResult/EmbeddingVector.)
    """
    forbidden_fragments = {"embeddingresult", "embeddingvector", "embeddingmeta"}
    routing_layer_files = [
        fp for fp in _py_files_in(_LAYER_DIRS) if any(kw in fp.name.lower() for kw in ("routing", "tier"))
    ]
    violations: list[str] = []
    for fp in routing_layer_files:
        for imp in _ast_imports(fp):
            if any(frag in imp.lower() for frag in forbidden_fragments):
                violations.append(f"{fp.relative_to(_REPO_ROOT)}: {imp}")
    assert not violations, "Routing layer files importing embedding metadata types:\n" + "\n".join(violations)


# ===========================================================================
# HF Embedder Pin
# ===========================================================================


@pytest.mark.governance
def test_hf_embedder_pin_defined():
    pin = INVARIANT_EMBEDDING_PROVIDER_PIN
    assert pin is not None
    assert "repo" in pin
    assert "revision" in pin
    assert pin["repo"] == "BAAI/bge-large-en-v1.5"
    assert len(pin["revision"]) == 40


@pytest.mark.governance
def test_hf_embedder_pin_revision_is_hex():
    rev = INVARIANT_EMBEDDING_PROVIDER_PIN["revision"]
    assert all(c in "0123456789abcdef" for c in rev.lower())


@pytest.mark.governance
def test_hf_embedder_config_validation_pass():
    valid = INVARIANT_EMBEDDING_PROVIDER_PIN.copy()
    assert validate_hf_embedder_config(valid) is True


@pytest.mark.governance
def test_hf_embedder_config_validation_fail_wrong_repo():
    bad = INVARIANT_EMBEDDING_PROVIDER_PIN.copy()
    bad["repo"] = "wrong-model"
    assert validate_hf_embedder_config(bad) is False


@pytest.mark.governance
def test_hf_embedder_config_validation_fail_missing_field():
    bad = INVARIANT_EMBEDDING_PROVIDER_PIN.copy()
    del bad["dtype"]
    assert validate_hf_embedder_config(bad) is False


@pytest.mark.governance
def test_hf_embedder_pin_dtype_float32():
    assert INVARIANT_EMBEDDING_PROVIDER_PIN["dtype"] == "float32"


@pytest.mark.governance
def test_hf_embedder_pin_normalize_true():
    assert INVARIANT_EMBEDDING_PROVIDER_PIN["normalize"] is True


@pytest.mark.governance
def test_hf_embedder_pin_device_cpu():
    assert INVARIANT_EMBEDDING_PROVIDER_PIN["device"] == "cpu"


@pytest.mark.governance
def test_hf_embedder_pin_thread_locks():
    tl = INVARIANT_EMBEDDING_PROVIDER_PIN["thread_locks"]
    assert tl["OMP_NUM_THREADS"] == "1"
    assert tl["MKL_NUM_THREADS"] == "1"


# ===========================================================================
# Kill-Switch Propagation
# ===========================================================================


@pytest.mark.governance
def test_embedding_killswitch_defined():
    ks = INVARIANT_EMBEDDING_KILLSWITCH_GLOBAL
    assert ks is not None
    assert "description" in ks
    assert "rules" in ks


@pytest.mark.governance
def test_killswitch_no_silent_fallback_rule():
    rules = INVARIANT_EMBEDDING_KILLSWITCH_GLOBAL["rules"]
    assert any("silent" in r.lower() or "fallback" in r.lower() for r in rules)


class _MockEmbeddingService:
    def __init__(self, enabled: bool) -> None:
        self.enabled = enabled

    def get_embeddings(self, texts: list[str]) -> list[list[float]]:
        if not self.enabled:
            raise RuntimeError("Embedding service is disabled")
        return [[0.1, 0.2, 0.3] for _ in texts]

    @classmethod
    def from_env(cls) -> "_MockEmbeddingService":
        return cls(os.environ.get("EMBEDDING_ENABLED", "true").lower() == "true")


@pytest.mark.governance
def test_killswitch_enabled_allows_retrieval():
    with patch.dict(os.environ, {"EMBEDDING_ENABLED": "true"}):
        svc = _MockEmbeddingService.from_env()
    assert svc.enabled is True
    assert len(svc.get_embeddings(["hello"])) == 1


@pytest.mark.governance
def test_killswitch_disabled_blocks_retrieval():
    with patch.dict(os.environ, {"EMBEDDING_ENABLED": "false"}):
        svc = _MockEmbeddingService.from_env()
    assert svc.enabled is False
    with pytest.raises(RuntimeError, match="Embedding service is disabled"):
        svc.get_embeddings(["hello"])


# ===========================================================================
# Replay Key Schema
# ===========================================================================


@pytest.mark.governance
def test_replay_key_schema_defined():
    schema = INVARIANT_REPLAY_KEY_SCHEMA
    assert schema is not None
    assert "required_fields" in schema
    assert len(schema["required_fields"]) > 0


@pytest.mark.governance
def test_replay_key_completeness_valid():
    fields = INVARIANT_REPLAY_KEY_SCHEMA["required_fields"]
    assert validate_replay_key_completeness({f: f"v_{f}" for f in fields}) is True


@pytest.mark.governance
def test_replay_key_completeness_missing_last():
    fields = INVARIANT_REPLAY_KEY_SCHEMA["required_fields"]
    assert validate_replay_key_completeness({f: f"v_{f}" for f in fields[:-1]}) is False


@pytest.mark.governance
def test_replay_key_completeness_empty():
    assert validate_replay_key_completeness({}) is False


@pytest.mark.governance
def test_replay_key_essential_fields_present():
    required = INVARIANT_REPLAY_KEY_SCHEMA["required_fields"]
    for field in (
        "embedder_repo",
        "embedder_revision",
        "tokenizer_revision",
        "embedding_dim",
        "dtype",
        "normalize_flag",
        "generation_model_id",
    ):
        assert field in required, f"Essential replay-key field missing: {field}"


# ===========================================================================
# Deterministic Digest
# ===========================================================================


@pytest.mark.governance
def test_w0_invariant_digest_deterministic():
    d1 = compute_invariant_digest()
    d2 = compute_invariant_digest()
    assert d1 == d2
    assert len(d1) == 64
    assert all(c in "0123456789abcdef" for c in d1)


@pytest.mark.governance
def test_w0_invariant_digest_printed():
    """Prints W0-INVARIANT-DIGEST once to stdout (captured by -s flag)."""
    digest = _print_digest_once()
    assert len(digest) == 64


# ===========================================================================
# Comprehensive gate
# ===========================================================================


@pytest.mark.governance
def test_architectural_invariants_comprehensive():
    digest = _print_digest_once()
    assert len(digest) == 64

    for inv in (
        INVARIANT_LAYER_SOVEREIGNTY,
        INVARIANT_GATEWAY_TOPOLOGY,
        INVARIANT_C0_ONLY_EMBEDDINGS,
        INVARIANT_EMBEDDING_PROVIDER_PIN,
        INVARIANT_EMBEDDING_KILLSWITCH_GLOBAL,
        INVARIANT_REPLAY_KEY_SCHEMA,
    ):
        assert inv is not None
        assert "description" in inv

    assert validate_hf_embedder_config(INVARIANT_EMBEDDING_PROVIDER_PIN)
    sample = {f: f"s_{f}" for f in INVARIANT_REPLAY_KEY_SCHEMA["required_fields"]}
    assert validate_replay_key_completeness(sample)


# ===========================================================================
# Negative Control  (W0_NEGCTRL_TAMPER=1)
# ===========================================================================


@pytest.mark.governance
def test_negative_control_embedder_repo_tamper():
    """
    W0_NEGCTRL_TAMPER=1  -> simulate forbidden repo mismatch, confirm
                             validate_hf_embedder_config returns False,
                             then call pytest.xfail() -> XFAIL, exit 0.
    No env var           -> normal path: valid config must return True (PASS).
    """
    if os.environ.get("W0_NEGCTRL_TAMPER") == "1":
        tampered = INVARIANT_EMBEDDING_PROVIDER_PIN.copy()
        tampered["repo"] = "tampered-model/forbidden"
        result = validate_hf_embedder_config(tampered)
        assert result is False, "Tampered config unexpectedly passed validation"
        pytest.xfail("W0_NEGCTRL_TAMPER=1: embedder repo mismatch violation confirmed -- XFAIL")
    else:
        assert validate_hf_embedder_config(INVARIANT_EMBEDDING_PROVIDER_PIN) is True
