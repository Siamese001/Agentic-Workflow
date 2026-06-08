---
name: plan-governance
description: Plan lifecycle procedures — registration, scope authorization, wave/deferral markers, Notion identity verification, backlog linkage. Invoke for plan creation, wave execution, scope expansion, or Plans/Backlog Notion writes. Invariants remain in plan-location.md and notion-plans-taxonomy.md; Notion MCP routing in mcp-integration §7.
metadata:
  enforcement_layer: cursor
  enforcement_timing: before_work
  enforcement_type: procedural
---

# Plan Governance (Tier 2 procedural SSOT)

> **Invariants (glob/on-demand rules):** `plan-location.md` (path, format floor, Notion status discipline), `plan-update-enforcement.md` (authorization invariant), `notion-plans-taxonomy.md` (status taxonomy).  
> **Notion MCP:** `mcp-integration` SKILL §7 · workspace map in `AGENTS.md`.

---

## 1. Plan Registration (§36)

### Invariant
Every `plans/<slug>-<6hex>.md` (legacy: `.claude/plans/<slug>-<6hex>.md`) MUST have a Notion Plans DB row before wave execution.

### Required Marker
When creating a plan:
```
PLAN_CREATED: slug=<slug-6hex> path=plans/<slug>-<6hex>.md status=Not Started|In Progress
```

### Chokepoint Block
`tools/cursor/wave_execution_state.py start` refuses unregistered plans:
```
BLOCKED: plan <slug> not registered in Notion Plans DB.
Required: API-post-page into Plans DB
Bypass: PLAN_REGISTRATION_BYPASS=1
```

### Query Before Claim
> Claude Code MUST NOT assert registration status without live `API-query-data-source` call in same response.

### Consolidated wave summary at top (PLAN-WAVE-TOP)

After Context (SCQA), every execution plan MUST include:

1. `## Status Tables`
2. `### Wave Progress` with canonical wave table (Wave, Focus, Status minimum)
3. Table **before** the first `## Wave N` detail section

Enforcement: `check_plan_wave_summary_top.py` (advisory repo scan), `check_plan_format_compliance.py` (strict per path), `after_file_edit` hook (warn; `PLAN_WAVE_SUMMARY_TOP_HOOK_STRICT=1` blocks), `post_agent_plan_wave_summary_audit.py`.

---

## 2. Plan Update Authorization (Scope Expansion)

### Four-Step Discipline

```
Step 1: DISCOVERED_SCOPE marker   — Document before any work
Step 2: AUTHORIZATION_DECISION     — ACCEPTED / DEFERRED / SPLIT / REJECTED
Step 3: Plan file updates          — Tables, DoD, last_updated
Step 4: SCOPE_EXPANSION marker     — Execute only after Step 3
```

### Markers

**Discovery** (before any new work):
```
DISCOVERED_SCOPE: plan=<slug> wave=<N> phase=<M> gap="<description>" impact="<severity>"
```

**Authorization** (same response as discovery):
```
AUTHORIZATION_DECISION: plan=<slug> decision=ACCEPTED|DEFERRED|SPLIT_TO_NEW_PLAN|REJECTED authorized_by=<user|author_gate|self> decisive_reason="<justification>"
```

**Expansion** (after all updates complete):
```
SCOPE_EXPANSION: plan=<slug> reason="<summary>" added="<waves/phases/gaps>" authorized="yes"
```

### Decision Semantics

| Decision | When | Plan Update | Continues? |
|----------|------|-------------|------------|
| ACCEPTED | Critical-path, in-charter | Yes — all updates | On expanded scope |
| DEFERRED | Time/volume gated | No — emit DEFERRED_SCOPE | Original only |
| SPLIT_TO_NEW_PLAN | Too large | No — new plan | Original only |
| REJECTED | Gold-plating/off-charter | No | Original only |

---

## 3. Wave Execution & Deferral

### Notion Wave Deferral Protocol

