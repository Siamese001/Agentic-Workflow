# Codex Primary Execution

Codex is the primary local execution surface for this repository. The repo-owned governance files remain the rule source of truth; Codex owns run readiness, execution evidence, and verification receipts.

## Source Of Truth Split

| Concern | Source |
| --- | --- |
| Local run state, readiness, verification, and closeout evidence | Codex primary execution surface |
| Shared governance rules during migration | `AGENTS.md`, `docs/codex-primary-execution.md`, `scripts/governance/**`, root `.mcp.json` |
| Agentic Workflow project memory | `memory/MEMORY.md` plus Codex-specific project memory under `memory/codex/` |
| MCP configured-server truth | `.mcp.json` |
| Optional Codex live route evidence | `docs/reports/codex/` snapshots such as `codex_primary_mcp_live_snapshot.md` |
| Route evidence and Codex preflight | `scripts/governance/audit_codex_mcp_transports.py` and `scripts/governance/codex_readiness.py` |
| Run receipts | JSON receipts validated by `scripts/governance/verify_codex_run_receipt.py` |

No parallel registry: do not copy rule bodies, MCP server definitions, or hook logic into a Codex-only store. Codex should consume the repo-owned files and produce fresh execution evidence.

For non-trivial Codex work in this repo, load repo-local project memory before relying on global Codex memory: read `memory/MEMORY.md`, then `memory/codex/memory_summary.md` when the task may depend on previous Agentic Workflow Codex runs, branch/worktree workflows, or repo-specific Codex skills. Keep `C:\Users\amita\.codex\memories` for cross-project/user memory only.

## Required Preflight

Before long Codex-primary runs, run:

```bash
python scripts/governance/codex_readiness.py --json
```

For strict preflight before expensive proof/eval work, use:

```bash
python scripts/governance/codex_readiness.py --require-clean-worktree --fail-duplicate-processes --json
```

The readiness gate checks:

- Codex primary contract files are present.
- Git state is known, with optional clean-worktree enforcement.
- `AGENTIC_REPO_ROOT`, `ADG_REDIS_URL`, and pytest plugin-autoload state are sane.
- Required Codex routes have callable evidence when marked required.
- ADG is callable or a named direct SQLite fallback exists.
- Duplicate MCP process cohorts are visible before the run starts.

Shell-side scripts cannot see the live Codex MCP namespace. When a route is proven callable by the active Codex session, pass evidence through the existing environment convention:

```text
CODEX_MCP_CALLABLE_MEMORY=healthy
CODEX_MCP_CALLABLE_GITKRAKEN=healthy
CODEX_MCP_CALLABLE_VECTOR_DB=healthy
CODEX_MCP_CALLABLE_ADG_SQLITE=closed_transport
```

Accepted status values are inherited from `scripts/governance/audit_codex_mcp_transports.py`: `healthy`, `closed_transport`, `plugin_callable`, `substitute_callable`, and `absent`.

## MCP Lifecycle Cleanup Guard

Process presence is not transport ownership. Do not kill Codex-owned MCP child processes by hand; the OS process table cannot prove which child owns the active stdio transport.

Use the read-only audit first:

```bash
python scripts/governance/audit_codex_mcp_transports.py --json
```

Then inspect the guarded cleanup plan:

```bash
python scripts/governance/cleanup_duplicate_mcp_cohorts.py --json
```

The cleanup helper can apply legacy duplicate cohort cleanup because those cohorts are grouped by parent process:

```bash
python scripts/governance/cleanup_duplicate_mcp_cohorts.py --apply --json
```

If Codex-owned duplicates are also present, `--apply` returns exit code 2 and refuses to terminate anything unless attached PID proof is supplied. To clean only legacy cohorts while leaving Codex-owned duplicates blocked, add `--ignore-codex-duplicates`.

Codex-owned duplicate cohorts are blocked from cleanup unless the active host-attached PID is supplied for each duplicate server:

```bash
python scripts/governance/cleanup_duplicate_mcp_cohorts.py --apply --codex-attached-pid memory=<pid> --codex-attached-pid adg_sqlite=<pid> --codex-attached-pid vector_db=<pid> --json
```

Attached PID proof must come from the active Codex tool transport, not from newest/oldest process heuristics. For repo-owned Python MCP servers, call the cheap process-identity tool first:

| Server | Tool | PID proof field |
| --- | --- | --- |
| `memory` | `mcp__memory.mem_process_identity` | `process.cleanup_arg` |
| `adg_sqlite` | `mcp__adg_sqlite.adg_process_identity` or `mcp__adg_sqlite.adg_runtime_info` | `process.cleanup_arg` or `data.process.cleanup_arg` |
| `vector_db` | `mcp__vector_db.vector_process_identity` | `process.cleanup_arg` |

Then pass each returned `cleanup_arg` value to the cleanup helper. Example:

```bash
python scripts/governance/cleanup_duplicate_mcp_cohorts.py --apply --codex-attached-pid memory=1234 --codex-attached-pid adg_sqlite=2345 --codex-attached-pid vector_db=3456 --json
```

If a process-identity tool is absent, the live MCP child is still serving older code. Restart or reload the Codex MCP host and rerun strict readiness instead of killing child processes.

## Run Receipt Contract

Every substantial Codex-primary implementation or verification run should produce a JSON receipt and validate it:

```bash
python scripts/governance/verify_codex_run_receipt.py artifacts/codex/run_receipts/<run-id>.json
```

The receipt schema is `codex-run-receipt/v1`. It must record:

- `run_id` and `generated_at`.
- `repo.root`, `repo.worktree`, `repo.branch`, `repo.head`, `repo.dirty_before`, and `repo.dirty_after`.
- `scope.request`, `scope.plan_id`, and `scope.files_changed`.
- `execution.status`, `execution.commands`, and any `execution.fallbacks`.
- `verification.checks`.
- `rca` when execution fails, blocks, or any command/check fails.

Failure RCA fields are mandatory: `symptom`, `root_cause`, `evidence`, `fix_or_next`, and `recurrence_guard`. `fix_or_next` must begin with `fix:` when the turn fixed the failure or `next:` when a follow-up remains.

## MCP Route Policy

Use live Codex callable routes when exposed. When a route is unavailable, report the degraded substitute by name.

| Route | Codex-primary policy |
| --- | --- |
| `memory` | Required for session recall/writeback when available; no honest substitute for claiming Memory MCP compliance. |
| `GitKraken` | Required git/PR authority when callable; the GitKraken CLI (`gk`) is the substitute proof path when the live MCP surface is unavailable. Raw `git`/`gh` are not primary routes for governed git/PR actions. |
| `vector_db` | Preferred semantic retrieval route when callable; `rg` is lexical fallback, not semantic parity. |
| `adg_sqlite` | Preferred structural route. If not callable, direct SQLite against the newest `artifacts/adg/adg_indexed_*.sqlite` is an explicit degraded fallback. |
| `notion` | Codex plugin substitute is acceptable for manual Plans/Backlog access when schema is fetched first. |
| `playwright` | Browser/node substitutes are acceptable for UI verification unless raw browser MCP parity is explicitly required. |
| `deepwiki` and `context7` | Use official docs, GitHub, Tavily, or web only as named degraded substitutes until raw tools are exposed. |

Codex must ask a plain-text clarifying question directly in the assistant response before editing whenever a turn cannot proceed safely without a user choice; do not assume a branch or defer to a missing prompt surface.

## Verification

Run the primary verifier after changing Codex execution docs or scripts:

```bash
python scripts/governance/verify_codex_primary.py
```
