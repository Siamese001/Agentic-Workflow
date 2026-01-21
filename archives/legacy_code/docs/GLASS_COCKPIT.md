# The Glass Cockpit: Subatomic Flight Recorder

## Overview

The Glass Cockpit is a comprehensive observability system that provides complete visibility into agent execution. It transforms agent cognition from a black box into a transparent, debuggable process through structured telemetry and real-time visualization.

## Architecture

```text
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Hardened      │────▶│  Telemetry       │────▶│   DuckDB        │
│   AutonomousHop │     │  Recorder        │     │   Database      │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐     ┌─────────────────┐
                       │  Streamlit       │◀────│   Flight Data   │
                       │  Dashboard       │     │   Analytics     │
                       └──────────────────┘     └─────────────────┘
```

## Components

### 1. Telemetry Engine (`runtime/core/telemetry.py`)

The telemetry system captures structured events during agent execution:

#### Core Classes

- **`TraceEvent`**: A single telemetry event with metadata

  ```python
  @dataclass
  class TraceEvent:
      trace_id: str      # Unique workflow identifier
      span_id: str       # Individual hop identifier
      agent_role: str    # Agent role (RESEARCHER, CODER, etc.)
      event_type: str    # Event type (THINK, ACT, ERROR, etc.)
      payload: Dict      # Event-specific data
      timestamp: float   # Unix timestamp
  ```

- **`TelemetryRecorder`**: High-performance event ingestion

  - DuckDB backend for analytical queries
  - Batch writing for performance
  - Automatic schema management
  - Index optimization for fast queries

#### Event Types

| Event Type | Description | Payload Data |
|------------|-------------|--------------|
| `HOP_START` | Agent execution begins | goal, constraints, hardening features |
| `THINK_START` | Reasoning phase begins | goal, available engines |
| `DSPY_SUCCESS` | DSPy optimization completed | plan_length, reasoning_length |
| `THINK_COMPLETE` | Reasoning completed | confidence_score, tool_choice |
| `ACT_START` | Action phase begins | verification/sandbox status |
| `TOOL_CALL` | Tool execution initiated | tool_name, is_mcp_tool |
| `MCP_CALL` | MCP tool invoked | tool, args, server_count |
| `SANDBOX_EXECUTION` | Code execution in sandbox | attempt, exit_code, duration |
| `CODE_REPAIR` | Self-correction attempt | repair_duration, success |
| `HOP_SUCCESS` | Agent completed successfully | duration, result_type |
| `HOP_ERROR` | Agent failed | error_type, error_message |

### 2. Agent Instrumentation (`runtime/core/hardened_autonomous_hop.py`)

The HardenedAutonomousHop is fully instrumented with telemetry:

#### Configuration

```python
@dataclass
class HardeningConfig:
    # ... other config ...
    enable_telemetry: bool = False
    telemetry_db_path: str = "flight_recorder.duckdb"
```

#### Automatic Event Logging

```python
# Events are automatically logged throughout execution:
self._log_event("THINK_START", {"goal": goal, "has_structured_engine": True})
self._log_event("MCP_CALL", {"tool": tool_name, "args": tool_args})
self._log_event("SANDBOX_EXECUTION", {"attempt": attempt, "exit_code": result.exit_code})
```

### 3. Streamlit Dashboard (`dashboard/app.py`)

A real-time visualization interface for debugging agents:

#### Key Features

1. **Trace Selection**
   - Browse recent agent executions
   - Filter by duration and event count
   - Global statistics sidebar

2. **Timeline Visualization**
   - Gantt chart of agent execution
   - Color-coded by agent role
   - Hover details for each span

3. **Event Stream Inspection**

   - Chronological event list
   - Filter by event type
   - Detailed payload viewer

4. **Performance Analytics**

   - MCP tool usage statistics
   - Execution duration metrics
   - Error analysis and tracking

5. **Black Box Data Viewer**

   - JSON payload exploration
   - Special handling for key events
   - Export capabilities

## Usage Guide

### 1. Enable Telemetry

```python
from runtime.core.hardened_autonomous_hop import (
    HardenedAutonomousHop,
    HardeningConfig,
    HardenedAutonomousHopConfig
)

# Configure with telemetry enabled
config = HardeningConfig(
    enable_telemetry=True,
    telemetry_db_path="flight_recorder.duckdb",
    enable_mcp=True,
    mcp_role="RESEARCHER"
)

# Create hardened agent
agent = HardenedAutonomousHop(
    hop_function=my_function,
    config=HardenedAutonomousHopConfig(hardening=config)
)

# Run - automatically records telemetry
result = await agent.run("Research latest AI trends")
```

### 2. Launch Dashboard

```bash
# Install dependencies
pip install streamlit plotly pandas duckdb

# Run dashboard
streamlit run dashboard/app.py
```

### 3. Debug Agent Execution

1. **Select a Trace**: Choose from recent executions in the sidebar
2. **View Timeline**: Identify bottlenecks and parallel execution
3. **Inspect Events**: Click events to see detailed payloads
4. **Analyze Errors**: Review error events and their context
5. **Monitor Tools**: Track MCP tool usage and performance

