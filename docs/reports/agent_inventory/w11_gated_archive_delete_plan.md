# W11 — Gated Archive/Delete Plan (planning only)

**Generated:** 2026-05-19  
**Wave:** W11 planning/proof — **no execution**  
**ADG snapshot:** `05192026_0920` (M2: 8 module groups queried; 4 env/CLI `NOT_SUPPORTED_PATTERN`)  
**M1+M2:** [w11_m1_m2_unblock_receipt.md](w11_m1_m2_unblock_receipt.md)  
**SHIM-ARCHIVE:** [w11_shim_archive_receipt.md](w11_shim_archive_receipt.md) — archived `20260519`  
**SHIM-ARCHIVE-PREP:** [w11_shim_archive_prep_receipt.md](w11_shim_archive_prep_receipt.md)  
**M2.2+M3+M4 prep:** [w11_remaining_candidates_prep_receipt.md](w11_remaining_candidates_prep_receipt.md)  
**M3A+M4A:** [w11_m3_m4_facade_dispatch_migration.md](w11_m3_m4_facade_dispatch_migration.md)  
**M3B+M4B+M4C+M4D:** [w11_fast_blocker_burn_m3b_m4d.md](w11_fast_blocker_burn_m3b_m4d.md)

## Executive summary

| Metric | Count |
|--------|------:|
| Candidates assessed | 13 |
| DELETE_READY | **0** |
| ARCHIVE_READY (gated) | **1** (shim only) |
| MIGRATION_REQUIRED | 8 |
| BLOCKED / not deletable yet | 12 |

**M3B–M4D (2026-05-19):** PA compile SSOT in `apps_rg/runtime/sections/*_pa.py`; dispatch re-exports only. Lanes import sections PA. Competencies canonical entry via `competencies_lane_execution` (body still in dispatch). `apps_eval` narrative judge via `rg_integrations_facade`.

**W11 CLOSEOUT (2026-05-19):** Wave **closed** — shim archive only. All other candidates **DO_NOT_DELETE**. Blocker-burn work deferred to [apps-rg-legacy-dependency-burndown-b7e4a2.md](../../.cursor/plans/apps-rg-legacy-dependency-burndown-b7e4a2.md). Receipt: [w11_closeout_and_next_plan_handoff.md](w11_closeout_and_next_plan_handoff.md).

Static fan-in matrix: [w11_candidate_fanin_matrix.json](w11_candidate_fanin_matrix.json)  
Migration steps: [w11_migration_checklist.md](w11_migration_checklist.md)  
Rollback: [w11_rollback_plan.md](w11_rollback_plan.md)

---

## 1. W11_CANDIDATE_MATRIX

> Fan-in counts are **static** (git grep + import scan). Not runtime reachability. ADG `imports` fan-in: 8 module groups **0** (M2.2+M3+M4); dry_run expanded (2 files, fan-in 0).

| Candidate | Current | Proposed final | Active confidence | Fan-in | ADG | Migration | Delete ready | Blocker |
|-----------|---------|----------------|-------------------|--------|-----|-----------|--------------|---------|
| `archives/l2_rationalization_20260519/.../apps_rg_l2_binding.py` | RETIRE_CANDIDATE | **ARCHIVED** | LOW | quarantine string refs | archived (ADG N/A) | NO | **DONE** | DELETE_READY=NO |
| `agentic_core/L2_execution/reasoning/validation_orchestrator.py` | QUARANTINE | **ARCHIVE_CANDIDATE_AFTER_30D** | LOW | 5 static | ok, **0** import | YES | NO | CI baselines; 30d clock |
| `agentic_core/L2_execution/_agentic_core_smoke.py` | QUARANTINE | **KEEP_TEST_SUPPORT_ONLY** | LOW | 27 test refs | NOT_RUN | YES | NO | L2 smoke harness |
| `agentic_core/L2_execution/reasoning/examples/code_quality_*` | QUARANTINE | **ARCHIVE_CANDIDATE** | LOW | 5 | NOT_RUN | YES | NO | exemplar tests |
| `apps_rg/runtime/dry_run/` | QUARANTINE | **QUARANTINE_30D** | LOW | 6 | ok, **0** (2 files) | YES | NO | contract quarantine tests |
| `apps_rg/runtime/orchestrate_full_resume.py` | TEST_SUPPORT | **KEEP_TEST_SUPPORT_ONLY** | MEDIUM | 9 | NOT_RUN | YES | NO | e2e resume tests + preflight |
| `apps_rg/reasoning/Rg*.py` | SUPERSEDED | **QUARANTINE_30D** | LOW | 40+ | ok, **0** per file | YES | NO | facades, unit tests; no product import |
| `apps_rg/runtime/dispatch/*_dispatch.py` | DOC_DEPRECATE | **QUARANTINE_30D** | MEDIUM | 58 | ok (8 files) | YES | NO | lanes import PA helpers; CLI retired |
| `APPS_RG_R4_GENERATION_MODE=legacy_full_resume` | ROLLBACK | **KEEP_ROLLBACK_ONLY** | HIGH | env refs | N/A | NO | NO | intentional rollback |
| `APPS_RG_QWEN_OFFLINE_CONTRACT_STUB` | TEST | **KEEP_TEST_SUPPORT_ONLY** | MEDIUM | env refs | N/A | NO | NO | offline contract tests |
| `APPS_RG_L2_PROVIDER_MODE=stub_only` | TEST | **KEEP_TEST_SUPPORT_ONLY** | MEDIUM | env refs | N/A | NO | NO | CI/stub paths |
| `--mock-judges` / `--allow-test-mock-judges` | TEST | **KEEP_TEST_SUPPORT_ONLY** | MEDIUM | CLI refs | N/A | NO | NO | mock judge policy |
| `apps_shared` signal stubs | QUARANTINE | **QUARANTINE_30D** | LOW | 13 | NOT_RUN | YES | NO | W4 — wire SSOT first |

