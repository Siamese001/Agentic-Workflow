## §8 — Tavily Research

**Upstream:** https://docs.tavily.com/documentation/agent-skills

### Prerequisites
`TAVILY_API_KEY` must be set as Windows OS env var (`setx TAVILY_API_KEY tvly-...`). `pre_mcp_gate.py` blocks until present.

### Tool Routing — Pick the Right Tool

| User Intent | Tool | When NOT To Use |
|-------------|------|-----------------|
| One-shot question, news | `tavily-search` | Don't use for known URLs |
| Pull full text from URL | `tavily-extract` | Don't search-via-extract |
| Discover URLs on site | `tavily-map` | Cheaper than crawl |
| Pull every page on site | `tavily-crawl` | Credit-heavy; map first |
| Multi-source synthesis | `tavily-research` | Don't use when 1-2 hits answer |

### Hard Rules
1. **Tavily ONLY for external web content** — this repo → `adg_sqlite`, library docs → `context7`, GitHub → `deepwiki`
2. **Prefer direct `httpx` for known API endpoints**
4. **`tavily-research` takes 30–120s** — don't pre-empt

---
