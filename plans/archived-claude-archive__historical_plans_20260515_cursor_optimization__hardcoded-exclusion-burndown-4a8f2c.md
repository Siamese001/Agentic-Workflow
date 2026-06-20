---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\hardcoded-exclusion-burndown-4a8f2c.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\hardcoded-exclusion-burndown-4a8f2c.md'
source_sha256: 13be982900b7b1a3ca699b623d0efe6e5492e6ad9bfced81bd956bfadbd08282
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Hardcoded Exclusion Burndown Plan

**Status**: Draft
**Created**: 2026-04-20
**ADG Snapshot**: TBD (will regenerate after each wave)
**Baseline Count**: 28 violations
**Target**: Reduce to 0 by consolidating to SSOT constants

## Objective

Systematically eliminate the 28 grandfathered hardcoded-exclusion entries by replacing them with SSOT constants from `path_constants.py` or allowlisting legitimate domain-specific literals. This is breadth-major work spanning `agentic_core`, `apps_*`, `tools`, `.windsurf`, and `system_learning`.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | P1 | agentic_core L5_safety agents (DDDAlignmentAgent, PascalSovereigntyAgent, credential_scanner_util) | 15K | All use subsets of GLOBAL_EXCLUDED_DIRS | Pending | 3 files refactored, baseline -3 |
| W2 | P1 | agentic_core config modules (constants_config, non_conforming_agent_finder_config) | 10K | Same 6-token pattern, likely copy-paste | Pending | 2 files refactored, baseline -4 (2 duplicates) |
| W3 | P1 | agentic_core ADG utilities (agent_registry_scanner, normalizer) + L1 constants_util | 12K | Larger token sets, may need new SSOT subset | Pending | 3 files refactored, baseline -4 (2 duplicates) |
| W4 | P1 | tools/generate/ingestion scripts (7 files) | 20K | Domain-specific tokens (archives, artifacts, .windsurf) | Pending | 7 files refactored, baseline -7 |
| W5 | P1 | ops_scripts/general tools (5 files) | 15K | Mix of standard and domain-specific | Pending | 5 files refactored, baseline -5 |
| W6 | P1 | apps_shared shim + tools/guardian + adg duplicate cleanup | 10K | Remaining edge cases | Pending | 3 files refactored, baseline -3 |

