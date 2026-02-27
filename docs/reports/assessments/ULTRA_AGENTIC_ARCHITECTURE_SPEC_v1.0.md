# ULTRA_AGENTIC_ARCHITECTURE_SPEC_v1.0

**Classification:** Authoritative Control-Plane Contract
**Status:** CANONICAL — Supersedes all prior architecture documents
**Method:** Ontology extraction → conflict resolution → canonical spine consolidation. Zero text merging. Zero invariant loss.
**Scope:** This document is the single authoritative source for all architecture requirements, invariants, compliance criteria, and enforcement protocols.

---

# PHASE 1 — ONTOLOGY EXTRACTION

## 1.1 Process Mapping Ontology

| ID | Concept | Layer | Primitive Type | Enforcement | Determinism | Mutation Auth | Replay | Artifact | Boundary |
|----|---------|-------|---------------|-------------|-------------|---------------|--------|----------|----------|
| PM-01 | apps_* zero authority | apps_* | Authority Rule | Diagram line 7 | None at emission | None | None | {intent_delta, tool_requests[], state_diff_proposal} | Cannot approve/execute/certify |
| PM-02 | L1 propose-only | L1 | Layer Invariant | Sovereignty Matrix L305 | LLM bounded; drift detection | None | None | U0 UserPrompt | Cannot approve/execute |
| PM-03 | L0 route-only | L0 | Layer Invariant | Sovereignty Matrix L306 | Ruleset+ML; registry hash in digest | None | None | InstructionPacket | Cannot evaluate/execute |
| PM-04 | L5 certify-only | L5 | Layer Invariant | Sovereignty Matrix L307 | COMPLIANCE HASH/STAMP | None | None | SandboxEnvelope | Sole certification authority |
| PM-05 | L2 execute-only | L2 | Layer Invariant | Sovereignty Matrix L308 | W-DETERMINISM-DIGEST; double-run identical | UWG sole | replay_mode blocks un-transcripted calls | SandboxEnvelope→ToolTranscript | Sig verified before execution |
| PM-06 | L4 persist-only | L4 | Layer Invariant | Sovereignty Matrix L309 | Write-once content-hash keyed | None (UWG-routed) | None | L4A/L4B/L4C snapshots | Never authorizes/executes |
| PM-07 | L6 observe-only | L6 | Layer Invariant | Sovereignty Matrix L310 | Telemetry deterministic | None | None | DPOPair; anomaly signal | No write authority |
| PM-08 | Upward mutation forbidden | All | Authority Rule | Sovereignty Matrix L311 | N/A | N/A | N/A | N/A | No layer commands above |
| PM-09 | UWG sole mutation chokepoint | L2 | Mutation Rule | Runtime block all non-gateway writes L190 | All writes logged | UWG only | Transcript includes side-effects | ToolCall→ToolResult | Non-UWG writes hard-blocked |
| PM-10 | SovereignLLMGateway sole LLM seam | External | Authority Rule | AST blocks direct SDK imports L85-86 | Deterministic invocation logs | N/A | ReplayEnvelope; stored response | AgentExecutionProfile | CI fails on AST violation |
| PM-11 | AgentExecutionProfile enforcement | L0 | Authority Rule | Registry; unregistered→HARD FAIL L113 | Registry hash in digest | None | None | Profile enum | LOW=deterministic; HIGH=LLM via Gateway |
| PM-12 | InstructionPacket | L0→L2/L3 | Artifact Schema | HMAC-SHA256 canonical JSON; boundary_verifier L44 | trace_id+policy_hash | None | plan_hash in replay_key | [trace_id,policy_hash,route_mode,allowed_tools[],sig] | Unsigned→HARD FAIL |
| PM-13 | SandboxEnvelope | L2 entry | Artifact Schema | verify_sandbox_envelope SignatureBoundaryError L265 | replay_key=trace+plan+transcript | None | HMAC-SHA256+ReplayEnvelope | [InstructionPacket,ToolBudget] | Sig verified before exec |
| PM-14 | PTC ToolContracts | L2 exec | Artifact Schema | STDOUT-only,redacted,byte caps L266 | Deterministic schema | UWG | ToolTranscript | ToolCall(id,args)→ToolResult(exit,stdout) | Max bytes enforced |
| PM-15 | ExecutionTrace | L6/L4 | Artifact Schema | HashChainAuditLog GENESIS+seal() | prev_hash chain; replay_key | None | replay_key=trace+plan+transcript | [trace_id,plan_hash,...,prev_hash,replay_key] | Immutable append-only |
| PM-16 | HumanDecisionArtifact | Path D | Artifact Schema | L5 re-clear mandatory L268 | original_plan_hash ref | None | N/A | [trace_id,...,action,structured_patch,reviewer_sig] | MODIFY_DIFF→original_plan_hash; re-clear L5 |
| PM-17 | HealCheckResult | L2.3 | Artifact Schema | CONTRACT_VERSION=2 | needs_llm_escalation deterministic | None | None | [check_id,status,changes_made(sorted),...] | Opt-in only; policy failures→False |
| PM-18 | EscalationContext | L2.3 SSOT | Artifact Schema | Built from HealCheckResult ONLY | sha256(check_id:retry)[:12] | None | None | [check_id,healer_name,...,trace_id] | ONLY source for FailureSignal |
| PM-19 | FailureSignal | L2.3→Router | Artifact Schema | .to_healing_input()→HealingInput | Deterministic from EscalationContext | None | None | [source_agent,...,blast_radius] | NO_TIERING agents MUST emit |
| PM-20 | HealingDecision | Router out | Artifact Schema | route_healing_tier() chokepoint | X=0.75 LOCAL,Y=0.40 QWEN,<Y GEMINI | None | None | [heal_confidence,tier,reason_codes] | retry>=3 forces GEMINI |
| PM-21 | EmbeddingResult | L2 RAG | Artifact Schema | C0 informational only L279 | score_round6; content_hash | None | None | [content_hash,score,row_idx,artifact_hash] | Never drives routing |
| PM-22 | SeedEmbeddingPackManifest | Plan B | Artifact Schema | SHA-256 match at boot L338 | matrix_hash integrity | None | None | [seed_ver,model_ver,...,matrix_hash] | Mismatch→EmbeddingIntegrityError |
| PM-23 | DPOPair | L6 | Artifact Schema | Deterministic from Path D | Sorted (control_hash,candidate_hash) | None | None | [example_id,human_decision,reasons] | Clamp [0.1,2.0]; delta ±0.1 |
| PM-24 | ChangePackage | MetaLearning | Artifact Schema | proposal_only=True default L282 | timestamp_utc:int | None until ApprovalGate | None | [source,target,changes,confidence,...] | Dual injection for Stage B |
| PM-25 | JSON canonicalization | Global | Mutation Rule | Applied before HMAC L263 | Alpha key sort,UTF-8,zero whitespace | N/A | N/A | N/A | Non-canonical bytes→INVALID |
| PM-26 | Healing tier single chokepoint | L2.3 | Routing Rule | route_healing_tier(); TIERING_ALLOWLIST frozenset L216 | Deterministic thresholds | None | HealingDecision | N/A | Non-allowlisted→emit FailureSignal |
| PM-27 | Model resolution via Gateway | L2.3/GW | Routing Rule | Symbolic model_id only; concrete in Gateway L225 | Deterministic binding | None | InvocationRecord | N/A | Direct SDK prohibited |
| PM-28 | Meta-learning proposal default | ML Bus | Promotion Rule | proposal_only=True; dual injection L336 | No activation without dual inject | VersionStore+Activator | ChangePackage | N/A | Stage B requires approval_gate |
| PM-29 | DPO bounded | L6/ML | Monitoring Rule | Clamp [0.1,2.0]; delta ±0.1 L337 | Sorted for replay | None | DPOPair | N/A | Oscillation→auto-reject |
| PM-30 | Embedding integrity boot | Factory | CI Enforcement Rule | SHA-256 match at instantiation L338 | Hash deterministic | None | SeedManifest | N/A | Mismatch→hard-fail |
| PM-31 | Replay strictness | L2 | Replay Rule | Un-transcripted call→HARD FAIL L244 | Nondeterminism captured or blocked | N/A | ToolTranscript | N/A | No hidden IO in replay |
| PM-32 | Determinism digest | L2 | CI Enforcement Rule | ONE stable W-DIGEST per phase L237 | Double-run identical | N/A | W-DIGEST | N/A | Multiple digests→FAIL |
| PM-33 | Negative control test | CI | CI Enforcement Rule | NEGCTRL_TAMPER=1→XFAIL strict L339 | Tamper simulation | N/A | N/A | N/A | Restore must PASS |
| PM-34 | Healed plans re-clear L5 | L5 | Authority Rule | RE-CLR mandatory L163; old sigs invalid L318 | New plan_hash | None | New SandboxEnvelope | N/A | No old signature reuse |
| PM-35 | C0 informational-only | L1/L4 | Authority Rule | routing_hash excludes c0 L70 | Containment deterministic | None | EmbeddingResult | N/A | Never a decision input |
| PM-36 | ML pipeline stage order | ML | Promotion Rule | Fixed stages 1-9 L287-301; L0→RAG→L1→L5 | Stage 7 validators+OscillationDetector | ApprovalGate+VersionStore | Snapshot;ChangePackage | N/A | Stage 9 only if not proposal_only |
| PM-37 | CommitProofInvariant | CI | CI Enforcement Rule | Bind to true impl commit L283 | HEAD only if naturally contains impl | N/A | N/A | N/A | No churn commits |
| PM-38 | No skip safety gates | L5 | Authority Rule | Un-governed exec prevented L315 | N/A | N/A | N/A | N/A | All non-PATH-A→L5 |
| PM-39 | ToolBudget caps | L2 | Authority Rule | budget_enforcer.py:89 | ToolBudget fields | N/A | SandboxEnvelope | N/A | Exceeded→termination |
| PM-40 | EMBEDDING_ENABLED kill-switch | Factory | CI Enforcement Rule | embedding_factory.py:24-30; fail-closed | Hash at instantiation | None | None | N/A | False→EmbeddingDisabledError |

