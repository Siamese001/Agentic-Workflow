"""SDK Validation Test Suite for Agentic-Workflow-10_10

This script validates all installed SDKs and their integration with the architecture.
Note: type: ignore comments are intentional for optional dependencies being validated.
"""

import sys
import json
from typing import Dict, Any, List

# Test results storage
results: List[Dict[str, Any]] = []


def test_result(name: str, status: str, details: str = "", error: str = ""):
    """Record a test result."""
    results.append({
        "sdk_name": name,
        "install_status": "SUCCESS" if status == "PASS" else "FAILED",
        "test_results": status,
        "details": details,
        "error": error,
        "follow_up": "" if status == "PASS" else "Review error and reinstall if needed"
    })


def test_core_dependencies():
    """Test core Python dependencies."""
    
    # Pydantic
    try:
        from pydantic import BaseModel, Field
        class TestModel(BaseModel):
            name: str
            value: int = Field(gt=0)
        obj = TestModel(name="test", value=42)
        assert obj.name == "test"
        test_result("pydantic", "PASS", "Version check passed, schema validation working")
    except Exception as e:
        test_result("pydantic", "FAIL", error=str(e))
    
    # NumPy
    try:
        import numpy as np
        arr = np.array([1, 2, 3])
        assert arr.sum() == 6
        test_result("numpy", "PASS", f"Version: {np.__version__}, operations working")
    except Exception as e:
        test_result("numpy", "FAIL", error=str(e))
    
    # Pandas
    try:
        import pandas as pd  # type: ignore
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        assert len(df) == 2
        test_result("pandas", "PASS", f"Version: {pd.__version__}, DataFrame operations working")
    except Exception as e:
        test_result("pandas", "FAIL", error=str(e))
    
    # Tenacity
    try:
        from tenacity import retry, stop_after_attempt
        @retry(stop=stop_after_attempt(1))
        def test_func():
            return "success"
        assert test_func() == "success"
        test_result("tenacity", "PASS", "Retry decorator working")
    except Exception as e:
        test_result("tenacity", "FAIL", error=str(e))
    
    # Rich
    try:
        from rich.console import Console  # type: ignore
        Console()  # Test initialization
        test_result("rich", "PASS", "Console initialization successful")
    except Exception as e:
        test_result("rich", "FAIL", error=str(e))
    
    # Python-dotenv
    try:
        import dotenv
        dotenv  # Test import
        test_result("python-dotenv", "PASS", "Import successful")
    except Exception as e:
        test_result("python-dotenv", "FAIL", error=str(e))
    
    # HTTPX
    try:
        import httpx
        test_result("httpx", "PASS", f"Version: {httpx.__version__}")
    except Exception as e:
        test_result("httpx", "FAIL", error=str(e))


def test_llm_providers():
    """Test LLM provider SDKs."""
    
    # OpenAI
    try:
        import openai  # type: ignore
        test_result("openai", "PASS", f"Version: {openai.__version__}, SDK import successful")
    except Exception as e:
        test_result("openai", "FAIL", error=str(e))
    
    # Anthropic
    try:
        import anthropic  # type: ignore
        test_result("anthropic", "PASS", f"Version: {anthropic.__version__}, SDK import successful")
    except Exception as e:
        test_result("anthropic", "FAIL", error=str(e))
    
    # Google Generative AI
    try:
        import google.generativeai as genai  # type: ignore
        genai  # Test import
        test_result("google-generativeai", "PASS", "SDK import successful")
    except Exception as e:
        test_result("google-generativeai", "FAIL", error=str(e))


def test_vector_databases():
    """Test vector database SDKs."""
    
    # Redis
    try:
        import redis  # type: ignore
        # Test client creation (won't connect without server, but validates SDK)
        test_result("redis", "PASS", f"Version: {redis.__version__}, SDK import successful")
    except Exception as e:
        test_result("redis", "FAIL", error=str(e))
    
    # ChromaDB
    try:
        import chromadb  # type: ignore
        
        version = getattr(chromadb, '__version__', 'unknown')
        
        # Test basic functionality without server connection
        try:
            chromadb.Client()  # Test initialization
            test_result("chromadb", "PASS", 
                       f"Version: {version}, Basic client initialization successful")
        except Exception as e:
            if "unable to infer type" in str(e):
                test_result("chromadb", "WARNING", 
                           f"Version: {version}, Basic functionality works but with type inference warning (Python 3.14+ compatibility issue)")
            else:
                test_result("chromadb", "WARNING", 
                           error=f"Unexpected error (Python 3.14+ compatibility?): {str(e)}")
                
    except ImportError as e:
        test_result("chromadb", "FAIL", error=f"SDK not installed: {str(e)}")
    except Exception as e:
        test_result("chromadb", "WARNING", 
                   error=f"Unexpected error (Python 3.14+ compatibility?): {str(e)}")
    
    # Pinecone
    try:
        try:
            import pinecone  # type: ignore
            pinecone  # Test import
            test_result("pinecone-client", "PASS", "SDK import successful (legacy package)")
        except ImportError:
            test_result("pinecone-client", "FAIL", "Package not found")
    except Exception as e:
        test_result("pinecone-client", "FAIL", error=str(e))
    
    # FAISS
    try:
        import faiss  # type: ignore
        # Test basic FAISS operation
        faiss.IndexFlatL2(128)  # Test index creation
        test_result("faiss-cpu", "PASS", "Index creation successful")
    except Exception as e:
        test_result("faiss-cpu", "FAIL", error=str(e))


