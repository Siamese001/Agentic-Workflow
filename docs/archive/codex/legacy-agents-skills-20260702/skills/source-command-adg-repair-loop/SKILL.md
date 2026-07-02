---
name: "source-command-adg-repair-loop"
description: "Thin alias \u2014 ADG-scoped repair loop (/adg-repair-loop)"
---

# source-command-adg-repair-loop

Use this skill when the user asks to run the migrated source command `adg-repair-loop`.

## Command Template

# /adg-repair-loop

**Tier:** Workflow alias only.

## Authority map

| Layer | SSOT |
|-------|------|
| Invariants | [adg-canonical-invariants.md](../rules/adg-canonical-invariants.md) |
| Repair protocol (full steps) | [adg-analysis-procedures.md](../rules/adg-analysis-procedures.md) §5 |
| P-band discipline | [adg-p-band-burn-down-discipline.md](../rules/adg-p-band-burn-down-discipline.md) |
| Tool routing | [graph-analysis/SKILL.md](../skills/graph-analysis/SKILL.md), [adg-sqlite/SKILL.md](../skills/adg-sqlite/SKILL.md) |
| P7 accelerator | [adg-analysis-procedures.md](../rules/adg-analysis-procedures.md) |

## Invocation steps

1. `adg_health` → confirm ADG MCP; refresh cache if stale (`/adg-redis-refresh` when needed).
2. Select cluster / scoped tests via ADG (never manual path expansion) — see §5 in `adg-analysis-procedures.md`.
3. Patch smallest seam; prove with scoped pytest; emit `ADG_REPAIR_LITMUS` when required.
4. Author-Gate if repair class is ambiguous.

⛔ No full-suite runs until convergence. No duplicate repair steps in this file.

## MANUAL MIGRATION REQUIRED

Migrated from source command `adg-repair-loop` into a Codex skill. Invoke it as `$source-command-adg-repair-loop` and manually rewrite any slash-command behavior that depended on provider-specific runtime expansion.
