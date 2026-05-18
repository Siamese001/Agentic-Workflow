# W2 — SRFS aggregator schema and deterministic rules

**Plan:** `apps-rg-srfs-aggregator-e7b2a1`  
**Date:** 2026-05-18  
**Depends on:** `docs/reports/apps_rg/srfs_aggregator_w1_receipt_inventory.md`  
**Proof level:** `SECTION_SRFS_STRUCTURAL_AUDIT_ONLY`

---

## 1. Canonical normalized receipt row (`apps_rg.canonical_section_metric_receipt.v1`)

Produced by `normalize_section_receipt(raw)` from on-disk `section_metric_receipt.json`.

```json
{
  "schema_version": "apps_rg.canonical_section_metric_receipt.v1",
  "section_id": "headline",
  "receipt_path": "path/to/section_metric_receipt.json",
  "receipt_completeness": "complete|pending|malformed",
  "run_id": "string|null",
  "prompt_hash": "string",
  "srfs_active": true,
  "proof_pool_type": "selected_role_fact_set|base_resume_fallback",
  "selected_role_fact_set_used": true,
  "x2_srfs_gate_status": "PASS|FAIL|UNKNOWN|NOT_APPLICABLE",
  "srfs_structural_status": "PASS|FAIL|UNKNOWN|NOT_APPLICABLE",
  "prompt_reflection_status": "PASS|FAIL|UNKNOWN|NOT_APPLICABLE",
  "full_resume_srfs_supported": false,
  "required_fact_ids_count": 0,
  "allowed_fact_ids_count": 0,
  "candidate_fact_pool_count": 0,
  "claim_ledger_union_matches_required_fact_ids": true,
  "out_of_slice_fact_ids": [],
  "fallback_used": false,
  "fallback_reason": "",
  "x3_code": "string|null",
  "product_quality_status": "string|null",
  "x2_failed_gates": [],
  "extensions": {}
}
```

### Derivation rules

| Derived field | Rule |
|---------------|------|
| `receipt_completeness` | `pending` if `raw.status == "pending"`; `malformed` if JSON invalid or cannot resolve `section_id`; else `complete` |
| `section_id` | `srfs_section_id` ?? `lane_id`; required on complete receipts |
| `srfs_active` | `selected_role_fact_set_used` OR `proof_pool_type == "selected_role_fact_set"` |
| `srfs_structural_status` | If not `srfs_active`: `NOT_APPLICABLE`. If `x2_srfs_gate_status` is `UNKNOWN`: `UNKNOWN`. If `PASS`/`FAIL`: same value. |
| `prompt_reflection_status` | If pending: `UNKNOWN`. If `srfs_active` and non-empty `prompt_hash`: `PASS`. If `srfs_active` and empty hash: `FAIL`. Else `NOT_APPLICABLE`. |
| `extensions` | Copy optional source keys not in core row (e.g. `proof_eligible`, `judge_proof_eligible`, hashes) |

### Required keys on `complete` receipts (SRFS-active / closeout track)

All W6 fields from W1 §2.3 plus `prompt_hash`, `lane_id` or `srfs_section_id`.

---

## 2. Receipt manifest (`apps_rg.srfs_receipt_manifest.v1`)

Preferred aggregator input (W4).

```json
{
  "schema_version": "apps_rg.srfs_receipt_manifest.v1",
  "receipts": {
    "headline": "relative/or/absolute/path/section_metric_receipt.json",
    "executive_summary": "...",
    "unify_bullets": "...",
    "unify_narrative": "...",
    "ibm_bullets": "...",
    "ibm_narrative": "...",
    "competencies": "..."
  }
}
```

**Rules:** Exactly one path per key in `receipts`; keys must be subset of `GENERATED_LANES`; duplicate resolved `section_id` → FAIL.

---

## 3. Audit report schema (`apps_rg.srfs_audit_report.v1`)

