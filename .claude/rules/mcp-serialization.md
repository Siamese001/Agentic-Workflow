
# MCP Serialization — Remote MCPs Only

> **Remote MCP tool calls MUST be isolated: one remote MCP tool invocation per model tool block where the protocol batches MCP calls, with no sibling remote calls in the same batch.** Sequential separate batches are fine. Local stdio MCPs may batch together per project policy.

## Invariant

1. **Remote MCPs serialize per batch.** Treat as **remote** (network or external subprocess you do not fully colocate with repo-local Python): `notion`, `tavily`, `deepwiki`, `context7`, `GitKraken`, `playwright` (see `.mcp.json` — adjust this list when servers change).
2. **Sequential remote batches OK.** Multiple isolated remote calls across separate model steps are fine.
3. **Local stdio MCPs batch freely** with each other and native file tools where allowed: `adg_sqlite`, `redis`, `memory`, `vector_db`, `pytest_mcp`, `otel_mcp`, `filesystem` (when enabled), `task_manager` (when enabled).
4. **No mixing** remote + local MCP invocations in the same serialized batch if your client batches them together in one transport unit — split across turns/blocks instead.

> **MCP serialization is NEVER an excuse to use `grep_search` for dependency analysis.** Hierarchy: (1) `adg_sqlite` MCP → (2) direct SQLite on latest `artifacts/adg/adg_indexed_*.sqlite` → (3) emit `DEGRADED_FALLBACK:` before any grep fallback. See `graph-analysis` / `adg-sqlite` skills.

## Bypass

`MCP_SERIAL_BYPASS=1` — advisory logging path when audits are enabled; do not use to bypass `pre_mcp_gate` hard blocks.

## References

- `.claude/governance/scripts/pre_mcp_gate.py` — Notion token gate, GitKraken upstream checks, wave deferral integration.
- `.claude/rules/mcp-config-ssot.md` — MCP SSOT and sync gates.
