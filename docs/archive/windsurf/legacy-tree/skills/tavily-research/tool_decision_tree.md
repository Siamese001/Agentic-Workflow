# Tavily Tool Decision Tree

```
┌──────────────────────────────────────────────────────────────────────┐
│ The user wants information that is on the public web.                │
└─────────────────┬────────────────────────────────────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────────────────────────────────────┐
│ Is the source already INSIDE this repo or in a known local artifact? │
│   YES → STOP. Tavily is the wrong tool.                              │
│         Use adg_sqlite (structural), vector_db (semantic),           │
│         or read_file (literal).                                      │
│   NO  → continue.                                                    │
└─────────────────┬────────────────────────────────────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────────────────────────────────────┐
│ Is the answer already in published API docs of an external library?  │
│   YES → STOP. Use context7 (resolve-library-id → get-library-docs).  │
│   NO  → continue.                                                    │
└─────────────────┬────────────────────────────────────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────────────────────────────────────┐
│ Is the source a single GitHub repository's wiki/Q&A?                 │
│   YES → STOP. Use deepwiki (ask_question, read_wiki_contents).       │
│   NO  → continue.                                                    │
└─────────────────┬────────────────────────────────────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────────────────────────────────────┐
│ Do you ALREADY have specific URL(s)?                                 │
│   YES → tavily-extract (single or multi-URL).                        │
│         For LinkedIn / paywalled / table-heavy → extract_depth=advanced.│
│   NO  → continue.                                                    │
└─────────────────┬────────────────────────────────────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────────────────────────────────────┐
│ Do you need to inventory a whole site without fetching content?      │
│   YES → tavily-map (cheap; great pre-step for crawl).                │
│   NO  → continue.                                                    │
└─────────────────┬────────────────────────────────────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────────────────────────────────────┐
│ Do you need to ingest an entire site / multiple pages?               │
│   YES → tavily-crawl (with select_paths/exclude_paths to bound cost).│
│   NO  → continue.                                                    │
└─────────────────┬────────────────────────────────────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────────────────────────────────────┐
│ Is this a multi-source synthesis question requiring 5+ pages and     │
│ comparative analysis?                                                │
│   YES → tavily-research (model='auto' default; 'pro' for broad/      │
│         heavy multi-subtopic; 'mini' for narrow tasks).              │
│   NO  → tavily-search (one shot, max_results=5, search_depth='basic').│
└──────────────────────────────────────────────────────────────────────┘
```

## Latency / Credit Budget Cheat Sheet

| Tool | Typical latency | Approx credit cost | When you can afford it |
|---|---|---|---|
| `tavily-search` (basic) | 1–3 s | 1× | Every prompt that asks "what's the latest on X" |
| `tavily-search` (advanced) | 3–8 s | 2–3× | Important fact you'll cite in an ADR / RCA |
| `tavily-extract` (basic, 1 URL) | 1–4 s | 1× | URL is already in conversation |
| `tavily-extract` (advanced, multiple URLs) | 5–20 s | 2–3× per URL | Deep technical pages, paywalls, tables |
| `tavily-map` | 2–6 s | 1× | Pre-step before any crawl |
| `tavily-crawl` (depth=1, limit=20) | 10–40 s | 10–20× | Bounded subset of a docs site |
| `tavily-crawl` (depth=2, limit=100) | 60–180 s | 50–100× | Whole product docs site — last resort |
| `tavily-research` (mini) | 20–60 s | 10–30× | Focused upstream-issue research |
| `tavily-research` (pro) | 60–180 s | 30–80× | Reserved for ADR background or competitive analysis |

Default to the cheapest tool that answers the question. Escalate only if the cheap tool's results are clearly insufficient.
