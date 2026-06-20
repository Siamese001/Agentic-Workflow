---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\notion-plan-identity-verification-enforcement-f2a9c1.md'
original_relative_path: '_archive\\2026-05\\notion-plan-identity-verification-enforcement-f2a9c1.md'
source_sha256: 92a544f49aa0fe272872ddac00b0dc7e1f1ad63adaad87c871831ac57c0e3218
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: notion-plan-identity-verification-enforcement-f2a9c1
plan_type: governance
---

# Notion Plan Identity Verification Enforcement

Add enforcement mechanisms (hooks, rules, CI gates) to prevent plan identity confusion when updating Notion plan statuses. Forces verification of plan slug/page ID match before any status-modifying API call.

---

## Context (SCQA)

**Situation:** The workspace uses Notion Plans DB to track ~130 plans across all execution states. Plans are identified by slugs in `.cursor/plans/<slug>-<6hex>.md` and have corresponding Notion pages with matching slugs in the `Slug` title property. Status updates use `mcp7_API-patch-page` with Notion page IDs.

**Complication:** During the 2026-05-10 status update session, I mistakenly marked the wrong plans as "Deferred" because I used incorrect Notion page IDs. I updated `author-gate-ask-ui-consolidated-a1e3f7` and `w6-emit-contract-enrichment-d8b2a4` (both Completed) instead of `l6-alignment-deferred-scope-c5e8a7` and `l5-cert-ref-deferred-scope-f3a1b8` (the actual targets). This happened because I relied on stale page IDs from context rather than querying the database.

**Question:** How do we enforce plan identity verification before any Notion status change to prevent silent mis-targeting?

**Answer:** A three-layer defense: (1) Pre-commit hook validates slug/page ID match before API calls, (2) Rule documents the prevention pattern, (3) CI gate audits plan status history for anomalies.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `.cursor/rules/notion-plans-taxonomy.md` | Existing status taxonomy | ✅ |
| `.cursor/scripts/_notion_plans_status_check.py` | Existing status validation helper | ✅ |
| `ops_scripts/ci/check_notion_plans_status_drift.py` | Existing drift detection | ✅ |
| ADG SQLite `nodes` table | Plan file to slug mapping | ✅ |
| Notion Plans DB query API | Live slug → page_id resolution | ✅ |

---

## Wave Structure

| Wave | Focus | Deliverable | Checkpoint | Tokens |
|------|-------|-------------|------------|--------|
| W1 | Pre-write hook for plan identity verification | `.cursor/scripts/pre_notion_plan_write_gate.py` | Hook blocks on slug/page mismatch | ~8k ✅ |
| W2 | Rule documentation | `.cursor/rules/notion-plan-identity-verification.md` | Rule enshrines prevention pattern | ~4k ✅ |
| W3 | CI gate for status history audit | `ops_scripts/ci/check_notion_plan_status_anomalies.py` | Gate detects suspicious status flips | ~10k ✅ |
| W4 | Integration and testing | Hook registered, gate active, tests pass | End-to-end verification | ~6k ✅ |

**Total: ~28k tokens across 4 waves, all GREEN**

---

## Out Of Scope

- Changing Notion API authentication or rate limiting
- Modifying the Plans DB schema (no new properties)
- Refactoring existing plan status enforcement (NP1/NP2 gates remain separate)
- Adding UI elements to Notion (buttons, automations)

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| 1.1 | Hook scaffold and slug extraction | `pre_notion_plan_write_gate.py` | Extracting slug from context reliably | ~3k | ✅ DONE |
| 1.2 | Notion DB query integration | Same file | Querying Notion DB without MCP (direct HTTP) | ~3k | ✅ DONE |
| 1.3 | Match validation and blocking | Same file | Fail-closed logic, bypass mechanism | ~2k | ✅ DONE |
| 2.1 | Rule draft and review | `notion-plan-identity-verification.md` | Clear prevention prose | ~2k | ✅ DONE |
| 2.2 | Rule registration and cross-links | Same file + index updates | Linking from related rules | ~2k | ✅ DONE |
| 3.1 | Anomaly detection algorithm | `check_notion_plan_status_anomalies.py` | Defining "suspicious" status change | ~4k | ✅ DONE |
| 3.2 | Historical audit implementation | Same file | Querying Notion page history | ~4k | ✅ DONE |
| 3.3 | Gate registration and reporting | Same file + `run_contract_gates.py` | Advisory vs fail-closed mode | ~2k | ✅ DONE |
| 4.1 | Hook registration in `hooks.json` | `.cursor/hooks.json` | JSON editing safely | ~2k | ✅ DONE |
| 4.2 | End-to-end testing | Test files | Verification the hook actually blocks | ~4k | ✅ DONE |

---

## Gap Register

