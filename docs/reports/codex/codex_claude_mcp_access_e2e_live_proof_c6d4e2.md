# Codex Claude MCP Access E2E Live Proof

Generated: 2026-06-11  
Plan: `codex-claude-mcp-access-parity-c6d4e2`  
Scope: post-completion live proof for the Codex/Claude MCP access parity plan.

## Result

The plan is complete and live-tested. The proof is route-accurate rather than overstated: Codex now has one raw healthy MCP route, two accepted callable substitutes, and explicit degraded/process-only outcomes for the remaining Claude-configured MCPs.

| Classification | MCPs |
|---|---|
| `CALLABLE` | `adg_sqlite` |
| `PLUGIN_SUBSTITUTE` | `notion` |
| `SUBSTITUTE_CALLABLE` | `playwright` |
| `PROCESS_ONLY` | `memory`, `vector_db`, `context7` |
| `DEGRADED_FALLBACK` | `GitKraken`, `deepwiki` |

## Live Proofs

| Surface | Live Test | Result |
|---|---|---|
| `adg_sqlite` MCP | `adg_health` | Success: `status=ok`, `sqlite=healthy`, `redis=healthy`, snapshot `06102026_1438`, 185328 nodes, 1097680 edges |
| Notion plugin route | Fetch Notion plan page `37c27693-f55c-8109-8837-f3169f38fff7` | Success: page fetched from Plans data source with Status `Completed` and Exists On Disk `__YES__` |
| Node/browser substitute | `node_repl.js` cwd/request metadata probe | Success: `ok=true`, cwd `C:\Git\Agentic-Workflow-FRESH`, request metadata present |
| Git fallback | `git rev-parse --show-toplevel` | Success: `C:/Git/Agentic-Workflow-FRESH` |
| Lexical fallback | `rg --version` | Success: `ripgrep 15.1.0` |

## Audit Evidence

The final audit was run with direct callable evidence from this session:

```text
CODEX_MCP_CALLABLE_ADG_SQLITE=healthy
CODEX_MCP_CALLABLE_NOTION=plugin_callable
CODEX_MCP_CALLABLE_PLAYWRIGHT=substitute_callable
python scripts/governance/audit_codex_mcp_transports.py --json
```

Audit exit code: `0`.

| MCP | Classification | Callable Status | Process Classification | Process Count |
|---|---|---|---|---:|
| `GitKraken` | `DEGRADED_FALLBACK` | `absent` | `none` | 0 |
| `adg_sqlite` | `CALLABLE` | `healthy` | `duplicate` | 2 |
| `deepwiki` | `DEGRADED_FALLBACK` | `absent` | `none` | 0 |
| `memory` | `PROCESS_ONLY` | `absent` | `duplicate` | 2 |
| `vector_db` | `PROCESS_ONLY` | `absent` | `duplicate` | 2 |
| `notion` | `PLUGIN_SUBSTITUTE` | `plugin_callable` | `duplicate_launch_tree` | 6 |
| `context7` | `PROCESS_ONLY` | `absent` | `duplicate_launch_tree` | 8 |
| `playwright` | `SUBSTITUTE_CALLABLE` | `substitute_callable` | `duplicate_launch_tree` | 6 |

## Verification Commands

| Command | Result |
|---|---|
| `python -m py_compile scripts/governance/audit_codex_mcp_transports.py` | Pass |
| `python tools/analysis/check_plan_format_forward.py plans/codex-claude-mcp-access-parity-c6d4e2.md` | Pass: 0 FAIL, 0 ERROR, 0 WARN, 0 INFO |
| `python scripts/governance/verify_codex_backup.py` | Pass |
| `python -m pytest tests/unit/scripts/governance/test_audit_codex_mcp_transports.py -q` | Pass: 7 passed, 3 warnings |

## Residual Notes

- Duplicate process cohorts remain visible for `adg_sqlite`, `memory`, `vector_db`, `notion`, `context7`, and `playwright`. They are process hygiene debt, not callable proof.
- `memory`, `vector_db`, and `context7` remain process-only until the Codex host exposes callable tools.
- `GitKraken` and `deepwiki` remain explicit degraded fallback routes.
- `notion` and `playwright` are accepted Codex routes for this plan, but they are not identical raw Claude MCP tool surfaces.
