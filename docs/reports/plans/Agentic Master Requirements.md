# Agentic Master Requirements — Finalized Corpus (v3.1 — Hardened)

**Status:** PROVISIONALLY CERTIFIED -- PENDING REQ-416 EXECUTION
**Total Requirements:** 417
**Severity Distribution:** CRITICAL: 348 | HIGH: 68 | MEDIUM: 1
**Finalization Report:** See `Agentic-Requirements-Finalization.md` for full 8-phase audit

## Machine-Verifiable Integrity Block

```
TOTAL_ROWS = 417
MAX_REQ_ID = REQ-417
NO_GAPS = TRUE
NO_DUP_IDS = TRUE
CRITICAL_COUNT = 348
HIGH_COUNT = 68
MEDIUM_COUNT = 1
HARDENING_REQS_ADDED = 5 (REQ-413, REQ-414, REQ-415, REQ-416, REQ-417)
CORPUS_VERSION = 3.1
ARITHMETIC_VERIFIED = TRUE
ENFORCEMENT_METADATA_SCHEMA = DEFINED (see finalization report Section 2.5)
ENFORCEMENT_METADATA_TAGGED = FALSE
CRITICAL_WITH_RUNTIME = PENDING (requires enforcement metadata tagging)
CRITICAL_WITH_2_LAYERS = PENDING (requires REQ-416 CI execution)
```

