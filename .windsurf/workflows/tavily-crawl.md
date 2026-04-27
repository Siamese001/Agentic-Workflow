---
description: Crawl a website and extract content from many pages. Credit-heavy — bound the scope first.
---

# /tavily-crawl

Walks a website's link graph and extracts content from each page. The most expensive Tavily tool — always bound it with `select_paths`, `exclude_paths`, and `limit`. Prefer running `tavily-map` first to see what you'll be paying for.

## When to use

- "Download the Next.js docs for offline reference"
- "Crawl the Stripe API docs and save them locally"
- "Pull every page under /api/ and /guides/ on docs.example.com"

## Steps

1. Confirm `TAVILY_API_KEY` is set.
2. **Strongly recommended first**: run `/tavily-map` (in a previous response) to inventory the site and pick the right `select_paths` / `exclude_paths` regex set.
3. Pick parameters:
   - `url`: base URL.
   - `max_depth`: 1 (default) or 2 — link-hops from base.
   - `max_breadth`: 20 (default) — links per page.
   - `limit`: 50 (default) — total pages crawled. **Bound this aggressively** — credits scale linearly.
   - `extract_depth`: `basic` (default) or `advanced` for tables/embedded content.
   - `format`: `markdown` (default) or `text`.
   - `instructions`: natural-language semantic focus (returns relevant chunks, NOT full pages — a ~5× cost reduction when you want focused content).
   - `select_paths` / `select_domains`: regex filters — required for cost control on large sites.
   - `exclude_paths`: regex filters for noise.
4. Invoke `tavily-crawl` (sole MCP call this response).
5. If the user asked for offline reference, save the response to `docs/external/<host>/` using a follow-up `write_to_file` step (the crawl tool itself returns content, not files).

## Examples

| User prompt | Suggested params |
|---|---|
| "Crawl Stripe docs API section" | `url="https://docs.stripe.com"`, `select_paths=["/api/.*"]`, `limit=100`, `extract_depth=advanced` |
| "Find auth-related content across docs.example.com" | `url=...`, `instructions="Find authentication and authorization docs"`, `limit=30` (chunks, not full pages) |
| "Pull the Anthropic MCP spec docs" | `url="https://modelcontextprotocol.io"`, `select_paths=["/docs/.*","/specification/.*"]`, `exclude_paths=["/blog/.*"]`, `limit=80` |

## Cost Controls (mandatory)

- Always set `limit` explicitly.
- Always set `select_paths` OR `select_domains` for sites larger than a single doc page.
- Prefer `instructions=` when you only need the relevant chunks — much cheaper than full-page extract for every page.

## Forbidden

- ❌ Unbounded crawls (`limit` not set, no path filter) on commercial-scale sites.
- ❌ Crawling this repo (use `directory_tree` / `find_by_name`).
- ❌ Pairing with any other MCP call this response (constitutional §25).
