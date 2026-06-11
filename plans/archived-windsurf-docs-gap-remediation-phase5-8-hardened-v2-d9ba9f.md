---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\gap-remediation-phase5-8-hardened-v2-d9ba9f.md'
original_relative_path: 'gap-remediation-phase5-8-hardened-v2-d9ba9f.md'
source_sha256: 924386f4467054299172f7732100176791b197fa0ddda5cc9726e130dd1ded9d
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-27'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Gap Remediation Plan — Phase 5–8 (Hardened v2) (Close All 72 Remaining PARTIAL)

Close all 72 CRITICAL PARTIAL findings from the post-Phase-4 audit by adding targeted governance tests, CI gates, and minimal production guards — additive only, no architectural redesign, with explicit sovereignty ordering, runtime enforcement, and cryptographically-bound activation gates.

---

## Baseline (post-Phase 4)
- PASS: 345 | PARTIAL: 72 | FAIL: 0
- CRITICAL FAIL: 0 | CRITICAL PARTIAL: 72
- Target: 417 PASS, 0 PARTIAL, 0 FAIL

---

## HARDENING RULES (BINDING — inherited from prior plan)
1. No corpus changes (REQ text/severity/IDs frozen).
2. Each phase declares ONE primary surface; all others frozen for that phase.
3. REQ-416 contract is a phase gate for any CRITICAL REQs touched.
4. REQ-417 mutation lock must remain active throughout.
5. CI/AST changes land BEFORE runtime behavior changes.
6. Every phase closes only after deterministic replay proof + full pytest pass.
7. **NEW:** Explicit dependency ordering: Wave 7 blocked on full Wave 2 closure.
8. **NEW:** Gateway monopoly enforced via runtime interceptor, not just AST.
9. **NEW:** Capability tokens replay-bound with canonical digest proof.
10. **NEW:** Tier III must revoke ALL L2 execution authority including active leases.
11. **NEW:** Promotion pointer updates go through write_gateway + scoped capability tokens.
12. **NEW:** Activation flags persisted in L4, signed, and replay-bound.
13. **NEW:** Global Sovereignty Invariant Test consolidates all guarantees.

---

## Sovereignty Ordering (Hardened Closure Sequence)

1. Discovery integrity (Wave 0) ✅
2. Typed artifacts (Wave 1) ✅
3. Guardian physics (Wave 2) ✅
4. Healer ordering (Wave 3) ✅
5. Control plane routing (Wave 4) ✅
6. Budget + semantic clock (Wave 5) ✅
7. **Execution boundary hardening (Wave 7)** ← CURRENT
8. **Incident freeze integration (Wave 6)** ← CURRENT
9. **Meta-learning (Wave 8)** ← CURRENT

---

## Structural Overview (Hardened v2)

| Phase | Wave | Gap Pattern | REQs Closed | Total | Dependency |
|-------|------|-------------|-------------|-------|------------|
| P5 | W11 | Gateway / SDK bypass + prompt determinism | REQ-011, 012, 095 | 3 | Wave 2 ✅ |
| P5 | W12 | Determinism canon: uuid4 elimination + wall-clock CI gate + no-eval/no-reflection | REQ-111, 114, 118, 129 | 4 | Wave 2 ✅ |
| P5 | W13 | **P0 Execution Boundary Hardening** — Runtime gateway monopoly + capability replay binding | REQ-071, 121, 126, 177, 354 | 5 | **Wave 2 ✅** |
| P6 | W14 | **P1 Tier III Freeze Authority** — Complete L2 revocation + forensic determinism | REQ-346, 347, 378, 384 | 4 | Wave 13 ✅ |
| P6 | W15 | **P2 Incident Monitoring** — CognitiveDiff + deterministic velocity + evacuation discipline | REQ-199, 211, 236, 243, 244, 247 | 6 | Wave 14 ✅ |
| P7 | W16 | **P2 Meta-Learning Prep** — Single metrics emission + blast radius + activation persistence | REQ-060, 063, 298, 337, 375 | 5 | Wave 15 ✅ |
| P7 | W17 | **P2 Promotion Authority** — Scoped pointer updates + single-use tokens | REQ-253, 254, 307, 308, 313, 320 | 6 | Wave 16 ✅ |
| P8 | W18 | **Replay Determinism Closure** — Seam + trace + evidence + cross-wave | REQ-136, 142, 157, 158, 256, 267, 270, 273, 302, 303 | 10 | Wave 17 ✅ |
| P8 | W19 | **Replay Determinism Closure** — Signature enclave + HMAC + canonical hashing | REQ-184, 186, 188, 189, 192, 201, 212, 222, 242, 262, 289, 327, 331, 360, 365, 390, 392, 393, 395, 396, 398, 399, 403, 404, 407, 409, 411, 413 | 29 | Wave 18 ✅ |
| P8 | W20 | **Global Sovereignty Invariant** — Consolidated sovereignty test | — | 1 | Wave 19 ✅ |

