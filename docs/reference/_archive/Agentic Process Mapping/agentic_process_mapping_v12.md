=========================================================================================================================================================================================================================
                                       🗺️ AGENTIC SYSTEM — PROCESS MAP v12.0 (FINAL SVP ARCHITECTURE ALIGNMENT) 🗺️
                     LAYER SOVEREIGNTY: Upward mutation FORBIDDEN · Runtime mutation FORBIDDEN · UWG = ONLY write path
=========================================================================================================================================================================================================================
                                                                    BUS NOMENCLATURE & ETYMOLOGY
  [ LEFT BUS: EXECUTION & CONTROL ]                                                                 [ RIGHT BUS: META-LEARNING & TELEMETRY ]
  🛑 [ BUS C ] CONTROL: real-time reroute (L6 → L0)                                                 📊 [ BUS T ] TELEMETRY: read-only signals
  🛡️ [ BUS D ] DENY: safety fail → re-entry (L5 → L1)                                                 🧠 [ BUS P ] PREFERENCE: eval/DPO signals
  ⚠️ [ BUS E ] ESCALATION: drift → Path D                                                           💾 [ BUS U ] UPDATES: governed ML commits

  LIBRARY ANALOGY (BUS LAYER ENHANCED):
  - BUS C = Circulation Director intercepting a book cart mid-transit to fix a routing error.
  - BUS D = Security Desk denying entry and sending a patron back to the reference desk to fix their forms.
  - BUS E = Fire Alarm / Escalation broadcast forcing the human Head Librarian to manually review a strange request.
  - BUS T = Turnstile counters and observational logs written into the library's read-only analytics ledger.
  - BUS P = The suggestion box: annotated corrections, grades, and preference notes sent to the library's Board of Directors.
  - BUS U = The official printing press: new, approved editions of the Staff Handbook pushed to all desks simultaneously.
=========================================================================================================================================================================================================================

[0] 🏛️ LIBRARY SYSTEM LAWS & TEMPORALITY (GLOBAL INVARIANTS)
=========================================================================================================================================================================================================================
PRE-ROUTING FLOW (COGNITION — NO AUTHORITY)

🗣️ U0 → 🤖 L1 → 🔍 C0 → 💾 L4
                 ↓
                👁️ L6 (observe only)

GLOBAL SYSTEM FLOW (CONTROL — AUTHORITY BEGINS AT L0):  [ 🚦 L0 ] ─────→ [ 🎼 L3 ] ─────→ [ 🛡️ L5 ] ─────→ [ ⚙️ L2 ] ─────→ [ ⚖️ EVALUATION SPINE ] ─────→ [ 👁️ L6 ] ─────→ [ 💾 L4 ]
=========================================================================================================================================================================================================================
TERMINOLOGY SSOT:
- "Evaluation Spine" = the ONLY valid term for the post-L2 scoring system
- "Evaluation" alone is deprecated shorthand and should not appear as a standalone system name
- "System Outcome Metrics" = the metric set produced by the Evaluation Spine

+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
| LIBRARY SYSTEM LAWS (GLOBAL INVARIANTS)                                                                                                                      |
| 1. Only L2 touches books (execution authority)            4. L1 decides what to look for (reasoning authority)  7. L5 decides if work is allowed (policy)    |
| 2. Only L4 stores books permanently (state authority)     5. C0 assembles what is looked at (context assembly)  8. L6 verifies what happened (observe only)  |
| 3. Only UWG writes to the archive (mutation authority)    6. L0 decides where work goes (routing authority)     9. Evaluation Spine judges outcomes but cannot act |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| TEMPORALITY RULE:                                                                                                                                            |
| - TEMPORARY: L1 reasoning, C0 context, execution state                                                                                                       |
| - PERMANENT: L4 archive, UWG writes, policy updates                                                                                                          |
| - TEMPORARY layers can NEVER directly mutate PERMANENT layers                                                                                                |
+--------------------------------------------------------------------------------------------------------------------------------------------------------------+

