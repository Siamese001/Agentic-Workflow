# ADG Packet Overflow Policy — C0 Bridge
**Stage 1 Design — No code changes**
**Date:** 2026-04-11 | Scope: Overflow actions, abstain/fail/refine semantics, and failure decision rules for C0-sourced packets

---

## 1. Executive Summary

Overflow and failure handling for the C0→PA bridge is a **two-stage gate**: the adapter gate (pre-shaping) and the budget gate (`apply_budget()` inside `_assemble()`). Each stage has its own decision tree. An additional pre-emission quality gate is defined for the bridge dispatcher. Together these three gates ensure that L2 never receives a packet with insufficient grounding, unresolved abstain signals, or budget-violated evidence blocks.

**Design law:** Emit the smallest packet that is fully grounded. Do not emit partial packets with concealed gaps. If in doubt, abstain.

---

## 2. Gate 1: Adapter Pre-shaping Gate

Executed by `c0_to_pa_adapter` before calling `shape_evidence()` or `_assemble()`.

### 2.1 Decision Tree

```
Receive C0EvidenceContract
    │
    ├── [A] abstain_hint == True?
    │       YES → ADAPTER_ABSTAIN immediately
    │       NO  → continue
    │
    ├── [B] len(cited_spans) == 0?
    │       YES → ADAPTER_ABSTAIN (empty spans)
    │       NO  → continue
    │
    ├── [C] All spans have relevance_score < 0.10?
    │       YES → ADAPTER_ABSTAIN (below minimum signal)
    │       NO  → continue
    │
    ├── [D] coverage_score < 0.30?
    │       YES → ADAPTER_ABSTAIN (below abstain threshold)
    │       NO  → continue
    │
    ├── [E] coverage_score >= 0.30 AND coverage_score < 0.50?
    │       YES → SET weak_support=True, add gap: "coverage_below_weak_threshold:0.50"
    │            → CONTINUE (partial coverage, do not abstain)
    │
    ├── [F] Prune spans below relevance_score < 0.30
    │       Log each pruned span as gap: "low_relevance_span:<span_id>"
    │
    ├── [G] Sort remaining spans by relevance_score DESC
    │       Apply source diversity cap: max 3 spans per source_ref
    │       Apply packet-specific span cap (15 for executive_summary, 20 otherwise)
    │
    └── PROCEED to shape_evidence() → _assemble()
```

### 2.2 ADAPTER_ABSTAIN Return

When any of conditions A–D fire, the adapter returns a pre-populated abstain bundle **without calling `shape_evidence()` or `_assemble()`**:

```python
EvidenceBundle(
    items=[],
    coverage_score=contract.coverage_score,
    contradiction_status="none",
    contradictions=[],
    gaps=["abstain_hint:<reason>"],
    freshness="<ISO-8601 UTC>",
    weak_support=True,
)
```

The dispatcher then builds a stub `PromptEnvelope` with:
- `assembly_result = "fail"`
- `abstain_instructions` = augmented with gap list
- All evidence blocks empty
- `replay_metadata` carries `abstain_hint=True`, `coverage_score=<value>`, `confidence_band="ABSTAIN"`

This stub envelope is **not written** to `artifacts/adg/packets/`.

---

## 3. Gate 2: `apply_budget()` Overflow Gate

Executed inside `_assemble()` by the existing `token_budgeter.apply_budget()` function.

### 3.1 Overflow Actions — Strict Priority Order

The following actions are applied in this strict priority order. Each action is tried first; if it produces a budget-compliant result, no further action is taken.

**Action 1: Trim low-support spans (NARROW)**

- Remove spans from the end of `must_use_evidence` list (lowest `relevance_score` first, due to adapter pre-sort)
- Continue trimming until within budget OR only 1 span remains
- Set `overflow_action = "narrow"`
- Populate `summary_note`: `"Evidence narrowed to top-N spans by relevance score. {N} spans retained."`
- Add gap: `"spans_trimmed_by_budget:<original_count>→<retained_count>"`

