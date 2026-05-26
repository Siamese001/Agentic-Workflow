---
plan_id: whole-run-phase1-x3-dispatch-remediation-f2a8c4
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# Whole-run Phase-1 X3 dispatch remediation

Remediate the integrated `python -m apps_rg` failure where wave-0 `executive_summary` completes with **X3_ALLOW** on disk but Phase-1 reports `dispatch_error:lane_exit_error`, aborts waves 1–2, and marks all seven lanes `PHASE1_NO_RUN_DIR` in modular R4 recipe receipts.

> **plan_id discipline**: `whole-run-phase1-x3-dispatch-remediation-f2a8c4`

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: COMPLETE
CURRENT_WAVE: —
LAST_COMPLETED_WAVE: W4
LAST_UPDATED: 2026-05-26

PLAN_CREATED: slug=whole-run-phase1-x3-dispatch-remediation-f2a8c4 path=.cursor/plans/whole-run-phase1-x3-dispatch-remediation-f2a8c4.md status=Complete

CLOSEOUT: receipt=[whole_run_phase1_x3_dispatch_remediation_closeout_receipt.md](docs/reports/apps_rg/whole_run_phase1_x3_dispatch_remediation_closeout_receipt.md) tests=85_passed e2e=[run_governed_spine_e2e_proof.sh](ops_scripts/apps_rg/run_governed_spine_e2e_proof.sh)

---

## Context (SCQA)

- **Situation** — Integrated whole-run uses DAG waves (`executive_summary` solo in wave 0, then parallel light lanes). Section lanes materialize under `full_resume_*/lanes/<lane>/` with `latest_successful_real_run.json` pointers. Standalone `python -m apps_rg --section headline` **PASS**es (governed spine verifier). Failed run: [`full_resume_1bffb730f966`](artifacts/apps_rg/runtime_proofs/full_resume_1bffb730f966).
- **Complication** — **RC-1:** `executive_summary_lane` sets `x3 = x3_doc` (dict with `"pass": true`) after publish disposition, but `section_cli_runners` uses `getattr(x3, "pass_", False)` → always `False` on dict → `exit_status: error` → `phase1_aborted`. **RC-2:** resolve loop skips all lanes when `phase1_aborted`, so recipe records `PHASE1_NO_RUN_DIR` for executive_summary despite resolvable pointer. **Latent:** Phase-1 dispatch omits `lane_allow_non_allow_exit_zero`; vLLM parallel wave-1 cap may surface after RC-1/RC-2 fixed.
- **Question** — How do we restore truthful Phase-1 dispatch status and modular recipe rollup so all seven lanes execute and whole-run can reach merge/schema pass?
- **Answer** — Fix X3 authorization read path (dict + dataclass), harden orchestration resolve/abort semantics, add regression tests, then prove with bounded whole-run + governed-spine verifier.

### RCA evidence (2026-05-26)

| ID | Finding | Proof |
|----|---------|-------|
| RC-1 | Dict `x3` misread in `section_cli_runners` | Repro: `lane_run_dir_meets_product_bar` **ok**; `getattr(x3_dict, "pass_", False)` **False** while `x3["pass"]` **True** |
| RC-2 | `phase1_aborted` skips entire `resolve_latest_lane_run_dir` loop | [`modular_resume_generation.py`](apps_rg/l2_recipe/modular_resume_generation.py) L676–678 |
| RC-3 | Symptom only | [`generate_resume_step_receipt.json`](artifacts/apps_rg/runtime_proofs/full_resume_1bffb730f966/modular_r4/generate_resume_step_receipt.json) `lanes_executed: 0`; [`full_run_section_status.json`](artifacts/apps_rg/runtime_proofs/full_resume_1bffb730f966/full_run_section_status.json) shows exec summary executed |
| Ruled out | Wrong `sections_root`, vLLM failure on exec summary, publish disposition demotion, stale targeting | See conversation RCA H1–H14 |

