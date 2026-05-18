# SRFS real-receipt fallback diagnosis (W1–W2)

**Plan:** apps-rg-srfs-aggregator-e7b2a1 (post-closeout)  
**Proof level:** `DIAGNOSIS_ONLY`  
**Date:** 2026-05-18  
**Binding trial:** `docs/reports/apps_rg/srfs_aggregator_real_receipt_trial_manifest.json`

---

## Executive summary

The aggregator behaved correctly. Six lanes emitted `base_resume_fallback` because the **operator commands that produced those on-disk receipts did not pass `--selected-role-fact-set`**. Lane SRFS wiring is present and covered by W3–W7 contract tests; the gap is **missing SRFS input on the real/plumbing runs**, not a broken receipt reporter.

`executive_summary` was SRFS-active because its `run_manifest.json` command includes:

`--selected-role-fact-set artifacts/apps_rg/fact_inventory/selected_role_fact_set_20260518T181200Z_exec_summary_srfs_cli_proof.json`

---

## W1 — Per-lane inspection

### Receipt signal (all six non-active lanes)

| Field | Observed value |
|-------|----------------|
| `proof_pool_type` | `base_resume_fallback` |
| `selected_role_fact_set_used` | `false` |
| `fallback_used` | `true` |
| `fallback_reason` | `no_selected_role_fact_set_supplied` |
| `x2_srfs_gate_status` | `NOT_APPLICABLE` |

Source: `selected_role_fact_set.base_proof_pool_metadata()` when `srfs_path` is empty in lane entry.

### Lane diagnosis table

| Lane | Receipt path (trial) | Command had `--selected-role-fact-set`? | Why `base_resume_fallback`? | SRFS load code? | Slice by section? | X2 SRFS gate when active? | Receipt fields correct? |
|------|----------------------|----------------------------------------|-----------------------------|-----------------|-------------------|---------------------------|-------------------------|
| **headline** | `.../headline/real/headline_20260518_182333/section_metric_receipt.json` | **No** | SRFS path absent on CLI → `headline_lane` uses `base_proof_pool_metadata` | Yes (`headline_lane.py` ~786–802) | Yes (`resolve_srfs_section_proof_bundle`) | Yes (`headline_x2`) | Yes |
| **unify_bullets** | `.../unify_bullets/real/unify_bullets_20260518_182346/...` | **No** | Same | Yes (`unify_bullets_lane.py` ~477–479) | Yes | Yes (`unify_bullets_x2`) | Yes |
| **unify_narrative** | `.../unify_narrative/real/unify_narrative_20260518_182352/...` | **No** | Same | Yes (`unify_narrative_lane.py` ~539–541) | Yes | Yes (`unify_narrative_x2`) | Yes |
| **ibm_bullets** | `.../ibm_bullets/plumbing/ibm_bullets_20260518_182358/...` | **No** | Same (plumbing bucket, still no SRFS flag) | Yes (`ibm_bullets_lane.py` ~439–441) | Yes | Yes (`ibm_bullets_x2`) | Yes |
| **ibm_narrative** | `.../ibm_narrative/real/ibm_narrative_20260518_182405/...` | **No** | Same | Yes (`ibm_narrative_dispatch.py` ~598–600) | Yes | Yes (`ibm_narrative_x2`) | Yes |
| **competencies** | `.../competencies/real/competencies_20260518_182432/...` | **No** | Same | Yes (`competencies_dispatch.py` ~1399–1401) | Yes | Yes (`competencies_x2`) | Yes |
| **executive_summary** (control) | `.../exec_summary_20260518_173654/...` | **Yes** | SRFS JSON supplied → `srfs_proof_pool_metadata` | Yes | Yes | Yes | Yes — **SRFS-active** |

### CLI / dispatch threading (static)

| Layer | Finding |
|-------|---------|
| `apps_rg/__main__.py` | `--selected-role-fact-set` defined (~679); passed to `run_canonical_apps_rg_from_cli_primitives(..., selected_role_fact_set=...)` (~881) |
| `canonical_dispatch.py` | Parameter forwarded for all seven generated lanes (~1015–1139) |
| Lane entry | Pattern: `srfs_path = getattr(args, "selected_role_fact_set", "").strip()` → if truthy, `resolve_srfs_section_proof_bundle`; else `base_proof_pool_metadata` |

### Prompt assembly

When SRFS path is set, lanes build `selected_fact_plan` and `proof_pool_metadata` from the **section slice** (not full base resume allowlist). When absent, lanes use `collect_employment_bullets(base)` (or section equivalent) — consistent with W6 no-SRFS tests.

