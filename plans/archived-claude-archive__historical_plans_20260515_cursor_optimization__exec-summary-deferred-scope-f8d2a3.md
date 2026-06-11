---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\exec-summary-deferred-scope-f8d2a3.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\exec-summary-deferred-scope-f8d2a3.md'
source_sha256: 861a281b076dc7b25d349f0a71daa2957101f6364116a1dbbceb3683601c12d6
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
description: Deferred scope from exec-summary-length-parity-remediation — future waves and generalizations
---

# Deferred Scope: Exec-Summary Remediation Follow-on Work

> Captured from `exec-summary-length-parity-remediation-a3c8e1` completion.
> Status: NOT IMPLEMENTED — saved for future prioritization.

---

## 1. Deferred Item: W2 vs W3 Decision Gate (AG-10)

**Original AG_QUEUE_SEED:** `ag-w2-or-w3`

**Context:** The original plan assumed W1 alone might not hit the ≥95% length_parity pass rate target. If W1 falls short, the choice is:
- **W2** (Tier B): Prompt-pattern bundle — XML structural slots, critique-and-revise loop, N=5 candidates
- **W3** (Tier C): Decoding-layer hard floor — vLLM min_tokens, generator routing override

**Current Status:** Both W2 and W3 were implemented in this session, so this decision gate is moot. However, the pattern is useful for future remediation work where we want to stage interventions by invasiveness.

**Future Applicability:** Save the decision rubric for other HOP remediations.

---

## 2. Deferred Item: Anthropic Claude Routing Approval (AG-10)

**Original AG_QUEUE_SEED:** `ag-tier-c-anthropic-routing`

**Context:** W3 implemented critical-hop routing that prefers Gemini Pro (not Anthropic) as the cloud fallback. The original plan envisioned Anthropic Claude as the primary cloud target.

**Rationale for Gemini over Anthropic:**
- Existing `GEMINI_PRO_MODEL_ID` already defined in model_registry.py
- No new API key management required
- Cost/reliability trade-off similar to Claude

**Future Work:** If Gemini Pro proves insufficient for exec_summary quality:
1. Add Anthropic routing tier to `CRITICAL_HOP_ROUTING`
2. Requires `ANTHROPIC_API_KEY` env var management
3. Update `get_critical_hop_generator()` to try Anthropic before Gemini

**Trigger Condition:** Gemini-based candidates show systematic quality issues (e.g., poor structural slot coverage, hallucinated outcomes) in production logs.

---

## 3. Deferred Item: Generalize to HOP-4A and HOP-4C (AG-10)

**Original AG_QUEUE_SEED:** `ag-generalize-other-hops`

**Context:** The sentence-count framing, XML slots, and repair mechanisms from exec_summary (HOP-4B) may benefit adjacent narrative hops:
- **HOP-4A** (Headline): One-line executive headline
- **HOP-4C** (Competencies): Technical/leadership competency bullets

**Why Deferred:**
- HOP-4B is the critical path (blocking run completion)
- HOP-4A and HOP-4C have different length constraints (shorter)
- Over-application of 4-sentence structure to 1-line headline would be inappropriate

**Future Work (Conditional):**
1. Audit HOP-4A and HOP-4C length_parity failure rates in production
2. If failure rate >15%, apply sentence-count framing
3. Adjust structural slot count (headline: 1 slot, competencies: 3-4 slots)
4. Reuse `_parse_exec_summary_xml()` pattern (rename to generic XML slot parser)

**Files to Touch:**
- `apps_rg/integrations/hops/headline_ensemble.py`
- `apps_rg/integrations/hops/competencies_ensemble.py`

---

## 4. Deferred Item: 10-Trial Benchmark (W5 Success Criteria)

**Original Success Criteria:**
> 10-trial benchmark: length_parity pass rate ≥95% on first round
> Latency Δ ≤ +12s on critical hop
> eval_harness_outcome ledger captures 10 rows with calibration metrics

**Status:** Infrastructure complete (71 tests pass), but production benchmark not executed.

**What Was Implemented:**
- All gate logic for quality enforcement
- Telemetry capture on Candidate dataclass
- vLLM hard floor for token-level enforcement
- N=5 ensemble for statistical robustness

**What Was NOT Executed:**
- 10 actual trial runs against live vLLM/Qwen
- Brown & Brown company brief (or other targets) test campaign
- Latency measurement under load
- eval_harness_outcome ledger population for this hop

**Future Work:**
1. Define benchmark script in `tools/apps_rg/benchmark_exec_summary.py`
2. Run 10 trials with fixed seed set
3. Record latency per trial
4. Emit eval_harness_outcome rows to ledger
5. Compute pass rate; if <95%, iterate on W1-W4

**Success Gate:**
- If pass rate ≥95%: declare remediation complete, archive this plan
- If pass rate 85-94%: tune temperature ladder or repair band
- If pass rate <85%: escalate to W6 (generator replacement)

---

## 5. Deferred Item: vLLM Tail Repetition Monitoring

**Risk from W3:** vLLM `min_tokens=140` hard floor can produce tail repetition (model forced to continue past natural EOS).

**Mitigations Implemented:**
- `repetition_penalty=1.15`
- `presence_penalty=0.4`
- `max_tokens=600` cap

**Monitoring Required:**
1. Track `repetition_detected` in scorecard telemetry
2. Define heuristic: same trigram appears ≥3 times in last 30 tokens
3. If repetition rate >5% in production: disable min_tokens, revert to W1+W2 stack

**Rollback Trigger:**
```python
if repetition_rate > 0.05:
    VLLM_HARD_FLOOR_PARAMS["hop_4b_exec_summary"]["min_tokens"] = None
```

---

## 6. Deferred Item: Post-Hoc Expansion Misalignment

**Risk from W1:** Repair band [80, 109] appends marquee_outcome sentence that may misalign with company facets.

**Current Mitigation:** Outcomes are from JD-aligned `marquee_outcomes` list; provenance traceable.

**Future Enhancement:**
- Weight outcomes by company facet similarity (cosine match)
- Prefer outcome that mentions same industry/technology as target company
- Requires: `company_facets` embedding + outcome embedding comparison

---

## 7. Summary: Decision Tree for Activating Deferred Work

| Item | Trigger Condition | Effort | Priority if Triggered |
|------|-------------------|--------|----------------------|
| W2 vs W3 | N/A (both done) | — | — |
| Anthropic routing | Gemini quality issues in prod | 4h | Medium |
| Generalize to HOP-4A/4C | >15% failure rate on those hops | 8h | Medium |
| 10-trial benchmark | Scheduled validation sprint | 6h | High |
| Tail repetition monitoring | >5% repetition rate in prod | 2h | High |
| Post-hoc alignment | User complaints on outcome relevance | 4h | Low |

---

## 8. References

- Source plan: `.windsurf/plans/exec-summary-length-parity-remediation-a3c8e1.md`
- Implementation commit: `1c284c04f0`
- Tests: `tests/_apps_contract/test_exec_summary_w1_length_parity_remediation.py`
- Success criteria: Notion Plans DB row (slug above)

---

## 9. Plan Registration

`PLAN_CREATED: slug=exec-summary-deferred-scope-f8d2a3 path=.windsurf/plans/exec-summary-deferred-scope-f8d2a3.md status=Not Started`
