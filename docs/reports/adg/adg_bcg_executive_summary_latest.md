## ADG Executive Brief

### BCG Executive Brief

- **North star:** Maintain SVP engineer-level repo standards: executive decisions, explicit prioritization, and technical evidence a layperson can follow.
- **Decision status:** REPORT_INCONSISTENT
- **Emit status:** PASS
- **Business read:** ADG is REPORT_INCONSISTENT: Repair report consistency first; the executive order of work is not trustworthy until graph and report agree. Repair report consistency before treating blocker order as authoritative.
- **Technical evidence:**
  - ADG source: C:\Users\amita\AppData\Local\Temp\pytest-of-amita\pytest-2967\test_clean_certification_run_r0\snap.sqlite (snapshot snap)
  - FIX gates: 0; burn-down gates: 0; KPI/watchlist gates: 0
  - KPI split: foundation blockers not loaded; P0 audit net 0; P0 live gate drivers 0
  - Missing or empty runtime proof is a measurement gap (blind spot), not automatically a product failure, unless an artifact shows runtime failure evidence.
  - Testing is a control gap where unknown lacks unit, regression coverage; fund tests with the relevant fix slice, not as a generic test campaign.
  - GraphDB/MV signals drive decisions only when the studied structural risk (centrality, blast radius, reverse deps, cones, chokepoints, SCC, newly-introduced paths) overlaps a blocker, testing exposure, ratchet, or planned slice; raw counts alone stay diagnostic.
  - Action rows emitted: 1
- **Priority rule:** Decision queue: repair consistency, then remove concrete P0 hard stops/regressions; do not let high-volume P3 hygiene outrank P0 safety/governance gates.

Decision gate:

| Gate | Why it matters | Evidence | Required before ranking |
|------|----------------|----------|-------------------------|
| Repair graph/report consistency | The executive order is not decision-grade until graph and report agree. | 2 graph/report mismatch row(s) block decision-grade ordering. | Repair report consistency, then rerun ADG before treating the ranked work queue as authoritative. |

Fix now:

| Priority | Move | Why it matters | Evidence | Next step |
|---------:|------|----------------|----------|-----------|
| 1 | Fund mapped tests for unknown | Testing exposure in a high-risk surface can reduce more delivery risk than blind ratchet burn-down. | Add mapped tests/unit, tests/regression coverage for unknown. | Add mapped tests before touching this surface again. |

Next step: Repair graph/report consistency first.

### 1. What ADG Is

ADG is the X-ray of the codebase. It maps code connections and lets the system ask health-check questions automatically. It turns 'is this codebase healthy?' from opinion into measured facts.

### 2. Patient Size

This patient has 28895 Python files: 23662 production files and 5233 test files. agentic_core contributes 2891 files; apps_* contributes 1456 files. Current snapshot/run ID: 06292026_0101.

### 3. Executive Decision

ADG is REPORT_INCONSISTENT: Repair report consistency first; the executive order of work is not trustworthy until graph and report agree. This is a material_risk; do not chase Do not rank work by raw MV row count alone., Do not let ordinary FIX gates hide report inconsistency or runtime failure..

### 3A. KPI Scorecard — Decision vs Audit

P0 is split into three ledgers: foundation blockers, audit inventory, and live gate drivers.

Do not add these counts together. A P0 audit finding is not a foundation blocker unless it comes from the foundation-blocker wave plan.

| KPI | Value | Plain-English meaning | Action rule |
|---|---|---|---|
| Foundation blockers | not loaded | P0 trust hazards that can make ADG evidence incomplete, unstable, or misleading. | Stop the line if greater than zero; if not loaded, do not claim clean. |
| P0 audit net | 0 | P0 severity audit inventory after guardian exemptions. | Audit-only unless mapped to a failing gate, runtime failure, hotspot, or changed code. |
| P0 live gate drivers | 0 | Current red P0 gates that can drive today's work order. | Can drive priority when the gate is FIX/red and decision-linked. |

Zero foundation blockers can coexist with nonzero P0 audit net because they measure different ledgers: run-trust hazards versus severity audit inventory.

