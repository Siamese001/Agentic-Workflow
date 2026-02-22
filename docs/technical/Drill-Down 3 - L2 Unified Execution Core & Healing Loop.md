============================================================================================================================================================
                                DRILL-DOWN 3: L2 UNIFIED EXECUTION CORE & HEALING LOOP (EXPANDED QUINTUPLE-CLICK)
     (TENSOR-LEVEL VIEW: L3 ENTRY, L5 BLOCKING GATE, MICRO-VM SANDBOXING, AST FENCING, REDLOCK MUTEXES, STATE MERKLE SNAPSHOTS, & CYCLICAL AUTHORITY RETURN)
============================================================================================================================================================

                                   [ FROM: L0 ROUTING — PATH B, C, OR D ]
                                   +---------------------------------------------------------------------------------+
                                   | PAYLOAD: { "task_id": "dag_node_4", "rbac_token": "jwt_write_scoped",           |
                                   |            "action_type": "python_exec", "code_block": "df.dropna().to_sql()",  |
                                   |            "route_mode": "PATH_C", "trace_id": "trc_88x2_node4",               |
                                   |            "dag": { "nodes": [...], "edges": [...] } }                          |
                                   +---------------------------------------------------------------------------------+
                                                         ||
                                                         || (Push: RBAC-Locked DAG Payload)
                                                         v
+==========================================================================================================================================================+
| \\\ L3 – ORCHESTRATION (ENTRY GATE & BLAST-RADIUS MINIMIZER)                                                                                        /// |
|==========================================================================================================================================================|
|                                                                                                                                                          |
|  +-------------------------------------------------------------------------------------------+                                                           |
|  | L3 ORCHESTRATION HANDSHAKE                                                                |                                                           |
|  |-------------------------------------------------------------------------------------------|                                                           |
|  | - [HNDS] SEQUENTIAL HANDSHAKE: Verifies DAG node ordering before any action is proposed   |                                                           |
|  | - [SYNC] WORK INSTRUCTION SYNTHESIS: Translates DAG node into concrete action descriptor  |                                                           |
|  | - [SHRED] MINIMIZE BLAST RADIUS: Decomposes compound intent into atomic sub-actions       |                                                           |
|  |           Each sub-action is independently scoped — failure cannot cascade sideways       |                                                           |
|  | - [GATE]  BLOCK HALLUCINATION: Rejects any proposed action that references non-existent   |                                                           |
|  |           tools, schemas, or data paths before forwarding to L5                           |                                                           |
|  | - [ESC]   ESCALATE TO L5 GUARD: All proposed actions forwarded to L5 Safety — no bypass  |                                                           |
|  +-------------------------------------------------------------------------------------------+                                                           |
|                                         ||                                                                                                               |
|                                         || (1. Proposed Action)                                                                                         |
|                                         v                                                                                                               |
+==========================================================================================================================================================+
| \\\ L5 – SAFETY (ACTIVE BLOCKING GUARDIAN — RUNS BEFORE EVERY L2 ENTRY)                                                                             /// |
|==========================================================================================================================================================|
|                                                                                                                                                          |
|  +-------------------------------------------------------------------------------------------+      +------------------------------------------+         |
|  | L5 SAFETY GATE                                                                            |      | L4: POLICY & GUARDIAN STATE              |         |
|  |-------------------------------------------------------------------------------------------|<====>| - Guardian Script Definitions            |         |
|  | - Runs BLOCKING guardian scripts (no async — L2 cannot proceed until L5 returns)          |      | - Policy & Permissions Schema            |         |
|  | - Evaluates Policy + Permissions against proposed action                                  |      | - Sandbox Constraints                    |         |
|  | - [CONF_CALIB] Risk Gate: Limits blind execution via confidence calibration thresholds    |      +------------------------------------------+         |
|  | - [RISK]  RISK TIER CLASSIFY: Assigns tier 1–5 to proposed action                        |                                                           |
|  | - [STMP]  COMPLIANCE HASH/STAMP: Stamps action with policy version hash                  |                                                           |
|  | - [STOP]  HARD STOP REJECTION: Immediately blocks tier 4–5 actions                       |                                                           |
|  | - [BLOCK] BLOCK HOSTILE INPUT: Strips any residual injection vectors                     |                                                           |
|  |                                                                                           |                                                           |
|  | OUTCOME:  ALLOW  -> emits approved_action.json -> proceeds to L2.1 Validator             |                                                           |
|  |           BLOCK  -> emits rejection signal -> re-routes to L1 for replanning             |                                                           |
|  |           ESCALATE -> forwards to HUMAN REVIEW (PATH D)                                  |                                                           |
|  +-------------------------------------------------------------------------------------------+                                                           |
|                                                                                                                                                          |
|  ML Integration:                                                                                                                                         |
|  | [1. Anomaly Classifier]  =====(Track False Pos/Neg)======> META-LEARNING BUS -> L4 Anchor                                                            |
|  | [2. Policy Optimization] =====(Tune Rule Strictness)=====> META-LEARNING BUS -> L4 Anchor                                                            |
|  |                          =====(Adapt Threshold Config)===> META-LEARNING BUS -> L4 Anchor                                                            |
|                                                                                                                                                          |
+==========================================================================================================================================================+
                                         ||
                                         || (2. IF ALLOW: approved_action.json)
                                         v
