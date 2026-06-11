---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\rtc-w2b-scenario-a-local-qwen-bd70e0.md'
original_relative_path: 'rtc-w2b-scenario-a-local-qwen-bd70e0.md'
source_sha256: 4d0f6217169314c1be07a165a0367028c65f5e1b14b1930ec150f8fe5495d63c
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-05-02'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# RTC W2b Scenario A — Local-qwen ALLOW-Path Flip for RTC-REQ-056

**Plan ID:** `rtc-w2b-scenario-a-local-qwen-bd70e0`
**Date:** 2026-05-01
**Tier:** T2 (infrastructure run + evidence regeneration; no code changes expected)
**Predecessor:** W2b infrastructure PR (`rtc-w2b-live-provider-allow-proof-b24f8e`)
**Branch:** new worktree `rtc-w2b-scenario-a-local-qwen-bd70e0` layered on top of the merged W2b PR (or on `rtc-w2b-live-provider-allow-proof-b24f8e` if running pre-merge)

**Status:** Todo — awaiting operator approval before execution.

---

## Goal

Flip `RTC-REQ-056` from **PENDING** to **ACCEPTED** using `local_qwen` via vLLM serving `Qwen2.5-7B-Instruct` at `localhost:8000`. No code changes. Runs the existing W2b chain against a live endpoint and captures `live_provider_attestation.json` at the canonical path, then regenerates the full verification chain and commits the evidence delta on a dedicated branch.

If the chain at any point fails to produce a stable SAFE attestation from `local_qwen`, this plan exits without flipping the row — RTC-REQ-056 stays PENDING and the operator either fixes the vLLM deployment or falls over to Scenario B (Anthropic Haiku).

---

## Non-Negotiables

- `mock_safe` MUST remain disabled. `LLMJUDGEVETO_APPROVED_MOCK_SAFE` MUST remain unset throughout.
- No edits to `LLMJudgeVeto` parsing, rubric, or fail-closed semantics.
- No edits to `probe_integrated_runtime_safe_reuse.py`, composer, or verifier — Scenario A is a **run**, not a code change.
- If `local_qwen` is unavailable OR the rubric stability check fails OR the probe fails OR the attestation is malformed, the operator stops here and does NOT proceed to flip. No workarounds.
- No W3 / W4 scope touched.
- Evidence artifacts regenerated on a clean branch; no force-push; no rewriting of pushed history.

---

## Prerequisites

| Prerequisite | Check command / action |
|---|---|
| W2b infrastructure on branch | `git log --oneline` shows W2b P1–P9 commits |
| Python 3.12 environment | `python --version` |
| Repo clean | `git status --short` returns nothing |
| `LLMJUDGEVETO_APPROVED_MOCK_SAFE` unset | `python -c "import os; assert not os.environ.get('LLMJUDGEVETO_APPROVED_MOCK_SAFE'), 'must be unset'; print('OK')"` |
| vLLM server running | See §1 — Start / Verify local_qwen |

---

## § 1 — Start / Verify local_qwen

### 1a. Start vLLM (if not already running)

```
docker run --rm --gpus all --ipc=host -p 8000:8000 \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  vllm/vllm-openai:latest \
  --model Qwen/Qwen2.5-7B-Instruct \
  --served-model-name Qwen/Qwen2.5-7B-Instruct \
  --dtype auto --max-model-len 8192
```

*Exact invocation will depend on the operator's GPU / driver environment. The* ***contract*** *is: OpenAI-compatible* `v1` *endpoint at* `http://localhost:8000/v1`*, serving* `Qwen/Qwen2.5-7B-Instruct` *or compatible rubric-respecting model.*

### 1b. Verify endpoint

```
curl -sS http://localhost:8000/v1/models
```

Expected: HTTP 200 with a `data: [{...}]` list including the served model id.

### 1c. (Optional) override endpoint URL

If vLLM is bound on a different port / host, set `LOCAL_QWEN_ENDPOINT` before running the probes:

```
$env:LOCAL_QWEN_ENDPOINT = "http://localhost:8000/v1"
```

