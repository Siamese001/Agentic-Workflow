---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\plan-format-simplification-rca-d4f8e2.md'
original_relative_path: 'plan-format-simplification-rca-d4f8e2.md'
source_sha256: 57fcbb28d5f359e299c3506273ca8444a0c91e5f1e299e75e5f3dcb8f3783b2c
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-05-12'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: plan-format-simplification-rca-d4f8e2
plan_type: governance
touches_agentic_core: false
touches_governance_ci: true
touches_windsurf_rules: true
touches_plan_templates: true
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# Plan Format Simplification RCA

Simplify plan markdown structure to enable reliable automated tracking of wave completion and scope changes. Replace complex nested tables with consistent, machine-updatable formats.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: DONE
CURRENT_WAVE: W4
LAST_COMPLETED_WAVE: W4
LAST_UPDATED: 2026-05-12

---

## Context (SCQA)

- **Situation** — Current plan format uses deeply nested tables (Phase status, Audit results, Artifacts) with verbose acceptance sections. Example: W3A mechanical audit requires 4 separate tables with 20+ rows to convey 8 checks passed.
- **Complication** — Complex markdown tables resist automated updates. Wave completion markers cannot reliably inject into nested table cells. Manual updates drift; automated updates fail due to inconsistent table shapes across plans.
- **Question** — How do we restructure plans to support both human readability and reliable machine updates?
- **Answer** — Flatten structure: single-line status markers outside tables, consistent Phase lists, artifact references as simple lists. Machine updates target standardized header markers (WAVE_STATUS, PHASE_STATUS, WAVE_COMPLETE, PHASE_COMPLETE) outside tables.

---

## Wave Overview

**Waves**: 4 total (W1–W4)
**Total Estimate**: ~16K tokens
**Current**: W4 (DONE)
**Plan Status**: DONE

**Wave Manifest**:
- **W1** — Forward-only format contract | ~3K tokens | Checkpoint A | DONE
- **W2** — Simplified spec | ~4K tokens | Checkpoint B | DONE
- **W3** — Migration pilot | ~5K tokens | Checkpoint C | DONE
- **W4** — Enforcement gate | ~4K tokens | Checkpoint D | DONE

---

## Wave 1 — Forward-Only Format Contract

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
CHECKPOINT: A

**Phases**:
- **W1.1** — Define forward-only marker contract | ~1.5K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.2** — Define forward-only enforcement rules | ~1.5K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- ✅ Forward-only marker contract defined in `docs/standards/simplified-plan-format.md`
- ✅ Enforcement rules defined in `artifacts/plan_format_forward_enforcement_rules.md`
- ✅ Optional dry-run validator at `tools/analysis/check_plan_format_forward.py`
- ✅ No historical plans inventoried, migrated, or rewritten
- ✅ No agentic_core modifications
- ✅ No CI gate created (deferred to W4)

---

## Wave 2 — Simplified Spec

WAVE_ID: W2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: B

**Authorization Granted**: 2026-05-12
User explicitly authorized modification of `.windsurf/templates/execution-plan-template.md`.

**Phases**:
- **W2.1** — Self-hosting format demonstration | ~2K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W2.2** — Template update | ~2K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- ✅ This plan file self-hosts the simplified format (verified by validator)
- ✅ `.windsurf/templates/execution-plan-template.md` updated with simplified format markers

---

## Wave 3 — Migration Pilot

WAVE_ID: W3
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: C

**Authorization Granted**: 2026-05-12
User explicitly authorized migration of 3 active plans and validator hardening.

**Phases**:
- **W3.1** — Pilot migration 3 plans | ~3K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W3.2** — Retrofit test + validator hardening | ~2K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- ✅ 3 active plans migrated to simplified format
- ✅ Strict validator hardened to exclude fenced code blocks
- ✅ All 3 pilot plans pass strict validation (0 FAIL, 0 ERROR)
- ✅ W3.2 validator hardening DONE

**Deferred to W4**:
- `wave_execution_state.py` compatibility testing (tool update + CI integration)

DEFERRED_SCOPE: plan=plan-format-simplification-rca-d4f8e2 wave=W3 phase=W3.2 item="wave_execution_state.py compatibility test" reason="moved to W4 because W4 owns CI/tool integration; precise blocker documented in wave_execution_state_receipt.md" tracked_in="W4.P1" p_band=P2

