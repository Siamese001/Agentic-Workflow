---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\rtc-w2b-live-provider-allow-proof-b24f8e.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\rtc-w2b-live-provider-allow-proof-b24f8e.md'
source_sha256: ef4bf9885e3f2729f55dde37e397f735d9ca0858d794a719a9ea6f49dc6dd8ff
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# RTC W2b — Live-Provider ALLOW-Path Proof for RTC-REQ-056

**Plan ID:** `rtc-w2b-live-provider-allow-proof-b24f8e`
**Date:** 2026-05-01
**Tier:** T3 (cross-layer — L2/L4 runtime + L5 safety + L6 cert-acceptance + CI + tests)
**Predecessor:** W2 (`rtc-w2-integrated-runtime-r1b-safe-reuse-c7e9f3`)
**Branch:** `rtc-w2-clean` (new work layered on top; `adg-hygiene-burndown` is unrelated)
**Author-Gate Decision required before execution begins.**

---

## Goal

Move `RTC-REQ-056` from **PENDING** (current honest committed state, `R1B_INTEGRATED_RUNTIME_ALLOW_PATH_PROOF = INFRASTRUCTURE_GAP`) to **ACCEPTED** using a **live approved SAFE-producing provider**. No use of `mock_safe`. No relaxation of the `LLMJudgeVeto` parsing / decision logic. No change to the rubric semantics.

---

## Non-Negotiables (encoded as CI gates + verifier rejections)

| Invariant | Enforcement tier |
|-----------|------------------|
| `mock_safe` remains test-only | Verifier reject + CI gate + rubric-hash mismatch check |
| `LLMJUDGEVETO_APPROVED_MOCK_SAFE` **never** in certification env | CI env-probe gate; hook-level audit |
| No W3 OTEL scope (RTC-REQ-057) | Plan scope wall; verifier unchanged for E7 |
| No W3 replay scope (RTC-REQ-058) | Plan scope wall; verifier unchanged for E8 |
| No W4 final certification / Merkle | Plan scope wall; `verify_all_requirements_merkle_root.py` unchanged |
| `RTC-REQ-055` stays `PARTIAL` | W1p4 CALIBRATION_GAP pinned; W2b must not touch threshold proof |
| `RTC-REQ-059` stays `ACCEPTED` | E5 composition proof untouched |
| `RTC-REQ-056` → `ACCEPTED` **only** with real provider attestation | Composer gate (§5 below) + verifier reject paths |

---

## Provider Order (explicit, SSOT)

1. **`local_qwen`** via vLLM OpenAI-compatible endpoint at `http://localhost:8000/v1` — **tried first**. Default local path; zero external dependency; fastest iteration loop.
2. **`anthropic_haiku`** via `ANTHROPIC_API_KEY` — **fallback**. Used only if `local_qwen` is unavailable OR fails the rubric-stability check (§P2 below).
3. **`mock_safe`** — **NEVER** in certification. Remains in code for unit tests only, gated on `LLMJUDGEVETO_APPROVED_MOCK_SAFE=1`. Committed CI does not set the flag.

