---
plan_id: askq-confidence-meta-learning-loop-c4e7a1
plan_format: v2
plan_type: governance
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
supersedes: []
---

# AskUserQuestion Confidence Meta-Learning Loop — Close the Open Loop

Wire the existing (but unconnected) `ask_user_question_decisions` ledger so that every native `AskUserQuestion` call persists its options + confidence + the user's actual selection to SQLite, and so future `AskUserQuestion` confidence levels are informed by that history (precedent-calibrated confidence).

> **plan_id discipline**: `plan_id: askq-confidence-meta-learning-loop-c4e7a1` matches the filename stem. Wave markers use `plan=askq-confidence-meta-learning-loop-c4e7a1`.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W0
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-06-14

---

## Context (SCQA)

- **Situation** — A full `ask_user_question_decisions` ledger subsystem already exists: a SQLite schema with `confidence_score`, `confidence_source`, `recommended_index`, `selected_index`, `context`, `packet_json` ([ask_user_question_ledger.py](tools/ledgers/ask_user_question_ledger.py) + [ask_user_question_ledger.schema.sql](.codex/schemas/ask_user_question_ledger.schema.sql)); a precedent-read consulter that computes `acceptance_rate` / `override_rate` / `avg_confidence` ([AskUserQuestionConsulter in consulter.py](tools/ledgers/consulter.py)); a telemetry dashboard ([telemetry_dashboard.py](tools/ledgers/telemetry_dashboard.py)); a weekly calibration report ([ask_user_question_weekly_report.py](ops_scripts/calibration/ask_user_question_weekly_report.py)); and green tests for the full read/write/consult pipeline ([test_ask_user_question_shadow_loop.py](tests/unit/ledgers/test_ask_user_question_shadow_loop.py), [test_ask_user_question_consulter.py](tests/unit/ledgers/test_ask_user_question_consulter.py)). The live native-tool path has one hook today — the PreToolUse SHAPE gate [pre_ask_user_question_recommendation_gate.py](.codex/governance/scripts/pre_ask_user_question_recommendation_gate.py) (via [before_ask_user_question.py](.codex/hooks/before_ask_user_question.py)), which enforces that a recommended option carries a `[confidence=0.NN]` signal.
- **Complication** — The loop is **open, not closed**. ADG fan-in is **0** for both `tools/ledgers/ask_user_question_ledger.py` (module id 11598) and the packet builder `tools/decisions/enriched_choice_builder.py` (module id 11289): no live (non-test) code imports them. Three seams are broken: (1) **no live WRITE** — the PreToolUse gate validates shape but never calls `write_decision`, so firing AskUserQuestion persists nothing; (2) **no SELECTION capture** — [hooks.json](.codex/hooks.json) has **no `PostToolUse` matcher for `AskUserQuestion`**, so the user's chosen option is never read and `selected_index` is only ever set in tests; (3) **no CONSULT** — nothing in the authoring path calls `AskUserQuestionConsulter` to bias a new question's confidence on prior acceptance/override. The dashboard + weekly report run over an empty table. The scaffolding was built for the retired Author-Gate `ASK_USER_QUESTION_PACKET` pipeline (ADR-093 / `claude-native-supersession-9d3f7a`), whose builder now has 0 callers, and was never reconnected to the native tool.
- **Question** — How do we close the meta-learning loop so AskUserQuestion confidence is recorded against the user's real selections and those records calibrate future confidence — reusing the existing ledger/consulter, not rebuilding it?
- **Answer** — Add the two missing live seams (a PostToolUse capture hook + a consult/calibration step), reusing every existing component. One atomic PostToolUse hook writes both the question's options+confidence and the user's selection (it receives `tool_input` and `tool_response` together); a calibration helper + skill step feeds prior acceptance back into the confidence the model states; the existing dashboard/weekly report then have real data and prove closure.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1, W1.2 | Probe PostToolUse payload + close WRITE+SELECTION seam (the critical gap) | ~45K | Claude Code emits a `PostToolUse` event for `AskUserQuestion` whose `tool_response` exposes the selected option(s) | 🔲 TODO | A real AskUserQuestion call writes one `ask_user_question_decisions` row with `recommended_index`, `selected_index`, and `confidence_score` populated from live data |
| W2 | W2.1, W2.2 | Close the CONSULT seam — prior acceptance calibrates future confidence | ~40K | ≥1 context accumulates ≥N decisions; `loop_metrics.py` Wilson CI reusable | 🔲 TODO | Consulter returns nonzero `acceptance_rate` for a populated context; calibration helper emits a precedent-adjusted confidence suggestion; authoring skill documents the consult step |
| W3 | W3.1, W3.2 | Calibration reporting, closure proof, wiring health gate, writeback | ~35K | W1+W2 landed; weekly report + dashboard read the live table | 🔲 TODO | End-to-end proof (fire → write → consult → weekly report reflects it); CI health check confirms the PostToolUse hook is registered + ledger writable; memory/ADR/Notion updated |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Probe & confirm the AskUserQuestion PostToolUse payload shape | 🔲 TODO |
| W1.2 | `after_ask_user_question.py` capture hook → `write_decision` + hooks.json registration | 🔲 TODO |
| W2.1 | `ask_user_question_calibration.py` — empirical acceptance → calibrated-confidence suggestion | 🔲 TODO |
| W2.2 | Wire consult into authoring path (skill step + advisory calibration note in the PreToolUse gate) | 🔲 TODO |
| W3.1 | Per-context calibration curve in weekly report + loop-wiring health check | 🔲 TODO |
| W3.2 | Closure tests, memory writeback, ADR note, Notion registration | 🔲 TODO |

