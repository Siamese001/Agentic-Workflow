"""ADG-hotspot scaffold tests for `agentic_core.L2_execution.config.hybrid_retriever_config` (fanin=1, band=P4).

Auto-generated speculative scaffold. Verify class/function names against actual
module before extending these scaffolds with behavioral assertions.
"""
from __future__ import annotations

import importlib
from pathlib import Path

import pytest

from agentic_core.L2_execution.config.ingestion_snapshot import IngestionLoadRequestV1, IngestionSnapshotError
from ops_scripts.apps_rg.package_source_snapshots import (
    publish_active_config_snapshot,
    publish_ingestion_snapshot,
)


MODULE_PATH = "agentic_core.L2_execution.config.hybrid_retriever_config"


def test_module_imports():
    mod = importlib.import_module(MODULE_PATH)
    assert mod is not None


def test_module_has_public_surface():
    mod = importlib.import_module(MODULE_PATH)
    public = [n for n in dir(mod) if not n.startswith("_")]
    assert public, f"{MODULE_PATH} has no public attributes"


def test_module_no_top_level_side_effects():
    importlib.import_module(MODULE_PATH)
    importlib.import_module(MODULE_PATH)


@pytest.mark.parametrize("attr_kind", ["class", "function"])
def test_module_exposes_callable(attr_kind):
    mod = importlib.import_module(MODULE_PATH)
    has_callable = any(
        callable(getattr(mod, n))
        for n in dir(mod)
        if not n.startswith("_")
    )
    assert has_callable, f"{MODULE_PATH} exposes no callable {attr_kind}"


def test_module_layer_path_matches():
    mod = importlib.import_module(MODULE_PATH)
    file = getattr(mod, "__file__", "")
    assert "agentic_core" in file.replace("\\", "/"), (
        f"{MODULE_PATH} not under agentic_core: {file}"
    )


class _VectorStore:
    async def similarity_search(self, _query, top_k=12):
        return []


class _Guardrail:
    async def rerank_documents(self, candidates, _query, top_k=12):
        return candidates[:top_k]


def _request(tmp_path: Path) -> IngestionLoadRequestV1:
    components = {}
    for name in ("budget", "model", "policy", "routing"):
        path = tmp_path / f"{name}.cfg"
        path.write_bytes(name.encode("ascii"))
        components[name] = path
    config_root = tmp_path / "config"
    publish_active_config_snapshot(
        component_paths=components,
        output_root=config_root,
        selected_profile_id="apps-rg-test",
        snapshot_boundary_id="run-001",
    )
    payload = tmp_path / "payload.json"
    payload.write_bytes(b'{"chunks":[{"metadata":{},"text":"alpha beta"}]}')
    ingestion_root = tmp_path / "ingestion"
    receipt = publish_ingestion_snapshot(
        payload_path=payload,
        output_root=ingestion_root,
        input_schema_version="chunks/v1",
        active_config_root=config_root,
        selected_profile_id="apps-rg-test",
        snapshot_boundary_id="run-001",
    )
    return IngestionLoadRequestV1(
        snapshot_root=ingestion_root,
        expected_input_digest=receipt.input_digest,
        expected_configuration_digest=receipt.configuration_digest,
        expected_input_schema_version="chunks/v1",
        expected_generation_id=receipt.generation_id,
    )


@pytest.mark.asyncio
async def test_hybrid_retriever_loads_only_from_explicit_snapshot(tmp_path):
    retriever = importlib.import_module(MODULE_PATH).HybridRetriever(
        _VectorStore(),
        _Guardrail(),
        ingestion_snapshot_request=_request(tmp_path),
    )
    await retriever._load_local_index()
    assert retriever.local_chunks == [{"metadata": {}, "text": "alpha beta"}]
    assert retriever.index_ready.is_set()


@pytest.mark.asyncio
async def test_hybrid_retriever_fails_closed_without_snapshot():
    retriever = importlib.import_module(MODULE_PATH).HybridRetriever(_VectorStore(), _Guardrail())
    with pytest.raises(IngestionSnapshotError, match="REBUILD_REQUIRED"):
        await retriever._load_local_index()
