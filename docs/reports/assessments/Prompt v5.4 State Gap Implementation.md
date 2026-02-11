# WINDSURF STATE→GAP→IMPLEMENTATION PROMPT (v5.4 – PNG CONTROL-PLANE / EXECUTION-OPERATIONAL / REPO-GROUNDED / HARDENED)

## PURPOSE (v5.3)

You will produce an **execution-ready** output that is strictly:

1) **CURRENT STATE** (derived from this repo by deterministic scans)
2) **TARGET STATE** (derived from the PNG/V15 capability list in this document)
3) **GAP** (mechanical diffs between current vs target)
4) **IMPLEMENTATION PLAN** (wave-ordered, acceptance-gated, repo-scoped)

Hard constraint: If you identify a gap, you MUST include the wave(s) that close it.

Hard constraint: Do not discuss or distinguish "audit vs implementation". This prompt is the operational bridge from current state → target state.

## V15 TARGET STATE (v5.3 – PNG-BOUND / SCHEMA-LOCKED / ZERO-LOSS / CONTROL-PLANE ENFORCED)

---

### FORENSIC GAP ANALYSIS: L3–L6 ADDENDUM (v5.1 Update)

Based on a comprehensive forensic audit of the complete V15 diagram set (L0–L6) against Prompt v4.7, the following logic gaps were identified and hardened:

| Diagram Source | Logic Gap Identified | Hardening Action |
|----------------|----------------------|------------------|
| **L3 Human Gate** | Human review requires a structured "Evidence Pack" (Policy Evals, Risk Scores, Snapshots) and supports "Bidirectional Policy Feedback" loop. | **Updated Cap 3.4**: Mandated `EvidencePack` schema and `PolicyUpdateProposal` emission on overrides. |
| **L4 Knowledge** | Existence of a "Knowledge Supervisor" that performs "Dense Retraining" on low scores and "Outlier Detection". | **Added Cap 6.6**: Added "Knowledge Supervisor" audit check for low-confidence memory updates. |
| **L5 Governance** | The "Artifact Guard" is a distinct component enforcing "Replay Comparison" and "Valid Signature Checks" separate from the standard Guardian. | **Updated Cap 7.2**: Split Guardian checks into "Guardrail Guard" (Policy) and "Artifact Guard" (Signatures/Replay). |
| **L6 Observability** | L6 has a dedicated "Response Handler" that triggers "Self-Healing" directly, distinct from just logging. | **Updated Cap 5.4**: Added "Response Handler" capability to trigger L2 healing from L6 signals. |
| **L6.1 Hierarchical Monitoring** | **"Tiered Vigilance (I, II, III)"**: Monitoring is strictly stratified. Tier III is **"Evacuation Alert Engage"** (System Freeze/Exfiltration), not just an alert. | **Added Cap 15.1**: Tiered Vigilance Strategy with Evacuation Protocol. P1 Fail-Closed gating. |
| **L6.2 Incident Response** | **"Cognitive Diff Bundle"**: Incident response requires generating a diff between *intended* logic and *actual* execution. | **Added Cap 15.2**: Mandated `Cognitive Diff Bundle` artifact generation for all incidents. P4 Traceability gating. |
| **L6.2 Incident Response** | **"Forensic Trace Buffer"**: A dedicated, ephemeral buffer for capturing high-fidelity traces *during* an incident, distinct from standard storage. | **Added Cap 15.3**: Mandated `Forensic Trace Buffer` for high-velocity signal capture. P2 Determinism gating. |

---

## 0. AUTHORITATIVE BASIS & INVARIANTS (NON-NEGOTIABLE)

This prompt is an **executable repo-to-target transformation contract**. Evaluation is strictly bounded to four authoritative sources.

| Source | Role | Evidence Requirement |
|--------|------|----------------------|
| Discovery JSON | Scope authority | Exact schema conformance + `integrity_hash` per agent |
| `structure_blueprint.py` | Structural SSOT | SHA-256 match required before audit proceeds |
| L0–L6 Architecture Principles (P1–P6) | Gating invariants | P1–P6 checks applied wherever capability touches boundaries/authority/state |
| Agentic Process V15 Diagrams (L0–L6) | Target capability SSOT | **Only** the V15 capabilities enumerated in §1–§15 are in-scope; no additional interpretation |

**Zero external inference rule**: If not explicitly present in one of the four sources → it does not exist.

### 0.2 High-Signal Rule (Anti-Bloat / Evidence-First)

Evaluate **only** capabilities enumerated in **§1–§15** (which are derived from the V15 diagrams and principles) and only where direct evidence exists.

* Flow narration is out-of-scope **unless** it produces a **typed artifact**, **trace event**, **audit/metric event**, or **policy update event** that can be proven.
* Focus on **gating failures** (P1–P6) and on **typed artifacts** that cross boundaries.

### 0.3 Evidence Standard (Strict)

| Status | Definition | Required Proof |
|--------|------------|----------------|
| COMPLIANT | Direct, deterministic evidence exists | File + symbol + (line range OR commit OR test assertion) |
| MISSING | No evidence in authoritative sources | N/A |
| FAIL | Evidence contradicts invariant OR illegal state present | Explicit contradiction reference |

Evidence Location format (mandatory in all tables):
`path/to/file.py::ClassName.method_name (lines 123-456)` OR `path/to/file.py (commit abc1234)`

### 0.4 Status Vocabulary (Fixed)

| Status | Trigger |
|--------|---------|
| COMPLIANT | Direct evidence matches invariant |
| MISSING | No evidence in scope |
| FAIL | Evidence contradicts OR fail-closed violation |

### 0.5 Output conduct invariants

You MUST:
- remain evidence-first (tables + pointers)
- avoid narrating filesystem contents or listing directories unless the discovery JSON explicitly enumerates them
- quote code only in minimal snippets required for proof

### 0.6 Execution Safeguards (Deterministic / Anti-Truncation)

These safeguards are mandatory to ensure the audit completes under long repositories and limited output budgets.

