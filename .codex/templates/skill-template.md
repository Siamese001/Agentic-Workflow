---
name: <skill-slug>
description: Use this skill when <user intent, task context, and the boundary from adjacent skills>.
# compatibility: "Include only when the workflow has specific product, package, OS, or network requirements."
metadata:
  owner: <team-or-owner>
  version: "1.0"
---

# <Skill title>

State the specialized outcome this skill enables. Keep always-on policy in `AGENTS.md`,
`.codex/rules/`, hooks, or CI; this file should contain only task-specific procedure.

## Workflow

1. Confirm the request matches the description and not an adjacent skill.
2. Read only the supporting reference needed for the current branch of work.
3. Execute the smallest reliable procedure.
4. Validate the result with the exact command or assertion below.
5. Report the result, residual uncertainty, and rollback path when applicable.

## Decision rules

- Use `<approach-a>` when `<condition>`.
- Use `<approach-b>` when `<condition>`.
- Stop or ask one focused question when `<decision cannot be resolved safely>`.

## Validation

```bash
<deterministic validation command>
```

## Resources

- Read [references/<topic>.md](references/<topic>.md) only when `<condition>`.
- Run `scripts/<script>.py --help` before first use when the workflow needs deterministic automation.
- Use files under `assets/` as output inputs; do not load them into context unless necessary.

Delete unused sections and placeholder files. Keep references one level below `SKILL.md`.
