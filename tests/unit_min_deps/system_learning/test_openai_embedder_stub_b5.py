"""Tests for OpenAIEmbedder (Plan B Phase 5) - unit tests with monkeypatch.

Unit tests that mock OpenAI client to avoid network calls.
"""

from __future__ import annotations

import os
import pytest
from unittest.mock import MagicMock, patch

from system_learning.engines.openai_embedder import OpenAIEmbedder


pytestmark = pytest.mark.unit_min_deps


class TestOpenAIEmbedderStub:
    """Test OpenAIEmbedder with mocked OpenAI client."""

    def test_init_missing_api_key(self):
        """Should raise ValueError when OPENAI_API_KEY missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="OPENAI_API_KEY environment variable is required"):
                OpenAIEmbedder()

    def test_init_success(self):
        """Should initialize successfully with API key."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            with patch("system_learning.engines.openai_embedder.OpenAI") as mock_openai:
                embedder = OpenAIEmbedder()
                assert embedder.model == "text-embedding-3-large"
                mock_openai.assert_called_once_with(api_key="test_key")

    def test_embed_batch_model_correct(self):
        """Should call OpenAI with correct model."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            with patch("system_learning.engines.openai_embedder.OpenAI") as mock_openai_class:
                mock_client = MagicMock()
                mock_openai_class.return_value = mock_client
                
                # Mock response
                mock_response = MagicMock()
                mock_response.data = [
                    MagicMock(embedding=[0.1, 0.2, 0.3]),
                    MagicMock(embedding=[0.4, 0.5, 0.6]),
                ]
                mock_client.embeddings.create.return_value = mock_response
                
                embedder = OpenAIEmbedder(model="text-embedding-3-large")
                result = embedder.embed_batch(["text1", "text2"])
                
                # Verify correct model used
                mock_client.embeddings.create.assert_called_once_with(
                    model="text-embedding-3-large",
                    input=["text1", "text2"]
                )
                assert result == [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]

    def test_newline_normalization_applied(self):
        """Should normalize newlines to spaces."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            with patch("system_learning.engines.openai_embedder.OpenAI") as mock_openai_class:
                mock_client = MagicMock()
                mock_openai_class.return_value = mock_client
                
                # Mock response
                mock_response = MagicMock()
                mock_response.data = [MagicMock(embedding=[0.1, 0.2, 0.3])]
                mock_client.embeddings.create.return_value = mock_response
                
                embedder = OpenAIEmbedder()
                embedder.embed_batch(["line1\nline2", "line3\r\nline4"])
                
                # Verify newlines normalized to spaces
                mock_client.embeddings.create.assert_called_once_with(
                    model="text-embedding-3-large",
                    input=["line1 line2", "line3 line4"]
                )

    def test_vector_length_matches_mocked_dimension(self):
        """Vector length should match mocked response dimension."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            with patch("system_learning.engines.openai_embedder.OpenAI") as mock_openai_class:
                mock_client = MagicMock()
                mock_openai_class.return_value = mock_client
                
                # Mock response with 1536 dimensions (text-embedding-3-large)
                mock_vector = list(range(1536))
                mock_response = MagicMock()
                mock_response.data = [MagicMock(embedding=mock_vector)]
                mock_client.embeddings.create.return_value = mock_response
                
                embedder = OpenAIEmbedder()
                result = embedder.embed_batch(["test"])
                
                assert len(result[0]) == 1536
                assert result[0] == mock_vector

    def test_embed_batch_multiple_texts(self):
        """Should handle batch of multiple texts."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            with patch("system_learning.engines.openai_embedder.OpenAI") as mock_openai_class:
                mock_client = MagicMock()
                mock_openai_class.return_value = mock_client
                
                # Mock response for 3 texts
                mock_response = MagicMock()
                mock_response.data = [
                    MagicMock(embedding=[0.1, 0.2]),
                    MagicMock(embedding=[0.3, 0.4]),
                    MagicMock(embedding=[0.5, 0.6]),
                ]
                mock_client.embeddings.create.return_value = mock_response
                
                embedder = OpenAIEmbedder()
                result = embedder.embed_batch(["text1", "text2", "text3"])
                
                assert len(result) == 3
                assert result[0] == [0.1, 0.2]
                assert result[1] == [0.3, 0.4]
                assert result[2] == [0.5, 0.6]

    def test_embed_batch_with_dimensions_param(self):
        """Should accept dimensions parameter but ignore it (API determines)."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            with patch("system_learning.engines.openai_embedder.OpenAI") as mock_openai_class:
                mock_client = MagicMock()
                mock_openai_class.return_value = mock_client
                
                mock_response = MagicMock()
                mock_response.data = [MagicMock(embedding=[0.1, 0.2, 0.3])]
                mock_client.embeddings.create.return_value = mock_response
                
                embedder = OpenAIEmbedder()
                result = embedder.embed_batch(["test"], dimensions=512)
                
                # Dimensions param should be ignored
                mock_client.embeddings.create.assert_called_once_with(
                    model="text-embedding-3-large",
                    input=["test"]
                )
                assert result == [[0.1, 0.2, 0.3]]

    def test_get_model_info(self):
        """Should return model information including dimensions."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            with patch("system_learning.engines.openai_embedder.OpenAI") as mock_openai_class:
                mock_client = MagicMock()
                mock_openai_class.return_value = mock_client
                
                # Mock embed_batch response
                mock_vector = list(range(1536))
                mock_response = MagicMock()
                mock_response.data = [MagicMock(embedding=mock_vector)]
                mock_client.embeddings.create.return_value = mock_response
                
                embedder = OpenAIEmbedder(model="text-embedding-3-large")
                info = embedder.get_model_info()
                
                assert info["model"] == "text-embedding-3-large"
                assert info["dimensions"] == 1536

    def test_get_model_checksum(self):
        """Should generate consistent checksum for model."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            embedder = OpenAIEmbedder(model="text-embedding-3-large")
            checksum1 = embedder.get_model_checksum()
            checksum2 = embedder.get_model_checksum()
            
            # Should be consistent
            assert checksum1 == checksum2
            # Should be 16 characters (SHA256[:16])
            assert len(checksum1) == 16
            # Should be hex
            assert all(c in "0123456789abcdef" for c in checksum1)

    def test_custom_model(self):
        """Should support custom model names."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            with patch("system_learning.engines.openai_embedder.OpenAI") as mock_openai_class:
                mock_client = MagicMock()
                mock_openai_class.return_value = mock_client
                
                mock_response = MagicMock()
                mock_response.data = [MagicMock(embedding=[0.1, 0.2])]
                mock_client.embeddings.create.return_value = mock_response
                
                embedder = OpenAIEmbedder(model="text-embedding-3-small")
                embedder.embed_batch(["test"])
                
                mock_client.embeddings.create.assert_called_once_with(
                    model="text-embedding-3-small",
                    input=["test"]
                )

    def test_import_error_without_openai(self):
        """Should raise ImportError if openai package not installed."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            with patch("system_learning.engines.openai_embedder.openai", None):
                with pytest.raises(ImportError, match="openai package is required"):
                    OpenAIEmbedder()