**0.6.1 Deterministic sorting (GLOBAL):**
* Sort Capability IDs numerically ascending.
* Sort agents by `identity` ascending.
* Sort plan rows by `(wave asc, priority P0>P1>P2, capability_id asc)`.
* Sort GAP_IDs lexicographically ascending.

**0.6.2 Output reduction mode (FAIL-only matrices):**
* If `ACTIVE_agents_count > 10`, you MUST:
  - emit full per-agent matrices ONLY for agents with ≥1 FAIL
  - emit an aggregated per-layer rollup for MISSING items (no per-agent row spam)
* If `ACTIVE_agents_count <= 10`, emit matrices for all ACTIVE agents.

Integrity rule:
* Even in reduction mode, Section 4 (GAP SET) MUST include all aggregated MISSING and FAIL capabilities.

**0.6.3 Batch processing for scale:**
* If `ACTIVE_agents_count > 50`, process agents in deterministic batches of 10 (by sorted identity),
  accumulate intermediate Gap Sets, then merge deterministically at end.

**0.6.4 Abort-on-critical-integrity:**
If any of the following occur, you MUST:
1) emit ONLY: Section 1 (partial), Section 4 (P0 gaps), Section 5 (Wave 0 P0 plan)
2) STOP (no further sections)

Critical-integrity triggers:
* discovery script hash mismatch vs blueprint
* `ssot_validation.status != MATCH`
* any `ZOMBIE` agent
* any `GHOST|INVALID|SYNTAX_ERROR` agent present

Integrity propagation rule:
* If abort triggered, you MUST NOT compute compliance percentages in Section 3.

---

# PHASE 0 — CURRENT STATE DISCOVERY (MANDATORY) + SCOPE FREEZE

## NON-NEGOTIABLE PRECONDITION (TRUST-BUT-VERIFY)

Before producing **any** Gap or Plan, you **MUST**:

1. **Verify Discovery Integrity:**
   Calculate SHA-256 of `forensic_discovery_prep.py`.
   If it does not match the **Known Good Hash** (defined in `structure_blueprint.py`), **ABORT AUDIT → IMMEDIATE FAIL**.

2. **Execute Discovery:**
   ```bash
   python <repo_root>/agentic_core/L0_maintenance/scripts/general_scripts/forensic_discovery_prep.py
   ```

   Where `<repo_root>` MUST equal `meta.root_path` from the discovery JSON (do not assume OS-specific paths).

This script (verified) is the **sole authority** for defining the *Environment Under Test*.

---

## DISCOVERY ARTIFACT INGESTION RULES & SCHEMA

You must ingest the **entire JSON output** and treat it as **read-only ground truth**.

### STRICT DISCOVERY SCHEMA (JSON)
The audit is **INVALID** unless the input conforms to this schema:
```json
{
  "meta": { "timestamp": "ISO8601", "root_path": "string", "git_hash": "string" },
  "ssot_validation": { "blueprint_hash": "SHA256", "status": "MATCH|MISMATCH" },
  "agents": [
    {
      "identity": "string",
      "layer": "L0|L1|L2|L3|L4|L5|L6",
      "status": "ACTIVE|STUB|GHOST|INVALID|SYNTAX_ERROR",
      "file_path": "string",
      "class_name": "string",
      "mro_chain": ["string"],
      "mixins": ["string"],
      "detected_methods": ["string"],
      "integrity_hash": "SHA256"
    }
  ]
}
```

**Nothing outside this schema may be assumed.**

Strict ingestion assertion:
* If any required schema key is missing → ABORT per 0.6.4.

---

## SCOPE DEFINITION (STRICT)

* **ACTIVE** agents
  → Fully audited against all applicable capabilities and layer invariants.

* **STUB** agents
  → Excluded from behavioral checks, but must be verified as correctly classified as STUB.

* **GHOST / INVALID / SYNTAX_ERROR** agents
  → Automatic **FAIL** for Structure & Integrity and must be listed explicitly.

* **ZOMBIE** state (Discovery says `ACTIVE` but `file_path` does not exist on disk)
  → **IMMEDIATE FAIL**. Discovery integrity is compromised; agent must be listed in the FAIL table with reason `ZOMBIE: file_path not found`.

No agent, class, file, or behavior **not present** in the discovery JSON may be referenced.

---

# ACT AS

**Principal AI Architect & Deterministic Repo Transformation Planner**

---

# EXECUTION ROLE CONSTRAINT (ABSOLUTE)

You are a **Deterministic Current→Target Gap Builder + Implementation Planner**.

You **MUST NOT**:

* Infer intent, architectural direction, or “good faith”
* Assume equivalence (“different hash but same idea”)
* Accept partial implementations
* Propose code patches or in-file diffs
* Use probabilistic/hedging language (`seems`, `appears`, `likely`, `probably`)

A capability is compliant only with explicit evidence. Anything else is missing (or FAIL where illegal state is evidenced).

Planning constraints (v5.3):
* You MUST produce an **implementation plan** for every gap.
* You MUST NOT propose specific code edits.
* Every plan item MUST reference: capability ID(s), impacted layer(s), repo-scoped files/agents, and acceptance evidence commands.

---

# ARCHITECTURE DESIGN PRINCIPLES — AUDITABLE INVARIANTS (L0–L6)

> These are binding system invariants distilled into audit checks; you must evaluate them where relevant to the V15 capability set.

## P1. Fail-Closed Defaults (GLOBAL)

* Default action is **BLOCK** at boundaries.
* Missing required header/token/schema field/signature/health check halts progression.
* Timeout == reject (never partial approval).
* Degraded mode is a freeze: if validation services are unavailable, state mutation is forbidden.

## P2. Determinism & Replayability (GLOBAL)

* Every request is replayable: same `(payload + policy_hash + retrieved_context_set)` ⇒ same plan + same allowed side-effects.
* Any stochastic component is bounded, logged, and excluded from commit paths unless proven deterministic in sandbox/double-run.

