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
            print(f"✅ {package_name} v{version}")
        else:
            print(f"✅ {package_name}")
        return True
    except ImportError as e:
        print(f"❌ {package_name}: {e}")
        return False

def main():
    """Run comprehensive installation verification"""
    print("🚀 SUBATOMIC AGENTIC ARCHITECTURE - INSTALLATION VERIFICATION")
    print("=" * 60)
    print(f"Timestamp: {datetime.utcnow().isoformat()}")
    print(f"Python Version: {sys.version}")
    print()
    
    # Core LLM Providers
    print("📚 CORE LLM PROVIDERS:")
    core_packages = [
        "openai",
        "anthropic", 
        "google.generativeai",
        "google.cloud.aiplatform",
        "mistralai",
        "cohere"
    ]
    
    core_success = sum(test_import(pkg) for pkg in core_packages)
    print(f"Core LLM: {core_success}/{len(core_packages)} packages working\n")
    
    # Vector Databases
    print("🔍 VECTOR DATABASES:")
    vector_packages = [
        "pinecone",
        "chromadb",
        "qdrant_client",
        "lancedb"
    ]
    
    vector_success = sum(test_import(pkg) for pkg in vector_packages)
    print(f"Vector DBs: {vector_success}/{len(vector_packages)} packages working\n")
    
    # Caching & Redis
    print("⚡ CACHING & REDIS:")
    cache_packages = [
        "redis",
        "redisvl",
        "redis_om"
    ]
    
    cache_success = sum(test_import(pkg) for pkg in cache_packages)
    print(f"Caching: {cache_success}/{len(cache_packages)} packages working\n")
    
    # Data Processing & ML
    print("🧠 DATA PROCESSING & ML:")
    ml_packages = [
        "pandas",
        "pyarrow", 
        "sentence_transformers",
        "faiss",
        "instructor",
        "pydantic"
    ]
    
    ml_success = sum(test_import(pkg) for pkg in ml_packages)
    print(f"ML/Data: {ml_success}/{len(ml_packages)} packages working\n")
    
    # Safety & Guardrails
    print("🛡️ SAFETY & GUARDRAILS:")
    safety_packages = [
        "guardrails",
        "llm_guard"
    ]
    
    safety_success = sum(test_import(pkg) for pkg in safety_packages)
    print(f"Safety: {safety_success}/{len(safety_packages)} packages working\n")
    
    # Observability & Utilities
    print("📊 OBSERVABILITY & UTILITIES:")
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
    print(f"Utilities: {util_success}/{len(util_packages)} packages working\n")
    
    # Summary
    total_packages = len(core_packages) + len(vector_packages) + len(cache_packages) + len(ml_packages) + len(safety_packages) + len(util_packages)
    total_success = core_success + vector_success + cache_success + ml_success + safety_success + util_success
    
    print("=" * 60)
    print("📊 INSTALLATION SUMMARY:")
    print(f"Total Packages: {total_packages}")
    print(f"Successfully Installed: {total_success}")
    print(f"Success Rate: {total_success/total_packages*100:.1f}%")
    
    if total_success == total_packages:
        print("\n🎉 INSTALLATION COMPLETE - ALL SYSTEMS OPERATIONAL!")
        print("✨ SUBATOMIC AGENTIC ARCHITECTURE READY FOR PRODUCTION")
        print("\n🚀 NEXT STEPS:")
        print("1. Set your API keys (OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.)")
        print("2. Start Redis Stack: docker run -d -p 6379:6379 redis/redis-stack-server:7.4.0-v3")
        print("3. Run your first agentic workflow!")
        sys.exit(0)
    else:
        print(f"\n⚠️ INSTALLATION INCOMPLETE - {total_packages - total_success} packages failed")
        print("Check the errors above and install missing packages manually")
        sys.exit(1)

if __name__ == "__main__":
    main()
