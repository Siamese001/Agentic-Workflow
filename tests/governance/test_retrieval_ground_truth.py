"""S7: Retrieval Ground Truth Validation.

Validates that the retrieval ground truth corpus is structurally sound and
that each entry's expected_document_ids reference files that actually exist
in the repository.  This is a deterministic structural test — no LLM or
embedding model is invoked.

A separate periodic evaluation run (out of band) computes live recall@k metrics.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).parent.parent.parent
_CORPUS_PATH = _REPO_ROOT / "data" / "golden_state" / "datasets" / "retrieval_ground_truth.jsonl"

_REQUIRED_FIELDS = frozenset(
    {
        "query_id",
        "query",
        "expected_document_ids",
        "expected_answer_spans",
        "expected_top_k_rank",
        "minimum_recall_at_3",
    }
)


def _load_corpus() -> list[dict]:
    assert _CORPUS_PATH.exists(), f"Retrieval ground truth corpus missing: {_CORPUS_PATH}"
    entries = []
    for lineno, line in enumerate(_CORPUS_PATH.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError as exc:
            pytest.fail(f"Corpus line {lineno}: JSON parse error — {exc}")
        entries.append(entry)
    return entries


class TestRetrievalGroundTruthCorpus:
    """Structural integrity checks for the retrieval ground truth corpus."""

    def test_corpus_exists_and_is_non_empty(self):
        entries = _load_corpus()
        assert len(entries) >= 1, "Corpus must contain at least one entry"

    def test_all_entries_have_required_fields(self):
        entries = _load_corpus()
        for entry in entries:
            missing = _REQUIRED_FIELDS - set(entry.keys())
            assert not missing, (
                f"Entry {entry.get('query_id', '?')} missing required fields: {missing}"
            )

    def test_query_ids_are_unique(self):
        entries = _load_corpus()
        ids = [e["query_id"] for e in entries]
        assert len(ids) == len(set(ids)), "Duplicate query_id values detected in corpus"

    def test_queries_are_non_empty_strings(self):
        entries = _load_corpus()
        for entry in entries:
            qid = entry["query_id"]
            assert isinstance(entry["query"], str) and entry["query"].strip(), (
                f"Entry {qid}: 'query' must be a non-empty string"
            )

    def test_expected_document_ids_reference_existing_files(self):
        entries = _load_corpus()
        missing_files: list[str] = []
        for entry in entries:
            for doc_id in entry["expected_document_ids"]:
                full_path = _REPO_ROOT / doc_id
                if not full_path.exists():
                    missing_files.append(f"{entry['query_id']}: {doc_id}")
        assert not missing_files, (
            "Corpus references non-existent files:\n" + "\n".join(missing_files)
        )

    def test_expected_answer_spans_are_non_empty(self):
        entries = _load_corpus()
        for entry in entries:
            qid = entry["query_id"]
            spans = entry["expected_answer_spans"]
            assert isinstance(spans, list) and len(spans) >= 1, (
                f"Entry {qid}: 'expected_answer_spans' must be a non-empty list"
            )
            for span in spans:
                assert isinstance(span, str) and span.strip(), (
                    f"Entry {qid}: each answer span must be a non-empty string, got {span!r}"
                )

    def test_minimum_recall_at_3_is_valid_float(self):
        entries = _load_corpus()
        for entry in entries:
            qid = entry["query_id"]
            val = entry["minimum_recall_at_3"]
            assert isinstance(val, (int, float)) and 0.0 <= float(val) <= 1.0, (
                f"Entry {qid}: 'minimum_recall_at_3' must be a float in [0, 1], got {val!r}"
            )

    def test_expected_top_k_rank_is_positive_int(self):
        entries = _load_corpus()
        for entry in entries:
            qid = entry["query_id"]
            rank = entry["expected_top_k_rank"]
            assert isinstance(rank, int) and rank >= 1, (
                f"Entry {qid}: 'expected_top_k_rank' must be a positive integer, got {rank!r}"
            )

    def test_answer_spans_present_in_referenced_documents(self):
        """Verify that each expected_answer_span appears verbatim in at least one
        of the referenced source files.  This prevents stale corpus entries where
        the source was refactored but the corpus was not updated.
        """
        entries = _load_corpus()
        stale: list[str] = []
        for entry in entries:
            qid = entry["query_id"]
            doc_texts: list[str] = []
            for doc_id in entry["expected_document_ids"]:
                full_path = _REPO_ROOT / doc_id
                if full_path.exists():
                    doc_texts.append(full_path.read_text(encoding="utf-8", errors="replace"))
            combined = "\n".join(doc_texts)
            for span in entry["expected_answer_spans"]:
                if span not in combined:
                    stale.append(f"{qid}: span {span!r} not found in {entry['expected_document_ids']}")
        assert not stale, (
            "Stale corpus entries — answer spans no longer present in referenced documents:\n"
            + "\n".join(stale)
        )
