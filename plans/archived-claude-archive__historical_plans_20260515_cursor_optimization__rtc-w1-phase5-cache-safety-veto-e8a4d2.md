---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\rtc-w1-phase5-cache-safety-veto-e8a4d2.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\rtc-w1-phase5-cache-safety-veto-e8a4d2.md'
source_sha256: ef59d19668e7327a3e6ef0b53abd39363e3535315b7a70defc94d243be017515
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: rtc-w1-phase5-cache-safety-veto-e8a4d2
plan_type: infra    # certification tooling — new code in tools/certification/safety/, no agentic_core refactor
---

# W1 Phase 5 — Semantic-Cache Safety Architecture (Veto Stage)

Plan ID: `rtc-w1-phase5-cache-safety-veto-e8a4d2`
Status: **DRAFT — awaiting user approval (Author-Gate on Wave A.3 picks Option B vs C)**
Parent: `rtc-w1-phase4-threshold-adr-b4c9e1.md` (commit `3f7af3d5f7` + parallel `60112b7ccf`)
User approval requested: 2026-04-30

---

## Context (SCQA)

- **Situation** — W1p4 produced an honest `NO_SAFE_THRESHOLD_FOUND`. At every candidate threshold in `[0.80, 0.85, 0.88, 0.90, 0.92, 0.95]`, the 100-pair certification dataset reports safety-critical false-positives (FP ≥ 2 at 0.95, ≥ 17 at 0.80). The ADR (`SEMCACHE-THRESH-001`) is on disk as `PROPOSED_NOT_APPLIED` / `PENDING_APPROVAL`. RTC-REQ-055 = `PARTIAL`.
- **Complication** — BGE-M3 dense cosine alone is **insufficient** for unsafe near-miss discrimination. Adversarial pairs like `cancel order` ↔ `place order`, `enable 2FA` ↔ `disable 2FA`, `add user` ↔ `remove user` exceed cosine ≥ 0.95 because they share > 95% tokens, yet they are semantically opposite and unsafe to reuse from cache. Lowering the threshold trades safety for recall and never reaches FP = 0. Removing the adversarial negatives would forge a green by hiding the failure mode.
- **Question** — How do we make semantic-cache reuse safe **without** weakening the threshold or the dataset, by adding a secondary veto stage that catches semantically-opposite intents?
- **Answer** — Adopt a layered safety architecture: dense cosine remains the candidate generator at the existing `0.95` threshold; a secondary **veto stage** (cross-encoder primary OR LLM-judge primary, with optional deterministic lexical pre-veto) must approve reuse before the cached answer is returned. Any veto `UNKNOWN` / `ERROR` / parse-failure fails closed (VETO). Certification passes only when dense + veto together yield FP = 0 on the unmodified 100-pair dataset.

---

## Goal

Design and prove a secondary veto stage for semantic-cache reuse that closes the FP-on-hard-negative gap surfaced by W1p4, **without** lowering the threshold and **without** removing adversarial pairs.

## Non-Goals (user-confirmed 2026-04-30)

- ❌ No W2 integrated runtime.
- ❌ No W3 OTEL / replay.
- ❌ No W4 final certification / Merkle.
- ❌ No threshold lowering (`SemanticCacheManager._TIER_THRESHOLD_DEFAULTS["dynamic"] = 0.95` stays untouched).
- ❌ No removal of adversarial hard negatives from `data/certification/calibration_pairs.json` v2.
- ❌ No forced green. RTC-REQ-055 stays `PARTIAL` until both dense + veto produce FP = 0 evidence.
- ❌ No threshold ADR auto-approval. The W1p4 ADR remains `PROPOSED_NOT_APPLIED`.
- ❌ No `agentic_core/L4_state/utils/memory/semantic_cache_manager.py` change in W1p5 (production wiring is W2's job, not W1p5's).

## What W1p5 Does NOT Promise