> ⛔ **During multi-wave execution: NO Notion MCP calls. Defer ALL writes until final wave completes.**

**Wave lifecycle via direct HTTP** (sanctioned non-MCP path):
1. **Wave 1 start**: `wave_execution_state.py start --plan <slug>` → Status=`In Progress`
2. **During execution**: NO MCP writes (blocked by `pre_mcp_gate.check_notion_wave_deferral()`)
3. **After each wave**: `wave_execution_state.py wave-progress --wave N` → Summary append
4. **Final wave**: `wave_execution_state.py complete` → Status=`Completed`
5. **Post-completion**: Batch MCP writes one-per-block

### Required Markers

```
WAVE_COMPLETE: plan=<slug-6hex> wave=<N> note="<files>, <tests>, <scope>"
PHASE_COMPLETE: plan=<slug-6hex> phase=<id> note="<one-liner>"
PLAN_COMPLETE: plan=<slug-6hex> note="<final outcome>"
```

### Retrospective Plans

> ⛔ **NEVER call `wave_execution_state.py start` on retrospective plans.**

**Correct protocol**:
1. Write plan to `plans/<slug>.md`
2. Register via `API-post-page` with `status=Completed`
3. Emit `PLAN_COMPLETE: plan=<slug>`
4. Do NOT emit `PLAN_CREATED:`

---

## 4. Plan Identity Verification

When targeting Notion plan pages, **query by slug before `API-patch-page`**. Re-query if page ID is from memory >5 min or another session.

See `notion-plan-identity-verification.md` for the invariant; use `tools/notion/` helpers where available.

---

## 5. Backlog-Plan Linkage

Every Backlog Items row MUST have (a) `Plan` relation OR (b) non-empty `Plan File` slug. Fix via `tools/notion/backfill_backlog_plan_relation.py` then `apply_orphan_disposition.py` if needed.

---

## 6. Supersession (auto-retire predecessors)

When a plan replaces an earlier one, declare it in a `## Supersedes` table (and/or `supersedes:` frontmatter). Each named predecessor still in a non-terminal Notion status is auto-flipped to `Retired` — with a dated `Summary` note **and** a posted comment linking the successor — by the post-agent hook `post_agent_plan_supersession_retire.py`. CI sweep gate `check_plan_supersession_consistency.py` (PLAN-SUPERSEDE) backstops cross-session/cross-worktree/Notion-only misses. Net-new plans declare `_None — net-new plan._`. Engine SSOT: `.claude/governance/scripts/_plan_supersession.py`. Grammar + invariant: `notion-plans-taxonomy.md`.

---

## Bypass Reference

| Bypass | Effect |
|--------|--------|
| `PLAN_REGISTRATION_BYPASS=1` | Skip wave-start block |
| `SCOPE_AUTHORIZATION_BYPASS=1` | Skip update auth checks |
| `PLAN_SUPERSESSION_RETIRE_BYPASS=1` | Disable supersession auto-retire hook |
| `PLAN_SUPERSESSION_GATE_BYPASS=1` | Skip PLAN-SUPERSEDE CI sweep |
| `NOTION_WAVE_DEFERRAL_BYPASS=1` | Allow MCP mid-wave (reads only) |
| `NOTION_PLAN_IDENTITY_BYPASS=1` | Skip ID verification (debug) |
| `PLAN_WAVE_SUMMARY_TOP_BYPASS=1` | Skip PLAN-WAVE-TOP CI gate |
| `PLAN_WAVE_SUMMARY_TOP_FAIL_CLOSED=1` | PLAN-WAVE-TOP fails CI on violations |
| `PLAN_WAVE_SUMMARY_TOP_HOOK_STRICT=1` | `afterFileEdit` blocks non-compliant plan edits |
| `PLAN_WAVE_SUMMARY_TOP_AUDIT_BYPASS=1` | Skip post-agent wave-summary audit |
