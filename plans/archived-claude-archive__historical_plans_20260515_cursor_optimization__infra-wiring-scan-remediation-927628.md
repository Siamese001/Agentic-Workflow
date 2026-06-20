---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\infra-wiring-scan-remediation-927628.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\infra-wiring-scan-remediation-927628.md'
source_sha256: f64aaa9ea88d12f6eee20c553e086634880481026d5edccd5f0bbacf496e8e9b
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: infra-wiring-scan-remediation-927628
plan_type: infrastructure_remediation
authored_at: 2026-05-12
last_updated: 2026-05-12T13:01:00Z
status: Completed
dod_exempt: false
touches_agentic_core: true
core_addition_author_gate_required: false
origin: Surfaced as known exclusion in core-addition-author-gate-governance-f3b9e2 W7
---

# Infra Wiring Scan Remediation

Eliminate all P0 failures in `ops_scripts/ci/infra_wiring_scan.py` that cause
`run_contract_gates.py` to exit non-zero. Each violation is a file that imports
a forbidden infrastructure library directly (outside a sanctioned adapter or
allowed directory). The fix for each is either (a) register the file as a
sanctioned adapter in `SANCTIONED_ADAPTER_FILES`, or (b) refactor the file to
route through an existing sanctioned adapter.

**Origin:** Documented as a pre-existing, unrelated blocker in
`core-addition-author-gate-governance-f3b9e2` W7 final evidence bundle.
`artifacts/governance/core_addition_author_gate_final_evidence_bundle.json` §known_exclusions.

---

## Violation Inventory (baseline at plan creation 2026-05-12)

| # | File | Line | Import | Classification | Fix path |
|---|------|------|--------|----------------|----------|
| V-1 | `agentic_core/L2_execution/providers/gemini_provider.py` | 91 | `import httpx` | Non-sanctioned provider | Register in SANCTIONED_ADAPTER_FILES or route via `optimized_vllm_client.py` pattern |
| V-2 | `agentic_core/runtime/providers/provider_gateway.py` | 395 | `import anthropic` | Non-sanctioned gateway | Register in SANCTIONED_ADAPTER_FILES (parallel to `claude_judge.py`) |
| V-3 | `agentic_core/runtime/providers/provider_gateway.py` | 436 | `import openai` | Non-sanctioned gateway | Same file as V-2 — single registration fixes both |
| V-4 | `apps_architect/engines/adg_client.py` | 11 | `import sqlite3` | Non-sanctioned client | Register in SANCTIONED_ADAPTER_FILES (ADG read consumer, peer of `adg_span_annotator.py`) |
| V-5 | `apps_qna/integrations/provider_adapter.py` | 107, 121, 136, 146 | `import anthropic`, `openai`, `google`, `httpx` | Multi-infra integration | Register in SANCTIONED_ADAPTER_FILES (peer of existing `llm_client.py` entries) |
| V-6 | `apps_qna/engines/dispatch/provider_dispatch.py` | 161, 181 | `import anthropic`, `google` | Dispatch layer | Register in SANCTIONED_ADAPTER_FILES |
| V-7 | `apps_qna/engines/judges/interview_card_quality_judge.py` | 106 | `import anthropic` | Judge adapter | Register in SANCTIONED_ADAPTER_FILES (peer of `narrative_judge_scorer.py`) |
| V-8 | `apps_research/engines/integration/chroma_research_store.py` | 164 | `import chromadb` | Research store | Register in SANCTIONED_ADAPTER_FILES (peer of `company_brief_engine.py`) |
| V-9 | `apps_underwriting_ai/engines/judges/rationale_quality_judge.py` | 500 | `import anthropic` | Judge adapter | Register in SANCTIONED_ADAPTER_FILES (peer of `frontier_rationale_judge.py`) |
| ADG | ADG view `v_p0_apps_direct_infra` | — | — | Structural P0 | Resolved by fixing V-4 through V-9 above |

**Total violation sites:** 9 files (13 import lines).
**Unique `SANCTIONED_ADAPTER_FILES` entries needed:** 8 (V-3 shares a file with V-2).

---

## Wave Structure

