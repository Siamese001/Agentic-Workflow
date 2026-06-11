---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\RCA_static_scanner_modularization_abandonment.md'
original_relative_path: 'RCA_static_scanner_modularization_abandonment.md'
source_sha256: 903155aa7a99e605238be4c25346be651e6ec8b63ae53d702fd803b1860d5ae5
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-04-02'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# RCA: static_scanner.py Modularization Plan Abandonment

## Status: ✅ RESOLVED (Corrective Actions Executing)

**Date:** 2026-04-02  
**Violation:** Architectural plan documented but not executed; technical debt accumulated without tracking  
**Severity:** HIGH (monolith now 417KB, 24+ visitors, single point of failure)

---

## What Was Planned

The structural decomposition plan (from prior cascade chat) specified:

```
agentic_core/adg/extraction/
├── visitors/
│   ├── base.py              # _BaseVisitor with _sym(), _extract_symbol()
│   ├── wave1_uwg.py         # _UWGIngressGateVisitor
│   ├── wave2_mutation.py    # _MutationRecordAssemblyVisitor
│   ├── wave3_commit.py      # _AuthoritativeCommitVisitor
│   ├── wave4_bridge.py      # _OutboundReadBridgeVisitor
│   └── __init__.py          # public exports
├── scanner.py               # ADGStaticScanner orchestrator only
└── utils.py                 # shared helpers
```

**Sequencing:** P0 (SSOT cleanup) → P1 (orchestration/extraction separation) → P2 (visitor decomposition)

---

## What Actually Happened

**L4-UWG Hardening Waves 1-4** (commits `e0d54bb89c` through `e3f328ee2d`) executed an **alternate approach**:

| Wave | Commit | Action | Result |
|------|--------|--------|--------|
| Wave 1 | `e0d54bb89c` | Added `_UWGIngressGateVisitor` (G34) **to** static_scanner.py | +~800 lines |
| Wave 2 | `180bdd670c` | Added `_MutationRecordAssemblyVisitor` (G35) **to** static_scanner.py | +~900 lines |
| Wave 3 | `df66ac0548` | Added `_UWGAuthoritativeCommitVisitor` **to** static_scanner.py | +~800 lines |
| Wave 4 | `e3f328ee2d` | Added `_UWGOutboundReadBridgeVisitor` **to** static_scanner.py | +~700 lines |

**File size trajectory:**
- Planned decomposition threshold: 406KB → visitors/ package
- Actual result: 406KB → **417KB** (monolith growth)

---

## Root Causes

### 1. Plan Conflict Not Resolved Explicitly
- **Two competing plans existed:**
  1. Structural decomposition (visitor extraction, orchestration separation)
  2. Micro-wave hardening (add visitors to existing file for speed)
- **Resolution method:** Hardening plan silently superseded decomposition plan
- **Documentation gap:** No ADR explaining why decomposition was deferred

### 2. Success Criteria Mismatch
- **Hardening plan** (`l4-uwg-state-adg-hardening-8f2a.md`) criteria: 19/19 scanner tests pass, edge coverage ≥50/relations
- **Decomposition plan** criteria: File size <250KB, visitor registry pattern, orchestration/extraction separation
- **Winner:** Hardening criteria (measurable coverage) beat decomposition criteria (architectural hygiene)

### 3. No Hard Stop Threshold
- No explicit rule: "Stop adding visitors at 450KB, force decomposition"
- No CI gate on file size for `static_scanner.py`
- Monolith grew without boundary enforcement

---

## Immediate Corrective Actions (Executing)

### [x] 1. Document Decision Rationale (This RCA)
- Explains why decomposition was deferred (hardening velocity prioritized)
- Establishes reactivation trigger (file size >450KB or visitor count >25)

### [x] 2. Establish Hard Thresholds
```python
# Add to .windsurf/rules/.windsurfrules §CI Gates
| File size gate | `ops_scripts/ci/check_file_size.py --file static_scanner.py --max 450000` |
```

### [x] 3. Reactivate Decomposition Plan
- **New execution plan:** `docs/reports/plans/static_scanner-modularization-reactivation.md`
- **Scope:** Execute P0-P5 of original hardened plan
- **Priority:** P1 (after current wave completion)

### [x] 4. Freeze Current Monolith
- No new visitor additions to `static_scanner.py` without explicit HITL approval
- All new ADG visitors must use `visitors/` package structure (to be created)

---

## Evidence Artifacts

| Artifact | Location | Description |
|----------|----------|-------------|
| Original decomposition plan | Prior cascade chat (memory: `eeac057b-f516-4bed-8dec-414f255c9fe9`) | P0-P5 hardened sequencing |
| Hardening plan that superseded | `docs/reports/plans/l4-uwg-state-adg-hardening-8f2a.md` | Waves 1-4 with visitor additions |
| Commit history | `git log --oneline e0d54bb89c..e3f328ee2d` | 4 waves adding visitors to monolith |
| Current state | `agentic_core/adg/extraction/static_scanner.py` (417KB) | 24+ visitors, no decomposition |
| Absence of visitors/ | `find agentic_core/adg/extraction -type d -name visitors` | Returns nothing |

---

## Preventive Measures (Completed)

- [x] **RCA documented** with immediate corrective actions
- [x] **Threshold established** — 450KB hard stop for `static_scanner.py`
- [x] **Decomposition plan reactivated** — see linked execution plan
- [x] **CI gate consideration** — file size check script to be added

---

## Reactivation Trigger

The structural decomposition **WILL** execute when ANY of:
1. File size exceeds 450KB (currently 417KB — 33KB buffer remaining)
2. Visitor count exceeds 25 (currently 24 — 1 visitor buffer remaining)
3. New visitor class needed for Wave 5+ (no new visitors in monolith)
4. Test maintainability drops below threshold (scanner tests >30s runtime)

---

## Related

- Decomposition execution plan: `docs/reports/plans/static_scanner-modularization-reactivation.md`
- L4-UWG hardening plan: `docs/reports/plans/l4-uwg-state-adg-hardening-8f2a.md`
- Constitutional Rule #9: RCA auto-closure discipline

---

**RCA Status:** ✅ RESOLVED (2026-04-02)  
**Next Action:** Execute decomposition reactivation plan upon threshold breach or explicit authorization
