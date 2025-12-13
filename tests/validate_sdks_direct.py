#!/usr/bin/env python3
"""Direct SDK validation without imports through __init__.py."""

import sys
import os
import importlib

def check_sdk_import(sdk_name, module_path):
    """Docstring."""
import logging

logger = logging.getLogger(__name__)

    """Check if SDK can be imported."""
    try:
        importlib.import_module(module_path)
        return True, None
    except ImportError as e:
        return False, str(e)

def check_env_var(env_var):
    """Check if environment variable is set."""
    return os.getenv(env_var) is not None

def main():
    """Docstring."""
    logger.info("=" * 60)
    logger.info("AGENTIC WORKFLOW - DIRECT SDK VALIDATION")
    logger.info("=" * 60)

    # Define all SDKs to check
    sdks = {
        # Core LLM Providers
        "openai": ("openai", "OPENAI_API_KEY"),
        "anthropic": ("anthropic", "ANTHROPIC_API_KEY"),
        "google-generativeai": ("google.generativeai", "GOOGLE_API_KEY"),
        "mistralai": ("mistralai", "MISTRAL_API_KEY"),
        "cohere": ("cohere", "COHERE_API_KEY"),

        # High-Performance Inference
        "groq": ("groq", "GROQ_API_KEY"),
        "together": ("together", "TOGETHER_API_KEY"),
        "fireworks-ai": ("fireworks.client", "FIREWORKS_API_KEY"),

        # Routing & Structured Outputs
        "litellm": ("litellm", None),
        "instructor": ("instructor", None),

        # Vector Stores
        "chromadb": ("chromadb", None),
        "qdrant-client": ("qdrant_client", "PINECONE_API_KEY"),
        "pinecone": ("pinecone", "PINECONE_API_KEY"),

        # Caching
        "redis": ("redis", None),
        "hiredis": ("hiredis", None),

        # Orchestration
        "langgraph": ("langgraph", None),
        "langchain-core": ("langchain_core", None),

        # Observability
        "opentelemetry-api": ("opentelemetry.trace", None),
        "opentelemetry-sdk": ("opentelemetry.sdk.trace", None),

        # Document Processing
        "unstructured": ("unstructured", None),
        "pypdf": ("pypdf", None),

        # MCP
        "mcp": ("mcp", None),
        "fastmcp": ("fastmcp", None),
    }

    logger.info("\nCHECKING ALL 21 SDKS...")
    logger.info("-" * 40)

    available = 0
    missing = 0
    missing_keys = 0

    for sdk_name, (module, env_var) in sdks.items():
        # Check if module is installed
        is_installed, error = check_sdk_import(sdk_name, module)

        # Check API key if required
        has_key = True
        if env_var and is_installed:
            has_key = check_env_var(env_var)
            if not has_key:
                missing_keys += 1

        status = "✅" if is_installed else "❌"
        key_status = "" if not env_var else ("🔑" if has_key else "⚠️")

        logger.info(f"{status} {key_status} {sdk_name:<20} {module:<30}")

        if is_installed:
            available += 1
        else:
            missing += 1

    logger.info("-" * 40)
    logger.info(f"Summary: {available}/21 installed,
        {missing} missing,
        {missing_keys} missing keys")

    # Check MCP functionality
    logger.info("\nCHECKING MCP FUNCTIONALITY...")
    logger.info("-" * 40)

    try:
        # Import directly
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

        # Create server
        server = mcp_tools.MCPToolServer("test-server")

        # Register a test tool
        def test_function(x: int) -> int:
            """Docstring."""
            return x * 2

        server.register_function(
            name="test_double",
            description="Double a number",
            parameters={
                "type": "object",
                "properties": {
                    "x": {"type": "integer"}
                },
                "required": ["x"]
            },
            handler=test_function
        )

        # Test execution
        result = server.execute_tool("test_double", {"x": 21})

        logger.info(f"✅ MCP Server: Operational")
        logger.info(f"✅ Tool Registration: OK")
        logger.info(f"✅ Tool Execution: OK (21 * 2 = {result.result})")

    except Exception as e:
        logger.info(f"❌ MCP Server: Failed - {e}")

    # Check multi-provider clients
    logger.info("\nCHECKING MULTI-PROVIDER CLIENTS...")
    logger.info("-" * 40)

    try:

        providers = mp_clients.get_available_providers()
        logger.info(f"✅ Multi-Provider Client: Operational")
        logger.info(f"Available providers: {len(providers)}")

        for provider in providers:
            logger.info(f"  - {provider.value}")

    except Exception as e:
        logger.info(f"❌ Multi-Provider Client: Failed - {e}")

    # Final verdict
    logger.info("\n" + "=" * 60)
    if missing == 0:
        logger.info("✅ ALL 21 SDKs INSTALLED")
        if missing_keys == 0:
            logger.info("✅ ALL REQUIRED API KEYS CONFIGURED")
            logger.info("\n🎉 SYSTEM FULLY OPERATIONAL!")
        else:
            logger.info("⚠️  SOME API KEYS MISSING - CHECK ABOVE")
    else:
        logger.info(f"❌ {missing} SDKs MISSING")
        logger.info("\nTo install missing SDKs:")
        logger.info("  pip install --upgrade -r requirements.txt")

    return 0 if missing == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