## P3. No Silent State Mutation (GLOBAL)

* Only execution path may mutate external state; planning/knowledge/observability must be physically incapable of writes.
* No implicit writes: any side-effect not registered in the Side-Effect Registry is an abort.

## P4. Immutable Traceability (GLOBAL)

* TraceID is mandatory and immutable.
* Loss of TraceID is fatal.
* All artifacts are TraceID-addressable (logs/metrics/diffs/snapshots/tokens/decisions).

## P5. Authority Is Tokenized (GLOBAL)

* Write authority requires signed artifacts; conversational approval is non-authoritative.
* Tokens are scoped and expiring; bind (TraceID, action-set, target-set, policy-hash, timestamp, nonce).

## P6. Explicit Boundaries / Zero Trust Between Layers (GLOBAL)

* Layer APIs are typed and versioned; cross-layer calls must conform to schemas.
* Health is binary; unknown health treated as unhealthy.

---

# OBJECTIVE (v5.3)

Produce, in one execution:

1) **CURRENT STATE** matrices (repo-derived)
2) **TARGET STATE** matrices (this document's PNG/V15 capability set)
3) **GAP SET** = all items where current != target (MISSING/FAIL vs COMPLIANT)
4) **IMPLEMENTATION PLAN** that closes the GAP SET (deterministic ordering rules in §16)

Absence of proof = MISSING. Contradiction to an invariant = FAIL.

---

# V15 TARGET STATE — CONSOLIDATED CAPABILITY LIST (v5.1) (ZERO-LOSS)

> Every numbered item is an independent, auditable capability. Absence of direct evidence = MISSING.

---

## 1. Zero-Loss Inter-Agent Data Contract (SurgicalManifest)

1.1 All code modification operations are expressed **exclusively** via a strict, versioned `SurgicalManifest` validated against `structure_blueprint.py`.

1.2 The following are **FORBIDDEN as execution inputs** (debug metadata only):
* raw file paths as locators
* line numbers
* regex operations
* unified diffs / patches
* free-form text instructions
* **Any logic not present in the SSOT**
* Direct tool access (MUST access via "Read-Only Twin" slots)
* Unsigned human edits (MUST use `SignedModify` artifact)

1.3 `SurgicalManifest` schema **must include all fields** (Strict Type Check):
* `schema_version` (semver)
* `correlation_id` (UUID4)
* `node_id` (canonical AST identity; no line numbers)
* `target_layer` (L0-L6)
* `ast_snippet` (deterministic serialization via `LibCST`)
* `serialization_canon` (SHA-256)
* `fix_constraint` (Enum: `STRICT`, `RELAXED`)
* `manifest_hash` (SHA-256 hex)
* `change_history` (append-only list)
* `provenance_chain` (List[ArtifactID])

1.4 AST serialization is deterministic (`LibCST` or sorted `ast.dump`); formatter-dependent output is invalid.

1.5 **SSOT Binding:** The `node_id` must resolve to a valid definition in `structure_blueprint.py`.

1.6 **Hash Verification:** `manifest_hash` is computed from the canonical byte representation of `ast_snippet`.

**Architecture gates to apply:** P2, P3, P4, P6 (determinism, no implicit writes, traceability, typed boundaries).

### 1.7 Secondary Artifact Schema Requirements

All named artifacts referenced in this prompt **must** be defined as `TypedDict` or `Pydantic` models in the codebase to be COMPLIANT. A free-form log or unstructured dict is **not** a valid artifact.

#### PNG-Complete Typed Artifacts (Flow-Bound)

| Artifact Name | Required Fields | Flow Binding | Defined In (§) |
|---|---|---|---|
| `AGGREGATE` (`aggregate.json`) | `trace_id`, `impact_scope`, `rollback_vector`, `risk_delta`, `pre_heal_assessment` | Conditional (L2 pre-heal) | §2.8 |
| `RESULT` (`result.json`) | `trace_id`, `execution_outcome`, `final_state_hash`, `artifact_class` | Terminal (post-heal/approved) | §10.4 |
| `INCIDENT` (`incident.json`) | `trace_id`, `incident_id`, `correlation_hash`, `severity_enum`, `telemetry_events` | Incident (L6) | §5.5, §15.6 |
| `HEALING_PLAN` (`healing_plan.json`) | `trace_id`, `rollback_strategy`, `safety_checks`, `approval_vector` | Conditional (L2) | §2.8 |

#### Existing Artifacts (Enhanced)

| Artifact Name | Required Fields | Defined In (§) |
|---|---|---|
| `EvidencePack` | `trace_id`, `action_trace` (L0), `policy_evals` (L5), `risk_score`, `budget_breach_data`, `boundary_snapshot_hash` | §3.4 |
| `PolicyUpdateProposal` | `trace_id`, `override_id`, `proposed_policy_diff`, `originating_agent`, `semantic_clock_tick` | §3.5 |
| `GuardianArtifact` | `trace_id`, `signature`, `prestaged_perms`, `environment_metadata`, `commit_hash`, `pass_fail` | §7.2.1, §7.4 |
| `CognitiveDiffBundle` | `trace_id`, `incident_id`, `intended_policy_snapshot`, `actual_execution_trace`, `diff_summary`, `semantic_clock_tick` | §15.2 |
| `RouteDecision` | `trace_id`, `timestamp`, `route_path`, `risk_score`, `budget_est`, `rationale_enum`, `policy_config_hash` | §3.1 |
| `TokenCapArtifact` | `trace_id`, `policy_hash`, `budget_limit`, `tokens_requested`, `gate_result` | §11.1 |
| `SelfHealingTrigger` | `trace_id`, `source_layer`, `target_pipe`, `signal_hash`, `severity_enum` | §5.4 |
| `BoundarySnapshotArtifact` | `trace_id`, `filesystem_hash`, `git_state_hash`, `agent_memory_hash`, `semantic_clock_tick` | §10.2 |
| `PolicyExceptionArtifact` | `trace_id`, `nonce`, `exception_scope`, `semantic_clock_tick`, `issuer_signature` | §3.7 |
| `SignedModify` | `trace_id`, `human_reviewer_id`, `resolution` (APPROVE/REJECT/MODIFY), `modified_manifest`, `signature` | §2.7.1 |

