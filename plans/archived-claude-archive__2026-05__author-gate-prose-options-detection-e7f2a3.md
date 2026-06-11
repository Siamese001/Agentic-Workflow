---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\author-gate-prose-options-detection-e7f2a3.md'
original_relative_path: '_archive\\2026-05\\author-gate-prose-options-detection-e7f2a3.md'
source_sha256: 08784d11b9adaec6470937bda54090d0c411a3468b2df382486410d8eb33d095
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: author-gate-prose-options-detection-e7f2a3
plan_type: governance
touches_agentic_core: false
touches_governance_ci: true
touches_windsurf_rules: true
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# Author-Gate Prose-Options Detection — Fix Prose Menu Miss

Fix the root cause identified in RCA (2026-05-12): Cursor Agent presented a multi-option next-phase decision as a Markdown prose menu ("Option A / B / C") without invoking the Author-Gate pipeline. The miss detector did not catch it because no multi-file edits occurred and keyword density was too low.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: COMPLETED
CURRENT_WAVE: DONE
LAST_COMPLETED_WAVE: W3
LAST_UPDATED: 2026-05-13

WAVE_COMPLETE: plan=author-gate-prose-options-detection-e7f2a3 wave=1 note="Added _PROSE_OPTIONS_PATTERNS, _has_prose_options_menu, _has_author_gate_completion_marker, Signal 5 (prose_options_menu +3) to miss detector"
WAVE_COMPLETE: plan=author-gate-prose-options-detection-e7f2a3 wave=2 note="Added Prose Options Menu prohibition block to author-gate-enforcement.md; added prose_options_menu to VIOLATION_REMEDIATION in pre_user_prompt_author_gate_reminder.py"
WAVE_COMPLETE: plan=author-gate-prose-options-detection-e7f2a3 wave=3 note="27 new tests all passing in test_author_gate_prose_options_detection.py (TC-1 through TC-9 + unit tests for helpers)"
PLAN_COMPLETE: plan=author-gate-prose-options-detection-e7f2a3 note="All 3 waves done, 27/27 new tests pass, 28/28 existing miss detector tests pass, no regressions"

## Execution Evidence

### Files Changed

| File | Wave | Change |
|------|------|--------|
| `.cursor/scripts/post_cursor_agent_author_gate_miss_detector.py` | W1 | Added `_PROSE_OPTIONS_PATTERNS`, `_has_author_gate_completion_marker()`, `_has_prose_options_menu()`, Signal 5 `prose_options_menu` (+3) |
| `.cursor/rules/author-gate-enforcement.md` | W2 | Added "Prose Options Menu — Explicit Prohibition" block under Continuous Execution Invariant |
| `.cursor/scripts/pre_user_prompt_author_gate_reminder.py` | W2 | Added `prose_options_menu` key to `VIOLATION_REMEDIATION` with canonical remediation text |
| `tests/unit/windsurf/scripts/test_author_gate_prose_options_detection.py` | W3 | Created with 27 test cases (TC-1..TC-9 + helpers); moved from windsurf_scripts/ to match co-located miss detector convention |

### Verification Outputs — Final Bundle (2026-05-13)

```
# 1. New prose-options tests — canonical path:
pytest tests/unit/windsurf/scripts/test_author_gate_prose_options_detection.py -v
→ 27 passed, 0 failed

# 2. Existing miss detector tests — zero regressions:
pytest tests/unit/windsurf/scripts/test_post_cursor_agent_author_gate_miss_detector.py -v
→ 28 passed, 0 failed

# 3. Miss detector: prose_options_menu symbol present at lines 164, 223, 225:
grep -n "prose_options_menu" .cursor/scripts/post_cursor_agent_author_gate_miss_detector.py
→ 164: def _has_prose_options_menu(text: str) -> bool:
→ 223: if _has_prose_options_menu(text) and not _has_author_gate_completion_marker(text):
→ 225:     positive_signals.append("prose_options_menu")

# 4. Enforcement rule: prohibition block present at line 53:
grep -n "Prose Options Menu" .cursor/rules/author-gate-enforcement.md
→ 53: ### Prose Options Menu — Explicit Prohibition

# 5. Reminder script: remediation entry present at line 123:
grep -n "prose_options_menu" .cursor/scripts/pre_user_prompt_author_gate_reminder.py
→ 123:     "prose_options_menu": (...)
```

All 5 checks green. No scope expansion required.

---

## RCA Summary

