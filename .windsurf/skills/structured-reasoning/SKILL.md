---
name: structured-reasoning
description: Teaches Cascade how to handle complex multi-step tasks consistently using native reasoning + current MCPs. Replaces Sequential Thinking MCP. Enforces plan-first, execute-second discipline with explicit branching, revision, and evidence validation.
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
| **Reasoning** | Goal normalization, decomposition, branch analysis | Native Cascade reasoning only |
| **Routing** | Tool selection, MCP health check, fallback planning | `mcp1_adg_health`, `mcp13_create_task` |
| **Execution** | Edits, writes, commands | All tools — only after APPROVED |
| **Verification** | Tests, health checks, diff review | `mcp11_run_tests`, `mcp0_git_status` |

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

Use `mcp13_create_task` + `mcp13_decompose_task` for tracking. Emit numbered steps:

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
- Session context loaded (`mcp9_mem_recall_session_start`)
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

Then update task: `mcp13_update_task` with `status=done` and `lessons_learned`.

---

## Branching Protocol

When uncertainty is high at any step:

```
BRANCH POINT — Step N:
  Plan A: <approach> — use if <evidence condition>
  Plan B: <approach> — use if <evidence condition>
  Selecting after evidence pull.
```

Never collapse a branch before evidence is gathered. If the branch cannot be resolved by evidence, invoke HITL:

```python
ask_user_question(
  question="Step N has two valid approaches — which should I use?",
  options=[
    {"label": "Plan A", "description": "<what it does> — Pros: X — Cons: Y"},
    {"label": "Plan B", "description": "<what it does> — Pros: X — Cons: Y"}
  ],
  allowMultiple=False
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

## MCP Role Mapping

| MCP | Functional Role | Failure fallback |
|-----|----------------|-----------------|
| `mcp1` ADG SQLite | Context / evidence (primary) | `/mcp-failure-rca` — STOP if unresolvable |
| `mcp9` Memory | Memory / checkpointing | Proceed; note `[MEMORY UNAVAILABLE]` |
| `mcp13` Task Manager | Plan tracking / decomposition | Use `todo_list` native tool |
| `mcp7` / `read_file` | Context / evidence (file reads) | `read_file` always available natively |
| `mcp11` Pytest | Validation / verification | `run_command` with pytest CLI |
| `mcp0` GitKraken | Validation / version control | `run_command` with git CLI |
| `mcp2` Brave Search | External lookup | `mcp5_fetch` as fallback |
| `mcp4` Enhanced HTTP | External lookup | `mcp5_fetch` as fallback |
| `mcp3` DeepWiki | External lookup (repo docs) | `mcp5_fetch` as fallback |
| `mcp12` Redis | Cache / state inspection | Note `[REDIS UNAVAILABLE]`; proceed |

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
