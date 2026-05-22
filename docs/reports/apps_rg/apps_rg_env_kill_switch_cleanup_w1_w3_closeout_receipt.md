# apps_rg Env Kill-Switch Cleanup — W1–W3 Closeout Receipt

**PLAN_ID:** [apps-rg-env-kill-switch-cleanup-f8e2a3](../../.cursor/plans/apps-rg-env-kill-switch-cleanup-f8e2a3.md)  
**Review:** Approved 2026-05-22 with material hardenings (FEC kill switch removed for product; C0_EVIDENCE_ROOM=0 fail-closed; positive receipt truth fields).

## STATUS

**PARTIAL** — W1–W3 **CONTRACT_TEST_PROOF** complete. W4 **BLOCKED** (parent BM25 index seeding + live Brown & Brown exec-summary run not in scope).

## SCOPE_MATCH

| Locked decision | Implemented |
|-----------------|-------------|
| Remove product FEC kill switch (test harness bypass only) | [product_runtime_guards.py](../../apps_rg/runtime/c0/product_runtime_guards.py) — `product_fec_bridge_mandatory()`; env `APPS_RG_SECTION_FEC_BRIDGE_KILL_SWITCH=0` forbidden on product |
| `APPS_RG_C0_EVIDENCE_ROOM=0` fail-closed on product | `assert_canonical_product_section_env()` in [wire_section_fec_bridge_for_lane](../../apps_rg/runtime/section_fec_bridge.py) |
| Positive `c02_vector_query` truth fields | [c02_hybrid_receipt_truth.py](../../apps_rg/runtime/c0/c02_hybrid_receipt_truth.py) |
| Delete `APPS_RG_SPINE_CHROMA_ENRICH` + spine merge in C0.5 | [c05_fec_packet.py](../../apps_rg/runtime/c0/c05_fec_packet.py) — no `c0_retrieve_apps_rg` |
| W4 not claimed | Deferred |

## SCOPE_DRIFT

None — no `agentic_core` edits; no BM25 seeding; no broad `APPS_RG_*` purge.

## FILES_CHANGED

- [product_runtime_guards.py](apps_rg/runtime/c0/product_runtime_guards.py)
- [c02_hybrid_receipt_truth.py](apps_rg/runtime/c0/c02_hybrid_receipt_truth.py)
- [c0_section_authority.py](apps_rg/runtime/c0/c0_section_authority.py)
- [c05_fec_packet.py](apps_rg/runtime/c0/c05_fec_packet.py)
- [evidence_room.py](apps_rg/runtime/c0/evidence_room.py)
- [c02_product_hybrid_retrieval.py](apps_rg/runtime/c0/c02_product_hybrid_retrieval.py)
- [c02_chroma_lifecycle.py](apps_rg/runtime/c02_chroma_lifecycle.py)
- [c07_handoff_audit.py](apps_rg/runtime/c0/c07_handoff_audit.py)
- [constants.py](apps_rg/runtime/c0/constants.py)
- [section_fec_bridge.py](apps_rg/runtime/section_fec_bridge.py)
- [executive_summary_pa.py](apps_rg/runtime/sections/executive_summary_pa.py)
- [test_apps_rg_env_kill_switch_cleanup.py](tests/_apps_contract/test_apps_rg_env_kill_switch_cleanup.py)
- [test_apps_rg_c0_ownership_split.py](tests/_apps_contract/test_apps_rg_c0_ownership_split.py)
- [test_apps_rg_c02_product_hybrid_w43.py](tests/_apps_contract/test_apps_rg_c02_product_hybrid_w43.py)
- [test_c0_evidence_room.py](tests/unit/apps_rg/test_c0_evidence_room.py)
- [c0_evidence_room_stress.py](tools/apps_rg/c0_evidence_room_stress.py)
- [apps_rg_runtime_proof.md](docs/cursor/apps_rg_runtime_proof.md)
- [apps-rg-env-kill-switch-cleanup-f8e2a3.md](../../.cursor/plans/apps-rg-env-kill-switch-cleanup-f8e2a3.md)

## COMMANDS_RUN

| Command | Exit |
|---------|------|
| `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=<repo> python -m pytest tests/_apps_contract/test_apps_rg_env_kill_switch_cleanup.py tests/_apps_contract/test_apps_rg_c0_ownership_split.py tests/_apps_contract/test_apps_rg_c02_product_hybrid_w43.py tests/unit/apps_rg/test_c0_evidence_room.py tests/unit/apps_rg/test_one_spine_fec_bridge_w4.py -q -o addopts=` | **0** (64 passed, 2 skipped) |
| `git diff --name-only agentic_core` | **0** (no output) |

## TESTS_GATES

- [test_apps_rg_env_kill_switch_cleanup.py](tests/_apps_contract/test_apps_rg_env_kill_switch_cleanup.py) — negative controls: C0_EVIDENCE_ROOM=0, FEC bridge disabled, positive receipt keys, no `APPS_RG_SPINE_CHROMA_ENRICH` in `apps_rg/`
- [test_apps_rg_c0_ownership_split.py](tests/_apps_contract/test_apps_rg_c0_ownership_split.py) — import boundary + C05/C07
- [test_apps_rg_c02_product_hybrid_w43.py](tests/_apps_contract/test_apps_rg_c02_product_hybrid_w43.py) — hybrid receipt truth
- [test_c0_evidence_room.py](tests/unit/apps_rg/test_c0_evidence_room.py) — room integration
- [test_one_spine_fec_bridge_w4.py](tests/unit/apps_rg/test_one_spine_fec_bridge_w4.py) — FEC bridge preconditions

## ARTIFACTS_WRITTEN

- [apps_rg_env_kill_switch_cleanup_w1_w3_closeout_receipt.md](apps_rg_env_kill_switch_cleanup_w1_w3_closeout_receipt.md)

## FORBIDDEN_FILES_TOUCHED

**None** — `git diff --name-only agentic_core` returned empty.

## PROOF_CLASSIFICATION

| Class | Claimed |
|-------|---------|
| CONTRACT_TEST_PROOF | **Yes** |
| IMPLEMENTATION_RECEIPT | **Yes** |
| LIVE_RUNTIME_PROOF | **No** |
| RELEASE_ELIGIBLE_PROOF | **No** |

## EXPLICIT_NON_CLAIMS

- No Brown & Brown live `executive_summary` run with `product_hybrid_attempted=true`
- No BM25 sparse index seeding (parent substitute burndown)
- No release eligibility from contract tests alone
- Historical runtime proof dirs may still contain `spine_chroma_enrich` in JSON (pre-cleanup artifacts)

## NEXT_BLOCKER

**W4:** Seed BM25 sparse index per [apps-rg-runtime-substitute-burndown-c4e8f1.md](../../.cursor/plans/apps-rg-runtime-substitute-burndown-c4e8f1.md), then run canonical Brown & Brown `executive_summary` and verify `c02_vector_query.json` has `product_hybrid_required=true`, `product_hybrid_attempted=true`, `bm25_available=true`.
