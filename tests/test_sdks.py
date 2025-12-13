#!/usr/bin/env python3
"""Test SDK functionality with configured API keys."""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_provider(provider_name, module_path, test_func):
import logging

logger = logging.getLogger(__name__)

    """Test a specific provider."""
    try:
        result = test_func()
        logger.info(f"✅ {provider_name}: Operational")
        return True, None
    except Exception as e:
        logger.info(f"❌ {provider_name}: Failed - {str(e)[:100]}")
        return False, str(e)

def main():
    logger.info("=" * 60)
    logger.info("AGENTIC WORKFLOW - SDK FUNCTIONALITY TEST")
    logger.info("=" * 60)

    # Test OpenAI
    def test_openai():
        from openai import OpenAI
        client = OpenAI()
        response = client.models.list()
        return len(response.data) > 0

    test_provider("OpenAI", "openai", test_openai)

    # Test Anthropic
    def test_anthropic():
        from anthropic import Anthropic
        client = Anthropic()
        # Just test client creation (no API call needed)
        return client is not None

    test_provider("Anthropic", "anthropic", test_anthropic)

    # Test Google
    def test_google():
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        models = genai.list_models()
        return len(models) > 0

    test_provider("Google", "google.generativeai", test_google)

    # Test Pinecone
    def test_pinecone():
        from pinecone import Pinecone
        client = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        indexes = client.list_indexes()
        return True  # Just test connection

    test_provider("Pinecone", "pinecone", test_pinecone)

    # Test ChromaDB
    def test_chromadb():
        import chromadb
        client = chromadb.Client()
        collection = client.create_collection("test")
        return collection is not None

    test_provider("ChromaDB", "chromadb", test_chromadb)

    # Test Redis
    def test_redis():
        import redis
        client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        client.ping()
        return True

    test_provider("Redis", "redis", test_redis)

    # Test LiteLLM
    def test_litellm():
        import litellm
        # Just test import
        return True

    test_provider("LiteLLM", "litellm", test_litellm)

    # Test Instructor
    def test_instructor():
        import instructor
        return True

    test_provider("Instructor", "instructor", test_instructor)

    # Test MCP
    def test_mcp():
        import mcp
        return True

    test_provider("MCP SDK", "mcp", test_mcp)

    # Test FastMCP
    def test_fastmcp():
        import fastmcp
        return True

    test_provider("FastMCP", "fastmcp", test_fastmcp)

    logger.info("\n" + "=" * 60)
    logger.info("Test complete. Check results above.")
    logger.info("Note: Some tests may fail due to missing local services (Redis)")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