**Importers (shim — product path clear):** Canonical `apps_rg.runtime.bindings.l2_binding` used by product; shim imported only by tests/CI/docs per W6. See matrix JSON for full lists.

**Tests depending on shim:** `test_ag6_apps_rg_golden_path`, `test_apps_rg_pipeline_capability`, W6/W10 boundary tests (string refs).

---

## 2. MIGRATION_REQUIRED_FIRST

Cannot archive/delete until migrated:

1. **Shim** — M1 checklist: ag6, pipeline_capability, 4× `check_apps_rg_*`, governance allowlist.
2. **validation_orchestrator** — **ARCHIVE_CANDIDATE_AFTER_30D**; E2 SSOT = `l2_phase_pipeline` (W9 proven); remove CI baselines after quarantine clock.
3. **Rg\*** — **QUARANTINE_30D**; zero product-path imports; migrate `apps_shared` facades + unit tests before any archive.
4. **deprecated dispatch** — **QUARANTINE_30D**; PA compile in sections (M4B); execution bodies remain; retired `python -m` CLIs are not product proof.
5. **code_quality examples** — Archive tests with files or move to `archives/`.
6. **signal stubs** — Author-Gate if replacing `get_signal_enhancer` (W4 QUARANTINE).

**Not migration — explicit KEEP:** legacy_full_resume, offline stub, stub_only, mock-judges (rollback/test hatches).

---

## 3. DELETE_GATE

A path may be **deleted** in a future execution wave only if **all** hold:

- [ ] ADG/static **import fan-in = 0** (product + tests + CI)
- [ ] No pytest imports module under delete
- [ ] No product CLI / `python -m apps_rg` default path references it
- [ ] No runtime proof receipt names path as SSOT
- [ ] Rollback plan does not require file on disk
- [ ] Docs/plans updated (DOC_DEPRECATE_ONLY satisfied)
- [ ] `python -m compileall agentic_core apps_rg apps_shared -q` exit 0
- [ ] W10 boundary + affected contract tests pass
- [ ] Migration receipt in `artifacts/governance/migration_receipts/`

**W11 result:** `DELETE_READY_COUNT = 0` for all 13 candidates.

---

## 4. ARCHIVE_GATE

Archive (move to `archives/l2_rationalization_<date>/`) only if:

- [ ] Product path has zero import dependency
- [ ] Tests migrated or explicitly scoped TEST_SUPPORT archive
- [ ] `MANIFEST.json` lists original → archive paths
- [ ] Expected import breakage covered by negative test or CI allowlist removal
- [ ] Replacement documented in `docs/reports/agent_inventory/`

**W11 result:** `ARCHIVE_READY_COUNT = 0` (candidates exist but gates not met).

---

## 5. KEEP_OR_QUARANTINE

