---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\author-gate-deferred-scope-b8c1d4.md'
original_relative_path: 'author-gate-deferred-scope-b8c1d4.md'
source_sha256: 10ec720f438bfc061af4559e8cbdbb32047ba26693fa6787acb9e3a1bded3c7a
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-05-05'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: author-gate-deferred-scope-b8c1d4
plan_type: governance
---

# Author-Gate Deferred Scope

Tracks deferred scope items from `author-gate-pipeline-hardening-d7e3f9` that were explicitly excluded from the hardening plan. None of these items are implemented here — this is a tracker only.

---

## Context (SCQA)

- **Situation** — `author-gate-pipeline-hardening-d7e3f9` (completed 2026-05-05, commit `f0b4c3a77d`) closed the silent-bypass loop by flipping audit hooks to visible and adding the `pre_user_prompt_author_gate_reminder.py` injector. 25 tests pass.
- **Complication** — Three deeper enforcement changes were identified during the RCA but deliberately excluded: flipping `enforcement: shadow → block` in the triggers YAML (requires FP-rate evidence), promoting `author-gate-enforcement.md` to `always_on` (blocked by §33 token budget), and adding a CI gate that enforces the pre-prompt hook is wired whenever AG audit hooks exist.
- **Question** — What is the minimal sequenced work remaining to achieve fully-blocking Author-Gate enforcement?
- **Answer** — Three ordered items: (1) measure FP rate from shadow violations log → flip to block, (2) audit always-on budget headroom → promote rule if space exists, (3) add CI gate to enforce hook wiring invariant.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `artifacts/windsurf/author_gate_violations.jsonl` | FP-rate measurement for shadow → block flip | ✅ |
| `.windsurf/schemas/author_gate_triggers.yaml` | `enforcement` field to flip | ✅ (`enforcement: block`) |
| `.windsurf/rules/author-gate-enforcement.md` | trigger frontmatter to evaluate | ✅ (`trigger: always_on`) |
| `ops_scripts/ci/check_always_on_token_budget.py` | §33 budget gate — must pass before always_on promotion | ✅ (8,199 bytes headroom) |
| `.windsurf/hooks.json` | CI gate would verify hook wiring invariant | ✅ (AG-WIRE-1..4 pass) |

---

## Wave Structure

| Wave | Focus | Scope (files) | Status |
|------|-------|---------------|--------|
| W1 | Shadow→block flip | `author_gate_triggers.yaml` | ✅ DONE — `enforcement: block` confirmed in schemas/author_gate_triggers.yaml |
| W2 | Always-on rule promotion | `author-gate-enforcement.md` frontmatter | ✅ DONE — `trigger: always_on` confirmed; §33 budget passes (8,199 bytes headroom) |
| W3 | CI gate for hook wiring | `ops_scripts/ci/check_ag_hook_wiring.py` + `run_contract_gates.py` | ✅ DONE — commit d37b3711b5; AG-WIRE-1..4 satisfied |

---

## Out Of Scope

- Any changes to `emit_packet.py`, `render_card.py`, or the packet schema (closed in `author-gate-four-req-enforcement-c4d2a8`)
- Runtime HITL (`agentic_core/L5_safety/`) — separate domain per ADR-023
- New Author-Gate trigger definitions — requires separate trigger-expansion plan

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.P1 | Measure shadow FP rate | `artifacts/windsurf/author_gate_violations.jsonl` scan | Need ≥7 days shadow data, FP rate < 5% | ~3K | ✅ DONE |
| W1.P2 | Flip enforcement to block | `.windsurf/schemas/author_gate_triggers.yaml` | Single field change; must have FP evidence first | ~1K | ✅ DONE |
| W2.P1 | Audit §33 budget headroom | `ops_scripts/ci/check_always_on_token_budget.py` run | Two-tier compliance §33 — must confirm headroom | ~2K | ✅ DONE (43,001 / 51,200 bytes; 8,199 headroom) |
| W2.P2 | Promote rule to always_on | `.windsurf/rules/author-gate-enforcement.md` frontmatter | Only if W2.P1 confirms headroom | ~1K | ✅ DONE (promoted 2026-05-09) |
| W3.P1 | CI gate for hook wiring | `ops_scripts/ci/check_ag_hook_wiring.py` (new) | No structural guarantee hooks stay wired | ~5K | ✅ DONE (commit d37b3711b5) |
| W3.P2 | Register gate | `ops_scripts/ci/run_contract_gates.py` | Gate must appear in contract gate sweep | ~1K | ✅ DONE |
| W3.P3 | Tests | `tests/unit/ops_scripts/ci/test_check_ag_hook_wiring.py` | Coverage for new CI gate | ~4K | ✅ DONE (23 tests) |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS · ✅ DONE · ❌ BLOCKED

---

## Gap Register

| ID | Gap | Blocking Condition | Target Wave |
|----|-----|--------------------|-------------|
| GAP-1 | `enforcement: shadow` — pre-write gate never blocks | FP rate < 5% over ≥7 days shadow data | W1 |
| GAP-2 | `author-gate-enforcement.md` is `model_decision` not `always_on` | §33 always-on token budget must have headroom | W2 |
| GAP-3 | No CI gate verifying hook wiring | Not blocked — additive gate | W3 |

---

## Sequencing Constraints

- W1 **must** precede W2 (block mode should be live before promoting rule to always_on to avoid double-fire confusion)
- W2.P1 **must** precede W2.P2 (budget audit gates the promotion)
- W3 is independent — can be done in parallel with W1/W2

---

## Parent Plan

Deferred from: `author-gate-pipeline-hardening-d7e3f9` (completed 2026-05-05)
Notion page: `35727693-f55c-819f-a38b-f6da45b62da7`