**Action 2: Summarize representative evidence (SUMMARIZE)**

- If after trimming to 1 span the budget is still exceeded (span itself is too long): truncate the span's `text_snippet` within `data` further (to 256 chars, then 128 chars)
- Set `overflow_action = "summarize"`
- Populate `summary_note`: `"Evidence summarized: text_snippet truncated to <N> chars."`
- Add gap: `"snippet_summarized:<span_id>"`

**Action 3: Narrow by source/layer (NARROW_SCOPE)**

- Not directly implemented in current `apply_budget()` — this is a **future improvement** (see §9)
- For current bridge: if Actions 1 and 2 fail to bring within budget, proceed to Action 4

**Action 4: Split into follow-on packet (SPLIT)**

- Current `apply_budget()` returns `overflow_action = "split"` but does not implement splitting
- For the bridge: when `overflow_action = "split"` is returned, the dispatcher must:
  1. Log `"split_required"` in `replay_metadata`
  2. Treat the current packet as partial (`assembly_result = "partial"`)
  3. Signal to L3 orchestration that a follow-on retrieval round is needed
  4. Write the partial packet to `artifacts/adg/packets/` with `assembly_result = "partial"` in the filename suffix
- This is a **forward-compatible design** — split handling is not fully implemented but the signal is well-defined

**Action 5: Abstain (ABSTAINED)**

- If `overflow_action = "abstained"` is returned by `apply_budget()` (budget cannot be met even with 1 span), treat identically to ADAPTER_ABSTAIN
- `assembly_result = "fail"`
- Do not write to `artifacts/adg/packets/`

### 3.2 Overflow Action Decision Table

| Condition | Overflow action | `assembly_result` | Write to disk? |
|-----------|---------------|--------------------|---------------|
| Within budget | `"none"` | `"pass"` | Yes |
| After narrow: within budget | `"narrow"` | `"partial"` | Yes |
| After summarize: within budget | `"summarize"` | `"partial"` | Yes |
| After all trims: still over budget, split required | `"split"` | `"partial"` | Yes (partial) |
| Budget cannot be met (abstained) | `"abstained"` | `"fail"` | No |

### 3.3 `assembly_result` → `evidence_contract_status` Mapping

| `evidence_contract_status` | `overflow_action` | `assembly_result` |
|---------------------------|------------------|------------------|
| `"complete"` (≥ 0.8) | `"none"` | `"pass"` |
| `"complete"` (≥ 0.8) | `"narrow"` or `"summarize"` | `"partial"` |
| `"partial"` (0.0–0.8) | `"none"` | `"partial"` |
| `"partial"` (0.0–0.8) | `"narrow"` or `"summarize"` | `"partial"` |
| `"partial"` (0.0–0.8) | `"split"` | `"partial"` |
| `"empty"` (= 0.0) | any | `"fail"` |
| any | `"abstained"` | `"fail"` |

The above is the **exact logic in `_assemble()` lines 89–103** — no change needed.

---

## 4. Gate 3: Bridge Dispatcher Pre-emission Quality Gate

Executed by the L3 dispatcher after `_assemble()` returns and before emitting the `PromptEnvelope` to L2.

### 4.1 Pre-emission checks

| Check | Condition | Action |
|-------|-----------|--------|
| Assembly result check | `assembly_result == "fail"` | Do not emit to L2; log failure; return abstain signal to caller |
| HMAC presence | `replay_metadata.get("evidence_hmac")` is None | Do not emit; this indicates bridge merger failed |
| Coverage sanity | `replay_metadata.get("coverage_score", 0) < 0.0` | Do not emit; invalid coverage signal |
| Contradiction overload | `len(envelope.contradiction_flags) > 4` | Truncate to 4 highest-severity; log suppression count in `replay_metadata` |
| Empty must-use evidence | `len(envelope.must_use_evidence) == 0` AND `assembly_result != "fail"` | This is a logic error — log as anomaly; downgrade to `"fail"` |

