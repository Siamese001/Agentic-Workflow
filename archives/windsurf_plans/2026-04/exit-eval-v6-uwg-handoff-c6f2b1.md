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
