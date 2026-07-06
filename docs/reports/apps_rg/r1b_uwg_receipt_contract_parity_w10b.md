# W10b — apps_rg R1B UWG receipt contract parity

**Wave:** W10b  
**Status:** PARTIAL (apps_rg end-to-end PASS; core receipt field gap documented)  
**Date:** 2026-05-18

## Goal

Harden W10 so durable R1B promotion preserves required governance refs end-to-end and blocks admission when refs are missing.

## Receipt field parity matrix

| Field | CommitRequest | StateDiff | UWGCommitReceipt (core) | apps_rg governance sidecar |
|---|---|---|---|---|
| source_surface | yes (Exit) | proposed_by_surface=Exit | no (committed_by_surface=UWG) | yes |
| l5_certification_ref | yes | no | shim_patched | yes |
| gate_verdict_refs | yes | no | no | yes |
| replay_key | yes | replay_refs | no | yes |
| policy_hash | yes | optional policy_refs | no | yes |
| blueprint_hash | yes | no | no | yes |
| affected_state_surfaces | yes | target_surface | yes | yes |
| cleared_exit_review_packet_ref | yes | no | no | yes |

## Shim vs core gap

Stock `DurableWriteGateway.commit` does not pass `l5_certification_ref` into `UWGCommitReceipt` construction. `AppsRgR1BUwgGateway` patches receipt `__new__` to inject l5, affected_state_surfaces, and audit_refs from `CommitRequest`.

Fields **not** on core `UWGCommitReceipt`: `gate_verdict_refs`, `replay_key`, `policy_hash`, `blueprint_hash`, `source_surface`, `cleared_exit_review_packet_ref`. These are preserved in the apps_rg `governance_receipt` sidecar on durable projection bundles.

## Pre-UWG validation

`validate_commit_request_governance()` fail-closes before `gateway.commit()` when any required ref is missing or placeholder.

## Fixtures

| Artifact | Path |
|---|---|
| Admitted + l5 | `artifacts/apps_rg/r1b_semantic_cache/w10b_fixtures/admitted_receipt_with_l5.json` |
| Blocked missing l5 | `artifacts/apps_rg/r1b_semantic_cache/w10b_fixtures/blocked_missing_l5.json` |
| Blocked missing gate | `artifacts/apps_rg/r1b_semantic_cache/w10b_fixtures/blocked_missing_gate_verdict.json` |
| Parity matrix | `artifacts/apps_rg/r1b_semantic_cache/w10b_fixtures/receipt_field_parity_matrix.json` |
| Shim/core gap | `artifacts/apps_rg/r1b_semantic_cache/w10b_fixtures/shim_vs_core_gap.json` |

Emitter: `python tools/apps_rg/emit_r1b_w10b_fixtures.py`

## W10 regression

W10 unit/contract tests and W7–W9b suites re-run in manifest.

## Non-claims

- Full parity on bare `UWGCommitReceipt` without apps_rg sidecar (PARTIAL by design).
- No `agentic_core` edits.
## 2026-07-06 Core Receipt Parity Update

`UWGCommitReceipt` now carries R1B durable-write provenance directly, including
L5 ref, gate refs, policy/blueprint hash, replay key, clearance proof,
staged-diff hash, content hash, and audit chain hash. The apps_rg sidecar
remains a projection convenience, not the only provenance source.
