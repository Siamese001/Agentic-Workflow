---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\apps-rg-contract-harness-modernization-f4e8b2.md'
original_relative_path: '_archive\\2026-05\\apps-rg-contract-harness-modernization-f4e8b2.md'
source_sha256: 0ec9d8565d8d2acf5582f73dd2f1307d831876a8501a944c4d8fad2057f0dc40
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-rg-contract-harness-modernization-f4e8b2
plan_type: governance
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
parent_plan: graph-skills-deferred-followup-d7f2a8
parent_plan_status: In Progress
---

# Apps RG Contract Harness Modernization (W0–W5)

Burndown **212+ filtered `_apps_contract` failures** after graph-skills authority and CLI provider policy changes. Complements runtime proof in [graph-skills-deferred-followup-d7f2a8](graph-skills-deferred-followup-d7f2a8.md) (REAL_LLM / C0.1–C0.7).

> **plan_id discipline:** `plan=apps-rg-contract-harness-modernization-f4e8b2`

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: Completed
CURRENT_WAVE: W5
LAST_COMPLETED_WAVE: W5
LAST_UPDATED: 2026-05-26

PLAN_CREATED: slug=apps-rg-contract-harness-modernization-f4e8b2 path=.cursor/plans/apps-rg-contract-harness-modernization-f4e8b2.md status=Not Started

---

## Context (SCQA)

- **Situation** — Product CLI accepts only `qwen_vllm`; lanes require `augmented_skills_graph` evidence authority; spine C0 wiring is contract-tested (17 unit tests PASS).
- **Complication** — Filtered `_apps_contract` run: **298 passed / 212 failed / 4 errors** — tests still subprocess `--provider mock` or assert legacy proof-source enums.
- **Question** — How do we modernize contract tests without weakening gates or reintroducing mock CLI?
- **Answer** — W0 taxonomy register → W1–W5 bucket burndown → fast harness + optional live CLI gate.

---

## Status Tables

### Wave Progress

| Wave | Focus | Status | Success Criteria |
|------|-------|--------|------------------|
| W0 | Failure taxonomy + register | **DONE** | Register + junit + receipt on disk |
| W1 | B1 CLI harness (`--provider mock` removal) | **DONE** | Zero tests expect mock provider exit 0 |
| W2 | B2/B3 graph authority contracts | **DONE** | `augmented_skills_graph` assertions aligned |
| W3 | B4 front-spine fixture bridge | **DONE** | commercial_medium containment PASS (9 tests) |
| W4 | B5 competencies / product_shape / PA | **DONE** | Profiles, PA, SRFS, C0 safety, manual review restored |
| W5 | Filtered gate + fast harness | **DONE** | Fast spot green; live CLI split to `run_contract_harness_live.py` |

---

## Closeout

### Proof commands

| Tier | Command | Expected |
|------|---------|----------|
| Fast spot | `python ops_scripts/apps_rg/run_contract_harness_fast.py spot` | ~218+ pass, live CLI skipped |
| Fast slice | `python ops_scripts/apps_rg/run_contract_harness_fast.py slice` | `-k` filter, `not contract_harness_live` |
| Live CLI | `python ops_scripts/apps_rg/run_contract_harness_live.py` | Serial subprocess lanes when vLLM up |

Set `APPS_RG_CONTRACT_HARNESS_FAST=1` to skip `contract_harness_live` tests during dev/CI.

### Artifacts

- [contract_harness_failure_register_20260526.md](../docs/reports/apps_rg/contract_harness_failure_register_20260526.md)
- [contract_harness_modernization_w0_receipt.json](../docs/reports/apps_rg/contract_harness_modernization_w0_receipt.json)
- [contract_harness_modernization_w2_receipt.json](../docs/reports/apps_rg/contract_harness_modernization_w2_receipt.json)
- [contract_harness_modernization_w3_receipt.json](../docs/reports/apps_rg/contract_harness_modernization_w3_receipt.json)
- [contract_harness_modernization_w4_receipt.json](../docs/reports/apps_rg/contract_harness_modernization_w4_receipt.json)
- [contract_harness_modernization_w5_receipt.json](../docs/reports/apps_rg/contract_harness_modernization_w5_receipt.json)
- [run_contract_harness_fast.py](../ops_scripts/apps_rg/run_contract_harness_fast.py)
- [run_contract_harness_live.py](../ops_scripts/apps_rg/run_contract_harness_live.py)

### Deferred (follow-up, not blocking closeout)

- Full filtered `-k` slice with all live `python -m apps_rg` subprocess lanes in one pytest invocation (>1h when vLLM up) — use `run_contract_harness_live.py` instead.

---

## Wave detail

### W0 — Failure taxonomy (DONE)

- Run: `python ops_scripts/apps_rg/emit_contract_harness_w0_failure_register.py`
- Artifacts:
  - [contract_harness_failure_register_20260526.md](../docs/reports/apps_rg/contract_harness_failure_register_20260526.md)
  - [contract_harness_modernization_w0_receipt.json](../docs/reports/apps_rg/contract_harness_modernization_w0_receipt.json)
  - [contract_harness_w0_junit.xml](../docs/reports/apps_rg/contract_harness_w0_junit.xml)

### W1 — B1 CLI harness (DONE)

- Migrate subprocess tests to `qwen_vllm` + `live_allowed`; keep mock **rejection** policy test.

### W2 — B2/B3 graph authority (DONE)

- `augmented_skills_graph` assertions; W2 receipt on disk.

### W3 — B4 front spine (DONE)

- `test_commercial_medium_claim_output_containment` — front spine before proof pool.

### W4 — B5 tail (DONE)

- Section treatment profiles, PA binding, SRFS resolve, C0 minimum safety, manual review harness.

### W5 — Gate + fast harness (DONE)

- Fast harness: `contract_harness_live` marker, module-scoped CLI fixtures (1 run/file).
- Closeout receipt: [contract_harness_modernization_w5_receipt.json](../docs/reports/apps_rg/contract_harness_modernization_w5_receipt.json)
- Notion sync: `python tools/notion/plan_notion_sync_apps_rg_contract_harness_modernization_closeout.py`

---

## Out of scope

- Reintroducing `--provider mock` on product CLI
- Weakening X2 / FEC gates
- `agentic_core` edits

---

## Split marker

```
SPLIT_TO_NEW_PLAN: parent=graph-skills-deferred-followup-d7f2a8 child=apps-rg-contract-harness-modernization-f4e8b2 authorized_by=user decisive_reason="Contract test debt blocks filtered gate; parallel to REAL_LLM proof track"
```

```
PLAN_COMPLETE: plan=apps-rg-contract-harness-modernization-f4e8b2 note="W0–W5 done; fast harness shipped; live CLI via run_contract_harness_live.py"
```
