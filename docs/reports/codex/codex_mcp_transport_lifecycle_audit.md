# Codex MCP Transport Lifecycle Audit

Generated: 2026-06-10  
Plan: `codex-mcp-transport-parity-4b9c7e` W4  
Scope: transport health probes, duplicate-process hygiene, and env placeholder preflight.

## W4 Result

W4 is complete with one live finding:

- `adg_sqlite` has **two** Python stdio server processes and should be treated as
  duplicate until the stale process is removed through the owning MCP host
  restart/cleanup path.
- `notion`, `context7`, and `playwright` each show multiple OS processes, but
  the audit classifies them as a single expected `cmd -> npx -> node` launch
  tree rather than duplicate server launches.
- `memory` and `vector_db` each show a single Python stdio server process.
- Dormant `redis`, `pytest_mcp`, `otel_mcp`, and `tavily` have no live
  standalone MCP processes, matching W3 policy.

The repeatable audit helper is:

```bash
python scripts/governance/audit_codex_mcp_transports.py --json
```

The helper is read-only: it does not launch, restart, or kill MCP servers.

## Evidence Snapshot

| Check | Result |
|---|---|
| `adg_health` | `mode=full`, `sqlite=healthy`, `redis=healthy`, `cache_hit_capable=true`, snapshot `06082026_1212` |
| `adg_runtime_info` | PID `12236`, startup nonce `17aa233dcc0d`, startup time `2026-06-10T09:16:54.190413` |
| ADG restart proof status | Baseline captured. A later restart is proven only if PID or startup nonce changes. |
| Redis TCP dependency | `localhost:6379` open |
| Command availability | `python`, `cmd`, `npx`, `node`, `git`, and `redis-cli` found |
| Script compile | ADG, Memory, Vector, Redis, pytest_mcp, OTel, and Redis ingest scripts compile |
| Credential presence | `ADG_REDIS_URL`, `AGENTIC_REPO_ROOT`, `GITKRAKEN_GK_PATH`, `MEMORY_DB`, `NOTION_TOKEN`, and `TAVILY_API_KEY` set |
| Optional/dormant env gaps | `CONTEXT7_API_KEY`, `OTEL_MCP_RUNTIME_ADG_DIR`, `PYTEST_DISABLE_PLUGIN_AUTOLOAD`, and `VECTOR_DB_CHROMA_PATH` unset |
| Tavily env file | `C:\Users\amita\env\.env` line 79 contains `TAVILY_API_KEY`, length 41 |
| Registry placeholders | `.mcp.json` contains expected source placeholders such as `${AGENTIC_REPO_ROOT}` and `${ADG_REDIS_URL}` |
| Runtime placeholder leakage | Current environment values checked by the audit have no unresolved `${...}` placeholders |
| Focused tests | `14 passed`, 5 existing warnings |

## Process Classification

| Server | Expected Shape | Count | Root Launchers | Classification | Notes |
|---|---|---:|---:|---|---|
| `adg_sqlite` | single Python stdio server | 2 | 2 | `duplicate` | PIDs `11052` and `12236`; live MCP tool runtime reports PID `12236`. |
| `memory` | single Python stdio server | 1 | 1 | `single` | PID `38996`. |
| `vector_db` | single Python stdio server | 1 | 1 | `single` | PID `38544`. |
| `notion` | single npx launch tree | 3 | 1 | `single_launch_tree` | Wrapper/child tree, not a duplicate launch. |
| `context7` | single npx launch tree | 4 | 1 | `single_launch_tree` | Wrapper/child tree, not a duplicate launch. |
| `playwright` | single npx launch tree | 3 | 1 | `single_launch_tree` | Wrapper/child tree, not a duplicate launch. |
| `redis` | dormant | 0 | 0 | `none` | Matches W3 policy. |
| `pytest_mcp` | dormant | 0 | 0 | `none` | Matches W3 policy. |
| `otel_mcp` | dormant/on-demand | 0 | 0 | `none` | Matches W3 policy. |
| `tavily` | dormant | 0 | 0 | `none` | Matches W3 policy. |

## Placeholder Policy

`.mcp.json` is allowed to store placeholders because it is the Claude Code SSOT
registry. Codex-started or locally tested paths must not receive unresolved
placeholder strings at runtime. The audit checks both sides:

- Source registry placeholders are inventoried and treated as expected source
  form.
- Current runtime env values are checked for literal `${...}` leakage.
- Focused tests cover sentinel/path rejection and Redis env override behavior.

Current gap: `AGENTIC_REPO_ROOT` resolves to the eval worktree, but the live ADG
MCP process still serves the primary checkout. This preserves the W2.3
`ADG-LIVE-CODE-MISMATCH` blocker.

## Non-Destructive Cleanup Guidance

For duplicate MCP processes, do not kill individual PIDs blindly. Use the owning
Codex/Claude MCP host restart path first, then re-run:

```bash
python scripts/governance/audit_codex_mcp_transports.py --json
```

For `adg_sqlite`, the successful cleanup condition is:

- exactly one `tools.adg.mcp.server` Python process remains, and
- `adg_runtime_info` reports a PID that matches the remaining process, and
- after an intentional restart, PID or startup nonce changed from the previous
  captured baseline.

If raw cleanup is unavoidable, classify it as operator remediation and terminate
only the stale process that is not reported by `adg_runtime_info`.

## Verification

```bash
python -m py_compile scripts/governance/audit_codex_mcp_transports.py
python scripts/governance/audit_codex_mcp_transports.py --json
python -m pytest -p pytest_timeout tests/unit/adg/test_path_resolver_sentinel_rejection.py tests/unit/tools/adg/test_adg_mcp_fixes.py::TestRedisUrlEnvOverride -q
```

The focused pytest slice passed: `14 passed, 5 warnings`.
