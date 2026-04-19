==========================================================================================================================================================================
                                            🗺️ AGENTIC SYSTEM — PROCESS MAP v22.0 (FINAL SVP ARCHITECTURE ALIGNMENT) 🗺️
                          LAYER SOVEREIGNTY: Upward mutation FORBIDDEN · Runtime mutation FORBIDDEN · UWG = ONLY write path
==========================================================================================================================================================================

[ THE 6 COMMUNICATION BUSES (SIGNAL ROUTING & ENFORCEMENT) ]
+--------------------------------------------------------------------------+---------------------------------------------------------------------------------------------+
| 🚦 LIVE EXECUTION & SAFETY INTERCEPTS                                    | 📊 POST-EXECUTION & SYSTEM LEARNING FEEDBACK                                                |
| 🛑 [ BUS C ] CONTROL:    L6 ─→ L0 (Real-time rerouting/throttling)       | 📈 [ BUS T ] TELEMETRY:  L6 ─→ L4 (Read-only observation logs and metrics)                  |
| 🛡️ [ BUS D ] DENY:       L5 ─→ L1 (Safety failure → forced re-entry)     | 🧠 [ BUS P ] PREFERENCE: Eval ─→ ML (DPO signals, grading, human alignment)                 |
| ⚠️ [ BUS E ] ESCALATION: Anomaly ─→ Path D (HITL / Human intervention)   | 💾 [ BUS U ] UPDATES:    ML ─→ UWG (Governed policy commits for future runs)                |
+--------------------------------------------------------------------------+---------------------------------------------------------------------------------------------+
 LIBRARY ANALOGY:
 - BUS C = Circulation Director intercepting a book cart.                  - BUS T = Turnstile counters and observational logs written into the read-only ledger.
 - BUS D = Security Desk denying entry and sending patron back.            - BUS P = The suggestion box: annotated corrections/grades sent to the Board.
 - BUS E = Fire Alarm forcing the Head Librarian to review.                - BUS U = The official printing press: new, approved rulebooks pushed to all desks.

===========================================================================================================================================
[ 🔄 RUNTIME EXECUTION (PIPELINE C) & SYSTEM EVOLUTION (PIPELINE D) ]

[ START ]   [ THINK ]   [ ROUTE / A-E DECIDE ]          [ ORCH ]    [ CHECK ]   [ EXEC ]    [ SCORE ]   [ VERIFY ]  [ STORE ]   [ LEARN ]
┌───────┐   ┌───────┐   ┌───────────────────────────┐   ┌───────┐   ┌───────┐   ┌───────┐   ┌───────┐   ┌───────┐   ┌───────┐   ┌───────┐
│ 🗣️ U0 │──>│ 🤖 L1 │──>│ 🚦 L0 DISPATCHER         │─>│ 🎼 L3 │─│ 🛡️ L5 │──>│ ⚙️ L2 │──>⚖️ Eval│     │ 👁️ L6│──>│ 💾 L4 │──>│ 🧠 ML │
└───────┘   └─▲───▲─┘   ├───────────────────────────┤   └───────┘   └───────┘   └───────┘   └───────┘   └───┬───┘   └───┬───┘   └───┬───┘
              │   │     │ A: 🟥 Exact Cache (End)   │                                                       │           │           │
