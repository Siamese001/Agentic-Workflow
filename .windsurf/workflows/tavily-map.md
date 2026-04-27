---
description: Discover the URL inventory of a website without fetching content. Cheap, fast, ideal pre-crawl step.
---

# /tavily-map

Returns a structured list of URLs reachable from a base URL, optionally filtered by natural-language instructions or path regex. Use BEFORE `tavily-crawl` to scope the crawl set without paying for content.

## When to use

- "What pages exist on docs.example.com?" — pure inventory question.
- Pre-flight for a `tavily-crawl` to check the actual size and shape of the target before paying for full content.
- "Find the auth/billing/changelog page on this site" — natural-language path discovery.

## Steps

1. Confirm `TAVILY_API_KEY` is set.
2. Pick parameters:
   - `url`: base URL to map.
   - `max_depth`: 1 (default) or 2 — how many link-hops to follow.
   - `max_breadth`: 20 (default) — links per page.
   - `limit`: 50 (default) — total URLs returned.
   - `instructions`: natural-language filter (e.g. `"Find API docs and guides"`).
   - `select_paths` / `select_domains`: regex filters when the site has predictable structure.
   - `exclude_paths`: regex filter to drop noisy sections (`/blog/.*`, `/changelog/.*`).
3. Invoke `tavily-map` (sole MCP call this response).
4. If the inventory looks right, follow up in a SEPARATE response with `tavily-crawl` (or `tavily-extract` for individual high-value URLs).

## Examples

| User prompt | Suggested params |
|---|---|
| "Map docs.stripe.com" | `url="https://docs.stripe.com"`, `limit=200` |
| "Find the API ref pages on docs.example.com" | `url=...`, `instructions="Find API reference pages"` |
| "List all /blog/ URLs on example.com" | `url=...`, `select_paths=["/blog/.*"]`, `limit=500` |

## Forbidden

- ❌ Mapping this repo (use `find_by_name` / `directory_tree`).
- ❌ Pairing with any other MCP call this response (constitutional §25).
