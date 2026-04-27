========================================================================================================================
MECE ALIGNMENT FULL OVERWRITE HEADER
Canonical filename: 00B_L4_State_Archive_and_UWG.md
Layer / subsystem: 00B — L4 State, Archive, and UWG (parent)
Parent file: docs/reference/README.md
Ownership surface: Durable system-of-record state (policy/blueprint/registry, memory and learning promotion, retrieval surface, cache, replay snapshot/audit ledger, read surface refresh, blueprint/policy migration) AND the Universal Write Gateway (sole durable-write admission).
Overwrite mode: full-file, no-overlap, executable contract
No-overlap boundary: 00B owns L4 state and UWG admission. It does not own planning (02), routing (03), retrieval (03A), prompt assembly (03B), execution (04), Exit disposition (05), or L6 learning mechanics (06). Live gate verdicts are 00C; certification is 00A; E2E proof is 99.
Source authority notes: Anchored on `00X` REQ_ID registry; aligned with constitutional §22, §23, §24.
Predecessor preserved at: `00B_L4_State_Archive_and_UWG.md.pre-reqid-rewrite.bak`
========================================================================================================================

1. PURPOSE
------------------------------------------------------------------------------------------------------------------------
This parent uniquely owns:
- the durable system-of-record state contract
- the **Universal Write Gateway** sole-admission invariant for durable writes
- the read surface refresh / projection rule
- the per-state-domain parent REQ_IDs

It does **not** own:
- per-domain detail (lives in `00B.1`..`00B.9`)
- live gate decisions (00C)
- certification evidence (00A)
- runtime planning, routing, retrieval, prompt assembly, execution, Exit, or L6 mechanics

2. AUTHORITY BOUNDARY
------------------------------------------------------------------------------------------------------------------------
**Upstream inputs**:
- `CommitRequest` from Exit (the only path to durable writes)
- L4 read requests from any layer
- Snapshot/audit refresh triggers

**Downstream outputs**:
- `UWGCommitReceipt` per accepted commit
- L4 read projections (cache state, retrieval surface, registry/policy/blueprint state)

**Forbidden behaviors**:
- 00B MUST NOT make routing or final-response decisions.
- 00B MUST NOT skip UWG; every durable write goes through UWG.
- 00B MUST NOT issue certifications (00A only).
- 00B MUST NOT mutate state on a non-cleared `CommitRequest`.

**Allowed outputs only**: durable state, read projections, UWG commit receipts, snapshot/audit ledger entries.

3. REQ_ID NAMESPACE
------------------------------------------------------------------------------------------------------------------------
This pack owns rows under `REQ-L4-*` and `REQ-UWG-*`.

4. ATOMIC REQUIREMENTS TABLE (PARENT-LEVEL INVARIANTS)
------------------------------------------------------------------------------------------------------------------------

