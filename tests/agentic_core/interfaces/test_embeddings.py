"""ADG-hotspot scaffold tests for `agentic_core.interfaces.embeddings` (fanin=10).

Auto-generated speculative scaffold. Module is high fan-in per ADG snapshot
04252026_0843. Verify class/function names against actual module before
treating these as authoritative tests.
"""
from __future__ import annotations

import importlib

import pytest

from agentic_core.interfaces.embeddings import (
    EmbeddingModelProfile,
    EmbeddingProvider,
    EmbeddingRequest,
    EmbeddingVector,
)

MODULE_PATH = "agentic_core.interfaces.embeddings"


def test_module_imports():
    """Smoke: hotspot module must import cleanly (high fan-in regression guard)."""
    mod = importlib.import_module(MODULE_PATH)
    assert mod is not None


def test_module_has_public_surface():
    """Smoke: hotspot module must expose at least one public attribute."""
    mod = importlib.import_module(MODULE_PATH)
    public = [n for n in dir(mod) if not n.startswith("_")]
    assert public, f"{MODULE_PATH} has no public attributes"


def test_module_no_top_level_side_effects():
    """Re-import must be idempotent — no top-level side effects that fail."""
    importlib.import_module(MODULE_PATH)
    importlib.import_module(MODULE_PATH)


@pytest.mark.parametrize("attr_kind", ["class", "function"])
def test_module_exposes_callable(attr_kind):
    """Hotspot modules with high fan-in should expose a callable surface."""
    mod = importlib.import_module(MODULE_PATH)
    has_callable = any(
        callable(getattr(mod, n))
        for n in dir(mod)
        if not n.startswith("_")
    )
    assert has_callable, f"{MODULE_PATH} exposes no callable {attr_kind}"


def test_module_layer_path_matches():
    """Module file path must contain expected layer prefix."""
    mod = importlib.import_module(MODULE_PATH)
    file = getattr(mod, "__file__", "")
    assert "agentic_core" in file.replace("\\", "/"), (
        f"{MODULE_PATH} not under agentic_core: {file}"
    )


def test_provider_neutral_embedding_contract_runtime_checkable() -> None:
    class StaticEmbeddingProvider:
        def embed(self, request: EmbeddingRequest) -> tuple[EmbeddingVector, ...]:
            return (
                EmbeddingVector(
                    text_index=0,
                    vector=(0.1, 0.2, 0.3),
                    profile_id=request.profile.profile_id,
                    dimensions=request.profile.dimensions,
                ),
            )

    profile = EmbeddingModelProfile(
        profile_id="local-small",
        model_ref="model-ref",
        dimensions=3,
        max_batch_size=16,
        local_execution=True,
    )
    request = EmbeddingRequest(texts=("hello",), profile=profile, namespace="test")
    provider = StaticEmbeddingProvider()

    assert isinstance(provider, EmbeddingProvider)
    result = provider.embed(request)
    assert result[0].profile_id == "local-small"
    assert result[0].dimensions == 3
