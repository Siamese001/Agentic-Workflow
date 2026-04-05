==============================================================================================================================
[C4] 🏛️ STATE SOVEREIGNTY & UNIVERSAL WRITE GOVERNANCE
     Library Persona: 🖋️ Master Clerk + 🏛️ Archivist + 🔐 Ledger Keeper
     Operational Span: All runtime and night-shift proposals must end here for real ink.
==============================================================================================================================

    [ RUNTIME & OFF-HOUR PROPOSALS ]
    🧠 L1 plan   🧭 L0 route   🛠️ L2 work   👥 HITL review   👁️ L6 learn   🌙 Night Board
      │             │             │              │               │               │
      └─────────────┴──────┬──────┴──────────────┴───────────────┴───────────────┘
                           │
                           │ [ proposed mutation ]
                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 📖 READ / ANSWER ONLY?                                                                                                     │
│ - Final check to determine if the visit requires a state change or just a response.                                        │
└──────────────────────────┬─────────────────────────────────────────────────────────────────────────────────────────────────┘
                           │
             ┌─────────────┴─────────────┐
      [ YES ]│                           │ [ NO ]
             ▼                           ▼
       [ NO WRITE ]              [ PROPOSED CHANGE ]
             │                           │
             │ [ answer only ]           │ [ ink requested ]
             │                           ▼
             │           ┌────────────────────────────────────────────────────────────────┐
             │           │ 🖋️ UWG ONLY (The Master Clerk)                                 │
             │           │ - Only one clerk exists with the master pen.                  │
             │           │ - Strictly serialized write queue to prevent race conditions. │
             │           └───────────────┬────────────────────────────────────────────────┘
             │                           │
             │                           │ [ verify authority ]
             │                           ▼
             │           ┌────────────────────────────────────────────────────────────────┐
             │           │ 🔍 VERIFY THE BOSS (Ledger Keeper)                             │
             │           │ - Validates signature, compliance_hash, and policy_hash.      │
             │           │ - Checks capability tokens for write authorization.           │
             │           └───────────────┬────────────────────────────────────────────────┘
             │                           │
             │                           │ [ check scope ]
             │                           ▼
             │           ┌────────────────────────────────────────────────────────────────┐
             │           │ 📚 CHECK CATALOG RULES (The Archivist)                         │
             │           │ - Verifies RBAC, blast radius, and structure constraints.      │
             │           │ - Performs before-after diff validation of the knowledge base. │
             │           └───────────────┬────────────────────────────────────────────────┘
             │                           │
             │                           │ [ lock substrate ]
             │                           ▼
             │           ┌────────────────────────────────────────────────────────────────┐
             │           │ 🔐 CLAIM WRITE LOCK                                            │
             │           │ - Prevents ghost writes and overlapping mutations.             │
             │           │ - Claims exclusive write-access to the knowledge substrate.    │
             │           └───────────────┬────────────────────────────────────────────────┘
             │                           │
             │                           │ [ execute ink ]
             │                           ▼
             │           ┌────────────────────────────────────────────────────────────────┐
             │           │ 🏛️ COMMIT + CHAIN APPEND                                       │
             │           │ - Durable ledger write and hash-chain audit log update.        │
             │           │ - Syncs the new record to the permanent L4 archive.            │
             │           └───────────────┬────────────────────────────────────────────────┘
             │                           │
             │                           │ [ materialization ]
             │                           ▼
             │           ┌────────────────────────────────────────────────────────────────┐
             │           │ 🔄 REFRESH READ SURFACES                                       │
             │           │ - Executes alias swap and clears retrieval caches.             │
             │           │ - Ensures the very next request sees the updated state.        │
             │           └───────────────┬────────────────────────────────────────────────┘
             │                           │
             ▼                           ▼
    [ RUNTIME ANSWER ]          [ FUTURE READS NOW SEE IT ]

==============================================================================================================================
[!] HARD LAW OF THE LIBRARY: No direct L2 write | No direct HITL write | No direct L6 write | No live bypass.
[!] Every real mutation must pass through the 🖋️ UWG to reach the 🏛️ L4 Knowledge Substrate.
==============================================================================================================================