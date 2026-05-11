# Holistic Plan: Prevent Wrong Plan Status at Creation

> Systemic fix for "In Progress" vs "Not Started" status misclassification — prevention, detection, and enforcement.

---

## Context (SCQA)

- **Situation** — Plan `notion-integration-consistency-audit-b2c4d8` was created with Status="In Progress" instead of "Not Started". Root cause: Cascade (the AI) mistakenly used wrong status in `API-post-page` call. This is a recurring pattern — manual plan creation via MCP calls is error-prone.
- **Complication** — Multiple paths can create plans: Cascade direct MCP calls, `wave_execution_state.py start`, retrospective plan creation, scripted batch creation. Each path has different status semantics. No automated validation exists to catch wrong initial status.
- **Question** — How do we ensure EVERY new plan starts as "Not Started" regardless of creation path, with automated detection and correction if wrong?
- **Answer** — Multi-layer defense: (1) Canonical creation helper that enforces correct status, (2) Pre-flight validation gate, (3) Post-creation audit hook, (4) CI gate for drift detection, (5) Documentation + template updates.

---

## Root Cause Deep Dive

### Why Status Errors Happen

| Creation Path | Current Behavior | Risk |
|-------------|-----------------|------|
| **Cascade direct MCP** | Manual `API-post-page` with hardcoded Status | High — developer (AI) can choose wrong value |
| **`wave_execution_state.py start`** | Flips to "In Progress" correctly | Low — designed for this |
| **Retrospective plan (same-turn)** | Created "Completed" correctly | Low — special case handled |
| **Scripted batch** | Depends on script implementation | Medium — may copy wrong pattern |

### The Core Issue

No **single canonical helper** exists for plan creation. Each caller constructs their own `API-post-page` payload, leading to inconsistency.

---

## Wave Structure

| Wave | Phase IDs | Focus | Status |
|------|-----------|-------|--------|
| W1 | 1.1-1.4 | Canonical creation helper + pre-flight gate | 🔲 TODO |
| W2 | 2.1-2.4 | Post-creation audit hook + auto-correction | 🔲 TODO |
| W3 | 3.1-3.3 | CI gate for status drift detection | 🔲 TODO |
| W4 | 4.1-4.3 | Documentation + template + rule updates | 🔲 TODO |
| W5 | 5.1-5.2 | Rollout verification + backfill | 🔲 TODO |

**Total: 5 waves, ~30K tokens**

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| 1.1 | Create `tools/notion/plan_creation_helper.py` | New canonical helper | Must handle all creation patterns (new, retrospective, batch) | ~4K | 🔲 |
| 1.2 | Add `_enforce_not_started_status()` validation | Helper internal validation | Reject any status other than "Not Started" at creation time | ~2K | 🔲 |
| 1.3 | Create `pre_notion_plan_creation_gate.py` | Pre-flight hook | Block non-canonical plan creation attempts | ~3K | 🔲 |
| 1.4 | Register gate in `hooks.json` | `.windsurf/hooks.json` | Ensure gate runs before any Notion MCP write | ~1K | 🔲 |
| 2.1 | Create `post_cascade_plan_creation_audit.py` | Post-creation hook | Verify created plan has correct status | ~3K | 🔲 |
| 2.2 | Add auto-correction logic | Audit hook extension | If wrong status detected, emit correction patch | ~3K | 🔲 |
| 2.3 | Add `PLAN_CREATED_MARKER:` validation | Hook enhancement | Ensure marker matches Notion row state | ~2K | 🔲 |
| 2.4 | Create alert/logging for manual intervention | Audit hook | Log cases where auto-correction fails | ~2K | 🔲 |
| 3.1 | Create `check_notion_plan_status_initial.py` | New CI gate | Query Plans DB for recent creations, validate status | ~4K | 🔲 |
| 3.2 | Add "recent plans" detection logic | Gate implementation | Time-windowed check (last 7 days) | ~2K | 🔲 |
| 3.3 | Register gate in `run_contract_gates.py` | Gate registration | NP-series gate slot | ~1K | 🔲 |
| 4.1 | Update `plan-location.md` rule | Rule edit | Add "Status must be Not Started at creation" invariant | ~2K | 🔲 |
| 4.2 | Update `execution-plan-template.md` | Template edit | Add Status discipline note in frontmatter guidance | ~1K | 🔲 |
| 4.3 | Update AGENTS.md Auto-Routing Rules | AGENTS.md edit | Document canonical creation path | ~2K | 🔲 |
| 5.1 | Backfill check: scan all existing plans | One-off script | Identify any other wrongly-created plans | ~3K | 🔲 |
| 5.2 | Verification: end-to-end test | Integration test | Create plan via helper, verify status, verify gates pass | ~3K | 🔲 |

