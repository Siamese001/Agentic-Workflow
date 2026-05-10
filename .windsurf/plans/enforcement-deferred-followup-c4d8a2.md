---
plan_id: enforcement-deferred-followup-c4d8a2
plan_type: governance
dod_exempt: true
deferred_from: enforcement-mechanisms-top5-c4d8a2
---

# Enforcement Mechanisms — Deferred Scope Follow-up

**DO NOT IMPLEMENT** — This plan captures deferred scope from `enforcement-mechanisms-top5-c4d8a2` (Completed). These items are intentionally tracked for future work but not scheduled for immediate execution.

---

## Context (SCQA)

**Situation**: The main enforcement plan `enforcement-mechanisms-top5-c4d8a2` completed 4 waves, delivering 2 new CI gates (MCP Config Schema, Deferred Scope CI mode) and discovering 3 existing gates already in place (NP9, NP10, NP4).

**Complication**: Three items were deferred during execution due to scope constraints, dependencies, or burn-in requirements.

**Question**: What work remains deferred that should be tracked for future implementation?

**Answer**: Capture these 3 items in a dedicated tracking plan for potential future waves.

---

## Deferred Scope Items

### Item 1: Real Notion API Integration Tests

**What**: Live Notion API integration tests for gates (NP9, NP10, MCP-SCHEMA, DEFER)

**Current State**: Gates use mock-based unit tests only. No live Notion API calls in test suite.

**Why Deferred**:
- Requires live `NOTION_TOKEN` / `NOTION_API_KEY` in CI environment
- Rate limiting concerns for automated test runs
- Mock-based tests provide sufficient coverage for gate logic

**Future Activation Criteria**:
- [ ] Notion test account provisioned for CI
- [ ] Rate limit handling implemented
- [ ] Separate integration test job (not blocking unit test suite)

**Tracked In**: Future plan `notion-test-harness-c7e3f1` (not yet created)

---

### Item 2: Rule Frontmatter Validation

**What**: Formal JSON Schema validation for `.windsurf/rules/*.md` frontmatter

**Current State**: Rule files have inconsistent frontmatter. Some have YAML frontmatter, some don't. No automated validation.

**Why Deferred**:
- Rule schema not yet formalized
- Significant refactor required to standardize all rules
- Separate concern from enforcement mechanisms

**Future Activation Criteria**:
- [ ] Rule schema defined (frontmatter fields, required vs optional)
- [ ] Schema version declared in rules
- [ ] CI gate created: `check_rule_frontmatter_schema.py`

**Tracked In**: Future plan `rule-schema-validation-d9e4b2` (not yet created)

---

### Item 3: Pre-commit Hook Wiring

**What**: Local pre-commit hook installation for deferred scope and MCP schema checks

**Current State**: Both gates are CI-only. No local pre-commit hooks installed.

**Why Deferred**:
- CI-only rollout first to establish baseline
- Local pre-commit after 14-day burn-in period
- Avoid disrupting developer workflows during initial rollout

**Future Activation Criteria**:
- [ ] 14 days of CI-only operation with no major issues
- [ ] Gate violation rates stable (<5% of commits)
- [ ] `.pre-commit-config.yaml` updated with new hooks
- [ ] Developer documentation updated

**Implementation Notes**:
```yaml
# .pre-commit-config.yaml addition
- repo: local
  hooks:
    - id: deferred-scope
      name: Deferred Scope Marker Check
      entry: python ops_scripts/ci/check_deferred_scope_markers.py --staged
      language: system
      files: ^\.windsurf/plans/.*\.md$
    - id: mcp-schema
      name: MCP Config Schema Validation
      entry: python ops_scripts/ci/check_mcp_config_schema.py
      language: system
      files: ^\.windsurf/mcp_config\.json$
```

---

## Gap Register

| Gap | Status | Source |
|-----|--------|--------|
| Notion API Integration Tests | Deferred | enforcement-mechanisms-top5-c4d8a2 W4 |
| Rule Frontmatter Validation | Deferred | enforcement-mechanisms-top5-c4d8a2 W4 |
| Pre-commit Hook Wiring | Deferred | enforcement-mechanisms-top5-c4d8a2 W4 |

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
| DoD-4 | Cross-reference maintained | Parent plan has link to this deferred plan | 🔲 |
| DoD-5 | No implementation work | Zero code changes in this plan | ✅ |

---

## Cascade Alignment Checks

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
