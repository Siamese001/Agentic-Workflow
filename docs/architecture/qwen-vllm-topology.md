# Qwen/vLLM Runtime Topology

> Canonical reference for the supported Qwen inference path in this repo.
> Last updated 2026-05-06 (Docker canonical-runtime declaration).
> Related: `docs/architecture/hardening_addendum.md`, `agentic_core/L2_execution/types/local_first_disposition.py`

---

## 0. Canonical Runtime — Docker Desktop (added 2026-05-06)

For repo `Agentic-Workflow-FRESH`, the Qwen vLLM stack runs under
**Docker Desktop**, NOT under WSL2 systemd-user.

| Field | Value |
|---|---|
| Container | `local-qwen-vllm` |
| Image | `vllm/vllm-openai:latest` |
| Model | `Qwen/Qwen2.5-32B-Instruct-AWQ` (32B-AWQ) |
| Endpoint | `http://localhost:8000/v1` (matches `VLLM_BASE_URL` in `agentic_core/L0_routing/config/model_registry.py`) |
| Port mapping | `0.0.0.0:8000->8000/tcp` |
| Container args | `--model Qwen/Qwen2.5-32B-Instruct-AWQ --served-model-name Qwen/Qwen2.5-32B-Instruct-AWQ --quantization awq_marlin --dtype auto --max-model-len 8192 --gpu-memory-utilization 0.88 --host 0.0.0.0 --port 8000` |

### Lifecycle

- Start: `docker start local-qwen-vllm`
- Stop: `docker stop local-qwen-vllm`
- Health: `curl http://localhost:8000/v1/models` should return JSON with `Qwen/Qwen2.5-32B-Instruct-AWQ` in `data[0].id`

### Strict-mode preflight

`agentic_core/L2_execution/healers/qwen_strict_diagnostic.py` provides
categorized failure modes — `docker_desktop_down`, `docker_cli_missing`,
`vllm_container_down`, `qwen_model_not_loaded`, `ok`. Engines that synthesize
via Qwen (e.g. `apps_research.engines.company_brief_engine.CompanyBriefEngine`)
honour `APPS_RESEARCH_REQUIRE_QWEN=1` and raise `QwenUnavailableError` with an
`action_hint` instead of silently falling through to stub.

### Legacy WSL2 path (DEPRECATED, archived 2026-05-06)

A prior topology ran vLLM natively in WSL2 Ubuntu under a systemd-user
service. That path is **deprecated** for `Agentic-Workflow-FRESH`. The launcher
scripts (`start_vllm_server_32b.sh`, `check_vllm.sh`, `vllm.service`) were
moved to `archives/wsl2_vllm_legacy_2026-05-06/` with a README. The WSL2-side
`~/.vllm_env` venv (~9.7 GB) and `/home/amita/.config/systemd/user/vllm.service`
were removed. The model weights at `~/models/Qwen2.5-32B-Instruct-AWQ` (~20 GB)
were preserved as a cheap-to-keep fallback artifact.

Do not start the WSL2 unit: port 8000 is owned by Docker; the unit will
restart-loop with port-bind failures.

---

## 1. App Classification

### Local-First (5 apps)

These apps route every Qwen call through the full local-first discipline:
routing predicates → adapter gate → gateway → hardened client → local vLLM.

| App | Orchestrator | Method |
|---|---|---|
| `apps_rg` | `RgResumeOrchestrator` | `generate_resume_with_qwen` |
| `apps_exec` | `ExecOrchestrator` | `generate_brief_with_qwen` |
| `apps_research` | `ResearchOrchestrator` | `synthesize_with_qwen` |
| `apps_rfp` | `RfpOrchestrator` | `generate_proposal_with_qwen` |
| `apps_lic` | `GovernanceShieldAgent` | `analyze_governance_with_qwen` |

### Controlled / Opt-In (1 app)

| App | Orchestrator | Method | Why opt-in |
|---|---|---|---|
| `apps_eval` | `EvalOrchestrator` | `evaluate_with_qwen` | Off main `run()` pipeline; evaluation reliability requires consistent provider; telemetry must be available before inference runs |

`apps_eval` does **not** use routing predicates, adapter gating, or `LocalFirstDisposition`.
Its `evaluate_with_qwen` is a standalone enrichment method — the deterministic eval pipeline
completes with full fidelity whether or not Qwen is called.

---

## 2. Supported Live Path (local-first apps)

