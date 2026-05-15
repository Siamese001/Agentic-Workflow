---
plan_id: notion-enforcement-consolidation-e8f3a2
plan_type: governance
dod_exempt: false
---

# Notion Enforcement Consolidation and Rectification

Consolidate 40+ fragmented Notion enforcement files into a unified Plan Lifecycle Manager, streamline 13 NP gates to 5, and implement a prevention layer that auto-detects and prompts for unstarted plans.

---

## Context (SCQA)

- **Situation** — Notion enforcement has evolved organically across 15+ plans, resulting in 40+ files (rules, hooks, gates, helpers, CLI tools) spanning 7 architectural layers. The system works but is cognitively unmanageable.

- **Complication** — `plan-complete-marker-enforcement-d2e9f1` was left at `Not Started` despite code-complete implementation. Root cause: no trigger converts "registered plan + user begins work" into `wave_execution_state.py start`. The spaghetti makes omissions invisible.

- **Question** — How do we consolidate enforcement into a debuggable, cohesive system while preserving all existing protections?

- **Answer** — Three-wave rectification: W1) Inventory and deprecation; W2) Unified Lifecycle Manager (UPLM) with consolidated hooks; W3) Prevention layer and gate streamlining.

---

## Evidence Sources

| Source | Why Needed | Status |
|--------|-----------|--------|
| `.cursor/rules/*.md` (7 files) | Current rule surface for consolidation | ✅ inventoried |
| `.cursor/hooks.json` (20+ hooks) | Hook registration and show_output flags | ✅ inventoried |
| `ops_scripts/ci/check_notion*.py` (13 gates) | NP1-NP13 gate functions | ✅ inventoried |
| `.cursor/scripts/post_cursor_agent_*plan*.py` (6 hooks) | Current capture/audit hooks | ✅ inventoried |
| `tools/plan_lifecycle/wave_execution_state.py` | Current CLI entry point | ✅ verified |
| `artifacts/cursor/wave_lifecycle_*.jsonl` | Log of recent activity | ✅ shows d2e9f1 never started |

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | 1.1-1.4 | Inventory finalization + deprecation marking | ~15K | No active plan conflicts | 🔲 | 40-file inventory complete; 6 deprecated files marked |
| W2 | 2.1-2.5 | Unified Plan Lifecycle Manager (UPLM) | ~35K | Wave state format preserved | 🔲 | UPLM module with 5 consolidated gates; 2 hooks vs 11 |
| W3 | 3.1-3.4 | Prevention layer + CI integration | ~20K | Auto-start approved | 🔲 | Pre-flight check auto-prompts; NP gates consolidated |
| W4 | 4.1-4.3 | Tests + DoD verification | ~12K | Test isolation available | 🔲 | 20+ tests pass; zero regressions |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| 1.1 | Inventory table | `docs/reference/notion-enforcement-inventory.md` NEW | Must catalog all 40+ files accurately | ~4K | 🔲 TODO |
| 1.2 | Deprecation marking | 6 files deprecated with `_deprecated_` prefix | Must preserve function while signaling intent | ~3K | 🔲 TODO |
| 1.3 | NP gate redundancy analysis | `docs/reference/np-gate-consolidation-map.md` NEW | Identify which gates can merge safely | ~4K | 🔲 TODO |
| 1.4 | Rule consolidation spec | `notion-plan-lifecycle.md` NEW (replaces 2 rules) | Merge wave-deferral + registration | ~4K | 🔲 TODO |
| 2.1 | UPLM module core | `tools/windsurf/plan_lifecycle_manager.py` NEW | State machine unification is complex | ~10K | 🔲 TODO |
| 2.2 | UPLM CLI integration | `tools/plan_lifecycle/wave_execution_state.py` EDIT | Preserve CLI contract while delegating | ~5K | 🔲 TODO |
| 2.3 | Hook consolidation (post-cursor-agent) | `.cursor/hooks.json` EDIT + 2 new hooks | 7 hooks → 1 unified capture hook | ~8K | 🔲 TODO |
| 2.4 | Hook consolidation (pre-user-prompt) | `.cursor/hooks.json` EDIT + 1 new hook | 4 hooks → 1 unified check hook | ~6K | 🔲 TODO |
| 2.5 | Helper module migration | `_plan_registration.py` → UPLM | Preserve queue format | ~6K | 🔲 TODO |
| 3.1 | Prevention layer core | UPLM `pre_flight_check()` method | Detect unstarted but ready plans | ~6K | 🔲 TODO |
| 3.2 | Auto-start prompt | UPLM `prompt_wave_start()` method | UX: prompt user, don't auto-execute | ~4K | 🔲 TODO |
| 3.3 | NP gate consolidation | 5 new `check_notion_consolidated_*.py` gates | Map NP1-NP13 to 5 without loss | ~7K | 🔲 TODO |
| 3.4 | run_contract_gates.py update | `ops_scripts/ci/run_contract_gates.py` EDIT | Register new gates, deprecate old | ~3K | 🔲 TODO |
| 4.1 | Unit tests for UPLM | `tests/unit/tools/windsurf/test_plan_lifecycle_manager.py` NEW | Cover state machine, transitions | ~5K | 🔲 TODO |
| 4.2 | Integration tests | `tests/integration/test_notion_lifecycle.py` NEW | End-to-end plan creation → completion | ~4K | 🔲 TODO |
| 4.3 | DoD verification | All files | Run test suite + gate sweep | ~3K | 🔲 TODO |

