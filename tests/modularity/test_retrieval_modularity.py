from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_retrieval_directory_structure_exists() -> None:
    """Ensure META retrieval directory tree exists."""
    expected_dirs = [
        PROJECT_ROOT / "meta",
        PROJECT_ROOT / "meta" / "retrieval",
        PROJECT_ROOT / "meta" / "retrieval" / "retrievers",
    ]
    for d in expected_dirs:
        assert d.exists(), f"Expected directory missing: {d}"


def test_retriever_placeholders_present() -> None:
    """Ensure placeholder retriever modules exist for future implementation."""
    expected_files = [
        PROJECT_ROOT / "meta" / "retrieval" / "retrievers" / "bm25.py",
        PROJECT_ROOT / "meta" / "retrieval" / "retrievers" / "dense.py",
    ]
    for f in expected_files:
        assert f.exists(), f"Expected retriever module missing: {f}"


def test_meta_ranking_and_hybrid_ranker_present() -> None:
    """Ensure META ranking + hybrid ranker modules exist and are wired."""
    ranking_file = PROJECT_ROOT / "meta" / "ranking.py"
    hybrid_ranker_file = PROJECT_ROOT / "meta" / "retrieval" / "hybrid_ranker.py"

    assert ranking_file.exists(), f"Expected META ranking module missing: {ranking_file}"
    assert hybrid_ranker_file.exists(), f"Expected hybrid_ranker module missing: {hybrid_ranker_file}"

    retrieval_file = PROJECT_ROOT / "retrieval.py"
    text = retrieval_file.read_text(encoding="utf-8")
    assert "from meta.retrieval.retrieval import orchestrate_retrieval" in text
    assert "from retrievers." not in text







