---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\exec-summary-srfs-bug-closeout-a3f291.md'
original_relative_path: '_archive\\2026-05\\exec-summary-srfs-bug-closeout-a3f291.md'
source_sha256: d903a68060293fc8fe3c5d2c5dd267340ac7166255b7705e7d4fc42f074272bd
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Executive Summary SRFS Bug Closeout (Minimum Scope)

PLAN_ID: exec-summary-srfs-bug-closeout-a3f291  
OBJECTIVE: Prove the original executive_summary proof-boundary bug is fixed (default CLI → active SRFS, not graph-only full PASS) with binding/regression tests plus one REAL_LLM artifact run; optionally close the remaining Claude synthesis soft-fail without weakening gates.

BUG_FIXED_DEFINITION:
- Default `python -m apps_rg --section executive_summary` with mandatory targeting inputs auto-materializes/resolves `artifacts/apps_rg/fact_inventory/selected_role_fact_set_active.json` (no `--selected-role-fact-set`).
- `section_metric_receipt.json` shows `selected_role_fact_set_used=true`, `proof_pool_type=selected_role_fact_set`, `x2_srfs_gate_status=PASS` (not `NOT_APPLICABLE`).
- `executive_summary_judge_packet.json` uses `SRFS_GRADE_ONLY_RUBRIC` (not `GRAPH_ONLY_GRADE_ONLY_RUBRIC`).
- No silent full PASS/ALLOW when SRFS is absent: graph-only path is explicit, non–proof-eligible, or fails closed.
- Any remaining X3 non-ALLOW is quality-only (e.g. `X3_REVIEW_JUDGE_SOFT_FAIL`), not proof-boundary regression.

NON_GOALS:
- agentic_core edits, all-section SRFS rollout, SRFS selection algorithm rewrite, gate/rubric weakening, graph-only as acceptable proof, smoke/mock-only proof, architecture cleanup.

---

## WAVES

### W1 — Binding and regression proof (unit/contract only)

**Already in repo (verify, do not re-litigate binding design):**
- `tests/_apps_contract/test_apps_rg_proof_pool_resolver_contract.py::test_executive_summary_default_resolves_active_srfs_binding` — default resolver, no manual SRFS path, `graph_only_claim_authority=false`.

**Add minimum regression tests (apps_rg only, ~2 small test functions):**

| Test | Assert |
|------|--------|
| `test_executive_summary_without_srfs_fails_closed_or_non_srfs_class` | Temporarily point active SRFS away or use empty `selected_facts_by_section.executive_summary`; resolver/lane metadata must **not** emit `selected_role_fact_set_used=true` + SRFS X2 PASS as a disguised full proof path. Expect explicit non-SRFS classification or blocked/NOT_APPLICABLE SRFS gates—not a proof-eligible ALLOW. |
| `test_executive_summary_judge_packet_srfs_rubric_when_srfs_active` | Build judge packet with `srfs_integration` + plan facts → `rubric_ref` ends with `#SRFS_GRADE_ONLY_RUBRIC`; without SRFS → `#GRAPH_ONLY_GRADE_ONLY_RUBRIC`. |

**Optional tighten (only if W1 gaps found):**
- Assert `resolve_section_proof_pool(..., section=executive_summary)` never sets `proof_source` to graph-only when `selected_role_fact_set_path=None` and active SRFS file exists (grep guard in `proof_pool_resolver.py` branch).

**W1 commands:**
```bash
set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
python -m pytest tests/_apps_contract/test_apps_rg_proof_pool_resolver_contract.py::test_executive_summary_default_resolves_active_srfs_binding -o addopts= -q
python -m pytest tests/_apps_contract/test_apps_rg_executive_summary_l2_proof_pool_alignment.py -o addopts= -q
python -m pytest tests/unit/apps_rg/test_executive_summary_cli_mandatory_inputs.py -o addopts= -q
# After new tests land:
python -m pytest tests/_apps_contract/test_apps_rg_proof_pool_resolver_contract.py tests/_apps_contract/test_apps_rg_executive_summary_l2_proof_pool_alignment.py -k executive_summary -o addopts= -q
```

**W1 exit:** All targeted pytest exit 0.

---

### W2 — Runtime proof and artifact inspection

**Canonical command (REAL_LLM, no mocks):**
```bash
python -m apps_rg --section executive_summary \
  --target-company "Unify Consulting" \
  --target-role "SVP Engineering, Agentic AI Platforms" \
  --jd apps_rg/config/default_jd_targeting.txt \
  --manual-brief apps_rg/config/default_targeting_briefing.txt
```

**Inspect latest** `artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_<ts>/`:

| Artifact | Pass signals |
|----------|----------------|
| `section_metric_receipt.json` | `selected_role_fact_set_used: true`, `proof_pool_type: selected_role_fact_set`, `x2_srfs_gate_status: PASS` |
| `selected_role_fact_set_ref.json` | `executive_summary_selected_fact_ids` non-empty; path → active SRFS |
| `executive_summary_judge_packet.json` | `rubric_ref` → `SRFS_GRADE_ONLY_RUBRIC`; `allowed_fact_packet` = SRFS slice |
| `x1d_*_provider_request_*.json` | Rubric/packet hash consistent with SRFS packet (no graph-only rubric text) |
| `x2_gate_outputs.json` | SRFS gates present and PASS: `x2_exec_summary_srfs_sentence_count_4_5`, `x2_exec_summary_srfs_density_word_count`, `x2_srfs_claim_business_metrics_substrate`, `x2_srfs_display_ledger_percent_parity`, `x2_north_star_style_echo_unsupported_zero` |
| `x3_disposition.json` | Not `X3_BLOCK` for decisive X1D factual-support on invented metrics/ops/commercialization |
| `srfs_judge_safe_repair.json` or `srfs_judge_safe_repair_final.json` | Present when model emits judge-risk prose; output fact-tight after repair |

