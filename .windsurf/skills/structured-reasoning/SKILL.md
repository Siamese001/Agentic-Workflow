---
name: structured-reasoning
description: Provides the plan-first, execute-second reasoning packet (SR_INTAKE, SR_PLAN, SR_APPROVAL, SR_EXECUTE, SR_VERIFY) for complex multi-step tasks. Use when the task is T2/T3 (2+ files, cross-layer, architecture decisions, or multi-file debugging) and requires explicit decomposition, branching, revision, and evidence validation before any edits begin.
metadata:
  enforcement_layer: windsurf
  enforcement_timing: before_work
  enforcement_type: behavioural
---

# Structured Reasoning Skill

**Replaces**: Sequential Thinking MCP (retired — historically hung on Windows, stdio fragility, no reliable stdio transport on this host)

**Prerequisite**: None. This skill is self-contained.

**Invocation**: Automatically applies to all T2/T3 tasks. Manually via `/structured-reasoning`.

---

## Core Principle

> **Reasoning and execution are separate phases. No edits occur until a plan is approved.**

Four layers — keep them separated at all times:

| Layer | What happens here | Allowed tools |
|-------|------------------|---------------|
| **Reasoning** | Goal normalization, decomposition, branch analysis | Native Cursor Agent reasoning only |
| **Routing** | Tool selection, MCP health check, fallback planning | `adg_health` (server: `adg_sqlite`), `create_task` (server: `task_manager`) |
| **Execution** | Edits, writes, commands | All tools — only after APPROVED |
| **Verification** | Tests, health checks, diff review | `run_tests` (server: `pytest_mcp`), `git_status` (server: `GitKraken`) |

Collapsing all four into one opaque step is **FORBIDDEN**.

---

## When This Skill Applies

**MANDATORY (T2/T3):**
- Touching 2+ files
- Cross-layer changes
- Architecture decisions
- Debugging multi-file bugs
- Planning waves/phases
- ADG graph analysis

**EXEMPT (T0/T1):**
- Pure questions (no code changes)
- ≤1 file, ≤20 lines, obvious scope

---

## Plan-First Protocol

### Step 1 — Emit SR_INTAKE block

Before any tool calls, write:

```
## SR_INTAKE
Objective: <one sentence>
Constraints: [list]
Assumptions: [list — flag uncertain ones]
Tier: T2 | T3
```

### Step 2 — Decompose into SR_PLAN

Use `create_task` + `decompose_task` (server: `task_manager`) for tracking. Emit numbered steps:

```
## SR_PLAN
1. [verb-first concrete step]
2. ...
N. [verification]

Tools needed: [list with justification]
Missing info: [list gaps]
Risks / stop conditions: [list]
```

### Step 3 — Pull evidence (reads only, no writes)

Execute only query/read calls. Confirm:
- ADG MCP healthy (`mcp1_adg_health`)
- Session context loaded (`mcp5_mem_recall_session_start`)
- All relevant files read
- Blast radius confirmed via ADG fanout/fanin

### Step 4 — Validate plan against evidence

Emit one of:
- `SR_APPROVAL: APPROVED`
- `SR_APPROVAL: REVISED` (re-emit plan, loop back)
- `SR_APPROVAL: CLARIFY` (ask user a specific question)
- `SR_APPROVAL: ABSTAIN` (evidence too weak)

### Step 5 — Execute (only after APPROVED)

Step-by-step. Name each step. State tool. Check result before next step.

### Step 6 — Emit SR_SUMMARY

After execution, emit this block with all fields:

```
## SR_SUMMARY
What changed:
  - <file or artifact> — <what was done>

What was verified:
  - <test run / health check / diff review>

What remains uncertain:
  - <item> — <why uncertain>
  - NONE (if fully resolved)

Rollback / repair note:
  - <git reset or file restore command>
  - N/A (if no destructive changes)

Recommended next step:
  - <concrete action — who, what, when>
```

Then update task: `update_task` (server: `task_manager`) with `status=done` and `lessons_learned`.

---

## Branching Protocol

When uncertainty is high at any step:

```
BRANCH POINT — Step N:
  Plan A: <approach> — use if <evidence condition>
  Plan B: <approach> — use if <evidence condition>
  Selecting after evidence pull.
```

Never collapse a branch before evidence is gathered. If the branch cannot be resolved by evidence, invoke the enriched choice builder:

```python
from tools.decisions.enriched_choice_builder import build_enriched_choice_question

# Build enriched question with UI invariants (confidence prefix, star, trade-off)
payload = build_enriched_choice_question(
    question="Step N has two valid approaches — which should I use?",
    options=[
        {
            "id": "A",
            "label": "Plan A — <approach>",
            "description": "<what it does>",
            "tradeoff": "Pros: X · Cons: Y",
        },
        {
            "id": "B",
            "label": "Plan B — <approach>",
            "description": "<what it does>",
            "tradeoff": "Pros: X · Cons: Y",
        },
    ],
    recommended_id="A",  # optional
    telemetry_context={"step": "N", "branch_reason": "evidence_inconclusive"},
)

# Emit the telemetry packet (REQUIRED)
print("ASK_USER_QUESTION_PACKET: " + json.dumps(payload["telemetry_packet"]))

# Present to user
ask_user_question(
    question=payload["question"],
    options=payload["options"],
    allowMultiple=False,
)
```

