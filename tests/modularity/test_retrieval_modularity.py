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