+==========================================================================================================================================================+
| \\\ L2 – UNIFIED EXECUTION CORE (SINGULAR BOTTLENECK FOR SYSTEM MUTATION)                                                                           /// |
|==========================================================================================================================================================|
|                                                                                                                                                          |
|   [ PRE-EXECUTION AUTHORITY & LOCKING ]                                                                                                                  |
|   +-----------------------------------------------------------------+      +-----------------------------------------------------------------+          |
|   | 1.0 DISTRIBUTED MUTEX & LEASE MANAGER [L2.1: ILeaseVerifier]   |      | 2.0 STATE FREEZE & MERKLE SNAPSHOTTING                          |          |
|   |-----------------------------------------------------------------|      |-----------------------------------------------------------------|          |
|   | [1.1] Redlock Acquisition: Acquires N/2+1 Redis quorum locks    |      | [2.1] Merkle Tree Construction: Computes hashes for target rows |          |
|   | [1.2] TTL Lease: Sets hard execution expiry (e.g., 5000ms)      | <==> | [2.2] Baseline Anchoring: Stores hash in ephemeral L2 cache     |          |
|   | [1.3] RBAC Token Verification: Validates JWT scopes for task    |      |       Emits: boundary_snapshot.json (pre-execution baseline)   |          |
|   | [FREEZ] FREEZE CLEAN SYSTEM STATE before any write begins       |      | [2.3] Resource Prediction: L6-fed cgroup RAM/CPU allocation     |          |
|   | [CLAIM] CLAIM EXCLUSIVE WRITE ACCESS (blocks concurrent writes) |      +-----------------------------------------------------------------+          |
|   | [GUARD] PRESERVE EXISTING CODE INTEGRITY (read-before-write)    |                                                                                   |
|   +-----------------------------------------------------------------+                                                                                   |
|                             ||                                                                       ||                                                   |
|                             v                                                                        v                                                   |
|   +----------------------------------------------------------------------------------------------------------------------------------+                   |
|   | 3.0 COMPILER-LEVEL FENCING (THE AST SCANNER) [L2.1: Validator — Pre-Side-Effect]                                                |                   |
|   |----------------------------------------------------------------------------------------------------------------------------------|                   |
|   | [3.1] Abstract Syntax Tree (AST) Parsing: Deconstructs LLM code into logical nodes                                               |                   |
|   | [3.2] Node Blocklist: Physically strips `os.system`, `subprocess`, `shutil`, and raw `eval()` calls                              |                   |
|   | [3.3] SQL Injection Guard: Parametrizes all raw strings before passing to database drivers                                       |                   |
|   | [CID]  RESTRICT UNREGISTERED INTENTS: Rejects any action referencing a tool not in L4 capability registry                       |                   |
|   | [ZERO_TRUST] SCOPE MINIMAL TOOL ACCESS: Each action granted only the minimum permissions required                               |                   |
|   | [3.4] Sandbox Dry-Run / Diff Analysis: Simulates action in read-only mode, generates expected diff                               |                   |
|   |        IF diff matches approved_action.json -> proceed to Execution                                                              |                   |
|   |        IF diff diverges -> treat as VALIDATION FAIL -> route to L2.3 Healer                                                     |                   |
|   +----------------------------------------------------------------------------------------------------------------------------------+                   |
|                             ||                                                                                                                           |
|                             v                                                                                                                            |
|   +-----------------------------------------------------------------+      [ OPTIMIZATION & TELEMETRY BUS ]                                              |
|   | 4.0 EPHEMERAL MICRO-VM SANDBOX (FIRECRACKER) [L2.2: Execution] |      +-----------------------------------------------------------------+          |
|   |-----------------------------------------------------------------|      | • [Kernel Metrics]: eBPF streams syscall usage to L6            |          |
|   | [4.1] Micro-VM Boot: Isolated Firecracker instance (<150ms)     |      | • [OOM Guard]: Kills VM if RAM > cgroup_limit (512MB)           |          |
|   | [4.2] Execution Ceilings: Hard cgroup CPU/Memory starvation caps| <==> | • [Latency Check]: Ceiling [CEIL] triggers L2.3 if > 2000ms     |          |
|   | [4.3] Virtual Network: Zero external ingress/egress allowed     |      | • [Diff Engine]: Generates JSON Patch (RFC 6902) post-run       |          |
|   | SOLE DURABLE MUTATION POINT — only L2.2 may write to state      |      +-----------------------------------------------------------------+          |
|   | [QUOTA] KILL INFINITE COMPUTE BURN: Hard cycle ceiling enforced |                                                                                   |
|   | [FEEDBACK] INJECT FAILURE CONTEXT: On error, enriches error     |                                                                                   |
|   |            payload with execution trace before routing to healer|                                                                                   |
|   +-----------------------------------------------------------------+                                                                                   |
|                             ||                                                                                                                           |
|           +-----------------++-----------------+                                                                                                         |
|           || (Exit Code 0: Success)           || (Exit Code >0: Failure / Validation Fail)                                                               |
|           v                                   v                                                                                                          |
|   +---------------------------+      +-----------------------------------------------------------------+                                                 |
|   | 5.0 COMMIT & RELEASE      |      | 6.0 THE DETERMINISTIC HEALER & RECOVERY ENGINE [L2.3: IHealer] |                                                 |
|   |---------------------------|      |-----------------------------------------------------------------|                                                 |
|   | [5.1] JSON Patch Apply    |      | [UNDO]    RESET STATE: Destroys micro-VM, reverts to            |                                                 |
|   |       (RFC 6902 diff)     |      |           boundary_snapshot.json Merkle baseline                |                                                 |
|   | [5.2] Telemetry Emit      |      | [CIRCUIT] KILL RUN: Prevents loop limits / infinite retry spin  |                                                 |
|   | [5.3] Mutex Release       |      | [ROOT]    CAPTURE ROOT CAUSE: Extracts stack trace + error log  |                                                 |
|   | [5.4] [WRITE] COMMIT      |      | [RESET]   REVERT STATE: Restores pre-execution snapshot         |                                                 |
|   |       VERIFIED STATE      |      | [CURE]    FIX AND RETRY: Correction Strategy Synthesis          |                                                 |
|   |       CHANGE to L4        |      |           Generates revised_action_proposal.json                |                                                 |
|   +---------------------------+      | [6.1] Cap: If retries > 3, hard abort to Path D (Human Review)  |                                                 |
|                                      +-----------------------------------------------------------------+                                                 |
|                                                         ||                                                                                               |
|   [ DATA MUTATION & RAG SYNC ]                          || (4. Error Root / Rollback Req)                                                               |
|   +-----------------------------------------------------------------+                                                                                   |
|   | • Sandbox Snapshot Revert (on failure — byte-for-byte restore)  |                                                                                   |
|   | • Embedding Generation: Computes new vector for mutated content  |                                                                                   |
|   | • Vector Store Write: Async push to external vector store        |                                                                                   |
|   | • [TRTH] ANCHOR KNOWLEDGE DRIFT: Prevents stale embeddings       |                                                                                   |
|   |   from persisting across sessions — drift detected and flagged   |                                                                                   |
|   | • [ASYNC_SYNC]: Vector store write is non-blocking after L2.2    |                                                                                   |
|   |   confirms commit — state update does not block response path    |                                                                                   |
|   +-----------------------------------------------------------------+                                                                                   |
|                                                                                                                                                          |
|   ML Integration (feeds Meta-Learning Bus):                                                                                                              |
|   | [1. Failure Classifier]  =====(Learn Syntax Errors)==========> META-LEARNING BUS -> L4 Anchor                                                       |
|   | [2. Resource Predictor]  =====(Optimize Compute Cost)========> META-LEARNING BUS -> L4 Anchor                                                       |
|   | [3. RL Rollback Refiner] =====(Self-Correct Heal Logic)======> META-LEARNING BUS -> L4 Anchor                                                       |
|                                                                                                                                                          |
+==========================================================================================================================================================+
                                                          ||
                                                          || (5. REVISED PROPOSAL ROUTING — FROM L2.3 HEALER)
                                                          v
