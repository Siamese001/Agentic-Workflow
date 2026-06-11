---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\request-intake-w7-deferred-4c8e1f.md'
original_relative_path: 'request-intake-w7-deferred-4c8e1f.md'
source_sha256: d2d525e5fc4f4fac6ac7e6c77eef578716abc876b0b4be4408765f8b1b2bdbe2
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-24'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Request Intake W7 — Deferred Scope Execution

**Plan ID**: `request-intake-w7-deferred-4c8e1f`
**Parent plan**: `.windsurf/plans/request-intake-envelope-gaps-3f9a12.md`
**Tier**: T2 (2–5 files per subwave, single layer focus)
**Status**: DRAFT

---

## 1. Scope

Three items deferred from W1–W6 of the parent plan:

| Phase | Scope | Layer | Status carried in |
|-------|-------|-------|-------------------|
| W7.1 | Refactor `apps_*` runners to route through U1–U4 ingress adapters | L_APP | Wave/Phase Convergence |
| W7.2 | Wire real OTEL sink for `IngressMetrics` | L6 | Wave/Phase Convergence |
| W7.3 | Cheap-model classifier augmentation for `InputSafetyScreen` | L5 | Wave/Phase Convergence |

---

## 2. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status |
|------|-----------|-------|:-----------:|:------:|
| W7 | W7.1 – W7.3 | Close residual P1/P2 from parent plan | ~18k | 🟡 |

---

## 3. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|:------:|
| W7.1 | Proof-of-pattern adapter wiring — apps_rg | `apps_rg/integrations/governed_rg_run.py` + new smoke test | 7+ app runners each bypass the ingress gate | 8k | todo |
| W7.2 | OTEL sink adapter for IngressMetrics | `agentic_core/L5_safety/enforcement/ingress_telemetry_otel.py` (NEW) + `tools/otel/*` wiring point + test | in-memory-only sink | 4k | todo |
| W7.3 | Regex+classifier hybrid safety screen | `agentic_core/L5_safety/enforcement/input_safety_screen.py` extension + pluggable `ClassifierScreen` protocol + tests | regex-only | 6k | todo |

---

## 4. Definitions of Done

**W7.1**:
- One `apps_*` runner (`apps_rg`) calls an ingress adapter before dispatching to L1.
- Smoke test proves a malformed envelope into that runner returns a rendered rejection without touching L1.
- `DEFERRED_SCOPE:` marker emitted for the remaining apps_* runners (apps_eval, apps_exec, apps_lic, apps_research, apps_rfp, apps_underwriting_ai).

**W7.2**:
- New `OtelMetricsSink` implementing `IngressMetricsSink` protocol forwards to OTEL counters / histograms.
- `set_default_sink()` used at process-start wiring point.
- Test covers counter increment and histogram observation against a stub OTEL meter.

**W7.3**:
- `InputSafetyScreen` protocol unchanged.
- New `HybridInputSafetyScreen` wraps regex screen + optional classifier callback. Tests cover: classifier agrees, classifier flags new category, classifier returns None (falls back to regex).

---

## 5. Assumptions

- **DERIVED**: `apps_rg` is the highest-fan-in runner and thus highest-leverage single-runner proof point.
- **UNRESOLVED**: Whether the existing `tools/otel/otel_mcp_server.py` OTEL meter should be reused or a fresh meter registered for ingress.