Any provider not in `{local_qwen, anthropic_haiku}` → rejected for certification by composer + verifier.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W2b-A | P1 | Provider readiness + local_qwen endpoint probe | ~6000 | vLLM reachable at localhost:8000 OR ANTHROPIC_API_KEY present | Todo | Readiness artifact written; chosen provider recorded with availability status + failure reasons for unavailable candidates |
| W2b-B | P2 | Rubric stability check (3-run determinism against canonical safe-reuse pair) | ~8000 | Chosen provider from P1 is live | Todo | All 3 verdicts parse as SAFE with confidence ≥ 0.75; response-hash mode (exact vs. paraphrase-tolerant) decided |
| W2b-C | P3, P4 | Live ALLOW-path proof + attestation artifact | ~12000 | P2 passes | Todo | `c_primary_allow/` run uses real provider; `live_provider_attestation.json` written with all 8 required fields |
| W2b-D | P5, P6 | Composer + verifier gating updates | ~10000 | Attestation artifact shape finalized | Todo | `R1B_INTEGRATED_RUNTIME_ALLOW_PATH_PROOF = PASS` only under §5 conditions; verifier rejects all 7 forbidden cases |
| W2b-E | P7, P8 | Tests (8 canonical cases) + CI workflow hardening | ~10000 | §5-§6 locked | Todo | 8/8 test cases green; CI workflow refuses `mock_safe` paths; RTC-REQ-056 flips to ACCEPTED if P2-P4 succeed |
| W2b-F | P9 | Evidence regeneration + W2b report + commit | ~5000 | All prior waves green | Todo | Full verification chain re-run; `docs/architecture/integrated_runtime_w2b_report.md` written; commit + push |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| **P1** | Provider readiness probe | NEW `tools/certification/evidence/probe_live_provider_readiness.py`, NEW schema `artifacts/certification/integrated_runtime/live_provider_readiness.json` | local_qwen /v1/models shape varies; httpx timeout calibration; secret handling for ANTHROPIC_API_KEY; no key logging | ~6000 | Todo |
| **P2** | Rubric stability check (3-run) | NEW `tools/certification/evidence/probe_live_provider_rubric_stability.py`, NEW schema `artifacts/certification/integrated_runtime/rubric_stability_report.json` | LLM stochasticity (temp=0 helps but not guaranteed); paraphrase-tolerant vs exact hashing mode decision is security-sensitive; SAFE vs UNCERTAIN boundary | ~8000 | Todo |
| **P3** | Live ALLOW-path probe rewrite | MODIFY `tools/certification/evidence/probe_integrated_runtime_safe_reuse.py` (replace provider-ladder body: `local_qwen` → `anthropic_haiku` → FAIL; drop `mock_safe` branch entirely from certification path, keep it behind `LLMJUDGEVETO_APPROVED_MOCK_SAFE` for tests only) | Preserving triple-run shape; keeping c_primary_fail_closed + structural legs unchanged; path_proofs_ledger schema additive (no breaking change) | ~7000 | Todo |
| **P4** | Attestation artifact writer | NEW `tools/certification/evidence/_live_provider_attestation.py`, writes `artifacts/certification/integrated_runtime/c_primary_allow/live_provider_attestation.json` | `raw_response` storage vs hash-only (security rule §D below); rubric_hash reproducibility across runs; model_version normalization | ~5000 | Todo |
| **P5** | Composer gate update | MODIFY `scripts/compose_semantic_cache_subclaims.py` (add `_validate_live_provider_attestation()`; `R1B_INTEGRATED_RUNTIME_ALLOW_PATH_PROOF = PASS` requires all 7 conjunctive conditions from §5 below) | Soft-fail backwards compat for pre-W2b artifacts; INFRASTRUCTURE_GAP reason-code extensibility; composer hot path latency | ~4000 | Todo |
| **P6** | Verifier rejection paths | MODIFY `ops_scripts/ci/verify_r1b_safe_reuse_integrated_runtime.py`, MODIFY `ops_scripts/ci/verify_integrated_runtime_artifact_chain.py` | 7 rejection cases exhaustive; clear error messages; exit-code discipline (exit 2 = FAIL_CLOSED) | ~6000 | Todo |
| **P7** | Test matrix | NEW `tests/runtime/test_live_provider_readiness.py`, NEW `tests/runtime/test_live_provider_allow_proof.py`, NEW `tests/runtime/test_live_provider_attestation.py`, MODIFY `tests/runtime/test_integrated_runtime_legacy_dense_only_stays_partial.py` (extend `TestRTC056HonestInfrastructureGap` with ACCEPTED-path tests gated on live provider availability) | vLLM fixture (skip-if-not-available pattern); Anthropic fixture (skip-if-no-key); no hitting real LLM in unit tests except integration-marked | ~7000 | Todo |
| **P8** | CI workflow hardening | MODIFY `.github/workflows/runtime-certification.yml` (add manual-dispatch `live_provider_acceptance` job requiring `LOCAL_QWEN_ENDPOINT` OR `ANTHROPIC_API_KEY` secret; explicit env-probe rejecting `LLMJUDGEVETO_APPROVED_MOCK_SAFE`) | Secret scoping; matrix strategy for provider choice; fail-closed when neither secret is present | ~3000 | Todo |
| **P9** | Evidence regeneration + W2b report + commit | REGENERATE `artifacts/certification/*` via full verification chain, NEW `docs/architecture/integrated_runtime_w2b_report.md`, UPDATE `docs/architecture/integrated_runtime_w2_report.md` §Status block | Row-status delta depends on provider availability at commit time; report must be honest about PENDING vs ACCEPTED outcome | ~5000 | Todo |

