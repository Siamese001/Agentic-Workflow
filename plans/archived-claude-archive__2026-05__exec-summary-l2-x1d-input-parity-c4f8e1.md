---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\exec-summary-l2-x1d-input-parity-c4f8e1.md'
original_relative_path: '_archive\\2026-05\\exec-summary-l2-x1d-input-parity-c4f8e1.md'
source_sha256: 88b73f362b88a0989bca431da673bd89108ef527f898f50703583e7848b27d13
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: exec-summary-l2-x1d-input-parity-c4f8e1
plan_type: remediation
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# Executive Summary — L2 / X1D Input Parity & Contract Unification

**North star:** Qwen (L2) and all X1D judges grade against **one explicit contract manifest**: same targeting material, same proof allowlist presentation, same style/proof rules (or a documented intentional GRADE_ONLY subset), and **authoritative X2 gate snapshot** before any judge call. Eliminate silent instruction drift (E0 gold vs I0, B4 vs credential policy, pre-X2 judge rounds, token-trim asymmetry).

**RCA SSOT:** [exec_summary_l2_x1d_input_parity_rca_20260525.md](../docs/reports/apps_rg/exec_summary_l2_x1d_input_parity_rca_20260525.md)  
**Related:** [exec-summary-x1d-transport-parity-d8f2a1.md](exec-summary-x1d-transport-parity-d8f2a1.md) (transport/reconcile — DONE), [exec-summary-operator-ship-a3f7c2.md](exec-summary-operator-ship-a3f7c2.md) (CERTIFIED loop), [exec-summary-targeting-ingress-u0](exec-summary-targeting-ingress-u0) (briefing cap — DONE on good runs)

> **plan_id discipline:** `exec-summary-l2-x1d-input-parity-c4f8e1` ↔ file stem ↔ markers `plan=exec-summary-l2-x1d-input-parity-c4f8e1`

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: Completed
CURRENT_WAVE: —
LAST_COMPLETED_WAVE: W5
LAST_UPDATED: 2026-05-25
WAVE_COMPLETE: plan=exec-summary-l2-x1d-input-parity-c4f8e1 wave=W5 note="closeout receipt, CI+pytest PASS, Notion Completed"
PLAN_COMPLETE: plan=exec-summary-l2-x1d-input-parity-c4f8e1 note="W0-W5 shipped; live Brown 3/3 deferred exec-summary-operator-ship-a3f7c2; receipt exec_summary_l2_x1d_input_parity_closeout_20260525.md"
DEFERRED_SCOPE: live_brown_3_of_3_certified → plan=exec-summary-operator-ship-a3f7c2 reason=implementation_complete_runtime_cert_loop_out_of_charter
PLAN_CREATED: slug=exec-summary-l2-x1d-input-parity-c4f8e1 path=.cursor/plans/exec-summary-l2-x1d-input-parity-c4f8e1.md status=Not Started notion_page=36b27693-f55c-819e-8604-e2bb21c951a6

NOTION_PAGE_ID: 36b27693-f55c-819e-8604-e2bb21c951a6
NOTION_PLAN_URL: https://www.notion.so/exec-summary-l2-x1d-input-parity-c4f8e1-36b27693f55c819e8604e2bb21c951a6

---

## Context (SCQA)

- **Situation** — Targeting ingress + material digest parity can be true while Claude still soft-fails and Qwen emits brushstroke stacks.
- **Complication** — `apps_rg` treats U0 as the task boundary but ships **three prompt surfaces** (full PA compile, judge packet, regen remediation). Judges never see E0/I0/composition_plan; first judge round runs **before** X2; `deterministic_gate_summary` omits most X2 gates (e.g. synthesis_quality).
- **Question** — How do we unify inputs without collapsing GRADE_ONLY (judges must not rewrite) or weakening X2?
- **Answer** — Contract manifest + ordered lane fixes + CI drift gates; keep GRADE_ONLY but **inject** generation-law summaries and **full** gate snapshots into the judge packet.

---

## Architecture Invariants

| ID | Invariant |
|----|-----------|
| INV-1 | No edits to `agentic_core` without separate authorization. |
| INV-2 | Do not weaken X2 gates/fixtures to force judge PASS. |
| INV-3 | GRADE_ONLY preserved — judges still do not receive full `compiled_prompt` as user message. |
| INV-4 | Targeting parity remains required; expand parity to **instructional manifest** where feasible. |
| INV-5 | Any intentional L2-only block (E0 detail) must be listed in manifest `judge_excluded_by_design` with rubric alignment proof. |

