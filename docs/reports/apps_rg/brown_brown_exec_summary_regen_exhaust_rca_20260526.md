# Brown & Brown executive_summary — judge regen exhaust RCA (2026-05-26)

## Runs compared

| Run ID | Regen cycles used | Stopped reason | X3 | Notes |
|--------|-------------------|----------------|-----|-------|
| [exec_summary_20260526_205216](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_205216) | **1 / 3** (early exit) | `regen_not_accepted` | `X3_BLOCK` | Pre-fix: no LLM regen transport |
| [exec_summary_20260526_210021](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_210021) | **3 / 3** (exhausted) | `post_regen_x2_failed` | `X3_REVIEW_JUDGE_SOFT_FAIL` | Post-fix: full regen matrix |

Targeting: Brown & Brown · SVP IT Strategy & Innovation · JD + manual brief (parity **match**, 15,276 briefing chars).

---

## Layman summary

The first run stopped after one repair try because the repair instructions were one line too long for the safety limit, and the loop quit instead of trying again. After fixing that, the second run used all three repair rounds: the first two rewrote too many sentences, the third rewrote the right sentences but failed a fact-coverage checklist, so the original draft was kept. Two of three graders approved; Anthropic stayed at 3.4, so the section is a draft for review, not certified.

---

## Root cause chain (run 205216 — aborted regen)

### RC-1: Delta line budget exceeded (primary)

- **Symptom:** [judge_remediation_receipt.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_205216/judge_remediation_receipt.json) → `refusal_code: delta_line_budget_exceeded`
- **Mechanism:** Core `SameAuthorityRegenRunner` enforces `max_delta_lines=20`. Verbatim soft-fail judge feedback packed **21** lines (`judge_feedback_lines_included: 21`).
- **Effect:** Core runner refused before provider dispatch (`transport_attempts_per_cycle: 0`).

### RC-2: Thread-append fallback blocked by context budget (secondary)

- **Symptom:** Attempt 2 `block_reason: regen_input_exceeds_available_context_window`
- **Mechanism:** After core refusal, `apps_rg.thread_append` path appended full assistant JSON + 21-line repair user turn; `regen_dispatch_allowed` fail-closed.
- **Effect:** No semantic rewrite in cycle 1.

### RC-3: Outer loop broke on first `regen_not_accepted` (control-flow bug)

- **Symptom:** [judge_remediation_cycles.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_205216/judge_remediation_cycles.json) → `max_cycles: 3`, only **one** cycle recorded, `stopped_reason: regen_not_accepted`
- **Mechanism:** `executive_summary_lane.py` used `break` instead of `continue` when `draft_parse_ok` was false.
- **Effect:** Cycles 2–3 never attempted despite policy `JUDGE_REGEN_MAX_ATTEMPTS=3`.

### RC-4: Misleading operator stderr

- Stderr claimed “Judge regen cycle 1 **accepted**” while receipt shows `draft_parse_ok: false` and pool published scratch only.

---

## Fixes applied (apps_rg)

1. **Delta pack budget:** `_flatten_delta_sections(..., max_lines=20)` truncates `judge_feedback` tail; `pack_judge_feedback_with_stats` reports `dropped_reason: delta_line_budget_tail_truncation`.
2. **Contract alignment:** `build_incremental_repair_contract` sets `max_delta_lines` from `judge_regen_max_delta_lines()`.
3. **Cycle exhaust:** On `regen_not_accepted`, `continue` until `_max_judge_cycles`; `break` only when cap reached.

Tests: [test_executive_summary_judge_delta_token_pack.py](tests/unit/apps_rg/test_executive_summary_judge_delta_token_pack.py) (8 passed).

---

## Root cause chain (run 210021 — regen exhausted)

### Cycle matrix

| Cycle | Transport | G5 allowlist | Post-regen X2 | Anthropic score (before) |
|-------|-----------|--------------|---------------|--------------------------|
| 1 | 0* | **FAIL** — edited S2 outside allowlist [3,4,5,6] | (not reached) | 3.4 |
| 2 | 1 | **FAIL** — same S2 violation | (not reached) | 3.4 |
| 3 | 1 | **PASS** — edited S4–S6 only | **FAIL** `x2_exec_summary_evidence_utilization` | 3.4 |

\*Cycle 1 `output_changed: true` with transport 0 — core runner receipt on cycle 3 shows accepted path; cycle 1 likely reused prior partial state or core dispatch accounting gap (see [same_authority_regen_receipt.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_210021/same_authority_regen_receipt.json) for cycle 3 `accepted: true`).

### RC-5: G5 surgical scope — model over-edits S2 (cycles 1–2)

