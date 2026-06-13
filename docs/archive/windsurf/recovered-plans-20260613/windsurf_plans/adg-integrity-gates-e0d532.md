# ADG Integrity Gates — P1/P2 Enforcement

Implement unconditional fail-fast gates for `in_cycle`/`dynamic_exec` (Tier 1), fix all Tier 2 pipeline-path swallow violations, wire Tier 2 path-scoped block gate, and record Tier 3 ratchet ceilings — producing a verifiably complete and topology-valid ADG baseline.

---

## Baseline Facts (from adg_indexed_04062026_1246.sqlite)

| Metric | Count |
|--------|-------|
| `in_cycle` edges | **0** ← Tier 1 gate can enable immediately |
| `dynamic_exec` edges | **0** ← Tier 1 gate can enable immediately |
| Tier 2 violations in `tools/generate/generate_full_adg.py` | 11 broad_exception_catch |
| Tier 2 violations in `tools/adg/mcp/server.py` | 10 broad_exception_catch |
| Tier 2 violations in `tools/adg/shared_modules/extracted_training_pipeline.py` | 24 broad_exception_catch + 24 return_none_swallow |
| Tier 3 ceiling `broad_exception_catch` (outside pipeline) | ~1,023 |
| Tier 3 ceiling `silent_exception_swallow` | ~227 |
| Tier 3 ceiling `log_and_swallow` | ~446 |
| Tier 3 ceiling `return_none_swallow` | ~162 |

---

## Wave Structure

| Wave | Phases | Focus | Est. Tokens | Status |
|------|--------|-------|------------|--------|
| W1 | P1–P2 | Tier 1 gate (`in_cycle` + `dynamic_exec`) in `_check_p1_defects` | 3K 🟢 | Pending |
| W2 | P3–P5 | Fix Tier 2 pipeline violations (generate_full_adg.py, server.py, extracted_training_pipeline.py) | 8K 🟢 | Pending |
| W3 | P6–P7 | Wire Tier 2 path-scoped block gate (`_check_p2_pipeline_integrity`) | 4K 🟢 | Pending |
| W4 | P8–P9 | Tier 3 ratchet ceiling — persist ceilings in snapshot, add `_check_p3_ratchet` | 4K 🟢 | Pending |
| W5 | P10 | Re-run ADG, validate all gates pass, commit | 2K 🟢 | Pending |

**Total: ~21K tokens across 5 waves, all GREEN**

---

## Gap Register

**GAP-1: Tier 1 — `in_cycle` / `dynamic_exec` not gated**
- `_check_p1_defects` only checks `violates` edges
- `in_cycle` = graph topology corruption; `dynamic_exec` = provably missing import edges
- Both should block unconditionally at `> 0`

**GAP-2: Tier 2 — Pipeline swallows not gated**
- `tools/generate/generate_full_adg.py` (11), `tools/adg/mcp/server.py` (10), `tools/adg/shared_modules/extracted_training_pipeline.py` (48) have broad catches/swallows
- These are inside the scanner/writer — exceptions suppress file/edge data, producing a silent incomplete graph
- No gate currently exists for pipeline-path swallows

**GAP-3: Tier 3 — No regression ratchet on P2 counts outside pipeline**
- 1,858 HIGH antipatterns across apps_*/agentic_core/L*/ — no ceiling enforced
- Count can grow silently without any signal

---

## Execution Plan

### Phase 1 — Extend `_check_p1_defects` for `in_cycle` (Tier 1A)
**Scope**: `tools/generate/generate_full_adg.py` — add `in_cycle` edge count query from SQLite; block if `> 0`

**Acceptance**: `_check_p1_defects` called with routing_summary containing `in_cycle > 0` → `sys.exit(1)`

---

### Phase 2 — Extend `_check_p1_defects` for `dynamic_exec` (Tier 1B)
**Scope**: Same function — add `dynamic_exec` edge count; block if `> 0`

**Acceptance**: `_check_p1_defects` called with `dynamic_exec > 0` → `sys.exit(1)`; tests added for both

---

### Phase 3 — Fix Tier 2: `tools/generate/generate_full_adg.py` (11 broad catches)
**Scope**: Replace broad `except Exception` with specific exception types or re-raise; add error logging without swallowing

**Files**: `tools/generate/generate_full_adg.py`

