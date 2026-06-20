---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\rca-wave-marker-emission-gap-c7d3f1.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\rca-wave-marker-emission-gap-c7d3f1.md'
source_sha256: 0d7c31b8a16eed9de7e7c3942f8d5c0e341602fa2d38da23315f2f7e7108a3b0
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: rca-wave-marker-emission-gap-c7d3f1
plan_type: governance
dod_exempt: false
---

# RCA: Wave Lifecycle Markers Never Emitted by Cascade

Cascade omitted `WAVE_START:` / `WAVE_COMPLETE:` markers during W0–W2 of
`chroma-graphrag-lic-rg-research-f4a2e9`, leaving the plan markdown stale and
the audit safety-net silenced. This plan hardens the enforcement chain so the
failure mode cannot recur silently.

---

## Context (SCQA)

- **Situation** — The wave lifecycle chain (`post_cascade_wave_lifecycle_capture.py` →
  `_plan_wave_table_updater.update_wave_in_plan()`, registered in `hooks.json` at line 281) is
  fully wired and unit-tested. The safety-net audit (`post_cascade_wave_completion_audit.py`)
  fires an advisory when ≥3 file writes occur without a marker.
- **Complication** — Cascade executed W0, W1, and W2 of
  `chroma-graphrag-lic-rg-research-f4a2e9` without emitting any `WAVE_START:` or
  `WAVE_COMPLETE:` markers. The safety-net also silenced itself because
  `wave_execution_state.py start` was never called, causing `_has_active_plan()`
  to return `False` and short-circuit the audit to `return 0`. The
  `wave_lifecycle_capture.jsonl` log contained only unit-test fixture entries
  (`demo-plan-abc123`, `alpha-plan-abc123`) — zero real-slug entries.
- **Question** — How do we make the "missing wave marker" failure mode
  self-detectable and self-correcting without relying on Cascade voluntarily
  emitting markers?
- **Answer** — Strengthen the safety-net audit to fire unconditionally (remove the
  `_has_active_plan()` short-circuit), surface its output visibly
  (`show_output=true`), and add a pre-commit CI gate that fails when the wave
  table in a plan shows `🔲 TODO` for waves that appear complete (edits present
  but no marker logged for that slug).

---

## Root Cause Analysis

### Primary root cause

**Cascade never emitted `WAVE_START:` / `WAVE_COMPLETE:` markers.**

The hook chain is reactive-only — it parses markers from response text and applies
updates. If Cascade omits the markers, nothing fires. The chain has no
proactive assertion that forces marker emission.

### Secondary root cause

**`wave_execution_state.py start` was never called**, so `_has_active_plan()` in
`post_cascade_wave_completion_audit.py` (line 123) returned `False` and the
function returned `0` immediately. The audit advisory — the one safety-net that
could have surfaced a visible warning — silenced itself because its own guard
predicate relied on a state file that Cascade never wrote.

### Compounding factor

`post_cascade_wave_completion_audit.py` is registered with `show_output=false`
in `hooks.json`. Even if the advisory had fired, it would have been invisible to
the user.

### Not a root cause (correctly wired)

- The hook IS registered (`hooks.json` line 281).
- `_plan_wave_table_updater.update_wave_in_plan()` correctly flips `🔲 TODO` →
  `✅ DONE` when given a real marker.
- The regex in `post_cascade_wave_lifecycle_capture.py` is correct.
- The `_wave_execution_state.py` state helper is correct.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `.windsurf/scripts/post_cascade_wave_completion_audit.py` | Contains `_has_active_plan()` short-circuit (line 123) | ✅ READ |
| `.windsurf/scripts/post_cascade_wave_lifecycle_capture.py` | Confirms hook is reactive-only | ✅ READ |
| `.windsurf/scripts/_wave_execution_state.py` | Confirms `is_active()` reads JSON state file | ✅ READ |
| `artifacts/windsurf/wave_lifecycle_capture.jsonl` | Confirmed: only fake-slug test entries, zero real slugs | ✅ CONFIRMED via RCA |
| `.windsurf/hooks.json` line 281 | Confirms hook IS registered | ✅ CONFIRMED via RCA |

---

## Wave Structure

| Wave | Scope | Checkpoint | Tokens | Status |
|------|-------|------------|--------|--------|
| W0 | Pre-flight: read all 3 affected scripts, confirm line numbers, verify hooks.json registration | scripts read ✅ | ~2k | ✅ DONE |
| W1 | Fix `post_cascade_wave_completion_audit.py`: remove `_has_active_plan()` guard, flip `show_output=true`, widen detection heuristic | audit hook patched + visible | ~4k | ✅ DONE |
| W2 | Add pre-commit CI gate `check_wave_marker_emission.py`: detects plan slugs with recent edits in git diff but no wave marker in the capture log | CI gate green | ~5k | ✅ DONE |
| W3 | Update `notion-plan-wave-deferral.md` and `AGENTS.md` to make `WAVE_START:` / `WAVE_COMPLETE:` emission explicit per-wave, not optional | rule patched | ~3k | ✅ DONE |
| W4 | Tests + registration + retroactive correction of chroma plan | 36 new tests green, gates registered | ~4k | ✅ DONE |

