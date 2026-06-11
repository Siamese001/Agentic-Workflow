---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\author-gate-bandit-arrow2-closure-d7c4e9.md'
original_relative_path: 'author-gate-bandit-arrow2-closure-d7c4e9.md'
source_sha256: 4b8fb79e34f1c1cb9e31c0a73cb9d800f3d47ecc9459f2e39a20a30ac618aabe
recovered_status: SURVIVED_IN_CURRENT
last_commit: '315fd11926d'
last_commit_date: '2026-05-06 06:26:53 -0400'
created_date: '2026-05-04'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Author-Gate Bandit Arrow-2 Closure

- **Plan ID**: `author-gate-bandit-arrow2-closure-d7c4e9`
- **Tier**: T2 (two files edited + one new test file)
- **Created**: 2026-05-04
- **Status**: Completed

---

## Problem Statement

`tools/meta_learning/author_gate_consumer.py` writes `bandit_state.json` correctly (Arrow 1 ✅), but `.windsurf/skills/author-gate-packet-builder/emit_packet.py` and `precedent_injector.py` **never read** that file. As a result, `AUTHOR_GATE_PACKET` carries no bandit-derived proof fields (`bandit_prior`, `confidence_source`, `causal_use_receipt`). Arrow 2 is broken: the test plan cannot prove "bandit_state.json → future AuthorGate confidence/depth".

**Scope:** Close Arrow 2 with the smallest safe change. Do not refactor routing logic. Do not touch `lookup_refactor_decisions.py`. Do not conflate precedent lookup with bandit learning.

---

## Current Pipeline Audit

| Arrow | From → To | Status |
|---|---|---|
| 1 | `decisions` + `decision_outcomes` (SQLite) → `bandit_state.json` via `author_gate_consumer.py --apply` | ✅ Implemented |
| 2 | `bandit_state.json` → `AUTHOR_GATE_PACKET` fields (`bandit_prior`, `confidence_source`, `causal_use_receipt`) | ❌ BROKEN — file never read |
| 3 | Packet C (bandit) differs from Packet B (precedent-only) on explicit fields | ❌ IMPOSSIBLE until Arrow 2 closed |

**Existing test coverage relevant to this plan:**

| Test | Location | Covers |
|---|---|---|
| `test_bandit_update` | `tests/unit/author_gate_hardening/test_author_gate_hardening.py` W4.P4.1 | `update_bandit()` math (alpha/beta/mean). Does NOT cover `_load_bandit_prior` or packet attachment. |
| `test_lookup_refactor_decisions.py` | `tests/unit/windsurf/skills/` | FTS5 precedent lookup. Unaffected. |
| None | — | `emit_packet.build_packet()` has zero existing unit tests |
| None | — | `test_author_gate_meta_learning_e2e.py` does not exist yet |

---

## Wave Structure

| Wave | Phase | Focus | Est. Tokens | Status |
|---|---|---|---|---|
| W1 | P1 | Add `_load_bandit_prior()` + attach proof fields in `emit_packet.py` | ~300 | ✅ Done |
| W2 | P2 | Create `tests/unit/tools/meta_learning/test_author_gate_meta_learning_e2e.py` with A/B/C causal proof + 6 fallback tests (10 tests total) | ~600 | ✅ Done |
| W3 | P3 | Verify: run new tests, confirm existing tests unaffected | ~100 | ✅ Done |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| P1 | Bandit reader + packet attachment | `.windsurf/skills/author-gate-packet-builder/emit_packet.py` | Must be fail-soft; must not fake confidence; must not touch routing or precedent logic | ~300 | ✅ Done |
| P2 | A/B/C causal test + fallback tests | `tests/unit/tools/meta_learning/test_author_gate_meta_learning_e2e.py` (new); `tests/unit/tools/meta_learning/__init__.py` (new stub) | Needs in-memory ledger seeding + consumer `--apply` path + monkeypatching `BANDIT_STATE_PATH` in emit_packet. `_load_bandit_prior` returns `tuple[dict\|None, str, bool]` so receipt gets precise reason codes. | ~600 | ✅ Done |
| P3 | Verify + regression guard | Run `pytest tests/unit/tools/meta_learning/ tests/unit/author_gate_hardening/ tests/unit/windsurf/skills/` | No regressions on existing 299-line test file; no regressions on lookup tests | ~100 | ✅ Done |

---

## Exact Implementation

### P1 — `emit_packet.py` changes

**File:** `.windsurf/skills/author-gate-packet-builder/emit_packet.py`

