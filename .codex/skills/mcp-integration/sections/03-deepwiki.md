## §3 — DeepWiki

DeepWiki indexes GitHub repos for AI-grounded answers. **Upstream:** https://github.com/deepwiki/deepwiki-mcp

### When To Use

| Intent | Use? | Alternative |
|--------|------|-------------|
| "How does facebook/react implement X?" | ✅ Yes | — |
| "What's the layout of microsoft/playwright?" | ✅ Yes | — |
| This repo's own code | ❌ No | `adg_sqlite` |
| Published library API | ❌ No | `context7` |
| Web search beyond GitHub | ❌ No | `tavily-search` |

### Tool Routing

| Goal | Tool |
|------|------|
| List doc topics | `read_wiki_structure` |
| View full docs | `read_wiki_contents` |
| Ask free-form question | `ask_question` |

### Hard Rules
1. **`owner/repo` format only** — `facebook/react`, not URLs
2. **`ask_question` accepts up to 10 repos**
3. **Do not use for this repo** — `adg_sqlite` is canonical

---
