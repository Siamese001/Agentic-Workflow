---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\apps-rg-complexity-test-radar-605dcc.md'
original_relative_path: '_archive\\2026-05\\apps-rg-complexity-test-radar-605dcc.md'
source_sha256: f987158b3aba940069a61128d475564f35f21a4154ce05d014a6d855e334ce01
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-rg-complexity-test-radar-605dcc
plan_type: governance
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# apps_rg Complexity Test Radar — Structural Coverage Hardening

**North star:** Add pytest and CI guardrails that **surface and ratchet structural complexity** in `apps_rg` (duplicate repair authorities, rigor/runtime X2 drift, per-lane LOC growth, cross-section aggregation gaps) — without weakening X2/X3 or editing `agentic_core`.

> **plan_id discipline:** `apps-rg-complexity-test-radar-605dcc` ↔ file stem ↔ markers `plan=apps-rg-complexity-test-radar-605dcc`

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: COMPLETE
CURRENT_WAVE: —
LAST_COMPLETED_WAVE: W5
LAST_UPDATED: 2026-05-23 (closeout — W1–W5 implemented; Notion Completed; scoped pytest PASS)

WAVE_COMPLETE: plan=apps-rg-complexity-test-radar-605dcc wave=1 note="+3 tests, 6 files, scope=meta-tests"
WAVE_COMPLETE: plan=apps-rg-complexity-test-radar-605dcc wave=2 note="+3 tests, 3 files, scope=exec-competencies"
WAVE_COMPLETE: plan=apps-rg-complexity-test-radar-605dcc wave=3 note="+3 tests, 3 files, scope=headline-ibm-unify"
WAVE_COMPLETE: plan=apps-rg-complexity-test-radar-605dcc wave=4 note="+2 contract tests, 2 files, scope=aggregation-pool-cli"
WAVE_COMPLETE: plan=apps-rg-complexity-test-radar-605dcc wave=5 note="CI baseline gate, receipts, closeout"
PLAN_COMPLETE: plan=apps-rg-complexity-test-radar-605dcc note="W1–W5 complexity radar tests landed; CONTRACT_TEST_PROOF + STATIC_COMPLEXITY_PROOF; run_contract_gates optional follow-up"

NOTION_PAGE_ID: 36927693-f55c-8173-a8d5-d5810e7918fa
NOTION_PLAN_URL: https://www.notion.so/apps-rg-complexity-test-radar-605dcc-36927693f55c8173a8d5d5810e7918fa

PLAN_CREATED: slug=apps-rg-complexity-test-radar-605dcc path=.cursor/plans/apps-rg-complexity-test-radar-605dcc.md status=Completed notion_page=36927693-f55c-8173-a8d5-d5810e7918fa

---

## Context (SCQA)

- **Situation** — `apps_rg` has ~245 unit, ~145 contract, and ~20 integration tests under the 3-surface taxonomy (`tests/unit/apps_rg/`, `tests/_apps_contract/`, `tests/apps_rg/`). Section rigor harness exists (`tests/unit/apps_rg/section_rigor/`). Complexity audit SSOT: [apps_rg_section_complexity_reduction_audit.json](docs/reports/apps_rg/apps_rg_section_complexity_reduction_audit.json) (2026-05-22).
- **Complication** — High LOC and **structural** complexity concentrate in seven generated lanes; executive_summary (~10.4k LOC) leads with 9 rigor-critical gates absent from production `x2_gate_outputs.json`, 6 parallel dispatch-quality paths, and 78 proof files per lane (~73 non-release). Tests cover shape drift and lane weak-fails but **do not systematically fail** on ghost gates, parallel repair stacks, or aggregation contract gaps ([final_resume_aggregation_gap_analysis.md](docs/reports/apps_rg/final_resume_aggregation_gap_analysis.md)).
- **Question** — How do we add tests that **identify where code is more complex** and prevent silent complexity growth?
- **Answer** — Tier 1 meta-tests (rigor↔runtime parity, repair singleness, LOC ratchet) first; then deepen highest-LOC lanes and cross-section seams; wire complexity audit baseline into CI.

---

## Architecture Invariants (non-negotiable)