┌───────┐     │   │     │ B: 🧠 Sem. Cache  (End)   │                                                       ▼           ▼           │
│ 🧰 APPS│─────┘ │     │ C: 📚 Agentic RAG (To C0) │                     (BUS C: CTRL)   (BUS T: TELEM)   │           │           │
└───────┘         │     │ D: 🛠️ Action      (To L3) │                                                       ▼           ▼           │
                  │     │ E: 🔮 LLM Fallback(To L3) │                                                   ┌───────┐   ┌───────┐       │
                  │     └─────────────┬─────────────┘                                                   │🚦ReRt │   │📥 UWG │       │
                  │                   │                                                                 └───────┘   └───┬───┘       │
                  │                   ▼                                                                                 │           │
                  │   ┌───────────────┴───────────────┐                                                                 │           │
                  │   │ 🔍 C0 CONTEXT ASSEMBLY STACK  │                                                (BUS U: UPDATE)  │           │
                  │   ├───────────────────────────────┤                                                                 │           │
                  │   │ • Vector Search               │                                                                 │           │
                  │   │ • BM25 Keyword                │                                                                 │           │
                  │   │ • Graph Expand                │                                                                 │           │
                  │   │ • Re-rank & Filter            │                                                                 │           │
                  │   │ • Build Context payload       │                                                                 │           │
                  │   └───────────────┬───────────────┘                                                                 │           │
                  │                   │                                                                                 │           │
                  └───────────────────┘                                                                                 │           │
                   (Returns context to L1)                                                                              │           │
                                                                                                                        │           │
   [ SYSTEM EVOLUTION LOOP ] <──────────────────────────────────────────────────────────────────────────────────────────┘           │
                 └────────────────────────────── ( SYSTEM LEARNING BUS: T / P / U ) <───────────────────────────────────────────────┘
===========================================================================================================================================

 [ LIFECYCLE NODE LEGEND: THE LIBRARY PERSONAS ]
 🧰 [1] APPS: Domain-specific intent generators (Zero Auth). 🛡️ [5] L5: Security Commandant. Enforces safety & policy.  👁️ [8] L6: Turnstile observer. Emits telemetry.
 🤖 [2] L1:   Research Librarian. Reasons, plans, primes.    ⚙️ [6] L2: Conservation Lab. Blindly executes tools.      💾 [9] L4: Head Archivist. Canonical state & memory.
 🚦 [3] L0:   Dispatcher. Evaluates Dual-Rail, routes.       ⚖️ [7] Eval: Grading Committee. Scores post-execution.    🧠 [10] ML: Meta-Learning Board. Proposes new rules.
 🎼 [4] L3:   Shift Supervisor. Sequences and orchestrates.  [!] UWG: (Nested in L4) Master Clerk. ONLY node allowed to mutate the Canonical Archive.
==========================================================================================================================================================================

==========================================================================================================================================================================
[0] 🏛️ GLOBAL ARCHITECTURE INVARIANTS, LAWS, & MACRO TOPOLOGY
==========================================================================================================================================================================
 [ TERMINOLOGY SSOT ]
 • "Evaluation Spine" = ONLY valid term for post-L2 scoring ("Evaluation" alone is deprecated).
 • "System Outcome Metrics" = Metric set produced by Spine.  |  "U0" = Raw User Intent.  |  "C0" = Context Assembly/RAG.
 • PRE-ROUTING FLOW:  [ 🗣️ U0 ] ─→ [ 🤖 L1 ] ─→ [ 🔍 C0 ] ─→ [ 💾 L4 ]  (Observed by 👁️ L6) ──> Authority begins at L0.

 [ THE 9 GOVERNANCE INVARIANTS ]
 ┌─────────────────────────── AUTHORITY ───────────────────────────┬──────────────────────────── COGNITION & ROUTING ────────────────────────────┐
 │ 1. ⚙️ L2 touches books  (sole execution authority)              │ 4. 🤖 L1 decides what to look for (reasoning authority)                     │
 │ 2. 💾 L4 stores books   (sole state authority)                  │ 5. 🔍 C0 assembles what is looked at (context assembly)                     │
 │ 3. 🚪 UWG writes        (sole mutation authority)               │ 6. 🚦 L0 decides where work goes (routing authority)                        │
 ├────────────────────────── VERIFICATION ─────────────────────────┴─────────────────────────────────────────────────────────────────────────────┤
 │ 7. 🛡️ L5 decides if work is allowed (policy)   |   8. 👁️ L6 verifies what happened (observe only)   |   9. ⚖️ Eval Spine judges outcomes       │
 └───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

 [ THE 4 LAWS OF SYSTEM LEARNING & LAYER GRAVITY ]
 ┌─────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────────────────────────┐
 │ 1. THE CREATOR CANNOT APPROVE:  [ L1/L3 ] ─X─> (Approve)│ ARROW TYPES & LAYER GRAVITY (STRICTLY ENFORCED VISUAL LANGUAGE)                       │
 │                                 [ L5 ] ───✅─> (Approve)│ 🟢 SOLID ARROWS (─→)  = Bus-mediated communication (✅ ALLOWED). Example: [L0] ─→ [L3]  │
 │ 2. THE OBSERVER CANNOT TOUCH:   [ L6 ] ───X──> (Route)  │ 🔴 DASHED ARROWS (-→) = Direct layer bypass (⚠️ VIOLATION). Example: [L0] -→ [L2]       │
 │ 3. THE EXECUTOR CANNOT LEARN:   [ L2 ] ───X──> (Learn)  │                                                                                       │
 │ 4. THE ONLY PERMANENT PEN:      [ UWG ] ──✅─> (Write)  │ [!] Lower layers CANNOT import upward. Dynamic runtime mutation (monkeypatch) FORBIDDEN.│
 ├─────────────────────────────────────────────────────────┴───────────────────────────────────────────────────────────────────────────────────────┤
 │ ⏳ TEMPORALITY: [ TEMPORARY ] L1 reasoning, C0 context, L2 state   ====== NEVER MUTATES =====>   [ PERMANENT ] L4 archive, UWG writes, ML rules │
 └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