**Total: 72 PARTIAL → PASS across 10 waves (with invariant consolidation)**

---

## Phase 5 — P0 Execution Boundary Hardening

### Wave 11: Gateway / SDK Bypass + Prompt Determinism
**Scope: 3 REQs | 3 files changed**

**Gap:** REQ-011/012 — SDK imports found in `apps_rg/tools/ResumeGenerator.py` and `healing_provider_adapters.py` outside SovereignLLMGateway. REQ-095 — prompt fragment concat not deterministically proven.

**Prod changes (additive):**
- `ops_scripts/ci/check_llm_sdk_imports.py` — harden to fail CI on `google.generativeai` outside gateway adapters

**Test files:**
- `tests/governance/test_req011_012_gateway_bypass.py` — assert AST scan finds 0 direct SDK imports outside allowlisted gateway paths; negative control
- `tests/governance/test_req095_prompt_determinism.py` — prove prompt fragment assembly is sorted + stable across two calls

**Evidence:** W11-DETERMINISM-DIGEST

---

### Wave 12: Determinism Canon (uuid4 / wall-clock / eval / reflection)
**Scope: 4 REQs | 2 prod guards + 2 test files**

**Gap:** REQ-111 — uuid4 found in 78 core locations. REQ-114 — 1127 wall-clock hits in determinism paths. REQ-118 — reflection-based bypass not mechanically blocked. REQ-129 — mutable global state guard absent.

**Prod changes (additive):**
- `agentic_core/L2_execution/determinism/determinism_guard.py` — add `assert_no_uuid4()` and `assert_no_wallclock()` context managers (no removal of existing code)
- `ops_scripts/ci/check_determinism_violations.py` — CI gate reading AST for uuid4 + datetime.now/time.time in determinism-critical paths (L0–L5 non-mixin files)

**Test files:**
- `tests/governance/test_req111_no_uuid4_determinism.py` — AST scan proves uuid4 absent from determinism-critical artifact classes
- `tests/governance/test_req114_no_wallclock_determinism.py` — AST scan proves no wall-clock in canonical byte computation paths
- `tests/governance/test_req118_no_reflection_bypass.py` — proves no `getattr`/`setattr` used to bypass layer boundary in core L0–L5
- `tests/governance/test_req129_no_mutable_globals.py` — AST scan: no module-level mutable state in L0–L5 sovereignty-critical modules

**Evidence:** W12-DETERMINISM-DIGEST

---

### Wave 13: P0 Execution Boundary Hardening (Runtime Gateway Monopoly + Capability Replay Binding)
**Scope: 5 REQs | 5 prod guards + 5 test files**

**Gap:** REQ-071 — Stage 8 INTAKE UWG routing not proven. REQ-121 — subprocess ToolTranscript hash binding missing. REQ-126 — direct env mutation not blocked. REQ-177/354 — sig-before-side-effect not proven for all consumption paths. **NEW:** Gateway monopoly not runtime-enforced; capability tokens not replay-bound with canonical digest.

