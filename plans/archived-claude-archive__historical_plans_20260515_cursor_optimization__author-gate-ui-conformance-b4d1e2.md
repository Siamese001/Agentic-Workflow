---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\author-gate-ui-conformance-b4d1e2.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\author-gate-ui-conformance-b4d1e2.md'
source_sha256: a7b315aebb6054d0de429ea0f7aa43c70289826f7425cb3ea605e2891359656f
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: author-gate-ui-conformance-b4d1e2
plan_type: governance
---

# Author-Gate UI Conformance — Star + Confidence Discipline

Lock star semantics to "dominance-fires-only", make `[confidence=0.NN]` mandatory on every surfaced option, and add a post-cascade + CI gate to enforce it.

---

## Context (SCQA)

- **Situation** — Author-Gate packets are produced by `@c:\Git\Agentic-Workflow-FRESH\.windsurf\skills\author-gate-packet-builder\emit_packet.py:286-305` which stars the highest-confidence surfaced option unconditionally. The ledger record carries `surface_label` and `surface_description_prefix` fields with confidence numbers and star glyphs.
- **Complication** — Four doctrine sources disagree on when the star fires. Template + code + SVP calibration say "always star the top". The user's corrected packet (top=0.77, dominance did_not_fire) shows no star. Additionally, nothing enforces that `ask_user_question` descriptions mirror the packet's confidence prefix, so Cascade's prose drops the number on many turns.
- **Question** — How do we make the Author-Gate UI (star + confidence prefix) match a single, unambiguous rule on every turn?
- **Answer** — Adopt "star iff `routing.rule_applied == dominance_fires`", make `[confidence=0.NN]` mandatory on every surfaced option, and add a post-cascade UI audit + CI twin that fails on drift.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `@c:\Git\Agentic-Workflow-FRESH\.windsurf\skills\author-gate-packet-builder\packet_template.md` | Gold-star section is one doctrine source to rewrite | ✅ |
| `@c:\Git\Agentic-Workflow-FRESH\.windsurf\skills\author-gate-packet-builder\emit_packet.py` | `build_packet()` code that applies star; must gate on routing verdict | ✅ |
| `@c:\Git\Agentic-Workflow-FRESH\.windsurf\rules\author-gate-svp-calibration.md` | Calibration table says "⭐ Always = Green" — must invert | ✅ |
| `@c:\Git\Agentic-Workflow-FRESH\.windsurf\rules\author-gate-enforcement.md` | Add invariant under Pipeline step 7 | ✅ |
| `@c:\Git\Agentic-Workflow-FRESH\.windsurf\hooks.json` | Wire new post_cascade hook | 🔲 |
| `@c:\Git\Agentic-Workflow-FRESH\.pre-commit-config.yaml` | Wire new CI gate | 🔲 |

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Doctrine + code lock-step; gate + tests in one cohesive change | 4 doctrine/code files + 2 new gate files + 1 test file + hooks.json + pre-commit wiring | A | ~6K 🟢 |

**Total: ~6K tokens across 1 wave, GREEN. Single-wave plan — no Notion deferral per `notion-plan-wave-deferral.md`.**

---

## Out Of Scope

- Changing the surface_threshold (0.72) or dominance parameters (0.85 / 0.12).
- Refactoring the packet schema at `@c:\Git\Agentic-Workflow-FRESH\.windsurf\schemas\decision_record.schema.json`.
- Changes to `post_cascade_author_gate_capture.py` or `post_cascade_author_gate_miss_detector.py`.
- Ledger migration or backfill — pre-existing decisions keep their recorded star state.

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| 1.1 | Doctrine lock-in — star = dominance only | `packet_template.md`, `author-gate-svp-calibration.md`, `author-gate-enforcement.md` | GAP-1 | ~1.5K | ✅ DONE |
| 1.2 | Code gate — `emit_packet.py` only stars on `dominance_fires` | `emit_packet.py` | GAP-2 | ~1K | ✅ DONE |
| 1.3 | Post-cascade UI audit hook | `.windsurf/scripts/post_cascade_author_gate_ui_audit.py` (NEW), `.windsurf/hooks.json` | GAP-3 | ~2K | ✅ DONE |
| 1.4 | CI twin + tests | `ops_scripts/ci/author_gate/check_ui_conformance.py` (NEW), `tests/unit/author_gate/test_author_gate_ui_audit.py` (NEW), `.pre-commit-config.yaml` | GAP-3 | ~1.5K | ✅ DONE |

---

## Gap Register

**GAP-1: Doctrine split on star-firing condition**
- Template + SVP calibration table + code treat star as "always top surfaced".
- User's corrected packet (top=0.77, did_not_fire) treats star as "dominance only".
- Cascade picks per-turn, producing inconsistent UI.

**GAP-2: Code follows the wrong doctrine**
- `emit_packet.py` `build_packet()` sets `is_recommended=True` on `surfaced_sorted[0]` unconditionally.
- Need to gate on `routing["rule_applied"] == "dominance_fires"`.