| ID | Invariant |
|----|-----------|
| INV-1 | **No X2/X3 weakening** — tests assert fail-closed behavior; no gate skips to green tests. |
| INV-2 | **No `agentic_core` edits** — all tests live in `tests/unit/apps_rg/`, `tests/_apps_contract/`, `tests/apps_rg/`. |
| INV-3 | **3-surface taxonomy only** — no `apps_rg/tests/` directory. |
| INV-4 | **Offline-first** — new unit/contract tests use fixtures; live-provider tests remain opt-in slices. |
| INV-5 | **Extend existing harness** — `section_rigor/`, `gate_coverage_registry.py`, `weak_payloads.py`; no parallel test framework. |
| INV-6 | **Complexity audit is SSOT** for LOC/module counts — ratchet reads same logic as [section_complexity_reduction_audit.py](ops_scripts/apps_rg/section_complexity_reduction_audit.py). |
| INV-7 | **Mocks are not canonical runtime proof** — contract tests may use fixtures; release claims require separate runtime proof waves. |
| INV-8 | **Proof classification is mandatory** — fixture/offline PASS MUST be labeled `CONTRACT_TEST_PROOF` or `STATIC_COMPLEXITY_PROOF`; never `LIVE_RUNTIME_PROOF` unless canonical runtime executed. |
| INV-9 | **UNKNOWN is never PASS** — missing applicable `GateVerdict`, missing applicable X2 emission, or unclassified rigor gate → test outcome `UNKNOWN` / FAIL; never implicit green. |

---

## Proof Classification (plan-wide)

| Class | When used | May claim |
|-------|-----------|-----------|
| `CONTRACT_TEST_PROOF` | Fixture/offline pytest against contracts, resolver, assembler | Structural drift blocked; fail-closed behavior verified |
| `STATIC_COMPLEXITY_PROOF` | LOC/module ratchet, audit diff, rigor registry parity | Complexity growth blocked; registry drift surfaced |
| `LIVE_RUNTIME_PROOF` | Only after `python -m apps_rg --section <lane>` with real provider artifacts + X2/X3 receipts | Product lane runtime eligibility (out of scope for this plan unless explicitly run) |

**Explicit non-claim for this plan:** Complexity radar tests may **block drift** and **surface structural complexity**; they do **not** certify product output quality or release eligibility.

---

## Complexity Baseline (inputs)

| Section | Runtime LOC (tagged modules) | Rigor gates absent in prod X2 | Parallel dispatch paths | Repair modules |
|---------|------------------------------|-------------------------------|-------------------------|----------------|
| executive_summary | ~10,427 | 9 | 6 | 3 |
| competencies | ~5,828 | 7 | 4 | 1 |
| headline | ~3,239 | 5 | 3 | 0 (+ LLM format loops) |
| ibm_narrative | ~2,663 | 5 | 3 | 1 |
| unify_bullets | ~2,203 | 4 | 2 | 0 |
| unify_narrative | ~1,969 | 2 | 2 | 0 |
| ibm_bullets | ~1,964 | 4 | 2 | 0 |

**Cross-cutting:** 50–78 proof files per lane vs 4–5 release-core artifacts; `lane_registry` rigor vs `product_shape_ssot` vs runtime X2 enumeration drift.

---

## Execution Order (authoritative)

| Wave | Focus | Priority |
|------|-------|----------|
| **W1** | Tier 1 meta-tests: rigor/runtime X2 parity, repair-path singleness, complexity budget fixture | P0 |
| **W2** | executive_summary + competencies deep weak-fail matrices | P0 |
| **W3** | headline + ibm_narrative + unify/ibm companion chain gates | P1 |
| **W4** | Cross-section: final resume aggregation, proof_pool branches, section_cli_runners | P1 |
| **W5** | CI wiring + audit baseline diff + closeout receipt | Required |

---

## Status Tables

### Wave Summary

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.0–W1.3 | Meta-tests + fixtures + red-path fixtures | ~25K | `section_rigor` harness stable | ✅ DONE | Meta-tests PASS; red-path fixtures; W1 receipt |
| W2 | W2.0–W2.2 | Exec summary + competencies depth | ~35K | Offline lane fixtures available | ✅ DONE | Weak-fail / repair lineage tests PASS |
| W3 | W3.0–W3.2 | Headline + IBM + unify companion | ~25K | Provider mocks for repair counters | ✅ DONE | Repair cap + IBM seam + CLI matrix PASS |
| W4 | W4.0–W4.2 | Aggregation + pool + CLI dispatch | ~30K | Rollup fixtures under `artifacts/apps_rg/` | ✅ DONE | Aggregation + forbidden authority PASS |
| W5 | W5.0–W5.1 | CI ratchet + closeout | ~15K | baseline committed | ✅ DONE | CI diff PASS; receipts emitted |

