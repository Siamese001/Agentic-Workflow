---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\rtc-w2-integrated-runtime-r1b-safe-reuse-c7e9f3.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\rtc-w2-integrated-runtime-r1b-safe-reuse-c7e9f3.md'
source_sha256: 91237e6a1daf8b5574eec1d79074d440749f65ef16346e4820c333b1637e564e
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# RTC W2 — Integrated Runtime Entry Point for RTC-REQ-059 Safe-Reuse Composite

> Status: **DRAFT — awaiting Author-Gate approval**
> Tier: **T3** (cross-layer, multi-file, new production entry point)
> Predecessors: W1p5 (Author-Gate APPROVED), W1p6 (RTC-REQ-059 ACCEPTED)
> Non-goals: W3 (OTEL/replay), W4 (Merkle/final cert), SEMCACHE-THRESH-001 recalibration,
> removal of adversarial calibration pairs, change to `SemanticCacheManager` threshold.

---

## SR_INTAKE

Prove the accepted RTC-REQ-059 safe-reuse composite path **through a single
production integrated-runtime entry point** that emits the full artifact
chain: `ValidatedRequest → L1PlanContract → RouteContract →
RuntimeGateVerdictBundle → SafeReuseDecision → TerminalRetPacket →
ExitReviewPacket → X3Disposition → RuntimeExhaustBundle`. No harness may
call any layer directly. Veto must be invoked inside the production path,
not stamped by a test.

Success condition: `R1B_INTEGRATED_RUNTIME_PROOF = PASS`; RTC-REQ-056
flips from `PENDING` → `ACCEPTED` at `E6_INTEGRATED_RUNTIME_PROOF`;
RTC-REQ-055 stays `PARTIAL`; RTC-REQ-059 stays `ACCEPTED` at E5.

Fact grading:
- **DIRECTLY OBSERVED**: `TerminalRetPacket`, `ExitReviewPacket`,
  `ExitEvalPipeline`, `run_request_intake`,
  `validated_request_to_plan_contract`, `check_d2_semantic_cache`,
  `SemanticCacheManager.recall` all exist and are callable.
- **DIRECTLY OBSERVED**: There is no existing `RuntimeGateVerdictBundle`
  contract — it must be created.
- **DIRECTLY OBSERVED**: `check_d2_semantic_cache` does **not** currently
  invoke the safety veto. The integrated entry point must wire the veto
  between the D2 hit and the reuse admission.
