# Windsurf Rules & CI Gates — Master Index

**Last Updated**: 2026-03-11
**Purpose**: Comprehensive mapping of all constitutional rules, skills, and CI enforcement gates

> **2026-03-11 CONSOLIDATION:** `.windsurfrules` reduced from 3906 → ~400 lines. All Python implementation code removed — it already lives in `ops_scripts/ci/`. Rules file now contains hard rules, forbidden/required patterns, and CI script cross-references only. 4 previously unwired CI gates added to `run_contract_gates.py`.

---

## Constitutional Rules

| Rule | Layer | Timing | Type | Location | Status |
|------|-------|--------|------|----------|--------|
| **§0: DEFAULT ANALYSIS MODE** | Windsurf | Before work | Behavioural | `.windsurf/skills/ast-first-gate/` | ✅ ENFORCED |
| **§ADG-1: ADG Repair Discipline** | Windsurf | Before work | Behavioural | `.windsurf/rules/adg-repair-discipline.md` | ✅ ENFORCED |
| **Plan Location Rule** | Pre-commit | After work | Structural | `.windsurf/rules/plan-location.md` | ✅ ENFORCED |

**Notes**:
- §0: CI gate removed (was misplaced — process rule cannot be verified at commit time)
- §ADG-1: Pre-commit gate reverted to manual stage (repair phase state is session context)
- Plan Location: Pure structural rule — file path observable at commit time

---

## Skills & Enforcement Gates

| # | Skill | Layer | Timing | Type | CI Gate | Pre-commit Hook | Status |
|---|-------|-------|--------|------|---------|----------------|--------|
| 1 | **AST-First Gate** | Windsurf | Before work | Behavioural | ~~Removed~~ | ~~T3a-ast~~ | ✅ ENFORCED (Windsurf only) |
| 2 | **Dedup Guard** | Both | Before work | Behavioural + Structural | `check_dedup_violations.py` (proxy) | T3a-dedup | ✅ ENFORCED |
| 3 | **Dependency Graph Analysis** | Windsurf | Before work | Behavioural | None | None | ✅ ENFORCED (Windsurf only) |
| 4 | **Evidence Bundle** | Windsurf | During work | Behavioural | None | None | ✅ WORKFLOW-ENFORCED |
| 5 | **Import Hygiene** | Both | After work | Structural | Ruff F401, `validate_import_dependencies.py` | T2a, T4a | ✅ ENFORCED |
| 6 | **Layer Boundary Guard** | Pre-commit | After work | Structural | ADG GV edges | None | ✅ ENFORCED |
| 7 | **MCP Tool Verify** | Windsurf | During work | Behavioural | None | None | ✅ RUNTIME-ENFORCED |
| 8 | **Pytest Integrity** | Pre-commit | After work | Structural | `adg_ci_lane_gate.py --fail-on-skip` | T3a-skip | ✅ ENFORCED |

| 9 | **Rollback Gate** | Both | Before work | Behavioural + Structural | `check_rollback_checkpoints.py` (artifact) | T3a-rollback | ✅ ENFORCED |
| 10 | **Scope Guard** | Windsurf | Before work | Behavioural | None | None | ✅ ENFORCED (Windsurf only) |
| 11 | **Script Sprawl Guard** | Both | Before work | Behavioural + Structural | `check_script_sprawl.py` | T3a-sprawl | ✅ ENFORCED |
| 12 | **Shim Discipline** | Both | Before work | Behavioural + Structural | `check_shim_discipline.py` | T3a-shim | ✅ ENFORCED |
| 13 | **SSOT Write Gate** | Pre-commit | After work | Structural | `validate_report_location.py` | T3b | ✅ ENFORCED |
| 14 | **Test Rigor Enforcement** | Pre-commit | After work | Structural | `adg_ci_lane_gate.py` | T3a-skip | ✅ ENFORCED |

**Key**:
- **Layer**: Windsurf (AI-time only) | Pre-commit (commit-time only) | Both (dual enforcement)
- **Timing**: Before work (process rules) | After work (structural checks) | During work (runtime)
- **Type**: Behavioural (HOW AI works) | Structural (WHAT is in code) | Both
- **CI Gate**: Script name or "None" if Windsurf-only enforcement
- **(proxy)** = Pre-commit can only detect symptoms, not full violation
- **(artifact)** = Pre-commit verifies artifact exists, not process compliance

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

- **Hook ID**: `check-ast-first-gate` ✅ NEW
- **Script**: `ops_scripts/ci/check_ast_first_gate.py`
- **Purpose**: Enforce §0 DEFAULT ANALYSIS MODE

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
7. `check_ci_integrity.py`
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
| Constitutional Rules | 3 | 3 | 0 | 0 |
| Skills | 14 | 14 | 0 | 0 |
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
**Last Audit**: 2026-03-11
**Next Audit**: 2026-04-11

**Changelog**:
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