| Item | Why | Next action |
|------|-----|-------------|
| Env rollback hatches | Operator/test recovery | KEEP until ADR retires hatch |
| `_agentic_core_smoke` | L2 unit smoke harness | KEEP_TEST_SUPPORT_ONLY |
| `orchestrate_full_resume` | Modular offline orchestrator tests | KEEP until e2e migrates |
| `deprecated dispatch` | Execution modules + contract tests | **QUARANTINE_30D** — PA in sections (M4B); shrink dispatch execution before archive |
| Shim | Archived 2026-05-19 | **DONE** — quarantine string refs only |
| `validation_orchestrator` | ADG 0; CI baselines | **ARCHIVE_CANDIDATE_AFTER_30D** |
| `Rg*` | Test/facade only | **QUARANTINE_30D** — no batch archive until facades migrated |
| Signal stubs | W4 QUARANTINE | 30d review or wire to `signal_quality_config` |

**NEEDS_DECISION:** Batch archive of entire `apps_rg/reasoning/Rg*.py` tree vs per-agent retirement — recommend **per-agent ADG fan-in** in execution wave.

---

## 6. DURABLE_WRITE_ADMISSION_PROOF

**Confidence: HIGH (structural) / MEDIUM (runtime `.admit()` fan-in)**

| Layer | Evidence |
|-------|----------|
| UWG façade | `agentic_core/runtime/uwg/universal_write_gate.py` — `UniversalWriteGate.admit()`; docstring: all writes must use admit |
| L4 adapter | `agentic_core/L4_state/adapters/write_adapters.py` — `_UWG_WRITE_TOKEN`; rejects L2/Exit/L6 direct writes |
| W10 tests | `test_l2_exit_uwg_l4_no_bypass_boundary.py`, `test_apps_rg_exit_uwg_l4_no_bypass_boundary.py` — structural invariants |
| proposed_state_diff | Inert until Exit/UWG (W10) |

**Gap (MEDIUM):** Production call graph to `.admit()` not fully traced via OTel in W11. **Needed for HIGH runtime confidence:** span-tagged proof that live apps_rg commit path invokes `UniversalWriteGate.admit()` before `L4WriteAdapter.write()`.

**Explicit non-claim:** Static grep of `admit(` is not proof of live product reachability.

---

## 7. FINAL_EXECUTION_PROMPT_DRAFT

```text
DO_NOT_RUN_UNTIL_APPROVED — W11 execution (archive/delete)

Preconditions:
- Human approval on w11_gated_archive_delete_plan.md
- M1–M6 migration checklist complete for target batch
- DELETE_READY=YES per candidate in w11_candidate_fanin_matrix.json
- compileall + W10 boundary tests green
- ADG adg_edge_fanin imports=0 for each deleted module

Scope (example batch 1 only):
- After M1: archive agentic_core/L2_execution/apps_rg_l2_binding.py to archives/l2_rationalization_<date>/

Steps:
1. git branch l2-rationalization-w11-exec-<date>
2. Run migrations (imports → canonical binding)
3. Move files per MANIFEST; no delete without fan-in zero
4. python -m compileall agentic_core apps_rg apps_shared -q
5. pytest (contract + boundary suites from W11 receipt)
6. Write artifacts/governance/migration_receipts/<ts>_l2_rationalization_w11.json

Rollback: docs/reports/agent_inventory/w11_rollback_plan.md

Forbidden: weakening X2/X3; live apps_rg proof run; treating stub/mock as product proof.
```

---

## Commands (W11-M2.2 / M3 / M4 prep)

| Command | Exit |
|---------|-----|
| `python -m compileall agentic_core apps_rg apps_shared -q` | 0 |
| `python docs/reports/agent_inventory/_w11_fanin_scan.py` | 0 |
| `python docs/reports/agent_inventory/_w11_adg_expand.py` | 0 |
| `python docs/reports/agent_inventory/_w11_remaining_candidates_prep.py` | 0 |
| `pytest` apps_rg contracts (39) + L2 E2 boundary (13) + Rg* targeted (27) | 0 (79 passed) |

Receipt: [w11_remaining_candidates_prep_receipt.md](w11_remaining_candidates_prep_receipt.md)

---

## Related artifacts

- [w11_gated_archive_delete_plan.json](w11_gated_archive_delete_plan.json)
- [w11_candidate_fanin_matrix.json](w11_candidate_fanin_matrix.json)
- [w11_migration_checklist.md](w11_migration_checklist.md)
- [w11_rollback_plan.md](w11_rollback_plan.md)
- Plan: [.cursor/plans/l2-rationalization-waves-c8e4f1.md](../../.cursor/plans/l2-rationalization-waves-c8e4f1.md)