## Query Examples

### Common Telemetry Queries

```python
# Get all errors in the last hour
conn.execute("""
    SELECT trace_id, span_id, event_type, payload
    FROM traces
    WHERE event_type LIKE '%ERROR%'
    AND timestamp > ?
    ORDER BY timestamp DESC
""", [time.time() - 3600])

# Find slow MCP tool calls
conn.execute("""
    SELECT
        trace_id,
        json_extract_string(payload, '$.tool') as tool,
        CAST(json_extract(payload, '$.duration_ms') AS DOUBLE) as duration
    FROM traces
    WHERE event_type = 'MCP_RESULT'
    AND CAST(json_extract(payload, '$.duration_ms') AS DOUBLE) > 5000
    ORDER BY duration DESC
""")

# Analyze agent decision patterns
conn.execute("""
    SELECT
        json_extract(payload, '$.tool_choice') as tool,
        COUNT(*) as usage_count,
        AVG(json_extract(payload, '$.confidence_score')) as avg_confidence
    FROM traces
    WHERE event_type = 'THINK_COMPLETE'
    GROUP BY tool
    ORDER BY usage_count DESC
""")
```

## Performance Considerations

### Database Optimization

1. **Indexes**: Automatically created on trace_id, timestamp, and event_type
2. **Batch Writing**: Events batched for high-throughput scenarios
3. **Cleanup**: Automatic cleanup of old traces (configurable)

### Memory Usage

- DuckDB uses columnar storage for efficient analytics
- Dashboard loads only necessary data
- Connection pooling for concurrent users

### Scaling

- Single database file per environment
- Can handle millions of events
- Export functionality for long-term storage

## Integration with Hardening Features

The telemetry system integrates seamlessly with all hardening layers:

### Constrained Decoding

- Tracks retry attempts and confidence scores
- Monitors schema validation failures
- Records structured output generation

### DSPy Optimization

- Logs optimization success/failure
- Tracks plan generation metrics
- Measures reasoning quality

### Enhanced Sandbox

- Records each code execution attempt
- Tracks self-correction loops
- Monitors resource usage

### Tool Verification

- Logs verification results
- Tracks blocked dangerous operations
- Records security policy violations

### MCP Integration

- Tracks server connection status
- Monitors tool discovery
- Records execution performance

## Best Practices

### 1. Event Design
- Keep payloads structured and queryable
- Include duration metrics for timing analysis
- Use consistent naming conventions

### 2. Query Performance
- Use indexed columns in WHERE clauses
- Leverage DuckDB's JSON functions for nested data
- Aggregate events for summary statistics

### 3. Dashboard Usage
- Start with timeline view for overall flow
- Drill down into specific events for details
- Use filters to focus on relevant events

### 4. Debugging Workflow
1. Identify failure point in timeline
2. Review preceding events for context
3. Examine error payloads for root cause
4. Check tool performance for bottlenecks

## Advanced Features

### Custom Events

Add custom telemetry to your code:

```python
# In your hop function
def my_hop_function(context):
    # Log custom event
    self._log_event("CUSTOM_PROCESSING", {
        "step": "data_validation",
        "records_processed": 1000,
        "validation_errors": 5
    })

    # Continue processing
    pass
```

### Export and Analysis

```python
# Export trace for analysis
telemetry = create_telemetry_recorder()
trace_data = telemetry.export_trace("trace-123", format="json")

# Load in pandas for custom analysis
df = pd.read_json(trace_data)
```

### Real-time Monitoring

```python
# Monitor live traces
while True:
    recent_traces = telemetry.get_recent_traces(limit=5)
    for trace in recent_traces:
        if trace['error_count'] > 0:
            send_alert(f"Errors in trace {trace['trace_id']}")
    time.sleep(60)
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check if DuckDB is installed
   - Verify database file permissions
   - Ensure no other process has locked the file

2. **No Traces Showing**
   - Confirm telemetry is enabled in config
   - Check if agents have run successfully
   - Verify database path is correct

3. **Dashboard Performance**
   - Limit trace history in queries
   - Use filters to reduce data volume
   - Consider database cleanup for old data

4. **Missing Events**
   - Check agent logs for telemetry errors
   - Verify event logging calls
   - Ensure database writes are succeeding

## Future Enhancements

1. **Real-time Streaming**: WebSocket updates for live monitoring
2. **Alerting System**: Automated notifications for errors
3. **Performance Baselines**: ML-based anomaly detection
4. **Multi-agent Views**: Correlate traces across workflows
5. **Export Formats**: Additional formats (CSV, Parquet)
6. **Retention Policies**: Automatic data lifecycle management

## Conclusion

The Glass Cockpit transforms agent debugging from guesswork into science. By capturing every decision, action, and result, it provides the visibility needed to build reliable, performant autonomous systems.

Combined with the hardening features, it creates a complete observability stack that ensures agents not only behave correctly but can be proven to do so.
