Use for Claude Code configuration, rules, hooks, skills, agents, MCP, and commands lookup questions.

# Claude Code Config Lookup

## Local-first lookup order

When the question is about Claude Code behavior or this repo's `.claude` config, search in this order:

1. `CLAUDE.md` (repo root — always-on operating contract + rules index)
2. `.claude/rules/*.md`
3. `.claude/skills/**/SKILL.md` plus supporting checklists/templates/resources
4. `.claude/agents/*.md`
5. `.claude/settings.json` and `.claude/hooks/**`
6. `.mcp.json` (repo root) and `.claude/mcp-notes.md`
7. `.claude/commands/*.md`

## Use

Locate the governing surface before answering configuration questions. Keep answers grounded in
file paths. The `.cursor/` tree is **legacy** (the prior Cursor config the `.claude/` config was
migrated from) — treat it as historical unless a user explicitly asks about Cursor or migration
history. The one live dependency on `.cursor/` is the governance script engine under
`.claude/governance/scripts/**`, which the Claude Code hooks still invoke (see `.claude/hooks/`).

## Archive boundary

`.cursor/**`, `.windsurf/**`, `.cursor/_zero_loss_originals/**`, and `.claude/plans/_archive/**`
are historical/compatibility material unless a user explicitly asks for migration history.