---

## Out Of Scope

- Migrating the `ask_user_question_decisions` table to the canonical intelligence-ledger family schema (`events`/`event_scope`/`events_fts` via `emit_ledger_event`). The existing dedicated table + `AskUserQuestionConsulter` already fit; migration is a larger, separate blast radius. See Decision Log D-2.
- Reviving the retired Author-Gate packet builder (`tools/decisions/enriched_choice_builder.py`) or any `ASK_USER_QUESTION_PACKET` marker flow (ADR-093 retired it). The native tool is the only entry point.
- Auto-blocking on a confidence/empirical-acceptance divergence. Calibration feedback is advisory in this plan (the model still authors the number); hard enforcement is a possible follow-up only after data accrues.
- Changing the PreToolUse shape gate's existing block semantics (recommendation-without-confidence still blocks by default — unchanged).

---

## Wave 1 — Probe + Close the WRITE+SELECTION Seam

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Authorization**: NOT_REQUIRED — additive new hook + hooks.json registration; no shared runtime contract weakened.

**Phases**:
- **W1.1** — Probe & confirm the AskUserQuestion PostToolUse payload shape | ~15K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.2** — `after_ask_user_question.py` capture hook → `write_decision` + hooks.json registration | ~30K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- A temporary logging hook captures one real `AskUserQuestion` PostToolUse payload to an artifact; the selected option index/label is located in `tool_response` (or the precise shape is documented and the capture logic adapted to it).
- After W1.2, firing a real `AskUserQuestion` results in exactly one new row in `ask_user_question_decisions` with `question`, `option_count`, `recommended_index`, `selected_index`, `confidence_score`, `confidence_source`, and `context` populated from the live call (verified via `python -m tools.ledgers.ask_user_question_ledger --list`).

---

## Wave 2 — Close the CONSULT Seam (Inform Future Confidence)

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Phases**:
- **W2.1** — `ask_user_question_calibration.py` — empirical acceptance → calibrated-confidence suggestion | ~20K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.2** — Wire consult into authoring path (skill step + advisory calibration note in the PreToolUse gate) | ~20K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- `AskUserQuestionConsulter.lookup(context=...)` returns nonzero `acceptance_rate`/`avg_confidence` once the table is populated (W1 data).
- A new `tools/ledgers/ask_user_question_calibration.py` maps `(context, stated_confidence)` → empirical acceptance with a Wilson lower bound (reusing [loop_metrics.py](tools/calibration/loop_metrics.py)) and returns a `calibrated_confidence` suggestion + sample size.
- The [ask-user-question-recommendation skill](.codex/skills/ask-user-question-recommendation/SKILL.md) procedure documents: "consult precedent for this context, then state confidence calibrated to prior acceptance."
- The PreToolUse gate surfaces an **advisory** stderr note when stated confidence diverges sharply from empirical acceptance for the context (never blocks on this; existing block semantics unchanged).

---

## Wave 3 — Calibration Reporting + Closure Proof + Governance

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Phases**:
- **W3.1** — Per-context calibration curve in weekly report + loop-wiring health check | ~20K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.2** — Closure tests, memory writeback, ADR note, Notion registration | ~15K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- The weekly report ([ask_user_question_weekly_report.py](ops_scripts/calibration/ask_user_question_weekly_report.py)) renders a per-context curve of stated confidence vs empirical acceptance over the live table.
- A health check (`ops_scripts/ci/check_ask_user_question_loop_wired.py`) asserts the `PostToolUse` `AskUserQuestion` hook is registered in hooks.json and the ledger path is writable; advisory by default.
- An end-to-end test extends [test_ask_user_question_shadow_loop.py](tests/unit/ledgers/test_ask_user_question_shadow_loop.py) to drive the **actual capture hook** with a synthetic PostToolUse payload and assert a row lands with correct `selected_index`.
- Memory entity + ADR note + Notion Plans row recorded.

---

## Execution Details

