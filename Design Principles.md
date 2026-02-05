This is the **Agentic Process v14 (PNG) Design Manifesto: Expanded Technical Specification**.

This document serves as the immutable "Rule of Law" for the system architecture. It defines the constraints, data structures, and execution logic with extreme precision to ensure the system remains Blocking, Machine-Readable, and Statically Safe.

---

# PART 1: The Core Layers (L0 - L6)

## L0: Contextual Router & Policy Enforcer (The Gateway)

**Role:** The immutable, zero-trust entry point for all ingress signals.
**Status:** Blocking // Stateless

* **Policy Config Hash Verification (Fire Destining):**
* **Mechanism:** Every incoming payload must include a header `X-Policy-Signature`. This is a SHA-256 hash of the currently active configuration state.
* **Logic:**
```python
if payload.hash != system.current_policy_hash:
    raise PolicyMismatchError("Configuration Drift Detected - Request Dropped")

```


* **Destining:** Requests are routed to specific processing lanes ("Fire Destining") based on signature validation. Mismatches are routed immediately to the *Audit Log* as a security event, bypassing all processing.


* **Strict Routing Paths:**
* **READ Operations:** Labeled `Safe-Idempotent`. Bypasses L5 Guardian checks to optimize latency. Routed directly to *L1 Architect*.
* **WRITE Operations:** Labeled `State-Mutating`. Must carry a `Pending-Validation` flag. Mandatory routing through *L5 Guardian* before and after execution.


* **Typed Trace Event Emission:**
* **TraceID Schema:** `v14-[Timestamp]-[IngressPath]-[RankScore]-[UUID]`
* **Persistence:** This ID is immutable. It is injected into every log, metric, and temporary file associated with the request. Loss of TraceID results in an immediate `zombie_process_kill`.



## L1: Advanced Cognitive Engine (The Architect)

**Role:** The reasoning core. Plans, strategizes, and structures data. DOES NOT modify external state.
**Status:** Non-Blocking (Async) // Deterministic

* **Generation (LLM-eration):**
* **Constraint:** Reasoning execution is bounded to "Domain Specific" contexts defined in the `manifest.json`.
* **System Prompt Injection:** A hard-coded, read-only block of 200 tokens is injected at the start of every context window. This block explicitly disables "chat," "roleplay," or "general assistance" behaviors.


* **Episodic Memory Query (Pre-Plan):**
* **Vector Search:** Before token generation, the engine executes a k-Nearest Neighbors (k-NN) search against the *L4 Knowledge System*.
* **Retrieval Logic:** Retrieve Top-3 "Success" trajectories and Top-3 "Failure" trajectories relevant to the current intent.
* **Integration:** These trajectories are appended to the context window as "Few-Shot constraints."


* **Automatic Prompt Augmentation:**
* **MRO (Method Resolution Order):** Prompts are assembled linearly: `System_Base` -> `Security_Overlays` -> `Retrieved_Context` -> `User_Intent`.
* **Fact Acts:** Dynamic injection of verified facts. If the plan involves "Database X," the schema for "Database X" is retrieved and locked into the prompt before generation begins.



## L2: Symmetric Validator-Healer Pipe (The Surgeon)

**Role:** The execution pipeline. Responsible for applying changes to the environment.
**Status:** Blocking // Atomic

* **Strict Order of Operations (The Pipeline):**
1. **Schema Validation:** Does the request match the JSON definition?
2. **Hash Verification:** Is the target file unchanged since the last read?
3. **Rollback Snapshot:** Create a temporary `.bak` of the target state.
4. **Incident Creation:** Open a tracking ticket in the *Audit Log*.
5. **Circuit Breaker:** Check *L5 Budget* and *Error Rates*.
6. **AST Deserialize:** Convert code strings to Abstract Syntax Trees.
7. **Transform:** Apply the change to the AST.
8. **Check:** Run linting/compilation on the new AST.
9. **Commit:** Write to disk.


* **Atomic Execution (ACID Compliance):**
* The pipe operates as a single transaction. If step 8 fails, the system reverts to step 3 instantly. No partial files are ever written to the active directory.


* **Side-Effect Registry:**
* **Virtual Buffer:** All intended file system touches (`open`, `write`, `delete`) are registered in an in-memory ledger first.
* **Conflict Detection:** The registry checks for "Double Writes" or "Race Conditions" within the current cycle. If two nodes attempt to touch the same file, the cycle is aborted.



## L3: Human Review Gate (The Judiciary)