| REQ_ID | Requirement | Owner | Inputs | Outputs | Runtime Evidence | OTEL Span | Artifact / Receipt | Validator | Negative Control | Expected Fail Reason | Replay Check | Release Gate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `REQ-UWG-SOLE-DURABLE-WRITE-001` | UWG MUST be the sole durable-write admission gateway into L4. Direct writes from L0, L1, C0, PA, L3, L2, HITL, L5, or L6 are FORBIDDEN. | 00B.6 | `CommitRequest` | `UWGCommitReceipt` | every L4 mutation has a matching `UWGCommitReceipt`; no orphan mutations | `uwg.commit` parent span | `uwg_commit_receipt_<commit_id>.json` | `validator: uwg_sole_admission_validator` (release-gate) | `NC-UWG-DIRECT-WRITE-001`: any layer mutates L4 without UWG | `direct_l4_write_attempt` | `byte_identical` per fixture | DOC_ONLY |
| `REQ-UWG-CLEARED-COMMIT-001` | UWG MUST accept only cleared `CommitRequest` (cleared by Exit X1J/X3C). Uncleared requests are rejected with `BLOCK_COMMIT`. | 00B.6 | `CommitRequest` | `UWGCommitReceipt` or `UWGRejection` | receipt carries `clearance_proof_id`; rejection carries reason | `uwg.commit` span; `uwg.reject` span | `uwg_commit_receipt.json` or `uwg_rejection.json` | `validator: uwg_clearance_validator` (release-gate) | `NC-UWG-UNCLEARED-001`: bypass clearance proof | `uwg_uncleared_commit_attempt` | `byte_identical` | DOC_ONLY |
| `REQ-UWG-LOCK-RECEIPT-AUDIT-001` | Every accepted commit MUST produce: write lock acquisition, atomic commit, receipt with `commit_id`, audit-ledger append, rollback metadata. | 00B.6 | `CommitRequest` | `UWGCommitReceipt` | receipt fields complete; audit ledger append confirmed | `uwg.commit` span events: `lock_acquired`, `commit_atomic`, `receipt_emit`, `audit_appended` | `uwg_commit_receipt.json`, `audit_ledger.append` | `validator: uwg_commit_completeness_validator` (release-gate) | `NC-UWG-PARTIAL-COMMIT-001`: receipt without audit append | `audit_append_missing` | `byte_identical` | DOC_ONLY |
| `REQ-UWG-VALIDATE-PRE-COMMIT-001` | UWG MUST run validation against `policy_hash`, `blueprint_hash`, `registry_digest_set`, capability_token, and the staged diff before commit. Validation failure produces `UWGRejection`. | 00B.6 | `CommitRequest` | validation result | validation receipt links commit_id | `uwg.validate` span | `uwg_validation_receipt.json` | `validator: uwg_validation_validator` (release-gate) | `NC-UWG-VALIDATE-SKIP-001`: commit without validation | `uwg_validation_skipped` | `byte_identical` | DOC_ONLY |
| `REQ-L4-DURABLE-STATE-001` | L4 MUST be the sole durable system-of-record for: policy/blueprint/registry state, memory and learning promotions, retrieval surface, cache, replay snapshots, audit ledger. Other layers hold ephemeral copies only. | 00B.1..00B.5 | post-UWG state | (read projections) | every read of canonical state resolves through L4 | `l4.read_projection` span | `l4_read_projection_<domain>.json` | `validator: l4_canonical_read_validator` (CI) | `NC-L4-SHADOW-WRITE-001`: a layer keeps a divergent shadow copy as canonical | `l4_shadow_canonical_violation` | `byte_identical` | DOC_ONLY |
| `REQ-L4-POLICY-BLUEPRINT-MIGRATION-001` | Policy/blueprint migrations MUST be additive and versioned; in-flight runs use the `policy_hash`/`blueprint_hash` bound at run start. | 00B.9 | migration plan | new versions | migration receipt links old/new hashes | `l4.migration` span | `l4_policy_blueprint_migration.json` | `validator: l4_migration_validator` (release-gate) | `NC-L4-MIGRATION-MID-RUN-001`: in-flight run sees new policy_hash | `policy_hash_drift_mid_run` | `byte_identical` | DOC_ONLY |
| `REQ-L4-READ-PROJECTION-001` | L4 read projections MUST present a deterministic snapshot tied to the run's `policy_hash` and `blueprint_hash`. | 00B.7 | read request | projection | each projection carries `snapshot_id`, `policy_hash`, `blueprint_hash` | `l4.read_projection` span | `l4_read_projection.json` | `validator: l4_read_projection_validator` (release-gate) | `NC-L4-PROJECTION-DRIFT-001`: projection emits stale snapshot for current run | `l4_projection_snapshot_drift` | `byte_identical` | DOC_ONLY |
| `REQ-L4-REPLAY-SNAPSHOT-001` | The replay snapshot manifest MUST be reproducible for any sealed run from the audit ledger and policy/blueprint state. | 00B.5 | run id | replay manifest | manifest links `run_id`, snapshot ids, policy_hash, blueprint_hash | `l4.replay_manifest` span | `replay_snapshot_manifest.json` | `validator: l4_replay_snapshot_validator` (release-gate) | `NC-L4-REPLAY-MISMATCH-001`: replay manifest disagrees with audit ledger | `replay_manifest_audit_mismatch` | `byte_identical` | DOC_ONLY |
| `REQ-L4-AUDIT-LEDGER-CHAIN-001` | The audit ledger MUST be hash-chained; every commit append carries `prev_chain_hash` and `chain_hash`. Chain breaks are FAIL. | 00B.5 | commit events | audit ledger | every entry has `prev_chain_hash`+`chain_hash` | `l4.audit_append` span | `audit_ledger_append.json` | `validator: l4_audit_chain_validator` (release-gate) | `NC-L4-CHAIN-FORGE-001`: chain hash forged | `audit_chain_forgery` | `byte_identical` | DOC_ONLY |
| `REQ-UWG-OBSERVABILITY-001` | UWG MUST emit observability and anti-bypass signals on every admission attempt (accepted or rejected). | 00B.8 | admission attempts | observability stream | every attempt logged with `commit_id` or `reject_id` | `uwg.observability` span | `uwg_observability.json` | `validator: uwg_observability_validator` (release-gate) | `NC-UWG-DARK-ATTEMPT-001`: write attempt not logged | `uwg_dark_admission` | `byte_identical` | DOC_ONLY |
| `REQ-UWG-CONTEXT-INVARIANT-001` | UWG MUST preserve a durable-write context invariant: identical inputs produce identical commit_id and receipt content_hash for accepted commits. | 00B.7a | commit set | (durability) | replay produces identical receipt content_hash | `uwg.context_invariant` span | `uwg_context_invariant_receipt.json` | `validator: uwg_context_invariant_validator` (release-gate) | `NC-UWG-CTX-DRIFT-001`: identical inputs produce different content_hash | `uwg_context_drift` | `byte_identical` | DOC_ONLY |
| `REQ-UWG-STATE-AUDIT-REPLAY-CONSISTENCY-001` | Cross-store consistency: state, audit ledger, and replay snapshot MUST agree for every committed run. | 00B.8a | committed run | (cross-check) | three-way digest agreement | `uwg.state_audit_replay_check` span | `uwg_state_audit_replay_consistency.json` | `validator: uwg_state_audit_replay_consistency_validator` (release-gate) | `NC-UWG-3WAY-DRIFT-001`: state stored but audit ledger missing entry | `state_audit_replay_inconsistency` | `byte_identical` | DOC_ONLY |

