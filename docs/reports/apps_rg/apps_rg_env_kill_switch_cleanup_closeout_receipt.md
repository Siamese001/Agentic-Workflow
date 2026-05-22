# apps_rg Env Kill-Switch Cleanup — Closeout Receipt (W0–W4)

## STATUS

**PARTIAL** — W0–W4 **complete**. **LIVE_RUNTIME_PROOF** PASS on C0 hybrid seam. **RELEASE_ELIGIBLE_PROOF** not claimed (live run `X3_BLOCK` on product quality).

## PLAN_ID

[apps-rg-env-kill-switch-cleanup-f8e2a3](../../.cursor/plans/apps-rg-env-kill-switch-cleanup-f8e2a3.md)

## CURRENT_WAVE

W4 (complete)

## SCOPE_MATCH

| Locked decision | Evidence |
|-----------------|----------|
| Remove product FEC kill switch | [product_runtime_guards.py](apps_rg/runtime/c0/product_runtime_guards.py) |
| `APPS_RG_C0_EVIDENCE_ROOM=0` fail-closed on product | [section_fec_bridge.py](apps_rg/runtime/section_fec_bridge.py) |
| Positive `c02_vector_query` truth fields | [c02_hybrid_receipt_truth.py](apps_rg/runtime/c0/c02_hybrid_receipt_truth.py) |
| Delete `APPS_RG_SPINE_CHROMA_ENRICH` + C0.5 spine merge | [c05_fec_packet.py](apps_rg/runtime/c0/c05_fec_packet.py) |
| W4 live Brown & Brown hybrid proof | [env_kill_switch_w4_validate_20260522](artifacts/apps_rg/runtime_proofs/executive_summary/real/env_kill_switch_w4_validate_20260522/) |

## SCOPE_DRIFT

None — no `agentic_core` edits; no broad `APPS_RG_*` purge.

## FILES_CHANGED

See [apps_rg_env_kill_switch_cleanup_w1_w3_closeout_receipt.md](apps_rg_env_kill_switch_cleanup_w1_w3_closeout_receipt.md) (W1–W3) plus W4 validation artifact dir (no additional code in W4).

## COMMANDS_RUN

| Command | Result |
|---------|--------|
| `python ops_scripts/ci/check_apps_rg_fact_vectors_readiness.py` | exit 0, 4 OK |
| `python -m pytest tests/_apps_contract/test_apps_rg_env_kill_switch_cleanup.py tests/_apps_contract/test_apps_rg_c0_ownership_split.py tests/_apps_contract/test_apps_rg_c02_product_hybrid_w43.py tests/unit/apps_rg/test_c0_evidence_room.py tests/unit/apps_rg/test_one_spine_fec_bridge_w4.py -q -o addopts=` | exit 0, 64 passed, 2 skipped |
| `python -m apps_rg --section executive_summary … --artifact-dir artifacts/.../env_kill_switch_w4_validate_20260522` | exit 1 (`X3_BLOCK`); C0 hybrid receipts **PASS** |

## TESTS_GATES

| Gate | Result |
|------|--------|
| Env kill-switch contract bundle | 64 passed, 2 skipped |
| CHECK-RG-FACT-VECTORS | PASS |
| W4 `c02_vector_query.json` | `product_hybrid_required=true`, `product_hybrid_attempted=true`, `bm25_available=true`, lanes `completed`, no `spine_chroma_enrich_disabled` |

## ARTIFACTS_WRITTEN

- [env_kill_switch_w4_validate_20260522/](artifacts/apps_rg/runtime_proofs/executive_summary/real/env_kill_switch_w4_validate_20260522/)
- [c02_vector_query.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/env_kill_switch_w4_validate_20260522/c02_vector_query.json)
- [apps_rg_env_kill_switch_cleanup_closeout_receipt.md](docs/reports/apps_rg/apps_rg_env_kill_switch_cleanup_closeout_receipt.md)

## PROOF_CLASSIFICATION

| Class | Claimed |
|-------|---------|
| CONTRACT_TEST_PROOF | Yes (W1–W3) |
| IMPLEMENTATION_RECEIPT | Yes |
| LIVE_RUNTIME_PROOF | Yes (W4.1 C0 hybrid seam) |
| RELEASE_ELIGIBLE_PROOF | No |

## EXPLICIT_NON_CLAIMS

- `RELEASE_ELIGIBLE_PROOF` / `proof_eligible=true` on W4 run
- Full X3 ALLOW (run ended `X3_BLOCK` on product quality)
- Removal of all test-harness `APPS_RG_*` envs (out of charter)

## W4 LIVE RECEIPT SNAPSHOT

From [c02_vector_query.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/env_kill_switch_w4_validate_20260522/c02_vector_query.json):

- `c0_retrieval_mode`: `ledger_plus_hybrid_retrieval`
- `reason`: `product_hybrid_bounded_section_retrieval`
- `product_fail_closed`: true (CLI + embedding settings)
- `proof_classification`: `PRODUCT_STRICT`

## NEXT_BLOCKER

None for this plan. Product-quality X2 failures are follow-on (PA/quality), not env-kill-switch scope.
