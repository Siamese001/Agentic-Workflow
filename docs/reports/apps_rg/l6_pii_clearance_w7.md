# L6 PII Clearance — W7 Report

**Report date:** 2026-05-18  
**Status:** PARTIAL (scan: **7/7** eligible_for_clearance on generated text; apply: **0** cleared via placeholder; reviewer export empty)  
**proof_eligible:** false  

---

## Workflow

1. **Scan** — [review_pii_clearance.py](../../ops_scripts/apps_rg/l6_benchmarks/review_pii_clearance.py) → [pii_review_report_w7.json](../../artifacts/apps_rg/benchmarks/collected/_manifests/pii_review_report_w7.json)
2. **Decisions placeholder** — [pii_clearance_decisions.placeholder.json](../../artifacts/apps_rg/benchmarks/collected/_manifests/pii_clearance_decisions.placeholder.json) (all `pending_review`; no fabricated clearance)
3. **Apply** — explicit decisions only → [pii_clearance_application_w7.json](../../artifacts/apps_rg/benchmarks/collected/_manifests/pii_clearance_application_w7.json)
4. **Validate** — [validation_report_w7.json](../../artifacts/apps_rg/benchmarks/collected/_manifests/validation_report_w7.json)
5. **Reviewer export** — [reviewer_packet_w7.json](../../artifacts/apps_rg/benchmarks/reviewer_exports/reviewer_packet_w7.json) (`cleared-only`)

## PII scan behavior

| Check | Scope |
|-------|--------|
| email, phone, SSN-like, URL, address-like | `generated_section_text` |
| path identifiers (`amit_ayer`, resume paths) | `input_refs` (flagged, does not block clearance eligibility) |

## Clearance application

- Apply mode requires `--decisions` with per-sample `decision`: `pending_review` \| `cleared` \| `rejected`
- `cleared` only when `decision=cleared` **and** no blocking flags in generated text
- Placeholder apply: **7 skipped** (`decision=pending_review`) — **no samples auto-cleared**

## Reviewer export

- `reviewer_export_count=0` — all samples remain `pii_status=pending_review`
- To export packets: set `decision=cleared` in decisions JSON (with reviewer/rationale) and re-run `--apply`

## Preserved metadata

`collection_metadata` unchanged except future `pii_clearance_*` fields when cleared. X2/X3 fields and `proof_eligible=false` preserved.

## Non-claims

- No human labels collected
- No calibration complete
- No runtime proofs modified
- No auto-clearance performed

## Receipt

[l6_pii_clearance_w7_receipt.md](l6_pii_clearance_w7_receipt.md) · [manifest](l6_pii_clearance_w7_manifest.json)
