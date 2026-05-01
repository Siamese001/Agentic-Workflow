# Semantic Cache Safety Architecture Decision

**ADR ID**: `SEMCACHE-SAFETY-001`  
**Status**: `PROPOSED_NOT_APPLIED` — pending W1p5 implementation evidence  
**Parent ADR**: `SEMCACHE-THRESH-001` (threshold recalibration, W1p4)  
**Date**: 2026-04-30  
**Deciders**: TBD — safety reviewer sign-off required after W1p5 evidence  

---

## Context

W1 Phase 4 produced an honest `NO_SAFE_THRESHOLD_FOUND`. BGE-M3 dense cosine at every candidate threshold in `[0.80, 0.85, 0.88, 0.90, 0.92, 0.95]` reports safety-critical false-positives (FP ≥ 2 at 0.95, ≥ 17 at 0.80) on the 100-pair certification dataset.

The root cause: **adversarial lexical-overlap pairs** with semantically opposite intents exceed the cosine similarity threshold because they share > 95% tokens. Examples:

| Query A | Query B | Cosine @ 0.95 | Unsafe to reuse? |
|---|---|:---:|---|
| `cancel my order` | `place an order` | ~0.96 | **YES** — opposite actions |
| `enable 2FA for my account` | `disable 2FA` | ~0.97 | **YES** — opposite security posture |
| `add user alice@example.com` | `remove user alice@example.com` | ~0.98 | **YES** — opposite lifecycle |
| `grant admin access` | `revoke admin access` | ~0.97 | **YES** — opposite permissions |

Lowering the threshold trades recall for safety and never reaches FP = 0. Removing these adversarial pairs would forge a green by hiding the failure mode.

**The only viable path**: keep the 0.95 threshold as the candidate generator, and add a **secondary veto stage** that discriminates semantic equivalence from semantic contradiction before cache reuse.

---

## Decision

Adopt a **layered defense architecture** for semantic-cache reuse:

```
Cache hit candidate
       │
       ▼
[ Layer 0: Dense cosine ≥ 0.95 ]   ← existing BGE-M3 bi-encoder (frozen)
       │  (candidate generator — high recall, low precision on adversarial pairs)
       ▼
[ Layer 1: Lexical/Intent Pre-Veto (Option A) ]   ← fast deterministic filter
       │  (optional — catches obvious contradictions; delegates ambiguous to Layer 2)
       ▼
[ Layer 2: Primary Safety Veto (Option B OR C) ]   ← semantic equivalence verifier
       │  (REQUIRED — cross-encoder or LLM-judge; only SAFE verdict allows reuse)
       ▼
   Reuse cached answer
```

**Fail-closed invariant**: Any `VETO`, `UNKNOWN`, `ERROR`, parse-failure, or timeout at any layer blocks reuse. The system defaults to re-execution (cache miss) rather than unsafe reuse.

---

## Options Evaluated

### Option A: Deterministic Lexical / Intent Contradiction Veto

**Mechanism**: Pure-Python rule engine detecting:
- Opposing-action verbs (cancel↔place, enable↔disable, add↔remove, grant↔revoke, accept↔reject, lock↔unlock, etc.)
- Negation operators (`not`, `n't`, `never`, `without`)
- Directional reversals (inbound↔outbound, ascending↔descending)
- Destructive-intent markers (`delete`, `purge`, `terminate`, `revoke`)

**Decision rule**: contradiction signal in (query XOR cached_query) → `VETO`; otherwise `DELEGATE` to Layer 2.

**Pros**:
- Fast (~1 ms), deterministic, no model dependency
- Easily auditable by non-engineers (data-driven lexicon)
- No calibration drift

**Cons**:
- Brittle / domain-specific; requires lexicon maintenance
- False-positive vetoes on benign paraphrases (loses recall)
- Cannot catch subtle contradictions (`buy 100 shares` ↔ `buy 1000 shares` — same verb, different magnitude)

**Verdict**: **Rejected as primary layer.** Accepted as **optional pre-veto** (Layer 1) but must not be the only safety layer.

---

### Option B: Cross-Encoder Reranker / Veto

