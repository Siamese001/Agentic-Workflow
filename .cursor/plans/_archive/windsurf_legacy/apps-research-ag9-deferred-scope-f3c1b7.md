---
plan_id: apps-research-ag9-deferred-scope-f3c1b7
plan_type: deferred-scope
parent_plan: apps-research-ag9-golden-template-adoption-e4f2b8
dod_exempt: false
---

# AG-9 apps_research Deferred Scope — Remaining Waves

Tracks the AG-9 waves that were deferred from
`apps-research-ag9-golden-template-adoption-e4f2b8` after spine binding
implementation (W3–W7 core + dispatch + CI gates) was completed and committed
(commit `8022620779`, 2026-05-10). The core pipeline is operational and
verified by 15 passing tests and 2 green CI gates.

**What was completed in the parent plan (committed):**
- W3 U0 binding (`u0_apps_research_binding.py`) — validated request, authority scan
- W4 L1 binding (`apps_research_l1_binding.py`) — plan projection (prior commit)
- W4 L0 binding (`apps_research_l0_binding.py`) — R3_SIMPLE_GROUNDED_READ route (prior commit)
- W5 C0 binding (`apps_research_c0_binding.py`) — FinalEvidenceContract
- W5 PA binding (`apps_research_pa_binding.py`) — CompiledPromptArtifact, BOM slots
- W6 L2 binding (`apps_research_l2_binding.py`) — Qwen vLLM / stub fallback
- W7 Exit binding (`apps_research_exit_binding.py`) — artifact write + X3Disposition
- Dispatch (`apps_research_dispatch.py`) — full U0→L1→L0→C0→PA→L2→Exit chain
- `apps_research/__main__.py` — `--spine` flag wired to dispatch
- CI gates: `check_apps_research_import.py`, `check_apps_research_dryrun.py`
- Tests: `test_apps_research_ag9_spine.py` (15 tests, all passing)
- Provenance chain: FEC.compilation_hash → prompt.evidence_digest → sealed.prompt_artifact_digest ✅

**What is deferred (this plan):**
- W0: Formal baseline gate run + recorded evidence
- W1/W1.5/W1.8: Discovery JSON artifacts + preservation matrix + prompt authority inventory
- W2: U0 payload schema JSON artifacts
- W5.5: Prompt authority hardening closure report
- W8: Full 21-test E2E golden-path suite (`test_ag9_apps_research_golden_path.py`)
- W9: Full runtime CI gate (`check_apps_research_golden_path_runtime.py`)
- W10: Prompt authority CI gate (`check_apps_research_prompt_authority.py`)
- W11: All 11 output artifacts under `artifacts/apps_research/`

---

## Wave Structure

| Wave | Focus | Scope | Status |
|------|-------|-------|--------|
| DS-W0 | Formal baseline gate run | 6 gates, recorded evidence | 🔲 |
| DS-W1 | Discovery JSON artifacts | `ag9_apps_research_discovery.json`, `ag9_no_bypass_map.json` | 🔲 |
| DS-W1.5 | Functionality preservation matrix | `ag9_apps_research_functionality_preservation_matrix.json` | 🔲 |
| DS-W1.8 | Prompt authority inventory | `ag9_prompt_authority_inventory.json` | 🔲 |
| DS-W2 | U0 payload schema artifacts | `ag9_apps_research_payload_schema.json`, `ag9_apps_research_payload_mapping_matrix.json` | 🔲 |
| DS-W5.5 | Prompt authority hardening closure | `ag9_prompt_authority_hardening_report.json` | 🔲 |
| DS-W8 | Full 21-test E2E golden-path suite | `test_ag9_apps_research_golden_path.py` ≥21 tests | 🔲 |
| DS-W9 | Full runtime CI gate | `check_apps_research_golden_path_runtime.py` registered | 🔲 |
| DS-W10 | Prompt authority CI gate | `check_apps_research_prompt_authority.py` registered | 🔲 |
| DS-W11 | All 11 output artifacts | `artifacts/apps_research/ag9_*.json` + `ag9_*.md` | 🔲 |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| DS-W0 | Baseline gates | 6 CI scripts | Run-record evidence | ~2K | 🔲 |
| DS-W1 | Discovery artifacts | `apps_research/` read-only | JSON serialization of findings | ~8K | 🔲 |
| DS-W1.5 | Preservation matrix | All apps_research capabilities | Per-capability row for every feature | ~6K | 🔲 |
| DS-W1.8 | Prompt authority inventory | `prompt_assembly/`, `engines/`, `integrations/` | Zero UNKNOWN at acceptance | ~6K | 🔲 |
| DS-W2 | Payload schema JSON | `research_ingress_payload.py` | Field mapping completeness | ~4K | 🔲 |
| DS-W5.5 | PA hardening closure | PA binding + prompt surfaces | No LEGACY_BRIDGE left unresolved | ~5K | 🔲 |
| DS-W8 | 21-test E2E suite | `tests/_apps_contract/` | Covers all 22 required test cases | ~10K | 🔲 |
| DS-W9 | Runtime CI gate | `ops_scripts/ci/` | Covers all 17 fail conditions | ~6K | 🔲 |
| DS-W10 | PA CI gate | `ops_scripts/ci/` | Import guard + slot separation check | ~4K | 🔲 |
| DS-W11 | Output artifacts | `artifacts/apps_research/` | All 11 artifacts, acceptance bundle | ~4K | 🔲 |