### Root Cause (DIRECTLY OBSERVED)

From the G1.P3 completion response:
```
**Option A — Continue G2 (Session Metadata):** ...
**Option B — Expand G1 (Additional Paths):** ...
**Option C — Proceed to A1/A2 (apps_contract):** ...
```

This is a **prose options menu** presented as a Markdown table with bold headers — NOT a `DECISION_CAPTURED:` marker, NOT an `AUTHOR_GATE_PACKET:`, NOT an `ask_user_question` invocation. Four rules were violated simultaneously:

| Violation | Rule |
|-----------|------|
| Options in prose, not `ask_user_question` | Cursor Agent-clickable requirement (§7) |
| No `AUTHOR_GATE_PACKET:` block | Canonical-emitter invariant |
| No confidence prefix, no ⭐, no tradeoff segment | Four-requirement contract |
| No `DECISION_CAPTURED:` marker emitted | Silent-marker invariant |

### Why the Miss Detector Did Not Catch It

`post_cursor_agent_author_gate_miss_detector.py` scores misses on:
1. `multi_file_edit` — requires ≥2 distinct file paths edited. **Not triggered** — this response had zero file edits.
2. `decision_keywords` — "refactor", "delete", "archive", etc. **Not triggered** — no qualifying keywords in "Option A/B/C continue G2 metadata" text.
3. `plan_file_touched` — plan path in response. **Partially triggered** (score=+1) but threshold is 2.
4. `SR_PLAN without SR_APPROVAL` — not triggered.

**Net result: miss_score=1, below threshold=2 → no log entry, no violation.**

### Two-Layer Fix Required

1. **`post_cursor_agent_author_gate_miss_detector.py`** — Add `prose_options_menu` signal: detect bold-labeled option patterns (`**Option A`, `**Option B`, `Option A —`, `Option B —`, `Option 1`, `Option 2`) without a corresponding `DECISION_CAPTURED:` or `AUTHOR_GATE_PACKET:` marker. Score: +3 (high weight — this is an almost-certain miss).

2. **`author-gate-enforcement.md`** — Add explicit prohibition: "Presenting options as Markdown bold/table prose is FORBIDDEN. Options MUST reach `ask_user_question`. Markdown option menus are not Author-Gate."

3. **`pre_user_prompt_author_gate_reminder.py`** — Add `prose_options_menu` to `VIOLATION_REMEDIATION` dict so Path B replays the correct remediation message when the pattern fires.

4. **Test**: New test cases for the prose options signal in `test_author_gate_miss_detector.py`.

---

## Context (SCQA)

- **Situation**: The Author-Gate pipeline has comprehensive enforcement for `ask_user_question` shape violations, packet/ask pairing, and queue drain. The miss detector catches multi-file refactor decisions that bypass the gate.
- **Complication**: A specific bypass pattern — presenting options as Markdown prose after completing a wave phase — is invisible to all existing detectors because it generates no file edits and weak keyword signals. Confirmed to score 0–1, below the miss threshold of 2.
- **Question**: How do we close the prose-options-menu bypass gap without over-triggering on legitimate response content?
- **Answer**: Add a targeted `prose_options_menu` signal to the miss detector, weight it heavily (+3), and add the corresponding rule prohibition + reminder remediation text.

---

## Wave Overview

**Waves**: 3 total (W1–W3)
**Total Estimate**: ~8K tokens
**Current**: W0 (pre-flight)

**Wave Manifest**:
- **W1** — Miss detector: add prose_options_menu signal | ~3K tokens | Checkpoint A | STATUS: ✅ DONE
- **W2** — Rule + reminder: add explicit prohibition to enforcement rule + VIOLATION_REMEDIATION | ~2K tokens | Checkpoint B | STATUS: ✅ DONE
- **W3** — Tests + CI registration | ~3K tokens | Checkpoint C | STATUS: ✅ DONE

---

## Wave 1 — Miss Detector: Prose Options Menu Signal

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Authorization**: NOT_REQUIRED — single-file edit to `.cursor/scripts/post_cursor_agent_author_gate_miss_detector.py`.

