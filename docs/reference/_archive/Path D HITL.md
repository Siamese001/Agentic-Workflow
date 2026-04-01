========================================================================================
    🗺️ PATH D — HUMAN-IN-THE-LOOP & DIRECT PREFERENCE OPTIMIZATION PROCESS FLOW 🗺️
CORE ANALOGY: Library Governance · UNIVERSAL WRITE GATEWAY = ONLY write path
========================================================================================

[ STAGE 1: ESCALATION & FREEZE ]
+--------------------------------------------------------------------------------------+
| 🎼 L3 ORCHESTRATOR (Reference Desk)                                                  |
|--------------------------------------------------------------------------------------|
| - 📝 Prepares Artifact for review.                                                   |
| - 🔑 Emits original_plan_hash.                                                       |
| - ⏸️ Freezes context pending human decision.                                       |
|--------------------------------------------------------------------------------------|
| LIBRARY ANALOGY:                                                                     |
| BUS E (Escalation) Fire Alarm pulled. Orchestrator halts tasks and preps             |
| the exact clipboard of context for the Head Librarian.                               |
+--------------------------------------------------------------------------------------+
                                      v
[ STAGE 2: THE AIRLOCK (ZERO-AUTHORIZATION SANDBOX) ]
+--------------------------------------------------------------------------------------+
| 🔒 HUMAN DECISION GATE (Chief Librarian Airlock)                                     |
|--------------------------------------------------------------------------------------|
| - 🛑 ISOLATE: Places request in a Zero-Authorization Sandbox.                        |
|                                                                                      |
| ⚖️ THE DECISION MATRIX (Human selects one path):                                     |
|                                                                                      |
| 1. [APPROVE] ──────> Fast-tracks to Level 5 Safety Guard.                            |
|                                                                                      |
| 2. [REJECT] ───────> Aborts wave, re-routes back to Level 1. 🛑                      |
|                                                                                      |
| 3. [MODIFY_DIFF] ──> Provides structured_patch_schema.                               |
|                      - MUST reference original_plan_hash.                            |
|                      - MUST use allowlisted tools only.                              |
|                      - Sets Level 5_reclear_required = True.                         |
|                                                                                      |
| 🗄️ HUMAN-IN-THE-LOOP DECISION LOGGER (Audit Receipt Ledger)                          |
| - Format: American Standard Code for Info Interchange (ASCII) / Thread-safe.         |
| - System Role: Deterministic replay format.                                          |
| - Action: Forces the modified patch down the "elevator shaft" to execution.          |
|--------------------------------------------------------------------------------------|
| LIBRARY ANALOGY:                                                                     |
| Glass-walled review room. Head Librarian marks up the slip. They CANNOT              |
| walk the change into the archive themselves (No Universal Write Gateway access).     |
| The marked-up slip MUST be handed back to L5 for official re-stamping.               |
+--------------------------------------------------------------------------------------+
                                      v
[ STAGE 3: ROUTING & EXECUTION ]
+--------------------------------------------------------------------------------------+
| 🛡️ L5 SAFETY GUARD (Governance Archivist)                                            |
|--------------------------------------------------------------------------------------|
| - 🔍 Re-evaluates all patches.                                                       |
| - 🚧 Enforces Level 5_reclear_required = True.                                       |
| - 🔏 Mints the [AUTHORIZATION] stamp.                                                |
| - 🛤️ Routes approved sequence to Level 2 Sandbox.                                    |
|--------------------------------------------------------------------------------------|
| LIBRARY ANALOGY:                                                                     |
| Commandant strictly verifies the Head Librarian's overrides before entry.            |
+--------------------------------------------------------------------------------------+
                                      v
+--------------------------------------------------------------------------------------+
| ⚙️ L2 EXECUTION CORE (Target Sandbox)                                                |
|--------------------------------------------------------------------------------------|
| - Receives officially stamped payload.                                               |
| - Executes validated script.                                                         |
| - Writes to 💾 L4 via Universal Write Gateway.                                       |
|--------------------------------------------------------------------------------------|
| LIBRARY ANALOGY:                                                                     |
| Restorer carries out approved work in isolated lab via Master Ledger Clerk.          |
+--------------------------------------------------------------------------------------+
                                      v
[ STAGE 4: META-LEARNING FEEDBACK ]
+--------------------------------------------------------------------------------------+
| 👁️ L6 DIRECT PREFERENCE OPTIMIZATION FEEDBACK (Cataloging Board)                     |
|--------------------------------------------------------------------------------------|
| - 📤 Extracts Direct Preference Optimization Pair.                                   |
| - 🧮 Hashes: Compares Control vs Candidate bytes using Secure Hash                    |
|   Algorithm 256-bit (SHA-256).                                                       |
| - ✅ Validates human decision for meta-learning record.                              |
| - 🔄 Reinforcement Learning from Human Feedback Optimizer loops                      |
|   data back to Stage 6 Pipeline for system adaptation.                               |
|--------------------------------------------------------------------------------------|
| DEFINITION & ANALOGY:                                                                |
| Direct Preference Optimization directly aligns AI behavior with human choices        |
| without a complex reward model. The Board uses pairs of data (what the human chose   |
| vs. AI proposal) to directly train the system to prefer the governed path.           |
+--------------------------------------------------------------------------------------+

========================================================================================
             HIGH-SIGNAL DATA CONTRACTS (LIBRARY RULES & RECEIPTS)
          Enforces deterministic replay and strict chain of custody.
========================================================================================
+--------------------------------------------------------------------------------------+
| 📜 HUMAN DECISION ARTIFACT                                                           |
| - [SCHEMA]: [trace_id, action, patch_schema, original_hash]                          |
| - [CONSTRAINT]: The MODIFY_DIFFERENCE action strictly enforces                       |
|   Level 5_reclear_required = True via the __post_init__() method, ensuring           |
|   no modification bypasses the Governance Archivist.                                 |
|--------------------------------------------------------------------------------------|
| ⚖️ DIRECT PREFERENCE OPTIMIZATION PAIR                                               |
| - [SCHEMA]: [example_id, human_decision]                                             |
| - [CONSTRAINT]: The example_id must contain the SHA-256 hashes of both the           |
|   Control and Candidate outputs to mathematically prove exactly what the             |
|   human was comparing.                                                               |
|--------------------------------------------------------------------------------------|
| 🗄️ HUMAN-IN-THE-LOOP DECISION RECORD                                                 |
| - [FORMAT]: Structured specifically for the Audit Receipt Ledger:                    |
|   HITL_DECISION_N: Agent=X | File=Y | Violation=Z | Proposed=W | Decision=D          |
|--------------------------------------------------------------------------------------|
| 🔄 REINFORCEMENT LEARNING FROM HUMAN FEEDBACK OPTIMIZER                              |
| - [SIGNATURE]: propose_from_direct_preference_optimization(batch, config, context)   |
|   -> ChangePackage                                                                   |
+--------------------------------------------------------------------------------------+
========================================================================================