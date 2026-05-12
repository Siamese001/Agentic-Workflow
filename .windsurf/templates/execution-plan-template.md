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
#
# NOTION STATUS DISCIPLINE (§plan-location.md):
#   - Plans MUST be created with Status="Not Started" (never "In Progress")
#   - Use: from tools.notion.plan_creation_helper import create_plan_in_notion
#   - Retrospective plans only: force_status="Completed"
#   - See: .windsurf/rules/plan-location.md § "Notion Status Discipline"
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
| `.windsurf/` rule / skill / workflow | governing repo procedure | 🔲 TODO |
| Exact files / symbols | direct repo evidence | 🔲 TODO |
| ADG / MCP evidence | structural or runtime proof | 🔲 TODO |
| External source (only if needed) | freshness or missing local evidence | 🔲 TODO |

---

## Wave Structure

> **W0 (optional)**: Pre-flight baseline verification — gate runs, smoke tests, environment checks. W0 is invisible to Notion status tracking; it runs while status remains "Not Started".

| Waves | Metric | Scope | Checkpoint | Tokens | Status |
|-------|--------|-------|------------|---------|--------|
| Wave 0 | [Metric 0] | Baseline gates | Pre-flight | [Tokens] | 🔲 TODO |
| Wave 1 | [Metric 1] | [Scope 1] | A | [Tokens] | 🔲 TODO |
| Wave 2 | [Metric 2] | [Scope 2] | B | [Tokens] | 🔲 TODO |
| Wave 3 | [Metric 3] | [Scope 3] | C | [Tokens] | 🔲 TODO |
| Wave 4 | [Metric 4] | [Scope 4] | D | [Tokens] | 🔲 TODO |

**Total: [Total] tokens across [N] waves, all GREEN**

**Status tracking**: Notion Status flips "Not Started" → "In Progress" at **Wave 1 start** (via `wave_execution_state.py start`). W0 completion does NOT trigger a status change — it is pre-flight, not execution.

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

## Scope Expansion Authorization

When scope is discovered during execution that requires modifying this plan:

### Four-Step Discipline (mandatory)

```
Step 1: DISCOVERED_SCOPE marker (in-session, before any new work)
Step 2: AUTHORIZATION_DECISION marker (same response, explicit verdict)
Step 3: Plan file updates (if ACCEPTED) — last_updated, tables, gaps, DoD
Step 4: SCOPE_EXPANSION marker (execution proceeds only after Step 3)
```

### Marker Grammars

**Step 1 — DISCOVERED_SCOPE:**
```
DISCOVERED_SCOPE: plan=<slug-6hex> wave=<N> phase=<M> gap="<what was found>" impact="<severity>"

Example:
DISCOVERED_SCOPE: plan=foo-abc123 wave=3 phase=5 gap="G12 cache invalidation race" impact="High — corrupts L2 receipts"
```

**Step 2 — AUTHORIZATION_DECISION:**
```
AUTHORIZATION_DECISION: plan=<slug-6hex> decision=<ACCEPTED|DEFERRED|SPLIT_TO_NEW_PLAN|REJECTED> authorized_by=<user|author_gate|self> decisive_reason="<why>"

Examples:
AUTHORIZATION_DECISION: plan=foo-abc123 decision=ACCEPTED authorized_by=user decisive_reason="Critical path blocker — G24 hardening depends on this gap fix"
AUTHORIZATION_DECISION: plan=foo-abc123 decision=DEFERRED authorized_by=author_gate decisive_reason="30-day time-gated; needs production log volume for calibration"
AUTHORIZATION_DECISION: plan=foo-abc123 decision=SPLIT_TO_NEW_PLAN authorized_by=user decisive_reason="Scope too large — creates plan apps-rg-g22-diagnostics-d9f4a2"
AUTHORIZATION_DECISION: plan=foo-abc123 decision=REJECTED authorized_by=user decisive_reason="Gold-plating; G22 diagnostics not required for v1 release"
```

**Step 4 — SCOPE_EXPANSION (only after ACCEPTED):**
```
SCOPE_EXPANSION: plan=<slug-6hex> reason="<summary>" added="<waves/phases/gaps>" authorized="yes"

Example:
SCOPE_EXPANSION: plan=foo-abc123 reason="W3 revealed G22 diagnostics gap requiring new phases" added="W5.P8 (G22 diagnostics), W5.P9 (G28 receipt ordering), GAP-12" authorized="yes"
```

### Decision Vocabulary

| Decision | When to use | Plan Update Required | Execution Continues? |
|---|---|---|---|
| **ACCEPTED** | Scope is critical path, in-charter, and absorbable | Yes — complete all Required Updates | Yes, on expanded scope |
| **DEFERRED** | Scope is valid but time/volume gated | No — emit `DEFERRED_SCOPE:` marker | Yes, on original scope only |
| **SPLIT_TO_NEW_PLAN** | Scope is valid but too large for current plan | No — create new plan, link to this one | Yes, on original scope only |
| **REJECTED** | Scope is gold-plating, off-charter, or low priority | No | Yes, on original scope only |

### Required Updates (if ACCEPTED)

Must complete ALL before emitting SCOPE_EXPANSION marker:
- [ ] **Refresh `last_updated`** — current date in frontmatter
- [ ] **Add/modify Wave Structure row** — new wave if needed, or modify existing
- [ ] **Add/modify Phase-Level Summary row** — new phase(s) with 🔲 TODO status
- [ ] **Add/modify Gap Register row** — document the discovered gap
- [ ] **Add/modify DoD criterion** — if new deliverables required
- [ ] **Append to Scope Expansion Authorization Log** — inline documentation

### Retroactive Authorization Negative-Control

> **Documentation ≠ Authorization.** A plan update filed after work completes is retroactive permission, not governance.

The `post_cascade_plan_scope_audit.py` hook detects **RETROACTIVE_AUTHORIZATION_DETECTED** when:
1. ≥3 file operations (edit/write) detected in response
2. Active plan exists (modified within 24h)
3. **NO** preceding `AUTHORIZATION_DECISION` marker with `decision=ACCEPTED` in same response

This prevents the anti-pattern where "plan update" becomes a post-hoc rationalization after gold-plating.

---

## Cascade Alignment Checks

- Keep always-on rules lean; place detailed procedures in skills or workflows.
- Retrieve local or scoped evidence before synthesis.
- Prefer exact or structural matches before broad semantic expansion.
- For high-risk outputs, extract evidence or quotes before summarizing.
- Reserve deterministic enforcement for hooks or scripts, not template prose.