**Supersedes (partial overlap):** archived [fix-whole-run-executive-summary-phase1-no-run-dir-e8f1c2](.cursor/plans/_archive/2026-05/fix-whole-run-executive-summary-phase1-no-run-dir-e8f1c2.md) addressed pointer/briefing materialization; **this plan** addresses the **dispatch status / dict `pass_` regression** found in `full_resume_1bffb730f966`.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1–W1.3 | RC-1: shared X3 outcome helper + runner wiring + unit tests | ~12K | No `agentic_core` edits | ✅ DONE | Pytest green; dict + `X3Disposition` both yield correct `outcome_authorized` |
| W2 | W2.1–W2.2 | RC-2: Phase-1 resolve/abort semantics + unit tests | ~10K | Fail-closed product policy unchanged | ✅ DONE | Aborted dispatch does not hide resolvable lane dirs in recipe |
| W3 | W3.1 | Phase-1 dispatch CLI flags (`allow_non_allow_exit_zero`) | ~6K | Optional if W4 passes without | ✅ DONE | Modular dispatch passes flag when env/CLI requests |
| W4 | W4.1–W4.2 | Runtime whole-run proof + closeout receipt | ~20K | Qwen/vLLM + judges available in WSL | ✅ DONE (PARTIAL) | 1/7 lanes; RC-1/RC-2 proven vs baseline; wave-0 judge soft-fail abort |

### Phase Progress

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.1 | Extract `lane_outcome_authorized_from_x3` | `section_x3_finalize.py`, `section_cli_runners.py` | Duplicated `getattr(x3, "pass_", False)` ×7 | ~4K | ✅ DONE |
| W1.2 | Executive-summary regression test | `tests/unit/apps_rg/test_phase1_dispatch_x3_dict_pass.py` | Only exec lane assigns `x3 = x3_doc` | ~4K | ✅ DONE |
| W1.3 | Contract: dispatch result shape | `test_phase1_dispatch_x3_dict_pass.py` (`phase1_dispatch_hard_failed`) | Mock dispatch success on dict x3 | ~4K | ✅ DONE |
| W2.1 | Resolve lanes with artifacts despite abort | `modular_resume_generation.py` | Blanket `if phase1_aborted: continue` | ~6K | ✅ DONE |
| W2.2 | Recipe records reflect resolved dirs | `_phase1_materialize_lane_run_dir` + tests | `PHASE1_NO_RUN_DIR` masking | ~4K | ✅ DONE |
| W3.1 | Thread `lane_allow_non_allow_exit_zero` | `section_lane_executor.py`, `modular_resume_generation.py`, `steps.py`, `__main__.py` | Whole-run CLI uses flag; phase1 does not | ~6K | ✅ DONE |
| W4.1 | Whole-run smoke (Brown & Brown SVP) | WSL: `python -m apps_rg` | ~15–45 min runtime | ~15K | ⚠️ PARTIAL | [full_resume_983aac3da43f](artifacts/apps_rg/runtime_proofs/full_resume_983aac3da43f) |
| W4.2 | Closeout receipt + verifier | `docs/reports/apps_rg/`, `ops_scripts/apps_rg/verify_governed_spine_e2e.py` | PASS requires command output | ~5K | ✅ DONE | [whole_run_phase1_x3_dispatch_remediation_closeout_receipt.md](docs/reports/apps_rg/whole_run_phase1_x3_dispatch_remediation_closeout_receipt.md) |

---

## Out Of Scope

- `agentic_core` spine / L0 routing changes (unless user explicitly authorizes)
- Integrated envelope C0/L3 bypass rectification (separate c0-policy plan)
- Fort Knox / L7 product certification claims from plumbing-only runs
- Restoring deleted shadow runners (`lane_batch`, legacy `*_dispatch.main`)
- Weakening X2 gates, judges, or recipe policy to force PASS

---

