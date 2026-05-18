"""Contract — W11-W12 R1B derived index and lifecycle."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
_FIXTURES = _REPO / "artifacts" / "apps_rg" / "r1b_semantic_cache" / "w11_w12_fixtures"


@pytest.fixture(scope="module")
def w11_w12_fixtures() -> Path:
    if not (_FIXTURES / "manifest.json").is_file():
        pytest.skip("run tools/apps_rg/emit_r1b_w11_w12_fixtures.py first")
    return _FIXTURES


def test_fixture_manifest(w11_w12_fixtures: Path) -> None:
    manifest = json.loads((w11_w12_fixtures / "manifest.json").read_text(encoding="utf-8"))
    assert manifest.get("wave") == "W11-W12"
    for name in manifest.get("artifacts", []):
        assert (w11_w12_fixtures / name).is_file(), name


def test_derived_index_refresh_artifact(w11_w12_fixtures: Path) -> None:
    data = json.loads((w11_w12_fixtures / "index_refresh_receipt.json").read_text(encoding="utf-8"))
    assert data.get("entries_projected", 0) >= 1
    assert data.get("child_chunks_indexed_as_independent_identities") is False
    assert data.get("c0_fact_vectors_used") is False


def test_child_chunk_not_independent(w11_w12_fixtures: Path) -> None:
    data = json.loads(
        (w11_w12_fixtures / "child_chunk_not_independent.json").read_text(encoding="utf-8")
    )
    assert data.get("child_chunks_independent_index_identities") is False


def test_r1b_vs_c0_separation(w11_w12_fixtures: Path) -> None:
    data = json.loads((w11_w12_fixtures / "r1b_vs_c0_separation.json").read_text(encoding="utf-8"))
    assert data.get("c0_fact_vectors_consulted") is False
    assert data.get("c0_collection_excluded") == "fact_vectors"


def test_w10b_gap_carry_forward(w11_w12_fixtures: Path) -> None:
    data = json.loads(
        (w11_w12_fixtures / "w10b_sidecar_gap_carry_forward.json").read_text(encoding="utf-8")
    )
    assert "core_uwg_commit_receipt_fields" in data or "shim_patches" in data or "carry_forward_wave" in data


def test_lifecycle_accepted_hit(w11_w12_fixtures: Path) -> None:
    data = json.loads((w11_w12_fixtures / "lifecycle_accepted_hit.json").read_text(encoding="utf-8"))
    assert data.get("accepted_hit") is True


def test_lifecycle_miss_and_reject(w11_w12_fixtures: Path) -> None:
    miss = json.loads((w11_w12_fixtures / "lifecycle_miss_fallthrough.json").read_text(encoding="utf-8"))
    reject = json.loads(
        (w11_w12_fixtures / "lifecycle_rejected_candidate.json").read_text(encoding="utf-8")
    )
    assert miss.get("miss_fallthrough") is True
    assert reject.get("rejected_candidate") is True
