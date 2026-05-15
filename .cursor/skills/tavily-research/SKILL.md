---
name: tavily-research
description: Web search, page extraction, site mapping, full-site crawl, and multi-source research via the Tavily MCP server. Invoke this skill when the user asks to search the web, look something up online, research a topic, find recent news or upstream issues, extract content from a URL, crawl a documentation site, or build a competitive/market analysis. Distinguishes Tavily's five tools (search/extract/map/crawl/research) and routes to the correct one. Adapts the upstream Tavily Agent Skills (https://docs.tavily.com/documentation/agent-skills) to the Cursor MCP architecture.
metadata:
  enforcement_layer: behavioural
  enforcement_timing: before_work
  enforcement_type: tool_routing
  deprecated: true
  redirect_to: mcp-integration
---

# ⚠️ DEPRECATED — Redirected to mcp-integration §8

> **Consolidated**: This skill content moved to `mcp-integration/SKILL.md` §8 — Tavily Research (2026-05-12, W4.P2).
> **Status**: Redirect stub — preserved for backwards compatibility.
> **Action**: Consult `.cursor/skills/mcp-integration/SKILL.md` §8 for current guidance.

---

# Tavily Research Skill (Legacy)

**PREREQUISITE:** `TAVILY_API_KEY` must be set as a Windows OS environment variable (`setx TAVILY_API_KEY tvly-...` then restart Cursor). `pre_mcp_gate.py` blocks every Tavily call with an actionable message until the key is present — the skill itself does not need to verify the key.