- **DERIVED**: `X3Disposition` (user's requirement-language) maps onto
  either `V6Disposition` in `agentic_core/L3_orchestration/exit_eval/v6/types.py`
  or `X3Disposition` in `system_learning/engines/exit_v6_engines.py`. The
  v6 pipeline emits `V6Disposition`; we'll standardize on that and expose
  a neutral JSON field `x3_disposition` in the artifact.
- **DERIVED**: `RuntimeExhaustBundle` (user's requirement-language) maps
  onto `RuntimeExhaustManifest` produced by `seal_runtime_exhaust`. The
  artifact filename will be `runtime_exhaust_bundle.json` and will carry
  the sealed manifest plus the bundle-level aggregation.
- **UNRESOLVED**: Whether RTC-REQ-056 should be flipped to ACCEPTED in
  this wave or remain PENDING until W3 adds OTEL. User said "RTC-REQ-056
  may become ACCEPTED only if the integrated runtime proof is real and
  complete". Plan proposes flipping on proof completeness; gate via
  acceptance-verifier output (no hand-edit).

## SR_PLAN

### Production entry point

**New**: `agentic_core/runtime/entrypoints/integrated_safe_reuse_run.py`

Exports `run_integrated_safe_reuse(raw_request, *, namespace, tenant_id,
artifact_dir=None) -> IntegratedRunResult`.

Implementation chain (no harness reach-through):

```
  raw_request
    │
    ▼
  (1) run_request_intake(raw_envelope)           ─→ ValidatedRequest
    │                                               artifact: validated_request.json
    ▼
  (2) validated_request_to_plan_contract(vr)     ─→ L1PlanContract
    │                                               artifact: l1_plan_contract.json
    ▼
  (3) _build_route_contract(plan, vr)            ─→ RouteContract (L0RouteContract dict)
    │                                               artifact: route_contract.json
    ▼
  (4) _evaluate_runtime_gates(request, ...)      ─→ RuntimeGateVerdictBundle (new)
    │    delegates to check_route_gates + veto       artifact: runtime_gate_verdict_bundle.json
    │
    ├─ on D1 hit: short-circuit as R1A (out of scope for R1B proof — still valid)
    ├─ on D2 hit: invoke SafetyVetoOrchestrator.evaluate(candidate_pair)
    │      ├─ veto BLOCK → produce SafeReuseDecision(allow=False, reason_code=VETOED)
    │      │              → route through Exit with terminal class "veto_blocked"
    │      └─ veto ALLOW → produce SafeReuseDecision(allow=True, reason_code=SAFE_REUSE)
    │                     → build TerminalRetPacket(route_id="R1B_SEMANTIC_CACHE")
    └─ on miss: out-of-scope for R1B proof (returns None from safe-reuse path)
    │                                               artifact: semantic_cache_safe_reuse_decision.json
    ▼
  (5) _emit_terminal_ret_packet(...)             ─→ TerminalRetPacket
    │                                               artifact: terminal_ret_packet.json
    ▼
  (6) ExitEvalPipeline.run(receipts_dict)        ─→ ExitEvalResult
    │   receipts assembled from above artifacts     artifacts:
    │                                                 exit_review_packet.json
    │                                                 x3_disposition_receipt.json
    ▼
  (7) seal_runtime_exhaust + RuntimeExhaustCollector.collect
                                                  ─→ RuntimeExhaustManifest + Bundle
                                                     artifact: runtime_exhaust_bundle.json
    ▼
  (8) emit integrated_runtime_artifact_manifest.json (links all 11 artifacts + chain sha256)
  (9) emit integrated_runtime_entrypoint_invocation.json (stamps entry-point provenance)
 (10) emit no_harness_stamp_receipt.json          (asserts producer_component != "harness"
                                                   for every artifact; cross-check)
```

**New contract module**: `agentic_core/runtime/contracts/runtime_gate_verdict_bundle.py`

```python
@dataclass(frozen=True)
class RuntimeGateVerdictBundle:
    d1_verdict: GateVerdict    # HIT | MISS | SKIPPED
    d2_verdict: GateVerdict    # HIT | MISS | SKIPPED
    veto_verdict: VetoVerdict  # ALLOWED | BLOCKED | FAIL_CLOSED_* | SKIPPED
    d2_similarity: float       # 0.0 if not evaluated
    veto_primary_mode: str     # "C_PRIMARY_LLM_JUDGE" when veto ran
    llm_judge_invocation_count: int
    reason_codes: tuple[str, ...]
    producer_component: str    # "agentic_core.runtime.entrypoints.integrated_safe_reuse_run"
```

**New contract module**: `agentic_core/runtime/contracts/safe_reuse_decision.py`

```python
@dataclass(frozen=True)
class SafeReuseDecision:
    allow: bool
    reason_code: str              # SAFE_REUSE | VETOED | FAIL_CLOSED | NOT_APPLICABLE
    dense_candidate_produced: bool
    veto_invoked: bool
    veto_verdict: str             # ALLOWED | BLOCKED | UNKNOWN | ERROR | TIMEOUT | PARSE_FAIL
    unsafe_reuse_allowed_count: int          # 0 or 1 — this decision
    safe_reuse_blocked_count: int            # 0 or 1
    hard_negative_allowed_count: int          # 0 or 1 (only if the candidate was a hard negative)
    unknown_error_timeout_parse_fail_block_count: int   # 0 or 1
    evidence_refs: tuple[str, ...]
    producer_component: str
```

### Artifact provenance envelope

Every artifact is produced by a **single helper** that stamps:

```json
{
  "producer_component":        "agentic_core.runtime.entrypoints.integrated_safe_reuse_run",
  "producer_module":           "integrated_safe_reuse_run",
  "producer_function_or_class":"run_integrated_safe_reuse",
  "emitted_at":                "<UTC ISO8601>",
  "artifact_hash":             "sha256 of canonical JSON of payload",
  "upstream_artifact_ref":     "sha256 of upstream artifact, or null for validated_request.json",
  "payload": { ... }
}
```

A harness-stamping check in `scripts/verify_integrated_runtime_no_harness_stamp.py`
fails if `producer_component` matches `^tests\.|^scripts\.verify_|harness$`.

### Metric cleanup (user §Metric cleanup required)

Add explicit safety-metric aliases in both:
1. `threshold_sweep_results_with_veto.json` → per-row safety aliases
2. `semantic_cache_safe_reuse_decision.json` → per-decision aliases

Aliases required (both sources):
- `unsafe_reuse_allowed_count`
- `safe_reuse_blocked_count`
- `hard_negative_allowed_count`
- `unknown_error_timeout_parse_fail_block_count`

Existing ambiguous fields (`FP`, `FN`, `unsafe_fp_count`) are retained for
back-compat but the tests and verifiers consume only the new aliases.

### Files to create

| Path | Purpose |
|---|---|
| `@c:/Git/Agentic-Workflow-FRESH/agentic_core/runtime/entrypoints/__init__.py` | package marker |
| `@c:/Git/Agentic-Workflow-FRESH/agentic_core/runtime/entrypoints/integrated_safe_reuse_run.py` | production entry point |
| `@c:/Git/Agentic-Workflow-FRESH/agentic_core/runtime/contracts/runtime_gate_verdict_bundle.py` | new contract |
| `@c:/Git/Agentic-Workflow-FRESH/agentic_core/runtime/contracts/safe_reuse_decision.py` | new contract |
| `@c:/Git/Agentic-Workflow-FRESH/agentic_core/runtime/artifacts/integrated_runtime_emitter.py` | stamping helper |
| `@c:/Git/Agentic-Workflow-FRESH/scripts/verify_integrated_runtime_entrypoint.py` | verifier §1 |
| `@c:/Git/Agentic-Workflow-FRESH/scripts/verify_r1b_safe_reuse_integrated_runtime.py` | verifier §2 |
| `@c:/Git/Agentic-Workflow-FRESH/scripts/verify_integrated_runtime_artifact_chain.py` | verifier §3 |
| `@c:/Git/Agentic-Workflow-FRESH/scripts/verify_integrated_runtime_no_harness_stamp.py` | verifier §4 |
| `@c:/Git/Agentic-Workflow-FRESH/scripts/verify_integrated_runtime_exit_x3.py` | verifier §5 |
| `@c:/Git/Agentic-Workflow-FRESH/tools/certification/evidence/probe_integrated_runtime_safe_reuse.py` | drives the real entry point; writes 12 artifacts |
| `@c:/Git/Agentic-Workflow-FRESH/tests/runtime/test_integrated_runtime_entrypoint_safe_reuse.py` | positive path |
| `@c:/Git/Agentic-Workflow-FRESH/tests/runtime/test_integrated_runtime_no_harness_stamping.py` | forbids harness producers |
| `@c:/Git/Agentic-Workflow-FRESH/tests/runtime/test_integrated_runtime_artifact_chain.py` | sha lineage |
| `@c:/Git/Agentic-Workflow-FRESH/tests/runtime/test_integrated_runtime_exit_x3.py` | X3 uniqueness |
| `@c:/Git/Agentic-Workflow-FRESH/tests/runtime/test_integrated_runtime_terminal_no_l2.py` | L2 not invoked on terminal cache |
| `@c:/Git/Agentic-Workflow-FRESH/tests/runtime/test_integrated_runtime_safe_reuse_veto.py` | veto invoked on every D2 hit |
| `@c:/Git/Agentic-Workflow-FRESH/tests/runtime/test_integrated_runtime_legacy_dense_only_stays_partial.py` | RTC-REQ-055 unchanged |
| `@c:/Git/Agentic-Workflow-FRESH/docs/architecture/integrated_runtime_w2_report.md` | W2 evidence report |

### Files to modify

| Path | Change |
|---|---|
| `@c:/Git/Agentic-Workflow-FRESH/scripts/compose_semantic_cache_subclaims.py` | Add evidence loader for `integrated_runtime_artifact_manifest.json`; map to `R1B_INTEGRATED_RUNTIME_PROOF = PASS` when manifest present + chain-valid + all 12 artifacts hash-verified. Remove the hardcoded `NOT_APPLICABLE` for this subclaim, replace with scope-gated logic. |
| `@c:/Git/Agentic-Workflow-FRESH/agentic_core/runtime/prove_requirements/r1b_subclaim_schema.py` | RTC-REQ-056 gating: add `R1B_INTEGRATED_RUNTIME_PROOF` (already there). No structural change needed. |
| `@c:/Git/Agentic-Workflow-FRESH/tools/certification/evidence/probe_threshold_sweep_with_veto.py` | Emit the 4 new safety-metric alias fields alongside existing `unsafe_fp_count` etc. |

### Files explicitly NOT modified

- `@c:/Git/Agentic-Workflow-FRESH/agentic_core/L4_state/utils/memory/semantic_cache_manager.py` — zero change
- `@c:/Git/Agentic-Workflow-FRESH/docs/architecture/adr/SEMCACHE-THRESH-001.md` — stays PENDING_APPROVAL
- The RTC-REQ-055 CSV row — unchanged
- The adversarial calibration dataset — unchanged
- Any SEMANTIC_CACHE env var or default threshold — unchanged

### Verifier scripts (all exit-2 on fail)

1. `scripts/verify_integrated_runtime_entrypoint.py` — asserts
   `integrated_runtime_entrypoint_used = true` + manifest has exactly the 12
   required artifact filenames + the entry-point stamp matches
   `agentic_core.runtime.entrypoints.integrated_safe_reuse_run`.
2. `scripts/verify_r1b_safe_reuse_integrated_runtime.py` — asserts the
   SafeReuseDecision was produced in the real path: dense candidate TRUE,
   veto invoked TRUE, allow aligned with veto verdict, and all 4 alias
   counters present.
3. `scripts/verify_integrated_runtime_artifact_chain.py` — asserts every
   artifact's `upstream_artifact_ref` matches `sha256(upstream.payload)`;
   chain is unbroken from `validated_request.json` through
   `runtime_exhaust_bundle.json`.
4. `scripts/verify_integrated_runtime_no_harness_stamp.py` — asserts no
   artifact's `producer_component` matches harness regex.
5. `scripts/verify_integrated_runtime_exit_x3.py` — asserts exactly one
   `x3_disposition_receipt.json` exists and its disposition maps to one
   of the V6 enum values; `exit_review_packet.json` consumes the same
   `terminal_ret_packet.json` (sha match).

### Tests — positive (7 files as specified)

Each file targets one structural invariant and runs the real probe to
generate evidence the first time, then asserts artifact content.

### Tests — fail-closed (14 scenarios in shared parametrized suite)

Grouped inside `test_integrated_runtime_entrypoint_safe_reuse.py` and
`test_integrated_runtime_safe_reuse_veto.py`:

1. harness calls `check_d2_semantic_cache` directly → expected `FAIL:
   DIRECT_LAYER_ACCESS`
2. missing `validated_request.json` → verifier emits
   `ARTIFACT_CHAIN_BROKEN`
3. missing `l1_plan_contract.json` → same
4. missing `route_contract.json` → same
5. missing `runtime_gate_verdict_bundle.json` → same
6. missing `semantic_cache_safe_reuse_decision.json` → same
7. missing `terminal_ret_packet.json` → same
8. missing `exit_review_packet.json` → same
9. missing `x3_disposition_receipt.json` → same
10. multiple X3 receipts present → `X3_DISPOSITION_NOT_UNIQUE`
11. terminal_ret_packet claims `no_l2_execution_assertion=False` →
    `TERMINAL_L2_EXECUTION_FORBIDDEN`
12. any artifact's `producer_component` starts with `tests.` →
    `HARNESS_STAMPING_DETECTED`
13. upstream_artifact_ref sha mismatch → `CHAIN_SHA_DIVERGENCE`
14. veto returns UNKNOWN/ERROR/TIMEOUT/PARSE_FAIL but SafeReuseDecision
    shows `allow=True` → `UNSAFE_FAIL_CLOSED_BYPASS`

Each failure scenario is implemented by mutating the artifact set in a
temp dir, re-running the matching verifier, and asserting exit code 2.

### Artifact set (exactly 12)

1. `integrated_runtime_entrypoint_invocation.json`
2. `validated_request.json`
3. `l1_plan_contract.json`
4. `route_contract.json`
5. `runtime_gate_verdict_bundle.json`
6. `semantic_cache_safe_reuse_decision.json`
7. `terminal_ret_packet.json`
8. `exit_review_packet.json`
9. `x3_disposition_receipt.json`
10. `runtime_exhaust_bundle.json`
11. `integrated_runtime_artifact_manifest.json`
12. `no_harness_stamp_receipt.json`

All land in `artifacts/certification/integrated_runtime/<run_id>/`.
Canonical "last-run" symlink: `artifacts/certification/integrated_runtime/latest/`.

### Expected final command sequence + outcomes

```
1. python tools/certification/evidence/probe_integrated_runtime_safe_reuse.py
   → exit 0, writes 12 artifacts into artifacts/certification/integrated_runtime/latest/

2. python scripts/verify_integrated_runtime_entrypoint.py
   → exit 0 (manifest + entrypoint stamp valid)

3. python scripts/verify_r1b_safe_reuse_integrated_runtime.py
   → exit 0 (safe-reuse decision emitted, veto invoked, counters aligned)

4. python scripts/verify_integrated_runtime_artifact_chain.py
   → exit 0 (upstream chain SHA-verified end-to-end)

5. python scripts/verify_integrated_runtime_no_harness_stamp.py
   → exit 0 (no artifact stamped by harness)

6. python scripts/verify_integrated_runtime_exit_x3.py
   → exit 0 (exactly one X3 receipt)

7. python scripts/compose_semantic_cache_subclaims.py
   → exit 0; subclaim R1B_INTEGRATED_RUNTIME_PROOF = PASS (first time it's
     not NOT_APPLICABLE)

8. python scripts/verify_semantic_cache_certification.py --strict
   → exit 1 (RTC-REQ-055 still PARTIAL — threshold CALIBRATION_GAP pinned)

9. python scripts/verify_runtime_certification_acceptance.py
   → exit 0 (87 legal, 0 illegal; RTC-REQ-056 flips to ACCEPTED at E6)

10. python scripts/verify_runtime_certification_matrix.py
    → exit 0 (87 rows)

11. python scripts/verify_source_divergence.py
    → exit 0 (peers aligned)
```

Expected final row statuses:

| Row | Before W2 | After W2 | Proof Depth |
|---|---|---|---|
| RTC-REQ-055 | PARTIAL | **PARTIAL (unchanged)** | E0 (threshold CALIBRATION_GAP) |
| RTC-REQ-056 | PENDING | **ACCEPTED** | E6_INTEGRATED_RUNTIME_PROOF |
| RTC-REQ-057 | PENDING | PENDING | E0 (W3 OTEL not claimed) |
| RTC-REQ-058 | PENDING | PENDING | E0 (W3 replay not claimed) |
| RTC-REQ-059 | ACCEPTED | **ACCEPTED (unchanged)** | E5 |

Expected subclaims:

| Subclaim | W2 target |
|---|---|
| `R1B_INTEGRATED_RUNTIME_PROOF` | **PASS** (new) |
| `R1B_PRODUCTION_THRESHOLD_PROOF` | **CALIBRATION_GAP (unchanged)** |
| `R1B_SAFE_REUSE_COMPOSITE_PROOF` | **PASS (unchanged)** |
| `R1B_SEMANTIC_CACHE_SAFETY_VETO_PROOF` | **PASS (unchanged)** |
| `R1B_REAL_OTEL_PROOF` | NOT_APPLICABLE (W3) |
| `R1B_REPLAY_PROOF` | NOT_APPLICABLE (W3) |

### Author-Gate trigger points during W2

Three decisions I've pre-resolved with conservative single-path choices
(no Author-Gate required):

- **Scope of veto invocation**: invoked inside the integrated entry
  point only, not inside `check_d2_semantic_cache`. This keeps the
  existing production cache path unchanged for all non-W2 callers.
  One correct path.
- **`RuntimeExhaustBundle` vs `RuntimeExhaustManifest`**: we use the
  v6 pipeline's sealed manifest as the payload of `runtime_exhaust_bundle.json`;
  optionally aggregate via `RuntimeExhaustCollector`. One correct path.
- **`X3Disposition` label source**: use `V6Disposition.value`. The
  `system_learning/engines/exit_v6_engines.py` `X3Disposition` enum is a
  KPI-board label, not the runtime disposition — it's a reporting
  shadow. The runtime path produces `V6Disposition`. One correct path.

Author-Gate **will** fire if during execution any of these emerge:
- Evidence that `check_d2_semantic_cache` MUST be modified (would
  expand blast radius beyond W2).
- Evidence that ExitEvalPipeline cannot accept the receipts dict we
  build without a fallback (may require Author-Gate on receipt-shape
  decision).
- Evidence of any path where the veto can be bypassed without a
  fail-closed counter (would require a safety-model Author-Gate).

### Ambiguities / source-owned boundary issues

1. **RTC-REQ-056 flipping to ACCEPTED**: this requires the composer to
   stop hard-coding `R1B_INTEGRATED_RUNTIME_PROOF = NOT_APPLICABLE`.
   Currently the composer explicitly returns `NOT_APPLICABLE` with notes
   "W2 scope". The W2 plan is to make that conditional on presence of
   a validated `integrated_runtime_artifact_manifest.json`. This is a
   **source-of-truth change** inside the composer, not inside the CSV
   or the evidence probes. Plan records this change explicitly.
2. **Scope flag**: `scope.runtime_certification_claimed` is currently
   hardcoded to `False`. In W2 we flip it to `True` when the manifest is
   valid. The composer update handles this automatically.
3. **`L1PlanContract` field shape**: The bridge does a 1:1 deterministic
   mapping. The artifact serialization uses `dataclasses.asdict()` so any
   future field addition flows through without code change.
4. **Run-directory rotation**: artifacts are per-run but tests consume
   `latest/`. If two probes run concurrently, `latest/` has a race. W2
   accepts that — runs are sequential in CI. W3/W4 may formalize.
5. **SemanticCacheManager singleton reuse across probe runs**: the
   singleton is process-scoped; fine for W2's single-process probe.
6. **Veto fixtures**: the probe uses the same adversarial + safe test
   pairs from the W1p5 dataset to drive D2 hits. A non-calibration pair
   is used to drive the ACCEPTED safe-reuse path.

### ADG_HOTSPOT_REPORT (additive wave — no refactoring)

This wave is purely additive. No existing files are deleted, consolidated,
or re-layered. The 4 files modified are low-fan-in configuration surfaces
(composer, schema, probe). Per §22 the report section is included for
completeness:

| Target file | Archetype | Layer | Fan-in (ADG) | Surface | Rationale |
|---|---|---|---:|---|---|
| `agentic_core/runtime/entrypoints/integrated_safe_reuse_run.py` (new) | ORCHESTRATOR | L-runtime (cross-layer) | 0 initially (grows as apps adopt) | Execution + Write | New orchestrator; owns the safe-reuse flow. L×1.75 multiplier. |
| `scripts/compose_semantic_cache_subclaims.py` (modify) | CENTRAL_DEPENDENCY | L6_observability | high (all verifiers depend) | Observability | Change scoped to mapping `R1B_INTEGRATED_RUNTIME_PROOF` verdict; no structural edit. L×0.75 multiplier. |

### ADG_GRAPH_LAYER_EVIDENCE (additive wave)

- `mv_graph_reverse_dependency_hotspots`: new entry point has zero fan-in
  at first commit — expected. No hotspot perturbation.
- `mv_graph_chokepoint_bridges`: the new entry point creates a **new
  chokepoint** that aggregates `intake → L1-bridge → L0-gates → L3-exit`.
  This is intentional — a chokepoint is the correct shape for a
  certification entry point.
- `mv_graph_critical_path_blast_radius`: composer modification has
  medium-high fan-in. Edit is scoped to one verdict-mapping function
  (additive, not mutating).
- Semantic edges: the new module will emit `resolves_callsite` edges to
  `run_request_intake`, `validated_request_to_plan_contract`,
  `check_route_gates`, `ExitEvalPipeline.run`. No new `writes_to` /
  `emits_side_effect` beyond the filesystem artifact emitter.
- P-views: no RTC-REQ row moves between `v_p0_*` / `v_p1_*` classes. The
  new row (RTC-REQ-059) was already added in W1p6 with the correct
  claim type.

## SR_APPROVAL

**Awaiting user go-ahead before SR_EXECUTE.** Per the "Required first
response: Produce a W2 implementation plan before edits" clause, this
plan is the first-response artifact.

## SR_EXECUTE (deferred until approval)

Implementation order once approved:

1. Contracts: `runtime_gate_verdict_bundle.py`, `safe_reuse_decision.py`
2. Artifact emitter: `integrated_runtime_emitter.py`
3. Production entry point: `integrated_safe_reuse_run.py`
4. Probe: `probe_integrated_runtime_safe_reuse.py` (drives entry point
   end-to-end, writes all 12 artifacts)
5. Verifiers (5 scripts)
6. Update composer to map `R1B_INTEGRATED_RUNTIME_PROOF` from manifest
7. Tests (7 positive + 14 fail-closed)
8. Report: `docs/architecture/integrated_runtime_w2_report.md`
9. Run the 11-command final sequence and record outputs in the report

## SR_VERIFY (deferred)

On completion, a final response will report:
- All 11 commands exit codes
- Final subclaim + row statuses (deltas vs W1p6 baseline)
- Artifact chain SHA verification result
- Evidence that RTC-REQ-055 is unchanged and SEMCACHE-THRESH-001 remains PENDING_APPROVAL