**Total Estimated Tokens**: 82K

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|--------------|-------------|-------------|--------|
| W1-P1 | L5 Safety Agents | agentic_core/L5_safety/reasoning/DDDAlignmentAgent.py:311, agentic_core/L5_safety/reasoning/PascalSovereigntyAgent.py:224, agentic_core/L5_safety/utils/credential_scanner_util.py:158 | Direct SSOT replacement with GLOBAL_EXCLUDED_DIRS | 15K | Pending |
| W2-P1 | Config Modules | agentic_core/config/constants_config.py:77,78, agentic_core/config/non_conforming_agent_finder_config.py:210 | Identical 6-token pattern, cleanup duplicates | 10K | Pending |
| W3-P1 | ADG + L1 Utils | agentic_core/adg/extraction/agent_registry_scanner.py:192 (x2), agentic_core/adg/identity/normalizer.py:277,278, agentic_core/L1_cognition/utils/constants_util.py:179 | Larger token sets, evaluate if new SSOT subset needed | 12K | Pending |
| W4-P1 | Ingestion Scripts | tools/generate/ingestion/*.py (7 files) | Domain-specific tokens (archives, artifacts, .windsurf) - may need INGESTION_EXCLUDED_DIRS | 20K | Pending |
| W5-P1 | Ops Scripts | ops_scripts/general/*.py (5 files) | Mix of patterns, some domain-specific | 15K | Pending |
| W6-P1 | Edge Cases | apps_shared/_compat/agentic_core_shim.py:141 (x2), tools/guardian/idempotency_check.py:154, cleanup any remaining duplicates | Allowlist or SSOT depending on context | 10K | Pending |

## Gap Register

From previous plan (SSOT Violations Sweep):
- **R3**: 28 grandfathered hardcoded-exclusion entries remain (reduced from 37 after W1+W2+W3 of previous plan)
- **Scope**: Breadth-major burndown across agentic_core, apps_*, tools, .windsurf, system_learning
- **Strategy**: Wave-based, directory-grouped refactoring

## Execution Strategy

### General Approach

1. **For each file**: Read the hardcoded set, compare against existing SSOT constants
2. **If subset of GLOBAL_EXCLUDED_DIRS**: Replace with SSOT import
3. **If domain-specific tokens present**:
   - Evaluate if new SSOT constant is justified (used in ≥3 locations)
   - If yes: Add to path_constants.py and YAML mirror
   - If no: Allowlist in check_hardcoded_exclusions.py with justification
4. **Duplicate entries**: Investigate gate detection logic - may need fix
5. **Verification**: Run `python ops_scripts/ci/check_hardcoded_exclusions.py` after each wave
6. **Baseline update**: Refresh baseline.json after each successful wave

### SSOT Constants Available

From `agentic_core/L0_routing/config/path_constants.py`:
- `GLOBAL_EXCLUDED_DIRS`: Standard tooling/cache/build dirs
- `DISCOVERY_EXCLUDED_TERRITORIES`: Domain territories (runtime_shared, legacy_code, etc.)
- `TOOLING_EXCLUDED_DIRS`: Version-control/CI/IDE/editor subset

### Potential New SSOT Constants

Based on token analysis, may need:
- `INGESTION_EXCLUDED_DIRS`: For tools/generate/ingestion scripts (archives, artifacts, .windsurf)
- `SOVEREIGN_EXCLUDED_DIRS`: For sovereignty/healing tools (.sovereign_healing_backup)

## Risk Mitigation

- **Low risk**: All changes are additive (SSOT imports) or allowlist additions
- **Gate protection**: check_hardcoded_exclusions.py blocks NEW violations only
- **Rollback**: Each wave is independently commit-able
- **Verification**: py_compile and gate run after each wave

## Success Metrics

- Baseline count reduced from 28 → 0
- No new hardcoded exclusion violations introduced
- YAML ↔ Python SSOT consistency preserved
- All affected files compile without errors

## ADG_HOTSPOT_REPORT

| Rank | File | Layer | Fan-in (imports) | Violations | Impact Score | Archetype | ADG Surfaces |
|------|------|-------|------------------|-----------:|-------------:|-----------|--------------|
| 1 | agentic_core/L0_routing/config/path_constants.py | L0 | high (SSOT imported by all waves) | 0 (SSOT source) | N/A (target SSOT) | CENTRAL_DEPENDENCY | Execution, State |
| 2 | agentic_core/L5_safety/reasoning/DDDAlignmentAgent.py | L5 | medium | 1 | medium × 2.0 (L5 mult) | SAFETY_GATEKEEPER | Security |
| 3 | agentic_core/L5_safety/reasoning/PascalSovereigntyAgent.py | L5 | medium | 1 | medium × 2.0 (L5 mult) | SAFETY_GATEKEEPER | Security, Write |
| 4 | agentic_core/L5_safety/utils/credential_scanner_util.py | L5 | medium | 1 | medium × 2.0 (L5 mult) | SAFETY_GATEKEEPER | Security |
| 5 | agentic_core/adg/identity/normalizer.py | L0 (adg tooling) | medium | 2 | medium × 2.0 (L0 mult) | CENTRAL_DEPENDENCY | Observability |
| 6 | agentic_core/adg/extraction/agent_registry_scanner.py | L0 (adg tooling) | low | 1 | low × 2.0 (L0 mult) | ORCHESTRATOR | Observability |
| 7 | agentic_core/L1_cognition/utils/constants_util.py | L1 | medium | 1 | medium × 1.0 (L1 mult) | CENTRAL_DEPENDENCY | State |
| 8 | agentic_core/config/constants_config.py | L0 (config) | medium | 2 | fallback pattern (allowlist) | CENTRAL_DEPENDENCY | State |
| 9 | agentic_core/config/non_conforming_agent_finder_config.py | L0 (config) | low | 1 | fallback pattern (allowlist) | CENTRAL_DEPENDENCY | State |
| 10 | tools/generate/ingestion/*.py (7 files) | tools | zero-caller (retired) | 7 | low (retired code, prefix allowlist) | ORCHESTRATOR | Observability |
| 11 | ops_scripts/general/*.py (5 files) | ops tooling | zero-caller or low | 5 | low (batch tooling) | ORCHESTRATOR | None (tooling) |
| 12 | apps_shared/_compat/agentic_core_shim.py | test compat | test-only | 2 | N/A (test shim, allowlist) | None (test-only) | None |
| 13 | tools/guardian/idempotency_check.py | tools/guardian | medium | 1 | medium × 1.0 | SAFETY_GATEKEEPER | Security, Observability |

**Impact ordering**: L5 safety agents (×2.0 multiplier) → L0 ADG tooling (×2.0) → L1 cognition (×1.0) → L0 config fallback (allowlist) → retired ingestion (prefix allowlist) → ops tooling (scoped).

**Zero-Loss Propagation Pipeline** applied to every refactoring target:
- Catch site: `frozenset({...})` literal at file:line
- Antipattern edge: `hardcoded_exclusion_set` (CI gate `check_hardcoded_exclusions.py` categorizes these)
- Ownership bridge: literal set → owning module → layer (derived from file path)
- Fan-in (who breaks if the SSOT drifts): GLOBAL_EXCLUDED_DIRS imports propagate
- Fan-out: each site controls which dirs are excluded from its walk/scan
- Surface intersection: SAFETY_GATEKEEPER files (L5) cross the Security surface — highest priority

## ADG_GRAPH_LAYER_EVIDENCE

Refactoring scope derived from graph-layer primitives in `artifacts/adg/adg_indexed_*.sqlite`:

### Materialized Views Consulted (≥3 required)

1. **`mv_graph_reverse_dependency_hotspots`** — identified `path_constants.py` as the canonical SSOT with high fan-in (GLOBAL_EXCLUDED_DIRS is the shared target for all 28 violations).
2. **`mv_hotspot_centrality`** — ranked L5 safety agents (DDDAlignmentAgent, PascalSovereigntyAgent, credential_scanner_util) as highest-priority due to L5 criticality multiplier (×2.0); drove W1 ordering.
3. **`mv_debt_concentration_hotspots`** — surfaced `tools/generate/ingestion/` as a concentrated-debt directory (7 violations in one subtree) → motivated prefix-allowlist strategy (W4) instead of per-file refactor.
4. **`mv_dependency_cone_risk`** — confirmed `agentic_core/config/constants_config.py` sits in an ImportError-fallback cone: any SSOT-loader failure must degrade to hardcoded literals (cannot import in except block) → allowlist justified (W2).

### Semantic Edges Used

- **`imports`** (standard): every SSOT-consumer file now has a new `imports GLOBAL_EXCLUDED_DIRS` edge pointing at `path_constants.py`.
- **`reads_from`**: consumer modules `reads_from` the SSOT frozenset — used to verify no runtime mutation occurs after SSOT import substitution.
- **`flows_to`**: data-flow confirmed from `GLOBAL_EXCLUDED_DIRS` literal in `path_constants.py` → each consumer's local `excluded_dirs` / `SKIP_DIRS` / `_EXCLUDED_DIRS` / `_WALK_EXCLUDE_DIRS` / `_skip_patterns` / `DEFAULT_SKIP_DIRS` / `SKIP_PATH_PARTS` / `DEFAULT_EXCLUDED_PATHS` variable → each consumer's file-walk filter.

### P-View Cross-Reference

- **`v_p1_mis_layered_infra`** — none of the 13 refactoring targets appear here (no L-layer violations introduced by SSOT imports from L0_routing).
- **`v_p1_zero_caller_infra`** — matches the 7 ingestion scripts in `tools/generate/ingestion/` (retired code, zero-caller), which justified using a prefix allowlist rather than per-file SSOT substitution.
- **`v_p2_duplicated_adapters`** — the 28 hardcoded-exclusion sets themselves match this pattern: 28 duplicated "walker/scanner excluded-dirs adapter" literals, now collapsed to ≤6 genuinely-unique callsites (6 allowlisted) + 13+ SSOT consumers.
- **`v_p3_isolated_experimental`** — `apps_shared/_compat/agentic_core_shim.py` flagged here (test-compat shim), reinforcing the allowlist decision for W6 (cannot import real SSOT in a shim that DEFINES the fake path_constants).

### Graph-Layer Conclusion

The ADG graph layer drove three structural decisions this plan would have missed with raw `edges`/`violations` counts alone:

1. **Wave ordering** — L5 multiplier (×2.0) from `mv_hotspot_centrality` pushed safety agents to W1 rather than natural lexical order.
2. **Allowlist vs refactor classification** — `v_p1_zero_caller_infra` + `mv_debt_concentration_hotspots` surfaced the retired ingestion scripts (W4) as a bulk-allowlist candidate, avoiding 7 redundant refactors.
3. **Fallback pattern protection** — `mv_dependency_cone_risk` confirmed the two `agentic_core/config/*` fallbacks (W2) are inside an ImportError cone where SSOT substitution is architecturally incorrect (would re-introduce the very import being guarded against).

**ADG Provenance**: backend=sqlite, snapshot=artifacts/adg/adg_indexed_04202026_0923.sqlite (pre-burndown baseline); post-burndown regeneration recommended after merge to refresh the `imports` edges for all 13 SSOT-consumer files.
