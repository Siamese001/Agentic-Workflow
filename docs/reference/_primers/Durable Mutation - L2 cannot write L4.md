================================================================================
#3 DURABLE MUTATION PATH: L2 CANNOT WRITE L4
================================================================================

L2 EXECUTION
------------

┌──────────────────────────────────────────────────────────────────────────────┐
│ L2 EXECUTE                                                                   │
│                                                                              │
│ Can produce:                                                                 │
│   - output_payload                                                            │
│   - generated_artifacts                                                       │
│   - telemetry_bundle                                                          │
│   - sealed artifact                                                           │
│   - proposed_state_diff                                                       │
│                                                                              │
│ Cannot do:                                                                   │
│   - write L4                                                                  │
│   - update memory                                                             │
│   - promote cache                                                             │
│   - update registry                                                           │
│   - commit policy                                                             │
└──────────────────────────────────────────────────────────────────────────────┘
             │
             │ sealed artifact + inert proposed_state_diff
             ▼

EXIT
----

┌──────────────────────────────────────────────────────────────────────────────┐
│ 05 EXIT                                                                      │
│                                                                              │
│ Checks:                                                                      │
│   X1A-X1J                                                                    │
│   X2 aggregation                                                             │
│   X3 disposition                                                             │
│                                                                              │
│ If durable mutation is requested and cleared:                                │
│   emits COMMIT_REQUEST_TO_UWG                                                │
│                                                                              │
│ Still cannot write L4 directly.                                              │
└──────────────────────────────────────────────────────────────────────────────┘
             │
             │ CommitRequest only if X3C
             ▼

UWG
---

┌──────────────────────────────────────────────────────────────────────────────┐
│ UNIVERSAL WRITE GATEWAY                                                      │
│                                                                              │
│ Validates:                                                                   │
│   - CommitRequest                                                             │
│   - StateDiff                                                                 │
│   - schema                                                                    │
│   - policy                                                                    │
│   - replay                                                                    │
│   - audit                                                                     │
│   - lock                                                                      │
│   - blast radius                                                              │
│   - rollback                                                                  │
│   - read-surface refresh                                                      │
│                                                                              │
│ Then:                                                                        │
│   write lock -> atomic commit -> commit receipt                              │
└──────────────────────────────────────────────────────────────────────────────┘
             │
             ▼

L4
--

┌──────────────────────────────────────────────────────────────────────────────┐
│ L4 DURABLE SYSTEM OF RECORD                                                  │
│                                                                              │
│ Stores durable truth:                                                        │
│   - policy / blueprint / registry records                                    │
│   - memory / learning promotion records                                      │
│   - cache entries                                                            │
│   - retrieval surface manifests                                              │
│   - replay snapshots                                                         │
│   - audit ledger                                                             │
│   - commit receipts                                                          │
└──────────────────────────────────────────────────────────────────────────────┘


HARD LAW:
  L2 proposes.
  Exit clears.
  UWG commits.
  L4 stores.

Anything else is a bypass.