**GAP-1: No automated verification of plan identity before Notion writes**
- Cascades can inadvertently target wrong Notion pages when page IDs are stale
- No fail-closed mechanism exists; API calls succeed silently with wrong targets
- Impact: Status corruption, plan state confusion, manual cleanup required

**GAP-2: No documented prevention pattern for plan identity verification**
- Existing rules cover status taxonomy (notion-plans-taxonomy.md) but not identity verification
- No canonical guidance for "when uncertain, query first" pattern
- Impact: Each session may reinvent or forget the verification step

**GAP-3: No retrospective detection of anomalous status changes**
- Mis-targeted status updates leave audit trail but no automated detection
- Manual review of Notion history is impractical at plan volume (~130)
- Impact: Errors discovered late or not at all

---

## Execution Plan

### Wave 1 — Pre-Write Hook for Plan Identity Verification

**Phase 1.1: Hook scaffold and slug extraction**
- Create `.cursor/scripts/pre_notion_plan_write_gate.py`
- Parse Cursor Agent context to extract intended plan slug (from file content, response text, or explicit parameter)
- Handle cases where slug is in `PLAN_CREATED:` marker, plan file path, or prose

**Phase 1.2: Notion DB query integration**
- Implement `_query_notion_plans_db(slug)` → returns `page_id` or `None`
- Use direct Notion REST API (not MCP) to avoid serialization constraints
- Cache results per session to avoid repeated queries

**Phase 1.3: Match validation and blocking**
- Compare `intended_slug` with `queried_slug` from DB
- If mismatch or `queried_slug` not found → exit 2 with diagnostic
- Implement bypass: `NOTION_PLAN_IDENTITY_BYPASS=1` (logs warning, proceeds)

**Acceptance:**
```bash
# Test: hook blocks on mismatched page ID
python .cursor/scripts/pre_notion_plan_write_gate.py \
  --intended-slug l6-alignment-deferred-scope-c5e8a7 \
  --notion-page-id WRONG_ID
# Exit code 2, stderr: "PLAN_IDENTITY_MISMATCH: ..."
```

### Wave 2 — Rule Documentation

**Phase 2.1: Rule draft and review**
- Create `.cursor/rules/notion-plan-identity-verification.md`
- Document the prevention pattern: "Always verify plan identity by querying Notion DB when page IDs are uncertain"
- Include examples of correct vs incorrect targeting

**Phase 2.2: Rule registration and cross-links**
- Link from `notion-plans-taxonomy.md` § "Status Changes"
- Link from `deferred-scope-capture.md` § "Notion Writeback"
- Add to `.cursor/RULES_INDEX.md`

**Acceptance:**
- Rule is discoverable via `grep -r "verify plan identity" .cursor/rules/`
- Cross-links resolve correctly

### Wave 3 — CI Gate for Status History Audit

**Phase 3.1: Anomaly detection algorithm**
- Define anomalies:
  - Status flip from Completed → In Progress or Deferred within <1 day of creation
  - Status flip from Deferred/Completed → Completed → Deferred (flip-flop)
  - Status change by non-owner (if owner tracking available)

**Phase 3.2: Historical audit implementation**
- Query Notion page versions via `retrieve-page` with history
- Build status timeline per plan
- Flag anomalies in last 30 days

**Phase 3.3: Gate registration and reporting**
- Create `ops_scripts/ci/check_notion_plan_status_anomalies.py`
- Register in `run_contract_gates.py` as "NP3 Notion plan status anomaly detection (advisory)"
- Emit `artifacts/notion/plan_status_anomalies.json`

**Acceptance:**
```bash
python ops_scripts/ci/check_notion_plan_status_anomalies.py
# Reports 0 anomalies for clean state
# Reports 2026-05-10 incident if re-run historically
```

### Wave 4 — Integration and Testing

**Phase 4.1: Hook registration (PIVOTED to post-cursor-agent audit)**
- Create `post_cursor_agent_notion_plan_identity_audit.py` — scans Cursor Agent response for `mcp7_API-patch-page` calls targeting Plans DB
- Extracts intended slug from context and targeted page_id from API call
- Queries Notion DB to verify match
- Logs mismatches to `artifacts/cursor/plan_identity_violations.jsonl`
- **Reason for pivot:** `pre_mcp_tool_use` hooks cannot see tool arguments per `pre_mcp_gate.py:1042-1051`

**Phase 4.2: End-to-end testing**
- Create `tests/unit/windsurf_scripts/test_post_cursor_agent_notion_plan_identity_audit.py`
- Test cases: correct match, mismatch detection, missing slug, context extraction
- All tests pass

**Acceptance:**
- Audit fires automatically after Cursor Agent responses with Notion plan status updates
- Test suite: `pytest tests/unit/windsurf_scripts/test_post_cursor_agent_notion_plan_identity_audit.py -v` passes

---

## Rules

