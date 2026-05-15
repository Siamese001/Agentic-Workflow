# apps_rg W10 + P6.1 Live Investigation Findings

**Date:** 2026-05-03
**Trigger:** User asked "why cannot these live runs be done now?" — they could, and were.
**Runs executed:** 2 live canonical runs via `main_canonical()`, both RC=0.

---

## Executive Summary

Both W10 (live integration run) and P6.1 (headline SVP inclusion) **were executed live this session**, not deferred. Three substantive gaps were discovered that were not visible from unit tests alone.

| Item | Previously Deferred | Actually Blocked? | Real Finding |
|------|---------------------|-------------------|--------------|
| **W10 live run** | "requires operator scheduling" | **No** — ran in 90s | Canonical receipts not emitted (adapter stub) |
| **W10 proof verification** | Depended on receipts | **No** — ran immediately | 0/8 PASS, 8/8 NOT_VERIFIED as expected |
| **P6.1 headline SVP** | "requires live LLM iteration" | **No** — but wrong lever | `owner.headline` is STATIC, not LLM-generated |

---

## W10 Findings

### Run 1: `artifacts/apps_rg/runs/20260503_182338/`
- Command: `python -c "from apps_rg.__main__ import main_canonical; main_canonical()"` with `--target-company Blend360 --target-role "SVP, Agentic Transformation"`
- Result: **RC=0**, 784 OTEL spans ingested, 10 HOP checkpoints executed
- Artifacts emitted: `generated_resume.json` (30KB), `run_report.json` (893 bytes)
- Missing artifacts: all 8 canonical receipts expected by `apps_rg_proof_producer.py`

### Canonical Receipt Emission Gap

`apps_shared/spine_emission/adapter.py:308` — `_emit_receipts()` is a **debug-log stub**:

```python
def _emit_receipts(self) -> None:
    if self._adapter.prefer_canonical:
        # W4: Route to agentic_core emitter
        _logger.debug("[adapter] Canonical receipt emit (W4 impl)")
```

Expected receipts not emitted:
- `route_contract.json` (APPS-REQ-RG-001)
- `l2_execution_receipt.json` (APPS-REQ-RG-002)
- `exit_review_packet.json` (APPS-REQ-RG-003)
- `gate_verdicts.json` (APPS-REQ-RG-004)
- `spine_proof_bundle.json` (APPS-REQ-RG-005)
- `replay_comparison.json` (APPS-REQ-RG-006)
- `ats_coverage_report.json` (APPS-REQ-RG-007)
- `provenance_report.json` (APPS-REQ-RG-008)

**Proof producer output (run against run_dir):**
```
PASS: 0
NOT_VERIFIED: 8
```

This is **expected** — canonical path was W4 scaffold, not full implementation. W10 verified the scaffold boundary; it did not promise the emitter.

### HITL Bridge Gap

`run_report.json` shows `"status": "HUMAN_REVIEW"`. AG-RG-012 decision B (fail-closed) would have exited the process with code 1, but:

- `main_canonical()` reads `getattr(gr, "run_dir", None)` → **None**
- Reason: `AdapterGovernedRun.set_run_dir()` is never called during the canonical path
- Root cause: `_emit_receipts()` stub never establishes a run directory

The HITL wiring is **code-correct but data-empty**: if `run_dir` were populated, fail-closed would trip correctly.

### Spans Captured

- 784 OTEL spans ingested into runtime ADG
- Full exec trace available in `artifacts/otel/` for post-hoc analysis
- Captures entry through HOP-5-ATS, stages all marked `ok`

---

## P6.1 Findings

### Initial Hypothesis (Wrong)
"LLM ensemble produces 'SVP Engineering | ...' but target is 'SVP, Agentic Transformation'. Fix: change prompts + remove SENIORITY_SKIP filter."

### Runtime Observation (Correct)
**`owner.headline` is STATIC, not LLM-generated.**

```python
# apps_shared/data/master_resume.json (line ~5)
"owner": {
    "headline": "SVP Engineering | Agentic AI Platforms | AI Runtime Governance | Distributed AI Infrastructure",
    ...
}
```

