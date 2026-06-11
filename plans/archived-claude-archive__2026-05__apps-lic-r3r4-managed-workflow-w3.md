---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\apps-lic-r3r4-managed-workflow-w3.md'
original_relative_path: '_archive\\2026-05\\apps-lic-r3r4-managed-workflow-w3.md'
source_sha256: 7fdfe80d33e4c80a03906d9a1a092bfd9a55b89a6f32b316d02fe80f88cdda41
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-lic-r3r4-managed-workflow-w3
plan_type: refactor
---

# W3: apps_lic R3R4 Managed Workflow Implementation

Implement and prove the managed R3R4 path for missing or stale briefing, ensuring fail-closed behavior and proper integration with apps_research via the governed bridge.

---

## Context (SCQA)

**Situation**: W2 is complete with 64/64 tests passing. The static R4 recipe (apps_lic_static_dag.yaml) works for fresh PreloadedOutreachContextManifest. The scaffold files for R3R4 managed workflow exist (managed_workflow_dispatcher.py, apps_research_bridge.py, apps_lic_managed_dag.yaml) and have P7-P9 sentinel tests.

**Complication**: The managed recipe is not registered in lic_l2_recipe_registry.py, and the step adapters (research_bridge_adapter, validate_research_and_build_manifest) are TODO stubs. The 14 required W3 integration tests don't exist yet.

**Question**: How do we complete the R3R4 managed workflow integration so L0 can route missing/stale briefings through the managed path, execute apps_research via the bridge, and resume R4 with a fresh manifest?

**Answer**: Register the managed recipe with all 8 stage adapters, implement the research bridge adapter with fail-closed translation, add the 14 required integration tests proving the full managed path works and fails correctly.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| apps_lic/integrations/lic_l2_recipe_registry.py | Register managed recipe | 🔲 |
| apps_lic/integrations/lic_l2_step_adapters.py | Implement R3R4 adapters | 🔲 |
| apps_lic/config/apps_lic_managed_dag.yaml | 8-stage DAG definition | ✅ |
| tests/governance/test_apps_lic_w3_managed_workflow.py | P7-P9 sentinel tests | ✅ |
| tests/governance/test_apps_lic_static_recipe.py | W2 test patterns to follow | ✅ |

---

## Wave Structure

| Waves | Metric | Scope | Status |
|-------|--------|-------|--------|
| W1 | Register managed recipe | lic_l2_recipe_registry.py + 2 tests | 🟢 |
| W2 | Implement R3R4 adapters | research_bridge_adapter + validate_research_and_build_manifest | 🟢 |
| W3 | Add 14 integration tests | test_apps_lic_r3r4_managed_workflow.py | 🟢 |
| W4 | Verify all tests pass | 78/78 governance tests | 🟢 |

**Total: 4 waves, all GREEN**

---

## Out Of Scope

- No changes to apps_lic/__main__.py (direct test failure fixes only)
- No changes to L0 routing logic (assumes R3R4_MANAGED_WORKFLOW signal)
- No changes to apps_research internals (bridge interface only)
- No new prompt assembly features (uses existing W2 compiler)

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.1 | Register managed recipe | lic_l2_recipe_registry.py | Adapter mapping for 8 stages | ~2K | 🔲 TODO |
| W1.2 | Recipe registration tests | test file additions | Verify registration | ~1K | 🔲 TODO |
| W2.1 | Research bridge adapter | lic_l2_step_adapters.py | Exception handling, R5 codes | ~3K | 🔲 TODO |
| W2.2 | Validate and build manifest | lic_l2_step_adapters.py | Fail-closed logic | ~2K | 🔲 TODO |
| W3.1 | Add 14 integration tests | new test file | Full path coverage | ~5K | 🔲 TODO |
| W4.1 | Run full test suite | all tests | 78/78 pass | ~1K | 🔲 TODO |

---

## Gap Register

**GAP-1: Managed recipe not registered**
- lic_l2_recipe_registry.py only registers static recipe
- Need register_managed_recipe call for apps_lic_managed

**GAP-2: R3R4 step adapters are stubs**
- research_bridge_adapter is TODO
- validate_research_and_build_manifest is TODO

**GAP-3: Missing 14 integration tests**
- No tests proving managed runner resolves recipe
- No tests proving research bridge executes only in L3
- No tests for fail-closed paths

---

## Execution Plan

### W1.1 — Register Managed Recipe
**Scope**: Add managed recipe registration to lic_l2_recipe_registry.py