**Change 1 — Add constant (after existing `PRECEDENT_SCRIPT` line ~57):**
```python
BANDIT_STATE_PATH = (
    REPO_ROOT / ".windsurf" / "state" / "refactor_decisions" / "bandit_state.json"
)
```

**Change 2 — Add function (before `build_packet`):**

Signature: `_load_bandit_prior(decision_type, reason_code) -> tuple[dict | None, str, bool]`

Return shape: `(cell_or_None, reason_code_str, bandit_state_was_read)`

This three-value return lets `build_packet` populate `causal_use_receipt.reason` with the exact failure code without a second file-existence check at call site.

Required reason codes (exhaustive):
- `bandit_prior_attached` — cell found and valid
- `bandit_state_missing` — file does not exist
- `bandit_state_invalid` — file exists but JSON is malformed or not a dict
- `bandit_cells_invalid` — file parsed but `cells` key absent or not a dict
- `bandit_cell_missing` — `cells` is a dict but the key is absent
- `bandit_cell_invalid` — key present but value is not a dict or missing required fields

```python
def _load_bandit_prior(
    decision_type: str,
    reason_code: str = "",
) -> tuple[dict[str, Any] | None, str, bool]:
    """Read per-cell Beta posterior from bandit_state.json.

    Returns (cell_or_None, reason_code, bandit_state_was_read).
    Never raises. Does not fake confidence when state is absent.

    reason_code values:
        bandit_prior_attached  — cell found and attached
        bandit_state_missing   — file absent
        bandit_state_invalid   — file present but JSON malformed or not a dict
        bandit_cells_invalid   — JSON parsed but cells key absent/not a dict
        bandit_cell_missing    — cells dict present but key absent
        bandit_cell_invalid    — key present but cell malformed
    """
    if not BANDIT_STATE_PATH.exists():
        return None, "bandit_state_missing", False
    try:
        raw = json.loads(BANDIT_STATE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None, "bandit_state_invalid", True
    if not isinstance(raw, dict):
        return None, "bandit_state_invalid", True
    cells = raw.get("cells")
    if not isinstance(cells, dict):
        return None, "bandit_cells_invalid", True
    key = f"{decision_type}|{reason_code or 'unknown'}"
    cell = cells.get(key)
    if cell is None:
        return None, "bandit_cell_missing", True
    if not isinstance(cell, dict):
        return None, "bandit_cell_invalid", True
    required = {"alpha", "beta", "mean", "ci95_width"}
    if not required.issubset(cell.keys()):
        return None, "bandit_cell_invalid", True
    # n is optional. If absent but alpha/beta are numeric, derive it.
    alpha = cell.get("alpha")
    beta = cell.get("beta")
    n = cell.get("n")
    if n is None and isinstance(alpha, (int, float)) and isinstance(beta, (int, float)):
        n = max(0, int(alpha + beta - 2))
    result = {"cell_key": key, **cell}
    result["n"] = n  # may be None only if alpha/beta are non-numeric (malformed)
    return result, "bandit_prior_attached", True
```

**Change 3 — In `build_packet()`, after `precedent = _fetch_precedent(...)` (line ~389), add:**
```python
bandit_cell, bandit_reason, bandit_state_read = _load_bandit_prior(
    decision_type, spec.get("reason_code") or ""
)
```

**Change 4 — In the `packet = {...}` dict (after `"precedent": precedent,`), add:**
```python
"bandit_prior": bandit_cell,
"confidence_source": "bandit_state" if bandit_cell is not None else "cold_prior",
"causal_use_receipt": {
    "bandit_state_read": bandit_state_read,
    "bandit_cell_found": bandit_cell is not None,
    "bandit_cell_key": (bandit_cell or {}).get("cell_key"),
    "precedent_verdict": precedent.get("verdict"),
    "reason": bandit_reason,
},
```

**Total change: ~60 lines. Minimal read-only instrumentation plus packet proof fields. No routing, precedent lookup, or scoring behavior changes.**

**Explicit non-changes:**
- `confidence_score` on candidates is NOT adjusted by bandit — that is a separate explicit change.
- `suggestion_depth` is NOT adjusted — bandit posterior is attached as evidence, not applied as a scoring modifier, in this pass.
- `precedent` key is NOT renamed or modified.
- `lookup_refactor_decisions.py` is NOT touched.
- `precedent_injector.py` is NOT touched.

---

### P2 — New test file

**New files:**
- `tests/unit/tools/meta_learning/__init__.py` (empty stub)
- `tests/unit/tools/meta_learning/test_author_gate_meta_learning_e2e.py`

