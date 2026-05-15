---
name: context7
description: Up-to-date, versioned official documentation for external libraries, frameworks, SDKs, APIs, CLI tools, and cloud services via the Context7 MCP server. Invoke whenever the user asks about an external package's API syntax, configuration, version migration, library-specific debugging, setup instructions, or CLI usage — even well-known libraries like React, Next.js, Prisma, Express, Tailwind, Django, Spring Boot. Distinguishes Context7 (external library docs) from deepwiki (GitHub repo wiki) and adg_sqlite (this repo's own code). Adapts upstream Context7 (https://context7.com/docs/skills) to the Cursor MCP architecture.
metadata:
  enforcement_layer: behavioural
  enforcement_timing: before_work
  enforcement_type: tool_routing
  deprecated: true
  redirect_to: mcp-integration
---

# ⚠️ DEPRECATED — Redirected to mcp-integration §4

> **Consolidated**: This skill content moved to `mcp-integration/SKILL.md` §4 — Context7 (2026-05-12, W4.P2).
> **Status**: Redirect stub — preserved for backwards compatibility.
> **Action**: Consult `.cursor/skills/mcp-integration/SKILL.md` §4 for current guidance.

---

# Context7 Skill (Legacy)

Context7 is the doc-lookup authority for **external** libraries. Prefer it over web search whenever you'd otherwise grep StackOverflow for an API signature — Context7 returns versioned, source-grounded examples.

**Upstream:** https://context7.com/docs/skills

## When To Use This MCP

| User intent | Use Context7? | Alternative |
|---|---|---|
| "How do I use React `useEffect` cleanup?" | ✅ Yes | — |
| "FastAPI dependency injection example" | ✅ Yes | — |
| "Prisma migration syntax" | ✅ Yes | — |
| "Tailwind v4 changes" | ✅ Yes | — |
| Anything about a published npm/PyPI package | ✅ Yes | — |
| This repo's own code | ❌ No | `adg_sqlite` |
| GitHub repo wiki / Q&A on third-party repo | ❌ No | `deepwiki` |
| Recent news / market data / arbitrary web | ❌ No | `tavily-search` |

## Two-Step Workflow (mandatory)

| Step | Tool | Purpose |
|---|---|---|
| 1 | `resolve-library-id` | Find the canonical library ID — format `/org/project` or `/org/project/version` |
| 2 | `query-docs` | Pose a specific question against that library ID |

Skip step 1 only when the user gave a literal Context7 ID like `/vercel/next.js`.

## Hard Rules

1. **Be specific in queries.** "How to set up authentication with JWT in Express.js" not "auth". The query is sent to Context7's API for ranking.
2. **No secrets in queries.** Don't include API keys, passwords, internal repo paths, or proprietary code in `query`.
3. **Max 3 calls per question.** If the answer isn't there after 3, fall back to web search.
4. **Use `researchMode: true` only on retry.** First call should be lightweight; escalate only if the answer was insufficient.

## Common Workflows

**Library API question:**
1. `resolve-library-id(libraryName='Next.js', query='app router')`
2. `query-docs(libraryId='/vercel/next.js', query='How do I configure middleware in app router?')`

**Version-specific question:**
1. `resolve-library-id(libraryName='Tailwind', query='v4 migration')` → look at returned versions
2. `query-docs(libraryId='/tailwindlabs/tailwindcss/v4.0.0', query='What breaking changes from v3?')`

## Configuration

`CONTEXT7_API_KEY` OS env var is **optional** — increases rate limits but not required. The MCP server works anonymously.

## Skill Registry

Context7 also maintains a public skill registry at https://context7.com/skills covering library-specific workflows (React best practices, web design, PDF processing, etc.). Those are project-installable via `ctx7` CLI; this Cursor skill governs the MCP routing layer above them.
