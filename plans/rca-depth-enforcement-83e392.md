---
plan_id: rca-depth-enforcement-83e392
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

# Root-Cause-Analysis Depth Enforcement

Make the refactor-turn Layered-RCA audit reject shallow diagnoses — a root cause asserted without stated confidence or a next step decoupled from it — and then promote the check from advisory to a blocking Stop-gate.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: IN_PROGRESS
CURRENT_WAVE: W2
LAST_COMPLETED_WAVE: W1
LAST_UPDATED: 2026-06-14

---

## Context (SCQA)

- **Situation** — `post_agent_runtime_rca_audit.py` (constitutional §37) grades refactor-turn RCAs for descent depth, symptom≠root, and failing-layer isolation, logging `shallow_rca` to `artifacts/governance/runtime_rca_violations.jsonl`.
- **Complication** — The frame's own `Confidence / unknowns:` line and the `Next` step were never checked: a frame could dig deep, assert a root cause with zero stated confidence, and end with "fix the bug" — and pass. "High confidence" was implied, never proven; the next step was not bound to the diagnosis.
- **Question** — How do we ensure a reported root cause AND its next steps reflect enough layers of analysis to claim high confidence, and make that enforceable rather than advisory?
- **Answer** — Add two high-precision `shallow_rca` triggers (W1, done), then promote the detector from advisory-log to a shadow→block Stop-gate on the highest-confidence case (W2).

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1, W1.2 | Strengthen shallow_rca: require stated confidence + diagnosis-coupled next step | ~8K | Detector stays advisory/fail-open; regex matchers high-precision | ✅ DONE | Two new triggers fire in isolation; 22 tests pass; no regressions |
| W2 | W2.1, W2.2 | Promote to a narrow shadow→block Stop-gate per the options doc | ~14K | Stop-block lever proven by stop_task_audit.py; shadow period first | 🔲 TODO | warn-mode never blocks; block-mode forces re-compose on a frameless edit-turn; loop-guarded |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Add missing_confidence + next_step_generic triggers | ✅ DONE |
| W1.2 | Isolating tests + positive control | ✅ DONE |
| W2.1 | New blocking Stop hook (reuse detect(); RUNTIME_RCA_ENFORCE=off/warn/block) | 🔲 TODO |
| W2.2 | Register in settings.json; shadow rollout then flip to block | 🔲 TODO |

---

## Out Of Scope

- The pre-existing `apps_rg` infra-wiring and ADG-manifest CI failures (unrelated to this work; their own concern).
- Rewriting the rule text in `001-runtime-seam-execution.md` — it already describes the confidence + next-step requirements; the detector now enforces them.

---

## Wave 1 — Strengthen the depth audit

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Authorization**: NOT_REQUIRED — advisory governance hook, no shared runtime surface.

**Phases**:
- **W1.1** — Add `missing_confidence` + `next_step_generic` triggers | ~5K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.2** — Isolating tests + full-contract positive control | ~3K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- A deep frame with no `Confidence` line is flagged `shallow_rca` (missing_confidence).
- A deep frame whose next step is a bare platitude is flagged (next_step_generic).
- The full-contract frame stays clean; suite green.

---

## Wave 2 — Promote to a blocking Stop-gate

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Phases**:
- **W2.1** — New `.claude/hooks/post_agent_runtime_rca_gate.py` reusing `detect()`; modes `RUNTIME_RCA_ENFORCE=off|warn|block`; per-session loop guard | ~9K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.2** — Register in `.claude/settings.json` Stop chain; ship in `warn` (shadow), review false-positive rate, flip default to `block` | ~5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- `warn` mode logs "would block" and never blocks.
- `block` mode forces a re-compose on a frameless edit-turn; framed turns pass; `RUNTIME_RCA_AUDIT_BYPASS=1` still escapes.
- Loop guard caps blocks at one per turn-cluster.

---

## Execution Details