#### Schema DDL for test fixture

Reuse the exact same `_SEED_DDL` pattern from `tests/unit/windsurf/skills/test_lookup_refactor_decisions.py` (which already creates `decisions`, `decision_scope`, `decision_outcomes`, `decisions_fts`). Add one extra column needed by the consumer:

```sql
ALTER TABLE decisions ADD COLUMN reason_code TEXT;
```

#### Shared fixture: `_make_seeded_ledger(tmp_path)`

Creates `tmp_path/ledger.sqlite` with 3 `refactor_scope` rows:
- `dec_s1`: `promote=1, rollback=0, regression=0` → success
- `dec_s2`: `promote=1, rollback=0, regression=0` → success
- `dec_s3`: `promote=0, rollback=1, regression=0` → failure

All with `reason_code = "override_recommendation"`. FTS5 populated via trigger or explicit INSERT into `decisions_fts`.

#### How `build_packet` is called in tests

`build_packet` is imported via `importlib.util.spec_from_file_location`. The `BANDIT_STATE_PATH` constant is monkeypatched on the imported module to point to `tmp_path/bandit_state.json`. Similarly, `_fetch_precedent` is monkeypatched to avoid real subprocess calls (returns `{"verdict": "none", ...}` for cold; returns `{"verdict": "suggestive", ...}` for seeded-ledger scenarios). `_context_fingerprint` is monkeypatched to avoid git calls.

Minimum valid `spec` input:
```python
{
    "decision_type": "refactor_scope",
    "normalized_intent": "extract bandit test",
    "reason_code": "override_recommendation",
    "files_in_scope": [],
    "candidates": [
        {
            "id": "minimal",
            "thesis": "smallest change",
            "confidence_score": 0.80,
            "principle_at_stake": "test",
            "what_youd_miss": "nothing",
            "what_would_flip": "blast_radius > 5",
            "key_tradeoffs": ["risk of rework", "scope creep"],
        }
    ],
}
```

#### Test cases (10 total)

**A/B/C causal tests (3):**

| Test | Setup | Assertions |
|---|---|---|
| `test_scenario_a_cold_ledger_no_bandit_state` | Empty ledger, `tmp_path/bandit_state.json` absent, precedent returns `verdict=none` | `packet["bandit_prior"] is None`; `packet["confidence_source"] == "cold_prior"`; `packet["causal_use_receipt"]["bandit_state_read"] is False`; `packet["causal_use_receipt"]["bandit_cell_found"] is False`; `packet["causal_use_receipt"]["reason"] == "bandit_state_missing"` |
| `test_scenario_b_precedent_only_no_bandit_state` | Seeded ledger (3 decisions + outcomes), `bandit_state.json` absent, precedent returns `verdict=suggestive` | `packet["precedent"]["verdict"] == "suggestive"`; `packet["bandit_prior"] is None`; `packet["confidence_source"] == "cold_prior"`; `packet["causal_use_receipt"]["bandit_cell_found"] is False` |
| `test_scenario_c_full_bandit` | Same seeded ledger; run `author_gate_consumer.main(["--db", str(db), "--state", str(state_path), "--apply"])`; `bandit_state.json` now present; build packet | `packet["bandit_prior"] is not None`; `packet["bandit_prior"]["alpha"] == 3.0`; `packet["bandit_prior"]["beta"] == 2.0`; `abs(packet["bandit_prior"]["mean"] - 3/5) < 0.001`; `packet["bandit_prior"]["ci95_width"] > 0`; `packet["confidence_source"] == "bandit_state"`; `packet["causal_use_receipt"]["bandit_state_read"] is True`; `packet["causal_use_receipt"]["bandit_cell_found"] is True`; `packet["causal_use_receipt"]["reason"] == "bandit_prior_attached"` |

**Causal diff assertion (1):**

| Test | Assertion |
|---|---|
| `test_scenario_c_differs_from_b_on_bandit_fields` | Build both B and C packets (same ledger, same spec — only difference is whether `bandit_state.json` exists). Assert `packet_c["bandit_prior"] != packet_b["bandit_prior"]` and `packet_c["confidence_source"] != packet_b["confidence_source"]`. Fail message: "bandit_state.json is not causally influencing the future packet — Arrow 2 not closed." |

**Fallback safety tests (6):**

All fallback tests call `_load_bandit_prior` directly (no need to invoke `build_packet`). They assert on the full `(cell, reason, state_read)` tuple.