**GAP-3: No UI conformance validator**
- `check_ledger_schema.py` validates the ledger record but does not inspect `ask_user_question` text.
- Nothing asserts every surfaced option starts with `[confidence=0.NN]` or that star appears iff dominance fires.
- Silent drift between packet JSON and user-facing UI is the observed failure mode.

---

## Execution Plan

### Phase 1.1 — Doctrine lock-in
**Scope**: Rewrite Gold-Star Marking in `packet_template.md` to fire only when `routing.rule_applied == "dominance_fires"`. Invert SVP calibration row so "star without dominance = Red". Add one-line invariant under Pipeline step 7 in `author-gate-enforcement.md`.

**Acceptance**: Three doctrine files say the same thing; no source contradicts the dominance-only rule.

### Phase 1.2 — Code gate
**Scope**: In `emit_packet.py` `build_packet()`, wrap the star-assignment block with `if routing.get("rule_applied") == "dominance_fires":`. Non-dominance surfaced options get `is_recommended=False` and a plain `[confidence=0.NN]` prefix. When dominance does not fire, `surface_description_prefix` is still emitted with the confidence number so the UI gate has something to assert on.

**Acceptance**: unit test emits a packet with top=0.77/second=0.74 and verifies no option has `is_recommended=True`.

### Phase 1.3 — Post-cascade UI audit hook
**Scope**: New `post_cascade_author_gate_ui_audit.py` in `.windsurf/scripts/`. Scans the turn response for `ask_user_question` calls. For each option, validates:
1. Description matches `^\[(RECOMMENDED ⭐ )?confidence=0\.\d\d\]`.
2. At most one option per packet has the ⭐ prefix.
3. Star presence matches routing verdict: if most recent `AUTHOR_GATE_PACKET:` in the turn has `routing.rule_applied == "dominance_fires"`, exactly one star is required; otherwise zero.
Violations append to `artifacts/windsurf/author_gate_ui_violations.jsonl`. Bypass env `AUTHOR_GATE_UI_BYPASS=1` logs `reason: "bypass"` and passes.
Wire into `.windsurf/hooks.json` under `post_cascade_end_of_turn` (follow existing `post_cascade_author_gate_capture.py` entry as the shape model).

**Acceptance**: hook script runs standalone with a crafted input fixture and emits the expected violation rows.

### Phase 1.4 — CI twin + tests
**Scope**: New `ops_scripts/ci/author_gate/check_ui_conformance.py` that tails `artifacts/windsurf/author_gate_ui_violations.jsonl` and fails if unresolved entries exist within a 7-day staleness window (follow `check_capture_queue_freshness.py` shape). Wire as a pre-commit hook id `author-gate-ui-conformance` under tier T7-equivalent.
New tests at `tests/unit/author_gate/test_author_gate_ui_audit.py` covering:
- dominance_fires → one star required, pass/fail cases
- surface_top_N → zero stars required, pass/fail cases
- missing confidence prefix → fail
- multiple stars → fail
- bypass env var → pass

**Acceptance**: `pytest tests/unit/author_gate/test_author_gate_ui_audit.py -x -q` passes; pre-commit hook id resolves.

---

## Rules

- Doctrine files touched in one commit as a lockstep; no partial rewrite.
- `emit_packet.py` change paired with its unit test in the same commit.
- New hook + CI gate follow the established single-helper / two-consumer pattern (same shape as `_ssot_folder_check.py` + `pre_write_gate.py` + `check_ssot_folder_routing.py`).
- No backfill of historical ledger entries.

---

## Success Criteria

- [x] All four doctrine sources state the same star rule (dominance-only).
- [x] `emit_packet.py` gates `is_recommended` on `routing["rule_applied"] == "dominance_fires"`.
- [x] Post-cascade hook produces violations on crafted mismatch, passes on crafted match.
- [x] CI gate integrates with pre-commit and fails on stale unresolved violations.
- [x] Full unit-test suite for audit + emit_packet passes (11/11).

---

## Rollback Strategy

1. Revert the commit; the prior unconditional-star behavior resumes automatically.
2. Delete `artifacts/windsurf/author_gate_ui_violations.jsonl` if populated during rollout.
3. Un-wire the hook from `.windsurf/hooks.json` and the CI entry from `.pre-commit-config.yaml`.

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| Doctrine sources aligned | 4 / 4 | grep for "star" / "⭐" in the four files; all say dominance-only |
| `emit_packet.py` star gated on routing | 1 assertion path in code | unit test at Phase 1.2 |
| UI audit hook wired | Entry in hooks.json | `rg post_cascade_author_gate_ui_audit .windsurf/hooks.json` |
| CI gate wired | Entry in pre-commit | `rg author-gate-ui-conformance .pre-commit-config.yaml` |
| Tests passing | 100% of new tests | pytest exit 0 |

## Cascade Alignment Checks

- Doctrine lean: keep rules short; procedural detail is in the skill template.
- Evidence-before-synthesis: every change cites the specific file+line.
- Deterministic enforcement: runtime hook + CI gate, not prose rule.
- Single-wave plan: Notion write not deferred per `notion-plan-wave-deferral.md`.