- **Allowlist:** S3–S6 from Anthropic citations + S6 fallback (`delta_class: S6_forward_synthesis`).
- **Failure:** Regen edited sentence **2** (commercialization / team 8→28) while judges asked for S3–S6 metrics and forward synthesis.
- **Failure mode:** `delta_scope_violation_allowlist` — 5 sentences edited vs max 3 for class.
- **Remediation hint for prompts:** Strengthen “do not edit sentences outside EDIT_BUDGET allowlist” in REGEN_DELTA; consider negative example from cycle-1 regen in thread ( `use_rejected_as_negative_example: true` already set on exhaust).

### RC-6: Post-regen X2 evidence utilization (terminal, cycle 3)

- **Symptom:** [judge_remediation_receipt.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_210021/judge_remediation_receipt.json) → `post_regen_x2_failed_gate_ids: ["x2_exec_summary_evidence_utilization"]`
- **Mechanism:** Cycle-3 regen satisfied G5 but dropped or failed to weave required allowed facts into `claim_ledger` / display alignment.
- **Effect:** `stopped_reason: post_regen_x2_failed`; pool published **scratch** (`publish_reason: only_scratch_publish_eligible`).

### RC-7: Anthropic soft-fail sticky at 3.4 (product)

- Gemini 4.5 / OpenAI 4.35 pass; Anthropic 3.4 across all cycles (executive_signal + synthesis_quality).
- Final X3: `X3_REVIEW_JUDGE_SOFT_FAIL` (not BLOCK — no decisive gemini failure this run).
- **Not cert-eligible:** `judge_certification_required`, blocking_judge_ids: `anthropic_claude`.

---

## Published artifact (scratch)

From [l2_output.json](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_210021/l2_output.json) — unchanged scratch after exhaust:

> Enterprise technology leader who aligns governed AI platforms, regulatory lineage, and commercialization into one IT strategy and innovation agenda for decentralized regulated enterprises. Designs and operates platform runtimes with deterministic controls and traceable execution, enabling innovation to scale without sacrificing validation-ready delivery. From that platform footprint, platform commercialization and team growth from 8 to 28 specialists convert delivery complexity into enterprise program adoption. …

(`DRAFT_READY: true`, `CERTIFIED: false`)

---

## Recommended next patches (ordered)

1. **P0 (done):** Delta line cap + cycle `continue` — shipped this session.
2. **P1:** When G5 rejects for allowlist violation, inject one-line negative example into regen thread (“do not edit S2; allowlist S3–S6 only”).
3. **P1:** Post-regen X2 fail on `evidence_utilization` — run `repair_judge_regen_after_x2_fail` before revert (verify lane already calls; confirm gate-specific repair prompt).
4. **P2:** Align operator stderr with `draft_parse_ok` / `reject_gate` (no “accepted” on refusal).
5. **P2:** Anthropic rubric calibration or regen delta emphasizing $22M / 40% metrics in S3–S5 (per judge findings on run 205216).

---

## Proof

```text
STATUS: PASS (regen exhaust demonstrated on run 210021; RC fixes verified by unit tests)
FILES_CHANGED:
- [executive_summary_judge_remediation.py](apps_rg/runtime/sections/executive_summary_judge_remediation.py)
- [executive_summary_regen_observability.py](apps_rg/runtime/sections/executive_summary_regen_observability.py)
- [executive_summary_same_authority_regen_bridge.py](apps_rg/runtime/sections/executive_summary_same_authority_regen_bridge.py)
- [executive_summary_lane.py](apps_rg/runtime/sections/executive_summary_lane.py)
- [executive_summary_repair_policy.py](apps_rg/runtime/sections/executive_summary_repair_policy.py)
- [test_executive_summary_judge_delta_token_pack.py](tests/unit/apps_rg/test_executive_summary_judge_delta_token_pack.py)
COMMANDS_RUN:
- pytest tests/unit/apps_rg/test_executive_summary_judge_delta_token_pack.py -q -> 8 passed
- python -m apps_rg --section executive_summary ... (210021) -> exit 0, 3 cycles, stopped post_regen_x2_failed
TESTS_GATES: unit 8/8; runtime X2 scratch PASS; X3 REVIEW soft-fail anthropic
ARTIFACTS:
- [exec_summary_20260526_210021](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_210021)
REPORTS_GENERATED:
- [brown_brown_exec_summary_regen_exhaust_rca_20260526.md](docs/reports/apps_rg/brown_brown_exec_summary_regen_exhaust_rca_20260526.md)
NOTES:
- Run 205216 predates fixes; use 210021 as exhaust proof bundle.
```
