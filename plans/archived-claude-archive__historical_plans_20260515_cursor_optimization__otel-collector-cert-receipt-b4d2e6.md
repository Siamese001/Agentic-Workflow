---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\otel-collector-cert-receipt-b4d2e6.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\otel-collector-cert-receipt-b4d2e6.md'
source_sha256: 50b4a4d531fb121e8f756a4d3d01ce4880982a3b07518557615565effa429628
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# OTEL Collector Certification Receipt — Close RTC-REQ-020/022 Collector Sub-Claim

> **Plan slug**: `otel-collector-cert-receipt-b4d2e6`
> **Plan path**: `.windsurf/plans/otel-collector-cert-receipt-b4d2e6.md`
> **Parent plan**: `agentic-core-signoff-hardening-b8e2c4` (AUTHORITY.md §4 deferral)
> **Status**: Not Started

PLAN_CREATED: slug=otel-collector-cert-receipt-b4d2e6 path=.windsurf/plans/otel-collector-cert-receipt-b4d2e6.md

## 1. Background

`rtc_req_otel_replay_report.json` marks RTC-REQ-020 and RTC-REQ-022 as `BLOCKED` because two
artifacts are missing:

- `artifacts/certification/otel_collector_receipt.json` — requires a live external OTEL collector
  (`docker-compose.otel.yml`) to receive spans from the runtime under test.
- `artifacts/certification/otel_metric_delta_report.json` — requires the R1B path to be
  instrumented with counters + attribute-tagged metric deltas exported via the collector.

These are a **separate, additive evidence sub-claim** from the apps_rg OTEL trace evidence that
already backs RTC-REQ-020/022's SIGNED_OFF status. Closing this sub-claim upgrades the
collector-receipt pathway from BLOCKED → PASS, providing an independent, external-collector-backed
proof chain alongside the existing apps_rg evidence.

Required attributes per RTC-REQ-022: `route_id`, `cache_tier`, `namespace`, `policy_hash`,
`result/reason`.

## 2. Scope

### 2.1 In scope

- Bring up `docker-compose.otel.yml` (local dev OTEL collector with OTLP gRPC receiver).
- Run the R1B route probe with OTEL export enabled; confirm spans are received by the collector.
- Export `otel_collector_receipt.json` as the collector's proof of span receipt.
- Instrument the R1B path with counters for the required attributes; export
  `otel_metric_delta_report.json`.
- Regenerate `rtc_req_otel_replay_report.json` to show both RTC-REQ-020 and RTC-REQ-022 as `PASS`.
- Recompile bundle; re-sign; verify both verifiers exit 0.

### 2.2 Out of scope

- Changes to apps_rg overlay evidence rows (already SIGNED_OFF via Pathway 2).
- L7 closure (separate plan `l7-route-family-closure-d3e8f1`).
- External Sigstore attestation (`FINAL_SIGNED_CERTIFICATION`).

### 2.3 Assumptions

- Docker is available on the dev machine where this plan executes.
- `docker-compose.otel.yml` is runnable without modifications (or requires only minor env patching).
- The R1B probe can be invoked to export spans to the local collector endpoint.

## 3. Files In Scope

### Read
- `docker-compose.otel.yml`
- `artifacts/certification/rtc_req_otel_replay_report.json`
- `scripts/compile_requirement_signoff.py`
- `certification/requirements_source.json` (RTC-REQ-020, RTC-REQ-022 controls + allowed_verifier_commands)

### Write
- `artifacts/certification/otel_collector_receipt.json` (new)
- `artifacts/certification/otel_metric_delta_report.json` (new)
- `artifacts/certification/rtc_req_otel_replay_report.json` (regenerated to PASS)
- `certification/evidence_assertions.jsonl` (new assertions for 020/022 collector sub-claim)
- `certification/agentic_core/compiler_output/*` (rebuilt signed bundle mirror)

## 4. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|------|-----------|-------|-------------|--------|------------------|
| W1 | P1.1 | Read `docker-compose.otel.yml`; read RTC-REQ-020/022 verifier contract; map required attributes | ~3k | Planned | Known: collector endpoint, required span attributes, required metric attributes |
| W2 | P2.1, P2.2 | Launch collector; run R1B probe with OTEL export; verify receipt | ~5k | Planned | Collector receives spans; `otel_collector_receipt.json` on disk with OTLP receipt proof |
| W3 | P3.1 | Instrument R1B counters + export `otel_metric_delta_report.json` | ~5k | Planned | `otel_metric_delta_report.json` on disk; all required attributes present |
| W4 | P4.1, P4.2 | Regenerate `rtc_req_otel_replay_report.json`; recompile + re-sign + verify | ~4k | Planned | Both RTC-REQ-020 and 022 → PASS; bundle verifier PASS; signature VERIFIED |
| W5 | P5.1 | Update AUTHORITY.md + closeout report | ~2k | Planned | AUTHORITY.md §3 Pathway 1 status updated to PASS; closeout report written |

## 5. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P1.1 | Contract mapping | `docker-compose.otel.yml`, `requirements_source.json` | Docker availability must be confirmed first | ~3k | Planned |
| P2.1 | Launch collector | `docker-compose.otel.yml` | Port conflicts; collector config; OTLP gRPC vs HTTP | ~2k | Planned |
| P2.2 | R1B probe + receipt | R1B route probe script | Probe invocation command; OTEL_EXPORTER_OTLP_ENDPOINT env | ~3k | Planned |
| P3.1 | Metric delta report | R1B instrumentation | Counter names + attribute tagging may require code changes to R1B | ~5k | Planned |
| P4.1 | Regenerate replay report | `scripts/` replay verifier | Freshness window on new assertions | ~2k | Planned |
| P4.2 | Recompile + re-sign | compiler + signer | git_dirty; use `--allow-dirty-git` or commit first | ~2k | Planned |
| P5.1 | AUTHORITY.md + closeout | `certification/agentic_core/AUTHORITY.md` | — | ~2k | Planned |

## 6. Success Criteria

- [ ] `rtc_req_otel_replay_report.json` shows `overall_result: PASS`, both RTC-REQ-020 and RTC-REQ-022 → `PASS`.
- [ ] `otel_collector_receipt.json` and `otel_metric_delta_report.json` on disk.
- [ ] Bundle recompiled; 102 rows SIGNED_OFF; verifier PASS; signature VERIFIED.
- [ ] AUTHORITY.md §3 Pathway 1 updated to PASS.
- [ ] Closeout report at `docs/reports/runtime_cert/otel_collector_receipt/<YYYY-Www>.md`.

## 7. References

- Parent plan `agentic-core-signoff-hardening-b8e2c4` — AUTHORITY.md §3 Pathway 1 / §4 deferral
- `docker-compose.otel.yml` — local collector stack
- `artifacts/certification/rtc_req_otel_replay_report.json` — current BLOCKED status
- Constitutional §32 (Fort Knox certification integrity)
