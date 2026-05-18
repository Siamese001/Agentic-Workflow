# apps_rg: SRFS receipt aggregation / audit consumer — wave plan (W1–W8)

> **Canonical SSOT:** `.cursor/plans/apps-rg-srfs-aggregator-e7b2a1.md` (Notion Plans DB row points here).  
> **Upstream closeout:** `docs/reports/apps_rg/srfs_per_section_w1_w7_closeout_manifest.json`  
> **Status:** CLOSED / STRUCTURAL PASS — disk (`.cursor/plans/apps-rg-srfs-aggregator-e7b2a1.md`) + Notion `Completed`. See `srfs_full_track_closeout.md` and `srfs_full_track_closeout_manifest.json`.  
> **Hardening:** 2026-05-18 — receipt precedence, PASS guard, W6 boundary, W7 naming, output language.

---

## 1. Objective

Build an **apps_rg product audit consumer** that:

1. Loads `section_metric_receipt.json` via **`--receipt-manifest`** (preferred: `section_id` → path) or **`--receipt-root`** (convenience recursive discovery only). **Never** auto-reads `latest_successful_*`.
2. Normalizes receipts and validates seven generated lanes.
3. Emits `apps_rg_srfs_audit_report.json` (+ `.md`) with deterministic PASS/WARN/FAIL at **`proof_level: SECTION_SRFS_STRUCTURAL_AUDIT_ONLY`**.
4. Optionally runs **apps_rg-local** advisory LLM review of the audit report (default off; NOT_RUN if not cleanly reusable).

---

## 2. Proof boundary

| Proves | Does not prove |
|--------|----------------|
| Cross-section SRFS structural receipt aggregation | Runtime certification |
| Deterministic PASS/WARN/FAIL on receipt inventory + PASS guard | Live Qwen quality |
| Optional advisory commentary on audit-report clarity | Real-judge X3 ALLOW / product release |
| `SECTION_SRFS_STRUCTURAL_AUDIT_ONLY` | Full résumé R4 SRFS |

### Receipt input precedence

1. **`--receipt-manifest`** — explicit `section_id` → receipt path (preferred).
2. **`--receipt-root`** — recursive discovery under caller directory (convenience).
3. **Forbidden** — inferring `latest_successful_real_run.json` or rollup chosen-run unless that exact path is in (1) or (2).

`--manifest` (closeout ref) does **not** resolve receipt paths.

### PASS guard (aggregate must FAIL, never PASS, if any section has)

- missing receipt
- pending receipt (`status: "pending"`)
- malformed receipt
- UNKNOWN SRFS/X2 status when SRFS active
- empty `prompt_hash` while SRFS active
- `full_resume_srfs_supported: true`

### Output language

- Always `proof_level: SECTION_SRFS_STRUCTURAL_AUDIT_ONLY`.
- Do **not** use *release proof*, *product ALLOW*, *certified*, *runtime certified*, or affirmative *full resume SRFS* outside `explicit_non_claims`.

---

## 3. Wave sequence

| Wave | Focus |
|------|--------|
| **W1** | Receipt inventory + canonical receipt schema |
| **W2** | Audit report schema + PASS/WARN/FAIL + PASS guard rules |
| **W3** | `apps_rg/audit/srfs_receipt_aggregator.py` (manifest-first loader) |
| **W4** | CLI: `--receipt-manifest` preferred, `--receipt-root` convenience |
| **W5** | Contract tests incl. pending, PASS-guard regressions, no latest_successful |
| **W6** | Optional **apps_rg-local** advisory judge; NOT_RUN if shared infra not reusable |
| **W7** | **Fixture-based** deterministic aggregator artifact (not product E2E) |
| **W8** | Closeout manifest |

### W6 (hardened)

- Optional, default off. **No** generic judge infra changes. **No** `agentic_core`.
- Reuse existing apps_rg helper only if **zero edits** to shared judge modules; else `advisory_judge_review.status = NOT_RUN` and continue.
- Judge cannot change deterministic `status`.

### W7 (renamed)

**Fixture-based deterministic aggregator artifact** — synthetic/commit fixtures + `--receipt-manifest` only. Not full résumé R4, not live orchestration E2E.

---

## 4. Report schema (minimum)

`proof_level` must be `"SECTION_SRFS_STRUCTURAL_AUDIT_ONLY"`. Include `receipt_manifest_ref` and/or `receipt_root` (null when unused). See canonical plan §4 for full JSON shape.

---

## 5. Recommended commands

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/_apps_contract/test_apps_rg_srfs_aggregator.py -q --tb=short -p pytest_timeout
```

```bash
python -m apps_rg.audit.srfs_receipt_aggregator \
  --receipt-manifest artifacts/apps_rg/test_fixtures/srfs_aggregator/seven_section_receipt_manifest.json \
  --manifest docs/reports/apps_rg/srfs_per_section_w1_w7_closeout_manifest.json \
  --out artifacts/apps_rg/audit/srfs_section_aggregation/<run_id>
```

---

## 6. Acceptance criteria

- PASS guard enforced; manifest-first loading; no `latest_successful` inference.
- `proof_level` fixed; forbidden phrasing only in `explicit_non_claims`.
- W6 optional, apps_rg-local, NOT_RUN when not reusable.
- W7 is fixture-based only.

---

## Explicit NOT_PROVEN

Full résumé R4 SRFS · `modular_resume_generation.py` · live Qwen · real-judge X3 ALLOW · runtime certification · product release via this aggregator

---

*Full detail: `.cursor/plans/apps-rg-srfs-aggregator-e7b2a1.md`*
