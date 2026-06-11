---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\v5_forensic_gap_analysis_report.md'
original_relative_path: 'v5_forensic_gap_analysis_report.md'
source_sha256: 3d8e94199f1aca3cfcdecb9db0492256e7e09a372ef1d5090a96201f06c749e3
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-09'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# FORENSIC GAP ANALYSIS REPORT — Prompt v5.0 Enhanced (V15 Target State)

**Generated**: 2026-02-09T19:37:00Z
**Discovery Commit**: `7f6d87befab360bf9cff3dd87772832cbbcbf742`
**Discovery Schema Version**: 1.2.1-corrected
**ACTIVE Agents**: 150
**Non-ACTIVE (INVALID)**: 40
**Auditor Role**: Deterministic Forensic Auditor (Static Capability Audit)

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## PHASE 0 — DISCOVERY INTEGRITY & SCOPE FREEZE

| Precondition | Status | Evidence |
|---|---|---|
| Discovery script exists | PASS | `agentic_core/L0_maintenance/scripts/forensic_discovery_prep.py` (SHA-256: `ce0c0bfa...`) |
| Known-good hash in `structure_blueprint.py` | FAIL | No known-good hash for the discovery script is stored in `structure_blueprint.py` or the `structure_blueprint/` package. The `blueprint_integrity.sha256` contains `56ce497e...` which is the hash of the blueprint **package .py files**, not the discovery script. |
| Discovery script import integrity | FAIL | Script imports from `agentic_core.utils.ssot_discovery_validator` which does not exist. Actual module: `agentic_core.L0_maintenance.utils.ssot_discovery_util`. Import patching required at runtime. |
| Discovery script field mapping | FAIL | Script expects `candidate.get("path", "")` and `candidate.get("name", "Unknown")` but `agent_discovery_full.json` uses fields `file` and `class_name`. Field remapping required. |
| Discovery executed successfully (corrected) | PASS | 150 ACTIVE, 40 INVALID (all INVALID due to missing `file` field in SSOT candidates — 40 entries with no path in `agent_discovery_full.json`) |
| SSOT Blueprint validation (`structure_blueprint.py`) | PASS | `agentic_core/L5_safety/config/structure_blueprint_config.py` is a backward-compatible shim re-exporting 163 names from `agentic_core/L5_safety/config/structure_blueprint/` package |
| Discovery schema conformance to §0 strict schema | FAIL | Discovery output schema version `1.2.0`/`1.2.1-corrected` does not match §0 required schema. Missing fields: `identity` (uses `agent_name`), `integrity_hash` (uses `file_sha256`), `mixins` (not separate from `mro_signature`). `ssot_validation` block absent. `meta` block uses `audit_meta` instead. |

**Scope Freeze**: 150 ACTIVE agents audited. 40 INVALID agents listed in Section 3. Zero GHOST, zero SYNTAX_ERROR, zero ZOMBIE detected.

---

# SECTION 1 — GLOBAL FRAMEWORK AUDIT

Capabilities: §1, §3, §4, §6, §7, §10, §11, §13, §14, §15

