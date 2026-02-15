<!-- VERSION: 0.1.0 -->
# V15 TARGET STATE — CONSOLIDATED CAPABILITY LIST (v5.1) (ZERO-LOSS)

> Every numbered item is an independent, auditable capability. Absence of direct evidence = MISSING. Capabilities are enumerated in §1–§16.

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
**Prohibition:** do not expand into "flow" narration; treat as pure evidence checks.

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

## 16. Governed Improvement (Meta-Learning) (CONTROLLED ADAPTATION, ZERO-BYPASS)

Meta-learning is part of the TARGET STATE only if it is governed and bounded by the control spine.
Meta-learning MUST NOT directly patch live logic. All behavior changes MUST be:
1) proposed as typed artifacts
2) evaluated via deterministic replay / drift evaluation
3) approved (L5 and/or HIL depending on risk)
4) versioned in L4
5) re-entered via L0 routing using the new version pointer

### 16.1 Metrics Foundation (MetaLearningMetricsArtifact)

16.1 A canonical `MetaLearningMetricsArtifact` MUST be emitted for every completed run:
* Answer-only
* L5-gated path
* HIL escalation path
* L2 execution path

16.2 Metrics MUST be deterministic and replayable:
* semantic_clock-bound
* no wall-clock dependence
* no uuid4
* sorted lists
* JSON emitted with sort_keys=True

Required fields (minimum):
* artifact_type = "META_LEARNING_METRICS"
* trace_id (deterministic)
* semantic_clock (required)
* route_path
* risk_tier
* vigilance_tier (optional)
* decision_outcome (ANSWER_ONLY / EXECUTED / ESCALATED / REJECTED)
* policy_config_hash (optional)
* model_version (optional)
* tool_invocations (int)
* token_usage {prompt:int, completion:int, total:int}
* errors (sorted list[str] of stable codes)
* healing_triggered (bool)
* human_review {required: bool, approved: bool|None}
* cost_units (deterministic formula derived from token_usage)

16.3 Emission point MUST be a single control-spine finalization chokepoint (no duplication).

### 16.2 Evaluation + Drift Detection (EvalReportArtifact)

16.4 Deterministic evaluators MUST consume MetaLearningMetricsArtifact sets and produce `EvalReportArtifact`.
Evaluation windows MUST be defined by semantic_clock tick intervals (not timestamps).

Required fields (minimum):
* artifact_type = "EVAL_REPORT"
* trace_id (deterministic)
* semantic_clock (required)
* window {start_tick:int, end_tick:int, sample_count:int}
* metrics_rollup {pass_rate:float, exec_rate:float, hil_rate:float, heal_rate:float}
* drift_signals (sorted list[{code:str, severity:str, value:float, threshold:float}])
* regressions (sorted list[str])
* recommendation (NO_CHANGE / PROPOSE_UPDATE)

### 16.3 Explicit Learning Proposals (LearningProposalArtifact)

16.5 Learning changes MUST be represented only as typed proposal artifacts (no implicit config edits).
Targets MUST be explicit:
* ROUTING thresholds
* POLICY versions
* PROMPT versions
* TOOL_PLAN sequences
* HEAL_PLAYBOOK configurations

Required fields (minimum):
* artifact_type = "LEARNING_PROPOSAL"
* proposal_id (deterministic)
* semantic_clock (required)
* target {kind, ref} where kind ∈ {ROUTING, POLICY, PROMPT, TOOL_PLAN, HEAL_PLAYBOOK}
* change {before_hash, after_hash, diff_summary (sorted list[str])}
* evidence {eval_report_trace_id, supporting_trace_ids (sorted list[str])}
* risk {tier, blast_radius}
* required_approvals {hil, quorum}
* success_metrics (sorted list[{name, direction, target}])
* rollback {enabled: bool, revert_to_hash: str}

16.6 Proposal artifacts MUST be non-mutating; they MUST NOT write L4.

### 16.4 Promotion Pipeline (Candidate → Shadow → Active)

16.7 All promotions MUST be mediated by a typed `PromotionDecisionArtifact` at a single chokepoint.
L4 MUST store versioned pointers per target kind:
* candidate pointer
* shadow pointer
* active pointer

16.8 Authorization rules (fail-closed):
* High-risk proposals require HIL approval
* Low-risk proposals may auto-promote only to SHADOW (never ACTIVE)
* ACTIVE promotion is forbidden without replay gate success (16.5)

### 16.5 Replay Harness Gate (ReplayRunArtifact)

16.9 A deterministic replay harness MUST evaluate archived traces under candidate/shadow configs.
If blocking regressions exist, promotion to ACTIVE is forbidden.

Required fields (minimum):
* artifact_type = "REPLAY_RUN"
* semantic_clock (required)
* proposal_id
* config_under_test_hash
* traces (sorted list[str])
* results (sorted list[{trace_id, outcome, regressions (sorted list[str])}])
* summary {pass_rate:float, blocking_regressions:int}
* gate {ALLOW_PROMOTION: bool, reason_codes (sorted list[str])}

### 16.6 Layer Touchpoints (Where Meta-learning "Touches" L0–L6)

Meta-learning MUST operate by producing governed artifacts that affect versions/configs only:
* L1: prompt refinements and model selection metadata (versioned; no direct mutation)
* L0: routing threshold/version pointer updates (re-enter via L0; logged RouteDecision)
* L3: workflow/tool-plan sequencing versions (via proposal + promotion)
* L5: policy version updates (via proposal + approvals)
* L6: anomaly classifier version updates (via proposal + promotion)
* L2: sandbox constraints / healing playbook versions (via proposal; capability-gated execution)
* L4: versioned storage of candidate/shadow/active pointers (single mutation chokepoint)

### 16.7 Meta-learning Safety Invariants (NON-NEGOTIABLE)

* No wall-clock timestamps in determinism-critical meta-learning artifacts.
* No uuid4 in determinism-critical meta-learning artifacts.
* All lists sorted; all JSON emitted with sort_keys=True.
* All behavior changes MUST re-enter via L0 routing and be visible to L5/HIL gates.
* Meta-learning activation is forbidden until P0 execution hardening is closed (P5.1, §12.3).

---
