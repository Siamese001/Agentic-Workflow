# Executive summary X2/X1D drift CI + judge X2 repair closeout

**Date:** 2026-05-24  
**Scope:** Multi-lane X2/X1D contract CI, judge-regen monotonicity RCA, adversarial tests, Brown & Brown live proof.

## Deliverables

| Item | Path |
|------|------|
| Per-lane drift contract | [section_x2_x1d_contract.py](../../apps_rg/runtime/sections/section_x2_x1d_contract.py) |
| Exec extensions (synthesis, judge packet, repair loop) | [executive_summary_x2_x1d_contract.py](../../apps_rg/runtime/sections/executive_summary_x2_x1d_contract.py) |
| CI gate (7 lanes) | [check_section_x2_x1d_drift.py](../../ops_scripts/ci/check_section_x2_x1d_drift.py) |
| Adversarial tests | [test_executive_summary_x2_x1d_adversarial.py](../../tests/unit/apps_rg/test_executive_summary_x2_x1d_adversarial.py) |
| Monotonicity fix | [executive_summary_synthesis_monotonic.py](../../apps_rg/runtime/sections/executive_summary_synthesis_monotonic.py) |

## RCA (cycle-2 monotonicity block — run `exec_summary_20260524_005722`)

Judge regen failed X2 on `sentence_count_6`, `synthesis_quality`, `no_inferred_bridge_claims`. X2-aware repair was rejected because `evaluate_synthesis_regen_monotonicity` used **synthesis_regen** rules: gate-id reject reasons did not trigger waivers, and 7→6 `source_fact_ids` was treated as regression.

**Fix:** `repair_context="judge_x2_repair"` + `failed_gate_ids` from X2 rows; waive shrink and allow controlled substance regression when fixing shape gates.

## Live proof — Brown & Brown SVP IT Strategy & Innovation

| Run ID | Exit | Operator | Judge cycles | X2 after regen | Notes |
|--------|------|----------|--------------|----------------|-------|
| [exec_summary_20260524_005722](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260524_005722) | 0 | DRAFT_READY | 2 | FAIL → repair blocked by monotonicity | Pre-fix |
| [exec_summary_20260524_014222](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260524_014222) | 0 | DRAFT_READY | **3** (max) | **PASS** each cycle | Post-fix; Claude still soft-fail |

Post-fix run artifacts: [judge_remediation_cycles.json](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260524_014222/judge_remediation_cycles.json) (`stopped_reason: max_cycles_reached`), no `judge_regen_x2_repair_receipt.json` (X2 stayed green on regen).

## Verification commands

```bash
python ops_scripts/ci/check_section_x2_x1d_drift.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest \
  tests/unit/apps_rg/test_executive_summary_x2_x1d_adversarial.py \
  tests/_apps_contract/test_section_x2_x1d_drift_ci.py \
  tests/unit/apps_rg/test_executive_summary_synthesis_monotonic.py -q
```

## Out of scope (unchanged)

- 2/3 judge quorum for CERTIFIED
- `repair_summary.json` consolidation (W4)
- Claude threshold / calibration changes
