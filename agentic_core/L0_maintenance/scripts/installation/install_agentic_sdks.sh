#!/bin/bash
# =============================================================================
# AGENTIC-WORKFLOW: COMPLETE AGENTIC SDK INSTALLER (21 SDKs)
# ZERO-LOSS MERGE — FINAL CONSOLIDATED & HARDENED
# Docker container execution only
# =============================================================================

set -euo pipefail

echo "=============================================="
echo "Installing Complete Agentic SDK Set (21 SDKs)"
echo "=============================================="

# Hardened install with reproducibility flags
pip install --upgrade --no-cache-dir --force-reinstall \
    "openai>=1.50.0" \
    "anthropic>=0.34.0" \
    "google-genai>=1.0.0" \
    "mistralai>=1.2.0" \
    "cohere>=5.11.0" \
    "groq>=0.11.0" \
    "together>=1.2.0" \
    "fireworks-ai>=0.15.0" \
    "litellm>=1.50.0" \
    "instructor>=1.3.0" \
    "chromadb>=0.5.0" \
    "qdrant-client>=1.12.0" \
    "pinecone>=5.0.0" \
    "redis>=5.0.0" \
    "hiredis>=3.0.0" \
    "langgraph>=0.2.0" \
    "langchain-core>=0.3.0" \
    "opentelemetry-api>=1.27.0" \
    "opentelemetry-sdk>=1.27.0" \
    "unstructured>=0.15.0" \
    "pypdf>=4.0.0" \
    "mcp>=1.0.0" \
    "fastmcp>=0.1.0" \
    "pip-tools>=7.4.0" \
    "pydantic>=2.5.0" \
    "httpx>=0.27.0" \
    "tenacity>=8.2.0" \
    "tiktoken>=0.7.0" \
    "numpy>=1.26.0" \
    "aiohttp>=3.9.0" \
    "uvicorn>=0.30.0" \
    "structlog>=24.1.0" \
    "python-json-logger>=2.0.0"

echo ""
echo "=============================================="
echo "Validating SDK Imports"
echo "=============================================="

python3 -c "
import sys
errors = []
success = []

def check(name, import_path):
    try:
        __import__(import_path)
        success.append(name)
        print(f'✓ {name}')
    except ImportError as e:
        errors.append(f'✗ {name}: {e}')

# Core LLM Providers (5)
check('openai', 'openai')
check('anthropic', 'anthropic')
check('google-genai', 'google.genai')
check('mistralai', 'mistralai')
check('cohere', 'cohere')

# High-Performance Inference (3)
check('groq', 'groq')
check('together', 'together')
check('fireworks-ai', 'fireworks')

# Routing & Structured Outputs (2)
check('litellm', 'litellm')
check('instructor', 'instructor')

# Vector Stores (3)
check('chromadb', 'chromadb')
check('qdrant-client', 'qdrant_client')
check('pinecone', 'pinecone')

# Caching (2)
check('redis', 'redis')
check('hiredis', 'hiredis')

# Orchestration (2)
check('langgraph', 'langgraph')
check('langchain-core', 'langchain_core')

# Observability (2)
check('opentelemetry-api', 'opentelemetry')
check('opentelemetry-sdk', 'opentelemetry.sdk')

# Document Processing (2)
check('unstructured', 'unstructured')
check('pypdf', 'pypdf')

# MCP (2)
check('mcp', 'mcp')
check('fastmcp', 'fastmcp')

print('')
print(f'Validated: {len(success)}/21 SDKs')
if errors:
    print('')
    print('FAILED:')
    for err in errors:
        print(f'  {err}')
    sys.exit(1)
else:
    print('All 21 agentic SDKs successfully installed and validated.')
    sys.exit(0)
"

echo ""
echo "=============================================="
echo "Installation Complete"
echo "=============================================="