==========================================================================================================================================================================
[1] 🧰 APPS (INTENT) — DOMAIN APPS & SHARED TYPE SYSTEM
==========================================================================================================================================================================
 [ SCOPE RULES ]: Domain Apps are ZERO AUTHORITY surfaces. They NEVER walk into restricted archives, NEVER dispatch runners, and NEVER stamp approvals. Strictly segmented.

 ┌───────────────────────────────────────┐    ┌───────────────────────────────────────┐    
 │ 🧰 DOMAIN APPS (apps_*)               │    │ 🧱 SHARED TYPE SYSTEM (apps_shared)   │    
 │ THE INTENT PRODUCERS                  │    │ THE ENFORCEMENT CONTRACT              │    
 ├───────────────────────────────────────┤    ├───────────────────────────────────────┤    
 │ • apps_lic (InMail Campaigns)         │──> │ SCHEMA MUST EMIT:                     │──> (Yields structured payload to L1)
 │ • apps_rg (Resume Generation)         │    │ ├─ {intent_delta}                     │    
 │ • apps_rfp (RFP Response)             │    │ ├─ {tool_requests[]}                  │    
 │ STRUCTURE: /agents, /engines, /tools  │    │ └─ {state_diff_proposal}              │    
 └───────────────────────────────────────┘    └───────────────────────────────────────┘    

==========================================================================================================================================================================
[2] 🤖 L1 (THINK) — COGNITIVE STUDIO
==========================================================================================================================================================================
 [ SCOPE RULES ]: Authority ends here. L1 CANNOT execute tools directly. L1 CANNOT route traffic. L1 proposes the plan.

 ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │ 🤖 L1: THE REASONING ENGINE                                                                                                                                           │
 ├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
 │ • P1: PRIMING: Hydrates context via Knowledge Graph and Semantic Memory.                                                                                              │
 │ • P2: ORCHESTRATION: Drafts Tool Agents needed to fulfill the {intent_delta}.                                                                                         │
 │ • P3: PTC CALIBRATION: Simulates Chain-of-Thought (CoT), calculates complexity.                                                                                       │
 │ • P4: SYNTHESIS: Emits intent, selected tools, and raw_reasoning.                                                                                                     │
 │                                                                                                                                                                       │
 │ [ C0 RAG CALL CLARIFIED ]: L1 calls C0 during reasoning ("What books exist?") to compile the [U0: USER PROMPT]. It then prepares the Dual-Rail payload for L0.        │
 └───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

