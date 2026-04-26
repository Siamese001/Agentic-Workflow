========================================================================================================================
MECE ALIGNMENT FULL OVERWRITE HEADER
Canonical folder: C0_Context_Engine
Canonical file: GraphDB and ADG Use Cases.md
Overwrite mode: full-file, no-overlap, implementation-grade, source-refreshed
Source refreshed from: GraphDB/GraphDB and ADG Use Cases.md
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

┌────────────────────────────────────────────────────────────────────────────────────────────┐
│                    LAYER 1: CANONICAL ADG IN SQLITE (LEDGER OF TRUTH)                      │
│                                                                                            │
│ Purpose: deterministic artifact, CI truth, canonical counts, canonical relations,          │
│          baseline comparison, rule enforcement inputs.                                     │
│                                                                                            │
│ Core Mental Model: SQLite tells you what exists. SQLite decides.                           │
└────────────────────────────────────────────────────────────────────────────────────────────┘

        [ source code ]   [ configs ]   [ repo metadata ]   [ commit / run metadata ]
               │               │               │                        │
               └───────────────┴───────────────┴────────────────────────┘
                                               │
                                               ▼
                              ┌────────────────────────────────┐
                              │  CANONICAL ADG SUBSTRATE       │
                              │                                │
                              │  • SNAPSHOT METADATA           │
                              │    - snapshot_id               │
                              │    - commit_sha                │
                              │    - schema_version            │
                              │    - digests / lineage         │
                              │                                │
                              │  • PROVENANCE / COVERAGE       │
                              │    - what was scanned          │
                              │    - where facts came from     │
                              │                                │
                              │  • NODES                       │
                              │    - modules, symbols, tools,  │
                              │      providers, gateways, etc. │
                              │                                │
                              │  • EDGES                       │
                              │    - imports, calls, routes,   │
                              │      reads, writes, guards     │
                              └───────────────┬────────────────┘
                                              │
                    policy rules evaluate     │
                    canonical payload         │
                                              ▼
                              ┌────────────────────────────────┐
                              │  DERIVED CI / POLICY SURFACES  │
                              │                                │
                              │  • VIOLATIONS                  │
                              │    - which node/edge/path      │
                              │      broke which rule          │
                              │                                │
                              │  • REPORTS                     │
                              │    - deterministic rollups     │
                              │    - scorecards / summaries    │
                              │                                │
                              │  • RATCHETS / BASELINES        │
                              │    - current vs prior snapshot │
                              │    - block / ratchet / watch   │
                              └───────────────┬────────────────┘
                                              │
                                              │ canonical truth stays here
                                              │
══════════════════════════════════════════════╪═══════════════════════════════════════════════
                                              │
                                              │ deterministic projection
                                              ▼
┌────────────────────────────────────────────────────────────────────────────────────────────┐
│               LAYER 2: GRAPH DB PROJECTION (NON-SOVEREIGN TRAVERSAL SURFACE)               │
│                                                                                            │
│ Purpose: Path traversal, neighborhood extraction, blast-radius analysis,                   │
│          topology diffing, exact path explanation.                                         │
│                                                                                            │
│ Core Mental Model: GraphDB tells you how it connects. GraphDB explains.                    │
└─────────────────┬────────────────────────────────────────────────────────┬─────────────────┘
                  │                                                        │
         ┌────────▼────────┐                                      ┌────────▼────────┐
         │ PROJECTION FEED │                                      │ EXCLUSION ZONE  │
         │                 │                                      │ (Does NOT Own)  │
         │ ├─ Nodes        │       ┌───────────────────┐          │                 │
         │ ├─ Edges        │──────▶│ THE GRAPH ENGINE  │          │  × Source Truth │
         │ ├─ Snapshots    │──────▶│                   │          │  × Policy Truth │
         │ ├─ Provenance   │       │  (Node)─[Edge]─▶  │          │  × Ratchets     │
         │   (selected)    │       └─────────┬─────────┘          └─────────────────┘
         └─────────────────┘                 │
                                             │   makes these questions materially
                                             │   easier, faster, and more explainable
                                             ▼
         ┌─────────────────────────────────────────────────────────────────────────┐
         │                         GRAPH-NATIVE CAPABILITIES                       │
         │                                                                         │
         │ ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐        │
         │ │ EXACT PATHING    │  │ BLAST RADIUS     │  │ TOPOLOGY DIFF    │        │
         │ │ ├─ Violating Path│  │ ├─ k-hop limits  │  │ ├─ Snapshot A vs │        │
         │ │ └─ 1st Illegal   │  │ └─ Gateway Impact│  │ └─ Snapshot B    │        │
         │ │    Hop           │  │                  │  │                  │        │
         │ └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘        │
         │          │                     │                     │                  │
         │          │            ┌────────▼─────────┐           │                  │
         │          └───────────▶│ SUBGRAPH ENGINE  ◀───────────┘                  │
         │                       │ ├─ By Layer/Agent│                              │
         │                       │ └─ Centrality &  │                              │
         │                       │    Hotspots      │                              │
         │                       └──────────────────┘                              │
         └─────────────────────────────┬───────────────────────────────────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │ ANALYST / AGENT / REVIEWER│
                         └───────────────────────────┘