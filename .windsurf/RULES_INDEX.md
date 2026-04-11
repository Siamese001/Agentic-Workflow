# Windsurf Rules & CI Gates — Master Index

**Last Updated**: 2026-04-15
**Purpose**: Comprehensive mapping of all constitutional rules, skills, and CI enforcement gates

> **2026-04-09 SSOT CLARIFICATION**: Windsurf discovers rules directly from `.windsurf/rules/*.md` (one file per rule, 12,000 char limit each). There is no preprocessor — rule files ARE the source of truth. The previously generated `.windsurfrules` aggregate has been deleted.

---

## SSOT Structure

| File | Type | Role | Editable |
|------|------|------|----------|
| `.windsurf/rules/*.md` | **Source** (15 files) | Modular rule definitions — discovered directly by Windsurf | ✅ YES |
| `AGENTS.md` (repo root) | **Conventions** | Concise repo-wide agent guidance including Windsurf config doc policy | ✅ YES |

### Maintenance Workflow

```bash
# Edit any rule file directly — no preprocessing step required
vim .windsurf/rules/hitl-enforcement.md
# Windsurf picks up changes automatically on next session
```

---

## Constitutional Rules

| Rule | Layer | Timing | Type | Location | Status |
|------|-------|--------|------|----------|--------|
| **§0: DEFAULT ANALYSIS MODE (Tier-Aware)** | Windsurf | Before work | Behavioural | `.windsurf/skills/graph-analysis/` | ✅ ENFORCED |
| **§ADG-1: ADG Repair Discipline** | Windsurf | Before work | Behavioural | `.windsurf/rules/adg-repair-discipline.md` | ✅ ENFORCED |
| **Windsurf Config Lookup** | Windsurf | On demand | Behavioural | `.windsurf/rules/windsurf-config-lookup.md` | ✅ ENFORCED |
| **§2.5: Test Failure Triage Protocol** | Both | Before repair | Behavioural + Structural | Referenced by `.windsurf/rules/adg-repair-discipline.md` — supporting doc at `docs/technical/TEST_FAILURE_decision_tree.md` (not a Windsurf-discoverable rule file) | ✅ ENFORCED (CI: cond. 8b) |
| **Global Rules Policy** | Windsurf | Always | Behavioural | `.windsurf/rules/global_rules.md` (always_on, 3.0K) | ✅ ENFORCED |
| **HITL Core Pipeline** | Windsurf | During work | Behavioural | `.windsurf/rules/hitl-enforcement.md` (always_on, 2.7K) | ✅ ENFORCED |
| **HITL Decision Points** | Windsurf | On demand | Behavioural | `.windsurf/rules/hitl-decision-points.md` (model_decision) | ✅ ENFORCED |
| **§10.0: Wave/Micro-Wave Plan Model** | Windsurf | Before plan draft | Behavioural | `.windsurf/rules/plan-location.md` + Constitutional Rule #13 | ✅ ENFORCED |
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
| 6 | **structured-reasoning** | Windsurf | Before work | Behavioural | None (behavioral) | None | ✅ ENFORCED |