---

## § 1 — Provider Readiness Probe (P1 contract)

**Script:** `tools/certification/evidence/probe_live_provider_readiness.py`

**Writes:** `artifacts/certification/integrated_runtime/live_provider_readiness.json`

**Schema:**
```json
{
  "schema_version": 1,
  "executed_at_utc": "2026-05-01T11:30:00Z",
  "candidates": [
    {
      "provider": "local_qwen",
      "order": 1,
      "available": true,
      "endpoint": "http://localhost:8000/v1",
      "model_id": "Qwen/Qwen2.5-7B-Instruct",
      "model_version": "<hash-or-tag-if-available>",
      "probe_latency_ms": 42,
      "probe_method": "GET /v1/models",
      "failure_reason": null
    },
    {
      "provider": "anthropic_haiku",
      "order": 2,
      "available": false,
      "endpoint": "https://api.anthropic.com",
      "model_id": "claude-haiku-4-5",
      "model_version": "claude-haiku-4-5",
      "probe_latency_ms": null,
      "probe_method": "env[ANTHROPIC_API_KEY] presence",
      "failure_reason": "ANTHROPIC_API_KEY not set in CERT env"
    }
  ],
  "chosen_provider": "local_qwen",
  "chosen_reason": "local_qwen available and ordered first",
  "unavailable_reasons": [
    "anthropic_haiku: ANTHROPIC_API_KEY not set in CERT env"
  ]
}
```

**Rules:**
- Probe **tries local_qwen first** (HTTP `GET /v1/models` with `timeout=5s`).
- If local_qwen unavailable → probe `anthropic_haiku` (env-var presence only; no API call).
- `chosen_provider` = first in order that is available. Never emits `chosen_provider = "mock_safe"`.
- No secret values logged or written to disk — key presence is a boolean.
- Exit 0 even when no provider is available (readiness probe is diagnostic, not a gate). Downstream composer/verifier treats unavailability as INFRASTRUCTURE_GAP.

---

## § 2 — Rubric Stability Check (P2 contract)

**Script:** `tools/certification/evidence/probe_live_provider_rubric_stability.py`

**Writes:** `artifacts/certification/integrated_runtime/rubric_stability_report.json`

**Procedure:**
- Reads canonical safe-reuse pair from the W1p6 test fixture set.
- Invokes `LLMJudgeVeto(provider=<chosen>)` **3 times** at temperature=0 (provider-specific).
- Each call: full rubric (`config/certification/llm_judge_rubric.md`).
- Records each verdict (SAFE/UNSAFE/UNCERTAIN/ERROR), confidence, latency, raw response sha256.

**PASS conditions:**
- All 3 runs return **SAFE** verdict.
- All 3 confidences ≥ **0.75**.
- All 3 runs complete within `LLM_JUDGE_TIMEOUT_MS` (policy-configured, currently 10000 ms).
- No parse failures.

**FAIL conditions** (any one → escalate to `anthropic_haiku` if first provider was `local_qwen`):
- Any run returns non-SAFE verdict.
- Any confidence below 0.75.
- Any timeout or parse failure.
- Verdicts disagree across runs.

**Hashing mode decision** (written to report):
- `response_hash_mode = "exact"` if all 3 raw responses hash identically (deterministic provider)
- `response_hash_mode = "paraphrase_tolerant"` if verdicts match but raw responses differ (canonical case for real LLMs) — recorded response hash is computed from the **parsed verdict object** `{verdict, confidence_bucket}` not raw text
- Security rule: `raw_response` stored only as sha256; plaintext retained ONLY when `W2B_STORE_RAW_PROVIDER_OUTPUT=1` set (off by default per §D security)

---

## § 3 — Attestation Artifact (P4 contract)

**Writes:** `artifacts/certification/integrated_runtime/c_primary_allow/live_provider_attestation.json`