**Prod changes (additive):**
- `system_learning/enforcement/` — add `assert_uwg_routed(bundle)` check to Stage 8 intake
- `agentic_core/L2_execution/tools/safe_subprocess.py` — ensure `ToolTranscript.hash` populated from stdout canonical bytes
- `agentic_core/L0_routing/enforcement/mutation_prohibition.py` — add `assert_no_direct_env_mutation()` guard
- `agentic_core/L2_execution/capability/capability_token.py` — add `bind_to_replay_digest(digest_hash)` method
- `ops_scripts/ci/check_gateway_monopoly.py` — AST scan enforcing zero FileIo imports outside L2
- **NEW** `agentic_core/L2_execution/enforcement/runtime_write_interceptor.py` — monkeypatch `open`, `os.open`, `pathlib.Path.write*` to route through write_gateway in replay_mode
- **NEW** `agentic_core/L2_execution/capability/canonical_digest.py` — compute digest including plan hash, ToolTranscript hash, capability scope, activation flags, provider binding, semantic clock tick, Guardian policy hash
- **NEW** `ops_scripts/ci/check_canonical_digest_stability.py` — prove digest identical across two runs

**Test files:**
- `tests/governance/test_req071_stage8_uwg_routing.py` — prove Stage 8 INTAKE routes through UWG; bypass raises
- `tests/governance/test_req121_126_subprocess_env.py` — prove ToolTranscript hash bound; direct `os.environ` mutation raises
- `tests/governance/test_req177_354_sig_before_effect.py` — prove sig verification precedes mutation in all 5 artifact consumption paths
- `tests/governance/test_req_p0_gateway_monopoly.py` — AST scan proves zero FileIo imports outside L2
- **NEW** `tests/governance/test_req_p0_runtime_write_interceptor.py` — prove runtime interceptor blocks all non-gateway writes; monkeypatch effective
- **NEW** `tests/governance/test_req_p0_canonical_digest_stability.py` — two-run digest computation proves identical output
- **NEW** `tests/governance/test_req_p0_capability_replay_binding.py` — prove capability tokens include canonical digest hash; missing hash → token invalid

**P0 Closure Criteria (Explicit):**
- [ ] Zero AST violations for FileIo imports outside L2
- [ ] Runtime write interceptor active and effective
- [ ] Gateway monopoly proven (100% writes through write_gateway)
- [ ] Capability tokens replay-bound with canonical digest
- [ ] Digest canonicalization proven stable across runs
- [ ] Decision artifacts cryptographically included in replay digest
- [ ] L0 seam allowlist verified
- [ ] Guardian signature enclave validated

**Evidence:** W13-P0-CLOSURE-DIGEST

---

## Phase 6 — P1 Tier III Freeze Authority + P2 Incident Monitoring

### Wave 14: P1 Tier III Freeze Authority (Complete L2 Revocation + Forensic Determinism)
**Scope: 4 REQs | 3 prod guards + 3 test files**

**Gap:** REQ-346/347 — Emergency Freeze halts promotion + blocks routing not independently tested. REQ-378/384 — TraceID generation + hash computation determinism not proven. **NEW:** Freeze must invalidate active leases and in-flight execution.

**Prod changes (additive):**
- `agentic_core/L2_execution/enforcement/emergency_freeze.py` — add `revoke_l2_execution_authority()` method
- **NEW** `agentic_core/L2_execution/enforcement/emergency_freeze.py` — add `kill_active_leases()` and `invalidate_in_flight_execution()` methods
- **NEW** `agentic_core/L2_execution/enforcement/emergency_freeze.py` — add `override_activation_flags()` method
- `agentic_core/L0_routing/types/determinism_types.py` — add `ForensicTraceBuffer` dataclass with semantic_clock ticks only
- `agentic_core/L0_routing/enforcement/trace_id_generator.py` — enforce deterministic TraceID under replay

