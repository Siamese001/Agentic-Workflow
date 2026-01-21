# SDK Integration Guide - Agentic Workflow

Complete guide for using all 21 agentic SDKs in end-to-end workflow execution.

## Table of Contents

1. [Overview](#overview)
2. [SDK Registry](#sdk-registry)
3. [LLM Provider Integration](#llm-provider-integration)
4. [Vector Store Integration](#vector-store-integration)
5. [Cache Integration](#cache-integration)
6. [Observability Integration](#observability-integration)
7. [MCP Tool Integration](#mcp-tool-integration)
8. [Workflow Orchestration](#workflow-orchestration)
9. [End-to-End Examples](#end-to-end-examples)

---

## Overview

The Agentic Workflow SDK integration layer provides unified access to 21 production-grade SDKs:

### Core LLM Providers (5)
- **OpenAI** - GPT-4o, o1, embeddings, function calling
- **Anthropic** - Claude 3.5 Sonnet, tool use, extended context
- **Google** - Gemini 2.0, multimodal, grounding
- **Mistral** - Mistral Large, code generation, EU compliance
- **Cohere** - Command R+, RAG, reranking, embeddings

### High-Performance Inference (3)
- **Groq** - Ultra-fast inference (Llama, Mixtral on LPU)
- **Together** - Cheap diversified access
- **Fireworks** - Strong tool-calling alternative

### Routing & Structured Outputs (2)
- **LiteLLM** - Unified router, 100+ provider support
- **Instructor** - Structured outputs, Pydantic validation

### Vector Stores (3)
- **ChromaDB** - Local/embedded vector DB
- **Qdrant** - Production vector DB, hybrid search
- **Pinecone** - Managed vector DB, serverless scaling

### Caching & State (2)
- **Redis** - Caching, session management, pub/sub
- **Hiredis** - C parser for Redis (10x faster)

### Orchestration (2)
- **LangGraph** - Stateful agent graphs, cycles
- **LangChain Core** - Minimal abstractions

### Observability (2)
- **OpenTelemetry API** - Tracing API
- **OpenTelemetry SDK** - Tracing implementation

### Document Processing (2)
- **Unstructured** - Universal document parser
- **PyPDF** - Lightweight PDF extraction

### MCP (2)
- **MCP** - Tool server SDK
- **FastMCP** - FastAPI-style MCP framework

---

## SDK Registry

### Validate All SDKs

```python
from runtime.shared import validate_all_sdks

# Get validation report
report = validate_all_sdks()

print(f"Available: {report['available']}/{report['total']}")
print(f"Missing: {report['missing']}")
print(f"Missing API keys: {report['missing_keys']}")

# Check specific SDK
for sdk_name, detail in report['details'].items():
    if not detail['available']:
        print(f"❌ {sdk_name}: {detail['error']}")
```

### Get Available SDKs

```python
from runtime.shared import get_available_sdks, get_sdk_by_category, SDKCategory

# List all available SDKs
available = get_available_sdks()
print(f"Available SDKs: {available}")

# Get SDKs by category
llm_providers = get_sdk_by_category(SDKCategory.LLM_PROVIDER)
vector_stores = get_sdk_by_category(SDKCategory.VECTOR_STORE)
```

---

## LLM Provider Integration

### Basic Usage

```python
from runtime.shared import Provider, get_client, AgentMessage, create_agent_executor

# Create agent executor
executor = create_agent_executor(
    provider=Provider.OPENAI,
    model="gpt-4o",
    temperature=0.7,
)

# Execute agent
messages = [
    AgentMessage(role="user", content="What is machine learning?")
]

response = executor.execute(
    messages=messages,
    system_prompt="You are a helpful AI assistant.",
)

print(response.content)
print(f"Tokens used: {response.usage['total_tokens']}")
```

### Multi-Provider Support

```python
from runtime.shared import Provider, create_agent_executor

# OpenAI
openai_executor = create_agent_executor(provider=Provider.OPENAI)

# Anthropic
anthropic_executor = create_agent_executor(provider=Provider.ANTHROPIC)

# Groq (ultra-fast)
groq_executor = create_agent_executor(provider=Provider.GROQ)

# Together (cost-optimized)
together_executor = create_agent_executor(provider=Provider.TOGETHER)
```

### Structured Outputs with Instructor

```python
from pydantic import BaseModel
from runtime.shared import Provider, create_agent_executor, AgentMessage

class Analysis(BaseModel):
    sentiment: str
    confidence: float
    key_points: list[str]

executor = create_agent_executor(provider=Provider.OPENAI)

messages = [
    AgentMessage(
        role="user",
        content="Analyze: 'This product is amazing! Best purchase ever.'"
    )
]

result = executor.execute_structured(
    messages=messages,
    response_model=Analysis,
)

print(f"Sentiment: {result.sentiment}")
print(f"Confidence: {result.confidence}")
print(f"Key points: {result.key_points}")
```

### Tool Calling

```python
from runtime.shared import create_agent_executor, AgentMessage

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location"],
            },
        },
    }
]

executor = create_agent_executor(provider=Provider.OPENAI)

messages = [
    AgentMessage(role="user", content="What's the weather in Paris?")
]

response = executor.execute(messages=messages, tools=tools)

if response.tool_calls:
    for tool_call in response.tool_calls:
        print(f"Tool: {tool_call['function']['name']}")
        print(f"Args: {tool_call['function']['arguments']}")
```

---

## Vector Store Integration

### ChromaDB (Local/Embedded)

```python
from runtime.shared import (
    VectorStoreProvider,
    get_vector_store,
    create_chroma_collection,
    upsert_vectors_chroma,
    search_vectors_chroma,
)

# Get ChromaDB client
client = get_vector_store(VectorStoreProvider.CHROMA)

# Create collection
collection = create_chroma_collection(client, "knowledge_base")

# Upsert vectors
upsert_vectors_chroma(
    collection,
    ids=["doc1", "doc2", "doc3"],
    embeddings=[[0.1] * 1536, [0.2] * 1536, [0.3] * 1536],
    documents=["First document", "Second document", "Third document"],
    metadatas=[{"source": "web"}, {"source": "pdf"}, {"source": "api"}],
)

# Search
results = search_vectors_chroma(
    collection,
    query_embeddings=[[0.15] * 1536],
    n_results=5,
    where={"source": "web"},
)

print(results)
```

### Qdrant (Production)

```python
from runtime.shared import (
    VectorStoreProvider,
    QdrantConfig,
    get_vector_store,
    create_qdrant_collection,
    upsert_vectors_qdrant,
    search_vectors_qdrant,
)

# Get Qdrant client
config = QdrantConfig(host="localhost", port=6333)
client = get_vector_store(VectorStoreProvider.QDRANT, config)

# Create collection
create_qdrant_collection(client, "documents", vector_size=1536)

# Upsert vectors
upsert_vectors_qdrant(
    client,
    collection_name="documents",
    ids=["1", "2", "3"],
    vectors=[[0.1] * 1536, [0.2] * 1536, [0.3] * 1536],
    payloads=[{"text": "doc1"}, {"text": "doc2"}, {"text": "doc3"}],
)

# Search
results = search_vectors_qdrant(
    client,
    collection_name="documents",
    query_vector=[0.15] * 1536,
    limit=5,
    score_threshold=0.7,
)

for result in results:
    print(f"Score: {result.score}, Payload: {result.payload}")
```

---

## Cache Integration

### Redis Caching

```python
from runtime.shared import (
    get_redis_client,
    cache_set,
    cache_get,
    cache_get_many,
    cache_set_many,
    cache_clear_pattern,
)

# Get Redis client
client = get_redis_client()

# Set value
cache_set(client, "user:123", {"name": "Alice", "role": "admin"}, ttl=3600)

# Get value
user = cache_get(client, "user:123")
print(user)

# Batch operations
cache_set_many(
    client,
    {
        "session:1": {"user_id": 123},
        "session:2": {"user_id": 456},
    },
    ttl=1800,
)

sessions = cache_get_many(client, ["session:1", "session:2"])
print(sessions)

# Clear pattern
deleted = cache_clear_pattern(client, "session:*")
print(f"Deleted {deleted} keys")
```

---

## Observability Integration

### OpenTelemetry Tracing

```python
from runtime.shared import (
    setup_tracing,
    create_span,
    set_span_attribute,
    add_span_event,
    record_exception,
)

# Setup tracing
setup_tracing()

# Create spans
with create_span("workflow.execute") as span:
    set_span_attribute("workflow.id", "wf-001")
    set_span_attribute("workflow.type", "resume_generation")

    with create_span("hop.analyze"):
        add_span_event("analysis_started", {"input_size": 1024})

        try:
            # Your code here
            result = analyze_data()
            add_span_event("analysis_completed", {"output_size": 512})
        except Exception as e:
            record_exception(e)
            raise
```

### Structured Logging

```python
from runtime.shared import setup_structured_logging, get_structured_logger

# Setup structured logging
setup_structured_logging(service_name="agentic-workflow", log_level="INFO")

# Get logger
logger = get_structured_logger(__name__)

# Log with structured data
logger.info(
    "workflow_started",
    workflow_id="wf-001",
    user_id=123,
    timestamp="2025-01-01T00:00:00Z",
)
```

---

## MCP Tool Integration

### Register Custom Tools

```python
from runtime.shared.mcp_tools import create_mcp_server, MCPTool

# Create MCP server
server = create_mcp_server(name="my-tools", register_defaults=True)

# Register custom tool
def search_database(query: str, limit: int = 10):
    """Search database and return results."""
    # Your search logic here
    return {"results": [], "count": 0}

server.register_function(
    name="search_database",
    description="Search the database for relevant documents",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"},
            "limit": {"type": "integer", "description": "Max results", "default": 10},
        },
        "required": ["query"],
    },
    handler=search_database,
)

# Get tools for LLM
tools = server.get_tools_for_provider("openai")

# Execute tool
result = server.execute_tool("search_database", {"query": "AI", "limit": 5})
print(result.result)
```

---

## Workflow Orchestration

### Create Workflow Context

```python
from runtime.shared import create_workflow_context, Provider

# Create workflow context with all integrations
context = create_workflow_context(
    workflow_id="resume-gen-001",
    provider=Provider.OPENAI,
    model="gpt-4o",
    enable_cache=True,
    enable_vector_store=True,
    enable_tracing=True,
)

# Use context
context.set_in_cache("state", {"status": "running"}, ttl=3600)
state = context.get_from_cache("state")

# Search knowledge base
results = context.search_knowledge(
    query_embedding=[0.1] * 1536,
    collection_name="resume_templates",
    n_results=10,
)
```

### Workflow Orchestrator

```python
from runtime.shared import WorkflowOrchestrator, AgentMessage

# Create orchestrator
orchestrator = WorkflowOrchestrator(
    workflow_id="analysis-workflow",
    provider=Provider.OPENAI,
)

# Define hop functions
def extract_hop(context):
    """Extract key information."""
    input_text = context.get_input("text")

    messages = [
        AgentMessage(role="user", content=f"Extract key points from: {input_text}")
    ]

    response = context.execute_agent(
        messages=messages,
        system_prompt="You are an extraction expert.",
    )

    context.set_output("extracted_points", response.content)

def analyze_hop(context):
    """Analyze extracted points."""
    points = context.get_input("extracted_points")

    messages = [
        AgentMessage(role="user", content=f"Analyze these points: {points}")
    ]

    response = context.execute_agent(
        messages=messages,
        system_prompt="You are an analysis expert.",
    )

    context.set_output("analysis", response.content)

# Register hops
orchestrator.register_hop("extract", extract_hop)
orchestrator.register_hop("analyze", analyze_hop, dependencies=["extract"])

# Execute workflow
outputs = orchestrator.execute(
    initial_inputs={"text": "Your input text here..."}
)

print(outputs["analysis"])
```

---

## End-to-End Examples

### Complete RAG Workflow

```python
from runtime.shared import (
    create_workflow_context,
    Provider,
    AgentMessage,
    get_vector_store,
    VectorStoreProvider,
    create_chroma_collection,
    search_vectors_chroma,
)

# Setup
context = create_workflow_context(
    workflow_id="rag-001",
    provider=Provider.OPENAI,
    enable_vector_store=True,
    enable_cache=True,
)

# Get embeddings (using OpenAI)
def get_embedding(text: str):
    from openai import OpenAI
    client = OpenAI()
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return response.data[0].embedding

# Index documents
collection = create_chroma_collection(context.vector_store, "knowledge")
docs = ["Doc 1 content", "Doc 2 content", "Doc 3 content"]
embeddings = [get_embedding(doc) for doc in docs]

from runtime.shared import upsert_vectors_chroma
upsert_vectors_chroma(
    collection,
    ids=[f"doc{i}" for i in range(len(docs))],
    embeddings=embeddings,
    documents=docs,
)

# Query with RAG
query = "What is in the documents?"
query_embedding = get_embedding(query)

results = search_vectors_chroma(
    collection,
    query_embeddings=[query_embedding],
    n_results=3,
)

# Generate response with context
context_docs = "\n".join(results["documents"][0])

messages = [
    AgentMessage(
        role="user",
        content=f"Context:\n{context_docs}\n\nQuestion: {query}"
    )
]

response = context.agent_executor.execute(
    messages=messages,
    system_prompt="Answer based only on the provided context.",
)

print(response.content)
```

### Multi-Agent Collaboration

```python
from runtime.shared import WorkflowOrchestrator, AgentMessage, Provider

orchestrator = WorkflowOrchestrator("multi-agent-001", Provider.OPENAI)

def researcher_hop(context):
    """Research agent gathers information."""
    topic = context.get_input("topic")

    messages = [
        AgentMessage(role="user", content=f"Research: {topic}")
    ]

    response = context.execute_agent(
        messages=messages,
        system_prompt="You are a research expert. Provide detailed findings.",
    )

    context.set_output("research", response.content)

def writer_hop(context):
    """Writer agent creates content."""
    research = context.get_input("research")

    messages = [
        AgentMessage(role="user", content=f"Write article based on: {research}")
    ]

    response = context.execute_agent(
        messages=messages,
        system_prompt="You are a professional writer. Create engaging content.",
    )

    context.set_output("article", response.content)

def editor_hop(context):
    """Editor agent reviews and refines."""
    article = context.get_input("article")

    messages = [
        AgentMessage(role="user", content=f"Edit and improve: {article}")
    ]

    response = context.execute_agent(
        messages=messages,
        system_prompt="You are an editor. Refine the content for clarity.",
    )

    context.set_output("final_article", response.content)

# Register pipeline
orchestrator.register_hop("research", researcher_hop)
orchestrator.register_hop("write", writer_hop, dependencies=["research"])
orchestrator.register_hop("edit", editor_hop, dependencies=["write"])

# Execute
result = orchestrator.execute(initial_inputs={"topic": "AI in Healthcare"})
print(result["final_article"])
```

---

## Environment Variables

Required environment variables for SDK integration:

```bash
# LLM Providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
MISTRAL_API_KEY=...
COHERE_API_KEY=...
GROQ_API_KEY=...
TOGETHER_API_KEY=...
FIREWORKS_API_KEY=...

# Vector Stores
PINECONE_API_KEY=...

# Cache
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=...

# Observability
OTEL_SERVICE_NAME=agentic-workflow
ENVIRONMENT=production
```

---

## Testing

Run end-to-end integration tests:

```bash
# Run all tests
pytest tests/integration/test_end_to_end_workflow.py -v

# Run specific test
pytest tests/integration/test_end_to_end_workflow.py::TestWorkflowOrchestration::test_end_to_end_workflow_execution -v

# Skip tests requiring API keys
pytest tests/integration/test_end_to_end_workflow.py -v -m "not requires_api_key"
```

---

## Best Practices

1. **Always validate SDKs** before workflow execution
2. **Use caching** for expensive operations (embeddings, LLM calls)
3. **Enable tracing** in production for observability
4. **Implement retry logic** for external API calls
5. **Use structured outputs** for reliable data extraction
6. **Leverage vector stores** for semantic search and RAG
7. **Register MCP tools** for reusable functionality
8. **Monitor token usage** to optimize costs

---

## Troubleshooting

### SDK Not Available

```python
from runtime.shared import validate_sdk

success, error = validate_sdk("openai")
if not success:
    print(f"Error: {error}")
    # Install: pip install openai>=1.50.0
```

### API Key Missing

```python
import os

if not os.getenv("OPENAI_API_KEY"):
    print("Set OPENAI_API_KEY environment variable")
```

### Redis Connection Failed

```python
from runtime.shared import get_redis_client

try:
    client = get_redis_client()
    client.ping()
except Exception as e:
    print(f"Redis unavailable: {e}")
    # Start Redis: docker run -d -p 6379:6379 redis
```

---

## Additional Resources

- [OpenAI Documentation](https://platform.openai.com/docs)
- [Anthropic Documentation](https://docs.anthropic.com)
- [ChromaDB Documentation](https://docs.trychroma.com)
- [Redis Documentation](https://redis.io/docs)
- [OpenTelemetry Documentation](https://opentelemetry.io/docs)
- [LiteLLM Documentation](https://docs.litellm.ai)
- [Instructor Documentation](https://python.useinstructor.com)