| ID | Capability | Status | Evidence Location | Notes |
|---|---|---|---|---|
| **1.1** | SurgicalManifest as exclusive execution input | **MISSING** | No file, class, or TypedDict named `SurgicalManifest` exists in the codebase. Grep: 0 results for `SurgicalManifest`. | P2, P3, P4, P6 gating. |
| **1.2** | Forbidden execution inputs (raw paths, regex, diffs, free-form) | **FAIL** | Agents universally operate on raw file paths (`pathlib.Path`), line numbers, and regex. E.g., `agentic_core/L5_safety/reasoning/LocationHealerAgent.py`, `CodeHealerAgent.py`. | Direct contradiction of §1.2. |
| **1.3** | SurgicalManifest schema (all 10 fields) | **MISSING** | No `schema_version`, `correlation_id`, `node_id`, `target_layer`, `ast_snippet`, `serialization_canon`, `fix_constraint`, `manifest_hash`, `change_history`, `provenance_chain` fields exist as a typed schema. | |
| **1.4** | Deterministic AST serialization (LibCST/sorted ast.dump) | **MISSING** | LibCST is present in `agentic_core/mixins/cst_healer_mixin.py` and `L5_safety/utils/unified_cst_healer_util.py` for CST transformations, but no deterministic canonical serialization with SHA-256 hash computation exists. | P2 gating. |
| **1.5** | SSOT Binding (node_id resolves to structure_blueprint.py) | **MISSING** | No `node_id` concept exists. | |
| **1.6** | Hash Verification (manifest_hash from ast_snippet bytes) | **MISSING** | No manifest hash verification mechanism exists. | |
| **1.7** | Secondary Artifact Schema Requirements (TypedDict/Pydantic) | **MISSING** | None of the V15 typed artifacts (`AGGREGATE`, `RESULT`, `INCIDENT`, `HEALING_PLAN`, `EvidencePack`, `PolicyUpdateProposal`, `CognitiveDiffBundle`, `RouteDecision` as typed artifact, `TokenCapArtifact`, `SelfHealingTrigger`, `BoundarySnapshotArtifact`, `PolicyExceptionArtifact`, `SignedModify`) exist as `TypedDict` or `Pydantic` models. | `GuardianArtifact` exists at `agentic_core/L0_maintenance/types/guardian_contract.py::GuardianArtifact` (lines 590–601) but lacks V15 required fields (`trace_id`, `signature`, `prestaged_perms`, `environment_metadata`, `commit_hash`, `pass_fail`). Status: **FAIL** per §1.7 audit rule. |
| **3.1** | RouteDecision typed artifact (6 required fields) | **FAIL** | `agentic_core/runtime/config/contextual_router_config.py::RouteDecision` (line 40) exists but is an `Enum` with 4 values (`BYPASS`, `VALIDATE`, `HUMAN_REVIEW`, `REJECT`), not a typed artifact. Missing required fields: `timestamp`, `route_path`, `risk_score`, `budget_est`, `rationale_enum`, `policy_config_hash`. | P1, P2, P4, P5, P6 gating. |
| **3.2** | Rationale restricted to finite enum | **MISSING** | No `rationale` enum exists on any routing artifact. | |
| **3.3** | Routing paths strictly defined (5 paths) | **FAIL** | `contextual_router_config.py::RouteDecision` defines 4 paths (`BYPASS`, `VALIDATE`, `HUMAN_REVIEW`, `REJECT`). Missing: "Policy Challenge Loop" and "Route Recovery (Budget Overflow)". | |
| **3.4** | Human escalation generates structured EvidencePack | **MISSING** | No `EvidencePack` class/schema exists. Grep: 0 results. | P4 gating. |
| **3.5** | Bidirectional Feedback (PolicyUpdateProposal) | **MISSING** | No `PolicyUpdateProposal` class/schema exists. Grep: 0 results. | |
| **3.6** | Law Slot Handler / Read-Only Twins / Capability Depletion | **MISSING** | No "Law Slot Handler", "Read-Only Twin", or "Capability Depletion" mechanism exists. | |
| **3.7** | Policy Challenge Protocol (PolicyExceptionArtifact) | **MISSING** | No `PolicyExceptionArtifact` exists. Grep: 0 results. | P5 gating. |
| **3.8** | Context Retrieval Request Artifact (L0→L4) | **MISSING** | No typed context retrieval request artifact exists. | |
| **4.1** | policy_config read-once per healing wave | **MISSING** | No "healing wave" scoped policy_config read-once mechanism exists. | P1, P2 gating. |
| **4.2** | SHA-256 of policy config at wave start, verified before routing | **MISSING** | No `policy_config_hash` or `policy_hash` found in codebase. Grep: 0 results. | P4 gating. |
| **4.3** | Policy mutation during wave = critical incident | **MISSING** | No policy mutation detection mechanism exists. | |
| **6.1** | Episodic memory queried before planning | **MISSING** | No episodic memory query-before-plan mechanism found as typed artifact chain. | P2 gating. |
| **6.2** | Trajectory reuse (similarity + exact failure_reason match) | **MISSING** | No trajectory reuse mechanism with typed constraints exists. | |
| **6.3** | Automatic prompt augmentation (≤300 tokens, logged, TokenControl Artifact) | **MISSING** | No `TokenControl Artifact` or `PreGuard Snapshot` exists. | |
| **6.4** | Static Policy Alignment Check | **MISSING** | No typed "Policy Alignment Check" mechanism exists. | |
| **6.5** | RAG Artifact Chain (RetrievalQuery→RetrievedChunks→RerankScores→CitationBundle) | **MISSING** | None of `RetrievalQuery`, `RetrievedChunks`, `RerankScores`, `CitationBundle` exist. Grep: 0 results for all four. | P4 gating. |
| **6.6** | Knowledge Supervisor (low-confidence retraining) | **MISSING** | No `MEMORY_CONFIDENCE_THRESHOLD` in `structure_blueprint.py`. No Knowledge Supervisor agent or retraining loop exists. | |
| **6.7** | Plan Provenance artifact | **MISSING** | No `Plan_Provenance` or `PlanProvenance` exists. Grep: 0 results. | |
| **6.8** | Memory Hypostates (Extended Trace Hypostate) | **MISSING** | No `hypostate` or `Extended Trace` memory snapshot mechanism exists. Grep: 0 results. | P2 gating. |
| **6.9** | Knowledge Graph advisory-only constraint | **MISSING** | No explicit typed enforcement preventing Knowledge Graph control authority. | |
| **6.10** | Episodic ↔ Semantic Linking | **MISSING** | No typed episodic-semantic outcome linking mechanism exists. | |
| **7.1** | Guardian files are pure deterministic Python (no LLMs) | **COMPLIANT** | `agentic_core/L0_maintenance/types/guardian_contract.py` (lines 1–784): Guardian contract is pure Python with dataclasses, enums, JSON schema validation. No LLM invocations. Guardian scripts in `agentic_core/L0_maintenance/scripts/` are deterministic. | |
| **7.2** | Artifact Guard (Replay Comparison + Valid Signature Checks) | **MISSING** | No "Artifact Guard" component or replay comparison mechanism exists. | P5 gating. |
| **7.2.1** | GuardianArtifact signed (trace_id, signature, prestaged_perms) | **FAIL** | `guardian_contract.py::GuardianArtifact` (lines 590–601) exists but contains only `type`, `path`, `description`. Missing: `trace_id`, `signature`, `prestaged_perms`, `environment_metadata`, `commit_hash`, `pass_fail`. | P5 gating. |
| **7.3** | Guardrail Guard (Budget, Payload Integrity, Safety Markers, Boundary Tokens) | **MISSING** | No unified "Guardrail Guard" component. Budget guard (`BudgetAgent` in L1), circuit breaker (`circuit_breaker.py` in L5) exist separately but are not a unified guardrail gate. No `TokenCapArtifact` emitted. | |
| **7.4** | Guardian signed artifact (env metadata, commit hash, pass/fail, signature) | **FAIL** | `GuardianResult` at `guardian_contract.py` (lines 604–698) has `guardian_id`, `status`, `checks`, `artifacts`, `metrics` but lacks `signature`, `commit_hash`, `environment_metadata` as required fields. | P5 gating. |
| **7.4.1** | Signature Enclave subsystem | **MISSING** | No `SignatureEnclave` exists. Grep: 0 results. | |
| **7.4.2** | Signatures verifiable against pinned Public Keys | **MISSING** | No public key infrastructure exists. | |
| **7.5** | Absence of artifact/signature = automatic failure | **MISSING** | No typed enforcement of "absent artifact = fail" exists. | P1 gating. |
| **7.6** | Meta-Guardian ≥95% invariant coverage in CI | **MISSING** | `meta_guardian` referenced in `tests/guardian/test_guardian_contract_gate_scope.py` (19 matches) and `tests/guardian/_contract_gate_ssot.py` but no ≥95% coverage enforcement found. | |
| **7.7** | Aggregate Gate Rule (Guardian validates AGGREGATE before L2) | **MISSING** | No typed AGGREGATE validation gate before L2 heal admission. | |
| **10.1** | Healing inside transactional boundary | **MISSING** | No typed transactional boundary wrapping healing operations. `AtomicExecutionMixin` exists but does not implement typed snapshot/rollback. | P1 gating. |
| **10.2** | Boundary Snapshot Artifact (filesystem, git state, agent memory) | **MISSING** | No `BoundarySnapshotArtifact` or `BoundarySnapshot` exists. Grep: 0 results. | P2, P4 gating. |
| **10.3** | Post-rollback hash matches pre-wave snapshot | **MISSING** | No snapshot hash comparison mechanism. | |
| **10.4** | RESULT emission exclusive to L2 post-heal | **MISSING** | No typed `RESULT` artifact (`result.json`) with required fields exists. | |
| **11.1** | TokenCap Enforcement (pre-route, pre-LLM, TokenCap Artifact, Perms Artifact) | **MISSING** | No `TokenCapArtifact` or `Perms Artifact` exists. Grep: 0 results for `TokenCap`. | P1, P2 gating. |
| **11.2** | Route Recovery (TokenOverflow → RouteRecovery Box) | **MISSING** | No `RouteRecovery` or `TokenOverflow` handling mechanism. | |
| **13.1** | Semantic Clock (Step ID + Vector Clock, not wall-clock) | **FAIL** | `semantic_clock` and `step_id` references found in `agentic_core/L0_maintenance/scripts/execution.py` (18 matches), `apps_shared/types/sovereign_severity_types.py` (4 matches), `execution_context.py` (2 matches). However, wall-clock `datetime.utcnow()` is used extensively (e.g., `contextual_router_config.py` line 59: `timestamp: datetime = field(default_factory=datetime.utcnow)`). Time is not exclusively semantic-clock-based. | P2, P4 gating. |
| **13.1.1** | Semantic Clock tick advances only on valid StateCommit | **MISSING** | No `StateCommit`-gated clock advance mechanism. | |
| **13.2** | No wall-clock ambiguity in hashes/signatures/dedup | **FAIL** | Wall-clock timestamps used in routing, tracing, discovery. | P2 gating. |
| **14.1** | Evaluation strictly evidence-based | N/A | Auditor conduct rule. | |
| **14.2** | Absence = MISSING | N/A | Auditor conduct rule. | |
| **15.1** | Tiered Vigilance (Tier I/II/III, Evacuation Protocol) | **MISSING** | `Evacuation` term found only in `FileClassificationAgent.py` (2 matches) and `RootHygieneAgent.py` (1 match) in unrelated contexts (file classification, not monitoring tiers). No Tier I/II/III monitoring strategy exists. | P1 gating. |
| **15.2** | Cognitive Diff Bundle generation | **MISSING** | No `CognitiveDiffBundle` or `cognitive_diff` exists. Grep: 0 results. | P4 gating. |
| **15.3** | Forensic Trace Buffer (high-velocity ephemeral capture) | **MISSING** | `trace_buffer` found in `agentic_core/mixins/tracing_mixin.py` (8 matches) but this is a general tracing buffer, not a forensic ephemeral buffer gated by `TRACE_BUFFER_VELOCITY_THRESHOLD`. No velocity threshold exists in `structure_blueprint.py`. | P2 gating. |
| **15.4** | Capability Depletion (tool slot depletion rate tracking) | **MISSING** | No capability depletion tracking mechanism. | |
| **15.5** | Trace Emission regex `^CC3AL1-[0-9A-F]{8}$` | **MISSING** | No trace IDs matching pattern `CC3AL1-XXXXXXXX` exist. Grep: 0 results. Trace IDs use UUID4 format (`tracing_mixin.py` line 47: `str(uuid.uuid4())`). | **FAIL** — active trace ID format contradicts requirement. |
| **15.6** | INCIDENT and RESULT emit telemetry events | **MISSING** | No typed INCIDENT or RESULT artifact emission to telemetry. | |