**Test files:**
- `tests/governance/test_req346_347_tier3_authority.py` — prove Tier III evacuation revokes L2 capability tokens and blocks new routing
- `tests/governance/test_req378_384_forensic_determinism.py` — prove ForensicTraceBuffer uses semantic clock only; TraceID deterministic under replay
- **NEW** `tests/governance/test_req_p1_freeze_complete_revocation.py` — prove freeze kills active leases, invalidates in-flight execution, overrides flags
- **NEW** `tests/governance/test_req_p1_freeze_timing.py` — prove freeze takes effect immediately; no execution window

**Evidence:** W14-P1-FREEZE-DIGEST

---

### Wave 15: P2 Incident Monitoring (CognitiveDiff + Deterministic Velocity + Evacuation Discipline)
**Scope: 6 REQs | 3 prod guards + 4 test files**

**Gap:** REQ-199/211 — CitationBundle + CognitiveDiffBundle emission not tested. REQ-236 — blueprint_hash in PromotionDecisionArtifact not proven. REQ-243/244/247 — WaveAuditSummary emission + immutability + wildcard scope not tested. **NEW:** Velocity calculation must be deterministic; no float drift.

**Prod changes (additive):**
- `agentic_core/L4_state/types/cognitive_diff.py` — add `compare_to_trusted_trace(trace_hash)` method
- `agentic_core/L4_state/types/telemetry.py` — add `EvacuationDiscipline` dataclass with semantic_clock
- **NEW** `agentic_core/L4_state/enforcement/deterministic_velocity.py` — velocity calculation using integer tick deltas, fixed window size, stable ordering, no float math

**Test files:**
- `tests/governance/test_req199_211_236_emission.py` — prove CitationBundle emitted; CognitiveDiffBundle emitted on Tier III; blueprint_hash in PromotionDecisionArtifact
- `tests/governance/test_req243_244_247_audit_completeness.py` — prove WaveAuditSummary emitted per wave; post-seal mutation raises; wildcard scope rejected
- `tests/governance/test_req_p2_cognitive_diff_trusted.py` — prove CognitiveDiff compares cryptographically sealed execution trace; advisory diff without trusted trace rejected
- `tests/governance/test_req_p2_evacuation_discipline.py` — prove evacuation uses semantic clock only; no wall-clock fallback
- **NEW** `tests/governance/test_req_p2_deterministic_velocity.py` — two-run velocity calculation with identical inputs produces identical anomaly output; no float drift

**Evidence:** W15-P2-INCIDENT-DIGEST

---

## Phase 7 — P2 Meta-Learning Prep + Promotion Authority

### Wave 16: P2 Meta-Learning Prep (Single Metrics Emission + Blast Radius + Activation Persistence)
**Scope: 5 REQs | 4 prod guards + 4 test files**

**Gap:** REQ-060/063 — meta-learning stage + proposer replay proof absent. REQ-298/337 — discovery scan + promotion decision determinism not tested. REQ-375 — phase lock persistence not tested. **NEW:** Activation flags must persist in L4; metrics emission must be mechanically sealed.

**Prod changes (additive):**
- `agentic_core/L4_state/enforcement/metrics_emission.py` — add `single_authoritative_emission()` control-spine chokepoint
- **NEW** `agentic_core/L4_state/enforcement/metrics_emission.py` — add runtime guard rejecting duplicate emissions per trace_id
- `agentic_core/L4_state/enforcement/blast_radius.py` — add `max_blast_radius_per_proposal` cap
- **NEW** `agentic_core/L4_state/enforcement/blast_radius.py` — add deterministic blast radius computation bound to explicit state surface
- `agentic_core/L4_state/enforcement/phase_lock_store.py` — add `persist()` / `restore()` for phase lock state
- **NEW** `agentic_core/L4_state/enforcement/activation_flags.py` — L4-persisted, signed, replay-bound activation flags
- **NEW** `ops_scripts/ci/check_metrics_emission_chokepoint.py` — AST scan forbidding metric emission outside control spine

