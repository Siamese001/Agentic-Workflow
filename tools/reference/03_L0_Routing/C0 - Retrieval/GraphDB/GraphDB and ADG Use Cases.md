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