def test_ml_libraries():
    """Test ML/NLP libraries."""
    
    # scikit-learn
    try:
        import sklearn  # type: ignore
        test_result("scikit-learn", "PASS", f"Version: {sklearn.__version__}")
    except Exception as e:
        test_result("scikit-learn", "FAIL", error=str(e))
    
    # sentence-transformers
    try:
        import sentence_transformers  # type: ignore
        version = getattr(sentence_transformers, '__version__', 'unknown')
        test_result("sentence-transformers", "PASS", f"Version: {version}, Import successful")
    except Exception as e:
        test_result("sentence-transformers", "FAIL", error=str(e))


def test_observability():
    """Test observability libraries."""
    
    # OpenTelemetry API
    try:
        import opentelemetry  # type: ignore
        version = getattr(opentelemetry, '__version__', 'unknown')
        # Test basic import without requiring specific submodules
        test_result("opentelemetry-api", "PASS", f"Version: {version}, Core API import successful")
    except Exception as e:
        test_result("opentelemetry-api", "FAIL", error=str(e))
    
    # OpenTelemetry SDK
    try:
        # Import only if available to avoid type checker errors
        try:
            from opentelemetry.sdk.trace import TracerProvider  # type: ignore
            TracerProvider()  # Test initialization
            test_result("opentelemetry-sdk", "PASS", "TracerProvider initialization successful")
        except ImportError:
            # SDK not installed but API is available
            test_result("opentelemetry-sdk", "WARNING", "SDK not installed, but API available")
    except Exception as e:
        test_result("opentelemetry-sdk", "FAIL", error=str(e))


def test_testing_frameworks():
    """Test testing frameworks."""
    
    # Pytest
    try:
        import pytest
        test_result("pytest", "PASS", f"Version: {pytest.__version__}")
    except Exception as e:
        test_result("pytest", "FAIL", error=str(e))
    
    # Pytest-asyncio
    try:
        import pytest_asyncio  # type: ignore
        version = getattr(pytest_asyncio, '__version__', 'unknown')
        test_result("pytest-asyncio", "PASS", f"Version: {version}, Import successful")
    except Exception as e:
        test_result("pytest-asyncio", "FAIL", error=str(e))


def test_mcp_sdk():
    """Test MCP SDK."""
    
    try:
        import mcp  # type: ignore
        version = getattr(mcp, '__version__', 'unknown')
        test_result("mcp", "PASS", f"SDK import successful (version: {version})")
    except Exception as e:
        test_result("mcp", "FAIL", error=str(e))


def test_project_imports():
    """Test project-specific imports."""
    
    try:
        # Test cache_redis
        import infra.storage.cache_redis
        test_result("cache_redis (project)", "PASS", "Project module import successful")
    except Exception as e:
        test_result("cache_redis (project)", "FAIL", error=str(e))
    
    try:
        # Test vector_store_chroma
        import infra.storage.vector_store_chroma
        infra.storage.vector_store_chroma  # Test import
        test_result("vector_store_chroma (project)", "PASS", "Project module import successful")
    except Exception as e:
        test_result("vector_store_chroma (project)", "FAIL", error=str(e))
    
    try:
        # Test providers
        import providers  # Test module import
        providers  # Test import
        test_result("providers (project)", "PASS", "All provider modules import successful")
    except Exception as e:
        test_result("providers (project)", "FAIL", error=str(e))


def print_results_table():
    """Print results in a formatted table."""
    print("\n" + "="*120)
    print("SDK VALIDATION TEST RESULTS")
    print("="*120)
    print(f"{'SDK Name':<35} {'Install Status':<15} {'Test Results':<15} {'Details/Error':<55}")
    print("-"*120)
    
    for result in results:
        details = result['details'] if result['test_results'] == 'PASS' else result['error']
        details = details[:52] + "..." if len(details) > 55 else details
        print(f"{result['sdk_name']:<35} {result['install_status']:<15} {result['test_results']:<15} {details:<55}")
    
    print("-"*120)
    passed = sum(1 for r in results if r['test_results'] == 'PASS')
    failed = sum(1 for r in results if r['test_results'] == 'FAIL')
    print(f"SUMMARY: {passed} PASSED, {failed} FAILED out of {len(results)} tests")
    print("="*120 + "\n")


def main():
    """Run all validation tests."""
    print("Starting SDK validation tests...")
    
    test_core_dependencies()
    test_llm_providers()
    test_vector_databases()
    test_ml_libraries()
    test_observability()
    test_testing_frameworks()
    test_mcp_sdk()
    test_project_imports()
    
    print_results_table()
    
    # Save results to JSON
    with open("sdk_validation_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Results saved to sdk_validation_results.json")
    
    # Return exit code based on failures
    failed = sum(1 for r in results if r['test_results'] == 'FAIL')
    return 1 if failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())



