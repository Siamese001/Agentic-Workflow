---
description: Extract clean markdown content from one or more known URLs via Tavily.
---

# /tavily-extract

Pulls full text/markdown from URL(s) you already have. Use this when the URL is in the conversation or is the obvious next step after a `tavily-search` result.

## When to use

- You already have specific URL(s) and need their full content (not snippets).
- You need to handle a difficult page: LinkedIn, paywalled article, table-heavy page, embedded content — set `extract_depth=advanced`.

## Steps

1. Confirm `TAVILY_API_KEY` is set.
2. Pick parameters:
   - `urls`: list of one or more URLs (Tavily charges per URL).
   - `extract_depth`: `basic` (default, fast) or `advanced` (LinkedIn / paywalls / tables / embedded content).
   - `format`: `markdown` (default) or `text`.
   - `include_images`: `true` if the page's images carry meaning.
   - `query`: optional — set to a focus query and Tavily will rerank chunks by relevance instead of returning the whole page.
3. Invoke `tavily-extract` (sole MCP call this response).
4. Cite the source URL for every fact carried forward.

## Examples

| User prompt | Suggested params |
|---|---|
| "Extract https://example.com/blog/post" | `urls=["https://example.com/blog/post"]` |
| "Pull docs from these three pages: A, B, C" | `urls=[A, B, C]`, `extract_depth=basic` |
| "Get only the auth section of https://docs.example.com/api" | `urls=["https://docs.example.com/api"]`, `query="authentication API"`, `extract_depth=advanced` |
| "Extract this LinkedIn profile" | `urls=[...]`, `extract_depth=advanced` |

## Forbidden

- ❌ Extracting from this repo's working tree (use `read_file`)
- ❌ Extracting raw API JSON (use direct `httpx` in code, or native `read_url_content` for one-off fetches)
- ❌ Pairing with any other MCP call this response (constitutional §25)
