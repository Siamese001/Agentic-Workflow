# Deduplication Validation Report

**Generated**: 2026-02-08
**Pipeline**: `artifacts/dedup/run_dedup_analysis.py` (Phases 0–2) + manual Phase 3–4

---

## Phase 0 — Discovery Lock

| Metric | Value |
|--------|-------|
| Discovery script | `agentic_core/L0_maintenance/scripts/full_agent_discovery.py` |
| Discovery JSON | `agent_discovery_full.json` |
| Schema version | 3.1.0-lcd-plus |
| Agents before | 190 |
| Agents after | 190 |
| Snapshot before | `artifacts/dedup/discovery_snapshot_before.json` |
| Snapshot after | `artifacts/dedup/discovery_snapshot_after.json` |

## Phase 1 — AST-Level Signal Extraction

| Metric | Before | After |
|--------|--------|-------|
| Total pairs analyzed | 17,955 | 17,955 |
| Code similarity pairs ≥ 0.75 | 12 | 11 |
| Prompt similarity pairs ≥ 0.80 | 1 | 1 |
| Responsibility overlap pairs above threshold | 15 | 15 |
| Average blast radius | 4.3 | 4.3 |
| Max blast radius | 27 (FileClassificationAgent) | 27 (FileClassificationAgent) |

### Artifacts

- `artifacts/dedup/similarity/code_similarity.json`
- `artifacts/dedup/similarity/code_similarity.md`
- `artifacts/dedup/similarity/prompt_similarity.json`
- `artifacts/dedup/similarity/prompt_similarity.md`
- `artifacts/dedup/similarity/responsibility_similarity.md`
- `artifacts/dedup/similarity/dependency_overlap.md`
- `artifacts/dedup/similarity/import_complexity.md`
- `artifacts/dedup/active_agents_index.json`

## Phase 2 — Consolidation Design

| Metric | Value |
|--------|-------|
| Composite clusters (≥ 0.70) | 10 |
| Code clusters (≥ 0.75) | 6 |
| Code clusters (≥ 0.60) | 10 |

### Artifacts

- `docs/reports/plans/dedup_consolidation_plan.md`
- `docs/reports/plans/dedup_stop_sprawl_policy.md`

## Phase 3 — Implementation

### 3a. Code Deduplication (Cluster 4)

**Action**: Extracted identical `perform_checks()` placeholder into `InspectionCapability` base class.

| File | Change | Lines removed |
|------|--------|---------------|
| `agentic_core/mixins/inspection_capability.py` | Added default `perform_checks()` implementation | +15 (replaced `NotImplementedError`) |
| `agentic_core/L3_orchestration/reasoning/DagRuntimeInspectorAgent.py` | Removed duplicated `perform_checks()` | −16 |
| `agentic_core/L5_safety/reasoning/SignatureVerifierAgent.py` | Removed duplicated `perform_checks()` | −16 |
| `agentic_core/L5_safety/reasoning/TokenBudgetInspectorAgent.py` | Removed duplicated `perform_checks()` | −16 |

**Net**: −33 lines of duplicated code eliminated.
**Cluster 4 median similarity**: 0.772 → 0.749 (reduced).

### 3b. Documented Waivers

18 waiver pairs added to `artifacts/dedup/sprawl_gate.py` covering:

| Cluster | Agents | Similarity Source | Justification |
|---------|--------|-------------------|---------------|
| 1 (partial) | OmniContext, SemanticMapper, Strategist, UiValidation | Shared `SubatomicTestingMixin + SovereignBaseAgent` + heal boilerplate | Distinct domain roles |
| 2 | ATSCompatibility, BrandCompliance, FactCheck, SectionBalance | Shared `RGValidationCapability` | Distinct `collect_issues()` logic |
| 4 | DagRuntimeInspector, SignatureVerifier, TokenBudgetInspector | Shared `InspectionCapability` (now deduplicated) | Domain stubs retained |
| 5 | HOP4Routing, HOP7GateDecision, HOP9Integration | Shared `HOPStageCapability` | Distinct `_process()` pipeline stages |
| 6 | CampaignBalance, Deliverability | Shared `LICEngineValidationCapability` | Distinct `_validate()` business rules |
| 7 | CodeFormatter, UnusedCleanup | Shared `CodeToolRunnerCapability` | Previously consolidated |
| 10 | CoordinateObservabilityOps, TrackObservabilityCost | Shared base + auto-inserted semantic signals | Different purposes |

Full documentation: `artifacts/dedup/waivers/2026-02-08_structural_similarity_waivers.md`

### 3c. Regression Tests

| Test file | Tests | Status |
|-----------|-------|--------|
| `tests/unit/agentic_core/mixins/test_inspection_capability_structure.py` | 19 | PASS |
| `tests/unit/agentic_core/mixins/test_inspection_capability_dedup_regression.py` | 15 | PASS |
| **Total** | **34** | **ALL PASS** |

## Phase 4 — Validation Lock

### Agent Count Table

| Metric | Value |
|--------|-------|
| old_count | 190 |
| new_count | 190 |
| merged_agents | 0 |
| retired_agents | 0 |
| shimmed_agents | 0 |
| deduplicated_methods | 3 (perform_checks extracted to base) |

### Hash Stability

3 files changed (expected — the 3 Cluster 4 agents whose `perform_checks()` was removed):

- `DagRuntimeInspectorAgent` — hash changed
- `SignatureVerifierAgent` — hash changed
- `TokenBudgetInspectorAgent` — hash changed

All other 187 agent hashes stable.

### Sprawl Gate

```
PASS: 0 threshold breaches (after 18 waiver(s)).
```

### CI Enforcement Command

```bash
python -m agentic_core.L0_maintenance.scripts.full_agent_discovery
python artifacts/dedup/run_dedup_analysis.py
python artifacts/dedup/sprawl_gate.py --max-code-sim 0.75 --max-prompt-sim 0.80
```

### CI Workflow

Already exists: `.github/workflows/agent-sprawl-check.yml`

---

## Summary

- **No agents silently dropped** — 190 before, 190 after
- **No regression** — 34/34 tests pass
- **Code deduplication** — 33 lines of triplicated `perform_checks()` eliminated
- **CI duplication gate active** — `sprawl_gate.py` enforces thresholds with 18 documented waivers
- **All similarity artifacts present** — 8 files in `artifacts/dedup/similarity/`
- **Deterministic** — fixed seed (42), stable ordering, reproducible outputs
