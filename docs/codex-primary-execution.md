# Codex Primary Execution

Codex is the primary local execution surface for this repository. The repo-owned governance files remain the rule source of truth; Codex owns run readiness, execution evidence, and verification receipts.

## Source Of Truth Split

| Concern | Source |
| --- | --- |
| Local run state, readiness, verification, and closeout evidence | Codex primary execution surface |
| Shared governance rules | `AGENTS.md`, `docs/codex-primary-execution.md`, `.codex/**`, `scripts/governance/**`, root `.mcp.json` |
| Agentic Workflow project memory | `memory/MEMORY.md` plus Codex-specific project memory under `memory/codex/` |
| MCP configured-server truth | `.mcp.json` |
| Optional Codex live route evidence | `docs/reports/codex/` snapshots such as `codex_primary_mcp_live_snapshot.md` |
| Route evidence and Codex preflight | `scripts/governance/audit_codex_mcp_transports.py` and `scripts/governance/codex_readiness.py` |
| Run receipts | JSON receipts validated by `scripts/governance/verify_codex_run_receipt.py` |

No parallel registry: `.codex` is the only repo governance tree for Codex rules, skills, hooks, schemas, templates, and state. Do not recreate the legacy Claude governance directory, root `.agents` skill tree, memory-hosted `SKILL.md` tree, or any second hook/rule tree. Codex consumes the repo-owned files and produces fresh execution evidence.

For non-trivial Codex work in this repo, load repo-local project memory before relying on global Codex memory: read `memory/MEMORY.md`, then `memory/codex/memory_summary.md` when the task may depend on previous Agentic Workflow Codex runs, branch/worktree workflows, or repo-specific Codex skills. Keep `C:\Users\amita\.codex\memories` for cross-project/user memory only.

Repo-specific Codex enforcement must live under this repository, not under the Windows user-profile Codex home. Cadence automation contracts live in `.codex/automations/`, repo-specific bootstrap skills live in `.codex/skills/`, and generated user-profile automation entries may only be digest-bound launcher mirrors with repo path metadata. They may mirror the repo contract's UI/runtime fields (`prompt`, `model`, `reasoning_effort`, `execution_environment`, and `cwds`) so Codex Desktop can display and run scheduled automations, but they must validate exactly against the repo-owned contract and must not carry hand-edited or stale payloads, handoff metadata, runtime optimization metadata, or other independent contract authority. The guard is:

```bash
python scripts/governance/verify_codex_enforcement_home.py --json
```

## Local Codex Skills

Agentic-Workflow Codex skills are repo-owned under `.codex/skills`. Personal Codex skills under `C:\Users\amita\.codex\skills` must not carry Agentic-Workflow enforcement.

Primary verification is repo-owned:

```bash
python scripts/governance/verify_codex_primary.py
```

The primary verifier includes `verify_codex_enforcement_home.py`, so it fails when Agentic-Workflow automation or skill enforcement drifts back into the user profile. To refresh Codex Desktop launcher mirrors without creating a second SSOT, run:

```bash
python scripts/governance/codex_automation_projection.py --disable-stale-user-profile-launchers --write-user-profile --json
```

Active plan files live under repo-root `plans/`. `.codex/plans/` is archive-only; top-level plan files there are treated as SSOT drift.

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
- ADG active-session transport is open; initialize/tools-list and process liveness are not enough, and direct SQLite is not a green readiness substitute for required ADG work.
- Duplicate MCP process cohorts are visible before the run starts.

## Main Publication And Cleanup Contract

For Codex branch publication, "on main" means commit ancestry, not just equivalent file content.
A branch is done only when its tip is reachable from `origin/main`:

```bash
git merge-base --is-ancestor <branch> origin/main
git branch --no-merged origin/main
```

`git cherry -v origin/main <branch>` is diagnostic evidence only. A `-` row means patch-equivalent
content is represented, but it does not make the branch safe to delete and it does not satisfy
closeout. If a branch is superseded or manually transplanted, record that decision in main history
with an explicit non-squash ancestry merge, normally:

```bash
git merge -s ours --no-ff <branch>
```

Use that only after confirming the desired content is already on `main` or intentionally superseded.
Then rerun `git branch --no-merged origin/main` after pushing. Cleanup may delete local branches or
worktrees only after the exact branch tip is ancestor-contained in `origin/main` and the worktree is
clean.

The local closeout authority reports two surfaces:

```bash
python scripts/governance/codex_main_closeout.py --check --json
python scripts/governance/codex_main_closeout.py --apply --json
```

`publication_closeout` proves local `main` equals `origin/main`, the root index and worktree are
clean, and no branch remains unmerged from the base ref. `workspace_topology_closeout` proves only
the expected main worktree remains and no non-main local branches remain. The top-level status stays
strict and fails unless both surfaces pass. The apply mode is cleanup-only: it may fast-forward clean
local `main` and remove clean ancestor-contained non-main branches/worktrees, but it never resets,
force-pushes, deletes dirty worktrees, or deletes unmerged branches.

The shell hook enforces this for local PR completion commands. A direct `gh pr merge` or push to
`main` must chain both closeout commands in the same shell command, normally after switching back to
`main`:

```bash
gh pr merge <number> --merge && git switch main && python scripts/governance/codex_main_closeout.py --apply --fetch --json --publication-only && python scripts/governance/codex_main_closeout.py --check --fetch --json --publication-only
```

Run the strict `codex_main_closeout.py --check --fetch --json` afterward as workspace-topology
evidence. A topology failure caused only by unrelated retained worktrees is reported as hygiene debt
with RCA, not as a publication failure.