**Role:** Final approval authority for high-risk changes (defined by Risk Score > Threshold).
**Status:** Blocking // Manual

* **Approval Queue Artifact:**
* **Digital Signature:** The output is a cryptographic object containing: `Reviewer_Public_Key` + `Diff_Hash` + `Timestamp`.
* **Compliance:** A simple "Yes" in chat is ignored. The system requires the signed artifact to proceed to the *L2 Commit* phase.


* **Diff-First Interface:**
* **Visual constraint:** The UI forces the display of the `diff` (lines added/removed) as the primary view. Contextual explanation is secondary. The "Approve" button remains disabled until the user has scrolled to the bottom of the diff.


* **Escalation Protocol:**
* **Timeout:** If a request sits in queue > 24 hours, it auto-rejects.
* **Rejection:** Triggers the *Exponential Backoff* arrow (see Part 3).



## L4: Knowledge System (The Vault)

**Role:** Long-term storage of semantic facts and episodic experience.
**Status:** Passive // Persistent

* **Ontology Management:**
* **Strict Schema:** Data cannot enter the Semantic Memory without a valid RDF (Resource Description Framework) triplet structure `(Subject, Predicate, Object)`. Unstructured blobs are rejected.


* **Experience Replay & Vectorization:**
* **Cycle Archival:** At `process_end`, the `TraceID`, `Inputs`, `Plan`, and `Result` are serialized into a vector embedding.
* **Anti-Pattern Detection:** If the result was `FAILURE`, the vector is tagged `negative_exemplar`. Future queries physically repel this vector during similarity search.


* **Embedding Services:**
* **Dirty Flags:** If the underlying model (e.g., text-embedding-3) is updated, all embeddings are marked `dirty`. A background cron job re-indexes them. Stale embeddings are never served to *L1*.



## L5: Guardian (Validation Gate)

**Role:** The static analysis firewall and safety interlock.
**Status:** Blocking // Deterministic

* **Emits Signed Artifact:**
* **Token Generation:** Generates a JWT-like token with specific claims: `Erit` (Write Permission), `Commit` (Execute Permission), `Result` (Read Permission), or `Seplature` (Process Termination).
* **Verification:** L2 cannot execute without a valid `Commit` token from L5.


* **MRO Verification (Dependency Safety):**
* **Cycle Detection:** Scans the dependency graph of the proposed code. If `A imports B` and `B imports A`, the Guardian throws a `CircularDependencyException` and blocks the write.
* **No Adapturs:** Enforces strict typing. Implicit type conversions ("adapters") are forbidden in critical paths.


* **Left-Side Safety (Fail-Closed):**
* **Default State:** `BLOCK`.
* **Logic:** `if guardian_status != "ONLINE_AND_HEALTHY": return BLOCK_ALL`. If the Guardian service crashes, the entire Agentic Process freezes to prevent unvalidated actions.



## L5: Budget Guard (The Comptroller)

**Role:** Resource governance and cost control.
**Status:** Blocking

* **Pre-Flight Check:**
* **Token Calculation:** Estimates input + output tokens *before* sending to the LLM API.
* **Equation:** `Projected_Cost = (Input_Tokens * Price_In) + (Max_Output_Tokens * Price_Out)`.


* **Hard Limits:**
* **Cap Enforcement:** `if (Daily_Spend + Projected_Cost) > Daily_Cap: return 429_Too_Many_Requests`.
* **Local Rejection:** Rejection happens locally, incurring zero API costs.



## L6: Event & Anomaly Detection Layer (The Watchtower)

**Role:** Signal processing, correlation, and noise reduction.
**Status:** Async // Observer

* **Signal Correlation:**
* **Triangulation:** A valid "Anomaly" requires triangulation.
* Log: "Error 500"
* Metric: "CPU Spike > 90%"
* Trace: "Latency > 2s"


* **Classification:** If only 1 or 2 sources report, it is classified as a "Warning Event." If all 3 correlate, it is an "Anomaly."


* **Deduplication (The 1-Second Window):**
* **Hashing:** Incoming alerts are hashed by `(Source + ErrorMessage)`.
* **Aggregation:** Identical hashes arriving within a 1-second window are aggregated into a single payload: `{ Error: "Timeout", Count: 1450 }`. The Router processes this as one signal.



---

# PART 2: Memory & Observability Systems

## Working Memory (Unified Deterministic Time Source)

**Role:** Shared state for the active execution cycle.