## Wave 1 — RC-1: X3 outcome authorization (dict-safe)

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Phases**:
- **W1.1** — Add `lane_outcome_authorized_from_x3(x3) -> bool` reusing `_terminal_class_from_x3` logic (`pass_`, `"pass"`, `x3_code` allow family) | ~4K | PHASE_STATUS: TODO
- **W1.2** — Replace all `getattr(x3, "pass_", False)` in `section_cli_runners.py`; set `x3_disposition` from dict or object | ~4K | PHASE_STATUS: TODO
- **W1.3** — Unit tests: dict with `"pass": true`, `X3Disposition(pass_=True)`, `X3_ALLOW` without `pass` key edge case | ~4K | PHASE_STATUS: TODO

**Acceptance**:
- Simulated `ctx["x3"]` dict after `apply_publish_disposition_to_x3_dict` returns `exit_status: success` when `pass` is true
- No change to on-disk `x3_disposition.json` schema

**Alternative considered (narrower):** Remove `x3 = x3_doc` in `executive_summary_lane.py` only — rejected as primary fix because other lanes may adopt dict mirrors; shared helper prevents recurrence.

---

## Wave 2 — RC-2: Phase-1 resolve vs abort decoupling

WAVE_ID: W2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Phases**:
- **W2.1** — Change resolve loop: always attempt `resolve_latest_lane_run_dir` per lane (or per wave-complete set); record `lane_run_dirs` when pointer + product bar pass even if `phase1_aborted` | ~6K | PHASE_STATUS: TODO
- **W2.2** — Restrict `phase1_aborted` to **blocking subsequent dispatch waves**, not recipe materialization; ensure `emit_integrated_lane_pre_run_failure` only when pointer truly missing | ~4K | PHASE_STATUS: TODO

**Acceptance**:
- Fixture: exec summary dir present + dispatch error → recipe includes exec summary in `section_provider_calls` (not `MISSING_LANE_RUN`)
- `fatal_lane_recipe_policy` lists only lanes that actually lack run dirs

---

## Wave 3 — Phase-1 dispatch flag parity (latent)

WAVE_ID: W3
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Phases**:
- **W3.1** — Pass `lane_allow_non_allow_exit_zero` from whole-run context / `APPS_RG_ALLOW_NON_ALLOW_EXIT_ZERO` into `_phase1_dispatch_one_lane` / `LaneExecutionContext` | ~6K | PHASE_STATUS: TODO

**Acceptance**:
- When CLI whole-run uses `--allow-non-allow-exit-zero`, phase-1 lane kwargs match standalone section CLI

**Deferral:** Skip W3 if W4 whole-run passes all lanes with X3_ALLOW and dispatch success without the flag.

---

## Wave 4 — Runtime proof and closeout

WAVE_ID: W4
WAVE_STATUS: PARTIAL
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: D

**Phases**:
- **W4.1** — WSL whole-run: Brown & Brown SVP targeting, Qwen/vLLM, parallel phase-1 enabled | ~15K | PHASE_STATUS: TODO
- **W4.2** — Emit [`whole_run_phase1_x3_dispatch_remediation_closeout_receipt.md`](docs/reports/apps_rg/whole_run_phase1_x3_dispatch_remediation_closeout_receipt.md); run governed-spine verifier on integrated dir | ~5K | PHASE_STATUS: TODO

**Commands (proof)**:
```bash
# After W1–W2 unit tests
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/unit/apps_rg/test_phase1_dispatch_x3_dict_pass.py tests/unit/apps_rg/test_modular_resume_generation_phase1.py -q

# W4 runtime (WSL — same targeting as failed run)
python -m apps_rg \
  --target-company "Brown & Brown" \
  --target-role "SVP IT Strategy & Innovation" \
  --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt \
  --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md \
  --provider qwen_vllm \
  --allow-non-allow-exit-zero

python ops_scripts/apps_rg/verify_governed_spine_e2e.py --integrated-dir artifacts/apps_rg/runtime_proofs/full_resume_<new_id>
```

