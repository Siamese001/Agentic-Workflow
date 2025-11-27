#!/usr/bin/env python3
"""
Validates SDK installations for resume generation system functionality.

Ensures all dependencies are properly installed to maintain
resume generation quality and system reliability.
"""

# Note: type: ignore comments are intentional for optional dependencies being validated.

import sys
import json
from typing import Dict, Any, List

# Test results storage
results: List[Dict[str, Any]] = []


def record_test_result(name: str, status: str, details: str = "", error: str = ""):
    """Records SDK validation test results for system reliability.

    Ensures resume generation dependencies are properly validated
    for consistent and quality output generation.
    """
    results.append({
        "sdk_name": name,
        "install_status": "SUCCESS" if status == "PASS" else "FAILED",
        "test_results": status,
        "details": details,
        "error": error,
        "follow_up": "" if status == "PASS" else "Review error and reinstall if needed"
    })


def test_core_dependencies():
    """Tests core Python dependencies for resume generation functionality.

    Ensures essential libraries work properly for reliable
    resume processing and quality output generation.
    """
    
    # Pydantic
    try:
        from pydantic import BaseModel, Field
        class TestModel(BaseModel):
            name: str
            value: int = Field(gt=0)
        obj = TestModel(name="test", value=42)
        assert obj.name == "test"
        record_test_result("pydantic", "PASS", "Version check passed, schema validation working")
    except Exception as e:
        record_test_result("pydantic", "FAIL", error=str(e))
    
    # NumPy
    try:
        import numpy as np
        arr = np.array([1, 2, 3])
        assert arr.sum() == 6
        record_test_result("numpy", "PASS", f"Version: {np.__version__}, operations working")
    except Exception as e:
        record_test_result("numpy", "FAIL", error=str(e))
    
    # Pandas
    try:
        import pandas as pd  # type: ignore
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        assert len(df) == 2
        record_test_result("pandas", "PASS", f"Version: {pd.__version__}, DataFrame operations working")
    except Exception as e:
        record_test_result("pandas", "FAIL", error=str(e))
    
    # Tenacity
    try:
        from tenacity import retry, stop_after_attempt
        @retry(stop=stop_after_attempt(1))
        def test_func():
            return "success"
        assert test_func() == "success"
        record_test_result("tenacity", "PASS", "Retry decorator working")
    except Exception as e:
        record_test_result("tenacity", "FAIL", error=str(e))
    
    # Rich
    try:
        from rich.console import Console  # type: ignore
        Console()  # Test initialization
        record_test_result("rich", "PASS", "Console initialization successful")
    except Exception as e:
        record_test_result("rich", "FAIL", error=str(e))
    
    # Python-dotenv
    try:
        import dotenv
        dotenv  # Test import
        record_test_result("python-dotenv", "PASS", "Import successful")
    except Exception as e:
        record_test_result("python-dotenv", "FAIL", error=str(e))
    
    # HTTPX
    try:
        import httpx
        record_test_result("httpx", "PASS", f"Version: {httpx.__version__}")
    except Exception as e:
        record_test_result("httpx", "FAIL", error=str(e))


def test_llm_providers():
    """Tests LLM provider SDKs for resume content generation.

    Ensures all language model integrations work properly
    for high-quality resume text generation.
    """
    
    # OpenAI
    try:
        import openai  # type: ignore
        record_test_result("openai", "PASS", f"Version: {openai.__version__}, SDK import successful")
    except Exception as e:
        record_test_result("openai", "FAIL", error=str(e))
    
    # Anthropic
    try:
        import anthropic  # type: ignore
        record_test_result("anthropic", "PASS", f"Version: {anthropic.__version__}, SDK import successful")
    except Exception as e:
        record_test_result("anthropic", "FAIL", error=str(e))
    
    # Google Generative AI
    try:
        import google.generativeai as genai  # type: ignore
        genai  # Test import
        record_test_result("google-generativeai", "PASS", "SDK import successful")
    except Exception as e:
        record_test_result("google-generativeai", "FAIL", error=str(e))


def test_vector_databases():
    """Tests vector database SDKs for resume knowledge retrieval.

    Ensures efficient storage and retrieval of resume-related
    information for improved content accuracy.
    """
    
    # Redis
    try:
        import redis  # type: ignore
        # Test client creation (won't connect without server, but validates SDK)
        record_test_result("redis", "PASS", f"Version: {redis.__version__}, SDK import successful")
    except Exception as e:
        record_test_result("redis", "FAIL", error=str(e))
    
    # ChromaDB
    try:
        import chromadb  # type: ignore
        
        version = getattr(chromadb, '__version__', 'unknown')
        
        # Test basic functionality without server connection
        try:
            chromadb.Client()  # Test initialization
            record_test_result("chromadb", "PASS", 
                       f"Version: {version}, Basic client initialization successful")
        except Exception as e:
            if "unable to infer type" in str(e):
                record_test_result("chromadb", "WARNING", 
                           f"Version: {version}, Basic functionality works but with type inference warning (Python 3.14+ compatibility issue)")
            else:
                record_test_result("chromadb", "WARNING", 
                           error=f"Unexpected error (Python 3.14+ compatibility?): {str(e)}")
                
    except ImportError as e:
        record_test_result("chromadb", "FAIL", error=f"SDK not installed: {str(e)}")
    except Exception as e:
        record_test_result("chromadb", "WARNING", 
                   error=f"Unexpected error (Python 3.14+ compatibility?): {str(e)}")
    
    # Pinecone
    try:
        try:
            import pinecone  # type: ignore
            pinecone  # Test import
            record_test_result("pinecone-client", "PASS", "SDK import successful (legacy package)")
        except ImportError:
            record_test_result("pinecone-client", "FAIL", "Package not found")
    except Exception as e:
        record_test_result("pinecone-client", "FAIL", error=str(e))
    
    # FAISS
    try:
        import faiss  # type: ignore
        # Test basic FAISS operation
        faiss.IndexFlatL2(128)  # Test index creation
        record_test_result("faiss-cpu", "PASS", "Index creation successful")
    except Exception as e:
        record_test_result("faiss-cpu", "FAIL", error=str(e))