* **Unified Time:** Uses a logical clock (Lamport Timestamps) rather than wall-clock time to ensure events in distributed modules are ordered causally, preventing race conditions.
* **SurgicalManifest:** The JSON object `current_operation.json` is locked. It contains the `node_list` (files to touch) and `schema_varifest` (variables involved). This is the **Single Source of Truth**.
* **Taint Tracking:** Every variable is tagged with a `taint_bit`. If a variable is derived from an unvalidated External System (L4), the `taint_bit` is 1. The L5 Guardian rejects any code where `taint_bit == 1` reaches a critical function (e.g., `exec()`).

## Audit Log (Evidence-Based Traceability)

**Role:** Immutable legal record.

* **Write-Only (WORM):** Implemented on WORM (Write Once Read Many) compliant storage. Deletion is physically impossible until retention expiry.
* **Cryptographic Chain:** Each log entry contains the hash of the *previous* log entry. Any tampering breaks the chain (Blockchain-style integrity).
* **Full Context:** Must store the `Policy Hash` active at the time of execution.

## Metrics Dashboard

**Role:** Real-time visibility.

* **Four Golden Signals:**
1. **Success Rate:** (Successful L2 Commits / Total Requests).
2. **MTTR:** Mean Time To Recovery (Time from L6 Anomaly to L2 Healed State).
3. **Cost:** Cumulative token spend per TraceID.
4. **HIR (Human Intervention Rate):** % of flows routed to L3.


* **Feedback Loop:** Metrics are exposed via API. The L1 Architect consumes `Success Rate` to adjust its "Confidence Threshold" dynamically.

---

# PART 3: The "Arrow" Manifestos (Transport Layer)

## Flow: Fix Rejected (Retry up to N)

**Type:** Error/Rejection Path (Red Dashed Arrow)

* **Exponential Backoff:**
* **Formula:** `Wait_Time = Base_Interval * (2 ^ Attempt_Count)`.
* **Jitter:** A random milliseconds jitter is added to prevent "thundering herd" problems.


* **Max Attempt Circuit Breaker:**
* **Threshold:** `MAX_RETRIES = 3`.
* **Action:** On the 4th failure, the loop breaks. The TraceID is tagged `IRRECOVERABLE` and routed to the L3 Human Gate. Infinite loops are mathematically impossible.



## Flow: Simulated & Tested Fix

**Type:** Conditional Flow (Blue Dashed Arrow)

* **Sandbox Verification:**
* **Isolation:** The generated code is executed in an ephemeral Docker container with no network access (unless explicitly allow-listed).
* **State Reset:** The container is destroyed immediately after the test.


* **Determinism Check:**
* **Double-Run:** The simulation runs the fix twice.
* **Requirement:** `Output_Run_1 == Output_Run_2`. If outputs differ (flaky code), the fix is rejected.



## Flow: Policy Update Mechanism

**Type:** Feedback Loop (Purple Arrow)

* **Performance-Driven Tuning:**
* **Trigger:** If `L6 Anomaly Rate > 5%`, a policy update signal is sent to L0.
* **Action:** The system automatically tightens constraints (e.g., lowers temperature, increases review thresholds).


* **Hot-Reload Safety:**
* **Atomic Swap:** The new policy configuration is loaded into memory in parallel. The pointer to the config is swapped in a single CPU instruction.



## Flow: Auto-Rollback

**Type:** Error Path (Bottom Right Arrow)

* **Instant Revert:**
* **Trigger:** L6 detects an anomaly *immediately* following an L2 Commit.
* **Mechanism:** `git checkout [Pre-Fix-Hash]`. This bypasses L3 and L5 for emergency stabilization.


* **Blacklist Generation:**
* **Episodic Memory Update:** The strategy hash used for the failed fix is added to a `Blacklist` vector. L1 is forbidden from generating a semantically similar plan for 24 hours.



---

# PART 4: Side Components & External Constraints

## AI Safety Quadimars (Right Sidebar)

**Role:** Global, non-negotiable safety constraints.

* **Constraint Supremacy:** These rules reside in the "hypervisor" layer. They override *all* L1 reasoning and L3 human inputs.
* **Hard-Coded Filters:**
* **PII Stripper:** Regex filters detect Social Security numbers/Emails.
* **Content Policy:** Pre-computation check for prohibited topics (e.g., political generation, malware creation).
* **Structure:** If a Quadimar is triggered, the output is replaced with `[REDACTED_SAFETY_VIOLATION]`.

