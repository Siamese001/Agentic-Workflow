# Retrieval System - Technical Implementation Guide

## Quick Start

### Prerequisites
- Python 3.10+
- Redis (optional, falls back to in-memory cache)
- OpenAI API key (optional, uses mock embeddings for testing)

### Installation
```bash
# The retrieval system is integrated into agentic_core
# No additional installation required
```

### Basic Usage
```python
from agentic_core.L4_state.engines.retrieval_layers import RetrievalOrchestrator

# Initialize the orchestrator
orchestrator = RetrievalOrchestrator()

# Query the system
results = orchestrator.retrieve("How does ADG work?", n_results=5)

# Process results
for result in results['results']:
    print(f"Layer: {result['layer']}")
    print(f"Content: {result['content'][:100]}...")
    print(f"Metadata: {result['metadata']}")
```

## Architecture Deep Dive

### Component Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Agent Query   │───▶│   Orchestrator  │───▶│   L1 Cache      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   L2 Cache      │
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   L3 RAG        │
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   L4 Actions    │
                       └─────────────────┘
```

### Data Flow

1. **Query Reception**: Orchestrator receives query
2. **L1 Check**: Exact match in Redis cache
3. **L2 Check**: Semantic similarity in cache
4. **L3 Search**: Vector search in ChromaDB
5. **L4 Validation**: Action validation if applicable
6. **Response Assembly**: Combine results from all layers

## Configuration

### Environment Variables
```bash
# OpenAI API (optional - uses mock embeddings if not set)
export OPENAI_API_KEY=your_api_key_here

# Redis (optional - uses in-memory fallback if not available)
export REDIS_URL=redis://localhost:6379
export REDIS_PASSWORD=your_password
```

### Cache Configuration
```python
from agentic_core.L4_state.engines.retrieval_layers import (
    L1ExactCache, L2SemanticCache
)

# Configure L1 cache
l1_cache = L1ExactCache(ttl_seconds=3600)

# Configure L2 cache
l2_cache = L2SemanticCache(
    similarity_threshold=0.95,
    ttl_seconds=3600
)
```

### ChromaDB Configuration
```python
from agentic_core.L4_state.engines.retrieval_layers import L3SemanticRAG

# Custom persist directory
rag = L3SemanticRAG(persist_directory="/custom/path/chromadb")
```

## Data Ingestion

### Document Ingestion
```bash
# Ingest all documentation
python tools/ingestion/ingest_docs.py

# Ingest with real embeddings
export OPENAI_API_KEY=your_key
python tools/ingestion/ingest_docs.py

# Test with limited files
python tools/ingestion/ingest_docs.py --limit 100 --dry-run
```

### Trace Ingestion
```bash
# Ingest healing traces
python tools/ingestion/ingest_traces.py

# Test with sample
python tools/ingestion/ingest_traces.py --limit 1000 --mock-embeddings
```

## API Reference

### RetrievalOrchestrator

#### `retrieve(query: str, n_results: int = 5) -> Dict`
Retrieve information using all layers.

**Parameters:**
- `query`: Search query string
- `n_results`: Number of results to return

**Returns:**
```python
{
    "query": "How does ADG work?",
    "layers_used": ["L3"],
    "results": [
        {
            "layer": "L3_Docs",
            "id": "doc_id",
            "content": "Document content...",
            "metadata": {"doc_type": "architecture"},
            "rank": 1
        }
    ],
    "stats": {
        "l1": {...},
        "l2": {...},
        "l3": {...},
        "l4": {...}
    }
}
```

#### `get_all_stats() -> Dict`
Get statistics from all layers.

### L1ExactCache

#### `get(query: str) -> Optional[str]`
Get exact match from cache.

#### `set(query: str, response: str) -> None`
Set response in cache.

#### `get_hit_rate() -> float`
Get cache hit rate.

### L2SemanticCache

#### `get(query: str) -> Optional[str]`
Get semantically similar cached response.

#### `set(query: str, response: str) -> None`
Set response in semantic cache.

#### `get_hit_rate() -> float`
Get cache hit rate.

### L3SemanticRAG

#### `query_docs(query: str, n_results: int = 5) -> List[Dict]`
Query document collection.

#### `query_traces(query: str, n_results: int = 5) -> List[Dict]`
Query traces collection.

### L4AgenticActions

#### `validate_action(action_name: str, parameters: Dict) -> bool`
Validate action parameters.

#### `list_available_actions() -> List[str]`
List available actions.

## Testing

### Run All Tests
```bash
python tools/ingestion/test_retrieval_layers.py
```

### Individual Layer Tests
```python
# Test L1 cache
from tools.ingestion.test_retrieval_layers import test_l1_exact_cache
test_l1_exact_cache()

# Test L2 cache
from tools.ingestion.test_retrieval_layers import test_l2_semantic_cache
test_l2_semantic_cache()

# Test L3 RAG
from tools.ingestion.test_retrieval_layers import test_l3_semantic_rag
test_l3_semantic_rag()

