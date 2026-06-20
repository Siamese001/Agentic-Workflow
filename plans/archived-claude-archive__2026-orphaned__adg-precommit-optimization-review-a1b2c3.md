---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-orphaned\\adg-precommit-optimization-review-a1b2c3.md'
original_relative_path: '_archive\\2026-orphaned\\adg-precommit-optimization-review-a1b2c3.md'
source_sha256: 0ae9fd1fd0e28d09348aad0b188e05122bc53f372c7c37d8ac080935a7876b10
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# ADG Generation & Pre-Commit Optimization Review

Comprehensive review of ADG generation process, pre-commit configuration, dependencies, and P1-P4 priority definitions usage.

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Dependency mapping | ADG artifacts ↔ pre-commit hooks | A | 15K 🟢 |
| Wave 2 | Logic order analysis | Hook sequencing optimization | B | 12K 🟢 |
| Wave 3 | Redundancy detection | Duplicate checks and consolidation | C | 10K 🟢 |
| Wave 4 | P1-P4 alignment | SSOT compliance verification | D | 8K 🟢 |

**Total: 45K tokens across 4 waves, all GREEN**

---

## Gap Register

**GAP-1: ADG Generation Timing**
- ADG must be generated before pre-commit hooks T13.5, T13.6, T19 can run
- No explicit hook in pre-commit to trigger ADG regeneration
- Risk: Stale ADG artifacts causing false positives/negatives in ADG-dependent gates

**GAP-2: P1-P4 Definition Fragmentation**
- `priority_definitions.json` exists but not dynamically loaded by pre-commit
- Pre-commit config hardcodes Ruff rule selectors (T2-P0/P1/P2/P3)
- `SeverityLevel` enum in `severity.py` maps to P1-P4 but not used by Ruff hooks
- SSOT exists in JSON but not enforced in YAML configuration

**GAP-3: ADG SQLite Dependency**
- T13.5 (layer violation), T13.6 (P1 defect), T19 (staleness) all query `adg_indexed_*.sqlite`
- No graceful degradation if SQLite missing (gates fail or return empty)
- T19 (staleness guard) checks Redis but doesn't validate SQLite freshness

**GAP-4: Redundant Severity Mappings**
- RepairRoute.py uses literal `Severity = Literal["critical", "high", "medium", "low"]`
- SeverityLevel enum exists but not used by repair routing
- P1-P4 defect table in generate_full_adg.py manually maps severity → priority

---

## Execution Plan

### Phase 1 — Dependency Mapping
**Scope**: Map all ADG artifact dependencies in pre-commit hooks

**Analysis**:
1. Identify all hooks that query ADG SQLite:
   - T13.5: `adg_layer_violation_gate.py` → queries `edges` table for `relation_type = 'violates'`
   - T13.6: `adg_p1_defect_gate.py` → queries `violations` table for `severity = 'critical'`
   - T19: `adg_stale_guard.py` → checks Redis cache freshness (not SQLite)

2. Identify all hooks that query ADG JSON artifacts:
   - T13: `adg_burndown_gate.py` → reads `adg_file_graph_*.json` for importer counts

3. Identify ADG generation triggers:
   - Manual: `python tools/generate/generate_full_adg.py`
   - Auto-commit: Uses `--no-verify` to bypass pre-commit (line 660 in generate_full_adg.py)
   - No pre-commit hook triggers ADG regeneration

**Findings**:
- **CRITICAL**: T13.5, T13.6, T13 depend on ADG artifacts but no hook ensures they're fresh
- **RISK**: Developer commits without regenerating ADG → gates query stale data
- **MITIGATION**: T19 (staleness guard) should check SQLite timestamp, not just Redis

**Acceptance**: Complete dependency graph with artifact → hook mappings

---

### Phase 2 — Logic Order Analysis
**Scope**: Analyze pre-commit hook sequencing for optimization opportunities

