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
| - SemanticClockValidator: Validates semantic clock consistency across replay runs       |             ||
|                                                                                         |             ||
| NETWORK & I/O INTERCEPTOR                                                               |             ||
| - Captures external API responses into an immutable ledger.                             |             ||
| - explicitly seeds all pseudo-random number generators.                                 |             ||
| - [!] Un-transcripted network calls -> HARD FAIL.                                       |             ||
|                                                                                         |             ||
| REPLAY GUARD (Context Manager)                                                          |             ||
| - Patches non-deterministic stdlib surfaces during replay (time, random, uuid)          |             ||
| - Ensures deterministic execution by intercepting stdlib calls                          |             ||
| - Context manager: with ReplayGuard(replay_envelope): ...                               |             ||
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
| DIGEST CALCULATION & EMISSION:                                                          |             ||
| - DigestCalculator: Computes SHA-256 digest from replay envelope components             |             ||
| - DeterminismDigestEmitter: Ensures exactly ONE digest per execution (singleton guard)  |             ||
| - LLM Replay Strategy: Captures raw LLM I/O for replay verification                     |             ||
| - Deterministic Replay Engine: Executes replay cases and computes replay digest         |             ||
|                                                                                         |             ||
| STRICT REPLAY EXECUTION (replay_mode = True)                                            |             ||
| 1. Re-runs execution using identical payload.                                           |             ||
| 2. UWG strictly simulates diffs (No real I/O).                                          |             ||
| 3. ReplayGuard patches stdlib non-determinism.                                          |             ||
| 4. Compares Run 2 Digest vs Run 1 Digest.                                               |             ||
|    - Match  => mathematically proven zero-loss.                                         |             ||
|    - Mismatch => FAIL (Multiple competing digests).                                     |             ||
+-----------------------------------------------------------------------------------------+             ||
======================================================================================================================================================================
  DETERMINISM PROOF STANDARD (HARDENED) — DIGEST FORMULAS
======================================================================================================================================================================
+-----------------------------------------------------------------------------------------+
| P5-DETERMINISM-DIGEST: compute_p5_determinism_digest()                                  |
|-----------------------------------------------------------------------------------------|
| Inputs:                                                                                 |
|   * registry_digest()          — from AGENT_REGISTRY                                    |
|   * allowed_models_map         — agent_id -> sorted models tuple                        |
|   * policy_versions            — agent_id -> version string                             |
|   * gateway_hash               — SHA-256 of SovereignLLMGateway.py                      |
+-----------------------------------------------------------------------------------------+
+-----------------------------------------------------------------------------------------+
| W6-DETERMINISM-DIGEST: compute_w6_determinism_digest()                                  |
|-----------------------------------------------------------------------------------------|
| Inputs:                                                                                 |
|   * agent_2x2_inventory.json   — ssot_registry + apps_lic + apps_rg                     |
|   * audited_paths              — SovereignLLMGateway, healing_tier_router,              |
|                                  agent_registry                                         |
+-----------------------------------------------------------------------------------------+
+-----------------------------------------------------------------------------------------+
| HARDEN-MERGE-LOCKDOWN-DIGEST: compute_lockdown_determinism_digest()                     |
|-----------------------------------------------------------------------------------------|
| Inputs:                                                                                 |
|   * registry_hash                                                                       |
|   * tool_inventory_hash                                                                 |
|   * healer_registry_hash                                                                |
|   * allowlists_hash                                                                     |
|   * routing_ruleset_hash                                                                |
|   * embedding_pack_hash                                                                 |
|   * meta_learning_config_hash                                                           |
+-----------------------------------------------------------------------------------------+

======================================================================================================================================================================
  CORE DETERMINISM & REPLAY ENFORCEMENT CONTRACTS (THE LIBRARIAN MODEL)
======================================================================================================================================================================
+--------------------------------------+  +--------------------------------------+
| 🎯 DETERMINISM SURFACE (SSOT)        |  | 🎲 ENTROPY & IDENTITY CONTRACT       |
|--------------------------------------|  |--------------------------------------|
| { time, entropy, identity, I/O,      |  | FORBIDDEN (runtime):                 |
|   state reads }                      |  | - random.*, numpy.random, uuid4      |
|                                      |  | - os.urandom, secrets.*, wall clock  |
|--------------------------------------|  | REQUIRED:                            |
| LIBRARY ANALOGY (ENHANCED):          |  | - seed = hash(trace_id + sem_clock)  |
| These are the only ways uncertainty  |  | - uuid5(namespace, deterministic_in) |
| enters the library: clocks, random   |  | - OR L0-issued trace-bound IDs       |
| choices, identity assignment,        |  | INVARIANT:                           |
| outside requests, and reading from   |  | No untracked entropy enters L2       |
| shelves. Control these surfaces and  |  |--------------------------------------|
| the entire system becomes perfectly  |  | LIBRARY ANALOGY (ENHANCED):          |
| reproducible.                        |  | The Restoration Lab forbids dice,    |
|                                      |  | coin flips, or “grab a random book.” |
|                                      |  | Every book request must reference a  |
|                                      |  | catalog number issued at the front   |
|                                      |  | desk (L0) or derived from the        |
|                                      |  | official index system. If a restorer |
|                                      |  | improvises, the work cannot be       |
|                                      |  | reconstructed and is rejected.       |
+--------------------------------------+  +--------------------------------------+

