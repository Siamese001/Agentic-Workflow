# Meta-Learning Telemetry API Documentation

**Version**: 1.0.0  
**Last Updated**: 2026-01-16  
**Phase**: 7 - Documentation and Deployment

This document provides technical documentation for developers who want to extend or integrate with the meta-learning telemetry system.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Telemetry Callback Interface](#telemetry-callback-interface)
3. [API Endpoints](#api-endpoints)
4. [Data Schemas](#data-schemas)
5. [Adding Custom Telemetry Hooks](#adding-custom-telemetry-hooks)
6. [Extension Points](#extension-points)
7. [Best Practices](#best-practices)

---

## Architecture Overview

### Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    canon_validator_agentic_v2_thin.py           │
│                         (Entry Point)                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ telemetry callbacks
┌─────────────────────────────────────────────────────────────────┐
│  MetaLearningAgent  │  SovereignRedisClient  │  PineconeTelemetry│
│     (L1 Cognition)  │    (Utils/Redis)       │   (L4 State)      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ write
┌─────────────────────────────────────────────────────────────────┐
│                      runtime_state.json                          │
│                    (Persistent State File)                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ read
┌─────────────────────────────────────────────────────────────────┐
│                 FastAPI Runtime API (port 8081)                  │
│              agentic_core/L6_observability/api/runtime_api.py    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ HTTP polling
┌─────────────────────────────────────────────────────────────────┐
│                  Dashboard JavaScript (port 8765)                │
│                    MetaLearningController                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ render
┌─────────────────────────────────────────────────────────────────┐
│                    Live Runtime Tab UI                           │
│                  autonomy_dashboard.html#runtime                 │
└─────────────────────────────────────────────────────────────────┘
```

### Component Locations

| Component | File Path |
|-----------|-----------|
| Runtime State Management | `canon_validator_agentic_v2_thin.py` |
| MetaLearningAgent | `agentic_core/L1_cognition/learning/MetaLearningAgent.py` |
| SovereignRedisClient | `agentic_core/utils/core_extensions/redis.py` |
| PineconeTelemetryWrapper | `agentic_core/L4_state/pinecone_telemetry.py` |
| Runtime API | `agentic_core/L6_observability/api/runtime_api.py` |
| Dashboard Controller | `agentic_core/L6_observability/dashboards/js/controllers/meta-learning-controller.js` |

---

## Telemetry Callback Interface

### Callback Signature

All telemetry-enabled components accept a callback with this signature:

```python
from typing import Callable, Dict, Any

TelemetryCallback = Callable[[str, Dict[str, Any]], None]

def my_telemetry_callback(event_type: str, data: Dict[str, Any]) -> None:
    """
    Handle telemetry events.
    
    Args:
        event_type: Type of event (e.g., 'experience_stored', 'redis_get')
        data: Event-specific data dictionary
    """
    print(f"Event: {event_type}, Data: {data}")
```

### MetaLearningAgent Events

```python
from agentic_core.L1_cognition.learning.MetaLearningAgent import MetaLearningAgent

def handle_meta_learning(event_type: str, data: dict):
    if event_type == 'experience_stored':
        # data: {experience_id, thought_type, reward, buffer_size, timestamp}
        pass
    elif event_type == 'patterns_extracted':
        # data: {patterns, total_patterns, timestamp}
        pass
    elif event_type == 'strategy_updated':
        # data: {strategy_weights, timestamp}
        pass

agent = MetaLearningAgent(telemetry_callback=handle_meta_learning)
```

### SovereignRedisClient Events

```python
from agentic_core.utils.core_extensions.redis import SovereignRedisClient

def handle_redis(event_type: str, data: dict):
    if event_type == 'redis_get':
        # data: {key, hit, value, timestamp}
        pass
    elif event_type == 'redis_set':
        # data: {key, ttl, timestamp}
        pass
    elif event_type == 'redis_delete':
        # data: {key, timestamp}
        pass

client = SovereignRedisClient(telemetry_callback=handle_redis)
```

### PineconeTelemetryWrapper Events

```python
from agentic_core.L4_state.pinecone_telemetry import PineconeTelemetryWrapper

def handle_pinecone(event_type: str, data: dict):
    if event_type == 'pinecone_upsert':
        # data: {count, namespace, vectors_stored, timestamp}
        pass
    elif event_type == 'pinecone_query':
        # data: {top_k, results_count, avg_score, namespace, timestamp}
        pass
    elif event_type == 'pinecone_delete':
        # data: {ids, namespace, timestamp}
        pass

wrapper = PineconeTelemetryWrapper(telemetry_callback=handle_pinecone)
```

---

## API Endpoints

### Base URL

```
http://localhost:8081/api
```

### Health Check

```http
GET /api/health
```

**Response:**
```json
{
    "status": "healthy",
    "version": "1.0.0"
}
```

### Runtime State

```http
GET /api/runtime/state
```

**Response:** Full runtime state object (see [Runtime State Schema](#runtime-state-schema))

### Meta-Learning Statistics

```http
GET /api/meta-learning/statistics
```

**Response:**
```json
{
    "total_experiences": 150,
    "buffer_size": 100,
    "buffer_capacity": 1000,
    "patterns_extracted": 12,
    "strategy_weights": {
        "cot": 1.2,
        "tot": 0.9,
        "react": 1.1,
        "reflection": 0.8
    },
    "recent_experiences": [
        {
            "id": "exp_abc123",
            "thought_type": "cot",
            "reward": 0.85,
            "timestamp": "2026-01-16T12:00:00"
        }
    ]
}
```

### Meta-Learning Activity

```http
GET /api/meta-learning/activity
```

**Response:**
```json
{
    "total_experiences": 150,
    "patterns_extracted": 12,
    "strategy_weights": {
        "cot": 1.2,
        "tot": 0.9,
        "react": 1.1,
        "reflection": 0.8
    }
}
```

### Post New Experience

```http
POST /api/meta-learning/experience
Content-Type: application/json

{
    "state": {"context": "validation"},
    "thought_type": "cot",
    "outcome": {"success": true},
    "reward": 0.9
}
```

**Response:**
```json
{
    "status": "ok",
    "experience_id": "exp_xyz789",
    "total_experiences": 151
}
```

### Redis Statistics

```http
GET /api/redis/stats
```

**Response:**
```json
{
    "connected": true,
    "operations": {
        "get": 1250,
        "set": 430,
        "delete": 15,
        "total": 1695
    },
    "cache_hits": 1100,
    "cache_misses": 150,
    "hit_rate": 0.88,
    "recent_operations": [
        {
            "operation": "get",
            "key": "agent_config_...",
            "hit": true,
            "timestamp": "2026-01-16T12:00:00"
        }
    ]
}
```

### Redis Logs

```http
GET /api/redis/logs?limit=50
```

**Response:**
```json
{
    "logs": [
        "[12:00:00] META store_experience exp_abc123 reward=0.85",
        "[11:59:58] REDIS GET agent_config hit=true"
    ]
}
```

### Pinecone Statistics

```http
GET /api/pinecone/stats
```

**Response:**
```json
{
    "connected": true,
    "operations": {
        "upsert": 50,
        "query": 200,
        "delete": 5,
        "total": 255
    },
    "vectors_stored": 5000,
    "avg_similarity": 0.82,
    "recent_queries": [
        {
            "top_k": 10,
            "results_count": 10,
            "avg_score": 0.85,
            "namespace": "default",
            "timestamp": "2026-01-16T12:00:00"
        }
    ]
}
```

### Execution Timeline

```http
GET /api/execution/timeline
```

**Response:**
```json
[
    {
        "agent": "NamingAgent",
        "layer": "L5",
        "start": 1705420800.123,
        "end": 1705420800.456,
        "duration": 0.333,
        "success": true
    }
]
```

### API Latency Metrics

```http
GET /api/metrics/latency
```

**Response:**
```json
{
    "pinecone": 42.5,
    "gemini_embeddings": 128.2,
    "redis_lookup": 1.4
}
```

---

## Data Schemas

### Runtime State Schema

```python
runtime_state = {
    "status": "idle",  # idle | running | completed | error
    "start_time": None,  # ISO timestamp or None
    "end_time": None,  # ISO timestamp or None
    "current_agent": None,  # Agent name or None
    "current_layer": None,  # Layer name or None
    "agents_order": [],  # List of agent names in execution order
    "total_agents": 0,  # Total agents to execute
    "completed_agents": [],  # List of completed agent names
    "events": [],  # List of event objects
    
    "meta_learning": {
        "enabled": False,
        "total_experiences": 0,
        "patterns_extracted": 0,
        "strategy_weights": {
            "cot": 1.0,
            "tot": 1.0,
            "react": 1.0,
            "reflection": 1.0
        },
        "recent_experiences": [],  # Last 10 experiences
        "pattern_history": []  # Pattern extraction timeline
    },
    
    "redis": {
        "connected": False,
        "operations": {
            "get": 0,
            "set": 0,
            "delete": 0,
            "total": 0
        },
        "cache_hits": 0,
        "cache_misses": 0,
        "hit_rate": 0.0,
        "recent_operations": []  # Last 20 operations
    },
    
    "pinecone": {
        "connected": False,
        "operations": {
            "upsert": 0,
            "query": 0,
            "delete": 0,
            "total": 0
        },
        "vectors_stored": 0,
        "avg_similarity": 0.0,
        "recent_queries": []  # Last 10 queries
    },
    
    "execution_timeline": []  # List of execution records
}
```

### Experience Schema

```python
experience = {
    "id": "exp_abc123",  # Unique identifier
    "thought_type": "cot",  # cot | tot | react | reflection
    "reward": 0.85,  # Float 0.0 to 1.0
    "state": {},  # Context state dictionary
    "outcome": {},  # Outcome dictionary
    "timestamp": "2026-01-16T12:00:00"  # ISO timestamp
}
```

### Execution Record Schema

```python
execution_record = {
    "agent": "NamingAgent",  # Agent class name
    "layer": "L5",  # Layer identifier
    "start": 1705420800.123,  # Unix timestamp (float)
    "end": 1705420800.456,  # Unix timestamp (float)
    "duration": 0.333,  # Duration in seconds
    "success": True  # Boolean success indicator
}
```

---

## Adding Custom Telemetry Hooks

### Step 1: Define Your Callback

```python
def my_custom_telemetry(event_type: str, data: dict):
    """Custom telemetry handler."""
    # Log to file
    with open('custom_telemetry.log', 'a') as f:
        f.write(f"{event_type}: {data}\n")
    
    # Send to external service
    # requests.post('https://my-service.com/telemetry', json=data)
```

### Step 2: Register with Components

```python
from agentic_core.L1_cognition.learning.MetaLearningAgent import MetaLearningAgent

agent = MetaLearningAgent(telemetry_callback=my_custom_telemetry)
```

### Step 3: Update Runtime State (Optional)

If you want your telemetry to appear in the dashboard, update the runtime state:

```python
from canon_validator_agentic_v2_thin import _runtime_state, _save_runtime_state

def my_custom_telemetry(event_type: str, data: dict):
    # Add custom data to runtime state
    if 'custom_metrics' not in _runtime_state:
        _runtime_state['custom_metrics'] = {}
    
    _runtime_state['custom_metrics'][event_type] = data
    _save_runtime_state(project_root)
```

### Step 4: Add API Endpoint (Optional)

Add a new endpoint to `runtime_api.py`:

```python
@app.get("/api/custom/metrics")
async def get_custom_metrics() -> Dict[str, Any]:
    """Get custom telemetry metrics."""
    try:
        if RUNTIME_STATE_FILE.exists():
            state = json.loads(RUNTIME_STATE_FILE.read_text(encoding='utf-8'))
            return state.get('custom_metrics', {})
        return {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Step 5: Add Dashboard Component (Optional)

Create a new JavaScript component in `js/components/`:

```javascript
// custom-metrics.js
class CustomMetricsPanel {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
    }
    
    update(data) {
        this.container.innerHTML = `
            <div class="custom-metrics">
                <h4>Custom Metrics</h4>
                <pre>${JSON.stringify(data, null, 2)}</pre>
            </div>
        `;
    }
}

window.CustomMetricsPanel = CustomMetricsPanel;
```

---

## Extension Points

### 1. New Telemetry Sources

Add telemetry to any agent by:

1. Adding `telemetry_callback` parameter to `__init__`
2. Calling callback at key points in execution
3. Following the `(event_type: str, data: dict)` signature

### 2. New API Endpoints

Add endpoints to `runtime_api.py`:

```python
@app.get("/api/my-feature/stats")
async def get_my_feature_stats() -> Dict[str, Any]:
    # Return your custom data
    pass
```

### 3. New Dashboard Panels

1. Create JS component in `js/components/`
2. Add CSS styles to `css/meta-learning.css`
3. Add HTML container to `autonomy_dashboard.html`
4. Update `MetaLearningController` to poll and update

### 4. Custom Event Types

Define new event types following the pattern:

```python
# Event type naming: {component}_{action}
# Examples:
# - meta_learning_experience_stored
# - redis_cache_hit
# - pinecone_query_completed
# - custom_agent_started
```

---

## Best Practices

### 1. Telemetry Callback Performance

```python
# DO: Keep callbacks lightweight
def good_callback(event_type: str, data: dict):
    queue.put((event_type, data))  # Async processing

# DON'T: Block on I/O in callbacks
def bad_callback(event_type: str, data: dict):
    requests.post(url, json=data)  # Blocks execution
```

### 2. Data Size Management

```python
# DO: Limit stored data
recent_experiences = recent_experiences[:10]  # Keep last 10

# DON'T: Store unlimited data
recent_experiences.append(exp)  # Memory leak
```

### 3. Error Handling

```python
# DO: Handle errors gracefully
def safe_callback(event_type: str, data: dict):
    try:
        process(data)
    except Exception as e:
        logging.error(f"Telemetry error: {e}")

# DON'T: Let errors propagate
def unsafe_callback(event_type: str, data: dict):
    process(data)  # May crash the agent
```

### 4. Thread Safety

```python
import threading

# DO: Use locks for shared state
_lock = threading.Lock()

def thread_safe_callback(event_type: str, data: dict):
    with _lock:
        _runtime_state['events'].append(data)
```

### 5. Testing

```python
# DO: Test telemetry in isolation
def test_telemetry_callback():
    events = []
    agent = MetaLearningAgent(
        telemetry_callback=lambda t, d: events.append((t, d))
    )
    agent.store_experience(...)
    assert len(events) == 1
    assert events[0][0] == 'experience_stored'
```

---

## Related Documentation

- [DASHBOARD_META_LEARNING_GUIDE.md](DASHBOARD_META_LEARNING_GUIDE.md) - User guide
- [DASHBOARD_LIVE_RUNTIME_META_LEARNING_PLAN.md](../DASHBOARD_LIVE_RUNTIME_META_LEARNING_PLAN.md) - Implementation plan

---

**End of Developer Documentation**