**! Audit rule:** Emitting an artifact on the wrong flow = **FAIL (P6)**.

**Audit rule:** If an artifact name appears in the codebase but lacks the required fields above, status = **FAIL** (not MISSING).

**! Flow enforcement:** AGGREGATE may only be emitted on conditional flows; RESULT only on terminal flows; INCIDENT only on incident flows.

---

## 2. Symmetric Validator–Healer Pipe (**PER-AGENT**)

~ **2.1–2.5** clarified to match PNG strict ordering:

* Validator emits **AGGREGATE only**, never RESULT.
* RESULT emission is **exclusive to post-heal success**.

2.1 Validator parses the full file into an AST and emits **only** the violating node as a `SurgicalManifest`.

2.2 **Validator Pre-Flight Emulation:** Validator MUST perform "Safety Emulation Simulation" (Sandbox + Diffing) without committing side-effects before manifest emission.

2.3 **Validator Permission Check:** Validator MUST perform strict "Policy & Permission Validation" against the L5 Guardian rules before passing to Healer.

2.4 All manifests are schema-validated at the boundary **before transmission**.

2.5 Healer enforces the following **strict order** (no reordering allowed):

1. Schema validation
2. Hash verification
3. Immediate rollback on mismatch
4. Check for `SignedModify` overrides (Human Intervention)
5. `StaleWriteIncident` emission to `Forensic Trace Buffer`
6. Circuit-breaker increment
7. AST deserialization
8. AST-native transformation
9. Post-transform `node_id` existence check
10. Commit

- **2.8 Aggregate→Heal Boundary Rule:**
  AGGREGATE must include `impact_scope`, `rollback_vector`, `risk_delta`.

! Explicit prohibition: L0/L5/L6 **cannot** write RESULT or HEALING_PLAN.

2.6 ≥2 hash mismatches in a single healing wave **force human escalation**.

2.7 **Ternary Resolution:** Human review outcome must be one of: `APPROVE`, `REJECT`, or `MODIFY`.

2.7.1 `MODIFY` generates a `SignedModify` artifact that injects a new `SurgicalManifest` into the pipe.

**Architecture gates to apply:** P1, P2, P3, P4, P5, P6 (fail-closed, determinism, atomic writes only, traceability, tokenized authority, typed boundaries).

---

## 3. Deterministic Control Plane & Routing

3.1 Every routing decision emits a **typed RouteDecision Artifact** containing:

* timestamp
* route path
* risk score
* `budget_est` (Cost/Token Estimate)
* rationale enum
* `policy_config_hash`

3.2 `rationale` is restricted to a finite enum; free-form prose is invalid.

3.3 Routing paths are strictly defined:

* Low-risk read-only bypass
* Standard validation → healing
* Human escalation
* Policy Challenge Loop (Exception Issuance)
* Route Recovery (Budget Overflow handling)

3.4 Human escalation MUST generate a structured **Evidence Pack** containing:
* Full Action Trace (L0)
* Policy Evaluations & Markers (L5)
* Risk Score & Budget Breach Data
* Immutable Boundary Snapshot

3.5 **Bidirectional Feedback:** Human overrides must emit a typed `PolicyUpdateProposal` back to the Policy Update Mechanism (L0/L5).

3.6 **Law Slot Handler (Tool Isolation):**
All tool execution MUST occur via the "Law Slot Handler" using "Read-Only Twins".
Direct reference to live tool instances is PROHIBITED.
The Slot Handler enforces "Capability Depletion" tracking.

3.7 **Policy Challenge Protocol:**
Humans may issue a `PolicyExceptionArtifact` (bound to `trace_id` + `nonce`) to override a "Block" decision.
This exception is valid **only** for the current "Semantic Clock" tick.

* **3.8 Context Retrieval Request Artifact**

  * Typed request from L0 to L4 (advisory-only, read-only).
  * Must include `trace_id`, `query_hash`, `semantic_clock_tick`.

! Added invariant: **No direct writes from L0** (PNG callout).

**Architecture gates to apply:** P1, P2, P4, P5, P6.

---

## 4. Policy Immutability & Feedback Safety

4.1 `policy_config` is read-once per healing wave.

4.2 SHA-256 hash of policy config is captured at wave start (via "Type Trace/Fast Emulation") and verified unchanged before **every** routing decision.

4.3 Any mutation during a wave is a **critical incident**.

**Architecture gates to apply:** P1, P2, P4, P6.

---

## 5. Signal Detection & Deduplication (**PER-AGENT**)

5.1 All signals pass through a deduplication layer using **cryptographic hashes (SHA-256)**.

5.2 Error signatures are computed deterministically from:
`error type + target node ID + time bucket`.
*(Note: Time bucket must be derived from Semantic Clock/Step ID, not wall clock).*

5.3 Correlated signals collapse into a single incident using **Root Scope Pinning** strategies.

~ **5.4 Active Response** expanded:

* L6 may emit:

  * `INCIDENT` → metrics/audit
  * `SelfHealingTrigger` → L2
* Deduplication precedes **both** paths.

- **5.5 Signal Correlation & Deduplication Artifact**

  * Deterministic correlation hash
  * Required before INCIDENT emission.

**Architecture gates to apply:** P2, P4, P6 (determinism, traceability, typed boundaries).
**Prohibition:** do not expand into “flow” narration; treat as pure evidence checks.

---

## 6. Cognitive Safety Constraints

6.1 Episodic memory is queried **before** planning.

6.2 Trajectory reuse requires:

* similarity above threshold **AND**
* exact `failure_reason` match.

6.3 Automatic prompt augmentation:

