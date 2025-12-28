"""
Test script to verify the new Sovereign Constitution integration.
Tests config validation, embedding generation, and Pinecone store creation.
"""
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_config():
    """Test SovereignConfig validation."""
    print("\n=== Testing SovereignConfig ===")
    try:
        from agentic_core.config.blueprint_sovereign.environments.sovereign_config import config
        
        # Test validation (will fail if API keys missing)
        try:
            config.validate()
            print("✓ Config validation passed")
        except ValueError as e:
            print(f"⚠ Config validation failed (expected): {e}")
            return False
        
        # Test config values
        print(f"✓ Embedding model: {config.DEFAULT_EMBEDDING_MODEL}")
        print(f"✓ Embedding dimensions: {config.DEFAULT_EMBEDDING_DIM}")
        print(f"✓ Pinecone environment: {config.PINECONE_ENV}")
        
        return True
    except Exception as e:
        print(f"✗ Config test failed: {e}")
        return False

def test_embedding():
    """Test embedding generation."""
    print("\n=== Testing Core Embedder ===")
    try:
        from agentic_core.semantic_memory.embedding_logic.core_embedder import get_embedding
        
        # Test embedding generation
        test_text = "This is a test of the sovereign embedding system."
        embedding = get_embedding(test_text)
        
        print(f"✓ Generated embedding with {len(embedding)} dimensions")
        print(f"✓ First 5 values: {embedding[:5]}")
        
        return True
    except Exception as e:
        print(f"✗ Embedding test failed: {e}")
        return False

def test_pinecone_store():
    """Test Pinecone store creation."""
    print("\n=== Testing SovereignPineconeStore ===")
    try:
        from agentic_core.semantic_memory.vector_stores.pinecone.pinecone_store import SovereignPineconeStore
        
        # Test store creation (will fail if PINECONE_API_KEY missing)
        try:
            store = SovereignPineconeStore()
            print("✓ Pinecone store created successfully")
            print(f"✓ Index name: {store.index_name}")
            print(f"✓ Dimensions: {store.dimension}")
            return True
        except Exception as e:
            print(f"⚠ Pinecone store creation failed (expected): {e}")
            return False
    except Exception as e:
        print(f"✗ Pinecone store test failed: {e}")
        return False

def test_bootstrap():
    """Test territory bootstrap."""
    print("\n=== Testing Territory Bootstrap ===")
    try:
        from agentic_core.config.blueprint_sovereign.structure_blueprint import bootstrap_territory_index
        
        # Test bootstrap (will fail if API keys missing)
        try:
            bootstrap_territory_index()
            print("✓ Bootstrap completed successfully")
            return True
        except Exception as e:
            print(f"⚠ Bootstrap failed (expected): {e}")
            return False
    except Exception as e:
        print(f"✗ Bootstrap test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🏛️ Testing Sovereign Constitution Integration")
    print("=" * 50)
    
    results = []
    results.append(test_config())
    results.append(test_embedding())
    results.append(test_pinecone_store())
    results.append(test_bootstrap())
    
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! The constitution is working.")
    else:
        print("⚠️  Some tests failed. Check your API key configuration.")
        print("\nRequired environment variables:")
        print("- PINECONE_API_KEY")
        print("- OPENAI_API_KEY")

if __name__ == "__main__":
    main()
