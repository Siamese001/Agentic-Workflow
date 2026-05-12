# Simplified Plan Format Specification

## Version

FORMAT_VERSION: simplified-plan-format-v1

## Purpose

This specification defines the canonical machine-readable format for all new or actively modified plans in the Agentic-Workflow repository. The format enables reliable automated tracking of wave completion, phase status, and scope changes without requiring table cell mutations.

## Philosophy

- **Forward-only**: This specification applies to new plans and active modifications only. Historical plans are not required to migrate.
- **Machine-first**: All status fields must be parseable by simple regex without emoji handling or table cell extraction.
- **Human-readable**: Structure remains intuitive for human readers while being deterministic for automation.
- **Tables are read-only**: Tables may exist for reference, but no script updates table cells. All live status lives in single-line markers.

---

## Required Top-Level Markers

Every plan MUST declare these markers before any content:

```markdown
FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: <TODO|IN_PROGRESS|DONE|BLOCKED|DEFERRED|WAITING|RETIRED|ARCHIVED>
CURRENT_WAVE: <W0|W1|W2|...>
LAST_COMPLETED_WAVE: <NONE|W1|W2|...>
LAST_UPDATED: <YYYY-MM-DD>
```

### Marker Definitions

| Marker | Enum Values | Description |
|--------|-------------|-------------|
| FORMAT_VERSION | `simplified-plan-format-v1` | Parser version selector |
| PLAN_STATUS | TODO, IN_PROGRESS, DONE, BLOCKED, DEFERRED, WAITING, RETIRED, ARCHIVED | Overall plan state |
| CURRENT_WAVE | W0, W1, W2, ... | Active wave identifier |
| LAST_COMPLETED_WAVE | NONE, W1, W2, ... | Most recently completed wave |
| LAST_UPDATED | ISO 8601 date (YYYY-MM-DD) | Last modification date |

### PLAN_STATUS Enum Semantics

- **TODO** — Not yet started, awaiting execution
- **IN_PROGRESS** — Active execution in current wave
- **DONE** — All waves completed, all DoD satisfied
- **BLOCKED** — Cannot proceed without external resolution
- **DEFERRED** — Intentionally delayed (time/volume gated)
- **WAITING** — Paused pending dependency
- **RETIRED** — Abandoned or superseded by another plan
- **ARCHIVED** — Long-term archive (read-only historical)

---

## Per-Wave Markers

Each wave MUST declare these markers before any table or prose content:

```markdown
## Wave N — <Title>

WAVE_ID: W<N>
WAVE_STATUS: <TODO|IN_PROGRESS|DONE|BLOCKED>
WAVE_COMPLETE: <YES|NO>
AUTHORIZATION_STATUS: <NOT_REQUIRED|REQUIRED|GRANTED|DENIED>
CHECKPOINT: <A|B|C|...>
```

### Wave Marker Definitions

| Marker | Enum Values | Description | Required |
|--------|-------------|-------------|----------|
| WAVE_ID | W1, W2, W3, ... | Wave identifier | Yes |
| WAVE_STATUS | TODO, IN_PROGRESS, DONE, BLOCKED | Wave execution state | Yes |
| WAVE_COMPLETE | YES, NO | Whether wave acceptance criteria are met | Yes |
| AUTHORIZATION_STATUS | NOT_REQUIRED, REQUIRED, GRANTED, DENIED | User authorization state | If wave requires explicit approval |
| CHECKPOINT | A-Z | Checkpoint identifier for gate tracking | Yes |

### AUTHORIZATION_STATUS Semantics

- **NOT_REQUIRED** — Wave can proceed without explicit user authorization (default if omitted)
- **REQUIRED** — User must explicitly approve before execution (e.g., modifies shared templates, CI, governance rules)
- **GRANTED** — User has authorized wave execution; may proceed
- **DENIED** — User has declined authorization; wave must become DEFERRED, RETIRED, or await re-authorization

### AUTHORIZATION_STATUS Rules

1. If a wave declares "requires user authorization" in prose or scope, AUTHORIZATION_STATUS marker must be present.
2. AUTHORIZATION_STATUS: REQUIRED is valid with WAVE_STATUS: TODO (awaiting authorization is not a BLOCKED state).
3. WAVE_STATUS must not be BLOCKED solely because authorization is required. BLOCKED indicates technical/policy/dependency failures.
4. AUTHORIZATION_STATUS: GRANTED is required before executing any wave that modifies shared templates, CI, governance rules, or other broad shared surfaces.
5. AUTHORIZATION_STATUS: DENIED prevents execution and requires explicit user re-authorization or wave transition to DEFERRED/RETIRED.

### WAVE_COMPLETE Logic

- WAVE_COMPLETE may be YES only when:
  - All phases in that wave have PHASE_COMPLETE: YES, OR
  - All incomplete phases are explicitly DEFERRED with DEFERRED_SCOPE marker
  - If AUTHORIZATION_STATUS was REQUIRED, it must be GRANTED (or explicitly waived for non-shared-surface waves)
- WAVE_COMPLETE must be NO if any phase is still TODO or IN_PROGRESS without deferral
- WAVE_COMPLETE must be NO if AUTHORIZATION_STATUS is DENIED

---

## Per-Phase Markers

Each phase MUST declare inline markers within the wave's phase list:

