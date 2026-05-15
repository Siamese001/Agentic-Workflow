---
description: Manual slash workflow for repeatable multi-step reasoning — plan first, execute second. Replaces Sequential Thinking MCP.
---

> **Cursor Agent workflow note:** This workflow is a reusable procedural lane, not always-on policy. Use it to hold staged retrieval, evidence gathering, execution order, and verification steps that would otherwise overload rules. For deep research, separate retrieval, quote extraction, synthesis, and final verification into distinct phases.

# Structured Reasoning Workflow

Invoke with `/structured-reasoning`. Use for any T2/T3 task (2+ files, cross-layer, architecture, debugging).

**First output MUST be a plan. No edits occur during planning.**

**Retrieval order for this workflow:** local repo guidance -> exact lookup -> ADG / structured MCP tools -> semantic retrieval only if gaps remain -> external only when local evidence is insufficient or stale. For dense tasks, retrieve first and synthesize second.

---

## PHASE A — Intake & Goal Normalization

Emit the following block before any tool calls:

```
## SR_INTAKE
Objective: <one sentence — what must be true when this is done>
Constraints:
  - <hard constraint 1>
  - <hard constraint 2>
Assumptions:
  - <assumption 1 — flag if uncertain>
Tier: T2 | T3
Complexity: simple | medium | complex
```

Stop. Do not proceed to Phase B until intake is written.

---

## PHASE B — Decomposition & Plan

Using `create_task` (server: `task_manager`), create the top-level task. Then emit a numbered plan:

> **MCP prefix note:** Tool names in the block below use numeric prefixes that are correct for the current load order (`adg_sqlite`=1, `memory`=5). Resolve live prefix from the tool list visible in your session if numbering has shifted.

```
## SR_PLAN
1. [Step — verb-first, concrete]
2. [Step]
...
N. [Verification step]

Tools needed:
  - mcp1_adg_health (ADG scope check)
  - mcp5_mem_recall_session_start (session context)
  - read_file / `read_text_file` (server: `filesystem`) (evidence pull)
  - <additional tools justified by plan>

Missing information:
  - <gap 1 — what is unknown>

Risks / stop conditions:
  - <risk 1> → STOP if <condition>
  - <risk 2> → STOP if <condition>
```

**Branching rule:** If uncertainty is high on a step, emit:
```
BRANCH POINT — Step N:
  Plan A: <approach> — use if <condition>
  Plan B: <approach> — use if <condition>
  Plan C: <approach> — use if <condition>
  Waiting for evidence before selecting branch.
```

Do not collapse branches prematurely. If genuinely unclear, invoke Author-Gate via `ask_user_question`.

---

## PHASE C — Evidence Pull & Context Validation

Execute only read/query tool calls. No writes. No edits.

Checklist before proceeding:
- [ ] `mcp1_adg_health` called — status confirmed
- [ ] `mcp5_mem_recall_session_start` called — session context loaded
- [ ] All files relevant to plan read
- [ ] ADG fanout/fanin queried for any cross-file changes
- [ ] Constitutional rules checked (pre-commit hooks, layer constraints)

After evidence pull, emit:

```
## SR_EVIDENCE_SUMMARY
Evidence gathered: <N items>
Plan still valid: YES | NO | PARTIAL
Revision needed: <describe change, or NONE>
Branch selected: <A | B | C | NONE>
Missing gaps resolved: YES | NO — <what remains>
```

If plan is invalid → go back to Phase B with revised plan. Document what changed.
If gaps remain → clarify with user or abstain.

---

## PHASE D — Plan Approval Gate

Emit one of:

```
SR_APPROVAL: APPROVED — proceeding to execution
```
or
```
SR_APPROVAL: REVISED — see SR_PLAN_v2 above
```
or
```
SR_APPROVAL: CLARIFY — [specific question for user]
```
or
```
SR_APPROVAL: ABSTAIN — evidence too weak; recommend [alternative]
```

**Only APPROVED or REVISED (with re-approval) may proceed to Phase E.**