### 4.2 Emit or Abstain Decision

```
After _assemble() returns PromptEnvelope:
    │
    ├── assembly_result == "fail"?
    │       YES → Do not emit to L2 / do not write to disk
    │            → Return abstain signal to caller with gap list
    │            → STOP
    │
    ├── evidence_hmac missing?
    │       YES → Log bridge merger error
    │            → Downgrade to "fail" and STOP
    │
    ├── assembly_result == "partial"?
    │       YES → Emit to L2 WITH explicit partial signal
    │            → Write to disk with "_partial" suffix
    │            → Include refine_instructions with narrowing guidance
    │
    └── assembly_result == "pass"?
            YES → Emit to L2 normally
                 → Write to disk
```

---

## 5. Abstain / Fail / Refine Decision Rules

### 5.1 `abstain_hint` Handling

**Rule:** `abstain_hint=True` is a C0 retrieval decision. It must be honored unconditionally by the adapter. The adapter is the **exclusive** abstain gate — downstream components (shaper, budgeter, builder) must not override it.

**Propagation:** `abstain_hint=True` is placed in `replay_metadata` and must survive to L2 unchanged. L2 reads `abstain_hint` and routes to its own abstain behavior (out of scope for this design).

### 5.2 Low Coverage Behavior

| `coverage_score` | Behavior |
|-----------------|---------|
| `< 0.30` | Adapter abstain gate fires (Gate 1, condition D). No packet emitted. |
| `0.30 – 0.49` | `weak_support=True` set. Gap injected. `evidence_contract_status="partial"`. Packet emitted with explicit partial signal. |
| `0.50 – 0.79` | Normal operation. `evidence_contract_status="partial"`. Packet emitted. |
| `>= 0.80` | `evidence_contract_status="complete"`. Full pass if budget is within bounds. |

### 5.3 Weak Support Behavior

**Rule:** `weak_support=True` in the `EvidenceBundle` does **not** prevent packet emission — it adds the following to the envelope:

- `abstain_instructions` is augmented: `_assemble()` prepends gap list when `coverage < 0.3`. For `0.30 ≤ coverage < 0.50`, the adapter injects the gap string `"coverage_below_weak_threshold:0.50"` into `bundle.gaps` before calling `_assemble()`, which augments `abstain_instructions` via the existing gap-list interpolation.
- `assembly_result` is at most `"partial"` (never `"pass"` when `weak_support=True`)

**Additional rule:** If `median(relevance_scores) < 0.50` across all cited spans, the adapter sets `weak_support=True` regardless of `coverage_score`. This is bridge-specific behavior not in the existing shaper.

### 5.4 Contradiction Load Behavior

| Contradiction load | Behavior |
|-------------------|---------|
| 0 contradictions | Normal operation |
| 1–4 contradictions, severity `"minor"` | Include in `contradiction_flags`. `contradiction_status="minor"`. Emit with partial signal. |
| 1–4 contradictions, severity `"major"` | Include in `contradiction_flags`. `contradiction_status="major"`. Emit with partial signal. L2 must not act on contradicted evidence without explicit resolution. |
| > 4 contradictions (any severity) | Keep top-4 by severity. Log `"suppressed_contradiction_count": N` in `replay_metadata`. Emit with partial signal. |
| Contradictions make coverage_score < 0.30 | Trigger abstain gate anyway. Contradictions alone do not override the coverage threshold. |

**No existing mechanism in `_assemble()` routes directly to abstain based on contradiction load alone.** The bridge dispatcher does not introduce one. Contradiction load affects `contradiction_status` in `PromptAssemblyStatus` and L2 receives the signal — L2 decides whether to act.

### 5.5 Missing Required Fields