**Phases**:
- **W1.1** — Add `_PROSE_OPTIONS_PATTERNS` regex + `_has_prose_options_menu()` detector | ~1.5K tokens | PHASE_STATUS: ✅ DONE | PHASE_COMPLETE: YES
- **W1.2** — Add Signal 5 (`prose_options_menu`) in `_compute_miss_score()` with weight +3 | ~1K tokens | PHASE_STATUS: ✅ DONE | PHASE_COMPLETE: YES
- **W1.3** — Add `prose_options_menu` to `VIOLATION_REMEDIATION` in `pre_user_prompt_author_gate_reminder.py` | ~0.5K tokens | PHASE_STATUS: ✅ DONE | PHASE_COMPLETE: YES

**Signal Design**:

```python
# Fires when ≥2 of these patterns appear in the response, AND
# no DECISION_CAPTURED / AUTHOR_GATE_PACKET anti-signal is present.
_PROSE_OPTIONS_PATTERNS = (
    re.compile(r"\*\*Option\s+[A-D\d]\b", re.IGNORECASE),        # **Option A / **Option 1
    re.compile(r"^#+\s*Option\s+[A-D\d]\s*[—\-:]", re.MULTILINE | re.IGNORECASE),  # ## Option A —
    re.compile(r"\bOption\s+[A-D]\s*[—\-–]\s+\w", re.IGNORECASE), # Option A — Continue
    re.compile(r"\bOption\s+[A-D]\s*\(", re.IGNORECASE),           # Option A (
    re.compile(r"^\*\*[A-D]\.\s+\w", re.MULTILINE),                # **A. Continue
    re.compile(r"Recommended\s+Next\s+(?:Phase|Step|Wave|Action)", re.IGNORECASE),  # exact phrase from miss
)
```

A response scores `prose_options_menu` (+3) when: ≥2 of the above patterns match AND the response does NOT contain `DECISION_CAPTURED:` or `AUTHOR_GATE_PACKET:` or a well-formed `ask_user_question` invocation.

**Anti-signal exemptions** (do NOT fire on):
- Responses that already contain `DECISION_CAPTURED:` — the correct pipeline was followed.
- Responses that contain `ask_user_question` with an `AUTHOR_GATE_PACKET:` — also correct.
- Single option occurrence without a second sibling — not a menu.

**Acceptance**:
- Signal fires on the exact G1.P3 response text (miss_score ≥ 2, threshold met, log entry written).
- Signal does NOT fire on responses that contain `DECISION_CAPTURED:`.
- Signal does NOT fire on single "Option A" references in prose context without a sibling.

---

## Wave 2 — Rule + Reminder: Explicit Prohibition

WAVE_ID: W2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Authorization**: NOT_REQUIRED — updates to `.cursor/rules/author-gate-enforcement.md` (always_on rule, not a new rule).

**Phases**:
- **W2.1** — Add explicit prohibition block to `author-gate-enforcement.md` Continuous Execution Invariant section | ~1K tokens | PHASE_STATUS: ✅ DONE | PHASE_COMPLETE: YES
- **W2.2** — Add `prose_options_menu` violation type + remediation text to `pre_user_prompt_author_gate_reminder.py` VIOLATION_REMEDIATION dict | ~0.5K tokens | PHASE_STATUS: ✅ DONE | PHASE_COMPLETE: YES

**Rule addition target** (insert after existing Continuous Execution Invariant paragraph):

```markdown
### Prose Options Menu — Explicit Prohibition

> ⛔ **Presenting options as Markdown prose is FORBIDDEN.** The following patterns are NOT Author-Gate and MUST NOT be used to present decisions to the user:
> - Bold-labeled options: `**Option A —**`, `**Option B —**`, `**A. Continue...**`  
> - Markdown table of options without `ask_user_question`
> - "Recommended Next Phase/Step/Action" menus in prose
>
> These patterns produce **zero decision capture** — no ledger entry, no packet, no user-clickable interface. They are indistinguishable from Cursor Agent making the decision unilaterally.
>
> **Correct path**: If a genuine decision point exists → invoke the full pipeline: `refactor-decision-memory` → `author-gate-packet-builder` → `author-gate-ui-renderer` → `ask_user_question`. If no genuine decision exists → continue execution per the Continuous Execution Invariant.
```

**Acceptance**:
- Rule file contains the prohibition block.
- `pre_user_prompt_author_gate_reminder.py` `VIOLATION_REMEDIATION` maps `prose_options_menu` to a remediation string that cites the full pipeline.

---

## Wave 3 — Tests + CI Registration

WAVE_ID: W3
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Authorization**: NOT_REQUIRED — new test file + existing CI gate registration.

