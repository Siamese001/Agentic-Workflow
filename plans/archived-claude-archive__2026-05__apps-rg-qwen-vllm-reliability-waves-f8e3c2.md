---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\apps-rg-qwen-vllm-reliability-waves-f8e3c2.md'
original_relative_path: '_archive\\2026-05\\apps-rg-qwen-vllm-reliability-waves-f8e3c2.md'
source_sha256: 92d38dd90e8e35f1b1eee0c7a696dac77b1fad11f59dede1855399417f472447
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_rg Qwen vLLM reliability — wave plan

**Slug**: `apps-rg-qwen-vllm-reliability-waves-f8e3c2`  
**Tier**: T2/T3 (apps_rg runtime + docs; optional core probe reuse)  
**Created**: 2026-05-18  
**Completed**: 2026-05-18  
**Status**: Completed  

## North star

For a fixed workstation and `VLLM_BASE_URL`, `python -m apps_rg` live Qwen paths behave as **probe → optional recover → chat**, with explicit artifacts when transport fails. Docker container restart remains **opt-in** and **probe-first** (`APPS_RG_QWEN_VLLM_DOCKER_RESTART`, `apps_rg/runtime/qwen_vllm_docker_restart.py`).

## Related SSOT

- `docs/architecture/qwen-vllm-topology.md` — topology, optional pre-run restart env vars  
- `agentic_core/L2_execution/healers/vllm_health_probe.py` — `/v1/models` probe  
- `agentic_core/L2_execution/healers/qwen_strict_diagnostic.py` — strict diagnostic taxonomy  
- `apps_rg/runtime/providers/competencies_live_provider_gate.py` — TCP preflight (competencies)

## Wave Structure

| Wave | Scope | Status |
|------|-------|--------|
| W0 | Semantics + operator checklist (failure taxonomy, env vars) | ✅ DONE |
| W1 | Instrumentation (resolved base URL, probe snapshot, HTTP errors in artifacts) | ✅ DONE |
| W2 | Unify preflight (HTTP `/v1/models` helper; align competencies with other lanes) | ✅ DONE |
| W3 | Bounded retries (transient transport only; artifact attempt trace) | ✅ DONE |
| W4 | Post-restart readiness (`Qwen` in model id; tests) | ✅ DONE |
| W5 | Infra guidance (compose healthcheck snippet; image pin policy) | ✅ DONE |

---

## W0 — Lock semantics

| Id | Deliverable | Exit criteria |
|----|-------------|---------------|
| W0.P1 | Failure taxonomy: TCP vs `/v1/models` vs chat timeout vs 5xx | Subsection in `docs/architecture/qwen-vllm-topology.md` |
| W0.P2 | Operator checklist: `VLLM_BASE_URL`, `APPS_RG_QWEN_TIMEOUT_SECONDS`, container name | Same doc |

---

## W1 — Instrument what breaks

| Id | Deliverable | Exit criteria |
|----|-------------|---------------|
| W1.P1 | On failed Qwen call, persist probe/URL class of error (redacted) in artifact | Sidecar JSON under lane or run root |
| W1.P2 | Greppable one-line run banner: effective base URL + docker-restart outcome | stdout/stderr contract documented |

**Likely files:** `apps_rg/runtime/providers/qwen_vllm_provider.py`, small `apps_rg/runtime/qwen_transport_diag.py`, lane dispatches.

---

## W2 — Unify preflight

| Id | Deliverable | Exit criteria |
|----|-------------|---------------|
| W2.P1 | Shared HTTP probe path before first live Qwen POST (reuse `probe()` or thin wrapper) | All live lanes share one gate |
| W2.P2 | Competencies: augment or replace raw TCP-only preflight with HTTP probe within same timeout budget | Same failure categories as other lanes |
| W2.P3 | Unit tests for probe outcomes | `tests/unit/apps_rg/` |

**Likely files:** `competencies_live_provider_gate.py`, `competencies_dispatch.py`, other `*_dispatch.py` touching Qwen.

---

## W3 — Bounded retries

| Id | Deliverable | Exit criteria |
|----|-------------|---------------|
| W3.P1 | Retry policy: connection reset, timeouts, narrow 5xx only; N≤2; bounded backoff | Documented in module docstring |
| W3.P2 | Artifacts: `attempt_count`, `retry_reasons` | Proof-friendly for X2 |
| W3.P3 | Contract tests: no accidental stub / proof downgrade | `tests/unit/apps_rg/` or `_apps_contract` |

**Likely files:** `apps_rg/runtime/providers/qwen_vllm_provider.py`.

---

## W4 — Post-restart readiness

| Id | Deliverable | Exit criteria |
|----|-------------|---------------|
| W4.P1 | After `docker restart`, ready only if healthy **and** model id contains configurable `Qwen` substring | `qwen_vllm_docker_restart.py` |
| W4.P2 | Tests: “HTTP up but wrong model” fails closed with clear audit | `tests/unit/apps_rg/test_qwen_vllm_docker_restart.py` |

---

## W5 — Infra guidance

| Id | Deliverable | Exit criteria |
|----|-------------|---------------|
| W5.P1 | Example Docker healthcheck against `/v1/models` | `docs/architecture/qwen-vllm-topology.md` |
| W5.P2 | vLLM image tag pinning policy | Same doc |

---

## Dependency order

W0 → W1 → W2 → W3; W4 after W1 (can parallel with W2); W5 parallel to W2–W4.

## Notes

- Do not weaken X2/provider proof gates; retries and preflight must remain observable.  
- No unconditional `docker restart` as default product behavior — operator env only.

## Closeout (2026-05-18)

- **Topology / operator SSOT**: `docs/architecture/qwen-vllm-topology.md` (includes W5 infra guidance and proof boundary).
- **Manifests**: `docs/reports/apps_rg/qwen_vllm_reliability_w0_w2_test_manifest.json`, `qwen_vllm_reliability_w3_test_manifest.json`, `qwen_vllm_reliability_w4_test_manifest.json`, `qwen_vllm_reliability_w5_test_manifest.json`, `qwen_vllm_reliability_w0_w5_closeout_manifest.json`.
- **Targeted proof slice** (last recorded): 33 passed — W0–W4 test modules in closeout manifest command.
