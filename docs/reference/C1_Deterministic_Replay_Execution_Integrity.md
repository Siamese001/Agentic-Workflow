==============================================================================================================================
[C1] 🔁 DETERMINISTIC REPLAY & EXECUTION INTEGRITY
     Library Persona: 🛠️ Stack Staff + ⏱️ Master Clock + 🧾 Receipts Clerk
     Spans: 🧭 L0 injects -> 🧵 L3 propagates -> 🛡️ L5 enforces -> 🛠️ L2 executes -> 👁️ L6 verifies
==============================================================================================================================

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 🔒 INVARIANTS (replay law - same packet, same snapshot, same answer)                                                          │
│ D1. Same input + same envelope + same policy_hash + same read snapshot -> same replay digest.                                 │
│ D2. No wall clock, raw entropy, uuid4, live network drift, or mixed-state reads inside the guarded run.                      │
│ D3. Writes remain proposal-only until UWG commits.                                                                            │
│ D4. Policy mismatch invalidates replay certification even if outputs look similar.                                            │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

                                              ✅ CERTIFIED PACKET
                                                         │
                                                         │
                                               [ bind replay metadata ]
                                                         │
                                                         ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 📦 BUILD REPLAY ENVELOPE (Stack Staff)                                                                                        │
│ - Generates replay_key bound to policy_hash, blueprint_hash, and run_id                                                       │
│ - Binds capability_token and snapshot identifiers for downstream state tracking                                               │
└────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────┘
                                                         │
                                                         │
                                                 [ signal propagation ]
                                                         │
                                                         ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 🚩 REPLAY MODE PROPAGATION (Master Clock)                                                                                     │
│ - Injects freeze signal across layers: L0 -> L3 -> L5 -> L2                                                                   │
│ - Halts wall-clock updates so every component observes the same runtime snapshot                                               │
└────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────┘
                                                         │
                                                         │
                                                [ system state freeze ]
                                                         │
                                                         ▼
==============================================================================================================================
                                     🔁 THE DETERMINISM SURFACE (Receipts Clerk)
==============================================================================================================================

      ⏱️ TIME               🎲 ENTROPY            🪪 IDENTITY           🌐 NETWORK           📚 STATE READS       🖋️ WRITES
      ───────────           ───────────           ───────────           ───────────          ───────────          ───────────
           │                     │                     │                     │                    │                    │
           ▼                     ▼                     ▼                     ▼                    ▼                    ▼
     Run Clock Only        Seeded Only           Stable IDs Only       Photocopy Calls      One Snapshot Only     Proposal Only
           │                     │                     │                     │                    │                    │
           │                     │                     │                     └──────────┬─────────┘                    │
           │                     │                     │                                │                              │
           └─────────────────────┴─────────────────────┼────────────────────────────────┴─────────── [ real ink ] ─────► 🏛️ UWG
                                                       │
                                               [ enforced boundary ]
                                                       │
                                                       ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 🛡️ REPLAY GUARD (Interception Layer)                                                                                          │
│ - Wraps every tool and model invocation to prevent non-deterministic leaks                                                     │
│ - Intercepts: wall clock, raw random, uuid4, live network drift, mixed-state reads, unstable provider metadata               │
└────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────┘
                                                         │
                                                         │
                                                  [ guard active ]
                                                         │
                                                         ▼
┌────────────────────────────────────────────────────────┴───────────────────────────────────────────────────────────────────┐
│ 🧰 EXECUTE UNDER GUARD (L2 Execution)                                                                                         │
│ - Isolated processing: Input -> Intercepted Tool/Model -> Output                                                              │
│ - Every invocation inherits the same replay envelope, policy_hash, and snapshot manifest                                      │
└───────────────────────┬────────────────────────────────────────────────────────────────────────────────────────────────────┘
                        │
             ┌──────────┴──────────┐
             │                     │
      [ verification ]      [ ❌ violation ] ───► [ HIDDEN TIME / RAW ENTROPY / MIXED READS / POLICY MISMATCH ]
             │                     │                          │
             │                     │                          ▼
             ▼                     ▼                 [ STOP + CLASSIFY CAUSE ]
             │            [ NON-REPLAYABLE ]                  │
             │                     │                          ▼
             │                     └──────────────────► [ FAULT TELEMETRY ]
             │
      [ valid trace ]
             │
             ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 🧾 RECEIPTS CLERK                                                                                                              │
│ - Logs request/response pairs, timing offsets, tool traces, state diffs, and replay-relevant metadata                        │
│ - Seals evidence needed for L6 replay verification and exit review                                                             │
└────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────┘
                                                         │
                                                         │
                                                  [ log collection ]
                                                         │
                                                         ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 🔒 SEAL FINAL DETERMINISM DIGEST (L6)                                                                                         │
│ - Produces exactly one stable proof: W<n>-DETERMINISM-DIGEST                                                                  │
│ - Invariant: same input + same envelope + same clock + same reads -> same digest                                              │
└────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────┘
                                                         │
                                                         │
                                                  [ proof handoff ]
                                                         │
             ┌─────────────────────────┬─────────────────┴───────────────┬─────────────────────────┐
             │                         │                                 │                         │
             ▼                         ▼                                 ▼                         ▼
        [ 🚪 EXIT ]          [ 👁️ L6 REPLAY CHECK ]           [ 🏛️ L4 TRACE SHELF ]      [ INVALID IF POLICY MISMATCH ]
