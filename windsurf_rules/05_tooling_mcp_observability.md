# /windsurf_rules/05_tooling_mcp_observability.md
## Tooling, MCP, SDK, and Observability Rules (Condensed)

### 1. L2 Tooling Rules
- Only L2 may execute tools.
- Tools require explicit schemas (input/output).
- Must implement retries, backoff, timeouts, circuit breakers.
- No tool logic allowed in L1, L3, L4, or L5.

### 2. MCP vs SDK
- MCP MUST be used when available.
- SDK allowed only when MCP unavailable.
- SDK usage must remain in L2 and be sandboxed.

### 3. Execution Sandbox
- Tools must not access host filesystem or environment.
- Must run in isolated execution environments.
- No shell escapes or OS command execution.

### 4. Observability
- Trace IDs required.
- DAG-level spans mandatory.
- Logs must exclude secrets/PII.
- Tool calls must emit latency, cost, and failure data.
