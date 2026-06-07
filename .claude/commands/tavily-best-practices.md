---
description: Thin alias — Tavily routing discipline (/tavily-best-practices)
---

# /tavily-best-practices

**Tier:** Workflow alias (routing cheat sheet)

**Procedure SSOT:** [mcp-integration/SKILL.md](../skills/mcp-integration/SKILL.md) §8 · [tavily-research/tool_decision_tree.md](../skills/tavily-research/tool_decision_tree.md)

## Tool pick (external web only)

| Intent | Slash alias | Tavily tool |
|--------|-------------|-------------|
| One-shot lookup | `/tavily-search` | `tavily-search` |
| Known URL text | `/tavily-extract` | `tavily-extract` |
| Site URL list | `/tavily-map` | `tavily-map` |
| Full site pull | `/tavily-crawl` | `tavily-crawl` |
| Multi-source synthesis | `/tavily-research` | `tavily-research` |

**Hard rules:** Repo code → `adg_sqlite`; semantics → `vector_db`; libraries → `context7`; GitHub repos → `deepwiki`.
