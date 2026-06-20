# Integrated-Runtime W2b Report — Live-Provider ALLOW-Path Proof

**Plan:** `.codex/plans/rtc-w2b-live-provider-allow-proof-b24f8e.md`
**Branch:** `rtc-w2b-live-provider-allow-proof-b24f8e` (layered on `rtc-w2-clean`)
**Predecessor:** W2 — `docs/architecture/integrated_runtime_w2_report.md`
**Date:** 2026-05-01
**Status at commit:** Scenario C (honest non-green). RTC-REQ-056 remains `PENDING`.

---

## Outcome (at commit time)

| Condition | Value |
|---|---|
| `live_provider_readiness.chosen_provider` | `null` (neither local_qwen nor anthropic_haiku reachable in commit env) |
| `path_proofs_ledger.c_primary_allow.pass` | `false` (INFRASTRUCTURE_GAP) |
| `path_proofs_ledger.c_primary_fail_closed.pass` | `true` (unchanged from W2) |
| `live_provider_attestation.json` | not written (no successful allow run) |
| `R1B_INTEGRATED_RUNTIME_ALLOW_PATH_PROOF` | `INFRASTRUCTURE_GAP` |
| `R1B_INTEGRATED_RUNTIME_FAIL_CLOSED_PATH_PROOF` | `PASS` |
| `R1B_INTEGRATED_RUNTIME_PROOF` | `NOT_APPLICABLE` (allow leg not proven) |
| **`RTC-REQ-056`** | **`PENDING`** |

Per the plan § 8, this is the **Scenario C** outcome: the W2b infrastructure
lands in the repository in an honest non-green state. When an approved
provider becomes available (either a running vLLM endpoint at
`localhost:8000/v1` OR `ANTHROPIC_API_KEY` in the environment), the
probe chain auto-flips the allow leg to PASS, writes the attestation, and
the composer flips RTC-REQ-056 to ACCEPTED with no further code changes.

---

## Row Status Matrix (unchanged in Scenario C)

| Row | W2 committed | W2b Scenario C (this commit) |
|-----|--------------|------------------------------|
| RTC-REQ-055 | PARTIAL | PARTIAL (untouched — W1p4 CALIBRATION_GAP) |
| RTC-REQ-056 | PENDING | **PENDING** (identical to W2; infra added) |
| RTC-REQ-057 | PENDING | PENDING (W3 scope — OTEL) |
| RTC-REQ-058 | PENDING | PENDING (W3 scope — replay determinism) |
| RTC-REQ-059 | ACCEPTED | ACCEPTED (untouched) |

---

## What W2b Adds

### P1 — Provider readiness probe
`tools/certification/evidence/probe_live_provider_readiness.py` — writes
`artifacts/certification/integrated_runtime/live_provider_readiness.json`
with per-candidate availability, chosen provider, and failure reasons.
Tries **local_qwen first** (per plan § 1 SSOT order), then anthropic_haiku.
No secret values are ever written — only booleans and public endpoint URLs.

### P2 — Rubric stability check
`tools/certification/evidence/probe_live_provider_rubric_stability.py` —
runs `LLMJudgeVeto(temperature=0).evaluate()` **three times** on a
canonical safe-reuse pair. PASS requires all 3 runs return SAFE with
confidence ≥ 0.75 and latency < 10 s. Computes `response_hash_mode`:
`exact` if all raw responses hash identically, `paraphrase_tolerant`
otherwise (the canonical mode for real LLMs).

### P3 — Probe ladder rewrite
`tools/certification/evidence/probe_integrated_runtime_safe_reuse.py` —
`_build_c_primary_allow_orchestrator()` now returns `(None, "NONE_AVAILABLE")`
instead of falling back to `mock_safe`. The ladder is:

1. `local_qwen` (if vLLM reachable at `localhost:8000/v1`)
2. `anthropic_haiku` (if `ANTHROPIC_API_KEY` set)
3. Otherwise → INFRASTRUCTURE_GAP, `latest/` stays empty, composer and
   verifier both report NOT_APPLICABLE.