### Global Framework Audit Summary

| Status | Count |
|---|---|
| COMPLIANT | 1 |
| MISSING | 51 |
| FAIL | 9 |
| N/A (auditor rules) | 2 |
| **Total evaluated** | **63 sub-capabilities** |

---

# SECTION 2 — AGENT MATRIX AUDIT

Capabilities: §2, §3, §5, §6, §7, §8, §9, §11, §12, §13, §15

> **Structural Finding**: All 150 ACTIVE agents share identical capability gaps for §2, §3.4, §3.7, §5, §6.5, §6.8, §7.2, §7.2.1, §7.4, §11.1, §12.1, §12.2, §13.1, §15.1, §15.2 because the V15 typed artifact infrastructure (SurgicalManifest, EvidencePack, CognitiveDiffBundle, TokenCapArtifact, SelfHealingTrigger, BoundarySnapshot, etc.) does not exist at the framework level. Per-agent behavioral evidence cannot exist when the framework contracts are absent.
>
> The per-agent matrix below evaluates **§8 (MRO/Structural Integrity)** and **§9 (Separation of Responsibilities)** where per-agent evidence is meaningful, plus the uniform MISSING/FAIL status for all other capabilities.

## Per-Agent MRO & Structural Audit (§8)

**MRO Evaluation Criteria**:
- §8.1: Adapter patterns PROHIBITED
- §8.2: All behavior via mixins
- §8.3: Safety mixins LEFT of base classes in MRO
- §8.4: MRO verified via discovery signature
- §8.5: Any MRO violation = FAIL

### L0_maintenance (6 agents)

| Agent | File | MRO Chain | §8.1 Adapters | §8.3 Safety LEFT | §8.4 MRO Verified | has_heal |
|---|---|---|---|---|---|---|
| BenchmarkingAgent | `agentic_core/L0_maintenance/reasoning/BenchmarkingAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A (no safety mixin) | PASS | YES |
| BootstrapAgent | `agentic_core/L0_maintenance/reasoning/BootstrapAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| DocstringComplianceAgent | `agentic_core/L0_maintenance/reasoning/DocstringComplianceAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | NO |
| FilesystemSSOTReconcilerAgent | `agentic_core/L0_maintenance/reasoning/FilesystemSSOTReconcilerAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| GospelSyncAgent | `agentic_core/L0_maintenance/reasoning/GospelSyncAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| SSOTFolderCleanupAgent | `agentic_core/L0_maintenance/reasoning/SSOTFolderCleanupAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |

### L1_cognition (11 agents)