---

## Product Decisions (lock W0)

| ID | Decision |
|----|----------|
| PD-1 | Remove `exec_summary_gold_base_resume_001` from `_EXEC_SUMMARY_POSITIVE_COMPILE_IDS`; lead with `exec_summary_pos_svp_it_strategy_001`. |
| PD-2 | B4: drop `fact_certs_001` from **required** brushstroke display binding; allow implied credibility only (align I0). |
| PD-3 | Tighten `check_exec_summary_no_credential_dump` to fail **named cert labels** in display text (≥2 markers or any FSA/AWS/Databricks phrase in S4–S6). |
| PD-4 | **No MODEL_BACKED X1D before X2 completes** on REAL_LLM path; first judge call uses `build_deterministic_gate_summary_from_x2_gates`. |
| PD-5 | Extend judge `deterministic_gate_summary` to include all `JUDGE_PACKET_REQUIRED_GATE_KEYS` **plus** synthesis/mechanical-opener gates mapped to rubric dims. |
| PD-6 | Emit `generation_grade_contract_manifest.json` per run (hashes of I0/E0/rubric/gates/targeting). |
| PD-7 | Token trim: if L2 JD/briefing compressed, apply **same** bounded text to judge packet `targeting_context` (or fail-closed parity break). |

---

## Findings backlog (waves map)

| ID | Finding | Wave |
|----|---------|------|
| F1 | E0 gold_base vs I0/negative E0 | W1 |
| F2 | B4 cert required vs I0 forbid cert names | W1 |
| F3 | ATS/JD themes without proof facts | W2 |
| F4 | X2 weak mechanism/credential vs judge residual | W1 |
| F5 | Pre-X2 judge + partial gate summary | W2 |
| F6 | Token-trim L2-only (C1) | W3 |
| F7 | Judge regen fourth surface | W4 |
| F8 | Metric derivative enrich judges-only | W3 |
| F9 | SRFS vs GRAPH rubric split | W2 |
| F10 | enrich_allowed_fact_packet asymmetry | W3 |

---

## Waves

### W0 — Lock decisions + manifest schema (no runtime behavior change)

| Task | Owner | Proof |
|------|-------|-------|
| W0.1 | Approve PD-1–PD-7 in plan | This file updated `PLAN_STATUS: In Progress` |
| W0.2 | Add `generation_grade_contract_manifest.schema.json` under `apps_rg/contracts/` | Schema file + unit test load |
| W0.3 | Document three surfaces in operator guide § Input parity | [executive_summary_operator_guide.md](../docs/apps_rg/executive_summary_operator_guide.md) |

**Exit:** Schema + operator doc; no lane edits.

---

### W1 — L2 compile / X2 alignment (generator contract)

| Task | Files | Proof |
|------|-------|-------|
| W1.1 | Reorder/remove gold E0 | `apps_rg/prompt_assembly/e0_examples.py`, `executive_summary_examples.yaml` | Unit: compiled E0 first id = svp_it_strategy |
| W1.2 | B4 cert optional | `executive_summary_composition.py` | Composition plan JSON on fixture run |
| W1.3 | Credential X2 tighten | `executive_summary_x2.py`, `executive_summary_composition.py` | Tests: 2-marker AWS/Databricks fails |
| W1.4 | Add C0 targeting gap note for EA/interop when JD demands | `format_strategy_executive_targeting_appendix` or composition | Fixture: gap_notes when no interop facts |

**Exit:** `pytest tests/unit/apps_rg/test_executive_summary_*` + `check_executive_summary_x2_x1d_drift.py` PASS.

---

### W2 — Judge packet / lane ordering

| Task | Files | Proof |
|------|-------|-------|
| W2.1 | Move initial `run_llm_judges` to **after** `run_x2_gates` (REAL_LLM) | `executive_summary_lane.py` | Artifact: no `x1d_llm_judge_outputs.json` before `x2_gate_outputs.json` |
| W2.2 | Merge SRFS dim-8 + synthesis gate keys into `build_deterministic_gate_summary` | `executive_summary_judge_packet.py` | `judge_packet_pre_x2_gate_keys()` ⊇ synthesis gates |
| W2.3 | Rubric dim → gate_id map in packet | `executive_summary_judge_packet.py` | `canonical_judge_contract.json` includes `dimension_gate_map` |
| W2.4 | Inject `generation_law_digest` block (I0 credential + anti-inventory one-liners) | `render_judge_prompt_from_packet` | Manifest hash includes digest |
| W2.5 | Unify GRAPH rubric with active I0 ATS rule (proof-gap clause) | `GRAPH_ONLY_GRADE_ONLY_RUBRIC` | Contract test in `test_executive_summary_x1d_judge_contract.py` |