---

## Revision Protocol

Revision is required after:
1. Initial plan — does it address the full objective?
2. Evidence pull — does new data invalidate any step?
3. Execution result — did an unexpected outcome change remaining steps?

Each revision must:
- State what changed and why
- Re-emit the affected steps as `SR_PLAN_v2` (or v3, etc.)
- Not silently carry forward stale assumptions

---

## Retrieval Loop

Use this order unless the task clearly needs a different path:

1. **Local context first**: `.windsurf/`, nearby docs, direct file reads
2. **Exact retrieval**: paths, symbols, filenames, commands
3. **Structured retrieval**: ADG for dependency questions, pytest MCP for tests, memory MCP for durable precedent
4. **Semantic retrieval**: vector search only when exact lookup leaves gaps
5. **Fresh external research**: only when local evidence is insufficient or freshness matters

## RAG Discipline

When evidence is dense or the task is research-heavy:

- Separate retrieval from synthesis — pull facts first, write second
- Broad pass first, narrow pass second, then re-rank before answering
- If precision matters, anchor claims to quotes, snippets, or exact tool output before summarizing
- Keep working context lean — split a large task into phases instead of carrying every reference forward

---

## MCP Role Mapping

> **Note on prefixes:** Windsurf assigns live `mcp0`/`mcp1`/`mcp2`... numbers by load order from
> `~/.codeium/windsurf/mcp_config.json`. Use the server names and tool names in this table, not
> numeric prefix labels — numeric prefixes shift whenever a server is added or removed.

| MCP (YAML name) | When to invoke | Failure fallback |
|-----------------|---------------|-----------------|
| **adg_sqlite** | Dependency analysis, blast radius, layer violations, node/edge lookup — required before any T2/T3 edit | `/mcp-failure-rca` — STOP if unresolvable |
| **memory** | Session start context (`mem_recall_session_start`), store durable architectural decisions, cross-session continuity | Proceed; note `[MEMORY UNAVAILABLE]` |
| **task_manager** | T2/T3 task decomposition (`create_task`, `decompose_task`, `update_task`) — one task per SR session | Use `todo_list` native tool |
| **filesystem** | File reads (`read_text_file`, `list_directory`, etc.) — write tools BLOCKED by gate, use native `edit`/`write_to_file` | `read_file` native tool always available |
| **pytest_mcp** | Scoped test runs, test discovery, coverage — prefer over `run_command pytest` for structured output | `run_command` with pytest CLI |
| **gitkraken** | Git status, log, commit, branch, PR/issue ops — prefer over `run_command git` | `run_command` with git CLI |
| **redis** | ADG hot cache inspection, namespace stats, sentinel key check — primary ADG health path per constitutional §13 | Note `[REDIS UNAVAILABLE]`; fall back to adg_sqlite probe |
| **direct `httpx` in code** | External API calls, URL fetching with POST/headers/auth, batch HTTP — write a small Python helper. The `enhanced_http` MCP was retired 2026-04-27. | `read_url_content` native tool for one-off fetches with user approval |
| **deepwiki** | Questions about external GitHub repos, third-party lib docs — not for this repo | `read_url_content` as fallback |
| **vector_db** | Similarity search against ChromaDB embeddings — any retrieval requiring "find facts similar to X" (RAG, duplicate detection) | Note `[VECTOR_DB UNAVAILABLE]`; proceed without semantic retrieval |
| **otel_mcp** | Runtime observability — query live spans, metrics, anomalies, healing chains, policy decisions. Use when evaluating *what happened at runtime* | Note `[OTEL UNAVAILABLE]`; read runtime_adg SQLite directly |

**No single MCP is an opaque reasoning black box.** Each has one concrete job.

---

## Structured Reasoning Evidence Standards

These evidence rules apply when this skill is used:
- Based on text search alone (no ADG confirmation)
- Assumes relationships without graph proof
- Relies on stale session context (>30 min since last `mem_recall`)
- Missing blast radius confirmation for cross-file changes

Weak evidence → `SR_APPROVAL: CLARIFY` or `SR_APPROVAL: ABSTAIN`.

---

## Forbidden Patterns

- ❌ Emitting edits before `SR_APPROVAL: APPROVED`
- ❌ Silently collapsing a branch without evidence
- ❌ Skipping `SR_INTAKE` block
- ❌ Retrying a hung MCP tool call in a loop
- ❌ Using grep as a substitute for ADG MCP when ADG fails
- ❌ Leaving tasks in `in_progress` indefinitely
- ❌ Carrying stale assumptions across revision cycles
- ❌ Collapsing reasoning + routing + execution + verification into one step

---

## Supporting Files

- `checklist.md` — pre-execution gate checklist
- `plan-template.md` — copy-paste SR_INTAKE + SR_PLAN template
- `verification-template.md` — copy-paste SR_SUMMARY template
- `failure-template.md` — what to emit when a step fails mid-execution