==========================================================================================================================================================================
[3] 🚦 L0 (ROUTE) — DUAL-RAIL SIGNAL ROUTING BUS & 🔍 C0 RAG MATRIX
==========================================================================================================================================================================
 L0 ROUTING (AUTHORITY NODE) EVALUATES DUAL-RAIL PAYLOAD: { TEXT: raw_query, INTENT: 🔵 intent_vec }. 
 P1: Assign TraceID | P2: Compute PolicyHash | P3: Intent Classify | P4: Deterministic Election | P5: Tool Budget | P6: Profile Enforce | P7: Seal Plan | P8: Dispatch
 ELEVATOR SHAFT: JIT context loading, vertical state synchronization, cross-layer transport.
 [METRIC RULE]: L0 Reads System Outcome Metrics from L6/L4 ONLY. NEVER reads directly from active L2. NEVER mutates current execution in-flight.
           
[RAW_TEXT] ──┬────────────────────────────────┬────────────────────────────────┬────────────────────────────────┬────────────────────────────────┐
[🔵 intent] ──┼────────────────────────────────┼────────────────────────────────┼────────────────────────────────┼────────────────────────────────┤
             ▼ (Text)                         ▼ (🔵intent)                     ▼ (🔵intent vs 🟠fact)           ▼ (Text)                         ▼ (Text)
+============+================================+================================+================================+================================+=======================+
| EXEC TIER  | 🟥 1. EXACT CACHE              | 🧠 2. SEMANTIC CACHE           | 📚 3. AGENTIC RAG (C0)         | 🛠️ 4. AGENTIC ACTION          | 🔮 5. LLM FALLBACK    |
+============+================================+================================+================================+================================+=======================+
| ANALOGY    | Exact text call number         | Compare new 🔵 to old 🔵       | Walk 🔵 to Master Archive      | Escalate to active spec.       | Answer from matrix    |
| EMBED/VEC  | NO Embed / NO Vector           | BGE / Embed Sim (>0.95)        | BGE / Concept Sim (Top-K)      | Bypassed / NO Vector           | Token Embed Matrix    |
| INFRA      | Redis (O(1) Hash)              | GPTCache (Redis backed)        | Vector DB (Master Arch)        | Local Process Heap             | Parametric Memory     |
| CONTROL    | EVAL: Exact Call Num?          | EVAL: Familiar Request?        | EVAL: 🟠 fact in DB?           | EVAL: External Action?         | EVAL: No Ext Matches? |
| FLOW       | ├─ [HIT] ─→ Exec & Ret         | ├─ [HIT] ─→ Exec & Ret         | ├─ [HIT] ─→ Exec & Ret         | ├─ [HIT] ─→ Exec & Ret         | ├─ [HIT] ─→ Exec & Ret|
|            | └─ [MISS]─→ Layer 2 ──>        | └─ [MISS]─→ Layer 3 ──>        | └─ [MISS]─→ Layer 4 ──>        | └─ [MISS]─→ Layer 5 ──>        | └─ [FAIL]─→ Exception |
+============+================================+================================+==================┬=============+================================+=======================+
                                                                                                  │
    ┌─────────────────────────────────────────────────────────────────────────────────────────────┴──────────────────────────────────────────────────────────────────┐
    │ 🔍 C0 INTERNAL RAG PIPELINE (TRIGGERED ONLY IF TIER 1 & 2 CACHE MISS)                                                ┌───────────────────────────────────────┐ │
    │ L4H DEFINITION: Ephemeral Redis Hot Cache. NEVER canonical. NEVER authoritative. Cache miss falls back to L4.        │ C0 RETRIEVAL METRICS (L4/L6)          │ │
    │ C0 HARD RULES: NO MEMORY WRITE | NO ROUTING CONTROL | NO EXECUTION AUTHORITY | C0 cannot influence tool selection.   │ - Precision@K | - Recall@K            │ │
    │                                                                                                                      │ - Completeness | - Answer Support     │ │
    │ - 📈 1. VECTOR SRCH: similarity match (FAISS/ChromaDB) vs Master Archive                                             └───────────────────────────────────────┘ │
    │ - 🔤 2. LEXICAL SRCH: BM25 keyword fallback parallel search                                                                                                     │
    │ - 🧬 3. FUSION/RERANK: ScoreFusion / Reciprocal Rank Fusion (RRF) deduplication                                                                                │
    │ - 🌳 4. CONTEXT BLD: Chunk stitching & multi-hop parent/child expansion                                                                                        │
    │ - 🎯 5. COMPLETENESS: Health & support scoring before yielding payload back to L1                                                                              │
    └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

