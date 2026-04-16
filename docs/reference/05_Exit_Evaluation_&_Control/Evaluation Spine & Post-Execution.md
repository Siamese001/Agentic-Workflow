=================================================================================================================
             POST-EXECUTION ARCHITECTURE: LIVE CONTROL, OBSERVABILITY, & META-LEARNING
=================================================================================================================

 [ FUTURE RUNS ONLY ]                              [ U0 / INGRESS ]
        ▲                                                 │
        │ [ BUS U: EVOLUTION UPDATES ]                    ▼
        │ • Prompts / Weights / Configs      ┌──────────────────┐       ┌────────────────────────┐
        └────────────────────────────────────┤   L1 REASONING   │◄─────►│ L0 / L3 TOOL & MEMORY  │
                                             └────────┬─────────┘       └────────────────────────┘
                                             ▲        │        ▲                    │
                                     (Deny)  │        │        │                    │
                                             │        ▼        │                    │
                                             │ ┌──────┴────────┴──────────────────┐ │
                                             │ │ L2 SEALED OUTPUT                 │ │
                                             │ │ • ExecTrace & StateDiff          │ │
                                             │ └──────┬───────────────────────────┘ │
=============================================│========│=============================│==========================
 [ LIVE RUNTIME BOUNDARY ] (Current Run)     │        │                             │
=============================================│========│=============================│==========================
                                             │        ▼                             │
                                     ┌───────┴────────┴─────────────────────────────┴──────┐
                                     │ A. LIVE EXIT CONTROL GATE                           │◄──┐(Escalate
                                     │ • Env integrity    • Schema validation              │   │ Return)
                                     │ • Sandbox isol.    • Mutation authorization         │   │
                                     │ • Policy pass/fail • Replay env completeness        │   │
                                     └─┬─────────────┬──────────────┬─────────────┬────────┘   │
                                       │             │              │             │            │
                              [ALLOW]  │      [DENY] │   [ESCALATE] │    [COMMIT] │            │
                                       ▼             │              ▼             │            │
                             ┌───────────────────┐   │    ┌───────────────────┐   │            │
                             │ RESPONSE / OUTCOME│   │    │ HITL              ├───┘            │
                             └───────────────────┘   │    │ • Human Review    │                │
                                                     │    └───────────────────┘                │
                                                     │                                         │
                                                     └─────────────────────────────────────────┼──(To L1
                                                                                               │   / L0)
                                                                                               │
===============================================================================================│=========
 [ SHADOW EVALUATION BOUNDARY ] (Night Watch / Observer)                                       │
===============================================================================================│=========
      ┌────────────────────────────────────────────────────────────────────────────────────────│┐
      │ L6 OBSERVABILITY (Reads L2 Sealed Output & Gate Dispositions)                          ││
      │ • Reads sealed outputs     • Normalizes evidence     • Seals async eval packet         ││
      └─────────┬───────────────────────────────────────────────────────────────┬──────────────│┘
                │                                                               │              │
     ┌──────────┼──────────┐                                                    │              │
     ▼          ▼          ▼                                                    ▼              │
┌────────────────┐ ┌────────────────┐ ┌────────────────┐                ┌────────────────┐     │
│B. OUTCOME EVALS│ │C. TRAJECT EVALS│ │D. G-GATE REGRES│                │F. HUMAN CALIB. │     │
│• Task complet. │ │• Tool sel/order│ │• Exact match   │◄──────────────►│(Calibrates     │     │
│• Groundedness  │ │• Arg correct.  │ │• Schema/state  │                │ B, C, and D)   │     │
│• Citation supp.│ │• Retry thrash  │ │• Traject in/any│                │• SME adjudicate│     │
│• Abstain corr. │ │• Budget discipl│ │• API drift     │                │• Spot checks   │     │
│• Escalation cor│ │• Policy compl. │ │• Rubric grader │                │• Grader calib. │     │
│• Answer relev. │ └───────┬────────┘ └───────┬────────┘                └────────┬───────┘     │
└───────┬────────┘         │                  │                                  │             │
        │                  └────────┬─────────┘                                  │             │
        └────────────────┐          │                                            │             │
                         ▼          ▼                                            │             │
                    ┌─────────────────────────────┐                              │             │
                    │ E. SIGNAL AGGREGATOR        │                              │             │
                    │ • Score bundle • Decis tags │                              │             │
                    │ • Drift flags  • Conf / Var │                              │             │
                    │ • Sever. class • Base/DS tag│                              │             │
                    └──────┬───────────────┬──────┘                              │             │
                           │               │                                     │             │
            ┌──────────────┘               └──────────────┐                      │             │
            ▼                                             ▼                      │             │
┌──────────────────────┐                      ┌──────────────────────┐           │             │
│ BUS P: PREF / GRADES │                      │ BUS T: TELEM / TRACE │           │             │
│ • Qualitative Metrics│                      │ • Quant/Exact Metrics│           │             │
└──────────┬───────────┘                      └──────────┬───────────┘           │             │
           │                                             │                       │             │
===========│=============================================│=======================│=============│=========
 [ SYSTEM LEARNING BOUNDARY ] (Night Shift / Archivists) │                       │             │
===========│=============================================│=======================│=============│=========
           ▼                                             ▼                       ▼             │
┌────────────────────────────────────────────────────────────────────────────────┴──┐          │
│ G. SYSTEM LEARNING PIPELINE                                                       │          │
│ 1. Case Compilation       (Ingests BUS P & T, bundles trails/complaints)          │          │
│ 2. Incident Investigation (Root Cause Analysis / heatmaps / triage)               │          │
│ 3. Rule Drafting          (Proposes updates to config, memory, policy)            │          │
│ 4. Approval Gauntlet      (Automated tests & SME sign-off)                        │          │
└───────────────────────────────────────┬───────────────────────────────────────────┘          │
                                        │                                                      │
                                        │[Approved Learning Commit]                            │[Live Authorized
                                        │                                                      │ Commit]
                                        ▼                                                      ▼
                                      ┌──────────────────────────────────────────────────────────┐
                                      │ UWG MASTER CLERK (The Sole Write Clerk)                  │
                                      │ • Canonical Write Gateway                                │
                                      └────────────────────────────┬─────────────────────────────┘
                                                                   │
                                                                   ▼
                                      ┌──────────────────────────────────────────────────────────┐
                                      │ L4 ARCHIVE                                               │
                                      │ • Durable Ledger                                         │
                                      └────────────────────────────┬─────────────────────────────┘
                                                                   │
                                                                   ▼
                                                      [ BUS U: EVOLUTION UPDATES ]
                                                      (Overnight rollout to L1 Next Run Env)
=================================================================================================================