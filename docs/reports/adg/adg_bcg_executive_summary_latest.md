## ADG Executive Brief

### 1. What ADG Is

ADG is the X-ray of the codebase. It maps code connections and lets the system ask health-check questions automatically. It turns 'is this codebase healthy?' from opinion into measured facts.

### 2. Patient Size

This patient has 12433 Python files: 7269 production files and 5164 test files. agentic_core contributes 2899 files; apps_* contributes 1500 files. Current snapshot/run ID: ts.

### 3. Executive Decision

ADG is TESTING_CONTROL_GAP: Fund the smallest slice that clears current blockers and attaches tests where hotspot evidence overlaps; keep ratchets after-green. This is a managed_debt; do not chase Do not rank work by raw MV row count alone., Do not treat guardian inventory as an automatic product failure..

### 4. Gap Analysis — Lens 1: Health Gates

FIX blocks green; TRACK is accepted backlog/ratchet work; CLEAR needs no action. A blocked ADG run is not automatically a platform crisis; regression delta and graph/test linkage determine urgency.

| Bucket | Count | Executive meaning |
|---|---:|---|
| CLEAR | 0 | No action now. |
| TRACK | 0 | Known debt or advisory inventory; burn down after red gates. |
| FIX | 0 | Current blocker or regression requiring action before decision-grade green. |

| Red gate | Total records | Regression / new delta | Executive read | Next action |
|---|---:|---:|---|---|
| None | 0 | 0 | No red gates. | No blocker action. |

### 5. Gap Analysis — Lens 2: Runtime Proof / Observability

Missing runtime proof is a measurement gap unless an artifact shows runtime failure evidence.

| Runtime proof signal | Status | Executive read | Action |
|---|---|---|---|
| runtime_spine | missing | Measurement blind spot; not automatically a product failure. | Enable or repair artifact emission if the decision needs runtime proof. |
| graphdb_queries | missing | Measurement blind spot; not automatically a product failure. | Enable or repair artifact emission if the decision needs runtime proof. |
| structural_outputs | missing | Measurement blind spot; not automatically a product failure. | Enable or repair artifact emission if the decision needs runtime proof. |

### 6. Gap Analysis — Lens 3: Product / App Risk

App/product risks were promoted only where hotspot or test evidence changes funding posture.

| App / product scope | Risk | Evidence | Executive read | Next action |
|---|---|---|---|---|
| apps_sales | Under-tested product hotspot | apps_sales/runtime/checkout.py | App risk is promoted because product surface and missing test scope overlap. | Add mapped tests/regression, tests/e2e or app-specific e2e coverage for apps_sales. |

### 7. Gap Analysis — Lens 4: Testing Control Gaps

Testing is a control gap where apps_sales/runtime/checkout.py lacks regression, e2e coverage; fund tests with the relevant fix slice, not as a generic test campaign.

| Rank | Production scope | Current tests found | Missing test scope | Risk | Recommended investment | Trigger |
|---:|---|---|---|---|---|---|
| 1 | apps_sales/runtime/checkout.py | none mapped | regression, e2e | CRITICAL | Add mapped tests/regression, tests/e2e or app-specific e2e coverage for apps_sales. | hotspot coverage MV / test inventory |

### 8. Gap Analysis — Lens 5: GraphDB / MV Decision Impact

GraphDB/MV signals are used as decision drivers only when linked to blockers, testing exposure, ratchets, artifact consistency, or planned slices; raw counts alone stay diagnostic.

| Signal | Decision role | Used now? | Why / why not | Action |
|---|---|---|---|---|
| mv_hotspot_coverage_risk | used_for_testing | True | Translates structural risk into concrete test-placement decisions. | Attach mapped tests to high-risk scopes. |
| mv_guardian_inventory | audit_only | False | Audit math unless mapped to a current failing gate. | Audit; do not treat as blocker by itself. |
| mv_empty_noise | deprecate_candidate | False | Empty or stale-looking signal; keep out of inline output until it proves decision value. | Deprecate/delete candidate if still empty next runs. |
| mv_p0_ratchet_inventory | used_after_green | False | Useful after CI is green to lower accepted ratchet debt. | Schedule after-green burn-down. |

### 9. Next Best Actions

| Rank | Action | Scope | Why now | Evidence used | Testing requirement | Done condition |
|---:|---|---|---|---|---|---|
| 1 | Fund mapped tests for apps_sales/runtime/checkout.py | apps_sales/runtime/checkout.py | Testing exposure in a high-risk surface can reduce more delivery risk than blind ratchet burn-down. | testing_hotspot | Add mapped tests/regression, tests/e2e or app-specific e2e coverage for apps_sales. | Rerun ADG and confirm the relevant gate/test/report status is green or explicitly waived. |
| 2 | Refine/deprecate low-value ADG signal mv_empty_noise | mv_empty_noise | Suppress or retire signals that do not affect decisions. | mv | No test required unless generator logic changes. | Rerun ADG and confirm the relevant gate/test/report status is green or explicitly waived. |

### 10. Defer / Delete / Deprecate

| Item | Current value | Recommendation | Rationale |
|---|---|---|---|
| mv_empty_noise | 0 rows; stale_or_empty | deprecate | Raw MV count alone is not a funding signal. |
| mv_guardian_inventory | 1 rows; audit_driver | keep_hide_inline | Raw MV count alone is not a funding signal. |
| mv_p0_ratchet_inventory | 2 rows; ratchet_driver | keep_hide_inline | Raw MV count alone is not a funding signal. |
| action_queue | unused or missing | hide_inline | Available only as diagnostic/evidence context or missing from this run. |
| review_template | unused or missing | hide_inline | Available only as diagnostic/evidence context or missing from this run. |
| burndown_table | unused or missing | hide_inline | Available only as diagnostic/evidence context or missing from this run. |
| burndown_report | unused or missing | hide_inline | Available only as diagnostic/evidence context or missing from this run. |

### 11. Honest Bottom Line

- Structurally healthy areas are those with CLEAR gates and no promoted GraphDB/testing gaps; do not spend executive time there.
- Actually blocking now: 0 FIX gates; inspect regression delta before declaring a platform crisis.
- Managed debt remains in TRACK ratchets and open non-ratchet rows; schedule it after green unless it overlaps current work.
- Runtime proof gaps are measurement gaps unless runtime artifacts show observed quality failure.
- Fund mapped tests for apps_sales/runtime/checkout.py
- Do not chase raw MV counts, guardian gross counts, or diagnostic reports without a decision role.