**Implementation**:
```python
register_managed_recipe(
    app_name="apps_lic",
    dag_path=str(repo_root / "apps_lic" / "config" / "apps_lic_managed_dag.yaml"),
    step_adapters={...},  # 8 stages
    recipe_id="apps_lic_managed",
)
```

**Acceptance**: Recipe resolves via resolve_recipe("apps_lic", "managed")

### W2.1 — Implement Research Bridge Adapter
**Scope**: research_bridge_adapter calls AppsResearchBridge.fetch()

**Implementation**:
- Import AppsResearchBridge from apps_research_bridge
- Call bridge.fetch() with context parameters
- Translate exceptions to R5 reason codes
- Set _r3_research_complete and research_result

**Acceptance**: Adapter returns result with _r3_research_complete=True

### W2.2 — Implement Validate and Build Manifest
**Scope**: validate_research_and_build_manifest validates ResearchResult

**Implementation**:
- Check evidence_items not empty
- Check not is_stale
- Check confidence >= threshold
- Build PreloadedOutreachContextManifest or fail closed

**Acceptance**: Returns _r3_manifest_built=True or raises fail-closed

### W3.1 — Add 14 Integration Tests
**Scope**: Create comprehensive test file

**Tests**:
1. test_apps_lic_missing_briefing_routes_r3r4_managed_workflow
2. test_apps_lic_managed_runner_resolves_managed_recipe_from_registry
3. test_apps_lic_research_bridge_executes_only_inside_l3_managed_workflow
4. test_apps_lic_managed_recipe_calls_apps_research_bridge_not_direct_import
5. test_apps_lic_apps_research_success_builds_manifest_then_resumes_r4
6. test_apps_lic_apps_research_failure_fails_closed_through_exit
7. test_apps_lic_apps_research_empty_fails_closed_no_draft
8. test_apps_lic_apps_research_stale_fails_closed_no_draft
9. test_apps_lic_apps_research_weak_support_fails_closed_no_draft
10. test_apps_lic_r3_failure_prevents_r4_static_execution
11. test_apps_lic_managed_path_preserves_policy_blueprint_replay_hashes
12. test_apps_lic_managed_path_preserves_prompt_assembly_invariants
13. test_apps_lic_managed_path_no_legacy_fallback
14. test_apps_lic_managed_path_seals_exit_review_packet_compatible_artifact

**Acceptance**: All 14 tests pass

### W4.1 — Verify Full Suite
**Scope**: Run all apps_lic governance tests

**Command**: `python -m pytest tests/governance/test_apps_lic*.py -v`

**Acceptance**: 78/78 tests pass, 0 skipped

---

## Rules

- No callable passing from apps_lic to anywhere
- No ad hoc prompt strings (use real PA compiler)
- No provider SDK calls outside governed gateway
- No legacy fallback
- Fail-closed on any research failure
- R4 stages only execute after R3 success

---

## Success Criteria

- [ ] Managed recipe registered and resolvable
- [ ] 14 W3 integration tests added and passing
- [ ] 78/78 apps_lic governance tests passing
- [ ] 0 skipped tests
- [ ] All invariants preserved

---

## Rollback Strategy

If tests fail:
1. Revert step adapter changes
2. Check test assertions match actual artifact structure
3. Verify input contract fields provided in tests
4. Ensure no import loops

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| W3 tests | 17 pass | pytest count |
| Total apps_lic tests | 81 pass | pytest tests/governance/test_apps_lic*.py |
| Skipped tests | 0 | pytest --collect-only |
| Recipe resolution | works | resolve_recipe("apps_lic", "managed") returns callable |

---

## W3 ACCEPTED — 2026-05-05

**Proof Command:**
```bash
python -m pytest tests/governance/test_apps_lic_entrypoint_purity.py \
       tests/governance/test_apps_lic_prompt_assembly.py \
       tests/governance/test_apps_lic_static_recipe.py \
       tests/governance/test_apps_lic_r3r4_managed_workflow.py \
       -q --tb=short
```

**Proof Output:**
```
81 passed, 75 warnings in 21.91s
```

**Acceptance Verified:**
- ✅ All 81 tests pass
- ✅ Zero skipped tests
- ✅ 17 W3 tests (14 original + 3 hardening)
- ✅ 25 entrypoint purity tests
- ✅ 25 prompt assembly tests  
- ✅ 14 static recipe tests