==========================================================================================================================================================================
[4] 🎼 L3 (ORCH) — EXECUTION PATHS & SEQUENCING
==========================================================================================================================================================================
 [ SCOPE RULES ]: L3 handles sequential handshakes, conflict arbitration, overlapping tools, and DAG resolution. It does NOT execute the tools itself.

+========================================+========================================+========================================+=============================================+
| 📖 PATH A                              | 🛡️ PATH B                              | ⚡ PATH C                              | 👤 PATH D (HUMAN REVIEW FIRST)              |
|----------------------------------------|----------------------------------------|----------------------------------------|---------------------------------------------|
| READ-ONLY RESPONSE                     | POLICY CHECK FIRST                     | EXECUTE SCRIPT DIRECT                  | 1. Generate review artifact                 |
| - No system mutation                   | - Sequential Handshake                 | - Sequential Handshake                 | 2. Freeze execution                         |
| - Logged outcome                       | - Conflict Arbitration                 | - Conflict Arbitration                 | 3. Human decision [APPROVE|MODIFY|REJECT]  |
| - ML consumes outcome                  | - Gate: Hallucination                  | - Eval Result vs DAG                   | 4. Route patch to L5 re-clearance           |
|                                        | - Seed: Strict heal                    | - Route: Complete/L2                   | HARD RULE: Human input is untrusted until L5|
+========================================+========================================+========================================+=============================================+

==========================================================================================================================================================================
[5] 🛡️ L5 (CHECK) — SOVEREIGN CONTROL PLANE & ASSEMBLY
==========================================================================================================================================================================
 [ SCOPE RULES ]: L5 is the Security Commandant. If a rule is not explicitly defined, L5 cannot invent one. CONFIG_WITH_LOGIC detection blocks hostile payloads.

 ┌──────────────────────────────────────────────────┐ ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │ L5 SAFETY & CLASSIFICATION KERNELS               │ │ GOVERNED PAYLOAD ASSEMBLY (ORDER MATTERS)                                                                        │
 ├──────────────────────────────────────────────────┤ ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
 │ • AST-based 19-priority queue.                   │ │ [ 📜 S0 SYSTEM RULES ] ─→ [ 🚧 D0 ENFORCEMENT ] ─→ [ 📚 C0 CONTEXT ] ─→ [ 🗣️ U0 REQUEST ]                     │
 │ • LRU cache for high-speed intercepts.           │ │                                                                                                                  │
 │ • STRUCTURE BLUEPRINT (sovereign_kernel).        │ │ Rules command restrictions → restrictions guard references → references contextualize the request.               │
 │ • is_path_allowed() strictly enforces paths.     │ │ Action: Splits into atomic tasks and permanently blocks hostile vectors before handing off to L2.                │
 └──────────────────────────────────────────────────┘ └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

==========================================================================================================================================================================
[6] ⚙️ L2 (EXEC) — PTC SANDBOX & SOVEREIGN LLM GATEWAY
==========================================================================================================================================================================
 [ SCOPE RULES ]: L2 EXECUTES BLINDLY. L2 HARD CONSTRAINTS: Cannot modify policy (L5) | Cannot modify routing (L0) | Cannot write directly to archive (must use UWG).