## 1.2 W6 Forensic Audit Ontology

| ID | Concept | Layer | Primitive Type | Enforcement | Determinism | Mutation Auth | Replay | Artifact | Boundary |
|----|---------|-------|---------------|-------------|-------------|---------------|--------|----------|----------|
| W6-01 | 48-arrow authority classification | Global | Layer Invariant | Independent re-derivation; 5 classes (S1A) | N/A | N/A | N/A | Arrow inventory | DOWN_EXEC(17),LAT_READ(5),GOV_BOUND(11),EXT_BOUND(3),META_FB(14) |
| W6-02 | InstructionPacket HMAC+ReplayGuard | L0 | Replay Rule | assembly_stage:17-32; crypto_trust:86; single-sighting | HMAC-SHA256 canonical JSON | None | ReplayGuardStore prevents reuse | InstructionPacket | Unsigned→rejected; replay→rejected |
| W6-03 | routing_hash excludes c0_context | Assembly | Determinism Binding | assembly_stage:72-80 CONFIRMED | C0 not hashed→cannot influence route | None | N/A | routing_hash | Embedding present but excluded from routing |
| W6-04 | SandboxEnvelope verify-before-exec | L2 | Authority Rule | boundary_verifier:82-85; execution_gateway:34,53 | Sig cryptographically bound | None | replay_key in envelope | SandboxEnvelope | Invalid sig→execution blocked |
| W6-05 | L5→L2 sole certification path | L5→L2 | Authority Rule | SandboxEnvelope only from L5; S5:53 refs | Certification deterministic | None | Replay_key | SandboxEnvelope | L5 sole producer; L2 verifies |
| W6-06 | apps_rg direct LLM bypass (RED) | apps_rg | Authority Rule | S8/S11: 4 files make direct SDK calls | VIOLATION | Unauthorized | N/A | None | Must route through SovereignLLMGateway |
| W6-07 | apps_shared embedding bypass (RED) | apps_shared | Authority Rule | S10: GlobalcacheStrategy:281, cache_entry_validator:123 | VIOLATION | Unauthorized | N/A | None | Must use create_embedding_client() |
| W6-08 | External weight pull (RED—missing) | External | Authority Rule | A-05: No sig, no L5 cert, no kill-switch | NOT ENFORCED | Not authorized | None | None | REQUIRED: HMAC sig+L5 cert+kill-switch |
| W6-09 | LocalFAISSStore write (RED—skeleton) | L2/Ext | Mutation Rule | A-41: skeleton; writes not implemented | NOT ENFORCED | UWG required | None | None | REQUIRED: UWG+EMBEDDING_ENABLED+SHA-256 |
| W6-10 | ChangePackage HMAC gap (ORANGE) | ML | Replay Rule | A-06: SHA-256 only; no HMAC key | Partial | ApprovalGate | No HMAC replay key | ChangePackage | REQUIRED: HMAC-SHA256 on package_hash |
| W6-11 | L4B heal snapshot HMAC gap (ORANGE) | L4B | Mutation Rule | A-42: IntakeRecord no HMAC; UWG unconfirmed | Partial | UWG unconfirmed | None | IntakeRecord | REQUIRED: HMAC+UWG for L4B write |
| W6-12 | HashChainAuditLog immutability | L2/L4 | Replay Rule | hash_chain_audit_log:117-157; seal(); verify_chain | prev_hash chain; GENESIS; seal() | None | transcript_hash=SHA-256(canonical(all)) | HashChainAuditLog | Sealed; post-seal→RuntimeError; tamper detectable |
| W6-13 | replay_mode blocks network | L2/GW | Replay Rule | SovereignLLMGateway:176-211; stored response only | Stored transcript | None | ReplayEnvelope | N/A | Un-transcripted call in replay→HARD FAIL |
| W6-14 | healing_provider bypass (RED) | L2.3 | Authority Rule | healing_provider_adapters:117-128 bypasses Gateway | VIOLATION | Unauthorized | None | None | REQUIRED: Route through Gateway or document exception |
| W6-15 | route_healing_tier AST-verified | L2.3 | Routing Rule | AST: 2 call sites; tiering_allowlist:21 frozenset | Deterministic | None | HealingDecision | N/A | 2 call sites; frozenset prevents runtime mod |
| W6-16 | Elevator shaft crypto (YELLOW) | L0↔L5 | Replay Rule | A-47/48: ReplayGuard+HMAC confirmed; call-site unwired | boundary_snapshot_hash | None | ReplayGuardStore | EvidencePack | REQUIRED: Explicit sign+verify at call-site |
| W6-17 | UWG at L4 write | L4 | Mutation Rule | filesystem_store:135; system_invariant_scanner:113 | All writes logged | UWG only | ToolNotAllowedError | None | Ledger path must be in _allowed_paths |
| W6-18 | No alternate tier-selection | L2.3 | Routing Rule | S12: 69 hits=enum refs only (NEG EVIDENCE) | N/A | None | N/A | N/A | No bypass of route_healing_tier() |
| W6-19 | needs_llm_escalation dual-gate | L2.3 | Authority Rule | remediation_dispatcher:526; S16:12 refs | Deterministic flag | None | None | None | Allowlist AND flag must pass |
| W6-20 | ChangePackage scope unenforced (YELLOW) | ML | Authority Rule | A-33: label-only; no payload validation | NOT ENFORCED | N/A | N/A | ChangePackage | REQUIRED: kind-scope validator |
| W6-21 | DPO sorted deterministically | L6 | Determinism Binding | determinism.py:206 | Sorted (control_hash,candidate_hash) | None | DPOPair | N/A | Non-deterministic sort→replay mismatch |
| W6-22 | OscillationDetector wired | ML | Monitoring Rule | determinism.py:207; Stage 7 Dampening | Cooldown enforced | None | None | N/A | Oscillation→auto-reject |
| W6-23 | HumanDecision plan_hash binding | Path D | Artifact Schema | human_decision_artifact:46; orchestrator:298 | Bound to original plan | None | None | HumanDecisionArtifact | MODIFY_DIFF→original_plan_hash |
| W6-24 | apps_* ingress schema (YELLOW) | L1 | Artifact Schema | No Pydantic validation at L1 ingress | None at ingress | None | None | {intent_delta,...} | REQUIRED: Pydantic at L1 ingress |
| W6-25 | Embedding containment confirmed | Assembly | Determinism Binding | assembly_stage:72-80; sovereignty_guard:30 | C0 excluded from routing | None | N/A | routing_hash | No C0→route_mode/safety/ToolBudget |
| W6-26 | 9 kill-switches confirmed | Global | CI Enforcement Rule | Section 12.7: all fail-closed | Each independent | N/A | N/A | N/A | No silent fallback on any switch |
| W6-27 | Integer timestamps only | L2/Audit | Determinism Binding | hash_chain: int(time.time()) captured once | Integer; no float drift | None | None | N/A | Float timestamps→FAIL |
| W6-28 | Transcript canonical ordering | L2 | Determinism Binding | canonical_bytes(sort_keys=True); prev_hash chain | Reorder→all subsequent hashes change | None | HashChainAuditLog | N/A | Tamper detectable by chain verify |
| W6-29 | GovernedPayload not frozen (YELLOW) | Assembly | Determinism Binding | assembly_stage:35-82; no frozen=True | Gap—mutable post-init | N/A | N/A | GovernedPayload | REQUIRED: frozen=True |
| W6-30 | Sovereignty: 10/11 confirmed | Global | Layer Invariant | W6+ Revalidation Step 3 | N/A | N/A | N/A | N/A | 1 PARTIAL: apps_rg/shared violations |

## 1.3 v5.4 Capability Framework Ontology

