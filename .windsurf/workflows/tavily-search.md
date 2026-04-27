---
description: Run a Tavily web search. Cheap, low-latency, 5–20 result snippets with source URLs.
---

# /tavily-search

Single-shot web search via the Tavily MCP. Fastest of the Tavily tools; default first choice for "what's the latest on X" / "find the upstream issue for Y" / "search for Z" prompts.

## When to use

- The answer is on the public web AND not in this repo, an external-library doc set (use `context7`), or a single GitHub repo wiki (use `deepwiki`).
- You want 5–20 ranked snippets with source URLs to skim before deciding what to extract or research.

## Steps

1. Confirm `TAVILY_API_KEY` is set (otherwise `pre_mcp_gate` blocks with setup instructions).
2. Compose the query as a natural-language sentence — Tavily is optimized for full sentences, not keyword soup.
3. Pick parameters:
   - `max_results`: 5 (default; bump to 10–20 only for breadth tasks)
   - `search_depth`: `basic` (default), `advanced` (deeper pages, slower), `fast`/`ultra-fast` (lowest latency)
   - `time_range`: omit for evergreen; set to `day`/`week`/`month`/`year` for news/recency
   - `topic`: `general` (default — only supported value)
   - `include_domains` / `exclude_domains`: list of host names when you trust or distrust specific sources
   - `include_raw_content`: `true` only when you need the parsed HTML inline (rare; prefer `tavily-extract` follow-up)
4. Invoke `tavily-search` (Tavily MCP tool — must be the only MCP call this response per constitutional §25).
5. Cite the source URL inline for every fact you carry forward.

## Examples

| User prompt | Suggested params |
|---|---|
| "Search for the latest news on AI regulations" | `time_range=week`, `topic=general`, `max_results=10` |
| "Find the upstream Anthropic MCP race-condition issue" | `include_domains=["github.com"]`, `search_depth=advanced` |
| "What's the current React 19 best practice for transitions?" | `include_domains=["react.dev","reactjs.org"]`, `search_depth=advanced` |
| "Recent SEC filings about Tesla deliveries" | `include_domains=["sec.gov","reuters.com"]`, `time_range=month`, `topic=general` |

## Forbidden

- ❌ Querying for content already inside this repo (use `adg_sqlite`/`vector_db`/`read_file`)
- ❌ Querying for an external library's API (use `context7`)
- ❌ Pairing this MCP call with any other MCP call in the same response (constitutional §25)