`mock_safe` is **entirely removed** from the certification path. It remains
in `llm_judge_veto.py` for unit tests only, behind the
`LLMJUDGEVETO_APPROVED_MOCK_SAFE=1` opt-in.

### P4 — Attestation writer
`tools/certification/evidence/_live_provider_attestation.py` —
`build_attestation_payload()` + `write_attestation()` emit a schema-v1
JSON payload next to the `c_primary_allow/` manifest. Payload includes
`rubric_hash_sha256` (replayability), `response_hash_sha256` (per
`response_hash_mode`), `env_probe` (presence-only booleans), and explicit
`mock_safe_used=false` / `approved_provider=true` flags.

### P5 — Composer gate
`scripts/compose_semantic_cache_subclaims.py` adds
`_validate_live_provider_attestation()` — a 7-condition conjunctive check
invoked by `_map_integrated_runtime_proof()`. Distinct reason codes:

- `REJECT_MISSING_ATTESTATION`
- `REJECT_ATTESTATION_SCHEMA_INVALID`
- `REJECT_MOCK_SAFE_IN_CERTIFICATION`
- `REJECT_UNAPPROVED_PROVIDER`
- `REJECT_DETERMINISTIC_PROOF_STAGE_IN_CERTIFICATION`
- `REJECT_UNAPPROVED_VETO_STAGE_CLASS`
- `REJECT_NON_SAFE_AS_ALLOW`
- `REJECT_SAFE_WITHOUT_RUBRIC_HASH`
- `REJECT_SAFE_WITHOUT_RESPONSE_HASH`

### P6 — Verifier rejection matrix
`ops_scripts/ci/verify_r1b_safe_reuse_integrated_runtime.py` implements
the same 8-row rejection matrix. Invoked from `main()` only when the
canonical run has `allow=True` — fail-closed-leg verification is
unchanged and does not require an attestation.

### P7 — Test matrix (8 canonical cases)
3 new test files, 33 new test cases. T1 and T2 are
`pytest.mark.integration` (skip unless `W2B_LIVE_LOCAL_QWEN=1` or
`W2B_LIVE_ANTHROPIC=1` set). T3-T8 are pure unit tests exercising
every REJECT_* reason code.

Plus retrofit of 5 pre-existing W2 test files with module-level
`pytestmark = pytest.mark.skipif(not LATEST_MANIFEST.exists(), reason=...)`
— these are W2 assertions that require `latest/` to be populated, which
only happens when an approved provider is available. Skip message tells
the reader exactly how to re-enable.

### P8 — CI workflow hardening
`.github/workflows/runtime-certification.yml` gains a manual-dispatch
job `live_provider_acceptance` gated on
`workflow_dispatch.inputs.live_provider_acceptance='true'`. The job's
pre-flight env-probe exits 2 if `LLMJUDGEVETO_APPROVED_MOCK_SAFE` is set
OR if neither `LOCAL_QWEN_ENDPOINT` nor `ANTHROPIC_API_KEY` is present.
Post-run step re-asserts the mock_safe flag did not get set mid-run.

### P9 — This report + honest evidence commit

---

## Re-enabling RTC-REQ-056 (operator runbook)

Scenario A: local_qwen

1. Start a vLLM server serving `Qwen2.5-7B-Instruct` (or equivalent) at
   `localhost:8000/v1`. Confirm with `curl http://localhost:8000/v1/models`.
2. Run `python tools/certification/evidence/probe_live_provider_readiness.py`
   and confirm `chosen_provider == "local_qwen"`.
3. Run `python tools/certification/evidence/probe_live_provider_rubric_stability.py`
   and confirm `stability.pass == true`.
4. Run `python tools/certification/evidence/probe_integrated_runtime_safe_reuse.py`
   and confirm `[c_primary_allow] match_status=PASS` and
   `attestation written: .../live_provider_attestation.json`.