| ID | Concept | Layer | Primitive Type | Enforcement | Determinism | Mutation Auth | Replay | Artifact | Boundary |
|----|---------|-------|---------------|-------------|-------------|---------------|--------|----------|----------|
| V5-01 | P1 Fail-Closed Defaults | Global | Layer Invariant | Default=BLOCK at boundaries | Missing header/token/sig halts | None | None | None | Timeout=reject; degraded=freeze |
| V5-02 | P2 Determinism & Replayability | Global | Replay Rule | Same(payload+policy_hash+context)⇒same plan | Stochastic bounded/logged/excluded | None | payload+policy_hash+context_set | None | Not proven deterministic→excluded |
| V5-03 | P3 No Silent Mutation | Global | Mutation Rule | Only L2 may mutate; write_gateway sole chokepoint | AST enforcement; regex=MISSING | write_gateway.py | None | None | Forbidden primitives in L3-L6 |
| V5-04 | write_gateway.py existence | L2 | Mutation Rule | Must exist with 15 functions; absence=FAIL(P3/P0) | AST scan | write_gateway.py | None | None | write_text,write_bytes,write_json,append_text,open_write,ensure_dir,remove_file,remove_dir,remove_tree,copy_file,move_path,rename_path,touch_file,copy_tree,makedirs |
| V5-05 | FileIo import boundary | L2 | Mutation Rule | file_io_impl.py MUST NOT import in L3-L6 | AST scan | write_gateway only | None | None | Higher layers→write_gateway or MutationIntent |
| V5-06 | P4 Immutable Traceability | Global | Layer Invariant | TraceID mandatory/immutable; all artifacts addressable | TraceID loss=fatal | None | TraceID propagation | All artifacts | Loss of TraceID=fatal |
| V5-07 | P5 Authority Tokenized | Global | Authority Rule | Signed artifacts required; conversational=non-auth | Tokens: scoped,expiring | Capability tokens | None | Capability token | No token=no write authority |
| V5-08 | P5.1 Capability-Gated L2 | L2 | Authority Rule | Single chokepoint; no scattered checks | Typed,deterministic,semantic-clock-bound | Capability token | None | ALLOW/DENY decision artifact | No token→FAIL-CLOSED |
| V5-09 | P6 Zero Trust Between Layers | Global | Layer Invariant | APIs typed/versioned; health binary | Schema conformance | None | None | Typed API | Unknown health=unhealthy |
| V5-10 | SurgicalManifest schema | L2 | Artifact Schema | Validated vs structure_blueprint; LibCST | SHA-256 of canonical ast_snippet | write_gateway | manifest_hash | [schema_ver,correlation_id,node_id,...] | node_id→structure_blueprint; line numbers FORBIDDEN |
| V5-11 | SSOT Binding node_id | L0/L2 | Authority Rule | node_id resolves in structure_blueprint; SHA-256 match | Deterministic SSOT hash | None | None | structure_blueprint.py | Mismatch→ABORT |
| V5-12 | Discovery JSON schema | Global | CI Enforcement Rule | Exact conformance+integrity_hash per agent | git_hash,blueprint_hash | None | None | {meta,ssot_validation,agents[]} | ZOMBIE→IMMEDIATE FAIL |
| V5-13 | EvidencePack schema | L3 HIL | Artifact Schema | Cap 3.4; bidirectional feedback | Bound to trace_id+policy_hash | None | None | [policy_evals,risk_scores,snapshots] | Required at all HIL gates |
| V5-14 | PolicyUpdateProposal | L3 | Artifact Schema | Cap 3.4; emitted on overrides | Bound to trace_id | None | None | PolicyUpdateProposal | Required on every override |
| V5-15 | Knowledge Supervisor (Cap 6.6) | L4 | Monitoring Rule | Low-confidence memory audit | Confidence threshold | None | None | None | Dense retraining trigger |
| V5-16 | Guardian split: Guardrail+Artifact | L5 | Authority Rule | Cap 7.2: Policy guard + Signatures/Replay guard | Each output deterministic | None | Replay Comparison | None | Both must be traversed |
| V5-17 | L6 Response Handler→L2 Healing | L6 | Monitoring Rule | Cap 5.4: triggers healing from L6 signals | Signal threshold deterministic | None | None | None | Distinct from L6 archival |
| V5-18 | Tiered Vigilance I/II/III | L6 | Monitoring Rule | Cap 15.1: Tier III=Evacuation(Freeze/Exfil) | Tier threshold deterministic | None | None | None | Tier III→System Freeze |
| V5-19 | Cognitive Diff Bundle | L6 | Artifact Schema | Cap 15.2: intended vs actual execution diff | Bound to trace_id | None | None | CognitiveDiffBundle | Required for ALL incidents |
| V5-20 | Forensic Trace Buffer | L6 | Artifact Schema | Cap 15.3: ephemeral high-fidelity capture | Sealed post-incident | None | None | ForensicTraceBuffer | Distinct from standard storage |
| V5-21 | Prompt ownership rules | core/apps | Authority Rule | §0.7: system prologues MUST NOT in apps_* | AST scan; regex=MISSING | None | prompt_hash lineage | None | Direct provider calls from apps_*=FAIL |
| V5-22 | AST governance tests mandatory | CI | CI Enforcement Rule | 3 specific test files required (v5.4.3) | Zero-violation ceilings | None | None | None | Regex enforcement=MISSING |
| V5-23 | L0 seam allowlist | L0 | Authority Rule | 3 seams only for importlib L1-L6 loads | AST scan | None | None | None | Other L0 upward imports→FAIL(P6/P0) |
| V5-24 | Healing re-entry via L0 seam | L2.3/L0 | Routing Rule | validation_orchestrator→safety_enforcement_seam; FileIo | AST: bare open("w")=FAIL | FileIo via seam | None | None | Approval via L0 seam; apply via FileIo |
| V5-25 | Meta-learning activation gate | ML | Promotion Rule | §16 blocked until P0 closures | Dual injection required | VersionStore+Activator | ReplayValidator+Shadow | ChangePackage | Governed,versioned L4,re-enters L0 |
| V5-26 | Discovery integrity abort | CI | CI Enforcement Rule | SHA-256 of discovery script vs blueprint | Hash deterministic | None | None | None | Mismatch→ABORT→IMMEDIATE FAIL |
| V5-27 | Abort-on-critical triggers | CI | CI Enforcement Rule | ZOMBIE/GHOST/INVALID→emit P0 gaps and STOP | N/A | None | None | None | No compliance % after abort |
| V5-28 | Capability token scope | L2 | Authority Rule | Min: permitted ops+targets+max invocations | Semantic-clock bound | Capability token | None | Capability token | Prerequisite for governed improvement |
| V5-29 | apps_* boundary enforcement | apps_* | Authority Rule | MUST NOT mutate state; same L2 chokepoint | AST enforcement | write_gateway via cap-gated L2 | None | None | Untrusted caller; same chokepoints |
| V5-30 | All artifacts typed | Global | Artifact Schema | TypedDict or Pydantic; §1.7 | Schema version | None | None | TypedDict/Pydantic | Free-form dict=NOT valid artifact |

---

# PHASE 2 — CROSS-DOCUMENT CONFLICT RESOLUTION

All conflicts from source documents have been resolved with the following canonical resolutions. No external references are required.

| Concept | Canonical Resolution | Rationale |
|---------|-------------------|-----------|
| Mutation chokepoint identity | **write_gateway.py is the implementation artifact; UWG is the architectural concept. Same single-spine authority.** | write_gateway.py MUST implement UWG contract. No substantive conflict. |
| Replay key binding | **INPUT replay = payload+policy_hash+context_set. OUTPUT replay = trace_id+plan_hash+transcript_hash.** | Both are required. Full spec includes both bindings. No invariant dropped. |
| C0 containment | **C0 informational only; never mutates routes/safety/tiers.** | Fully consistent across all sources. |
| apps_* authority boundary | **apps_* MUST NOT bypass prompt_governance or call LLM directly.** | Rule stands unchanged; violations must be fixed. |
| Meta-learning activation | **proposal_only=True always; Stage B = dual injection; ChangePackage MUST have HMAC-SHA256.** | All additive; combined definition includes all constraints. |
| Healing re-entry path | **(1) approval via safety_enforcement_seam.py, (2) apply/rollback via FileIo.save_file(), (3) tier via route_healing_tier() only, (4) LLM via SovereignLLMGateway only.** | v5.4 V5-24 provides strictest additive requirements. |
| L5 Guardian structure | **L5 has exactly two sub-gates: (1) Guardrail Guard (policy), (2) Artifact Guard (sig+replay). Both traversed for certification.** | v5.4 V5-16 provides finer decomposition; consistent with others. |
| Determinism enforcement | **All additive: PM = artifact binding, W6 = code proof, v5.4 = invariant statement.** | All consistent; combined definition is union. |
| CI enforcement scope | **Canonical CI = PM runtime AST + W6 S1-S17 scans + v5.4 mandatory test files.** | All additive; no conflict. |
| ChangePackage scope | **ChangePackage MUST include kind-scope validator rejecting proposals targeting wrong layers.** | Required hardening identified; canonical rule defined. |
| Artifact typed schema | **Every PM artifact MUST be TypedDict/Pydantic per V5-30 universal rule.** | V5-30 = universal rule; consistent across sources. |
| GovernedPayload immutability | **GovernedPayload MUST be frozen=True (dataclass frozen).** | Required hardening; canonical rule defined. |
| External boundary writes | **(1) A-05 REQUIRES HMAC sig+L5 cert+kill-switch before L4 write. (2) A-41 REQUIRES UWG+EMBEDDING_ENABLED+SHA-256 when implemented.** | Both P0 blockers; canonical requirements defined. |
| L4B heal snapshot integrity | **IntakeRecord MUST have HMAC-SHA256. UWG MUST be confirmed for L4B write path.** | Required hardening; canonical rule defined. |

---

# PHASE 3 — ULTRA ARCHITECTURE CONTROL SPINE

## SPINE 1: CONTROL SPINE (L0–L6 Ownership + Chokepoints)

**Canonical definition:** Each layer has exactly ONE role. No layer may perform the role of another. Upward mutation is forbidden.

| Invariant | Enforcement Location | Failure Mode | Proof Mechanism |
|-----------|---------------------|--------------|------------------|
| apps_* zero authority: emits {intent_delta, tool_requests[], state_diff_proposal} only | L1 ingress Pydantic validation (W6-24 REQUIRED) | Reject malformed payload | Pydantic schema; L0 trace_id assignment |
| L1 propose-only: cannot approve or execute | Layer Sovereignty Matrix; no write primitives in L1 | Write attempt → UWG ToolNotAllowedError | AST scan: zero write primitives in L1 tree |
| L0 route-only: cannot evaluate rules or execute | Layer Sovereignty Matrix; InstructionPacket producer only | Execution attempt → architectural violation | AST scan: L0 produces InstructionPacket; no execution gateway calls |
| L5 sole certification: two sub-gates (Guardrail Guard + Artifact Guard) | SandboxEnvelope produced only by L5; boundary_verifier:82-85 | Invalid SandboxEnvelope → SignatureBoundaryError | W6 S5 scan (53 refs); execution_gateway:34,53 |
| L2 execute-only: all execution is UWG-mediated, SandboxEnvelope-gated | UWG runtime block; SandboxEnvelope verified before execution | Non-UWG write → ToolNotAllowedError; unsigned → blocked | W6 S3 (17 refs); W6 S5 (53 refs) |
| L4 persist-only: never authorizes, never executes | filesystem_store:135 UWG-routed; no LLM calls | L4 LLM call → violation; unauthorized write → violation | W6 S8 scan; UWG confirmed |
| L6 observe-only: no mutation authority | No write primitives; DPOPair is proposal-only | Write attempt → UWG ToolNotAllowedError | test_l6_purity.py (V5-22) |
| Upward mutation forbidden across all layers | Layer Sovereignty Matrix; AST boundary scan | Cross-layer upward mutation → HARD FAIL | test_authority_boundaries.py (V5-22); AST cycle detection |
| SovereignLLMGateway sole outbound LLM seam | AST blocks direct SDK imports; CI fails on violation | Direct SDK import → CI build failure | W6 S1 (2 production sites); S8/S11 violations documented |
| AgentExecutionProfile: all agents registered | AgentExecutionProfileRegistry; hash in digest | Unregistered agent → SovereigntyViolation | SovereignLLMGateway:176-211 |
| L0 importlib seam allowlist: 3 seams only | AST scan of L0 module tree | Non-allowlisted upward import → FAIL (P6/P0) | safety_enforcement_seam.py, mutation_protocol.py, intent_router.py |
| 9 kill-switches all fail-closed | Each switch independently enforced (W6-26 Section 12.7) | Silent fallback → violation | EMBEDDING_ENABLED, SovereigntyViolation, L5 HARD STOP, proposal_only, ApprovalGate, UWG, REJECT, needs_llm_escalation, TIERING_ALLOWLIST |

