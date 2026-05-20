# W1 — SRFS aggregator receipt inventory

**Plan:** `apps-rg-srfs-aggregator-e7b2a1`  
**Date:** 2026-05-18  
**Proof level:** `SECTION_SRFS_STRUCTURAL_AUDIT_ONLY`  
**Method:** Static inspection of lane/dispatch writers, `normalized_srfs_section_reporting_fields`, W6 contract tests, and one on-disk real receipt (read-only).

---

## 1. Receipt write sites (production generated lanes)

| Section | Module | Line(s) | Writes | Pending interim write |
|---------|--------|---------|--------|------------------------|
| `headline` | `apps_rg/runtime/sections/headline_lane.py` | 1319 | Final only | No |
| `executive_summary` | `apps_rg/runtime/sections/executive_summary_lane.py` | 1205, 1348 | Pending → final overwrite | Yes (`1205`) |
| `unify_bullets` | `apps_rg/runtime/sections/unify_bullets_lane.py` | 732, 878 | Pending → final overwrite | Yes (`732`) |
| `unify_narrative` | `apps_rg/runtime/sections/unify_narrative_lane.py` | 816, 942 | Pending → final overwrite | Yes (`816`) |
| `ibm_bullets` | `apps_rg/runtime/sections/ibm_bullets_lane.py` | 799 | Final only | No |
| `ibm_narrative` | `apps_rg/runtime/sections/ibm_narrative_lane_api.py` | 1109 | Final only | No |
| `competencies` | `apps_rg/runtime/sections/competencies_lane_api.py` | 1934 | Final only | No |

**Shared normalizer:** `apps_rg/runtime/sections/selected_role_fact_set.py` — `merge_normalized_srfs_reporting_into_dict` / `normalized_srfs_section_reporting_fields` (called from every final write above).

**Registry / index (read-only for W1):**

| File | Role |
|------|------|
| `apps_rg/runtime/run_bundle_index.py:326` | Bundles `section_metric_receipt.json` in run index |
| `apps_rg/runtime/sections/executive_summary_proof_bundle.py:114` | Proof bundle member name |
| `apps_rg/runtime/validators/executive_summary_x2.py:166` | Required artifact filename in X2 set |

**Out of aggregator v1 scope (different shape):**

| File | Note |
|------|------|
| `apps_rg/runtime/dry_run/executive_summary_demo.py:2094–2122` | Demo receipt uses `section_id`, `quality_label`, `x1d_llm_judges` — **no W6 SRFS fields**. Exclude unless explicitly passed in manifest. |

---

## 2. Observed field sets

### 2.1 Pending interim receipt

Written mid-run for `executive_summary`, `unify_bullets`, `unify_narrative` only:

```json
{ "status": "pending", "prompt_hash": "<hex>" }
```

**Aggregator rule:** Treat as **incomplete** — aggregate PASS must **FAIL** (PASS guard). Not a third “complete” shape.

### 2.2 Final receipt — lane envelope (all seven)

Built as `_smr_*` dict before `merge_normalized_srfs_reporting_into_dict`:

| Field | Type | All 7 | Notes |
|-------|------|-------|-------|
| `run_id` | string | Yes | Per-section run id |
| `lane_id` | string | Yes | Same token as section key |
| `prompt_id` | string | Yes | Template id |
| `prompt_hash` | string | Yes | Non-empty on completed runs |
| `input_payload_hash` | string | Yes | |
| `output_payload_hash` | string \| null | Yes | `competencies` may be null |
| `claim_ledger_hash` | string \| null | Yes | `competencies` may be null |
| `runtime_generation_status` | string | Yes | e.g. `REAL_LLM`, stub modes |
| `product_quality_status` | string | Yes | e.g. `PASS`, `FAIL` |
| `x2_failed_gates` | string[] | Yes | Gate ids with `pass: false` |
| `x3_code` | string | Yes | Section disposition code |
| `proof_eligible` | bool | **6/7** | **Absent** on `unify_narrative` final write |
| `judge_proof_eligible` | bool | **6/7** | **Absent** on `unify_narrative` final write |

### 2.3 Final receipt — W6 SRFS block (merged)

Source: `normalized_srfs_section_reporting_fields` + `W6_FIELDS` in `tests/_apps_contract/test_apps_rg_srfs_w6_reporting.py`.

| Field | Type | Semantics |
|-------|------|-----------|
| `proof_pool_type` | string | `selected_role_fact_set` or `base_resume_fallback` |
| `selected_role_fact_set_used` | bool | SRFS path active |
| `srfs_section_id` | string | Section key (should match `lane_id`) |
| `candidate_fact_pool_count` | int | Slice pool size |
| `allowed_fact_ids_count` | int | Allowed id count |
| `required_fact_ids_count` | int | Required ids from plan |
| `claim_ledger_union_matches_required_fact_ids` | bool | Ledger/plan alignment |
| `out_of_slice_fact_ids` | string[] | From X2 gate observed_value |
| `fallback_used` | bool | True when base pool fallback |
| `fallback_reason` | string | Non-empty when fallback |
| `x2_srfs_gate_status` | enum | `PASS` \| `FAIL` \| `UNKNOWN` \| `NOT_APPLICABLE` |
| `srfs_allowed_fact_ids_count` | int | 0 when not SRFS-active |
| `full_resume_srfs_supported` | bool | Always `false` in normalizer today |

