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

## Context (SCQA)

> **Pyramid Principle / SCQA scaffold.** Use this 4-paragraph block to give any reader (next-session Cascade, reviewer, future you) the minimum context to act. Keep each section to 1–4 sentences. Delete this guidance line before saving.

- **Situation** — current state. What exists, what works, what the baseline metrics are. Cite ADG snapshot ID, current burndown counts, or relevant prior plans.
- **Complication** — what disrupts the situation. The defect, the gap, the new requirement, the regression, or the ratchet ceiling that forces action.
- **Question** — the single question this plan answers. Phrase as "How do we …?" or "Should we …?". One question, not a list.
- **Answer** — the one-line thesis of the plan. The remaining sections are the proof.

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

## Out Of Scope

> **Explicit guardrail.** List files, directories, refactors, or "while I'm here" urges that are NOT part of this plan. The scope-containment rule (`.windsurf/rules/scope-containment.md`) uses this section to deter gold-plating. Empty list allowed for narrow single-file plans; prefer explicit over implicit.

- [Out-of-scope item 1]
- [Out-of-scope item 2]

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

---

## Definition of Done

> **Mandatory section.** A plan may NOT be marked Completed in Notion or via `wave_execution_state.py complete` until every DoD row is ticked.
> Enforced by CI gate `ops_scripts/ci/check_plan_definition_of_done.py` (PLAN-DOD).
> A plan that is genuinely DoD-exempt (RCA-only, doc-only, audit observation report) MUST set `dod_exempt: true` in frontmatter — prose hand-waving is not an exemption.
>
> ⛔ Lesson from `apps-rg-declarative-ingress-only-spinal-governance-c8b3e1`: that plan was marked W9 COMPLETE while `python -m apps_rg` raised ImportError on first import. A DoD row of "smoke run exits 0 and produces an artifact" would have caught this. Every plan that touches an executable surface MUST include a smoke-test row.

| # | Criterion | Verification command / evidence | Status |
|---|---|---|---|
| DoD-1 | [Primary functional outcome — what changed code DOES, not what tests assert] | `[command that produces evidence]` | 🔲 |
| DoD-2 | [Smoke-run row if any executable surface is touched] | `python -m <module> [args]` exits 0 and produces a recognizable artifact at `artifacts/<path>` | 🔲 |
| DoD-3 | [Test count + zero regressions] | `pytest <selector>` shows N pass, 0 fail, baseline preserved | 🔲 |
| DoD-4 | [CI gate green / no new violations] | `python ops_scripts/ci/run_contract_gates.py` exits 0 (or known advisory baseline unchanged) | 🔲 |
| DoD-5 | [Documentation / memory writeback] | `mem:` entity updated; ADR linked; sibling rules referencing this work patched | 🔲 |

**Verification-vs-Deferral table** — fields that look like wins but were intentionally NOT verified must be listed here so a reviewer can audit scope honesty:

| Item | Why deferred | Tracked in |
|---|---|---|
| [E.g. real LLM E2E] | [Out of plan scope; covered by next plan] | [Next plan slug or `NEXT_STEP:` marker] |

---

## Cascade Alignment Checks

- Keep always-on rules lean; place detailed procedures in skills or workflows.
- Retrieve local or scoped evidence before synthesis.
- Prefer exact or structural matches before broad semantic expansion.
- For high-risk outputs, extract evidence or quotes before summarizing.
- Reserve deterministic enforcement for hooks or scripts, not template prose.