# Test L4 actions
from tools.ingestion.test_retrieval_layers import test_l4_agentic_actions
test_l4_agentic_actions()
```

### Performance Testing
```python
import time
from agentic_core.L4_state.engines.retrieval_layers import RetrievalOrchestrator

orchestrator = RetrievalOrchestrator()

# Benchmark queries
queries = [
    "How does ADG work?",
    "What is L4 state?",
    "Find similar traces",
    "Search architecture docs"
]

start_time = time.time()
for query in queries:
    results = orchestrator.retrieve(query)
    
end_time = time.time()
print(f"Average query time: {(end_time - start_time) / len(queries):.2f}s")
```

## Monitoring

### Cache Statistics
```python
# Get detailed stats
stats = orchestrator.get_all_stats()

for layer, layer_stats in stats.items():
    print(f"{layer}:")
    for key, value in layer_stats.items():
        print(f"  {key}: {value}")
```

### Performance Metrics
```python
# Monitor performance over time
import time
from collections import defaultdict

performance_log = defaultdict(list)

def log_performance(query, results):
    performance_log['queries'].append({
        'timestamp': time.time(),
        'query': query,
        'layers_used': results['layers_used'],
        'result_count': len(results['results'])
    })
```

## Troubleshooting

### Common Issues

#### 1. Cache Not Working
**Problem**: Queries always miss cache
**Solution**: Check Redis connection and TTL settings
```python
from agentic_core.cache import get_hot_cache
cache = get_hot_cache()
print(f"Cache stats: {cache.get_stats()}")
```

#### 2. Slow Queries
**Problem**: L3 queries taking too long
**Solution**: Check ChromaDB collection size and consider indexing
```python
rag = L3SemanticRAG()
stats = rag.get_stats()
print(f"Collection size: {stats}")
```

#### 3. No Results
**Problem**: Queries returning empty results
**Solution**: Verify data ingestion and embedding generation
```bash
# Check collection stats
python tools/ingestion/test_retrieval.py
python tools/ingestion/test_trace_retrieval.py
```

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now all retrieval operations will log detailed information
orchestrator = RetrievalOrchestrator()
results = orchestrator.retrieve("debug query")
```

## Advanced Usage

### Custom Actions
```python
from agentic_core.L4_state.engines.retrieval_layers import L4AgenticActions

actions = L4AgenticActions()

# Add custom action schema
actions.tool_schemas['custom_action'] = {
    "name": "custom_action",
    "description": "Custom action description",
    "parameters": {
        "param1": {"type": "string", "description": "Parameter 1"},
        "param2": {"type": "integer", "description": "Parameter 2"}
    },
    "required": ["param1"]
}
```

### Custom Embeddings
```python
from agentic_core.L4_state.engines.retrieval_layers import L3SemanticRAG

class CustomRAG(L3SemanticRAG):
    def _get_embedding(self, text: str) -> Optional[List[float]]:
        # Implement custom embedding logic
        return custom_embedding_function(text)

rag = CustomRAG()
```

### Batch Processing
```python
# Process multiple queries efficiently
queries = ["query1", "query2", "query3"]
results = []

for query in queries:
    result = orchestrator.retrieve(query)
    results.append(result)
```

## Deployment

### Production Configuration
```python
# config.py
RETRIEVAL_CONFIG = {
    'l1_cache': {
        'ttl_seconds': 7200,  # 2 hours
    },
    'l2_cache': {
        'similarity_threshold': 0.90,
        'ttl_seconds': 3600,
    },
    'l3_rag': {
        'persist_directory': '/data/chromadb',
        'batch_size': 1000,
    },
    'openai': {
        'model': 'text-embedding-ada-002',
        'batch_size': 100,
    }
}
```

### Docker Deployment
```dockerfile
FROM python:3.10

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["python", "-m", "agentic_core.api.server"]
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: retrieval-system
spec:
  replicas: 3
  selector:
    matchLabels:
      app: retrieval-system
  template:
    metadata:
      labels:
        app: retrieval-system
    spec:
      containers:
      - name: retrieval
        image: retrieval-system:latest
        ports:
        - containerPort: 8000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: openai-secret
              key: api-key
        - name: REDIS_URL
          value: "redis://redis-service:6379"
```

## Best Practices

### 1. Query Optimization
- Use specific, targeted queries
- Include relevant keywords
- Avoid overly broad queries

### 2. Cache Management
- Monitor hit rates
- Adjust TTL based on usage patterns
- Clear cache when updating documents

### 3. Performance Tuning
- Batch similar queries
- Use appropriate result limits
- Monitor query performance

### 4. Security
- Validate all inputs
- Use secure Redis connections
- Monitor access patterns

## Contributing

### Development Setup
```bash
# Clone repository
git clone https://github.com/your-org/agentic-workflow.git

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Run linting
ruff check .
ruff format .
```

### Adding New Features
1. Create feature branch
2. Implement with tests
3. Update documentation
4. Submit pull request

---

**Last Updated**: 2026-03-27
**Version**: 1.0
**Contact**: Agentic Workflow Team
