# Pinecone Vector Database Integration

## Overview

The Agentic-Workflow-10_10 system now includes full Pinecone vector database integration for semantic search and retrieval operations. The integration follows the strict L1/L2/L3 layering architecture.

## Architecture

### Layer Separation

- **L1 (Planning)**: `l1/vector_search_planning.py`
  - Pure planning functions that generate typed plans
  - No actual vector operations or SDK calls
  - Functions: `plan_vector_search()`, `plan_vector_upsert()`

- **L2 (Execution)**: `l2/vector_search_executor.py`
  - Executes vector operations using PineconeClient
  - Handles text embedding via OpenAI
  - Methods: `get_embedding()`, `upsert_text()`, `search()`

- **Providers**: `providers/pinecone_client/`
  - Thin wrapper around Pinecone SDK
  - Abstracts vector operations: upsert, query, delete
  - Integrates OpenAI embeddings

## Setup

### 1. Install Dependencies

```bash
pip install pinecone openai
```

### 2. Environment Variables

Set the following environment variables:

```bash
PINECONE_API_KEY=your_pinecone_api_key
OPENAI_API_KEY=your_openai_api_key
```

### 3. Create Pinecone Index

Before using the integration, create a Pinecone index with appropriate dimensions:

- For `text-embedding-3-small`: 1536 dimensions
- For `text-embedding-3-large`: 3072 dimensions

## Usage Examples

### Basic Usage

```python
from providers.pinecone_client import PineconeClient
from l2.vector_search_executor import VectorSearchExecutor
from l1.vector_search_planning import plan_vector_search, plan_vector_upsert

# Initialize clients
pinecone_client = PineconeClient(
    api_key="your_api_key",
    index_name="your_index_name"
)

executor = VectorSearchExecutor(pinecone_client)

# Upsert documents
executor.upsert_text(
    namespace="documents",
    id="doc1",
    text="This is a sample document about machine learning.",
    metadata={"category": "AI", "source": "example"}
)

# Search for similar documents
results = executor.search(
    namespace="documents",
    query_text="What is machine learning?",
    top_k=5
)

for result in results:
    print(f"ID: {result.id}, Score: {result.score}")
    print(f"Text: {result.metadata.get('text')}")
```

### Using L1 Planning

```python
from l1.vector_search_planning import plan_vector_search, plan_vector_upsert

# Create a search plan
search_plan = plan_vector_search(
    query="machine learning algorithms",
    namespace="documents",
    top_k=10,
    metadata_filters={"category": "AI"}
)

# Create an upsert plan
upsert_plan = plan_vector_upsert(
    id="doc2",
    text="Deep learning is a subset of machine learning.",
    namespace="documents",
    metadata={"category": "AI", "topic": "deep_learning"}
)
```

## Testing

Run the vector search tests:

```bash
python -m pytest tests/vector/ -v
```

## Key Features

1. **Semantic Search**: Find similar documents using vector embeddings
2. **Namespace Support**: Organize vectors into logical namespaces
3. **Metadata Filtering**: Filter search results by metadata
4. **OpenAI Embeddings**: Automatic text-to-vector conversion
5. **Type Safety**: Fully typed interfaces with dataclasses
6. **Layer Compliance**: Strict adherence to L1/L2/L3 architecture

## API Reference

### PineconeClient

```python
class PineconeClient:
    def __init__(self, api_key: str, index_name: str)
    def upsert(self, namespace: str, vectors: List[Vector], **kwargs) -> None
    def query(self, namespace: str, vector: List[float], top_k: int, **kwargs) -> List[Dict[str, Any]]
    def delete(self, namespace: str, ids: List[str], **kwargs) -> None
    def get_embedding(self, text: str) -> List[float]
```

### VectorSearchExecutor

```python
class VectorSearchExecutor:
    def __init__(self, pinecone_client: PineconeClient)
    def get_embedding(self, text: str) -> List[float]
    def upsert_text(self, namespace: str, id: str, text: str, metadata: Optional[Dict[str, Any]]) -> None
    def search(self, namespace: str, query_text: str, top_k: int, **kwargs) -> List[SearchResult]
```

### Planning Functions

```python
def plan_vector_search(
    query: str,
    namespace: str = "default",
    top_k: int = 5,
    metadata_filters: Optional[Dict[str, Any]] = None
) -> VectorSearchPlan

def plan_vector_upsert(
    id: str,
    text: str,
    namespace: str = "default",
    metadata: Optional[Dict[str, Any]] = None
) -> VectorUpsertPlan
```

## Notes

- The integration uses `text-embedding-3-small` by default (1536 dimensions)
- All vector operations are namespace-scoped
- Metadata is automatically stored with each vector
- The client handles both tuple and dict response formats from Pinecone

## Troubleshooting

### Import Errors

If you see import errors, ensure:
1. The `pinecone` package (not `pinecone-client`) is installed
2. You're running from the project root directory
3. All `__init__.py` files are present

### API Errors

If you encounter API errors:
1. Verify your API keys are set correctly
2. Ensure your Pinecone index exists and has the correct dimensions
3. Check that your namespace exists or create it on first use
