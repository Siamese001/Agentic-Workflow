"""W3 deferred fact-vector promotion tests."""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from apps_rg.runtime.c0.constants import PROOF_ELIGIBLE
from apps_rg.runtime.c0.fact_vector_write_back import (
    GENERATED,
    PROMOTION_MODE_DEFERRED,
    PROMOTION_MODE_ENV,
    PROMOTION_MODE_INLINE,
)


def _grounded_atom(**overrides: object) -> dict[str, object]:
    atom = {
        "fact_id": "fact_deferred_001",
        "confidence": "HIGH",
        "proof_status": PROOF_ELIGIBLE,
        "source_type": "candidate_fact_ledger",
        "source_span_ref": "ledger:fact_deferred_001",
        "text_to_embed": "Grounded evidence claim with enough detail for fact-vector staging.",
    }
    atom.update(overrides)
    return atom


def _patch_embedding_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    import apps_rg.runtime.embedding_settings as embedding_settings

    monkeypatch.setattr(embedding_settings, "bootstrap_apps_rg_embedding_env", lambda repo_root: None)
    monkeypatch.setattr(embedding_settings, "apply_apps_rg_embedding_env_guards", lambda **kwargs: None)
    monkeypatch.setattr(
        embedding_settings,
        "resolve_apps_rg_embedding_settings",
        lambda **kwargs: SimpleNamespace(
            embeddings_enabled=True,
            route_result="OK",
            decisive_reason="",
        ),
    )


def test_deferred_mode_stages_with_run_metadata_and_skips_promotion(monkeypatch, tmp_path) -> None:
    import apps_rg.runtime.c0.c02_fact_vector_ingest as ingest

    _patch_embedding_settings(monkeypatch)
    monkeypatch.setenv("CHROMA_PERSIST_DIR", str(tmp_path / "chroma"))
    monkeypatch.setenv(PROMOTION_MODE_ENV, PROMOTION_MODE_DEFERRED)
    captured: dict[str, object] = {}

    def _fake_upsert(chunks, *, chroma_path, collection_name, atoms):
        captured["chunks"] = chunks
        captured["atoms"] = atoms
        captured["collection_name"] = collection_name
        return len(chunks)

    def _unexpected_promotion(**kwargs):
        raise AssertionError(f"deferred mode must not promote inline: {kwargs}")

    monkeypatch.setattr(ingest, "upsert_fact_vector_chunks", _fake_upsert)
    monkeypatch.setattr(ingest, "promote_staged_fact_vectors", _unexpected_promotion)

    receipt = ingest.maybe_upsert_c02_fact_vectors(
        [_grounded_atom()],
        section_id="competencies",
        artifact_dir=tmp_path / "run",
        run_id="run-deferred",
    )

    assert receipt["status"] == "STAGED_DEFERRED"
    assert receipt["upserted_count"] == 0
    assert receipt["staged_count"] == 1
    staged_atom = captured["atoms"][0]
    assert staged_atom["run_id"] == "run-deferred"
    assert staged_atom["staged_at_utc"]


@pytest.mark.parametrize("mode", [PROMOTION_MODE_INLINE, PROMOTION_MODE_DEFERRED])
def test_generated_atom_never_reaches_fact_vector_staging(monkeypatch, tmp_path, mode) -> None:
    import apps_rg.runtime.c0.c02_fact_vector_ingest as ingest

    _patch_embedding_settings(monkeypatch)
    monkeypatch.setenv("CHROMA_PERSIST_DIR", str(tmp_path / f"chroma_{mode}"))
    monkeypatch.setenv(PROMOTION_MODE_ENV, mode)
    captured: dict[str, int] = {"chunk_count": -1}

    def _fake_upsert(chunks, *, chroma_path, collection_name, atoms):
        del chroma_path, collection_name, atoms
        captured["chunk_count"] = len(chunks)
        return len(chunks)

    monkeypatch.setattr(ingest, "upsert_fact_vector_chunks", _fake_upsert)

    receipt = ingest.maybe_upsert_c02_fact_vectors(
        [
            _grounded_atom(
                fact_id="generated_001",
                write_back_operation=GENERATED,
                proof_status="targeting_only",
                source_type="jd_payload",
            )
        ],
        section_id="competencies",
        artifact_dir=tmp_path / f"run_{mode}",
        run_id=f"run-{mode}",
    )

    assert receipt["status"] == "EMPTY"
    assert captured["chunk_count"] == 0
    assert receipt["routed_to_semantic_cache"] == 1
    assert receipt["skipped"][0]["reason"].startswith("route_semantic_cache")


def test_c05_write_back_fork_keeps_generated_atom_out_of_fact_vectors(monkeypatch, tmp_path) -> None:
    import apps_rg.runtime.c0.c02_fact_vector_ingest as ingest

    _patch_embedding_settings(monkeypatch)
    monkeypatch.setenv("CHROMA_PERSIST_DIR", str(tmp_path / "chroma_c05"))
    monkeypatch.setenv(PROMOTION_MODE_ENV, PROMOTION_MODE_DEFERRED)
    captured: dict[str, int] = {"chunk_count": -1}

    def _fake_upsert(chunks, *, chroma_path, collection_name, atoms):
        del chroma_path, collection_name, atoms
        captured["chunk_count"] = len(chunks)
        return len(chunks)

    monkeypatch.setattr(ingest, "upsert_fact_vector_chunks", _fake_upsert)
    c05 = {
        "fact_vector_write_back_atoms": [
            _grounded_atom(
                fact_id="generated_c05",
                write_back_operation=GENERATED,
                proof_status="targeting_only",
                source_type="jd_payload",
            )
        ]
    }

    receipt = ingest.maybe_upsert_c05_fact_vector_write_back_atoms(
        c05,
        section_id="competencies",
        artifact_dir=tmp_path / "run_c05",
        run_id="run-c05",
    )

    assert receipt["attempted"] is True
    assert captured["chunk_count"] == 0
    assert receipt["ingest"]["routed_to_semantic_cache"] == 1
    assert receipt["status"] == "EMPTY"
