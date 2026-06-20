---
name: playwright
description: Browser automation, accessibility-tree snapshots, end-to-end UI verification, screenshots, network capture, and form filling via the Playwright MCP server. Invoke when the user asks to test a web flow, verify UI behavior, take a screenshot, capture network requests, automate browser actions, or run end-to-end checks against a live site. Distinguishes Playwright MCP's snapshot/click/fill/evaluate/screenshot surface.
metadata:
  enforcement_layer: behavioural
  enforcement_timing: before_work
  enforcement_type: tool_routing
  deprecated: true
  redirect_to: mcp-integration
---
# ⚠️ DEPRECATED — Redirected to mcp-integration §5

> **Consolidated**: This skill content moved to `mcp-integration/SKILL.md` §5 — Playwright (2026-05-12, W4.P2).
> **Status**: Redirect stub — preserved for backwards compatibility.
> **Action**: Consult `.codex/skills/mcp-integration/SKILL.md` §5 for current guidance.

---

# Playwright Skill (Legacy)

Claude Code-native adaptation of the upstream Playwright agent skills. The MCP server ID is `playwright` in `.mcp.json` (Microsoft's `@playwright/mcp` thin wrapper).

**Upstream:** https://playwright.dev/agent-cli/skills

## When To Use This MCP

| User intent | Use Playwright MCP? | Alternative |
|---|---|---|
| Test a live web app flow | ✅ Yes | — |
| Verify UI renders correctly | ✅ Yes | — |
| Take a screenshot of a page | ✅ Yes | — |
| Fill a form and submit | ✅ Yes | — |
| Capture network requests during interaction | ✅ Yes | — |
| Fetch a known static URL (no JS) | ❌ No | direct `httpx` in code, or native `read_url_content` for one-off fetches |
| Search the web | ❌ No | `tavily-search` |
| Read GitHub repo wiki | ❌ No | `deepwiki` |

## Tool Routing — Pick the Right Playwright Tool

| Goal | Tool | Notes |
|---|---|---|
| Snapshot the page (preferred — better than screenshot for actions) | `browser_snapshot` | Returns accessibility tree with `ref` IDs |
| Click an element | `browser_click` | Needs `ref` from snapshot |
| Fill multiple fields | `browser_fill_form` | Batches `textbox`/`checkbox`/`radio`/`combobox` |
| Type into a single field | `browser_type` | Use `submit:true` for Enter |
| Navigate to URL | `browser_navigate` | — |
| Take screenshot (visual only) | `browser_take_screenshot` | Cannot drive actions; use snapshot for that |
| Run arbitrary JS | `browser_evaluate` | Returns serialized result |
| Read console logs | `browser_console_messages` | `level=error` for diagnosis |
| Inspect network | `browser_network_requests` | `filter=/api/.*` to scope |
| Resize viewport | `browser_resize` | For responsive testing |

## Hard Rules

1. **Always snapshot before clicking.** `browser_click` needs `ref` from `browser_snapshot`.
2. **Close tabs after use.** Call `browser_tabs(action='close')` or `browser_close` to free the headless browser.
3. **Output goes to `.playwright-mcp/`** at repo root (gitignored). Don't commit screenshots there.
4. **Do not use for static HTML.** If JS isn't required, direct `httpx` in code (or native `read_url_content` for a one-off fetch with user approval) is faster and cheaper.

## Common Workflows

**E2E flow verification:**
1. `browser_navigate` → URL
2. `browser_snapshot` → capture state, get `ref` IDs
3. `browser_click` / `browser_fill_form` → drive the flow
4. `browser_snapshot` → verify post-state
5. `browser_take_screenshot` (optional, for evidence)
6. `browser_close`

**Network capture:**
1. `browser_navigate`
2. perform interaction
3. `browser_network_requests(filter='/api/', requestBody=true)` → inspect payloads

## Upstream Skill References

The upstream Playwright skills cover: test running/debugging, request mocking, Playwright code execution, browser session management, storage state, test generation, tracing, video recording. Most of those map onto the same MCP tool surface above. When you need a deeper recipe (e.g., trace recording), consult https://playwright.dev/agent-cli/skills directly.