5. RUNTIME EVIDENCE CONTRACT
------------------------------------------------------------------------------------------------------------------------
Every UWG commit receipt MUST carry: `commit_id`, `request_id`, `run_id`, `trace_id`, `span_id`, `policy_hash`, `blueprint_hash`, `registry_digest_set`, `clearance_proof_id`, `staged_diff_hash`, `prev_chain_hash`, `chain_hash`, `content_hash`, `replay_key`, `validator_receipt_id`.

Every L4 projection / snapshot / audit append MUST carry: `req_id`, `domain`, `snapshot_id`, `policy_hash`, `blueprint_hash`, `chain_hash`, `replay_key`.

6. OTEL SPAN CONTRACT
------------------------------------------------------------------------------------------------------------------------
Required spans:
- `uwg.commit` (parent), with events `lock_acquired`, `commit_atomic`, `receipt_emit`, `audit_appended`
- `uwg.reject` for rejected commits
- `uwg.validate`
- `uwg.observability`
- `uwg.context_invariant`
- `uwg.state_audit_replay_check`
- `l4.read_projection`, `l4.replay_manifest`, `l4.audit_append`, `l4.migration`

Required attributes: `req_id`, `policy_hash`, `blueprint_hash`, `replay_key`. For UWG: `commit_id` or `reject_id`. For L4: `domain`, `snapshot_id`, `chain_hash`.

7. VALIDATOR CONTRACT
------------------------------------------------------------------------------------------------------------------------
- `uwg_sole_admission_validator` (release-gate)
- `uwg_clearance_validator` (release-gate)
- `uwg_commit_completeness_validator` (release-gate)
- `uwg_validation_validator` (release-gate)
- `uwg_observability_validator` (release-gate)
- `uwg_context_invariant_validator` (release-gate)
- `uwg_state_audit_replay_consistency_validator` (release-gate)
- `l4_canonical_read_validator` (CI)
- `l4_migration_validator` (release-gate)
- `l4_read_projection_validator` (release-gate)
- `l4_replay_snapshot_validator` (release-gate)
- `l4_audit_chain_validator` (release-gate)

