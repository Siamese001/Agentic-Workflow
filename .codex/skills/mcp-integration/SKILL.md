---
name: mcp-integration
description: Use this skill when choosing among repository-configured MCP servers, diagnosing MCP availability, or coordinating a cross-server workflow. Use adg-sqlite directly for structural dependency analysis.
metadata:
  owner: platform-team
  version: "2.0"
---

# MCP integration

Root `.mcp.json` is the configured-server source of truth. A declared server is not proven callable
until its tools are exposed and a suitable read-only health or discovery call succeeds in the current
session.

## Routing table

| Need | Procedure |
|---|---|
| Filesystem batches or cross-root reads | [sections/01-filesystem-mcp.md](sections/01-filesystem-mcp.md) |
| Redis projection and cache state | [sections/02-redis-cache.md](sections/02-redis-cache.md) |
| Third-party GitHub repository Q&A | [sections/03-deepwiki.md](sections/03-deepwiki.md) |
| Versioned external package documentation | [sections/04-context7.md](sections/04-context7.md) |
| Browser interaction and UI evidence | [sections/05-playwright.md](sections/05-playwright.md) |
| Semantic similarity retrieval | [sections/06-vector-db.md](sections/06-vector-db.md) |
| Notion page or database operations | [sections/07-notion.md](sections/07-notion.md) |
| Web search, extraction, mapping, or crawling | [sections/08-tavily-research.md](sections/08-tavily-research.md) |
| Runtime spans, anomalies, or telemetry | [sections/09-otel-telemetry.md](sections/09-otel-telemetry.md) |
| Structured pytest discovery and runs | [sections/10-pytest-mcp.md](sections/10-pytest-mcp.md) |
| Git, branch, PR, or issue operations | [sections/11-gitkraken.md](sections/11-gitkraken.md) |
| Optional cross-session knowledge graph | [sections/12-memory-mcp.md](sections/12-memory-mcp.md) |
| Explicit durable task tracking | [sections/13-task-manager-mcp.md](sections/13-task-manager-mcp.md) |

Load only the section needed for the current intent. Do not recreate per-server redirect skills in the
active skill tree.

## Workflow

1. Classify the user intent and select one primary authority.
2. Confirm the server is configured and the expected tool is currently exposed.
3. Inspect the current tool schema; do not infer parameters from a stale skill example.
4. Prefer a read-only health or discovery call before a state-changing call.
5. Apply least privilege, bounded results, explicit timeouts, and a rollback or compensating action for
   mutations.
6. Report the actual server/tool used and any degraded fallback.

## Boundaries

- Structural imports, consumers, layers, and blast radius belong to `adg-sqlite`/`graph-analysis`.
- Runtime traces do not replace static dependency evidence, and static graphs do not prove runtime
  execution.
- Vector similarity does not establish a code dependency.
- Native file tools are preferred for ordinary single-file workspace reads and writes.
- File memory under `memory/` remains project memory authority; a memory MCP is an optional graph
  projection.
- A dormant section is documentation for restoration, not evidence that a server is callable.

Read [agents-tier1-companion.md](agents-tier1-companion.md) for the compact operator view and
[SUPPORTING.md](SUPPORTING.md) only for legacy overflow that has not yet been retired.

## Validation

```bash
python .codex/governance/scripts/sync_mcp_config.py --check
python ops_scripts/ci/check_agents_mcp_coverage.py
python ops_scripts/ci/run_skill_contract_gates.py
```