| Missing field | Behavior |
|--------------|---------|
| `retrieval_id` is None | Adapter must reject the contract before translation; log error; do not call `_assemble()` |
| `request_id` is None | Same |
| `evidence_hmac` is None | Same — the contract is unvalidated; do not trust it |
| `cited_spans` is None (not empty list) | Same — indicates contract construction failure |
| `coverage_score` is None | Same |
| `coverage_score` is `NaN` or outside `[0.0, 1.0]` | Treat as `0.0`; trigger adapter abstain gate |

**All required field checks are the adapter's responsibility.** The shaper and `_assemble()` assume well-formed `EvidenceItem` objects.

### 5.6 Refine vs. Abstain Decision

**Refine** is the correct action when:
- Evidence is present but insufficient in depth (`coverage_score 0.30–0.79`)
- Budget overflow required trimming but some evidence remains
- The task can be narrowed (different packet type, narrower scope, more focused retrieval)

**Abstain** is the correct action when:
- `abstain_hint=True` (C0 decision — override forbidden)
- `coverage_score < 0.30` (below minimum meaningful evidence)
- All spans below `relevance_score < 0.10` (no meaningful signal)
- Budget overflow resulted in `overflow_action="abstained"` (no evidence can fit)

**Refine instructions content for C0-sourced bundles:**
`_SHARED_REFINE` mentions ADG regeneration — this is irrelevant for C0 evidence. The dispatcher should inject C0-specific refine guidance into `task_block` context:
- "Request a narrower retrieval scope (specific file, module, or layer)"
- "Reduce the span count by tightening the relevance threshold"
- "Provide a more specific query string to the retrieval engine"

This guidance rides in the `task_block` (which the dispatcher controls) without modifying `_SHARED_REFINE`.

---

## 6. Packet-Family-Specific Boundedness Rules

### 6.1 `executive_summary` — Primary C0 Bridge Packet

- **Max spans:** 15
- **`must_use_evidence` budget:** 2,000 tokens
- **Boundedness rule:** If 15 spans × 128 tokens = 1,920 tokens, the packet is within budget with no overflow. If any span exceeds the 128-token average (due to longer snippets even after truncation), the budgeter trims from the end.
- **Overflow escalation:** narrow → summarize → partial emit → (abstain only if budget cannot fit even 1 span)
- **C0 bundle mismatch behavior:** `must_use_sources = ["snapshot", "burndown", "closure_report", "ratchet"]` — none will be in C0 items. `_compute_coverage()` returns `0.0 / 4 = 0.0` → `weak_support=True` → BUT coverage_score is set by bridge merger to `contract.coverage_score` AFTER shaping. The bridge merger ensures `bundle.coverage_score = contract.coverage_score` overrides the shaper's `0.0`. This is the correct behavior; no coverage undercount.
- **`assembly_result` guarantee:** `"pass"` or `"partial"` (never `"fail"` unless budget overflow abstains)

### 6.2 `graph_path_explanation` — Conditional C0 Bridge Packet

- **Max spans:** 20
- **`must_use_evidence` budget:** 4,000 tokens
- **Required extras:** `from_node` and `to_node` must be populated by the dispatcher in `replay_extras`
- **Boundedness rule:** If `graph=None` (no NetworkX graph loaded), `_assemble()` receives an error `EvidenceItem` in `must_items`. For C0 bridge: C0 spans replace the graph-sourced `must_items`. Error item is not injected when the bridge supplies its own items. Correct behavior.
- **Overflow escalation:** narrow → summarize → partial emit
- **C0 bridge condition:** Only route to this packet type when the request explicitly concerns a structural path (module A → module B violation) AND C0 retrieval returned path-relevant spans.

### 6.3 ADG-File-First Packets (All Others)

Packets `determinism_rca`, `p0_failure`, `ratchet_review`, `unknown_unresolved_triage`, `hotspot_investigation`, `infrastructure_boundary` are ADG-file-first.

