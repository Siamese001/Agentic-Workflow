---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\plan-wave-inline-status-sync-8b4d2f.md'
original_relative_path: '_archive\\2026-05\\plan-wave-inline-status-sync-8b4d2f.md'
source_sha256: edad0e450499b64da1de55010d08c33279c02d3293fff49cadf299087076932f
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: plan-wave-inline-status-sync-8b4d2f
plan_type: governance
touches_agentic_core: false
touches_governance_ci: false
touches_windsurf_rules: false
touches_plan_templates: true
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# Plan Wave Inline Status Sync — Fix Stale Per-Wave Prose Fields

Extend `_plan_wave_table_updater.py` to also update free-form inline status fields
(`WAVE_STATUS`, `WAVE_COMPLETE`, `PHASE_STATUS`, `PHASE_COMPLETE`, and DoD `- Status:` lines)
inside per-wave prose sections, eliminating the drift between plan headers and wave bodies
that left `author-gate-prose-options-detection-e7f2a3` stale after all waves completed.
**No agentic_core changes. No new CI gate.**

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: COMPLETED
CURRENT_WAVE: W3
LAST_COMPLETED_WAVE: W3
LAST_UPDATED: 2026-05-12

---

## Hardening Decisions (pre-implementation)

| # | Requirement | Decision |
|---|-------------|----------|
| 1 | DoD status form | Grep-verified: **only `- Status: <value>`** exists in all 25 plan files. `DoD-N Status:` form does not appear anywhere. Regex targets `^- Status:\s*` only. |
| 2 | Skip code fences / examples | Section splitter strips fenced code blocks (`\`\`\`...`\`\`\``) from the content before applying inline-field regexes. Fenced content is preserved verbatim in output. |
| 3 | Section parsing | `_split_wave_sections(text)` splits on `^##\s+Wave\s+\d+\b` (case-insensitive, `re.MULTILINE`). Returns list of `(header, body, start_offset)` tuples. Target section identified by wave number. Non-matching wave → `(True, "no matching wave section")` safe no-op. |
| 4 | Monotonic / idempotent | Transition table: `wave_start` only upgrades TODO→IN_PROGRESS (never degrades DONE). `wave_complete` upgrades TODO/IN_PROGRESS→DONE. `plan_complete` upgrades all non-DONE→DONE. Replay of any marker on already-DONE fields is a no-op. |
| 5 | wave_complete + child phases | `wave_complete` does **NOT** flip child `PHASE_STATUS`/`PHASE_COMPLETE` fields. Child phases are only updated by explicit `PHASE_COMPLETE:` markers. Test TC-9 proves this. `plan_complete` flips all remaining child fields. |
| 6 | Drift detection scope | `plan_driven_closer.parse_plan_file()` extended to scan `WAVE_STATUS`, `WAVE_COMPLETE`, `PHASE_STATUS`, `PHASE_COMPLETE`, and `- Status:` (DoD) inline fields. Any open value when header=COMPLETED → `plan_header_inline_drift`. |
| 7 | Negative tests | 8 negative/edge-case tests added (TC-N1..TC-N8) on top of 8 happy-path tests. |
| 8 | agentic_core | Not touched. Scope is `tools/windsurf/`, `.cursor/scripts/`, `tests/unit/windsurf/`. |
| 9 | Implementation receipt | W3 produces a receipt section with files, test commands, pass counts, before/after diff, and code-fence / table-row non-regression confirmations. |

---

## Context (SCQA)

- **Situation** — `post_cursor_agent_wave_lifecycle_capture.py` fires on `WAVE_COMPLETE:` /
  `PHASE_COMPLETE:` / `PLAN_COMPLETE:` markers and calls
  `_plan_wave_table_updater.update_wave_in_plan()`. That function updates pipe-table rows
  (Wave Structure table, Phase-Level Summary table) from `TODO` → `✅ DONE`.
- **Complication** — The execution-plan template also specifies **inline prose fields**
  inside each wave's prose section:
  ```text
  WAVE_STATUS: TODO        ← never touched by updater
  WAVE_COMPLETE: NO        ← never touched by updater
  PHASE_STATUS: TODO       ← inside phase bullet, never touched
  PHASE_COMPLETE: NO       ← inside phase bullet, never touched
  - Status: TODO           ← DoD bullet, never touched
  ```
  `_plan_wave_table_updater.py` uses `_ROW_RE` / `_PHASE_ROW_RE` which only match
  pipe-delimited table rows. Free-form prose lines are invisible to it.
  `plan_driven_closer.py` warns on header↔table drift but does not scan inline fields.
  Confirmed: `author-gate-prose-options-detection-e7f2a3.md` — `PLAN_STATUS: COMPLETED`
  set, but all wave-body fields read `TODO`/`NO` until manually corrected last session.
