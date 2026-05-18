# W10 — apps_rg R1B UWG durable persistence

**Wave:** W10  
**Status:** PASS  
**Date:** 2026-05-18

## Goal

Move R1B semantic-cache durable admission from file-backed-only writes to governed **Exit → UWG → L4** promotion, while keeping file-backed paths as **fixture/proof mirrors** only.

## Durable write path

```
Post-Exit eligibility (W8)
  → R1BCachePromotionCandidate
  → CommitRequest (source_surface=Exit)
  → DurableWriteGateway.commit()
  → UWGCommitReceipt (ADMITTED) | UWGBlockedCommitReceipt (BLOCKED)
  → durable/uwg_admitted/ projection (ADMITTED only)
  → optional fixture mirror (tests / backward compat)
```

**Target surface:** `l4.apps_rg.r1b_semantic_cache`  
**Operation:** `memory_promotion`

## CommitRequest fields (representative)

| Field | Value |
|---|---|
| `source_surface` | `Exit` |
| `cleared_exit_review_packet_ref` | `exit_packet_digest:<x3 digest>` |
| `affected_state_surfaces` | `l4.apps_rg.r1b_semantic_cache` |
| `gate_verdict_refs` | `gv:r1b:post_exit:<run_id>` |
| `l5_certification_ref` | `l5:r1b:post_exit:<run_id>` |
| `replay_key` | `r1b:<normalized_intent_digest>` |
| `state_diff.operation_type` | `memory_promotion` |

## Direct-write guards

- `assert_r1b_durable_write_authority` blocks **L2**, **L6**, and other non-Exit surfaces.
- `DurableWriteGateway.reject_direct_write` emits blocked receipts for proof.

## File-backed tier

`R1BSemanticCacheStore.storage_tier = fixture_proof_mirror` with `is_durable_production_truth: false` in `store_manifest()`.

## Fixtures

| Fixture | Path |
|---|---|
| UWG admitted | `artifacts/apps_rg/r1b_semantic_cache/w10_fixtures/uwg_admitted_promotion.json` |
| Blocked promotion | `artifacts/apps_rg/r1b_semantic_cache/w10_fixtures/blocked_promotion.json` |
| L2 blocked | `artifacts/apps_rg/r1b_semantic_cache/w10_fixtures/l2_direct_write_blocked.json` |
| L6 blocked | `artifacts/apps_rg/r1b_semantic_cache/w10_fixtures/l6_direct_write_blocked.json` |
| Non-durable manifest | `artifacts/apps_rg/r1b_semantic_cache/w10_fixtures/file_backed_non_durable_manifest.json` |

Emitter: `python tools/apps_rg/emit_r1b_w10_fixtures.py`

## W7–W9b regression

W7/W8/W9/W9b contract tests re-run in W10 receipt; behavior preserved via fixture mirror on blocked UWG env and unchanged lookup paths.

## apps_rg UWG gateway shim

`AppsRgR1BUwgGateway` (apps_rg-only) patches `UWGCommitReceipt` construction so
`l5_certification_ref` is copied from `CommitRequest` until core propagates it
generically. Fixture emitters set `APPS_RG_R1B_SKIP_UWG=1` to keep W7–W9b
file-mirror fixtures stable.

## Non-claims

- No `agentic_core` edits.
- No section-level R1B lookup.
- No C0 `fact_vectors` for R1B identity.
- File-backed artifacts are not durable production SSOT.
