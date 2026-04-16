# Wave D Freeze-Gate and Regression Validation Report

**Wave**: D8.1 — validation sweep
**Date**: 2026-04-16 (UTC)
**Basis**: post-D7.1 collection state
**Predecessors**: `docs/reports/wave_c_freeze_gates.md` (all 11 gates PASS at Wave C end), `docs/reports/wave_c_closeout.md`
**Binding scope**: `.windsurf/plans/wave_d_plan.md` §3 Slice D8.1
**Compared against**: Wave C baseline (ext_authority=604, repo_evidence=3480, ext_raw=70)

> **Verdict (one line):** **D8.1 PASS — proceed to D8.2.** All 11 freeze gates PASS, all 229 scoped Wave D tests PASS, all three always-frozen source files are byte-unchanged at HEAD.

---

## 1. Collection Counts

| Collection | Wave C end | Wave D post-D7.1 | Delta | Expected | Verdict |
|------------|-----------|------------------|-------|----------|---------|
| `ext_authority` | 604 | **604** | 0 | 604 (B7-frozen) | ✓ UNCHANGED |
| `repo_evidence` | 3,480 | **3,489** | +9 | 3,480 + 9 (D7.1 advisory note, 9 heading-chunks) | ✓ EXPECTED DELTA |
| `ext_raw` | 70 | **70** | 0 | 70 (B3-frozen) | ✓ UNCHANGED |

The +9 delta on `repo_evidence` is fully attributable to the D7.1 advisory note at `docs/architecture/write_governance_note.md` (Lane C, `required=True`), which chunked into 9 heading-level segments at ingestion. `ext_authority` and `ext_raw` were not touched by any Wave D slice.

**Source of data**: `python tools/debug/probe_wave_c_freeze_gates.py` re-run at 2026-04-16T23:11:21Z against the live Chroma store at `data/cache/chromadb/`. Raw results persisted to `tools/debug/wave_c_freeze_gates_results.json`.

---

## 2. Gate-by-Gate Results (G1–G11)

All gates computed against the full live collection state (metadata + top-5 target-state queries). Implementation identical to the Wave C audit (same `REQUIRED_FIELDS`, same `AUDIT_QUERIES`, same `STRONG_DIST` / `ADEQUATE_DIST` thresholds from `tools/eval/audit_wave_b_target_state.py`).

| Gate | Scope | Definition | n | Wave D result | Wave C reference | Delta |
|------|-------|-----------|---|---------------|------------------|-------|
| **G1** | `ext_authority` | `invalid_for_normative_use == False` on all chunks | 604 | **PASS ✓** (0 mismatches) | PASS (604) | IDENTICAL |
| **G2** | `ext_authority` | `source_url` starts with `https://` on all chunks | 604 | **PASS ✓** (0 non-https) | PASS (604) | IDENTICAL |
| **G3** | `ext_authority` | all 14 required metadata fields present | 604 | **PASS ✓** (0 missing) | PASS (604) | IDENTICAL |
| **G4** | `repo_evidence` | `invalid_for_normative_use == True` on all chunks | 3,489 | **PASS ✓** (0 mismatches) | PASS (3,480) | +9 chunks all compliant |
| **G5** | `repo_evidence` | no `https://` `source_url` on any chunk | 3,489 | **PASS ✓** (0 https) | PASS (3,480) | +9 chunks all compliant |
| **G6** | `repo_evidence` | all 14 required metadata fields present | 3,489 | **PASS ✓** (0 missing) | PASS (3,480) | +9 chunks all compliant |
| **G7** | `ext_raw` | `invalid_for_normative_use == True` on all chunks | 70 | **PASS ✓** (0 mismatches) | PASS (70) | IDENTICAL |
| **G8** | `ext_raw` | no `source_url` overlap with `ext_authority` | 70 | **PASS ✓** (0 overlap) | PASS (70) | IDENTICAL |
| **G9** | target-state audit | ≥15/20 queries STRONG or ADEQUATE | 20 | **PASS ✓** STRONG=5 ADEQUATE=11 WEAK=4 EMPTY=0 → **covered=16/20 (80%)** | PASS 16/20 (80%) | IDENTICAL |
| **G10** | target-state audit | 0 non-`ext_authority` hits in top-5 across 20 queries | 100 | **PASS ✓** (0 contam) | PASS (0) | IDENTICAL |
| **G11** | target-state audit | 0 `ext_raw` hits in top-5 across 20 queries | 100 | **PASS ✓** (0 contam) | PASS (0) | IDENTICAL |

**All 11 gates PASS.** Zero drift from Wave C baseline on G1/G2/G3/G7/G8/G9/G10/G11 (external-lane and audit gates). The three `repo_evidence` gates (G4/G5/G6) still pass despite the +9 chunks added by D7.1.

### G9 per-query grounding (Wave D vs Wave C)

