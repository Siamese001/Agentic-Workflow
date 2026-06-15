# Codex Backup Adapter

Codex is configured as a backup agent for this repository. Claude Code governance remains the source of truth; Codex should act as an adapter that reads and follows it.

## Source of truth

Use these repo files as authoritative:

| Concern | SSOT |
| --- | --- |
| Agent operating rules | `CLAUDE.md` and the Codex-facing `AGENTS.md` adapter |
| Always-on and on-demand rules | `.claude/rules/*.md` / `.claude/rules/*.mdc` |
| Structured reasoning | `.claude/skills/structured-reasoning/SKILL.md` |
| MCP live routing | `.mcp.json` and `.claude/skills/mcp-integration/SKILL.md` |
| MCP dormant/re-add routing | `.claude/mcp-notes.md` and `.claude/skills/mcp-integration/sections/*.md` |
| Hook behavior | `.claude/settings.json` and `.claude/hooks/*.py` |
| Plan lifecycle | `.claude/skills/plan-governance/SKILL.md` and the active repo plan SSOT folder |
| Windows artifact path budget | `.claude/rules/windows-path-budget.md` and `scripts/governance/check_windows_path_budget.py` |

## Codex-specific layer

Keep the Codex layer intentionally small:

| File | Purpose |
| --- | --- |
| `C:\Users\amita\.codex\skills\agentic-workflow-governance\SKILL.md` | Teaches Codex how to consume the repo governance SSOT. |
| `C:\Users\amita\.codex\skills\agentic-workflow-verification\SKILL.md` | Teaches Codex how to verify backup-agent work without duplicating hooks. |
| `scripts/governance/verify_codex_backup.py` | Checks that the adapter points to live SSOT files and the personal Codex skills exist. |
| `scripts/governance/audit_codex_mcp_transports.py` | Read-only Codex transport audit for command/script readiness, placeholder leakage, and duplicate MCP process classification. |
| `scripts/governance/check_windows_path_budget.py` | Codex-callable preflight for nested Windows artifact output roots. |

## MCP parity notes

Codex MCP parity evidence belongs in reports, not in a second registry. Use:

| Artifact | Purpose |
| --- | --- |
| `docs/reports/codex/codex_mcp_capability_matrix.md` | Codex callable surface inventory against Claude live and dormant MCP SSOT. |
| `docs/reports/codex/codex_mcp_live_route_contract.md` | Live `.mcp.json` route contracts, substitutes, and blocked routes. |
| `docs/reports/codex/codex_mcp_dormant_policy.md` | Dormant Redis/Tavily/pytest/OTel substitute and re-add policy. |
| `docs/reports/codex/codex_mcp_transport_lifecycle_audit.md` | Transport health, duplicate-process, and placeholder preflight evidence. |
| `docs/reports/codex/codex_claude_mcp_access_inventory_c6d4e2.md` | Current Codex-vs-Claude configured/process/callable inventory for plan `codex-claude-mcp-access-parity-c6d4e2`. |
| `docs/reports/codex/codex_claude_mcp_access_contract_c6d4e2.md` | Route contract, no-parallel-registry invariants, and fallback wording for Codex MCP access. |
| `docs/reports/codex/codex_claude_mcp_access_w4_proof_c6d4e2.md` | Final callable proof matrix and operating procedure for the Codex MCP access plan. |

These files are evidence snapshots. For live routing decisions, read `.mcp.json`,
`.claude/mcp-notes.md`, and `.claude/skills/mcp-integration/SKILL.md` first.

## Operating rules for Codex

1. For T0/T1 tasks, answer or edit directly while honoring `CLAUDE.md` and the Codex-facing `AGENTS.md` adapter.
2. For T2/T3 tasks, enter the repo's native plan-mode workflow: present a structured plan for approval before edits, using `structured-reasoning` only as decomposition / retrieval guidance.
3. Do not edit during the planning phase.
4. Prefer repo scripts and `.claude` guidance over ad hoc shell logic.
5. Before artifact-heavy Windows `apps_eval`, `apps_rg`, or proof runs, follow `.claude/rules/windows-path-budget.md` and preflight the output root with `scripts/governance/check_windows_path_budget.py`.
6. Do not duplicate Claude Code hooks in Codex. Use `scripts/governance/verify_codex_backup.py` as the Codex-facing adapter check.
7. Do not create a Codex-specific MCP registry. If a Claude MCP is unavailable in Codex, name the missing route and use the documented substitute or degraded fallback.
8. On any runtime failure (`STATUS: FAIL` or a runtime-failure signal — `X3_BLOCK`, traceback, non-zero exit, pytest `N failed`, `BLOCKED_*`/`MISSING_GRAPH_PATH`), include an `RCA:` block in the run summary (symptom · root_cause · evidence · fix_or_next · recurrence_guard) per `.claude/rules/001-runtime-seam-execution.md` and constitutional §37. Never report a green status over a body failure-signal.

## Test

Run:

```bash
python scripts/governance/verify_codex_backup.py
```

The script fails if a required SSOT file or Codex skill is missing, or if adapter files stop referencing the expected governance anchors.

For Windows artifact path-budget preflight, run:

```bash
python scripts/governance/check_windows_path_budget.py --out-dir artifacts/ae_rg_live --suite apps_rg.dev.resume_generation
```

Shorten `--out-dir` until the check passes before starting long live-adapter evaluations.

For MCP transport hygiene, run:

```bash
python scripts/governance/audit_codex_mcp_transports.py --json
```

This audit is read-only and should not be used as a launcher or cleanup tool.

For Codex/Claude MCP access parity work, interpret the audit's `route_evidence`
section instead of process presence alone. A visible MCP process is not a
callable Codex tool. When a proof call has been run in the current Codex
session, pass that evidence to the audit using environment variables such as:

```text
CODEX_MCP_CALLABLE_ADG_SQLITE=closed_transport
CODEX_MCP_CALLABLE_NOTION=plugin_callable
CODEX_MCP_CALLABLE_PLAYWRIGHT=substitute_callable
```

Accepted values are `healthy`, `closed_transport`, `plugin_callable`,
`substitute_callable`, and `absent`. Treat `PLUGIN_SUBSTITUTE` and
`SUBSTITUTE_CALLABLE` as useful Codex routes, not raw Claude MCP parity.
Treat `PROCESS_ONLY` as blocked for MCP calls even when the local OS process is
healthy.
