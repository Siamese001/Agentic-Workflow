# Codex Backup Adapter

Codex is configured as a backup agent for this repository. Claude/Cursor governance remains the source of truth; Codex should act as an adapter that reads and follows it.

## Source of truth

Use these repo files as authoritative:

| Concern | SSOT |
| --- | --- |
| Agent operating rules | `AGENTS.md` |
| Always-on and on-demand rules | `.cursor/rules/*.mdc` |
| Structured reasoning | `.cursor/skills/structured-reasoning/SKILL.md` |
| MCP routing | `.cursor/mcp.json` and `.cursor/skills/mcp-integration/SKILL.md` |
| Hook behavior | `.cursor/hooks.json` and `.cursor/hooks/*.py` |
| Plan lifecycle | `.cursor/skills/plan-governance/SKILL.md` and `.cursor/plans/*.md` |

## Codex-specific layer

Keep the Codex layer intentionally small:

| File | Purpose |
| --- | --- |
| `C:\Users\amita\.codex\skills\agentic-workflow-governance\SKILL.md` | Teaches Codex how to consume the repo governance SSOT. |
| `C:\Users\amita\.codex\skills\agentic-workflow-verification\SKILL.md` | Teaches Codex how to verify backup-agent work without duplicating hooks. |
| `scripts/governance/verify_codex_backup.py` | Checks that the adapter points to live SSOT files and the personal Codex skills exist. |

## Operating rules for Codex

1. For T0/T1 tasks, answer or edit directly while honoring `AGENTS.md`.
2. For T2/T3 tasks, first output a structured plan using the repo's `SR_INTAKE` through `SR_VERIFY` phases.
3. Do not edit during the planning phase.
4. Prefer repo scripts and `.cursor` guidance over ad hoc shell logic.
5. Do not duplicate Claude/Cursor hooks in Codex. Use `scripts/governance/verify_codex_backup.py` as the Codex-facing adapter check.

## Test

Run:

```bash
python scripts/governance/verify_codex_backup.py
```

The script fails if a required SSOT file or Codex skill is missing, or if adapter files stop referencing the expected governance anchors.