This skill is the Cursor-native adaptation of [Tavily's Agent Skills](https://docs.tavily.com/documentation/agent-skills). The upstream skills are designed for Claude Code's `npx skills add` framework; this skill maps the same five capabilities onto the Tavily MCP tool surface that Cursor Agent actually invokes.

**Decision tree:** see [`tool_decision_tree.md`](./tool_decision_tree.md) in this skill directory for a step-by-step routing flowchart and a latency/credit budget cheat sheet.

## Tool Routing — Pick the Right Tavily Tool

| User intent | Required tool | Slash workflow | When NOT to use |
|---|---|---|---|
| One-shot question, recent news, latest article | `tavily-search` | `/tavily-search` | Don't use for known URLs (use extract); don't use for whole sites (use crawl) |
| You already have a URL — pull its full text/markdown | `tavily-extract` | `/tavily-extract` | Don't search-via-extract; if you don't know the URL, search first |
| Discover what URLs exist on a site without fetching them | `tavily-map` | `/tavily-map` | Cheaper than crawl when you only need URL inventory + selection |
| Pull every page on a site to disk for offline reference | `tavily-crawl` | `/tavily-crawl` | Use sparingly — credit-heavy. Map first to scope the crawl |
| Multi-source synthesis with citations across many pages | `tavily-research` | `/tavily-research` | Don't use when 1-2 search hits would answer; expensive (deep mode = `pro`) |

## Hard Routing Rules (do not violate)

| Rule | Why |
|---|---|
| Use Tavily ONLY for **external** web content | This repo's code goes through `adg_sqlite`; semantic code search through `vector_db`; GitHub repo Q&A through `deepwiki`; library docs through `context7`. |
| Prefer direct `httpx` for known programmatic API endpoints | Tavily extract is for human-readable pages; raw API responses go through `httpx` in code (or native `read_url_content` for one-off fetches with user approval). |
| `tavily-research` is the ONLY Tavily tool that uses chained internal calls | One `tavily-research` invocation may take 30–120s; treat its progress notice as authoritative and do not pre-empt with manual searches. |

## Topic / Time-Range / Domain Tuning (search & research)

| Need | Param | Value |
|---|---|---|
| Tech / general topic | `topic` | `general` (default) |
| Latest news, last 7 days | `topic`, `time_range` | `general` + `week` |
| Specific domain authority | `include_domains` | List of host names (e.g. `["github.com", "anthropic.com"]`) |
| Exclude noisy SEO domains | `exclude_domains` | List of host names |
| Deep coverage when latency is OK | `search_depth` | `advanced` |
| Lowest-latency check | `search_depth` | `fast` or `ultra-fast` |

## Extract Tuning

| Need | Param | Value |
|---|---|---|
| LinkedIn / paywalled / table-heavy page | `extract_depth` | `advanced` |
| Plain markdown page | `extract_depth` | `basic` |
| Embedded images matter | `include_images` | `true` |
| Content is huge — get only relevant chunks | (use `tavily-crawl` with `instructions=` instead) | — |

## Crawl Tuning

| Need | Param | Value |
|---|---|---|
| Save full pages to disk for offline ref | (output is tool's response — pipe to file) | — |
| Get only relevant chunks instead of full pages | (use natural-language `instructions=`) | — |
| Restrict to subset of paths | `select_paths` | List of regex patterns (e.g. `["/api/.*", "/guides/.*"]`) |
| Avoid blogs / changelog | `exclude_paths` | List of regex patterns |
| Cap crawl size | `limit` | Integer (default 50) |

## Standard Procedure

1. **Identify intent** — match the user's prompt to one of the 5 tools above.
2. **Check API key state** — if `pre_mcp_gate` blocks, surface its actionable message and stop. Do NOT attempt curl/grep workarounds.
3. **Pick parameters** — use the topic/time-range/domain matrix; default to fast cost-conscious params unless the user asked for `advanced` or `pro`.
4. **Invoke the Tavily tool** chosen for the task.
5. **Cite sources** — every web-derived fact in Cursor Agent's response must include the source URL inline so the user can verify.
6. **Capture findings to memory** if reusable — durable upstream-issue findings or domain research go into Memory MCP as a `ProceduralPattern` entity (see `memory-notion-writeback.md`).

## Explicit Slash-Command UX (matches upstream Tavily Skills)

The user can invoke any Tavily tool explicitly with a slash command. Each maps 1:1 to a Tavily MCP tool — see the per-workflow files for parameter shape.

| Slash command | Workflow file | Maps to |
|---|---|---|
| `/tavily-search <query>` | `.cursor/workflows/tavily-search.md` | `tavily-search` |
| `/tavily-extract <url(s)>` | `.cursor/workflows/tavily-extract.md` | `tavily-extract` |
| `/tavily-map <url>` | `.cursor/workflows/tavily-map.md` | `tavily-map` |
| `/tavily-crawl <url>` | `.cursor/workflows/tavily-crawl.md` | `tavily-crawl` |
| `/tavily-research <topic>` | `.cursor/workflows/tavily-research.md` | `tavily-research` |
| `/tavily-best-practices` | `.cursor/workflows/tavily-best-practices.md` | meta — read this skill + linked decision tree |

## Forbidden Patterns

- ❌ Calling `tavily-search` to look up something **inside this repo** — use `adg_sqlite` (structural) or `vector_db` (semantic) or `read_file`.
- ❌ Calling `tavily-search` to look up an **external library API** — use `context7` (`resolve-library-id` → `get-library-docs`).
- ❌ Calling `tavily-search` to look up **GitHub repository internals** — use `deepwiki` (`ask_question`).
- ❌ Pre-emptively calling `tavily-search` "to be safe" before answering a question already grounded in repo state.
- ❌ Hand-assembling a curl/scrape workflow because `pre_mcp_gate` blocked the call — the gate exists for a reason; surface the actionable message.
## References

- Upstream documentation: <https://docs.tavily.com/documentation/agent-skills>
- Tavily MCP server config: `.cursor/mcp.json` → `tavily`
- Auth gate: `.cursor/scripts/pre_mcp_gate.py::check_tavily_gate`
- Intent detection: `.cursor/scripts/pre_prompt_classifier.py` (`_TAVILY_SIGNALS`)
- Authority registry: `docs/guides/MCP_Registry.md` → `tavily`
- Sibling skill (external library docs): `context7` MCP via `resolve-library-id` → `get-library-docs`