**Artifacts**:
- `artifacts/plan_format_w3_pilot_migration_receipt.md`
- `artifacts/plan_format_w3_validator_strict_receipt.md`
- `artifacts/plan_format_w3_wave_execution_state_receipt.md` (documents precise blocker)

---

## Wave 4 — Enforcement Gate

WAVE_ID: W4
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: D

**Authorization Granted**: 2026-05-12
User explicitly authorized W4 to implement forward-only plan format enforcement.

**Preconditions Met**:
1. ✅ **wave_execution_state.py marker-based update compatibility**
   - Implementation: `tools/plan_lifecycle/wave_execution_state.py`
   - Testing: Dry-run validated on all 5 canonical files
   - Outcome: IMPLEMENTED

2. ✅ **Strict validator passes on all canonical files**
   - All 5 files: 0 FAIL, 0 ERROR
   - Status: DONE

3. ✅ **Unclassified WARN count is zero**
   - 20 WARN total, all classified EMOJI-7 (cosmetic)
   - Status: DONE

4. ✅ **CI gate behavior tested in non-mutating mode**
   - Advisory mode: Exit 0, reports findings
   - Strict mode: Exit 0 on valid, non-zero on invalid
   - Unit tests: 20 passed
   - Status: DONE

**Phases**:
- **W4.1** — wave_execution_state.py compatibility | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
  - Evidence: `artifacts/plan_format_w4_wave_execution_state_compat_receipt.md`
- **W4.2** — CI gate implementation | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
  - Evidence: `artifacts/plan_format_w4_ci_gate_receipt.md`
- **W4.3** — Gate registration | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
  - Evidence: `artifacts/plan_format_w4_gate_registration_receipt.md`

**Acceptance**:
- ✅ W3 accepted deferral resolved (wave_execution_state.py compatibility)
- ✅ CI gate implemented with --advisory and --strict modes
- ✅ Gate registered in run_contract_gates.py as PFC1
- ✅ Strict mode passes on canonical plan, template, and 3 pilot plans
- ✅ No unclassified WARNs remain
- ✅ Unit tests pass (20/20)
- ✅ No additional plans migrated
- ✅ No archived/completed plans touched
- ✅ No agentic_core changes (governance CI only)

**Acceptance**:
- `ops_scripts/ci/check_plan_format_compliance.py` exists with tests
- Gate registered in `run_contract_gates.py`
- Negative controls validated (see below)

---

## Evidence Sources

- **Example plan showing complexity**: `apps-rg-golden-state-section-generation-a4f9e1.md` — Proves current format unsustainable
- **W3A mechanical audit output**: Captured in user request — Shows table sprawl problem
- **wave_execution_state.py**: Tracks what format hooks expect — Reviewed

---

## Out Of Scope

- Rewriting archived/completed plans (retrospective value low)
- Changing Notion DB schema (out of charter)
- ADG structural changes (unrelated)

---

## Gap Register

**GAP-1: What elements can be safely flattened?**
- Audit result tables with 8+ checks → simple bulleted list
- Artifact tables → simple path list with links
- Acceptance sections → standardized verdict line

**GAP-2: What constitutes machine-parseable format?**
- Header markers must be outside tables for regex targeting
- Phase status must be single-line for reliable replacement
- No nested tables (tables within tables)

**GAP-3: How to validate format compliance?**
- Lint for nested tables
- Verify WAVE_COMPLETE marker exists before any table
- Check all status lives in single-line markers, not table cells

---

## Format Specification (Demonstrated by This Plan)

### Required Top-Level Markers

```
FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: <TODO|IN_PROGRESS|DONE|BLOCKED|DEFERRED|WAITING|RETIRED|ARCHIVED>
CURRENT_WAVE: <W0|W1|W2|...>
LAST_COMPLETED_WAVE: <None|W1|W2|...>
LAST_UPDATED: <YYYY-MM-DD>
```

**Status Enum Definitions**:
- `TODO` — Not yet started (may require authorization)
- `IN_PROGRESS` — Active execution
- `DONE` — All acceptance criteria met
- `BLOCKED` — Technical, policy, validation, dependency, or governance failure preventing progress
- `DEFERRED` — Intentionally delayed (time/volume gated)
- `WAITING` — Paused pending external dependency
- `RETIRED` — Abandoned or superseded
- `ARCHIVED` — Long-term archive (read-only)

**Authorization Status (separate from WAVE_STATUS)**:
- `NOT_REQUIRED` — Wave can proceed without explicit user authorization
- `REQUIRED` — User must explicitly approve before execution (e.g., template changes)
- `GRANTED` — User has authorized wave execution
- `DENIED` — User has declined authorization (wave becomes BLOCKED or RETIRED)