+--------------------------------------+  +--------------------------------------+
| 🌐 NETWORK TRANSCRIPT CONTRACT       |  | 🔁 REPLAY MODE PROPAGATION           |
|--------------------------------------|  |--------------------------------------|
| REQUIRED CAPTURE:                    |  | L0: inject {replay_flag, replay_key} |
| - request_hash                       |  | → L3: propagate unchanged            |
| - endpoint + method                  |  | → L5: enforce replay constraints     |
| - headers (sanitized)                |  | → L2: switch execution mode          |
| - payload_hash                       |  | MODE SWITCH EFFECTS:                 |
| - response_hash                      |  | - disable external I/O               |
| - status_code + latency              |  | - freeze entropy                     |
| REPLAY MODE:                         |  | - bind SemanticClock                 |
| - NO live calls                      |  | INVARIANT:                           |
| - MUST stub from transcript          |  | replay = system-wide state           |
| HARD FAIL: untranscripted I/O        |  |--------------------------------------|
|--------------------------------------|  | LIBRARY ANALOGY (ENHANCED):          |
| LIBRARY ANALOGY (ENHANCED):          |  | The front desk stamps the request as |
| Every external archive request must  |  | “ARCHIVAL REPLAY MODE.” Every staff  |
| be photocopied and logged before a   |  | member must follow that stamp. No    |
| runner leaves the building. During   |  | new books may be fetched, no new     |
| replay, no runner is sent outside.   |  | decisions made. The entire workflow  |
| The librarian replays the exact      |  | becomes a strict reenactment of a    |
| photocopy instead of re-fetching.    |  | previously logged circulation path.  |
| Missing paperwork means the trip     |  |                                      |
| never officially happened.           |  |                                      |
+--------------------------------------+  +--------------------------------------+

+--------------------------------------+  +--------------------------------------+
| ⏱️ SEMANTIC CLOCK COORDINATION       |  | 🔐 CREDENTIAL DETERMINISM BOUNDARY   |
|--------------------------------------|  |--------------------------------------|
| SOURCE: L4                           |  | NOT part of determinism digest       |
| INJECTED: L0                         |  | NOT stored in replay envelope        |
| FROZEN: L2 sandbox                   |  | REQUIRED:                            |
| VERIFIED: L6                         |  | - credential_id_hash logged          |
| INVARIANT:                           |  | - usage transcripted                 |
| single temporal authority            |  | INVARIANT:                           |
|--------------------------------------|  | same scope → same behavior           |
| LIBRARY ANALOGY (ENHANCED):          |  |--------------------------------------|
| The library runs on a single master  |  | LIBRARY ANALOGY (ENHANCED):          |
| clock in the control room. All desks |  | Staff keys (credentials) open doors  |
| must reference that clock. No        |  | but are never copied into the public |
| personal watches allowed. Every      |  | record. Instead, the ledger records  |
| receipt and action is timestamped    |  | which authorized staff member used   |
| against this single authoritative    |  | which key. Replay assumes the same   |
| time source.                         |  | clearance level, not the physical    |
|                                      |  | key itself.                          |
+--------------------------------------+  +--------------------------------------+

+--------------------------------------+  +--------------------------------------+
| 🔑 REPLAY KEY vs DIGEST              |  | ❌ DIGEST MISMATCH HANDLING          |
|--------------------------------------|  |--------------------------------------|
| ReplayKey: entry point identifier    |  | DETECT: L6 or ReplayValidator        |
| DeterminismDigest: full fingerprint  |  | CLASSIFY ROOT CAUSE:                 |
| RELATION:                            |  | - time | entropy | network | state   |
| 1 ReplayKey → N Digests              |  | ACTION:                              |
|--------------------------------------|  | - mark NON-REPLAYABLE                |
| LIBRARY ANALOGY (ENHANCED):          |  | - emit violation                     |
| The ReplayKey is the patron’s ticket |  | - block meta-learning ingestion      |
| number at entry. The Determinism     |  |--------------------------------------|
| Digests are the stamped receipts at  |  | LIBRARY ANALOGY (ENHANCED):          |
| every desk visited. One ticket       |  | If the checkout receipts do not      |
| produces many stamped checkpoints    |  | match the security footage and       |
| across the library journey.          |  | ledger, the entire session is        |
|                                      |  | flagged as corrupted. The record is  |
|                                      |  | quarantined and cannot be used to    |
|                                      |  | update library policy or training.   |
+--------------------------------------+  +--------------------------------------+
======================================================================================================================================================================