## SPINE 2: EXECUTION SPINE (Single Execution Authority Boundary)

**Canonical definition:** L2 is the sole execution layer. All execution passes through a single capability-gated chokepoint. SandboxEnvelope verification is mandatory before any side-effect.

| Invariant | Enforcement Location | Failure Mode | Proof Mechanism |
|-----------|---------------------|--------------|------------------|
| L2 is sole execution authority | L2 execution core; SandboxEnvelope verified at boundary | Non-L2 execution → architectural FAIL | boundary_verifier:82-85; execution_gateway:34,53 |
| SandboxEnvelope HMAC-SHA256 verified before any execution | boundary_verifier.py verify_sandbox_envelope() | Invalid sig → SignatureBoundaryError → blocked | W6-04; W6 S5 (53 refs) |
| Capability token required at L2 boundary (P5.1) | Single chokepoint; no scattered checks | No token → FAIL-CLOSED; every invocation → ALLOW/DENY artifact | V5-08; typed decision artifact emitted |
| ToolBudget caps enforced post-verify | budget_enforcer.py:89 | Exceeded budget → immediate termination | SandboxEnvelope ToolBudget field |
| PTC ToolCall→ToolResult strict schema | STDOUT-only; redacted; byte caps | Schema violation → reject | PM-14 |
| Sandbox isolation: zero durable damage on failure | Snapshot revert on failure; FREEZE clean state | Failure outside sandbox → UWG block | L2 P1:INITIALIZATION freeze |
| All non-PATH-A execution MUST pass through L5 first | L5 certification required for Paths B/C/D | Unverified execution → no SandboxEnvelope → blocked | PM-38; W6-05 |
| Healed plans MUST re-clear L5; old signatures invalid | RE-CLR mandatory; new plan_hash post-re-clear | Old signature reuse → rejection | PM-34; human_decision_artifact original_plan_hash |

## SPINE 3: MUTATION SPINE (Exclusive Mutation Locus + Write Gateway)

**Canonical definition:** write_gateway.py (implementing UWG contract) is the sole durable-mutation authority for the entire system. No layer outside L2_execution may perform durable writes except through write_gateway or an approved L0 seam.

| Invariant | Enforcement Location | Failure Mode | Proof Mechanism |
|-----------|---------------------|--------------|------------------|
| write_gateway.py is sole mutation chokepoint | agentic_core/L2_execution/tools/write_gateway.py | Absence → FAIL (P3/P0) | V5-04; must contain 15 functions |
| Runtime block of ALL non-gateway FS/DB/Vector writes | UWG ToolNotAllowedError on non-allowed paths | Non-UWG write → ToolNotAllowedError | W6-17; system_invariant_scanner:113 |
| Forbidden mutation primitives in L3/L4/L5/L6 | AST governance test: test_intent_emission_no_mutation.py | Primitive detected → zero-violation ceiling breach → CI FAIL | V5-03; V5-22 |
| FileIo (file_io_impl.py) MUST NOT be imported in L3-L6 | AST scan | Import detected → FAIL | V5-05 |
| Higher layers route mutations via: (a) MutationIntent→L0 intent_router→L2 or (b) write_gateway.* if inside L2 | L0 intent_router.py; write_gateway.py | Direct mutation primitive → FAIL | V5-03 |
| L4 writes UWG-routed | filesystem_store:135 | Non-UWG L4 write → ToolNotAllowedError | W6-17 |
| L4B heal snapshot writes require HMAC + UWG confirmation | IntakeRecord HMAC-SHA256; UWG path | No HMAC → integrity gap; no UWG → unauthorized | W6-11 REQUIRED hardening |
| External FAISS writes (when implemented) require UWG + EMBEDDING_ENABLED + SHA-256 | LocalFAISSStore (future) | Non-UWG FAISS write → blocked | W6-09 REQUIRED when implemented |
| External weight pull requires HMAC sig + L5 cert + kill-switch | External Model Registry ingress (future) | No sig → blocked; no cert → blocked | W6-08 REQUIRED P0 |
| GovernedPayload MUST be frozen=True post-assembly | assembly_stage.py dataclass | Mutable post-init → determinism gap | W6-29 REQUIRED hardening |

## SPINE 4: ARTIFACT SPINE (Typed Artifact Registry + Emission Rules)

**Canonical definition:** Every named artifact in the system MUST be a TypedDict or Pydantic model. Free-form dicts are not valid artifacts. All artifacts are TraceID-addressable.

| Invariant | Enforcement Location | Failure Mode | Proof Mechanism |
|-----------|---------------------|--------------|------------------|
| ALL artifacts MUST be TypedDict or Pydantic models | Codebase-wide; §1.7 | Untyped artifact → NOT valid | V5-30 |
| TraceID mandatory and immutable on all artifacts | All artifact schemas | Loss of TraceID → fatal | V5-06 |
| InstructionPacket: [trace_id, policy_hash, route_mode, allowed_tools[], signature(HMAC-SHA256)] | assembly_stage:17-32; boundary_verifier:44-49 | Unsigned → HARD FAIL | PM-12; W6-02 |
| SandboxEnvelope: [InstructionPacket, ToolBudget(compute_ms, memory_mb, stdout_bytes)] | boundary_verifier:82-85 | Invalid sig → SignatureBoundaryError | PM-13; W6-04 |
| ExecutionTrace: [trace_id, plan_hash, actor, target, diff, policy_hash, timestamp, prev_hash, replay_key] | hash_chain_audit_log:117-157 | Tamper → chain verification fails | PM-15; W6-12 |
| HumanDecisionArtifact: [trace_id, policy_hash, reviewer_id, action, patch_schema, reviewer_sig] | human_decision_artifact:46 | MODIFY_DIFF without original_plan_hash → reject | PM-16; W6-23 |
| HealCheckResult: [check_id, status, changes_made(sorted), rollback_info, notes, needs_llm_escalation, escalation_hint] | CONTRACT_VERSION=2 | needs_llm_escalation set on policy failure → FAIL | PM-17 |
| EscalationContext: ONLY source for FailureSignal construction | Built from HealCheckResult ONLY | Raw notes passed to router → FAIL | PM-18 |
| FailureSignal: [source_agent, failure_type, error_signature, trace_id, context, retry_count, blast_radius] | .to_healing_input()→HealingInput | NO_TIERING agent not emitting → FAIL | PM-19 |
| HealingDecision: [heal_confidence, tier, reason_codes] | route_healing_tier() | Bypass → FAIL | PM-20 |
| ChangePackage: [source, target, changes, confidence, reason, timestamp_utc] + HMAC-SHA256 | proposal_only=True default; HMAC REQUIRED | No HMAC → integrity gap | PM-24; W6-10 |
| EvidencePack: [policy_evals, risk_scores, snapshots] | L3 HIL gate | Missing at HIL → FAIL | V5-13 |
| PolicyUpdateProposal: emitted on every Human Review override | L3 orchestration | Missing on override → FAIL | V5-14 |
| SurgicalManifest: [schema_version, correlation_id, node_id, target_layer, ast_snippet, ...] | Validated vs structure_blueprint.py | node_id unresolvable → FAIL | V5-10 |
| CognitiveDiffBundle: intended vs actual execution diff | L6 incident response | Missing during incident → FAIL | V5-19 |
| ForensicTraceBuffer: ephemeral high-fidelity capture during incident | L6 incident response | Missing during active incident → FAIL | V5-20 |
| DPOPair: [example_id:{control_hash, candidate_hash}, human_decision, reasons] | determinism.py:206 | Non-deterministic sort → replay mismatch | PM-23 |
| EmbeddingResult: [content_hash, score_round6, row_idx, embedding_artifact_hash] — C0 only | C0 informational rule | Drives routing → FAIL | PM-21 |
| SeedEmbeddingPackManifest: SHA-256 integrity at boot | embedding_factory instantiation | Mismatch → EmbeddingIntegrityError | PM-22 |

## SPINE 5: REPLAY SPINE (Hash Model + HMAC Binding + Transcript Binding)

**Canonical definition:** Replay is defined at two levels: INPUT replay (same inputs → same plan) and OUTPUT replay (transcript hash binds execution). All execution boundaries have mathematically complete replay guarantees.

