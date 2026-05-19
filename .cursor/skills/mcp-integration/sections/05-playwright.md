## §5 — Playwright

Browser automation/E2E. **Upstream:** https://playwright.dev/agent-cli/skills

### When To Use

| Intent | Use? | Alternative |
|--------|------|-------------|
| Test live web app flow | ✅ Yes | — |
| Verify UI renders | ✅ Yes | — |
| Take screenshot | ✅ Yes | — |
| Fill/submit form | ✅ Yes | — |
| Capture network requests | ✅ Yes | — |
| Static URL (no JS) | ❌ No | direct `httpx` or `read_url_content` |
| Web search | ❌ No | `tavily-search` |

### Tool Routing

| Goal | Tool | Notes |
|------|------|-------|
| Snapshot (preferred) | `browser_snapshot` | Returns accessibility tree with `ref` IDs |
| Click element | `browser_click` | Needs `ref` from snapshot |
| Fill multiple fields | `browser_fill_form` | Batches field types |
| Type single field | `browser_type` | Use `submit:true` for Enter |
| Navigate | `browser_navigate` | — |
| Screenshot | `browser_take_screenshot` | Visual only |
| Run JS | `browser_evaluate` | Serialized result |
| Console logs | `browser_console_messages` | `level=error` for diagnosis |
| Network inspect | `browser_network_requests` | `filter=/api/.*` |
| Resize viewport | `browser_resize` | Responsive testing |

### Hard Rules
1. **Always snapshot before clicking** — `browser_click` needs `ref`
2. **Close tabs after use** — `browser_tabs(action='close')` or `browser_close`
3. **Output to `.playwright-mcp/`** (gitignored)
4. **Not for static HTML** — use direct `httpx` if no JS needed

---
