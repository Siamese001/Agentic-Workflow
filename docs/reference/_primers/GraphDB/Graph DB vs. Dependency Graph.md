========================================================================================================================
MECE ALIGNMENT FULL OVERWRITE HEADER
Canonical folder: 03A_C0_Context_Engine
Canonical file: Graph DB vs. Dependency Graph.md
Overwrite mode: full-file, no-overlap, implementation-grade, source-refreshed
Source refreshed from: GraphDB/Graph DB vs. Dependency Graph.md
Owner summary: C0 retrieval/evidence engine. Owns retrieval planning, fetch/hydration, graph expansion, shaping, verification, evidence contract, and weak-support refinement. Does not answer or assemble prompts.

GLOBAL NO-OVERLAP LAW
- 00A L5 owns governance certification evidence, not live runtime dispositions and not durable write admission.
- 00B L4/UWG owns durable system-of-record state and durable write admission, not planning, routing, retrieval, execution, Exit disposition, or L6 learning mechanics.
- 00C Runtime Gates owns G01-G29 current-run GateVerdict law, not final Exit X3 aggregation and not L5 certification evidence.
- 00X owns traceability and no-loss mapping only.
- 01 Intake owns request envelope validation and identity/session/tenant baseline only.
- 02 L1 owns advisory interpretation and planning only.
- 03 L0/L3 owns deterministic route selection and optional workflow orchestration only.
- C0 owns retrieval/evidence contracts only.
- PA owns prompt packet construction only.
- 04 L2 owns bounded execution and sealing only.
- 05 Exit owns current-run checkout aggregation and exactly one X3 disposition only.
- 06 L6 owns completed-run evaluation, RCA, and future-run learning proposals only.
- 99 owns proof harnesses only; it does not own runtime behavior.

REFERENCE POINTERS
- Cross-cutting governance/certification evidence: 00A_L5_Governance_Safety/
- Durable state and Universal Write Gateway: 00B_L4_State_Archive_and_UWG/
- Current-run reusable gate mesh: 00C_Runtime_Gates_Current_Run_Mesh/
- Traceability and zero-loss proof: 00X_Requirements_Traceability_and_No_Loss_Map.md
- End-to-end runtime proof harness: 99_End_to_End_Runtime_Proof_and_Acceptance/
========================================================================================================================

+=======================================================================================================+
|                            VECTOR DB vs. GRAPH DB: PARADIGM COMPARISON                                |
+=======================================================================================================+
| MEMORY HOOK:                                                                                          |
| VECTOR DB: Spread outward ("Looks like", "Close to", "Similar to", "Related by meaning")              |
| GRAPH DB:  Walk the chain ("Links to", "Depends on", "Owned by", "Connected by path")                 |
+=======================================================================================================+

      VECTOR DB: "What is similar?"                       GRAPH DB: "What is connected?"
      ---------------------------------                   ---------------------------------

+-------------------------------------------------------------------------------------------------------+
| SCENARIO 1: THE CORE EXAMPLE & QUERYING "ALICE"                                                       |
|                                                                                                       |
| "Who is related to Alice by similarity?"                "What exactly does Alice connect to?"         |
+-------------------------------------------------------------------------------------------------------+

               ┌───────────┐                                         ┌───────────┐
               │   Alice   │                                         │   Alice   │
               └─────┬─────┘                                         └─────┬─────┘
                     │                                                     │
                     │ (embed / compare)                                   │ [manages] (follow edge)
                     v                                                     v
           ╔══════════════════╗                                      ┌───────────┐
           ║ Similarity Space ║                                      │  Team 1   │
           ╚══════════════════╝                                      └─────┬─────┘
              ↙      ↓      ↘                                              │
             ↙       ↓       ↘                                             │ [owns]
            v        v        v                                            v
      ┌───────┐  ┌───────┐  ┌───────┐                                ┌───────────┐
      │ Mgr B │  │ Team 1│  │ Svc X │                                │ Service X │
      └───────┘  └───────┘  └───────┘                                └─────┬─────┘
          \          |          /                                          │
           \         |         /                                           │ [reads]
            \        |        /                                            v
             v       v       v                                       ┌───────────┐
           ┌───────────────────┐                                     │ Database 9│
           │ Nearest Neighbors │                                     └───────────┘
           └───────────────────┘

+-------------------------------------------------------------------------------------------------------+
| SCENARIO 2: USE CASE FLOW                                                                             |
|                                                                                                       |
| "What other services are like Service X?"               "Who owns the thing reading Database 9?"      |
| (Find similar things)                                   (Trace exact structure)                       |
+-------------------------------------------------------------------------------------------------------+

               ┌───────────┐                                         ┌───────────┐
               │ Service X │                                         │ Database 9│
               └─────┬─────┘                                         └─────┬─────┘
                     │                                                     │
                     │ (embed / compare)                                   │ (reverse traversal)
                     v                                                     v
           ╔══════════════════╗                                      ┌───────────┐
           ║ Similarity Space ║                                      │ Service X │
           ╚══════════════════╝                                      └─────┬─────┘
              ↙      ↓      ↘                                              │
             v       v       v                                             │ (follow dependents)
      ┌───────┐  ┌───────┐  ┌────────┐                                     v
      │ Svc Y │  │ API Z │  │Billing │                               ┌───────────┐
      └───────┘  └───────┘  └────────┘                               │  Team 1   │
                                                                     └─────┬─────┘
                                                                           │
                                                                           v
                                                                     ┌───────────┐
                                                                     │   Alice   │
                                                                     └───────────┘

+-------------------------------------------------------------------------------------------------------+
| SCENARIO 3: BLAST RADIUS (FAILURE IMPACT)                                                             |
|                                                                                                       |
| "What other databases are similar?"                     "Who is impacted if this DB fails?"           |
+-------------------------------------------------------------------------------------------------------+

               ┌───────────┐                                         ┌───────────┐
               │ Database 9│                                         │ Database 9│
               └─────┬─────┘                                         └─────┬─────┘
                     │                                                     │
                     │ (compare to similar)                                │ (follow dependents up)
                     v                                                     v
               ┌───────────┐                                         ┌───────────┐
               │ DB 4      │                                         │ Service X │
               │ Warehouse │                                         └─────┬─────┘
               │ Store 3   │                                               │
               └───────────┘                                               v
                                                                     ┌───────────┐
                                                                     │  Team 1   │
                                                                     └─────┬─────┘
                                                                           │
                                                                           v
                                                                     ┌───────────┐
                                                                     │   Alice   │
                                                                     └───────────┘
+=======================================================================================================+