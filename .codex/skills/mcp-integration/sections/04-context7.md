## §4 — Context7

**Upstream:** https://context7.com/docs/skills. Doc-lookup authority for **external** libraries.

### When To Use

| Intent | Use? | Alternative |
|--------|------|-------------|
| "How do I use React `useEffect`?" | ✅ Yes | — |
| "FastAPI dependency injection example" | ✅ Yes | — |
| "Prisma migration syntax" | ✅ Yes | — |
| This repo's own code | ❌ No | `adg_sqlite` |
| GitHub repo Q&A | ❌ No | `deepwiki` |
| Recent news/web | ❌ No | `tavily-search` |

### Two-Step Workflow (Mandatory)

| Step | Tool | Purpose |
|------|------|---------|
| 1 | `resolve-library-id` | Find canonical ID (`/org/project`) |
| 2 | `query-docs` | Ask specific question |

### Hard Rules
1. **Be specific in queries** — "JWT auth in Express.js" not "auth"
2. **No secrets in queries**
3. **Max 3 calls per question**
4. **Use `researchMode: true` only on retry**

---