| Test | Input | Expected `(cell, reason, state_read)` |
|---|---|---|
| `test_load_bandit_prior_file_missing` | `bandit_state.json` absent | `(None, "bandit_state_missing", False)` |
| `test_load_bandit_prior_invalid_json` | file contains `"not json{{"` | `(None, "bandit_state_invalid", True)` |
| `test_load_bandit_prior_cells_not_dict` | `{"cells": "wrong_type"}` | `(None, "bandit_cells_invalid", True)` |
| `test_load_bandit_prior_cell_missing` | `{"cells": {"other_type|unknown": {...}}}` — key absent | `(None, "bandit_cell_missing", True)` |
| `test_load_bandit_prior_valid_cell_returned` | Valid cell with `refactor_scope|override_recommendation`; `n` present in JSON | `cell` has `cell_key`, `alpha`, `beta`, `mean`, `ci95_width`, `n`; reason=`"bandit_prior_attached"`; state_read=`True` |
| `test_load_bandit_prior_no_reason_code_falls_back_to_unknown` | Valid state with `refactor_scope|unknown` key; called with `reason_code=""` | Returns the `unknown`-keyed cell; reason=`"bandit_prior_attached"` |

**Additional assertion in `test_load_bandit_prior_valid_cell_returned`** — `n` tolerance:
- When `n` is absent from the JSON cell but `alpha=3.0`, `beta=2.0`, assert `cell["n"] == 3` (i.e. `max(0, int(3+2-2)) = 3`).
- When `n` is present in the JSON (e.g. `n=2`), assert `cell["n"] == 2` (JSON value wins).

---

## Remaining Gap After This Pass

This plan explicitly does **not** adjust `confidence_score` on individual candidates or `suggestion_depth` based on the bandit posterior. Those are a separate explicit change with a separate Author-Gate decision. The current pass only:

1. Reads the posterior and attaches it as evidence fields.
2. Sets `confidence_source` so auditors and tests can distinguish cold-prior from bandit-informed packets.
3. Provides `causal_use_receipt` so the causal chain is traceable.

**What remains for a follow-on plan (not in scope here):**
- Adjust per-candidate `confidence_score` or `raw_score` using `bandit_cell["mean"]` as a prior signal in `_attach_signal_vectors()`.
- Define `suggestion_depth` as a packet-level field (e.g., `deep` / `moderate` / `shallow`) derived from `ci95_width` — narrower CI → deeper suggestion.
- Add `confidence_band` mapping (e.g., mean > 0.75 → `high`, 0.5–0.75 → `moderate`, < 0.5 → `low`).

---

## Test Command

```
pytest tests/unit/tools/meta_learning/test_author_gate_meta_learning_e2e.py \
       tests/unit/author_gate_hardening/test_author_gate_hardening.py \
       tests/unit/windsurf/skills/test_lookup_refactor_decisions.py \
       -v
```

Expected: 10 new + existing passing, 0 failures.

---

## Pass/Fail Criteria

| Criterion | Expected after this plan |
|---|---|
| `bandit_state.json` read by `emit_packet.py` | ✅ |
| `AUTHOR_GATE_PACKET` carries `bandit_prior` | ✅ |
| `AUTHOR_GATE_PACKET` carries `confidence_source` | ✅ |
| `AUTHOR_GATE_PACKET` carries `causal_use_receipt` | ✅ |
| Packet C differs from Packet B on bandit fields | ✅ |
| Missing / malformed `bandit_state.json` does not crash | ✅ |
| No fake confidence when state absent | ✅ (`confidence_source == "cold_prior"`) |
| `confidence_score` / `suggestion_depth` adjusted | ❌ Deferred to follow-on plan |
| Existing `test_author_gate_hardening.py` regressions | 0 regressions |
| Existing `test_lookup_refactor_decisions.py` regressions | 0 regressions |

---

## Files Changed

| File | Change type | Notes |
|---|---|---|
| `.windsurf/skills/author-gate-packet-builder/emit_packet.py` | Edit | Add `BANDIT_STATE_PATH`, `_load_bandit_prior()`, 3 packet fields |
| `tests/unit/tools/meta_learning/__init__.py` | New | Empty stub |
| `tests/unit/tools/meta_learning/test_author_gate_meta_learning_e2e.py` | New | 10 tests: A/B/C + causal diff + 6 fallback |

**Production files NOT changed:** `precedent_injector.py`, `lookup_refactor_decisions.py`, `author_gate_consumer.py`, `render_card.py`, `post_cascade_author_gate_capture.py`, schema files, any CI gate.
