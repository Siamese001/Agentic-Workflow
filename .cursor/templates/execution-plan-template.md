---
plan_id: <descriptive-name>-<6hex>
plan_type: refactor    # refactor | governance | audit | doc | infra | tracker | platform_core_change
touches_agentic_core: false   # true → plan_type MUST be platform_core_change + core_addition_author_gate_required=true
touches_governance_ci: false   # true when modifying CI gates, schemas, or enforcement rules
touches_cursor_rules: false   # true when modifying .cursor/rules/*.md
touches_plan_templates: false   # true when modifying .cursor/templates/*.md
core_addition_author_gate_required: false   # true when touches_agentic_core=true; receipt ref required
author_gate_receipt_ref: ""   # path to CoreAdditionAuthorGateReceipt JSON (required when core_addition_author_gate_required=true)
dod_exempt: false   # true for RCA-only, doc-only, audit observation plans (exempt from PLAN-DOD gate)
---

# [Plan Title]

One-sentence summary of what this plan accomplishes.

> **plan_id discipline**: the `plan_id:` frontmatter value MUST match the filename stem
> (with or without numeric prefix). Wave markers use `plan=<plan_id>`. The hook resolves
> the file by exact match, numeric-prefix strip, or frontmatter scan — but slug must
> match. Example: file `foo-bar-abc123.md` → `plan_id: foo-bar-abc123` → marker `plan=foo-bar-abc123`.

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

## Status Tables

> These tables are auto-updated by `post_cursor_agent_wave_lifecycle_capture.py` when
> `WAVE_COMPLETE:` / `PHASE_COMPLETE:` / `PLAN_COMPLETE:` markers are emitted.
> Status tokens: `✅ DONE` · `🔄 IN PROGRESS` · `🔲 TODO` · `❌ BLOCKED`
> Test/scope columns are populated from the `note=` field on `WAVE_COMPLETE:` markers
> (e.g. `note="+8 tests, 3 files, scope=exit-binding"`).

### Wave Progress

| Wave | Focus | Status | Tests Added | Files Changed |
|------|-------|--------|-------------|---------------|
| W1 | [Wave 1 scope] | 🔲 TODO | — | — |
| W2 | [Wave 2 scope] | 🔲 TODO | — | — |
| W3 | [Wave 3 scope] | 🔲 TODO | — | — |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | [Phase title] | 🔲 TODO |
| W1.2 | [Phase title] | 🔲 TODO |
| W2.1 | [Phase title] | 🔲 TODO |
| W2.2 | [Phase title] | 🔲 TODO |
| W3.1 | [Phase title] | 🔲 TODO |

---

## Out Of Scope

- [Out-of-scope item 1]
- [Out-of-scope item 2]

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

## Wave 3 — [Wave Title]

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Phases**:
- **W3.1** — [Phase title] | ~[N]K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.2** — [Phase title] | ~[N]K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- [Criterion 1]
- [Criterion 2]

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

## Gap Register

**GAP-1: [Gap description]**
- Details about the gap
- Impact

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

When scope is discovered during execution, emit markers in order:

```
DISCOVERED_SCOPE: plan=<plan_id> wave=<N> phase=<M> gap="<what>" impact="<severity>"
AUTHORIZATION_DECISION: plan=<plan_id> decision=<ACCEPTED|DEFERRED|SPLIT_TO_NEW_PLAN|REJECTED> authorized_by=<user|author_gate|self> decisive_reason="<why>"
SCOPE_EXPANSION: plan=<plan_id> reason="<summary>" added="<waves/phases>" authorized="yes"
```

| Decision | When | Continues? |
|---|---|---|
| ACCEPTED | In-charter, absorbable | Yes, expanded scope |
| DEFERRED | Valid but time-gated | Yes, original scope |
| SPLIT_TO_NEW_PLAN | Too large | Yes, original scope |
| REJECTED | Gold-plating | Yes, original scope |

> **Documentation ≠ Authorization.** Retroactive plan updates are not governance.

---

## Marker Quick Reference

Wave lifecycle markers (must be at start of line, use exact plan_id):
```
WAVE_START: plan=<plan_id> wave=<N>
WAVE_COMPLETE: plan=<plan_id> wave=<N> note="+N tests, N files, scope=<summary>"
PHASE_COMPLETE: plan=<plan_id> phase=<W1.1>
PLAN_COMPLETE: plan=<plan_id> note="<final outcome>"
```

> **Auto-maintained**: `WAVE_STATUS`, `WAVE_COMPLETE`, `PHASE_STATUS`, `PHASE_COMPLETE`,
> wave table ✅/🔲/🔄 status cells, and DoD `- Status:` fields are updated automatically
> by `post_cursor_agent_wave_lifecycle_capture.py`. Manual edits only needed if hook was
> bypassed (`WAVE_TABLE_UPDATE_BYPASS=1`).
>
> **note= format for auto-capture**: `note="+N tests, N files, scope=<one-word>"` — the
> hook parses `+N tests` and `N files` and writes them to the wave table's Tests Added
> and Files Changed columns.
