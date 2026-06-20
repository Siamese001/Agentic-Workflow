---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\author-gate-enforcement-fix-c9d4e2.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\author-gate-enforcement-fix-c9d4e2.md'
source_sha256: d68a2c51c0b33275689b2c4495149c2d7571e077c25769a8bbb8b0d612b5194b
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Author-Gate Enforcement Fix — Implementation Plan

**Plan ID:** `author-gate-enforcement-fix-c9d4e2`  
**Status:** Not Started  
**Parent Plan:** `author-gate-deferred-scope-b8c1d4` (W1 shadow→block)  
**Created:** 2026-05-09  
**Estimated Tokens:** ~8,000

---

## Problem Statement

Author-Gate is currently not reliably firing because:
1. **enforcement is set to shadow** — matched triggers log but return 0 instead of blocking
2. **Tier-1/Tier-2 classification returns early** before trigger evaluation for sensitive paths
3. **blast_radius_fan_in_min is declared but not implemented** against ADG fan-in
4. **layer_crossing detection is path-heuristic only** and misses real architectural crossings
5. **sensitive governance paths need a tier override** so they cannot bypass as "harmless single-file edits"

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|------|-----------|-------|-------------|--------|------------------|
| W1 | P1.1-P1.3 | Enforcement mode (shadow→block) | 1,500 | ⬜ | block mode exits 2 with AUTHOR_GATE_REQUIRED |
| W2 | P2.1-P2.4 | Tier bypass hardening + sensitive paths | 2,000 | ⬜ | Sensitive single-file edits trigger Author-Gate |
| W3 | P3.1-P3.5 | ADG blast-radius implementation | 2,500 | ⬜ | fan_in >= threshold triggers; missing ADG fails closed |
| W4 | P4.1-P4.3 | ADG-backed layer crossing | 1,500 | ⬜ | Cross-layer detected via ADG with path fallback |
| W5 | P5.1-P5.2 | Active decision ledger + bypass | 500 | ⬜ | Matching fingerprint passes; non-matching triggers |
| W6 | P6.1-P6.4 | Comprehensive test suite | 2,000 | ⬜ | 25+ new tests, all green |
| W7 | P7.1-P7.2 | Verification + integration | 1,000 | ⬜ | Self-test passes, dry-run shows triggers |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|---------------|-------------|--------|
| P1.1 | Change default enforcement to block | author_gate_triggers.yaml | Preserving shadow as option | 500 | ⬜ |
| P1.2 | Update pre_author_gate.py main() | pre_author_gate.py | Exit code handling | 500 | ⬜ |
| P1.3 | Add enforcement validation to self-test | pre_author_gate.py | Test coverage | 500 | ⬜ |
| P2.1 | Define sensitive path patterns | author_gate_triggers.yaml | Path glob design | 500 | ⬜ |
| P2.2 | Implement sensitive path detection | pre_author_gate.py | check_tier() modification | 800 | ⬜ |
| P2.3 | Add sensitive_path_override trigger | author_gate_triggers.yaml | Trigger definition | 400 | ⬜ |
| P2.4 | Test sensitive path enforcement | test_pre_author_gate.py | Edge cases | 300 | ⬜ |
| P3.1 | ADG artifact discovery | pre_author_gate.py | SQLite path resolution | 500 | ⬜ |
| P3.2 | Implement fan_in lookup | pre_author_gate.py | Query proj_centrality | 800 | ⬜ |
| P3.3 | Integrate blast_radius_fan_in_min | pre_author_gate.py | Trigger evaluation | 700 | ⬜ |
| P3.4 | Fail-closed on missing/stale ADG | pre_author_gate.py | Degraded mode | 300 | ⬜ |
| P3.5 | Blast radius receipts | pre_author_gate.py | Logging format | 200 | ⬜ |
| P4.1 | ADG layer lookup | pre_author_gate.py | Query proj_nodes | 500 | ⬜ |
| P4.2 | Layer crossing with ADG fallback | pre_author_gate.py | Hybrid detection | 600 | ⬜ |
| P4.3 | Cross-layer receipts | pre_author_gate.py | Logging format | 400 | ⬜ |
| P5.1 | Active decision matching | pre_author_gate.py | has_active_decision() | 300 | ⬜ |
| P5.2 | Bypass condition audit | pre_author_gate.py | check_bypass() | 200 | ⬜ |
| P6.1 | Shadow mode tests | test_pre_author_gate.py | Mock triggers | 600 | ⬜ |
| P6.2 | Block mode tests | test_pre_author_gate.py | Exit code assertions | 600 | ⬜ |
| P6.3 | Tier bypass + sensitive path tests | test_pre_author_gate.py | Path fixtures | 500 | ⬜ |
| P6.4 | Blast radius + layer crossing tests | test_pre_author_gate.py | ADG mocking | 800 | ⬜ |
| P7.1 | Self-test verification | pre_author_gate.py | --self-test | 400 | ⬜ |
| P7.2 | Dry-run verification | pre_author_gate.py | --dry-run --verbose | 600 | ⬜ |

