#!/usr/bin/env python3
"""
Subatomic Agentic Architecture Installation Verification
Validates all core components are working correctly
"""

import sys
import importlib
from datetime import datetime

def test_import(package_name, min_version=None):
    """Test if a package can be imported and optionally check version"""
    try:
        module = importlib.import_module(package_name)
        if min_version and hasattr(module, '__version__'):
            version = module.__version__

        else:

        return True
    except ImportError as e:

        return False

def main():
    """Run comprehensive installation verification"""

    # Core LLM Providers

    core_packages = [
        "openai",
        "anthropic",
        "google.generativeai",
        "google.cloud.aiplatform",
        "mistralai",
        "cohere"
    ]

    core_success = sum(test_import(pkg) for pkg in core_packages)

    # Vector Databases

    vector_packages = [
        "pinecone",
        "chromadb",
        "qdrant_client",
        "lancedb"
    ]

    vector_success = sum(test_import(pkg) for pkg in vector_packages)

    # Caching & Redis

    cache_packages = [
        "redis",
        "redisvl",
        "redis_om"
    ]

    cache_success = sum(test_import(pkg) for pkg in cache_packages)

    # Data Processing & ML

    ml_packages = [
        "pandas",
        "pyarrow",
        "sentence_transformers",
        "faiss",
        "instructor",
        "pydantic"
    ]

    ml_success = sum(test_import(pkg) for pkg in ml_packages)

    # Safety & Guardrails

    safety_packages = [
        "guardrails",
        "llm_guard"
    ]

    safety_success = sum(test_import(pkg) for pkg in safety_packages)

    # Observability & Utilities

    util_packages = [
        "opentelemetry.api",
        "opentelemetry.sdk",
        "structlog",
        "httpx",
        "tenacity",
        "rich",
        "typer"
    ]

    util_success = sum(test_import(pkg) for pkg in util_packages)

    # Summary
    total_packages = len(core_packages) + len(vector_packages) + len(cache_packages) + len(ml_packages) + len(safety_packages) + len(util_packages)
    total_success = core_success + vector_success + cache_success + ml_success + safety_success + util_success

    if total_success == total_packages:

        sys.exit(0)
    else:

        sys.exit(1)

if __name__ == "__main__":
    main()
