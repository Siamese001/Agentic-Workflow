---
name: deepwiki
description: AI-powered structured documentation and Q&A for any third-party GitHub repository via the DeepWiki MCP server. Invoke when the user asks about an external GitHub project's architecture, file layout, how a specific feature is implemented in another codebase, or wants to ask a free-form question about a public repo. Distinguishes DeepWiki (third-party GitHub) from context7 (published library docs) and adg_sqlite (this repo's own code). Adapts the upstream DeepWiki MCP (https://github.com/deepwiki/deepwiki-mcp) for the Cursor MCP architecture.
metadata:
  enforcement_layer: behavioural
  enforcement_timing: before_work
  enforcement_type: tool_routing
  deprecated: true
  redirect_to: mcp-integration
---

# ⚠️ DEPRECATED — Redirected to mcp-integration §3

> **Consolidated**: This skill content moved to `mcp-integration/SKILL.md` §3 — DeepWiki (2026-05-12, W4.P2).
> **Status**: Redirect stub — preserved for backwards compatibility.
> **Action**: Consult `.cursor/skills/mcp-integration/SKILL.md` §3 for current guidance.

---

# DeepWiki Skill (Legacy)

DeepWiki indexes GitHub repos and serves AI-grounded answers about their structure, behavior, and code patterns. Use it to study other people's code without cloning.

**Upstream:** https://github.com/deepwiki/deepwiki-mcp

## When To Use This MCP

| User intent | Use DeepWiki? | Alternative |
|---|---|---|
| "How does facebook/react implement hooks?" | ✅ Yes | — |
| "What's the layout of `microsoft/playwright`?" | ✅ Yes | — |
| "Find the auth flow in `supabase/supabase`" | ✅ Yes | — |
| Any free-form question about a public repo | ✅ Yes | — |
| This repo's own code | ❌ No | `adg_sqlite` |
| Published library API docs | ❌ No | `context7` |
| Web search beyond GitHub | ❌ No | `tavily-search` |

## Tool Routing

| Goal | Tool |
|---|---|
| List documentation topics for a repo | `read_wiki_structure` |
| View full documentation for a repo | `read_wiki_contents` |
| Ask a free-form question | `ask_question` |

## Hard Rules

1. **`owner/repo` format only.** `read_wiki_structure(repoName='facebook/react')`, not URLs or branches.
2. **`ask_question` accepts up to 10 repos** — use a list for cross-repo questions.
3. **Do not use for this repo.** `adg_sqlite` is canonical for our own dependency graph and code structure.
4. **Public repos only** unless private mode is configured upstream.

## Common Workflows

**Study an unfamiliar repo:**
1. `read_wiki_structure(repoName='owner/repo')` → scan topic list
2. `read_wiki_contents(repoName='owner/repo')` → read full wiki if small
3. `ask_question(repoName='owner/repo', question='How does X work?')` → drill in

**Cross-repo comparison:**
- `ask_question(repoName=['repo1', 'repo2', 'repo3'], question='How does each handle Y?')`
