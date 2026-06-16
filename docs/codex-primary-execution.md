# Codex Primary Execution

Codex is the primary local execution surface for this repository when Claude API rate limits or host instability make Claude-first runs unreliable. The repo-owned governance files remain the rule source of truth; Codex owns run readiness, execution evidence, and verification receipts.

## Source Of Truth Split

| Concern | Source |
| --- | --- |
| Local run state, readiness, verification, and closeout evidence | Codex primary execution surface |
| Shared governance rules during migration | `CLAUDE.md`, `AGENTS.md`, `.claude/rules/**`, `.claude/skills/**`, `.claude/settings.json` |
| MCP configured-server truth | `.mcp.json` plus `.claude/mcp-notes.md` |
| Optional Codex live route evidence | `docs/reports/codex/` snapshots such as `codex_primary_mcp_live_snapshot.md` |
| Hook parity and Codex hook preflight | `scripts/governance/codex_hook_parity.py` consuming `.claude/settings.json` |
| Run receipts | JSON receipts validated by `scripts/governance/verify_codex_run_receipt.py` |

No parallel registry: do not copy `.claude` rule bodies, MCP server definitions, or hook logic into a Codex-only store. Codex should consume the repo-owned files and produce fresh execution evidence.

## Local Codex Skills

Personal Codex skills under `C:\Users\amita\.codex\skills` are optional bootstrap shims. They help a new Codex session route into this repo contract quickly, but they are not required for normal verification and must not become a second source of truth.

Primary verification is repo-owned:

```bash
python scripts/governance/verify_codex_primary.py
```

Legacy compatibility verification treats personal skills as advisory by default. Run it only when changing backup-adapter docs or workstation bootstrap skills; use strict mode only when auditing the workstation bootstrap layer itself:

```bash
python scripts/governance/verify_codex_backup.py
python scripts/governance/verify_codex_backup.py --require-personal-skills
```

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
- The Claude hook matrix is registered and present for Codex preflight through `scripts/governance/codex_hook_parity.py`.
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

## Hook Parity Contract

Claude Code automatically runs hooks from `.claude/settings.json`; Codex does not. Codex-primary work must therefore treat `scripts/governance/codex_hook_parity.py` as the executable bridge to the Claude hook SSOT, not as a copied hook registry.

Use the matrix/probe check before governed Codex runs:

```bash
python scripts/governance/codex_hook_parity.py --json check
```

Use explicit preflight when a Codex step is about to perform a governed tool action:

```bash
python scripts/governance/codex_hook_parity.py run-pre-tool Edit --file-path scripts/governance/codex_hook_parity.py
python scripts/governance/codex_hook_parity.py run-stop artifacts/codex/candidate-final-response.txt
```

The parity runner validates whatever hook registrations are active in `.claude/settings.json` and confirms their registered target files exist. It does not maintain a copied required-hook registry, so intentionally removed hooks do not require Codex-side rebaselining. Bounded probes are executable smoke tests for important guard behavior, not a second hook inventory. Hook behavior remains authored only under `.claude/settings.json` and `.claude/hooks/**`.

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
| `GitKraken` | Preferred git/PR authority when callable; native `git` is a degraded fallback and must follow normal Codex git safety rules. |
| `vector_db` | Preferred semantic retrieval route when callable; `rg` is lexical fallback, not semantic parity. |
| `adg_sqlite` | Preferred structural route. If not callable, direct SQLite against the newest `artifacts/adg/adg_indexed_*.sqlite` is an explicit degraded fallback. |
| `notion` | Codex plugin substitute is acceptable for manual Plans/Backlog access when schema is fetched first. |
| `playwright` | Browser/node substitutes are acceptable for UI verification unless raw Claude Playwright MCP parity is explicitly required. |
| `deepwiki` and `context7` | Use official docs, GitHub, Tavily, or web only as named degraded substitutes until raw tools are exposed. |

## Verification

Run the primary verifier after changing Codex execution docs or scripts:

```bash
python scripts/governance/verify_codex_primary.py
```

The compatibility verifier is legacy/advisory for the backup-adapter name. Run it only when changing backup-adapter docs or personal bootstrap skills. It does not require personal Codex skills unless `--require-personal-skills` is supplied.

```bash
python scripts/governance/verify_codex_backup.py
```

The backup verifier name is compatibility terminology. The active Codex operating contract is this file plus `AGENTS.md`.