```json
{
  "schema_version": "apps_rg.srfs_audit_report.v1",
  "status": "PASS|WARN|FAIL",
  "proof_level": "SECTION_SRFS_STRUCTURAL_AUDIT_ONLY",
  "run_id": "aggregator_run_<utc_compact>",
  "created_at_utc": "ISO-8601-Z",
  "source_manifest_ref": "docs/reports/apps_rg/srfs_per_section_w1_w7_closeout_manifest.json",
  "receipt_manifest_ref": "path|null",
  "receipt_root": "path|null",
  "expected_sections": ["headline", "executive_summary", "unify_bullets", "unify_narrative", "ibm_bullets", "ibm_narrative", "competencies"],
  "observed_sections": [],
  "missing_sections": [],
  "unexpected_sections": [],
  "duplicate_sections": [],
  "section_results": {
    "<section_id>": {
      "receipt_path": "...",
      "receipt_completeness": "complete|pending|malformed",
      "srfs_active": true,
      "srfs_structural_status": "PASS|FAIL|UNKNOWN|NOT_APPLICABLE",
      "x2_srfs_gate_status": "PASS|FAIL|UNKNOWN|NOT_APPLICABLE",
      "prompt_reflection_status": "PASS|FAIL|UNKNOWN|NOT_APPLICABLE",
      "selected_role_fact_set_used": true,
      "full_resume_srfs_supported": false,
      "x3_code": null,
      "pass_guard_violations": []
    }
  },
  "cross_section_findings": {
    "all_expected_sections_present": false,
    "any_pending_receipt": false,
    "any_malformed_receipt": false,
    "any_unknown_srfs_status": false,
    "any_full_resume_srfs_true": false,
    "any_section_x2_srfs_fail": false,
    "sections_srfs_active_count": 0
  },
  "deterministic_findings": [],
  "advisory_judge_review": {
    "enabled": false,
    "status": "NOT_RUN",
    "mocked_or_live": "not_run",
    "can_change_deterministic_status": false,
    "findings": [],
    "limitations": ["W6 advisory judge not in scope for W3-W5 implementation"]
  },
  "explicit_non_claims": [
    "proof_level is SECTION_SRFS_STRUCTURAL_AUDIT_ONLY only.",
    "This report does not assert runtime certification.",
    "This report does not assert live Qwen or vLLM output quality.",
    "This report does not assert real-judge X3 ALLOW or product release.",
    "This report does not assert full résumé R4 SRFS or modular_resume_generation wiring.",
    "Section x3_code and product_quality_status are informational only, not aggregate PASS criteria.",
    "Advisory LLM judge output does not override deterministic status."
  ],
  "decisive_reason": "string"
}
```

**Fixed string:** `proof_level` MUST always be exactly `SECTION_SRFS_STRUCTURAL_AUDIT_ONLY`.

---

## 4. Deterministic PASS / WARN / FAIL rules

Evaluated **after** all sections normalized. **Advisory judge ignored.**

### 4.1 Aggregate FAIL if any

1. `missing_sections` non-empty  
2. `duplicate_sections` non-empty  
3. Any section `receipt_completeness` ∈ `{pending, malformed}`  
4. Any section fails **PASS guard** (§5)  
5. `explicit_non_claims` empty  
6. Loader used `latest_successful_*` inference (forbidden — test/grep guard in W5)  
7. Internal error: UNKNOWN coerced to PASS (meta/regression)

### 4.2 Aggregate WARN if

- No FAIL conditions, and  
- (`unexpected_sections` non-empty **OR** any complete receipt had extra top-level keys moved to `extensions` **OR** advisory judge `NOT_RUN`), and  
- All PASS guards satisfied for expected sections  

### 4.3 Aggregate PASS if

- No FAIL/WARN triggers except: all seven expected sections present, all `receipt_completeness == complete`, all PASS guards pass, `explicit_non_claims` populated, no duplicates  

**Note:** Aggregate PASS **does not** require section `x3_code == X3_ALLOW` or `product_quality_status == PASS`. A section may be `X3_BLOCK` with a structurally complete SRFS receipt (see W1 sample).

**Note:** `x2_srfs_gate_status == FAIL` on a section is **allowed** for aggregate PASS (known failure); only `UNKNOWN` is fail-closed for SRFS-active sections.

---

## 5. PASS guard (per-section → blocks aggregate PASS)