+==========================================================================================================================================================+
| \\\ CYCLICAL AUTHORITY RETURN LOOP (HEALER OUTPUT MUST RE-ENTER L5 — ZERO DIRECT PATH TO EXECUTION)                                                 /// |
|==========================================================================================================================================================|
|                                                                                                                                                          |
|  revised_action_proposal.json  ====>  L3 ORCHESTRATION  ====>  L5 SAFETY GATE  ====>  L2.1 VALIDATOR  ====>  L2.2 EXECUTION                             |
|                                                                                                                                                          |
|  INVARIANT: Any healed or revised plan MUST re-clear L5 Safety before retry.                                                                             |
|             There is ZERO direct path from L2.3 Healer to L2.2 Execution.                                                                               |
|             Bypassing L5 on a healed plan is a HARD CONSTITUTIONAL VIOLATION.                                                                            |
|                                                                                                                                                          |
|  [SEED] FORCE STRICT HEAL DETERMINISM: During L3 re-entry after healing, non-deterministic                                                               |
|         hallucination drift is suppressed. L3 must use the exact revised_action_proposal.json                                                            |
|         — no re-interpretation, no creative expansion of scope.                                                                                          |
|                                                                                                                                                          |
|  Retry Budget: configurable via L4 (default: 3 attempts). On exhaustion -> PATH D (Human Review).                                                       |
|                                                                                                                                                          |
+==========================================================================================================================================================+
                                                          ||
                                                          v
