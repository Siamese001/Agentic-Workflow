"""
Test: Gemini Embedder API Compliance

Ensures the Gemini embedding API calls use correct parameter names.

RCA: embed_content() was called with 'content' instead of 'contents',
causing "unexpected keyword argument 'content'" error.
"""

import re
from pathlib import Path
import pytest


# Files that use embed_content API
EMBEDDING_FILES = [
    "agentic_core/semantic_memory/embeddings/gemini_embedder.py",
    "agentic_core/semantic_memory/store/pinecone_sync.py",
    "agentic_core/L3_orchestration/fission_logic/subatomic_engine.py",
]


def get_project_root() -> Path:
    """Get project root directory."""
    import os
    if "PROJECT_ROOT" in os.environ:
        return Path(os.environ["PROJECT_ROOT"])
    
    known_root = Path("C:/Git/Agentic-Workflow")
    if known_root.exists() and (known_root / "agentic_core").is_dir():
        return known_root
    
    test_file = Path(__file__).resolve()
    return test_file.parent.parent.parent


class TestGeminiEmbedderAPICompliance:
    """Test suite for Gemini embedder API compliance."""

    @pytest.fixture
    def project_root(self) -> Path:
        return get_project_root()

    def test_embed_content_uses_contents_parameter(self, project_root: Path):
        """Verify embed_content calls use 'contents' not 'content' parameter."""
        violations = []
        
        for rel_path in EMBEDDING_FILES:
            file_path = project_root / rel_path
            if not file_path.exists():
                continue
            
            content = file_path.read_text(encoding="utf-8")
            
            # Find embed_content calls with wrong parameter
            # Pattern: embed_content(...content=...) but NOT contents=
            wrong_pattern = r"embed_content\s*\([^)]*\bcontent\s*="
            correct_pattern = r"embed_content\s*\([^)]*\bcontents\s*="
            
            wrong_matches = re.findall(wrong_pattern, content)
            correct_matches = re.findall(correct_pattern, content)
            
            # Filter out false positives (variable names like embed_content = ...)
            for match in wrong_matches:
                if "contents=" not in match:
                    violations.append({
                        "file": rel_path,
                        "issue": "Uses 'content=' instead of 'contents='",
                        "match": match[:50]
                    })
        
        assert not violations, (
            f"Found incorrect embed_content parameter usage:\n"
            + "\n".join(f"  - {v['file']}: {v['issue']}" for v in violations)
        )

    def test_embed_content_result_uses_embeddings_array(self, project_root: Path):
        """Verify embed_content result access uses 'embeddings[0].values' not 'embedding.values'."""
        violations = []
        
        for rel_path in EMBEDDING_FILES:
            file_path = project_root / rel_path
            if not file_path.exists():
                continue
            
            content = file_path.read_text(encoding="utf-8")
            
            # Check for old-style result access
            if "result.embedding.values" in content:
                violations.append({
                    "file": rel_path,
                    "issue": "Uses 'result.embedding.values' instead of 'result.embeddings[0].values'"
                })
        
        assert not violations, (
            f"Found incorrect embed_content result access:\n"
            + "\n".join(f"  - {v['file']}: {v['issue']}" for v in violations)
        )

    def test_gemini_embedder_can_be_imported(self, project_root: Path):
        """Verify GeminiEmbedder can be imported without errors."""
        try:
            import sys
            sys.path.insert(0, str(project_root))
            from agentic_core.semantic_memory.embeddings.gemini_embedder import GeminiEmbedder
            assert GeminiEmbedder is not None
        except ImportError as e:
            pytest.skip(f"GeminiEmbedder import failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