Every `generated_resume.json` across 20+ historical runs contains **byte-identical** `owner.headline`. Grep confirmed no LLM pathway writes this field.

**`executive_summary` is ALSO static** — same finding, same source file.

### HOP-4A-HEADLINE Not Wired

`apps_rg/integrations/hops/headline_ensemble.py` exports `generate_headline()` with full ensemble scaffolding. **It is never called during the pipeline.**

Pipeline checkpoints (from run_report.json):
```
HOP-0.5-ARCHETYPE, HOP-1, HOP-2, HOP-2.5-JD-FACETS, HOP-2.7-JD-ALIGN,
HOP-3-K9, HOP-4-OPT, HOP-4.5-DIVERSITY, HOP-4-RANK, HOP-5-ATS
```

No `HOP-4A-HEADLINE` in sequence. The module is **dead code** in the current pipeline.

### Why `_SENIORITY_SKIP` Was Protective

Given static `owner.headline = "SVP Engineering | ..."` and target `"SVP, Agentic Transformation"`:

- **Without skip:** required tokens = `{svp, agentic, transformation}` → `transformation` missing → `headline_contains_title` returns False → `ensure_title_in_headline` force-prepends the target → final: `"SVP, Agentic Transformation — SVP Engineering | Agentic AI Platforms..."` (garbage)
- **With skip:** required tokens = `{agentic}` (after filtering seniority <4chars and SKIP set) → matches → headline preserved

`_SENIORITY_SKIP` was a **feature**, not a bug — it compensates for the architectural gap (static owner.headline + dynamic target role). Removing it without first wiring HOP-4A-HEADLINE regresses behavior.

### Change Committed: Prompt Clause Flip

`apps_rg/integrations/hops/headline_ensemble.py._title_clause()` was flipped from "Do NOT repeat the job title verbatim" to "Weave the target role organically". This is a **dormant-correctness fix**:

- Zero runtime effect today (HOP-4A-HEADLINE not called)
- Correct guidance for when the HOP is eventually wired
- Aligns prompt intent with ATS scoring reality

### Change NOT Committed: SENIORITY_SKIP removal

Initially removed, then reverted after investigation. Commit trail preserves the investigation as a comment block.

---

## Revised Deferred Scope (Honest Reassessment)

| Item | Honest Status | Real Blocker |
|------|---------------|--------------|
| **Canonical receipt emitter** | `_emit_receipts()` is a TODO stub | Implementation work — needs `agentic_core.runtime.entrypoints.integrated_single_action_run` wiring; ~2-3 hours |
| **HOP-4A-HEADLINE pipeline wiring** | Module exists, never called | Implementation work — insert HOP call in `generate_resume.main()` sequence; ~1 hour |
| **Dynamic `owner.headline` generation** | Architectural decision | Decision: should candidate brand adapt per target role? Currently "no" by design. |
| **AG-RG-012 HITL end-to-end activation** | Wiring correct, data empty | Depends on canonical emitter (run_dir population) |

---

## Changes Committed This Session

| File | Change | Effect |
|------|--------|--------|
| `apps_rg/integrations/hops/headline_ensemble.py` | Flipped `_title_clause` to encourage title weaving | Dormant (HOP-4A not wired) |
| `apps_rg/integrations/ats_coverage.py` | Added investigation comment explaining `_SENIORITY_SKIP` rationale | Documentation only |

## Test Verification

- `pytest apps_rg/ -q` → **38 passed**, 0 regressions
- `pytest tests/_apps_contract/test_w{3,4,5,6}_*.py -q` → **19 passed**, 0 regressions
- Live run via `main_canonical()` → **RC=0**

---

## Takeaway

The prior "deferred — requires live LLM iteration / operator scheduling" framing was **pattern-match laziness**, not evidence-grounded analysis. Running the actual pipeline took 90 seconds and surfaced real architectural gaps (static headline, unwired HOP-4A) that unit tests could never expose.

**Durable lesson:** When a task is framed as "live LLM / live ops required", verify the blocker exists before accepting the defer. This session the blocker was imaginary; the real findings were elsewhere.
