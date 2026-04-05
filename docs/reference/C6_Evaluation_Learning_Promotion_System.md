==============================================================================================================================
[C6] 🧪 EVALUATION & LEARNING PROMOTION SYSTEM
     Library Persona: ✅ Checkout Reviewer + 🌙 Night Board + 🖋️ Master Clerk
     Operational Span: 🚪 current-run exit -> 👁️ shadow eval -> 🌙 learning pipeline -> 🏛️ UWG/L4
==============================================================================================================================

                                              [ PHASE 1: CURRENT RUN EXIT ]
                                              ─────────────────────────────
                                                   🛠️ L2 SEALED OUTPUT
                                                            │
                                                            │ [ work folder ]
                                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ ✅ LIVE EXIT REVIEW (Checkout Reviewer)                                                                                    │
│ - Validates environment integrity, schema compliance, and mutation policy                                  │
│ - Checks replay completeness and validates "real ink" write requests                                                       │
└────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────┘
                                                         │
          ┌──────────────────────────┬───────────────────┴───────────────────┬──────────────────────────┐
          │                          │                                       │                          │
          │ [ pass ]                 │ [ fail ]                              │ [ review ]               │ [ commit ]
          ▼                          ▼                                       ▼                          ▼
      [ ALLOW ]                  [ DENY ]                               [ ESCALATE ]               [ COMMIT REQ ]
          │                          │                                       │                          │
          └──────────────────────────┴───────────────────┬───────────────────┴──────────────────────────┘
                                                         │
                                                         │ [ 🔒 sealed result + verdict ]
                                                         ▼
                                              [ PHASE 2: SHADOW EVAL ]
                                              ────────────────────────
                                                ┌──────────────────┐
                                                │ 👁️ L6 SHADOW EVAL │ ──► [ Dependency: Read-Only Access ]
                                                └────────┬─────────┘
                                                         │
┌────────────────────────────────────────────────────────┴───────────────────────────────────────────────────────────────────┐
│ L6 ANALYSIS CORE                                                                                                           │
│ - B Outcome Evals: Task completion, groundedness, citation support, abstain correctness                         │
│ - C Trajectory Evals: Tool selection order, argument correctness, retry thrash, policy compliance                          │
│ - D Gate Regressions: Drift detection (Exact match, Schema, API, and Grader drift)                                         │
│ - F Human Calibration: SME spot checks to calibrate automated grading signals                                               │
└────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────┘
                                                         │
                                                         │ [ raw scores ]
                                                         ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ E SIGNAL AGGREGATOR                                                                                                        │
│ - Compiles unified score bundle, severity classification, and drift flags                                                  │
└────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────┘
                                                         │
                                    ┌────────────────────┴────────────────────┐
                                    │                                         │
                         [ 🚌 BUS P: PREFS ]                       [ 🚌 BUS T: TELEM ]
                                    │                                         │
                                    └────────────────────┬────────────────────┘
                                                         │
                                                         │ [ aggregate signals ]
                                                         ▼
                                     [ PHASE 3: NIGHT SHIFT / FUTURE VISITS ONLY ]
                                     ─────────────────────────────────────────────
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 1-3 📦 ARCHIVE FREEZE                                                                                                      │
│ - Captures patron trails, freezes active rules, and seals the master archive payload                                   │
└────────────────────────────────────────────────────────┬─────────────► [ Rule: Future Visits Only ]
                                                         │
                                                         │ [ frozen state ]
                                                         ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 4 🗂️ CASE FILE COMPILATION                                                                                                 │
│ - Generates unique incident IDs and attaches correlated logs and context                                                   │
└────────────────────────────────────────────────────────┬─────────────► [ Dependency: Telemetry correlation ]
                                                         │
                                                         │ [ case file ]
                                                         ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 5 🔎 INVESTIGATION                                                                                                         │
│ - Maps failure flow and classifies root cause (RCA)                                                                        │
└───────────────────────┬────────────────────────────────┴─────────────► [ no stable pattern ] ──► [ HOLD / WATCH ]
                        │
                        │ [ RCA packet ]
                        ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 6 📝 RULE DRAFTING                                                                                                         │
│ - Drafts prompt/config updates, policy tweaks, and new memory controls                                                     │
└────────────────────────────────────────────────────────┬─────────────► [ Dependency: Rollback plan ]
                                                         │
                                                         │ [ proposed rules ]
                                                         ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 7 🧪 COMMANDANT GAUNTLET                                                                                                   │
│ - Executes shadow replay, regression tests, and final SME sign-off                                                     │
└───────────────────────┬────────────────────────────────┴─────────────► [ fail ] ──► [ REJECT ]
                        │
                        │ [ pass: approved packet ]
                        ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 8 🧭 KNOWLEDGE EXTRACTION                                                                                                  │
│ - Routes updates to rubrics, desk rules, catalog refs, or reason priors                                                    │
└────────────────────────────────────────────────────────┬─────────────► [ Dependency: Target classification ]
                                                         │
                                                         │ [ promotion packet ]
                                                         ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 9 🖋️ MASTER LEDGER COMMIT                                                                                                  │
│ - Sole ink gate: executes edition rollout and ledger update                                                            │
└────────────────────────────────────────────────────────┬─────────────► [ Rule: Clerk Gate Only ]
                                                         │
                                                         │ [ commit complete ]
                                                         ▼
                                              ┌───────────────────────┐
                                              │ 🌅 OVERNIGHT UPDATES  │ ──► [ Rubric / Desk / Catalog ]
                                              └───────────────────────┘

==============================================================================================================================
[!] INVARIANT: Learning signals are recorded for later only; they do not mutate the completed run live.
[!] ARCHITECTURE: Observe -> Seal Evidence -> Learning Loop -> Approved Promotion updates the manual for tomorrow.
==============================================================================================================================