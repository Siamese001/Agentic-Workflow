# Codex Backup Adapter

Codex is configured as a backup agent for this repository. Claude Code governance remains the source of truth; Codex should act as an adapter that reads and follows it.

## Source of truth

Use these repo files as authoritative:

| Concern | SSOT |
| --- | --- |
| Agent operating rules | `AGENTS.md` |
| Always-on and on-demand rules | `.claude/rules/*.mdc` |
| Structured reasoning | `.claude/skills/structured-reasoning/SKILL.md` |
| MCP live routing | `.mcp.json` and `.claude/skills/mcp-integration/SKILL.md` |
| MCP dormant/re-add routing | `.claude/mcp-notes.md` and `.claude/skills/mcp-integration/sections/*.md` |
| Hook behavior | `.claude/settings.json` and `.claude/hooks/*.py` |
| Plan lifecycle | `.claude/skills/plan-governance/SKILL.md` and the active repo plan SSOT folder |

## Codex-specific layer

Keep the Codex layer intentionally small:

| File | Purpose |
| --- | --- |
| `C:\Users\amita\.codex\skills\agentic-workflow-governance\SKILL.md` | Teaches Codex how to consume the repo governance SSOT. |
| `C:\Users\amita\.codex\skills\agentic-workflow-verification\SKILL.md` | Teaches Codex how to verify backup-agent work without duplicating hooks. |
| `scripts/governance/verify_codex_backup.py` | Checks that the adapter points to live SSOT files and the personal Codex skills exist. |
| `scripts/governance/audit_codex_mcp_transports.py` | Read-only Codex transport audit for command/script readiness, placeholder leakage, and duplicate MCP process classification. |

## MCP parity notes

Codex MCP parity evidence belongs in reports, not in a second registry. Use:

| Artifact | Purpose |
| --- | --- |
| `docs/reports/codex/codex_mcp_capability_matrix.md` | Codex callable surface inventory against Claude live and dormant MCP SSOT. |
| `docs/reports/codex/codex_mcp_live_route_contract.md` | Live `.mcp.json` route contracts, substitutes, and blocked routes. |
| `docs/reports/codex/codex_mcp_dormant_policy.md` | Dormant Redis/Tavily/pytest/OTel substitute and re-add policy. |
| `docs/reports/codex/codex_mcp_transport_lifecycle_audit.md` | Transport health, duplicate-process, and placeholder preflight evidence. |

These files are evidence snapshots. For live routing decisions, read `.mcp.json`,
`.claude/mcp-notes.md`, and `.claude/skills/mcp-integration/SKILL.md` first.

## Operating rules for Codex

1. For T0/T1 tasks, answer or edit directly while honoring `AGENTS.md`.
2. For T2/T3 tasks, first output a structured plan using the repo's `SR_INTAKE` through `SR_VERIFY` phases.
3. Do not edit during the planning phase.
4. Prefer repo scripts and `.claude` guidance over ad hoc shell logic.
5. Do not duplicate Claude Code hooks in Codex. Use `scripts/governance/verify_codex_backup.py` as the Codex-facing adapter check.
6. Do not create a Codex-specific MCP registry. If a Claude MCP is unavailable in Codex, name the missing route and use the documented substitute or degraded fallback.

## Test

Run:

```bash
python scripts/governance/verify_codex_backup.py
```

The script fails if a required SSOT file or Codex skill is missing, or if adapter files stop referencing the expected governance anchors.

For MCP transport hygiene, run:

```bash
python scripts/governance/audit_codex_mcp_transports.py --json
```

This audit is read-only and should not be used as a launcher or cleanup tool.
