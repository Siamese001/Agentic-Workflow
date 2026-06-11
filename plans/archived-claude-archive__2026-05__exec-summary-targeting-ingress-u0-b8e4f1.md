---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\exec-summary-targeting-ingress-u0-b8e4f1.md'
original_relative_path: '_archive\\2026-05\\exec-summary-targeting-ingress-u0-b8e4f1.md'
source_sha256: e3083a1f4fe11de9ea5f52819e35323661d9a26265ac911ba32e08ba4b02d63c
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: exec-summary-targeting-ingress-u0-b8e4f1
plan_type: feature
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: true
---

# Executive summary targeting ingress (U0-aligned)

**Slug:** `exec-summary-targeting-ingress-u0-b8e4f1`  
**Status:** Completed (2026-05-24)  
**Related:** Context parity containment (`targeting_context_authority.py`), live proof `exec_summary_20260524_233409`

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: COMPLETE
CURRENT_WAVE: W4
LAST_COMPLETED_WAVE: W4
LAST_UPDATED: 2026-05-24
NOTION_STATUS: Completed
NOTION_PAGE_ID: 36a27693-f55c-814d-8710-e92bf325b319
NOTION_PLAN_URL: https://www.notion.so/exec-summary-targeting-ingress-u0-b8e4f1-36a27693f55c814d8710e92bf325b319
NOTION_RECONCILED: 2026-05-24
PLAN_COMPLETED: 2026-05-24
PLAN_CREATED: slug=exec-summary-targeting-ingress-u0-b8e4f1 path=.cursor/plans/exec-summary-targeting-ingress-u0-b8e4f1.md status=Completed notion_page=36a27693-f55c-814d-8710-e92bf325b319

PLAN_COMPLETE: plan=exec-summary-targeting-ingress-u0-b8e4f1 note="Ingress cap before U0; parity_match true exec_summary_20260524_233409"

## Problem

Briefing was capped for L2 (Qwen/vLLM) **after** proof-pool/U0 saw the full CLI briefing. C0 graph targeting and judges could disagree with what generation received. Pre-fix run `exec_summary_20260524_140149`: judge saw ~15k briefing chars; L2 compiled prompt had ~692.

## Fix (two layers)

| Layer | Where | What |
|-------|--------|------|
| **Ingress** | `prepare_executive_summary_targeting_ingress` before `load_section_proof_for_lane` | Ranked section selection + vLLM char cap; same text to U0 front spine + proof pool |
| **Lane parity** | Freeze + `targeting_context_parity_receipt` | `generation_material_digest == judge_material_digest` on compiled prompt |

Evidence facts unchanged — U0 graph proof pool only. Briefing/JD remain non-proof targeting.

## Implementation waves

- [x] W1: `apps_rg/runtime/ingress/executive_summary_targeting_ingress.py`
- [x] W2: `section_proof_loader` + `front_contracts` overrides (`jd_text_override`, `briefing_text_override`)
- [x] W3: `executive_summary_lane` ingress-first; artifacts `targeting_ingress_receipt.json`, parity receipt, truthful ledger
- [x] W4: Live Brown run `exec_summary_20260524_233409` — `parity_match: true` on disk

## Key files

- `apps_rg/runtime/ingress/executive_summary_targeting_ingress.py`
- `apps_rg/runtime/targeting_context_authority.py`
- `apps_rg/runtime/c0/section_proof_loader.py`
- `apps_rg/runtime/spine/front_contracts.py`
- `apps_rg/runtime/sections/executive_summary_lane.py`
- `apps_rg/runtime/exit/executive_summary_x3.py`

## Live proof (W4)

| Check | Result |
|-------|--------|
| Ingress | 15210 → 11788 chars (`pre_proof_pool_u0_aligned`) |
| Parity | `parity_match: true`; gen/judge briefing 2596 chars; digest `f609b273…` |
| X3 parity codes | None (X3_BLOCK from ledger X2 + Claude soft-fail — out of scope) |

Receipt: [exec_summary_targeting_parity_live_proof_20260524_233409_receipt.md](docs/reports/apps_rg/exec_summary_targeting_parity_live_proof_20260524_233409_receipt.md)  
Artifacts: `artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260524_233409/`

## Proof commands

```bash
pytest -p pytest_timeout tests/unit/apps_rg/runtime/ingress/test_executive_summary_targeting_ingress.py tests/_apps_contract/test_targeting_context_authority_contract.py -o addopts=

python -m apps_rg --section executive_summary \
  --target-company "Brown & Brown" \
  --target-role "SVP IT Strategy & Innovation" \
  --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt \
  --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md
```

## Follow-up (completed)

- [exec-summary-targeting-wiring-closeout-b9e2a4.md](exec-summary-targeting-wiring-closeout-b9e2a4.md) — ledger before X2, regen X2 JD, parity-gated judge regen

## Out of scope / follow-ups

- Phase-2 runtime matrix for other lanes (`targeting_context_lane_runtime_audit.py`)
- X3 judge calibration / product quality PASS (separate plans)