**Hardening Tests Added:**
1. `test_apps_lic_apps_research_blocked_fails_closed_no_draft` — APPS_RESEARCH_BLOCKED path
2. `test_apps_lic_r3r4_does_not_execute_static_r4_until_manifest_valid` — R3→R4 gate
3. `test_apps_lic_managed_recipe_uses_prompt_registry_hash_after_r4_resume` — Hash binding verification

**Invariants Preserved:**
- No callable passing from apps_lic
- No direct apps_research import from __main__.py or L0
- Bridge executes only as registered L3/L2 managed workflow step
- No ad hoc prompt strings
- No provider SDK calls outside governed gateway
- No legacy fallback
- No generic draft on research failure

| Rank | File | Layer | Fan-in | Archetype | Surface | Impact |
|------|------|-------|--------|-----------|---------|--------|
| 1 | apps_lic/integrations/lic_l2_recipe_registry.py | L_APP | 4 | ORCHESTRATOR | Execution Surface | medium |
| 2 | apps_lic/integrations/lic_l2_step_adapters.py | L_APP | 3 | STATE_NODE | State Surface | medium |

---

## W4 ACCEPTED — Final Spine Acceptance (2026-05-05)

**Scope**: Final acceptance, legacy quarantine, documentation update

### W4 Completion

| Task | Status | Evidence |
|------|--------|----------|
| Full governance suite | ✅ | 81 tests pass |
| Legacy quarantine | ✅ | run_workflow_lic.py QUARANTINED |
| Unreachability verified | ✅ | No imports from active paths |
| RUNBOOK.md updated | ✅ | W4 acceptance section added |
| Proof captured | ✅ | Command and count recorded |

### Legacy Quarantine Details

**File**: `apps_lic/tools/run_workflow_lic.py`

**Quarantine Header Added**:
```python
# =============================================================================
# QUARANTINED — LEGACY CODE — DO NOT USE
# =============================================================================
# This file is QUARANTINED as of W4 (2026-05-05) per apps_lic spine acceptance.
#
# REASON:
#   This legacy workflow runner is replaced by the governed R3R4 managed workflow
#   (apps_lic_static and apps_lic_managed recipes via lic_l2_recipe_registry).
#
# UNREACHABLE FROM:
#   - apps_lic/__main__.py (governed spine entrypoint)
#   - L0 routing (R4_STATIC_RECIPE, R3R4_MANAGED_WORKFLOW route families)
#   - R4 recipe resolution (static DAG)
#   - R3R4 recipe resolution (managed DAG)
#   - Active step adapters (STEP_ADAPTERS registry)
# =============================================================================
```

### Final Test Count

| Suite | Tests |
|-------|-------|
| P0 Entrypoint purity | 25 |
| P1.5 Prompt Assembly | 25 |
| W2 Static recipe | 14 |
| W3 R3R4 managed workflow | 17 |
| **TOTAL** | **81** |

### Deferred Scope

None — all waves complete.

### SR_SUMMARY Ready

See final SR_SUMMARY output in response.

## ADG_HOTSPOT_REPORT

| Rank | File | Layer | Fan-in | Archetype | Surface | Impact |
|------|------|-------|--------|-----------|---------|--------|
| 1 | apps_lic/integrations/lic_l2_recipe_registry.py | L_APP | 4 | ORCHESTRATOR | Execution Surface | medium |
| 2 | apps_lic/integrations/lic_l2_step_adapters.py | L_APP | 3 | STATE_NODE | State Surface | medium |
| 3 | apps_lic/engines/generation_engine.py | L_APP | 2 | CENTRAL_DEPENDENCY | Execution Surface | medium |
| 4 | apps_lic/engines/HOP6ValidationAgent.py | L_APP | 2 | SAFETY_GATEKEEPER | Security Surface | medium |

## ADG_GRAPH_LAYER_EVIDENCE

Graph-layer primitives consulted during plan authoring:

- `mv_hotspot_centrality` — ranked apps_lic modules by degree_centrality to identify orchestration hotspots
- `mv_graph_reverse_dependency_hotspots` — confirmed lic_l2_recipe_registry.py as central dependency
- `mv_dependency_cone_risk` — assessed blast radius of recipe registration changes
- `mv_authority_boundary_breaches` — confirmed L_APP_core_bypass violations for vllm_health_probe imports
- Semantic edge `flows_to`: managed workflow dispatcher → apps_research bridge
- Semantic edge `controls_flow`: recipe registry → step adapters
- P-view `v_p1_not_on_spine`: verified managed path adapters are on the execution spine
