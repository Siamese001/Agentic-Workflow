======================================================================================================================================================
[9] 💾 L4 (STORE) & 🚪 UWG (WRITE) - STATE, REGISTRY, SNAPSHOTS, & MUTATION AUTHORITY
[ SCOPE RULES ] L4 ONLY STORES/SERVES; L6 PROPOSES FUTURE-RUNS; UWG HOLDS EXCLUSIVE WRITE LOCK; HOT CACHES NON-AUTHORITATIVE.
======================================================================================================================================================

                                 [ APPROVED FUTURE-RUN UPDATE ] --(Policy Promotion via Learning Path)--> [ BUS U ]
                                                                                                              |
  ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────▼────────────────────────────────────┐
  │ 1. POLICY SNAPSHOT / HOT-SWAP (The Catalog Update Protocol)                                                                                    │
  │ [Shadow Stage] Preps config -> [Merkle / policy_hash] Computes root -> [Pointer Swap] Atomic flip -> [Session Drain] Old runs complete         │
  └──────────────────────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────┘
                                                                                         │ [ Active policy_hash / Allowed capability check ]
                                                                                         ▼
  ┌─────────────────────────┐                                              ┌───────────────────────────────────────────────┐
  │ L2 EXECUTION CORE       │- - - - -(Direct Write Bypass PROHIBITED)- - >│ [ 🛑 BLOCKED ] (Gravity Breach)               │
  │ (Untrusted / Sandboxed) │                                              └───────────────────────────────────────────────┘
  └────────────┬────────────┘                                                                      
               │ [ Raw Write Intent Payload ]                                                      
               ▼                                                                                   
  ┌───────────────────────────────────────────────┐                                                
  │ 2. UWG INGRESS GATE (The Front Desk)          │--(Mismatch)--> [ ORPHAN / RECONCILE ]          
  │ > Verify signature                            │                                                
  │ > Verify active policy_hash                   │                                                
  └────────────────────┬──────────────────────────┘                                                
                       │ [ Validated Mutation Intent ]                                             
                       ▼                                                                           
  ┌───────────────────────────────────────────────┐                                                
  │ 3. VALIDATION GATE (Perimeter Check)          │                                                
  │ > Enforce active policy reference             │                                                
  │ > Check allowed capability set                │                                                
  │ > Scope / RBAC / Blast Radius                 │                                                
  └────────────────────┬──────────────────────────┘                                                
                       │ [ Scoped Execution Trace ]                                                
                       ▼                                                                           
  ┌───────────────────────────────────────────────┐                                                
  │ 4. MUTATION RECORD ASSEMBLY (Exact Diffing)   │                                                
  │ > Generate Before/After Diff                  │                                                
  │ > Compute Replay Key                          │                                                
  │ > Apply HMAC Seal                             │                                                
  │ > Package ExecutionTrace Artifact             │                                                
  └────────────────────┬──────────────────────────┘                                                
                       │ [ Signed ExecutionTrace Artifact ]                                        
                       ▼                                                                           
  ┌───────────────────────────────────────────────────┐                                                
  │ 5. AUTHORITATIVE COMMIT (UWG -> L4 Master Ledger) │                                                
  │ > Claim sole write lock                           │
  │ > Execute durable commit                          │
  │ > Hash chain append                               │
  │ > Rollback / heal on fail                         │
  └────────────────────┬──────────────────────────────┘
                       │ [ Durable Commit Ack ]
                       ▼
  ┌────────────────────────────────────────────────────────┐
  │ 6. L4 READ SURFACE MATERIALIZATION (Views / Index Swap)│
  │ > Generate Materialized Read Views                     │
  │ > Retrieval surface refresh                            │
  │ > Versioned alias swap                                 │
  │ > Telemetry/audit sync                                 │
  └────────────────────┬───────────────────────────────────┘
                       │ [ Materialized Read Surface / Append-Only Audit Stream ]
                       ▼
+====================================================================================================================================================+
| 7. OUTBOUND READ BRIDGES (How L4 anchors read-only system state)                                                                                   |
|====================================================================================================================================================|
| > C0 / L1: Context builds from L4 materialized read surfaces. No L1 access to storage internals.                                                   |
| > L0: Receives active policy_hash (to stamp ingress tickets) & definitive allowed capability registry for triage.                                  |
| > L5: Pulls raw constitution boundaries, forbidden token lists, and active L4 policy references for exact bounding.                                |
| > L3: Reads DAG workflow rules and branching thresholds. L3 holds ZERO mutation authority.                                                         |
| > L6: Ingests append-only execution trace audits and materialized telemetry. Proposes future rules, NO direct runtime mutation.                    |
| > HOT MEM: Ephemeral sync (Session Cache TTL, Pub/Sub Hint Bus, Vector Scratchpad). Strictly NON-AUTHORITATIVE.                                    |
+====================================================================================================================================================+