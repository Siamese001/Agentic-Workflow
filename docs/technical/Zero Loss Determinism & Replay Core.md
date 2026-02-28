======================================================================================================================================================================
                                   AGENTIC SYSTEM — ZERO-LOSS DETERMINISM & REPLAY CORE (VERTICAL TOPOLOGY)
======================================================================================================================================================================
  [ THE TOP LAYER: INGESTION & OBSERVABILITY ]                                [ THE SIDE LAYER: THE DETERMINISM & REPLAY STATE BUS ]
+---------------------------------------------------+                         +--------------------------------------------------------------------------------------+
| L1: COGNITIVE STUDIO / L6: OBSERVABILITY          |                         | L4: STATE, MEMORY & PERSISTENCE (TELEMETRY LEDGER & AUDIT ENVELOPE)                  |
|---------------------------------------------------|                         |--------------------------------------------------------------------------------------|
| - [L1] Ingests intent & initiates raw payload.    |<=====(Trace Egress)=====| - Consumes the `ExecutionTrace` (transcript, replay_key, and digest).              |
| - [L6] ANOMALY ENGINE: Monitors UWG violations    |                         | - Validated traces become the foundation for Stage 1-9 Meta-Learning Pipeline.       |
|        and un-transcripted network calls.         |                         | - [DIGEST] Stores W<n>-DETERMINISM-DIGEST.                                           |
+---------------------------------------------------+                         +--------------------------------------------------------------------------------------+
                          |                                                                             ||
                          v (Passes Payload)                                                            ||
========================================================================================================||============================================================
  [ L0 ROUTING -> PATHS -> L3 ORCHESTRATION -> L5 SAFETY ]                                              ||
+-----------------------------------------------------------------------------------------+             ||
| ASSEMBLY STAGE (SANDBOX AIRLOCK) via L0/L3/L5                                           |<============|| (Validates against active deterministic rules)
|-----------------------------------------------------------------------------------------|             ||
| - Compiles S0/I0/D0/C0/U0 into a validated, hash-signed `SandboxEnvelope`.              |             ||
| - L0 Routes, L3 Sequences, L5 Safety Chokepoint grants permission.                      |             ||
| - Passes [AUTH] stamped payload down the shaft.                                         |             ||
+-----------------------------------------------------------------------------------------+             ||
                          |                                                                             ||
                          v (Injects Signed `SandboxEnvelope` into L2)                                  ||
========================================================================================================||============================================================
  [ L2: PTC EXECUTION ENGINE (THE ZERO-LOSS CORE / UNTRUSTED LOGIC) ]                                   ||
+-----------------------------------------------------------------------------------------+             ||
| P2: SANDBOXED AGENT ACTIONS & RAW I/O THREADS                                           |             ||
|-----------------------------------------------------------------------------------------|             ||
| - Agent executes LLM-generated script. Attempts to write to memory/DB.                  |             ||
| - Requests time / random seed. Attempts external network calls.                         |             ||
| - [!] External nondeterminism leaks (un-transcripted API, RNG) break mathematical       |             ||
|   zero-loss guarantee. Diverging state breaks W<n>-DIGEST.                              |             ||
+-----------------------------------------------------------------------------------------+             ||
                          | (State Mutations & I/O Requests)                                            ||
                          v                                                                             ||
+-----------------------------------------------------------------------------------------+             ||
| THE DETERMINISM CHOKEPOINT (UWG & ISOLATION)                                            |             ||
|-----------------------------------------------------------------------------------------|             ||
| UNIVERSAL WRITE GATEWAY (UWG) [THE PRISON GUARD]                                        |             ||
| - Intercepts ALL File System (FS) & Database (DB) writes.                               |             ||
| - [AST Block] Direct non-UWG writes -> SovereigntyError.                                |             ||
| - Forces all state changes into a strict Diff Transcript.                               |             ||
| - [!] FAILED UWG CHECK => Triggers L2.3 Healing Loop.                                   |             ||
|                                                                                         |             ||
| THE SEMANTIC CLOCK (TIME ISOLATION)                                                     |             ||
| - Wall-clock (`time.time()`, `datetime.now()`) is FORBIDDEN.                            |             ||
| - `SemanticClock` acts as the SOLE temporal authority (Advances via exec steps).        |             ||
|                                                                                         |             ||
| NETWORK & I/O INTERCEPTOR                                                               |             ||
| - Captures external API responses into an immutable ledger.                             |             ||
| - explicitly seeds all pseudo-random number generators.                                 |             ||
| - [!] Un-transcripted network calls -> HARD FAIL.                                       |             ||
+-----------------------------------------------------------------------------------------+             ||
                          | (Passes strictly governed State Diffs & Transcripts)                        ||
                          v                                                                             ||
+-----------------------------------------------------------------------------------------+             ||
| [P4: SYNTHESIS & EGRESS] -> STRICT REPLAY EXECUTION                                     |============>|| (Emits ExecutionTrace up to L4/L6)
|-----------------------------------------------------------------------------------------|             ||
| - Aggregates transcripted I/O & state diffs.                                            |             ||
| - Generates exactly ONE stable artifact: [W<n>-DETERMINISM-DIGEST]                      |             ||
|   (provider + model + gateway + sem_clock).                                             |             ||
|                                                                                         |             ||
| STRICT REPLAY EXECUTION (replay_mode = True)                                            |             ||
| 1. Re-runs execution using identical payload.                                           |             ||
| 2. UWG strictly simulates diffs (No real I/O).                                          |             ||
| 3. Compares Run 2 Digest vs Run 1 Digest.                                               |             ||
|    - Match  => mathematically proven zero-loss.                                         |             ||
|    - Mismatch => FAIL (Multiple competing digests).                                     |             ||
+-----------------------------------------------------------------------------------------+             ||
======================================================================================================================================================================
  CORE DETERMINISM & REPLAY DATA CONTRACTS
======================================================================================================================================================================
| [2] SandboxEnvelope     : [InstructionPacket, ToolBudget(compute_ms, memory_mb, stdout_bytes)] -> Signature verified at L2 boundary before ANY I/O.                |
| [UWG] Sovereignty Proof : Any un-transcripted network call -> HARD FAIL. Transcript must fully reconstruct all side-effects.                                       |
| [4] ExecutionTrace      : [trace_id, plan_hash, actor, target, diff, policy_hash, timestamp, prev_hash(chaining), replay_key(trace_id+plan_hash+transcript_hash)]  |
| [DIGEST] Proof Standard : W<n>-DETERMINISM-DIGEST -> MUST include [provider_id + model_id + gateway_version + semantic_clock_vector]. MUST print exactly once.     |
======================================================================================================================================================================