### Required Per-Wave Markers (before any table)

```
## Wave N — <Title>

WAVE_STATUS: <TODO|IN_PROGRESS|DONE|BLOCKED>
WAVE_COMPLETE: <Yes|No>
CHECKPOINT: <A|B|C|...>
```

### Required Per-Phase Markers

```
- **P.N** — <Title> | <tokens> | PHASE_STATUS: <TODO|IN_PROGRESS|DONE|BLOCKED> | PHASE_COMPLETE: <Yes|No>
```

**Design Principle**: Emojis may appear in prose or display contexts, but canonical machine-readable status markers use only uppercase ASCII enums. This eliminates emoji parsing ambiguity in scripts.

### Read-Only Reference Tables (Allowed)

Tables may appear AFTER all live markers for:
- Historical wave manifest (read-only summary)
- Decision vocabulary reference
- Gap register detail

**Rule**: No script updates table cells. All live status lives in single-line markers.

---

## Current vs Proposed Format

### Current (Complex - W3A Example)

```markdown
## ✅ W3A COMPLETE — Mechanical Audit Passed

### Summary
| Phase | Status |
|-------|--------|
| W3.P1 | ✅ Author-Gate Consolidation |

### Audit Results
| Check | Status |
|-------|--------|
| 1. RULES_INDEX.md | ⚠️ WARN |

### Artifacts Produced (5)
| Artifact | Path |
|----------|------|
| Mechanical Audit | `w3a_rule_mechanical_audit.json` |
```

**Problems**:
- 3 nested tables, 20+ rows
- Status scattered across tables
- Hard to regex-replace "🔲 TODO" → "✅ DONE"
- Verbose acceptance section repeats what tables already say

### Proposed (Simplified - As Demonstrated in This Plan)

```markdown
## Wave 3A — Mechanical Audit

WAVE_STATUS: ✅ DONE
WAVE_COMPLETE: Yes
CHECKPOINT: A

**Phases**:
- **W3.P1** — Author-Gate Consolidation | PHASE_STATUS: ✅ DONE | PHASE_COMPLETE: Yes

**Checks** (8 total, 1 warn, 7 pass):
1. RULES_INDEX.md references — ⚠️ (acceptable)
2. Consolidated files exist — ✅

**Artifacts**:
- `w3a_rule_mechanical_audit.json`
```

**Benefits**:
- Single flat structure
- Status is single line: `WAVE_STATUS: ✅ DONE`
- Machine can replace `🔲 TODO` → `✅ DONE` reliably
- Bulleted lists easier to append during scope expansion
- Same information, 60% less markup

---

## Execution Details

### W1.1 — Define Forward-Only Marker Contract
**Scope**: Define canonical machine-readable fields for future/new plans only

**Deliverable**: `docs/standards/simplified-plan-format.md`

**Key Markers Defined**:
- Top-level: FORMAT_VERSION, PLAN_STATUS, CURRENT_WAVE, LAST_COMPLETED_WAVE, LAST_UPDATED
- Per-wave: WAVE_ID, WAVE_STATUS, WAVE_COMPLETE, CHECKPOINT
- Per-phase: PHASE_ID, PHASE_STATUS, PHASE_COMPLETE
- Per-DoD: DOD_ID, DOD_STATUS
- Scope expansion: DISCOVERED_SCOPE, AUTHORIZATION_DECISION, SCOPE_EXPANSION

### W1.2 — Define Forward-Only Enforcement Rules
**Scope**: Define validation rules for new or actively touched plans only

**Deliverable**: `artifacts/plan_format_forward_enforcement_rules.md`

**Key Rules Defined**:
- TLM-1..5: Top-level marker requirements
- ENUM-1..5: Canonical enum validity
- EMOJI-1..7: No emojis in canonical status fields
- TABLE-1..5: Status must be outside tables
- CONS-1..4: Consistency requirements
- SCOPE-1..4: Scope expansion sequence enforcement

**Optional Helper**:
```bash
python tools/analysis/check_plan_format_forward.py .windsurf/plans/my-plan.md
```

### W2.1 — Design Simplified Format
**Scope**: This plan file demonstrates the format (self-hosting validation)

### W2.2 — Validation Spec
**Scope**: `docs/standards/simplified-plan-format.md` with lint rules

### W3.1 — Pilot Migration
**Scope**: Convert 3 active plans to new format

