---
plan_id: historical-plans-memorial-consolidation-d4e7a2
plan_format: v2
plan_type: governance
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
supersedes: []
---

# Historical Plans Memorial Consolidation

Consolidate historical Windsurf, Cursor/Claude, and reports-plan material into the root `plans/` SSOT as archived, non-executable memorial records for review and lessons learned.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: DONE
CURRENT_WAVE: COMPLETE
LAST_COMPLETED_WAVE: W3
LAST_UPDATED: 2026-06-11

---

## Context (SCQA)

- **Situation** - The approved active plans SSOT is `C:\Git\Agentic-Workflow-FRESH\plans`, but historical plans are scattered across `.codex/plans`, `docs/reports/plans`, and recovered Windsurf material under `C:\Git\windsurf-plans-recovered`.
- **Complication** - The historical material includes active-plan-shaped files, archives, RCAs, evidence reports, duplicate names, and recovered files. Leaving it scattered makes it hard to query failures, repeated work, and lessons learned.
- **Question** - How do we create one flat review plane in `plans/` without turning historical material into executable work or overwriting current active plans?
- **Answer** - Copy historical material into `plans/` with collision-safe archived filenames, prepend a non-executable memorial metadata block, preserve originals, and emit a manifest for audit.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1, W1.2 | Inventory and collision plan | ~3K | Source folders are readable | DONE | Counts and target naming rules are established |
| W2 | W2.1, W2.2 | Copy archived memorial files into root `plans/` | ~5K | Historical records should be copied, not moved | DONE | Imported files are marked archived and do not overwrite active plans |
| W3 | W3.1, W3.2 | Verify flat review plane | ~3K | Manifest can be used as audit trail | DONE | Counts, collisions, and metadata are verified |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Read plan governance and source inventories | DONE |
| W1.2 | Define import rules and manifest fields | DONE |
| W2.1 | Generate archive-marked copied files | DONE |
| W2.2 | Preserve provenance and collision decisions | DONE |
| W3.1 | Validate counts and metadata | DONE |
| W3.2 | Report final risks and next actions | DONE |

---

## Out Of Scope

- Deleting `.codex/plans` or recovered Windsurf source folders.
- Registering each historical archive record as active Notion work.
- Reclassifying the current active root `plans/*.md` files as archived.
- Changing code, ADG extraction, CI gates, or governance rules.

---

## Wave 1 - Inventory And Rules

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: A

**Authorization**: GRANTED - User explicitly requested plan creation and implementation.

**Phases**:
- **W1.1** - Inventory `plans/`, `.codex/plans`, `docs/reports/plans`, and recovered Windsurf folders | ~1K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.2** - Define archived metadata, collision-safe naming, and manifest shape | ~2K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- Source folder counts are captured.
- No active root plan is overwritten.
- Historical imports are marked `status: Archived` and `do_not_execute: true`.

---

## Wave 2 - Memorial Import

WAVE_ID: W2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: B

**Phases**:
- **W2.1** - Copy historical `.md` files into flat root `plans/` using archive-prefixed names | ~3K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W2.2** - Write `plans/historical-plans-memorial-manifest.csv` with source and target provenance | ~2K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- Imports are copies only; sources remain intact.
- Collision handling is deterministic.
- Metadata is prepended without destroying original content.

---

## Wave 3 - Verification

WAVE_ID: W3
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Phases**:
- **W3.1** - Verify file counts, target uniqueness, and archive metadata | ~2K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W3.2** - Summarize remaining cleanup decisions for `.codex/plans` | ~1K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- The root `plans/` folder is the single flat review plane.
- Current active root plans remain distinguishable from imported archived records.
- `.codex/plans` is left as source evidence pending a later pointer-only cleanup.

---

## Definition Of Done

| Item | Verification | Status |
|------|--------------|--------|
| Execution plan exists in root `plans/` | `plans/historical-plans-memorial-consolidation-d4e7a2.md` exists | DONE |
| Historical files copied into `plans/` only | Import manifest source and target paths reviewed | DONE |
| Imported records are non-executable | Aggregate metadata check for `status: Archived` and `do_not_execute: true` passed | DONE |
| No current active plan overwritten | Pre-import active filenames were preserved and collision-safe targets were used | DONE |
| Manifest written | `plans/historical-plans-memorial-manifest.csv` exists with source, target, hash, and import status | DONE |
| Source folders preserved | `.codex/plans`, `docs/reports/plans`, and recovered folders still exist | DONE |

---

## Supersedes

_None - this is a consolidation/memorialization plan, not a replacement for a specific execution plan._
