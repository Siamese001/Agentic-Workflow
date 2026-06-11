---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\apps-repo-brief-closeout-impl-b3e7a2.md'
original_relative_path: '_archive\\2026-05\\apps-repo-brief-closeout-impl-b3e7a2.md'
source_sha256: 65a49e017ba8c3717a010385d71ead450bee9fd4f7097ecd3ddb2469a7ab43a8
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_repo_brief Deferred Scope Closeout — Implementation

> **Status:** Completed · **Tier:** T2 · **Slug:** `apps-repo-brief-closeout-impl-b3e7a2`
> **Source plan:** `apps-repo-brief-deferred-scope-closeout-a7d2f1` (deferred scope registry)
> **Purpose:** Implement DS-1 through DS-6 from the deferred scope registry, one wave at a time.

---

## Context

The deferred scope registry (`apps-repo-brief-deferred-scope-closeout-a7d2f1`) captures 8 items from Plans 3 & 4.
This plan implements 4 of them (DS-1, DS-4, DS-5, DS-6). DS-8 is already complete (verified 2026-05-05 — `apps_research/__main__.py` already has `_maybe_run_exit_hook` fully wired). DS-2, DS-3, DS-7 are deferred to a separate plan.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|------|-----------|-------|-------------|--------|-----------------|
| W1 | W1.1–W1.2 | DS-4: `apps_underwriting_ai` plan doc + Notion status sync | ~1k | ✅ DONE | Plan wave table all ✅ DONE; Notion page Completed |
| W2 | W2.1–W2.3 | DS-5: 7 P0 ADG layer violations remediation | ~8k | ✅ DONE | Zero P0 violations in ADG; all 7 files fixed |
| W3 | W3.1–W3.3 | DS-6: `apps_underwriting_ai` spine allowlist burndown | ~6k | ✅ DONE | Allowlist entry removed; spine delegation gate passes |
| W4 | W4.1–W4.3 | DS-1: `apps_repo_brief` FEC producer live wiring + tests | ~6k | ✅ DONE | FEC producer not retired; `__main__.py` cert hook; 7 tests pass |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Est. Tokens | Status |
|----------|-------|--------------|-------------|--------|
| W1.1 | Update underwriting plan doc wave table | `.windsurf/plans/apps-underwriting-ai-spine-hardening-d7f3b2.md` | ~500 | ✅ |
| W1.2 | Patch Notion page to Completed | Notion API call | ~500 | ✅ |
| W2.1 | Fix `apps_rg_prerequisite_gate.py` P0 violation (L0→L_APP) | `agentic_core/L0_routing/gates/apps_rg_prerequisite_gate.py` | ~1k | ✅ |
| W2.2 | Fix `l2_recipe_resolver.py` P0 violation (agentic_core→L_APP) | `agentic_core/runtime/l2_recipe_resolver.py` | ~1k | ✅ |
| W2.3 | Fix 5 `llm_client.py` P0 violations (apps_*→L_INFRA) | 5 × `apps_*/integrations/llm_client.py` | ~4k | ✅ |
| W3.1 | Audit `apps_underwriting_ai` spine imports into `agentic_core` | `apps_underwriting_ai/` | ~2k | ✅ |
| W3.2 | Wire any missing spine imports + update manifest | `apps_underwriting_ai/spine_manifest.yaml`, integrations | ~3k | ✅ |
| W3.3 | Remove allowlist entry | `config/apps_spine_delegation_allowlist.yaml` | ~500 | ✅ |
| W4.1 | Restore `apps_repo_brief` FEC producer (remove RETIRED) | `apps_repo_brief/cert/fec_producer.py` | ~2k | ✅ |
| W4.2 | Wire cert hook in `apps_repo_brief/__main__.py` | `apps_repo_brief/__main__.py` | ~2k | ✅ |
| W4.3 | 7 FEC producer tests | `tests/_apps_contract/test_apps_repo_brief_fec_producer.py` | ~2k | ✅ |

---

## Non-Goals

- DS-2 (`apps_repo_brief` C0 runtime wiring) — separate plan
- DS-3 (`apps_repo_brief` L3 workflow adapter) — separate plan
- DS-7 (`apps_eval` phase 2 items) — separate plan
- No changes to `agentic_core` core routing logic

---

## Gap Register

| ID | Gap | Wave |
|----|-----|------|
| G1 | Underwriting plan doc shows all waves as Not Started but they're done | W1.1 |
| G2 | Underwriting Notion page still In Progress | W1.2 |
| G3 | `apps_rg_prerequisite_gate.py` L0→L_APP import violation | W2.1 |
| G4 | `l2_recipe_resolver.py` agentic_core→L_APP import violation | W2.2 |
| G5-G9 | 5 `llm_client.py` apps_*→L_INFRA violations | W2.3 |
| G10 | `apps_underwriting_ai` on allowlist with 2026-05-31 expiry | W3 |
| G11 | `apps_repo_brief` FEC producer marked RETIRED; should be live | W4.1 |
| G12 | `apps_repo_brief/__main__.py` missing cert hook | W4.2 |