`ANTHROPIC_API_KEY` MUST remain unset so the ladder picks local_qwen (it's first anyway, but explicit is better).

```
$env:ANTHROPIC_API_KEY = $null
```

---

## § 2 — Scenario A Execution Chain

Run in order. Stop immediately if any step reports failure.

### P1 — Readiness probe

```
python tools/certification/evidence/probe_live_provider_readiness.py
```

**Expected output keys in `artifacts/certification/integrated_runtime/live_provider_readiness.json`:**
- `chosen_provider == "local_qwen"`
- `candidates[0].available == true`
- `candidates[0].probe_latency_ms` < 5000
- `unavailable_reasons` contains only anthropic_haiku (because ANTHROPIC_API_KEY unset)

**Fail-closed outcomes:**
- `chosen_provider == null` → vLLM not reachable. Fix vLLM, retry. Do NOT proceed.
- `chosen_provider == "anthropic_haiku"` → vLLM unavailable and ANTHROPIC_API_KEY set. Fall over to Scenario B plan (separate).

### P2 — Rubric stability

```
python tools/certification/evidence/probe_live_provider_rubric_stability.py
```

**Expected in `rubric_stability_report.json`:**
- `provider == "local_qwen"`
- `stability.pass == true`
- All 3 runs: `verdict == "SAFE"`, `confidence >= 0.75`, `latency_ms < 10000`
- `stability.response_hash_mode` is `"exact"` (deterministic) or `"paraphrase_tolerant"`

**Fail-closed outcomes:**
- `stability.pass == false` with `verdict != SAFE` on any run → model mis-scoring the canonical safe-reuse pair. Investigate rubric / model. Do NOT proceed.
- Any `confidence < 0.75` → model unsure on a trivial case; quality too low for certification. Do NOT proceed.
- Any `latency_ms > 10000` → endpoint too slow for the 10 s policy budget. Fix endpoint or falls over to Scenario B.
- Any parse error / timeout / exception → fail-closed outcome, do NOT proceed.

### P3 — Integrated runtime probe (triple-run)

```
python tools/certification/evidence/probe_integrated_runtime_safe_reuse.py
```

**Expected stdout lines:**
- `[c_primary_allow] provider=local_qwen`
- `[c_primary_allow] match_status=PASS det_used=False allow=True x3=X3D outcome=ALLOWED`
- `attestation written: artifacts/certification/integrated_runtime/c_primary_allow/live_provider_attestation.json`
- `[c_primary_fail_closed] match_status=PASS ... outcome=<one of TIMEOUT/UNKNOWN/ERROR/PARSE_FAIL>` (unchanged from W2)
- `[structural] match_status=STRUCTURAL_ONLY allow=True x3=X3D` (unchanged)
- `allow_pass=True fc_pass=True`

**Expected artifact path (canonical):**
```
artifacts/certification/integrated_runtime/c_primary_allow/live_provider_attestation.json
```

Schema (§3 of the W2b parent plan):
- `provider == "local_qwen"`
- `mock_safe_used == false`
- `deterministic_proof_stage_used == false`
- `veto_stage_class == "LLMJudgeVeto"`
- `verdict == "SAFE"` AND `safe_reuse_allow == true` AND `x3_disposition == "X3D"`
- Non-empty `rubric_hash_sha256` and `response_hash_sha256`
- `approved_provider == true`

**Fail-closed outcomes:**
- `allow_pass=False` → integrated run did not produce SAFE / X3D. Do NOT proceed. Investigate whether (a) L0 routing mis-classified the seed, (b) D2 cache recall failed, (c) the veto returned UNKNOWN or errored. Evidence is in `c_primary_allow/`.
- Attestation file missing → probe skipped the writer (likely because `allow_succeeded` was false). Do NOT proceed.

### P4 — W2 verifier chain (5 verifiers) + ledger

```
python ops_scripts/ci/record_w2_verifier_results.py
```

**Expected:** all 5 verifiers exit 0. Ledger at
`artifacts/certification/integrated_runtime/verifier_results.json`.

**Fail-closed outcomes:**
- Any verifier non-zero → specific `REJECT_*` reason code identifies the failure. Do NOT proceed without remediating the exact reason code.

### P5 — Composer

```
python scripts/compose_semantic_cache_subclaims.py
```

**Expected:**
- `R1B_INTEGRATED_RUNTIME_ALLOW_PATH_PROOF = PASS`
- `R1B_INTEGRATED_RUNTIME_FAIL_CLOSED_PATH_PROOF = PASS`
- `R1B_INTEGRATED_RUNTIME_PROOF = PASS`
- `RTC-REQ-056 = ACCEPTED` in the composed sidecar

**Fail-closed outcomes:**
- Any `REJECT_*` reason code from `_validate_live_provider_attestation` → attestation malformed or schema-invalid. Do NOT proceed.
- `INFRASTRUCTURE_GAP` on the allow leg → upstream probe step didn't actually produce a valid attestation. Do NOT proceed.

### P6 — Strict-mode sidecar verifier

```
python scripts/verify_semantic_cache_certification.py --strict
```

**Expected:** exit 0. Strict mode requires the sidecar to exist, be well-formed, and every required subclaim to PASS.

**Fail-closed outcome:** non-zero exit → sidecar contract broken. Do NOT proceed.

### P7 — Acceptance verifier

```
python scripts/verify_runtime_certification_acceptance.py
```

**Expected:** exit 0 with RTC-REQ-056 listed as ACCEPTED, RTC-REQ-059 ACCEPTED, RTC-REQ-055 PARTIAL, RTC-REQ-057/058 PENDING.

**Fail-closed outcome:** non-zero exit → acceptance matrix mismatch. Do NOT proceed.

### P8 — Matrix verifier

```
python scripts/verify_runtime_certification_matrix.py
```

**Expected:** exit 0 with the matrix universe intact.

### P9 — Source divergence

```
python scripts/verify_source_divergence.py
```

**Expected:** exit 0. No divergence between committed source and the schema-validated universe.

**Fail-closed outcome:** non-zero exit → schema drift. Re-run `scripts/generate_runtime_cert_schema.py` and commit before proceeding.

---

## § 3 — Canonical Verification Chain (required — copy-pasteable)

When implementing this plan later, run exactly this sequence:

```
python tools/certification/evidence/probe_live_provider_readiness.py
python tools/certification/evidence/probe_live_provider_rubric_stability.py
python tools/certification/evidence/probe_integrated_runtime_safe_reuse.py
python ops_scripts/ci/record_w2_verifier_results.py
python scripts/compose_semantic_cache_subclaims.py
python scripts/verify_semantic_cache_certification.py --strict
python scripts/verify_runtime_certification_acceptance.py
python scripts/verify_runtime_certification_matrix.py
python scripts/verify_source_divergence.py
```

All nine commands MUST exit 0 for Scenario A to succeed.

---

## § 4 — Expected Row Transition

**Success path:**

| Row | Before | After Scenario A |
|-----|:------:|:---------------:|
| RTC-REQ-055 | PARTIAL | **PARTIAL** (untouched) |
| RTC-REQ-056 | PENDING | **ACCEPTED** (flipped by live local_qwen SAFE attestation) |
| RTC-REQ-057 | PENDING | PENDING (W3 scope) |
| RTC-REQ-058 | PENDING | PENDING (W3 scope) |
| RTC-REQ-059 | ACCEPTED | **ACCEPTED** (untouched) |

**Failure path (any of §2 fail-closed outcomes):**

| Row | Before | After failed Scenario A |
|-----|:------:|:---------------------:|
| RTC-REQ-056 | PENDING | **PENDING** (unchanged) |

No row regresses. The operator either fixes the underlying failure and retries, or proceeds to Scenario B (Anthropic Haiku).

---

## § 5 — Commit & PR

If all 9 verification steps pass:

1. Ensure only these files changed:
   - `artifacts/certification/integrated_runtime/live_provider_readiness.json`
   - `artifacts/certification/integrated_runtime/rubric_stability_report.json`
   - `artifacts/certification/integrated_runtime/path_proofs_ledger.json`
   - `artifacts/certification/integrated_runtime/verifier_results.json`
   - `artifacts/certification/integrated_runtime/c_primary_allow/*` (new attestation + manifest)
   - `artifacts/certification/integrated_runtime/c_primary_fail_closed/*`
   - `artifacts/certification/integrated_runtime/latest/*` (mirror of c_primary_allow)
   - `artifacts/certification/integrated_runtime/structural_allow_topology/*`
   - Composed sidecar(s) under `artifacts/certification/`
2. ⚠️ **Note:** `artifacts/certification/` is in `.gitignore` by default (evidence is regenerable). The Scenario A commit may require an explicit `-f` add for a small subset of attestation / ledger files if they are to be persisted for audit, OR the commit may be limited to doc updates referencing the run timestamp. Decide BEFORE the run whether evidence is committed or only attached to the PR as a CI upload artifact.
3. Commit on branch `rtc-w2b-scenario-a-local-qwen-bd70e0`:
   ```
   git checkout -b rtc-w2b-scenario-a-local-qwen-bd70e0
   git add <explicit whitelist>
   git commit -m "feat(rtc-w2b): Scenario A — live local_qwen SAFE attestation flips RTC-REQ-056 to ACCEPTED"
   ```
4. Push and open PR against `rtc-w2-clean` (or `main` if W2b PR has already merged).
5. PR description MUST include: vLLM model id + version, runtime environment (OS, GPU, CUDA), `rubric_hash_sha256`, `response_hash_sha256`, `latency_ms`, and a link to the `live_provider_attestation.json` artifact upload.

---

## § 6 — Rollback

If the Scenario A commit is later found to have used:
- a mis-configured vLLM (wrong model id, wrong rubric, deterministic-mode stub),
- a non-approved provider,
- `mock_safe`,
- a fabricated SAFE output,

then:
1. Revert the Scenario A commit (`git revert <sha>`).
2. Re-run the verification chain from §3; it MUST now report RTC-REQ-056 PENDING again.
3. File an ADR documenting the bad attestation + remediation.
4. No silent rollbacks; every revert carries an ADR.

---

## § 7 — Success Metric

Scenario A succeeds iff:
1. `live_provider_attestation.json` at the canonical path has `provider=local_qwen`, `verdict=SAFE`, `safe_reuse_allow=true`, `x3_disposition=X3D`, `mock_safe_used=false`, `deterministic_proof_stage_used=false`, non-empty rubric + response hashes.
2. All 9 commands in §3 exit 0.
3. Composed sidecar reports `RTC-REQ-056 = ACCEPTED`.
4. RTC-REQ-055 stays PARTIAL; RTC-REQ-059 stays ACCEPTED; RTC-REQ-057/058 stay PENDING.
5. `LLMJUDGEVETO_APPROVED_MOCK_SAFE` was unset throughout.

Anything less → RTC-REQ-056 stays PENDING; Scenario A aborted; evaluate Scenario B or fix local_qwen and retry.

---

## Status

**Todo — awaiting operator approval before execution.**

Do not execute until the user explicitly approves.
