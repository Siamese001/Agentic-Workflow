# Agentic Hardening Architecture

This document describes the comprehensive hardening suite implemented for the Agentic-Workflow system, transforming agents from "probabilistic text generators" into "deterministic logic engines."

## Overview

The hardening architecture consists of four major components:

1. **Semantic Cache** - Memory for RAG pipeline
2. **MCP Integration** - Dynamic tool discovery
3. **Cognitive Hardening** - Structured outputs and safe execution
4. **Flight Recorder** - Complete observability

---

## 1. Semantic Cache (Phase 0.5)

**Location:** `runtime/shared/semantic_cache.py`

### Purpose
Short-circuits the RAG pipeline for known queries, reducing latency from ~4s to ~0.05s for recurring queries.

### Key Features
- **Cosine Similarity Search**: Local vector index using numpy
- **LRU Eviction**: Automatic cache management
- **Quality Filtering**: Only caches high-confidence responses (>0.8)
- **Statistics Tracking**: Hit rate, miss rate, evictions

### Usage
```python
from runtime.shared.semantic_cache import SemanticCache

cache = SemanticCache(similarity_threshold=0.92, max_entries=1000)

# Lookup
cached_result = await cache.lookup(query_text, query_vector)
if cached_result:
    return cached_result["content"]

# Store
await cache.store(query_text, query_vector, response)

# Stats
stats = cache.get_stats()
print(f"Hit rate: {stats['hit_rate']:.2%}")
```

### Benefits
- **Defensive Resource Management**: Prevents redundant work
- **Latency Floor**: Guarantees <50ms response for cached queries
- **Cache Hygiene**: Confidence-based filtering prevents hallucination memorization

---

## 2. MCP Integration

**Locations:**
- Configuration: `config/mcp_mappings.yaml`
- Manager: `agentic_core/L2_execution/mcp_manager.py`

### Purpose
Transforms agents from hardcoded tool registries to dynamic MCP-native clients with "USB port" connectivity to any data source.

### Architecture Shift
- **Old Way**: Agent → Python Function → API
- **MCP Way**: Agent → MCP Client → MCP Server → Capabilities

### Configuration Example
```yaml
roles:
  RESEARCHER:
    - server: "brave-search"
      command: "npx"
      args: ["-y", "@modelcontextprotocol/server-brave-search"]
      env:
        BRAVE_API_KEY: "${BRAVE_API_KEY}"
```

### Usage
```python
from agentic_core.L2_execution.mcp_manager import create_mcp_manager

# Create and connect
manager = await create_mcp_manager(role="RESEARCHER")

# Discover tools
tools = manager.get_tools_schema()

# Execute tool
result = await manager.execute_tool("search_brave", {"query": "AI research"})

# Cleanup
await manager.cleanup()
```

### Benefits
- **Dynamic Skill Acquisition**: Add capabilities without code changes
- **Context Window Expansion**: Subscribe to resources for updates
- **Separation of Concerns**: Cognition vs IO cleanly separated

---

## 3. Cognitive Hardening

### 3.1 Structured Engine (Instructor)

**Location:** `agentic_core/L2_execution/structured_engine.py`

#### Purpose
Forces LLMs to output valid, schema-compliant JSON using grammar-based constrained decoding.

#### Usage
```python
from agentic_core.L2_execution.structured_engine import StructuredEngine

engine = StructuredEngine(api_key=api_key, model="gpt-4o")

result = await engine.think_structured(
    system_prompt="You are a Python expert",
    user_prompt="Generate code to sort a list"
)

# Result is GUARANTEED to match AgentThoughtProcess schema
print(result.tool_choice)  # "CODE", "SEARCH", etc.
print(result.confidence_score)  # 0.0 to 1.0
```

#### Schema
```python
class AgentThoughtProcess(BaseModel):
    reasoning_trace: List[str]
    relevant_context_keys: List[str]
    tool_choice: Literal["SEARCH", "CODE", "ANSWER", "DELEGATE", "TERMINATE"]
    tool_arguments: Dict[str, Any]
    confidence_score: float  # 0.0 to 1.0
```

### 3.2 Docker Sandbox

**Location:** `runtime/core/sandbox.py`

#### Purpose
Provides ephemeral execution environment where agents can run dangerous code without destroying your system.

#### Usage
```python
from runtime.core.sandbox import create_sandbox

sandbox = await create_sandbox(network_disabled=True)

result = await sandbox.run_code(
    code="print('Hello from sandbox!')",
    timeout=30
)

print(result.stdout)  # "Hello from sandbox!"
print(result.exit_code)  # 0
```

#### Features
- **Isolation**: Runs in Docker container
- **Resource Limits**: 512MB memory limit
- **Network Control**: Optional network disable
- **Timeout Protection**: Prevents infinite loops
- **Automatic Cleanup**: Containers are nuked after execution

---

## 4. Flight Recorder (Telemetry)

**Locations:**
- Recorder: `runtime/core/telemetry.py`
- Dashboard: `dashboard/app.py`

### Purpose
Temporal database of agent cognition for debugging, optimization, and replay.

### Components