+------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| AGENT EXECUTION PROFILE REGISTRY — COMPILE-TIME FROZEN SSOT                                                                                                            |
| - ExecMode.DETERMINISTIC: No LLM calls. ExecMode.LLM_API: Requires SovereignLLMGateway. Unregistered invocation → HARD FAIL. registry_digest() validates.              |
| SOVEREIGN LLM GATEWAY — SOLE LLM EGRESS SEAM                                                                                                                           |
| - Model resolution: symbolic -> concrete. Injection detection. Hash-chained audit log. Replay mode support (ReplayEnvelope). Fail-closed kill-switch.                  |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| L2 EXECUTION LIFECYCLE:  🔒 PRE-COMMIT (Freeze JIT state) ─→ ✅ VALIDATION (Verify signature/budget) ─→ 🛠️ EXECUTION (PTC iso) ─→ 🏥 HEALING/EVAL                     |
+------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

==========================================================================================================================================================================
[7] ⚖️ Eval (SPINE) — POST-L2 EVALUATION
==========================================================================================================================================================================
 [ SCOPE RULES ]: ⚠️ EXECUTES STRICTLY POST-L2. WRITES TO L4. DOES NOT FEED L1 INLINE.
 AUTHORITY: ⚖️ READ-ONLY | NO EXECUTE | NO ROUTE | NO MUTATION | SIGNALS ONLY                                                  ┌───────────────────────────────────────┐
 FLOW: ⚙️ L2 Execute ─→ ⚖️ Eval Spine scores ─→ 👁️ L6 validates/observes ─→ 💾 L4 stores ─→ 🧠 ML ingests later                │ EVALUATION SPINE METRICS (L4/L6)      │
                                                                                                                             │ - Faithfulness | - Groundedness       │
                                                                                                                             │ - Answer Relevancy | - Regression Delta │
                                                                                                                             └───────────────────────────────────────┘
==========================================================================================================================================================================
[8] 👁️ L6 (VERIFY) — OBSERVABILITY & REPLAY
==========================================================================================================================================================================
 [ SCOPE RULES ]: DOES NOT EXECUTE. DOES NOT ROUTE. ONLY OBSERVES, VALIDATES, AND AUDITS.

 ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │ L6: MASTER CLOCK & OBSERVABILITY                                                                                                                                      │
 ├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
 │ • Determinism + replay authority. Manages the Semantic Clock (sole time authority). Timestamps/randomness captured and blocked to ensure exact replayability.         │
 │ • P1: INGESTION: Latency, Error Rates.                                     • P3: BROADCAST: Emits anomaly signals (Triggers BUS E: Escalation if needed).             │
 │ • P2: ANOMALY ENGINE: Detects structural drift.                            • P4: ARCHIVER: Prepares Raw Metrics and Snapshots for L4 storage.                         │
 │                                                                                                                            ┌───────────────────────────────────────┐  │
 │ FINAL DECISION / OUTCOME LOGGING (Monitored by L6)                                                                         │ SYSTEM OUTCOME METRICS (L6/L4)        │  │
 │ - Outcome and state diffs are logged and versioned via ExecutionTrace Audit Envelope.                                      │ - Task Success Rate | - Latency       │  │
 │ - [L1 UPDATE] FINAL ANSWER GENERATED USING ONLY ToolTranscript (Maintains PTC Context Isolation).                          │ - Error Rate        | - Cost          │  │
 │ - [RECON] VERIFY DATA MATCHES REALITY (Detect ghost mutations).                                                            └───────────────────────────────────────┘  │
 └───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