| Wave | Scope | Metric | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-------|--------|-------------|-------------|--------|-----------------|
| W0 | Pre-flight: verify baseline count, read scanner + affected files | Zero writes | ~200 | Scanner logic stable | ✅ DONE | `infra_wiring_scan.py` read; all 9 violation files confirmed; all classified as SANCTIONED_ADAPTER |
| W1 | Register all 8 files in `SANCTIONED_ADAPTER_FILES` + 6 apps_* paths in `_SANCTIONED_APP_DIRECT_INFRA` | 8 new scanner entries + 6 ADG view entries | ~300 | Confirmed in W0 | ✅ DONE | Each entry has justification comment |
| W2 | Verify `run_contract_gates.py` infra section green; update scorecard | CI infra section green | ~200 | No new violations introduced | ✅ DONE | infra_wiring_scan.py exits 0; run_contract_gates.py infra section passes |
| W3 | Write tests + update plan status | Test coverage for new entries | ~300 | | ✅ DONE | 8 positive + 1 negative = 9 new tests; 28/28 total pass |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W0.P1 | Read + confirm violations | `infra_wiring_scan.py`, 9 violation files | Must confirm each file is a thin adapter / lazy-import, not a deep architectural smell | ~200 | ✅ DONE |
| W1.P1 | Register `gemini_provider.py` + `provider_gateway.py` in scanner | `infra_wiring_scan.py` | Two agentic_core files — confirmed peer pattern | ~150 | ✅ DONE |
| W1.P2 | Register 6 apps_* files in scanner + ADG view allowlist | `infra_wiring_scan.py`, `tools/generate/infra_wiring_views.py` | All 6 registered in both SANCTIONED_ADAPTER_FILES and _SANCTIONED_APP_DIRECT_INFRA | ~150 | ✅ DONE |
| W2.P1 | Run full gate and confirm infra section green | `run_contract_gates.py` | Infra section prints ✅; exit 1 from unrelated executor_theater_gate (out of scope) | ~100 | ✅ DONE |
| W3.P1 | Write `is_allowed_path` tests for new entries | `tests/unit/ops_scripts/ci/test_infra_wiring_scan.py` (extend) | 8 parametrized positive + 1 negative; 28/28 pass | ~300 | ✅ DONE |

---

## Non-Goals

- Do **not** restructure the affected files or move their imports to different modules.
- Do **not** introduce new sanctioned adapters that don't already exist in the repo.
- Do **not** touch `run_contract_gates.py` beyond verifying it passes.
- Do **not** remediate any P1/P2/P3 ADG findings — this plan covers only the file-scan P0 failures.
- Do **not** merge with `core-addition-author-gate-governance-f3b9e2` — these are fully independent tracks.

---

## Definition of Done

| # | Criterion | Verification |
|---|-----------|-------------|
| DoD-1 | `python ops_scripts/ci/infra_wiring_scan.py` exits 0 | Direct execution |
| DoD-2 | `python ops_scripts/ci/run_contract_gates.py` no longer fails on infra wiring section | Observe "✅ Infrastructure wiring scan passed" in output |
| DoD-3 | 8 new `SANCTIONED_ADAPTER_FILES` entries each have a justification comment | Code review |
| DoD-4 | At least 8 new test cases in `test_infra_wiring_scan.py` (one per new entry) | `pytest tests/unit/ops_scripts/ci/test_infra_wiring_scan.py -v` exits 0 |
| DoD-5 | No regressions in `tests/unit/ops_scripts/ci/test_infra_wiring_scan.py` | Full test suite pass count ≥ pre-plan baseline |

### Verification-vs-Deferral

| Item | Verify in plan | Defer |
|------|---------------|-------|
| File-scan P0 violations eliminated | ✅ DoD-1 | — |
| `run_contract_gates.py` infra section green | ✅ DoD-2 | — |
| Justification comments present | ✅ DoD-3 | — |
| P1/P2/P3 ADG findings | ❌ | Future plan |
| Deeper refactor of any affected file | ❌ | Future plan |

---

## Gap Register

| ID | Description | P-Band | Status |
|----|-------------|--------|--------|
| GAP-01 | P1/P2/P3 ADG structural views still have non-zero counts | P4 | Deferred — separate ADG cleanup plan |
| GAP-02 | `run_contract_gates.py` exits 0 on all other gates (non-infra sections) already passing | — | Not a gap — confirmed passing |
| GAP-03 | `run_contract_gates.py` **remains red overall** (exit 1) due to `executor_theater_gate.py` failing with `ModuleNotFoundError: No module named 'tools'`. This is a pre-existing import-path issue **unrelated to infra wiring**. Full contract gate suite is NOT green. Requires separate governance/import-path remediation. | P3 | Out of scope — track as separate remediation |