The publication audit remains the broader planning view:

```bash
python scripts/governance/codex_publication_audit.py --json
python scripts/governance/codex_publication_audit.py --json --require-ancestor-cleanup
python scripts/governance/codex_publication_audit.py --json --require-publication-closeout
```

The first form reports remaining branches as warnings for planning. The `--require-ancestor-cleanup`
form is a closeout gate and fails while any branch remains outside `origin/main`.

Every enabled server in root `.mcp.json` is part of the Codex startup MCP set for this repo. The repo-owned projection into Codex Desktop config marks those servers `required = true`, which is the host-owned spawn/reattach path: a new chat should fail startup/resume rather than silently omit a configured MCP.

Keep the user-level Codex runtime projection synchronized before relying on a new chat:

```bash
python .codex/governance/scripts/sync_mcp_config.py --sync-user-config --json
python .codex/governance/scripts/sync_mcp_config.py --check-user-config --json
```

The SessionStart hook runs `.codex/hooks/session_start_mcp_bootstrap.py`, which refreshes that projection and runs advisory health probes. It does not claim detached stdio subprocesses as host-attached MCP parity.

Shell-side scripts cannot see the live Codex MCP namespace. When a core route is proven callable by the active Codex session, pass evidence through the existing environment convention:

```text
CODEX_MCP_CALLABLE_MEMORY=healthy
CODEX_MCP_CALLABLE_GITKRAKEN=healthy
CODEX_MCP_CALLABLE_ADG_SQLITE=healthy
```

Accepted status values are inherited from `scripts/governance/audit_codex_mcp_transports.py`: `healthy`, `closed_transport`, `plugin_callable`, `substitute_callable`, and `absent`.

ADG has an additional hard per-turn and readiness gate: ordinary T2/T3 prompts require
`tools.adg.mcp.supervisor.transport_status().status == "open"`. A readable
SQLite snapshot and a live ADG process are necessary but not sufficient when the
active Codex MCP route is closed. The ADG PostToolUse proof hook writes a
short-lived proof file after `adg_health`, `adg_runtime_info`, or
`adg_process_identity` succeeds; explicit ADG transport recovery/RCA prompts may
proceed while the proof is absent so the route can be repaired.

## MCP Lifecycle Cleanup Guard

Process presence is not transport ownership. Do not kill Codex-owned MCP child processes by hand; the OS process table cannot prove which child owns the active stdio transport.

Historical route-contract files under `docs/reports/codex/` are snapshots. They do not prove current-session callability unless the active session also provides live proof through `CODEX_MCP_CALLABLE_<SERVER_ID>=healthy`, or an operator deliberately sets `CODEX_MCP_TRUST_ROUTE_CONTRACT=1` for the same verification context.

Use the read-only audit first:

```bash
python scripts/governance/audit_codex_mcp_transports.py --json
```

When a specific server reports `Transport closed` or process-only callability,
use the read-only diagnosis wrapper before any cleanup decision:

```bash
python scripts/governance/diagnose_codex_mcp_transport.py --server adg_sqlite --json
```

The diagnosis command does not launch servers, kill processes, or call Codex MCP
tools. It distinguishes host/TUI reconnect requirements from process-only
evidence, stale callability proof, duplicate cohorts, and explicitly degraded
fallbacks.

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

## Native Hook Contract

Codex primary enforcement uses the native Codex hook registry at `.codex/hooks.json`. Hook entrypoints live under `.codex/hooks/**`, and delegated governance scripts live under `.codex/governance/scripts/**`. The legacy Claude governance directory is forbidden.

Workspace-specific avatar enforcement lives in `.codex/hooks/selected_avatar_guard.py` and is registered on `SessionStart`, `UserPromptSubmit`, and `PreToolUse` so the workspace blocks before startup, prompt submission, or tool execution when the active Codex avatar is not `patch-fox`.

## High-Signal Lessons

The repo only hard-enforces the lessons that repeatedly prevented failures. Keep the surface narrow:

- Deterministic workflow first, single bounded agent second, multi-agent only after contracts, gates, replay, and state authority.
- A file, plan, receipt, dashboard, or manifest is not progress until the live product trace consumes it and leaves replayable evidence.
- One product path beats many control planes. Static evidence does not certify runtime behavior.
- L6 learns only after the run boundary; postmortems are future-run constraints, not current-run rescue.
- When a product artifact appears, freeze route expansion and ship before widening certification.

The avatar pin is identity-only. The narrow enforcement surfaces for these lessons are the existing plan-mint gate and north-star edit gate. They are reminders and scope guards, not a license to add broad new blocks.

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
| `adg_sqlite` | Required structural route for dependency/refactor work. If closed, stop for ADG transport recovery/RCA; direct SQLite is a named degraded diagnostic or CI-parity path, not a green readiness substitute. |
| `notion` | Codex plugin substitute is acceptable for manual Plans/Backlog access when schema is fetched first. |
| `playwright` | Browser/node substitutes are acceptable for UI verification unless raw browser MCP parity is explicitly required. |
| `deepwiki` and `context7` | Use official docs, GitHub, Tavily, or web only as named degraded substitutes until raw tools are exposed. |

Codex must ask a plain-text clarifying question directly in the assistant response before editing whenever a turn cannot proceed safely without a user choice; do not assume a branch or defer to a missing prompt surface.

## Verification

Run the primary verifier after changing Codex execution docs or scripts:

```bash
python scripts/governance/verify_codex_primary.py
```

The primary verifier also enforces the Codex-only migration: no legacy Claude governance directory, no tracked legacy Claude instruction or project-dir references, and no missing `.codex/hooks.json` command targets.
