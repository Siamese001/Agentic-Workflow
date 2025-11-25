# Provider Layer - External SDK Isolation

This directory enforces strict architectural separation between the application layers (L1-L5) and external SDK dependencies.

## 🏗️ Architecture Principle

**External SDKs MUST only be imported in the `providers/` directory.**

All other layers (L1-L5, infra, meta, core) should delegate to provider clients instead of importing SDKs directly.

## 📦 Available Providers

### Redis Client (`redis_client.py`)
- **Purpose**: Redis caching operations
- **Usage**: `from providers.redis_client import RedisClient, init_redis_client`
- **Replaces**: Direct `import redis` in infra/storage layers

### ChromaDB Client (`chromadb_client.py`)
- **Purpose**: Vector storage and retrieval
- **Usage**: `from providers.chromadb_client import ChromaClient, ChromaConfig, init_chroma_client`
- **Replaces**: Direct `import chromadb` in infra/storage layers

### OpenAI Client (`openai_client.py`)
- **Purpose**: OpenAI API operations
- **Usage**: `from providers.openai_client import OpenAIClient`

### Anthropic Client (`anthropic_client.py`)
- **Purpose**: Anthropic Claude API operations
- **Usage**: `from providers.anthropic_client import AnthropicClient`

### Google GenAI Client (`google_genai_client.py`)
- **Purpose**: Google Generative AI API operations
- **Usage**: `from providers.google_genai_client import GoogleGenAIClient`

### Pinecone Client (`pinecone_client/`)
- **Purpose**: Pinecone vector database operations
- **Usage**: `from providers.pinecone_client import PineconeClient`

## 🚫 Forbidden Patterns

❌ **Direct SDK imports outside providers**:
```python
# WRONG - Violates isolation
import redis
import chromadb
from pinecone import Pinecone
```

✅ **Provider delegation pattern**:
```python
# CORRECT - Maintains isolation
from providers.redis_client import RedisClient
from providers.chromadb_client import ChromaClient
```

## 🧪 Enforcement

The provider isolation is automatically enforced by:
```bash
pytest tests/modularity/test_provider_isolation.py::test_only_providers_contain_provider_sdks -v
```

This test scans all Python files and ensures external SDKs are only imported in the `providers/` directory.

## 🔧 Adding New Providers

1. Create provider client in `providers/your_provider.py`
2. Isolate all SDK imports to that file
3. Provide clean interface methods
4. Update other layers to use your provider instead of direct imports
5. Add your SDK to the test's `external_sdks` set
6. Verify the isolation test still passes

## 📋 Benefits

- **Clean Architecture**: Clear separation between application logic and external dependencies
- **Testability**: Easy to mock providers for testing
- **Maintainability**: SDK changes only affect provider implementations
- **Security**: Controlled surface area for external dependencies
- **Compliance**: Enforced by automated testing

## 🎯 Current Status

✅ **Zero violations** - All external SDKs properly isolated
✅ **118 tests passing** - No regressions introduced
✅ **Backward compatibility** - Existing imports still work
✅ **Production ready** - Full test coverage and architectural enforcement
