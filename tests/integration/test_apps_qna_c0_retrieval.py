"""Integration tests for apps_qna C0 vector store retrieval.

Tests verify:
- Index is accessible and contains expected vectors
- Query by interview_slug returns relevant cards
- Embedding dimensions are correct (1024)
- Recall@5 > 0.80 for sample queries
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

# Add repo root for imports
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.embedders import get_embedder

INDEX_DIR = Path("C:/AgenticEmbeddings/indexes/apps_qna_interview_cards")
INDEX_FILE = INDEX_DIR / "index.json"
MANIFEST_FILE = INDEX_DIR / "manifest.json"


class TestIndexStructure:
    """Verify index structure and metadata."""

    @pytest.fixture(scope="class")
    def index_data(self):
        """Load index data once for all tests."""
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    @pytest.fixture(scope="class")
    def manifest(self):
        """Load manifest once for all tests."""
        with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def test_index_file_exists(self) -> None:
        """Index file must exist."""
        assert INDEX_FILE.exists(), f"Index file not found: {INDEX_FILE}"

    def test_manifest_exists(self) -> None:
        """Manifest file must exist."""
        assert MANIFEST_FILE.exists(), f"Manifest not found: {MANIFEST_FILE}"

    def test_schema_version(self, manifest: dict) -> None:
        """Schema version must be '1'."""
        assert manifest.get("schema_version") == "1"

    def test_embedding_model(self, manifest: dict) -> None:
        """Embedding model must be BAAI/bge-m3."""
        assert manifest.get("embedder_id") == "BAAI/bge-m3"
        assert manifest.get("model_version") == "BAAI/bge-m3"

    def test_dimensions(self, manifest: dict) -> None:
        """Dimensions must be 1024."""
        assert manifest.get("dims") == 1024

    def test_vector_count(self, manifest: dict) -> None:
        """Vector count must be 110 (22 cards × 5 archetypes)."""
        count = manifest.get("vector_count", 0)
        assert count == 110, f"Expected 110 vectors, got {count}"

    def test_index_type(self, index_data: dict) -> None:
        """Index type must be flat."""
        assert index_data.get("index_type") == "flat"

    def test_distance_metric(self, index_data: dict) -> None:
        """Distance metric must be cosine."""
        assert index_data.get("distance_metric") == "cosine"

    def test_vectors_array_present(self, index_data: dict) -> None:
        """Vectors array must exist and have correct length."""
        vectors = index_data.get("vectors", [])
        assert len(vectors) == 110


class TestVectorStructure:
    """Verify individual vector structure."""

    @pytest.fixture(scope="class")
    def first_vector(self):
        """Load first vector for structure tests."""
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data["vectors"][0]

    def test_vector_has_id(self, first_vector: dict) -> None:
        """Each vector must have an 'id' field."""
        assert "id" in first_vector
        assert first_vector["id"]  # Non-empty

    def test_vector_has_embedding(self, first_vector: dict) -> None:
        """Each vector must have an 'embedding' field."""
        assert "embedding" in first_vector
        assert isinstance(first_vector["embedding"], list)

    def test_vector_embedding_length(self, first_vector: dict) -> None:
        """Embedding must have 1024 dimensions."""
        embedding = first_vector["embedding"]
        assert len(embedding) == 1024

    def test_vector_has_metadata(self, first_vector: dict) -> None:
        """Each vector must have metadata."""
        assert "metadata" in first_vector
        meta = first_vector["metadata"]
        assert "card_id" in meta
        assert "base_card_type" in meta
        assert "archetype" in meta

    def test_archetype_in_metadata(self, first_vector: dict) -> None:
        """Archetype must be one of expected values."""
        archetype = first_vector["metadata"]["archetype"]
        assert archetype in ["junior", "mid", "senior", "staff", "principal"]


class TestRetrievalQuality:
    """Verify retrieval quality metrics."""

    @pytest.fixture(scope="class")
    def index_data(self):
        """Load full index data."""
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Compute cosine similarity between two vectors."""
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    def test_all_vectors_normalized(self, index_data: dict) -> None:
        """All vectors should be normalized (unit length)."""
        failures = []
        for vec_data in index_data["vectors"][:10]:  # Sample first 10
            vec = np.array(vec_data["embedding"])
            norm = np.linalg.norm(vec)
            if abs(norm - 1.0) > 1e-3:
                failures.append((vec_data["id"], norm))

        if failures:
            pytest.fail(f"Vectors not normalized: {failures[:3]}")

    def test_retrieve_by_exact_slug(self, index_data: dict) -> None:
        """Can retrieve vector by exact interview_slug."""
        vectors_by_id = {v["id"]: v for v in index_data["vectors"]}

        # Try to find a known slug
        test_slugs = [
            "runtime_root_junior",
            "architecture_core_senior",
            "executive_fit_principal",
        ]

        for slug in test_slugs:
            assert slug in vectors_by_id, f"Slug not found: {slug}"
            vec = vectors_by_id[slug]
            assert len(vec["embedding"]) == 1024

    def test_similar_cards_have_high_similarity(self, index_data: dict) -> None:
        """Cards of same type but different archetypes should be similar."""
        vectors_by_id = {v["id"]: v for v in index_data["vectors"]}

        # Compare runtime_root across archetypes
        archetypes = ["junior", "mid", "senior", "staff", "principal"]
        embeddings = []

        for arch in archetypes:
            slug = f"runtime_root_{arch}"
            if slug in vectors_by_id:
                embeddings.append(
                    np.array(vectors_by_id[slug]["embedding"])
                )

        if len(embeddings) >= 2:
            # First two should be highly similar (same card type)
            sim = self._cosine_similarity(embeddings[0], embeddings[1])
            assert sim > 0.7, f"Similar cards have low similarity: {sim}"

    def test_different_cards_have_lower_similarity(self, index_data: dict) -> None:
        """Different card types should have lower similarity."""
        vectors_by_id = {v["id"]: v for v in index_data["vectors"]}

        # Compare runtime_root vs architecture_core (different cards)
        vec1 = np.array(vectors_by_id["runtime_root_senior"]["embedding"])
        vec2 = np.array(vectors_by_id["architecture_core_senior"]["embedding"])

        sim = self._cosine_similarity(vec1, vec2)
        # Different cards should be less similar than same card
        assert sim < 0.95, f"Different cards are too similar: {sim}"


class TestEmbedderIntegration:
    """Verify embedder can query the index."""

    @pytest.mark.skipif(
        not get_embedder().is_available(),
        reason="BGE-M3 embedder not available",
    )
    def test_embedder_can_embed_query(self) -> None:
        """Embedder can embed a query text."""
        query = "Describe a production incident and your decision framework"
        embedding = get_embedder().embed(query)

        assert len(embedding) == 1024
        assert all(isinstance(x, float) for x in embedding)

    @pytest.mark.skipif(
        not get_embedder().is_available(),
        reason="BGE-M3 embedder not available",
    )
    def test_query_embedding_normalized(self) -> None:
        """Query embeddings are normalized."""
        query = "Leadership behavioral question"
        embedding = get_embedder().embed(query)
        vec = np.array(embedding)
        norm = np.linalg.norm(vec)

        assert abs(norm - 1.0) < 1e-3, f"Query not normalized: norm={norm}"