**Phases**:
- **W3.1** — New test file `tests/unit/windsurf/scripts/test_author_gate_prose_options_detection.py` | ~2K tokens | PHASE_STATUS: ✅ DONE | PHASE_COMPLETE: YES
- **W3.2** — Verify existing `post_cursor_agent_author_gate_miss_detector.py` test file still passes; add prose_options cases to it if it exists | ~0.5K tokens | PHASE_STATUS: ✅ DONE | PHASE_COMPLETE: YES

**Test cases (W3.1)**:

| Case | Input signal | Expected |
|------|-------------|----------|
| TC-1 | G1.P3 verbatim "Option A/B/C" block | miss_score ≥ 2, `prose_options_menu` in signals |
| TC-2 | Response with `DECISION_CAPTURED:` + "Option A" | miss_score = 0 (anti-signal) |
| TC-3 | Response with `AUTHOR_GATE_PACKET:` + options | miss_score = 0 (anti-signal) |
| TC-4 | Single "Option A" reference (no sibling) | miss_score < 2 (not a menu) |
| TC-5 | "Recommended Next Phase: Option A — Continue" | miss_score ≥ 2 (phrase match + option) |
| TC-6 | "**A. Continue G2**\n**B. Expand G1**\n**C. Proceed**" | miss_score ≥ 2 |
| TC-7 | ask_user_question WITHOUT packet + options | miss_score ≥ 2 (double violation) |
| TC-8 | ask_user_question WITH AUTHOR_GATE_PACKET + options | miss_score = 0 |

**Acceptance**:
- ≥8 test cases pass.
- Existing miss detector tests (if any) still pass — zero regressions.
- No new CI gate registration required (detector already runs via `post_cursor_agent_author_gate_audit.py` miss_detector subcommand).

---

## Out Of Scope

- Changing the miss threshold (remains 2 — the new signal weight (+3) is sufficient alone).
- Adding new CI gate (detector already registered via suite hook).
- Retroactive backfill of historical misses — advisory log only.
- Changing `MISS_SCORE_THRESHOLD` — not needed; +3 weight alone exceeds threshold.

---

## Gap Register

**GAP-1: ask_user_question without canonical packet**
- Already handled by `post_cursor_agent_ask_user_question_packet_audit.py` and `post_cursor_agent_author_gate_pipeline_audit.py`.
- This plan adds detection for the case where NEITHER `ask_user_question` NOR a packet is present — only prose options.

**GAP-2: False positive on legitimate "Option" usage**
- Mitigated by requiring ≥2 pattern matches (single "Option A" reference → score += 0 from this signal).
- "Option" in config/YAML prose unlikely to have sibling bold-labeled options.
- Anti-signal: `DECISION_CAPTURED:` clears score entirely.

---

## Definition of Done

DoD-1: `post_cursor_agent_author_gate_miss_detector.py` contains `_PROSE_OPTIONS_PATTERNS` and Signal 5 with weight +3.
- Evidence: `grep -n "prose_options_menu" .cursor/scripts/post_cursor_agent_author_gate_miss_detector.py` returns ≥2 hits.
- Status: ✅ DONE — grep returns 3 hits (lines 164, 223, 225)

DoD-2: The exact G1.P3 "Option A/B/C" response text scores miss_score ≥ 2 (detector fires).
- Evidence: TC-1 test confirms miss_score=3, `prose_options_menu` in positive_signals.
- Status: ✅ DONE

DoD-3: ≥8 new unit tests pass; zero existing test regressions.
- Evidence: `pytest tests/unit/windsurf/scripts/test_author_gate_prose_options_detection.py -v` → 27 passed, 0 failed. Existing 28 tests also pass.
- Status: ✅ DONE

DoD-4: `author-gate-enforcement.md` contains the "Prose Options Menu — Explicit Prohibition" block.
- Evidence: `grep -n "Prose Options Menu" .cursor/rules/author-gate-enforcement.md` returns line 53.
- Status: ✅ DONE

DoD-5: Memory writeback: this plan slug + pattern documented in memory for future sessions.
- Evidence: Deferred — no memory MCP call was made this session; pattern is self-documented via plan + rule + test.
- Status: ⚠️ DEFERRED (advisory only — plan and rule are authoritative SSOT)

---

## Scope Expansion Authorization

When scope is discovered during execution:

### Four-Step Discipline

Step 1: DISCOVERED_SCOPE marker
Step 2: AUTHORIZATION_DECISION marker
Step 3: Plan updates (if ACCEPTED)
Step 4: SCOPE_EXPANSION marker