| Band | Audit gross | Guardian / exempted | Audit net | Foundation blockers | Live gate drivers | Action role |
|---|---|---|---|---|---|---|
| P0 | 0 | 0 | 0 | not loaded | 0 | Stop-the-line only if foundation blockers are present; otherwise audit net is evidence to map. |
| P1 | 0 | 0 | 0 | n/a | 0 | Severity inventory to map to a failing gate, hotspot, changed code, or owner. |
| P2 | 0 | 0 | 0 | n/a | 0 | Severity inventory to map to a failing gate, hotspot, changed code, or owner. |
| P3 | 0 | 0 | 0 | n/a | 0 | Severity inventory to map to a failing gate, hotspot, changed code, or owner. |

### 4. Lens 0 — Foundation Blockers

Foundation blockers are P0 trust hazards: if this artifact is missing, leaders cannot see whether the graph itself is structurally trustworthy.

P0 wave-plan JSON was not loaded; do not claim there are no foundation blockers.

| Foundation signal | Count | Plain-English meaning |
|---|---:|---|
| Layer violations | 0 | Wrong-way dependencies across protected architecture layers. |
| Circular imports | 0 | Modules depend on each other in a loop, making load order brittle. |
| Dynamic execution | 0 | Code is executed dynamically, which can make graph evidence incomplete. |
| Protected surfaces | 0 | Cracks in routing, execution, orchestration, or safety surfaces. |

| Foundation blocker | File | Line | Layer path | Wrong-way? | Protected? | Fan-in | Recommended action |
|---|---|---|---|---|---|---|---|
| None |  | 0 |  | False | False | 0 | No foundation-blocker action required. |

Action impact:

| Signal | Action impact | Recommended action |
|---|---|---|
| none | No immediate action impact. | Load the emitted P0 wave-plan JSON before trusting this lens. |

### 5. Gap Analysis — Lens 1: Health Gates

Health gates tell leaders whether the run is green, blocked, carrying owned burn-down debt, or merely showing KPI/watchlist signals.

FIX blocks green; BURN is accepted work; KPI is trend/watchlist; CLEAR needs no action. A blocked ADG run is not automatically a platform crisis; regression delta and graph/test linkage determine urgency.

| Bucket | Count | Executive meaning |
|---|---:|---|
| CLEAR | 0 | No action now. |
| BURN | 0 | Owned backlog; burn down after red gates. |
| KPI | 0 | Watchlist/trend only; no burn-down unless planned. |
| FIX | 0 | Current blocker or regression requiring action before decision-grade green. |

| Red gate | Total records | Regression / new delta | Executive read | Next action |
|---|---:|---:|---|---|
| None | 0 | 0 | No red gates. | No blocker action. |

Action impact:

| Signal | Action impact | Recommended action |
|---|---|---|
| none | No immediate action impact. | No red-gate action required. |

KPI / watchlist signals:

| Signal | Rows | Executive read | Recommended action |
|---|---|---|---|
| None | 0 | No KPI/watchlist signal was promoted. | No KPI action. |

### 6. Gap Analysis — Lens 2: Runtime Proof / Observability

Runtime proof separates a real observed failure from a blind spot; leaders should not treat missing traces as proof of health.

Missing or empty runtime proof is a measurement gap (blind spot), not automatically a product failure, unless an artifact shows runtime failure evidence.

| Runtime proof signal | Status | Executive read | Action |
|---|---|---|---|
| runtime_spine | missing | Measurement blind spot; not automatically a product failure. | Enable or repair artifact emission if the decision needs runtime proof. |
| graphdb_queries | missing | Measurement blind spot; not automatically a product failure. | Enable or repair artifact emission if the decision needs runtime proof. |
| structural_outputs | missing | Measurement blind spot; not automatically a product failure. | Enable or repair artifact emission if the decision needs runtime proof. |

Action impact:

| Signal | Action impact | Recommended action |
|---|---|---|
| runtime_spine | Measurement blind spot; not automatically a product failure. | Enable or repair artifact emission if the decision needs runtime proof. |
| graphdb_queries | Measurement blind spot; not automatically a product failure. | Enable or repair artifact emission if the decision needs runtime proof. |
| structural_outputs | Measurement blind spot; not automatically a product failure. | Enable or repair artifact emission if the decision needs runtime proof. |

### 7. Gap Analysis — Lens 3: Product / App Risk

Product risk shows whether a structural issue touches user-facing app behavior, not just internal cleanup.

No app-specific product gap was promoted in this run; app risk remains diagnostic-only unless tied to a hotspot, gate, or action queue row.