**Current Order**:
```
T0:   Admission guards (no-verify, Author-Gate, agent-deletion)
T0:   Whitespace normalization
T1:   py_compile (syntax check)
T2:   Ruff P0/P1/P2/P3 (linting with --fix)
T3:   ruff-format
T4:   Guardian comment auto-fixer
T5:   ADG CI gates (manual only)
T6:   Hollow file gate (AST semantic check)
T7:   Report location SSOT
T7.5: Plan location SSOT
T7.7: Windsurf governance health
T8:   Reject generated artifacts
T9:   Tooling/apps boundary
T10:  Module collision
T10.5: Eager import lint
T10.6: ADG preflight
T11:  MCP config sovereignty
T11.2: MCP config drift
T11.3: Pytest config SSOT
T12:  Guardian exemption ratchet
T13:  ADG burndown gate
T13.5: ADG layer violation (warning)
T13.6: ADG P1 defect (BLOCKING)
T14:  ADG Python ban (grep/mypy/pytest)
T15:  ADG YAML grep ban
T16:  Skip-file ratchet
T19:  ADG staleness guard (warning)
T20:  Pycache purge
T21:  Pre-commit summary report
```

**Issues Identified**:
1. **T19 (staleness guard) runs AFTER T13.5/T13.6/T13**:
   - Should run BEFORE ADG-dependent gates to warn about stale data
   - Current position: after T16, before T20
   - Recommended position: after T10.6 (ADG preflight), before T12

2. **T13.6 (P1 defect BLOCKING) runs AFTER T13.5 (layer violation warning)**:
   - Logical: P1 is more severe than generic layer violations
   - But T13.5 is warning-only, T13.6 is blocking
   - Consider merging or reordering

3. **T10.6 (ADG preflight) runs early but doesn't validate ADG freshness**:
   - Runs gap analysis and collection safety
   - Should add ADG artifact timestamp check

4. **T4 (guardian fixer) runs AFTER T2/T3**:
   - Correct: formatting should be canonical before guardian fixes
   - But guardian fixes might introduce new formatting issues

**Optimizations**:
1. Move T19 before T12 (before all ADG-dependent gates)
2. Add ADG regeneration trigger hook if T19 detects staleness > threshold
3. Consider merging T13.5 and T13.6 into single ADG violation gate with severity tiers
4. Move T4 after T13 to ensure guardian comments are canonical before violation checks

**Acceptance**: Optimized hook sequence with rationale for each change

---

### Phase 3 — Redundancy Detection
**Scope**: Identify duplicate checks and consolidation opportunities

**Redundancies Found**:

1. **Severity Mapping Redundancy**:
   - `priority_definitions.json` defines P0-P4 mappings
   - `SeverityLevel` enum in `severity.py` defines same mappings
   - `RepairRoute.py` uses literal strings instead of enum
   - Pre-commit config hardcodes Ruff selectors instead of loading from JSON

2. **ADG Violation Checks**:
   - T13.5: Queries `edges` table for `relation_type = 'violates'`
   - T13.6: Queries `violations` table for `severity = 'critical'`
   - Both query same SQLite file, could be single query with severity filtering
   - RepairRoute.py already computes severity routing

3. **Boundary Checks**:
   - T9: Tooling/apps boundary (imports check)
   - T10: Module collision (duplicate modules)
   - T13.5: Layer boundary violations (ADG-based)
   - Overlap in architectural enforcement

4. **Config Validation**:
   - T11: MCP config sovereignty
   - T11.2: MCP config drift
   - T11.3: Pytest config SSOT
   - Could consolidate into single config SSOT gate

5. **Ratchets**:
   - T12: Guardian exemption ratchet
   - T13: ADG burndown ratchet
   - T16: Skip-file ratchet
   - Similar pattern, could share ratchet infrastructure

**Consolidation Opportunities**:
1. Create `config_ssot_gate.py` that validates all YAML/JSON configs
2. Merge T13.5 and T13.6 into `adg_violation_gate.py --severity=critical,high,medium,low`
3. Extract ratchet logic into shared module used by T12/T13/T16
4. Load Ruff selectors from `priority_definitions.json` dynamically

**Acceptance**: Consolidated gate list with reduced redundancy

---

### Phase 4 — P1-P4 Alignment Verification
**Scope**: Ensure P1-P4 definitions are used consistently across all systems

