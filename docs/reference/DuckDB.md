====================================================================================================
                    DUCKDB IN YOUR AGENTIC MODEL - HIGH-SIGNAL FIT
====================================================================================================

                         CURRENT RUN PATH                                  ANALYTICS / LEARNING PATH
                         ────────────────                                  ─────────────────────────

 U0        L1          L0          C0/PA          L3          L2          EXIT
Ask  ──► Plan ──► Route ──► Retrieve/Pack ──► Orchestrate ──► Execute ──► Control
           │          │          │              │             │            │
           │          │          │              │             │            │
           ▼          ▼          ▼              ▼             ▼            ▼
        plan logs   route logs  evidence logs   step logs     tool logs   verdicts
           │          │          │              │             │            │
           └──────────┴──────────┴──────────────┴─────────────┴────────────┘
                                      │
                                      │ runtime exhaust only
                                      ▼
                            ┌──────────────────────┐
                            │  C2 / L6 TELEMETRY   │
                            │  Trace + Eval Shelf  │
                            └──────────┬───────────┘
                                       │
                                       │ export / mirror
                                       ▼
                            ┌──────────────────────┐
                            │       DUCKDB         │
                            │  local analytics DB  │
                            │  SQL over traces,    │
                            │  evals, ADG, logs    │
                            └──────────┬───────────┘
                                       │
                                       │ aggregate / diagnose
                                       ▼
                            ┌──────────────────────┐
                            │ L6 SHADOW LEARNING   │
                            │ RCA / trends / drift │
                            │ promotion candidates │
                            └──────────┬───────────┘
                                       │ approved only
                                       ▼
                            ┌──────────────────────┐
                            │  UWG -> L4 COMMIT    │
                            │  future-run updates  │
                            └──────────────────────┘


====================================================================================================
WHAT DUCKDB IS IN YOUR MODEL
====================================================================================================

┌────────────────────────────┬─────────────────────────────────────────────────────────────────────┐
│ Layer / Plane              │ DuckDB Role                                                         │
├────────────────────────────┼─────────────────────────────────────────────────────────────────────┤
│ C2 Observability           │ SQL workbench over traces, spans, route events, latency, failures    │
│ L6 Shadow Evaluation       │ Batch analysis for eval outcomes, drift, retry thrash, RCA signals   │
│ ADG Analysis               │ Fast local joins over nodes/edges/violations exports                 │
│ Meta-learning Prep         │ Evidence aggregator before promotion candidates go to UWG            │
└────────────────────────────┴─────────────────────────────────────────────────────────────────────┘


====================================================================================================
WHAT DUCKDB IS NOT
====================================================================================================

┌────────────────────────────┬─────────────────────────────────────────────────────────────────────┐
│ Not This                   │ Why                                                                 │
├────────────────────────────┼─────────────────────────────────────────────────────────────────────┤
│ L4 canonical memory        │ L4 remains source of truth; DuckDB is analytical mirror/read surface  │
│ UWG write path             │ DuckDB must not become a side-door durable mutation channel           │
│ C0 vector retrieval store  │ Use Chroma/FAISS/etc. for 🟦 query_vec vs 🟧 fact_vec similarity       │
│ Graph DB replacement       │ Use graph/ADG for lineage traversal; DuckDB can analyze exports       │
│ Redis replacement          │ Redis stays hot cache/locks/short-lived runtime state                 │
│ L2 execution authority     │ L2 executes bounded tasks; DuckDB only supports analysis              │
└────────────────────────────┴─────────────────────────────────────────────────────────────────────┘


====================================================================================================
BEST FIT SUMMARY
====================================================================================================

                Runtime agents do the work.
                C2/L6 records the exhaust.
                DuckDB analyzes the exhaust.
                L6 proposes improvements.
                UWG commits approved future-run changes.

====================================================================================================