+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
| LAYER GRAVITY MATRIX (ARROWS SHOW PERMITTED COMMUNICATION)                                                                                                   |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------|
|                                                                                                                                                              |
|   U0 (User)                                                                               [BUS C/D/E]                                                        |
|      ↓                                                                                                                                                       |
|   L1 (Cognition) ────────→ C0 (Context)                                                   [BUS T/P/U]                                                        |
|      ↓                         ↓                                                                                                                             |
|   L0 (Routing) ←──────────┬─────┴─────┬──────────┐                                                                                                           |
|      ↓                    ↓           ↓          ↓                                                                                                           |
|   L3 (Orchestration) → L5 (Safety) → L2 (Execution) → ⚖️ Evaluation Spine → L6 (Observe) → L4 (Store) → 🧠 Meta-Learning                                   |
|                                                                                                                                                              |
|   SOLID ARROWS  = Official bus-mediated communication (✅ ALLOWED)                                                                                           |
|   DASHED ARROWS = Direct layer-to-layer imports (⚠️ VIOLATION — see [10])                                                                                    |
|   ←→            = Bidirectional flow with chokepoint enforcement                                                                                             |
|                                                                                                                                                              |
|   KEY RULE: Lower layers cannot import upward. L0→L2 direct = gravity breach.                                                                                |
+--------------------------------------------------------------------------------------------------------------------------------------------------------------+

+-------------------------------------------------------------------------+   +--------------------------------------------------------------------------------+
| LAYER SOVEREIGNTY MATRIX                                                |   | ARCHITECTURE VALIDATION (ADG VERIFIED)                                         |
| L1: Propose only        L0: Route only                                  |   | • All mutation paths terminate at UWG                                          |
| L3: Orchestrate only    L2: Execute only                                |   | • No upward authority leakage                                                  |
| L4: Persist only        L5: Certify only                                |   | • Replay + determinism enforced                                                |
| L6: Observe only                                                        |   | • Dynamic runtime mutation (monkeypatch/setattr/importlib.reload) FORBIDDEN    |
| Strict authority boundaries                                             |   |--------------------------------------------------------------------------------|
+-------------------------------------------------------------------------+   +--------------------------------------------------------------------------------+

[1] 🧰 DOMAIN APPS & SHARED TYPE SYSTEM (ZERO AUTHORITY SURFACE)
+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
| apps_* = intent producers only (no execution authority). E.g., apps_lic (InMail Campaign), apps_rg (Resume Generation), apps_rfp (RFP Response).             |
| [STRUCTURE]: reasoning/ (agents), engines/ (logic), config/ (params), tools/ (actions), types/ (models), validators/ (checks), enforcement/ (strategies).    |
| apps_shared = shared types, schemas, enforcement contracts. Cross-domain infrastructure, configs, validators.                                                |
| => SCHEMA MUST EMIT: {intent_delta, tool_requests[], state_diff_proposal}                                                                                    |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| CRITICAL CLARITY:                                                                                                                                            |
| - These components NEVER walk into the restricted archive. NEVER dispatch runners. NEVER stamp approvals.                                                    |
| - [SCOPE] TOOLS STRICTLY SEGMENTED BY ROUTE/ROLE/AGENT.                                                                                                      |
+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
                                                                             v
=========================================================================================================================================================================================================================

[2] 📥 ENTRY + CORE PLANES (L1 / L6 / L4)
                                                                             v