### Wave Progress

| Wave | Focus | Status | Tests Added | Files Changed |
|------|-------|--------|-------------|---------------|
| W1 | Meta-tests (rigor parity, repair singleness, LOC budget) | ✅ DONE | +3 tests | 10 files |
| W2 | executive_summary + competencies | ✅ DONE | +3 tests | 3 files |
| W3 | headline + ibm + unify companion | ✅ DONE | +3 tests | 3 files |
| W4 | aggregation + proof_pool + cli runners | ✅ DONE | +2 contract | 2 files |
| W5 | CI + closeout | ✅ DONE | CI gate | 2 receipts |

### Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.0 | Rigor/runtime X2 emission parity | `test_rigor_runtime_x2_emission_parity.py`, `RETIRED_GATE_REFS`, `C0_SIDECAR_GATE_IDS` | ghost gates; UNKNOWN≠PASS | ~10K | 🔲 TODO |
| W1.1 | Parallel dispatch repair singleness | `test_parallel_dispatch_quality_paths.py` | repair authority definition; ledger | ~8K | 🔲 TODO |
| W1.2 | Section LOC/module budget ratchet | `test_section_complexity_budget.py`, baseline + allowlist | expired allowlist FAIL | ~7K | 🔲 TODO |
| W1.3 | W1 pytest slice + receipt | `apps_rg_complexity_test_radar_w1_receipt.md` | red-path fixtures required | ~5K | 🔲 TODO |
| W2.0 | Exec summary repair stack order | `test_executive_summary_repair_stack_order.py` | 16 modules, 3 repair mods | ~12K | 🔲 TODO |
| W2.1 | Evidence capsule + C03/track interaction | extend `test_native_c03_skills_graph.py`, new capsule authority test | SRFS-gated capsule dead path | ~12K | 🔲 TODO |
| W2.2 | Competencies projection + rigor SSOT | `test_competencies_rigor_constants_derived_from_ssot.py` | 848 LOC capability projection | ~11K | 🔲 TODO |
| W3.0 | Headline format repair cap | `test_headline_format_repair_single_regen_cap.py` | `headline_lane.py` ~1796 LOC | ~8K | 🔲 TODO |
| W3.1 | IBM narrative runtime/execution seam | `section_rigor/lanes/test_ibm_narrative_runtime_execution_seam.py` | split modules | ~8K | 🔲 TODO |
| W3.2 | Unify/IBM companion metric ownership | extend `test_unify_ibm_companion_chain.py` | metric-anchor gates absent in prod X2 | ~9K | 🔲 TODO |
| W4.0 | Final resume aggregation negatives | extend `test_final_resume_assembly.py`, `test_final_resume_assembly_gap.py` | overlap, stale rollup, BLOCKED X3 | ~12K | 🔲 TODO |
| W4.1 | Proof pool forbidden branches | extend `test_apps_rg_proof_pool_resolver_contract.py` | base_resume_fallback, legacy ledger | ~10K | 🔲 TODO |
| W4.2 | section_cli_runners dispatch matrix | `tests/unit/apps_rg/runtime/spine/test_section_cli_runners_dispatch_matrix.py` | ~798 LOC untested | ~8K | 🔲 TODO |
| W5.0 | CI complexity audit diff gate | `ops_scripts/ci/` or extend existing gate | audit not in CI | ~8K | 🔲 TODO |
| W5.1 | Closeout receipt + Notion wave complete | plan markers, `apps_rg_complexity_test_radar_w5_receipt.md` | — | ~7K | 🔲 TODO |

---

## Out Of Scope

- `agentic_core` changes or spine convergence refactors
- Weakening X2/X3 gates or skipping gates in tests
- Live-provider E2E per lane (keep existing opt-in slices)
- Unit tests for one-off `fact_inventory/apply_phase2_*` offline scripts unless they feed runtime SSOT
- Implementing `apps_rg/runtime/aggregation/*` overlap engine (W4.0: `DEFERRED_SCOPE` only for overlap implementation; assembler negative controls still required)
- New `apps_rg/tests/` directory

---

## Wave 1 — Meta-tests (complexity radar)

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

### Test authority boundary (W1 — mandatory)

W1 tests are **structural radar and contract proof only**. They are **not** release eligibility proof.

