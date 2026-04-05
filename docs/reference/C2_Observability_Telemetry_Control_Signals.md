==============================================================================================================================
[C2] 👁️ OBSERVABILITY, TELEMETRY & CONTROL SIGNALS
     Library Persona: 🕰️ Master Clock + 🎥 Tape Reviewer + 🔔 Bell Tower Keeper
     Spans: 🛠️ L2 sealed output -> 🚪 Exit gate -> 👁️ L6 verify -> 🏛️ L4/UWG -> 🌙 future runs
==============================================================================================================================

                                              [ THE CRUMB TRAIL ]
   👤 apps ──► 🚪 U0 ──► 🧠 L1 ──► 🧭 L0/L3 ──► 🛠️ L2 ──► 🚪 Exit ──► 👥 HITL ──► 🏛️ UWG
                                                     │
                                                     │ [ logs / traces / state ]
                                                     ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 📖 L6 READ SURFACES (Tape Reviewer)                                                                                        │
│ - Sealed Execution Trace: The literal record of every tool/model interaction and state change                              │
│ - Exit Dispositions: The final check-out status (Allow / Deny / Escalate)                                                  │
│ - L4 Telemetry Shelf: Historical baseline metrics and prior run logs                                                       │
└────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────┘
                                                         │
                                                         │ [ inspection request ]
                                                         ▼
==============================================================================================================================
                                       👁️ L6 VERIFY SPINE (The Bell Tower)
                          does not execute | does not route | generates signals only
==============================================================================================================================

      ⏱️ CLOCK              🔁 DETERMINISM         🚨 ANOMALY             🧾 EVIDENCE SEAL
      ───────────           ───────────           ───────────           ───────────────
           │                     │                     │                     │
           ▼                     ▼                     ▼                     ▼
┌─────────────────────┐ ┌─────────────────────┐ ┌─────────────────────┐ ┌─────────────────────┐
│ 1. TIME AUDIT       │ │ 2. ISOLATION CHECK  │ │ 3. DRIFT DETECTION  │ │ 4. PACKET SEAL      │
│ - Verify stamps     │ │ - Verify seeds      │ │ - Budget usage      │ │ - Normalize metrics │
│ - Order & latency   │ │ - Check isolation   │ │ - Thrash / Spikes   │ │ - Seal exec env     │
│ - Clock drift detect│ │ - Replay strictness │ │ - Unusual patterns  │ │ - Final provenance  │
└──────────┬──────────┘ └──────────┬──────────┘ └──────────┬──────────┘ └──────────┬──────────┘
           │                       │                       │                       │
           │                       │                       │                       │
           └───────────────────────┴──────────┬────────────┴───────────────────────┘
                                              │
                                   [ deviation / anomaly signal ]
                                              │
                    ┌─────────────────────────┴─────────────────────────┐
                    ▼                                                   ▼
┌────────────────────────────────────────┐            ┌────────────────────────────────────────┐
│ 🔔 BUS D / BUS E (Live Control)        │            │ 🚌 BUS T (Trace & Telemetry)           │
│ - Real-time signal: Deny / Re-enter    │            │ - Async data: Metrics / Timing / Drift │
│ - Escalation triggers for HITL         │            │ - Performance & Grounding telemetry    │
└───────────────────┬────────────────────┘            └───────────────────┬────────────────────┘
                    │                                                     │
                    │ [ live signal ]                                     │ [ async payload ]
                    ▼                                                     ▼
             [ 🚪 EXIT GATE ]                         ┌────────────────────────────────────────┐
                                                      │ L6EvidenceBundle                       │
                                                      │ - replay_key & determinism_status      │
                                                      │ - anomaly_flags & audit_traces         │
                                                      │ - normalized_metrics: Recall@K / MRR   │
                                                      │ - citation_precision / support_rate    │
                                                      └───────────────────┬────────────────────┘
                                                                          │
                                                                          │ [ evidence for RCA ]
                                                                          ▼
                                                      [ 🌙 SYSTEM LEARNING / RCA / TUNING ]
                                                                          │
                                                                          │ [ approved promotion ]
                                                                          ▼
                                                       [ 🏛️ UWG -> L4 -> BUS U (Next Run) ]

==============================================================================================================================
[!] LIVE SIDE: Observe -> Detect -> Ring Bell -> Exit Gate decides the current run.
[!] FUTURE SIDE: Observe -> Seal Evidence -> Learning Loop -> Approved Promotion updates the manual for tomorrow.
==============================================================================================================================