+---------------------------------------------------+  +---------------------------------------------------+  +---------------------------------------------------+
| 🤖 L1: COGNITIVE STUDIO                           |  | 👁️ L6: OBSERVABILITY & REPLAY                     |  | 💾 L4: STATE / MEMORY / REGISTRY                  |
|---------------------------------------------------|  |---------------------------------------------------|  |---------------------------------------------------|
| [PHASE 1-4 / PTC COMPILER]                        |  | Determinism + replay authority                    |  | Canonical state + registries                      |
| - P1: PRIMING: Hydrate via KG, Sem-Mem            |  | Replay keys, semantic clock                       |  | Policy, tools, memory, cache                      |
| - P2: ORCHESTRATION: Tool Agents Draft            |  | Performance budgets                               |  | - P1: COGNITIVE REG: Prompts, Temp, Calibration   |
| - P3: PTC CALIB: Simulate CoT, Calc Complexity    |  | - P1: INGESTION: Latency, Error Rates             |  | - P2: CAPABILITY REG: Tools, APIs, Policies       |
| - P4: SYNTHESIS: Emit intent, tools, raw_reasoning|  | - P2: ANOMALY ENGINE: Detect Drift                |  | - P3: WORKFLOW MEMORY: Pending Steps, DAG         |
| Generates [U0: USER PROMPT] (ZERO auth)           |  | - P3: BROADCAST: Emit anomaly signals             |  | - P4: TELEMETRY LEDGER: Exec Logs, Decisions      |
| - Log Original User Intent                        |  | - P4: ARCHIVER: Raw Metrics, Snapshots            |  | [RULES]: L4 never authorizes/executes.            |
|---------------------------------------------------|  |---------------------------------------------------|  |---------------------------------------------------|
| C0 RAG CALL CLARIFIED:                            |  | DOES NOT EXECUTE                                  |  | DOES NOT DECIDE                                   |
| - L1 calls C0 during reasoning                    |  | DOES NOT ROUTE                                    |  | DOES NOT EXECUTE                                  |
| - L1 asks: “What books exist on this?”            |  | ONLY OBSERVES + VALIDATES + AUDITS                |  | ONLY STORES + SERVES                              |
|                                                   |  |---------------------------------------------------|  |                                                   |
|                                                   |  | HARD CONSTRAINT:                                  |  |                                                   |
|                                                   |  | - L6 CANNOT intervene, modify, or reroute exec    |  |                                                   |
+-------------------------+-------------------------+  +---------------------------------------------------+  +-------------------------+-----------------------+-+
                          | (Invokes C0)                                                                                                ^ (Feeds L4)            |
                          |                                                                                                             |                       |
                          |                                                                                                             | (Supplies C0)         |
                          |                                                                                                             |                       |
                          |                        +--------------------------------------------------+                                 |                       |
                          |                        | ⚖️ EVALUATION SPINE (REFERENCE ONLY)             |                                 |                       |
                          |                        | - Executes strictly AFTER L2                     |                                 |                       |
                          |                        | - See [POST-L2 EVALUATION SPINE] below           |                                 |                       |
                          |                        |                                                  |                                 |                       |
                          |                        | INPUT: Final execution result (from L2)          |                                 |                       |
                          |                        | OUTPUT: Metrics → L4 → Meta-learning             |                                 |                       |
                          |                        +--------------------------------------------------+                                 |                       |
                          |                                                                                                             |                       |
                          v                                                                                                             v                       v
=========================================================================================================================================================================================================================

[3] 🔍 C0 RAG PIPELINE                                                                                                                                                    | SYSTEM METRICS (GLOBAL LEDGER) |
+--------------------------------------------------------------------------------------------------------------------------------------------------------------+          | C0 Retrieval Metrics           |
| 🔍 C0 RAG PIPELINE (INFORMATIONAL CONTEXT ASSEMBLY)                                                                                                          |          | - Precision@K                  |
| ⚠️ C0 IS AN EPHEMERAL ASSEMBLY PROCESS (NOT A SYSTEM LAYER)                                                                                                  |          | - Recall@K                     |
+--------------------------------------------------------------------------------------------------------------------------------------------------------------+          | - Completeness                 |
C0 is a transient retrieval process invoked by L1. It assembles context but has ZERO authority.                                                                           | - Supported Answer Rate        |
                                                                                                                                                                          |--------------------------------|
L4H DEFINITION:                                                                                                                                                           |                                |
- L4H = Redis Hot Cache                                                                                                                                                   |                                |
- L4H is an ephemeral, non-authoritative projection of L4                                                                                                                 |                                |
- L4H optimizes latency only                                                                                                                                              |                                |
- L4 remains the canonical source of truth                                                                                                                                |                                |
                                                                                                                                                                          |                                |
  [ 🤖 L1 INVOCATION ] ── invokes → [ 🔍 C0 ] (retrieve context only)                                                                                                     |                                |
                                                                  v                                                                                                       |                                |
                                              [ FROM 💾 L4 ARCHIVE ]                                                                                                      |                                |
                                              |-----------------------------------------------|                                                                           |                                |
                                              | [PULL] C0 reads ONLY from L4                  |                                                                           |                                |
                                              | Deep archive lookup (read-only)               |                                                                           |                                |
                                              | Cannot modify catalog                         |                                                                           |                                |
                                              | Cannot write back                             |                                                                           |                                |
                                              |-----------------------------------------------|                                                                           |                                |
                                                                     |                                                                                                    |                                |
                                                                     v                                                                                                    |                                |