For each **expected** section, aggregate PASS forbidden when:

| Guard | Condition |
|-------|-----------|
| G-missing | No receipt path in manifest / not discovered under root |
| G-pending | `receipt_completeness == pending` |
| G-malformed | `receipt_completeness == malformed` |
| G-unknown-srfs | `srfs_active` and `x2_srfs_gate_status == UNKNOWN` |
| G-unknown-structural | `srfs_active` and `srfs_structural_status == UNKNOWN` |
| G-prompt | `srfs_active` and `prompt_reflection_status == FAIL` |
| G-full-resume | `full_resume_srfs_supported == true` |
| G-srfs-required | Closeout track: `srfs_active == false` when manifest expects SRFS receipts (all seven SRFS-mode) |

Record violations in `section_results[].pass_guard_violations` and `deterministic_findings`.

---

## 6. Forbidden proof-language rules

Applies to: `decisive_reason`, markdown body, CLI stdout, closeout `decisive_reason`.

**Forbidden unless inside `explicit_non_claims` as negation:**

- release proof  
- product ALLOW  
- certified / certification (affirmative)  
- runtime certified  
- full resume SRFS (affirmative product claim)  

**Allowed:** structural audit terms — receipt inventory, PASS guard, SRFS field completeness, `SECTION_SRFS_STRUCTURAL_AUDIT_ONLY`.

---

## 7. Explicit NOT_PROVEN enforcement

Every `apps_rg_srfs_audit_report.json` MUST include `explicit_non_claims` (≥6 strings per schema §3).

W8 closeout manifest MUST repeat `proof_level: SECTION_SRFS_STRUCTURAL_AUDIT_ONLY` and list same NOT_PROVEN family.

Aggregator MUST NOT emit `agentic_core` paths, judge execution artifacts, or `latest_successful_real_run.json` reads.

---

## 8. W5 fixture / test matrix (planned)

| Test ID | Fixture/setup | Expected `status` |
|---------|---------------|-------------------|
| T-pass-7 | Manifest with 7 valid SRFS-complete receipts | PASS |
| T-missing-sec | Manifest missing `competencies` | FAIL |
| T-pending | One receipt `status: pending` | FAIL |
| T-malformed-json | Invalid JSON file | FAIL |
| T-malformed-id | `lane_id` ≠ `srfs_section_id` | FAIL |
| T-missing-srfs-field | SRFS-active receipt missing `x2_srfs_gate_status` | FAIL |
| T-unknown-x2 | SRFS-active, `x2_srfs_gate_status: UNKNOWN` | FAIL |
| T-empty-prompt | SRFS-active, `prompt_hash: ""` | FAIL |
| T-full-resume-true | `full_resume_srfs_supported: true` | FAIL |
| T-nonclaims-empty | Builder omits non-claims (unit) | FAIL |
| T-unknown-coerce | Regression: UNKNOWN must not map to PASS | FAIL |
| T-extra-fields | Benign extra keys | WARN |
| T-extra-section | Manifest includes `unknown_section` | WARN |
| T-no-latest | Static/grep: loader must not reference `latest_successful` | guard |
| T-x2-fail-ok | SRFS receipt with `x2_srfs_gate_status: FAIL`, else valid | PASS (structural) |
| T-manifest-preferred | Load via `--receipt-manifest` only | PASS |

Fixtures dir: `artifacts/apps_rg/test_fixtures/srfs_aggregator/` (W5 creates).

---

## 9. W3 proceed decision

| Criterion | Result |
|-----------|--------|
| Receipt shapes documented | Yes (W1) |
| Canonical row + audit schema locked | Yes (§1–3) |
| PASS guard unambiguous | Yes (§5) |
| Blocker shapes | None — optional-field variance handled via `extensions` |
| Lane code changes required for W3 | **No** |

**`can_start_w3`: `true`**

**W3 first tasks:** `apps_rg/audit/srfs_receipt_aggregator.py` — `load_section_receipts_from_manifest`, `normalize_section_receipt`, `validate_section_inventory`, `build_srfs_audit_report` (deterministic only; no judge).