**If a C0 bundle is routed to any of these:**
- `must_use_sources` for the packet will not match any C0 `source_type` values
- `_compute_coverage()` returns `0.0 / N = 0.0` for all N must-use sources
- Bridge merger sets `coverage_score = contract.coverage_score` (correct)
- If `contract.coverage_score >= 0.30`: packet emits as `"partial"` with `weak_support=True`
- If `contract.coverage_score < 0.30`: adapter abstain gate already prevented this path

**This means:** Routing a C0 bundle to an ADG-file-first packet type is not catastrophically wrong — it produces a partial packet with explicit weak-support and gap signals. However, it is semantically incorrect (a C0 span bundle is not a provenance report). The dispatcher must avoid this routing except as a deliberate diagnostic fallback.

**Safe fallback rule:** When in doubt, route to `executive_summary`. Never route to `determinism_rca` or `p0_failure` with C0-only evidence — these packets require structured violation records.

---

## 7. Confidence Band → Packet Selection Interaction

The `confidence_band` value (computed by bridge merger) should influence the dispatcher's packet type selection:

| `confidence_band` | Recommended packet type | Overflow stance |
|-------------------|------------------------|-----------------|
| `"HIGH"` (≥ 0.80, no weak_support) | Any applicable type | Normal — no extra restrictions |
| `"MEDIUM"` (0.50–0.79) | `executive_summary` preferred; `graph_path_explanation` if path-specific | Tolerate `"partial"` result |
| `"LOW"` (0.30–0.49, weak_support) | `executive_summary` only | Emit with explicit partial signal; L2 must see refine instructions |
| `"ABSTAIN"` (< 0.30 or abstain_hint) | No packet | Return abstain signal to caller |

---

## 8. Optional Future Improvements (Separated from Baseline)

These are design extensions that do not affect the current bridge baseline:

| Improvement | Description | Prerequisites |
|------------|-------------|--------------|
| **Narrow-by-source overflow action** | Extend `apply_budget()` to filter C0 spans by `source_ref` pattern (e.g., keep only spans from the most relevant file) | Future iteration; requires budgeter change |
| **Split packet sequencing** | Implement the `"split"` overflow action — produce two packets from one over-budget bundle, with part 1 and part 2 `span_range` in `replay_metadata` | Future iteration; requires dispatcher support |
| **Adaptive span cap** | Compute the span cap dynamically from `template.token_budget.must_use_evidence / 128` rather than using fixed per-type caps | Removes hardcoded values; safer as budgets evolve |
| **Contradiction-driven abstain** | If contradiction load exceeds N major flags, auto-abstain regardless of coverage | Only if L2 evidence shows contradiction overload produces bad outputs |
| **`relevance_score` stratification in budgeter** | Extend `_severity_key()` in `token_budgeter.py` to use `data.get("relevance_score")` for C0 items, enabling the budgeter to trim independently of adapter pre-sort | Cleaner separation; minor additive change |
| **Replay HMAC verification gate** | CI gate that checks all packets in `artifacts/adg/packets/` carry `evidence_hmac` and verifies it is valid | E21 phase; separate gate module |

---

## 9. Risks and Mitigations

| Risk | Severity | Mitigation |
|------|---------|-----------|
| Bridge merger `coverage_score` override does not fire before `_assemble()` | HIGH | Bridge merger runs AFTER `shape_evidence()` returns; `_assemble()` receives raw bundle; merger post-processes. Design must be: adapter calls `shape_evidence()` → merger patches → then calls `_assemble()` with the patched bundle. **But:** `_assemble()` calls `shape_evidence()` internally. **Resolution:** Adapter must call `shape_evidence()` and `_assemble()` in separate calls. Or `_assemble()` must accept a pre-shaped bundle. This is the **most critical implementation risk** — `_assemble()` currently calls `shape_evidence()` internally and there is no way to pass a pre-shaped bundle. |
| `abstain_hint=True` bypassed by ADG-file-first packet routing | HIGH | Dispatcher must check `replay_extras["abstain_hint"]` before selecting a packet type |
| `evidence_hmac` dropped during `replay` dict construction | MEDIUM | Confirmed non-collision between existing `replay` keys and C0 extras; `replay.update(replay_extras)` preserves HMAC |
| `overflow_action="split"` causes dispatcher to emit a split packet without implementing part-2 follow-on | MEDIUM | Document: if `overflow_action="split"`, treat as `"partial"`, log split signal, do not attempt part-2 in initial implementation |
| Adapter pre-sort does not match budgeter's trim order (trim from list end) | LOW | Confirmed: `apply_budget()` pops from the end; adapter sorts descending by `relevance_score` → lowest at end → trimmed first |