+-------------------------+   +-------------------------+   +-------------------------+   +-------------------------+   +-------------------------+                         |                                |
| ⚡ 0. REDIS CACHE CHECK | ─>| 🔢 1. EMBED QUERY       | ─>| 📈 2a. VECTOR SEARCH    | ─>| 🧬 3. RERANK / FUSION   | ─>| 🌳 4. CONTEXT BUILD     |                         |                                |
| Semantic cache lookup   |   | U0 → Ephemeral query    |   | FAISS (BLAS Locked)     |   | ScoreFusion / RRF       |   | Chunk stitching         |                         |                                |
| (L4H = Redis Hot Cache) |   | vector                  |   | ⟪ SEARCHES 💾 L4 ⟫      |   | Dedupe by chunk_id      |   | Parent-child expansion  |                         |                                |
+-------------------------+   +-------------------------+   +-------------------------+   +-------------------------+   +-------------------------+                         |                                |
            | (Cache Miss)                                            ^ 2b. Lexical retrieval (BM25/ASTAwareTok)                                                          |                                |
            v                                                                                                                                                             |                                |
+-------------------------+                                                                                         +---------------------------------------------------+ |                                |
| 💾 CACHE WRITE          |                                                                                         | 🎯 5. COMPLETENESS CHECK                          | |                                |
| Store result in Redis   |                                                                                         |---------------------------------------------------| |                                |
+-------------------------+                                                                                         | Context completeness scoring & monitoring signals.| |                                |
                                                                                                                    | Answer support & chunk manifest validation.       | |                                |
                                                                                                                    |---------------------------------------------------| |                                |
                                                                                                                    | [ RETURNS TO 🤖 L1 REASONING ]                    | |                                |
                                                                                                                    |-----------------------------------------------|   | |                                |
                                                                                                                    | [OUT] C0 → L1                                 |   | |                                |
                                                                                                                    | Returns curated reading stack                 |   | |                                |
                                                                                                                    | Enables answer synthesis                      |   | |                                |
                                                                                                                    | No side effects                               |   | |                                |
                                                                                                                    |-----------------------------------------------|   | |                                |
                                                                                                                    +---------------------------------------------------+ |                                |
                                                                                                                                                                          |                                |
C0 HARD RULES: NO MEMORY WRITE | NO ROUTING CONTROL | NO EXECUTION AUTHORITY | C0 cannot influence tool selection (L2)                                                    |                                |
L4H HARD RULES: NEVER canonical | NEVER authoritative | Cache miss falls back to L4 | Cache hit does NOT bypass governance                                                |                                |
                                                                                                                                                                          |                                |
=========================================================================================================================================================================================================================

[4] 🛡️ L5 SAFETY (SOVEREIGN CONTROL PLANE) — SSOT GOVERNANCE & STRUCTURAL INTEGRITY                                                                                           |                                |
+--------------------------------------------------------------------------------------------------------------------------------------------------------------+          |                                |
| CLASSIFICATION KERNEL [core_kernel/classification_kernel.py] — ZERO-DEPENDENCY SSOT                                                                          |          |                                |
| - AST-based classification with 19-priority queue. FileType taxonomy (20 canonical types).                                                                   |          |                                |
| - LRU cache (@lru_cache(maxsize=1024)). Dual-tag conflict detection.                                                                                         |          |                                |
| - CONFIG_WITH_LOGIC detection. Error hardening: catch-all guard prevents batch crash.                                                                        |          |                                |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------|          |                                |
| STRUCTURE BLUEPRINT [config/structure_blueprint/] — SOVEREIGN TERRITORIES & PATH VALIDATION                                                                  |          |                                |
| - ssot.py: LAYER_ROOTS, ENFORCED_TERRITORIES. sovereign_kernel.py: SOVEREIGN_KERNEL_COMPONENTS.                                                              |          |                                |
| - Path validation: is_path_allowed(). Forbidden patterns: duplicate prefixes, versioned files.                                                               |          |                                |
| - Root protection: ROOT_PROTECTED_FILES. Test placement SSOT.                                                                                                |          |                                |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------|          |                                |
| HARD RULE:                                                                                                                                                   |          |                                |
| - If a rule is not explicitly defined, L5 cannot invent one                                                                                                  |          |                                |
+--------------------------------------------------------------------------------------------------------------------------------------------------------------+          |                                |
                                                                                                                                                                          |                                |