---

## Execution Plan

### Wave 1 — Canonical Creation Helper + Pre-Flight Gate

**Phase 1.1 — Create `tools/notion/plan_creation_helper.py`**

Single SSOT helper for ALL plan creation. Enforces:
- Status MUST be "Not Started" (no exceptions)
- Slug validation (kebab-case-6hex pattern)
- Required fields: Slug, Status, Exists On Disk=true, Plan File Path, Summary, AI Summary
- Fail-closed: any validation error → no API call

**Signature:**
```python
def create_plan_in_notion(
    slug: str,
    summary: str,
    ai_summary: str,
    plan_file_path: str = ".windsurf/plans/{slug}.md",
    # Optional: override for special cases (retrospective completed plans)
    force_status: Literal["Not Started", "Completed"] | None = None,
) -> dict:
    """
    Canonical plan creation. Default status="Not Started".
    
    force_status="Completed" only for retrospective plans created-and-completed
    in same session. All other cases use "Not Started".
    """
```

**Phase 1.2 — Add `_enforce_not_started_status()`**

Internal validation that raises `ValueError` if:
- Status is "In Progress" (creation-time error)
- Status is "Waiting" (creation-time error)
- Status is any non-canonical value

**Phase 1.3 — Create `pre_notion_plan_creation_gate.py`**

Pre-flight hook that intercepts Cascade responses containing `API-post-page` targeting Plans DB.

Checks payload BEFORE Notion call:
- If Status != "Not Started" → BLOCK with error message
- If missing required fields → BLOCK
- Bypass: `NOTION_PLAN_CREATION_GATE_BYPASS=1` (logged)

**Phase 1.4 — Register in `hooks.json`**

Add to `pre_mcp_tool_use` or `pre_cascade_response` chain (depending on injection point).

### Wave 2 — Post-Creation Audit + Auto-Correction

**Phase 2.1 — Create `post_cascade_plan_creation_audit.py`**

Post-cascade hook that:
1. Scans response for successful `API-post-page` to Plans DB
2. Extracts created page ID and status from response
3. Validates status is correct for creation context

**Phase 2.2 — Add auto-correction**

If audit detects wrong status:
- Immediately emit `API-patch-page` to correct status
- Log correction to `artifacts/windsurf/plan_status_corrections.jsonl`
- If correction fails, escalate to user notification

**Phase 2.3 — `PLAN_CREATED_MARKER:` validation**

Ensure marker emission matches actual Notion state:
- If marker says `PLAN_CREATED:` but status is "In Progress" → discrepancy flagged
- Enforce marker/Notion consistency

**Phase 2.4 — Alert/logging**

For cases where auto-correction fails (e.g., API error):
- Log to `artifacts/windsurf/plan_creation_alerts.jsonl`
- Include payload, error, recommended manual fix

### Wave 3 — CI Gate for Drift Detection

**Phase 3.1 — Create `check_notion_plan_status_initial.py`**

CI gate (NP-series) that:
1. Queries Notion Plans DB for plans created in last 7 days
2. Checks each has Status="Not Started" OR "Completed" (retrospective OK)
3. Flags any "In Progress" or "Waiting" as creation-time error

**Phase 3.2 — Recent plans detection**

Use `created_time` filter in Notion API query:
```python
filter: {
    "timestamp": "created_time",
    "created_time": {"after": "2026-05-11T00:00:00Z"}
}
```

**Phase 3.3 — Register in `run_contract_gates.py`**

Add as "NP-INIT Notion plan initial status (advisory)" in assurance_gates.

### Wave 4 — Documentation + Rules

**Phase 4.1 — Update `plan-location.md`**