| Agent | File | MRO Chain | §8.1 Adapters | §8.3 Safety LEFT | §8.4 MRO Verified | has_heal |
|---|---|---|---|---|---|---|
| ASTValidatorAgent | `agentic_core/L1_cognition/reasoning/ASTValidatorAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| AgentInfo | `agentic_core/L1_cognition/types/agent_info_types.py` | `NONE` | COMPLIANT | N/A | PASS | NO |
| AutonomousPromptEvolutionAgent | `agentic_core/L1_cognition/reasoning/AutonomousPromptEvolutionAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | NO |
| BudgetAgent | `agentic_core/L1_cognition/reasoning/BudgetAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | NO |
| ContextCuratorAgent | `agentic_core/L1_cognition/reasoning/ContextCuratorAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| LLMPromptGovernorAgent | `agentic_core/L1_cognition/reasoning/LLMPromptGovernorAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| MetaLearningAgent | `agentic_core/L1_cognition/reasoning/MetaLearningAgent.py` | `AtomicExecutionMixin, SovereignBaseAgent` | COMPLIANT | COMPLIANT (AtomicExecutionMixin LEFT) | PASS | YES |
| RgReflectionAgent | `agentic_core/L1_cognition/reasoning/RgReflectionAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | NO |
| SherlockAgent | `agentic_core/L1_cognition/reasoning/SherlockAgent.py` | `SovereignBaseAgent, SubAtomicAgent` | COMPLIANT | N/A | PASS | YES |
| StrategicRecommendationAgent | `agentic_core/L1_cognition/reasoning/StrategicRecommendationAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| SupremeCourtAgent | `agentic_core/L1_cognition/reasoning/SupremeCourtAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | NO |

### L2_execution (9 agents)

| Agent | File | MRO Chain | §8.1 Adapters | §8.3 Safety LEFT | §8.4 MRO Verified | has_heal |
|---|---|---|---|---|---|---|
| AgentPlan | `agentic_core/L2_execution/types/agent_plan_types.py` | `NONE` | COMPLIANT | N/A | PASS | NO |
| EmbeddingSovereignAgent | `agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py` | `AtomicExecutionMixin, SovereignBaseAgent` | COMPLIANT | COMPLIANT | PASS | NO |
| GitAgent | `agentic_core/L2_execution/reasoning/GitAgent.py` | `AtomicExecutionMixin, SovereignBaseAgent` | COMPLIANT | COMPLIANT | PASS | YES |
| HistorianAgent | `agentic_core/L2_execution/reasoning/HistorianAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | NO |
| PeerIntelligenceAuditorAgent | `agentic_core/L2_execution/reasoning/PeerIntelligenceAuditorAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| SovereignMCPGatewayAgent | `agentic_core/L2_execution/reasoning/SovereignMCPGatewayAgent.py` | `AtomicExecutionMixin, SovereignBaseAgent` | COMPLIANT | COMPLIANT | PASS | NO |
| SovereignPineconeMcpClientAgent | `agentic_core/L2_execution/reasoning/SovereignPineconeMcpClientAgent.py` | `AtomicExecutionMixin, SovereignBaseAgent` | COMPLIANT | COMPLIANT | PASS | NO |
| SubAtomicRegistryAgent | `agentic_core/L2_execution/reasoning/sub_atomic_registry.py` | `AtomicExecutionMixin, SovereignBaseAgent` | COMPLIANT | COMPLIANT | PASS | YES |
| ToolsmithAgent | `agentic_core/L2_execution/reasoning/ToolsmithAgent.py` | `AtomicExecutionMixin, SovereignBaseAgent` | COMPLIANT | COMPLIANT | PASS | YES |

### L3_orchestration (13 agents)

