---
name: scope-containment
description: Use when managing scope boundaries, retrieval discipline, cross-turn topic transitions, or applying scope-containment procedures.
trigger: model_decision
---

# Scope Containment Skill

Procedural execution guide for the `scope-containment` always-on rule. Use this skill when:
- Determining in-scope vs out-of-scope boundaries
- Managing cross-turn topic transitions
- Applying retrieval discipline caps
- Deciding whether to emit `NEXT_STEP:` or `SCOPE_RESET:` markers

## When to Use

- **In scope**: files user named; files in plan `Files In Scope`; files required for compile/type-check/pass tests
- **Out of scope**: files only discovered via `grep_search`/`code_search` (read-only, never edit); unrelated anti-pattern/formatting touches; doc updates unless requested

## Retrieval Discipline

| Cap | Limit | Audit Hook | Bypass |
|-----|-------|------------|--------|
| `grep_search` + `code_search` | 3/response | `post_agent_grep_budget_audit.py` | `GREP_BUDGET_BYPASS=1` |
| File reads (native + MCP) | 10/response | `post_agent_read_budget_audit.py` | `READ_BUDGET_BYPASS=1` |

**Rule**: Read named files; don't grep "to be sure". Plan names files → read directly.  
**ADG > grep**: Never grep "who imports X / what depends on Y". Use `adg_edge_fanin` / `adg_edge_fanout`.

## Scope-Reset Marker (Cross-Turn Topic Transitions)

When user shifts to different module/layer/concern, emit before any tool call:

```
SCOPE_RESET: from=<prior-scope> to=<new-scope> dropped=<files-or-topics>
```

**Triggers**: different top-level dir; different layer (L0→L4) or app (apps_qna→apps_rg); different task type (refactor→debug→plan); explicit "new task" / "switch to".

**Do NOT emit for**: natural continuations ("now W2", "verify that", "fix the typo").

## Summarize-Before-Return

After `code_search` or multi-file `grep_search`, state retained paths and discard chunks:

```
[After code_search] Retained: <path1>, <path2>. Discarded: chunk contents (will read targeted files if needed).
```

Chunks served their purpose (locating files); paths are the durable artifact.

## Escape Hatches

| Situation | Action |
|-----------|--------|
| User approved expansion | Proceed ("yes, also fix Y") |
| Transitive requirement | State requirement inline before editing |
| Emergency rollback | Constitutional §7 auto-closure |
| Scripted batch | `SCOPE_CONTAINMENT_BYPASS=1` — logs bypass row |

## Markers Reference

| Marker | Use When | Captured By |
|--------|----------|-------------|
| `NEXT_STEP:` | Optional follow-up ideas, out-of-scope improvements | `post_agent_next_step_capture.py` |
| `SCOPE_RESET:` | Cross-turn topic transitions | This rule |
| `DEFERRED_SCOPE:` | Wave/phase descoping decisions | `post_agent_deferred_scope_capture.py` |

## Enforcement Layer Mapping

| Layer | Component |
|-------|-----------|
| Composition | `scope-containment.md` rule (always_on, advisory) |
| Text-search cap | `post_agent_grep_budget_audit.py` → `artifacts/governance/grep_budget_violations.jsonl` |
| File-read cap | `post_agent_read_budget_audit.py` → `artifacts/governance/read_budget_violations.jsonl` |
| Token telemetry | `post_agent_token_telemetry.py` → `artifacts/governance/turn_budget.jsonl` |
| Out-of-scope ideas | out-of-scope work → native `spawn_task` (constitutional §24) |
| Topic transitions | `SCOPE_RESET:` marker |

## References

- Rule: `.claude/rules/scope-containment.md` (invariants)
- Sibling: constitutional §24 (native `spawn_task`)
- Constitutional: §18 (no hidden scope expansion), §28 (ADG over grep), §31 (SSOT folder routing)
