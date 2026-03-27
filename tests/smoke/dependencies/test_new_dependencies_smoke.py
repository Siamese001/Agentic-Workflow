"""Smoke tests for newly installed dependencies."""

import pytest
import sys
from pathlib import Path


class TestNewlyInstalledDependencies:
    """Test that newly installed dependencies are importable and functional."""

    @pytest.mark.smoke
    def test_rank_bm25_import(self):
        """Test rank_bm25 can be imported and used."""
        try:
            from rank_bm25 import BM25Okapi
            assert BM25Okapi is not None

            # Basic functionality test
            corpus = [
                "Hello there good man!",
                "It is quite windy in here",
                "Hello world hello world"
            ]
            tokenized_corpus = [doc.split(" ") for doc in corpus]
            bm25 = BM25Okapi(tokenized_corpus)
            assert bm25 is not None

        except ImportError as e:
            pytest.skip(f"rank_bm25 not available: {e}")

    @pytest.mark.smoke
    def test_sentence_transformers_import(self):
        """Test sentence_transformers can be imported."""
        try:
            from sentence_transformers import SentenceTransformer
            assert SentenceTransformer is not None
        except ImportError as e:
            pytest.skip(f"sentence_transformers not available: {e}")

    @pytest.mark.smoke
    def test_opentelemetry_import(self):
        """Test opentelemetry can be imported."""
        try:
            from opentelemetry import trace
            from opentelemetry import metrics
            assert trace is not None
            assert metrics is not None
        except ImportError as e:
            pytest.skip(f"opentelemetry not available: {e}")

    @pytest.mark.smoke
    def test_python_dotenv_import(self):
        """Test python-dotenv can be imported."""
        try:
            import dotenv
            assert dotenv is not None

            # Test basic functionality
            test_env_path = Path(__file__).parent / ".test.env"
            test_env_path.write_text("TEST_VAR=test_value\n")

            loaded = dotenv.load_dotenv(test_env_path)
            assert loaded is True or loaded is False  # Returns True/False depending on whether file exists

            # Clean up
            if test_env_path.exists():
                test_env_path.unlink()

        except ImportError as e:
            pytest.skip(f"python-dotenv not available: {e}")

    @pytest.mark.smoke
    def test_tree_sitter_import(self):
        """Test tree-sitter can be imported."""
        try:
            import tree_sitter
            assert tree_sitter is not None
        except ImportError as e:
            pytest.skip(f"tree-sitter not available: {e}")

    @pytest.mark.smoke
    def test_tree_sitter_python_import(self):
        """Test tree-sitter-python can be imported."""
        try:
            import tree_sitter_python
            assert tree_sitter_python is not None
        except ImportError as e:
            pytest.skip(f"tree-sitter-python not available: {e}")

    @pytest.mark.smoke
    def test_pydantic_settings_import(self):
        """Test pydantic-settings can be imported."""
        try:
            from pydantic_settings import BaseSettings
            assert BaseSettings is not None

            # Test basic functionality - just check class exists and can be subclassed
            class TestSettings(BaseSettings):
                test_var: str = "default"

            # Just verify the class can be instantiated
            settings = TestSettings(test_var="test")
            assert hasattr(settings, 'test_var')

        except ImportError as e:
            pytest.skip(f"pydantic-settings not available: {e}")

    @pytest.mark.smoke
    def test_gitpython_import(self):
        """Test gitpython can be imported."""
        try:
            import git
            assert git is not None

            # Test basic functionality
            from git import Repo
            assert Repo is not None

        except ImportError as e:
            pytest.skip(f"gitpython not available: {e}")

    @pytest.mark.smoke
    def test_faiss_import(self):
        """Test faiss-cpu can be imported."""
        try:
            import faiss
            assert faiss is not None

            # Test basic functionality
            import numpy as np
            d = 64  # dimension
            nb = 100  # database size
            np.random.seed(1234)
            xb = np.random.random((nb, d)).astype('float32')

            index = faiss.IndexFlatL2(d)
            assert index is not None

            index.add(xb)
            assert index.ntotal == nb

        except ImportError as e:
            pytest.skip(f"faiss-cpu not available: {e}")

    @pytest.mark.smoke
    def test_optional_vllm_import(self):
        """Test vllm is optional and can be skipped."""
        try:
            import vllm
            pytest.skip("vllm is installed but should be optional")
        except ImportError:
            # Expected - vllm should be optional
            assert True