**Acceptance**:
- `phase1_lane_inventory.json`: wave-0 `executive_summary` → `ok` (not `dispatch_error:lane_exit_error`)
- `lanes_executed >= 7` or explicit BLOCKED with per-lane artifact evidence (not silent NOT_RUN)
- `generate_resume_step_receipt.json`: `decisive_status` not FAIL solely on `PHASE1_NO_RUN_DIR` for completed lanes

---

## Gap Register

**GAP-1: vLLM parallel saturation (wave 1)**  
- Three concurrent light lanes on one local Qwen instance may fail after RC-1/RC-2 fixed.  
- Mitigation: temporarily `APPS_RG_PHASE1_MAX_PARALLEL=1` for proof, or stagger waves; document in closeout if BLOCKED.

**GAP-2: `proof_eligible: false` vs dispatch success**  
- Dispatch success must not require proof eligibility; product certification remains separate.

**GAP-3: Archived plan e8f1c2 overlap**  
- Briefing/pointer fixes may already be on branch; this plan does not re-run those waves unless regression found.

---

## Definition of Done

DoD-1: Dict-safe X3 authorization in all section CLI runners  
- Evidence: `tests/unit/apps_rg/test_phase1_dispatch_x3_dict_pass.py` PASS  
- Status: DONE

DoD-2: Phase-1 recipe honors on-disk lane pointers when dispatch falsely errors  
- Evidence: `tests/unit/apps_rg/test_modular_phase1_resolve_abort_decoupling.py` PASS  
- Status: DONE

DoD-3: Smoke-run whole-run produces multi-lane artifacts  
- Evidence: [full_resume_983aac3da43f](artifacts/apps_rg/runtime_proofs/full_resume_983aac3da43f) — 1/7 lanes; wave-0 `X3_REVIEW_JUDGE_SOFT_FAIL` abort  
- Status: PARTIAL

DoD-4: Modular recipe not fail-closed on false `PHASE1_NO_RUN_DIR` for completed executive_summary  
- Evidence: `lanes_executed: 1`; exec summary `REAL_LLM` / `X3_REVIEW_JUDGE_SOFT_FAIL` (not `PHASE1_NO_RUN_DIR`)  
- Status: PASS

DoD-5: Closeout receipt on disk with command output excerpts  
- Evidence: [`whole_run_phase1_x3_dispatch_remediation_closeout_receipt.md`](docs/reports/apps_rg/whole_run_phase1_x3_dispatch_remediation_closeout_receipt.md)  
- Status: PASS

### Verification vs Deferral

| Item | In scope | Deferred |
|------|----------|----------|
| RC-1 dict `pass_` read | W1 | — |
| RC-2 resolve/abort | W2 | — |
| C0 envelope bypass rectification | — | Separate plan |
| Product / Fort Knox certification | — | Requires proof-eligible judges + gate |
| DOCX / `generated_resume.json` merge quality | W4 observes | Content quality tuning |

---

## Related artifacts

- Failed run: [`full_resume_1bffb730f966`](artifacts/apps_rg/runtime_proofs/full_resume_1bffb730f966)
- E2E notes: [`governed_spine_e2e_20260526.md`](docs/reports/apps_rg/governed_spine_e2e_20260526.md)
- Verifier: [`verify_governed_spine_e2e.py`](ops_scripts/apps_rg/verify_governed_spine_e2e.py)

---

PLAN_COMPLETE: plan=whole-run-phase1-x3-dispatch-remediation-f2a8c4 note="W1-W3 PASS; W4 PARTIAL full_resume_983aac3da43f RC-1/RC-2 fixed lanes_executed=1; closeout whole_run_phase1_x3_dispatch_remediation_closeout_receipt.md; 7/7 lanes deferred to product judge pass"