| Invariant | Enforcement Location | Failure Mode | Proof Mechanism |
|-----------|---------------------|--------------|------------------|
| INPUT replay: same(payload + policy_hash + context_set) ⇒ same plan + same side-effects | Global determinism invariant | Non-deterministic plan from identical inputs → FAIL | V5-02 |
| OUTPUT replay_key = trace_id + plan_hash + transcript_hash | ExecutionTrace; SandboxEnvelope | Missing replay_key at execution boundary → FAIL | PM-15; W6 N1.2 |
| InstructionPacket HMAC-SHA256 + ReplayGuardStore single-sighting | assembly_stage:17-32; crypto_trust:86 | Replay attempt → rejected by ReplayGuardStore | W6-02 |
| SandboxEnvelope replay_key bound at L5→L2 | SandboxEnvelope contract [4] | Missing replay_key → reject | PM-13; W6 N1.2 A-35/A-37 |
| HashChainAuditLog GENESIS-anchored, sealed, tamper-detectable | hash_chain_audit_log:117-157 | Tamper → verify_chain_integrity() fails; post-seal append → RuntimeError | W6-12 |
| transcript_hash = SHA-256(canonical_bytes(all_entries)) at seal() | hash_chain_audit_log seal() | Transcript mismatch → replay verification fails | W6-12; W6 N1.2 |
| replay_mode blocks actual network calls | SovereignLLMGateway:176-211 | Un-transcripted network call in replay → HARD FAIL | W6-13; PM-31 |
| ChangePackage MUST have HMAC-SHA256 key on package_hash | meta_learning_bus (REQUIRED hardening) | SHA-256-only → integrity-only, no auth | W6-10 REQUIRED |
| Elevator shaft (L0↔L5) MUST have explicit sign+verify at call-site | L0 routing engine call-site (REQUIRED hardening) | Unverified context load → trust gap | W6-16 REQUIRED |
| Execution boundaries with COMPLETE replay: A-14 (L0→Assembly), A-35/A-37 (L5→L2), A-43/A-44 (L2→Outcome), A-46 (→L4 Ledger), A-47 (L0↔L5) | Per-arrow verification | Missing replay at execution boundary → FAIL | W6 N9.3: 5 COMPLETE; 28 PARTIAL; 8 NOT-DET (all NOT-DET lack execution authority) |
| Timestamps integer-only (no float nondeterminism) | hash_chain_audit_log: int(time.time()) | Float timestamp → nondeterminism → FAIL | W6-27 |
| Canonical ordering: canonical_bytes(sort_keys=True) on all hashing inputs | hash_chain_audit_log; assembly_stage; determinism.py | Non-canonical bytes → hash mismatch → FAIL | W6-28; PM-25 |

## SPINE 6: DETERMINISM SPINE (Semantic Clock + Hash Rules + UUID Prohibitions)

**Canonical definition:** Every execution path produces exactly one stable determinism digest. Two independent runs with identical inputs MUST produce identical digests. All hashing uses canonical JSON with alphabetical key sorting.

| Invariant | Enforcement Location | Failure Mode | Proof Mechanism |
|-----------|---------------------|--------------|------------------|
| JSON canonicalization: alphabetical key sort, UTF-8, zero whitespace before HMAC | All hashing points; canonical_bytes() | Non-canonical hash → INVALID | PM-25; W6-28 |
| W-DETERMINISM-DIGEST: exactly ONE stable artifact per phase | Per-phase determinism check | Multiple competing digests → FAIL | PM-32 |
| Double-run identical: two independent runs → identical digest | CI enforcement | Divergence → FAIL | PM-32 |
| Integer timestamps only: int(time.time()) captured once before canonical_bytes | hash_chain_audit_log | Float timestamp → nondeterminism | W6-27 |
| GENESIS anchor seeds every audit log deterministically | hash_chain_audit_log:117 | Non-deterministic GENESIS → all hashes diverge | W6-12 |
| DPO sorted by (control_hash, candidate_hash) | determinism.py:206 | Unsorted → replay mismatch | W6-21 |
| check_ids sorted lexicographically | assembly_stage:163 | Unsorted → determinism breach | W6 N9.4 |
| C0 excluded from routing_hash | assembly_stage:72-80 | C0 in routing_hash → nondeterminism from embedding variance | W6-03/25 |
| GovernedPayload frozen=True required | assembly_stage dataclass (REQUIRED) | Mutable post-init → determinism gap | W6-29 |
| Stochastic components bounded, logged, excluded from commit paths | Global | Unproven stochastic in commit → FAIL | V5-02 |
| Registry hash in determinism digest | AgentExecutionProfileRegistry | Registry change undetected → determinism gap | PM-11 |
| Negative control: NEGCTRL_TAMPER=1 → pytest XFAIL(strict=True) exit 0 | CI test | Tamper not detected → FAIL | PM-33 |
| Embedding determinism: BLAS locked, eps=1e-12, max K=20, cutoff>=0.5 | EmbeddingServiceFactory | BLAS unlocked → nondeterministic embeddings | PM diagram L65-68 |

## SPINE 7: GOVERNANCE SPINE (Guardian + Artifact Guard + Policy Guard)

**Canonical definition:** L5 is the sole governance authority. It contains exactly two sub-gates: Guardrail Guard (policy evaluation) and Artifact Guard (signature verification + replay comparison). Both must be traversed for any certification.

| Invariant | Enforcement Location | Failure Mode | Proof Mechanism |
|-----------|---------------------|--------------|------------------|
| L5 sole certification authority | SandboxEnvelope produced only by L5 | Non-L5 SandboxEnvelope → INVALID | PM-04; W6-05 |
| Guardrail Guard: policy evaluation (VALIDATE, ENFORCE, REMEDIATE, CERTIFY) | L5 safety pipeline P1-P4 | Policy violation → L5 HARD STOP or re-route to L1 | PM diagram L160-168 |
| Artifact Guard: signature verification + replay comparison | L5 enforcement (distinct from Guardrail Guard) | Invalid signature → reject; replay mismatch → reject | V5-16 |
| L5 HARD STOP [STOP]: blocks all non-PATH-A execution on rejection | L5 safety enforcement | Rejected plan continues → sovereignty violation | PM-38 |
| RE-CLR mandatory for human MODIFY_DIFF plans | L5 re-clear pipeline | Modified plan without re-clear → old sig invalid | PM-34 |
| Risk Tier Classification at L5 | L5 RISK TIER CLASSIFY | Unclassified risk → default BLOCK (P1 fail-closed) | PM diagram L160 |
| Compliance Hash/Stamp computation | L5 STMP | Missing stamp → cannot produce SandboxEnvelope | PM diagram L161 |
| EvidencePack required at HIL (Path D) gates | L3→L5 HIL interface | Missing EvidencePack → cannot proceed | V5-13 |
| PolicyUpdateProposal emitted on every Human Review override | L3 orchestration | Missing proposal → governance gap | V5-14 |
| Tiered Vigilance I/II/III at L6 | L6 monitoring (feeds L5 via signals) | Tier III not triggering freeze → evacuation gap | V5-18 |
| Knowledge Supervisor audit for low-confidence updates | L4 (feeds L5 via signals) | Low-confidence update unaudited → quality gap | V5-15 |

## SPINE 8: META-LEARNING SPINE (Proposal → Replay → Promotion → Version Pointer)

**Canonical definition:** Meta-learning is proposal-only by default. Activation requires: (1) all P0 closures complete, (2) dual injection of version_store + approval_gate, (3) governed promotion via L0, (4) L4 versioning, (5) cannot bypass L5/HIL/L2.

| Invariant | Enforcement Location | Failure Mode | Proof Mechanism |
|-----------|---------------------|--------------|------------------|
| proposal_only=True at ALL times unless dual injection | determinism.py:199; MetaLearningPipeline | Activation without dual injection → FAIL | PM-28; W6 confirmed |
| Dual injection required: version_store + approval_gate both present | Stage 9 COMMIT gate | Single injection → bypass risk (ORANGE W6-10) | PM-36; V5-25 |
| Fixed stage order 1-9: AUDIT→TELEMETRY→CONFIG→SNAPSHOT→RCA→PROPOSE→VALIDATE→INTAKE→COMMIT | meta_learning_pipeline.py | Stage skip → integrity gap | PM-36 |
| Proposers run in fixed order: L0→RAG→L1→L5 (enabled subset only) | Stage 6 PROPOSE | Order violation → determinism gap | PM-36 |
| Stage 7 VALIDATE: ReplayValidator + ShadowEvaluator + DampeningValidators + OscillationDetector | Stage 7 pipeline | Oscillation detected → auto-reject | PM-36; W6-22 |
| DPO feedback bounded: clamp [0.1, 2.0]; delta ±0.1 per decision | RLHFOptimizer | Unbounded adjustment → instability | PM-29 |
| ChangePackage MUST have HMAC-SHA256 key (not SHA-256-only) | meta_learning_bus (REQUIRED hardening) | SHA-256-only → auth gap | W6-10 |
| ChangePackage kind-scope validator: reject proposals targeting wrong layers | ML ingestion (REQUIRED hardening) | Wrong-layer proposal accepted → governance violation | W6-20 |
| Meta-learning activation blocked until P0 closures: P5.1 + §12.3 + all explicit P0 | Global gate | Premature activation → ungoverned improvement | V5-25 |
| Meta-learning MUST be governed, versioned in L4, re-enter via L0 | L0/L4/L5 pipeline | Direct mutation bypassing L0/L5/HIL/L4 → FAIL (P3/P6) | V5-25 |
| L6 Response Handler triggers L2 healing from L6 signals (distinct from archival) | L6 Response Handler | L6 healing trigger absent → monitoring gap | V5-17 |
| HealingOutcomeIntakeAdapter persists to L4B (always, before proposal_only check) | Stage 8 INTAKE | Skipped persist → feedback loop broken | PM-36 Stage 8 |
| PatternAnalysisEngine: flapping, drift spikes | Stage 8.6 PATTERN | Undetected flapping → oscillation risk | PM-36 Stage 8.6 |

## SPINE 9: CI ENFORCEMENT SPINE (AST Guards + Mutation Ratchets + Gateway Scan)

**Canonical definition:** All enforcement MUST be AST-based (not regex). CI detects and fails on violations — never repairs. All governance tests enforce zero-violation ceilings.

