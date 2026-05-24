# Executive Summary X1D Transport Parity — Closeout Receipt

**Date:** 2026-05-24  
**Plan:** [exec-summary-x1d-transport-parity-d8f2a1.md](../../.cursor/plans/exec-summary-x1d-transport-parity-d8f2a1.md)  
**Notion:** [36a27693-f55c-8100-81af-f56aa9b4421c](https://www.notion.so/36a27693f55c810081aff56aa9b4421c)

## Status

**PLAN COMPLETE (in-scope)** — W1–W3 + DoD-1–4,6 **PASS**. Post-regen soft-judge rerun uses authoritative **post-X2** packet. Live Brown **2/3** `MODEL_BACKED_PASS` with shared `judge_packet_hash` (transport parity **PASS**). **DoD-5 live 3/3** deferred to [exec-summary-operator-ship-a3f7c2.md](../../.cursor/plans/exec-summary-operator-ship-a3f7c2.md) W5 (synthesis/regen, not X1D transport).

**Plan:** `PLAN_STATUS: COMPLETED` on disk + Notion (2026-05-24).

| Tier | Result |
|------|--------|
| W1–W3 code + CI | PASS |
| Frozen + adversarial + transport + drift tests | PASS |
| Live same `judge_packet_hash` all providers (post-X2) | PASS (`exec_summary_20260524_111311`) |
| Live 3/3 `MODEL_BACKED_PASS` (DoD-4) | **FAIL** (2/3) |

## Live proof — `exec_summary_20260524_111311` (authoritative)

**Command:**

```text
python -m apps_rg --section executive_summary \
  --target-company "Brown & Brown" \
  --target-role "SVP IT Strategy & Innovation" \
  --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt \
  --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md
```

**Shell exit:** `0` | **OPERATOR_STATUS:** `DRAFT_READY` | **CERTIFIED:** `false`

| Provider | `provider_status` | Score | `judge_packet_ref` |
|----------|-------------------|-------|---------------------|
| Gemini | `MODEL_BACKED_PASS` | 4.0 | `executive_summary_judge_packet_post_x2.json` |
| OpenAI | `MODEL_BACKED_PASS` | 4.3 | `executive_summary_judge_packet_post_x2.json` |
| Claude | `MODEL_BACKED_FAIL` | 3.2 | `executive_summary_judge_packet_post_x2.json` |

Shared `judge_packet_hash`: `071e3716e8a3d81e` (all three).

**Post-X2 refresh:** Claude 2.4 → 3.2 on same contract ([post_x2_x1d_refresh_receipt.json](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260524_111311/post_x2_x1d_refresh_receipt.json)).

**Judge regen:** accepted then **reverted** — `x2_executive_summary_synthesis_quality`, `x2_exec_summary_mechanical_opener_stack_zero` ([judge_remediation_receipt.json](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260524_111311/judge_remediation_receipt.json)).

**Artifacts:** [x1d_llm_judge_outputs.json](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260524_111311/x1d_llm_judge_outputs.json) · [canonical_judge_contract.json](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260524_111311/canonical_judge_contract.json)

## Closeout patches (2026-05-24)

| Fix | Path |
|-----|------|
| Soft-judge rerun uses post-X2 gate summary (not pre-X2 packet) | [executive_summary_judge_remediation.py](../../apps_rg/runtime/sections/executive_summary_judge_remediation.py) |
| Lane passes `x2_gates` into soft rerun | [executive_summary_lane.py](../../apps_rg/runtime/sections/executive_summary_lane.py) |
| Regen user message: X2 phrase guards + synthesis shape | [executive_summary_judge_remediation.py](../../apps_rg/runtime/sections/executive_summary_judge_remediation.py) |

## Verification commands

```text
python ops_scripts/ci/check_section_x2_x1d_drift.py -> exit 0

PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest \
  tests/unit/apps_rg/test_executive_summary_x1d_judge_contract.py \
  tests/unit/apps_rg/test_x1d_canonical_contract_hash_parity.py \
  tests/unit/apps_rg/test_x1d_provider_transport_parity.py \
  tests/unit/apps_rg/test_executive_summary_judge_remediation.py \
  tests/_apps_contract/test_section_x2_x1d_drift_ci.py -q -o addopts= -> passed
```

## Explicit non-claims

- Does **not** certify other sections’ X1D transport
- Does **not** change operator CERTIFIED quorum policy
- Does **not** weaken X2 or reconcile-launder residual synthesis FAILs
- Does **not** make Claude optional
- Does **not** claim plan PASS on DoD-4 until 3/3 `MODEL_BACKED_PASS`

## Deferred (operator-ship)

`DEFERRED_SCOPE: live_brown_3_of_3_model_backed_pass` → [exec-summary-operator-ship-a3f7c2.md](../../.cursor/plans/exec-summary-operator-ship-a3f7c2.md) W5: judge regen surviving `x2_executive_summary_synthesis_quality` + Claude ≥ 4.0 on post-X2 packet.