- **Question** — How do we keep inline prose fields in sync with wave/phase completion
  without global regex replace, code-fence corruption, or monotonicity violations?
- **Answer** — Add `_update_inline_fields_in_plan()` to `_plan_wave_table_updater.py`
  using section-scoped parsing with code-fence exclusion, monotonic transition guards,
  and explicit wave_complete/phase_complete/plan_complete dispatch; extend
  `plan_driven_closer.py` drift detection to cover all inline fields; add ≥16 tests
  including 8 negative cases.

---

## Wave Overview

**Waves**: 3 total (W1–W3)
**Total Estimate**: ~12K tokens
**Current**: W0 (pre-flight)

**Wave Manifest**:
- **W1** — Extend `_plan_wave_table_updater.py` with inline-field sync | ~5K tokens | Checkpoint A | STATUS: DONE
- **W2** — Extend `plan_driven_closer.py` drift detection + update template | ~3K tokens | Checkpoint B | STATUS: DONE
- **W3** — Tests + implementation receipts | ~4K tokens | Checkpoint C | STATUS: DONE

---

## Wave 1 — Extend `_plan_wave_table_updater.py`

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Authorization**: NOT_REQUIRED — single-file edit to `tools/windsurf/_plan_wave_table_updater.py`.

**Phases**:
- **W1.1** — Add `_split_wave_sections()`, `_strip_fenced_blocks()`, inline-field regex constants | ~2K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.2** — Implement `_update_inline_fields_in_plan()` with section-scoped dispatch and monotonic guard | ~2.5K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.3** — Wire `_update_inline_fields_in_plan()` into `update_wave_in_plan()` and `_update_phase_in_plan()` | ~0.5K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

### W1.1 — Section splitter and code-fence stripper

```python
# Split plan text into wave sections.
# Returns list of (wave_num: int | None, section_text: str, start: int, end: int).
# Sections before the first ## Wave N header get wave_num=None.
_WAVE_SECTION_HEADER_RE = re.compile(
    r"^(##\s+Wave\s+(\d+)\b[^\n]*)", re.MULTILINE | re.IGNORECASE
)

def _split_wave_sections(text: str) -> list[tuple[int | None, str, int, int]]:
    """Split text into (wave_num, text, start, end) tuples.
    wave_num=None for content before the first ## Wave N header."""
    ...

# Strip fenced code blocks before applying inline-field regexes.
# Returns (stripped_text, fence_map) where fence_map restores fences verbatim.
_FENCE_RE = re.compile(r"^```.*?^```", re.MULTILINE | re.DOTALL)

def _strip_fenced_blocks(text: str) -> tuple[str, list[tuple[int, int, str]]]:
    """Replace fenced code blocks with same-length whitespace placeholder.
    fence_map is list of (start, end, original) for restoration."""
    ...

def _restore_fenced_blocks(text: str, fence_map: list[tuple[int, int, str]]) -> str:
    """Restore fenced blocks from fence_map."""
    ...
```

### W1.2 — Inline field update dispatch

**Regex constants** (applied only to the non-fenced portion of a target section):

```python
# Standalone line fields (must start at column 0, not inside a table row)
_INLINE_WAVE_STATUS_RE = re.compile(r"^(WAVE_STATUS:\s*)(\S+)", re.MULTILINE)
_INLINE_WAVE_COMPLETE_RE = re.compile(r"^(WAVE_COMPLETE:\s*)(\S+)", re.MULTILINE)

# Phase bullet inline fields — match within phase bullet line only
# e.g.: - **W1.2** — Title | tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
_INLINE_PHASE_STATUS_RE = re.compile(r"(PHASE_STATUS:\s*)(\S+)")
_INLINE_PHASE_COMPLETE_RE = re.compile(r"(PHASE_COMPLETE:\s*)(\S+)")

# DoD status bullet: "- Status: TODO" (confirmed sole form in all 25 plan files)
_INLINE_DOD_STATUS_RE = re.compile(r"^(- Status:\s*)(\S+)", re.MULTILINE)
```

**Monotonic transition table** (checked before every substitution):

