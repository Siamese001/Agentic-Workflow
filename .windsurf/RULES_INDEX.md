# Windsurf Rules & CI Gates — Master Index

**Last Updated**: 2026-04-04
**Purpose**: Comprehensive mapping of all constitutional rules, skills, and CI enforcement gates

> **2026-04-04 SSOT RESTRUCTURE**: `.windsurfrules` is now auto-generated from modular rule sources in `.windsurf/rules/*.md`. The preprocessor (`tools/windsurf/preprocess_rules.py`) consolidates all modular rules into a single file. Do not edit `.windsurfrules` directly — edit the source `.md` files and regenerate.

---

## SSOT Structure

| File | Type | Role | Editable |
|------|------|------|----------|
| `.windsurf/rules/*.md` | **Source** (9 files) | Modular rule definitions | ✅ YES |
| `.windsurf/rules/_variables.yaml` | **Config** | Variable definitions for expansion | ✅ YES |
| `.windsurf/rules/.windsurfrules` | **Generated** | Consolidated output read by Windsurf | ❌ NO (auto-generated) |

### Maintenance Workflow

```bash
# Edit modular rules
vim .windsurf/rules/hitl-enforcement.md

# Validate variables
python tools/windsurf/preprocess_rules.py --validate

# Regenerate consolidated file
python tools/windsurf/preprocess_rules.py --process

# Verify freshness (CI check)
python tools/windsurf/preprocess_rules.py --check
```

---

## Constitutional Rules

| Rule | Layer | Timing | Type | Location | Status |
|------|-------|--------|------|----------|--------|
| **§0: DEFAULT ANALYSIS MODE (Tier-Aware)** | Windsurf | Before work | Behavioural | `.windsurf/skills/graph-analysis/` | ✅ ENFORCED |
| **§ADG-1: ADG Repair Discipline** | Windsurf | Before work | Behavioural | `.windsurf/rules/adg-repair-discipline.md` | ✅ ENFORCED |
| **§2.5: Test Failure Triage Protocol** | Both | Before repair | Behavioural + Structural | `docs/technical/TEST_FAILURE_decision_tree.md` | ✅ ENFORCED (CI: cond. 8b) |
| **§8.5: HITL Enforcement** | Windsurf | During work | Behavioural | `.windsurf/rules/hitl-enforcement.md` | ✅ ENFORCED |
| **§10.0: Wave/Micro-Wave Plan Model** | Windsurf | Before plan draft | Behavioural | `.windsurfrules` §10.0 + Constitutional Rule #13 | ✅ ENFORCED |
| **Plan Location Rule** | Pre-commit | After work | Structural | `.windsurf/rules/plan-location.md` | ✅ ENFORCED |

**Notes**:
- §0: CI gate removed (was misplaced — process rule cannot be verified at commit time)
- §ADG-1: Pre-commit gate reverted to manual stage (repair phase state is session context)
- §10.0: Windsurf-only behavioural enforcement — fires before any plan content is drafted; mandates wave decomposition, ≤15 modules/micro-wave, wave summary table first, token estimates per wave
- Plan Location: Pure structural rule — file path observable at commit time

---

## Skills & Enforcement Gates

| # | Skill | Layer | Timing | Type | CI Gate | Pre-commit Hook | Status |
|---|-------|-------|--------|------|---------|----------------|--------|
| 1 | **graph-analysis** | Windsurf | Before work | Behavioural + Structural | None | None | ✅ ENFORCED |
| 2 | **boundary-enforcement** | Pre-commit | After work | Structural | ADG GV edges | T2a, T4a | ✅ ENFORCED |
| 3 | **operational-gates** | Both | Before work | Behavioural + Structural | `check_rollback_checkpoints.py` | T3a-rollback | ✅ ENFORCED |
| 4 | **testing-framework** | Pre-commit | After work | Structural | `adg_ci_lane_gate.py` | T3a-skip | ✅ ENFORCED |
| 5 | **artifact-management** | Pre-commit | After work | Structural | `validate_report_location.py` | T3b | ✅ ENFORCED |