### W3.2 — Retrofit Test
**Scope**: Verify wave_execution_state.py works with new format

### W4.1 — Format Compliance Gate
**Scope**: New CI gate checking plan format with negative controls

**Negative Controls** (must fail validation):
1. **Status only inside table cell** → FAIL
2. **Missing WAVE_STATUS marker** → FAIL
3. **Missing PHASE_STATUS marker** → FAIL
4. **Missing WAVE_COMPLETE before first table** → FAIL
5. **Nested table detected** → FAIL
6. **DoD status stored only in table cell** → FAIL
7. **Unknown status enum** → FAIL (e.g., "In Progress", "Completed" instead of "IN_PROGRESS", "DONE")
8. **Emoji-only status** → FAIL (e.g., "🔲 TODO", "✅ DONE" — emojis allowed in prose, not in canonical markers)
9. **Missing FORMAT_VERSION** → FAIL (required for parser selection)

**Validator Warning Classification Discipline**:
All WARN-level findings must be classified before CI promotion (W4):
- **EXPECTED_OPEN_WORK** — Waves/phases not yet started (W2, W3, W4 show TODO). Expected and harmless.
- **FALSE_POSITIVE** — Code block examples or template syntax detected as violations. Documentation artifact.
- **REAL_WARNING** — Genuine style issues requiring attention (e.g., emojis in prose allowed but discouraged).

**W1/W2 Validation Results**:

| Mode | Result | FAIL | ERROR | WARN | Classification |
|------|--------|------|-------|------|----------------|
| Advisory | PASS | 0 | 0 | 29 | Acceptable for in-progress development |
| Strict | FAIL | 12 | 0 | 17 | Not CI-ready — fenced code false positives |

**Strict Mode Failure Analysis**:
| Classification | Count | Description | Hardening Required |
|---------------|-------|-------------|-------------------|
| FENCED_CODE_FALSE_POSITIVE | 5 | Format spec code blocks trigger ENUM-2, ENUM-3, EMOJI-3 | YES — W3.2 |
| EXPECTED_OPEN_WORK | 7 | W3, W4 waves show TODO status (correct) | No — expected |
| REAL_WARNING | 17 | Emojis in prose (allowed per design) | No — acceptable |

**Validator Hardening Requirement (W3.2 / W4)**:
Strict mode is not CI-ready until the following hardening is completed:
1. Fenced markdown code blocks (```...```) must be excluded from canonical marker enum validation
2. Format reference examples must not trigger FAIL
3. Real plan body markers must still be validated strictly
4. Hardening must be completed before W4 CI registration

**Advisory Mode vs Strict Mode**:
- **Advisory mode** — Acceptable for in-progress plan development. Suitable for local validation.
- **Strict mode** — Not CI-ready until fenced-code false positives are eliminated. Strict mode is the target for W4 CI gate.

**W4 Gate Promotion Requirement**: Before CI registration, strict mode must produce zero FAIL on valid plans. Fenced-code exclusion is mandatory.

**Gate Logic**:
```python
# Pseudocode for check_plan_format_compliance.py
def validate_plan(path):
    content = read(path)
    
    # Must have top-level markers
    assert has_marker(content, "PLAN_STATUS:")
    assert has_marker(content, "CURRENT_WAVE:")
    
    # Must have WAVE markers before any table
    for wave in extract_waves(content):
        table_pos = find_first_table(wave)
        wave_status_pos = find_marker(wave, "WAVE_STATUS:")
        wave_complete_pos = find_marker(wave, "WAVE_COMPLETE:")
        assert wave_status_pos < table_pos
        assert wave_complete_pos < table_pos
    
    # No nested tables
    assert not has_nested_table(content)
    
    # No status emojis in table cells
    for table in extract_tables(content):
        for cell in table.cells:
            assert "🔲" not in cell and "✅" not in cell and "🔄" not in cell and "❌" not in cell
```

### W4.2 — Gate Registration
**Scope**: Register in run_contract_gates.py

---

## Success Criteria

- [ ] New template demonstrates 50%+ reduction in table complexity
- [ ] Machine can reliably update wave status via single-line markers
- [ ] 3 pilot plans converted and working
- [ ] CI gate validates format on PR with negative controls passing

---

## Implementation Commands

```bash
# W1.1: Inventory
python tools/analysis/plan_table_inventory.py --out artifacts/plan_format_inventory.json

# W1.2: Friction analysis
python tools/analysis/wave_update_friction_report.py

# W4.1: Gate verification
pytest tests/unit/ops_scripts/ci/test_check_plan_format_compliance.py -v
```