| # | Topic | Wave D d@1 | Wave D grounding | Wave C grounding | Change |
|---|-------|-----------|------------------|------------------|--------|
| TS-01 | context_engineering | 0.415 | ADEQUATE | ADEQUATE | — |
| TS-02 | contextual_retrieval | 0.434 | ADEQUATE | ADEQUATE | — |
| TS-03 | hybrid_retrieval | 0.511 | WEAK | WEAK | — (C4.1 boundary noise) |
| TS-04 | reranking | 0.403 | ADEQUATE | ADEQUATE | — |
| TS-05 | metadata_provenance | 0.496 | ADEQUATE | ADEQUATE | — |
| TS-06 | chunking_strategy | 0.485 | ADEQUATE | ADEQUATE | — |
| TS-07 | parent_child_expansion | 0.514 | WEAK | WEAK | — (C4.1 boundary noise) |
| TS-08 | evidence_shaping | 0.445 | ADEQUATE | ADEQUATE | — |
| TS-09 | abstain_refine | 0.505 | WEAK | WEAK | — (C4.1 boundary noise) |
| TS-10 | routing_principles | 0.473 | ADEQUATE | ADEQUATE | — |
| TS-11 | agentic_architecture | 0.415 | ADEQUATE | ADEQUATE | — |
| TS-12 | orchestrator_workers | 0.349 | STRONG | STRONG | — |
| TS-13 | tool_contracts_mcp | 0.277 | STRONG | STRONG | — |
| TS-14 | fastmcp_patterns | 0.347 | STRONG | STRONG | — |
| TS-15 | agent_handoffs | 0.335 | STRONG | STRONG | — |
| TS-16 | safety_guardrails | 0.456 | ADEQUATE | ADEQUATE | — |
| TS-17 | evaluator_optimizer | 0.420 | ADEQUATE | ADEQUATE | — |
| TS-18 | single_vs_multi_agent | 0.329 | STRONG | STRONG | — |
| TS-19 | embedding_model | 0.492 | ADEQUATE | ADEQUATE | — |
| TS-20 | normative_requirements | 0.529 | WEAK | WEAK | — (per Wave C disposition — TS-20 lives in Lane C only) |

**Zero query-level grounding changes** between Wave C end-state and Wave D post-D7.1. The identical outcome is expected: no `ext_authority` source was added, no query was edited, and the shaper/router remain frozen.

---

## 3. Wave D Scoped Test Summary

All scoped unit + integration suites relevant to D2–D5 + D7.1 re-run end-to-end. Command:

```
python -m pytest tests/unit/agentic_core/L3_orchestration/reasoning/engines/test_hybrid_search_engine.py \
                 tests/unit/agentic_core/L3_orchestration/reasoning/engines/test_hybrid_search_bge.py \
                 tests/unit/agentic_core/L3_orchestration/reasoning/engines/test_hybrid_search_adg.py \
                 tests/unit/agentic_core/L1_cognition/reasoning/test_abstain_planner.py \
                 tests/unit/agentic_core/L0_routing/reasoning/test_path_router.py \
                 tests/unit/agentic_core/L3_orchestration/reasoning/test_coverage_signal_consumer.py \
                 tests/integration/test_coverage_signal_consumer_e2e.py
```

| Slice | Test file | Tests | Status | Notes |
|-------|-----------|-------|--------|-------|
| **D2.1** + **D2.2** + **D2.3** | `tests/unit/agentic_core/L3_orchestration/reasoning/engines/test_hybrid_search_engine.py` | **88** | ✓ PASS | 28 D2.1 + 29 D2.2 + 31 D2.3 |
| D2 regression (pre-existing) | `test_hybrid_search_bge.py` + `test_hybrid_search_adg.py` | **24** | ✓ PASS | 11 BGE + 13 ADG — no drift from the `enable_lexical=False` default path |
| **D3.1** | `test_abstain_planner.py` | **34** | ✓ PASS | 5 abstain-fires + 4 proceed + 13 shape/serialization + 8 input-validation + 3 no-regression (TestPlanAbstainFires, TestPlanAbstainProceeds, TestDecisionShapeIsStableAndSerializable, TestInputValidation, TestNoRegressionOfExistingPlanner) |
| **D4.1** | `test_path_router.py` | **27** | ✓ PASS | 5 R5-fires + 6 existing-routes-unchanged + 3 contract-error + 7 shape/serialization + 4 D3-consumption + 2 signature stability |
| **D5.1** | `test_coverage_signal_consumer.py` | **33** | ✓ PASS | 7 abstain-flow + 6 continue-flow + 6 D3-delegation + 10 shape/serialization + 4 shaper-byte-unchanged |
| **D5.2** | `tests/integration/test_coverage_signal_consumer_e2e.py` | **23** | ✓ PASS | 6 low-coverage-R5 + 6 adequate-continue + 5 D4-compat + 4 frozen-invariants + 2 full-pipeline |
| **D7.1** | (gate probe via G4/G5/G6) | — | ✓ PASS | see §2 above — D7.1-specific probe at `tools/debug/probe_wave_d71_gates.py` also PASS |
| **Total** | — | **229** | **✓ PASS** | 5.34 s elapsed, 0 failures, 0 errors, 0 skips |