**Total: ~18k tokens across 4 execution waves**

**Status tracking**: W1 start triggers `wave_execution_state.py start`. W4 completion emits `PLAN_COMPLETE:`.

---

## Out Of Scope

- Changing the wave lifecycle writer or Notion sync path (wired correctly).
- Fixing `chroma-graphrag-lic-rg-research-f4a2e9` W3+ execution (separate plan).
- Retrofitting markers into the git history of prior waves (manual retroactive patch already applied).
- Modifying `_plan_wave_table_updater.py` (works correctly when given markers).

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.P1 | Remove `_has_active_plan()` guard | `post_cascade_wave_completion_audit.py` | Guard causes total audit silence when `wave_execution_state.py start` skipped | ~2k | 🔲 TODO |
| W1.P2 | Flip `show_output=true` for audit hook | `hooks.json` | Advisory with `show_output=false` is invisible | ~1k | 🔲 TODO |
| W1.P3 | Widen heuristic: also detect `read_file`/`edit` tool call counts from marker-free responses | `post_cascade_wave_completion_audit.py` | Existing regex patterns for EDIT_PATTERNS are too narrow | ~1k | 🔲 TODO |
| W2.P1 | CI gate `check_wave_marker_emission.py` | `ops_scripts/ci/check_wave_marker_emission.py` | No pre-commit catch for plan-table stale state | ~3k | 🔲 TODO |
| W2.P2 | Register gate in `run_contract_gates.py` | `ops_scripts/ci/run_contract_gates.py` | Gate must be discoverable | ~1k | 🔲 TODO |
| W3.P1 | Update `notion-plan-wave-deferral.md` | `.windsurf/rules/notion-plan-wave-deferral.md` | Rule says markers are "SHOULD" — elevate to "MUST" per wave | ~2k | 🔲 TODO |
| W3.P2 | Update `AGENTS.md` wave lifecycle table | `AGENTS.md` | Auto-routing table does not mention per-wave marker requirement | ~1k | 🔲 TODO |
| W4.P1 | Unit tests for patched audit hook | `tests/unit/windsurf_scripts/test_wave_completion_audit.py` | No tests currently cover the `_has_active_plan=False` short-circuit path | ~2k | 🔲 TODO |
| W4.P2 | Unit tests for CI gate | `tests/unit/ops_scripts/ci/test_check_wave_marker_emission.py` | New gate needs coverage | ~2k | 🔲 TODO |

---

## Gap Register

| Gap ID | Description | Introduced by | Fix wave |
|--------|-------------|--------------|----------|
| GAP-1 | `_has_active_plan()` guard silences audit when `wave_execution_state.py start` skipped | `post_cascade_wave_completion_audit.py` line 123 | W1.P1 |
| GAP-2 | Audit hook `show_output=false` makes advisory invisible even when it fires | `hooks.json` registration | W1.P2 |
| GAP-3 | EDIT_PATTERNS regex too narrow — misses `write_to_file` with `CodeContent=` shape | `post_cascade_wave_completion_audit.py` lines 32–35 | W1.P3 |
| GAP-4 | No pre-commit gate detecting stale plan wave tables vs. git edit history | missing gate | W2.P1 |
| GAP-5 | Rule says marker emission is "SHOULD", not "MUST" | `notion-plan-wave-deferral.md` | W3.P1 |
| GAP-6 | `AGENTS.md` auto-routing table omits per-wave marker as mandatory step | `AGENTS.md` | W3.P2 |

---

## Definition of Done

| DoD ID | Criterion | Verification |
|--------|-----------|-------------|
| DoD-1 | `post_cascade_wave_completion_audit.py` fires advisory without requiring `_has_active_plan()=True` | Unit test: mock `is_active=None`, assert advisory emitted |
| DoD-2 | Audit hook `show_output` flipped to `true` in `hooks.json` | `grep '"show_output": true' hooks.json` → entry present |
| DoD-3 | CI gate `check_wave_marker_emission.py` exits 0 on clean repo, exits advisory-warn when stale plan table detected | `python ops_scripts/ci/check_wave_marker_emission.py` exits 0 |
| DoD-4 | Gate registered in `run_contract_gates.py` | `grep WAVE-MARKER ops_scripts/ci/run_contract_gates.py` → entry present |
| DoD-5 | Rule `notion-plan-wave-deferral.md` states `WAVE_START:` / `WAVE_COMPLETE:` are MANDATORY (not optional) per wave | Manual review of patched rule |
| DoD-6 | ≥10 new tests pass covering W1.P1–P3 and W2.P1 | `pytest tests/unit/windsurf_scripts/test_wave_completion_audit.py tests/unit/ops_scripts/ci/test_check_wave_marker_emission.py -v` → all green |

| Item | Verification | Deferral |
|------|-------------|---------|
| Retroactive marker emission for prior plans | Manual — already applied for chroma plan | Not deferred |
| Real-time Notion sync | Existing chain, not changed | Not in scope |
| Marker injection by hook (auto-emit) | Out of scope — Cascade must emit | Permanent out-of-scope |