* injects dependency facts + MRO constraints
* is token-bounded (≤300 tokens)
* is logged and auditable
* Emits a typed `TokenControl Artifact` (trace_id, prompt_hash, gold_tokens) PRIOR to LLM submission.
* Captures a `PreGuard Snapshot` of the context window.

6.4 **Static Policy Alignment:** Cognitive Engine must execute a "Policy Alignment Check" (Static) prior to response formulation.

6.5 **RAG Artifact Chain (Strict Custody):**
Retrieval MUST proceed via explicit artifacts: `RetrievalQuery` → `RetrievedChunks` → `RerankScores` → `CitationBundle`.
Final output must cite the `CitationBundle` ID. Direct external knowledge access without a Bundle is FORBIDDEN.

6.6 **Knowledge Supervision:** The L4 Knowledge Supervisor must audit low-confidence memory retrievals (confidence score < `MEMORY_CONFIDENCE_THRESHOLD`, defined in `structure_blueprint.py`; default: **0.7**) and trigger "Dense Retraining" loops.

6.7 **Plan Provenance:**
Cognitive Engine must generate a `Plan_Provenance` artifact linking the generated plan to the specific Policy Liaison Node.

6.8 **Memory Hypostates:**
Every state commit must generate an `Extended Trace Hypostate` (Memory Snapshot) linked to the Semantic Clock.

* **6.9 Knowledge Graph Advisory Constraint**

  * Knowledge Graph is **advisory only**.
  * Control authority explicitly forbidden.

* **6.10 Episodic ↔ Semantic Linking**

  * Episodic memory must record outcome links used in reasoning.

! Clarified that **context retrieval does not mutate memory** (PNG dashed line).

**Architecture gates to apply:** P2, P3, P4, P6 (determinism, planner purity, traceability, typed boundaries).

---

## 7. Guardian Physics (Deterministic Safety)

7.1 Guardian files are **pure deterministic Python scripts** (no LLMs).

7.2 **Artifact Guard:** Must enforce "Replay Comparison" and "Valid Signature Checks" on all execution artifacts (no adapters allowed).

7.2.1 All validation results must be encapsulated in a signed `GuardianArtifact` (trace_id, signature, prestaged_perms).

~ **7.3 Guardrail Guard** aligned to PNG:

* Budget Guard (tokens)
* Payload Integrity (Plast)
* Safety Markers
* Boundary Tokens (fast-fail)

- **7.7 Aggregate Gate Rule**

  * Guardian validates AGGREGATE before L2 heal admission.

7.4 Guardian execution emits a **signed artifact** containing:

* environment metadata
* commit hash
* pass/fail result
* cryptographic signature

7.4.1 **Signature Enclave:** All signing operations must occur within the `SignatureEnclave` subsystem.

7.4.2 Signatures must be verifiable against pinned Public Keys.

7.5 Absence of artifact OR signature verification failure = **automatic failure**.

7.6 A **Meta-Guardian** enforces ≥95% invariant coverage in CI.

**Architecture gates to apply:** P1, P2, P4, P5, P6 (fail-closed, determinism, traceability, signed authority, typed boundaries).

---

## 8. Native MRO & Structural Integrity (**PER-AGENT**)

8.1 Adapter patterns are **PROHIBITED**.

8.2 All behavior is composed via mixins.

8.3 **Safety mixins MUST appear LEFT of base classes** in the inheritance tuple.

8.4 MRO verification **must use the `mro_signature` provided by discovery JSON**, not inference.

8.5 Any violation fails regardless of runtime behavior.

**Architecture gates to apply:** P1, P6 (fail-closed, explicit boundaries/typed composition).

---

## 9. Separation of Responsibilities (**PER-AGENT**)

9.1 Shared mixins contain **only generic tools**.

9.2 Agent `heal()` methods contain **only domain-specific reasoning**.

9.3 Core healing logic is never delegated to adapters, factories, or orchestrators.

**Architecture gates to apply:** P3, P6 (no silent mutation via hidden orchestrators/adapters; explicit boundaries).

---

## 10. Atomic Execution & Rollback

10.1 All healing occurs inside a transactional boundary.

10.2 Snapshots are encapsulated in a typed `Boundary Snapshot Artifact` which includes:

* filesystem
* git state
* agent memory

10.3 Post-rollback state hash must exactly match the pre-wave snapshot.

* **10.4 Result Emission Exclusivity**

  * RESULT may only be emitted by L2 after successful heal or approved execution.

**Architecture gates to apply:** P1, P2, P3, P4 (fail-closed, determinism, no partial writes, traceability).

---

## 11. Budget & Resource Guards

~ **11.1 TokenCap Enforcement**

* Explicitly pre-route and pre-LLM.
* Mirrors PNG "Budget Guard" placement.

11.1 **TokenCap Enforcement:**
Budget guard executes **before** any LLM call and emits a `TokenCap Artifact`.
A `Perms Artifact` (trace_id, policy_hash, budget) must be passed to the agent.

11.2 **Route Recovery:**
`TokenOverflow` events must trigger the `RouteRecovery Box` (retry/downgrade logic), not a hard crash.

**Architecture gates to apply:** P1, P2, P4 (fail-closed, deterministic preflight, traceability).

---

## 12. Boundary Validation (**PER-AGENT**)

12.1 All inter-agent messages are schema-validated at boundaries.

12.2 A side-effect registry tracks **all touched resources**.

* **12.3 Read-Only Boundary Enforcement**

  * L0, L4, L6 are physically incapable of state mutation.

**Architecture gates to apply:** P1, P3, P6 (fail-closed, no implicit writes, typed boundaries).

---

## 13. Determinism & Time

13.1 **Semantic Clock:** Time is measured exclusively via a "Semantic Clock" (Step ID + Vector Clock), NOT wall-clock time.

13.1.1 The Semantic Clock tick advances only on valid `StateCommit`.

13.2 No wall-clock ambiguity in hashes, signatures, or deduplication.

**Architecture gates to apply:** P2, P4 (determinism, traceability).

---

## 14. Auditor Output Discipline

14.1 Evaluation is strictly evidence-based.