---

## Rollback Strategy

If simplified format breaks tools:
1. Revert pilot plans to original format
2. Disable format compliance gate
3. Update `wave_execution_state.py` to support both formats
4. Document dual-format support in ADR

---

## Definition of Done

DoD-1: Simplified format spec published
- Evidence: `docs/standards/simplified-plan-format.md` exists
- Status: DONE

DoD-2: Template updated with new format
- Evidence: `.windsurf/templates/execution-plan-template.md` has simplified sections with FORMAT_VERSION, per-wave markers, AUTHORIZATION_STATUS, per-phase markers, DoD markers, scope expansion markers
- Status: DONE

DoD-3: 3 pilot plans migrated
- Evidence: `artifacts/plan_format_w3_pilot_migration_receipt.md`
- Status: DONE

DoD-4: Validator strict mode hardened + accepted deferral
- Evidence: `artifacts/plan_format_w3_validator_strict_receipt.md`
- Deferred: wave_execution_state.py compatibility → W4 (explicit DEFERRED_SCOPE marker)
- Status: DONE (with documented deferral)

DoD-5: Rule writeback
- Evidence: Simplified format enforced via PFC1 CI gate
- Status: DONE (enforcement via CI gate)

**Deferred Items**:
- Archived plan migration → Low value, high volume → Tracked in `NEXT_STEP: batch-archive-plan-cleanup`
- Full 400+ plan conversion → Too large for single plan → Future plan after pilot validation

---

## Scope Expansion Authorization

When scope is discovered during execution that requires modifying this plan:

### Four-Step Discipline (mandatory)

```
Step 1: DISCOVERED_SCOPE marker (in-session, before any new work)
Step 2: AUTHORIZATION_DECISION marker (same response, explicit verdict)
Step 3: Plan file updates (if ACCEPTED) — update LAST_UPDATED, markers, gaps, DoD
Step 4: SCOPE_EXPANSION marker (execution proceeds only after Step 3)
```

### Marker Grammars

**Step 1 — DISCOVERED_SCOPE:**
```
DISCOVERED_SCOPE: plan=<slug-6hex> wave=<N> phase=<M> gap="<what was found>" impact="<severity>"
```

**Step 2 — AUTHORIZATION_DECISION:**
```
AUTHORIZATION_DECISION: plan=<slug-6hex> decision=<ACCEPTED|DEFERRED|SPLIT_TO_NEW_PLAN|REJECTED> authorized_by=<user|author_gate|self> decisive_reason="<why>"
```

**Step 4 — SCOPE_EXPANSION (only after ACCEPTED):**
```
SCOPE_EXPANSION: plan=<slug-6hex> reason="<summary>" added="<waves/phases/gaps>" authorized="yes"
```

### Decision Vocabulary Reference

| Decision | When to use | Plan Update Required | Execution Continues? |
|---|---|---|---|
| **ACCEPTED** | Scope is critical path, in-charter, and absorbable | Yes — update markers | Yes, on expanded scope |
| **DEFERRED** | Scope is valid but time/volume gated | No — emit DEFERRED_SCOPE marker | Yes, on original scope only |
| **SPLIT_TO_NEW_PLAN** | Scope is valid but too large for current plan | No — create new plan | Yes, on original scope only |
| **REJECTED** | Scope is gold-plating, off-charter, or low priority | No | Yes, on original scope only |

---

## Acceptance Criteria Summary

**Metrics**:
- Table reduction: 50% fewer tables per plan
- Machine update reliability: 95% success rate
- Readability score: User preference confirmed
- CI gate coverage: All new plans validated with negative controls

**Verification Methods**:
- Inventory comparison for table reduction
- Wave update test suite for reliability
- User confirmation for readability
- Gate run on sample PR for coverage

---

## Cursor Agent Alignment Checks

- Keep always-on rules lean; place detailed procedures in skills or workflows.
- Retrieve local or scoped evidence before synthesis.
- Prefer exact or structural matches before broad semantic expansion.
- For high-risk outputs, extract evidence or quotes before summarizing.
- Reserve deterministic enforcement for hooks or scripts, not template prose.

---

FINAL_CLOSEOUT_COMPLETE: plan=plan-format-simplification-rca-d4f8e2 verdict=DONE overall=DONE

PLAN_Hardened: plan=plan-format-simplification-rca-d4f8e2 version=3 format=simplified-plan-format-v1