**Negative control (one run, documents bug cannot return):** Same command with active SRFS renamed/missing → must **not** show graph-only full proof triple (`selected_role_fact_set_used=false` + `x2_srfs_gate_status=NOT_APPLICABLE` + proof-eligible ALLOW). Record as BLOCKED/NOT_APPLICABLE/non–proof-eligible only.

**W2 exit:** Binding artifacts green; X2 SRFS PASS; X1D uses SRFS rubric; no proof-boundary regression vs `exec_summary_20260520_000526`.

---

### W3 — Optional synthesis-only finish (only if W2 ends `X3_REVIEW_JUDGE_SOFT_FAIL` / Claude &lt; 4.0)

**Evidence gate:** Proceed only if W2 shows 2/3 X1D pass, `product_quality_status: PASS`, `x2_failed_gates: []`, and Claude findings are synthesis/voice only (overloaded S2, tactical S3, credential-heavy S5)—not unsupported claims.

**Tiny changes (apps_rg only, no new facts):**
1. **S2 split discipline** — In `exec_summary_srfs_judge_safe.py` / SRFS prompt appendix: prefer single-thread mechanism sentence (platform **or** governance metric, not both jammed) when both `001` and `003` cited; keep 40% only on governance clause.
2. **S5 arc closure** — Strengthen `build_fact_tight_s5_sentence` / `s5_needs_integrated_rewrite` to forbid bare “Holds … credentials” / “platform/governance depth”; require quant tail from `fact_quant_hpc_003` when in slice.
3. **Re-run W2 command once** — Confirm Claude ≥ 4.0 or acceptable `X3_REVIEW` with documented soft-fail only.

**W3 non-actions:** No new metrics, tools, AWS ops claims, commercialization, or SRFS fact selection changes.

---

## ACCEPTANCE_CRITERIA

| # | Criterion |
|---|-----------|
| 1 | Default targeting CLI resolves active SRFS without `--selected-role-fact-set` |
| 2 | `proof_pool_type=selected_role_fact_set`, `selected_role_fact_set_used=true` |
| 3 | Graph-only is not the default proof authority for executive_summary |
| 4 | Regression tests prevent silent SRFS-off full PASS |
| 5 | Judge packet uses SRFS rubric when SRFS active |
| 6 | REAL_LLM run: SRFS X2 gates PASS (including substrate + display/ledger parity) |
| 7 | No decisive X1D failure for unsupported margin/ops/commercialization (000526 class) |
| 8 | If X3 ≠ ALLOW, failure is quality-only (soft-fail), not binding regression |

**Plan PASS:** Criteria 1–7 on W2 artifact dir + W1 pytest green. Criterion 8 = W3 optional.

---

## COMMANDS_TO_RUN

```bash
# W1
set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
python -m pytest tests/_apps_contract/test_apps_rg_proof_pool_resolver_contract.py -k executive_summary -o addopts= -q
python -m pytest tests/_apps_contract/test_apps_rg_executive_summary_l2_proof_pool_alignment.py -o addopts= -q

# W2
python -m apps_rg --section executive_summary \
  --target-company "Unify Consulting" \
  --target-role "SVP Engineering, Agentic AI Platforms" \
  --jd apps_rg/config/default_jd_targeting.txt \
  --manual-brief apps_rg/config/default_targeting_briefing.txt
```

---

## ARTIFACTS_TO_INSPECT

- `artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_<latest>/section_metric_receipt.json`
- `selected_role_fact_set_ref.json`
- `executive_summary_judge_packet.json`
- `x1d_*_provider_request_*.json`
- `x2_gate_outputs.json`
- `x3_disposition.json`
- `srfs_judge_safe_repair.json` / `srfs_judge_safe_repair_final.json` (if present)
- Reference bad run (regression baseline): `exec_summary_20260520_000526`
- Reference improved run: `exec_summary_20260520_100247`

---

## RISKS

| Risk | Mitigation |
|------|------------|
| Qwen live provider down | W1 still proves binding; W2 BLOCKED until provider up—do not substitute mock |
| Active SRFS file drift between runs | Use `selection_id` + manifest digest in ref receipt; compare `executive_summary_selected_fact_ids` |
| W3 prompt tweak reintroduces hallucination | Judge-safe final pass + substrate/parity X2 gates must stay PASS |
| Over-scoping tests | Cap at 2 new regression tests; no cross-section parametrization |

---

## STOP_CONDITIONS

- **Stop success:** W1 green + W2 artifacts satisfy acceptance 1–7; document X3 code and whether W3 needed.
- **Stop blocked:** Provider/API unavailable—report BLOCKED, binding proof from W1 only.
- **Stop escalate:** W2 shows `selected_role_fact_set_used=false` or `GRAPH_ONLY` rubric with default CLI—binding regression; halt W3, fix resolver only.
- **Stop W3:** All three X1D ≥ 4.0 and proof-eligible policy satisfied—or user accepts REVIEW-only with 2/3 pass and explicit quality debt.

---

## Current state (2026-05-20)

| Run | Binding | X2 SRFS | X1D | X3 |
|-----|---------|---------|-----|-----|
| `exec_summary_20260520_000526` | Fixed | PASS | 0/3 decisive FAIL | `X3_BLOCK` (bug symptom) |
| `exec_summary_20260520_100247` | OK | PASS | 2/3 PASS, Claude 3.8 soft | `X3_REVIEW_JUDGE_SOFT_FAIL` (quality-only) |

Code already landed: percent parity regex, substrate union check, final `apply_srfs_judge_safe_repair` after density (`executive_summary_lane.py`, `executive_summary_x2.py`).
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