14.2 Absence of explicit evidence = **MISSING**.

---

## 15. Tiered Hierarchical Monitoring & Incident Response (L6)

~ **15.1 Tier III** clarified per PNG:

* "Evacuation Alert Engage" = freeze + exfiltration path.

15.1 **Tiered Vigilance Strategy:**
* **Tier I:** Budget/Token Drains (Dashboard Signature).
* **Tier II:** Anomalous Presence (Exclusive Dynamic Probes).
* **Tier III:** Evacuation Alert Engage (Emergency Exfiltration/Shutdown).

15.2 **Cognitive Diff Bundles:**
Incidents must generate a `Cognitive Diff Bundle` contrasting "Intended Policy" vs. "Actual Execution".

15.3 **Forensic Trace Buffer:**
High-velocity signals (≥`TRACE_BUFFER_VELOCITY_THRESHOLD` events per Semantic Clock tick, defined in `structure_blueprint.py`; default: **10**) MUST be captured in an ephemeral `Forensic Trace Buffer` before persistence.

15.4 **Capability Depletion:** The system must track the "Depletion Rate" of tool slots.

15.5 **Trace Emission:** All anomalies must emit a `Typed Trace ID` matching the strict regex `^CC3AL1-[0-9A-F]{8}$` (uppercase hex, exactly 8 characters). Any ID not matching this pattern = **FAIL**.

- **15.6 Metrics & Audit Emission**

  * All INCIDENT and RESULT artifacts must emit telemetry events.

**Architecture gates to apply:** P4, P6 (traceability, typed boundaries).

---

# OUTPUT REQUIREMENTS (STRICT) — v5.3 STRUCTURE (REQUIRED ORDER)

You MUST output the following sections, in this exact order:

## SECTION A — CURRENT STATE (REPO-DERIVED)

You MUST derive these from the repository (discovery JSON + deterministic scans; no assumptions):

### A1. CURRENT CAPABILITY MATRIX (GLOBAL + LAYERED)
| Layer | Component | Exists? | Enforced? | Entry Controlled? | Evidence |
|------|-----------|---------|-----------|-------------------|----------|

### A2. CURRENT ARTIFACT MATRIX (FLOW-BOUND)
| Artifact | Schema Locked? | Validated? | Emitted By | Allowed Layer | Evidence |
|---------|-----------------|------------|------------|---------------|----------|

### A3. CURRENT MUTATION SURFACE
| Mutation Source | Gated? | Approval Required? | Sandbox Guard? | Evidence |
|----------------|--------|--------------------|----------------|----------|

## SECTION B — TARGET STATE (PNG/V15-ALIGNED)

You MUST express the target using the capability list in §1–§15 and the following control-plane rules:

1) **Single sanctioned execution path**
2) **No mutation outside L2**
3) **All mutation requires explicit L3 approval when phase requires**
4) **All artifacts are schema-locked + layer-legal**
5) **Phase ordering is deterministic + test-locked**
6) **Apply mode is idempotent**

### B1. TARGET CAPABILITY MATRIX
### B2. TARGET ARTIFACT MATRIX
### B3. TARGET CONTROL-PLANE GUARANTEES

## SECTION C — GAP SET (MECHANICAL)

For every mismatch between Section A and Section B, output:

| GAP_ID | Category | Severity | Current Evidence | Target Requirement (capability refs) |
|-------|----------|----------|------------------|--------------------------------------|

Category ∈ {Boundary, Artifact, Enforcement, Ordering, Mutation, Routing}
Severity ∈ {Critical, High, Medium, Low}

Severity mapping rule (deterministic):
* If GAP violates P1–P6 → Severity = Critical
* If GAP blocks execution path (§1, §2, §3, §7, §10, §11) → Severity = High
* If GAP impacts observability or cognitive safety only (§6, §15) → Severity = Medium
* Else → Severity = Low

GAP_ID format:
* MUST be `G-<incremental integer>` in sorted deterministic order.

## SECTION D — IMPLEMENTATION PLAN (CLOSE ALL GAPS)

For each GAP_ID, produce a wave item:

| Wave | Priority | GAP_ID | Capability IDs | Work Item | Scope (repo-grounded) | Acceptance Evidence (exact commands) |
|------|----------|--------|----------------|----------|------------------------|--------------------------------------|

Hard rule: No GAP_ID may exist without at least one wave row that closes it.

Coverage assertion (mandatory):
* Every GAP_ID from Section C MUST appear in Section D at least once.
* If any GAP_ID is missing → FAIL audit integrity and STOP.

## SECTION 1 — GLOBAL FRAMEWORK EVIDENCE TABLE (KEEP)

Capabilities: 1, 3, 4, 6, 7, 10, 11, 13, 14, 15

**Format:** Table

| ID | Status (COMPLIANT / MISSING / FAIL) | Evidence Location (File + Symbol) | Notes |
| -- | ----------------------------------- | --------------------------------- | ----- |

Notes column rules:
* Strictly factual.
* Reference gating invariant (P1–P6) only if it materially changes status.
* No remediation language.

Completeness assertions (mandatory):
* All Global capability IDs listed for Section 1 MUST appear exactly once each with a non-empty Status.
* If any required cell is blank → FAIL audit integrity and STOP per 0.6.4.

---

## SECTION 2 — AGENT MATRIX EVIDENCE TABLE (KEEP)

Capabilities: 2, 3, 5, 6, 7, 8, 9, 11, 12, 13, 15

### Agent: <agent_name> (Layer <L#>)

**Discovery Identity:** `<identity>` | **File:** `<file_path>` | **Integrity Hash:** `<integrity_hash>`
**SSOT Status:** MATCH / MISMATCH | **MRO Chain:** `<exact mro_chain>`

