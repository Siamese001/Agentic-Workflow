---
name: "source-command-skill-creator"
description: "Scaffold a new Claude Code skill (.claude/skills/<slug>/SKILL.md) from the house-style template. Use when authoring a new skill so it inherits the canonical frontmatter, trigger table, hard rules, procedure, forbidden patterns, and references shape."
---

# source-command-skill-creator

Use this skill when the user asks to run the migrated source command `skill-creator`.

## Command Template

# /skill-creator — Scaffold a New Skill

This workflow stamps a new skill from `.claude/templates/skill-template.md` so every skill in this repo shares the same shape that auto-invocation, `pre_prompt_classifier.py`, and the MCP Registry expect.

## When to use

- You are about to author a new skill in `.claude/skills/<slug>/SKILL.md`.
- You want auto-invocation to fire reliably — that requires a specific frontmatter `description` shape.
- You want the new skill to declare its sibling-skill boundaries up front (prevents overlap drift).

Do NOT use for: editing an existing skill (just edit it directly), or for one-shot prose docs (use `docs/`).

## Inputs (gather before running)

| Field | Example | Notes |
|---|---|---|
| `<slug>` | `redis-cache` | kebab-case; must match folder name |
| Capability sentence | "Redis cache inspection — health, key scanning, TTL, namespace stats — via the in-house redis MCP server." | 1 sentence, leads the description |
| Invocation triggers | "Invoke when the user asks about Redis cache state, ADG hot-cache status, …" | 1–3 sentences, matched by auto-invoke |
| Sibling distinctions | "Distinguishes Redis MCP (cache state) from adg_sqlite (canonical truth)." | 1 sentence per sibling |
| Upstream source (if any) | `https://docs.upstream.com/skills` | Cite if adapting external docs |
| Underlying tool/MCP | `redis` MCP server | Or "Claude Code tool" |

## Steps

### 1. Confirm the skill is not duplicative

Search existing skills for overlapping capability before authoring:

```
.claude/skills/  →  list_dir
```

If a skill within ~80% capability already exists, edit it instead of creating a new one. The MCP authority rule (`global_rules.md` §MCP Authority) requires one SSOT per capability.

### 2. Create the skill folder

```
.claude/skills/<slug>/
```

### 3. Stamp SKILL.md from template

Copy `.claude/templates/skill-template.md` to `.claude/skills/<slug>/SKILL.md` and fill in:

- **Frontmatter `name`** — `<slug>` exactly (must match folder).
- **Frontmatter `description`** — capability sentence + invocation triggers + sibling distinctions + upstream citation. ~3–5 sentences. This is the auto-invocation match surface; be specific.
- **Frontmatter `metadata`** — pick `enforcement_layer` / `enforcement_timing` / `enforcement_type`.
- **PREREQUISITE block** — env vars, MCP health, gate scripts. Delete the block if none apply.
- **When to Invoke table** — 3+ rows mapping user intent → action.
- **Hard Routing Rules table** — invariants that MUST hold.
- **Standard Procedure** — keep at 5 numbered steps unless the skill is genuinely more complex.
- **Forbidden Patterns** — 3+ rows; cite the constitutional rule or sibling skill that gets violated.
- **References** — fill every row that applies; delete rows that don't.

### 4. Add supporting files only if needed

- A decision tree (`tool_decision_tree.md`) — only if there are >3 tools/branches and the SKILL.md routing table grows past ~6 rows.
- An examples file — only if the SKILL.md examples would push it past ~200 lines.

Most skills fit cleanly in a single SKILL.md.

### 5. Wire intent detection (optional, T2/T3 invocation only)

If the skill should be SR_MANDATE-injected for tier-2/3 prompts:

- Add `_<SKILL>_SIGNALS = (...)` and `_detect_<skill>_intent(text)` in `.claude/governance/scripts/pre_prompt_classifier.py`.
- Add a routing trace and SR-hint block following the existing patterns (e.g. `_NOTION_SIGNALS`, `_MEMORY_INTENT_SIGNALS`).

Skip this for skills that should only auto-invoke from the description match.

### 6. Update AGENTS.md MCP Quick Reference (only if skill wraps an MCP)

If the skill wraps an MCP server, run:

```
python .claude/governance/scripts/sync_mcp_config.py
```

This rewrites the MCP Quick Reference block with a row pointing at the new skill.

### 7. Verify

```
python ops_scripts/ci/check_mcp_sync_integrity.py
python ops_scripts/ci/check_agents_mcp_coverage.py
```

Both must pass before commit.

## House-Style Invariants (hard rules)

- **Frontmatter `name` MUST match folder slug.** The skill loader keys off this.
- **`description` MUST be specific.** Generic descriptions ("helps with X") fail auto-invocation. Lead with capability, list triggers, name siblings.
- **Reference siblings explicitly.** Every skill that overlaps another must declare the boundary in the description and again in the body. Prevents drift.
- **Cite upstream when adapting.** External skill ports MUST link back; differences from upstream MUST be called out.
- **No emojis** unless the user explicitly requested them (constitutional convention).
- **Third-person, deterministic prose.** Skills are read by Claude Code, not authored as a chat reply.

## References

- Skill template: `.claude/templates/skill-template.md`
- Plan template (sibling pattern): `.claude/templates/execution-plan-template.md`
- Sync script: `.claude/governance/scripts/sync_mcp_config.py`
- Coverage gates: `ops_scripts/ci/check_mcp_sync_integrity.py`, `check_agents_mcp_coverage.py`
- Frontmatter precedent: `.claude/skills/tavily-research/SKILL.md`, `.claude/skills/adg-sqlite/SKILL.md`
- Constitutional rule §17 (Memory Lifecycle), §25 (MCP serialization), §29 (Closed-Loop Router) — common cite targets in skill bodies

## MANUAL MIGRATION REQUIRED

Migrated from source command `skill-creator` into a Codex skill. Invoke it as `$source-command-skill-creator` and manually rewrite any slash-command behavior that depended on provider-specific runtime expansion.