---

## PHASE E — Controlled Execution

Execute the approved plan step by step. For each step:

1. Name the step: `## EXECUTING Step N — <title>`
2. State the tool(s) being used and why
3. Execute the tool call
4. Check result before proceeding to Step N+1
5. Update task status: `update_task` (server: `task_manager`)

**MCP failure rule:** If any MCP hangs or errors:
- STOP that step
- Route around it (document fallback)
- Do NOT retry the same call in a loop
- If ADG MCP fails → run `/mcp-failure-rca` before continuing

**No hidden state:** Every assumption made during execution must be stated explicitly.

---

## PHASE F — Post-Run Verification & Summary

After execution, emit:

```
## SR_SUMMARY
What changed:
  - <file or artifact 1> — <what was done>
  - <file or artifact 2> — <what was done>

What was verified:
  - <test run / health check / manual check>

What remains uncertain:
  - <item 1> — <why uncertain>

Rollback / repair note:
  - <git reset / file restore command if something went wrong>
  - N/A if no destructive changes

Recommended next step:
  - <concrete action>
```

Update task to done: `task_manager` → `update_task` with status=done and lessons learned.

---

## MCP Failure Routing Table

| MCP (YAML name) | Role | Fallback if down |
|-----------------|------|-----------------|
| **adg_sqlite** `adg_health` | Scope/blast radius | Run `/mcp-failure-rca` STEP 1; DO NOT grep |
| **memory** `mem_recall_session_start` | Session context | Proceed; note `[MEMORY UNAVAILABLE]` |
| **task_manager** `create_task` | Step tracking | Use `todo_list` native tool |
| **filesystem** `read_text_file` | File reads | Use `read_file` Windsurf native |
| direct `httpx` in code | External lookup / fetch (the `enhanced_http` MCP was retired 2026-04-27) | Use `read_url_content` native tool for one-off fetches with user approval |
| **gitkraken** `git_status` | Git state | Use `run_command` with git CLI |
| **pytest_mcp** `run_tests` | Test execution | Use `run_command` with pytest CLI |

---

## Tier Applicability

| Task | Tier | Use This Workflow? |
|------|------|--------------------|
| Explain code | T0 | ❌ NO — answer directly |
| Fix typo / add docstring | T1 | ❌ NO — edit directly |
| Debug 2–5 files | T2 | ✅ YES |
| Refactor single layer | T2 | ✅ YES |
| Cross-layer architecture | T3 | ✅ YES — full protocol |
| ADG graph analysis | T3 | ✅ YES |
| New feature > 5 files | T3 | ✅ YES |

---

## Example Invocation

Task: "Refactor the confidence engine to use the new ADG cache layer."

```
/structured-reasoning

## SR_INTAKE
Objective: Replace direct Redis calls in confidence/engine.py with ADG cache layer calls
Constraints:
  - Must not break existing L5 tests
  - Layer boundary L4→L5 must be respected
Assumptions:
  - ADG cache layer is at system_learning/confidence/
  - Redis is currently accessed directly (to be confirmed)
Tier: T2
Complexity: medium

## SR_PLAN
1. Call mcp1_adg_health — confirm ADG MCP is healthy
2. Call mcp5_mem_recall_session_start — load session context
3. Read system_learning/confidence/engine.py
4. Run mcp1_adg_nodes_by_file on engine.py — identify all Redis call nodes
5. Run mcp1_adg_edge_fanout — find downstream dependents
6. Read ADG cache layer interface
7. Draft replacement — swap Redis calls for cache layer calls
8. Run scoped tests: pytest tests/unit/system_learning/confidence/ -q
9. Verify no layer violations introduced

Tools needed: mcp1_adg_health, mcp1_adg_nodes_by_file, mcp1_adg_edge_fanout,
              mcp5_mem_recall_session_start, read_file, pytest_mcp_run_tests

Missing information: None
Risks: Layer inversion if cache layer is at wrong L → STOP if ADG shows violation
```