- ❌ Does **not** flip `R1B_PRODUCTION_THRESHOLD_PROOF` to `PASS`. That subclaim is gated on a separate APPROVED+APPLIED threshold ADR (W1p4's domain) and remains `CALIBRATION_GAP` after W1p5.
- ❌ Does **not** flip `RTC-REQ-055` to `ACCEPTED`. RTC-REQ-055 inherits the partial-blocker chain.
- ✅ **Does** add a new subclaim `R1B_SEMANTIC_CACHE_SAFETY_VETO_PROOF` that can land at `PASS` with veto-FP=0 evidence — without that, composition cannot pass even if a future threshold ADR is approved.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `.windsurf/plans/rtc-w1-phase4-threshold-adr-b4c9e1.md` | parent plan, dataset / probe contract | ✅ committed |
| `data/certification/calibration_pairs.json` (v2, 100 pairs) | unchanged input — must not be modified | ✅ on disk |
| `artifacts/certification/threshold_sweep_results.json` | baseline (no-veto) numbers per threshold | ✅ on disk |
| `artifacts/certification/semantic_cache_threshold_adr.json` | confirms threshold pinned at 0.95 (`PROPOSED_NOT_APPLIED`) | ✅ on disk |
| `tools/certification/evidence/probe_threshold_sweep.py` | template for sweep probe; W1p5 forks `_with_veto` variant | ✅ |
| `scripts/compose_semantic_cache_subclaims.py` | will gain Rule 8 (composition requires veto PASS) | ✅ |
| `agentic_core/L4_state/utils/memory/semantic_cache_manager.py` | READ-ONLY in W1p5 — confirms threshold = 0.95 dynamic | ✅ |
| Local environment probe — BGE-reranker-v2-m3 cache state | decides Wave A.3 (Option B vs C) | 🔲 W1p5.A.2 |
| External: BGE-reranker-v2-m3 model card; ms-marco-MiniLM-L-12-v2 model card | option-B sizing | 🔲 if needed |

---

## The Three Candidate Designs (User-Provided)

### Option A — Deterministic Lexical / Intent Contradiction Veto

**Mechanism**: Pure-Python rule engine. Detects opposing-action verbs (cancel↔place, enable↔disable, allow↔deny, add↔remove, grant↔revoke, accept↔reject, start↔stop, lock↔unlock, mute↔unmute), negation operators (`not`, `n't`, `never`, `without`), directional reversals (incoming↔outgoing, inbound↔outbound, up↔down, ascending↔descending), and destructive-intent markers (`delete`, `drop`, `purge`, `terminate`, `revoke`).

**Decision rule**: if any contradiction signal is present in (query XOR cached_query) → `VETO`. Otherwise → `ALLOW` (delegates to next stage).

**Files**:
- `tools/certification/safety/lexical_intent_veto.py` (~150 LOC)
- `config/certification/safety_lexicon.json` (data, not code — easy review by safety reviewer)

**Pros**: deterministic, fast (~1 ms), no model dependency, no external service, easily auditable, no calibration drift.
**Cons**: brittle / domain-specific, can produce false-positive vetoes (loses recall on benign paraphrases), requires lexicon maintenance, cannot catch subtle contradictions (`buy 100 shares` ↔ `buy 1000 shares` — same verb, different magnitude).

**On its own**: insufficient. **As a pre-veto layer**: cheap and high-precision for obvious cases. User directive: A may be added as additional pre-veto, but **must not be the only safety layer**.

### Option B — Cross-Encoder Reranker / Veto

**Mechanism**: A cross-encoder model (BGE-reranker-v2-m3, ~568 M params, OR ms-marco-MiniLM-L-12-v2, ~33 M params) takes the (query, cached_query) pair and produces a single semantic-equivalence score. A reuse decision requires score ≥ veto_threshold AND no negation/contradiction flag.

**Decision rule**: `ce_score(query, cached_query) ≥ τ_veto` → `ALLOW`. Else `VETO`. Calibration determines `τ_veto` from the 100-pair dataset such that all hard negatives score < τ.

**Files**:
- `tools/certification/safety/cross_encoder_veto.py` (~200 LOC)
- `tools/certification/evidence/probe_cross_encoder_availability.py` (Wave A.2 environment probe)
- `artifacts/certification/cross_encoder_calibration_results.json`
- Model files: cached locally under `~/.cache/huggingface/hub/`. **No model weights committed to repo.**

**Pros**: Strong pairwise discrimination for paraphrase vs. contradiction (cross-encoders attend across the pair, unlike bi-encoder cosine which encodes independently). Established model class with public benchmarks. Local-only deployment possible (no network at inference time).

**Cons**: Model dependency (~ 1.4 GB on disk for BGE-reranker-v2-m3). Latency ~50–200 ms per call (acceptable for cache writes; possibly tight for high-QPS reuse). Needs its own calibration pass and adversarial robustness check. Could still miss magnitude / numeric / temporal contradictions.

**On its own**: candidate primary safety layer. User recommendation: **start here if local CE is available**.

### Option C — Lightweight LLM-as-Judge Veto

**Mechanism**: A small instruction-following model (Qwen2.5-7B-Instruct or Llama-3-8B-Instruct, or a hosted endpoint such as Anthropic Haiku) is called with a structured rubric. The rubric: given `(query, cached_query, cached_answer)`, classify into `{SAFE, UNSAFE_DIFFERENT_INTENT, UNSAFE_POLICY_DRIFT, UNCERTAIN}`. Anything other than `SAFE` → `VETO` (fail-closed). Parse-failure → `VETO`.

**Decision rule**: structured JSON return; only `verdict == "SAFE"` allows reuse. Latency cap (e.g. 2 s) → on timeout, `VETO`.

**Files**:
- `tools/certification/safety/llm_judge_veto.py` (~250 LOC)
- `config/certification/llm_judge_rubric.md` (the rubric — version-controlled, hash-stamped)
- `artifacts/certification/llm_judge_calibration_results.json`

**Pros**: Strongest semantic-contradiction detection. Naturally catches numeric, temporal, policy, magnitude contradictions. Most robust against adversarial paraphrases that defeat cross-encoders.

**Cons**: Cost ($/call for hosted models), latency (1–3 s typical), prompt-injection risk (cache contents could be adversarial), needs offline rubric calibration with inter-rater agreement, unbounded scope (can hallucinate judgments).

**Gating**: User directive — escalate to LLM judge only for **safety-sensitive cache reuse**. This means LLM-judge is invoked when (a) action-sensitive, (b) policy-sensitive, OR (c) high lexical-overlap / low-confidence according to the deterministic pre-filter. Not invoked on every cache hit.

**On its own**: candidate primary if no local cross-encoder is available. User recommendation: **fallback path if Wave A.2 finds no local CE**.

---

## Architecture Decision (locked once Wave A.3 closes)

The plan assumes a **layered defense**:

```
Cache hit candidate
       │
       ▼
[ Layer 0: dense cosine ≥ 0.95 ]   ← unchanged from W1p4 (W1p5 keeps it pinned)
       │  ALLOW
       ▼
[ Layer 1: lexical/intent pre-veto (Option A) ]   ← optional, fast, deterministic
       │  ALLOW or DELEGATE
       ▼
[ Layer 2: primary safety veto (Option B OR Option C) ]   ← REQUIRED — picked at Wave A.3
       │  ALLOW (only if SAFE)
       ▼
   Reuse cached answer
```

Any `VETO`, `UNKNOWN`, `ERROR`, parse-fail, or timeout at any layer → **block reuse**. Fail-closed by construction.

Wave A.3 is an Author-Gate decision point: pick **B-primary** if Wave A.2 confirms a local cross-encoder fits the latency / VRAM / disk budget; else **C-primary**. Option A is appended as a pre-veto in either path (cheap, deterministic, easy to disable if it costs too much positive recall).

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|---|---|---|---:|---|---|
| **A** | A.1, A.2, A.3 | Architecture decision doc + local-CE availability probe + Author-Gate B vs C | ~10K | 🔲 TODO | Decision MD written; CE-availability probe emitted; user signs Wave A.3 picking B or C |
| **B** | B.1, B.2 | Veto policy schema + protocol contract | ~6K | 🔲 TODO | Schema + Protocol class compile; `semantic_cache_veto_policy.json` lands |
| **C** | C-B.1, C-B.2, C-B.3 *(if B chosen)* OR C-C.1, C-C.2, C-C.3 *(if C chosen)* | Implement primary veto | ~14K | 🔲 TODO | Primary veto module + calibration artifact emitted; module-level tests pass |
| **D** | D.1, D.2, D.3 | Optional Lexical/Intent pre-veto (Option A) | ~6K | 🔲 TODO | Pre-veto module + lexicon + tests pass |
| **E** | E.1, E.2, E.3 | Veto probe + sweep-with-veto + veto-negative controls | ~10K | 🔲 TODO | All 3 evidence artifacts emitted; FP=0 on hard negs at 0.95 + veto |
| **F** | F.1, F.2, F.3 | Composer Rule 8 + new subclaim wiring + tests | ~8K | 🔲 TODO | New subclaim emits PASS / PARTIAL honestly; 6 new test files green |
| **G** | G.1, G.2 | CI wiring + final verification | ~4K | 🔲 TODO | Workflow updated; full chain rerun; RTC-REQ-055 unchanged at PARTIAL |

**Total estimate**: ~58K tokens across 7 waves.

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---:|---|
| A.1 | Architecture decision MD | NEW `docs/architecture/semantic_cache_safety_architecture_decision.md` — A/B/C side-by-side, latency budgets, fail-modes, expected probe outcomes | Must be readable by safety reviewer; cite W1p4 sweep numbers verbatim | ~5K | 🔲 |
| A.2 | Local cross-encoder availability probe | NEW `tools/certification/evidence/probe_cross_encoder_availability.py`; OUTPUT `artifacts/certification/cross_encoder_availability_report.json` (CE present? VRAM headroom? disk?) | Must not download — only check cache + driver | ~2K | 🔲 |
| **A.3** | **Author-Gate: B-primary vs C-primary** | NO files — `ask_user_question` decision based on A.1 + A.2 evidence | Refactor-class architecture decision: emit `DECISION_CAPTURED:` marker | ~3K | 🔲 |
| B.1 | Veto Protocol contract | NEW `tools/certification/safety/__init__.py`; NEW `tools/certification/safety/veto_protocol.py` (Protocol class `VetoStage` with `evaluate(query, cached_query, cached_answer) -> VetoResult`) | Stable API — Wave C / D / F all bind to it | ~3K | 🔲 |
| B.2 | Veto policy schema + JSON | NEW `config/certification/veto_policy_schema.json` (fields: `enabled_stages`, `fail_closed_defaults`, `latency_budget_ms`, `error_handling`); NEW output `artifacts/certification/semantic_cache_veto_policy.json` | Schema must be deterministic from policy file — no live config | ~3K | 🔲 |
| **C-B.1** | Cross-encoder veto module *(if B chosen)* | NEW `tools/certification/safety/cross_encoder_veto.py`; loads BGE-reranker-v2-m3 OR ms-marco-MiniLM-L-12-v2; implements `VetoStage` Protocol | Model load latency (cold start); fail-closed on import error | ~5K | 🔲 cond |
| **C-B.2** | CE veto threshold calibration *(if B chosen)* | EXEC probe → emit `artifacts/certification/cross_encoder_calibration_results.json` per-pair scores + chosen `τ_veto` | Must use the unmodified 100-pair v2 dataset; report recall@FP=0 honestly | ~5K | 🔲 cond |
| **C-B.3** | CE veto unit tests *(if B chosen)* | NEW `tests/runtime/test_cross_encoder_veto.py` (~30 tests: pos pairs ALLOW, hard negs VETO, model-error VETO, timeout VETO, mtime invariance) | Local-only via `pytest.mark.skipif(not _ce_cached, ...)`; CI continue-on-error | ~4K | 🔲 cond |
| **C-C.1** | LLM-judge veto module *(if C chosen)* | NEW `tools/certification/safety/llm_judge_veto.py`; pluggable provider (local Qwen / hosted Haiku); structured JSON parsing; fail-closed on parse error | Prompt-injection guard (escape cached_answer); timeout=2s default; deterministic temperature=0 | ~6K | 🔲 cond |
| **C-C.2** | LLM-judge calibration *(if C chosen)* | NEW `config/certification/llm_judge_rubric.md`; emit `artifacts/certification/llm_judge_calibration_results.json` (per-pair verdicts + token cost + latency p50/p95) | Rubric must be version-controlled with sha256 hash | ~5K | 🔲 cond |
| **C-C.3** | LLM-judge unit tests *(if C chosen)* | NEW `tests/runtime/test_llm_judge_veto.py` (~30 tests including adversarial cached_answer with prompt-injection attempt → fail-closed VETO) | Mockable provider for CI; local-only for end-to-end | ~4K | 🔲 cond |
| D.1 | Lexical/intent pre-veto module | NEW `tools/certification/safety/lexical_intent_veto.py`; implements `VetoStage` Protocol | Lexicon-driven, not regex-soup; data-as-config | ~3K | 🔲 |
| D.2 | Safety lexicon | NEW `config/certification/safety_lexicon.json` (opposing-verb pairs, negation tokens, directional reversals, destructive markers) | Must be reviewable by non-engineer; provenance comments inline | ~1K | 🔲 |
| D.3 | Lexical pre-veto unit tests | NEW `tests/runtime/test_lexical_intent_veto.py` (~25 tests: cancel↔place VETO, enable↔disable VETO, paraphrase pass DELEGATE, empty-token edge cases) | Default DELEGATE for ambiguous cases — never auto-ALLOW alone | ~2K | 🔲 |
| E.1 | Integration veto probe | NEW `tools/certification/evidence/probe_semantic_cache_veto.py`; runs configured pipeline (Layer 1 + Layer 2 [+ optional Layer 0 noise]) on the 100-pair dataset; OUTPUT `artifacts/certification/semantic_cache_veto_probe.json` | Anti-cheat: probe MUST NOT modify the dataset; MUST NOT cache results between runs | ~4K | 🔲 |
| E.2 | Sweep-with-veto probe | NEW `tools/certification/evidence/probe_threshold_sweep_with_veto.py`; rerun the 6-threshold sweep but ALSO require veto ALLOW; OUTPUT `artifacts/certification/threshold_sweep_results_with_veto.json` | Must match sweep schema for diff-ability against W1p4 baseline | ~3K | 🔲 |
| E.3 | Veto-specific negative controls | NEW `tools/certification/evidence/probe_semantic_cache_veto_negatives.py`; tests `near_miss_negative` + `lexical_overlap_different_meaning_negative` + `policy_tenant_freshness_reuse_negative` get VETO; OUTPUT `artifacts/certification/semantic_cache_veto_negative_controls.json` | Acceptance: FP=0 on every hard negative; failures must surface, not be masked | ~3K | 🔲 |
| F.1 | Composer Rule 8 (composition needs veto PASS) | MODIFY `scripts/compose_semantic_cache_subclaims.py` — add new subclaim `R1B_SEMANTIC_CACHE_SAFETY_VETO_PROOF`; extend `R1B_DENSE_SIMILARITY_COMPOSITION_PROOF` mapping with safety-veto requirement (Rule 8) | New status `MISSING_VETO_EVIDENCE` may need entry in `ALLOWED_STATUSES`; fall back to `PARTIAL` not `BLOCKED` | ~4K | 🔲 |
| F.2 | Verifier subclaim recognition | MODIFY `scripts/verify_semantic_cache_certification.py` to recognize new subclaim and propagate to RTC-REQ-055 caveat | Must NOT change RTC-REQ-055 acceptance status calculation in this wave | ~2K | 🔲 |
| F.3 | Composer + integration tests | NEW `tests/runtime/test_safety_veto_composer.py` (~25 tests covering all gate-priority paths) | Must preserve all 320 existing W1p4 tests | ~4K | 🔲 |
| G.1 | CI wiring | MODIFY `.github/workflows/runtime-certification.yml` — add 4 new probe steps (W1.5a-d) + new tests; bump timeout if needed; upload veto artifacts | CE / LLM steps `continue-on-error` (CI lacks local model cache) | ~2K | 🔲 |
| G.2 | Final verification | EXEC full pipeline locally; capture verdict; assert R1B_PRODUCTION_THRESHOLD_PROOF still CALIBRATION_GAP, RTC-REQ-055 still PARTIAL, NEW R1B_SEMANTIC_CACHE_SAFETY_VETO_PROOF lands at honest verdict | All 320 + ~80 new tests pass | ~2K | 🔲 |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS · ✅ DONE · ❌ BLOCKED · `cond` = conditional on Wave A.3 outcome.

---

## Required Outputs (per user W1p5 spec)

| # | Artifact | Producer | Wave |
|---:|---|---|---|
| 1 | `docs/architecture/semantic_cache_safety_architecture_decision.md` | hand-authored | A.1 |
| 2 | `artifacts/certification/semantic_cache_veto_policy.json` | `probe_semantic_cache_veto.py` reads policy + emits | B.2 / E.1 |
| 3 | `artifacts/certification/semantic_cache_veto_probe.json` | `probe_semantic_cache_veto.py` | E.1 |
| 4 | `artifacts/certification/threshold_sweep_results_with_veto.json` | `probe_threshold_sweep_with_veto.py` | E.2 |
| 5 | `artifacts/certification/semantic_cache_veto_negative_controls.json` | `probe_semantic_cache_veto_negatives.py` | E.3 |
| 6 | `artifacts/certification/semantic_cache_subclaims.json` (regenerated) | `compose_semantic_cache_subclaims.py` | F.1 |
| 7 | `artifacts/certification/semantic_cache_certification_report.{json,md}` (regenerated) | `verify_semantic_cache_certification.py` | G.2 |

All 7 outputs match the user's W1p5 required-outputs list.

---

## Acceptance Criteria (per user spec, mapped to verifications)

| # | Criterion | How verified |
|---:|---|---|
| 1 | Original expanded dataset (v2, 100 pairs) remains intact | `tests/runtime/test_calibration_dataset_expanded.py` (existing 16+ tests) reruns unchanged. New `test_w1_phase5_invariants.py` asserts `data/certification/calibration_pairs.json` sha256 matches W1p4 commit. |
| 2 | All hard lexical-overlap negatives remain in test set | Same — invariant test asserts every `LO-*`, `NM-*`, `RC-*` id from W1p4 v2 is still present. |
| 3 | Reuse passes only if dense AND veto approves | Composer Rule 8 — `R1B_DENSE_SIMILARITY_COMPOSITION_PROOF = PASS` only if both `DENSE` and `SAFETY_VETO` subclaims are PASS. Tested in `test_safety_veto_composer.py`. |
| 4 | Any veto UNKNOWN / ERROR blocks reuse | `VetoStage.evaluate()` Protocol doc-strings + every implementing module has unit test for error path → VETO. Tested in C-B.3 / C-C.3 / D.3. |
| 5 | False positives must be 0 on hard negatives | `probe_semantic_cache_veto_negatives.py` asserts `unsafe_fp_count == 0`. CI gate (G.1) fails if not. |
| 6 | Positive recall must be reported, not hidden | `threshold_sweep_results_with_veto.json` carries per-threshold `recall` field; W1p5 invariant test (G.2) asserts the report markdown surfaces the recall numbers. |
| 7 | `R1B_PRODUCTION_THRESHOLD_PROOF` remains `CALIBRATION_GAP` until approved safety architecture + evidence exist | Composer Rule 7 (W1p4) unchanged. New status `CALIBRATION_GAP` retained when any of: ADR not APPROVED+APPLIED, threshold ≠ 0.95, sweep_with_veto FP > 0. |
| 8 | RTC-REQ-055 remains PARTIAL unless full safety gate passes | Verifier propagation logic — RTC-REQ-055 = ACCEPTED only if every R1B_* subclaim is PASS. With threshold_proof = CALIBRATION_GAP, RTC-REQ-055 = PARTIAL. |

---

## Expected Certification Impact

| Subclaim | Current (post-W1p4) | Expected (post-W1p5) | Gating |
|---|---|---|---|
| `R1B_APPROVED_MODEL_PROOF` | PASS (LOCAL_ONLY scope) | PASS (unchanged) | n/a |
| `R1B_PRODUCTION_THRESHOLD_PROOF` | **CALIBRATION_GAP** (ADR PENDING) | **CALIBRATION_GAP** (unchanged — W1p5 does not approve threshold change) | ADR APPROVED+APPLIED + sweep_with_veto FP=0 |
| `R1B_DENSE_SIMILARITY_COMPOSITION_PROOF` | **PARTIAL** (Rule 5: threshold ≠ PASS) | **PARTIAL** (Rule 8: threshold + safety_veto required) | Both DENSE PASS and SAFETY_VETO PASS |
| `R1B_SEMANTIC_CACHE_SAFETY_VETO_PROOF` *(NEW)* | — | **PASS** if veto FP=0 on hard negs at 0.95 + chosen veto stage; else **PARTIAL** with veto FP count + recall reported | veto probe FP=0 |
| `R1B_NEGATIVE_CONTROL_PROOF` | PASS | PASS (unchanged) | n/a |
| `R1B_POLICY_FRESHNESS_TENANT_REUSE_PROOF` | PASS | PASS (unchanged) | n/a |
| `R1B_TERMINAL_EXIT_PROOF` | PASS | PASS (unchanged) | n/a |
| 3 NOT_APPLICABLE (W2/W3) | NOT_APPLICABLE | NOT_APPLICABLE (unchanged) | W2/W3 not in scope |
| **`RTC-REQ-055` final** | **PARTIAL** | **PARTIAL** (unchanged — threshold proof still CALIBRATION_GAP) | full chain |

The honest delta: W1p5 adds a **new PASS** at the safety-veto subclaim (assuming veto evidence shows FP=0). Threshold-proof remains gap and so RTC-REQ-055 remains PARTIAL. **No forced green.**

---

## Gap Register

**GAP-1: Local cross-encoder availability is unknown until Wave A.2.**
- BGE-reranker-v2-m3 may or may not be cached on the dev machine. If absent, downloading it is ~1.4 GB and may exceed bandwidth/quota.
- Mitigation: Wave A.2 environment probe + Author-Gate at A.3 — if no CE available, switch to Option C path.

**GAP-2: Option C requires an LLM provider. The current repo has no LLM-as-judge infrastructure.**
- If Wave A.3 picks C, we need a pluggable provider: local Qwen via vLLM (preferred per `local-llm-wsl2-gpu.md`) or hosted Anthropic Haiku.
- Mitigation: Wave C-C.1 makes provider pluggable; calibration uses whichever local-or-hosted is available. Tests use a mock provider so CI doesn't depend on a live LLM.

**GAP-3: Veto calibration on the same dataset that drives certification could overfit.**
- Risk: tuning `τ_veto` or rubric on `calibration_pairs.json` v2 trains on the test set.
- Mitigation: split the dataset into `calibration_train` (60 pairs) + `calibration_holdout` (40 pairs). Tune on train, report on holdout. New artifact `calibration_pairs_split_v2.json` declares the split; original v2 remains unchanged.

**GAP-4: Composer status enum extension.**
- Adding `R1B_SEMANTIC_CACHE_SAFETY_VETO_PROOF` requires updating `ALLOWED_STATUSES` and `subclaim_targets` lists in composer + verifier.
- Mitigation: Phase F.1/F.2 modifies both in lockstep with new test (F.3) covering the new enum.

**GAP-5: Workflow runtime impact.**
- Wave G.1 adds 4+ new probe steps to the CI workflow. Cross-encoder load is ~3 s, LLM-judge can be 30+ s if it actually runs.
- Mitigation: all CE/LLM steps `continue-on-error` in CI (per the W1p4 pattern). Local validation gates the merge; CI only checks that the deterministic pieces pass.

---

## Author-Gate Decision Points

### Wave A.3 — Primary Veto Choice (REFACTOR-CLASS / `architecture_choice`)

**Trigger**: After A.1 (decision MD draft) + A.2 (CE-availability probe), the user must choose primary path B or C. The choice changes which Wave-C track executes.

**Surface**: `ask_user_question` with these options:

- **Option A — Cross-encoder primary (B-track)** — recommended IF Wave A.2 confirms ≥ 1 CE model cached locally with ≥ 4 GB free VRAM headroom. Advantages: deterministic latency, no per-call cost, fully local. Risks: model dep, GPU contention.
- **Option B — LLM-judge primary (C-track)** — recommended IF Wave A.2 reports no local CE. Advantages: strongest semantic discrimination, naturally handles numeric / temporal contradictions. Risks: cost, latency, prompt-injection surface.
- **Option C — Hybrid: cross-encoder primary + LLM-judge escalation** — ⭐ may be recommended if A.2 confirms BOTH local CE and a local LLM are available; gives fast majority path + robust escalation for safety-sensitive cases.
- **Option D — Lexical pre-veto only (Wave D)** — ❌ DOMINATED — user explicitly stated A is not sufficient on its own. Surface only as a documentation control answer.

A `DECISION_CAPTURED:` marker fires when the user picks. The chosen track determines which subset of Wave-C phases are executed.

### Wave F.1 — Composer Status Enum (REFACTOR-CLASS / `architecture_choice`)

**Trigger**: Adding a new subclaim `R1B_SEMANTIC_CACHE_SAFETY_VETO_PROOF` requires extending `ALLOWED_STATUSES` and the verifier's RTC-REQ-055 propagation logic.

**Likely deterministic** (single correct path: status enum extension is mechanical). May fire silently with `principle="schema-extension-with-back-compat"`.

---

## Rules

- **R-W1p5-1**: No edits to `agentic_core/L4_state/utils/memory/semantic_cache_manager.py`. The W1p5 work lives entirely in `tools/certification/safety/` and `tools/certification/evidence/`.
- **R-W1p5-2**: No edits to `data/certification/calibration_pairs.json`. The dataset is frozen; sha256 in `test_w1_phase5_invariants.py` enforces.
- **R-W1p5-3**: No new pair removed from any existing class. Adversarial lexical-overlap pairs remain in the certification dataset.
- **R-W1p5-4**: No edit to `_TIER_THRESHOLD_DEFAULTS`. Threshold remains 0.95 dynamic / 1.0 static.
- **R-W1p5-5**: No threshold-override env var (`SEMANTIC_CACHE_THRESHOLD_*`) assignment in any W1p5 code path. CI gate already checks; W1p5 invariant test re-asserts.
- **R-W1p5-6**: Every veto stage MUST fail-closed on error / timeout / parse-fail. Open-fail (treat error as ALLOW) is FORBIDDEN — covered by mandatory unit test in C-B.3 / C-C.3 / D.3.
- **R-W1p5-7**: All new probes MUST be anti-cheat: never modify the dataset, never write the ADR, never modify other artifacts they don't own. Same anti-cheat block as W1p4 probes.
- **R-W1p5-8**: Composer Rule 8 (composition requires both DENSE and SAFETY_VETO PASS) is **strictly added** — never replaces or relaxes the existing 7 rules.
- **R-W1p5-9**: RTC-REQ-055 final_acceptance_status calculation is unchanged. Adding a new R1B_* subclaim cannot flip RTC-REQ-055 to ACCEPTED on its own.
- **R-W1p5-10**: Calibration data split (Gap-3 mitigation) MUST land before any τ-tuning. Tuning on the full v2 dataset directly is FORBIDDEN.

---

## Implementation Commands (for reference, after plan approval)

```powershell
# Wave A — decisions only, no execution beyond A.2 probe
$env:EMBEDDING_ENABLED = "true"
python tools/certification/evidence/probe_cross_encoder_availability.py
# → Author-Gate at A.3 picks B or C

# Wave B — protocol + policy
python -c "import tools.certification.safety.veto_protocol; print('protocol importable')"

# Wave C (B-track) — cross-encoder
python tools/certification/safety/cross_encoder_veto.py --calibrate
# → cross_encoder_calibration_results.json

# OR Wave C (C-track) — LLM judge
python tools/certification/safety/llm_judge_veto.py --calibrate
# → llm_judge_calibration_results.json

# Wave D — lexical pre-veto
python -m pytest tests/runtime/test_lexical_intent_veto.py -p no:xdist -q

# Wave E — probes
python tools/certification/evidence/probe_semantic_cache_veto.py
python tools/certification/evidence/probe_threshold_sweep_with_veto.py
python tools/certification/evidence/probe_semantic_cache_veto_negatives.py

# Wave F — composer + verifier
python scripts/compose_semantic_cache_subclaims.py
python scripts/verify_semantic_cache_certification.py
python scripts/verify_runtime_certification_acceptance.py

# Wave G — final
python -m pytest tests/runtime/ -p no:xdist -p no:testmon --timeout=300 -q
```

---

## Rollback Strategy

Per-wave rollback discipline:

1. **Wave A** — pure documentation; revert by `git revert` on the doc commit.
2. **Wave B / C / D** — each module lands as a separate commit. Revert in reverse order without affecting prior waves (Protocol → impl → tests).
3. **Wave E probes** — additive; reverting deletes the artifact files but leaves the dataset and W1p4 sweep results intact.
4. **Wave F composer change** — most invasive. Backed by `test_safety_veto_composer.py` covering all 8 priority paths. If the new subclaim is misbehaving, revert F.1 + F.2 in one commit; W1p4 composer logic stays intact.
5. **Wave G** — workflow YAML edit + final verification commit. Revert leaves all source changes intact.

The composer change is the only "irreversible-feeling" edit. Mitigated by:
- F.1 lands as a pure additive enum + new mapping function (existing 7 rules unchanged in behavior).
- F.3 tests cover every existing rule path PLUS the new Rule 8 paths.
- Hot-rollback escape hatch: `SEMANTIC_CACHE_VETO_BYPASS=1` env var → composer treats SAFETY_VETO subclaim as `NOT_APPLICABLE`, identical to pre-W1p5 composition behavior. Logged with reason=bypass for audit.

---

## Acceptance Criteria — Final Gate

| Metric | Target | Verification |
|---|---|---|
| Dataset sha256 unchanged | sha256 matches W1p4 commit | `test_w1_phase5_invariants.py::test_dataset_unchanged` |
| Hard-negative FP count (sweep_with_veto, t=0.95) | 0 | `threshold_sweep_results_with_veto.json` |
| Positive recall reported (not hidden) | every threshold row has `recall` field | sweep schema test |
| `R1B_PRODUCTION_THRESHOLD_PROOF` after W1p5 | CALIBRATION_GAP | `semantic_cache_subclaims.json` |
| `R1B_SEMANTIC_CACHE_SAFETY_VETO_PROOF` after W1p5 | PASS *(if veto FP=0)* OR PARTIAL *(honest)* | `semantic_cache_subclaims.json` |
| `RTC-REQ-055 final_acceptance_status` | PARTIAL | `runtime_evidence_overrides.json` |
| All W1p4 320 tests | PASS | `pytest tests/runtime/` |
| New W1p5 tests (~80) | PASS | same |
| `_TIER_THRESHOLD_DEFAULTS` SSOT | unchanged | `test_w1_phase5_invariants.py` |
| Threshold ADR | still PROPOSED_NOT_APPLIED | `test_w1_phase5_invariants.py` |
| W1p5 anti-cheat invariants | all 10 honored | `test_w1_phase5_invariants.py` |

---

## Cascade Alignment Checks

- ✅ Plan-first; no code in this step.
- ✅ Plan saved to repo SSOT `.windsurf/plans/<slug>-<6hex>.md`.
- ✅ Wave Structure + Phase-Level Summary tables present (mandatory for T2/T3).
- ✅ Honest expected certification impact — no forced green claimed.
- ✅ Author-Gate point identified at Wave A.3 (B vs C).
- ✅ All 7 user-required output artifacts mapped to producer phases.
- ✅ All 8 user-required acceptance criteria mapped to verification points.
- ✅ Frontmatter `plan_type: infra` — §22 graph-layer-evidence gate skipped (no agentic_core refactor).
- ✅ Token estimate is a sizing heuristic, not a budget gate (per `plan-location.md`).
- ✅ Non-goals exhaustive — no W2 / W3 / W4 / threshold-lower / dataset-shrink / forced-green leakage.
