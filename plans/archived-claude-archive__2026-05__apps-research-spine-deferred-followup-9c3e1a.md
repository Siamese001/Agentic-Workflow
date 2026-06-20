---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\apps-research-spine-deferred-followup-9c3e1a.md'
original_relative_path: '_archive\\2026-05\\apps-research-spine-deferred-followup-9c3e1a.md'
source_sha256: 2aa197e8a6a5daf0afe07a97339e8e22ab87465af1e7f4806c94d932e2d3475a
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-research-spine-deferred-followup-9c3e1a
plan_type: refactor
parent_plan: apps-research-spine-alignment-c0-briefing-2f8a4b
---

# apps_research Spine Alignment — Deferred Scope Followup

Parent plan `apps-research-spine-alignment-c0-briefing-2f8a4b` completed
W1–W5. This plan captures the three items explicitly out-of-scope in the
parent and deferred to a subsequent work cycle.

**Status: NOT STARTED — do not implement until scheduled.**

---

## Context

Parent plan closed all 9 declared gaps (GAP-1 through GAP-9). Three items
were identified during W4/W5 execution as out-of-scope for the alignment
sprint but are required for production-readiness:

1. **GAP-8 E2E (live pipeline)** — FEC ↔ Exit v6 integration under real
   `--apps-e2e-live` conditions. The parent plan's test suite uses unit
   stubs and mocks. The `produce_fec()` v1.1 fields (depth profile, section
   coverage, c0_bundle sub-objects, JD fields) are not yet exercised through
   the full `GovernedResearchRun → ExitControlGate → L6 shadow-eval` path.

2. **`query_decomposer.py` C0 fan-out wiring** — W4 plan referenced
   `query_decomposer.py` as a C0 augmentation target but it was out-of-scope
   for W4's bounded changes. The coverage-family catalog in
   `company_brief_engine.py` handles fan-out inline today; a proper
   query-decomposer integration would move that dispatch into the L1 cognition
   layer and enable multi-step query planning.

3. **Live Tavily DOSSIER-depth retrieval** — `COMPANY_BRIEF_DOSSIER`
   (25 sources, 45 citation anchors, 15 max queries) cannot be verified
   offline. No E2E test covers the depth-profile ↔ retrieval volume
   relationship under real Tavily traffic. Live integration test + SLO
   baseline needed.

---

## Wave Structure

| Wave | Focus | Files | Est. Tokens | Status |
|------|-------|-------|-------------|--------|
| W1 | GAP-8 E2E: wire `produce_fec()` v1.1 through GovernedResearchRun → ExitControlGate | `governed_research_run.py`, `__main__.py`, `cert/fec_producer.py` | ~15K | 🔲 TODO |
| W2 | `query_decomposer.py` C0 fan-out integration | `query_decomposer.py`, `company_brief_engine.py`, new tests | ~20K | 🔲 TODO |
| W3 | Live Tavily DOSSIER-depth retrieval SLO baseline | `engines/company_brief_engine.py`, `tests/e2e/`, `SLO.md` | ~10K | 🔲 TODO |
| W4 | Regression + verification (all three items green) | `tests/_apps_contract/test_apps_research_spine_alignment.py`, CI | ~5K | 🔲 TODO |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| 1.1 | Wire `produce_fec()` v1.1 into GovernedResearchRun | `governed_research_run.py`: pass `c0_bundle`, `depth_profile`, `jd_context` into `run_context` before FEC call | FEC v1.1 fields silently absent in live path | ~7K | 🔲 TODO |
| 1.2 | `__main__.py` cert entrypoint: surface FEC v1.1 fields in GovernedE2ERunRecord | `apps_research/__main__.py`: assert `fec["schema_version"] == "1.1"` and non-None `research_depth_profile` | Live cert run missing evidence | ~5K | 🔲 TODO |
| 1.3 | Add E2E integration test: FEC v1.1 through ExitControlGate | `tests/_apps_contract/test_apps_research_spine_alignment.py`: new class `TestFECv11E2E` | No live-path test coverage for v1.1 | ~5K | 🔲 TODO |
| 2.1 | Extract coverage-family dispatch into `query_decomposer.py` | `query_decomposer.py`: add `decompose_coverage_families(topic, depth_profile, jd_context)` → list of `QueryPlan`; move `_COVERAGE_FAMILY_CATALOG` here | Catalog inline in engine is mis-layered (L2 not L1) | ~10K | 🔲 TODO |
| 2.2 | Update `CompanyBriefEngine` to call `query_decomposer` | `company_brief_engine.py`: replace inline `_COVERAGE_FAMILY_CATALOG` with `query_decomposer.decompose_coverage_families()` call | Backward-compat shim required | ~7K | 🔲 TODO |
| 2.3 | Tests for query_decomposer integration | `tests/_apps_contract/test_apps_research_spine_alignment.py`: fan-out count per depth, JD-theme injection, graceful fallback | | ~5K | 🔲 TODO |
| 3.1 | DOSSIER-depth retrieval volume test (mocked Tavily) | `tests/_apps_contract/test_apps_research_spine_alignment.py`: assert `max_queries == 15`, stub 25 sources, verify gate PASS | Can't verify DOSSIER threshold offline otherwise | ~5K | 🔲 TODO |
| 3.2 | Live retrieval SLO baseline (E2E only, network required) | `tests/e2e/test_apps_research_live.py`: DOSSIER depth, assert ≥25 sources, ≥45 citation anchors, gate PASS within SLO TTL | Requires `TAVILY_API_KEY` | ~5K | 🔲 TODO |
| 4.1 | Regression suite: confirm parent W5 43 tests still pass | `tests/_apps_contract/test_apps_research_spine_alignment.py`: full run, zero regressions | | ~3K | 🔲 TODO |
| 4.2 | CI gate: gate registration in `run_contract_gates.py` | `ops_scripts/ci/run_contract_gates.py`: add `apps-research-e2e-fec-v1.1` gate advisory | | ~2K | 🔲 TODO |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS · ✅ DONE · ❌ BLOCKED

---

## Out Of Scope

- Real LLM-judge scoring for briefing rubric dims (separate eval-harness plan)
- `apps_rg` / `apps_lic` internal C0 binding changes
- UWG / L4 durable write path
- `agentic_core` contract type modifications
- New depth profiles beyond DOSSIER

---

## Gap Register (from parent)

**GAP-8 (partial)** — FEC producer v1.1 fields exist on disk but are NOT
yet exercised through the live `GovernedResearchRun → ExitControlGate → L6`
path. Parent plan W5 unit tests cover the producer in isolation only.
Closes when W1.3 integration test passes `--apps-e2e-live`.

**NEW-1: query_decomposer.py mis-layering** — Coverage-family fan-out logic
lives inline in `company_brief_engine.py` (L2). Should be in
`query_decomposer.py` (L1 cognition layer) per the apps_research layer map.
Closes when W2 integration passes.

**NEW-2: DOSSIER-depth unverified** — No test exercises DOSSIER thresholds
(25 sources, 45 citation anchors). Closes when W3.2 live test passes.

---

## Prerequisites

- Parent plan `apps-research-spine-alignment-c0-briefing-2f8a4b` must be
  in **Completed** status (confirmed ✅ 2026-05-04).
- `TAVILY_API_KEY` available in environment for W3.2 (live E2E only).
- ADG MCP green before starting W2 (L1 layer changes require hotspot check).
