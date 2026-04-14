---
trigger: model_decision
description: Use this rule when deciding whether HITL is required and when shaping the recommendation packet for architectural or governance decisions.
---

# HITL SVP Calibration — Target State & Measurable Thresholds

**Status**: ACTIVE  
**Phase**: Wave 2 Phase 2.8  
**Authority**: `.windsurf/rules/hitl-enforcement.md` §HITL-0  
**Constitutional**: §6 HITL Discipline

---

## Purpose

Define measurable, objective thresholds for when HITL is REQUIRED vs when Cascade
MUST continue executing without stopping. Prevents both under-HITL (silent decisions)
and over-HITL (unnecessary interruptions).

---

## Target State: HITL Decision Matrix

### REQUIRED — Stop and Present Options

| Trigger | Threshold | Tool |
|---------|-----------|------|
| Multiple valid architectural approaches | ≥2 genuinely viable designs | `ask_user_question` |
| Refactor scope spans >1 layer | Any cross-layer change | `ask_user_question` |
| New external dependency | Any new PyPI/npm package | `ask_user_question` |
| Anti-pattern introduction | Any new guardian comment | `ask_user_question` |
| File/module deletion (production) | Any production file deletion | `ask_user_question` |
| Test repair class ambiguous | >1 valid repair class applies | `ask_user_question` |
| Configuration governance change | Any policy/threshold change | `ask_user_question` |

### FORBIDDEN — Do NOT Stop (continue executing)

| Scenario | Reason |
|----------|--------|
| Single clearly-correct path | No genuine choice exists |
| Deterministic follow-up steps | Outcome is fixed by prior decision |
| Reading files to gather context | Research, not decision |
| Running scoped tests after a fix | Verification, not decision |
| Committing after green tests | Mechanical step |
| Pushing after commit | Mechanical step |
| Writing a single doc file | No architectural tradeoff |

---

## SVP Recommendation Calibration

When presenting HITL options, the SVP Engineering ⭐ recommendation MUST prioritize:

| Priority | Lens | Example Recommendation |
|----------|------|----------------------|
| 1st | Operational simplicity | Prefer fewer moving parts over elegant abstraction |
| 2nd | Dependency hygiene | Prefer in-house over new external library |
| 3rd | Archival over deletion | Prefer `tools/archive/` over `git rm` |
| 4th | Documentation | Prefer ADR + rule over undocumented change |
| 5th | Zero-regression validation | Prefer full test pass over speed |

---

## Measurable Thresholds (Calibration Targets)

| Metric | Red (Bad) | Yellow (Acceptable) | Green (Target) |
|--------|-----------|--------------------|-|
| HITL prompts per T2 session | >5 | 2-5 | ≤2 |
| HITL prompts per T3 session | >8 | 3-8 | ≤4 |
| False HITL stops (no real choice) | >2/session | 1-2/session | 0/session |
| Missed HITL (silent architectural choice) | Any | — | 0 |
| Options presented per prompt | <2 or >4 | — | 2-4 |
| ⭐ Recommendation included | Never | Sometimes | Always |

---

## Format Requirements

Every HITL prompt MUST use `ask_user_question` tool with:

```
question: Must include header packet:
  Recommended: <option_title>
  Why it wins: <one sentence, case-specific, not generic>
  What you are optimizing for: <the actual goal this decision serves>
  What is being traded off: <the precise cost of the winning path>
  Candidates evaluated: N | Surfaced: M | Suppressed (low confidence): X | Suppressed (non-distinct): Y
options: 2-4 items (HITL-10 shape, see hitl-decision-points.md)
  label: Short name (≤6 words)
  description: Architecture-specific justification, not generic pros/cons
allowMultiple: false
```

**FORBIDDEN HITL anti-patterns:**

- Plain text "yes/no" question without `ask_user_question` tool
- More than 4 options (forces analysis paralysis)
- No ⭐ recommendation (abdicates SVP responsibility)
- Stopping without a real decision point ("just checking in")
- Generic pros/cons without architecture-specific justification
- Bare `ask_user_question` after analysis prose (analysis belongs inside description field)

---

## Confidence Scoring Pipeline

Before surfacing any HITL prompt, score all candidates:

| Parameter | Value |
|-----------|-------|
| `surface_threshold` | 0.72 — suppress below this |
| `dominance_score_threshold` | 0.85 — top score must reach this |
| `dominance_delta` | 0.12 — gap to next must exceed this |
| `max_surface_options` | 4 |

If top scores ≥ 0.85 AND gap to next ≥ 0.12 → surface only the top option (dominance rule).
If no candidate clears 0.72 → emit `LOW_CONFIDENCE_AMBIGUITY`, do not fabricate options.

For **refactor-class decisions** (`architecture_choice`, `refactor_scope`, `anti_pattern`,
`deletion_strategy`, `dependency_addition`, `test_strategy`, `error_handling`), emit after
user selection — as the **first plain-text line** of the response, before any tool calls:

```
DECISION_CAPTURED: type=<type>, repo_area=<area>, selected=<chosen_label>, outcome=executed
```

---

## Continuous Execution Mandate

Between HITL decision points, Cascade MUST execute ALL deterministic steps without
interruption. The correct cadence for a T3 task:

```
[HITL] Select approach A/B/C
→ [AUTO] Read relevant files
→ [AUTO] Query ADG for blast radius
→ [AUTO] Make edits
→ [AUTO] Run scoped tests
→ [AUTO] Commit (pre-commit hooks run normally)
→ [AUTO] Push
→ [HITL] Next decision point (if any)
```

Stopping between [AUTO] steps = constitutional violation of §HITL-0.1.

---

## References

- Rule: `.windsurf/rules/hitl-enforcement.md`
- Constitutional: `.windsurf/rules/constitutional.md` §6
- Workflow: `.windsurf/workflows/hitl-decision-gate.md`
