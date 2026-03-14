==========================================================================================================================================================================
                                                      🗺️ AGENTIC SYSTEM — PRODUCTION PROCESS MAP 🗺️
                                   LAYER SOVEREIGNTY: Upward mutation FORBIDDEN · Dynamic runtime mutation FORBIDDEN
==========================================================================================================================================================================
 ◄ LEFT BUS: CONTROL & SAFETY ►                                                        ◄ RIGHT BUS: TELEMETRY & LEARNING ►
 [C] Vigilance re-route    L6 anomaly detected → immediately re-enters L0              [T] Metrics / evaluation reads  → ML engine
 [D] Safety fail re-entry  L5 violation → re-enters L1 (plan discarded)                [P] DPO pairs / drift proposals → ML engine
 [E] Drift broadcast       forces stall + locks execution to human-review path          [U] ML parameter commits        → L0 routing + L1 weights
==========================================================================================================================================================================

[1] DOMAIN APPS  —  agents have zero execution authority; they propose, they never act
  +-------------------------------------+  +-------------------------------------+  +-------------------------------------+
  | apps_lic  InMail Campaigns          |  | apps_rg   Resume Generation         |  | apps_research / apps_rfp / apps_exec|
  | Intent deltas surface through a     |  | Multi-step reasoning chain. Each    |  | Domain-isolated orchestrators.      |
  | shared orchestration contract.      |  | agent scoped to a single concern.   |  | No cross-domain write authority.    |
  | No agent can approve its own output.|  | Evaluation wired to every hop.      |  | Proposals only; sovereignty DOWN.   |
  +-------------------------------------+  +-------------------------------------+  +-------------------------------------+
                                                    v  (raw intent — no authority passes this boundary)
==========================================================================================================================================================================

[2] COGNITIVE ENTRY  —  reasoning is separated from routing; L1 cannot dispatch itself
  +-----------------------------------------------+      +-----------------------------------------------+  +-------------------------------+
  | L1: COGNITIVE STUDIO              [pulls: U]   |      | L6: OBSERVABILITY & ANOMALY DETECTION         |  | L4: STATE & MEMORY            |
  |-----------------------------------------------|      |-----------------------------------------------|  |-------------------------------|
  | Priming → Orchestration → Synthesis            |      | Tiered vigilance: signal → score → re-route   |  | Capability + CID registries   |
  | Emits a U0 query intent — nothing more.        |<--[E]| Anomaly RCA engine. Execution transcripts.    |  | Workflow memory + checkpoints |
  | Cannot approve. Cannot dispatch. Cannot write. |      | Detects drift and fires [E] stall if needed.  |  | Semantic cache. Telemetry.    |
  | RAG context is informational only (C0).        |      +---------------------------+-------------------+  +---------------+---------------+
  +---------------------+-------------------------+                                  |                                       |
                        | U0 query                                                   v                                       v (feeds ML)
                        v                                        +---------------------------------------------+
                                                                 | EVALUATION SPINE                            |
                                                                 | P@K · MRR · NDCG · Groundedness  [emits: T] |
                                                                 | DPOBatchBuilder → preference pairs[emits: P] |
                                                                 | EvalSnap → L4 · DriftAlert → L6             |
                                                                 +---------------------------------------------+
==========================================================================================================================================================================

[3] C0 RAG PIPELINE  —  retrieval is informational; it cannot alter routing, safety thresholds, or policies
  +----------+   +----------+   +----------------+   +----------+   +----------+   +----------+   +----------+
  | 0. CACHE |-->| 1. EMBED |-->| 2a. VECTOR     |-->| 3. FUSE  |-->| 4. P-C   |-->| 5. SCORE |-->| 6. WRITE |
  | Redis    |   | ephemeral|   | FAISS/Pinecone |   | RRF/dedup|   | siblings |   | complete.|   | TTL/LRU  |
  +----------+   +----------+   +----------------+   +----------+   +----------+   +----------+   +----------+
                             \->| 2b. LEXICAL    |--/
                                | BM25/ASTAware  |
                                +----------------+
  C0 context flows directly to [6] Assembly — it bypasses routing entirely.
  RAG cannot mutate routing decisions, safety thresholds, execution tiers, or policy state.
==========================================================================================================================================================================

[4] L5 SAFETY ENFORCEMENT  —  four independent validators; all must pass before routing proceeds
  +------------------------------+  +------------------------------+  +------------------------------+  +------------------------------+
  | [1] CLASSIFICATION KERNEL    |  | [2] STRUCTURAL BLUEPRINT     |  | [3] AGENT REGISTRY           |  | [4] SOVEREIGN LLM GATEWAY    |
  | AST-based filetype analysis  |  | Territory + path validation  |  | Profile + registry digest    |  | Sole egress to AI providers  |
  | 19-priority queue, zero deps |  | SSOT-enforced boundaries     |  | Allowlist + exec mode check  |  | Hash audit / injection detect|
  +------------------------------+  +------------------------------+  +------------------------------+  +------------------------------+
              |                                  |                                  |                                  |
  [D] <-------+----------------------------------+-----(FAIL)----------------------+----------------------------------+
                                                                 | PASS
                                                                 v
==========================================================================================================================================================================

