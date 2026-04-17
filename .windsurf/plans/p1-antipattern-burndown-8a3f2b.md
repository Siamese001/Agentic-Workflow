# P1 Anti-Pattern Burndown Plan

Burn down 98 P1 anti-pattern violations in `.windsurf/scripts/` infrastructure files via three waves targeting different violation types. Zero production blast radius - all violations are in hook/auditor scripts executed by Windsurf, not imported by production code.

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | ALL_CAPS constants | 27 instances across 12 files | A | ~15K 🟢 |
| Wave 2 | Broad exception catching | 30 instances across 12 files | B | ~20K 🟢 |
| Wave 3 | Literal strings/regex | 6 instances across 4 files | C | ~10K 🟢 |

**Total: ~45K tokens across 3 waves, all GREEN**

---

## Phase-Level Summary

> **MANDATORY for T2/T3 plans.** A plan missing this table is invalid and must not be saved.

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| 1.1 | Rename ALL_CAPS constants to snake_case | pre_mcp_gate.py, pre_prompt_classifier.py, post_mcp_audit.py, post_cascade_hitl_capture.py, post_write_mcp_config_sync.py, post_cascade_adg_audit.py, post_run_audit.py, backfill_cat4_decisions.py, post_cascade_cleanup.py, post_setup_worktree.py, post_write_audit.py, pre_run_gate.py | PP-1: Mechanical renames, GAP-1: Zero production consumers | ~15K | 🔲 TODO |
| 1.2 | Verify Wave 1 fixes | Regenerate ADG, check P1 count | PP-2: ADG generation time (~120s), GAP-2: Ratchet ceiling adjustment | ~5K | 🔲 TODO |
| 2.1 | Replace broad exception catching with specific types | Same 12 files as Wave 1 | PP-3: Context-specific type selection, GAP-3: Guardian exemptions required | ~20K | 🔲 TODO |
| 2.2 | Verify Wave 2 fixes | Regenerate ADG, check P1 count | PP-4: ADG generation time, GAP-4: Ratchet ceiling adjustment | ~5K | 🔲 TODO |
| 3.1 | Evaluate and fix literal strings/regex | post_cascade_hitl_capture.py, post_cascade_adg_audit.py, post_write_mcp_config_sync.py, pre_prompt_classifier.py | PP-5: Case-by-case necessity evaluation, GAP-5: Some may be legitimate patterns | ~10K | 🔲 TODO |
| 3.2 | Verify Wave 3 fixes | Regenerate ADG, final P1 count check | PP-6: ADG generation time, GAP-6: Target P1 = 0 | ~5K | 🔲 TODO |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS · ✅ DONE · ❌ BLOCKED

---

## Gap Register

**GAP-1: Zero production consumers for infrastructure scripts**
- All P1 violations are in `.windsurf/scripts/` hook/auditor scripts
- ADG fan-in analysis confirms zero production imports
- Risk: Minimal - these are Windsurf-executed hooks, not production code paths

**GAP-2: Ratchet ceiling may need adjustment**
- P1 ceiling currently at 1086
- Wave 1 should reduce by ~27 violations
- May need ceiling bump if regressions occur from MCP hardening work

**GAP-3: Guardian exemptions for probe safety**
- Some broad exceptions in probe functions may require guardian comments
- Example: `pre_mcp_gate.py` probe functions use broad `Exception` to prevent gate crashes
- HITL approval required for new guardian exemptions per anti-pattern-hitl-gate.md

**GAP-4: Context-specific exception type selection**
- Cannot mechanically replace all `Exception` with specific types
- Requires case-by-case analysis of what exceptions each operation can raise
- Example: `OSError` for file I/O, `sqlite3.OperationalError` for DB operations

**GAP-5: Literal patterns may be legitimate**
- Regex patterns like `_ADG_MCP_CALL_RE` are intentional pattern matching
- Hard-coded paths like `D:\` are Windows-specific path literals
- Must evaluate each case for necessity vs anti-pattern status

**GAP-6: P1 target of zero may not be achievable**
- Some violations may be legitimate infrastructure patterns
- May need to allow-list certain patterns via anti-pattern-hitl-gate
- Final target may be >0 with documented exemptions

---

## Execution Plan

### Phase 1 — Wave 1: ALL_CAPS Constants
**Scope**: Rename ~27 ALL_CAPS constants to snake_case across 12 infrastructure scripts

**Constants to rename** (from ADG violations):
- `DB_PATH`, `SESSION_STATE`, `REPO_ROOT`, `SQLITE_PROBE_TIMEOUT_MS`
- `_PROBE_CACHE`, `ADG_WRITE_TOOLS`, `GITKRAKEN_WORKSPACE_ROOT`
- `_SESSION_STATE_MAX_AGE_HOURS`, `_ALLOWED_SCRIPT_SUFFIXES`
- `_FS_LAUNCHER`, `_FS_ALLOWED_DIR`
- `T3_KEYWORDS`, `T2_KEYWORDS`, `T1_KEYWORDS`, `T0_KEYWORDS`
- `_SR_MANDATE`, `_NOTION_SR_HINT`, `_OTEL_SR_HINT`, `_PYTEST_SR_HINT`, `_ADG_GRAPH_SR_HINT`
- `WINDSURF_DIR`, `NOTION_SERVER_NAME`, `_NOTION_API`, `_NOTION_VERSION`, `_DEFAULT_DB_ID`

**Commands**:
```bash
# Phase 1.1: Mechanical renames (edit each file)
# Example: DB_PATH → db_path, SESSION_STATE → session_state, etc.