**Test files:**
- `tests/governance/test_req060_063_meta_learning_replay.py` — two-run Stage 6 proposer order; assert identical ChangePackage list
- `tests/governance/test_req298_337_discovery_promotion.py` — discovery scan deterministic; promotion decision replay stable
- `tests/governance/test_req375_phase_lock_persistence.py` — phase lock survives process restart
- `tests/governance/test_req_p2_metrics_single_emission.py` — prove metrics artifact emitted from single control-spine point; duplicate emissions rejected
- `tests/governance/test_req_p2_blast_radius_containment.py` — enforce maximum blast radius per proposal; exceed → rejection; deterministic computation
- **NEW** `tests/governance/test_req_p2_activation_flags_persistence.py` — prove activation flags persist in L4, survive restart, are replay-bound
- **NEW** `tests/governance/test_req_p2_metrics_chokepoint_ast.py` — AST scan proves zero metric emissions outside control spine

**Evidence:** W16-P2-META-PREP-DIGEST

---

### Wave 17: P2 Promotion Authority (Scoped Pointer Updates + Single-Use Tokens)
**Scope: 6 REQs | 3 prod guards + 4 test files**

**Gap:** REQ-253/254 — cross-wave prev_wave_hash linkage not tested. REQ-307/308 — evidence artifacts + ToolTranscript hash binding not tested. REQ-313/320 — surgical edit + SSOT hash determinism not tested. **NEW:** Promotion tokens must be scope-limited, single-use, time-bounded.

**Prod changes (additive):**
- `agentic_core/L4_state/enforcement/promotion_authority.py` — add `update_pointer_via_gateway(new_pointer, capability_token)` method
- `agentic_core/L2_execution/UniversalWriteGateway.py` — add `validate_promotion_pointer_update()` method
- **NEW** `agentic_core/L2_execution/capability/promotion_token.py` — scoped capability token with allowed_action="pointer_update", target_namespace, semantic_clock_window, replay_digest_binding, single_use_nonce
- **NEW** `agentic_core/L2_execution/capability/promotion_token.py` — add `validate_scope_and_use()` method

**Test files:**
- `tests/governance/test_req253_254_cross_wave_linkage.py` — prove consecutive WaveAuditSummary prev_wave_hash linkage; tamper → fail
- `tests/governance/test_req307_308_evidence_replay.py` — prove EvidencePack hash-bound; ToolTranscript missing → gap detected
- `tests/governance/test_req313_320_surgical_ssot_replay.py` — two-run SurgicalManifest apply + SSOT hash; assert identical
- `tests/governance/test_req_p2_promotion_gateway_authority.py` — prove promotion pointer updates route through write_gateway with capability tokens; bypass raises
- `tests/governance/test_req_p2_promotion_capability_scope.py` — prove promotion capability tokens limited to pointer updates only
- **NEW** `tests/governance/test_req_p2_promotion_token_single_use.py` — prove promotion tokens are single-use; reuse rejected
- **NEW** `tests/governance/test_req_p2_promotion_token_time_bounded.py` — prove promotion tokens expire via semantic clock window

**Evidence:** W17-P2-PROMOTION-DIGEST

---

## Phase 8 — Replay Determinism Closure + Global Invariant

### Wave 18: Replay Determinism Closure — Seam + Trace + Evidence + Cross-Wave
**Scope: 10 REQs | 1 prod guard + 4 test files**

**Gap:** REQ-136/256 — cross-layer typed schema version mismatch not mechanically tested. REQ-142/267/273 — seam audit artifact emission + replay not tested. REQ-157/158/302/303 — trace + hash-chain replay not tested. REQ-270 — mutable seam reference not blocked.

**Prod changes (additive):**
- `agentic_core/L0_routing/seam/seam_audit.py` — add `SeamAuditRecord` dataclass with `invocation_hash` field; emit from existing seam hooks