8. NEGATIVE CONTROL CONTRACT
------------------------------------------------------------------------------------------------------------------------
Every `NC-UWG-*` and `NC-L4-*` listed in §4 has a target REQ_ID, tamper kind, expected validator, and `Expected Fail Reason` matching the row. Two cross-pack invariants:
- Any `NC-*-DIRECT-WRITE-*` from upstream packs (e.g. `NC-L2-DIRECT-L4-WRITE-*`, `NC-EXIT-DIRECT-WRITE-*`, `NC-L6-DIRECT-WRITE-*`) MUST trip `REQ-UWG-SOLE-DURABLE-WRITE-001`.
- A successful commit's audit append MUST be inseparable from the receipt; receipt-without-append is `audit_append_missing`.

9. REPLAY CONTRACT
------------------------------------------------------------------------------------------------------------------------
Every UWG commit receipt and L4 projection MUST replay byte-identical for the same `(domain, policy_hash, blueprint_hash, registry_digest_set, input)`. Allowed nondeterminism: only `commit_id` (uuid4) for receipts and `snapshot_id` for projections; receipt `content_hash` MUST match.

10. RELEASE GATE CONTRACT
------------------------------------------------------------------------------------------------------------------------
A 00B row's `Release Gate` is `PASS` only when:
- UWG is the sole admission path (no orphan mutations)
- Every commit has receipt + audit append + validation receipt
- Every L4 projection carries the run's policy_hash/blueprint_hash
- All cross-store consistency checks pass

11. NO-OVERLAP LOCK
------------------------------------------------------------------------------------------------------------------------
**This file owns**: L4 durable state and UWG sole admission.

**Related files own**: per-domain detail in `00B.1`..`00B.9` and `00B.6_UWG_Durable_Write_Gateway.md`.

**Forbidden duplicated ownership**: 00B MUST NOT make runtime gate decisions (00C) or final-response decisions (05). 00C/05 MUST NOT redefine UWG admission rules. 00A MUST NOT issue durable writes.

**Forbidden output vocabulary**: `ALLOW_FINISH`, `DENY`, `REROUTE`, `ESCALATE_HITL`, `SAFE_FALLBACK`, `route_changed`, `workflow_expanded`, `evidence_contract_issued`, `prompt_envelope_constructed`, `learning_promoted`, `policy_certified`. The token `durable_write_committed` is allowed only inside a `UWGCommitReceipt`.

12. CHILD FILE MAP
------------------------------------------------------------------------------------------------------------------------
- `00B.1_L4_Policy_Blueprint_and_Registry_State.md` — `REQ-L4-POLICY-*`, `REQ-L4-BLUEPRINT-*`, `REQ-L4-REGISTRY-*`
- `00B.2_L4_Memory_and_Learning_Promotion_State.md` — `REQ-L4-MEMORY-*`, `REQ-L4-LEARNING-*`
- `00B.3_L4_Retrieval_Surface_State.md` — `REQ-L4-RETRIEVAL-SURFACE-*`
- `00B.4_L4_Cache_State.md` — `REQ-L4-CACHE-*`
- `00B.5_L4_Replay_Snapshot_and_Audit_Ledger.md` — `REQ-L4-REPLAY-*`, `REQ-L4-AUDIT-*`
- `00B.6_UWG_Durable_Write_Gateway.md` — `REQ-UWG-*`
- `00B.7_L4_Read_Surface_Refresh_and_Projection.md` — `REQ-L4-PROJECTION-*`
- `00B.7a_L4_UWG_Durable_Write_Context_Invariant.md` — `REQ-UWG-CONTEXT-*`
- `00B.8_L4_UWG_Observability_Tests_and_Anti_Bypass.md` — `REQ-UWG-OBSERVABILITY-*`
- `00B.8a_L4_UWG_State_Audit_Replay_Consistency_Tests.md` — `REQ-UWG-STATE-AUDIT-REPLAY-*`
- `00B.9_L4_Blueprint_Policy_Version_Migration.md` — `REQ-L4-MIGRATION-*`

13. ACCEPTANCE CRITERIA
------------------------------------------------------------------------------------------------------------------------
- Every parent invariant row in §4 has all 13 cells filled.
- The UWG sole-admission rule is binding and validated.
- Every L4 store has a child file with its own atomic table (deferred — see deferred scope).
- The audit-chain rule is fail-closed.
- The cross-store consistency rule is fail-closed.
- Forbidden output vocabulary in §11 reproduces the global ban list.

END OF 00B — L4 STATE ARCHIVE AND UWG PARENT
========================================================================================================================