#### 4.1 Telemetry Recorder
```python
from runtime.core.telemetry import TelemetryRecorder, TraceEvent

recorder = TelemetryRecorder(db_path="flight_recorder.duckdb")

# Record event
event = TraceEvent(
    trace_id="mission-001",
    span_id="hop-1",
    agent_role="RESEARCHER",
    event_type="THINK_START",
    payload={"context_keys": ["query", "history"]},
    timestamp=time.time()
)
recorder.record_event(event)

# Query
gantt_data = recorder.get_trace_gantt("mission-001")
tool_stats = recorder.get_tool_stats("mission-001")
```

#### 4.2 Streamlit Dashboard

**Launch:**
```bash
streamlit run dashboard/app.py
```

**Features:**
- **Timeline View**: Gantt chart of agent execution
- **Event Stream**: Chronological event browser
- **Black Box Data**: Detailed payload inspection
- **Tool Performance**: MCP tool usage analytics
- **Error Analysis**: Automatic error detection and display

### Benefits
- **Observe**: See agent failures in real-time
- **Orient**: Inspect reasoning payloads
- **Decide**: Identify prompt ambiguities
- **Act**: Re-compile prompts with DSPy
- **Verify**: Confirm fixes with green bars

---

## Integration Example

Here's how all components work together in a hardened SubatomicHop:

```python
from runtime.shared.semantic_cache import SemanticCache
from agentic_core.L2_execution.mcp_manager import create_mcp_manager
from agentic_core.L2_execution.structured_engine import StructuredEngine
from runtime.core.sandbox import create_sandbox
from runtime.core.telemetry import TelemetryRecorder

class HardenedSubatomicHop:
    async def __init__(self, role: str, trace_id: str):
        # Semantic Cache
        self.cache = SemanticCache()

        # MCP Integration
        self.mcp_manager = await create_mcp_manager(role=role)

        # Cognitive Hardening
        self.structured_engine = StructuredEngine(api_key=api_key)
        self.sandbox = await create_sandbox()

        # Telemetry
        self.telemetry = TelemetryRecorder()
        self.trace_id = trace_id

    async def run(self, query: str):
        # Check cache first
        query_vector = await self.embedder.embed(query)
        cached = await self.cache.lookup(query, query_vector)
        if cached:
            return cached

        # Think with structured output
        self.telemetry.record_event(TraceEvent(
            trace_id=self.trace_id,
            span_id=self.id,
            agent_role=self.role,
            event_type="THINK_START",
            payload={},
            timestamp=time.time()
        ))

        decision = await self.structured_engine.think_structured(
            system_prompt=self.system_prompt,
            user_prompt=query
        )

        # Execute in sandbox if code
        if decision.tool_choice == "CODE":
            result = await self.sandbox.run_code(
                code=decision.tool_arguments["code"],
                timeout=30
            )

            if result.exit_code != 0:
                # Self-correction loop
                return await self._repair_code(decision, result.stderr)

        # Use MCP tools
        elif decision.tool_choice == "SEARCH":
            result = await self.mcp_manager.execute_tool(
                "search_brave",
                decision.tool_arguments
            )

        # Cache high-quality results
        if decision.confidence_score > 0.8:
            await self.cache.store(query, query_vector, result)

        return result
```

---

## Installation

### Dependencies
```bash
# Core dependencies
pip install numpy pydantic

# MCP Integration
pip install mcp pyyaml

# Cognitive Hardening
pip install instructor openai docker

# Telemetry
pip install duckdb streamlit plotly pandas
```

### Environment Variables
```bash
# .env file
BRAVE_API_KEY=your_brave_api_key
GITHUB_TOKEN=your_github_token
DATABASE_URL=postgresql://localhost/mydb
OPENAI_API_KEY=your_openai_key
```

---

## Architecture Benefits

### 1. No Infinite Loops
- Genealogy Registry tracks mutation attempts
- Budget-aware execution prevents runaway processes

### 2. No DDOS/Zombies
- Semantic Gatekeeper enforces concurrency limits
- Timeout enforcement kills hanging agents

### 3. No Corrupted Files
- Blob Storage Adapter uses atomic write-move pattern
- Cryptographic verification ensures integrity

### 4. No Redundant Compute
- Semantic Cache prevents duplicate work
- LRU eviction maintains cache hygiene

### 5. No Broken JSON
- Instructor forces schema compliance
- Automatic retry with error feedback

### 6. No System Destruction
- Docker Sandbox isolates dangerous code
- Network disable prevents external attacks

### 7. Complete Observability
- DuckDB stores all agent cognition
- Streamlit provides visual debugging

---

## Next Steps

1. **Deploy to Production**: Swap `LocalDiskAdapter` for `S3Adapter`
2. **Optimize Prompts**: Use DSPy to compile better instructions
3. **Scale Horizontally**: Add more MCP servers as needed
4. **Monitor Performance**: Use Flight Recorder dashboard
5. **Iterate**: Analyze failures and improve

---

## References

- MCP Protocol: https://modelcontextprotocol.io
- Instructor: https://github.com/jxnl/instructor
- DSPy: https://github.com/stanfordnlp/dspy
- DuckDB: https://duckdb.org
- Streamlit: https://streamlit.io
