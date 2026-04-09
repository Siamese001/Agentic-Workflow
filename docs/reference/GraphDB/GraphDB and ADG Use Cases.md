┌──────────────────────────────────────────────────────────────────────────────────────┐
│ LAYER 1: CANONICAL ADG IN SQLITE (THE SOURCE OF TRUTH)                               │
│                                                                                      │
│ Purpose: CI truth, deterministic artifact storage, exact counts, rule enforcement.   │
│                                                                                      │
│                              ┌─────────────────┐                                     │
│                              │   PROVENANCE    │ ◀─ (Source code, config files,      │
│                              │                 │     and commit metadata)            │
│                              └────────┬────────┘                                     │
│                                       │ feeds into                                   │
│                                       ▼                                              │
│ ┌─────────────────┐          ┌─────────────────┐          ┌─────────────────┐        │
│ │    COVERAGE     │ scope    │                 │ tracks   │                 │        │
│ │ (Defines what   │─────────▶│    SNAPSHOTS    │◀─────────│    RATCHETS     │        │
│ │  was scanned    │          │                 │          │ (Enforces CI    │        │
│ │  for this run)  │          └────────┬────────┘          │  gates to stop  │        │
│ └─────────────────┘                   │ contains          │  regressions)   │        │
│                                       │                   └────────▲────────┘        │
│                                       │                            │                 │
│ ┌─────────────────────────────────────┼────────────────────────────┼──────────┐      │
│ │ THE GRAPH PAYLOAD                   ▼                            │ enforces │      │
│ │                            ┌─────────────────┐                   │          │      │
│ │                     ┌─────▶│      NODES      │◀─────┐            │          │      │
│ │                     │      │ (Entities like  │      │            │          │      │
│ │                     │      │  DBs, APIs,     │      │            │          │      │
│ │                     │      │  gateways)      │      │            │          │      │
│ │            source / │      └────────┬────────┘      │            │          │      │
│ │              target │               │               │ refers     │          │      │
│ │                     │               ▼               │ to         │          │      │
│ │                     │      ┌─────────────────┐      │            │          │      │
│ │                     └──────│      EDGES      │──────┘            │          │      │
│ │                            │ (Connections /  │                   │          │      │
│ │                            │  permissions)   │                   │          │      │
│ │                            └────────┬────────┘                   │          │      │
│ └─────────────────────────────────────┼────────────────────────────┼──────────┘      │
│                                       │                            │                 │
│                            results in │                            │                 │
│                                       ▼                            │                 │
│                              ┌─────────────────┐                   │                 │
│                              │   VIOLATIONS    │                   │                 │
│                              │ (Rules broken   │                   │                 │
│                              │  by specific    │                   │                 │
│                              │  nodes & edges) │                   │                 │
│                              └────────┬────────┘                   │                 │
│                                       │                            │                 │
│                            aggregated │                            │                 │
│                                  into │                            │                 │
│                                       ▼                            │                 │
│                              ┌─────────────────┐                   │                 │
│                              │     REPORTS     │───────────────────┘                 │
│                              │ (Deterministic  │ evaluated by                        │
│                              │  rollups)       │                                     │
│                              └─────────────────┘                                     │
└───────────────────────────────────────┬──────────────────────────────────────────────┘
                                        │
                                        │
             deterministic projection   │ (extracts only Snapshots, Nodes, and Edges
             from SQLite payload        │  and re-shapes them for traversal)
                                        │
                                        ▼
┌──────────────────────────────────────────────────────────────────────────────────────┐
│ LAYER 2: GRAPH DB PROJECTION (THE TRAVERSAL SURFACE)                                 │
│                                                                                      │
│ Purpose: Path explanation, blast-radius, neighborhood mapping, subgraph extraction.  │
│                                                                                      │
│     ┌────────────────────────────────┐    ┌────────────────────────────────────┐     │
│     │ TOPOLOGY PROJECTION            │    │ GRAPH-NATIVE CAPABILITIES          │     │
│     │                                │    │                                    │     │
│     │  (Node) ──────[Edge]─────▶ (Node)   │  • Find shortest illegal hop       │     │
│     │   │             │           │  │    │  • Extract k-hop neighborhood      │     │
│     │ Label         Typed       Label│    │  • Calculate node centrality       │     │
│     │ Index       Traversal     Index│    │  • Map exact ingress-to-sink path  │     │
│     │                                │    │  • Diff topology between Snapshots │     │
│     └────────────────────────────────┘    └────────────────────────────────────┘     │
└───────────────────────────────────────┬──────────────────────────────────────────────┘
                                        │
                                        │
                                        │ queried interactively by
                                        ▼
                       ┌─────────────────────────────────┐
                       │   ANALYST / AGENT / REVIEWER    │
                       └─────────────────────────────────┘