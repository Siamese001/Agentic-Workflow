---
plan_id: <descriptive-name>-<6hex>
plan_type: refactor    # refactor | governance | audit | doc | infra | tracker
# plan_type governs §22 ADG graph-layer-evidence gate:
#   refactor   → ENFORCED (ADG_HOTSPOT_REPORT + ADG_GRAPH_LAYER_EVIDENCE required)
#   governance → SKIPPED (gates, schemas, CI, rule changes)
#   audit      → SKIPPED (observational / inventory)
#   doc        → SKIPPED (documentation only)
#   infra      → SKIPPED (tooling / infrastructure, no code refactor)
#   tracker    → SKIPPED (descope trackers, status dashboards)
# See: .windsurf/rules/adg-graph-layer-enforcement.md § "Plan Scope via Frontmatter"
---

# [Plan Title]

One-sentence summary of what this plan accomplishes.

---


## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `.windsurf/` rule / skill / workflow | governing repo procedure | 🔲 |
| Exact files / symbols | direct repo evidence | 🔲 |
| ADG / MCP evidence | structural or runtime proof | 🔲 |
| External source (only if needed) | freshness or missing local evidence | 🔲 |

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | [Metric 1] | [Scope 1] | A | [Tokens] 🟢 |
| Wave 2 | [Metric 2] | [Scope 2] | B | [Tokens] 🟢 |
| Wave 3 | [Metric 3] | [Scope 3] | C | [Tokens] 🟢 |
| Wave 4 | [Metric 4] | [Scope 4] | D | [Tokens] 🟢 |

**Total: [Total] tokens across 4 waves, all GREEN**

---

## Phase-Level Summary

> **MANDATORY for T2/T3 plans.** A plan missing this table is invalid and must not be saved.

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| 1.1 | [Phase 1.1 title] | [files affected] | [PP-N, GAP-N] | ~[N]K | 🔲 TODO |
| 1.2 | [Phase 1.2 title] | [files affected] | [PP-N, GAP-N] | ~[N]K | 🔲 TODO |
| 2.1 | [Phase 2.1 title] | [files affected] | [PP-N, GAP-N] | ~[N]K | 🔲 TODO |
| 2.2 | [Phase 2.2 title] | [files affected] | [PP-N, GAP-N] | ~[N]K | 🔲 TODO |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS · ✅ DONE · ❌ BLOCKED

---

## Gap Register

**GAP-1: [Gap description]**
- [Details about the gap]
- [Impact]

**GAP-2: [Gap description]**
- [Details about the gap]
- [Impact]

---

## Execution Plan

### Phase 1 — [Phase Title]
**Scope**: [What this phase does]

**Commands**:
```bash
# Command 1
# Command 2
```

**Acceptance**: [Success criteria]

### Phase 2 — [Phase Title]
**Scope**: [What this phase does]

**Commands**:
```bash
# Command 1
# Command 2
```

**Acceptance**: [Success criteria]

---

## Rules

- [Rule 1]
- [Rule 2]
- [Rule 3]

---

## Success Criteria

- [ ] [Criteria 1]
- [ ] [Criteria 2]
- [ ] [Criteria 3]

---

## Implementation Commands

```bash
# Full implementation sequence
python tools/[script].py --option
python tools/[script].py --option
```

---

## Rollback Strategy

If things go wrong:
1. [Rollback step 1]
2. [Rollback step 2]
3. [Rollback step 3]

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| [Metric 1] | [Target] | [How to verify] |
| [Metric 2] | [Target] | [How to verify] |

## Cascade Alignment Checks

- Keep always-on rules lean; place detailed procedures in skills or workflows.
- Retrieve local or scoped evidence before synthesis.
- Prefer exact or structural matches before broad semantic expansion.
- For high-risk outputs, extract evidence or quotes before summarizing.
- Reserve deterministic enforcement for hooks or scripts, not template prose.