**Mechanism**: Cross-encoder model (e.g., BGE-reranker-v2-m3, ~568M params, or ms-marco-MiniLM-L-12-v2, ~33M) scores the `(query, cached_query)` pair as a single input. A reuse decision requires `ce_score ≥ τ_veto`.

**Calibration**: Determine `τ_veto` from the 60-pair training split such that all hard negatives score < τ, while maximizing recall on positives.

**Pros**:
- Strong pairwise discrimination (cross-encoders attend across the pair, unlike bi-encoder independent encoding)
- Established model class with public benchmarks (MS MARCO, etc.)
- Local-only deployment (no network at inference time)
- Deterministic latency (~50–200 ms per call)

**Cons**:
- Model dependency (~1.4 GB on disk for BGE-reranker-v2-m3)
- GPU VRAM required for acceptable latency
- Needs its own calibration pass
- May still miss numeric / temporal contradictions (cross-encoders are semantic, not arithmetic)

**Verdict**: **Candidate primary layer (Layer 2)** if local CE is available. Recommended starting point.

---

### Option C: Lightweight LLM-as-Judge Veto

**Mechanism**: Small instruction-following model (Qwen2.5-7B-Instruct local via vLLM, or hosted Anthropic Haiku) called with a structured rubric:

```
Given:
  Query: {query}
  Cached query: {cached_query}
  Cached answer: {cached_answer}

Classify into exactly one of:
  SAFE — semantic equivalence, safe to reuse
  UNSAFE_DIFFERENT_INTENT — semantically different or opposite intent
  UNSAFE_POLICY_DRIFT — policy/tenant/freshness contract violation
  UNCERTAIN — ambiguous, insufficient confidence

Return ONLY valid JSON: {"verdict": "...", "confidence": 0.0-1.0, "rationale": "..."}
```

Only `verdict == "SAFE"` allows reuse. Parse-failure, timeout (> 2s), or any other verdict → `VETO`.

**Invocation scope**: Escalation-only — called when (a) action-sensitive, (b) policy-sensitive, OR (c) high lexical-overlap / low confidence per deterministic pre-filter. Not invoked on every cache hit.

**Pros**:
- Strongest semantic-contradiction detection
- Naturally catches numeric, temporal, policy, magnitude contradictions
- Robust against adversarial paraphrases that defeat cross-encoders

**Cons**:
- Cost ($/call for hosted models; GPU allocation for local)
- Latency (1–3 s typical; timeout fallback required)
- Prompt-injection risk (cache contents could be adversarial)
- Needs offline rubric calibration with inter-rater agreement
- Unbounded scope (can hallucinate judgments)

**Verdict**: **Candidate primary layer (Layer 2)** if no local CE is available. Also viable as **escalation layer** in a hybrid B+C architecture.

---

## Selected Architecture: Layered Defense with Conditional Primary Veto

The safety system MUST implement:

1. **Layer 0** (unchanged): BGE-M3 dense cosine ≥ 0.95 as candidate generator.
2. **Layer 1** (optional but recommended): Lexical/intent pre-veto (Option A) for fast rejection of obvious contradictions.
3. **Layer 2** (required): One of:
   - **Path B**: Cross-encoder primary veto (if local CE cached and ≥ 4 GB VRAM available)
   - **Path C**: LLM-judge primary veto (if no local CE available)
   - **Path B+C Hybrid**: Cross-encoder majority path with LLM-judge escalation for safety-sensitive edge cases (if both resources available)

The choice between B, C, or hybrid is determined by local environment probing (Wave A.2) and confirmed via Author-Gate (Wave A.3).

---

## Rationale

**Why not Option A alone?**
Deterministic lexical rules are brittle and domain-specific. They catch obvious opposites but miss magnitude, temporal, and subtle semantic contradictions. Relying solely on Option A would leave the adversarial lexical-overlap pairs (LO-07..LO-20) unaddressed, failing W1p5's core goal.

**Why start with Option B if available?**
Cross-encoders provide strong pairwise discrimination with deterministic local-only inference. The latency (~50–200 ms) is acceptable for cache-hit validation, and the model footprint (~1.4 GB) is manageable on modern dev workstations. Public benchmarks (MS MARCO) provide confidence in discrimination capability.

