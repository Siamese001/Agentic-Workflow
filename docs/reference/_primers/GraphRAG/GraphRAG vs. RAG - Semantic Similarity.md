========================================================================================================================
MECE ALIGNMENT FULL OVERWRITE HEADER
Canonical folder: 03A_C0_Context_Engine
Canonical file: GraphRAG vs. RAG - Semantic Similarity.md
Overwrite mode: full-file, no-overlap, implementation-grade, source-refreshed
Source refreshed from: GraphRAG/GraphRAG vs. RAG - Semantic Similarity.md
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

==========================================================================================
🕸️ FROM STANDARD RAG TO GRAPHRAG: 🟦 INTENT vs 🟧 CHUNKS vs 🔗 NEIGHBORS
==========================================================================================

PART 1: 📖 STANDARD RAG
------------------------------------------------------------------------------------------
🗣️ User Question: "Can L0 write directly to durable state?" -> 🧠 embed -> 🟦 QUERY VECTOR Q

🗄️ Stored Knowledge Base (Ingestion Time) -> 🧠 embed -> 🟧 CHUNK VECTORS (O1, O2, O3, O4)
[C1] "L0 routes but does not write" 
[C2] "UWG is the only durable writer"
[C3] "L6 observes but does not mutate"
[C4] "Exit control validates action disposition"

⚖️ Similarity Search: Compare 🟦 Q vs 🟧 O1-O4
✅ Q vs O1 = 0.94  |  ✅ Q vs O2 = 0.92  |  ☑️ Q vs O3 = 0.74  |  ❌ Q vs O4 = 0.70

📋 STANDARD RAG CONTEXT PACKET:
[ C1 ] "L0 routes but does not write"
[ C2 ] "UWG is the only durable writer"
[ C3 ] "L6 observes but does not mutate"
🎯 Result: LLM sees semantically similar chunks with weak/no explicit structural linkage.

PART 2: 🕸️ GRAPHRAG ADDS GRAPH STRUCTURE
------------------------------------------------------------------------------------------
🔗 The same chunks are now linked into a graph.

[🟧 C1] ──mentions──> [🟣 Entity: L0] ──belongs_to──> [🟢 Layer: Routing]
   └──related_to──> [🔴 Rule: No durable write from L0]

[🟧 C2] ──mentions──> [🟣 Entity: UWG] ──controls──> [🛣️ Durable Write Path]
   └──related_to──> [🔴 Rule: UWG-only write]

[🟧 C4] ──mentions──> [🟣 Entity: Exit Control] ──precedes──> [🛣️ Durable Write Path]

⚡ RETRIEVAL IN TWO STEPS:
STEP A: 🔍 Semantic Retrieval -> 🟦 Q finds top 🟧 chunks: C1 & C2.
STEP B: 🌐 Graph Expansion -> Traverse from C1 & C2 to neighbors (entities, rules, paths).

📋 GRAPHRAG CONTEXT PACKET:
📍 SEMANTIC ROOTS: 🟧 C1, 🟧 C2
🔗 GRAPH NEIGHBORS: [🟣 L0], [🔴 Rule: No durable write from L0], [🟣 UWG], [🛣️ Durable Write Path], [🟣 Exit Control]
🎯 Result: LLM sees semantic chunks + structural neighborhood + explicit relationships.

PART 3: 👁️ VISUAL COMPARISON
------------------------------------------------------------------------------------------
📖 STANDARD RAG                          🕸️ GRAPHRAG
         🟦 Q                                     🟦 Q
         / | \                                    /   \
        /  |  \                                  /     \
      🟧O1 🟧O2 🟧O3                           🟧O1   🟧O2
                                               | \   / |
Meaning: Retrieve nearest                      |  \ /  |
orange chunks only.                            |   X   |
                                               |  / \  |
                                               v v   v v
                                             🔗N1 N2 N3 N4
                                         Meaning: Retrieve nearest chunks (O), 
                                         then expand through graph structure (N).

PART 4: 🎯 WHY THIS MATTERS
------------------------------------------------------------------------------------------
📖 STANDARD RAG asks: "What text looks similar to my question?"
🕸️ GRAPHRAG asks:     "What text looks similar, AND what connected entities/rules/paths surround it?"

GraphRAG excels when you need:
✅ Exact rules/paths related to a chunk.
✅ Neighboring concepts (even if not semantically identical).
✅ Connected gateways, control points, or downstream nodes.
✅ Explanatory paths (rather than just relevant text).

PART 5: 🤖 IN AGENTIC ARCHITECTURE TERMS
------------------------------------------------------------------------------------------
🗣️ Query: "Why is this path illegal?"
📖 Standard RAG retrieves: Text about L0, UWG, exit control (misses exact relationship structure).
🕸️ GraphRAG retrieves: Text chunks + Graph-linked neighbors (L0 node, UWG node, write path node, first illegal hop, missing choke point, related structural rule, prior snapshot).
🎯 GraphRAG Result: More grounded, more explainable, more path-aware, less dependent on pure text similarity.

PART 6: 🧩 WHAT THE GRAPH NEIGHBORS CAN BE
------------------------------------------------------------------------------------------
Graph neighbors are NOT just entities. They encompass:
🟣 Entities      🔴 Rules         🚪 Gateways     🏢 Providers   📝 Prompts
🧩 Chunks        📸 Snapshots     ⚠️ Violations   🛣️ Paths       ⚙️ Controls   🌐 Communities

[🟧 Chunk] ──mentions──> [🟣 Entity]
           ──supports──> [🔴 Rule]
           ──part_of───> [🌐 Community Summary]
           ──appears_in─>[📸 Snapshot]
           ──near──────> [⚠️ Violation Path]

PART 7: 🔄 END-TO-END STACK
------------------------------------------------------------------------------------------
[📄 Raw Docs] -> ✂️/🧠 -> [🟧 Orange Chunks] -> 🔗 Extract Relations -> [🕸️ Graph Layer]
                                                                            |
[🟦 Blue Query] -> 🔍 Semantic Search (O) -> 🌐 Traversal (N) -> [📋 Context Packet] -> 🤖 LLM Answer

PART 8: 📏 SIMPLE RULE OF THUMB
------------------------------------------------------------------------------------------
❓ "What text is relevant?" ➡️ Use 📖 STANDARD RAG.
❓ "What connected evidence, rule, path, or neighborhood explains this?" ➡️ Use 🕸️ GRAPHRAG.

PART 9: 💡 🟦 / 🟧 / 🔗 SUMMARY
------------------------------------------------------------------------------------------
🟦 BLUE   = Live intent vector from user question
🟧 ORANGE = Stored chunk/fact vectors from ingestion
🔗 GRAPH  = Relationships linking chunks, entities, rules, paths, snapshots

🕸️ GRAPHRAG EQUATION:
(🟦 vs 🟧 Semantic Similarity) ➕ (🟧 ➡️ 🔗 Graph Neighbor Expansion) = Structural Relatedness
==========================================================================================