### W1.1 — Probe & confirm the AskUserQuestion PostToolUse payload shape
**Scope**: Determine exactly how Claude Code surfaces the user's selection so the capture hook reads the right field. This is the one true unknown (graded DERIVED until observed).

**Commands**:
```bash
# 1. Add a temporary PostToolUse:AskUserQuestion hook that dumps stdin to an artifact, register it.
# 2. Fire one real AskUserQuestion (this plan's own review can serve), then:
python -c "import json,pathlib;print(pathlib.Path('artifacts/governance/auq_payload_probe.jsonl').read_text())"
# 3. Document the shape (tool_input.questions[*].options, tool_response selected option/index) in the plan; remove the probe hook.
```

### W1.2 — `after_ask_user_question.py` capture hook → `write_decision`
**Scope**: Single atomic PostToolUse hook (`.codex/hooks/after_ask_user_question.py` → testable SSOT `.codex/governance/scripts/post_ask_user_question_capture.py`). Parse `tool_input` (question text, option labels, `(Recommended)` position → `recommended_index`, `[confidence=0.NN]` from the recommended option's description → `confidence_score` + `confidence_source="explicit"`), parse `tool_response` for the selected option(s) → `selected_index`, derive `context` from the question header, then call `tools.ledgers.ask_user_question_ledger.write_decision(...)`. Fail-soft (a capture error must never wedge a turn). Register a `PostToolUse` block with `matcher: "AskUserQuestion"` in [hooks.json](.codex/hooks.json).

**Commands**:
```bash
python -m pytest tests/unit/ops_scripts/hooks/codex/test_post_ask_user_question_capture.py -q
python -m tools.ledgers.ask_user_question_ledger --list   # row present after a live call
```

### W2.1 — `ask_user_question_calibration.py`
**Scope**: `lookup_calibrated_confidence(context, stated_confidence)` → reads `AskUserQuestionConsulter`, computes empirical acceptance with Wilson lower bound via [loop_metrics.py](tools/calibration/loop_metrics.py), returns `{empirical_acceptance, wilson_lower, n, calibrated_confidence, signal: strong|suggestive|none}`. Pure-read, stdlib + existing helper only.

**Commands**:
```bash
python -m pytest tests/unit/ledgers/test_ask_user_question_calibration.py -q
```

### W2.2 — Wire the consult into the authoring path
**Scope**: Update the [ask-user-question-recommendation skill](.codex/skills/ask-user-question-recommendation/SKILL.md) to add a "consult precedent first" step; add an **advisory** divergence note to [pre_ask_user_question_recommendation_gate.py](.codex/governance/scripts/pre_ask_user_question_recommendation_gate.py) (`question_findings` gains a soft `advisory` finding when `|stated − empirical|` is large for the context). No change to block semantics.

**Commands**:
```bash
python -m pytest tests/unit/ops_scripts/hooks/codex/test_pre_ask_user_question_recommendation_gate.py -q
```

### W3.1 — Reporting + wiring health check
**Scope**: Extend the weekly report with a per-context confidence-vs-acceptance curve; add `ops_scripts/ci/check_ask_user_question_loop_wired.py` (PostToolUse hook registered + ledger writable). Register the CI check (advisory) in `run_contract_gates.py`.

**Commands**:
```bash
python ops_scripts/calibration/ask_user_question_weekly_report.py
python ops_scripts/ci/check_ask_user_question_loop_wired.py
```

### W3.2 — Closure tests + writeback + Notion
**Scope**: Hook-driven end-to-end test; memory entity `askq-confidence-meta-learning-loop`; short ADR note; Notion Plans row sync.

**Commands**:
```bash
python -m pytest tests/unit/ledgers/test_ask_user_question_shadow_loop.py -q
python ops_scripts/ci/run_contract_gates.py
```

---

## Gap Register

**GAP-1: No live WRITE on the native AskUserQuestion path.**
- `write_decision` ([ask_user_question_ledger.py:118](tools/ledgers/ask_user_question_ledger.py)) has **0 import fan-in** (ADG snapshot 06132026_2227, module id 11598). The PreToolUse gate validates shape only; nothing persists the question/options/confidence.
- Impact: every AskUserQuestion records nothing → the ledger stays empty → dashboard + weekly report describe an empty table.

**GAP-2: No SELECTION capture.**
- [hooks.json](.codex/hooks.json) has no `PostToolUse` matcher for `AskUserQuestion` (PostToolUse only matches `Edit|Write|MultiEdit|NotebookEdit`). The chosen option is never read; `selected_index` is set only in tests.
- Impact: the core learning signal (recommended vs selected → acceptance/override) is never captured live, so confidence can never be calibrated against reality.

**GAP-3: No CONSULT to inform future confidence.**
- The authoring path never calls `AskUserQuestionConsulter` ([consulter.py:235](tools/ledgers/consulter.py)). The stated `[confidence=0.NN]` is a fresh heuristic each time.
- Impact: no meta-learning — past outcomes do not change future confidence even if the table were populated.

---

## Definition of Done

DoD-1: A live `AskUserQuestion` call persists one fully-populated `ask_user_question_decisions` row (the WRITE+SELECTION seam is closed).
- Evidence: `python -m tools.ledgers.ask_user_question_ledger --list` shows a row with non-null `recommended_index`, `selected_index`, `confidence_score` after a real call.
- Status: TODO

DoD-2: Smoke-run of the capture + report surfaces exits 0.
- Evidence: `python ops_scripts/calibration/ask_user_question_weekly_report.py` exits 0 and renders the per-context curve; `python ops_scripts/ci/check_ask_user_question_loop_wired.py` exits 0.
- Status: TODO

DoD-3: Consult/calibration returns a precedent-adjusted confidence from real data with zero regressions.
- Evidence: `python -m pytest tests/unit/ledgers/test_ask_user_question_calibration.py tests/unit/ledgers/test_ask_user_question_consulter.py tests/unit/ledgers/test_ask_user_question_shadow_loop.py -q` → all pass, 0 fail.
- Status: TODO

DoD-4: CI gates green / no new violations.
- Evidence: `python ops_scripts/ci/run_contract_gates.py` exits 0 (modulo the documented pre-existing apps_rg infra-wiring red on main, unrelated to this plan).
- Status: TODO

DoD-5: Documentation + memory writeback.
- Evidence: memory entity `askq-confidence-meta-learning-loop` written; ADR note added; [ask-user-question-recommendation skill](.codex/skills/ask-user-question-recommendation/SKILL.md) documents the consult step; Notion Plans row synced.
- Status: TODO

DoD-6: Hook-driven closure test proves the live path (not just direct API calls).
- Evidence: the extended `test_ask_user_question_shadow_loop.py` drives `post_ask_user_question_capture` with a synthetic PostToolUse payload and asserts the row + `selected_index`.
- Status: TODO

---

## Scope Expansion Authorization

When scope is discovered during execution, emit markers in order:

```
DISCOVERED_SCOPE: plan=askq-confidence-meta-learning-loop-c4e7a1 wave=<N> phase=<M> gap="<what>" impact="<severity>"
AUTHORIZATION_DECISION: plan=askq-confidence-meta-learning-loop-c4e7a1 decision=<ACCEPTED|DEFERRED|SPLIT_TO_NEW_PLAN|REJECTED> authorized_by=<user|author_gate|self> decisive_reason="<why>"
SCOPE_EXPANSION: plan=askq-confidence-meta-learning-loop-c4e7a1 reason="<summary>" added="<waves/phases>" authorized="yes"
```

---

## Decision Log

**D-1 — Capture mechanism: single PostToolUse hook (RECOMMENDED) vs PreToolUse-write + PostToolUse-correlate vs self-report marker.**
- Chosen: **single PostToolUse hook**. The `PostToolUse` event carries both `tool_input` (options + confidence) and `tool_response` (selection) together, so one atomic write needs no correlation key and no pending row. The PreToolUse gate stays shape-only. Alternatives rejected: PreToolUse-write + PostToolUse-update needs a fragile decision_id correlation across two events; a self-report `DECISION_SELECTED:` marker is brittle and re-introduces the retired marker pattern. (Confirmed feasible by W1.1 probe; if the PostToolUse payload does not expose the selection, fall back to PreToolUse-write + a Stop-hook selection scan — recorded as the W1.1 contingency.)

**D-2 — Store: reuse `ask_user_question_decisions` table (RECOMMENDED) vs migrate to canonical events-table ledger family.**
- Chosen: **reuse**. The dedicated table already has the exact columns and a working `AskUserQuestionConsulter`; migration to `events`/`events_fts` is a larger blast radius for no immediate gain. Migration is captured in Out Of Scope as a possible later consolidation.

**D-3 — Calibration feedback: advisory (RECOMMENDED) vs blocking.**
- Chosen: **advisory** for this plan. Hard-blocking on confidence/acceptance divergence requires accrued data and a calibrated threshold; start by surfacing the signal and documenting the consult step, leaving enforcement as a data-gated follow-up.

---

## Supersedes

| Predecessor slug | Reason |
|---|---|
| — | — |

_None — net-new plan._

---

## Marker Quick Reference

```
WAVE_START: plan=askq-confidence-meta-learning-loop-c4e7a1 wave=<N>
WAVE_COMPLETE: plan=askq-confidence-meta-learning-loop-c4e7a1 wave=<N> note="+N tests, N files, scope=<summary>"
PHASE_COMPLETE: plan=askq-confidence-meta-learning-loop-c4e7a1 phase=<W1.1>
PLAN_COMPLETE: plan=askq-confidence-meta-learning-loop-c4e7a1 note="<final outcome>"
```