| Agent | File | MRO Chain | §8.1 Adapters | §8.3 Safety LEFT | §8.4 MRO Verified | has_heal |
|---|---|---|---|---|---|---|
| AgentCategory | `agentic_core/L3_orchestration/types/agent_category_types.py` | `Enum` | COMPLIANT | N/A | PASS | NO |
| AgentFactory | `agentic_core/L3_orchestration/reasoning/AgentFactory.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | NO |
| AgentGym | `agentic_core/L3_orchestration/reasoning/AgentGym.py` | `AtomicExecutionMixin, SovereignBaseAgent` | COMPLIANT | COMPLIANT | PASS | NO |
| CoverageAgent | `agentic_core/L3_orchestration/reasoning/CoverageAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | NO |
| DAGMutatorAgent | `agentic_core/L3_orchestration/reasoning/DAGMutatorAgent.py` | `AtomicExecutionMixin, SovereignBaseAgent` | COMPLIANT | COMPLIANT | PASS | YES |
| NervousSystemAgent | `agentic_core/L3_orchestration/reasoning/NervousSystemAgent.py` | `AtomicExecutionMixin, SovereignBaseAgent` | COMPLIANT | COMPLIANT | PASS | YES |
| OrchestrationHandshakeAgent | `agentic_core/L3_orchestration/reasoning/OrchestrationHandshakeAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | NO |
| SemanticGatekeeperAgent | `agentic_core/L3_orchestration/reasoning/SemanticGatekeeperAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| SubAtomicAgent | `agentic_core/L3_orchestration/reasoning/SubAtomicAgent.py` | `AtomicExecutionMixin, SovereignBaseAgent` | COMPLIANT | COMPLIANT | PASS | YES |
| SubatomicHopAgent | `agentic_core/L3_orchestration/reasoning/SubatomicHopAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | NO |
| context_curator_engine | `agentic_core/L3_orchestration/reasoning/context_curator_engine.py` | `AtomicExecutionMixin, SovereignBaseAgent` | COMPLIANT | COMPLIANT | PASS | NO |
| omni_context_engine | `agentic_core/L3_orchestration/reasoning/omni_context_engine.py` | `SubAtomicAgent` | COMPLIANT | N/A | PASS | NO |
| sovereign_mcp_router | `agentic_core/L3_orchestration/reasoning/sovereign_mcp_router.py` | `AtomicExecutionMixin, SovereignBaseAgent` | COMPLIANT | COMPLIANT | PASS | NO |

### L4_state (6 agents)

| Agent | File | MRO Chain | §8.1 Adapters | §8.3 Safety LEFT | §8.4 MRO Verified | has_heal |
|---|---|---|---|---|---|---|
| CachedStateLedgerAgent | `agentic_core/L4_state/reasoning/CachedStateLedgerAgent.py` | `AtomicExecutionMixin, SovereignBaseAgent` | COMPLIANT | COMPLIANT | PASS | YES |
| MemoryArchitectAgent | `agentic_core/L4_state/reasoning/MemoryArchitectAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| RedisSovereignAgent | `agentic_core/L4_state/reasoning/RedisSovereignAgent.py` | `AtomicExecutionMixin, SovereignBaseAgent` | COMPLIANT | COMPLIANT | PASS | YES |
| SovereignPineconeStoreAgent | `agentic_core/L4_state/reasoning/SovereignPineconeStoreAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| sovereign_reasoning_memory_ledger | `agentic_core/L4_state/memory/sovereign_reasoning_memory_ledger.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | NO |
| sovereign_semantic_cache | `agentic_core/L4_state/memory/sovereign_semantic_cache.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | NO |

### L5_safety (77 agents)

| Agent | File | MRO Chain | §8.1 Adapters | §8.3 Safety LEFT | §8.4 MRO Verified | has_heal |
|---|---|---|---|---|---|---|
| AdversarialProbeAgent | `agentic_core/L5_safety/reasoning/AdversarialProbeAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| AdversarialRedTeamerAgent | `agentic_core/L5_safety/reasoning/AdversarialRedTeamerAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | NO |
| AgentPermission | `agentic_core/L5_safety/types/agent_permission_types.py` | `Enum` | COMPLIANT | N/A | PASS | NO |
| ArchitectureGovernorAgent | `agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| AutonomousThreatEvolutionAgent | `agentic_core/L5_safety/reasoning/AutonomousThreatEvolutionAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | NO |
| AutonomyGuardianAgent | `agentic_core/L5_safety/reasoning/AutonomyGuardianAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| BoundaryTestingAgent | `agentic_core/L5_safety/reasoning/BoundaryTestingAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | NO |
| CachedSafetyShieldAgent | `agentic_core/L5_safety/reasoning/CachedSafetyShieldAgent.py` | `AtomicExecutionMixin, SovereignBaseAgent` | COMPLIANT | COMPLIANT | PASS | YES |
| ChaosEngineeringAgent | `agentic_core/L5_safety/reasoning/ChaosEngineeringAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| CodeDeduplicationAgent | `agentic_core/L5_safety/reasoning/CodeDeduplicationAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| CodeDetectorAgent | `agentic_core/L5_safety/reasoning/CodeDetectorAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| CodeEnforcerAgent | `agentic_core/L5_safety/reasoning/CodeEnforcerAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| CodeFormatterAgent | `agentic_core/L5_safety/reasoning/CodeFormatterAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| CodeHealerAgent | `agentic_core/L5_safety/reasoning/CodeHealerAgent.py` | `CSTHealerMixin, AtomicExecutionMixin, SovereignBaseAgent` | COMPLIANT | COMPLIANT (CSTHealerMixin LEFT) | PASS | YES |
| CodeValidatorAgent | `agentic_core/L5_safety/reasoning/CodeValidatorAgent.py` | `AtomicExecutionMixin, SovereignBaseAgent` | COMPLIANT | COMPLIANT | PASS | YES |
| CognitiveDispositionAgent | `agentic_core/L5_safety/reasoning/CognitiveDispositionAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | NO |
| ComplexityAnalyzerAgent | `agentic_core/L5_safety/reasoning/ComplexityAnalyzerAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| CompositeGuardrailAgent | `agentic_core/L5_safety/reasoning/CompositeGuardrailAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| ConfigurationSecurityGuardrailAgent | `agentic_core/L5_safety/reasoning/ConfigurationSecurityGuardrailAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| ConstitutionalReviewerAgent | `agentic_core/L5_safety/reasoning/ConstitutionalReviewerAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| CostGovernorAgent | `agentic_core/L5_safety/reasoning/CostGovernorAgent.py` | `AtomicExecutionMixin, SovereignBaseAgent` | COMPLIANT | COMPLIANT | PASS | YES |
| CredentialScannerAgent | `agentic_core/L5_safety/reasoning/CredentialScannerAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| DDDAlignmentAgent | `agentic_core/L5_safety/reasoning/DDDAlignmentAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| DependencyPruningAgent | `agentic_core/L5_safety/reasoning/DependencyPruningAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| DocumentationAgent | `agentic_core/L5_safety/reasoning/DocumentationAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| DuplicateCodeDetectorAgent | `agentic_core/L5_safety/reasoning/DuplicateCodeDetectorAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| DynamicSealAgent | `agentic_core/L5_safety/reasoning/DynamicSealAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| FileClassificationAgent | `agentic_core/L5_safety/reasoning/FileClassificationAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| GenerativeGuardAgent | `agentic_core/L5_safety/reasoning/GenerativeGuardAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| GitHygieneAgent | `agentic_core/L5_safety/reasoning/GitHygieneAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| GitSafetyHandlerAgent | `agentic_core/L5_safety/reasoning/GitSafetyHandlerAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | NO |
| GovernanceAgent | `agentic_core/L5_safety/reasoning/GovernanceAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| GravityLeakRepairAgent | `agentic_core/L5_safety/reasoning/GravityLeakRepairAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| HealValidatorAgent | `agentic_core/L5_safety/reasoning/HealValidatorAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| HierarchyAgent | `agentic_core/L5_safety/reasoning/HierarchyAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| HygieneGuardianAgent | `agentic_core/L5_safety/reasoning/HygieneGuardianAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| InterfaceBoundaryAgent | `agentic_core/L5_safety/reasoning/InterfaceBoundaryAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| L5SafetyExerciserAgent | `agentic_core/L5_safety/reasoning/L5SafetyExerciserAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| LocationAgent | `agentic_core/L5_safety/reasoning/LocationAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| LocationHealerAgent | `agentic_core/L5_safety/reasoning/LocationHealerAgent.py` | `AtomicExecutionMixin, SovereignBaseAgent` | COMPLIANT | COMPLIANT | PASS | YES |
| LocationValidatorAgent | `agentic_core/L5_safety/reasoning/LocationValidatorAgent.py` | `AtomicExecutionMixin, SovereignBaseAgent` | COMPLIANT | COMPLIANT | PASS | YES |
| MCPGuardianAgent | `agentic_core/L5_safety/reasoning/MCPGuardianAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | NO |
| NamingAgent | `agentic_core/L5_safety/reasoning/NamingAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| NeuralAutoImmuneAgent | `agentic_core/L5_safety/reasoning/NeuralAutoImmuneAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| PIISanitizerAgent | `agentic_core/L5_safety/reasoning/PIISanitizerAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| PineconeSovereignAgent | `agentic_core/L5_safety/reasoning/PineconeSovereignAgent.py` | `AtomicExecutionMixin, SovereignBaseAgent` | COMPLIANT | COMPLIANT | PASS | YES |
| PolicyNeuralAutoImmuneAgent | `agentic_core/L5_safety/reasoning/PolicyNeuralAutoImmuneAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | NO |
| PreCommitSovereignAgent | `agentic_core/L5_safety/reasoning/PreCommitSovereignAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| PredictiveCostAuditorAgent | `agentic_core/L5_safety/reasoning/PredictiveCostAuditorAgent.py` | `AtomicExecutionMixin, SovereignBaseAgent` | COMPLIANT | COMPLIANT | PASS | YES |
| PromptRegistryAgent | `agentic_core/L5_safety/reasoning/PromptRegistryAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | NO |
| RagHealthCheckAgent | `agentic_core/L5_safety/reasoning/RagHealthCheckAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| RedSentinelAgent | `agentic_core/L5_safety/reasoning/RedSentinelAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| RedTeamAgent | `agentic_core/L5_safety/reasoning/RedTeamAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| RegressionOracleAgent | `agentic_core/L5_safety/reasoning/RegressionOracleAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| ReportLocationAgent | `agentic_core/L5_safety/reasoning/ReportLocationAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| ResourceManagerAgent | `agentic_core/L5_safety/reasoning/ResourceManagerAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| RootHygieneAgent | `agentic_core/L5_safety/reasoning/RootHygieneAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| SafetyDetectorAgent | `agentic_core/L5_safety/reasoning/SafetyDetectorAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| SafetyExecutorAgent | `agentic_core/L5_safety/reasoning/SafetyExecutorAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| SafetyInspectorAgent | `agentic_core/L5_safety/reasoning/SafetyInspectorAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| SelfUpdatingSafetyEngineAgent | `agentic_core/L5_safety/reasoning/SelfUpdatingSafetyEngineAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| SovereignActionPlaneAgent | `agentic_core/L5_safety/reasoning/SovereignActionPlaneAgent.py` | `SovereignBaseAgent, IActionPlane` | COMPLIANT | N/A | PASS | YES |
| SprawlInspectorAgent | `agentic_core/L5_safety/reasoning/SprawlInspectorAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| StructuralEngineerAgent | `agentic_core/L5_safety/reasoning/StructuralEngineerAgent.py` | `SovereignBaseAgent, HealerMixin` | COMPLIANT | N/A (HealerMixin RIGHT of base) | PASS | NO |
| StructuralValidatorAgent | `agentic_core/L5_safety/reasoning/StructuralValidatorAgent.py` | `AtomicExecutionMixin, SovereignBaseAgent` | COMPLIANT | COMPLIANT | PASS | YES |
| StructureEnforcerAgent | `agentic_core/L5_safety/reasoning/StructureEnforcerAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| StructureHealerAgent | `agentic_core/L5_safety/reasoning/StructureHealerAgent.py` | `AtomicExecutionMixin, SovereignBaseAgent` | COMPLIANT | COMPLIANT | PASS | YES |
| SystemArchitectAgent | `agentic_core/L5_safety/reasoning/SystemArchitectAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| TerritoryChangeHandlerAgent | `agentic_core/L5_safety/reasoning/TerritoryChangeHandlerAgent.py` | `SovereignBaseAgent, FileSystemEventHandler` | COMPLIANT | N/A | PASS | NO |
| TestCoverageGuardianAgent | `agentic_core/L5_safety/reasoning/TestCoverageGuardianAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| TestGeneratorAgent | `agentic_core/L5_safety/reasoning/TestGeneratorAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | NO |
| TypeHintFixerAgent | `agentic_core/L5_safety/reasoning/TypeHintFixerAgent.py` | `SovereignBaseAgent, ast.NodeTransformer` | COMPLIANT | N/A | PASS | NO |
| TypeMechanicAgent | `agentic_core/L5_safety/reasoning/TypeMechanicAgent.py` | `SovereignBaseAgent, SubAtomicAgent` | COMPLIANT | N/A | PASS | NO |
| UnusedCleanupAgent | `agentic_core/L5_safety/reasoning/UnusedCleanupAgent.py` | `CodeToolRunnerCapability, SovereignBaseAgent` | COMPLIANT | COMPLIANT (Capability LEFT) | PASS | NO |
| input_validation_guardrail | `agentic_core/L5_safety/enforcement/input_validation_guardrail.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| toxic_dependency_auditor | `agentic_core/L5_safety/enforcement/toxic_dependency_auditor_enforcer.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| verification_gate | `agentic_core/L5_safety/enforcement/verification_gate.py` | `AtomicExecutionMixin, HallucinationDetectionMixin, SovereignBaseAgent` | COMPLIANT | COMPLIANT (Mixins LEFT) | PASS | NO |

