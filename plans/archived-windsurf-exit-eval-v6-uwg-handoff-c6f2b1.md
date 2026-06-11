---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\exit-eval-v6-uwg-handoff-c6f2b1.md'
original_relative_path: 'exit-eval-v6-uwg-handoff-c6f2b1.md'
source_sha256: ad17548cb7c4238cc9f3e3e7a1b1af70d17ed9697048331d8b69a0f6af13cdb8
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-25'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Exit Eval v6 — UWG U1-U5 Handoff

Plan ID: exit-eval-v6-uwg-handoff-c6f2b1
Source spec: `docs/reference/05_Exit_Evaluation_&_Control/05_Live_Runtime_Exit_Control_&_Evaluation_v6.md` §X3C.

## Goal

Implement the UWG sub-flow that consumes an `X3CommitRequestPacket` and produces
a commit outcome. UWG is the **sole** ink path to L4.

## Spec sub-flow (§X3C)

| Step | Spec | Implementation |
|---|---|---|
| U1 VERIFY BOSS | signature, compliance_hash, policy_hash, capability_token, write authority | `verify_boss(packet)` |
| U2 CHECK CATALOG | RBAC, tenant, ACL, region, structure, blast radius | `check_catalog(packet, catalog)` |
| U3 CLAIM WRITE LOCK | serialize commit, prevent ghost writes, freeze conflicts | `claim_write_lock(packet, lock_store)` |
| U4 COMMIT + CHAIN APPEND | durable ledger write, hash-chain append, sync to L4, emit receipt | `commit_and_append(packet, ledger, after_state)` |
| U5 REFRESH READ SURFACES | alias swap, cache invalidation, retrieval refresh | `refresh_read_surfaces(packet, refresher)` |

Outcomes: `COMMIT_ACCEPTED`, `COMMIT_REJECTED`, `COMMIT_HELD`.

## Scope

`agentic_core/L3_orchestration/exit_eval/v6/uwg.py`:

- `UwgOutcome` enum
- `UwgReceipt` dataclass (commit_request_id, outcome, ledger_seq, hash_chain_tip, l4_alias)
- `UwgError` + subclasses (`InvalidSignature`, `WriteLockConflict`, `RbacDenied`)
- 5 sub-flow functions
- `process_commit_request(packet, *, catalog, lock_store, ledger, refresher)` orchestrator

In-memory reference implementations (`InMemoryCatalog`, `InMemoryLockStore`,
`InMemoryLedger`, `NoopReadSurfaceRefresher`) — production swaps these for
real backends (SQLite, Redis, etc.). Out of scope: real backends.
