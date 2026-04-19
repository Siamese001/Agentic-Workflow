┌──────────────────────────────────┬──────────────────────────────────┬──────────────────────────────────┬──────────────────────────────────┬──────────────────────────────────┐
│ STAGE 1                          │ STAGE 2                          │ STAGE 3                          │ STAGE 4                          │ STAGE 5                          │
│ STATIC ADG (LIBRARY RULES)       │ OTel + STATE (AUDIT TRAIL)       │ ZERO-LOSS LINKING (INDEXING)     │ RUNTIME OVERLAY (THE RECEIPT)    │ HARD GOVERNANCE GATE             │
├──────────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┤
│ FOCUS                            │ FOCUS                            │ FOCUS                            │ FOCUS                            │ FOCUS                            │
│                                  │                                  │                                  │                                  │                                  │
│ Full AST Dependency Graph        │ OpenTelemetry traces +           │ Zero-loss overwrite ETL          │ Per-run runtime nodes, edges,    │ Strict Static ADG vs Runtime     │
│ snapshots = structural blueprint │ captured state                   │ Relational index + Full JSON     │ and instantiated graphs          │ Graph diff                       │
│ of the system                    │                                  │ payloads                         │                                  │ L1 to L5 compliance checks       │
├──────────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┤
│ CAPABILITIES                     │ CAPABILITIES                     │ CAPABILITIES                     │ CAPABILITIES                     │ CAPABILITIES                     │
│                                  │                                  │                                  │                                  │                                  │
│ U0->C0->L1->L5->L6 static flows  │ Timing, spans, and parent        │ Trace/span -> exact AST node/    │ Runtime read/write graph         │ Undocumented runtime edges       │
│ mapped                           │ relationships                    │ symbol mapping                   │ Runtime policy graph             │ blocked via Middleware Halt      │
│ Nodes, edges, and violations     │ State mutations captured         │ Component -> symbol mapping      │ Runtime artifact graph           │ Dead static edges flagged        │
│ defined strictly in AST          │ Reasoning payloads captured      │ Layer & policy tagging           │ Runtime commit graph             │ Cross-layer violations rejected  │
│ Symbol-level dependencies        │ Agent deterministic proof        │ Lossless payload retention       │                                  │ Write-path enforcement locked    │
│ extracted directly from code     │                                  │                                  │                                  │                                  │
├──────────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┤
│ ANSWERS                          │ ANSWERS                          │ ANSWERS                          │ ANSWERS                          │ PROVES & ENFORCES                │
│                                  │                                  │                                  │                                  │                                  │
│ "What exists?"                   │ "What ran & why?"                │ "What static ADG entity maps     │ "What exact graph instantiated   │ "Did L1 attempt to bypass L5?"   │
│ "What is the L1-L5 path?"        │ "What was the exact state?"      │ to the lossless payload?"        │ in run R123?"                    │ "Did the run violate the         │
│ "What violations exist in the    │ "What reasoning drove the        │ "Which layer executed?"          │ "Who read what?"                 │ architecture?"                   │
│ structural AST graph?"           │ agent's decision?"               │                                  │ "Who wrote what?"                │                                  │
├──────────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┤
│ LIMITATION                       │ LIMITATION                       │ REQUIREMENT                      │ LIMITATION                       │ RESULT                           │
│                                  │                                  │                                  │                                  │                                  │
│ No runtime truth                 │ Trace tree is not yet a          │ Must not strip granular JSON     │ Per-run graph exists but lacks   │ Runtime ADG is a first-class     │
│ Only architecture truth          │ graph authority                  │ context during relational        │ authority until compared to      │ authority and deployment         │
│                                  │                                  │ mapping                          │ static ADG                       │ blocker                          │
├──────────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┤
│ STORAGE                          │ STORAGE                          │ STORAGE                          │ STORAGE                          │ STORAGE & ENFORCEMENT            │
│                                  │                                  │                                  │                                  │                                  │
│ SQLite full ADG snapshots        │ OTel backend (Jaeger/Tempo)      │ SQLite mapping tables            │ Graph Materialization Views /    │ SQLite + views + strict policy   │
│                                  │ + logs + spans + state JSON      │ (pointers + full JSON)           │ In-Memory Graph Construction     │ diff + metrics rollups           │
│                                  │                                  │                                  │ built on top of Stage 3 SQLite   │ L5 Compliance Validator /        │
│                                  │                                  │                                  │                                  │ Active Middleware Interceptor    │
├──────────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┤
│ LIBRARIAN ANALOGY                │ LIBRARIAN ANALOGY                │ LIBRARIAN ANALOGY                │ LIBRARIAN ANALOGY                │ LIBRARIAN ANALOGY                │
│                                  │                                  │                                  │                                  │                                  │
│ The Library rules (extracted     │ The camera records L1 walking    │ The catalog links the tape to    │ A precise map is drawn of L1's   │ The Compliance Guard (L5)        │
│ from the books via AST) dictate  │ and captures their exact         │ the exact Library floorplan      │ exact steps during this session. │ verifies L1 never touched a      │
│ that L1 cannot bypass L5.        │ clipboard (state & reasoning).   │ without erasing the tape.        │                                  │ restricted door and halts the    │
│                                  │                                  │                                  │                                  │ action immediately if they did.  │
└──────────────────────────────────┴──────────────────────────────────┴──────────────────────────────────┴──────────────────────────────────┴──────────────────────────────────┘