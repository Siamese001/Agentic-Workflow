# Dashboard Meta-Learning Guide

**Version**: 1.0.0
**Last Updated**: 2026-01-16
**Phase**: 7 - Documentation and Deployment

This guide explains how to use and interpret the Live Runtime Dashboard's meta-learning visualization features.

---

## Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Meta-Learning Activity Panel](#meta-learning-activity-panel)
4. [Redis Cache Activity Panel](#redis-cache-activity-panel)
5. [Pinecone Vector Operations Panel](#pinecone-vector-operations-panel)
6. [Agent Execution Flow Panel](#agent-execution-flow-panel)
7. [Troubleshooting](#troubleshooting)
8. [FAQ](#faq)

---

## Overview

The Live Runtime Dashboard provides real-time visualization of the agentic system's meta-learning capabilities. It displays:

- **Experience Stream**: Real-time feed of learning experiences as agents execute
- **Strategy Weights**: Current weighting of different reasoning strategies (CoT, ToT, ReAct, Reflection)
- **Redis Cache Activity**: Cache hit/miss rates and recent operations
- **Pinecone Vector Operations**: Vector storage and query statistics
- **Agent Execution Timeline**: Visual representation of agent execution sequence

### Key Benefits

- **Real-time Observability**: Monitor system behavior as it happens
- **Performance Insights**: Identify bottlenecks and optimization opportunities
- **Learning Transparency**: Understand how the system adapts over time
- **Debugging Support**: Trace issues through the execution timeline

---

## Getting Started

### Prerequisites

1. Python 3.10+
2. FastAPI and Uvicorn installed (`pip install fastapi uvicorn`)
3. Redis server (optional, for cache monitoring)
4. Pinecone account (optional, for vector operations)

### Starting the Dashboard

1. **Start the Runtime API Server**:
   ```bash
   python scripts/start_runtime_api.py
   ```
   The API server runs on port 8081 by default.

2. **Start the Dashboard Server**:
   ```bash
   python -m http.server 8765 --directory agentic_core/L6_observability/dashboards
   ```

3. **Access the Dashboard**:
   Open your browser and navigate to:
   ```
   http://localhost:8765/autonomy_dashboard.html#runtime
   ```

4. **Run the Canon Validator** (to generate live data):
   ```bash
   python canon_validator_agentic_v2_thin.py --heal
   ```

---

## Meta-Learning Activity Panel

### Experience Stream

The experience stream shows real-time learning experiences as they are captured by the `MetaLearningAgent`.

#### Understanding Experience Items

Each experience item displays:

| Field | Description |
|-------|-------------|
| **ID** | Unique identifier for the experience |
| **Thought Type** | The reasoning strategy used (cot, tot, react, reflection) |
| **Reward** | Numerical reward value (0.0 to 1.0) |
| **Timestamp** | When the experience was recorded |

#### Reward Color Coding

- 🟢 **Green (High)**: Reward ≥ 0.7 - Successful outcome
- 🟡 **Yellow (Medium)**: Reward 0.4-0.7 - Partial success
- 🔴 **Red (Low)**: Reward < 0.4 - Needs improvement

### Strategy Weights Chart

The strategy weights chart shows the current weighting of different reasoning strategies:

| Strategy | Description |
|----------|-------------|
| **CoT** | Chain-of-Thought reasoning |
| **ToT** | Tree-of-Thought exploration |
| **ReAct** | Reasoning + Acting interleaved |
| **Reflection** | Self-reflection and correction |

#### Interpreting Weights

- **Higher bars** indicate strategies that have been more successful
- **Balanced weights** suggest the system is still exploring
- **Dominant strategy** may indicate specialization for the current task type

### Pattern Timeline

Shows patterns extracted from accumulated experiences over time:

- **Pattern Type**: Category of the extracted pattern
- **Timestamp**: When the pattern was identified
- **Confidence**: How confident the system is in the pattern

---

## Redis Cache Activity Panel

### Cache Statistics

| Metric | Description |
|--------|-------------|
| **Total Operations** | Total GET/SET/DELETE operations |
| **Cache Hits** | Successful cache retrievals |
| **Cache Misses** | Failed cache lookups |
| **Hit Rate** | Percentage of successful cache hits |

### Hit Rate Interpretation

- 🟢 **≥ 80%**: Excellent - Cache is highly effective
- 🟡 **50-80%**: Good - Normal operation
- 🔴 **< 50%**: Poor - Consider cache warming or TTL adjustment

### Recent Operations Log

Shows the last 20 Redis operations with:

- **Operation Type**: GET, SET, or DELETE
- **Key**: The cache key (truncated for display)
- **Hit/Miss**: Whether the operation was a cache hit
- **Timestamp**: When the operation occurred

### Optimization Tips

1. **Low Hit Rate?**
   - Increase cache TTL for stable data
   - Pre-warm cache on startup
   - Review cache key patterns for consistency

2. **High Memory Usage?**
   - Reduce TTL for volatile data
   - Implement LRU eviction
   - Monitor key expiration patterns

---

## Pinecone Vector Operations Panel

### Vector Statistics

| Metric | Description |
|--------|-------------|
| **Vectors Stored** | Total vectors in the index |
| **Total Operations** | Upsert + Query + Delete count |
| **Avg Similarity** | Average similarity score from queries |

### Query Results Visualizer

Shows recent vector queries with:

- **Top-K**: Number of results requested
- **Results Count**: Actual results returned
- **Avg Score**: Average similarity score
- **Timestamp**: When the query was executed

### Similarity Score Interpretation

- 🟢 **≥ 0.8**: High similarity - Strong semantic match
- 🟡 **0.5-0.8**: Moderate similarity - Related content
- 🔴 **< 0.5**: Low similarity - Weak match

### Best Practices

1. **Improving Query Quality**:
   - Use more specific query vectors
   - Increase top_k for broader results
   - Filter by metadata when possible

2. **Optimizing Storage**:
   - Batch upserts for efficiency
   - Use namespaces to organize vectors
   - Regularly clean up stale vectors

---

## Agent Execution Flow Panel

### Execution Timeline

Shows the sequence of agent executions with:

- **Agent Name**: Which agent executed
- **Layer**: The architectural layer (L0-L6)
- **Duration**: Execution time in milliseconds
- **Status**: Success or failure indicator

### Layer Flow Diagram

Visual representation of execution flow through layers:

```
L0 → L1 → L2 → L3 → L4 → L5 → L6
```

#### Layer Status Colors

- 🟢 **Green (Completed)**: Layer execution finished successfully
- 🔵 **Blue (Active)**: Currently executing
- ⚪ **Gray (Pending)**: Not yet started

### Execution Summary

Aggregated statistics:

| Metric | Description |
|--------|-------------|
| **Total Agents** | Number of agents executed |
| **Avg Duration** | Average execution time |
| **Success Rate** | Percentage of successful executions |
| **Total Duration** | End-to-end execution time |

---

## Troubleshooting

### Dashboard Not Loading

1. **Check API Server**:
   ```bash
   curl http://localhost:8081/api/health
   ```
   Should return `{"status": "healthy"}`

2. **Check Dashboard Server**:
   Ensure port 8765 is not in use

3. **Check Browser Console**:
   Look for JavaScript errors (F12 → Console)

### No Data Appearing

1. **Verify Runtime State File**:
   ```bash
   cat runtime_state.json
   ```
   Should contain recent data

2. **Check Polling**:
   The dashboard polls every 2 seconds by default

3. **Run Canon Validator**:
   ```bash
   python canon_validator_agentic_v2_thin.py --heal
   ```

### Stale Data

1. **Hard Refresh Browser**:
   - Windows/Linux: `Ctrl+Shift+R`
   - Mac: `Cmd+Shift+R`

2. **Clear Browser Cache**:
   Or use incognito/private browsing

3. **Restart API Server**:
   ```bash
   # Stop existing server (Ctrl+C)
   python scripts/start_runtime_api.py
   ```

### Redis Connection Issues

1. **Check Redis Server**:
   ```bash
   redis-cli ping
   ```
   Should return `PONG`

2. **Check Environment Variable**:
   ```bash
   echo $REDIS_URL
   ```
   Default: `redis://localhost:6379`

### Pinecone Connection Issues

1. **Check API Key**:
   Ensure `PINECONE_API_KEY` is set

2. **Check Index Name**:
   Verify the index exists in your Pinecone console

---

## FAQ

### Q: How often does the dashboard update?

**A**: The dashboard polls the API every 2 seconds by default. You can modify this in `meta-learning-controller.js`.

### Q: Can I export the data?

**A**: Yes, the runtime state is stored in `runtime_state.json`. You can also access raw data via the API endpoints.

### Q: How do I add custom metrics?

**A**: See the [Developer Documentation](META_LEARNING_TELEMETRY_API.md) for instructions on adding custom telemetry hooks.

### Q: What's the performance impact?

**A**: Minimal. The telemetry system adds < 5% CPU overhead and < 100MB memory footprint.

### Q: Can I run multiple dashboard instances?

**A**: Yes, the API server supports multiple concurrent connections.

### Q: How do I disable telemetry?

**A**: Set `telemetry_callback=None` when initializing agents, or don't start the API server.

---

## Consolidated Pipeline (January 2026)

The dashboard pipeline has been consolidated for easier maintenance. Use these canonical scripts:

### Regeneration

```bash
# Full regeneration (HTML + data)
python scripts/regenerate_dashboard.py --full

# Data files only
python scripts/regenerate_dashboard.py --data-only
```

### Verification

```bash
# Quick check
python scripts/verify_dashboard.py --quick

# Full validation
python scripts/verify_dashboard.py --full
```

### Testing

```bash
# Run all dashboard tests
pytest tests/dashboard/
```

For detailed developer documentation, see [DASHBOARD_DEVELOPER_GUIDE.md](DASHBOARD_DEVELOPER_GUIDE.md).

---

## Related Documentation

- [DASHBOARD_DEVELOPER_GUIDE.md](DASHBOARD_DEVELOPER_GUIDE.md) - Developer guide for dashboard pipeline
- [META_LEARNING_TELEMETRY_API.md](META_LEARNING_TELEMETRY_API.md) - Developer API documentation
- [DASHBOARD_LIVE_RUNTIME_META_LEARNING_PLAN.md](../DASHBOARD_LIVE_RUNTIME_META_LEARNING_PLAN.md) - Implementation plan

---

**End of User Guide**