+==========================================================================================================================================================+
| FINAL DECISION / OUTCOME LOGGING                                                                                                                         |
|==========================================================================================================================================================|
| - Outcome and state diffs are versioned and committed to L4 audit log                                                                                    |
| - [SYNC]  UPDATE SHARED TEAM MEMORY: Non-blocking state update occurs only after L2.2 confirms commit                                                    |
| - [RECON] VERIFY DATA MATCHES REALITY: Detects ghost mutations across state layers (L4 vs. live state)                                                   |
| - Metrics captured: Execution Latency, Outcome Accuracy, Compute Cost, Human Correction Rate                                                             |
|                                                                                                                                                          |
|  +===(ZERO-LOSS LOOP: COMMIT TO L4 VIA META-LEARNING BUS)=================================================================>  L4 ANCHOR (VERSIONED UPDATE) |
+==========================================================================================================================================================+

+==========================================================================================================================================================+
| CRITICAL DISSEMINATION GUARANTEES (L2 SCOPE)                                                                                                            |
|==========================================================================================================================================================|
| 1.  NO SKIPPING THE SAFETY GATES: Every proposed action — including healed ones — must clear L5 before L2 entry.                                        |
| 2.  ALWAYS ATTACH THE SAFETY FENCES: [D0] fences from L5 Elevator Shaft remain active throughout L2 execution.                                          |
| 3.  ONLY LOAD DATA WHEN NEEDED: [JIT] context loading prevents stale or over-broad context injection.                                                    |
| 4.  HEALED PLANS MUST RE-CLEAR SAFETY: Zero trust on corrected actions — trust is not inherited from prior approved_action.json.                         |
| 5.  DON'T LOSE DATA ON ERROR: [FEEDBACK] enriches error payload before routing to healer — full context preserved.                                       |
| 6.  ISOLATE EVERY CHANGE IN SANDBOX: Firecracker micro-VM ensures zero durable damage on failure.                                                        |
| 7.  ONLY USE PRE-APPROVED SYSTEM TOOLS: [CID] physically blocks rogue function calls not in L4 capability registry.                                      |
| 8.  BREAK TASKS INTO TINY PIECES: [SHRED] at L3 minimizes blast radius — each atomic sub-action is independently scoped.                                 |
| 9.  PROTECT KNOWLEDGE FROM AGENT DRIFT: [TRTH] anchoring prevents agents from corrupting the vector truth store.                                         |
| 10. STOP AGENTS FROM BURNING MONEY: [QUOTA] + [CEIL] kill infinite loops and compute spikes before they propagate.                                       |
| 11. RECORD THE WHY, NOT WHAT: [ROOT] RCA captures decision logic and stack trace — not just the error code.                                              |
| 12. DOUBLE-CHECK DATA MATCHES THE WORLD: [RECON] detects ghost or hidden mutations across state layers post-commit.                                      |
+==========================================================================================================================================================+
