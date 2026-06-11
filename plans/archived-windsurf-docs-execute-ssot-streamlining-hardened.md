---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\execute-ssot-streamlining-hardened.md'
original_relative_path: 'execute-ssot-streamlining-hardened.md'
source_sha256: 622b6f109f01144c3b34e7d11c7cca1a5fe83b19b699d6ddcd191c462202aa19
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-04'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# execute_ssot Streamlining Plan

Consolidate the execute_ssot healing pipeline from 11 agents and 5,485 lines to a leaner, deterministic architecture by eliminating deprecated shims, merging agents with genuine overlap, collapsing the 3-class decision engine, and streamlining the phase execution model.

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Findings From Deep Review

### Agent Roster (11 active keys + 1 deprecated alias)
| Key | Class | Lines | Role |
|---|---|---|---|
| `reconciler` | FilesystemSSOTReconcilerAgent | 1,450 | Folder-level drift detection + repair |
| `location` | **LocationAgent (shim)** | **79** | Shim → delegates to LocationValidatorAgent |
| `hierarchy` | HierarchyAgent | 1,797 | Folder structure + depth enforcement |
| `arch_governor` | ArchitectureGovernorAgent | 1,649 | Layer boundaries, naming, gravity, healing plans |
| `gravity_repair` | GravityLeakRepairAgent | 689 | Upward-import repair |
| `system_architect` | SystemArchitectAgent | 451 | Import graph, nesting, file size checks |
| `file_classification` | FileClassificationAgent | 5,609 | Naming, layer alignment, sovereignty purge |
| `observability_probe` | ObservabilityProbeExecutorAgent | — | Conversational pattern scan |
| `conversational_repair` | *(alias for observability_probe)* | — | **Dead deprecated alias** |
| `cognitive_disposition` | CognitiveDispositionAgent | — | AI-powered violation triage |
| `root_hygiene` | RootHygieneAgent | — | Root-level cleanup |

---

## Confirmed Overlaps and Redundancies

**1. LocationAgent is a live deprecated shim**
`agents["location"]` → `LocationAgent` (79 lines) → immediately delegates to `LocationValidatorAgent`. Phase 1 already instantiates `LocationValidatorAgent` directly via `_get_location_validator_agent()`. The shim is pure indirection with no added value.

**2. SystemArchitectAgent is nearly fully covered by ArchitectureGovernorAgent**
`execute_phase3_validation_impl` already skips it for non-AC territories. Its 4 checks: (a) core module existence, (b) no deep nesting >4 levels, (c) no large files >1000 lines, (d) circular imports — are all covered by `ArchitectureGovernorAgent._get_structure_validator()` (lazy-loads `StructuralValidatorAgent` with `check_gravity=True, check_hierarchy=True`). Only check (c) file-size is unique and trivial to add as a method.

**3. GravityLeakRepairAgent is double-invoked**
The pipeline calls `_run_gravity_repair_global()` AND `ArchitectureGovernorAgent._get_gravity_repair_agent()` internally. These are two separate passes over the same violations. Noted for future consolidation (deferred — needs deeper audit of arch_governor heal interaction).

**4. Decision engine is a 3-level class chain for one singleton**
`AutonomousDecisionEngine → EnhancedAutonomousDecisionEngine → SovereignDecisionEngine`. Always instantiated as `SovereignDecisionEngine`. The intermediate class only adds `analyze_violations_with_cognitive_disposition()`. The base adds core scoring. Three classes, one object. All behavior can live in one flat class.

**5. FileClassificationAgent double-scans every territory**
Phase 1: `file_classification.run(validate_only=True, dry_run=True)` — full scan.
Phase 2.5: `file_classification.heal_repository()` — full scan again.
No state is shared. Every file in the territory is walked twice.

**6. `conversational_repair` is a dead alias**
Registered as `ObservabilityProbeExecutorAgent`, never dispatched by any phase function, kept only for compat. Zero risk to remove.

**7. Phase execution order is broken**
`_legacy_main` actual execution order: P1 → P2 → **P3-validation** → **P2.5-alignment**. Phase 3 runs *before* Phase 2.5 in the code, despite the numbering implying the reverse. The half-step numbering (2.5, 4.5) also makes the pipeline hard to reason about.

---

## Implementation Plan (6 items, ranked value/effort)