Add invariant section:
```
## Plan Status Discipline

> ⛔ **At creation time, Status MUST be "Not Started".**
>
> The only exception is retrospective plans completed in the same session,
> which use Status="Completed".
>
> "In Progress" is FORBIDDEN at creation time — it can only be set via
> `wave_execution_state.py start` or `WAVE_START` marker after creation.
```

**Phase 4.2 — Update `execution-plan-template.md`**

Add to frontmatter guidance:
```yaml
---
# Plan creation checklist:
# [ ] Status = "Not Started" (mandatory)
# [ ] AI Summary populated (mandatory)
# [ ] Plan file exists on disk (mandatory)
---
```

**Phase 4.3 — Update AGENTS.md**

Document canonical creation path:
```
| Create new plan | `.windsurf/plans/<slug>.md` | Use `tools/notion/plan_creation_helper.py` — enforces Status="Not Started" |
```

### Wave 5 — Rollout + Backfill

**Phase 5.1 — Backfill scan**

Script to identify any existing plans with wrong creation status:
```python
# Query all Plans DB rows
# Filter: Status IN ("In Progress", "Waiting") AND created_time > 2026-01-01
# Check if these should be "Not Started"
# Generate report for manual review
```

**Phase 5.2 — End-to-end verification**

Test the full stack:
1. Create plan via helper → Verify Status="Not Started"
2. Run pre-flight gate → Verify no blocks
3. Check post-creation audit → Verify no corrections needed
4. Run CI gate → Verify passes
5. Emit `WAVE_START` → Verify flips to "In Progress"
6. Emit `PLAN_COMPLETE` → Verify flips to "Completed"

---

## Definition of Done

| # | Criterion | Verification | Status |
|---|---|---|---|
| DoD-1 | `plan_creation_helper.py` exists and enforces "Not Started" | Unit test: rejects wrong status | 🔲 |
| DoD-2 | Pre-flight gate blocks wrong status at creation time | Integration test: gate fires, blocks bad payload | 🔲 |
| DoD-3 | Post-creation audit auto-corrects wrong status | Test: create with wrong status → audit patches → verify correction | 🔲 |
| DoD-4 | CI gate detects drift in recent plans | Test: create plan with wrong status → gate flags in next run | 🔲 |
| DoD-5 | All documentation updated (plan-location, template, AGENTS) | `grep` verification for invariant language | 🔲 |
| DoD-6 | Backfill scan complete — any existing wrong-status plans identified | Report generated, manual fixes applied | 🔲 |
| DoD-7 | End-to-end test passes | Full workflow verification | 🔲 |
| DoD-8 | Plan registered in Notion | Plans DB row Status="Completed" | 🔲 |

---

## Non-Goals

- ❌ Change working Plans DB automation (wave lifecycle, registration)
- ❌ Modify wave_execution_state.py behavior
- ❌ Change "In Progress" semantics (it's correct for active work)
- ❌ Add new Notion databases
- ❌ Remove existing gates — only add new ones

---

## Success Criteria

After this plan completes:
- **Zero** new plans created with wrong initial status
- **100%** of plan creations use canonical helper
- **<100ms** overhead for pre-flight gate
- Auto-correction resolves 95%+ of any residual errors without human intervention

---

## Risk Assessment

| Risk | Mitigation |
|---|---|
| Pre-flight gate too strict → blocks legitimate creations | Bypass env var + advisory-only mode for first 7 days |
| Auto-correction creates notification spam | Rate-limit: max 1 correction alert per hour |
| Backfill finds many existing errors | Batch correction script + human review for edge cases |
| Helper doesn't handle all creation patterns | Extensible design: `force_status` param for edge cases |

---

## Verification-vs-Deferral

| Item | Verified This Plan | Deferred |
|---|---|---|
| Canonical helper | ✅ | — |
| Pre-flight gate | ✅ | — |
| Post-creation audit | ✅ | — |
| CI gate | ✅ | — |
| Documentation | ✅ | — |
| Backfill scan | ✅ | — |
| Helper adoption across all creation paths | — | ✅ Requires ongoing enforcement |
| Legacy plan cleanup | — | ✅ Manual review if >10 found |
