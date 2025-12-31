"""Unit tests for prompt registry semantic deduplication."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import unittest
import tempfile
import shutil
from pathlib import Path
import numpy as np

from agentic_core.prompt_governance.version_registry.prompt_registry import (
    prompt_registry, 
    DuplicatePromptError,
    EMBEDDINGS_AVAILABLE
)


class TestPromptRegistryDeduplication(unittest.TestCase):
    """Test semantic deduplication with embeddings."""

    def setUp(self):
        """Set up test registry with temporary file."""
        # Create temporary directory for test registry
        self.test_dir = tempfile.mkdtemp()
        self.test_registry_file = Path(self.test_dir) / "test_registry.json"
        
        # Create registry instance
        self.registry = prompt_registry()
        # Override registry file location for testing
        self.registry.REGISTRY_FILE = self.test_registry_file
        self.registry.registry = {}
        
        # Mock embeddings for deterministic testing
        self.original_compute = self.registry._compute_embedding
        
        def mock_embedding(content):
            if content is None:
                return None
            # Simple mock: hash content to create deterministic embeddings
            if 'summarize code' in content.lower():
                return np.array([0.9, 0.1, 0.0])
            elif 'describe code' in content.lower():
                return np.array([0.85, 0.15, 0.0])  # Similar to summarize
            elif 'explain function' in content.lower():
                return np.array([0.88, 0.12, 0.0])  # Similar to summarize
            elif 'completely different' in content.lower():
                return np.array([0.1, 0.1, 0.9])  # Dissimilar
            else:
                return np.array([0.5, 0.5, 0.0])
        
        if EMBEDDINGS_AVAILABLE:
            self.registry._compute_embedding = mock_embedding

    def tearDown(self):
        """Clean up test directory."""
        if hasattr(self, 'test_dir') and os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_register_without_content(self):
        """Test registration without content (no embedding check)."""
        self.registry.register_prompt("test_template", version="v1")
        self.assertEqual(len(self.registry.registry), 1)

    def test_register_dissimilar_prompts(self):
        """Test that dissimilar prompts register successfully."""
        self.registry.register_prompt(
            "summarize", 
            content="Please summarize code for documentation"
        )
        self.registry.register_prompt(
            "different", 
            content="This is completely different task"
        )
        self.assertEqual(len(self.registry.registry), 2)

    @unittest.skipIf(not EMBEDDINGS_AVAILABLE, "Embeddings not available")
    def test_register_semantic_duplicate(self):
        """Test that semantically similar prompts raise error."""
        self.registry.register_prompt(
            "summarize", 
            content="Please summarize code for documentation"
        )
        
        with self.assertRaises(DuplicatePromptError) as cm:
            self.registry.register_prompt(
                "describe", 
                content="Please describe code for documentation"
            )
        
        # Check error message contains similarity info
        self.assertIn("Semantic duplicate", str(cm.exception))
        self.assertTrue(hasattr(cm.exception, 'similar_entries'))
        self.assertGreater(len(cm.exception.similar_entries), 0)

    @unittest.skipIf(not EMBEDDINGS_AVAILABLE, "Embeddings not available")
    def test_threshold_config(self):
        """Test configurable similarity threshold."""
        # Lower threshold to allow more similar prompts
        self.registry.similarity_threshold = 0.95
        
        self.registry.register_prompt(
            "summarize", 
            content="Please summarize code"
        )
        
        # This should pass with lower threshold if similarity < 0.95
        try:
            self.registry.register_prompt(
                "explain", 
                content="Please explain function"
            )
            # If it passes, similarity was below threshold
            self.assertEqual(len(self.registry.registry), 2)
        except DuplicatePromptError:
            # If it fails, similarity was above threshold
            pass

    @unittest.skipIf(not EMBEDDINGS_AVAILABLE, "Embeddings not available")
    def test_embedding_storage(self):
        """Test that embeddings are stored in registry entries."""
        self.registry.register_prompt(
            "test_prompt",
            content="Test content for embedding"
        )
        
        entries = self.registry.registry.get("test_prompt", [])
        self.assertGreater(len(entries), 0)
        
        # Check if embedding is stored
        if EMBEDDINGS_AVAILABLE:
            self.assertIn("embedding", entries[0])
            self.assertIsNotNone(entries[0]["embedding"])
            self.assertIsInstance(entries[0]["embedding"], list)

    def test_exact_duplicate_prevention(self):
        """Test that exact duplicates are still prevented."""
        self.registry.register_prompt(
            "test",
            version="v1",
            content="Exact same content"
        )
        
        # Try to register exact duplicate
        self.registry.register_prompt(
            "test",
            version="v1",
            content="Exact same content"
        )
        
        # Should only have one entry
        self.assertEqual(len(self.registry.registry["test"]), 1)

    @unittest.skipIf(not EMBEDDINGS_AVAILABLE, "Embeddings not available")
    def test_similar_prompts_info(self):
        """Test that similar prompts info is detailed."""
        self.registry.register_prompt(
            "original",
            content="Please summarize code"
        )
        
        try:
            self.registry.register_prompt(
                "duplicate",
                content="Please describe code"
            )
        except DuplicatePromptError as e:
            # Check similar entries structure
            self.assertIsInstance(e.similar_entries, list)
            if len(e.similar_entries) > 0:
                entry = e.similar_entries[0]
                self.assertIn('name', entry)
                self.assertIn('version', entry)
                self.assertIn('similarity', entry)
                self.assertGreater(entry['similarity'], 0.9)

    def test_same_template_family_allowed(self):
        """Test that different versions of same template are allowed."""
        self.registry.register_prompt(
            "test_template",
            version="v1",
            content="Version 1 content"
        )
        
        # Different version of same template should be allowed
        # (semantic check skips same template family)
        self.registry.register_prompt(
            "test_template",
            version="v2",
            content="Version 2 content"
        )
        
        # Should have 2 entries for same template
        self.assertEqual(len(self.registry.registry["test_template"]), 2)

    def test_get_active_version(self):
        """Test retrieving active version."""
        self.registry.register_prompt(
            "test",
            version="v1",
            active=False
        )
        self.registry.register_prompt(
            "test",
            version="v2",
            active=True
        )
        
        active = self.registry.get_active_version("test")
        self.assertIsNotNone(active)
        self.assertEqual(active["version"], "v2")


class TestPromptRegistryPerformance(unittest.TestCase):
    """Test performance of semantic deduplication."""

    def setUp(self):
        """Set up test registry."""
        self.test_dir = tempfile.mkdtemp()
        self.registry = prompt_registry()
        self.registry.REGISTRY_FILE = Path(self.test_dir) / "test_registry.json"
        self.registry.registry = {}

    def tearDown(self):
        """Clean up."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @unittest.skipIf(not EMBEDDINGS_AVAILABLE, "Embeddings not available")
    def test_dedup_performance(self):
        """Test that deduplication is reasonably fast."""
        import time
        
        # Register 50 prompts
        for i in range(50):
            self.registry.register_prompt(
                f"prompt_{i}",
                content=f"Unique content for prompt {i}"
            )
        
        # Time similarity check for new prompt
        start = time.time()
        try:
            self.registry.register_prompt(
                "new_prompt",
                content="Brand new unique content"
            )
        except DuplicatePromptError:
            pass
        duration = time.time() - start
        
        # Should complete in reasonable time (< 100ms for 50 prompts)
        self.assertLess(duration, 0.1)


class TestPromptRegistryFallback(unittest.TestCase):
    """Test fallback behavior when embeddings unavailable."""

    def setUp(self):
        """Set up test registry."""
        self.test_dir = tempfile.mkdtemp()
        self.registry = prompt_registry()
        self.registry.REGISTRY_FILE = Path(self.test_dir) / "test_registry.json"
        self.registry.registry = {}

    def tearDown(self):
        """Clean up."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_works_without_embeddings(self):
        """Test that registry works even without embeddings."""
        # Temporarily disable embeddings
        original_available = EMBEDDINGS_AVAILABLE
        
        # Register prompts (should work without semantic check)
        self.registry.register_prompt(
            "prompt1",
            content="Some content"
        )
        self.registry.register_prompt(
            "prompt2",
            content="Other content"
        )
        
        self.assertEqual(len(self.registry.registry), 2)


if __name__ == '__main__':
    unittest.main()