**Exit:** Frozen packet regression + Brown run 3/3 or documented residual with gate map receipt.

---

### W3 — Parity hardening (targeting + trim + fact packet)

| Task | Files | Proof |
|------|-------|-------|
| W3.1 | `generation_grade_contract_manifest.json` writer in lane | `executive_summary_lane.py` | Artifact path in run dir |
| W3.2 | Token trim sync to judge `targeting_context` | `executive_summary_token_budget.py`, `build_executive_summary_judge_packet` | Simulated trim test: parity false or synced digest |
| W3.3 | Align C0 display with judge enrich (derivatives) | `executive_summary_pa.py` or document exclusion | Manifest `fact_packet_digest` match |
| W3.4 | CI gate `check_exec_summary_l2_x1d_manifest_drift.py` | `ops_scripts/ci/` | `run_contract_gates.py` PASS |

**Exit:** CI green + manifest on proof run.

---

### W4 — Regen path unification

| Task | Files | Proof |
|------|-------|-------|
| W4.1 | Regen: optional `recompile_pa_from_runtime_payload` flag | `executive_summary_judge_remediation.py` | Regen receipt shows `pa_recompiled: true` |
| W4.2 | Regen uses post-X2 packet + full gate summary only | `executive_summary_lane.py` | `judge_regen` never references pre-X2 packet hash |
| W4.3 | Dimension remediation lines capped + deduped with manifest | `executive_summary_x1d_dimension_verdicts.py` | Unit test |

**Exit:** Cert loop script ≥1 run 3/3 or honest FAIL with manifest diff.

---

### W5 — Closeout

| Task | Proof |
|------|-------|
| W5.1 | Receipt [exec_summary_l2_x1d_input_parity_closeout_20260525.md](../docs/reports/apps_rg/exec_summary_l2_x1d_input_parity_closeout_20260525.md) | PASS/PARTIAL with commands |
| W5.2 | Notion Plans row Completed | `plan_notion_sync_*` exit 0 |
| W5.3 | Link from operator-ship plan if CERTIFIED unblocked | Cross-link in both plans |

---

## Definition of Done

| DoD | Criterion | Status |
|-----|-----------|--------|
| D1 | RCA on disk | PASS |
| D2 | Plan on disk + Notion | PASS |
| D3 | W1 E0 + credential alignment tests PASS | PASS |
| D4 | W2 No pre-X2 MODEL_BACKED judges | PASS |
| D5 | W3 Manifest + CI drift gate | PASS |
| D6 | Live Brown 3/3 MODEL_BACKED_PASS (or BLOCKED receipt) | DEFERRED → exec-summary-operator-ship-a3f7c2 |
| D7 | No X2/judge weakening commits | PASS (named-cert tighten only) |

---

## Commands (verification)

```bash
# Contract / drift
python ops_scripts/ci/check_executive_summary_x2_x1d_drift.py
python ops_scripts/ci/check_section_x2_x1d_drift.py

# Unit
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/unit/apps_rg/test_executive_summary_x1d_judge_contract.py tests/_apps_contract/test_executive_summary_x2_x1d_drift_ci.py -q

# Live (Brown)
python -m apps_rg --section executive_summary --target-company "Brown & Brown" --target-role "SVP IT Strategy & Innovation" --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md

# Notion
python tools/notion/plan_notion_sync_exec_summary_l2_x1d_input_parity.py
```

---

## Deferred / out of scope

- New proof facts for brokerage EA/interop (product/content decision) — W2 may use `gap_notes` only until facts exist.
- Core judge panel harness migration (`core-judge-panel-harness-f3c8d1`) — apps manifest first.
- Headline/competencies judge packets — separate plan if needed.

---

DEFERRED_SCOPE: live_brown_3_of_3_certified → exec-summary-operator-ship-a3f7c2 (plan closed; runtime proof out of charter).