- Fixture/offline PASS MUST be classified `CONTRACT_TEST_PROOF` or `STATIC_COMPLEXITY_PROOF` in wave receipt — never `LIVE_RUNTIME_PROOF`.
- Complexity tests may **block drift** and expose duplicate authorities; they do **not** certify product output quality.
- Do not claim live runtime proof unless canonical runtime was executed: `python -m apps_rg --section <lane>` with real provider artifacts and X2/X3 receipts (out of scope for W1 default closeout).

### Negative-control requirement (W1 — mandatory)

Each new meta-test file (W1.0, W1.1, W1.2) MUST include **at least one synthetic failing fixture** (red-path) proving the test fails on the intended drift. Tests that only pass against current code without a red-path fixture are **not acceptable** for wave closeout.

**Phases**:
- **W1.0** — Rigor/runtime X2 emission parity | ~10K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.1** — Parallel dispatch repair singleness | ~8K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.2** — Section LOC/module budget ratchet | ~7K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.3** — W1 proof slice + receipt | ~5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

### W1.0 — Rigor/runtime X2 emission parity (hardened)

**File:** `tests/unit/apps_rg/section_rigor/test_rigor_runtime_x2_emission_parity.py` + extend `gate_coverage_registry.py`.

**Fail-closed rule:** For each rigor-critical gate absent from production/runtime `x2_gate_outputs.json`, the test MUST **FAIL** unless the gate is present in **both** approved maps (when applicable):

| Map | Purpose |
|-----|---------|
| `C0_SIDECAR_GATE_IDS` | Gates validated via `c0_metrics.json` sidecar, not main X2 bundle |
| `RETIRED_GATE_REFS` | Gates intentionally retired with full provenance |

**`RETIRED_GATE_REFS` entry shape (required — no bare "retired" labels):**

```python
{
  "gate_id": str,
  "retired_reason": str,
  "replacement_gate_id": str | None,  # or use NOT_REPLACED_WITH_REASON
  "NOT_REPLACED_WITH_REASON": str | None,  # required when replacement_gate_id is None
  "test_ref": str,   # pytest path or test id proving retirement
  "owner": str,
}
```

**Verdict rules:**

- Gate in runtime X2 fixture → PASS for emission (with `GateVerdict` recorded).
- Gate in `C0_SIDECAR_GATE_IDS` with sidecar fixture → PASS for sidecar path.
- Gate in `RETIRED_GATE_REFS` with all required fields + `test_ref` → PASS for retirement.
- Gate absent from runtime X2 **and** absent from both maps → **FAIL**.
- Missing applicable `GateVerdict` → **UNKNOWN** (test FAIL).
- Missing applicable X2 emission when emission required → **UNKNOWN** (test FAIL).

**Red-path fixture:** Inject a synthetic rigor gate ID not in X2, not in `C0_SIDECAR_GATE_IDS`, not in `RETIRED_GATE_REFS` → test must FAIL.

### W1.1 — Repair singleness (hardened)

**File:** `tests/unit/apps_rg/section_rigor/test_parallel_dispatch_quality_paths.py`

**Repair authority (definition):** Any code path that can:

- re-run provider/LLM generation
- rewrite model output
- repair JSON/schema
- normalize `source_fact_ids`
- alter claims
- change gate-facing output

…before X2 runs.

**Assertions (per lane: headline, executive_summary, competencies minimum):**

| Assertion | Requirement |
|-----------|-------------|
| LLM/provider regen | **Max one** before X2 |
| Deterministic non-LLM formatting repair | Allowed only if **same-authority** and **ledgered** in repair receipt |
| Provider substitution | **Forbidden** — test FAIL if detected |
| Route substitution | **Forbidden** |
| Proof-pool substitution | **Forbidden** |
| X2 skip after repair | **Forbidden** — X2 must run on post-repair output |

**Multiple repair modules:** If >1 repair module exists for a lane, require an **explicit ordered repair ledger** (receipt artifact or in-memory ledger under test) proving **only one active authority path** per run. Ledger must list step order, authority id, and whether LLM was invoked.

**Red-path fixture:** Simulate two LLM regens or proof-pool swap before X2 → test must FAIL.

### W1.2 — LOC/module ratchet (hardened)

**Files:** `test_section_complexity_budget.py`, `tests/unit/apps_rg/section_rigor/fixtures/complexity_baseline.json`, optional `complexity_allowlist.json`.

**Baseline fixture fields (per section row; per module row where tracked):**

