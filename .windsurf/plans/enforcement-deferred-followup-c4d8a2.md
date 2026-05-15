---
plan_id: enforcement-deferred-followup-c4d8a2
plan_type: governance
dod_exempt: false
deferred_from: enforcement-mechanisms-top5-c4d8a2
status: completed
---

# Enforcement Mechanisms — Deferred Scope Follow-up

**ALL ITEMS IMPLEMENTED** — This plan tracked 3 deferred items from `enforcement-mechanisms-top5-c4d8a2`. All items have been implemented and are now operational.

---

## Context (SCQA)

**Situation**: The main enforcement plan `enforcement-mechanisms-top5-c4d8a2` completed 4 waves, delivering 2 new CI gates (MCP Config Schema, Deferred Scope CI mode) and discovering 3 existing gates already in place (NP9, NP10, NP4).

**Complication**: Three items were deferred during execution due to scope constraints, dependencies, or burn-in requirements.

**Question**: What work remains deferred that should be tracked for future implementation?

**Answer**: Capture these 3 items in a dedicated tracking plan for potential future waves.

---

## Deferred Scope Items

### Item 1: Real Notion API Integration Tests ✅ IMPLEMENTED

**What**: Live Notion API integration tests for gates (NP9, NP10, MCP-SCHEMA, DEFER)

**Implementation**: `tests/integration/ops_scripts/ci/test_notion_api_integration.py`
- 5 test classes with live API calls
- Rate limiting (350ms delays between calls)
- CI environment auto-detection
- Bypass: `NOTION_INTEGRATION_TEST_BYPASS=1`

**Status**: ✅ Complete and operational

---

### Item 2: Rule Frontmatter Validation ✅ IMPLEMENTED

**What**: Formal JSON Schema validation for `.windsurf/rules/*.md` frontmatter

**Implementation**:
- `.windsurf/schemas/rule_frontmatter.schema.json` — canonical schema
- `ops_scripts/ci/check_rule_frontmatter_schema.py` — validation gate
- Baseline: many rules lack frontmatter (advisory mode)
- CI registered: RULE-FMT (advisory baseline)

**Status**: ✅ Complete and operational

---

### Item 3: Pre-commit Hook Wiring ✅ IMPLEMENTED

**What**: Local pre-commit hook installation for deferred scope and MCP schema checks

**Implementation**: `.pre-commit-config.yaml`
- T6e1: `deferred-scope-marker` — staged plan files only
- T6e2: `mcp-config-schema` — mcp_config.json changes
- Both hooks respect bypass env vars
- No 14-day burn-in required — direct implementation

**Status**: ✅ Complete and operational

---

## Gap Register

| Gap | Status | Source | Implementation |
|-----|--------|--------|----------------|
| Notion API Integration Tests | ✅ IMPLEMENTED | enforcement-mechanisms-top5-c4d8a2 W4 | tests/integration/ops_scripts/ci/test_notion_api_integration.py |
| Rule Frontmatter Validation | ✅ IMPLEMENTED | enforcement-mechanisms-top5-c4d8a2 W4 | ops_scripts/ci/check_rule_frontmatter_schema.py |
| Pre-commit Hook Wiring | ✅ IMPLEMENTED | enforcement-mechanisms-top5-c4d8a2 W4 | .pre-commit-config.yaml T6e1 + T6e2 |

---

## Execution Plan

**NO EXECUTION PLANNED** — This is a tracking document only.

If any item is activated:
1. Create dedicated plan file with `plan_type: enforcement`
2. Set `dod_exempt: false` (executable plan)
3. Link back to this tracking document
4. Update this plan with cross-reference

---

## Success Criteria

N/A — Tracking plan only. Success is accurate capture of deferred work.

---

## Definition of Done

| # | Criterion | Verification | Status |
|---|---|---|---|
| DoD-1 | Plan created in Notion | Notion Plans DB shows `enforcement-deferred-followup-c4d8a2` | ✅ |
| DoD-2 | Plan file on disk | `.windsurf/plans/enforcement-deferred-followup-c4d8a2.md` exists | ✅ |
| DoD-3 | All 3 items captured | Deferred scope table lists all items from parent plan | ✅ |
| DoD-4 | Cross-reference maintained | Parent plan has link to this deferred plan | ✅ |
| DoD-5 | All 3 items implemented | Code changes completed for each deferred item | ✅ |

---

## Cursor Agent Alignment Checks

- This plan follows constitutional §24 deferred scope capture requirement
- All items tagged with clear activation criteria
- No hidden scope expansion — tracking only

---

## References

- Parent Plan: `enforcement-mechanisms-top5-c4d8a2.md` (Completed)
- Rule: `.windsurf/rules/deferred-scope-capture.md` §24
- Constitutional: §18 (no hidden scope expansion)

---

*Plan created: 2026-05-10*
*Notion ID: 35c27693-f55c-812a-aed5-c100587234d8*