# Phase 1.2: Regenerate ADG to verify
python tools/generate_full_adg.py
```

**Acceptance**: 
- P1 count reduces by ~27 (from 1086 to ~1059)
- No ratchet regression
- All hook scripts still execute correctly

---

### Phase 2 — Wave 2: Broad Exception Catching
**Scope**: Replace ~30 broad `Exception` and `OSError` catches with specific types

**Commands**:
```bash
# Phase 2.1: Replace with specific types per context
# File I/O → OSError, FileNotFoundError, PermissionError
# SQLite → sqlite3.OperationalError, sqlite3.DatabaseError
# JSON → json.JSONDecodeError
# Subprocess → subprocess.TimeoutExpired, subprocess.CalledProcessError
# Add guardian comments where broad exceptions are required for safety

# Phase 2.2: Regenerate ADG to verify
python tools/generate_full_adg.py
```

**Acceptance**:
- P1 count reduces by ~30 (from ~1059 to ~1029)
- No ratchet regression
- Probe functions still fail-safe (guardian comments where needed)

---

### Phase 3 — Wave 3: Literal Strings/Regex
**Scope**: Evaluate and fix ~6 literal string and regex pattern violations

**Commands**:
```bash
# Phase 3.1: Case-by-case evaluation
# _ADG_MCP_CALL_RE, _DEGRADED_FALLBACK_RE, _LITERAL_CONFIRM_PATTERNS → Keep (legitimate patterns)
# D:\ → Replace with Path handling or Windows path constants
# _CAPTURE_MARKER_RE, _PACKET_HEADER_RE → Keep (legitimate patterns)

# Phase 3.2: Regenerate ADG to verify
python tools/generate_full_adg.py
```

**Acceptance**:
- P1 count reduces by 2-4 (D:\ fixes only)
- Legitimate patterns documented via guardian comments or allow-list
- Final P1 count documented with exemptions

---

## Rules

- Constitutional §15: Precise exception handling - catch specific types
- Constitutional §8: Guardian exemptions require HITL approval via anti-pattern-hitl-gate.md
- Zero production blast radius - all changes are in infrastructure scripts
- ADG ratchet discipline - regenerate after each wave, adjust ceiling if needed
- MCP green light protocol - check ADG health before T2/T3 work (already verified)

---

## Success Criteria

- [ ] Wave 1: P1 reduced by ~27 (ALL_CAPS → snake_case)
- [ ] Wave 2: P1 reduced by ~30 (broad exceptions → specific types)
- [ ] Wave 3: P1 reduced by 2-4 (literal path fixes), remaining documented
- [ ] All ADG ratchets pass after each wave
- [ ] All hook scripts still execute correctly
- [ ] Guardian exemptions documented where required

---

## Implementation Commands

```bash
# Wave 1: ALL_CAPS constants
# Edit each file to rename constants (mechanical)
python tools/generate_full_adg.py  # Verify

# Wave 2: Broad exceptions
# Edit each file to replace with specific types (context-aware)
# Add guardian comments where needed
python tools/generate_full_adg.py  # Verify

# Wave 3: Literals/regex
# Evaluate case-by-case, fix D:\ literals
python tools/generate_full_adg.py  # Final verification
```

---

## Rollback Strategy

If things go wrong:
1. Git revert each wave's commit individually (isolated changes)
2. ADG snapshot rollback: restore previous `adg_indexed_*.sqlite` from artifacts/adg/
3. Ratchet ceiling rollback: manually adjust in anti-pattern detector config
4. Hook script verification: run `python .windsurf/scripts/pre_mcp_gate.py` with test payload

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| P1 reduction Wave 1 | -27 violations | ADG burndown table post-generation |
| P1 reduction Wave 2 | -30 violations | ADG burndown table post-generation |
| P1 reduction Wave 3 | -2 to -4 violations | ADG burndown table post-generation |
| Hook script correctness | All execute | Manual test with sample payloads |
| Ratchet compliance | Pass all waves | ADG generation exit code 0 |