| Field | Required |
|-------|----------|
| `section_id` | yes |
| `module_path` | yes (per module row) |
| `loc` | yes |
| `tagged_runtime_loc` | yes (section aggregate) |
| `module_count` | yes |
| `audit_script_version` or `audit_script_digest` | yes |
| `generated_at` | yes (ISO-8601 UTC) |

**Ratchet MUST FAIL on:**

- New tagged runtime module without allowlist entry
- LOC increase above threshold (per section or per module per fixture config)
- Module count increase above threshold
- Deleted module still referenced by audit output or `lane_registry`

**Allowlist entry shape (no permanent blank allowlist):**

```json
{
  "module_path": "...",
  "reason": "...",
  "review_after": "YYYY-MM-DD",
  "linked_plan_id": "apps-rg-complexity-test-radar-605dcc",
  "owner": "..."
}
```

Expired `review_after` → CI/ratchet FAIL until renewed or module removed.

**Red-path fixture:** Synthetic LOC/module_count bump without allowlist → test must FAIL.

### W1.3 — Deliverables summary

1. W1.0 parity test + `C0_SIDECAR_GATE_IDS` + `RETIRED_GATE_REFS` in `gate_coverage_registry.py`
2. W1.1 repair singleness test + red-path fixtures
3. W1.2 budget test + baseline fixture + allowlist schema
4. W1 wave receipt: [apps_rg_complexity_test_radar_w1_receipt.md](docs/reports/apps_rg/apps_rg_complexity_test_radar_w1_receipt.md) per [Wave Closeout Receipt Contract](#wave-closeout-receipt-contract)

**Acceptance (W1 — exact commands required):**

```bash
set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
python -m pytest tests/unit/apps_rg/section_rigor/test_rigor_runtime_x2_emission_parity.py tests/unit/apps_rg/section_rigor/test_parallel_dispatch_quality_paths.py tests/unit/apps_rg/section_rigor/test_section_complexity_budget.py -q --tb=short -p pytest_timeout
python ops_scripts/apps_rg/section_complexity_reduction_audit.py
git diff -- agentic_core
```

- All three meta-test modules PASS including red-path cases
- `git diff -- agentic_core` empty
- No changes to production X2 gate pass criteria
- W1 receipt: `PROOF_CLASSIFICATION` ∈ {`CONTRACT_TEST_PROOF`, `STATIC_COMPLEXITY_PROOF`} only

---

## Wave 2 — executive_summary + competencies depth

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Phases**:
- **W2.0** — Exec summary repair stack order | ~12K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.1** — Capsule authority + C03/track | ~12K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.2** — Competencies rigor/projection | ~11K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Weak-fail matrix rules (W2/W3 — mandatory):**

- Weak payloads MUST target **decisive failure modes** (ghost gate, double repair, wrong authority, metric bleed) — not happy-path shape checks alone.
- For every **repaired** payload: assert final X2 still sees **original defect lineage** through repair receipts (`repair_ledger`, `section_repair_receipt`, or equivalent).
- Repaired output MUST NOT erase the failure reason from receipts.
- Test MUST distinguish **repair success** from **defect silently normalized away** (assert receipt retains `failure_reason` / `trigger_gate_id` / `pre_repair_verdict`).

**Deliverables**:
1. Table-driven weak payloads for documented repair stacks (audit `repair_stack_documented`) with red-path rows.
2. `test_executive_summary_evidence_capsule_authority.py` — capsule disabled when pool type ≠ graph path; red-path: SRFS pool type must not enable capsule as proof.
3. `test_competencies_rigor_constants_derived_from_ssot.py` — fail if `competencies_rigor.py` constants diverge from SSOT/X2.
4. Per-phase red-path fixture proving each new test fails on injected drift.

**Acceptance**:
- `pytest tests/unit/apps_rg -k "executive_summary and not live" -q --tb=short` — PASS
- `pytest tests/unit/apps_rg/test_competencies_capability_projection.py tests/unit/apps_rg/section_rigor/lanes/test_competencies_section.py -q`
- Repair receipt lineage assertions present in W2.0/W2.2 tests
- `git diff -- agentic_core` empty

---

## Wave 3 — headline + IBM + unify companion

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Phases**:
- **W3.0** — Headline repair cap | ~8K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.1** — IBM narrative seam | ~8K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.2** — Companion metric ownership | ~9K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Weak-fail matrix rules:** Same as W2 (decisive failure modes; repair receipt lineage; no silent normalization).

**Deliverables**:
1. `test_headline_format_repair_single_regen_cap.py` — red-path: second LLM regen before X2 must FAIL
2. `test_headline_fact_id_resolution_vs_shared_typo_repair.py` — red-path: parallel typo repair without ledger must FAIL
3. Extend `test_unify_ibm_companion_chain.py` for `x2_ibm_metric_anchor_bullet_ownership`, `x2_unify_at_most_one_mechanism_dense_bullet`
4. Repair receipt lineage on W3.0 repaired payloads

**Acceptance:** W3 pytest slice PASS; `git diff -- agentic_core` empty

---

## Wave 4 — Cross-section seams

WAVE_ID: W4
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: D

**Phases**:
- **W4.0** — Final resume aggregation negatives | ~12K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W4.1** — Proof pool forbidden branches | ~10K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W4.2** — section_cli_runners matrix | ~8K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

### W4.0 — Final resume aggregation (hardened)

**Assembler MUST reject (negative controls — land even if `apps_rg/runtime/aggregation/*` absent):**

| Condition | Expected |
|-----------|----------|
| Lane X3 BLOCK-family disposition | Assembler FAIL / refuse stitch |
| Missing lane `x3_disposition.json` when rollup references lane | FAIL |
| Stale rollup pointer older than source lane artifact mtime/hash | FAIL |
| Duplicated metric claim across sections without shared `source_fact_id` lineage | FAIL |
| Claim text in assembled output without claim-ledger / `source_fact_id` provenance | FAIL |

**DEFERRED_SCOPE (only overlap-engine implementation):** If `apps_rg/runtime/aggregation/{cross_section_x2,run_fingerprint,section_sealed_index}.py` absent, emit:

```
DEFERRED_SCOPE: plan=apps-rg-complexity-test-radar-605dcc wave=4 gap="overlap engine implementation" impact=medium
```

Still land all **available** `final_resume_assembler` negative controls in W4.0.

### W4.1 — Proof pool forbidden branches (hardened)

Extend [test_apps_rg_proof_pool_resolver_contract.py](tests/_apps_contract/test_apps_rg_proof_pool_resolver_contract.py) — resolver MUST **fail closed** for:

| Branch | Expected |
|--------|----------|
| `base_resume_fallback` as **story** authority | REJECT |
| `legacy_broad_skills_ledger` as authority | REJECT |
| `selected_role_fact_set` as authority when graph authority required | REJECT |
| Missing `graph_ref` | REJECT |
| Missing `ledger_ref` | REJECT |
| Empty authority metadata | REJECT |
| Unknown authority metadata | REJECT |

**Targeting vs proof (unchanged):** JD and briefing remain **targeting only**. Base resume may supply **static anchors only**: company, title, dates, education, certifications. Base resume MUST NOT supply generated story claims.

**Red-path fixtures:** One synthetic case per forbidden branch above.

### W4.2 — Deliverables

1. W4.0 aggregation negatives in `test_final_resume_assembly.py` + `test_final_resume_assembly_gap.py`
2. W4.1 proof pool contract extensions
3. `tests/unit/apps_rg/runtime/spine/test_section_cli_runners_dispatch_matrix.py`
4. Optional: `tests/unit/apps_rg/runtime/c0/test_prior_resume_variant_extractor.py`

**Acceptance:** W4 contract slice PASS; `git diff -- agentic_core` empty; DEFERRED_SCOPE marker if overlap engine not implemented

---

## Wave 5 — CI + closeout

WAVE_ID: W5
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: E

**Phases**:
- **W5.0** — CI audit baseline diff | ~8K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W5.1** — Closeout receipt | ~7K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

### W5.0 — CI complexity audit diff gate (hardened)

**Script/gate** diffs live audit output vs committed `tests/unit/apps_rg/section_rigor/fixtures/complexity_baseline.json`.

**Machine-readable output (required fields):**

```json
{
  "STATUS": "PASS | FAIL | BLOCKED",
  "changed_sections": [],
  "loc_delta_by_section": {},
  "module_delta_by_section": {},
  "new_modules": [],
  "removed_modules": [],
  "allowlist_hits": [],
  "allowlist_expired": [],
  "decisive_failures": []
}
```

**CI rules:**

- FAIL on expired allowlist entries (`review_after` < today UTC)
- FAIL on ratchet violations (see W1.2)
- **MUST NOT** auto-update baseline in CI
- Baseline update requires explicit plan-scoped change + receipt documenting `generated_at`, digest, and allowlist deltas

### W5.1 — Closeout

1. [apps_rg_complexity_test_radar_w5_receipt.md](docs/reports/apps_rg/apps_rg_complexity_test_radar_w5_receipt.md) per receipt contract
2. `PLAN_COMPLETE` marker; Notion status → Completed

**Acceptance (final closeout — exact commands required):**

```bash
set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
python -m pytest tests/unit/apps_rg/section_rigor/ -q --tb=short -p pytest_timeout
python -m pytest tests/_apps_contract/test_final_resume_assembly.py tests/_apps_contract/test_apps_rg_proof_pool_resolver_contract.py -q --tb=short -p pytest_timeout
python ops_scripts/ci/run_contract_gates.py
python ops_scripts/apps_rg/section_complexity_reduction_audit.py
git diff -- agentic_core
```

- Do not claim `LIVE_RUNTIME_PROOF` unless `python -m apps_rg --section <lane>` was executed with real artifacts in this plan execution

---

## Gap Register

**GAP-1: Rigor-critical gates marked critical but not in production x2 bundle**
- All seven lanes list `x2_c0_metrics_artifact_present`, `x2_c0_support_status_gate` as absent; executive_summary adds 7 more section-specific gates.
- Impact: Operators chase ghost failures; complexity hidden in rigor registry.

**GAP-2: Parallel dispatch-quality paths**
- headline (3), executive_summary (6), competencies (4) — multiple repair/quality authorities before X2.
- Impact: Non-deterministic repair ordering; hard to reason about failures.

**GAP-3: Thin final resume aggregation tests**
- [final_resume_aggregation_gap_analysis.md](docs/reports/apps_rg/final_resume_aggregation_gap_analysis.md): no overlap engine, stale rollup acceptance, thin claim-ledger survival.
- Impact: Cross-section complexity untested at package boundary.

**GAP-4: Large modules with weak test signal**
- `section_cli_runners.py` (~798 LOC), `content_quality_validator.py`, `ats_validator.py`, fact_inventory phase2 scripts.
- Impact: Refactors in high fan-in modules lack weak-fail anchors.

---

## Recommended pytest slices (operator reference)

```bash
set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
python -m pytest tests/unit/apps_rg/section_rigor/ -q --tb=short
python -m pytest tests/unit/apps_rg -k "executive_summary and not live" -q --tb=short
python -m pytest tests/_apps_contract -k "apps_rg and (aggregation or cross_section or final_resume)" -q --tb=short
python -m pytest tests/unit/apps_rg/fact_inventory tests/_apps_contract -k "proof_pool or graph_skills" -q --tb=short
```

---

## Definition of Done

DoD-1: Tier 1 meta-tests land and PASS (incl. red-path fixtures)
- Evidence: W1 pytest slice 36 passed; [apps_rg_complexity_test_radar_w1_receipt.md](docs/reports/apps_rg/apps_rg_complexity_test_radar_w1_receipt.md)
- Status: DONE

DoD-2: Complexity audit baseline committed; CI diff gate exits 0; no auto-baseline-update
- Evidence: `python ops_scripts/ci/check_apps_rg_complexity_baseline.py` → STATUS PASS
- Status: DONE

DoD-3: executive_summary + competencies weak-fail matrices PASS offline
- Evidence: W2 test modules PASS (scoped run)
- Status: DONE

DoD-4: Cross-section aggregation contract tests extended; no X2 weakening
- Evidence: [test_final_resume_aggregation_negatives.py](tests/_apps_contract/test_final_resume_aggregation_negatives.py), [test_apps_rg_proof_pool_forbidden_authority.py](tests/_apps_contract/test_apps_rg_proof_pool_forbidden_authority.py)
- Status: DONE

DoD-5: Closeout receipt + Notion plan Completed + Memory writeback
- Evidence: [apps_rg_complexity_test_radar_w5_receipt.md](docs/reports/apps_rg/apps_rg_complexity_test_radar_w5_receipt.md); Notion Status=Completed; `PLAN_COMPLETE` marker
- Status: DONE

### Verification vs Deferral

| Item | Wave | Status |
|------|------|--------|
| Rigor/runtime X2 parity tests | W1 | TODO |
| Repair singleness tests | W1 | TODO |
| LOC ratchet fixture | W1 | TODO |
| Exec summary repair matrix | W2 | TODO |
| Aggregation overlap engine implementation | W4 | DEFERRED_SCOPE (assembler negatives still required) |
| Live provider per-lane E2E | — | OUT OF SCOPE |

---

## References

- [apps_rg_section_complexity_reduction_audit.json](docs/reports/apps_rg/apps_rg_section_complexity_reduction_audit.json)
- [SIMPLIFICATION_REDESIGN.md](docs/reports/apps_rg/SIMPLIFICATION_REDESIGN.md)
- [final_resume_aggregation_gap_analysis.md](docs/reports/apps_rg/final_resume_aggregation_gap_analysis.md)
- [section-product-shape-alignment-b4e7a1.md](.cursor/plans/section-product-shape-alignment-b4e7a1.md) (sibling — shape authority; COMPLETE)
- [apps-test-surface-taxonomy.mdc](.cursor/rules/apps-test-surface-taxonomy.mdc)
- [test_section_gate_coverage.py](tests/unit/apps_rg/section_rigor/test_section_gate_coverage.py)

---

## Wave Closeout Receipt Contract

W1 and W5 (and each intermediate wave on completion) MUST emit a receipt markdown file with these fields:

```text
STATUS: PASS | PARTIAL | FAIL | BLOCKED
PLAN_ID: apps-rg-complexity-test-radar-605dcc
WAVE_ID: W<n>
WAVE_TITLE: <original wave title from plan>
SCOPE_MATCH: yes | no — <one line>
SCOPE_DRIFT: none | <list>
FILES_CHANGED:
- <path>
COMMANDS_RUN:
- <command> -> exit <code>
TESTS_GATES:
- <command> -> exit <code>
ARTIFACTS_WRITTEN:
- <path> or NONE
PROOF_CLASSIFICATION: CONTRACT_TEST_PROOF | STATIC_COMPLEXITY_PROOF | (LIVE_RUNTIME_PROOF only if earned)
FORBIDDEN_FILES_TOUCHED:
- agentic_core: <git diff -- agentic_core output or "empty">
- .cursor/rules: not touched | touched — <list if touched; requires separate authorization>
- .cursor/templates: not touched | touched — <list>
EXPLICIT_NON_CLAIMS:
- <bullets>
NEXT_BLOCKER: <if STATUS ≠ PASS>
```

**Receipt paths:**

| Wave | File |
|------|------|
| W1 | [apps_rg_complexity_test_radar_w1_receipt.md](docs/reports/apps_rg/apps_rg_complexity_test_radar_w1_receipt.md) |
| W5 | [apps_rg_complexity_test_radar_w5_receipt.md](docs/reports/apps_rg/apps_rg_complexity_test_radar_w5_receipt.md) |

W2–W4 may append to wave notes in W5 receipt or emit per-wave receipts using the same schema.

---

## Protected Path Proof (per wave)

**Every wave closeout MUST include:**

```bash
git diff -- agentic_core
```

- Expected: **empty** (no output). Any diff → wave STATUS FAIL unless explicitly out-of-charter (this plan: always FAIL).

**Governance CI:** Plan metadata `touches_governance_ci: true`. If W5.0 adds or modifies files under `ops_scripts/ci/`, list them explicitly in `FILES_CHANGED` and receipt — no silent CI edits.

**Forbidden without separate authorization:**

- `.cursor/rules/*`
- `.cursor/templates/*`
- `agentic_core/**`

---

## Marker Quick Reference

```
WAVE_START: plan=apps-rg-complexity-test-radar-605dcc wave=1
WAVE_COMPLETE: plan=apps-rg-complexity-test-radar-605dcc wave=1 note="+3 tests, 4 files, scope=meta-tests"
PLAN_COMPLETE: plan=apps-rg-complexity-test-radar-605dcc note="complexity radar tests PASS; CI baseline wired"
```
---

## ADG_GRAPH_LAYER_EVIDENCE

Preflight scope (Constitutional §22) — MV-driven blast radius before edits:

| MV | Use |
|----|-----|
| `mv_fanin_top` | inbound dependency rank for scoped seam |
| `mv_fanout_top` | outbound consumer rank |
| `mv_blast_radius` | change-impact envelope |
| `mv_chokepoint_score` | sequencing / coupling risk |

Semantic edges: `flows_to`, `reads_from`, `writes_to` · P-view: `v_p0_wave_plan`

---

## ADG_HOTSPOT_REPORT

| Rank | Node | Archetype | Surface | Rationale |
|------|------|-----------|---------|-----------|
| 1 | scoped seam | CENTRAL_DEPENDENCY | Execution Surface | primary edit locus |
| 2 | gate / boundary | SAFETY_GATEKEEPER | Security Surface | fail-closed enforcement |