**Note**: 30 individual skills consolidated into 5 canonical skills (2026-04-03). `structured-reasoning` added 2026-04-07; `refactor-decision-memory` added 2026-04-15. Current total: **7 canonical skills**. See [Consolidation Note](#skill-consolidation-2026-04-03) below.

**2026-04-14 update**: All skill entry files renamed `skill.md` → `SKILL.md` (uppercase) per Windsurf canonical naming. Support files (5 per skill) added for all incomplete skill directories.
**2026-04-15 update**: `constitutional.md` shrunk 29K→3.3K (always_on core only); `hitl-enforcement.md` shrunk 33K→2.7K (always_on core only); `hitl-decision-points.md` added (model_decision, full doctrine); `sequential-thinking-enforcement.md` converted from always_on to model_decision; `adg-test-accelerator-enforcement.md` description frontmatter added; `skills/graph-analysis/fail_closed_discipline.md` added.

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
| Skills | 6 | 6 | 0 | 0 |
| CI Gates | 41 | 41 | 0 | 0 |
| Pre-commit Hooks | 25+ | 25+ | 0 | 0 |

**Overall Coverage**: 100% ✅

---

## Conditional Rules (model_decision & glob triggers)

All `model_decision` and `glob` rules require a `description` field in frontmatter for Cascade trigger mapping.

| Rule File | Trigger | Description |
|---|---|---|
| `adg-repair-discipline.md` | `model_decision` | Use when diagnosing ADG failures or running the ADG repair loop |
| `anti-pattern-hitl-gate.md` | `model_decision` | Use before introducing any new anti-pattern instance |
| `memory-management.md` | `model_decision` | Use when reading/writing the persistent memory graph |
| `security-hardening.md` | `model_decision` | Use when handling credentials, env vars, secrets, or external auth |
| `windsurf-config-lookup.md` | `model_decision` | Use for Windsurf IDE configuration, rules, hooks, MCP, skills, workflows |
| `hitl-decision-points.md` | `model_decision` | Use when a HITL decision point is reached — full trigger patterns, option shape, scoring guidance |
| `sequential-thinking-enforcement.md` | `model_decision` | Use when a T2/T3 task requires structured reasoning before execution |
| `adg-test-accelerator-enforcement.md` | `glob` | Fires on ADG test files and tools — enforces adg_test_accelerator.py usage |
| `mcp-config-ssot.md` | `glob` | Fires on edits to `.windsurf/mcp_config.json` |
| `mcp-pytest-enforcement.md` | `glob` | Fires on edits to `test_*.py` and `conftest.py` |
| `refactor-decision-memory.md` | `model_decision` | Before opening HITL for any refactor-class decision, consult the refactor-decision-memory skill for historical precedent |

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
**Last Audit**: 2026-04-15
**Next Audit**: 2026-05-09

**Changelog**:
- 2026-04-15: **REFACTOR DECISION MEMORY** — New rule `refactor-decision-memory.md` (model_decision). New skill `refactor-decision-memory/` with `lookup_refactor_decisions.py`. New hook `post_cascade_hitl_capture.py` wired into `post_cascade_response`. SQLite+FTS5 ledger at `.windsurf/state/refactor_decisions/`. `hitl-enforcement.md` unchanged — memory system sits under the policy layer. 30 unit tests added.
- 2026-04-15: **RULE SIZE REDUCTION** — `constitutional.md` 29K→3.3K (always_on core, 16 constraints + tier table). `hitl-enforcement.md` 33K→2.7K (always_on pipeline + bypass + thresholds). New `hitl-decision-points.md` (model_decision, 10 decision triggers + HITL-10 shape + telemetry). `sequential-thinking-enforcement.md` converted from always_on (6.9K) to model_decision (1.8K). `adg-test-accelerator-enforcement.md` description frontmatter added. `skills/graph-analysis/fail_closed_discipline.md` created. All 6 skill entry files confirmed as `SKILL.md`. Always_on rules: constitutional (3.3K), global_rules (3.0K), hitl-enforcement (2.7K), plan-location (1.9K).
- 2026-04-14: **WINDSURF DOC ALIGNMENT** — All 6 skill entry files renamed `skill.md` → `SKILL.md` (canonical naming). Added `description` frontmatter to 4 `model_decision` rules (`adg-repair-discipline`, `anti-pattern-hitl-gate`, `memory-management`, `security-hardening`) and 2 `glob` rules (`mcp-config-ssot`, `mcp-pytest-enforcement`). New rule: `windsurf-config-lookup.md`. Removed non-standard `file_pattern` fields from `hooks.json`; moved path filtering logic into `post_write_mcp_config_sync.py`. Added 25 support files across all 5 incomplete skill directories (5 per skill). Added `## Windsurf Configuration Docs` block to repo-root `AGENTS.md`. Updated RULES_INDEX: file count 13→14, skills count 5→6, added Conditional Rules table.
- 2026-04-09: **WINDSURF DRIFT CLEANUP** — Deleted `.windsurf/rules/.windsurfrules` (90KB aggregate, not a documented Windsurf rule artifact, preprocessor archived). Deleted `.windsurf/rules/_variables.yaml` (orphaned config for archived preprocessor). Relocated `pytest-optimization.md` from `.windsurf/` root to `docs/` (no activation path at root). Flattened `.windsurf/plans/plans/` and `.windsurf/plans/tasks/` subdirs into `.windsurf/plans/` per plan-location.md SSOT. Archived `_show_diffs.py` to `tools/archive/`. Updated RULES_INDEX.md: removed dead preprocessor workflow, corrected file count (9→13), fixed `.windsurfrules` status claim. All 6 `SKILL.md` files: moved non-standard frontmatter fields (`enforcement_layer`, `enforcement_timing`, `enforcement_type`) into `metadata:` block per Agent Skills spec.
- 2026-04-08: **POWERSHELL-BAN CI GATE FIXED** — Root cause: `check_powershell_ban.py` had 20 over-broad regex patterns (`$var`, `|pipe|`, `if(){`) generating 7,244 false-positive violations per commit, overflowing Windsurf context and causing internal error `170ba0ebe0fc4955bb7b3ae6ada485f7`. Fix: replaced with 17 precise `\bVerb-Noun\b` patterns scoped to unambiguous PS cmdlets only. Also fixed `pre_run_gate.py` which blocked running the checker itself (substring match on script filename containing "powershell"). Now 0 violations. Committed: `8c1719c99a`.
- 2026-04-08: **MCP ROSTER CLEANUP + GLOBAL CONFIG FIXES** — Deleted 5 redundant/broken MCP servers (Playwright, Figma, Brave Search, Fetch, GitHub MCP) dropping ~50 tools. Fixed Redis MCP env vars from bash `${VAR:-default}` syntax (broken on Windows) to literal values. Removed `disabledTools: [read_file]` from filesystem MCP. Removed web allowlist restriction (all sites now accessible). Added turbo allow/deny lists and global `files.exclude` patterns.
- 2026-04-07: **SEQUENTIAL THINKING MCP RETIRED** — Permanently removed Sequential Thinking MCP from active roster. Root causes: stdio fragility on Windows, zombie node.exe processes, opaque tool surface, no reliable timeout, architectural mismatch. Replacement: native Cascade reasoning + compositional MCP pattern. New artifacts: `.windsurf/workflows/structured-reasoning.md`, `.windsurf/skills/structured-reasoning/SKILL.md` (+ checklist, plan-template, verification-template, failure-template), `docs/mcp/sequential-thinking-replacement.md`. Updated `mcp-failure-rca.md` STEP 6 to tombstone. Updated RULES_INDEX skills table with skill #6.
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