---

## DS-W0 — Formal Baseline Gate Run

Run and record evidence for all 6 gates from the parent plan W0:

```bash
python -m pytest tests/_apps_contract/test_ag6_apps_rg_golden_path.py -v
python ops_scripts/ci/check_apps_rg_golden_path_runtime.py --fail-closed
python ops_scripts/ci/check_exit_x1_evaluator_wiring.py --fail-closed
python ops_scripts/ci/check_evidence_contract_carriers.py
python -m pytest tests/_apps_contract/test_ag8_apps_lic_golden_path.py -v
python ops_scripts/ci/check_apps_lic_golden_path_runtime.py --fail-closed
```

**Produce**: `artifacts/apps_research/ag9_baseline_gate_run.json` with exit codes + timestamps.

---

## DS-W1 — Discovery JSON Artifacts

Read-only inspection of `apps_research/` codebase. Produce:
- `artifacts/apps_research/ag9_apps_research_discovery.json` — full capability inventory
- `artifacts/apps_research/ag9_no_bypass_map.json` — proof of no stage bypasses

Fields per capability row per parent plan §W1.

---

## DS-W1.5 — Functionality Preservation Matrix

Produce `artifacts/apps_research/ag9_apps_research_functionality_preservation_matrix.json`.

Every current apps_research capability must have status `PRESERVED` | `PARTIAL` | `DEFERRED_WITH_REASON`. No `MISSING` rows at acceptance.

Fields per parent plan §W1.5.

---

## DS-W1.8 — Prompt Authority Inventory

Produce `artifacts/apps_research/ag9_prompt_authority_inventory.json`.

Every prompt surface in `prompt_assembly/`, `engines/`, `integrations/` classified as
`PA_OWNED` | `TASK_DATA` | `EVIDENCE_DATA` | `LEGACY_BRIDGE`. Zero `UNKNOWN`.

Fields per parent plan §W1.8.

---

## DS-W2 — U0 Payload Schema Artifacts

Produce:
- `artifacts/apps_research/ag9_apps_research_payload_schema.json`
- `artifacts/apps_research/ag9_apps_research_payload_mapping_matrix.json`

Derive from the implemented `u0_apps_research_binding.py` `_make_payload_dict()` function.

---

## DS-W5.5 — Prompt Authority Hardening Closure

Produce `artifacts/apps_research/ag9_prompt_authority_hardening_report.json`.

For each surface from W1.8 inventory: confirm binding, add authority annotation, verify no
unauthorized import. Tests:
- PA is the only stage importing `research_pa_compiler`
- No L0/L1/C0/L2 import of prompt assembly modules
- TASK_DATA slot ≠ EVIDENCE_DATA slot

---

## DS-W8 — Full 21-Test E2E Golden-Path Suite

Create `tests/_apps_contract/test_ag9_apps_research_golden_path.py` with all 22 required
test cases from parent plan §W8 (including W5.5 hardening tests, X1/X3 tests, no-bypass
tests, ChromaDB non-mutation, embedding non-generation).

Existing `test_apps_research_ag9_spine.py` (15 tests) covers the core pipeline.
This new suite adds the 7+ additional contract and governance tests.

---

## DS-W9 — Full Runtime CI Gate

Create `ops_scripts/ci/check_apps_research_golden_path_runtime.py`.

Covers all 17 fail conditions from parent plan §W9. Register in `run_contract_gates.py`.

---

## DS-W10 — Prompt Authority CI Gate

Create `ops_scripts/ci/check_apps_research_prompt_authority.py`.

Import guard: `research_pa_compiler` only imported from `apps_research_pa_binding.py`.
Slot separation check: no TASK_DATA/EVIDENCE_DATA conflation.
Register in `run_contract_gates.py`.

---

## DS-W11 — All 11 Output Artifacts

Produce all 11 artifacts listed in parent plan §W11 under `artifacts/apps_research/`.
Final artifact: `ag9_acceptance_evidence.json` with `ag9_invariant_met: true`.

---

## Definition of Done

| # | Criterion | Verification | Status |
|---|---|---|---|
| DoD-1 | DS-W0 baseline gates all exit 0, evidence recorded | `artifacts/apps_research/ag9_baseline_gate_run.json` exists | 🔲 |
| DoD-2 | Discovery + preservation + prompt-authority JSON artifacts present, zero MISSING/UNKNOWN | All 5 artifacts under `artifacts/apps_research/ag9_*.json` exist | 🔲 |
| DoD-3 | 21-test E2E suite passes, zero regressions | `pytest tests/_apps_contract/test_ag9_apps_research_golden_path.py -v` | 🔲 |
| DoD-4 | Both full CI gates green and registered | `check_apps_research_golden_path_runtime.py` + `check_apps_research_prompt_authority.py` both exit 0 | 🔲 |
| DoD-5 | All 11 output artifacts present, acceptance evidence `ag9_invariant_met: true` | `artifacts/apps_research/ag9_acceptance_evidence.json` | 🔲 |

---

## Rollback

All deferred waves are read-only artifact-generation or new test/gate files. None modify
existing bindings. Safe to execute independently of other plan work.

Parent plan bindings (`u0_`, `l1_`, `l0_`, `c0_`, `pa_`, `l2_`, `exit_` bindings +
dispatch + `__main__.py`) are already committed and proven green — no rollback risk.