**SRFS-active detection (normalizer):** `selected_role_fact_set_used == true` **OR** `proof_pool_type == "selected_role_fact_set"`.

**`x2_srfs_gate_status` derivation:** Looks up per-section gate in `SRFS_SLICE_SOURCE_FACT_GATE_BY_SECTION` (e.g. `x2_headline_source_fact_ids_within_srfs_slice`). Missing gate when SRFS active → `UNKNOWN`. Not SRFS active → `NOT_APPLICABLE`.

### 2.4 On-disk sample (real, read-only)

`artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260518_173654/section_metric_receipt.json` — matches envelope + W6 block; `x2_srfs_gate_status: PASS`, `x3_code: X3_BLOCK` (section disposition does **not** block receipt structural completeness for aggregator).

---

## 3. Field aliases and normalization (W3 input)

| Source | Canonical | Rule |
|--------|-----------|------|
| `lane_id` | `section_id` | Prefer `srfs_section_id` if present and non-empty; else `lane_id` |
| `srfs_section_id` | `section_id` | Must equal `lane_id` when both present; mismatch → FAIL malformed |
| `status: "pending"` | `receipt_completeness: pending` | Fail PASS guard |
| (absent `status`) + full envelope | `receipt_completeness: complete` | Normal path |
| Missing W6 keys on complete envelope | — | FAIL missing SRFS status fields when SRFS-active |

**Optional envelope fields** (preserve under `extensions`, do not require for PASS):

- `proof_eligible`, `judge_proof_eligible` — missing on `unify_narrative` today.

---

## 4. SRFS-active vs not-applicable behavior

| Mode | `selected_role_fact_set_used` | `proof_pool_type` | `x2_srfs_gate_status` | Aggregator SRFS track |
|------|--------------------------------|-------------------|----------------------|------------------------|
| SRFS required (v1 default) | `true` | `selected_role_fact_set` | Must be `PASS` or `FAIL` (not `UNKNOWN`) | Enforce PASS guard |
| Base fallback | `false` | `base_resume_fallback` | `NOT_APPLICABLE` | Out of scope for seven-lane SRFS closeout PASS template |
| SRFS active, gate missing | `true` | `selected_role_fact_set` | `UNKNOWN` | **FAIL** aggregate (UNKNOWN never PASS) |

W6 tests: `test_apps_rg_srfs_w6_reporting.py` (SRFS mode all fields), `test_section_metric_receipt_w6_no_srfs_base_pool` (NOT_APPLICABLE path).

---

## 5. Prompt reflection proxy (v1 decision)

**Decision:** Use **`prompt_hash`** as v1 prompt-reflection proxy when SRFS-active.

| Condition | `prompt_reflection_status` |
|-----------|---------------------------|
| SRFS active + non-empty `prompt_hash` | `PASS` |
| SRFS active + empty/missing `prompt_hash` | `FAIL` |
| Not SRFS active | `NOT_APPLICABLE` |
| Pending receipt | `UNKNOWN` (receipt incomplete) |

**Rationale:** W5 prompt hierarchy is not persisted as a dedicated receipt field; `prompt_hash` is always set on completed lane writes and on pending stubs. **Deferred:** explicit `prompt_srfs_hierarchy_status` on receipts (lane change — not W1/W2).

---

## 6. Risks / gaps affecting W3

| ID | Gap | W3 handling |
|----|-----|-------------|
| G1 | `unify_narrative` omits `proof_eligible` / `judge_proof_eligible` | Optional in canonical row; store in `extensions` |
| G2 | Pending overwrite only on 3/7 lanes | Detect `status == "pending"` universally |
| G3 | `output_payload_hash` / `claim_ledger_hash` nullable | Allow null in schema; not PASS-guard fields |
| G4 | Demo/dry_run receipt shape | Reject or quarantine via manifest paths only |
| G5 | No `latest_successful` in loader | **Must not** import `resolve_run_dir_from_latest_successful_pointer` |
| G6 | Per-section `x3_code` / `product_quality_status` vary | Record in `section_results`; **do not** use for aggregate PASS (structural audit only) |
| G7 | Recursive `--receipt-root` may find multiple receipts per section | FAIL on duplicate `section_id` |

**W2 safety verdict:** Shapes are **consistent enough** for a canonical schema — one pending shape, one complete shape, stable W6 block. **No BLOCKER** for W2 schema.

---

## 7. Inspected files

- `apps_rg/runtime/sections/headline_lane.py`
- `apps_rg/runtime/sections/executive_summary_lane.py`
- `apps_rg/runtime/sections/unify_bullets_lane.py`
- `apps_rg/runtime/sections/unify_narrative_lane.py`
- `apps_rg/runtime/sections/ibm_bullets_lane.py`
- `apps_rg/runtime/sections/ibm_narrative_lane_api.py`
- `apps_rg/runtime/sections/competencies_lane_api.py`
- `apps_rg/runtime/sections/selected_role_fact_set.py`
- `apps_rg/runtime/internal/generated_lane_rollup.py` (`GENERATED_LANES`)
- `tests/_apps_contract/test_apps_rg_srfs_w6_reporting.py`
- `artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260518_173654/section_metric_receipt.json`