---

## Gap Register

**GAP-1: No unified state view**
- Wave state, registration queue, Notion status are 3 separate systems
- Impact: Impossible to answer "what's the status of plan X?" without querying 3 sources

**GAP-2: No prevention layer**
- User can work on a registered plan indefinitely without starting waves
- Impact: Plans silently accumulate work without lifecycle tracking (d2e9f1)

**GAP-3: Gate overlap and noise**
- NP1 (AI summary), NP3 (status canonical), NP4 (wave freshness), NP12 (plan_complete) overlap in purpose
- Impact: CI noise, maintenance burden, cognitive load

**GAP-4: 11 hooks in post_cursor_agent_response**
- Each hook parses JSON independently, adds latency, increases failure surface
- Impact: Slower response processing, harder debugging

**GAP-5: No canonical "plan status" query**
- Must check `wave_execution_state.py status`, `_plan_registration.py`, and Notion API separately
- Impact: Operational friction, inconsistent status reports

---

## Consolidation Target Architecture

### Unified Plan Lifecycle Manager (UPLM)

```
tools/windsurf/plan_lifecycle_manager.py
├── class PlanLifecycleManager
│   ├── state_machine: UnifiedStateMachine  # Not Started → In Progress → Completed
│   ├── registration_queue: PlanRegistrationQueue  # from _plan_registration.py
│   ├── notion_sync: NotionSyncClient  # from wave_lifecycle_writer.py
│   └── audit_log: LifecycleAuditLog  # unified logging
│
│   # Public API (replaces CLI + hooks)
│   ├── pre_flight_check(plan_slug) -> PreFlightResult
│   ├── start_wave(plan_slug, note=None) -> StartResult
│   ├── log_wave_progress(plan_slug, wave, note=None) -> LogResult
│   ├── complete_plan(plan_slug, note=None) -> CompleteResult
│   ├── capture_markers(response_text) -> list[MarkerAction]
│   └── query_status(plan_slug) -> UnifiedStatus
│
│   # Gate API (replaces NP1-NP13)
│   ├── gate_presence() -> GateResult  # row exists
│   ├── gate_freshness() -> GateResult  # not stale
│   ├── gate_completeness() -> GateResult  # DoD verified
│   ├── gate_compliance() -> GateResult  # AI summary, canonical status
│   └── gate_divergence() -> GateResult  # on-disk vs Notion mismatch
```

### Consolidated Hook Surface

| Old Hooks | New Hook | Function |
|-----------|----------|----------|
| `pre_user_prompt_plan_registration_surface` | `pre_user_prompt_lifecycle_check` | Unified pre-flight check + prevention layer |
| `pre_user_prompt_plan_registration_refresh` | *(merged)* | Cache refresh inside unified hook |
| `pre_user_prompt_plans_dup_surface` | *(merged)* | Dup detection inside unified hook |
| `post_cursor_agent_plan_registration_capture` | `post_cursor_agent_lifecycle_capture` | Unified marker capture |
| `post_cursor_agent_wave_lifecycle_capture` | *(merged)* | Wave markers captured by unified hook |
| `post_cursor_agent_plan_complete_audit` | *(merged)* | PLAN_COMPLETE checked by unified hook |
| `post_cursor_agent_notion_plans_status_audit` | *(merged)* | Status audit by unified hook |
| `post_cursor_agent_notion_plan_identity_audit` | *(merged)* | Identity audit by unified hook |
| `post_cursor_agent_plans_dup_audit` | *(merged)* | Dup audit by unified hook |

