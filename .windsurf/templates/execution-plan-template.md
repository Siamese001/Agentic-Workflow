---
plan_id: <descriptive-name>-<6hex>
plan_type: refactor    # refactor | governance | audit | doc | infra | tracker | platform_core_change
touches_agentic_core: false   # true → plan_type MUST be platform_core_change + core_addition_author_gate_required=true
touches_governance_ci: false   # true when modifying CI gates, schemas, or enforcement rules
touches_windsurf_rules: false   # true when modifying .windsurf/rules/*.md
touches_plan_templates: false   # true when modifying .windsurf/templates/*.md
core_addition_author_gate_required: false   # true when touches_agentic_core=true; receipt ref required
author_gate_receipt_ref: ""   # path to CoreAdditionAuthorGateReceipt JSON (required when core_addition_author_gate_required=true)
dod_exempt: false   # true for RCA-only, doc-only, audit observation plans (exempt from PLAN-DOD gate)
---

# [Plan Title]

One-sentence summary of what this plan accomplishes.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W0
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-01-01

---

## Context (SCQA)

- **Situation** — Current state. What exists, what works, what baseline metrics are.
- **Complication** — What disrupts the situation. The defect, gap, new requirement, or regression.
- **Question** — The single question this plan answers. Phrase as "How do we …?"
- **Answer** — One-line thesis. Remaining sections are the proof.

---

## Wave Overview

**Waves**: [N] total (W1–W[N])
**Total Estimate**: ~[N]K tokens
**Current**: W0 (pre-flight)

**Wave Manifest**:
- **W1** — [Scope] | ~[N]K tokens | Checkpoint A | STATUS: TODO
- **W2** — [Scope] | ~[N]K tokens | Checkpoint B | STATUS: TODO
- **W3** — [Scope] | ~[N]K tokens | Checkpoint C | STATUS: TODO

---

## Wave 1 — [Wave Title]

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Authorization**: NOT_REQUIRED — No shared surface modifications in this wave.

**Phases**:
- **W1.1** — [Phase title] | ~[N]K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.2** — [Phase title] | ~[N]K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- [Criterion 1]
- [Criterion 2]

---

## Wave 2 — [Wave Title]

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Phases**:
- **W2.1** — [Phase title] | ~[N]K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.2** — [Phase title] | ~[N]K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- [Criterion 1]
- [Criterion 2]

---

## Out Of Scope

- [Out-of-scope item 1]
- [Out-of-scope item 2]

---

## Gap Register

**GAP-1: [Gap description]**
- Details about the gap
- Impact

**GAP-2: [Gap description]**
- Details about the gap
- Impact

---

## Execution Details

### W1.1 — [Phase Title]
**Scope**: [What this phase does]

**Commands**:
```bash
# Command 1
# Command 2
```

### W1.2 — [Phase Title]
**Scope**: [What this phase does]

**Commands**:
```bash
# Command 1
# Command 2
```

---

## Definition of Done

DoD-1: [Primary functional outcome]
- Evidence: [command that produces evidence]
- Status: TODO

DoD-2: [Smoke-run if executable surface touched]
- Evidence: `python -m <module> [args]` exits 0, produces artifact at `artifacts/<path>`
- Status: TODO

DoD-3: [Test count + zero regressions]
- Evidence: `pytest <selector>` shows N pass, 0 fail, baseline preserved
- Status: TODO

DoD-4: [CI gate green / no new violations]
- Evidence: `python ops_scripts/ci/run_contract_gates.py` exits 0
- Status: TODO

DoD-5: [Documentation / memory writeback]
- Evidence: `mem:` entity updated; ADR linked; sibling rules patched
- Status: TODO

---

## Scope Expansion Authorization

When scope is discovered during execution:

### Four-Step Discipline

Step 1: DISCOVERED_SCOPE marker
Step 2: AUTHORIZATION_DECISION marker
Step 3: Plan updates (if ACCEPTED)
Step 4: SCOPE_EXPANSION marker

### Marker Grammars

**Step 1 — DISCOVERED_SCOPE:**
```
DISCOVERED_SCOPE: plan=<slug-6hex> wave=<N> phase=<M> gap="<what was found>" impact="<severity>"
```
Example:
DISCOVERED_SCOPE: plan=foo-abc123 wave=3 phase=5 gap="Cache race condition" impact="High — corrupts receipts"

