# apps_rg R1B W7–W12 closeout

## Summary

The R1B cache track (W7–W12) is reproducible: all seven fixture emitters exit 0, and all 92 dedicated W7–W12 unit/contract tests pass. W7 emitter regression (rejected offline/stub fixtures) is fixed without weakening post-Exit rejection semantics.

## W7 emitter fix

Rejected records (`OFFLINE_CONTRACT_STUB`, `proof_eligible=false`) are not mirrored into `intents/` when UWG promotion blocks non-admissible writes. The emitter now exports those fixtures by building the post-Exit `HistoricalIntentRecord` when the store mirror is absent, while still asserting `cache_admissible=false`.

## Wave index

| Wave | Report manifest |
|------|-----------------|
| W7 | `r1b_semantic_cache_persistence_w7_manifest.json` |
| W8 | `r1b_post_exit_ingestion_w8_manifest.json` |
| W9 | `r1b_whole_run_lookup_w9_manifest.json` |
| W9b | `r1b_whole_run_entrypoint_parity_w9b_manifest.json` |
| W10 | `r1b_uwg_durable_persistence_w10_manifest.json` |
| W10b | `r1b_uwg_receipt_contract_parity_w10b_manifest.json` |
| W11–W12 | `r1b_index_lifecycle_w11_w12_manifest.json` |

Closeout receipt: `r1b_w7_w12_closeout_manifest.json`

## Broader regression note

Required broad filters (`pytest -k r1b`) surface **9 pre-existing failures** outside W7–W12 modules (5× `test_l0_wiring_gaps`, 4× legacy w2/w3/exit contract tests). They were not introduced by this closeout and are listed in the closeout manifest for follow-up.

## Notion

- **Plan (Completed):** [apps-rg-r1b-w7-w12-closeout-e8f4a1](https://www.notion.so/36427693f55c81b28511fcb3b83f0c68)
- **Backlog rows:** W7–W12 each marked **Completed** in Backlog Items DB (linked to plan)
- **Disk index:** `docs/reports/apps_rg/r1b_w7_w12_ssot_index.json`

## Non-claims

- File-backed fixtures are not durable production truth.
- Core `UWGCommitReceipt` field parity is **not** solved (W10b gap carried forward).
- Broad `-k r1b` pytest is not fully green (pre-existing debt documented above).
- No new architecture features were added in closeout.
## 2026-07-06 L4 Best-Practices Hardening Note

R1B fixture mirrors are proof/test-only and no longer serve production lookup
truth when the derived index is missing. Production hits require UWG-admitted
durable projection plus a derived read-surface refresh receipt.
