---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\heal_bug_inventory_plan.md'
original_relative_path: 'heal_bug_inventory_plan.md'
source_sha256: fad066690a00544b5c6279867dabfe15424ad6b01d23eaf8994a35a57844fd53
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-04'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Heal Run Bug Inventory & Fix Plan

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Bug Inventory (from AGGREGATE JSON + source audit)

### BUG-1 (CRITICAL): Wrong agent in `agents["location"]` registry
- **File**: `agentic_core/L0_routing/scripts/execute_ssot.py` line 5155
- **Root cause**: `agents["location"] = LocationValidatorAgent` — this class intentionally raises
  `NotImplementedError` from `heal_repository()`. Every `suggested_agent="location"` violation
  dispatched to Phase 2 crashes with `NotImplementedError`, is caught by the outer `except`, and
  logged as a failure. Zero location violations ever healed.
- **Fix**: Replace `LocationValidatorAgent` with `LocationHealerAgent` in the `agents` dict and
  add `LocationHealerAgent` to `_get_l5_agent_roster()`.

### BUG-2 (CRITICAL): `violations_fixed` always 0 in all reports
- **Root cause**: `compliance_report.get("stats", {}).get("violations_fixed", 0)` reads from the
  ArchitectureGovernor compliance_report. Phase 2 reconciliation result (`reconciliation_log`)
  is never fed back into `compliance_report["stats"]["violations_fixed"]`. The cert builds
  `violations_fixed` from stale pre-heal stats, not from what Phase 2 actually fixed.
- **Fix**: Pass Phase 2 `reconciliation_result["violations_fixed"]` into the cert builder so the
  final count is accurate.

### BUG-3 (HIGH): LOCATION violations show `file: "unknown"` in aggregate
- **Root cause**: `location_violations` stored in state are tuples `(Path, str)`. When the
  tuple serialisation path hits `str(loc_violation)` (the `else` branch at line 3282), the whole
  tuple stringifies to `"(PosixPath(...), 'msg')"` but `file_path` is set to `"unknown"`. The
  tuple branch at line 3278-3280 works, but dict violations from `location_scan_result` go through
  a separate code path that loses the `file` key.
- **Fix**: Normalise the violation-to-dict conversion so all shapes produce a `file` key with the
  actual path string.

### BUG-4 (HIGH): JSON write corruption — backslash escape error
- **Root cause**: Windows paths written verbatim into JSON (`"C:\\Git\\..."`) cause
  `json.decoder.JSONDecodeError: Invalid \escape` on re-read when `default=str` serialises a
  `WindowsPath` to `C:\Git\...` without escaping the backslashes. The `default=str` call on
  `Path` objects produces raw backslashes.
- **Fix**: In `save_comprehensive_reports` and `save_aggregate_report`, normalise all `Path`
  objects to forward-slash strings (`path.as_posix()`) before serialising, or use
  `json.dumps(..., ensure_ascii=False)` with explicit path conversion.

### BUG-5 (MEDIUM): `_get_l5_agent_roster` imports `LocationValidatorAgent` but never `LocationHealerAgent`
- **Root cause**: Roster function only imports the validator. `LocationHealerAgent` is never
  imported at the call-site, so even after fixing the registry key in BUG-1 it would fail at
  `agents = {...}` when the name is undefined.
- **Fix**: Add `LocationHealerAgent` import to `_get_l5_agent_roster` and return it.

### BUG-6 (MEDIUM): `suggested_agent="location"` violations dispatched to Phase 2 but Phase 1 already attempts healing via `heal_violations()` on the validator
- **Root cause**: Phase 1 calls `location_validator.heal_violations(violations, ...)` — which
  succeeds (LocationValidatorAgent has `heal_violations`? No — it only has `heal()`). Then the
  same violations are also sent to Phase 2 with `suggested_agent="location"`. Double-dispatch.
- **Verify**: Confirm whether `LocationValidatorAgent` has `heal_violations`. If not, Phase 1
  silently skips healing (`hasattr` guard). Either way Phase 2 should use LocationHealerAgent.

## Fix Plan (ordered)

| Step | ID | Action | File | Scope |
|------|----|--------|------|-------|
| P1 | BUG-1+5 | Add `LocationHealerAgent` to `_get_l5_agent_roster` + fix `agents["location"]` | execute_ssot.py | 2 lines |
| P2 | BUG-2 | Thread Phase 2 `violations_fixed` count back into cert builder | execute_ssot.py | ~5 lines |
| P3 | BUG-3 | Normalise location violation file-path extraction for dict violations | execute_ssot.py | ~10 lines |
| P4 | BUG-4 | Convert Path objects to posix strings before JSON serialisation | execute_ssot.py | 2 lines |
| P5 | Tests | Add regression tests covering all 4 bugs | tests/unit_min_deps/ | new test class |

## Acceptance Criteria
- `agents["location"]` resolves to `LocationHealerAgent`
- `LocationHealerAgent.heal_repository()` is callable (no NotImplementedError)
- `violations_fixed` in per-territory certs reflects actual Phase 2 fixes
- LOCATION violation dicts always have a non-`"unknown"` `file` key when path is available
- `compliance_report_*.json` re-readable by `json.load()` without escape errors
- All existing tests pass

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

