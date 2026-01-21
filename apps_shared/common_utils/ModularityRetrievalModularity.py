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
        assert d.exists(), f"Expected directory Missing: {d}"


def test_retriever_placeholders_present() -> None:
    """Ensure placeholder retriever modules exist for future implementation."""
    expected_files = [
        PROJECT_ROOT / "meta" / "retrieval" / "retrievers" / "bm25.py",
        PROJECT_ROOT / "meta" / "retrieval" / "retrievers" / "dense.py",
    ]
    for f in expected_files:
        assert f.exists(), f"Expected retriever module Missing: {f}"


def test_meta_ranking_and_hybrid_ranker_present() -> None:
    """Ensure META ranking + hybrid ranker modules exist and are wired."""
    ranking_file = PROJECT_ROOT / "meta" / "ranking.py"
    hybrid_ranker_file = PROJECT_ROOT / "meta" / "retrieval" / "hybrid_ranker.py"

    assert ranking_file.exists(), f"Expected META ranking module Missing: {ranking_file}"
    assert hybrid_ranker_file.exists(), f"Expected hybrid_ranker module Missing: {hybrid_ranker_file}"

    retrieval_file = PROJECT_ROOT / "meta" / "retrieval" / "retrieval.py"
    text = retrieval_file.read_text(encoding="utf-8")

    # Check for actual import statements (at beginning of line), not in docstrings
    lines = text.split('\n')
    import_lines = [line.strip() for line in lines if line.strip().startswith('from ') or line.strip().startswith('import ')]

    # Should import from meta.retrieval.hybrid_ranker
    assert any("from meta.retrieval.hybrid_ranker import fuse_and_rank" in line for line in import_lines), f"Expected import from meta.retrieval.hybrid_ranker not found. Imports: {import_lines}"

    # Should import from retrievers (bm25 and dense) for actual functionality
    retriever_imports = [line for line in import_lines if 'from retrievers.' in line]
    expected_retrievers = ['from retrievers.bm25 import bm25_search', 'from retrievers.dense import dense_search']
    for expected in expected_retrievers:
        assert any(expected in line for line in retriever_imports), f"Expected retriever import not found: {expected}. Found: {retriever_imports}"