```
app orchestrator
  │
  ├─ routing_ctx = {
  │      "requires_policy_read": bool,
  │      "iteration_count": int,
  │      "max_iterations": int,
  │      "invalid_ast": bool,
  │      "routing_version": "1",
  │  }
  │
  ├─ evaluate_routing(routing_ctx)  →  Provider.LOCAL_VLLM | Provider.OPUS
  │
  └─ [Provider.LOCAL_VLLM]
       │
       ├─ VLLMGatewayAdapter.evaluate(task_class, content_preview, ...)
       │       route_to_gemini=True  →  LocalFirstDisposition.for_escalate(...)
       │       route_to_gemini=False →  proceed
       │
       ├─ AppsQwenGateway.infer(AppsQwenRequest)
       │       └─ HardenedVLLMClient  (circuit breaker, retry)
       │               └─ OptimizedVLLMClient  (connection pool, batching)
       │                       └─ local vLLM server  (Qwen/Qwen2.5-32B-Instruct-AWQ)
       │
       └─ LocalFirstDisposition outcome
              for_allow(...)      — inference succeeded
              for_fail_exec(...)  — inference raised an exception
              for_fail_init(...)  — gateway init failed
              for_skip(...)       — gateway None or provider != LOCAL_VLLM
```

### Observability

Every local-first app emits:
- `apps_qwen_telemetry.record_request_start/success/error` per call
- `LocalFirstDisposition` packet for every outcome (stored as `_dsp`, logged on completion)
- `VLLMGatewayAdapter.record_local_success / record_local_failure` for circuit-breaker feedback

### Supported live imports (apps_* orchestrators)

```python
# Module-level (top of orchestrator file)
from agentic_core.L3_orchestration.inference.qwen_vllm import (
    AppsQwenGateway,
    AppsQwenRequest,
    apps_qwen_telemetry,
)

# Deferred in-method (inside run() / inference method) — noqa: PLC0415
from agentic_core.L2_execution.types.local_first_disposition import LocalFirstDisposition
from agentic_core.L2_execution.types.vllm_gateway_adapter_types import VLLMGatewayAdapter
from agentic_core.L4_state.config.vllm_routing_predicates import Provider, evaluate as evaluate_routing
```

---

## 3. Supported Public API (`qwen_vllm` package)

### Gateway (primary)
| Symbol | Role |
|---|---|
| `AppsQwenGateway` | App-facing gateway — use this in all orchestrators |
| `AppsQwenRequest` | Request type for `AppsQwenGateway.infer()` |
| `AppsQwenResponse` | Response type |
| `get_apps_qwen_gateway` / `close_apps_qwen_gateway` | Singleton lifecycle helpers |
| `apps_qwen_telemetry` | Module-level telemetry singleton |

### Engines (infrastructure — not called directly by orchestrators)
| Symbol | Role |
|---|---|
| `HardenedVLLMClient` | Circuit breaker + retry wrapper |
| `OptimizedVLLMClient` | Connection pool, batching, base HTTP |
| `CircuitBreaker` / `CircuitBreakerConfig` / `CircuitState` | Circuit breaker primitives |
| `VLLMRequest` / `VLLMResponse` | Low-level request/response types |
| `get_vllm_client` / `close_vllm_client` | Client lifecycle |

### GPU tools
`GPUMemoryMonitor`, `GPUMemoryInfo`, `GPURecommendation`, `get_gpu_monitor`, `stop_gpu_monitor`

### Config (exported for external configuration use)
`AppsQwenConfig`, `AppsQwenModelConfig`, `AppsQwenPromptConfig`, `AppsQwenTelemetry`,
`AppsQwenMetric`, `AppsQwenSessionMetrics`

---

## 4. Intentionally Removed (obsolete)

The following were removed in Apr 2026 and must not be re-introduced:

| Removed | Reason |
|---|---|
| `qwen_inference_worker.py` (`QwenInferenceWorker`, `AppsQwenInferenceWorker`) | Mock-only (`_mock_inference`, `time.sleep`); never connected to real vLLM; superseded by `AppsQwenGateway` |
| `apps_shared/utils/vllm_shared_utils.py` (`VLLMSharedManager`, `VLLMConfigPresets`, `VLLMPromptTemplates`) | Zero callers; `_qwen_enabled = False` silent-disable anti-pattern contradicts hardened orchestrator discipline |
| Worker symbols in `engines/__init__.__all__` | Removed alongside worker file |
| `_qwen_inference_worker` attribute in orchestrators | Worker construction in `__post_init__`; never called in hot path |

**There is no worker path. There is no `apps_shared` helper path. There is no hidden fallback.**
All inference goes through `AppsQwenGateway.infer()` exclusively.

---

## 5. Adding a New App to the Local-First Pattern

1. Import the four symbols listed in §2.
2. In `__post_init__`: construct `AppsQwenGateway`, start telemetry session, capture init error in `self._qwen_init_error`.
3. In the inference method: build `routing_ctx`, call `evaluate_routing()`, gate with `VLLMGatewayAdapter`, call `gateway.infer()`, emit `LocalFirstDisposition`.
4. Add tests mirroring `tests/unit/apps_lic/reasoning/test_governance_shield_agent_qwen.py`.
5. Do **not** construct `AppsQwenInferenceWorker` — it no longer exists.