| Req ID | Domain | Requirement | Enforcement | Severity |
|--------|--------|------------|------------|----------|
| REQ-001 | Layer Sovereignty | apps_* MUST NOT execute tools | AST + runtime import hook | CRITICAL |
| REQ-002 | Layer Sovereignty | apps_* MUST NOT certify plans | AST + runtime import hook | CRITICAL |
| REQ-003 | Layer Sovereignty | apps_* MUST NOT perform durable mutation | AST + runtime import hook | CRITICAL |
| REQ-004 | Layer Sovereignty | L1 is propose-only | AST + runtime boundary assertion | CRITICAL |
| REQ-005 | Layer Sovereignty | L0 is route-only | AST + runtime boundary assertion | CRITICAL |
| REQ-006 | Layer Sovereignty | L5 is certify-only | AST + runtime boundary assertion | CRITICAL |
| REQ-007 | Layer Sovereignty | L2 is execute-only | AST scan | HIGH |
| REQ-008 | Layer Sovereignty | L4 is persist-only | AST scan | HIGH |
| REQ-009 | Layer Sovereignty | L6 is observe-only | AST scan | CRITICAL |
| REQ-010 | Layer Sovereignty | Upward mutation across layers is forbidden | Cross-layer import + runtime | CRITICAL |
| REQ-011 | Gateway | All outbound LLM calls MUST pass through SovereignLLMGateway | AST + runtime dispatch | CRITICAL |
| REQ-012 | Gateway | Model literals MUST NOT exist outside gateway | AST + runtime scan | CRITICAL |
| REQ-013 | Gateway | Embeddings MUST be instantiated only via EmbeddingServiceFactory | AST + runtime assertion | CRITICAL |
| REQ-014 | Gateway | AgentExecutionProfile MUST validate execution | Runtime registry check | CRITICAL |
| REQ-015 | Gateway | Determinism digest MUST include registry hash, artifact registry hash, and execution registry hash | Output inspection + CI | HIGH |
| REQ-016 | META-INVARIANT | All boundary/signature/timeout/kill-switch/guardian/freeze/validator/budget/blueprint failures MUST fail-closed with no silent fallback | Runtime + CI ratchet | CRITICAL |
| REQ-017 | Canonicalization | Canonical JSON MUST sort keys, use UTF-8, eliminate whitespace variance, be byte-stable, reject NaN/float | Unit + serialization test | HIGH |
| REQ-018 | Canonicalization | All authenticity-critical artifacts MUST use HMAC-SHA256 over canonical bytes | Signature test + CI | CRITICAL |
| REQ-019 | META-INVARIANT | Signature/HMAC/hash verification MUST occur before any state mutation, commit, activation, or side-effect | Runtime boundary + guard | CRITICAL |
| REQ-020 | META-INVARIANT | All sealed artifacts, audit logs, snapshots, diff bundles, registries, hash chains, pointer lineages, change histories MUST be append-only and immutable post-seal | Integrity test + runtime | CRITICAL |
| REQ-021 | Packet | InstructionPacket MUST include trace_id, policy_hash, route_mode, allowed_tools[] | Schema validation | HIGH |
| REQ-022 | Packet | InstructionPacket MUST include signature; signature MUST verify | Schema + runtime verification | CRITICAL |
| REQ-023 | Replay | ReplayGuardStore MUST enforce single-use packets | Runtime replay check | CRITICAL |
| REQ-024 | Envelope | SandboxEnvelope MUST embed InstructionPacket; signature MUST verify at L2 boundary | Schema + runtime boundary | CRITICAL |
| REQ-025 | Budget | ToolBudget MUST include compute_ms, memory_mb, stdout_bytes; caps MUST be enforced | Schema + runtime + CI | CRITICAL |
| REQ-026 | Tools | ToolCall MUST include id, args; ToolResult MUST include exit_code, stdout | Schema validation | HIGH |
| REQ-027 | Tools | Tool output MUST be STDOUT-only | Runtime enforcement | HIGH |
| REQ-028 | Tools | Tool stdout MUST be redacted before artifact emission; byte caps MUST be enforced | Redaction + runtime + CI | CRITICAL |
| REQ-029 | Mutation | write_gateway.py MUST exist; all durable writes MUST go through UWG | Static + AST + runtime | CRITICAL |
| REQ-030 | Mutation | Non-UWG FS/DB/vector writes MUST raise ToolNotAllowedError | Runtime test | CRITICAL |
| REQ-031 | Mutation | UWG MUST expose 15 named write primitives | Static file inspection | HIGH |
| REQ-032 | Artifact | All artifacts MUST be typed (TypedDict or Pydantic) | AST + runtime type check | CRITICAL |
| REQ-033 | Artifact | ExecutionTrace MUST include trace_id, plan_hash, policy_hash, timestamp_utc(int), prev_hash | Schema + runtime hash-chain | CRITICAL |
| REQ-034 | Artifact | replay_key MUST bind trace_id + plan_hash + transcript_hash; transcript_hash MUST be deterministic | Runtime + determinism test | CRITICAL |
| REQ-035 | Determinism | Determinism artifact MUST print exactly once per wave and per replay | Runtime output check | CRITICAL |
| REQ-036 | Determinism | Two independent executions with identical inputs MUST produce identical digest | Replay test | CRITICAL |
| REQ-037 | Determinism | Negative control MUST be env-toggle driven, strict XFAIL, exit 0, restore PASS cleanly | Test harness validation | CRITICAL |
| REQ-038 | Healing | route_healing_tier MUST be sole tier selector | AST scan | CRITICAL |
| REQ-039 | Healing | needs_llm_escalation MUST be explicit opt-in | Runtime check | CRITICAL |
| REQ-040 | Healing | retry_count MUST be monotonic; >=3 MUST force GEMINI tier | Runtime validation | HIGH |
| REQ-041 | Healing | HealCheckResult must include CONTRACT_VERSION=2 | Schema validation | MEDIUM |
| REQ-042 | Healing | HealCheckResult changes_made must be deterministically sorted | Runtime check | HIGH |
| REQ-043 | Healing | EscalationContext must derive only from HealCheckResult; FailureSignal only from EscalationContext | Runtime validation | CRITICAL |
| REQ-044 | Healing | NO_TIERING agents must emit FailureSignal | Runtime contract check | HIGH |
| REQ-045 | RAG | Embeddings are C0 informational only | Runtime route test | CRITICAL |
| REQ-046 | RAG | Embedding pack SHA-256 MUST verify at startup | Startup + CI hash check | CRITICAL |
| REQ-047 | RAG | SeedEmbeddingPackManifest MUST include model_version, vector_count, dimensions, matrix_hash | Schema validation | CRITICAL |
| REQ-048 | RAG | embeddings.f32 SHA-256 must match matrix_hash; EmbeddingResult MUST include embedding_artifact_hash | Startup validation | CRITICAL |
| REQ-049 | Meta-Learning | ChangePackage MUST default proposal_only=True; kill-switch fail-closed | Config + runtime test | CRITICAL |
| REQ-050 | Meta-Learning | Activation requires explicit VersionStore injection; Activator.activate() requires VersionPointer | Runtime gate | CRITICAL |
| REQ-051 | Meta-Learning | ChangePackage MUST be HMAC-SHA256 signed; package_hash MUST be HMAC-SHA256 | Signature validation | CRITICAL |
| REQ-052 | Meta-Learning | ChangePackage targeting wrong layer MUST be rejected | Scope validator | HIGH |
| REQ-053 | Meta-Learning | ChangePackage MUST include trace_id, kind, payload, layer_target, delta_payload, timestamp_utc, package_hash | Schema validation | HIGH |
| REQ-054 | Meta-Learning | ChangePackage kind MUST be allowlisted; payload validated by kind-specific schema | Runtime validation | CRITICAL |
| REQ-055 | Meta-Learning | HMAC key material MUST be managed outside repo code | Static scan + config | CRITICAL |
| REQ-056 | Meta-Learning | proposal_only MUST remain enforced unless dual injection; Stage 9 MUST NOT run when proposal_only=True | Runtime gate | CRITICAL |
| REQ-057 | Meta-Learning | Dual injection MUST require both version_store AND approval_gate; single-injection MUST hard-fail | Runtime Stage 9 precheck | CRITICAL |
| REQ-058 | Meta-Learning | Stage order fixed: AUDIT→TELEMETRY→CONFIG→SNAPSHOT→RCA→PROPOSE→VALIDATE→INTAKE→COMMIT | Runtime pipeline controller | CRITICAL |
| REQ-059 | Meta-Learning | Stage controller MUST reject unknown stage ids and persist transitions as audit trail | Runtime validation + logging | HIGH |
| REQ-060 | Meta-Learning | Each stage MUST be deterministic (no wall-clock/random); Stage 1 AUDIT before proposals | Determinism tests + ordering | CRITICAL |
| REQ-061 | Meta-Learning | Stages 2-5 MUST emit typed artifacts (CandidateConfig, Snapshot, RCAReport) | Schema + runtime | HIGH |
| REQ-062 | Meta-Learning | Stage 6 PROPOSE MUST be only stage to emit ChangePackage proposals | Runtime invariant | CRITICAL |
| REQ-063 | Meta-Learning | Proposers fixed order L0→RAG→L1→L5; deterministic under enable/disable subsets | Runtime + determinism | CRITICAL |
| REQ-064 | Meta-Learning | Stage 6 single consolidated ChangePackage per trace_id per cycle; each proposer emits typed artifacts | Runtime invariant + schema | HIGH |
| REQ-065 | Meta-Learning | Stage 7 MUST include ReplayValidator, ShadowEvaluator, DampeningValidators, OscillationDetector | Runtime composition check | CRITICAL |
| REQ-066 | Meta-Learning | ReplayValidator MUST reject proposals failing replay constraints | Runtime tests | CRITICAL |
| REQ-067 | Meta-Learning | ShadowEvaluator MUST produce typed shadow_score, MUST NOT commit | Schema + runtime guard | CRITICAL |
| REQ-068 | Meta-Learning | CooldownValidator MUST reject within cooldown; MinSampleValidator MUST reject insufficient samples | Runtime tests | CRITICAL |
| REQ-069 | Meta-Learning | OscillationDetector MUST reject flip-flop patterns; validator failures fail-closed | Runtime tests | CRITICAL |
| REQ-070 | Meta-Learning | Stage 7 MUST emit typed ValidationReport | Schema validation | HIGH |
| REQ-071 | Meta-Learning | Stage 8 INTAKE MUST persist to L4, be HMAC-signed, be UWG-routed | Runtime + signature + interception | CRITICAL |
| REQ-072 | Meta-Learning | Stage 9 MUST be only stage writing VersionStore | Runtime invariant | CRITICAL |
| REQ-073 | Meta-Learning | ApprovalGate.decide() before VersionStore.commit(); denied = hard-stop | Runtime ordering + tests | CRITICAL |
| REQ-074 | Meta-Learning | VersionStore.commit() MUST produce typed VersionPointer; Stage 9 two sub-stages | Schema + runtime | HIGH |
| REQ-075 | Meta-Learning | Activation governed via L0 promotion; MUST NOT bypass L5/HIL/L2 boundaries | Runtime boundary | CRITICAL |
| REQ-076 | Meta-Learning | kind-scope validator MUST enforce payload scope, be payload-enforced; scope violations emit AbortArtifact | Runtime validation | CRITICAL |
| REQ-077 | Meta-Learning | Embedding artifacts in ChangePackage MUST be C0 audit metadata only | Runtime enforcement | CRITICAL |
| REQ-078 | Meta-Learning | Proposals altering routing thresholds, safety strictness, or allowed_tools require L5 certification | Runtime gate | CRITICAL |
| REQ-079 | Meta-Learning | Stage 9 commit/activate MUST emit immutable CommitAudit bound to trace_id + version_pointer | Runtime validation | CRITICAL |
| REQ-080 | Guardian | Guardrail Guard MUST evaluate policy; Artifact Guard MUST verify signatures | Boundary enforcement | CRITICAL |
| REQ-081 | Guardian | Both guards MUST be traversed; bypass = sovereignty violation | Boundary traversal test | CRITICAL |
| REQ-082 | Guardian | L5 HARD STOP / REJECT MUST block rejected plans and halt execution | Runtime check | CRITICAL |
| REQ-083 | Guardian | Guardrail Guard enforce VALIDATE→ENFORCE→REMEDIATE→CERTIFY order | Runtime check | CRITICAL |
| REQ-084 | Guardian | Artifact Guard verify replay consistency and signature chain | Runtime validation | CRITICAL |
| REQ-085 | HIL | HumanDecisionArtifact MUST include reviewer_id and reviewer_sig | Schema validation | CRITICAL |
| REQ-086 | HIL | MODIFY_DIFF MUST reference original_plan_hash, include structured_patch_schema, require L5 re-clear | Schema + runtime gate | CRITICAL |
| REQ-087 | HIL | Old signatures must be invalidated after MODIFY_DIFF | Signature test | CRITICAL |
| REQ-088 | Incident | CognitiveDiffBundle MUST exist for incidents with snapshot + trace + diff | Artifact validation | HIGH |
| REQ-089 | Incident | ForensicTraceBuffer MUST be append-only, seal post-incident; post-seal mutation raises error | Runtime test + integrity | CRITICAL |
| REQ-090 | Vigilance | Tier I log; Tier II increase scope | Runtime test | HIGH |
| REQ-091 | Vigilance | Tier III MUST freeze: disable WriteGateway, halt tokens, freeze promotion, freeze routing, block meta-learning | Runtime + guard + gate | CRITICAL |
| REQ-092 | Prompt Governance | All prompts via governance chokepoint; apps_* no system/safety content, no SDK | Static + runtime + AST | CRITICAL |
| REQ-093 | Prompt Governance | prompt_governance MUST emit deterministic prompt_hash binding policy_config_hash | Runtime assertion + check | CRITICAL |
| REQ-094 | Prompt Governance | TokenControl MUST include prompt_hash; RouteDecision MUST include prompt_hash | Schema validation | CRITICAL |
| REQ-095 | Prompt Governance | Prompt composition deterministic (sorted fragments); no concat outside governance | Determinism + static | CRITICAL |
| REQ-096 | Prompt Governance | prompt_governance MUST log domain fragment lineage | Runtime artifact | HIGH |
| REQ-097 | Auth | Capability tokens MUST be scoped, include scope metadata, restrict target resources | Runtime validation + guard | CRITICAL |
| REQ-098 | Auth | Capability tokens MUST expire, be time-bound | Runtime validation | CRITICAL |
| REQ-099 | Auth | L2 MUST enforce tokens at single chokepoint | Structural + runtime | CRITICAL |
| REQ-100 | Auth | Every invocation MUST emit typed ALLOW/DENY decision artifact | Runtime validation | CRITICAL |
| REQ-101 | Auth | Conversational input must not confer authority | Runtime boundary test | HIGH |
| REQ-102 | Kill-Switch | EMBEDDING_ENABLED fail-closed; SovereigntyViolation halts execution | Runtime check | CRITICAL |
| REQ-103 | Kill-Switch | ApprovalGate blocks without approval; UWG enforcement fail-closed | Runtime gate + interception | CRITICAL |
| REQ-104 | Kill-Switch | needs_llm_escalation=False blocks escalation; TIERING_ALLOWLIST blocks non-allowlisted | Runtime routing check | CRITICAL |
| REQ-105 | Replay | Replay input MUST include payload + policy_hash + prompt_hash + context_set | Schema validation | CRITICAL |
| REQ-106 | Replay | Replay MUST be read-only sandbox blocking network IO and SDK invocation | Runtime boundary + env | CRITICAL |
| REQ-107 | Replay | Replay transcript must fully reconstruct side-effects | Replay test | CRITICAL |
| REQ-108 | Replay | Replay MUST use deterministic stubs, detect regressions, forbid mutation tokens | Test + runtime guard | CRITICAL |
| REQ-109 | Replay | Replay gating MUST precede promotion to ACTIVE; harness MUST be versioned | Promotion gate + VersionStore | CRITICAL |
| REQ-110 | Replay | Replay results MUST emit ReplayRunArtifact; artifacts hash-bound; log semantic_clock window | Schema validation | HIGH |
| REQ-111 | Determinism Canon | uuid4 forbidden in determinism-critical artifacts | AST + CI ratchet | CRITICAL |
| REQ-112 | Determinism Canon | All JSON MUST use sort_keys=True; all lists sorted before hashing | Static + runtime test | CRITICAL |
| REQ-113 | Determinism Canon | Canonical encoding UTF-8; hash inputs canonical byte representation | Unit test | CRITICAL |
| REQ-114 | Determinism Canon | No wall-clock in determinism paths; Semantic Clock sole authority | AST + CI + runtime | CRITICAL |
| REQ-115 | Determinism Canon | Semantic Clock tick advances only on StateCommit; dedupe buckets from Semantic Clock | Runtime invariant + unit | CRITICAL |
| REQ-116 | Determinism Canon | Determinism violations MUST fail CI | CI rule | CRITICAL |
| REQ-117 | Sovereignty | No upward import from lower to higher layer | AST + CI | CRITICAL |
| REQ-118 | Sovereignty | No reflection-based bypass of layer boundaries | AST + runtime | CRITICAL |
| REQ-119 | Sovereignty | No dynamic eval/exec in core layers | AST scan | CRITICAL |
| REQ-120 | Sovereignty | No subprocess outside L2; L2 subprocess allowlisted | AST + runtime | CRITICAL |
| REQ-121 | Sovereignty | All subprocess emit ToolTranscript hash-bound to ExecutionTrace | Runtime enforcement | CRITICAL |
| REQ-122 | Sovereignty | L2 reject unsigned envelope, expired tokens, unscoped tokens | Runtime boundary | CRITICAL |
| REQ-123 | Sovereignty | Gateway reject unknown models, audit all outbound, block if kill-switch | Runtime check + logging | CRITICAL |
| REQ-124 | Sovereignty | Embedding factory verify EMBEDDING_ENABLED, no silent backend fallback | Runtime check | CRITICAL |
| REQ-125 | Sovereignty | All vector index writes through UWG; external weight pull requires L5 cert + audit | AST + runtime | CRITICAL |
| REQ-126 | Sovereignty | No direct env mutation in core; no config mutation without ChangePackage | AST + runtime | CRITICAL |
| REQ-127 | Sovereignty | VersionStore injection explicit and logged; all policy_hash changes emit PolicyUpdateProposal | Runtime validation | CRITICAL |
| REQ-128 | Sovereignty | PolicyUpdateProposal bind previous hash, HMAC signed, signature verify | Signature validation | CRITICAL |
| REQ-129 | Sovereignty | No mutable global state; all exceptions subclass SovereigntyError; SovereigntyError halts | AST + static + runtime | CRITICAL |
| REQ-130 | Sovereignty | All aborts emit AbortArtifact with reason_code, trace_id, timestamp_utc | Runtime + schema | HIGH |
| REQ-131 | Sovereignty | CI fail on CRITICAL violation, prevent merge, output failure list by Req ID | CI validation + output | CRITICAL |
| REQ-132 | Sovereignty | CI abort on discovery mismatch, signature failure, replay mismatch | CI validation | CRITICAL |
| REQ-133 | Sovereignty | No TODO/bypass flags; no test-only backdoors in production | Static scan | CRITICAL |
| REQ-134 | Sovereignty | Final compliance = zero CRITICAL violations | Compliance calculation | CRITICAL |
| REQ-135 | Governance | All boundary errors typed exceptions; all sovereignty violations halt | Runtime validation | CRITICAL |
| REQ-136 | Governance | Cross-layer calls typed versioned schemas; version mismatch aborts | AST + runtime | CRITICAL |
| REQ-137 | Governance | Boundary validations log structured audit with trace_id | Runtime audit check | HIGH |
| REQ-138 | Governance | Replay prevents durable mutation; enforces deterministic clock | Runtime enforcement | CRITICAL |
| REQ-139 | Governance | Integer timestamps only; digest includes embedding + commit hash | Schema + output validation | HIGH |
| REQ-140 | Seam | L0 importlib only in allowlisted seams; only allowlisted files import L1-L6 | AST + static scan | CRITICAL |
| REQ-141 | Seam | Only safety_enforcement_seam, mutation_protocol, intent_router upward | AST scan | HIGH |
| REQ-142 | Seam | Seam emit audit artifact, log usage, bind TraceID, no state mutation, deterministic | Runtime + AST + determinism | CRITICAL |
| REQ-143 | Seam | Seam failures abort wave; allowlist versioned; unauthorized expansion fails CI | Runtime + VersionStore + CI | CRITICAL |
| REQ-144 | CI | AST governance tests exist; governance tests enforce zero-violation ceiling + upward coverage | CI inspection + behavior | CRITICAL |
| REQ-145 | CI | Discovery integrity mismatch aborts; abort-on-critical stops compliance | CI pipeline check | CRITICAL |
| REQ-146 | CI | CommitProofInvariant verify implementation commit; AST block SDK + embedding outside factory | CI git + AST job | CRITICAL |
| REQ-147 | CI Ratchet | Zero mutation outside L2; AST-based enforcement required; fail on new forbidden primitive | CI rule | CRITICAL |
| REQ-148 | CI Ratchet | Verify deterministic artifact emission; no provider imports in apps_*; no uuid4 | CI test + static | CRITICAL |
| REQ-149 | CI Ratchet | No wall-clock in determinism paths; verify schema completeness | Static + schema | CRITICAL |
| REQ-150 | CI Ratchet | Verify PromotionDecisionArtifact signature; verify freeze enforcement | Test | CRITICAL |
| REQ-151 | CI Ratchet | Verify TraceID regex; hash canonicalization; replay determinism | Static + unit + test | CRITICAL |
| REQ-152 | CI Ratchet | Verify token lifecycle; side-effect registry; artifact flow legality | Test | CRITICAL |
| REQ-153 | CI Ratchet | Verify Semantic Clock monotonicity; HMAC + SignatureEnclave; meta-learning lock | Test + static | CRITICAL |
| REQ-154 | Boundary | Missing header/token/sig halts; unknown health = unhealthy | Runtime boundary + health | CRITICAL |
| REQ-155 | Discovery | Discovery JSON include integrity_hash, git_hash, blueprint_hash per agent | Schema + CI validation | HIGH |
| REQ-156 | Discovery | ZOMBIE detection hard-fail + abort audit; integrity mismatch aborts | CI + runtime invariant | CRITICAL |
| REQ-157 | Trace | ExecutionTrace include transcript_hash over canonical order | Schema + determinism test | CRITICAL |
| REQ-158 | Trace | HashChainAuditLog detect reorder tampering | Tamper test | CRITICAL |
| REQ-159 | Evidence | EvidencePack bind trace_id, include policy_evals, risk_scores, snapshot_refs | Schema validation | HIGH |
| REQ-160 | Override | PolicyUpdateProposal emitted on override with delta rationale | Runtime + schema | CRITICAL |
| REQ-161 | Surgical | SurgicalManifest validate node_id vs blueprint, manifest_hash SHA-256, forbid line-number | Validation + static + runtime | CRITICAL |
| REQ-162 | Surgical | SSOT/blueprint hash mismatch MUST abort wave | Validation + runtime gate | CRITICAL |
| REQ-163 | Capability Tokens | Tokens typed artifacts binding trace_id + scope + policy_hash | Schema + runtime | CRITICAL |
| REQ-164 | Capability Tokens | Lifecycle: ISSUED→ACTIVE→CONSUMED→EXPIRED→REVOKED | Runtime state machine | CRITICAL |
| REQ-165 | Capability Tokens | Expiration bind semantic_clock; decisions emit ALLOW/DENY artifact | Runtime invariant + artifact | CRITICAL |
| REQ-166 | Side-Effect Registry | All L2 actions declare class; taxonomy-locked; guardian compare declared vs observed | Static + schema + runtime | CRITICAL |
| REQ-167 | Side-Effect Registry | No effects outside registry; registry immutable during execution, versioned | Runtime + VersionStore | CRITICAL |
| REQ-168 | Side-Effect Registry | Registry changes require L5; bind TraceID; enforcement fail-closed | Approval + schema + runtime | CRITICAL |
| REQ-169 | Promotion State | L4 store candidate, shadow, active pointers | VersionStore check | CRITICAL |
| REQ-170 | Promotion State | Candidate→Shadow needs replay; Shadow→Active needs L5 approval | Promotion guard | CRITICAL |
| REQ-171 | Promotion State | Pointer updates emit artifact, atomic, rollback-capable, append-only lineage | Schema + runtime + unit | CRITICAL |
| REQ-172 | Promotion State | Pointer activation re-enter via L0 routing | Runtime guard | CRITICAL |
| REQ-173 | Emergency Freeze | EmergencyFreezeArtifact emitted; bind semantic_clock | Schema validation | CRITICAL |
| REQ-174 | Emergency Freeze | Freeze exit requires L5; state auditable | Runtime guard + log | CRITICAL |
| REQ-175 | Artifact Legality | RESULT/HEALING_PLAN=L2, AGGREGATE=L2 validator, INCIDENT=L6 | Static + runtime | CRITICAL |
| REQ-176 | Artifact Legality | Emission schema-validated; types versioned; flow violation aborts wave | Runtime + schema | CRITICAL |
| REQ-177 | Artifact Legality | Signatures verified before use; hash precedes side-effects | Runtime guard | CRITICAL |
| REQ-178 | Sovereignty Matrix | L0/L3/L4/L5/L6 no mutation; L1 no policy; L4 no execution; L2 no routing | AST + static | CRITICAL |
| REQ-179 | Sovereignty Matrix | Cross-layer schema-validated; imports respect seam allowlist; violations fail CI | Runtime + static + CI | CRITICAL |
| REQ-180 | Phase Lock | Candidate requires Wave 7; shadow requires W7+W6; active requires Guardian+Replay stable | Phase gate | CRITICAL |
| REQ-181 | Phase Lock | Prompt auto-adjust requires governance lock; activation auditable | Phase gate + artifact | CRITICAL |
| REQ-182 | TraceID Canon | TraceID regex ^CC3AL1-[0-9A-F]{8}$; deterministic per seed; propagate all artifacts; collision aborts | Runtime + unit + CI | CRITICAL |
| REQ-183 | Canonical Hashing | All hashing on canonical bytes; input immutable during computation | Unit + runtime guard | CRITICAL |
| REQ-184 | Canonical Hashing | Remove whitespace, sorted keys, deterministic AST serializer | Determinism + static + unit | CRITICAL |
| REQ-185 | Canonical Hashing | SHA-256 default; version in metadata; mismatch emits Incident; collision aborts | Static + schema + runtime | CRITICAL |
| REQ-186 | HMAC Custody | Key NOT in repo; loaded from secure enclave; rotation supported; scope-limited | Static + runtime + key mgmt | CRITICAL |
| REQ-187 | HMAC Custody | Version in metadata; auditable; failed verification emits GuardianArtifact | Schema + log + runtime | CRITICAL |
| REQ-188 | Signature Enclave | All signing in SignatureEnclave; verify pinned keys; log issuance | Static + unit + audit | CRITICAL |
| REQ-189 | Signature Enclave | Reject expired/revoked keys; isolated from L2; deterministic | Runtime + static + determinism | CRITICAL |
| REQ-190 | Signature Enclave | Verification includes artifact hash; artifacts include metadata; missing sig aborts | Runtime + schema + invariant | CRITICAL |
| REQ-191 | Semantic Clock | Vector clock; monotonic entries; conflicts abort wave | Unit + runtime + invariant | CRITICAL |
| REQ-192 | Semantic Clock | State versioned in L4; serialization canonical; advancement emits artifact; bind TraceID | VersionStore + determinism + schema | CRITICAL |
| REQ-193 | Semantic Clock | Resets forbidden; divergence emits Incident; misuse fails CI | Runtime + test + CI | CRITICAL |
| REQ-194 | Knowledge Supervisor | Low-confidence triggers supervision; emit KnowledgeAuditArtifact | Runtime + schema | HIGH |
| REQ-195 | Knowledge Supervisor | Retraining proposal-only; updates via L0; graph advisory-only | Runtime gate + static | CRITICAL |
| REQ-196 | Knowledge Supervisor | Threshold SSOT-bound; artifacts bind semantic_clock; drift emits EvalReport | Static + schema + runtime | HIGH |
| REQ-197 | Knowledge Supervisor | Retraining requires L5 approval + rollback support | Approval gate + VersionStore | CRITICAL |
| REQ-198 | RAG Custody | Emit RetrievalQuery, RetrievedChunks, RerankScores artifacts | Schema validation | HIGH |
| REQ-199 | RAG Custody | Emit CitationBundle; final output cite CitationBundle ID | Schema + runtime | CRITICAL |
| REQ-200 | RAG Custody | Direct external knowledge forbidden; artifacts hash-bound + bind prompt_hash | Static + schema | CRITICAL |
| REQ-201 | RAG Custody | Retrieval deterministic; custody violations fail CI | Determinism + CI | CRITICAL |
| REQ-202 | Guardian Meta | >=95% invariant coverage; block merge on FAIL; deterministic suite | CI rule + test | CRITICAL |
| REQ-203 | Guardian Meta | Verify aggregate gate before L2; verify replay consistency; verify promotion sig | Runtime guard | CRITICAL |
| REQ-204 | Guardian Meta | Reject adapter patterns; verify no illegal imports; validate artifact flow | Static + runtime | CRITICAL |
| REQ-205 | Guardian Meta | Guardian failures fail-closed | Runtime invariant | CRITICAL |
| REQ-206 | L0 Seam | Dynamic import via importlib only; allowlist versioned; unauthorized fails CI | Static + VersionStore + CI | CRITICAL |
| REQ-207 | Incident Telemetry | INCIDENT emit telemetry binding trace_id, semantic_clock, severity, correlation_hash | Runtime + schema | CRITICAL |
| REQ-208 | Incident Telemetry | Correlation hash deterministic; high-velocity via ForensicTraceBuffer; buffer ephemeral | Unit + runtime guard | CRITICAL |
| REQ-209 | Incident Telemetry | Buffer flush atomic; missing buffer on Tier II/III aborts wave | Runtime invariant + guard | CRITICAL |
| REQ-210 | Cognitive Diff | Compare intended vs actual; diff deterministic; bind clock_tick + version pointers | Runtime + unit + schema | CRITICAL |
| REQ-211 | Cognitive Diff | Emit on all Tier III; signed; immutable; stored in L4; replay trace linking | Runtime + sig + VersionStore | CRITICAL |
| REQ-212 | Cognitive Diff | Diff mismatch fails replay | Replay test | CRITICAL |
| REQ-213 | Boundary Snapshot | Include filesystem_hash, git_state_hash, agent_memory_hash, semantic_clock | Schema + runtime | CRITICAL |
| REQ-214 | Boundary Snapshot | Pre-heal + post-heal; post-rollback match pre-wave; hash deterministic; signed | Runtime + unit + sig | CRITICAL |
| REQ-215 | Boundary Snapshot | Storage append-only; retrieval version-bound | VersionStore check + test | CRITICAL |
| REQ-216 | Budget Routing | TokenOverflow triggers RouteRecovery; emit RouteDecision; deterministic | Runtime + schema + unit | CRITICAL |
| REQ-217 | Budget Routing | BudgetGuard before LLM call; bind prompt_hash + policy_hash | Runtime guard + schema | CRITICAL |
| REQ-218 | Budget Routing | Limits SSOT-bound; changes require L5; artifact signed; exhaustion fail-closed | Static + approval + sig | CRITICAL |
| REQ-219 | Law Slot Handler | All execution via LawSlotHandler; enforce capability depletion | Static + runtime | CRITICAL |
| REQ-220 | Law Slot Handler | Depletion bind semantic_clock; overflow aborts wave | Schema + runtime guard | CRITICAL |
| REQ-221 | Law Slot Handler | Log invocations; bind TraceID; isolate tools (ReadOnlyTwins) | Schema + static | CRITICAL |
| REQ-222 | Law Slot Handler | Verify token scope; reject unsigned; deterministic | Runtime + guard + determinism | CRITICAL |
| REQ-223 | MRO Integrity | mro_signature authoritative; safety mixins left of base; adapters forbidden | Runtime + static + scan | CRITICAL |
| REQ-224 | MRO Integrity | Changes require L5; signature hash-bound; violations fail CI | Approval + schema + CI | CRITICAL |
| REQ-225 | MRO Integrity | Signature immutable during wave; mixins no mutation primitives; base no override safety | Runtime + AST + static | CRITICAL |
| REQ-226 | MRO Integrity | Discovery integrity_hash match class source | Runtime validation | CRITICAL |
| REQ-227 | Structure Blueprint | blueprint.py SHA-256 matched before audit; SSOT resolve node_id deterministically | Runtime gate + validation | CRITICAL |
| REQ-228 | Structure Blueprint | Binding failure aborts wave; modifications require L5; hash bind discovery JSON | Runtime + approval + validation | CRITICAL |
| REQ-229 | Structure Blueprint | Discovery JSON schema-validated; ZOMBIE abort; GHOST/INVALID/SYNTAX_ERROR = FAIL | Runtime validation + rule | CRITICAL |
| REQ-230 | Structure Blueprint | root_path authoritative; version recorded in artifacts | Runtime + schema | HIGH |
| REQ-231 | SSOT Enforcement | Manifests bind blueprint version; node_id single definition; serialization_canon match | Schema + runtime + test | CRITICAL |
| REQ-232 | SSOT Enforcement | fix_constraint strict; change_history append-only; provenance ArtifactIDs only | Runtime + invariant + schema | CRITICAL |
| REQ-233 | SSOT Enforcement | Unsigned edits rejected; SignedModify bind original; mismatch emits INCIDENT; violations fail CI | Runtime + test + CI | CRITICAL |
| REQ-234 | Structural Lock | Blueprint hash verified pre-execution; changes trigger audit re-run; load deterministic | Runtime + CI + unit | CRITICAL |
| REQ-235 | Structural Lock | Forbid dynamic class injection; define ownership matrix, thresholds, freeze invariants | Static + schema | CRITICAL |
| REQ-236 | Structural Lock | Blueprint versioned, immutable during wave; hash in PromotionDecision + ReplayRun + RouteDecision + TokenControl + Guardian | VersionStore + runtime + schema | CRITICAL |
| REQ-237 | Structural Lock | Mismatch aborts replay, emits INCIDENT; binding enforced in proposals; quorum required | Runtime + test + approval | CRITICAL |
| REQ-238 | Structural Lock | Binding failures fail-closed | Runtime invariant | CRITICAL |
| REQ-239 | Quorum Governance | Blueprint updates enforce N-of-M signature threshold; threshold versioned in metadata | Runtime sig aggregation + schema | CRITICAL |
| REQ-240 | Quorum Governance | Signatures unique identities, bind blueprint_hash; failure aborts mutation | Signature validation + invariant | CRITICAL |
| REQ-241 | Rollback Integrity | Rollback restore pointers atomically, restore semantic_clock, restore registry snapshot | Runtime + invariant + test | CRITICAL |
| REQ-242 | Rollback Integrity | Artifacts include reason_code; events replay-testable | Schema + replay test | CRITICAL |
| REQ-243 | Audit Completeness | Every wave produce WaveAuditSummary enumerating all artifact IDs, bind clock window | Schema validation | CRITICAL |
| REQ-244 | Audit Completeness | Summaries immutable post-seal; missing summary fails CI | Runtime invariant + CI | CRITICAL |
| REQ-245 | Human Override | Exception include TTL, bind reviewer_sig; expired auto-revoke | Schema + signature + runtime | CRITICAL |
| REQ-246 | Human Override | Activation emit OverrideActivationArtifact; revocation emit OverrideRevocationArtifact | Schema validation | HIGH |
| REQ-247 | Policy Exception | Scope explicitly enumerated (no wildcard), bind policy_hash; require L5 certification | Runtime + schema + approval | CRITICAL |
| REQ-248 | Policy Exception | Lifecycle versioned in L4; override MUST NOT persist beyond TTL | VersionStore + runtime | CRITICAL |
| REQ-249 | Artifact Registry | Unique ArtifactID namespace; deterministic under replay; append-only | Runtime + unit + invariant | CRITICAL |
| REQ-250 | Artifact Registry | Corruption aborts wave | Runtime invariant | CRITICAL |
| REQ-251 | Drift Escalation | Repeated drift escalates tier; emit DriftEscalationArtifact; bind frequency window | Runtime + schema | HIGH |
| REQ-252 | Drift Escalation | Thresholds SSOT-bound; escalation deterministic | Static + unit | HIGH |
| REQ-253 | Cross-Wave Integrity | Consecutive waves link via prev_wave_hash matching prior WaveAuditSummary | Schema + runtime | CRITICAL |
| REQ-254 | Cross-Wave Integrity | Linkage replay-testable; hash chain detects reorder; failure emits INCIDENT | Replay + tamper + invariant | CRITICAL |
| REQ-255 | Governance | All boundary errors MUST be typed exceptions; sovereignty violations halt | Runtime validation | CRITICAL |
| REQ-256 | Governance | Cross-layer calls MUST use typed versioned schemas; version mismatch aborts | AST + runtime | CRITICAL |
| REQ-257 | Governance | Boundary validations MUST log structured audit with trace_id | Runtime audit check | HIGH |
| REQ-258 | Governance | Replay MUST prevent durable mutation; enforce deterministic clock | Runtime enforcement | CRITICAL |
| REQ-259 | Governance | Integer timestamps only; digest includes embedding + commit hash | Schema + output validation | HIGH |
| REQ-260 | Governance | Cross-layer schema changes require VersionStore entry and approval | VersionStore + approval | CRITICAL |
| REQ-261 | Governance | Boundary violation artifacts MUST include trace_id, boundary_name, direction, severity | Schema validation | HIGH |
| REQ-262 | Governance | Governance enforcement deterministic; no conditional bypass paths | Runtime + determinism test | CRITICAL |
| REQ-263 | Governance | Governance configuration SSOT-bound; changes require L5 | Static + approval | CRITICAL |
| REQ-264 | Governance | All governance decisions emit typed artifacts; artifact flow auditable | Runtime + schema | HIGH |
| REQ-265 | Seam | L0 importlib ONLY in allowlisted seams; only allowlisted files import L1-L6 | AST + static scan | CRITICAL |
| REQ-266 | Seam | Only safety_enforcement_seam, mutation_protocol, intent_router upward | AST scan | HIGH |
| REQ-267 | Seam | Seam emit audit artifact, log usage, bind TraceID, no state mutation, deterministic | Runtime + AST + determinism | CRITICAL |
| REQ-268 | Seam | Seam failures abort wave; allowlist versioned; unauthorized expansion fails CI | Runtime + VersionStore + CI | CRITICAL |
| REQ-269 | Seam | Seam audit artifacts include source_module, target_module, invocation_hash | Schema validation | HIGH |
| REQ-270 | Seam | No seam may pass mutable references across layer boundary | Runtime + static | CRITICAL |
| REQ-271 | Seam | Seam allowlist changes require L5 approval and VersionStore entry | Approval + VersionStore | CRITICAL |
| REQ-272 | Seam | Seam invocation count tracked per wave; anomalous count emits INCIDENT | Runtime + schema | HIGH |
| REQ-273 | Seam | All seam modules MUST be deterministic under replay | Replay test + determinism | CRITICAL |
| REQ-274 | Seam | Seam import resolution cached per wave; cache invalidation requires restart | Runtime invariant | HIGH |
| REQ-275 | CI | AST governance tests MUST exist; enforce zero-violation ceiling + upward coverage | CI inspection + behavior | CRITICAL |
| REQ-276 | CI | Discovery integrity mismatch aborts; abort-on-critical stops compliance | CI pipeline check | CRITICAL |
| REQ-277 | CI | CommitProofInvariant verify implementation commit; AST block SDK + embedding outside factory | CI git + AST job | CRITICAL |
| REQ-278 | CI Ratchet | Zero mutation outside L2; AST-based enforcement; fail on new forbidden primitive | CI rule | CRITICAL |
| REQ-279 | CI Ratchet | Verify deterministic artifact emission; no provider imports in apps_*; no uuid4 | CI test + static | CRITICAL |
| REQ-280 | CI Ratchet | No wall-clock in determinism paths; verify schema completeness | Static + schema | CRITICAL |
| REQ-281 | CI Ratchet | Verify PromotionDecisionArtifact signature; verify freeze enforcement | Test | CRITICAL |
| REQ-282 | CI Ratchet | Verify TraceID regex; hash canonicalization; replay determinism | Static + unit + test | CRITICAL |
| REQ-283 | CI Ratchet | Verify token lifecycle; side-effect registry; artifact flow legality | Test | CRITICAL |
| REQ-284 | CI Ratchet | Verify Semantic Clock monotonicity; HMAC + SignatureEnclave; meta-learning lock | Test + static | CRITICAL |
| REQ-285 | CI Ratchet | CI MUST block merge on any CRITICAL violation; output failure list by Req ID | CI validation + output | CRITICAL |
| REQ-286 | CI Ratchet | CI abort on discovery mismatch, signature failure, replay mismatch | CI validation | CRITICAL |
| REQ-287 | CI Ratchet | No TODO/bypass flags in production code; no test-only backdoors | Static scan | CRITICAL |
| REQ-288 | CI Ratchet | CI ratchet thresholds SSOT-bound; changes require L5 | Static + approval | CRITICAL |
| REQ-289 | CI Ratchet | CI pipeline deterministic; same inputs produce same pass/fail | Determinism test | CRITICAL |
| REQ-290 | CI Ratchet | All CI gates emit structured pass/fail artifacts with trace_id | Schema + CI | HIGH |
| REQ-291 | CI Ratchet | New forbidden patterns automatically added to ratchet; no manual bypass | CI rule + static | CRITICAL |
| REQ-292 | CI Ratchet | CI coverage report includes per-domain enforcement layer counts | CI report + schema | HIGH |
| REQ-293 | CI Ratchet | Final compliance = zero CRITICAL violations across full suite | Compliance calculation | CRITICAL |
| REQ-294 | CI Ratchet | CI must verify schema field presence (exact fields, not just type existence) | CI schema validation | CRITICAL |
| REQ-295 | Boundary | Missing header/token/sig halts; unknown health = unhealthy | Runtime boundary + health | CRITICAL |
| REQ-296 | Discovery | Discovery JSON include integrity_hash, git_hash, blueprint_hash per agent | Schema + CI validation | HIGH |
| REQ-297 | Discovery | ZOMBIE detection hard-fail + abort audit; integrity mismatch aborts | CI + runtime invariant | CRITICAL |
| REQ-298 | Discovery | Discovery scan deterministic; same repo state = same discovery output | Determinism test | CRITICAL |
| REQ-299 | Discovery | Agent count waterfall auditable; new agents require manifest update | CI + static | HIGH |
| REQ-300 | Discovery | Discovery JSON schema-validated at CI; schema version tracked | CI + schema | HIGH |
| REQ-301 | Discovery | GHOST/INVALID/SYNTAX_ERROR agents = FAIL; no silent skip | Runtime + CI | CRITICAL |
| REQ-302 | Trace | ExecutionTrace include transcript_hash over canonical order | Schema + determinism test | CRITICAL |
| REQ-303 | Trace | HashChainAuditLog detect reorder tampering | Tamper test | CRITICAL |
| REQ-304 | Trace | Trace artifacts bind semantic_clock tick; log entries append-only | Runtime + invariant | CRITICAL |
| REQ-305 | Trace | Trace hash chain verified at wave end; mismatch emits INCIDENT | Runtime + schema | CRITICAL |
| REQ-306 | Evidence | EvidencePack bind trace_id, include policy_evals, risk_scores, snapshot_refs | Schema validation | HIGH |
| REQ-307 | Evidence | Evidence artifacts hash-bound; replay-verifiable | Schema + replay test | CRITICAL |
| REQ-308 | Evidence | All ToolTranscript hash-bound to ExecutionTrace; missing transcript = gap | Runtime + schema | CRITICAL |
| REQ-309 | Evidence | Evidence retention policy SSOT-bound; no silent deletion | Static + runtime | HIGH |
| REQ-310 | Override | PolicyUpdateProposal emitted on override with delta rationale | Runtime + schema | CRITICAL |
| REQ-311 | Surgical | SurgicalManifest validate node_id vs blueprint, manifest_hash SHA-256, forbid line-number | Validation + static + runtime | CRITICAL |
| REQ-312 | Surgical | SSOT/blueprint hash mismatch MUST abort wave | Validation + runtime gate | CRITICAL |
| REQ-313 | Surgical | Surgical edits MUST be deterministic; same manifest = same edit | Determinism test | CRITICAL |
| REQ-314 | Surgical | Surgical manifest changes audited; bind trace_id + semantic_clock | Schema + runtime | CRITICAL |
| REQ-315 | SSOT | Manifests bind blueprint version; node_id single definition; serialization_canon match | Schema + runtime + test | CRITICAL |
| REQ-316 | SSOT | fix_constraint strict; change_history append-only; provenance ArtifactIDs only | Runtime + invariant + schema | CRITICAL |
| REQ-317 | SSOT | Unsigned edits rejected; SignedModify bind original; mismatch emits INCIDENT; violations fail CI | Runtime + test + CI | CRITICAL |
| REQ-318 | SSOT | SSOT version tracked in all artifacts referencing it | Schema validation | HIGH |
| REQ-319 | SSOT | SSOT changes require L5 approval; audit trail immutable | Approval + invariant | CRITICAL |
| REQ-320 | SSOT | SSOT serialization canonical; hash deterministic | Determinism test + unit | CRITICAL |
| REQ-321 | SSOT | SSOT integrity verified at wave start; mismatch aborts | Runtime gate | CRITICAL |
| REQ-322 | SSOT | SSOT schema versioned; version mismatch fails CI | Schema + CI | CRITICAL |
| REQ-323 | Side-Effect Registry | All L2 actions declare effect class; taxonomy-locked; guardian compare declared vs observed | Static + schema + runtime | CRITICAL |
| REQ-324 | Side-Effect Registry | No effects outside registry; registry immutable during execution, versioned | Runtime + VersionStore | CRITICAL |
| REQ-325 | Side-Effect Registry | Registry changes require L5; bind TraceID; enforcement fail-closed | Approval + schema + runtime | CRITICAL |
| REQ-326 | Side-Effect Registry | Side-effect declarations schema-validated; unknown effect class rejected | Schema + runtime | CRITICAL |
| REQ-327 | Side-Effect Registry | Observed vs declared comparison deterministic; mismatch emits INCIDENT | Runtime + determinism | CRITICAL |
| REQ-328 | Side-Effect Registry | Registry versioned in VersionStore; version bind wave artifacts | VersionStore + schema | HIGH |
| REQ-329 | Side-Effect Registry | Undeclared side-effects abort wave | Runtime invariant | CRITICAL |
| REQ-330 | Side-Effect Registry | Registry taxonomy changes require quorum approval | Approval gate | HIGH |
| REQ-331 | Side-Effect Registry | All registry queries deterministic; same state = same result | Determinism test | CRITICAL |
| REQ-332 | Side-Effect Registry | Registry audit trail append-only; bind trace_id per mutation | Invariant + schema | CRITICAL |
| REQ-333 | Promotion State | L4 store candidate, shadow, active pointers | VersionStore check | CRITICAL |
| REQ-334 | Promotion State | Candidate->Shadow needs replay; Shadow->Active needs L5 approval | Promotion guard | CRITICAL |
| REQ-335 | Promotion State | Pointer updates emit artifact, atomic, rollback-capable, append-only lineage | Schema + runtime + unit | CRITICAL |
| REQ-336 | Promotion State | Pointer activation re-enter via L0 routing | Runtime guard | CRITICAL |
| REQ-337 | Promotion State | Promotion decisions bind semantic_clock; deterministic under replay | Runtime + determinism | CRITICAL |
| REQ-338 | Promotion State | Rollback restores prior pointer atomically; emits RollbackArtifact | Runtime + schema | CRITICAL |
| REQ-339 | Promotion State | No promotion without guardian pass; guardian failure blocks transition | Guardian gate | CRITICAL |
| REQ-340 | Promotion State | Promotion artifacts hash-bound; include prev_state + new_state | Schema + runtime | HIGH |
| REQ-341 | Promotion State | Promotion state machine: CANDIDATE->SHADOW->ACTIVE; no skip | Runtime state machine | CRITICAL |
| REQ-342 | Promotion State | All promotions auditable; lineage queryable by trace_id | Schema + runtime | HIGH |
| REQ-343 | Emergency Freeze | EmergencyFreezeArtifact emitted; bind semantic_clock | Schema validation | CRITICAL |
| REQ-344 | Emergency Freeze | Freeze exit requires L5; state auditable | Runtime guard + log | CRITICAL |
| REQ-345 | Emergency Freeze | Freeze disables WriteGateway; halts token issuance | Runtime enforcement | CRITICAL |
| REQ-346 | Emergency Freeze | Freeze halts promotion pipeline; blocks meta-learning | Runtime gate | CRITICAL |
| REQ-347 | Emergency Freeze | Freeze blocks routing changes; existing routes continue read-only | Runtime enforcement | CRITICAL |
| REQ-348 | Emergency Freeze | Freeze state persisted in L4; survives process restart | VersionStore + runtime | CRITICAL |
| REQ-349 | Emergency Freeze | Partial freeze forbidden; freeze is all-or-nothing | Runtime invariant | CRITICAL |
| REQ-350 | Emergency Freeze | Freeze duration tracked; auto-escalate if exceeds threshold | Runtime + schema | HIGH |
| REQ-351 | Emergency Freeze | Freeze/unfreeze emit paired artifacts for audit | Schema validation | HIGH |
| REQ-352 | Artifact Legality | RESULT/HEALING_PLAN=L2, AGGREGATE=L2 validator, INCIDENT=L6 | Static + runtime | CRITICAL |
| REQ-353 | Artifact Legality | Emission schema-validated; types versioned; flow violation aborts wave | Runtime + schema | CRITICAL |
| REQ-354 | Artifact Legality | Signatures verified before use; hash precedes side-effects | Runtime guard | CRITICAL |
| REQ-355 | Artifact Legality | Artifact type registry authoritative; unknown types rejected | Runtime + static | CRITICAL |
| REQ-356 | Artifact Legality | Artifact flow direction enforced: L2->L4->L6 for results; L6->L5 for incidents | Static + runtime | CRITICAL |
| REQ-357 | Artifact Legality | Version mismatch between artifact type and schema aborts | Runtime validation | CRITICAL |
| REQ-358 | Artifact Legality | Artifact emission rate limited per wave; overflow emits INCIDENT | Runtime + schema | HIGH |
| REQ-359 | Artifact Legality | All artifacts include creation_tick from semantic_clock | Schema validation | CRITICAL |
| REQ-360 | Artifact Legality | Artifact legality checks deterministic; same input = same verdict | Determinism test | CRITICAL |
| REQ-361 | Sovereignty Matrix | L0/L3/L4/L5/L6 no mutation; L1 no policy; L4 no execution; L2 no routing | AST + static | CRITICAL |
| REQ-362 | Sovereignty Matrix | Cross-layer schema-validated; imports respect seam allowlist; violations fail CI | Runtime + static + CI | CRITICAL |
| REQ-363 | Sovereignty Matrix | Matrix verified at CI; drift from declared matrix emits INCIDENT | CI + runtime | CRITICAL |
| REQ-364 | Sovereignty Matrix | Matrix version tracked; changes require L5 + quorum | Approval + VersionStore | CRITICAL |
| REQ-365 | Sovereignty Matrix | No dynamic capability acquisition; capabilities fixed at wave start | Runtime invariant | CRITICAL |
| REQ-366 | Sovereignty Matrix | Matrix enforcement AST-based; no regex heuristics | AST scan | CRITICAL |
| REQ-367 | Sovereignty Matrix | Layer capability violations halt execution | Runtime invariant | CRITICAL |
| REQ-368 | Sovereignty Matrix | Matrix includes read/write/execute/certify permissions per layer | Schema + static | HIGH |
| REQ-369 | Sovereignty Matrix | Matrix audit log append-only; bind trace_id per check | Invariant + schema | HIGH |
| REQ-370 | Sovereignty Matrix | Matrix consistency verified across all enforcement layers | CI + runtime | CRITICAL |
| REQ-371 | Phase Lock | Candidate requires Wave 7; shadow requires W7+W6; active requires Guardian+Replay stable | Phase gate | CRITICAL |
| REQ-372 | Phase Lock | Prompt auto-adjust requires governance lock; activation auditable | Phase gate + artifact | CRITICAL |
| REQ-373 | Phase Lock | Phase transitions emit typed artifacts; bind semantic_clock | Schema + runtime | CRITICAL |
| REQ-374 | Phase Lock | No phase skip; sequential progression enforced | Runtime state machine | CRITICAL |
| REQ-375 | Phase Lock | Phase lock state persisted; survives process restart | VersionStore + runtime | CRITICAL |
| REQ-376 | TraceID Canon | TraceID regex ^CC3AL1-[0-9A-F]{8}$; deterministic per seed | Runtime + unit | CRITICAL |
| REQ-377 | TraceID Canon | Propagate all artifacts; collision aborts wave | Runtime + CI | CRITICAL |
| REQ-378 | TraceID Canon | TraceID generation deterministic under replay | Determinism test | CRITICAL |
| REQ-379 | TraceID Canon | TraceID uniqueness enforced per wave; duplicate detection at emission | Runtime guard | CRITICAL |
| REQ-380 | Canonical Hashing | All hashing on canonical bytes; input immutable during computation | Unit + runtime guard | CRITICAL |
| REQ-381 | Canonical Hashing | Remove whitespace, sorted keys, deterministic AST serializer | Determinism + static + unit | CRITICAL |
| REQ-382 | Canonical Hashing | SHA-256 default; version in metadata; mismatch emits Incident; collision aborts | Static + schema + runtime | CRITICAL |
| REQ-383 | Canonical Hashing | Hash function selection SSOT-bound; no per-module overrides | Static + runtime | CRITICAL |
| REQ-384 | Canonical Hashing | Hash computation deterministic; same bytes = same hash always | Determinism test | CRITICAL |
| REQ-385 | Canonical Hashing | All hash inputs logged (not content, just source ref + byte count) | Schema + runtime | HIGH |
| REQ-386 | Canonical Hashing | Hash chain integrity verified at wave boundaries | Runtime + test | CRITICAL |
| REQ-387 | Canonical Hashing | No truncated hashes in artifacts; full SHA-256 always | Schema validation | HIGH |
| REQ-388 | Canonical Hashing | Hash metadata includes algorithm_id, input_source, computation_tick | Schema validation | HIGH |
| REQ-389 | Canonical Hashing | Hash verification failures emit INCIDENT with expected vs actual | Runtime + schema | CRITICAL |
| REQ-390 | HMAC Custody | Key NOT in repo; loaded from secure enclave; rotation supported; scope-limited | Static + runtime + key mgmt | CRITICAL |
| REQ-391 | HMAC Custody | Version in metadata; auditable; failed verification emits GuardianArtifact | Schema + log + runtime | CRITICAL |
| REQ-392 | HMAC Custody | Key rotation atomic; old signatures remain verifiable during transition | Runtime + key mgmt | CRITICAL |
| REQ-393 | HMAC Custody | Key scope limits which artifact types a key may sign | Runtime + schema | CRITICAL |
| REQ-394 | HMAC Custody | Key usage logged; anomalous signing rate emits INCIDENT | Runtime + schema | HIGH |
| REQ-395 | HMAC Custody | HMAC verification deterministic; same key + same input = same result | Determinism test | CRITICAL |
| REQ-396 | HMAC Custody | Expired keys rejected at verification; no grace period | Runtime guard | CRITICAL |
| REQ-397 | HMAC Custody | Key metadata includes creation_time, rotation_count, scope_list | Schema validation | HIGH |
| REQ-398 | Signature Enclave | All signing in SignatureEnclave; verify pinned keys; log issuance | Static + unit + audit | CRITICAL |
| REQ-399 | Signature Enclave | Reject expired/revoked keys; isolated from L2; deterministic | Runtime + static + determinism | CRITICAL |
| REQ-400 | Signature Enclave | Verification includes artifact hash; artifacts include metadata; missing sig aborts | Runtime + schema + invariant | CRITICAL |
| REQ-401 | Signature Enclave | Enclave key store append-only; revocation logged | Invariant + audit | CRITICAL |
| REQ-402 | Signature Enclave | Signature format versioned; version in artifact metadata | Schema validation | HIGH |
| REQ-403 | Signature Enclave | Enclave isolated process; no direct memory sharing with L2 | Static + runtime | CRITICAL |
| REQ-404 | Signature Enclave | Batch signing deterministic; order-independent | Determinism test | CRITICAL |
| REQ-405 | Signature Enclave | Signature verification cache per wave; invalidated on key rotation | Runtime + invariant | HIGH |
| REQ-406 | Signature Enclave | All verification failures emit SignatureViolationArtifact | Schema + runtime | CRITICAL |
| REQ-407 | Signature Enclave | Enclave startup verifies key integrity before accepting requests | Runtime gate | CRITICAL |
| REQ-408 | Semantic Clock | Vector clock; monotonic entries; conflicts abort wave | Unit + runtime + invariant | CRITICAL |
| REQ-409 | Semantic Clock | State versioned in L4; serialization canonical; advancement emits artifact; bind TraceID | VersionStore + determinism + schema | CRITICAL |
| REQ-410 | Semantic Clock | Resets forbidden; divergence emits Incident; misuse fails CI | Runtime + test + CI | CRITICAL |
| REQ-411 | Semantic Clock | Clock sole time authority; no wall-clock references in determinism paths | AST + CI + runtime | CRITICAL |
| REQ-412 | Semantic Clock | Clock tick bound to state transitions only; idle ticks forbidden | Runtime invariant | CRITICAL |
| REQ-413 | Provider Binding Determinism | Determinism digest MUST include provider_id, model_id, gateway_version, semantic_clock_vector | Runtime digest construction + replay verification + CI determinism test | CRITICAL |
| REQ-414 | Network Egress Guard | All outbound HTTP requests to LLM-serving endpoints (including localhost) MUST originate exclusively from SovereignLLMGateway | Runtime egress filter at L2 boundary + CI test for raw requests | CRITICAL |
| REQ-415 | Provider Substitution Prohibition | SovereignLLMGateway MUST NOT substitute provider/model on failure; any failure MUST be fail-closed | Runtime dispatch check + CI negative control test | CRITICAL |
| REQ-416 | CRITICAL Dual Enforcement Guarantee | Every CRITICAL requirement MUST have >=2 enforcement layers including at least one runtime (except ENFORCEMENT_CLASS=STRUCTURAL which requires >=1 CI/AST layer); CI MUST read ENFORCEMENT_LAYERS and ENFORCEMENT_CLASS metadata per requirement and fail if audit conditions unmet | CI enforcement audit reading per-requirement metadata + runtime meta-check | CRITICAL |
| REQ-417 | Dynamic Runtime Mutation Prohibition | Dynamic runtime mutation of classes, modules, or permissions via monkeypatch, setattr on core layer objects, importlib.reload of core modules, metaclass injection altering layer permissions, or equivalent reflection mechanisms is forbidden in all core layers (L0-L6 and apps_*); AST-only checks are insufficient -- runtime guard required at module load and class definition time | AST scan + runtime guard at module load/class definition + CI ratchet | CRITICAL |
