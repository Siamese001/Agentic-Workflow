# Codex MCP Transport Remaining Gaps (c9e187)

Generated at: 2026-07-05T11:14:20Z
Worktree: `C:\Git\Agentic-Workflow-FRESH-worktrees\codex-mcp-transport-remaining-gaps-latest-main`
Branch: `codex-mcp-transport-remaining-gaps-latest-main`
Baseline: `origin/main` at `c9e187f99eeac7218ab42f48e2582dfd1e57b3d0`

## W0 Command Evidence

| Evidence | Exit | Result |
| --- | ---: | --- |
| `python scripts/governance/audit_codex_mcp_transports.py --json` | 0 | Read-only audit completed. It found route evidence but no active callability proof for required raw routes. |
| `python scripts/governance/diagnose_codex_mcp_transport.py --server adg_sqlite --json` | 0 | `adg_sqlite` classified as `server_healthy_codex_transport_closed`; direct SQLite/process liveness stayed diagnostic only. |
| `python scripts/governance/codex_readiness.py --json --skip-searxng` | 1 | Readiness failed on required MCP protocol/callability gates, including closed ADG transport. |
| Live Codex MCP calls | n/a | `mcp__adg_sqlite.adg_health`, `mcp__memory.memory_health`, and `mcp__vector_db.vector_process_identity` returned `Transport closed`; `mcp__GitKraken.git_status` succeeded for this worktree. |

No green ADG readiness is claimed in this report.

## Required Route Matrix

Current aggregate command:

```bash
python scripts/governance/diagnose_codex_mcp_transport.py --all-required --summary --json
```

| Required route | Classification | Callable proof state | Process state | Cleanup safety | Degraded fallback | Exact next action |
| --- | --- | --- | --- | --- | --- | --- |
| `memory` | `host_mcp_required` | `absent` | `none`, count `0` | `false` | `false` | Sync/start host MCP management or a new Codex session, then prove a live Memory MCP tool call before marking green. |
| `GitKraken` | `duplicate_cohort` | `absent` | `duplicate`, count `16` | `requires_attached_pid` | `false` | Do not kill processes. Get host-attached PID proof before guarded cleanup; the live `git_status` success still needs shell-visible callability proof for readiness. |
| `adg_sqlite` | `server_healthy_codex_transport_closed` | `absent` | `single`, count `1` | `false` | `false` | Use Codex host/TUI MCP reconnect, then prove a live `mcp__adg_sqlite.adg_health` call before setting any callability override. |
| `vector_db` | `degraded_fallback_available` | `absent` | `none`, count `0` | `false` | `true` | Use only the stamped degraded fallback; do not count it as green readiness until active Vector DB MCP callability is proven. |

## Notes

- Current aggregate counts: required routes `4`, callable `0`, blocked `4`, process-only `0`, duplicate-cohort `1`, stale-proof `0`.
- The direct GitKraken MCP call succeeded, but shell-side readiness still lacks accepted `CODEX_MCP_CALLABLE_GITKRAKEN`/epoch proof; process duplication remains a separate cleanup concern.
- This report is evidence-only. It did not launch servers, kill processes, invoke cleanup, or treat direct SQLite access as callability.