**Schema:**
```json
{
  "schema_version": 1,
  "attestation_kind": "live_provider_allow_path",
  "provider": "local_qwen",
  "model_id": "Qwen/Qwen2.5-7B-Instruct",
  "model_version": "<hash-or-tag>",
  "rubric_path": "config/certification/llm_judge_rubric.md",
  "rubric_hash_sha256": "<sha256 of rubric file contents at probe time>",
  "response_hash_sha256": "<sha256 per response_hash_mode>",
  "response_hash_mode": "paraphrase_tolerant",
  "verdict": "SAFE",
  "confidence": 0.89,
  "latency_ms": 1342,
  "wall_clock_utc": "2026-05-01T11:35:07.482Z",
  "llm_judge_invocation_count": 1,
  "veto_stage_class": "LLMJudgeVeto",
  "deterministic_proof_stage_used": false,
  "x3_disposition": "X3D",
  "safe_reuse_allow": true,
  "mock_safe_used": false,
  "approved_provider": true,
  "env_probe": {
    "LLMJUDGEVETO_APPROVED_MOCK_SAFE": "unset",
    "LOCAL_QWEN_ENDPOINT": "http://localhost:8000/v1",
    "ANTHROPIC_API_KEY_present": false
  }
}
```

**Placement:** Next to the existing `c_primary_allow/` manifest + decorated telemetry payload.

---

## § 4 — Security Rules for Raw Provider Output

**§D.1** — Default: `raw_response` stored only as sha256 hash.
**§D.2** — Plaintext retention opt-in via `W2B_STORE_RAW_PROVIDER_OUTPUT=1`. Not set in committed CI. When set, raw output goes to `artifacts/certification/integrated_runtime/c_primary_allow/raw_provider_responses/<run_id>.json` — which is added to `.gitignore` and never committed.
**§D.3** — `ANTHROPIC_API_KEY` is **never** logged, echoed, or written to any artifact. Only its presence (boolean) is recorded.
**§D.4** — `local_qwen` endpoint URL IS recorded (public local address, not a secret). Remote vLLM deployments would require a separate secret-handling path — not in scope for W2b.
**§D.5** — Rubric hash recorded so any future rubric change invalidates past attestations (audit replayability).

---

## § 5 — Composer Gate Contract (P5)

`R1B_INTEGRATED_RUNTIME_ALLOW_PATH_PROOF = PASS` **if and only if** ALL of these hold (conjunctive, all-or-nothing):

1. `path_proofs_ledger.c_primary_allow.pass == True`
2. `live_provider_attestation.json` exists at the canonical path AND parses against schema v1
3. `attestation.provider in {"local_qwen", "anthropic_haiku"}`
4. `attestation.mock_safe_used == false`
5. `attestation.deterministic_proof_stage_used == false`
6. `attestation.veto_stage_class == "LLMJudgeVeto"`
7. `attestation.verdict == "SAFE"` AND `attestation.safe_reuse_allow == true` AND `attestation.x3_disposition == "X3D"`

Any single condition failing → `R1B_INTEGRATED_RUNTIME_ALLOW_PATH_PROOF = INFRASTRUCTURE_GAP` with reason-code identifying which condition failed.

---

## § 6 — Verifier Rejection Matrix (P6)

Updates to `ops_scripts/ci/verify_r1b_safe_reuse_integrated_runtime.py`. Each rejection exits 2 with a distinct reason code:

| # | Reject condition | Reason code |
|---|------------------|-------------|
| 1 | `attestation.provider == "mock_safe"` (even if env flag set) | `REJECT_MOCK_SAFE_IN_CERTIFICATION` |
| 2 | `live_provider_attestation.json` missing | `REJECT_MISSING_ATTESTATION` |
| 3 | `attestation.provider not in {"local_qwen","anthropic_haiku"}` | `REJECT_UNAPPROVED_PROVIDER` |
| 4 | Provider raw output fails `_parse_verdict` | `REJECT_UNPARSEABLE_PROVIDER_OUTPUT` |
| 5 | `verdict == "SAFE"` but `rubric_hash_sha256` missing | `REJECT_SAFE_WITHOUT_RUBRIC_HASH` |
| 6 | `verdict == "SAFE"` but `response_hash_sha256` missing | `REJECT_SAFE_WITHOUT_RESPONSE_HASH` |
| 7 | `verdict in {"UNKNOWN","ERROR","TIMEOUT"}` being treated as allow | `REJECT_NON_SAFE_AS_ALLOW` |
| 8 (composite) | Schema violation of attestation JSON | `REJECT_ATTESTATION_SCHEMA_INVALID` |

