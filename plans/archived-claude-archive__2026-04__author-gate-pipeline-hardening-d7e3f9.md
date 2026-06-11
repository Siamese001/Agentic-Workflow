---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-04\\author-gate-pipeline-hardening-d7e3f9.md'
original_relative_path: '_archive\\2026-04\\author-gate-pipeline-hardening-d7e3f9.md'
source_sha256: 0c2bea2e8b628d59b1aa71c3f8f018a824cbd00bb92b6fc799c8538ebc16de3d
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: author-gate-pipeline-hardening-d7e3f9
plan_type: governance
---

# Author-Gate Pipeline Hardening

Hardens the Author-Gate enforcement stack so canonical pipeline bypass (hand-crafted `ask_user_question` without `AUTHOR_GATE_PACKET`) is visible and corrected on the next turn rather than silently logged.

---

## Context (SCQA)

- **Situation** — The Author-Gate stack (emitter, renderer, auditor, CI gate) was fully implemented. The `post_cascade_author_gate_ui_audit.py` hook correctly detected pipeline bypasses and logged violations to `artifacts/windsurf/author_gate_ui_violations.jsonl`. The miss-detector and ask-packet-audit hooks were also wired.
- **Complication** — All three detection hooks had `show_output: false`, so every violation was silently swallowed into log files Cascade never sees. No `pre_user_prompt` hook existed to inject a pipeline reminder before response composition. As a result Cascade could repeatedly bypass the pipeline and never receive corrective feedback.
- **Question** — How do we make Author-Gate pipeline violations immediately visible to Cascade so the bypass loop is broken within one turn?
- **Answer** — Flip the three audit hooks to `show_output: true` and add a `pre_user_prompt` behavioral injector that emits `AUTHOR_GATE_PIPELINE_REMINDER` (proactive) and `AUTHOR_GATE_VIOLATION_REPLAY` (reactive from recent violations log) before every response where AG context is detected.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `.windsurf/hooks.json` | hook wiring and show_output values | ✅ |
| `.windsurf/scripts/post_cascade_author_gate_ui_audit.py` | audit logic and violation schema | ✅ |
| `.windsurf/scripts/post_cascade_author_gate_miss_detector.py` | bypass detection | ✅ |
| `.windsurf/scripts/post_cascade_ask_user_question_packet_audit.py` | packet-absence detection | ✅ |
| `.windsurf/schemas/author_gate_triggers.yaml` | enforcement mode (`shadow`) | ✅ |
| `.windsurf/rules/author-gate-enforcement.md` | pipeline contract | ✅ |

---

## Wave Structure

| Wave | Focus | Scope (files) | Status |
|------|-------|---------------|--------|
| W1 | Audit hook visibility | `hooks.json` (3 show_output flips) | ✅ DONE |
| W2 | Pre-prompt behavioral injector | `pre_user_prompt_author_gate_reminder.py` (new) + `hooks.json` (wiring) | ✅ DONE |
| W3 | Regression tests | `tests/unit/windsurf/scripts/test_pre_user_prompt_author_gate_reminder.py` (25 tests) | ✅ DONE |

---

## Out Of Scope

- Changing `enforcement: shadow` → `block` in `author_gate_triggers.yaml` (separate decision requiring FP-rate review)
- Changing `author-gate-enforcement.md` trigger from `model_decision` to `always_on` (would violate Anthropic two-tier token budget §33)
- Any changes to `emit_packet.py`, `render_card.py`, or the packet schema
- Runtime HITL (`agentic_core/L5_safety/`)

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.P1 | Show_output flips | `.windsurf/hooks.json` | Violations silent → never seen by Cascade | ~1K | ✅ DONE |
| W2.P1 | Reminder hook creation | `.windsurf/scripts/pre_user_prompt_author_gate_reminder.py` | No pre-composition enforcement existed | ~8K | ✅ DONE |
| W2.P2 | Hook wiring | `.windsurf/hooks.json` | New hook not in pre_user_prompt chain | ~1K | ✅ DONE |
| W3.P1 | Regression tests | `tests/unit/windsurf/scripts/test_pre_user_prompt_author_gate_reminder.py` | No test coverage for new hook | ~6K | ✅ DONE |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS · ✅ DONE · ❌ BLOCKED

---

## Gap Register

| ID | Gap | Resolution |
|----|-----|-----------|
| GAP-1 | `show_output: false` on all three AG audit hooks | Fixed: flipped to `true` in `hooks.json` |
| GAP-2 | No pre-composition pipeline reminder | Fixed: `pre_user_prompt_author_gate_reminder.py` PATH A/B |
| GAP-3 | Recent violations never replayed to Cascade | Fixed: PATH B reads violations JSONL with 120-min window |

---

## Root Cause Analysis

The bypass loop persisted because all three detection hooks silently logged to files Cascade never read, and there was no hook that fired before response composition. The `pre_author_gate.py` hook fired on `pre_write_code` (too late) and was in `enforcement: shadow` mode (no blocking). The `author-gate-enforcement.md` rule was `model_decision`-triggered — it only loaded if Cascade chose to load it, which it didn't when bypassing.

---

## Files Changed

### Modified
- `.windsurf/hooks.json` — `show_output: true` on `post_cascade_author_gate_miss_detector`, `post_cascade_author_gate_ui_audit`, `post_cascade_ask_user_question_packet_audit`; new `pre_user_prompt_author_gate_reminder.py` entry wired into `pre_user_prompt` chain

### Created
- `.windsurf/scripts/pre_user_prompt_author_gate_reminder.py` — PATH A (prompt signal detection, threshold=2) + PATH B (violation replay within 120-min window); always exits 0; bypass via `AG_REMINDER_BYPASS=1`
- `tests/unit/windsurf/scripts/test_pre_user_prompt_author_gate_reminder.py` — 25 tests: signal detection thresholds, window filtering, bypass env, PATH A/B firing, pipeline content contract

---

## Test Results

```
25 passed in 15.19s — zero regressions
```

WAVE_COMPLETE: author-gate-pipeline-hardening-d7e3f9