| Invariant | Enforcement Location | Failure Mode | Proof Mechanism |
|-----------|---------------------|--------------|------------------|
| AST-based enforcement only; regex enforcement = MISSING | All governance tests | Regex-based test → does not count as enforcement | V5-03; V5-22 |
| Mandatory governance test files: test_intent_emission_no_mutation.py, test_l6_purity.py, test_authority_boundaries.py | tests/governance/ | Absence → FAIL (P3/P0) | V5-22 |
| Zero-violation ceilings; ratchet-only enforcement = MISSING | Governance tests | Ratchet (non-zero ceiling) → MISSING | V5-22 |
| 17 W6 scan categories (S1-S17) across entire codebase | CI scan pipeline | Missing scan → enforcement gap | W6 Section 12.4 |
| SovereignLLMGateway AST scan: blocks direct provider SDK imports | CI build | Direct import outside gateway → FAIL | PM-10; W6 S1/S8/S11 |
| EmbeddingFactory AST scan: blocks instantiation outside factory | CI build | Direct embedding instantiation → FAIL | PM-10; W6 S2 |
| Discovery script integrity: SHA-256 vs structure_blueprint.py | Pre-audit gate | Mismatch → ABORT AUDIT → IMMEDIATE FAIL | V5-26 |
| Abort-on-critical: ZOMBIE/GHOST/INVALID/SYNTAX_ERROR → emit P0 only, STOP | Discovery ingestion | Critical agent found → no further processing | V5-27 |
| CommitProofInvariant: bind to true implementation commit | Evidence sealing | HEAD without implementation → churn commit → FAIL | PM-37 |
| Negative control test: NEGCTRL_TAMPER=1 → XFAIL(strict=True) exit 0 | CI test suite | Tamper not detected → enforcement gap | PM-33 |
| Determinism digest: ONE stable W-DIGEST per phase; double-run identical | CI verification | Multiple digests → FAIL; divergence → FAIL | PM-32 |
| Embedding integrity at boot: SHA-256(embeddings.f32) vs manifest | EmbeddingServiceFactory instantiation | Mismatch → EmbeddingIntegrityError | PM-30 |
| EMBEDDING_ENABLED kill-switch: false → EmbeddingDisabledError | embedding_factory.py:24-30 | Silent fallback → violation | PM-40 |

---

# PHASE 4 — ULTRA SPEC CANONICAL DEFINITIONS

The following are the single authoritative definitions for each contested or multi-defined concept. These definitions are self-contained within this document and do not reference external sources.

## 4.1 Execution Authority

**Single definition:** L2 is the sole execution layer. Execution is gated by: (1) SandboxEnvelope HMAC-SHA256 verification, (2) Capability token validation at a single chokepoint, (3) ToolBudget enforcement. No other layer may execute.

## 4.2 Mutation Authority

**Single definition:** `agentic_core/L2_execution/tools/write_gateway.py` (implementing the Universal Write Gateway contract) is the sole durable-mutation authority. It MUST contain 15 functions (write_text, write_bytes, write_json, append_text, open_write, ensure_dir, remove_file, remove_dir, remove_tree, copy_file, move_path, rename_path, touch_file, copy_tree, makedirs). All durable writes in L3/L4/L5/L6 MUST route through write_gateway or emit MutationIntent via L0 intent_router.py. AST-based governance tests enforce zero forbidden mutation primitives.

## 4.3 Replay Binding

**Single definition:** Replay operates at two levels:
- **INPUT replay:** Same (payload + policy_hash + retrieved_context_set) ⇒ same plan + same allowed side-effects.
- **OUTPUT replay:** replay_key = trace_id + plan_hash + transcript_hash, bound to ExecutionTrace and SandboxEnvelope.
- **Cryptographic replay prevention:** ReplayGuardStore single-sighting on InstructionPacket.
- **Network replay blocking:** replay_mode=true in SovereignLLMGateway blocks actual network calls; stored transcript used.

## 4.4 Determinism Clock

**Single definition:** All timestamps are integer UTC epoch seconds captured once before canonical_bytes(). No float timestamps. No wall-clock dependency in replay_key. GENESIS anchor seeds every audit log deterministically. canonical_bytes() uses json.dumps(sort_keys=True, separators=(',',':'), ensure_ascii=True).encode('utf-8').

## 4.5 Artifact Emission Legality

**Single definition:** Every named artifact MUST be a TypedDict or Pydantic model. All artifacts are TraceID-addressable. 18 canonical artifact types are defined (PM-12 through PM-24, plus additional governance artifacts). Free-form dicts, unstructured logs, or untyped schemas are NOT valid artifacts.

## 4.6 Meta-Learning Activation

**Single definition:** Meta-learning is proposal_only=True at ALL times unless: (1) all P0 closures are complete, (2) both version_store AND approval_gate are explicitly injected (dual injection), (3) ChangePackage has HMAC-SHA256 key (not SHA-256-only), (4) ChangePackage includes kind-scope validator, (5) learning is governed, versioned in L4, re-enters via L0, and cannot bypass L5/HIL/L2.

## 4.7 Promotion Gate

**Single definition:** Stage 9 COMMIT in MetaLearningPipeline. Requires: proposal_only=False (explicit override), ApprovalGate.decide(), Stage A (VersionStore.commit), Stage B (Activator.activate). Stage 7 VALIDATE must pass first (ReplayValidator + ShadowEvaluator + DampeningValidators + OscillationDetector). OscillationDetector auto-rejects proposals with threshold flip-flopping within cooldown window.

## 4.8 CI Enforcement Boundary

**Single definition:** CI enforcement is the union of:
1. **Runtime AST scanners**: SovereignLLMGateway SDK import blocking + EmbeddingFactory instantiation blocking
2. **17 scan categories**: Codebase-wide scans across all files
3. **Mandatory governance test files**: test_intent_emission_no_mutation.py, test_l6_purity.py, test_authority_boundaries.py with zero-violation ceilings
4. **Discovery integrity**: SHA-256 verification of discovery script vs structure_blueprint.py
5. **Determinism digest**: ONE W-DIGEST per phase; double-run identical
6. **Negative control**: NEGCTRL_TAMPER simulation
7. **Embedding integrity**: SHA-256 boot verification

All enforcement MUST be AST-based. Regex-based enforcement evaluates to MISSING. CI detects and fails — never repairs.

---

# ACTIVE VIOLATIONS REGISTER

The following violations are confirmed and MUST be remediated before the architecture can be declared compliant.

| ID | Violation | Severity | Source Evidence | Canonical Rule Violated | Fail-Closed Proof (Yes/No + evidence pointer) |
|----|-----------|----------|-----------------|------------------------|---------------------------------------------|
| VIO-01 | apps_rg direct LLM SDK calls (4 files) | RED | AST scan S8/S11 | SPINE 1: apps_* zero authority + sole Gateway seam | No | 
| VIO-02 | apps_shared SentenceTransformer bypass (2 files) | RED | AST scan S10 | SPINE 1: EmbeddingServiceFactory sole instantiation | No | 
| VIO-03 | healing_provider_adapters Gateway bypass | RED | AST scan S8 | SPINE 1: SovereignLLMGateway sole LLM seam | No | 
| VIO-04 | External weight pull: no sig, no L5 cert, no kill-switch (A-05) | RED | Code analysis A-05 | SPINE 3: external boundary requires signed ingress | No | 
| VIO-05 | LocalFAISSStore skeleton: writes not UWG-gated (A-41) | RED | Code analysis A-41 | SPINE 3: UWG sole mutation authority | No | 
| VIO-06 | ChangePackage SHA-256-only (no HMAC key) (A-06) | ORANGE | Code analysis A-06 | SPINE 5: HMAC-SHA256 required for auth | No | 
| VIO-07 | L4B IntakeRecord no HMAC; UWG unconfirmed (A-42) | ORANGE | Code analysis A-42 | SPINE 3: L4 writes must be HMAC-signed + UWG-routed | No | 
| VIO-08 | GovernedPayload not frozen=True | YELLOW | Code analysis W6-29 | SPINE 6: determinism requires immutable post-assembly | No | 
| VIO-09 | ChangePackage scope not payload-enforced | YELLOW | Code analysis W6-20 | SPINE 8: kind-scope validator required | No | 
| VIO-10 | L1 ingress: no Pydantic schema validation for apps_* payload | YELLOW | Code analysis W6-24 | SPINE 1: typed APIs at all boundaries | No | 
| VIO-11 | Elevator shaft call-site crypto not confirmed | YELLOW | Code analysis W6-16 | SPINE 5: explicit sign+verify at every boundary | No |

---

# Windsurf Gap Analysis Contract (Standalone)

## Required Output Sections (Exact Order)

### (1) CURRENT STATE
Repo-derived facts only:
- File paths and their existence/absence
- AST scan findings (import statements, class definitions, function calls)
- Observable behavior (test results, runtime outputs)
- Concrete evidence lines (no interpretation)

