==============================================================================================================================
[C1] 🔁 DETERMINISTIC REPLAY & EXECUTION INTEGRITY
     Library Persona: 🛠️ Stack Staff + ⏱️ Master Clock + 🧾 Receipts Clerk
     Spans: 🧭 L0 injects -> 🧵 L3 propagates -> 🛡️ L5 enforces -> 🛠️ L2 executes -> 👁️ L6 verifies
==============================================================================================================================

                                              ✅ CERTIFIED PACKET
                                                         │
                                                         │
                                               [ bind replay metadata ]
                                                         │
                                                         ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 📦 BUILD REPLAY ENVELOPE (Stack Staff)                                                                                     │
│ - Generates unique replay_key tied to the active policy_hash                                                               │
│ - Binds the capability_token to the specific run_id for state tracking                                                     │
└────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────┘
                                                         │
                                                         │
                                                 [ signal propagation ]
                                                         │
                                                         ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 🚩 REPLAY MODE PROPAGATION (Master Clock)                                                                                  │
│ - Injects "Freeze" signal across layers: L0 -> L3 -> L5 -> L2                                                              │
│ - Halts wall-clock updates to ensure every internal component sees the same snapshot                                       │
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
│ 🛡️ REPLAY GUARD (Interception Layer)                                                                                       │
│ - Wraps every tool and model invocation to prevent "leaks" of non-deterministic data                                       │
│ - Intercepts: no wall clock, no raw random, no uuid4, no live network calls, no mixed-state reads                          │
└────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────┘
                                                         │
                                                         │
                                                  [ guard active ]
                                                         │
                                                         ▼
┌────────────────────────────────────────────────────────┴───────────────────────────────────────────────────────────────────┐
│ 🧰 EXECUTE UNDER GUARD (L2 Execution)                                                                                      │
│ - Isolated processing: Input -> Intercepted Tool/Model -> Output                                                           │
└───────────────────────┬────────────────────────────────────────────────────────────────────────────────────────────────────┘
                        │
             ┌──────────┴──────────┐
             │                     │
      [ verification ]      [ ❌ violation ] ───► [ HIDDEN TIME / RAW ENTROPY / MIXED READS ]
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
│ Receipts Clerk                                                                                  │
│ - Logs request/response pairs, exact timing offsets, tool traces, and state diffs                                          │
└────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────┘
                                                         │
                                                         │
                                                  [ log collection ]
                                                         │
                                                         ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 🔒 SEAL FINAL DETERMINISM DIGEST (L6)                                                                                      │
│ - Produces exactly one stable proof: W<n>-DETERMINISM-DIGEST                                                               │
│ - Invariant: same input + same envelope + same clock + same reads -> same digest                                           │
└────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────┘
                                                         │
                                                         │
                                                  [ proof handoff ]
                                                         │
             ┌─────────────────────────┬─────────────────┴───────────────┬─────────────────────────┐
             │                         │                                 │                         │
             ▼                         ▼                                 ▼                         ▼
        [ 🚪 EXIT ]          [ 👁️ L6 REPLAY CHECK ]           [ 🏛️ L4 TRACE SHELF ]      [ INVALID IF POLICY MISMATCH ]