=========================================================================================================================================================================================================================

[5] 🚦 L0 ROUTING + 🧠 META-LEARNING BUS                                                                                                                                  |                                |
+--------------------------------------------------------------------------+ +---------------------------------------------------------------------------------+          |                                |
| 🚦 L0 ROUTING (THE AUTHORITY NODE)                                       | | 🧠 META-LEARNING BUS (system_learning/pipelines/)                               |          |                                |
|--------------------------------------------------------------------------| |---------------------------------------------------------------------------------|          |                                |
| - P1: Assign TraceID                                                     | | [Stage order immutable: AUDIT→TELEM→CFG→SNAP→RCA→PROP→VAL→IN→COM]             |          |                                |
| - P2: Compute PolicyHash                                                 | | STAGE 1 [AUDIT]    : Read-only audit slice.                                   |          |                                |
| - P3: Intent classification                                              | | STAGE 2 [TELEMETRY]: Read-only telemetry + Evaluation Spine metric events.    |          |                                |
| - P4: Deterministic routing election                                     | | STAGE 3 [CONFIG]   : Materialized config bytes.                               |          |                                |
| - P5: Tool budget arbitration                                            | | STAGE 4 [SNAPSHOT] : MetaLearningSnapshot (SemanticClockSnapshot).            |          |                                |
| - P6: Agent execution profile enforcement                                | | STAGE 5 [RCA]      : analyze_failures() -> RCAReport.                         |          |                                |
| - P7: Seal signed execution plan (InstructionPacket)                     | | STAGE 6 [PROPOSE]  : Fixed order: L0 -> RAG -> L1 -> L5 using prior metric signals only. |                                |
|       [trace_id, policy_hash, route_mode, allowed_tools, signature]      | |                      + ResourcePrediction + DPO PATH (RLHF).                  |          |                                |
| - P8: Dispatch to assembly stage                                         | | STAGE 7 [VALIDATE] : ReplayValidator + ShadowEvaluator + Oscillation          |          |                                |
|--------------------------------------------------------------------------| |                      Oscillation detected -> auto-rejected.                   |          |                                |
| ELEVATOR SHAFT: JIT context loading, vertical state                      | | STAGE 8 [INTAKE]   : HealingOutcomeIntakeAdapter.build_record().              |          |                                |
| synchronization, cross-layer context transport.                          | |         [PATTERN]  : PatternAnalysisEngine -> PatternFindingReport.           |          |                                |
|--------------------------------------------------------------------------| | STAGE 9 [COMMIT]   : IF proposal_only=False -> ApprovalGate ->                |          |                                |
| METRIC INGESTION RULE:                                                   | |                      VersionStore -> Activator. (Default: True).              |          |                                |
| - Reads System Outcome Metrics from 👁️ L6 / 💾 L4 only                   | |                      [Dual injection REQUIRED. Single => HARD FAIL]             |          |                                |
| - Never reads directly from active L2 execution                          | |                      [CommitProofInvariant: binds to true implementation]       |          |                                |
| - Never mutates current execution in-flight                              | |---------------------------------------------------------------------------------|          |                                |
|--------------------------------------------------------------------------| | TEMPORAL RULE:                                                                |          |                                |
| HARD CONSTRAINT:                                                         | | - Meta-learning NEVER affects current execution                               |          |                                |
| - Routing decisions are rule-based, not intelligent                      | | - Only future executions after approval                                       |          |                                |
| - Cannot dynamically change destination outside rules                    | |                                                                               |          |                                |
+--------------------------------------------------------------------------+ +---------------------------------------------------------------------------------+          |                                |
                                                                                                                                                                          |                                |
=========================================================================================================================================================================================================================