### L6_observability (8 agents)

| Agent | File | MRO Chain | §8.1 Adapters | §8.3 Safety LEFT | §8.4 MRO Verified | has_heal |
|---|---|---|---|---|---|---|
| AutonomicMonitorAgent | `agentic_core/L6_observability/reasoning/AutonomicMonitorAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| MetricsAgent | `agentic_core/L6_observability/reasoning/MetricsAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| MetricsWitnessAgent | `agentic_core/L6_observability/reasoning/MetricsWitnessAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | NO |
| PerformanceAnalystAgent | `agentic_core/L6_observability/reasoning/PerformanceAnalystAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| ReportingAgent | `agentic_core/L6_observability/reasoning/ReportingAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | YES |
| SovereignObservabilityAgent | `agentic_core/L6_observability/reasoning/SovereignObservabilityAgent.py` | `event_emission_mixin, ContextPropagationMixin, SovereignBaseAgent` | COMPLIANT | COMPLIANT (Mixins LEFT) | PASS | YES |
| TelemetryAgent | `agentic_core/L6_observability/reasoning/TelemetryAgent.py` | `AtomicExecutionMixin, SovereignBaseAgent` | COMPLIANT | COMPLIANT | PASS | YES |
| TracingAgent | `agentic_core/L6_observability/reasoning/TracingAgent.py` | `AtomicExecutionMixin, SovereignBaseAgent` | COMPLIANT | COMPLIANT | PASS | YES |

### apps_lic (13 agents)

| Agent | File | MRO Chain | §8.1 Adapters | §8.3 Safety LEFT | §8.4 MRO Verified | has_heal |
|---|---|---|---|---|---|---|
| DispatchOutreachToolsAgent | `apps_lic/engines/DispatchOutreachToolsAgent.py` | `LICAgentBase` | COMPLIANT | N/A | PASS | NO |
| GovernanceShieldAgent | `apps_lic/engines/GovernanceShieldAgent.py` | `LICAgentBase` | COMPLIANT | N/A | PASS | NO |
| LicS2SupervisorAgent | `apps_lic/engines/LicS2SupervisorAgent.py` | `LICAgentBase` | COMPLIANT | N/A | PASS | NO |
| MessageDiversityValidator | `apps_lic/engines/MessageDiversityValidator.py` | `LICAgentBase` | COMPLIANT | N/A | PASS | NO |
| OutreachAgent (×5) | `apps_lic/engines/OutreachAgent.py` + 4 others | `LICAgentBase` | COMPLIANT | N/A | PASS | NO |
| OutreachSignalRouterAgent | `apps_lic/engines/OutreachSignalRouterAgent.py` | `LICAgentBase` | COMPLIANT | N/A | PASS | NO |
| OutreachValidationExecutorAgent | `apps_lic/engines/OutreachValidationExecutorAgent.py` | `LICAgentBase` | COMPLIANT | N/A | PASS | NO |
| PII_SanitizerSpecialistAgent | `apps_lic/engines/PII_SanitizerSpecialistAgent.py` | `LICAgentBase` | COMPLIANT | N/A | PASS | NO |
| ValidatorAgent | `apps_lic/engines/ValidatorAgent.py` | `LICAgentBase` | COMPLIANT | N/A | PASS | NO |

### apps_rg (4 agents)

| Agent | File | MRO Chain | §8.1 Adapters | §8.3 Safety LEFT | §8.4 MRO Verified | has_heal |
|---|---|---|---|---|---|---|
| ContentQualityAgent | `apps_rg/engines/ContentQualityAgent.py` | `RGAgentBase` | COMPLIANT | N/A | PASS | NO |
| DispatchResumeToolsAgent | `apps_rg/engines/DispatchResumeToolsAgent.py` | `RGAgentBase` | COMPLIANT | N/A | PASS | NO |
| ProactiveAgent | `apps_rg/engines/ProactiveAgent.py` | `RGAgentBase` | COMPLIANT | N/A | PASS | NO |
| RgReflectionAgent | `apps_rg/engines/RgReflectionAgent.py` | `RGAgentBase` | COMPLIANT | N/A | PASS | NO |

### apps_shared (1 agent)

| Agent | File | MRO Chain | §8.1 Adapters | §8.3 Safety LEFT | §8.4 MRO Verified | has_heal |
|---|---|---|---|---|---|---|
| AppBase | `apps_shared/reasoning/AppBase.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | NO |