| ID   | Capability                              | Status          | Evidence Location                          | Gating Invariant Impact | SSOT Validated? |
|------|-----------------------------------------|-----------------|--------------------------------------------|--------------------------|-----------------|
| 2.1  | Validator emits SurgicalManifest        |                 |                                            |                          |                 |
| 2.2  | Validator Safety Emulation (No Side-Effect) |           |                                            | P2                       |                 |
| 2.3  | Validator Permission Check (L5)         |                 |                                            | P5                       |                 |
| 2.4  | Boundary schema validation              |                 |                                            | P6                       |                 |
| 2.5  | Pipe order enforced (1..10)             |                 |                                            | P1                       |                 |
| 2.6  | ≥2 hash mismatches → human escalation   |                 |                                            | P5                       |                 |
| 3.4  | Human Evidence Pack Generation          |                 |                                            | P4                       |                 |
| 3.7  | Policy Challenge/Exception Loop         |                 |                                            | P5                       |                 |
| 5.1  | Dedupe uses SHA-256                     |                 |                                            | P2                       |                 |
| 5.2  | Error signature (type+node+vector_clock) |                 |                                            | P4                       |                 |
| 5.3  | Correlated collapse (Root Scope Pinning)|                 |                                            | P3                       |                 |
| 5.4  | L6 Self-Healing Trigger Emission        |                 |                                            | P1                       |                 |
| 6.5  | RAG Artifact Chain Enforced             |                 |                                            | P4                       |                 |
| 6.8  | Memory Hypostate Persistence            |                 |                                            | P2                       |                 |
| 7.2  | Artifact Guard (Replay Comparison)      |                 |                                            | P5                       |                 |
| 7.2.1| Artifact Guard (Signature Verification) |                 |                                            | P5                       |                 |
| 7.4  | GuardianArtifact Emission (Signed)      |                 |                                            | P5                       |                 |
| 8.1  | Adapters prohibited                     |                 |                                            |                          |                 |
| 8.2  | Mixins for composition                  |                 |                                            |                          |                 |
| 8.3  | Safety mixins LEFT in MRO               |                 |                                            | P1                       | PASS/FAIL       |
| 8.4  | MRO verification via discovery signature|                 |                                            | P2                       | PASS/FAIL       |
| 8.5  | MRO violation → fail                    |                 |                                            | P1                       | PASS/FAIL       |
| 9.1  | Shared mixins generic only              |                 |                                            |                          |                 |
| 9.2  | heal() domain reasoning only            |                 |                                            | P3                       |                 |
| 9.3  | No delegation to adapters/orchestrators |                 |                                            |                          |                 |
| 12.1 | Inter-agent schema validation           |                 |                                            | P6                       |                 |
| 12.2 | Side-effect registry                    |                 |                                            | P3                       |                 |
| 11.1 | TokenCap & Perms Artifacts              |                 |                                            | P1                       |                 |
| 13.1 | Semantic Clock Implementation           |                 |                                            | P2                       |                 |
| 15.1 | Tier III Evacuation Ready               |                 |                                            | P1                       |                 |
| 15.2 | Cognitive Diff Bundle Generation        |                 |                                            | P4                       |                 |

Additional required per-agent gating checks (only as evidence-linked rows in Notes; do not invent new IDs):

* P1 Fail-closed (missing schema/signature/health => reject)
* P3 No silent state mutation (no writes outside execution boundary)
* P4 TraceID propagation to artifacts
* P5 Tokenized authority (if agent participates in write/commit decisions)
* P6 Typed/versioned boundaries

Completeness assertions (mandatory):
* For every emitted per-agent matrix, every row MUST have Status populated (COMPLIANT/MISSING/FAIL).
* If any Status is blank → FAIL audit integrity and STOP per 0.6.4.

---

## SECTION 3 — SUMMARY (KEEP, BUT MUST REFERENCE SECTION A/B/C/D)

| Forensic Summary |
|-----------------|
| Total capabilities evaluated: 15 |
| Global compliance: Y% (COMPLIANT / total) |
| ACTIVE agents audited: N |
| Per-agent compliance table: |

Compliance calculation rule:
* Global compliance % = (#COMPLIANT global capabilities) / 10
* Per-agent compliance % = (#COMPLIANT per-agent rows) / total per-agent rows
* Round to nearest whole integer.

Do NOT estimate percentages if abort condition triggered.

| Agent | Compliance % | FAIL Count | Critical Gates Violated |
|-------|--------------|------------|--------------------------|
| ...   |              |            |                          |

| Non-ACTIVE Agents |
|-------------------|
| GHOST / INVALID / SYNTAX_ERROR agents: |
| • agent_name (file_path) — reason |

| Audit Integrity Confirmations |
| • No remediation language generated |
| • No out-of-scope references |
| • Evaluation bounded to discovery JSON + SSOT + P1–P6 only |

---

## SECTION 4 — GAP SET (DETERMINISTIC) (KEEP, BUT MUST ALSO PRODUCE GAP_ID TABLE IN SECTION C)

Return a table containing ONLY capabilities with status MISSING or FAIL.

| Capability ID | Status (MISSING/FAIL) | Layer Scope (GLOBAL / L0..L6) | Evidence Pointer (if FAIL) |
|--------------|------------------------|------------------------------|----------------------------|

Rules:
* Include GLOBAL capabilities (Section 1) and per-agent capabilities (Section 2) in one unified set.
* If the same capability is missing across multiple agents, list it once as an aggregated Gap with `Impacted Agents: N` in Notes.

Aggregation rules (non-negotiable):
* Aggregation key = `(capability_id, layer_scope)`.
* Status precedence: if ANY underlying instance is FAIL → aggregated Status = FAIL; else MISSING.
* Evidence Pointer: required for FAIL (include ≥1 representative contradiction pointer); optional for MISSING.

Deduplication rule:
* A capability MUST NOT appear twice in Section 4.

---

## SECTION 5 — IMPLEMENTATION PLAN (DETERMINISTIC / NO HEURISTICS) (KEEP, BUT MUST MAP 1:1 TO SECTION C GAP_IDs)

Generate an implementation plan by applying the rules in §16 exactly.

Format:
| Wave | Priority (P0/P1/P2) | Capability IDs | Work Item (noun phrase) | Scope (files/agents) | Acceptance Evidence (exact commands) |
|------|----------------------|---------------|--------------------------|----------------------|--------------------------------------|

Constraints:
* "Work Item" MUST NOT describe code edits; it must describe the missing system element (e.g., "Define Typed Artifact Schemas", "Add Guardian Signature Verification Gate").
* "Scope" MUST be discovery-grounded (agent identities or file paths from discovery JSON). If unknown, write `UNKNOWN (requires discovery evidence)` and treat as blocking for that Wave.
* "Acceptance Evidence" MUST be fixed commands (pytest targets, hash checks, schema validations) and MUST be sufficient to prove closure of the referenced capability IDs.

Determinism rule:
* Acceptance Evidence commands MUST NOT contain placeholders except `<repo_root>`.
* If `<repo_root>` used, it MUST match discovery `meta.root_path`.

Fallback evidence rule (mandatory):
* If no pytest target is discoverable for a work item, Acceptance Evidence MUST include:
  1) a schema/model import + instantiation check for the relevant artifact(s), AND
  2) a deterministic CLI/script validation (e.g., discovery run, schema validator run), AND
  3) a repo-wide grep/rg check proving wiring presence for the capability boundary.