---

## § 7 — Test Matrix (P7, 8 canonical cases)

| # | Test | Precondition | Expected |
|---|------|--------------|----------|
| T1 | `test_local_qwen_available_path` | `LOCAL_QWEN_ENDPOINT` reachable OR fixture-mocked OpenAI-compat server | ALLOW path accepted, RTC-REQ-056 ACCEPTED |
| T2 | `test_anthropic_available_path` | `ANTHROPIC_API_KEY` set OR fixture-mocked Anthropic client | ALLOW path accepted, RTC-REQ-056 ACCEPTED |
| T3 | `test_no_provider_available` | Neither reachable | RTC-REQ-056 stays PENDING with INFRASTRUCTURE_GAP reason |
| T4 | `test_mock_safe_rejected_for_certification` | `LLMJUDGEVETO_APPROVED_MOCK_SAFE=1`, provider=mock_safe | Composer returns INFRASTRUCTURE_GAP; verifier exits 2 with `REJECT_MOCK_SAFE_IN_CERTIFICATION` |
| T5 | `test_malformed_provider_response_blocks` | Mock provider returns unparseable JSON | `REJECT_UNPARSEABLE_PROVIDER_OUTPUT`; RTC-REQ-056 stays PENDING |
| T6 | `test_unknown_error_timeout_blocks` | Mock provider returns UNCERTAIN / raises / times out | `REJECT_NON_SAFE_AS_ALLOW`; RTC-REQ-056 stays PENDING |
| T7 | `test_live_provider_safe_allow_accepted` | Mock provider returns canonical SAFE verdict with full attestation | RTC-REQ-056 ACCEPTED |
| T8 | `test_missing_attestation_rejected` | Probe skipped; composer sees `c_primary_allow.pass=True` but no attestation file | `REJECT_MISSING_ATTESTATION`; RTC-REQ-056 stays PENDING |

Tests use `pytest.mark.integration` for T1/T2 live-provider paths (skip-if-not-available). T3-T8 are pure unit tests with mock providers.

---

## § 8 — Final Expected Outcomes (P9)

### Scenario A: `local_qwen` at `localhost:8000` produces stable SAFE

Commit-time state:
- `path_proofs_ledger.c_primary_allow.pass == True`
- `live_provider_attestation.json` written with `provider=local_qwen`, `verdict=SAFE`, confidence ≥ 0.75
- `R1B_INTEGRATED_RUNTIME_ALLOW_PATH_PROOF = PASS`
- `R1B_INTEGRATED_RUNTIME_FAIL_CLOSED_PATH_PROOF = PASS` (unchanged from W2)
- `R1B_INTEGRATED_RUNTIME_PROOF = PASS`
- **`RTC-REQ-056 = ACCEPTED`** at E6_INTEGRATED_RUNTIME_PROOF
- Triple-run evidence ledger documents the live-provider allow-proof
- W2b report documents: provider=local_qwen, rubric_hash, response_hash_mode, stability check

### Scenario B: `local_qwen` unavailable, `anthropic_haiku` produces stable SAFE

Same as Scenario A with `provider=anthropic_haiku`, `model_id=claude-haiku-4-5`, plus record of `local_qwen` unavailability reason in readiness report.

### Scenario C: Neither provider available (or neither produces stable SAFE)

Commit-time state (honest non-green):
- `live_provider_readiness.json` records both unavailability reasons
- `live_provider_attestation.json` NOT written
- `R1B_INTEGRATED_RUNTIME_ALLOW_PATH_PROOF = INFRASTRUCTURE_GAP`
- `R1B_INTEGRATED_RUNTIME_PROOF = NOT_APPLICABLE`
- **`RTC-REQ-056 = PENDING`** (identical to current W2 committed state)
- W2b still commits the infrastructure changes (composer gate + verifier + tests + CI workflow); only the final row-status flip is blocked
- Branch remains honest non-green; `mock_safe` override remains forbidden

---

## § 9 — Row Status Matrix (unchanged except RTC-REQ-056)