```markdown
**Phases**:
- **W<N>.<M>** — <Title> | <tokens> | PHASE_STATUS: <TODO|IN_PROGRESS|DONE|BLOCKED> | PHASE_COMPLETE: <YES|NO>
```

### Phase Marker Definitions

| Marker | Enum Values | Description |
|--------|-------------|-------------|
| PHASE_ID | W1.1, W1.2, W2.1, ... | Phase identifier (wave.phase) |
| PHASE_STATUS | TODO, IN_PROGRESS, DONE, BLOCKED | Phase execution state |
| PHASE_COMPLETE | YES, NO | Whether phase acceptance criteria are met |

### Phase Semantics

- Phases are linear within a wave (W1.1 → W1.2 → W1.3)
- PHASE_COMPLETE: YES allows progression to next phase
- PHASE_STATUS: BLOCKED prevents wave completion until resolved

---

## Definition of Done Markers

Each DoD item MUST declare inline status:

```markdown
DoD-<N>: <Criterion description>
- Evidence: <What proves completion>
- Status: <TODO|IN_PROGRESS|DONE|BLOCKED|DEFERRED>
```

### DoD Status Enum

| Status | Meaning |
|--------|---------|
| TODO | Not yet addressed |
| IN_PROGRESS | Work ongoing |
| DONE | Criterion satisfied |
| BLOCKED | Cannot complete due to external dependency |
| DEFERRED | Explicitly deferred to future work |

### PLAN_STATUS: DONE Requirements

PLAN_STATUS may be DONE only when:
- All required DoD items have Status: DONE, OR
- Incomplete items are explicitly DEFERRED with DEFERRED_SCOPE marker
- LAST_COMPLETED_WAVE matches the highest wave number
- All waves have WAVE_COMPLETE: YES (or DEFERRED)

---

## Scope Expansion Markers

When scope changes during execution, these markers MUST be used:

### Step 1: DISCOVERED_SCOPE
```markdown
DISCOVERED_SCOPE: plan=<slug-6hex> wave=<N> phase=<M> gap="<what was found>" impact="<severity>"
```

### Step 2: AUTHORIZATION_DECISION
```markdown
AUTHORIZATION_DECISION: plan=<slug-6hex> decision=<ACCEPTED|DEFERRED|SPLIT_TO_NEW_PLAN|REJECTED> authorized_by=<user|author_gate|self> decisive_reason="<why>"
```

### Step 3: DEFERRED_SCOPE (when applicable)
```markdown
DEFERRED_SCOPE: plan=<slug-6hex> item="<description>" reason="<why deferred>" tracked_in="<next plan or marker>"
```

### Step 4: SCOPE_EXPANSION (only after ACCEPTED)
```markdown
SCOPE_EXPANSION: plan=<slug-6hex> reason="<summary>" added="<waves/phases/gaps>" authorized="yes"
```

---

## Format Constraints

### Allowed

- Single-line markers with colon separator
- Bullet lists for phases, artifacts, checklists
- Read-only tables AFTER all live markers
- Code blocks for examples
- Emojis in prose (not in canonical status)

### Forbidden

- Status stored only in table cells
- Emojis in canonical status fields (PLAN_STATUS, WAVE_STATUS, PHASE_STATUS, DOD_STATUS)
- Nested tables (tables within tables)
- Live status markers inside table cells
- Missing FORMAT_VERSION
- Unknown enum values

### Table Usage Rules

1. Tables may appear ONLY after all live markers for a section
2. Tables are READ-ONLY reference material
3. No script shall parse or update table cells for status
4. Tables may contain emojis for human readability
5. Tables may summarize what markers already declare

---

## Example: Minimal Compliant Plan

```markdown
---
plan_id: example-minimal-a1b2c3
plan_type: governance
touches_agentic_core: false
touches_governance_ci: false
touches_windsurf_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# Minimal Example Plan

One-sentence summary.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W0
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-05-12

---

## Wave 1 — Single Wave Plan

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
CHECKPOINT: A

**Phases**:
- **W1.1** — Do the thing | ~1K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- The thing is done

---

## Definition of Done

DoD-1: The thing is done
- Evidence: File exists at path
- Status: TODO

---

## Scope Expansion Authorization

When scope is discovered:

### Four-Step Discipline

Step 1: DISCOVERED_SCOPE marker
Step 2: AUTHORIZATION_DECISION marker
Step 3: Plan updates (if ACCEPTED)
Step 4: SCOPE_EXPANSION marker

---

PLAN_CREATED: plan=example-minimal-a1b2c3
```

---

## Validation Checklist

A plan is format-compliant when:

- [ ] FORMAT_VERSION declared as first marker
- [ ] PLAN_STATUS uses canonical enum (not emoji, not prose)
- [ ] CURRENT_WAVE declared
- [ ] LAST_COMPLETED_WAVE declared
- [ ] LAST_UPDATED declared
- [ ] Every wave has WAVE_ID, WAVE_STATUS, WAVE_COMPLETE, CHECKPOINT
- [ ] Every phase has PHASE_ID, PHASE_STATUS, PHASE_COMPLETE
- [ ] No canonical status field contains emojis
- [ ] All live status markers appear before any table
- [ ] Tables (if any) are read-only reference

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| simplified-plan-format-v1 | 2026-05-12 | Initial specification |