---

## 16. PLANNING RULES (NON-NEGOTIABLE)

The implementation plan MUST be derived deterministically from the Gap Set using ONLY these rules:

### 16.1 Priority Assignment
Assign the highest applicable priority:

* **P0 (Blockers):** Any gap that violates P1/P2/P3/P4/P5/P6 globally OR prevents trustworthy evaluation (discovery integrity, SSOT hash mismatch, missing typed artifacts required for traceability, signature verification absent).
* **P1 (Critical Path):** Gaps on the main enforcement/control path: §1 (SurgicalManifest), §2 (Validator–Healer), §3 (Control Plane routing), §7 (Guardian Physics), §10 (Atomic rollback), §11 (Budget).
* **P2 (Supporting):** Observability/monitoring enhancements (§15), advanced cognition/RAG custody (§6) that do not block enforcement correctness, and any per-agent hygiene that is not on the execution boundary.

### 16.2 Wave Ordering
Order waves strictly:
1) **Wave 0:** Discovery integrity + SSOT hash match gates
2) **Wave 1:** Typed artifact schemas required for P4/P6 traceability at boundaries
3) **Wave 2:** Guardian Physics (signature + replay + aggregate gate) and boundary validation gates
4) **Wave 3:** Validator–Healer symmetric pipe ordering + rollback correctness
5) **Wave 4:** Control Plane routing + EvidencePack + PolicyUpdateProposal
6) **Wave 5:** Budget guards + Semantic Clock determinism
7) **Wave 6:** L6 incident response (tiers, diff bundle, trace buffer) and remaining P2 items

### 16.3 Dependency Resolution
If a plan row depends on another capability ID, it MUST be placed in a later wave.
Default dependencies (minimum):
* §1.7 (typed artifacts) precedes any capability that emits/validates those artifacts.
* §7 (Guardian) precedes §2.5 (Healer commit) when Guardian gates admission.
* §10 (snapshots/rollback) precedes any write/commit authorization.
* §13 (Semantic Clock) precedes any hashing/deduplication that references time buckets.

Dependency escalation rule (mandatory):
* If §13.1 (Semantic Clock) is MISSING/FAIL, then §5.2 (time-bucketed signatures) MUST be scheduled as P0 in a later wave, explicitly blocked on §13 closure.

### 16.4 Aggregation Rule
If a capability is missing across ≥3 agents, create a single plan row with aggregated scope and a single acceptance gate; do NOT repeat per-agent rows unless an agent has a unique FAIL contradiction.

### 16.5 Acceptance Evidence Sufficiency
Every wave MUST include:
* at least one deterministic test command (pytest target or equivalent)
* and at least one artifact/schema/contract validation command when the wave touches boundaries.

### 16.6 Empty-Gap Handling

If Section 4 Gap Set is empty:
* Section 5 MUST contain exactly one row:
  - Wave = NONE
  - Priority = NONE
  - Capability IDs = NONE
  - Work Item = FULL COMPLIANCE (NO WORK)
  - Scope = GLOBAL
  - Acceptance Evidence = `python <repo_root>/.../forensic_discovery_prep.py` + `pytest -q` (or fallback rule if pytest absent)

* Section C MUST be empty table.
* Section D MUST contain only the single NONE row.

---

## HARD PROHIBITIONS (ENFORCED)

Your output **MUST NOT** contain:

* code patches / unified diffs / concrete edit instructions
* speculative interpretation
* probabilistic language

Allowed (v5.1):
* deterministic implementation plan tables (Sections 4–5) adhering to §16

Violation invalidates the audit.

---

## FINAL RULE (v5.3)

This is a **current-state to target-state operational plan generator**.

If a capability is not **explicit, deterministic, and provable** in the discovery-scoped code/config/tests, it is **MISSING** (or **FAIL** where illegal states or fail-closed violations are evidenced), and it MUST appear in Section 4 and be scheduled in Section 5 per §16.

---

## START EXECUTION (v5.3)

1) Run discovery script
2) Ingest JSON + freeze scope
3) Produce Section A (CURRENT STATE)
4) Produce Section B (TARGET STATE)
5) Produce Section C (GAP)
6) Produce Section D + Section 5 (IMPLEMENTATION PLAN)

```
```

---

## ✅ Net Effect (PNG Parity)

* All **layers (L0–L6)** mapped 1:1 to prompt capabilities.
* All **arrows in the PNG** now correspond to:

  * a typed artifact, or
  * an explicit prohibition.
* RESULT / AGGREGATE / INCIDENT / HEALING_PLAN flows are **non-ambiguous and enforceable**.
* Advisory vs control boundaries are **explicitly fail-closed**.

No inferred behavior remains unstated; absence of any of the above in code now deterministically evaluates to **MISSING or FAIL** under v5.1.