**Constitutional §1 compliance**: no `pytest.mark.skip`, no `xfail`, no weakened assertions. Zero skipped tests across the full run.

---

## 4. Frozen-File Verification

All three always-frozen production files verified byte-unchanged at HEAD via `git diff --stat`:

| File | Wave D plan reference | Diff size | Verdict |
|------|----------------------|-----------|---------|
| `agentic_core/L3_orchestration/reasoning/engines/evidence_shaper.py` | §2d | 0 lines | ✓ BYTE-UNCHANGED |
| `agentic_core/L3_orchestration/reasoning/engines/query_router.py` | §2c | 0 lines | ✓ BYTE-UNCHANGED |
| `tools/eval/retrieval_eval_curated.py` | §2e | 0 lines | ✓ BYTE-UNCHANGED |

Cross-check: the D5.2 integration test (`TestFrozenInvariants::test_frozen_file_has_no_uncommitted_diff`) is parametrized over all three paths and ran green as part of the 229-test sweep in §3.

### Other Wave D frozen references (for completeness)

| File | Wave D plan reference | Status |
|------|----------------------|--------|
| `agentic_core/L4_state/utils/memory/bm25_store.py` | D2.1 allowed-scope (read-only imports only) | BYTE-UNCHANGED (git diff --stat shows 0 lines) |
| `docs/architecture/healing_dispatch_routing_adr.md` (F25-int ADR) | §2f | NOT MODIFIED (no Wave D slice touched F25) |
| `docs/requirements/normative_requirements_spec.md` (TS-20) | §2g | NOT MODIFIED (Lane C placement preserved) |

---

## 5. Regressions / Near-Regressions

**None.**

The only observable delta between the Wave C end-state and the Wave D post-D7.1 state is:
- +9 chunks on `repo_evidence` (the 9 heading-chunks of the D7.1 advisory note, all contract-compliant)
- No other collection-level change
- No gate-level change (G1–G11 all identical verdicts, G9 grounding table byte-identical)
- No scoped-test regression (229/229 PASS, same pass rate as each slice's individual closeout)

### Pre-existing near-regressions carried forward from Wave C

Per `docs/reports/wave_c_freeze_gates.md` §C4.1, three queries live at the WEAK boundary:

| Query | d@1 | Classification |
|-------|-----|----------------|
| TS-03 hybrid_retrieval | 0.511 | Pre-existing compute-path noise, disposed in Wave C §C4.1 — no ext_authority addition allowed per the B7-closed disposition |
| TS-07 parent_child_expansion | 0.514 | Same disposition |
| TS-09 abstain_refine | 0.505 | Same disposition |
| TS-20 normative_requirements | 0.529 | Lane C only per TS-20 final disposition (Wave C §2g) |

These are not Wave D regressions — they are pre-existing, documented, adjudicated. G9 still passes at 16/20 = 80% (threshold ≥75%).

### Warnings

- 25 deprecation warnings during the scoped test run, all originating from `agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py:20` (`agentic_core.L2_execution.providers` → `agentic_core.utils.providers`). Pre-existing across the repo; unrelated to any Wave D slice. Not counted as near-regression.

---

## 6. Verdict

**D8.1 PASS — proceed to D8.2.**

Justification:
- All 11 freeze gates PASS (G1–G11) against the live post-D7.1 collection state.
- `ext_authority` = 604 (B7-frozen ✓), `ext_raw` = 70 (B3-frozen ✓), `repo_evidence` = 3,489 (Wave C 3,480 + 9 D7.1 advisory-note chunks).
- All 229 scoped Wave D tests PASS (0 failures, 0 errors, 0 skips) across D2.1/D2.2/D2.3/D3.1/D4.1/D5.1/D5.2 plus the 24 pre-existing D2 regression tests.
- Three always-frozen source files (`evidence_shaper.py`, `query_router.py`, `retrieval_eval_curated.py`) are byte-unchanged at HEAD.
- Zero new regressions; zero query-level grounding changes; zero anti-patterns introduced; zero cross-lane contamination.

No blocker. The repository is ready for D8.2 (final Wave D closeout report).

---

*Wave D8.1 validation frozen at this version. Machine-readable results: `tools/debug/wave_c_freeze_gates_results.json` (re-run timestamp 2026-04-16T23:11:21Z) and `tools/debug/wave_d71_gates_results.json` (D7.1 probe).*