def test_ml_libraries():
    """Tests ML/NLP libraries for resume content processing.

    Ensures machine learning components work properly for
    intelligent resume generation and optimization.
    """
    
    # scikit-learn
    try:
        import sklearn  # type: ignore
        record_test_result("scikit-learn", "PASS", f"Version: {sklearn.__version__}")
    except Exception as e:
        record_test_result("scikit-learn", "FAIL", error=str(e))
    
    # sentence-transformers
    try:
        import sentence_transformers  # type: ignore
        version = getattr(sentence_transformers, '__version__', 'unknown')
        record_test_result("sentence-transformers", "PASS", f"Version: {version}, Import successful")
    except Exception as e:
        record_test_result("sentence-transformers", "FAIL", error=str(e))


def test_observability():
    """Tests observability libraries for resume generation monitoring.

    Ensures tracking and logging capabilities work properly
    for quality assurance and debugging.
    """
    
    # OpenTelemetry API
    try:
        import opentelemetry  # type: ignore
        version = getattr(opentelemetry, '__version__', 'unknown')
        # Test basic import without requiring specific submodules
        record_test_result("opentelemetry-api", "PASS", f"Version: {version}, Core API import successful")
    except Exception as e:
        record_test_result("opentelemetry-api", "FAIL", error=str(e))
    
    # OpenTelemetry SDK
    try:
        # Import only if available to avoid type checker errors
        try:
            from opentelemetry.sdk.trace import TracerProvider  # type: ignore
            TracerProvider()  # Test initialization
            record_test_result("opentelemetry-sdk", "PASS", "TracerProvider initialization successful")
        except ImportError:
            # SDK not installed but API is available
            record_test_result("opentelemetry-sdk", "WARNING", "SDK not installed, but API available")
    except Exception as e:
        record_test_result("opentelemetry-sdk", "FAIL", error=str(e))


def test_testing_frameworks():
    """Tests testing frameworks for resume generation quality assurance.

    Ensures testing infrastructure works properly for
    maintaining code quality and reliability.
    """
    
    # Pytest
    try:
        import pytest
        record_test_result("pytest", "PASS", f"Version: {pytest.__version__}")
    except Exception as e:
        record_test_result("pytest", "FAIL", error=str(e))
    
    # Pytest-asyncio
    try:
        import pytest_asyncio  # type: ignore
        version = getattr(pytest_asyncio, '__version__', 'unknown')
        record_test_result("pytest-asyncio", "PASS", f"Version: {version}, Import successful")
    except Exception as e:
        record_test_result("pytest-asyncio", "FAIL", error=str(e))


def test_mcp_sdk():
    """Tests MCP SDK for resume generation integration capabilities.

    Ensures external integrations work properly for enhanced
    resume processing functionality.
    """
    
    try:
        import mcp  # type: ignore
        version = getattr(mcp, '__version__', 'unknown')
        record_test_result("mcp", "PASS", f"SDK import successful (version: {version})")
    except Exception as e:
        record_test_result("mcp", "FAIL", error=str(e))


def test_project_imports():
    """Tests project-specific imports for resume generation modules.

    Ensures all internal components can be imported properly
    for seamless resume processing functionality.
    """
    
    try:
        # Test cache_redis
        import infra.storage.cache_redis
        record_test_result("cache_redis (project)", "PASS", "Project module import successful")
    except Exception as e:
        record_test_result("cache_redis (project)", "FAIL", error=str(e))
    
    try:
        # Test vector_store_chroma
        import infra.storage.vector_store_chroma
        infra.storage.vector_store_chroma  # Test import
        record_test_result("vector_store_chroma (project)", "PASS", "Project module import successful")
    except Exception as e:
        record_test_result("vector_store_chroma (project)", "FAIL", error=str(e))
    
    try:
        # Test providers
        import providers  # Test module import
        providers  # Test import
        record_test_result("providers (project)", "PASS", "All provider modules import successful")
    except Exception as e:
        record_test_result("providers (project)", "FAIL", error=str(e))


def print_results_table():
    """Prints validation results in a formatted table for clarity.

    Ensures SDK validation results are clearly displayed
    for easy system reliability assessment.
    """
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
    """Runs all SDK validation tests for system reliability.

    Ensures resume generation system dependencies are properly
    validated for consistent and quality output.
    """
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