**Result: 11 hooks → 2 hooks**

### Consolidated Gate Surface (NP1-NP13 → NP-5)

| Old Gates | New Gate | Function |
|-----------|----------|----------|
| NP1 (AI summary) | NP-COMPLIANCE | AI summary + canonical status + schema compliance |
| NP3 (status canonical) | *(merged)* | |
| NP4 (wave freshness) | NP-FRESHNESS | Staleness + activity detection |
| NP12 (plan_complete marker) | *(merged into NP-COMPLETENESS)* | |
| NP13 (marker freshness) | NP-COMPLETENESS | PLAN_COMPLETE + DoD verification |
| NP2 (status drift) | NP-DIVERGENCE | On-disk vs Notion mismatch detection |
| NP-duplicates | NP-PRESENCE | Row existence + uniqueness |

**Result: 13 gates → 5 gates**

---

## Prevention Layer Specification

### Pre-Flight Check Logic

```python
def pre_flight_check(plan_slug: str) -> PreFlightResult:
    """Called at every user prompt for the active plan."""
    
    # 1. Check wave execution state
    wave_state = get_wave_state(plan_slug)
    
    # 2. Check registration
    registration = check_registration(plan_slug)
    
    # 3. Check Notion status
    notion_status = query_notion_status(plan_slug)
    
    # 4. Detect unstarted-but-ready
    if (
        wave_state is None  # No active wave
        and registration.registered  # Row exists
        and notion_status == "Not Started"  # Notion agrees
        and plan_has_work(plan_slug)  # Has tasks/todos
    ):
        return PreFlightResult(
            status=PlanStatus.UNSTARTED_BUT_READY,
            action=RecommendedAction.PROMPT_START,
            message=f"Plan {plan_slug} is registered but waves not started. Start now?"
        )
    
    return PreFlightResult(status=PlanStatus.OK)
```

### Auto-Start Prompt (Author-Gate Style)

When `PROMPT_START` is recommended:

```
[PLAN_LIFECYCLE] Plan 'd2e9f1' is registered and has work in progress, but wave execution has not started.

Recommended action: Start wave execution now?
[Yes - Start waves]  [No - Continue without tracking]  [Defer - Remind next prompt]
```

**Governance**: This is a convenience prompt, not an architectural decision. No Author-Gate required per constitutional §6 (single correct path: tracking is better than not tracking).

---

## Execution Plan

### Phase 1.1 — Inventory Documentation

**Scope**: `docs/reference/notion-enforcement-inventory.md`

Create comprehensive inventory table:
```markdown
| File | Layer | Purpose | Consolidation Target | Deprecation |
|------|-------|---------|---------------------|-------------|
| _wave_execution_state.py | L2 | Wave state persistence | UPLM state_machine | Mark deprecated |
| ... | ... | ... | ... | ... |
```

### Phase 1.2 — Deprecation Marking

Mark 6 files with `_deprecated_` prefix:
- `_deprecated_wave_execution_state.py` (function merged to UPLM)
- `_deprecated_plan_registration.py` (function merged to UPLM)
- `_deprecated_notion_plans_status_check.py` (function merged to UPLM)
- `_deprecated_plans_dup_detector.py` (function merged to UPLM)
- Plus 3 redundant post-cursor-agent hooks

### Phase 2.1 — UPLM Core Module

**Scope**: `tools/windsurf/plan_lifecycle_manager.py`

Implement `PlanLifecycleManager` class with:
- Unified state machine (Not Started → In Progress → Completed)
- Integration with existing registration queue format
- Integration with existing wave_lifecycle_writer
- Fail-soft behavior preserved

### Phase 2.2 — CLI Preservation

**Scope**: `tools/plan_lifecycle/wave_execution_state.py` EDIT

Preserve CLI interface but delegate to UPLM:
```python
def main():
    # CLI parsing unchanged
    # Delegate to UPLM
    from plan_lifecycle_manager import PlanLifecycleManager
    manager = PlanLifecycleManager()
    result = manager.start_wave(args.plan, note=args.note)
    # Exit codes preserved
```