### Item 1 — Remove dead `conversational_repair` alias *(, Risk: None)*
- Delete `"conversational_repair": ObservabilityProbeExecutorAgent` from `agents` dict
- Remove from `CANONICAL_ROSTER_KEYS`, `AGENT_DEPENDENCIES`, `EXECUTION_PLAN`
- Pre-check: `grep -r "conversational_repair"` across codebase to confirm no live dispatch

### Item 2 — Wire `location` directly to `LocationValidatorAgent` *(, Risk: Low)*
- In `_get_l5_agent_roster()`, import and return `LocationValidatorAgent` instead of `LocationAgent`
- `LocationAgent` shim stays on disk for any external callers — only pipeline entry changes
- Aligns with the existing `_get_location_validator_agent()` helper already used in Phase 1

### Item 3 — Fix phase execution order + renumber cleanly *(1 h, Risk: Low)*

Current broken order in code: P1 → P2 → **P3** → **P2.5** → P4 → P4.5 → P5

Corrected sequential map:
| Old Label | New Label | Name |
|---|---|---|
| Phase 1 | Phase 1 | Discovery |
| Phase 2 | Phase 2 | Reconciliation |
| Phase 3 (runs before 2.5!) | Phase 3 | Validation |
| Phase 2.5 | Phase 4 | Structural Alignment |
| Phase 4 | Phase 5 | Healing |
| Phase 4.5 | Phase 6 | Additional Agents |
| Phase 5 | Phase 7 | Certification |

- Rename `execute_phase2_alignment` → `execute_phase4_alignment` etc.
- Update `EXECUTION_PLAN` entries and `--plan` output
- Update any AST contract tests referencing phase names

### Item 4 — Merge `system_architect` into `arch_governor` *(3 h, Risk: Low)*
- Add `check_file_sizes(territory)` method to `ArchitectureGovernorAgent` (mirrors SystemArchitect's >1000 lines check)
- Replace `sys_arch.validate_core_architecture()` call in `execute_phase3_validation_impl` with `arch_gov.check_file_sizes(territory)` for AC-layer territories
- Remove `system_architect` key from `agents` dict, `CANONICAL_ROSTER_KEYS`, `AGENT_DEPENDENCIES`, `EXECUTION_PLAN`
- `SystemArchitectAgent.py` file stays on disk for any external callers
- All 4 validation checks remain, just consolidated

### Item 5 — Single-pass FileClassificationAgent with scan cache *(3 h, Risk: Low-Medium)*
- Add `_last_scan_result` cache to `FileClassificationAgent`
- Phase 1 stores: `state_mgr.state["classification_scan"] = file_classifier.run(...)`
- Phase 2.5 (now Phase 4) passes: `pascal.heal_repository(cached_scan=state_mgr.state.get("classification_scan"))`
- `heal_repository` skips scan step when `cached_scan` is provided; falls back gracefully if absent
- Eliminates one full-repo file walk per territory per run

### Item 6 — Flatten 3-class decision engine to 1 flat class *(4 h, Risk: Medium)*
- Inline `AutonomousDecisionEngine` and `EnhancedAutonomousDecisionEngine` methods directly into `SovereignDecisionEngine`
- Keep identical public interface (no call site changes)
- Add backward compat aliases: `AutonomousDecisionEngine = SovereignDecisionEngine`
- All 3 classes are in `execute_ssot.py` — purely in-file refactor
- Pre-check: search tests for class-hierarchy assertions

---

## What Is NOT Changing

- `GravityLeakRepairAgent` stays separate (double-invocation is a separate, deeper issue — deferred)
- `CognitiveDispositionAgent` stays (optional LLM advisory path)
- `ObservabilityProbeExecutorAgent` / `RootHygieneAgent` stay (no overlap identified)
- All confidence gating, sovereignty tokens, routing logic unchanged
- No SSOT config, test infra, or evidence contract changes

---

## Target State

| Metric | Before | After |
|---|---|---|
| Agent keys in roster | 11 (+1 dead alias) | 9 |
| Decision engine classes | 3 (chain) | 1 (flat) |
| File scans per territory | 2 (classification) | 1 |
| Phase labels with `.5` suffix | 2 | 0 |
| Broken phase execution order | Yes | Fixed |

---

## Acceptance Criteria

- `python -m pytest -q --color=no` full suite passes, no deselection
- `--plan` output shows sequential phases 1-7, no `.5` suffixes
- `CANONICAL_ROSTER_KEYS` has <=9 entries
- `agents` dict in `_legacy_main` has <=9 entries
- No new files created; in-place refactor only
- `grep conversational_repair` returns zero hits in pipeline code

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