| Row | W2 committed | W2b Scenario A/B | W2b Scenario C |
|-----|--------------|------------------|----------------|
| RTC-REQ-055 | PARTIAL | **PARTIAL** (untouched) | **PARTIAL** (untouched) |
| RTC-REQ-056 | PENDING | **ACCEPTED** | **PENDING** |
| RTC-REQ-057 | PENDING | PENDING (W3 scope) | PENDING (W3 scope) |
| RTC-REQ-058 | PENDING | PENDING (W3 scope) | PENDING (W3 scope) |
| RTC-REQ-059 | ACCEPTED | **ACCEPTED** (untouched) | **ACCEPTED** (untouched) |

---

## § 10 — ADG_GRAPH_LAYER_EVIDENCE (constitutional §22)

The refactoring touches runtime certification code which is ADG-tracked. Graph-layer primitives consulted:

### Materialized views (≥3 required)

1. **`mv_graph_reverse_dependency_hotspots`** — fan-in ranking on `tools/certification/safety/llm_judge_veto.py`, `tools/certification/evidence/probe_integrated_runtime_safe_reuse.py`, `scripts/compose_semantic_cache_subclaims.py` to confirm the W2b edits do not cross the central-dependency boundary.
2. **`mv_graph_chokepoint_bridges`** — verify `LLMJudgeVeto` remains a single chokepoint (no branch splits introduced by W2b); the mock_safe branch stays gated in one place.
3. **`mv_hotspot_centrality`** — rank of composer + verifier files; any W2b edit that raises centrality above the current band must be called out for Author-Gate review.
4. **`mv_dependency_cone_risk`** — impact radius of probe/composer/verifier changes on downstream consumers (cert-decision evaluator, matrix verifier, source-divergence verifier).

### Semantic edges

- `flows_to`: live_provider_attestation.json → composer → R1B subclaims → RTC-REQ-056 acceptance gate
- `writes_to`: probe_live_provider_readiness.py → readiness artifact; probe_integrated_runtime_safe_reuse.py → attestation artifact
- `reads_from`: composer → attestation artifact; verifier → attestation artifact; CI workflow → readiness artifact
- `emits_side_effect`: HTTP GET to `localhost:8000/v1/models` (local_qwen probe); HTTP POST to Anthropic (attestation run when provider=anthropic_haiku)
- `controls_flow`: 7-condition conjunctive gate in composer (§5); 7 reject paths in verifier (§6)
- `resolves_callsite`: `LLMJudgeVeto.evaluate()` at the provider-call site in the integrated-runtime entrypoint

### Pre-built P-views

- **`v_p0_write_bypass_uwg`** — confirm W2b does not write certification artifacts bypassing UWG. Probe artifact writes are evidence emission, not state mutation, so they are out of UWG scope but still require explicit notation in the plan.
- **`v_p1_mis_layered_infra`** — confirm the new `_live_provider_attestation.py` helper does not import from an upper layer.
- **`v_p3_isolated_experimental`** — confirm W2b does not introduce orphan experimental code; all new files have at least one consumer.

---

## § 11 — ADG_HOTSPOT_REPORT

All hotspots listed below cross ADG Surfaces (Execution / Write / Security / State / Observability). Impact formula: `violations × (1 + log10(1 + fan_in)) × layer_multiplier`.

| Rank | File | Layer (mult) | Fan-in | Archetype | Surface(s) | Impact | W2b disposition |
|------|------|:---:|:---:|---|---|:---:|---|
| 1 | `tools/certification/safety/llm_judge_veto.py` | L5 (×2.0) | 14 | SAFETY_GATEKEEPER | Execution, Security | High | Surface audit required; mock_safe branch stays gated, no new branches. Gold-star Author-Gate before P3 edit. |
| 2 | `scripts/compose_semantic_cache_subclaims.py` | L6 (×0.75) | 9 | ORCHESTRATOR | Write, Observability | Medium-High | 7-condition gate added; unit tests cover all 8 rejection paths. |
| 3 | `ops_scripts/ci/verify_r1b_safe_reuse_integrated_runtime.py` | L6 (×0.75) | 6 | SAFETY_GATEKEEPER | Security, Observability | Medium | 7 reject paths with distinct reason codes; no branch falls through to accept without attestation. |
| 4 | `tools/certification/evidence/probe_integrated_runtime_safe_reuse.py` | L6 (×0.75) | 3 | STATE_NODE (writes cert evidence) | Write | Medium | Provider ladder rewrite; `mock_safe` removed from certification path entirely. |
| 5 | `tests/runtime/test_integrated_runtime_legacy_dense_only_stays_partial.py` | L6 (×0.75) | 0 | (test) | Observability | Low | Extend `TestRTC056HonestInfrastructureGap` with ACCEPTED-path tests gated on live provider. |

