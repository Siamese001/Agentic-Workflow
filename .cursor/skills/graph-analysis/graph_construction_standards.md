# Graph Construction Standards

## Valid Graph Evidence

Evidence is valid only when it comes from the ADG MCP tools. Text search output is confirmation-only.

## Node Types

| Type | Description |
|---|---|
| `MODULE` | Python module file |
| `CLASS` | Python class definition |
| `FUNCTION` | Python function/method |
| `CONSTANT` | Module-level constant |
| `AGENT` | Registered agent class |

## Edge Types

| Type | Description |
|---|---|
| `IMPORTS` | Module-level import dependency |
| `CALLS` | Function call relationship |
| `INHERITS` | Class inheritance |
| `REGISTERS` | Agent/factory registration |
| `READS` | Data read dependency |
| `WRITES` | Data write dependency |

## Graph Roots

Select graph roots by:
1. Files directly modified by the task
2. Files containing the failing test or failing assertion
3. Entry point modules (CLI, `__main__`, factory registries)

## Analysis Depth

| Tier | Fan-out depth | Fan-in depth |
|---|---|---|
| T2 | 1–2 hops | 1 hop |
| T3 | All reachable | All reachable |

## Fail-Closed Rule

If the ADG MCP fails to parse or returns an error:
1. STOP — do not fall back silently to grep/text search
2. Run `/mcp-failure-rca`
3. Wait for recovery before proceeding with T2/T3 work
