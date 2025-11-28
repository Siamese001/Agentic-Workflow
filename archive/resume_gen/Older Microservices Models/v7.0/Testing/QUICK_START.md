# V7.0 Quick Start Guide

## TL;DR
Your v6.5 Resume Generation Engine has been refactored to v7.0 with:
- **LangGraph** replacing custom Governor orchestration
- **Redis** for persistent, resumable workflows  
- **LangSmith** for complete observability

## Installation

```bash
# 1. Install new dependencies
pip install -r requirements.txt

# 2. Start Redis (required)
docker run -d -p 6379:6379 redis:latest
# OR: redis-server

# 3. Configure LangSmith (optional but recommended)
# Edit master_config_v7_0.json:
{
  "tracing_config": {
    "langsmith_enabled": true,
    "langsmith_api_key": "YOUR_KEY_HERE"  # Get from smith.langchain.com
  }
}
```

## Running Workflows

### Single Job
```bash
python main_v7_0.py -j job_input.json -m master_resume.json -o output/
```

### Batch Processing
```bash
# Place job files in batch_queue/
python run_batch_v7_0.py
```

### Meta-Learning
```bash
python run_learning_v7_0.py
```

## Key Differences from v6.5

### What Changed
| v6.5 | v7.0 |
|------|------|
| `WorkflowV65()` | `get_graph_app(RedisSaver)` |
| `CrewOrchestrator` | LangGraph StateGraph |
| `Governor` class | Node wrapper functions |
| In-memory state | Redis persistence |
| No tracing | LangSmith observability |

### What Stayed the Same
- ✅ All agent classes (ThemeClassifierAgent, RAG agents, QA agents, etc.)
- ✅ Master resume JSON format
- ✅ Job input JSON format
- ✅ Batch processing logic
- ✅ Meta-learning feedback loop
- ✅ Cost tracking agents

## Architecture Overview

```python
# v7.0 Execution Flow
app = get_graph_app(RedisSaver(...))

inputs = {
    "master_resume": {...},
    "job_input": {...},
    "artifacts": {},
    "replan_count": 0,
    "workflow_id": "unique-id"
}

final_state = app.invoke(inputs, config={"configurable": {"thread_id": "unique-id"}})
```

### Graph Structure
```
strategy → rag_stack → drafting_stack → qa_swarm
                                            ↓
                                      [check results]
                                       ↙         ↘
                                    END      replanner → (loop to drafting)
```

## Debugging & Observability

### LangSmith Traces
1. Visit smith.langchain.com
2. Find project "ResumeFactory_v7"
3. View complete execution traces with timing and token counts

### Redis Inspection
```bash
# View all workflows
redis-cli KEYS "*"

# Inspect specific workflow
redis-cli GET "workflow:your-workflow-id"
```

### Logs
- **Structured Logs:** `workflow_execution.log` (JSON format)
- **Feedback Log:** `feedback_log.jsonl` (for meta-learning)

## Resuming Failed Workflows

```python
from agent_swarm_v7_0 import get_graph_app
from langgraph.checkpoint.redis import RedisSaver

checkpointer = RedisSaver(host="localhost", port=6379, db=0)
app = get_graph_app(checkpointer)

# Use the SAME thread_id from the failed run
run_config = {"configurable": {"thread_id": "failed-workflow-id"}}

# Resume from last checkpoint
final_state = app.invoke(inputs, config=run_config)
```

## Common Issues

### Redis Not Running
**Error:** `ConnectionRefusedError: [Errno 111] Connection refused`  
**Fix:** Start Redis: `docker run -d -p 6379:6379 redis:latest`

### LangSmith API Key Invalid
**Error:** `Invalid API key`  
**Fix:** Get key from smith.langchain.com or disable tracing:
```json
{"tracing_config": {"langsmith_enabled": false}}
```

### Import Error
**Error:** `ImportError: cannot import name 'Governor'`  
**Fix:** Governor was deleted in v7.0. Use `get_graph_app()` instead.

## Performance Notes

- **Parallel Jobs:** Run 2-3 workflows simultaneously with different `thread_id` values
- **Redis Memory:** ~2-5 MB per workflow checkpoint
- **LangSmith:** Minimal overhead (<50ms per trace)
- **Cost:** Same as v6.5 (agent costs unchanged)

## Migration Checklist

- [ ] Backup v6.5 files
- [ ] Install requirements.txt
- [ ] Start Redis server
- [ ] Configure LangSmith key (or disable)
- [ ] Test single workflow
- [ ] Verify LangSmith traces appear
- [ ] Test workflow resumption
- [ ] Test batch processing
- [ ] Verify meta-learning still works

## Next Steps

1. **Test v7.0 thoroughly** with your existing job inputs
2. **Monitor LangSmith** to identify performance bottlenecks
3. **Experiment with resumption** for long-running or failed jobs
4. **Scale horizontally** by running multiple workers with Redis

## Support

See `V7.0_REFACTOR_SUMMARY.md` for complete technical details.

---

*Architecture Version: 7.0.0-langgraph-redis*