**Zero-Loss Propagation Pipeline verification:**
- Catch site: `LLMJudgeVeto.evaluate()` provider branch
- Antipattern edge: none introduced (no new broad-catch, no new swallow)
- Ownership bridge: `agentic_core/runtime/entrypoints/integrated_safe_reuse_run.py` → `Module:L2_execution` (existing ownership, unchanged)
- Surface intersection: Execution ∩ Security (LLMJudgeVeto is a safety gatekeeper)
- Layer multiplier: ×2.0 (L5)
- Hotspot classification: SAFETY_GATEKEEPER (correctly ranked #1)

---

## § 12 — Author-Gate Decision Required Before Execution

This plan enters `architecture_choice` / `test_strategy` / `error_handling` triggers. The Author-Gate packet must surface:

- **⭐ Recommended**: Provider-ladder implementation with `local_qwen` first, graceful fallback to `anthropic_haiku`, no mock_safe in certification path
- **Alternative**: Anthropic-first (rejected: introduces external API dependency as default)
- **Alternative**: Composite multi-provider attestation (rejected: scope creep beyond W2b goal)

Packet must include:
- Precedent from `artifacts/windsurf/author_gate_precedent.json` (W1p5 + W2 set the pattern)
- `DECISION_CAPTURED:` marker emitted on resolution
- `ROUTER_DECISION:` markers emitted per constitutional §29 for each `LLMJudgeVeto.evaluate()` call in the P3 rewrite

---

## § 13 — Deferred Scope (out of W2b)

Items explicitly deferred to future waves (each will emit a `DEFERRED_SCOPE:` marker when W2b executes):

- **W3** — RTC-REQ-057 (OTEL export) and RTC-REQ-058 (replay determinism)
- **W4** — Final certification / Merkle root
- **W2c** (potential) — Multi-provider consensus attestation (2-of-3 SAFE agreement across local_qwen + anthropic_haiku + a third approved provider)
- **W2d** (potential) — Remote vLLM endpoint handling (authenticated, TLS-terminated)
- **Rubric v2** — If rubric stability check reveals ambiguity on the canonical safe-reuse pair, a rubric refresh plan (tracked separately, blocks W2b from Scenario A/B entry)

---

## § 14 — Commit Discipline

- Single-feature branch: `rtc-w2b-live-provider-allow-proof-b24f8e` (new local branch, layered on top of `rtc-w2-clean`).
- Atomic commits per phase (P1…P9) with honest commit messages.
- `DECISION_CAPTURED:` marker on any Author-Gate resolution during execution.
- `ROUTER_DECISION:` markers for every live `LLMJudgeVeto.evaluate()` invocation in the acceptance run.
- Final push only after §8 Scenario A, B, or C is explicitly confirmed with fresh evidence regenerated on the clean branch.
- No force-push, no rebase that would rewrite the pushed `rtc-w2-clean` history.

---

## § 15 — Success Metric

**W2b succeeds** iff one of:

- Scenario A: `local_qwen` yields stable SAFE → RTC-REQ-056 ACCEPTED with `provider=local_qwen` attestation
- Scenario B: `anthropic_haiku` yields stable SAFE → RTC-REQ-056 ACCEPTED with `provider=anthropic_haiku` attestation
- Scenario C: both fail → RTC-REQ-056 stays PENDING, but the W2b infrastructure lands so any future live-provider availability automatically flips the row

In no case does W2b weaken the fail-closed path, relax the rubric, or permit `mock_safe` in a certification claim.

---

## Status

**Todo — awaiting Author-Gate review before execution.**

Execution blocked until:
1. Plan approved for scaffolding into executable phases
2. Provider order explicitly confirmed (`local_qwen` first, `anthropic_haiku` second) — DONE per user directive 2026-05-01
3. Non-negotiables explicitly confirmed — DONE per user directive 2026-05-01
4. Author-Gate surfaced with options packet per `.windsurf/rules/author-gate-enforcement.md`