### (2) TARGET STATE
Cite spine + invariant IDs from THIS spec only:
- Reference specific SPINE sections (1-9)
- Reference specific invariant IDs (PM-##, V5-##, W6-##)
- Reference specific ACTIVE VIOLATIONS (VIO-##)
- No external document references

### (3) GAPS
One row per mismatch with exact schema:
| GAP_ID | Severity | Enforcement Site | Fix Scope | Target Invariant(s) |
|--------|----------|-----------------|-----------|-------------------|
| GAP-001 | CRITICAL | apps_rg/ | Remove direct SDK imports | SPINE 1, VIO-01 |

### (4) IMPLEMENTATION WAVES
Each GAP_ID assigned to wave with acceptance check:
- **Wave 0**: CRITICAL only (sovereignty integrity violations)
- **Wave 1**: HIGH severity
- **Wave 2**: MEDIUM/LOW severity

Each wave requires:
- Owner assignment
- Acceptance check definition
- Due wave specification

## Severity Scale (Defined Here)
- **CRITICAL**: Sovereignty integrity violation (bypass/upward mutation/kill-switch bypass/unsigned side-effects)
- **HIGH**: Authority boundary violation (unauthorized mutation, LLM bypass, Gateway circumvention)
- **MEDIUM**: Integrity gap (missing HMAC, weak validation, scope issues)
- **LOW**: Compliance gap (missing validation, incomplete typing, documentation gaps)

## Wave Policy
- Wave 0: Must be completed before any other work
- Wave 1: Must be completed before Wave 2
- Wave 2: May be run in parallel within the wave
- Each wave produces evidence file with pass/fail per GAP

## Prohibition on Narrative Reviews
- Every statement MUST tie to an invariant ID + evidence
- No "should", "could", "consider" language
- Only factual findings with invariant references
- All gaps must have concrete enforcement locations

# Definition of Compliant (Standalone)

## Compliance Requirements
The system is COMPLIANT only when:

1. **Active Violations Register**: All CRITICAL and HIGH items are remediated (count = 0)
2. **MEDIUM/LOW items**: May remain only if explicitly listed in IMPLEMENTATION WAVES with:
   - Owner assignment
   - Acceptance check definition
   - Due wave specification
3. **Fail-Closed Verification**: All seams, especially stubbed/unimplemented features, MUST:
   - Invocation hard-fails with typed, named error
   - No silent fallback path exists
   - Failure is detectable by test/guard
   - Violation is surfaced in Active Violations Register until implemented

## Compliance Evidence
Compliance MUST be evidenced by:
- Gap analysis output following Windsurf Gap Analysis Contract
- Evidence files for each wave showing PASS/FAIL per GAP
- Updated Active Violations Register showing remediation status
- Test suite showing 0 failures for all invariants

## Non-Compliance Conditions
System is NON-COMPLIANT if ANY:
- CRITICAL or HIGH violation remains unremediated
- MEDIUM/LOW violation exists without wave assignment
- Stubbed component lacks fail-closed behavior
- Evidence does not follow this contract

# Invariant-to-Verification Binding Tables (Standalone)

## Table Schema
| Invariant ID | Statement | Enforcement Location(s) | Verification Action | Pass Criterion | Evidence Artifact |
|-------------|-----------|------------------------|-------------------|---------------|-------------------|

## SPINE 1: Control Spine Bindings
| Invariant ID | Statement | Enforcement Location(s) | Verification Action | Pass Criterion | Evidence Artifact |
|-------------|-----------|------------------------|-------------------|---------------|-------------------|
| SPINE-1-01 | apps_* zero authority | L1 ingress validation | Pydantic schema validation test | Reject malformed payload | test_apps_ingress_validation.py |
| SPINE-1-02 | L1 propose-only | L1 module tree | AST scan for write primitives | Zero write primitives found | test_l1_no_write_primitives.py |
| SPINE-1-03 | SovereignLLMGateway sole LLM seam | CI build pipeline | AST scan for direct SDK imports | Zero direct imports | test_gateway_sole_seam.py |
| SPINE-1-04 | 9 kill-switches fail-closed | Kill-switch implementations | Runtime test with toggle=false | Typed error raised | test_kill_switch_fail_closed.py |

## SPINE 2: Execution Spine Bindings
| Invariant ID | Statement | Enforcement Location(s) | Verification Action | Pass Criterion | Evidence Artifact |
|-------------|-----------|------------------------|-------------------|---------------|-------------------|
| SPINE-2-01 | L2 sole execution authority | L2 execution core | Integration test with non-L2 execution | Architectural FAIL | test_l2_sole_execution.py |
| SPINE-2-02 | SandboxEnvelope verification | boundary_verifier.py | Unit test with invalid signature | SignatureBoundaryError | test_sandbox_envelope_verification.py |
| SPINE-2-03 | Capability token required | L2 boundary chokepoint | Test with missing token | FAIL-CLOSED rejection | test_capability_token_required.py |

## SPINE 3: Mutation Spine Bindings
| Invariant ID | Statement | Enforcement Location(s) | Verification Action | Pass Criterion | Evidence Artifact |
|-------------|-----------|------------------------|-------------------|---------------|-------------------|
| SPINE-3-01 | write_gateway.py sole mutation | agentic_core/L2_execution/tools/ | AST scan for 15 required functions | All 15 functions present | test_write_gateway_complete.py |
| SPINE-3-02 | Runtime block non-gateway writes | UWG implementation | Integration test with direct write | ToolNotAllowedError | test_non_gateway_write_blocked.py |
| SPINE-3-03 | Forbidden primitives in L3-L6 | Governance tests | AST scan across layers | Zero forbidden primitives | test_forbidden_primitives_ast.py |

## SPINE 4: Artifact Spine Bindings
| Invariant ID | Statement | Enforcement Location(s) | Verification Action | Pass Criterion | Evidence Artifact |
|-------------|-----------|------------------------|-------------------|---------------|-------------------|
| SPINE-4-01 | All artifacts typed | Codebase-wide | AST scan for TypedDict/Pydantic | 100% typed artifacts | test_all_artifacts_typed.py |
| SPINE-4-02 | TraceID mandatory | All artifact schemas | Schema validation test | TraceID loss = fatal | test_traceid_mandatory.py |
| SPINE-4-03 | InstructionPacket schema | assembly_stage.py | Unit test with malformed packet | HARD FAIL | test_instruction_packet_schema.py |

## SPINE 5: Replay Spine Bindings
| Invariant ID | Statement | Enforcement Location(s) | Verification Action | Pass Criterion | Evidence Artifact |
|-------------|-----------|------------------------|-------------------|---------------|-------------------|
| SPINE-5-01 | INPUT replay determinism | Global determinism check | Double-run with identical inputs | Identical outputs | test_input_replay_determinism.py |
| SPINE-5-02 | OUTPUT replay_key binding | ExecutionTrace | Unit test with missing replay_key | FAIL | test_replay_key_binding.py |
| SPINE-5-03 | ReplayGuardStore single-sighting | crypto_trust.py | Integration test with replay attempt | Replay rejected | test_replay_guard_single_sighting.py |

## SPINE 6: Determinism Spine Bindings
| Invariant ID | Statement | Enforcement Location(s) | Verification Action | Pass Criterion | Evidence Artifact |
|-------------|-----------|------------------------|-------------------|---------------|-------------------|
| SPINE-6-01 | JSON canonicalization | All hashing points | Test with non-canonical JSON | INVALID | test_json_canonicalization.py |
| SPINE-6-02 | W-DETERMINISM-DIGEST stability | Per-phase check | Double-run digest comparison | Identical digests | test_determinism_digest_stable.py |
| SPINE-6-03 | Integer timestamps only | hash_chain_audit_log | Test with float timestamps | FAIL | test_integer_timestamps_only.py |

## SPINE 7: Governance Spine Bindings
| Invariant ID | Statement | Enforcement Location(s) | Verification Action | Pass Criterion | Evidence Artifact |
|-------------|-----------|------------------------|-------------------|---------------|-------------------|
| SPINE-7-01 | L5 sole certification | L5 implementation | Test with non-L5 SandboxEnvelope | INVALID | test_l5_sole_certification.py |
| SPINE-7-02 | Guardrail Guard evaluation | L5 safety pipeline | Policy violation test | L5 HARD STOP | test_guardrail_guard_evaluation.py |
| SPINE-7-03 | Artifact Guard verification | L5 enforcement | Invalid signature test | Reject | test_artifact_guard_verification.py |

## SPINE 8: Meta-Learning Spine Bindings
| Invariant ID | Statement | Enforcement Location(s) | Verification Action | Pass Criterion | Evidence Artifact |
|-------------|-----------|------------------------|-------------------|---------------|-------------------|
| SPINE-8-01 | proposal_only=True default | MetaLearningPipeline | Test activation without dual injection | FAIL | test_proposal_only_default.py |
| SPINE-8-02 | Dual injection required | Stage 9 COMMIT | Single injection test | Bypass risk | test_dual_injection_required.py |
| SPINE-8-03 | Fixed stage order 1-9 | meta_learning_pipeline.py | Stage skip test | Integrity gap | test_fixed_stage_order.py |

## SPINE 9: CI Enforcement Spine Bindings
| Invariant ID | Statement | Enforcement Location(s) | Verification Action | Pass Criterion | Evidence Artifact |
|-------------|-----------|------------------------|-------------------|---------------|-------------------|
| SPINE-9-01 | AST-based enforcement only | Governance tests | Regex-based test detection | Does not count | test_ast_enforcement_only.py |
| SPINE-9-02 | Mandatory governance tests | tests/governance/ | File existence test | All 3 files present | test_mandatory_governance_tests.py |
| SPINE-9-03 | Zero-violation ceilings | Governance tests | Ratchet detection | MISSING | test_zero_violation_ceilings.py |

## Missing Binding GAP Creation Rule
If any invariant lacks ≥1 verification action or enforcement location is unknown:
1. Create GAP_ID with severity HIGH
2. Assign to Wave 1
3. Mark enforcement location as "REQUIRED LOCATION PATTERN: <pattern>"
4. Evidence artifact = "GAP: Missing verification binding"

# Evidence Protocol (Standalone)

## Determinism Proof Requirements

### Double-Run Protocol
1. **Two independent invocations** with identical inputs
2. **Exactly one digest line** printed per run:
   ```
   W*-DETERMINISM-DIGEST: <hash>
   ```
3. **Digests must match** exactly
4. **Inputs must be identical** (payload + policy_hash + context_set)
5. **Environment must be stable** (no external dependencies)

### Acceptance Criteria
- PASS: Digests match exactly
- FAIL: Digests differ OR missing digest line OR multiple digest lines
- Evidence: Full stdout transcript showing both digest lines

## Negative Control Protocol

### Tamper Simulation
1. **Environment toggle**: `W*_NEGCTRL_TAMPER=1`
2. **Tamper run MUST exit 0** and report expected failure:
   - pytest: `XFAIL(strict=True)`
   - Custom: Defined strict expected-failure semantics
3. **Restore run MUST PASS** with normal environment
4. **Tamper must be detectable** by the test/guard

### Acceptance Criteria
- PASS: Tamper run exits 0 with XFAIL + restore run passes
- FAIL: Tamper run non-zero exit OR restore run fails OR tamper undetected
- Evidence: Tamper run output + restore run output

## Evidence Artifact Acceptance

### Acceptable Forms
1. **Stdout transcript**: Full command output with digest lines
2. **Stored log path**: Referenced file with complete content
3. **Test result file**: pytest JSON or custom format
4. **Digest file**: Separate file containing only digest lines

### Evidence Requirements
- Must be referenced in gap analysis output
- Must be reproducible (same inputs → same evidence)
- Must include timestamps for temporal validation
- Must be machine-readable for automated verification

### Evidence Integrity
- Evidence files must be immutable after creation
- Evidence must be bound to specific commit hash
- Evidence must include environment fingerprint
- Evidence must be verifiable independently

# Stubbed or Unimplemented Components Must Fail-Closed

## Fail-Closed Requirements

### Acceptable Interim State
Stubbed or unimplemented components MUST:

#### (a) Invocation Hard-Fails with Typed, Named Error
- Error class MUST follow naming convention: `<Component>NotImplementedError`
- Error MUST be typed (not string)
- Error MUST include component name and required capability
- Example: `ExternalModelRegistryNotImplementedError: External model registry not implemented - requires HMAC sig + L5 cert + kill-switch`

#### (b) No Silent Fallback Path
- Component MUST NOT degrade gracefully
- Component MUST NOT return mock/placeholder data
- Component MUST NOT skip required validation
- Any attempt to use MUST raise the typed error

#### (c) Failure Detectable by Test/Guard
- Unit test MUST exist that expects the typed error
- Integration test MUST verify error propagation
- Runtime guard MUST catch and log the error
- Test MUST be part of CI pipeline

#### (d) Violation Surfaced in Active Violations Register
- Each stubbed component MUST have VIO entry
- VIO entry MUST reference the typed error class
- VIO entry MUST have Fail-Closed Proof = "Yes: <test_name>"
- VIO entry MUST remain until component is implemented

## Enforcement Protocol

### CI Integration
1. **AST scan** detects stubbed components (functions with `raise NotImplementedError`)
2. **Test verification** confirms typed error usage
3. **Register validation** ensures VIO entry exists
4. **Fail-closed test** confirms error is raised on invocation

### Remediation Path
1. Implement component according to spine requirements
2. Remove typed error and raise statements
3. Update VIO entry with implementation evidence
4. Remove VIO entry when fully compliant

## Examples of Acceptable Fail-Closed

### External Model Registry (A-05)
```python
class ExternalModelRegistryNotImplementedError(NotImplementedError):
    """External model registry not implemented - requires HMAC sig + L5 cert + kill-switch"""
    pass

def fetch_external_model(model_id: str) -> bytes:
    raise ExternalModelRegistryNotImplementedError(
        f"External model registry not implemented - model_id: {model_id}"
    )
```

### LocalFAISSStore (A-41)
```python
class LocalFAISSStoreNotImplementedError(NotImplementedError):
    """LocalFAISSStore not implemented - requires UWG + EMBEDDING_ENABLED + SHA-256"""
    pass

def write_to_faiss(index_path: str, vectors: np.ndarray) -> None:
    raise LocalFAISSStoreNotImplementedError(
        f"LocalFAISSStore not implemented - path: {index_path}"
    )
```

# Handshake Enforcement Granularity (Standalone)

## Handshake Definition
Every interface/handshake in the architecture MUST correspond to:

### Required Elements
1. **Input Schema**: Typed (TypedDict/Pydantic) with field validation
2. **Output Schema**: Typed (TypedDict/Pydantic) with field validation
3. **Signer/Verifier Identity**: Where signatures apply, explicit identity fields
4. **Side-Effect Boundary Definition**: Clear statement of what side-effects are allowed
5. **Replay Key Inputs**: All inputs that affect replay must be explicitly listed
6. **Fail-Closed Behavior**: Typed error for all failure modes
7. **Verification Hook**: Test or runtime guard that validates the handshake

## Handshake GAP Creation

### GAP Generation Rules
If any handshake is defined in this ULTRA spec without the required elements:

1. **Create GAP row** with severity HIGH
2. **Assign to Wave 1** (unless sovereignty impact, then Wave 0)
3. **Element missing**: Specify which required element(s) are missing
4. **Enforcement pattern**: "REQUIRED HANDSHAKE PATTERN: <interface_name>"
5. **Evidence**: "GAP: Handshake incomplete - missing <element(s)>"

### Handshake Examples

#### L5→L2 SandboxEnvelope Transfer
- Input Schema: SandboxEnvelope (✓ defined)
- Output Schema: ToolTranscript (✓ defined)
- Signer Identity: L5 certification signature (✓ defined)
- Side-Effect Boundary: Execution only within sandbox (✓ defined)
- Replay Key: trace_id + plan_hash + transcript_hash (✓ defined)
- Fail-Closed: SignatureBoundaryError (✓ defined)
- Verification Hook: boundary_verifier.py test (✓ defined)
**Status: COMPLETE**

#### External Model Registry Ingress (A-05)
- Input Schema: Not defined ❌
- Output Schema: Not defined ❌
- Signer Identity: Not defined ❌
- Side-Effect Boundary: Not defined ❌
- Replay Key: Not defined ❌
- Fail-Closed: Not defined ❌
- Verification Hook: Not defined ❌
**Status: GAP-001 created**

#### L0↔L5 Elevator Shaft
- Input Schema: ContextSnapshot (✓ defined)
- Output Schema: CertifiedContext (✓ defined)
- Signer Identity: Not explicitly defined ❌
- Side-Effect Boundary: Read-only context load (✓ defined)
- Replay Key: boundary_snapshot_hash (✓ defined)
- Fail-Closed: Not explicitly defined ❌
- Verification Hook: Not explicitly defined ❌
**Status: GAP-002 created**

## Enforcement Protocol

### AST-Based Handshake Detection
1. Scan for function calls crossing layer boundaries
2. Verify schema definitions exist for inputs/outputs
3. Check for signature verification where required
4. Validate side-effect boundary definitions
5. Confirm replay key inclusion
6. Test fail-closed error handling
7. Verify verification hook existence

### Gap Remediation
1. Define missing schemas (TypedDict/Pydantic)
2. Implement signature verification where needed
3. Document side-effect boundaries explicitly
4. Add replay key inputs to schemas
5. Implement typed error classes
6. Create verification tests/guards
7. Update handshake documentation

# SUPERSESSION STATEMENT

This document **ULTRA_AGENTIC_ARCHITECTURE_SPEC_v1.0** is the sole authoritative future-state architecture specification for the Agentic Workflow system. It is fully standalone and self-contained.

**Total invariants captured:** 100 (PM: 40, W6: 30, V5: 30)
**Conflicts resolved:** 14 (0 substantive contradictions; 14 additive/enforcement-gap resolutions)
**Active violations:** 11 (5 RED, 2 ORANGE, 4 YELLOW)
**Spines defined:** 9 (Control, Execution, Mutation, Artifact, Replay, Determinism, Governance, Meta-Learning, CI Enforcement)
**Canonical definitions:** 8 (Execution authority, Mutation authority, Replay binding, Determinism clock, Artifact emission, Meta-learning activation, Promotion gate, CI enforcement boundary)
**Verification bindings:** 27+ across all spines
**Gap analysis contract:** Defined and standalone
**Evidence protocol:** Determinism + negative control defined
**Fail-closed requirements:** Stubbed components protocol defined
**Handshake granularity:** Complete enforcement pattern defined

---

END OF SPEC

# Compliance Checklist (Standalone)

## PASS/FAIL Criteria

### [ ] External References Removed
- **PASS**: Zero references to other documents as requirements in normative sections
- **FAIL**: Any "see X", "per X", "derived from X", "as defined in X" remains

### [ ] Requirements Fully Inlined
- **PASS**: All previously externalized requirements are contained within this document
- **FAIL**: Any requirement depends on external document content

### [ ] Gap Analysis Contract Exists
- **PASS**: Windsurf Gap Analysis Contract section exists with severity scale and waves defined
- **FAIL**: Contract missing, incomplete, or references external definitions

### [ ] Definition of Compliant Exists
- **PASS**: Definition of Compliant section exists and gates on Violations Register
- **FAIL**: Definition missing or does not reference Active Violations Register

### [ ] Evidence Protocol Complete
- **PASS**: Evidence Protocol includes determinism (2 runs, single digest line) + negative control (exit 0 XFAIL + restore PASS)
- **FAIL**: Protocol missing or incomplete

### [ ] Invariant→Verification Tables Complete
- **PASS**: Tables exist for SPINE 1-9 with ≥1 row each; missing bindings expressed as GAP_IDs
- **FAIL**: Tables missing, incomplete, or missing GAP creation for unknown locations

### [ ] Active Violations Register Preserved
- **PASS**: Register preserved with only augmentation (Fail-Closed Proof column added)
- **FAIL**: Register modified, rows removed, or columns removed

### [ ] Handshake Enforcement Granularity Exists
- **PASS**: Handshake Enforcement Granularity section exists and creates GAPs where bindings are missing
- **FAIL**: Section missing or does not define GAP creation protocol

### [ ] All Normative Sections Self-Contained
- **PASS**: Every requirement, definition, and protocol can be understood with ONLY this document
- **FAIL**: Any normative content requires external context

### [ ] Fail-Closed Protocol Defined
- **PASS**: Stubbed or unimplemented components have clear fail-closed requirements
- **FAIL**: No protocol for handling incomplete implementations

## Overall Compliance Status
**[ ] COMPLIANT** - All criteria PASS
**[ ] NON-COMPLIANT** - Any criteria FAIL