### W1.1 — Confidence + coupled-next-step triggers
**Scope**: Add `_LAYERED_CONFIDENCE_RE` and anchored `_GENERIC_NEXT_FULL_RE`; extend the refactor-turn branch to flag `missing_confidence` / `next_step_generic`.

**Commands**:
```bash
python -c "import ast; ast.parse(open('.claude/governance/scripts/post_agent_runtime_rca_audit.py').read())"
```

### W1.2 — Tests
**Scope**: Three isolating tests + positive control.

**Commands**:
```bash
pytest tests/unit/ops_scripts/hooks/claude/test_post_agent_runtime_rca_audit.py --noconftest -o addopts="" -q
```

### W2.1 — Blocking Stop hook
**Scope**: New gate importing `detect()`; block only `missing_refactor_outcome` on confirmed edit-tool turns; modes + loop guard.

### W2.2 — Register + shadow rollout
**Scope**: settings.json Stop entry; shadow then block.

---

## Gap Register

**GAP-1: high confidence unproven** — root cause could be claimed without grading certainty. Closed by `missing_confidence` (W1).

**GAP-2: next step decoupled from diagnosis** — "fix the bug" passed. Closed by `next_step_generic` (W1).

**GAP-3: advisory only** — violations log but never block. Addressed by W2 Stop-gate.

---

## Definition of Done

DoD-1: Confidence is enforced
- Evidence: `test_refactor_root_cause_without_confidence_flagged` asserts `missing_confidence is True`
- Status: DONE

DoD-2: Next step coupled to root cause is enforced
- Evidence: `test_refactor_generic_next_step_flagged` asserts `next_step_generic is True`
- Status: DONE

DoD-3: No regression / positive control clean
- Evidence: `pytest tests/unit/ops_scripts/hooks/claude/test_post_agent_runtime_rca_audit.py --noconftest -o addopts="" -q` → 22 passed
- Status: DONE

DoD-4: Detector smoke-run (executable surface)
- Evidence: `python .claude/governance/scripts/post_agent_runtime_rca_audit.py < /dev/null` exits 0 (advisory/fail-open)
- Status: DONE

DoD-5: W2 Stop-gate ships in shadow then block
- Evidence: `.claude/hooks/post_agent_runtime_rca_gate.py` + settings.json entry; shadow review of `runtime_rca_violations.jsonl`
- Status: TODO

### Verification vs Deferral

| Item | Verified now | Deferred |
|------|--------------|----------|
| Two new triggers + tests (W1) | ✅ 22 tests pass | — |
| Detector fail-open smoke | ✅ exits 0 | — |
| Blocking Stop-gate (W2) | — | Shadow rollout, then flip to block |

---

## Scope Expansion Authorization

When scope is discovered during execution, emit markers in order:

```
DISCOVERED_SCOPE: plan=rca-depth-enforcement-83e392 wave=<N> phase=<M> gap="<what>" impact="<severity>"
AUTHORIZATION_DECISION: plan=rca-depth-enforcement-83e392 decision=<ACCEPTED|DEFERRED|SPLIT_TO_NEW_PLAN|REJECTED> authorized_by=<user|author_gate|self> decisive_reason="<why>"
SCOPE_EXPANSION: plan=rca-depth-enforcement-83e392 reason="<summary>" added="<waves/phases>" authorized="yes"
```

---

## Supersedes

| Predecessor slug | Reason |
|---|---|

_None — net-new plan._

---

## Marker Quick Reference

```
WAVE_START: plan=rca-depth-enforcement-83e392 wave=<N>
WAVE_COMPLETE: plan=rca-depth-enforcement-83e392 wave=<N> note="+N tests, N files, scope=<summary>"
PHASE_COMPLETE: plan=rca-depth-enforcement-83e392 phase=<W1.1>
PLAN_COMPLETE: plan=rca-depth-enforcement-83e392 note="<final outcome>"
```