### knowledge (1 agent)

| Agent | File | MRO Chain | §8.1 Adapters | §8.3 Safety LEFT | §8.4 MRO Verified | has_heal |
|---|---|---|---|---|---|---|
| SovereignRAGManagerAgent | `agentic_core/knowledge/reasoning/SovereignRAGManagerAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | NO |

### runtime (1 agent)

| Agent | File | MRO Chain | §8.1 Adapters | §8.3 Safety LEFT | §8.4 MRO Verified | has_heal |
|---|---|---|---|---|---|---|
| DiscoveredAgent | `agentic_core/runtime/reasoning/DiscoveredAgent.py` | `SovereignBaseAgent` | COMPLIANT | N/A | PASS | NO |

---

## Uniform Per-Agent Capability Matrix (All 150 ACTIVE agents)

The following capabilities are **uniformly MISSING** across **all 150 ACTIVE agents** because the underlying V15 typed artifact infrastructure does not exist at the framework level:

| ID | Capability | Status (all 150 agents) | Gating Invariant |
|---|---|---|---|
| 2.1 | Validator emits SurgicalManifest | **MISSING** | P2, P3, P4, P6 |
| 2.2 | Validator Safety Emulation (No Side-Effect) | **MISSING** | P2 |
| 2.3 | Validator Permission Check (L5) | **MISSING** | P5 |
| 2.4 | Boundary schema validation | **MISSING** | P6 |
| 2.5 | Pipe order enforced (1..10) | **MISSING** | P1 |
| 2.6 | ≥2 hash mismatches → human escalation | **MISSING** | P5 |
| 2.7 | Ternary Resolution (APPROVE/REJECT/MODIFY) | **MISSING** | P5 |
| 2.8 | AGGREGATE→Heal boundary (impact_scope, rollback_vector, risk_delta) | **MISSING** | P1 |
| 3.4 | Human Evidence Pack Generation | **MISSING** | P4 |
| 3.7 | Policy Challenge/Exception Loop | **MISSING** | P5 |
| 5.1 | Dedupe uses SHA-256 | **MISSING** | P2 |
| 5.2 | Error signature (type+node+vector_clock) | **MISSING** | P4 |
| 5.3 | Correlated collapse (Root Scope Pinning) | **MISSING** | P3 |
| 5.4 | L6 Self-Healing Trigger Emission | **MISSING** | P1 |
| 5.5 | Signal Correlation & Deduplication Artifact | **MISSING** | P2, P4 |
| 6.5 | RAG Artifact Chain Enforced | **MISSING** | P4 |
| 6.8 | Memory Hypostate Persistence | **MISSING** | P2 |
| 7.2 | Artifact Guard (Replay Comparison) | **MISSING** | P5 |
| 7.2.1 | Artifact Guard (Signature Verification) | **MISSING** | P5 |
| 7.4 | GuardianArtifact Emission (Signed) | **FAIL** | P5 — `GuardianArtifact` exists but lacks required fields |
| 9.1 | Shared mixins generic only | **COMPLIANT** | — Mixins (`AtomicExecutionMixin`, `CSTHealerMixin`, `TracingMixin`, etc.) contain only generic infrastructure tools |
| 9.2 | heal() domain reasoning only | **COMPLIANT** | P3 — agents with `has_heal=YES` (88/150) contain domain-specific logic in `heal()` methods |
| 9.3 | No delegation to adapters/orchestrators | **COMPLIANT** | — No adapter pattern detected in MRO chains |
| 11.1 | TokenCap & Perms Artifacts | **MISSING** | P1 |
| 12.1 | Inter-agent schema validation | **MISSING** | P6 |
| 12.2 | Side-effect registry | **MISSING** | P3 |
| 12.3 | Read-Only Boundary Enforcement (L0, L4, L6) | **MISSING** | P3 — No typed enforcement preventing L0/L4/L6 state mutation |
| 13.1 | Semantic Clock Implementation | **FAIL** | P2 — Wall-clock `datetime.utcnow()` used instead of Semantic Clock |
| 15.1 | Tier III Evacuation Ready | **MISSING** | P1 |
| 15.2 | Cognitive Diff Bundle Generation | **MISSING** | P4 |
| 15.5 | Trace ID format `^CC3AL1-[0-9A-F]{8}$` | **FAIL** | UUID4 format used instead |

### §8 MRO Summary (Per-Agent)

| Check | COMPLIANT | FAIL | Notes |
|---|---|---|---|
| §8.1 Adapters prohibited | 150/150 | 0 | No adapter patterns in MRO |
| §8.2 Mixins for composition | 150/150 | 0 | All composition via mixins/base classes |
| §8.3 Safety mixins LEFT | 150/150 | 0 | Where safety mixins present, always LEFT of `SovereignBaseAgent` |
| §8.4 MRO via discovery | 150/150 | 0 | All MRO signatures from AST-verified discovery |
| §8.5 MRO violation = fail | 0 violations | 0 | No MRO violations detected |

---

# SECTION 3 — FORENSIC SUMMARY

| Forensic Summary | |
|---|---|
| Total capabilities evaluated | 15 (§1–§15), comprising 63 global sub-capabilities + 31 per-agent capability checks × 150 agents |
| Global compliance | **1.6%** (1 COMPLIANT / 63 sub-capabilities) |
| ACTIVE agents audited | 150 |

### Per-Agent Compliance Table

| Agent Layer | Agent Count | §8 MRO Compliance % | §9 Compliance % | Overall (all caps) % | FAIL Count | Critical Gates Violated |
|---|---|---|---|---|---|---|
| L0_maintenance | 6 | 100% | 100% | 9.7% | 3 (§7.4, §13.1, §15.5) | P1, P2, P5 |
| L1_cognition | 11 | 100% | 100% | 9.7% | 3 | P1, P2, P5 |
| L2_execution | 9 | 100% | 100% | 9.7% | 3 | P1, P2, P5 |
| L3_orchestration | 13 | 100% | 100% | 9.7% | 3 | P1, P2, P5 |
| L4_state | 6 | 100% | 100% | 9.7% | 3 | P1, P2, P5 |
| L5_safety | 77 | 100% | 100% | 9.7% | 3 | P1, P2, P5 |
| L6_observability | 8 | 100% | 100% | 9.7% | 3 | P1, P2, P5 |
| apps_lic | 13 | 100% | 100% | 9.7% | 3 | P1, P2, P5 |
| apps_rg | 4 | 100% | 100% | 9.7% | 3 | P1, P2, P5 |
| apps_shared | 1 | 100% | 100% | 9.7% | 3 | P1, P2, P5 |
| knowledge | 1 | 100% | 100% | 9.7% | 3 | P1, P2, P5 |
| runtime | 1 | 100% | 100% | 9.7% | 3 | P1, P2, P5 |

### Non-ACTIVE Agents

| Status | Count | Reason |
|---|---|---|
| INVALID | 40 | All 40 entries have `agent_name: "Unknown"` and empty `file_path` — SSOT candidates in `agent_discovery_full.json` without `file` field. Layer distribution: L0_maintenance (6), L1_cognition (12), L2_execution (10), L3_orchestration (12), L4_state (7), L5_safety (18), L5_safety (continuation from above counts to 40 total across layers). |
| GHOST | 0 | — |
| SYNTAX_ERROR | 0 | — |
| ZOMBIE | 0 | — |

### Discovery Infrastructure Defects

| Defect | Severity | Evidence |
|---|---|---|
| `forensic_discovery_prep.py` imports from nonexistent `agentic_core.utils.ssot_discovery_validator` | FAIL | Script line 50–52 |
| Discovery script expects `path`/`name` fields but SSOT uses `file`/`class_name` | FAIL | Script lines 267–269 vs `agent_discovery_full.json` schema |
| No known-good hash for discovery script in `structure_blueprint.py` | FAIL | §0 precondition |
| Discovery output schema does not conform to §0 strict schema | FAIL | Missing `identity`, `integrity_hash`, `mixins`, `ssot_validation` |

### Audit Integrity Confirmations

| Confirmation | |
|---|---|
| No remediation language generated | ✓ |
| No out-of-scope references | ✓ |
| Evaluation bounded to discovery JSON + SSOT + P1–P6 only | ✓ |
| No fixes, plans, recommendations, or refactors proposed | ✓ |
| All evidence locations cite file paths and symbols | ✓ |
| Status vocabulary restricted to COMPLIANT / MISSING / FAIL | ✓ |

## Gap Register

| Gap | Priority | Impact | Status |
|------|----------|--------|---------|
| [Gap 1] | High | Critical | Open |
| [Gap 2] | Medium | Moderate | In Progress |

---

## Execution Plan

1. **Phase 1**: Analysis and Planning
2. **Phase 2**: Implementation
3. **Phase 3**: Testing and Validation
4. **Phase 4**: Documentation and Cleanup

---

