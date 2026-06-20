---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\notion-plans-new-status-enforcement-c9f2a3.md'
original_relative_path: '_archive\\2026-05\\notion-plans-new-status-enforcement-c9f2a3.md'
source_sha256: d1b6474844b21700e9eecdb085f20c6dc38dd888371c9b84536a4dbd500ebf88
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: notion-plans-new-status-enforcement-c9f2a3
plan_type: governance
# CI gate enforcement — not a refactor, ADG graph layer evidence skipped per template §5
dod_exempt: false
---

# Notion Plans New-Plan Status Enforcement

CI gate (NP6) to enforce that newly-created plans in Notion Plans DB use canonical status **"Not Started"**, not "Deferred" or "Waiting". Closes semantic gap where `check_notion_plans_status_canonical.py` allows "Deferred" as valid but new plans must never use it.

---

## Context (SCQA)

**Situation:** Notion Plans DB has canonical statuses: In Progress, Not Started, Deferred, Waiting, Completed, Retired, Archived. NP2 gate (`check_notion_plans_status_canonical.py`) blocks stale/emoji statuses (Draft, 🟡Draft) but permits "Deferred" since it's a valid state for intentionally parked work.

**Complication:** RCA-2026-05-10 (`notion-plan-identity-deferred-scope-a3b7e2`) was created with status "Deferred" when it should have been "Not Started". The marker `status=deferred` was passed through. NP2 gate would not catch this — "Deferred" is canonical.

**Question:** How do we automate enforcement that new plans must use "Not Started", while still allowing intentional "Deferred" transitions later?

**Answer:** NP6 gate that inspects `Created time` vs `Last edited time`. If status != "Not Started" AND created within detection window (e.g., 24h), flag as NEW_PLAN_WRONG_STATUS.

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|--------|
| W1 | Gate logic + test | CI gate file | A | ~3k 🟢 |
| W2 | Registration + CI wiring | run_contract_gates.py | B | ~1k 🟢 |

**Total: ~4k tokens across 2 waves, all GREEN**

---

## Out Of Scope

- Modifying existing NP2 gate behavior (separate concern)
- Changing Notion DB schema
- Plan scaffolding logic (addressed by manual marker discipline)
- Backfill of existing plans (detection window intentionally limited)

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.P1 | Gate implementation | 1 new file | GAP-1: detection window logic | ~2k | 🔲 TODO |
| W1.P2 | Unit tests | 1 new test file | GAP-2: mocking Notion API | ~1k | 🔲 TODO |
| W2.P1 | CI registration | 1 edit | PP-1: gate ordering | ~500 | 🔲 TODO |
| W2.P2 | Rule cross-ref | 1 edit | PP-2: rule coherence | ~500 | 🔲 TODO |

---

## Gap Register

**GAP-1: Detection window logic**
Notion API returns `created_time` and `last_edited_time`. For new plans, these are nearly identical. Gate must handle: (a) brand-new plans (created == last_edited), (b) recently created with edits (delta < 24h), (c) intentional "Deferred" transitions (created_time older than window).

**GAP-2: Mocking Notion API**
Tests need deterministic `created_time` injection. Use `freezegun` or timestamp patching.

---

## Definition of Done

| DoD | Criteria | Verification |
|-----|----------|--------------|
| DoD-1 | Gate file exists at `ops_scripts/ci/check_notion_plans_new_status.py` | File on disk + imports without error |
| DoD-2 | Gate emits `NEW_PLAN_WRONG_STATUS` when status != "Not Started" AND created within 24h | Unit test with mocked Notion response |
| DoD-3 | Gate skips rows where created > 24h ago (allows intentional "Deferred") | Unit test with old timestamp |
| DoD-4 | Registered as "NP6 Notion Plans new-plan status (advisory)" in `run_contract_gates.py` | Line present in assurance_gates list |
| DoD-5 | Rule `.cursor/rules/notion-plans-taxonomy.md` cross-references NP6 | Section added with gate invocation |

**Verification vs Deferral:**
| Check | Verified | Deferred |
|-------|----------|----------|
| Gate logic | Unit tests | — |
| Live Notion test | Manual with real token | — |
| Fail-closed mode | Future enhancement | Documented in code only |

---

## Execution Plan

### W1.P1 — Gate Implementation
**Scope:** Create `ops_scripts/ci/check_notion_plans_new_status.py`

**Logic:**
1. Query Plans DB for rows where `Created time >= now() - 24h`
2. For each row, check `Status.select.name`
3. If status != "Not Started", emit violation `NEW_PLAN_WRONG_STATUS`
4. Report to `artifacts/ci/notion_plans_new_status.json`

**Exit codes:**
- 0 = All new plans use "Not Started" (or advisory mode)
- 1 = Violations found (fail-closed mode)

**Bypass:** `NOTION_PLANS_NEW_STATUS_BYPASS=1`

### W1.P2 — Unit Tests
**Scope:** `tests/unit/ops_scripts/ci/test_check_notion_plans_new_status.py`

**Cases:**
- New plan with "Not Started" → pass
- New plan with "Deferred" → violation
- New plan with "Waiting" → violation  
- Old plan (25h) with "Deferred" → pass (outside window)
- API error → fail-open (exit 0)

### W2.P1 — CI Registration
**Scope:** Edit `ops_scripts/ci/run_contract_gates.py`

Add after NP5:
```python
(
    "NP6 Notion Plans new-plan status (advisory)",
    "ops_scripts/ci/check_notion_plans_new_status.py",
),
```

### W2.P2 — Rule Cross-Reference
**Scope:** Edit `.cursor/rules/notion-plans-taxonomy.md`

Add to "Status Taxonomy" section:
> New plans MUST use "Not Started". Enforced by NP6 gate (`check_notion_plans_new_status.py`).

---

## Appendix

**Detection window rationale:** 24 hours balances:
- Catches immediate mis-status from PLAN_CREATED markers
- Allows manual triage where a plan is created then intentionally parked as "Deferred"
- Aligns with CI gate polling frequency (nightly runs)

**Related:**
- RCA-2026-05-10: `notion-plan-identity-deferred-scope-a3b7e2` status error
- Memory: `2fe76ae0-2c34-4a2e-94e4-f8f26d2a04db` (canonical statuses)
- Gate NP2: `check_notion_plans_status_canonical.py` (stale/emoji detection)

---

PLAN_CREATED: slug=notion-plans-new-status-enforcement-c9f2a3 path=.cursor/plans/notion-plans-new-status-enforcement-c9f2a3.md status=Not Started tier=T2 layer=L_OPS