| Event | Field | Allowed source values | Target value |
|-------|-------|-----------------------|--------------|
| `wave_start` | `WAVE_STATUS` | `TODO`, `IN_PROGRESS` | `IN_PROGRESS` |
| `wave_start` | `WAVE_COMPLETE` | — | no change |
| `wave_complete` | `WAVE_STATUS` | `TODO`, `IN_PROGRESS` | `DONE` |
| `wave_complete` | `WAVE_COMPLETE` | `NO` | `YES` |
| `wave_complete` | `PHASE_STATUS` bullet | — | **no change** (see hardening #5) |
| `wave_complete` | `PHASE_COMPLETE` bullet | — | **no change** (see hardening #5) |
| `wave_complete` | `- Status:` (DoD, in section) | `TODO`, `IN_PROGRESS`, `BLOCKED` | `DONE` |
| `phase_complete` | `PHASE_STATUS` (matching phase ID) | `TODO`, `IN_PROGRESS` | `DONE` |
| `phase_complete` | `PHASE_COMPLETE` (matching phase ID) | `NO` | `YES` |
| `plan_complete` | all `WAVE_STATUS` | `TODO`, `IN_PROGRESS` | `DONE` |
| `plan_complete` | all `WAVE_COMPLETE` | `NO` | `YES` |
| `plan_complete` | all `PHASE_STATUS` | `TODO`, `IN_PROGRESS` | `DONE` |
| `plan_complete` | all `PHASE_COMPLETE` | `NO` | `YES` |
| `plan_complete` | all `- Status:` (DoD) | `TODO`, `IN_PROGRESS`, `BLOCKED` | `DONE` |

**Already-terminal values** (`DONE`, `YES`, `DEFERRED`, `RETIRED`, `ARCHIVED`) are
**never overwritten** by any event — idempotent replay guaranteed.

**`wave_complete` child-phase policy (hardening #5)**:
`wave_complete` does **not** flip `PHASE_STATUS`/`PHASE_COMPLETE` fields in phase
bullets. Only `PHASE_COMPLETE:` markers and `plan_complete` do. This preserves
visibility of stale child phases (they remain `TODO` as a signal that `PHASE_COMPLETE:`
markers were missing) rather than masking them. Test TC-N5 asserts this.

**Code-fence exclusion**:
Before applying any regex to a wave section body, call `_strip_fenced_blocks()`.
Apply all substitutions to the stripped copy, then call `_restore_fenced_blocks()`.
The final written content contains original fenced text unchanged.

**Duplicate `WAVE_ID` section handling**:
If `_split_wave_sections()` finds two sections with the same wave number, emit
`print(f"[inline_updater] WARN: duplicate Wave {wave} sections in {slug}; skipping",
file=sys.stderr)` and return `(True, "duplicate wave sections — skipped")`. No partial
corruption.

**Function signature**:
```python
def _update_inline_fields_in_plan(
    repo_root: Path,
    slug: str,
    wave: int,          # -1 for plan_complete (all waves)
    kind: str,          # wave_start | wave_complete | phase_complete | plan_complete
    phase_id: str = "", # only used for phase_complete
) -> tuple[bool, str]:
    ...
```

### W1.3 — Wire into existing call path

In `update_wave_in_plan()`, after the existing table-row loop and before the final
`write_text()` call, add:

```python
# Inline prose field sync (hardening plan-wave-inline-status-sync-8b4d2f)
ok2, msg2 = _update_inline_fields_in_plan(repo_root, slug, wave, kind)
if not ok2:
    _log(...)  # non-fatal
```

In `_update_phase_in_plan()`, similarly after the phase-table loop:

```python
ok2, msg2 = _update_inline_fields_in_plan(repo_root, slug, -1, "phase_complete",
                                           phase_id=phase)
```

The existing `write_text()` calls remain the sole file-write points — `_update_inline_fields_in_plan()` returns the modified content as a string (pure function); callers do the write.

**Refactor note**: to avoid double writes, restructure so both the table-row update
and the inline-field update operate on the same in-memory `content` string, then
write once. This is a same-wave-1 internal change — no API surface change.

**Acceptance**:
- `wave_complete` wave=2 updates `WAVE_STATUS`/`WAVE_COMPLETE` only inside `## Wave 2`
  section; `## Wave 1` and `## Wave 3` sections unchanged.
- `wave_complete` does not change `PHASE_STATUS`/`PHASE_COMPLETE` in any phase bullet.
- `plan_complete` updates all inline fields including DoD `- Status:` rows.
- Fenced code block content is byte-identical before and after any update.
- `wave_start` does not downgrade `WAVE_STATUS: DONE` to `IN_PROGRESS`.
- Duplicate wave sections: returns warning message, file unchanged.
- Existing pipe-table row updates (`✅ DONE`) still fire correctly after refactor.

---

## Wave 2 — Drift Detection + Template Update

WAVE_ID: W2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Authorization**: NOT_REQUIRED — extends existing `plan_driven_closer.py` drift warning
(no new CI gate, no new hook); updates plan template prose.

**Phases**:
- **W2.1** — Extend `plan_driven_closer.py` `parse_plan_file()` to scan all inline fields | ~2K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W2.2** — Update `execution-plan-template.md` Format Reference to note auto-maintenance | ~0.5K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W2.3** — Memory writeback for this pattern | ~0.5K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

### W2.1 — Inline drift scan in `parse_plan_file()`

Add to `parse_plan_file()` after the existing Markdown-table scan:

```python
# ── Inline field drift scan ──────────────────────────────────────────────
# Detects WAVE_STATUS / WAVE_COMPLETE / PHASE_STATUS / PHASE_COMPLETE / DoD
# fields that remain open when PLAN_STATUS says COMPLETED.
_INLINE_OPEN_VALUES = {"todo", "no", "in_progress", "in progress", "blocked"}

INLINE_SCAN_RES = [
    ("wave_status",    re.compile(r"^WAVE_STATUS:\s*(\S+)", re.MULTILINE)),
    ("wave_complete",  re.compile(r"^WAVE_COMPLETE:\s*(\S+)", re.MULTILINE)),
    ("phase_status",   re.compile(r"\bPHASE_STATUS:\s*(\S+)")),
    ("phase_complete", re.compile(r"\bPHASE_COMPLETE:\s*(\S+)")),
    ("dod_status",     re.compile(r"^- Status:\s*(\S+)", re.MULTILINE)),
]

# Strip fenced blocks before scanning (same helper as W1.1)
stripped, _ = _strip_fenced_blocks(text)

open_inline: list[str] = []
for field_name, pattern in INLINE_SCAN_RES:
    for m in pattern.finditer(stripped):
        val = m.group(1).strip().lower().rstrip(".,")
        if val in _INLINE_OPEN_VALUES:
            open_inline.append(f"{field_name}={m.group(1).strip()!r}")

if open_inline:
    status.inline_open_fields = open_inline  # new field on PlanStatus dataclass
```

In `reconcile()`, extend the existing `plan_header_table_drift` check:

```python
if hs == "done":
    has_inline_open = bool(getattr(plan, "inline_open_fields", []))
    if has_open_rows or has_open_waves or has_inline_open:
        warnings.append({
            "kind": "plan_header_inline_drift",
            "plan_file": plan_file,
            "header": plan.header_status,
            "open_inline_fields": getattr(plan, "inline_open_fields", [])[:20],
            "open_phases": [...],
            "open_waves": [...],
        })
```

**Scope**: only scans for informational drift warnings. Does not auto-repair.
`--show-drift` flag surfaces them. No Notion write.

### W2.2 — Template update

Under `### Required Per-Wave Markers` in Format Reference, append:

```
> **Auto-maintained**: `WAVE_STATUS`, `WAVE_COMPLETE`, `PHASE_STATUS`, `PHASE_COMPLETE`,
> and DoD `- Status:` fields are updated automatically by
> `post_cursor_agent_wave_lifecycle_capture.py` when `WAVE_COMPLETE:` / `PHASE_COMPLETE:` /
> `PLAN_COMPLETE:` markers are emitted. Manual edits are only needed if a marker was
> never emitted or the hook was bypassed (`WAVE_TABLE_UPDATE_BYPASS=1`).
```

**Acceptance**:
- `plan_driven_closer.py --show-drift` reports `plan_header_inline_drift` for a fixture
  where `PLAN_STATUS: COMPLETED` but `WAVE_STATUS: TODO` remains.
- Drift warning includes `open_inline_fields` list.
- Template documents auto-maintenance.
- Memory writeback entity created.

---

## Wave 3 — Tests + Implementation Receipts

WAVE_ID: W3
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Authorization**: NOT_REQUIRED — new test file only.

**Phases**:
- **W3.1** — New test file `tests/unit/windsurf/test_plan_wave_inline_status_sync.py` with ≥16 cases | ~3K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W3.2** — Run test suite; produce implementation receipts | ~0.5K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W3.3** — Run existing `_plan_wave_table_updater` smoke to confirm table-row regression-free | ~0.5K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

### Happy-path tests (TC-1..TC-8)

| Case | Input | Expected |
|------|-------|----------|
| TC-1 | `wave_complete` wave=2 on 3-wave plan | W2 section: `WAVE_STATUS: DONE`, `WAVE_COMPLETE: YES`; W1 and W3 sections unchanged |
| TC-2 | `wave_complete` wave=1 on plan with W1 already `WAVE_STATUS: DONE` | No field change; returns `(True, "no matching rows found/changed ...")` |
| TC-3 | `phase_complete` phase=W1.2 | Only `W1.2` bullet: `PHASE_STATUS: DONE`, `PHASE_COMPLETE: YES`; W1.1 bullet unchanged |
| TC-4 | `plan_complete` on plan with mixed wave statuses | All waves: DONE/YES; all phase bullets: DONE/YES; all DoD `- Status: TODO` → `DONE` |
| TC-5 | `wave_start` wave=3 on plan with W3 `WAVE_STATUS: TODO` | W3: `WAVE_STATUS: IN_PROGRESS`; `WAVE_COMPLETE: NO` unchanged |
| TC-6 | Existing table-row update (pipe table) still fires | `✅ DONE` in Wave Structure pipe-table row for wave_complete wave=2 |
| TC-7 | `wave_complete` on plan with DoD `- Status: TODO` inside W2 section | DoD row inside W2 → `DONE`; DoD rows inside W1 and W3 unchanged |
| TC-8 | `plan_driven_closer.parse_plan_file` on stale plan | Returns `inline_open_fields` non-empty; `reconcile()` emits `plan_header_inline_drift` |

### Negative / edge-case tests (TC-N1..TC-N8)

| Case | Input | Expected |
|------|-------|----------|
| TC-N1 | Plan text has fenced code block containing `WAVE_STATUS: TODO` | Field inside fence is NOT rewritten; only prose field is rewritten |
| TC-N2 | Plan text has Format Reference section with `WAVE_STATUS: TODO` example inside code fence | Not rewritten |
| TC-N3 | `wave_start` wave=1 on plan where W1 `WAVE_STATUS: DONE` | No downgrade; field stays `DONE` |
| TC-N4 | `phase_start` phase=W2.1 on plan where W2.1 `PHASE_STATUS: DONE` | No downgrade; field stays `DONE` |
| TC-N5 | `wave_complete` wave=2 on plan with W2 phases still `PHASE_STATUS: TODO` | WAVE_STATUS/WAVE_COMPLETE updated; phase bullet fields **remain** `TODO` (policy: wave_complete does not imply child phases done) |
| TC-N6 | Plan with no `## Wave 3` section, target wave=3 | Returns `(True, "no matching wave section for wave=3")`; file unchanged; no crash |
| TC-N7 | Plan with duplicate `## Wave 2` sections | Returns `(True, "duplicate wave sections — skipped")`; file unchanged; warning printed to stderr |
| TC-N8 | `plan_driven_closer.parse_plan_file` on plan with `PHASE_STATUS: TODO` and `- Status: TODO` when header=COMPLETED | `open_inline_fields` includes both `phase_status='TODO'` and `dod_status='TODO'` entries |

**Acceptance**:
- ≥16 test cases pass (TC-1..TC-8 + TC-N1..TC-N8).
- Zero regressions in existing `_plan_wave_table_updater` table-row tests (run via same
  pytest invocation).
- Implementation receipt section populated (see below).

---

## Implementation Receipt Template (populate in W3.2)

```
## Implementation Receipt

### Files Changed
| File | Change |
|------|--------|
| `tools/windsurf/_plan_wave_table_updater.py` | Added _split_wave_sections, _strip_fenced_blocks, _restore_fenced_blocks, _update_inline_fields_in_plan; wired into update_wave_in_plan + _update_phase_in_plan |
| `tools/windsurf/plan_driven_closer.py` | Extended parse_plan_file + reconcile with inline drift detection |
| `.cursor/templates/execution-plan-template.md` | Added auto-maintenance note under Required Per-Wave Markers |
| `tests/unit/windsurf/test_plan_wave_inline_status_sync.py` | NEW — 16 tests |

### Test Commands and Results
pytest tests/unit/windsurf/test_plan_wave_inline_status_sync.py -v
→ NN passed, 0 failed

pytest tests/unit/windsurf/ -v   (regression sweep)
→ NN passed, 0 failed

### Sample Before/After (e7f2a3 fixture, wave_complete wave=1)
BEFORE:
  WAVE_STATUS: TODO
  WAVE_COMPLETE: NO
  ...
  - Status: TODO

AFTER:
  WAVE_STATUS: DONE
  WAVE_COMPLETE: YES
  ...
  - Status: DONE   (DoD rows inside Wave 1 section only)

### Code-Fence Non-Regression Confirmation
Content of fenced blocks containing "WAVE_STATUS: TODO" is byte-identical
before and after update. Confirmed by TC-N1 and TC-N2.

### Table-Row Non-Regression Confirmation
Pipe-table Wave Structure row for wave=1 correctly shows ✅ DONE after
wave_complete. Confirmed by TC-6.
```

---

## Out Of Scope

- Any changes to `agentic_core/` — this is Windsurf plan lifecycle tooling only.
- New CI gate — `plan_driven_closer.py` drift detection is sufficient.
- Retroactive bulk-repair of stale plans — advisory `--show-drift` only.
- `post_cursor_agent_wave_completion_audit.py` — it audits for missing WAVE markers in
  Cursor Agent responses, not for plan file field state.
- `MISS_SCORE_THRESHOLD` or Author-Gate signal changes.

---

## Gap Register

**GAP-1: Section boundary vs non-standard headers**
`_split_wave_sections()` matches `^## Wave N` (case-insensitive). Plans using
`## W1 — Title` (no "Wave" keyword) will not match. These plans have no
`WAVE_STATUS:` prose fields (they use only pipe tables) so the inline updater
is a clean no-op. If future plans use both non-standard headers and inline fields,
a separate `WAVE_ID:` key scan can be added as a fallback (deferred, out of scope).

**GAP-2: Phase bullet scope within wave sections**
Phase bullet `PHASE_STATUS`/`PHASE_COMPLETE` updates for `phase_complete` are applied
globally by phase ID (e.g. `W1.2`). They do not need section scoping because phase IDs
are unique across the plan. This is safe and consistent with the existing `_PHASE_ROW_RE`
approach.

**GAP-3: DoD rows keyed by wave on `wave_complete`**
`wave_complete` flips DoD `- Status:` rows only within the target wave section (section
scoping via `_split_wave_sections()`). `plan_complete` flips all remaining DoD rows
globally. Test TC-7 verifies per-section DoD scoping.

---

## Definition of Done

DoD-1: `_plan_wave_table_updater.py` contains `_split_wave_sections`, `_strip_fenced_blocks`,
`_restore_fenced_blocks`, and `_update_inline_fields_in_plan`.
- Evidence: `grep -n "def _update_inline_fields_in_plan\|def _split_wave_sections\|def _strip_fenced_blocks" tools/windsurf/_plan_wave_table_updater.py` returns 3+ hits.
- Status: DONE

DoD-2: `wave_complete` wave=2 updates only W2 section inline fields; W1/W3 sections and
phase bullets unchanged. Code-fence content unchanged.
- Evidence: TC-1 and TC-N1 pass.
- Status: DONE

DoD-3: `plan_complete` updates all inline fields (WAVE, PHASE, DoD). `wave_start`/`wave_complete`
do not downgrade DONE fields. Duplicate sections produce warning, no corruption.
- Evidence: TC-4, TC-N3, TC-N4, TC-N7 pass.
- Status: DONE

DoD-4: Zero regressions — existing pipe-table row updates still fire after refactor.
- Evidence: `pytest tests/unit/windsurf/ -v` → 0 failures; TC-6 passes explicitly.
- Status: DONE

DoD-5: `plan_driven_closer.py` drift scan covers WAVE_STATUS, WAVE_COMPLETE, PHASE_STATUS,
PHASE_COMPLETE, and DoD `- Status:` fields. `--show-drift` reports `plan_header_inline_drift`
with full `open_inline_fields` list for stale plan fixture.
- Evidence: TC-8 and TC-N8 pass.
- Status: DONE

---

## Scope Expansion Authorization

When scope is discovered during execution:

### Four-Step Discipline

Step 1: DISCOVERED_SCOPE marker
Step 2: AUTHORIZATION_DECISION marker
Step 3: Plan updates (if ACCEPTED)
Step 4: SCOPE_EXPANSION marker