**Test files:**
- `tests/governance/test_req136_256_cross_layer_schema.py` — prove typed cross-layer call schemas are version-pinned; simulate mismatch → abort
- `tests/governance/test_req142_267_seam_audit_determinism.py` — two-run digest of seam audit records proves identical output
- `tests/governance/test_req270_273_seam_mutable_ref.py` — prove seam passes only immutable (frozen dataclass / tuple) references; prove seam replay stable
- `tests/governance/test_req157_302_trace_replay.py` — two-run replay of ExecutionTrace; assert transcript_hash identical
- `tests/governance/test_req158_303_hash_chain_tamper.py` — inject reorder into HashChainAuditLog; assert detection raises

**Evidence:** W18-REPLAY-SEAM-TRACE-DIGEST

---

### Wave 19: Replay Determinism Closure — Signature Enclave + HMAC + Canonical Hashing
**Scope: 29 REQs | 2 prod guards + 8 test files**

**Gap:** REQ-184/381/384 — canonical hashing determinism not replay-proven. REQ-186/390/392/393/395/396 — HMAC custody + lifecycle not tested. REQ-188/189/398/399/403/404/407 — Signature Enclave isolation + batch signing not tested. REQ-192/201/212/222/242/262/289/327/331/360/365 — semantic clock, RAG, law slot, rollback, governance, CI, side-effect registry, artifact legality not replay-proven. REQ-409/411/413 — semantic clock advancement + no wall-clock + provider binding not tested.

**Prod changes (additive):**
- `agentic_core/L2_execution/enforcement/key_source.py` — add `assert_key_scope(artifact_type)` method; add `reject_expired_key()` guard
- `agentic_core/L0_routing/types/determinism_types.py` — add `SemanticClockAdvancementArtifact` dataclass (if absent)

**Test files:**
- `tests/governance/test_req184_381_384_canonical_hash_replay.py` — two-run canonical serializer; assert identical bytes both runs
- `tests/governance/test_req186_390_392_393_395_396_hmac_lifecycle.py` — prove HMAC key not in repo; key scope limits; rotation atomic; expired key rejected; verification deterministic
- `tests/governance/test_req188_189_398_399_403_404_407_enclave_replay.py` — prove signing enclave-only; expired key rejection; isolation; batch signing deterministic; startup integrity
- `tests/governance/test_req192_409_semantic_clock_replay.py` — two-run SemanticClock advancement; assert identical artifact + L4 version binding; no wall-clock in AST
- `tests/governance/test_req201_212_222_242_262_289_rag_law_rollback.py` — RAG retrieval deterministic; CognitiveDiff mismatch fails replay; LawSlotHandler token scope replay; rollback artifacts replay-testable; governance enforcement deterministic; CI pipeline deterministic
- `tests/governance/test_req327_331_360_365_side_effect_legality.py` — side-effect registry comparison/query deterministic; artifact legality deterministic; capability acquisition lock
- `tests/governance/test_req411_413_provider_binding.py` — no wall-clock in SemanticClock AST; provider_id in digest

**Evidence:** W19-REPLAY-FINAL-DIGEST

---

### Wave 20: Global Sovereignty Invariant (Consolidated Test)
**Scope: 1 invariant | 1 test file**

**Purpose:** Consolidate all sovereignty guarantees into a single test that prevents drift.

**Test file:**
- `tests/governance/test_global_sovereignty_invariant.py` — asserts:
  - No upward mutation possible (runtime interceptor active)
  - Gateway is sole LLM seam (AST + runtime proof)
  - Embedding cannot affect routing (deterministic replay)
  - Kill-switch cannot be bypassed (freeze authority test)
  - Signature verification always precedes side-effect (5 paths tested)
  - Activation flags are persisted and replay-bound
  - Capability tokens are scoped and single-use
  - Metrics emission is mechanically sealed
  - Blast radius is deterministically bounded
  - Digest canonicalization is stable

**Evidence:** W20-GLOBAL-SOVEREIGNTY-DIGEST

---

## Meta-Learning Activation Gate (Hardened v2)