[6] 🧩 ASSEMBLY (GOVERNED PAYLOAD CREATION)                                                                                                                               |                                |
+--------------------------------------+ +--------------------------------------+ +--------------------------------------+ +--------------------------------------+         |                                |
| 📜 S0 SYSTEM RULES                   | | 🚧 D0 ENFORCEMENT                    | | 📚 C0 CONTEXT                        | | 🗣️ U0 REQUEST                        |         |                                |
| (Hard-coded constitutions)           | | (Semantic fences/tool constraints)   | | (Elevator Shaft/RAG knowledge)       | | (Raw intent from L1)                 |         |                                |
+--------------------------------------+ +--------------------------------------+ +--------------------------------------+ +--------------------------------------+         |                                |
| => Final Package = Validated Script ready for Path B/C Execution                                                                                              |         |                                |
| => [BLOCK] BLOCK HOSTILE INPUT VECTORS (Neutralize Attack Paths)                                                                                              |         |                                |
| => [SPLIT] SPLIT INTO ATOMIC TASKS (Limit Scope, Prevent Collateral)                                                                                          |         |                                |
| - Emits: Governed Payload => Passes to Paths A / B / C / D                                                                                                    |         |                                |
+---------------------------------------------------------------------------------------------------------------------------------------------------------------+         |                                |
| ORDER MATTERS: Rules command restrictions → restrictions guard references → references contextualize the request.                                             |         |                                |
+---------------------------------------------------------------------------------------------------------------------------------------------------------------+         |                                |
                                                                                                                                                                          |                                |
=========================================================================================================================================================================================================================

[7] 🛤️ EXECUTION PATHS                                                                                                                                                    |                                |
+======================================+ +======================================+ +======================================+ +======================================+         |                                |
| 📖 PATH A                            | | 🛡️ PATH B                            | | ⚡ PATH C                            | | 👤 PATH D (HUMAN REVIEW FIRST)       |         |                                |
|--------------------------------------| |--------------------------------------| |--------------------------------------| |--------------------------------------|         |                                |
| READ-ONLY RESPONSE                   | | POLICY CHECK FIRST                   | | EXECUTE SCRIPT DIRECT                | | 1. Generate review artifact          |         |                                |
| - No system mutation                 | |--------------------------------------| |--------------------------------------| | 2. Freeze execution                  |         |                                |
| - Logged outcome                     | | L3 ORCHESTRATION                     | | L3 ORCHESTRATION                     | | 3. Human decision matrix             |         |                                |
| - ML consumes outcome                | | - Sequential Handshake               | | - Sequential Handshake               | |    [APPROVE | MODIFY_DIFF | REJECT]  |         |                                |
|                                      | | - Conflict Arbitration               | | - Conflict Arbitration               | | 4. Validate patch schema             |         |                                |
|                                      | | - Merge Overlap Tools                | | - Merge Overlap Tools                | | 5. Route patch to L5 re-clearance    |         |                                |
|                                      | | - Gate: Hallucination                | | - Eval Result vs DAG                 | | 6. Execute approved modification     |         |                                |
|                                      | | - Seed: Strict heal                  | | - Seq: Branches/Parallel             | | 7. Record HITL decision              |         |                                |
|                                      | |                                      | | - Coord: Sync                        | | [ML]: Drift Monitor, Policy Shift    |         |                                |
|                                      | |                                      | | - Route: Complete/L2                 | |--------------------------------------|         |                                |
|                                      | |                                      | |                                      | | HARD RULE: Human input is untrusted  |         |                                |
|                                      | |                                      | |                                      | | until re-certified by L5             |         |                                |
+======================================+ +======================================+ +======================================+ +======================================+         |                                |
                                                                                                                                                                          |                                |
=========================================================================================================================================================================================================================

[8] ⚙️ L2 EXECUTION CORE (PTC SANDBOX) & CONTROL SPINE                                                                                                                    |                                |
+--------------------------------------------------------------------------------------------------------------------------------------------------------------+          |                                |
| AGENT EXECUTION PROFILE REGISTRY — COMPILE-TIME FROZEN SSOT                                                                                                  |          |                                |
| - ExecutionMode.DETERMINISTIC: No LLM calls. ExecutionMode.LLM_API: Requires SovereignLLMGateway.                                                            |          |                                |
| - Unregistered agent invocation → HARD FAIL. registry_digest() for validation.                                                                               |          |                                |
| SOVEREIGN LLM GATEWAY — SOLE LLM EGRESS SEAM                                                                                                                 |          |                                |
| - route_generation(). Model resolution: symbolic -> concrete. Provider health monitoring. Injection detection.                                               |          |                                |
| - Hash-chained audit log. Replay mode support (ReplayEnvelope). Fail-closed kill-switch.                                                                     |          |                                |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------|          |                                |
| HARD CONSTRAINTS:                                                                                                                                            |          |                                |
| - Cannot modify policy (L5) | Cannot modify routing (L0) | Cannot write directly to archive (must use UWG)                                                   |          |                                |
+--------------------------------------------------------------------------------------------------------------------------------------------------------------+          |                                |