[5] L0 ROUTING + META-LEARNING BUS  —  routing is deterministic; ML improves it but never bypasses it
  +--------------------------------------------------+   +----------------------------------------------------------+
  | L0: ROUTING                          [pulls: C]  |   | META-LEARNING BUS                          [pulls: T, P] |
  |--------------------------------------------------|   |----------------------------------------------------------|
  | Classify intent against L4 state                 |   | IMMUTABLE STAGE ORDER:                                   |
  | Assign TraceID + PolicyHash                      |   | S1 Audit → S2 Telemetry → S3 Config → S4 Snapshot        |
  | Deterministic agent election                     |-->| S5 RCA → S6 Propose (DPO/RLHF/HITL) → S7 Validate       |
  | Tool budget arbitration                          |   | S8 Intake (HealingOutcome) → S9 Commit (proposal_only)   |
  | Seal + dispatch cryptographically signed plan    |   | ApprovalGate → VersionStore → dual-inject activation     |
  | Cannot evaluate. Cannot execute.                 |   +----------------------------------------------------------+
  | Unregistered agent → hard fail.                  |                        | [emits: U] (L0 rules + L1 weights)
  +--------------------------------------------------+                        v
                         | (dispatches signed execution plan)
                         v
==========================================================================================================================================================================

[6] ASSEMBLY  —  prompt is a governed payload; constitution is immutable, injections are fenced
  C0 RAG context ──┐
  Signed L0 plan ──+──> [ S0: System prompt (constitutional, hard-coded) ]
                        [ D0: Injection fences / tool fences              ]
                        [ C0: RAG-injected knowledge (informational only) ]
                        [ U0: Raw user intent from L1                     ]
                        [ PROMPT GOVERNANCE: template validation, hostile input block, split → governed payload ]
                                                       | governed payload
                                                       v
==========================================================================================================================================================================

[7] EXECUTION PATHS  —  path selected by L0; [E] stall collapses all paths to D
  +---------------------+  +---------------------+  +---------------------+  +---------------------+
  | PATH A  Read-Only   |  | PATH B  Policy-First |  | PATH C  Direct      |  | PATH D  Human-First |
  | No mutation.        |  | L3 orchestrator with |  | L3 DAG engine.      |  | Human reviews diff. |
  | Logged + audited.   |  | conflict arbitration,|  | Multi-agent coord.  |  | Zero authority.     |
  |                     |  | HSM state machine,   |  | MCP tool routing.   |  | DPO pair generated. |
  |                     |  | hallucination gate.  |  | Escalation routing. |  | [E] always lands    |
  +---------------------+  +---------------------+  +---------------------+  | here if drift active|
           |                         |                         |              +---------------------+
           v                         v                         v                         |
  +---------------------------------------------------------------------------------------------+
  | L5: CROSS-PATH SAFETY GUARD                                                                 |
  | Risk tier · compliance hash · proposal vs policy · Approve / Remediate / Reject  [emits: P] |
  | RE-CLEAR mandatory after any human MODIFY_DIFF                                              |
  +---------------------------------------------------------------------------------------------+
           | PASS → stamp work contract → sandbox permission
  [D] <----+ FAIL → re-route to L1 (plan discarded, trace preserved)
           v
==========================================================================================================================================================================

[8] L2 EXECUTION CORE  —  every capability call is authorized; mutation has exactly one exit point
  +---------------------------------------------------------------------------------------------+
  | authorize_and_execute() is the single chokepoint — no capability runs without it            |
  | Sandbox isolation (Docker/Firecracker) · SovereignLLMGateway (no direct HTTP to providers) |
  | Protocol: pre_commit → validate → execute → heal · Circuit breakers + timeout enforcement  |
  +---------------------------------------------------------------------------------------------+
  +-------------------+  +-------------------+  +-------------------+  +-------------------+
  | P1: INIT          |  | P2: EXECUTE        |  | P3: HEAL          |  | P4: SYNTHESIZE    |
  | Validate plan     |->| Enforce ToolCall   |->| Tiered escalation |->| Aggregate outputs |
  | Freeze clean state|  | Structured stdout  |  | LOCAL→QWEN→GEMINI |  | Validate schema   |
  | Claim write access|  | CEIL on stuck loops|  | HealingOutcome    |  | ToolTranscript    |
  +-------------------+  +-------------------+  +-------------------+  +-------------------+

  UNIVERSAL WRITE GATEWAY (UWG) — sole exit point for all durable state mutation
  Agents · orchestrators · routers cannot write directly. UWG enforces replay-diff audit on every write.
  Dependency graph validation continuously verifies no component has acquired a bypass path.
==========================================================================================================================================================================

[9] OUTCOME  —  every execution is a training signal; the system learns from its own traces
  +---------------------------------------------------------------------------------------------+
  | Answer via signed ExecutionTrace · RCA artifacts · Compliance records · Audit trail        |
  | Metrics feed [T] bus · Preference pairs feed [P] bus · L4 state committed                 |
  | Deterministic replay: every trace is reproducible — supports debugging, audit, fine-tuning |
  +---------------------------------------------------------------------------------------------+
                         v  (L4 Activity Ledger + Redis Cache + ML intake)

==========================================================================================================================================================================
 WHAT THIS DEMONSTRATES
 • Agents that propose, never act — authority is structurally impossible to acquire, not just discouraged
 • Fail-closed safety — violation triggers upward re-routing; the system cannot proceed through a failed check
 • Deterministic routing with ML improvement — L0 is rule-based; the learning bus improves rules, never replaces them
 • Self-healing at scale — tiered recovery (local → external model) with automated DPO pair generation from failures
 • Mutation sovereignty — one write gateway, verified by dependency graph in CI; bypasses are structurally detectable
 • Architecture-as-code — this diagram's boundaries are continuously verified against the live AST dependency graph
==========================================================================================================================================================================
