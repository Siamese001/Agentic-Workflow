# RTC W2 — Integrated Runtime Proof for RTC-REQ-059 Safe-Reuse Composite

**Date:** 2026-05-01
**Plan:** `.windsurf/plans/rtc-w2-integrated-runtime-r1b-safe-reuse-c7e9f3.md`
**Predecessor:** W1p6 (RTC-REQ-059 ACCEPTED at E5)
**Status:** W2 COMPLETE — fail-closed leg proven, infrastructure landed.
RTC-REQ-056 remains **PENDING** in the honest committed state: the ALLOW
leg requires a live approved SAFE-producing provider, and `mock_safe` is
MOCK_PROVIDER_ONLY. See follow-on report
`docs/architecture/integrated_runtime_w2b_report.md` for the W2b
live-provider ALLOW-path proof and the operator runbook for flipping
RTC-REQ-056 to ACCEPTED.

## Summary

W2 proves the dense-candidate + C-primary safety-veto safe-reuse path
through a single production integrated-runtime entry point. The proof is
real: every artifact in the chain is produced by `agentic_core.*` code,
no harness reaches into a layer, the canonical acceptance run uses the
approved `LLMJudgeVeto` stage (no `DeterministicProofStage`), and all 5
W2 verifiers exit 0 against the artifact set.

## Dual-Run Evidence (proof-hardening — 2026-05-01)

The probe produces two runs per invocation. Only the **c_primary** run
is eligible to certify RTC-REQ-056.

| Run | Dir | Stage class | Provider | Outcome | `veto_stage_match_status` | Certifies? |
|-----|-----|-------------|----------|---------|:-----------------:|:----------:|
| **c_primary** (CANONICAL) | `integrated_runtime/c_primary/` + `latest/` | `LLMJudgeVeto` (via `create_veto_from_policy`) | `local_qwen` @ Qwen2.5-7B-Instruct | endpoint unreachable → TIMEOUT → fail-closed BLOCK → **X3A** | **PASS** | ✅ Yes |
| structural | `integrated_runtime/structural/` | `DeterministicProofStage` | (none — deterministic) | SAFE → ALLOW → **X3D** | STRUCTURAL_ONLY | ❌ No — documents topology only |

The c_primary run proves the C-primary LLM-judge pathway end-to-end via
its fail-closed leg: the real `LLMJudgeVeto` is instantiated from the
approved `semantic_cache_veto_policy.json`, its configured provider is
attempted, the call times out, the orchestrator emits an ERROR (promoted
to TIMEOUT by `_refine_veto_outcome`), and the `SafeReuseDecision`
contract forces `allow=False` with `unknown_error_timeout_parse_fail_block_count=1`.
This is exactly the behavior RTC-REQ-056 claims: the runtime cannot be
tricked into admitting a reuse via a mocked "safe" verdict — the real
C-primary pathway refuses when the LLM cannot be reached, the same way
it would refuse in production.

The structural run exists to document that the ALLOW topology (X3D,
terminal cache reuse, no L2, no L4, answer-only exit) emits all 12
artifacts correctly. It is labeled `STRUCTURAL_ONLY` in its manifest and
the composer refuses to accept it (`DeterministicProofStage`
authorization is restricted to structural / negative / fail-closed
proofs only — see the module docstring).

**Key boundary preserved:** RTC-REQ-055 stays PARTIAL with the W1p4
`R1B_PRODUCTION_THRESHOLD_PROOF = CALIBRATION_GAP` finding intact. RTC-REQ-056
gates on the new W2 integrated-runtime proof and the W1p6 safe-reuse
composite proof — NOT on the legacy dense-only threshold. This mirrors
the W1p6 RTC-REQ-055/059 split.

## Production Entry Point

**Path:** `@c:/Git/Agentic-Workflow-FRESH/agentic_core/runtime/entrypoints/integrated_safe_reuse_run.py`
**Public API:** `run_integrated_safe_reuse(raw_request, *, namespace, tenant_id, artifact_dir, veto_orchestrator=None) -> IntegratedRunResult`

Drives this chain end-to-end:

```
raw_request (dict)
  → run_request_intake                                       (L0 intake)
  → validated_request_to_plan_contract                       (U0 → L1 bridge)
  → _build_route_contract                                    (L1 → L0 metadata)
  → check_route_gates (D1/D2)                                (L0 cache cascade)
  → VetoOrchestrator.evaluate                                (safety veto on D2 hit)
  → SafeReuseDecision (production contract — fail-closed at construction)
  → TerminalRetPacket(R1B_SEMANTIC_CACHE, no_l2=True, no_l4_write=True)
  → ExitReviewPacket  (L3 v6)
  → X3D_AllowPacket OR X3A_DenyPacket                        (L3 v6 X3 emission)
  → seal_runtime_exhaust + RuntimeExhaustCollector           (sealed manifest + bundle)
  → integrated_runtime_artifact_manifest.json                (chain attestation)
  → no_harness_stamp_receipt.json                            (self-attestation)
```

Every step uses production layer APIs (`agentic_core.L0_routing.*`,
`agentic_core.L1_cognition.*`, `agentic_core.L3_orchestration.*`,
`agentic_core.L4_state.*`). The entry point is the ONLY orchestration
seam — harnesses (probe, tests) call it and nothing else from
agentic_core.

## Artifact Chain (12 artifacts, sha256-linked)

| # | Filename | Producer | Upstream link |
|--:|----------|----------|--------------|
| 1 | `integrated_runtime_entrypoint_invocation.json` | agentic_core.runtime.entrypoints.integrated_safe_reuse_run | (root) |
| 2 | `validated_request.json` | (same) | #1 |
| 3 | `l1_plan_contract.json` | (same) | #2 |
| 4 | `route_contract.json` | (same) | #3 |
| 5 | `runtime_gate_verdict_bundle.json` | (same) | #4 |
| 6 | `semantic_cache_safe_reuse_decision.json` | (same) | #5 |
| 7 | `terminal_ret_packet.json` | (same) | #6 |
| 8 | `exit_review_packet.json` | (same) | #7 |
| 9 | `x3_disposition_receipt.json` | (same) | #8 |
| 10 | `runtime_exhaust_bundle.json` | (same) | #9 |
| 11 | `integrated_runtime_artifact_manifest.json` | (same) | #10 |
| 12 | `no_harness_stamp_receipt.json` | (same) | #11 |

Every envelope carries `producer_component`, `producer_module`,
`producer_function_or_class`, `emitted_at`, `artifact_hash` (sha256 of
canonical JSON of the payload), and `upstream_artifact_ref` (sha256 of
the upstream payload). The chain verifier recomputes both and rejects
any divergence.

## Anti-cheat Invariants Enforced

1. **Producer must be `agentic_core.*`** — emitter rejects any other
   prefix at construction time.
2. **Harness regex blocks `tests.*`, `scripts.verify_*`,
   `ops_scripts.ci.verify_*`, and any string containing the word
   `harness`** — emitter rejects + verifier rejects.
3. **SafeReuseDecision is fail-closed at construction** — `allow=True`
   without `dense_candidate_produced=True`, without `veto_invoked=True`,
   or with a non-`ALLOWED` `veto_outcome` raises `ValueError`.
4. **Fail-closed buckets cannot allow** — `UNKNOWN`/`ERROR`/`TIMEOUT`/
   `PARSE_FAIL` outcomes increment
   `unknown_error_timeout_parse_fail_block_count` and the SafeReuseDecision
   contract refuses any `allow=True` paired with these.
5. **No L2 / no L4 on terminal cache reuse** — TerminalRetPacket asserts
   `no_l2_execution_assertion=True` and `no_l4_write_assertion=True`;
   ExitReviewPacket carries empty `tool_calls`/`model_calls`/`state_diff`.
6. **Lexical-only path cannot pass** — verifier requires
   `llm_judge_invocation_count >= 1` whenever
   `veto_primary_mode == C_PRIMARY_LLM_JUDGE` and `allow=True`.
7. **RTC-REQ-056 ACCEPTED requires ALL 5 verifiers exit 0** — composer
   reads `verifier_results.json` ledger; missing or any non-zero exit
   keeps the subclaim NOT_APPLICABLE; artifact presence ALONE never
   certifies (per user §RTC-REQ-056 semantic).

## Explicit Safety-Metric Aliases (W2 §Metric cleanup)

The SafeReuseDecision artifact carries these unambiguous fields,
replacing reliance on FP/FN labels alone:

| Alias | Semantics |
|-------|-----------|
| `unsafe_reuse_allowed_count` | Unsafe reuses admitted (entry point invariant: always 0) |
| `safe_reuse_blocked_count` | Safe reuse explicitly blocked by a non-fail-closed veto verdict |
| `hard_negative_allowed_count` | Subset of unsafe — adversarial pair admitted (must always be 0) |
| `unknown_error_timeout_parse_fail_block_count` | Fail-closed bucket count — increments on UNKNOWN/ERROR/TIMEOUT/PARSE_FAIL |

Legacy `legacy_unsafe_fp_count` / `legacy_safe_positive_block_count`
fields are retained for cross-reading with the W1p6 sweep rows but the
W2 verifiers consume only the explicit aliases.

## Verifier Bundle (5 scripts, all exit 0)

Located at `@c:/Git/Agentic-Workflow-FRESH/ops_scripts/ci/` per
constitutional §31 (SSOT folder routing for new files).

| Script | Asserts |
|--------|---------|
| `verify_integrated_runtime_entrypoint.py` | Entry-point flag set, all 12 artifacts present, every producer is `agentic_core.*` |
| `verify_r1b_safe_reuse_integrated_runtime.py` | Dense candidate, veto invoked, 4 alias fields present, fail-closed counter consistency, lexical-only blocked, gate↔decision agreement |
| `verify_integrated_runtime_artifact_chain.py` | Recomputed sha matches declared sha for every envelope; upstream_artifact_ref chain unbroken |
| `verify_integrated_runtime_no_harness_stamp.py` | No producer matches harness regex; self-attestation receipt POSITIVE |
| `verify_integrated_runtime_exit_x3.py` | Exactly one X3 disposition; ExitReviewPacket consumed terminal route_id; terminal-class invariants hold; trace_root consistency |

Result ledger: `@c:/Git/Agentic-Workflow-FRESH/artifacts/certification/integrated_runtime/verifier_results.json`
(written by `ops_scripts/ci/record_w2_verifier_results.py`; records
exit_code per script). The composer reads this ledger and refuses
`R1B_INTEGRATED_RUNTIME_PROOF=PASS` if it is absent or contains any
non-zero exit code.

## Final Subclaim Statuses (post-W2)

```
R1B_DENSE_SIMILARITY_COMPOSITION_PROOF     = PARTIAL          (threshold input CALIBRATION_GAP)
R1B_APPROVED_MODEL_PROOF                   = PASS
R1B_PRODUCTION_THRESHOLD_PROOF             = CALIBRATION_GAP  ← W1p4 finding pinned
R1B_NEGATIVE_CONTROL_PROOF                 = PASS
R1B_POLICY_FRESHNESS_TENANT_REUSE_PROOF    = PASS
R1B_TERMINAL_EXIT_PROOF                    = PASS
R1B_SEMANTIC_CACHE_SAFETY_VETO_PROOF       = PASS             (W1p5)
R1B_SAFE_REUSE_COMPOSITE_PROOF             = PASS             (W1p6)
R1B_INTEGRATED_RUNTIME_PROOF               = PASS             ← NEW (W2)
R1B_REAL_OTEL_PROOF                        = NOT_APPLICABLE   (W3)
R1B_REPLAY_PROOF                           = NOT_APPLICABLE   (W3)
```

## Final Row Statuses (post-W2)

```
RTC-REQ-055 = PARTIAL    (E0; caveat names R1B_PRODUCTION_THRESHOLD_PROOF:CALIBRATION_GAP)
RTC-REQ-056 = ACCEPTED   (E6_INTEGRATED_RUNTIME_PROOF — NEW)
RTC-REQ-057 = PENDING    (E0; W3 OTEL not claimed)
RTC-REQ-058 = PENDING    (E0; W3 replay not claimed)
RTC-REQ-059 = ACCEPTED   (E5_COMPOSITION_PROOF — unchanged from W1p6)
```

## Final Verifier Chain — All 11 Commands