+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
| L2 EXECUTION LIFECYCLE                                                                                                                                       |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 🔒 PRE-COMMIT → ✅ VALIDATION → 🛠️ EXECUTION → 🏥 HEALING/EVAL                                                                                                 |
|                                                                                                                                                              |
| Pre-Commit:   Receive SandboxEnvelope, freeze JIT state, claim write locks                                                                                   |
| Validation:   Verify InstructionPacket signature, CapToken scope, tool budget                                                                                |
| Execution:    Enforce ToolCall→Result schema, PTC isolation, CID tracking                                                                                    |
| Healing:      EscalationContext → FailureSignal → Route_healing_tier()                                                                                       |
+--------------------------------------------------------------------------------------------------------------------------------------------------------------+

+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
| EXECUTION LIFECYCLE FLOW (PHASE TRANSITIONS)                                                                                                                 |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------|
|                                                                                                                                                              |
│   ┌──────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐                                                                       │
│   │    U0    │──────→│    L1    │──────→│    L0    │──────→│    L3    │──────→│    L5    │                                                                       │
│   │  INPUT   │      │  THINK   │      │  ROUTE   │      │  ORCH    │      │  CHECK   │                                                                       │
│   └──────────┘      └──────────┘      └──────────┘      └──────────┘      └────┬─────┘                                                                       │
│                                                                                │                                                                             │
│                                                                                ↓                                                                             │
│   ┌──────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐                                                                       │
│   │    L4    │←─────│    L6    │←─────│ ⚖️ Eval  │←─────│    L2    │←─────│  APPROVE │                                                                       │
│   │  STORE   │      │  VERIFY  │      │  SPINE   │      │ EXECUTE  │      │          │                                                                       │
│   └──────────┘      └──────────┘      └──────────┘      └──────────┘      └──────────┘                                                                       │
│        ↑                                                                       │                                                                             │
│        └───────────────────────────────────────────────────────────────────────┘                                                                             │
│                                    (Feedback loop via BUS T/P/U only)                                                                                        │
│                                                                                                                                                              │
│   ARROW TYPES:                                                                                                                                               │
│   ────→ = Execution flow (has authority)                                                                                                                     │
│   ─ ─ → = Telemetry flow (read-only signals)                                                                                                                 │
│   ←──── = Return/response flow                                                                                                                               │
│                                                                                                                                                              │
│   LOOP BACK TO L1?  ❌ NEVER. L6→L1 direct = architecture violation.                                                                                         │
│   FEEDBACK PATH:    L6 → BUS P → Meta-Learning → BUS U → L5 → (future executions)                                                                            │
+--------------------------------------------------------------------------------------------------------------------------------------------------------------+

                                                                                                | (Clean result produced)                                                 |                                |
                                                                                                v                                                                         |                                |
                                                                                    (From L2 Execution Result)                                                            |                                |
                                                                                                ↓                                                                         |--------------------------------|
                                                                                                                                                                          | Evaluation Spine Metrics       |
[POST-L2] ⚖️ EVALUATION SPINE (TRUE EXECUTION POSITION)                                                                                                            | - Faithfulness                 |
⚠️ EXECUTES POST-L2 | WRITES TO L4 | DOES NOT FEED L1 INLINE                                                                                                       | - Groundedness                 |
================================================================================================================================================================   | - Answer Relevancy             |
                                                                                                                                                                   | - Regression Delta             |
[ ⚙️ L2 EXECUTION ] ─────→ [ ⚖️ EVALUATION SPINE ] ─────→ [ 👁️ L6 VALIDATE ] ─────→ [ 💾 L4 STORE ] ─────→ [ 🧠 META-LEARNING ]                                         |--------------------------------|
                                                                                                                                                                          |                                |
AUTHORITY: ⚖️ READ-ONLY | NO EXECUTE | NO ROUTE | NO MUTATION | SIGNALS ONLY                                                                                           |                                |

FLOW (STRICT, SINGLE LINE): ⚙️ L2 Execute → ⚖️ Evaluation Spine scores → 👁️ L6 validates/observes → 💾 L4 stores → 🧠 Meta-learning ingests later
=========================================================================================================================================================================================================================