| App / product scope | Risk | Evidence | Executive read | Next action |
|---|---|---|---|---|
| None | No app-specific product gap was promoted in this run |  | App risk remains diagnostic-only unless tied to a hotspot, gate, or action queue row. | Monitor. |

Action impact:

| Signal | Action impact | Recommended action |
|---|---|---|
| none | No immediate action impact. | No product-scope action promoted. |

### 8. Gap Analysis — Lens 4: Testing Control Gaps

Tests are the control that prove a risky fix actually works; missing mapped tests turn every red-gate fix into a repeat-risk.

Testing is a control gap where unknown lacks unit, regression coverage; fund tests with the relevant fix slice, not as a generic test campaign.

| Rank | Production scope | Current tests found | Missing test scope | Risk | Recommended investment | Trigger |
|---:|---|---|---|---|---|---|
| 1 | unknown | none mapped | unit, regression | HIGH | Add mapped tests/unit, tests/regression coverage for unknown. | hotspot coverage MV / test inventory |
| 2 | unknown | none mapped | unit, regression | HIGH | Add mapped tests/unit, tests/regression coverage for unknown. | hotspot coverage MV / test inventory |
| 3 | unknown | none mapped | unit, regression | HIGH | Add mapped tests/unit, tests/regression coverage for unknown. | hotspot coverage MV / test inventory |
| 4 | unknown | none mapped | unit, regression | HIGH | Add mapped tests/unit, tests/regression coverage for unknown. | hotspot coverage MV / test inventory |
| 5 | unknown | none mapped | unit, regression | HIGH | Add mapped tests/unit, tests/regression coverage for unknown. | hotspot coverage MV / test inventory |
| 6 | unknown | none mapped | unit, regression | HIGH | Add mapped tests/unit, tests/regression coverage for unknown. | hotspot coverage MV / test inventory |
| 7 | unknown | none mapped | unit, regression | HIGH | Add mapped tests/unit, tests/regression coverage for unknown. | hotspot coverage MV / test inventory |
| 8 | unknown | none mapped | unit, regression | HIGH | Add mapped tests/unit, tests/regression coverage for unknown. | hotspot coverage MV / test inventory |
| 9 | unknown | none mapped | unit, regression | HIGH | Add mapped tests/unit, tests/regression coverage for unknown. | hotspot coverage MV / test inventory |

Action impact:

| Signal | Action impact | Recommended action |
|---|---|---|
| unknown | Fix confidence improves when this scope has mapped tests. | Add mapped tests/unit, tests/regression coverage for unknown. |
| unknown | Fix confidence improves when this scope has mapped tests. | Add mapped tests/unit, tests/regression coverage for unknown. |
| unknown | Fix confidence improves when this scope has mapped tests. | Add mapped tests/unit, tests/regression coverage for unknown. |
| unknown | Fix confidence improves when this scope has mapped tests. | Add mapped tests/unit, tests/regression coverage for unknown. |
| unknown | Fix confidence improves when this scope has mapped tests. | Add mapped tests/unit, tests/regression coverage for unknown. |

### 9. Gap Analysis — Lens 5: GraphDB / MV Decision Impact

Graph signals show where a change can ripple through the codebase; they should change priorities only when tied to a blocker, hotspot, or planned slice.

GraphDB/MV signals drive decisions only when the studied structural risk (centrality, blast radius, reverse deps, cones, chokepoints, SCC, newly-introduced paths) overlaps a blocker, testing exposure, ratchet, or planned slice; raw counts alone stay diagnostic.

| Signal | Decision role | Used now? | Why / why not | Action |
|---|---|---|---|---|

Action impact:

| Signal | Action impact | Recommended action |
|---|---|---|
| none | No immediate action impact. | Keep graph signals diagnostic until they overlap a blocker, hotspot, or planned slice. |

### 10. MECE Decision Gate and Work Queue

Decision gate — fixes report/runtime trust before ranking becomes authoritative:

| Gate | Why it matters | Evidence | Required before ranking |
|---|---|---|---|
| Repair graph/report consistency | The executive order is not decision-grade until graph and report agree. | 2 graph/report mismatch row(s) block decision-grade ordering. | Repair report consistency, then rerun ADG before treating the ranked work queue as authoritative. |

Fix now — ranked work items only:

| Priority | Move | Why it matters | Evidence | Next step |
|---|---|---|---|---|
| 1 | Fund mapped tests for unknown | Testing exposure in a high-risk surface can reduce more delivery risk than blind ratchet burn-down. | Add mapped tests/unit, tests/regression coverage for unknown. | Add mapped tests before touching this surface again. |

### 11. Defer / Delete / Deprecate

### BCG Deletion Brief

- **North star:** Maintain SVP engineer-level repo standards: executive decisions, explicit prioritization, and technical evidence a layperson can follow.
- **Deletion status:** NO_DELETIONS_APPROVED
- **Business read:** No deletions are approved in this run because ADG found 0 confirmed dead-code candidates; reduce uncertainty first, then deprecate noisy diagnostics.
- **Technical evidence:**
  - Dead code candidates: 0
  - Dead imports: 0
  - Unresolved imports: 0
  - First-party low-confidence ratio: 0.00%
  - Inferred-symbol ratio: 0.00%
  - Cleanup candidates surfaced: 13
- **Priority rule:** Confirmed dead code first, then unresolved imports, then low-confidence noise, then low-value diagnostics.

Fix now:

| Priority | Move | Why it matters | Evidence | Next step |
|---------:|------|----------------|----------|-----------|
| 1 | Hold all deletion | The scan found no confirmed dead code, so deleting anything now would be speculative and could break working paths. | Dead-code candidates = 0 and dead imports = 0. | No deletion move until a proven target appears. |
| 2 | Triage unresolved imports | Unresolved imports are the biggest uncertainty and can hide real cleanup opportunities. | 0 unresolved imports; lead hotspot none (0). | Trace the top unresolved scope before deleting anything else. |
| 3 | Reduce low-confidence noise | Cleaner evidence makes later reviews faster and lowers the risk of deleting the wrong thing. | First-party low-confidence ratio = 0.00% and inferred-symbol ratio = 0.00%. | Lower the noise floor, then rerun the scan. |
| 4 | Deprecate low-value ADG signals | Remove empty or low-value diagnostics to cut review overhead once the evidence layer is stable. | 0 MV candidates and 13 unused artifacts surfaced by the report. | Deprecate only after higher-confidence cleanup is complete. |

Next step: Deprecate first, then delete after the evidence stays clean.

Current low-value cleanup candidates:

| Item | Type | Current value | Recommendation | Rationale |
|---|---|---|---|---|
| bcg_adapter | artifact | unused or missing | hide_inline | Available only as diagnostic/evidence context or missing from this run. |
| review_template | artifact | unused or missing | hide_inline | Available only as diagnostic/evidence context or missing from this run. |
| burndown_report | artifact | unused or missing | hide_inline | Available only as diagnostic/evidence context or missing from this run. |
| structural_outputs | artifact | unused or missing | hide_inline | Available only as diagnostic/evidence context or missing from this run. |
| refactor_accelerator | artifact | unused or missing | hide_inline | Available only as diagnostic/evidence context or missing from this run. |
| graphdb_queries | artifact | unused or missing | hide_inline | Available only as diagnostic/evidence context or missing from this run. |
| runtime_spine | artifact | unused or missing | hide_inline | Available only as diagnostic/evidence context or missing from this run. |
| graphdb_projection | artifact | unused or missing | hide_inline | Available only as diagnostic/evidence context or missing from this run. |
| graphdb_metadata | artifact | unused or missing | hide_inline | Available only as diagnostic/evidence context or missing from this run. |
| graphdb_index | artifact | unused or missing | hide_inline | Available only as diagnostic/evidence context or missing from this run. |
| graph_watchlist | artifact | unused or missing | hide_inline | Available only as diagnostic/evidence context or missing from this run. |
| p0_wave_plan | artifact | unused or missing | hide_inline | Available only as diagnostic/evidence context or missing from this run. |

### 12. Honest Bottom Line

- Structurally healthy areas are those with CLEAR gates and no promoted GraphDB/testing gaps; do not spend executive time there.
- Actually blocking now: 0 FIX gates; inspect regression delta before declaring a platform crisis.
- Managed debt remains in TRACK ratchets and open non-ratchet rows; schedule it after green unless it overlaps current work.
- Runtime proof gaps are measurement gaps unless runtime artifacts show observed quality failure.
- Fund mapped tests for unknown
- Do not chase raw MV counts, guardian gross counts, or diagnostic reports without a decision role.