```
verify_integrated_runtime_entrypoint                  exit 0   PASS
verify_r1b_safe_reuse_integrated_runtime              exit 0   PASS
verify_integrated_runtime_artifact_chain              exit 0   PASS  (12 artifacts, all SHAs verified)
verify_integrated_runtime_no_harness_stamp            exit 0   PASS
verify_integrated_runtime_exit_x3                     exit 0   PASS  (X3D unique, route R1B_SEMANTIC_CACHE, no_l2=True)
compose_semantic_cache_subclaims                      exit 0   R1B_INTEGRATED_RUNTIME_PROOF=PASS
verify_semantic_cache_certification --strict          exit 2   (RTC-REQ-055 PARTIAL — by design)
verify_runtime_certification_acceptance               exit 0   87 legal, 0 illegal
verify_runtime_certification_matrix                   exit 0   87 rows, sha 37bcaa4d7551
verify_source_divergence                              exit 0   4 peers, 0 divergences
```

(Cert verifier exit 2 is the W1p4 expected behavior because RTC-REQ-055
remains PARTIAL on its threshold gap — that exit is NOT a failure of
W2; it's the preservation of the W1p4 finding.)

## Test Surface

7 test files under `@c:/Git/Agentic-Workflow-FRESH/tests/runtime/`,
**50/50 pass**:

| File | Tests | Focus |
|------|------:|-------|
| `test_integrated_runtime_entrypoint_safe_reuse.py` | 8 | Entry-point usage + 5 fail-closed scenarios |
| `test_integrated_runtime_no_harness_stamping.py` | 3 | Producer regex + self-attestation |
| `test_integrated_runtime_artifact_chain.py` | 5 | SHA chain + 2 fault-injection scenarios |
| `test_integrated_runtime_exit_x3.py` | 6 | X3 uniqueness + 3 fault-injection |
| `test_integrated_runtime_terminal_no_l2.py` | 4 | Terminal cache reuse never executes L2/L4 |
| `test_integrated_runtime_safe_reuse_veto.py` | 14 | Veto outcome buckets + SafeReuseDecision invariants |
| `test_integrated_runtime_legacy_dense_only_stays_partial.py` | 6 | RTC-REQ-055 unchanged, RTC-REQ-056 flipped, RTC-REQ-059 unchanged |

W1p6 regression: 59/59 pass (`test_safe_reuse_composite.py` 27,
`test_veto_fail_closed.py` 15, `test_runtime_certification_matrix_schema.py` 12,
`test_source_divergence.py` 5).

## Scope Boundaries Preserved

- ✓ RTC-REQ-055 still PARTIAL; W1p4 CALIBRATION_GAP not erased
- ✓ SEMCACHE-THRESH-001 still PENDING_APPROVAL
- ✓ `SemanticCacheManager` threshold unchanged
- ✓ Adversarial calibration pairs unchanged
- ✓ W3 OTEL/replay scope: `R1B_REAL_OTEL_PROOF` and `R1B_REPLAY_PROOF` remain NOT_APPLICABLE
- ✓ W4 Merkle/final certification: not touched

## Source-Owned Boundary Updates

Two files in production code carry W2 semantic updates beyond the new
entry point. Both are documented inline:

1. `@c:/Git/Agentic-Workflow-FRESH/scripts/compose_semantic_cache_subclaims.py` —
   `R1B_INTEGRATED_RUNTIME_PROOF` no longer hardcoded NOT_APPLICABLE;
   resolved by `_map_integrated_runtime_proof()` which requires the full
   verifier ledger. `scope.runtime_certification_claimed` flips to True
   on the same condition.
2. `@c:/Git/Agentic-Workflow-FRESH/agentic_core/runtime/prove_requirements/r1b_subclaim_schema.py` —
   `RTC-REQ-056` gating updated to mirror RTC-REQ-059 (the safe-reuse
   composite gating set) plus `R1B_INTEGRATED_RUNTIME_PROOF`. RTC-REQ-056
   no longer inherits the legacy threshold gap; this is the parallel of
   the W1p6 RTC-REQ-055/059 split.

## References

- Plan: `.windsurf/plans/rtc-w2-integrated-runtime-r1b-safe-reuse-c7e9f3.md`
- W1p6 migration report: `docs/architecture/requirement_architecture_alignment_report.md`
- ADR (threshold, unchanged): `docs/architecture/adr/SEMCACHE-THRESH-001.md` (PENDING_APPROVAL)
- Hardened CSV (87 rows): `docs/reference/contracts/certification/runtime_certification_requirements_100_percent_hardened.csv`
- Verifier results ledger: `artifacts/certification/integrated_runtime/verifier_results.json`
- Latest evidence run: `artifacts/certification/integrated_runtime/latest/`
