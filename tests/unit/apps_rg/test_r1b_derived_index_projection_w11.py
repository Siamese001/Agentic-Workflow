"""W11 — derived R1B index projection from UWG-admitted durable truth."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.cache.r1b_constants import C0_FACT_VECTORS_COLLECTION
from apps_rg.cache.r1b_derived_index import (
    EXCLUDED_FROM_INDEX,
    INDEXED_FIELDS,
    derived_index_available,
    list_derived_index_record_ids,
    load_derived_index_entry,
    project_durable_to_derived_index,
)
from apps_rg.cache.r1b_uwg_gateway_shim import AppsRgR1BUwgGateway
from apps_rg.cache.r1b_store import R1BSemanticCacheStore
from apps_rg.cache.r1b_uwg_promotion import promote_and_project_r1b_cache
from tests.unit.apps_rg.test_r1b_uwg_durable_persistence_w10 import _candidate


def _promote(tmp_path: Path) -> str:
    cand = _candidate(tmp_path)
    store = R1BSemanticCacheStore(tmp_path / "proj")
    outcome = promote_and_project_r1b_cache(
        candidate=cand,
        projection_root=store.root,
        gateway=AppsRgR1BUwgGateway(),
    )
    assert outcome.status == "ADMITTED"
    return cand.record.record_id


def test_derived_index_refresh_after_admission(tmp_path: Path) -> None:
    rec_id = _promote(tmp_path)
    root = tmp_path / "proj"
    assert derived_index_available(root)
    assert rec_id in list_derived_index_record_ids(root)


def test_index_only_intent_vectors_not_chunks(tmp_path: Path) -> None:
    rec_id = _promote(tmp_path)
    root = tmp_path / "proj"
    vec_dir = root / "derived_index" / "intent_vectors"
    assert vec_dir.is_dir()
    assert not (vec_dir / "hoc_w10_1.json").exists()
    entry = load_derived_index_entry(root, rec_id)
    assert entry is not None
    assert entry.get("child_chunks_independent_index_identities") is False
    assert entry.get("c0_fact_vectors_consulted") is False
    assert entry.get("c0_collection_excluded") == C0_FACT_VECTORS_COLLECTION


def test_projection_receipt_fields(tmp_path: Path) -> None:
    _promote(tmp_path)
    root = tmp_path / "proj"
    receipt = project_durable_to_derived_index(root)
    assert receipt.entries_projected >= 1
    assert receipt.child_chunks_indexed_as_independent_identities is False
    assert receipt.c0_fact_vectors_used is False
    assert set(receipt.indexed_fields) == set(INDEXED_FIELDS)
    assert "chunk_id_as_lookup_key" in EXCLUDED_FROM_INDEX


def test_durable_bundle_is_truth_source(tmp_path: Path) -> None:
    rec_id = _promote(tmp_path)
    root = tmp_path / "proj"
    bundle = json.loads(
        (root / "durable" / "uwg_admitted" / "intents" / f"{rec_id}.json").read_text(encoding="utf-8")
    )
    assert bundle.get("storage_tier") == "uwg_admitted_durable_projection"
    entry = load_derived_index_entry(root, rec_id)
    assert entry.get("durable_bundle_ref", "").endswith(f"{rec_id}.json")