+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 🚪 UWG (UNIVERSAL WRITE GATEWAY) — SOLE DURABLE MUTATION PATH                                                                                                |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| - All FS/DB/Vector writes route through single gateway with MutationRecord logging                                                                           |
| - Allowed: artifacts/, docs/reports/, logs/, temp/. Blocked: .exe, .dll, .py, .js, .ts                                                                       |
| - Non-UWG mutation → ToolNotAllowedError. Replay-verified via digest chain.                                                                                  |
| - Cannot modify: policy (L5) | routing (L0) | direct archive writes (must use UWG)                                                                           |
+--------------------------------------------------------------------------------------------------------------------------------------------------------------+

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ UWG AUTHORITY CHAIN (ALL MUTATION PATHS TERMINATE HERE)                                                                                                    │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                                                                            │
│   L2 Execution ──┐                                                                                                                                         │
│   L4 Store ──────┼──→ ┌───────────────┐                                                                                                                    │
│   L5 Policy ─────┤    │     UWG       │                                                                                                                    │
│   L3 Config ─────┼──→ │  (Universal   │ ──→ ┌─────────────┐                                                                                                │
│   L0 Routing ────┤    │ Write Gateway)│     │  Artifacts  │                                                                                                │
│   L6 Audit ──────┘    └───────────────┘     │  Reports    │                                                                                                │
│                              │              │  Logs       │                                                                                                │
│                              ↓              └─────────────┘                                                                                                │
│                        ┌───────────────┐                                                                                                                   │
│                        │ Replay Digest │                                                                                                                   │
│                        │  Chain Link   │                                                                                                                   │
│                        └───────────────┘                                                                                                                   │
│                                                                                                                                                            │
│   ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐   │
│   │ VIOLATION PATTERN DETECTED: Direct FS write from L2/L4/L5 bypassing UWG → BLOCKED                                                                  │   │
│   │ Arrow paths show required routing. Any direct dashed line = architecture drift.                                                                    │   │
│   └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                                                                                            │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

=========================================================================================================================================================================================================================

[9] 🏁 OUTCOME + WRITEBACK & DETERMINISM PROOF STANDARD                                                                                                                |--------------------------------|
+--------------------------------------------------------------------------------------------------------------------------------------------------------------+       | System Outcome Metrics         |
| FINAL DECISION / OUTCOME LOGGING                                                                                                                             |       | - Task Success Rate            |
| - Outcome and state diffs are logged and versioned via ExecutionTrace Audit Envelope.                                                                        |       | - Latency                      |
| - [L1 UPDATE] FINAL ANSWER GENERATED USING ONLY ToolTranscript (Maintains PTC Context Isolation).                                                            |       | - Error Rate                   |
| - [SYNC] UPDATE SHARED TEAM MEMORY & ACTIVITY Ledger (Non-blocking state update occurs only after L2.2 confirms).                                            |       | - Cost                         |
| - [RECON] VERIFY DATA MATCHES REALITY (Detect ghost mutations).                                                                                              |       +--------------------------------+
|--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| DETERMINISM PROOF STANDARD                                                                                                                                   |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| - Digest chain: registry_digest, agent_inventory, tool_inventory_hash, meta_learning_config_hash                                                             |
| - SemanticClock = sole time authority. Timestamps/randomness captured/blocked.                                                                               |
| - Replay strictness: All mutations reconstructable from ExecutionTrace Audit Envelope.                                                                       |
+--------------------------------------------------------------------------------------------------------------------------------------------------------------+

FINAL SYSTEM TRUTH:
- 🤖 L1 = THINK (Research Librarian mapping the strategy)
- C0 = READ (Temporary stack of reference books)
- 🚦 L0 = ROUTE (Pneumatic tube dispatcher stamping the order)
- 🎼 L3 = COORDINATE (Shift Supervisor sequencing the tasks)
- 🛡️ L5 = GOVERN (Armed Commandant enforcing the perimeter)
- ⚙️ L2 = EXECUTE (Restorer working inside the secure lab)
- 💾 L4 = STORE (The Deep Archive and canonical ledger)
- 👁️ L6 = OBSERVE (Security cameras and turnstile counters — read-only, no enforcement)
=========================================================================================================================================================================================================================