---

## Files to Modify

### Primary Changes
1. **`.windsurf/scripts/pre_author_gate.py`** (752 lines)
   - Change enforcement default handling (line 721-745)
   - Modify `check_tier()` to check sensitive paths before early return (line 405-429)
   - Add `is_sensitive_path()` helper
   - Add `get_adg_fan_in()` helper for ADG queries
   - Modify `evaluate_trigger()` to handle `blast_radius_fan_in_min` (line 450-509)
   - Add `get_layers_from_adg()` helper
   - Modify `_layers_in_changed_files()` with ADG fallback (line 432-447)
   - Add receipt logging for ADG-backed decisions

2. **`.windsurf/schemas/author_gate_triggers.yaml`** (208 lines)
   - Change `enforcement: shadow` → `enforcement: block` (line 17)
   - Add `sensitive_path_override` trigger (new)
   - Document `blast_radius_fan_in_min` feature (line 64)
   - Add `tier_override` stanza for sensitive paths

### Test Files
3. **`tests/unit/windsurf_scripts/test_pre_author_gate.py`** (new file, ~800 lines)
   - Comprehensive test coverage for all 7 requirement categories
   - Mock ADG fixtures for fan_in and layer queries
   - Parametrized tests for bypass conditions

4. **`tests/unit/windsurf_scripts/test_pre_author_gate_integration.py`** (new file, ~400 lines)
   - Integration tests with real ADG artifacts
   - SQLite fixture setup/teardown

---

## Files to Create

| File | Purpose | Size |
|------|---------|------|
| `tests/unit/windsurf_scripts/test_pre_author_gate.py` | Main test suite | ~800 lines |
| `tests/unit/windsurf_scripts/test_pre_author_gate_integration.py` | Integration tests | ~400 lines |
| `tests/unit/windsurf_scripts/fixtures/adg_mock.py` | ADG mocking helpers | ~200 lines |
| `.windsurf/schemas/author_gate_triggers_v2.yaml` | Schema backup/validation | 208 lines |

---

## Assumptions About ADG Data

### ADG Artifact Location
- **Canonical ADG**: `artifacts/adg/adg_indexed_<ts>.sqlite` (source of truth)
- **Graph Projection**: `artifacts/adg/adg_graph_<ts>.sqlite` (pre-computed metrics)
- **Discovery**: Latest file by timestamp suffix

### Relevant Tables
```sql
-- For fan_in lookup
SELECT fan_in, blast_radius_direct 
FROM proj_centrality 
WHERE adg_name LIKE '%/path/to/file.py';

-- For layer lookup  
SELECT layer 
FROM proj_nodes 
WHERE resolved_path = 'path/to/file.py';
```

### Fallback Strategy
1. Try `adg_graph_*.sqlite` (has pre-computed `proj_centrality`)
2. If stale/missing, try `adg_indexed_*.sqlite` direct query
3. If both fail, emit `DEGRADED_FALLBACK` and use path heuristic only

---

## Implementation Details

### 1. Enforcement Mode (W1)

**Current (shadow)**:
```python
enforcement = str(cfg.get("enforcement", "shadow")).lower()
if enforcement == "shadow":
    append_violation({...})  # Logs only
    return 0  # Does NOT block
```