### Secondary note: executive-only SRFS inventory file

`selected_role_fact_set_20260518T181200Z_exec_summary_srfs_cli_proof.json` lists all seven section keys but **only `executive_summary` has facts** (7 rows); other sections have **empty slices**. Passing this file to non-exec lanes may activate SRFS mode but **fail-closed on empty slice** (early load / X2). For seven-lane SRFS-active receipts, use a **multi-section SRFS with non-empty per-section facts** (e.g. `artifacts/apps_rg/test_fixtures/srfs_w7/w7_realistic_nested_facts.json` or `w7_realistic_bare_list.json`) — not a lane code change.

### competencies run_manifest caveat

Trial competencies receipt’s `run_manifest.command` references pytest, not a governed `python -m apps_rg --section competencies` invocation. Treat as **non-representative operator path** for SRFS CLI proof; re-run with explicit apps_rg CLI when repairing.

---

## W2 — Repair strategy matrix

| Lane | Repair classification | Smallest repair |
|------|----------------------|-----------------|
| headline | **expected fallback due to missing SRFS fixture/input** | Re-run with `--selected-role-fact-set <seven-section SRFS>` |
| unify_bullets | **expected fallback due to missing SRFS fixture/input** | Same |
| unify_narrative | **expected fallback due to missing SRFS fixture/input** | Same |
| ibm_bullets | **expected fallback due to missing SRFS fixture/input** | Same |
| ibm_narrative | **expected fallback due to missing SRFS fixture/input** | Same |
| competencies | **expected fallback due to missing SRFS fixture/input** (+ manifest hygiene) | Same + fresh governed CLI run |
| executive_summary | **no repair** (already SRFS-active on trial receipt) | Optional re-run with shared seven-section SRFS for consistency |

**Not indicated (no code change before input proof):**

- CLI argument plumbing issue — flag exists and threads when provided  
- dispatcher parameter issue — forwarded in `canonical_dispatch`  
- lane runtime argument issue — all lanes read `args.selected_role_fact_set`  
- receipt reporting issue — accurately reports fallback  
- X2 validator issue — gates exist; inactive only because pool is base fallback  

---

## Recommended batch order (next waves)

### R1 — SRFS input SSOT (no lane edits)

1. Pin one **seven-section, non-empty** SRFS JSON for real reruns (candidate: `artifacts/apps_rg/test_fixtures/srfs_w7/w7_realistic_nested_facts.json` or bare-list twin).  
2. Document canonical CLI template:

```text
python -m apps_rg --section <lane> \
  --selected-role-fact-set <path-to-seven-section-srfs.json> \
  ... (existing provider/judge flags as needed for structural proof only)
```

3. Do **not** use `latest_successful_*` pointers for receipt selection.

### R2 — Representative lane proof (single lane)

- **First lane:** `unify_bullets` (representative generated lane + pending interim receipt pattern in code).  
- Verify: `runtime_payload.proof_pool_metadata.proof_pool_type == selected_role_fact_set`, receipt `selected_role_fact_set_used == true`, `x2_srfs_gate_status` in `PASS|FAIL` (not `NOT_APPLICABLE`).  
- Static gate: existing `test_apps_rg_srfs_w6_reporting.py` / `test_apps_rg_srfs_w3_lane_adoption.py` (no new generation in diagnosis wave).

### R3 — Six-lane rerun batch

Re-run the six non-active lanes with the **same** SRFS path. Prefer offline/stub provider flags already used in structural proof (no live Qwen in this track).

### R4 — Real-receipt aggregator trial v2

Build new explicit manifest under `artifacts/apps_rg/audit/srfs_section_aggregation/real_receipt_trial_v2/` and re-run aggregator (unchanged).

### Changes to avoid

- Do not modify `apps_rg/audit/*` aggregator or PASS guard.  
- Do not weaken X2/X3.  
- Do not patch on-disk receipts.  
- Do not assume lane bugs before one SRFS-flagged rerun proves input hypothesis.  
- Do not use exec-summary-only SRFS file for non-exec lanes without populating slices.

---

## Root cause (decisive)

**Operator / run-input gap:** Real and plumbing section runs were invoked without `--selected-role-fact-set`, so lanes correctly selected base resume proof pools and receipts correctly recorded `no_selected_role_fact_set_supplied`.

---

## Stop condition met

Diagnosis shows **missing real SRFS input on the commands that produced the six receipts**, not missing lane SRFS wiring. Next step is a **real SRFS fixture + governed CLI rerun plan** (R1–R4 above), not preemptive lane patches.