**Step 2 — AUTHORIZATION_DECISION:**
```
AUTHORIZATION_DECISION: plan=<slug-6hex> decision=<ACCEPTED|DEFERRED|SPLIT_TO_NEW_PLAN|REJECTED> authorized_by=<user|author_gate|self> decisive_reason="<why>"
```
Examples:
AUTHORIZATION_DECISION: plan=foo-abc123 decision=ACCEPTED authorized_by=user decisive_reason="Critical path blocker"
AUTHORIZATION_DECISION: plan=foo-abc123 decision=DEFERRED authorized_by=author_gate decisive_reason="Time-gated; needs data"
AUTHORIZATION_DECISION: plan=foo-abc123 decision=SPLIT_TO_NEW_PLAN authorized_by=user decisive_reason="Scope too large"
AUTHORIZATION_DECISION: plan=foo-abc123 decision=REJECTED authorized_by=user decisive_reason="Gold-plating"

**Step 4 — SCOPE_EXPANSION:**
```
SCOPE_EXPANSION: plan=<slug-6hex> reason="<summary>" added="<waves/phases/gaps>" authorized="yes"
```
Example:
SCOPE_EXPANSION: plan=foo-abc123 reason="W3 revealed diagnostics gap" added="W5.P8, GAP-12" authorized="yes"

### Decision Vocabulary

| Decision | When to use | Execution Continues? |
|---|---|---|
| **ACCEPTED** | In-charter, absorbable | Yes, on expanded scope |
| **DEFERRED** | Valid but time-gated | Yes, on original scope |
| **SPLIT_TO_NEW_PLAN** | Too large | Yes, on original scope |
| **REJECTED** | Gold-plating, off-charter | Yes, on original scope |

### Retroactive Authorization Negative-Control

> **Documentation ≠ Authorization.** A plan update filed after work completes is retroactive permission, not governance.

---

## Format Reference

### Required Top-Level Markers

```
FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: <TODO|IN_PROGRESS|DONE|BLOCKED|DEFERRED|WAITING|RETIRED|ARCHIVED>
CURRENT_WAVE: <W0|W1|W2|...>
LAST_COMPLETED_WAVE: <NONE|W1|W2|...>
LAST_UPDATED: <YYYY-MM-DD>
```

### Required Per-Wave Markers

```
WAVE_ID: W<N>
WAVE_STATUS: <TODO|IN_PROGRESS|DONE|BLOCKED>
WAVE_COMPLETE: <YES|NO>
AUTHORIZATION_STATUS: <NOT_REQUIRED|REQUIRED|GRANTED|DENIED>
CHECKPOINT: <A|B|C|...>
```

> **Auto-maintained**: `WAVE_STATUS`, `WAVE_COMPLETE`, `PHASE_STATUS`, `PHASE_COMPLETE`,
> and DoD `- Status:` fields are updated automatically by
> `post_cascade_wave_lifecycle_capture.py` when `WAVE_COMPLETE:` / `PHASE_COMPLETE:` /
> `PLAN_COMPLETE:` markers are emitted. Manual edits are only needed if a marker was
> never emitted or the hook was bypassed (`WAVE_TABLE_UPDATE_BYPASS=1`).

### Required Per-Phase Markers (inline)

```
- **W<N>.<M>** — <Title> | ~<N>K tokens | PHASE_STATUS: <TODO|IN_PROGRESS|DONE|BLOCKED> | PHASE_COMPLETE: <YES|NO>
```

### Required DoD Markers (inline)

```
DoD-<N>: <Criterion description>
- Evidence: <What proves completion>
- Status: <TODO|IN_PROGRESS|DONE|BLOCKED|DEFERRED>
```

### Status Definitions

| Status | Meaning |
|---|---|
| **TODO** | Not yet started (may require authorization) |
| **IN_PROGRESS** | Active execution |
| **DONE** | All acceptance criteria met |
| **BLOCKED** | Technical, policy, validation, dependency, or governance failure |
| **DEFERRED** | Intentionally delayed |
| **WAITING** | Paused pending external dependency |
| **RETIRED** | Abandoned or superseded |
| **ARCHIVED** | Long-term archive |

### AUTHORIZATION_STATUS Definitions

| Status | Meaning |
|---|---|
| **NOT_REQUIRED** | Wave proceeds without explicit authorization |
| **REQUIRED** | User must explicitly approve (e.g., modifies shared templates, CI, governance) |
| **GRANTED** | User has authorized; may proceed |
| **DENIED** | User declined; must become DEFERRED/RETIRED or await re-authorization |

---

## Cascade Alignment Checks

- Keep always-on rules lean; place detailed procedures in skills or workflows.
- Retrieve local or scoped evidence before synthesis.
- Prefer exact or structural matches before broad semantic expansion.
- Reserve deterministic enforcement for hooks or scripts, not template prose.