**Target (block)**:
```python
enforcement = str(cfg.get("enforcement", "block")).lower()  # Changed default
if enforcement == "shadow":
    append_violation({...})
    return 0
# Fall through to emit_author_gate_required() which exits 2
```

**YAML change**:
```yaml
enforcement: block  # Changed from shadow
```

### 2. Tier Bypass Hardening (W2)

**New sensitive path patterns**:
```python
SENSITIVE_PATH_PATTERNS = [
    ".windsurf/rules/*",
    ".windsurf/schemas/*",
    ".windsurf/scripts/pre_author_gate.py",
    "apps_rg/config/*",
    "agentic_core/L5_safety/*",
    "agentic_core/L4_state/*",
    "docs/reference/00A_L5_Governance_Safety/*",
    "docs/reference/00B_L4_State_Archive_and_UWG/*",
    "docs/reference/00C_Runtime_Gates_Current_Run_Mesh/*",
]
```

**Modified check_tier()**:
```python
def check_tier(cfg, snap):
    # Check sensitive paths FIRST
    if _touches_sensitive_path(snap.changed_files + snap.deleted_files):
        return "tier_3"  # Force trigger evaluation
    
    # Existing tier logic...
    if snap.files_changed == 0:
        return "tier_1"
    # ... rest unchanged
```

### 3. ADG Blast-Radius (W3)

**New helper**:
```python
def get_adg_fan_in(file_path: str) -> tuple[int | None, str]:
    """Return (fan_in, artifact_source) or (None, error_msg)."""
    backend = GraphProjectionBackend()
    if not backend.is_available():
        return None, "projection_unavailable"
    if backend.is_stale():
        return None, "projection_stale"
    
    # Try to find node by resolved_path
    # Query proj_centrality for fan_in
    # Return value + provenance
```

**Trigger integration**:
```python
if "blast_radius_fan_in_min" in feats:
    fan_in, provenance = get_adg_fan_in(changed_file)
    if fan_in is None:
        if not cfg.get("allow_degraded_mode", False):
            return True  # Fail closed - treat as trigger
    elif fan_in >= feats["blast_radius_fan_in_min"]:
        return True
```

### 4. ADG-Backed Layer Crossing (W4)

**New helper**:
```python
def get_layers_from_adg(files: list[str]) -> tuple[set[str], str]:
    """Return (layers_set, source) where source is 'adg' or 'path_fallback'."""
```

**Modified layer detection**:
```python
def _layers_in_changed_files(files: list[str]) -> tuple[set[str], str]:
    # Try ADG first
    layers, source = get_layers_from_adg(files)
    if layers:
        return layers, source
    
    # Path fallback (existing logic)
    return _layers_from_path_heuristic(files), "path_fallback"
```

### 5. Receipt Format

**ADG-backed blast radius receipt**:
```
BLAST_RADIUS_TRIGGER: file=agentic_core/L3_orchestration/pipeline.py 
    fan_in=15 threshold=10 
    adg_artifact=adg_graph_05052026_0722.sqlite 
    trigger_id=HITL-1.3
```

**Layer crossing receipt**:
```
LAYER_CROSSING_TRIGGER: files_span=[L0_routing, L5_safety] 
    detection_source=adg 
    trigger_id=HITL-1.1
```

---

## Test Coverage Matrix

| Test Category | Test Count | Key Scenarios |
|---------------|------------|---------------|
| A. Shadow mode | 3 | Would-block logs, returns 0, no AUTHOR_GATE_REQUIRED |
| B. Block mode | 4 | Exits 2, emits marker, increments counters, escalation |
| C. Tier bypass | 5 | Normal single-file passes, sensitive triggers, multi-layer |
| D. Blast radius | 6 | Below threshold, at threshold, missing ADG, stale ADG |
| E. Layer crossing | 4 | Same-layer passes, ADG cross-layer, path fallback |
| F. Sensitive paths | 4 | Each path pattern triggers correctly |
| G. Active decisions | 3 | Matching fingerprint passes, non-matching triggers, expired |
| H. Bypass conditions | 4 | Whitespace, commit message, session match |

