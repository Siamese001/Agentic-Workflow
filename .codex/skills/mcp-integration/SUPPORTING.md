# MCP Integration — Supporting Detail

> This file holds content split from `SKILL.md` to keep it within the Anthropic 500-line budget.
> Cross-references in `SKILL.md` point here.

---

## §13 — Task Manager MCP (Full Detail)

**In-house.** **Selective use only.** For durable, queryable task state — not ordinary planning.

### When To Use

| Intent | Use? | Alternative |
|--------|------|-------------|
| "Track this as tasks" | ✅ Yes | — |
| "Decompose into subtasks" across sessions | ✅ Yes | — |
| Long-horizon multi-session epic | ✅ Yes | — |
| In-session multi-step work | ❌ No | native plan mode + `structured-reasoning` guidance |
| Plan-file work | ❌ No | `.codex/plans/*.md` |

### Tool Routing

| Goal | Tool |
|------|------|
| Create task | `create_task` |
| Decompose | `decompose_task` |
| Get details | `task_info` |
| Update status | `update_task` |

### Hard Rules
1. **Decomposition mandatory** for complexity above `low` (`decompose_task` first)
2. **Status discipline** — `in-progress` before executing, `done`/`failed` when finished
3. **Parallelizable subtasks share `sequenceOrder`**
5. **Don't replicate plan-file content**

---

## §Redirects — Legacy Skill Index

Individual MCP guide skills redirect to the corresponding section in `SKILL.md`:

| Old Skill | Section in SKILL.md |
|-----------|---------------------|
| `filesystem-mcp` | §1 |
| `redis-cache` | §2 |
| `deepwiki` | §3 |
| `context7` | §4 |
| `playwright` | §5 |
| `vector-db` | §6 |
| `notion` | §7 |
| `tavily-research` | §8 |
| `otel-telemetry` | §9 |
| `pytest-mcp` | §10 |
| `gitkraken` | §11 |
| `memory-mcp` | §12 |
| `task-manager-mcp` | §13 |