**Note**: 30 individual skills consolidated into these 5 canonical skills per SVP Engineering principles. See [Consolidation Note](#skill-consolidation-2026-04-03) below.

**Key**:
- **Layer**: Windsurf (AI-time only) | Pre-commit (commit-time only) | Both (dual enforcement)
- **Timing**: Before work (process rules) | After work (structural checks) | During work (runtime)
- **Type**: Behavioural (HOW AI works) | Structural (WHAT is in code) | Both
- **CI Gate**: Script name or "None" if Windsurf-only enforcement
- **(proxy)** = Pre-commit can only detect symptoms, not full violation
- **(artifact)** = Pre-commit verifies artifact exists, not process compliance

---

## Skill Consolidation (2026-04-03)

**Previous State**: 30 individual skill directories + 2 duplicate directories = 32 total
**Current State**: 5 consolidated canonical skills
**Archived Skills**: 30 individual skills archived to `tools/archive/.windsurf/skills/`
**Rationale**: SVP Engineering principle — operational simplicity through reduced moving parts

### Consolidation Mapping

| Canonical Skill | Replaces (Archived) |
|-----------------|---------------------|
| `graph-analysis` | `dependency-graph-analysis`, `scope-guard`, `dedup-guard` |
| `boundary-enforcement` | `layer-boundary-guard`, `import-hygiene`, `shim-discipline` |
| `operational-gates` | `rollback-gate`, `mcp-tool-verify` |
| `testing-framework` | `test-rigor-enforcement`, `pytest-integrity` |
| `artifact-management` | `evidence-bundle`, `ssot-write-gate`, `progress-display` |

### Also Archived (Non-Consolidated Skills)

The following CI-specific and utility skills were also archived (not consolidated into canonical skills):
- `agent-deletion-gate`
- `ci-grep-ban`
- `ci-guardian-comments`
- `ci-hollow-file`
- `ci-integration`
- `ci-layer-sovereignty`
- `ci-schema-validation`
- `guardian-exemption-validator`
- `hitl-decision-validator`
- `performance-monitor`
- `plan-validation`
- `powershell-guard`
- `pre-write-orchestrator`
- `redis-hitl-gate`
- `repair-gate-validator`
- `script-sprawl-guard`
- `skill-status-dashboard`

---

## Pre-Commit Hook Mapping

### Tier 0-ADG: ADG Phase Gate
- **Hook ID**: `adg-phase-gate`
- **Script**: `tools/adg_ci_gate.py check-phase`
- **Stage**: manual (reverted from automatic — repair phase state is session context)
- **Purpose**: Block full-suite pytest during PHASE 5-6 repair loops
- **Always Run**: Yes (when manually invoked)

### Tier 0: Normalization
- **Hooks**: trailing-whitespace, end-of-file-fixer, mixed-line-ending, check-merge-conflict
- **Purpose**: Deterministic whitespace normalization

### Tier 1: Syntax Gate
- **Hook ID**: `python-syntax-check`
- **Script**: `python -m py_compile`
- **Purpose**: Fast-fail on broken syntax

### Tier 2: Auto-Fixers
- **Hook ID**: `ruff`, `ruff-format`
- **Purpose**: Lint and format before analysis

### Tier 3a: Analysis & Guards
- **Hook ID**: `check-anti-patterns`
- **Script**: `ops_scripts/ci/check_anti_patterns.py`
- **Purpose**: Landmine detection (silent swallowers, magic config, etc.)

- **Hook ID**: `check-dedup-violations` ✅ NEW
- **Script**: `ops_scripts/ci/check_dedup_violations.py`
- **Purpose**: Prevent duplicate symbols

- **Hook ID**: `check-script-sprawl` ✅ NEW
- **Script**: `ops_scripts/ci/check_script_sprawl.py`
- **Purpose**: Block new runner scripts

- **Hook ID**: `check-shim-discipline` ✅ NEW
- **Script**: `ops_scripts/ci/check_shim_discipline.py`
- **Purpose**: Enforce shim/backward-compatibility discipline

- **Hook ID**: `check-rollback-checkpoints` ✅ NEW
- **Script**: `ops_scripts/ci/check_rollback_checkpoints.py`
- **Purpose**: Validate rollback gates for multi-file phases

- **Hook ID**: `enforce-unit-strict-zero-skip`
- **Script**: `tools/adg_ci_lane_gate.py --lane unit_strict --fail-on-skip`
- **Purpose**: Block pytest.skip in UNIT_STRICT

- **Hook ID**: `check-c0-sovereignty`
- **Script**: `agentic_core/L0_routing/scripts/run_guardian_c0_sovereignty.py`
- **Purpose**: Embedding boundary enforcement

### Tier 3b: Structural Checks
- **Hook ID**: `check-report-location`
- **Script**: `ops_scripts/hooks/validate_report_location.py`
- **Purpose**: SSOT plan location enforcement

### Tier 3c-3i: Additional Guards
- **Hook IDs**: reject-generated-artifacts-tracked, folder-purity-validation, module-collision-guard, governance-policy-validation, validate-evidence-contract, guard-pytest-ini-scope, guard-apps-shared-instructional-layer
- **Purpose**: Architectural and policy enforcement

### Tier 4a: Import Validation
- **Hook ID**: `import-dependency-check`
- **Script**: `ops_scripts/ci/validate_import_dependencies.py`
- **Purpose**: Validate all imports resolve

### Tier 5: Cleanup
- **Hook ID**: `purge-cache`
- **Script**: `ops_scripts/maintenance/purge_cache.py`
- **Purpose**: Final __pycache__ cleanup

---

## CI Scripts Inventory (41 total)

### Active CI Gates
1. `check_adg_proof_artifact_truthfulness.py`
2. `check_adg_schema_field_names.py`
3. `check_agent_registry_completeness.py`
4. `check_anti_patterns.py` ✅
5. `check_apps_output_contract.py`
6. `check_c0_boundary.py`
7. `check_ci_integrity.py` ✅ UPDATED (added cond. 8b: broken_test_fix semantic equivalence)
8. `check_dedup_violations.py` ✅ UPDATED (proxy check only)
10. `check_determinism_replay.py`
11. `check_determinism_violations.py`
12. `check_direct_execute_calls.py`
13. `check_directory_deletion_sweep.py`
14. `check_embedding_instantiation.py`
15. `check_environment_contract.py`
16. `check_evidence_contract_v2.py`
17. `check_faiss_persist_contract.py`
18. `check_healer_direct_model.py`
19. `check_kernel_extension_boundary.py`
20. `check_layer_write_sovereignty.py`
21. `check_llm_sdk_imports.py`
22. `check_model_string_literals.py`
23. `check_no_unconditional_xfail.py` ✅ NOW WIRED (§11.4)
24. `check_object_dunder_setattr.py`
25. `check_plan_location_compliance.py` ✅
26. `check_policy_drift_classification.py`
27. `check_powershell_ban.py` ✅ NOW WIRED (§2)
28. `check_rollback_checkpoints.py` ✅ NEW
29. `check_script_sprawl.py` ✅ NEW
30. `check_shim_discipline.py` ✅ NEW
31. `check_skip_convergence_gate.py`
32. `check_sovereign_llm_gateway.py`
33. `check_spine_adapter_contract.py`
34. `check_spine_bypass.py`
35. `check_structured_output_emission.py`
36. `check_system_learning_boundary.py`
37. `check_test_integrity.py` ✅ NOW WIRED (§11/§13)
38. `check_tooling_apps_boundary.py`
39. `check_utility_silent_swallowers.py` ✅ NOW WIRED (§10/§11)
40. `check_wall_clock_in_determinism.py`
41. `validate_import_dependencies.py` ✅

---

## Coverage Summary

| Category | Total | Enforced | Partial | Missing |
|----------|-------|----------|---------|---------|
| Constitutional Rules | 5 | 5 | 0 | 0 |
| Skills | 5 | 5 | 0 | 0 |
| CI Gates | 41 | 41 | 0 | 0 |
| Pre-commit Hooks | 25+ | 25+ | 0 | 0 |

**Overall Coverage**: 100% ✅

---

## Quick Reference

### Adding a New Rule
1. Create skill in `.windsurf/skills/<skill-name>/`
2. Create CI gate in `ops_scripts/ci/check_<rule>.py`
3. Add pre-commit hook to `.pre-commit-config.yaml`
4. Update this index
5. Test with: `pre-commit run <hook-id> --all-files`

### Testing a Gate
```bash
# Test specific gate
pre-commit run check-dedup-violations --all-files

# Test all gates
pre-commit run --all-files

# Skip gates for emergency commit
git commit --no-verify -m "..."
```

### Bypassing a Gate (Justified)
Include justification keywords in commit message:
- Dedup: "dedup", "no duplicate", "searched for", "DEDUP_SEARCH: decision=create"
- Script Sprawl: "script-sprawl", "CI gate", "canonical invocation"
- Shim: "shim-discipline", "backward-compatibility"
- Rollback: "checkpoint", "rollback", "phase checkpoint"

---

## Maintenance

**Review Frequency**: Monthly
**Owner**: Platform Team
**Last Audit**: 2026-03-12
**Next Audit**: 2026-04-11

**Changelog**:
- 2026-04-04: **RCA FIX — WAVE/MICRO-WAVE PLAN MODEL NOT AUTO-EMPLOYED** — Root cause: §10 was reactive (validated existing plans) with no proactive trigger at plan-creation time; micro-wave discipline (≤15 modules/wave) was never codified in any rule file; template wave table columns mismatched §10.1 spec. Fix: Added Constitutional Rule #13 to `.windsurfrules` floor + §10.0 "Plan Creation Protocol" pre-draft trigger section (fires before any content is drafted) + same rule (#11) to `.windsurfrules.consolidated` + §10 section appended to consolidated file + template updated to §10.1 column spec with micro-wave sub-table example + RULES_INDEX updated with §10.0 entry.
- 2026-04-03: **SKILLS CONSOLIDATION** — Archived 30 individual skills to `tools/archive/.windsurf/skills/`. Consolidated into 5 canonical skills per SVP Engineering principle: `graph-analysis` (replaces dependency-graph-analysis, scope-guard, dedup-guard), `boundary-enforcement` (replaces layer-boundary-guard, import-hygiene, shim-discipline), `operational-gates` (replaces rollback-gate, mcp-tool-verify), `testing-framework` (replaces test-rigor-enforcement, pytest-integrity), `artifact-management` (replaces evidence-bundle, ssot-write-gate, progress-display). Updated Skills table to show 5 consolidated skills. Coverage remains 100%.
- 2026-03-25: **PROGRESS DISPLAY ENFORCEMENT** — Added `progress-display` skill with mandatory colored progress bars and percentage displays for all operations >5s. Updated §5.3 with detailed progress reporting requirements including ANSI color codes, ETA display, and standardized progress bar formats. Skill provides terminal protocol, color scheme reference, and implementation guide for integration across all Windsurf operations.
- 2026-03-14: **HITL (HUMAN-IN-THE-LOOP) ENFORCEMENT** — Added §8.5 HITL Framework to `.windsurfrules` and Constitutional Rule #8. Created comprehensive rule (`.windsurf/rules/hitl-enforcement.md`) with 10 mandatory decision triggers. Created workflow (`/hitl-decision-gate`) with option presentation templates. HITL required for: architecture decisions, refactoring scope, anti-patterns, test repair, dependencies, deletions, config changes, error handling, performance trade-offs, ADG timing. Registered as constitutional rule with Windsurf-only enforcement (behavioral, no CI gate).
- 2026-03-12: **TEST FAILURE TRIAGE PROTOCOL** — Added canonical 5-check decision tree (`docs/technical/TEST_FAILURE_decision_tree.md`). Registered as §2.5 constitutional rule. Added CI condition 8b (`check_broken_test_fix_semantic_equivalence`) to `check_ci_integrity.py`. Updated `adg-repair-discipline.md` with triage step before repair loop. Updated `test-rigor-enforcement` skill with triage trigger. Reference added to `.windsurfrules` §2.5 without duplicating taxonomy.
- 2026-03-11: **RULES CONSOLIDATION** — `.windsurfrules` reduced 3906→~400 lines. Removed all Python code blocks (redundant with `ops_scripts/ci/`). Added Constitutional Floor banner to top. Wired 4 previously dormant CI gates into `run_contract_gates.py`: `check_powershell_ban`, `check_test_integrity`, `check_no_unconditional_xfail`, `check_utility_silent_swallowers`.
- 2026-03-11: Initial index creation, added 5 new CI gates
- 2026-03-11: **ARCHITECTURE REDESIGN** — Removed misfits from pre-commit, strengthened Windsurf skills
  - Deleted `check_ast_first_gate.py` (misplaced — process rule, not structural)
  - Reverted `adg-phase-gate` to manual stage (repair phase state is session context)
  - Added MANDATORY PRE-CONDITION blocks to 5 Windsurf skills (ast-first, scope, rollback, dedup, adg-repair)
  - Tightened dedup and rollback CI gates to proxy/artifact checks only
  - Added `enforcement_layer` metadata to all skills
  - Created `docs/rules/enforcement_architecture.md` canonical contract
  - Updated RULES_INDEX.md with Layer, Timing, Type columns