**SSOT Sources**:
1. `agentic_core/config/priority_definitions.json`:
   - P0 (CRITICAL): 11 Ruff rules, 7 ADG dimensions, blocks commit
   - P1 (HIGH): 20 Ruff rules, 11 ADG dimensions, blocks commit
   - P2 (MEDIUM): 18 Ruff rules, 7 ADG dimensions, warning only
   - P3 (LOW): 14 Ruff rules, 13 ADG dimensions, info only
   - P4 (INFO): 10 Ruff rules, 14 ADG dimensions, no enforcement

2. `agentic_core/L5_safety/config/severity.py`:
   - `SeverityLevel.CRITICAL` → P0/P1 (Ruff) / P1 (ADG)
   - `SeverityLevel.HIGH` → P1/P2 (Ruff) / P2 (ADG)
   - `SeverityLevel.MEDIUM` → P2/P3 (Ruff) / P3 (ADG)
   - `SeverityLevel.LOW` → P3/P4 (Ruff) / P4 (ADG)

**Current Usage**:
- ✅ `adg_p1_defect_gate.py` uses `SeverityLevel.CRITICAL` (line 54)
- ✅ `adg_layer_violation_gate.py` imports `SeverityLevel` (line 25)
- ❌ `RepairRoute.py` uses literal strings instead of `SeverityLevel` enum (line 44)
- ❌ Pre-commit config hardcodes Ruff selectors instead of loading from JSON (lines 179-211)
- ❌ `generate_full_adg.py` manually maps severity → P1-P4 (lines 130-138)

**Misalignments**:
1. **Ruff P0 vs ADG P1**:
   - Ruff uses P0 for critical, ADG uses P1 for critical
   - Pre-commit config labels T2 hooks as T2-P0 but severity.py maps P0/P1 to CRITICAL
   - Confusing: T2-P0 should map to SeverityLevel.CRITICAL which is P1 in ADG

2. **Pre-commit gate labeling**:
   - T2-P0, T2-P1, T2-P2, T2-P3 in config
   - But priority_definitions.json maps P0-P4 to precommit gates differently
   - T13.6 labeled as "P1 defect gate" but queries SeverityLevel.CRITICAL

3. **Missing P4 enforcement**:
   - priority_definitions.json defines P4 (INFO) gates
   - No corresponding pre-commit hook for P4-level checks
   - T5 (ADG CI gates) is manual-only, not P4

**Recommendations**:
1. Standardize on ADG P1-P4 terminology (drop Ruff P0)
2. Update pre-commit config to load Ruff selectors from priority_definitions.json
3. Refactor RepairRoute.py to use SeverityLevel enum
4. Update generate_full_adg.py to use SeverityLevel.adg_category property
5. Add pre-commit hook for P4-level checks (documentation, observability)

**Acceptance**: P1-P4 alignment matrix showing all systems using consistent definitions

---

## Rules

- No code changes in this review (analysis only)
- Use SSOT sources (priority_definitions.json, severity.py) as truth
- Maintain backward compatibility during consolidation
- Preserve all blocking gates (P0/P1 critical checks)
- Document all optimization rationales

---

## Success Criteria

- [ ] Complete dependency graph showing ADG artifact → hook mappings
- [ ] Optimized pre-commit hook sequence with documented rationale
- [ ] List of redundant checks with consolidation recommendations
- [ ] P1-P4 alignment matrix showing current vs. target state
- [ ] Risk assessment for ADG staleness in pre-commit context
- [ ] Recommendation for ADG regeneration trigger mechanism

---

## Implementation Commands

```bash
# No implementation commands - this is a review-only plan
# Generate evidence report:
python tools/adg/adg_insight_cli.py --analyze-dependencies > docs/reports/adg_precommit_dependency_analysis.md
python tools/adg/adg_insight_cli.py --analyze-redundancy > docs/reports/precommit_redundancy_analysis.md
```

---

## Rollback Strategy

N/A - Review-only plan, no code changes

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| Dependency coverage | 100% of ADG-dependent hooks identified | Manual review of all pre-commit hooks |
| Redundancy reduction | Identify 5+ consolidation opportunities | Phase 3 deliverable |
| P1-P4 alignment | 100% of systems use SSOT definitions | Phase 4 deliverable |
| Risk mitigation | Document ADG staleness mitigation strategy | Phase 1 deliverable |