5. Run `python ops_scripts/ci/record_w2_verifier_results.py`.
6. Run `python scripts/compose_semantic_cache_subclaims.py` and confirm
   `R1B_INTEGRATED_RUNTIME_PROOF = PASS`, `RTC-REQ-056 = ACCEPTED`.

Scenario B: anthropic_haiku

1. Set `ANTHROPIC_API_KEY=sk-ant-...` in the shell.
2. Ensure vLLM is NOT reachable at `localhost:8000/v1` (or set
   `LOCAL_QWEN_ENDPOINT=http://localhost:65535/v1` to force fallback).
3. Steps 2-6 as above — `chosen_provider` will be `anthropic_haiku` and
   the attestation will record `provider=anthropic_haiku`, `model_id=claude-haiku-4-5`.

Scenario C (this commit):

Both unavailable → W2b infrastructure lands but RTC-REQ-056 stays
PENDING. Nothing else to do; the flip is automatic once a provider
becomes reachable.

---

## Non-Negotiables Preserved

- `mock_safe` is NEVER a certification path. Probe ladder refuses it,
  composer rejects it with `REJECT_MOCK_SAFE_IN_CERTIFICATION`, verifier
  rejects it with the same code, CI workflow env-probe exits 2 if the
  opt-in flag is set.
- `LLMJUDGEVETO_APPROVED_MOCK_SAFE` stays unset in committed CI. The
  CI workflow W2b.0 and W2b.7 both assert this.
- No W3 scope touched (RTC-REQ-057 OTEL, RTC-REQ-058 replay remain
  PENDING).
- No W4 scope touched (Merkle root unchanged).
- RTC-REQ-055 stays PARTIAL (W1p4 CALIBRATION_GAP pinned).
- RTC-REQ-059 stays ACCEPTED (E5 composition untouched).
- No change to rubric, `LLMJudgeVeto` parsing, or fail-closed semantics.

---

## Test Summary

```
tests/runtime/test_live_provider_readiness.py         — 10 passed, 0 skipped
tests/runtime/test_live_provider_attestation.py       — 11 passed, 0 skipped
tests/runtime/test_live_provider_allow_proof.py       — 14 passed, 2 skipped (T1/T2 integration)
test_integrated_runtime_legacy_dense_only_stays_partial.py — 7 passed

W2 regression slice (13 files, 131 tests) — 109 passed, 22 skipped, 0 failed
  (all 22 skips are "latest/ empty without approved provider" — matches
   committed Scenario C state exactly)
```

---

## File Index

### New

- `tools/certification/evidence/probe_live_provider_readiness.py`
- `tools/certification/evidence/probe_live_provider_rubric_stability.py`
- `tools/certification/evidence/_live_provider_attestation.py`
- `tests/runtime/test_live_provider_readiness.py`
- `tests/runtime/test_live_provider_attestation.py`
- `tests/runtime/test_live_provider_allow_proof.py`
- `docs/architecture/integrated_runtime_w2b_report.md` (this file)

### Modified

- `tools/certification/evidence/probe_integrated_runtime_safe_reuse.py` —
  provider-ladder rewrite; mock_safe removed from cert path; attestation
  emission; path_proofs_ledger schema bumped to v2.
- `scripts/compose_semantic_cache_subclaims.py` — 7-condition attestation
  gate invoked from `_map_integrated_runtime_proof()`.
- `ops_scripts/ci/verify_r1b_safe_reuse_integrated_runtime.py` — 8-row
  rejection matrix on allow runs.
- `.github/workflows/runtime-certification.yml` —
  `live_provider_acceptance` manual-dispatch job with env-probe gating.
- `tests/runtime/test_integrated_runtime_entrypoint_safe_reuse.py`,
  `test_integrated_runtime_artifact_chain.py`,
  `test_integrated_runtime_exit_x3.py`,
  `test_integrated_runtime_terminal_no_l2.py`,
  `test_integrated_runtime_no_harness_stamping.py` — module-level skipif
  when `latest/` is empty (Scenario C).
