# /windsurf_rules/07_concurrency_parallelism.md
## Concurrency, Parallel DAG Execution, and Shared Resource Governance

### 1. Parallel Execution Isolation
- Each DAG run must be fully isolated.
- No DAG run may share global mutable state.

### 2. Concurrency Limits
- Maximum parallel DAGs = min(CPU_CORES, CONFIG_LIMIT).
- No unbounded async spawning.
- L2 tools must declare concurrency and rate limits.

### 3. Shared Resource Governance
- Vector-store writes must be serialized.
- Reads may be parallelized with bounded concurrency.
- Redis operations must use pooled connections and timeouts.

### 4. Safety Integration
- L5 may pause, block, or reroute concurrent runs.
- Cross-thread unsafe behavior is prohibited.