### Phase 2.3 — Post-Cursor-Agent Hook Consolidation

**Scope**: New `.cursor/scripts/post_cursor_agent_lifecycle_capture.py`

Single hook that:
1. Parses all markers (PLAN_CREATED, WAVE_START, WAVE_COMPLETE, PHASE_COMPLETE, PLAN_COMPLETE)
2. Delegates to UPLM for processing
3. Logs unified audit entry

Update `.cursor/hooks.json` to register single hook, remove 7 old hooks.

### Phase 3.1 — Prevention Layer Implementation

**Scope**: UPLM `pre_flight_check()` method

Implement detection logic for unstarted-but-ready plans.

### Phase 3.2 — Auto-Start Prompt

**Scope**: UPLM `prompt_wave_start()` + `pre_user_prompt_lifecycle_check.py`

Implement user prompt (not auto-execution) for starting waves on ready plans.

### Phase 3.3 — NP Gate Consolidation

**Scope**: 5 new consolidated gates in `ops_scripts/ci/`

Create:
- `check_notion_presence.py` (NP-PRESENCE)
- `check_notion_freshness.py` (NP-FRESHNESS)
- `check_notion_completeness.py` (NP-COMPLETENESS)
- `check_notion_compliance.py` (NP-COMPLIANCE)
- `check_notion_divergence.py` (NP-DIVERGENCE)

### Phase 3.4 — run_contract_gates.py Update

**Scope**: `ops_scripts/ci/run_contract_gates.py` EDIT

Register new gates, mark old gates as deprecated in comments.

### Phase 4.1-4.3 — Tests and DoD

Standard test and verification phases.

---

## Definition of Done

| # | Criterion | Verification | Status |
|---|-----------|--------------|--------|
| DoD-1 | 40-file inventory documented | `docs/reference/notion-enforcement-inventory.md` exists and is complete | 🔲 |
| DoD-2 | UPLM module functional | `python -c "from tools.windsurf.plan_lifecycle_manager import PlanLifecycleManager; m = PlanLifecycleManager(); print('OK')"` exits 0 | 🔲 |
| DoD-3 | 11 hooks consolidated to 2 | `grep -c "post_cascade.*plan\|pre_user_prompt.*plan" .cursor/hooks.json` returns 2 | 🔲 |
| DoD-4 | 13 NP gates consolidated to 5 | `grep -c "NP.*notion\|notion.*NP" ops_scripts/ci/run_contract_gates.py` returns 5 | 🔲 |
| DoD-5 | Prevention layer catches unstarted plans | Test: create plan, don't start waves, verify prompt appears | 🔲 |
| DoD-6 | Zero regressions in existing plans | `pytest tests/unit/tools/windsurf/ -v` passes | 🔲 |

**Verification-vs-Deferral table**:

| Item | Why Deferred | Tracked In |
|------|--------------|------------|
| Full NP gate deletion (vs deprecation) | Need 30-day deprecation window per policy | `docs/reference/deprecation-schedule.md` (deferred) |
| Old hook removal (vs just registration removal) | Keep files for 30 days for rollback | This plan §1.2 |
| UPLM metrics/monitoring | Observability enhancement, not core function | NEXT_STEP marker |
| Batch migration of existing plans | No functional impact; gradual adoption | Not tracked — organic adoption |

---

## Rules

- UPLM must preserve all existing fail-soft behavior (exit 0 on errors)
- CLI interfaces (`wave_execution_state.py`) must remain backward compatible
- Registration queue format must not change (preserve `.cursor/state/plan_registration_queue.jsonl` format)
- Consolidation must not lose coverage — each NP gate's unique check must map to a consolidated gate
- Prevention layer must prompt, not auto-execute (user confirmation required)
- All deprecated files must keep `_deprecated_` prefix for 30 days before deletion
- hooks.json edits must re-read file before editing (precedent: NP10 hooks.json corruption incident)

---

## Non-Goals

- Changing Notion database schema
- Modifying wave_lifecycle_writer.py processing logic (machinery is correct)
- Adding new status values to Plans DB
- Breaking changes to plan file format
- Real-time bidirectional sync (Notion → on-disk)

---

PLAN_CREATED: slug=notion-enforcement-consolidation-e8f3a2 path=.cursor/plans/notion-enforcement-consolidation-e8f3a2.md status=Not Started