**Acceptance**: `broad_exception_catch` count in pipeline path = 0; tests for specific error paths pass

---

### Phase 4 — Fix Tier 2: `tools/adg/mcp/server.py` (10 broad catches)
**Scope**: Replace broad catches with specific exception types; ensure MCP tool errors surface rather than silently return empty

**Files**: `tools/adg/mcp/server.py`

**Acceptance**: `broad_exception_catch` count in `tools/adg/mcp/server.py` = 0

---

### Phase 5 — Fix Tier 2: `tools/adg/shared_modules/extracted_training_pipeline.py` (48 violations)
**Scope**: Fix 24 broad_exception_catch + 24 return_none_swallow; replace with specific exceptions + explicit error returns

**Files**: `tools/adg/shared_modules/extracted_training_pipeline.py`

**Acceptance**: Both violation types = 0 in that file

---

### Phase 6 — Implement `_check_p2_pipeline_integrity` gate
**Scope**: New function in `generate_full_adg.py` — queries SQLite violations table for Tier 2 sub-types scoped to pipeline paths (`tools/adg/`, `tools/generate/`, `agentic_core/adg/`); blocks if `> 0`

**Logic**:
```
pipeline_paths = ['tools/adg/', 'tools/generate/', 'agentic_core/adg/']
swallow_types = [broad_exception_catch, silent_exception_swallow, log_and_swallow, return_none_swallow]
if any count > 0 in those paths → sys.exit(1)
```

**Acceptance**: Gate added; test for block + test for clean pass

---

### Phase 7 — Wire Tier 2 gate into generation flow
**Scope**: Call `_check_p2_pipeline_integrity(sqlite_path)` after SQLite is written (post artifact generation)

**Acceptance**: Gate fires on dirty pipeline path; generation completes on clean pipeline path

---

### Phase 8 — Implement `_check_p3_ratchet` + persist ceilings
**Scope**: Read current Tier 3 counts from SQLite; compare to ceiling stored in latest snapshot JSON; block if any count exceeds ceiling; write ceilings into new snapshot on clean run

**Ceiling values** (to seed from current run):
- `broad_exception_catch`: 1,023
- `silent_exception_swallow`: 227
- `log_and_swallow`: 446
- `return_none_swallow`: 162

**Acceptance**: Ratchet gate added; test for ceiling exceeded = block; test for at/below ceiling = pass

---

### Phase 9 — Wire Tier 3 ratchet into generation flow
**Scope**: Call `_check_p3_ratchet(sqlite_path, snapshot_path)` after Tier 2 gate; persist updated ceilings into snapshot on success

**Acceptance**: Full gate chain: P1 → Tier1 → Tier2 pipeline → Tier3 ratchet → generation proceeds

---

### Phase 10 — Re-run ADG + validate all gates
**Scope**: Run `python tools/generate/generate_full_adg.py`; verify exit 0; run full test suite on modified files

**Acceptance**:
- ADG generation completes (exit 0)
- All 3 tiers of gates present in code
- `in_cycle = 0`, `dynamic_exec = 0` verified from new SQLite
- Tier 2 pipeline violations = 0
- Tier 3 ceilings recorded in snapshot
- All modified test files pass full-file pytest

---

## Rules

- No changes outside `tools/generate/generate_full_adg.py`, `tools/adg/mcp/server.py`, `tools/adg/shared_modules/extracted_training_pipeline.py`, and direct test files
- No guardian exemptions without Author-Gate approval
- Tier 2 fixes must use specific exception types — no broad `except Exception` replacement with another broad catch
- All gates must have tests: block path + clean path
- No full test suite run until Phase 10

---

## Success Criteria

- [ ] Tier 1A: `in_cycle > 0` blocks ADG generation
- [ ] Tier 1B: `dynamic_exec > 0` blocks ADG generation
- [ ] Tier 2: 0 pipeline-path swallow violations in `tools/adg/`, `tools/generate/`, `agentic_core/adg/`
- [ ] Tier 2 gate: `_check_p2_pipeline_integrity` fires on dirty pipeline path
- [ ] Tier 3: Ratchet ceilings seeded and persisted in snapshot
- [ ] Tier 3 gate: `_check_p3_ratchet` blocks when ceiling exceeded
- [ ] ADG generation completes clean with all gates live (exit 0)
- [ ] All modified test files pass full-file pytest