**Why fallback to Option C?**
If local CE is not cached (disk or VRAM constraints), Option C provides stronger discrimination than no veto at all. The cost/latency tradeoff is acceptable because the LLM-judge is escalation-only (not every hit). The rubric + JSON structured return provides fail-closed behavior (parse-fail = VETO).

**Why hybrid B+C is attractive:**
Layer 2 can be composite: cross-encoder for fast majority path, LLM-judge for edge cases where CE confidence is marginal or the query is action-sensitive. This gives defense-in-depth without paying LLM cost on every hit.

---

## Consequences

### Positive

- Semantic cache becomes safe for adversarial near-miss inputs (FP = 0 on hard negatives when veto is properly calibrated).
- Threshold can remain at 0.95 (no recall sacrifice on benign positives).
- Dataset remains intact (no removal of adversarial pairs).
- Architecture is inspectable: Layer 1 lexicon is human-readable; Layer 2 CE or LLM decisions are logged with full context.

### Negative / Risks

- **Latency**: Layer 2 adds 50–3000 ms per cache hit depending on path. Mitigated by Layer 1 pre-veto (fast path for obvious allows) and by calling Layer 2 only when necessary (escalation).
- **Complexity**: Two (or three) moving parts instead of one. Mitigated by Protocol abstraction (`VetoStage` interface) and comprehensive test coverage.
- **Calibration overhead**: CE and LLM both need per-environment calibration on the 100-pair dataset. Mitigated by deterministic split (60 train / 40 holdout) and automated probes.
- **Operational cost**: LLM-judge path incurs per-call cost or local GPU reservation. Mitigated by making it conditional on CE absence.

### Neutral

- `R1B_PRODUCTION_THRESHOLD_PROOF` remains `CALIBRATION_GAP` — W1p5 does not approve a threshold change; the existing ADR (`SEMCACHE-THRESH-001`) stays `PROPOSED_NOT_APPLIED`.
- `RTC-REQ-055` remains `PARTIAL` — the threshold proof is still a soft blocker.
- A new subclaim `R1B_SEMANTIC_CACHE_SAFETY_VETO_PROOF` is added; it can reach `PASS` when veto evidence shows FP=0.

---

## Implementation Phases (W1p5 Waves)

| Wave | Deliverable | Status |
|---|---|---|
| A.1 | This ADR document | ✅ |
| A.2 | Cross-encoder availability probe | 🔲 |
| A.3 | **Author-Gate: B-primary vs C-primary vs hybrid** | 🔲 |
| B | Veto Protocol contract + policy schema | 🔲 |
| C | Primary veto (B-track OR C-track per A.3) | 🔲 |
| D | Lexical pre-veto (Layer 1) | 🔲 |
| E | Evidence probes (veto, sweep_with_veto, veto_negatives) | 🔲 |
| F | Composer Rule 8 + new subclaim wiring | 🔲 |
| G | CI wiring + final verification | 🔲 |

---

## Related Documents

- Plan: `.windsurf/plans/rtc-w1-phase5-cache-safety-veto-e8a4d2.md`
- Parent ADR: `artifacts/certification/semantic_cache_threshold_adr.json` (`SEMCACHE-THRESH-001`)
- Dataset: `data/certification/calibration_pairs.json` (v2, 100 pairs, frozen)
- W1p4 sweep baseline: `artifacts/certification/threshold_sweep_results.json`

---

## Sign-Off (for Safety Reviewer)

| Role | Name | Date | Status |
|---|---|---|---|
| Safety Architect | ___ | ___ | ⬜ PENDING |
| ML Engineer | ___ | ___ | ⬜ PENDING |
| Product Owner | ___ | ___ | ⬜ PENDING |

**Acceptance criteria for sign-off**:
1. Veto probe evidence shows FP = 0 on hard negatives (`near_miss_negative`, `lexical_overlap_different_meaning_negative`, `policy_tenant_freshness_reuse_negative`) at threshold 0.95.
2. Positive recall is reported (not hidden) — per-threshold recall numbers are surfaced.
3. Composer Rule 8 is implemented and tested.
4. All anti-cheat invariants honored (no dataset mutation, no threshold change, no forced green).

---

**ADG snapshot**: `adg_indexed_20260430183000.sqlite`  
**Evidence bundle**: `artifacts/certification/semantic_cache_safety_veto_bundle.json` (produced by W1p5 Wave E probes)