### L4-Persisted Activation Flags
File: `agentic_core/L4_state/enforcement/activation_flags.py`
```python
@dataclass(frozen=True)
class ActivationFlags:
    # P0 Execution Boundary
    execution_hardened: bool = False
    mutation_surface_zero: bool = False
    guardian_coverage: float = 0.0

    # P1 Freeze Authority
    freeze_authority_active: bool = False

    # P2 Meta-Learning Prepared
    meta_learning_prepared: bool = False
    blast_radius_containment_active: bool = False

    # Meta-Learning Activation (requires all above)
    meta_learning_enabled: bool = False

    # Metadata for replay binding
    semantic_clock_tick: int = 0
    replay_digest_hash: str = ""
    signature: str = ""  # Guardian signature
```

### Activation Check in Meta-Learning Entry
```python
def assert_meta_learning_allowed():
    flags = load_activation_flags_from_l4()

    # Verify signature
    if not verify_guardian_signature(flags.signature, flags):
        raise RuntimeError("Activation flags signature invalid")

    # Check P0
    if not (flags.execution_hardened and flags.mutation_surface_zero and flags.guardian_coverage >= 0.95):
        raise RuntimeError("P0 execution boundary not hardened")

    # Check P1
    if not flags.freeze_authority_active:
        raise RuntimeError("P1 freeze authority not active")

    # Check P2
    if not (flags.meta_learning_prepared and flags.blast_radius_containment_active):
        raise RuntimeError("P2 meta-learning not prepared")

    # Final gate
    if not flags.meta_learning_enabled:
        raise RuntimeError("Meta-learning explicitly disabled")

    # Verify replay binding
    current_digest = compute_canonical_digest()
    if flags.replay_digest_hash != current_digest:
        raise RuntimeError("Activation flags digest mismatch")
```

---

## Execution Protocol (per wave)

Each wave follows the Phase Execute workflow:
1. Preflight — inspect all prod modules referenced
2. Prod diff — additive changes only (declare N files before starting)
3. Test files — create `test_req*.py` with `@pytest.mark.governance`
4. `python -m pytest -q --color=no` — full suite, verify 0 new failures
5. `git commit` → CODE_COMMIT
6. Write + commit evidence file → EVIDENCE_COMMIT
7. Seal evidence

**Additional for P0/P1/P2 waves:**
- After evidence seal, update activation flags in L4 with Guardian signature
- Verify flags persist across process restart
- Verify flags are replay-bound in subsequent waves

---

## Target End State

| Metric | Current | Target |
|--------|---------|--------|
| PASS | 345 | **417** |
| PARTIAL | 72 | **0** |
| FAIL | 0 | 0 |
| CRITICAL FAIL | 0 | 0 |
| CRITICAL PARTIAL | 72 | **0** |
| Governance tests | 885 | ~1000+ |
| P0 Closure | ❌ | ✅ |
| P1 Authority | ❌ | ✅ |
| P2 Prepared | ❌ | ✅ |
| Meta-Learning Ready | ❌ | ✅ |
| Global Invariant | ❌ | ✅ |

---

## Sovereignty Verification Checklist (Final)

Before meta-learning activation:
- [ ] Wave 2 (Guardian Physics) fully closed
- [ ] Wave 13 (P0 Execution Boundary) explicit closure criteria met
- [ ] Runtime write interceptor active and effective
- [ ] Gateway monopoly AST + runtime proof shows 0 violations
- [ ] Capability tokens include canonical digest hash
- [ ] Digest canonicalization proven stable across runs
- [ ] Tier III can revoke ALL L2 execution authority including leases
- [ ] Promotion pointer updates go through write_gateway with scoped tokens
- [ ] Activation flags persisted in L4, signed, replay-bound
- [ ] Metrics emission mechanically sealed at runtime
- [ ] Blast radius deterministically bounded
- [ ] Global Sovereignty Invariant test passes
- [ ] Full pytest suite passes
- [ ] Deterministic replay proof for all surfaces
- [ ] Guardian signature on activation flags valid

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

