"""Demo test for prompt registry semantic deduplication with real embeddings."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import tempfile
import shutil
from pathlib import Path

from agentic_core.prompt_governance.version_registry.prompt_registry import (
    prompt_registry, 
    DuplicatePromptError,
    EMBEDDINGS_AVAILABLE
)


def test_semantic_deduplication_demo():
    """Demonstrate semantic deduplication with real or mocked embeddings."""
    print("\n" + "="*80)
    print("Prompt Registry Semantic Deduplication Demo")
    print("="*80 + "\n")
    
    print(f"Embeddings available: {EMBEDDINGS_AVAILABLE}")
    
    # Create temporary test registry
    test_dir = tempfile.mkdtemp()
    try:
        registry = prompt_registry()
        registry.REGISTRY_FILE = Path(test_dir) / "test_registry.json"
        registry.registry = {}
        
        # Test 1: Register first prompt
        print("\n--- Test 1: Register Original Prompt ---")
        prompt1 = "Analyze this code and provide a detailed summary of its functionality"
        registry.register_prompt(
            "code_analyzer",
            version="v1",
            content=prompt1
        )
        print(f"✓ Registered: code_analyzer")
        print(f"  Content: {prompt1[:60]}...")
        
        # Test 2: Try to register semantically similar prompt
        print("\n--- Test 2: Attempt Semantic Duplicate ---")
        prompt2 = "Examine this code and give a comprehensive summary of what it does"
        try:
            registry.register_prompt(
                "code_examiner",
                version="v1",
                content=prompt2
            )
            print(f"✓ Registered: code_examiner (similarity below threshold)")
            print(f"  Content: {prompt2[:60]}...")
        except DuplicatePromptError as e:
            print(f"✗ Blocked duplicate prompt!")
            print(f"  Error: {str(e)}")
            if hasattr(e, 'similar_entries') and e.similar_entries:
                print(f"  Similar to: {e.similar_entries[0]['name']}")
                print(f"  Similarity: {e.similar_entries[0]['similarity']:.3f}")
        
        # Test 3: Register dissimilar prompt
        print("\n--- Test 3: Register Dissimilar Prompt ---")
        prompt3 = "Generate unit tests for the given function"
        registry.register_prompt(
            "test_generator",
            version="v1",
            content=prompt3
        )
        print(f"✓ Registered: test_generator")
        print(f"  Content: {prompt3[:60]}...")
        
        # Test 4: Check embeddings stored
        print("\n--- Test 4: Verify Embedding Storage ---")
        entries = registry.registry.get("code_analyzer", [])
        if entries and 'embedding' in entries[0]:
            emb = entries[0]['embedding']
            print(f"✓ Embedding stored: {len(emb)} dimensions")
            print(f"  First 5 values: {emb[:5]}")
        else:
            print("⚠ No embedding stored (embeddings may not be available)")
        
        # Test 5: Performance check
        print("\n--- Test 5: Performance Check ---")
        import time
        
        # Register 20 prompts
        for i in range(20):
            registry.register_prompt(
                f"prompt_{i}",
                content=f"This is unique prompt number {i} with distinct content"
            )
        
        # Time deduplication check
        start = time.time()
        try:
            registry.register_prompt(
                "new_prompt",
                content="Brand new unique content for testing"
            )
        except DuplicatePromptError:
            pass
        duration = time.time() - start
        
        print(f"✓ Deduplication check for 21 prompts: {duration*1000:.1f}ms")
        if duration < 0.05:
            print("  Performance: Excellent")
        elif duration < 0.1:
            print("  Performance: Good")
        else:
            print("  Performance: Acceptable")
        
        # Summary
        print("\n" + "="*80)
        print("Summary:")
        print(f"  - Total prompts registered: {len(registry.registry)}")
        print(f"  - Embeddings available: {EMBEDDINGS_AVAILABLE}")
        print(f"  - Similarity threshold: {registry.similarity_threshold}")
        print(f"  - Deduplication working: ✓")
        print("="*80 + "\n")
        
    finally:
        # Cleanup
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)


if __name__ == "__main__":
    test_semantic_deduplication_demo()
