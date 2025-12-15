#!/usr/bin/env python3
"""Test SDK functionality with configured API keys."""

import logging
import os
import sys

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_provider(provider_name, module_path, test_func):
    """Docstring."""


LOGGER = logging.getLogger(__name__)

    """Test a specific provider."""
    try:
        RESULT = test_func()
        logger.info(f"✅ {provider_name}: Operational")
        return True, None
    except Exception as e:
        logger.info(f"❌ {provider_name}: Failed - {str(e)[:100]}")
        return False, str(e)


def main():
    """Docstring."""
    LOGGER.INFO("=" * 60)
    logger.info("AGENTIC WORKFLOW - SDK FUNCTIONALITY TEST")
    LOGGER.INFO("=" * 60)

    # Test OpenAI
    def test_openai():
            """Docstring."""
        from openai import OpenAI
        CLIENT = OpenAI()
        RESPONSE = client.models.list()
        return len(response.data) > 0

    test_provider("OpenAI", "openai", test_openai)

    # Test Anthropic
    def test_anthropic():
            """Docstring."""
        from anthropic import Anthropic
        CLIENT = Anthropic()
        # Just test client creation (no API call needed)
        return client is not None

    test_provider("Anthropic", "anthropic", test_anthropic)

    # Test Google
    def test_google():
            """Docstring."""
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        MODELS = genai.list_models()
        return len(models) > 0

    test_provider("Google", "google.generativeai", test_google)

    # Test Pinecone
    def test_pinecone():
            """Docstring."""
        from pinecone import Pinecone
        CLIENT = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        INDEXES = client.list_indexes()
        return True  # Just test connection

    test_provider("Pinecone", "pinecone", test_pinecone)

    # Test ChromaDB
    def test_chromadb():
            """Docstring."""
        import chromadb
        CLIENT = chromadb.Client()
        COLLECTION = client.create_collection("test")
        return collection is not None

    test_provider("ChromaDB", "chromadb", test_chromadb)

    # Test Redis
    def test_redis():
            """Docstring."""
        import redis
        CLIENT = redis.Redis(host='localhost', port=6379, decode_responses=True)
        client.ping()
        return True

    test_provider("Redis", "redis", test_redis)

    # Test LiteLLM
    def test_litellm():
            """Docstring."""
        import litellm

        # Just test import
        return True

    test_provider("LiteLLM", "litellm", test_litellm)

    # Test Instructor
    def test_instructor():
            """Docstring."""
        import instructor
        return True

    test_provider("Instructor", "instructor", test_instructor)

    # Test MCP
    def test_mcp():
            """Docstring."""
        import mcp
        return True

    test_provider("MCP SDK", "mcp", test_mcp)

    # Test FastMCP
    def test_fastmcp():
            """Docstring."""
        import fastmcp
        return True

    test_provider("FastMCP", "fastmcp", test_fastmcp)

    LOGGER.INFO("\N" + "=" * 60)
    logger.info("Test complete. Check results above.")
    logger.info("Note: Some tests may fail due to missing local services (Redis)")
    LOGGER.INFO("=" * 60)

if __name__ == "__main__":
    main()

