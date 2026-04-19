---
trigger: model_decision
description: Use for Windsurf IDE configuration, rules, hooks, skills, workflows, and local Windsurf documentation lookup questions.
---
# Windsurf Config Lookup

## Local-First Lookup Order

When the question is about Windsurf behavior, search in this order:

1. `.windsurf/RULES_INDEX.md`
2. `.windsurf/rules/*.md`
3. `.windsurf/skills/**/SKILL.md`
4. `.windsurf/workflows/*.md`
5. `.windsurf/hooks.json`
6. `.windsurf/mcp_config.json`
7. local docs mirror such as `docs/windsurf/`

## Good Uses

- "why is this rule firing?"
- "which file governs this behavior?"
- "how do hooks and skills interact?"
- "where is the MCP config SSOT?"
- "what workflow should I run for this issue?"

## Bad Uses

- general repo architecture questions unrelated to Windsurf
- feature design questions that do not depend on Windsurf behavior

## Fallback

Use web search only when the answer is likely version-sensitive or newly-changed. Prefer `docs/windsurf/changelog.md` for recent product changes.