==========================================================================================================================================================================
[9] 💾 L4 (STORE) & 🚪 UWG (WRITE) — STATE, REGISTRY, & UNIVERSAL GATEWAY
==========================================================================================================================================================================
 [ SCOPE RULES ]: L4 DOES NOT DECIDE. L4 DOES NOT EXECUTE. ONLY STORES, SERVES, AND LEARNS. UWG is the ONLY write path.

 ┌─────────────────────────────────────────────────────────┐ ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │ 💾 L4: CANONICAL STATE & REGISTRIES                     │ │ 🚪 UWG: UNIVERSAL WRITE GATEWAY & VIOLATION ENFORCEMENT                                                   │
 ├─────────────────────────────────────────────────────────┤ ├───────────────────────────────────────────────────────────────────────────────────────────────────────────┤
 │ • P1: COGNITIVE REG: Prompts, Calibrations              │ │ • All FS/DB/Vector writes route through single gateway with MutationRecord logging.                       │
 │ • P2: CAPABILITY REG: Tools, Policies                   │ │ • Allowed: artifacts/, docs/reports/, logs/, temp/. Blocked: .exe, .dll, .py, .js, .ts.                 │
 │ • P3: WORKFLOW MEMORY: Pending Steps, DAG               │ │                                                                                                           │
 │ • P4: TELEMETRY LEDGER: Exec Logs, System Outcomes      │ │ [ UWG AUTHORITY CHAIN & GRAVITY MATRIX DEMONSTRATION ]                                                    │
 │                                                         │ │ [ L0/L2/L3/L4/L5/L6 ] ──(Solid ─→ Governed Req)──> [ 🚪 UWG ] ──(Solid ─→ Digest Chain)──> [ 💾 ARCHIVE ] │
 │ [SYNC] L4 updates Shared Team Memory & Activity Ledger  │ │           │                                                                                     ^         │
 │ (Non-blocking state update occurs only after L2 seals). │ │           └- - - - - - - - - - (-→ Dashed: Direct FS/DB Write Bypassing Gateway) - - - - - - - -┘         │
 │                                                         │ │ ⚠️ VIOLATION DETECTED: Direct write bypassing UWG → BLOCKED. Direct dashed line = gravity breach.       │
 └─────────────────────────────────────────────────────────┘ └───────────────────────────────────────────────────────────────────────────────────────────────────────────┘

==========================================================================================================================================================================
[10] 🧠 ML (LEARN) — SYSTEM LEARNING BUS & DETERMINISM PROOF
==========================================================================================================================================================================
 [ SCOPE RULES ]: Executes offline/asynchronously (Pipeline D) for FUTURE-RUNS ONLY. Never mutates live execution.

 ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │ SYSTEM LEARNING LOOP: PERSONA-MAPPED 9-STAGE STATE MACHINE                                                                                                            │
 ├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
 │ • STG 1: AUDIT SNAPSHOT FREEZE   | L4 freezes state based on L6 Clock. No hindsight allowed. The Time Capsule.                                                        │
 │ • STG 2: TELEMETRY COLLECTION    | L4 maps agent actions to breaches via L6 execution tape. The Raw Footage.                                                          │
 │ • STG 3: CONFIGURATION SNAPSHOT  | L4 records active L0/L5 rules and safety thresholds. The Rulebook Check.                                                           │
 │ • STG 4: META-LEARNING SNAPSHOT  | L4 bundles L6 Clock, L0/L5 Rules, and C0 Context into one immutable Sealed Case File.                                              │
 │ • STG 5: ROOT CAUSE ANALYSIS     | L4 generates Bad-Habit Heatmap from L3 orchestration blast radius. The Incident Autopsy.                                           │
 │ • STG 6: PROPOSAL GENERATION     | L1/L3 propose tuning (`proposal_only=True`). NO authority to change live rules.                                                    │
 │ • STG 7: VALIDATION GAUNTLET     | L5 Commandment acts as ultimate filter (APPROVE/REJECT) via Shadow/Replay checks. Oscillation detected -> auto-rejected.           │
 │ • STG 8: PATTERN EXTRACTION      | L4 updates Semantic Vector Store with approved motif. The New Call Number.                                                         │
 │ • STG 9: COMMIT & ACTIVATION     | UWG writes final proven rule into Control Spine. DUAL INJECTION REQUIRED. Single => HARD FAIL. Archivist Receipt.                  |
 ├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
 │ DETERMINISM PROOF STANDARD                                                                                                                                            │
 │ - Digest chain requires: registry_digest, agent_inventory, tool_inventory_hash, meta_learning_config_hash.                                                            │
 │ - Replay strictness: ALL historical mutations must be mathematically reconstructable from the ExecutionTrace Audit Envelope.                                          │
 └───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
==========================================================================================================================================================================