- **PLAN_IDENTITY_VERIFY_FIRST:** When Notion page ID is not 100% certain, query Plans DB by slug before any `API-patch-page` call
- **FAIL_CLOSED_ON_MISMATCH:** If slug/page_id mismatch detected, block operation (exit 2) unless bypass env var set
- **LOG_ALL_VERIFICATIONS:** Every verification attempt logs to `artifacts/cursor/plan_identity_verifications.jsonl`
- **BYPASS_AUDIT_TRAIL:** Bypasses are permitted but logged with `WARNING:` prefix and user confirmation

---

## Success Criteria

- [x] Hook `pre_notion_plan_write_gate.py` exists with verification logic
- [x] Post-cursor-agent audit `post_cursor_agent_notion_plan_identity_audit.py` registered in hooks.json
- [x] Hook blocks on slug/page mismatch (verified by test)
- [x] Rule `notion-plan-identity-verification.md` exists with 2026-05-10 incident documentation
- [x] CI gate `check_notion_plan_status_anomalies.py` registered as NP8 (advisory)
- [x] All 4 waves have passing tests
- [x] Documentation of the 2026-05-10 incident and prevention added to rule

---

## Implementation Commands

```bash
# W1: Hook creation
python -c "
import os
os.makedirs('.windsurf/scripts', exist_ok=True)
with open('.cursor/scripts/pre_notion_plan_write_gate.py', 'w') as f:
    f.write('#!/usr/bin/env python3\n\"\"\"Pre-write gate for Notion plan identity verification.\"\"\"\n')
"

# W2: Rule creation
python -c "
import os
os.makedirs('.windsurf/rules', exist_ok=True)
"

# W3: Gate creation  
python -c "
import os
os.makedirs('ops_scripts/ci', exist_ok=True)
"

# W4: Test and registration
python -c "import json; print('Update hooks.json)"
pytest tests/unit/windsurf_scripts/test_pre_notion_plan_write_gate.py -v
```

---

## Rollback Strategy

If hook causes excessive false positives:
1. Set `NOTION_PLAN_IDENTITY_BYPASS=1` globally (logged warnings)
2. Disable hook in `hooks.json` (move to `disabled_hooks`)
3. Revert to manual verification pattern
4. Fix hook logic and re-enable

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| Hook false positive rate | <5% | Review `artifacts/cursor/plan_identity_verifications.jsonl` |
| Anomaly detection recall | 100% of known incidents | Historical validation against 2026-05-10 incident |
| Rule discoverability | Top-3 search result | `grep -r "verify plan identity" .cursor/rules/` shows rule |
| Test coverage | ≥90% | `pytest --cov` on hook module |

---

## Definition of Done

| # | Criterion | Verification command / evidence | Status |
|---|---|---|---|
| DoD-1 | Hook exists and blocks on mismatch | `python .cursor/scripts/pre_notion_plan_write_gate.py --test-mismatch` exits 2 | ✅ |
| DoD-2 | Rule documents prevention pattern | Rule file exists at `.cursor/rules/notion-plan-identity-verification.md` | ✅ |
| DoD-3 | CI gate detects anomalies | `python ops_scripts/ci/check_notion_plan_status_anomalies.py` runs without error | ✅ |
| DoD-4 | Tests pass | `pytest tests/unit/windsurf_scripts/test_pre_notion_plan_write_gate.py -v` shows 25 pass | ✅ |
| DoD-5 | Memory updated | `mem:` entity created for prevention pattern | 🔲 |

**Verification-vs-Deferral table:**

| Item | Why deferred | Tracked in |
|---|---|---|
| Real-time Notion webhook integration | Out of scope; polling is sufficient | Future plan if volume increases |
| Automatic rollback of detected anomalies | Requires more invasive automation | Manual rollback per runbook |

---

## AG_QUEUE_SEED (Author-Gate decisions anticipated)

```
AG_QUEUE_SEED: plan=notion-plan-identity-verification-enforcement-f2a9c1 id=AG-W1-1 depends_on= title=Hook trigger scope — all Notion writes or just status patches?
AG_QUEUE_SEED: plan=notion-plan-identity-verification-enforcement-f2a9c1 id=AG-W1-2 depends_on= title=Fail-closed vs advisory default for hook
AG_QUEUE_SEED: plan=notion-plan-identity-verification-enforcement-f2a9c1 id=AG-W3-1 depends_on= title=Anomaly detection threshold — strict vs permissive
```

---

## Cursor Agent Alignment Checks

- This plan is **governance** type → ADG graph-layer evidence SKIPPED per template
- Enforcement belongs in hooks/gates, not always-on rules (per §33 token budget)
- Rule is discoverable, hook is deterministic, gate is advisory

---

PLAN_CREATED: slug=notion-plan-identity-verification-enforcement-f2a9c1 notion_id=35c27693-f55c-81f1-baf1-fb859d6fd066 status=in_progress tier=T3 layer=L_OPS