---

## Verification Commands

After implementation, run:

```bash
# 1. Self-test
python .windsurf/scripts/pre_author_gate.py --self-test

# 2. Dry-run verbose
python .windsurf/scripts/pre_author_gate.py --dry-run --verbose

# 3. Targeted unit tests
python -m pytest tests/unit/windsurf_scripts/test_pre_author_gate.py -v

# 4. Integration tests (with real ADG)
python -m pytest tests/unit/windsurf_scripts/test_pre_author_gate_integration.py -v

# 5. Regression on existing author-gate tests
python -m pytest tests/unit/author_gate/ -v
python -m pytest tests/unit/author_gate_hardening/ -v

# 6. Hook regression
python -m pytest tests/unit/windsurf/scripts/ -v -k "author_gate"
```

---

## Remaining Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| ADG projection stale/missing | Medium | Fail-closed logic + degraded mode config |
| Sensitive path false positives | Low | Precise glob patterns + tests |
| Performance regression (ADG queries) | Low | Query timeout (5s) + caching |
| Existing bypasses broken | Low | Preserve all bypass conditions |
| Tier-2 workflows disrupted | Medium | Shadow mode still available via env var |

---

## Acceptance Criteria Checklist

- [ ] Author-Gate cannot silently pass sensitive governance edits (Tier-2 hardening)
- [ ] enforcement: block actually blocks with AUTHOR_GATE_REQUIRED and exits 2
- [ ] blast_radius_fan_in_min is real, ADG-backed, and test-covered
- [ ] layer_crossing is ADG-backed where possible, path fallback otherwise
- [ ] shadow mode remains available (configurable, not default)
- [ ] All changes are small, local, and test-backed (25+ new tests)
- [ ] Sensitive edit example: Editing `.windsurf/rules/ssot-folder-enforcement.md` (single file) now triggers Author-Gate
- [ ] Low-risk edit example: Editing `tests/unit/test_foo.py` still passes in Tier-2

---

## Non-Goals (Explicitly Out of Scope)

1. No changes to `emit_packet.py` or `render_card.py` (packet shape stable)
2. No changes to runtime HITL (ADR-023) — this is developer-loop only
3. No new trigger types beyond `sensitive_path_override`
4. No changes to Author-Gate UI renderer
5. No changes to decision ledger schema
6. No removal of existing bypass conditions
7. No changes to hooks.json wiring (pre_write_code stays)

---

## Dependencies

- `tools/adg/core/graph_projection_backend.py` (existing, for ADG queries)
- `pyyaml` (existing, for trigger config)
- `sqlite3` (stdlib, for ADG reads)

---

## Related Memory References

- Memory `6e7e9afe` — author-gate-deferred-scope-b8c1d4 (W1/W2 tracking)
- Memory `f220bb61` — author-gate-four-req-enforcement-c4d2a8 (UI discipline)
- Memory `da4a7d9a` — SSOT folder routing discipline
- Memory `3ba710ed` — Notion plans status enforcement (pattern reference)

---

## Gap Register

| Gap ID | Description | Owner | Resolution Path |
|--------|-------------|-------|-----------------|
| G1 | ADG query timeout edge cases | @cascade | P3.4 degraded mode |
| G2 | Windows vs POSIX path matching in sensitive paths | @cascade | P2.2 normalize paths |
| G3 | Concurrent ADG writes during read | @cascade | SQLite WAL mode |
| G4 | Test isolation for ADG-dependent tests | @cascade | Mock backend fixture |

---

## Plan Metadata

- **Files In Scope**: `.windsurf/scripts/pre_author_gate.py`, `.windsurf/schemas/author_gate_triggers.yaml`, `tests/unit/windsurf_scripts/test_pre_author_gate*.py`
- **Files Not In Scope**: Anything in `agentic_core/L5_safety/` (runtime HITL), `emit_packet.py`, `render_card.py`
- **Estimated Duration**: 1-2 sessions
- **Review Required**: Yes — Author-Gate behavior change
- **Rollback Plan**: Revert YAML enforcement value, restore check_tier() early return logic

---

*End of Implementation Plan*