### Critical Risk Resolution: `_assemble()` Internal `shape_evidence()` Call

**Problem:** `_assemble()` at line 57 calls `shape_evidence(all_items, must_use_sources=template.must_use_sources)` internally. The bridge merger needs to patch the bundle **after** shaping. There is no way to pass a pre-shaped bundle to `_assemble()`.

**Resolution options (design, not code):**

**Option A (recommended):** The bridge does not call `_assemble()` directly. Instead:
1. Adapter calls `shape_evidence(items, must_use_sources=[])` directly and gets `EvidenceBundle`
2. Bridge merger patches `bundle.coverage_score`, merges contradictions, gaps, computes `confidence_band`
3. Bridge builds the `PromptEnvelope` manually using the same field structure as `_assemble()`, but with the patched bundle

This makes the bridge a partial re-implementation of `_assemble()`. Not ideal — duplication risk.

**Option B:** Accept that `_assemble()` re-runs shaping on the adapter-provided items. The bridge merger must run **after `_assemble()` returns** and patch `PromptEnvelope.replay_metadata` and `assembly_status.replay_metadata` directly.

The key insight: `coverage_score` in the output `PromptEnvelope` appears in two places:
- `PromptEnvelope.replay_metadata["coverage_score"]` — comes from `replay_extras` (bridge supplies correct value)
- `PromptAssemblyStatus.evidence_contract_status` — derived from `bundle.coverage_score` inside `_assemble()`

For `evidence_contract_status`, the shaper's incorrect `coverage_score` (from `_compute_coverage` with `must_use_sources=template.must_use_sources`) will produce a lower value than C0's actual coverage. This may cause `evidence_contract_status = "empty"` when C0's `coverage_score >= 0.30`.

**Recommended resolution for initial implementation:** The bridge dispatcher passes `must_use_sources=[]` equivalent by supplying C0 `source_type` values that match the packet's `must_use_sources` list. Specifically: the adapter sets `source_type` to match one of the packet's `must_use_sources` strings. For `executive_summary`, this means setting `source_type="json_report"` (which is in the packet's coverage-check domain) and treating one C0 item as a `"snapshot"` proxy. This is a pragmatic interim — the `evidence_contract_status` then reflects partial coverage from C0 sources, which is correct.

**This risk is the primary design issue for initial implementation and must be resolved before coding begins.**

---

## 10. Assumptions and Uncertainties

| Item | Status |
|------|--------|
| `_assemble()` calls `shape_evidence()` internally — bridge cannot pass pre-shaped bundle | **Confirmed** — critical risk documented above |
| `apply_budget()` trims `must_use_evidence` from end of list | **Confirmed** |
| `overflow_action="split"` is returned but not implemented in current `apply_budget()` | **Confirmed** |
| Bridge merger coverage override can be done via `replay_extras["coverage_score"]` | **Confirmed** — this puts correct value in `replay_metadata` but not in `evidence_contract_status` |
| `abstain_hint=True` in `replay_metadata` is the authoritative signal for L2 | **Architectural assumption** — L2 contract is out of scope |
| `_SHARED_REFINE` ADG regeneration guidance is irrelevant for C0 bundles but not harmful | **Confirmed** — refine fires only when coverage insufficient |
