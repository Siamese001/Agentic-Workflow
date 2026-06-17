# Qwen/vLLM Runtime Topology

> Canonical reference for the supported Qwen inference path in this repo.
> Last updated 2026-05-26 (24k context default for 32B-AWQ executive-summary headroom).
> Related: `docs/architecture/hardening_addendum.md`, `agentic_core/L2_execution/types/local_first_disposition.py`

---

## 0. Canonical Runtime — Docker Desktop (added 2026-05-06)

For repo `Agentic-Workflow-FRESH`, the Qwen vLLM stack runs under
**Docker Desktop**, NOT under WSL2 systemd-user.

| Field | Value |
|---|---|
| Container | `local-qwen-vllm` |
| Compose SSOT | `docker-compose.qwen.yml` |
| legacy editor boot runbook | `docs/cursor/local_qwen_docker_boot.md` |
| Image | `vllm/vllm-openai:latest` in compose (workstation default); see **W5 — Image tag and digest pinning** to pin tag+digest for proof runs |
| Model | `Qwen/Qwen2.5-32B-Instruct-AWQ` (32B-AWQ) served from `/models/qwen` (WSL bind mount) |
| Endpoint | `http://localhost:8000/v1` (matches `VLLM_BASE_URL` in `agentic_core/L0_routing/config/model_registry.py`) |
| Port mapping | `0.0.0.0:8000->8000/tcp` |
| Weights host path | `${QWEN_MODEL_HOST_PATH:-/home/amita/models/Qwen2.5-32B-Instruct-AWQ}` (WSL ext4) |
| Container args | `--model /models/qwen --served-model-name Qwen/Qwen2.5-32B-Instruct-AWQ --quantization awq_marlin --attention-backend TRITON_ATTN --max-model-len 24576 --gpu-memory-utilization 0.88 --max-num-seqs 8` |
| `shm_size` | `16gb` (default Docker 64 MiB breaks vLLM workers) |
| Restart policy | `unless-stopped` (set 2026-05-06 W3 of plan apps-rg-vllm-deferred-followup-f7d3a9) |

**Context window SSOT:** `24576` tokens. Set matching `VLLM_MAX_MODEL_LEN=24576` for apps_rg / agentic_core token budgets. Do not set env to 32k while the container stays at 16k (or vice versa).

### Boot / recreate (operator)

**SSOT:** [`docs/cursor/local_qwen_docker_boot.md`](../cursor/local_qwen_docker_boot.md)

Run **Compose from WSL** so the model bind mount resolves (PowerShell-only `docker compose` often leaves `/models/qwen` empty):

```powershell
wsl -e bash -lc 'cd /mnt/c/Git/Agentic-Workflow-FRESH && docker compose -f docker-compose.qwen.yml up -d qwen-vllm'
```

Recreate after changing image, `max-model-len`, or mount:

```powershell
wsl -e bash -lc 'cd /mnt/c/Git/Agentic-Workflow-FRESH && docker compose -f docker-compose.qwen.yml up -d --force-recreate qwen-vllm'
```

Or: `wsl bash /mnt/c/Git/Agentic-Workflow-FRESH/ops_scripts/apps_rg/boot_local_qwen_vllm.sh`

Verify:

```powershell
docker exec local-qwen-vllm test -f /models/qwen/config.json
curl -fsS http://localhost:8000/v1/models
```

If the container OOMs on load, compose already uses `--gpu-memory-utilization 0.88`; or step down to `20480` (update `VLLM_MAX_MODEL_LEN` to match).

### Lifecycle

- Start: `docker start local-qwen-vllm`
- Stop: `docker stop local-qwen-vllm`
- Health: `curl http://localhost:8000/v1/models` should return JSON with `Qwen/Qwen2.5-32B-Instruct-AWQ` in `data[0].id`
- Boot helper (WSL): `ops_scripts/apps_rg/boot_local_qwen_vllm.sh` — compose up + mount/API checks.
- Interactive helper (Windows): `ops_scripts/apps_rg/Fix-AppsRgWslRuntime.ps1` — boot vLLM + WSL venv smoke test.

### apps_rg section CLI — opt-in auto-start (Wave D)

When `python -m apps_rg --section …` uses live `qwen_vllm`, preflight fails closed if Docker reports the container stopped. Set:

| Env | Role |
|-----|------|
| `APPS_RG_VLLM_AUTO_START=1` | Run `docker start local-qwen-vllm` once when inspect shows not running, then re-check before failing. |

Default is **off** (fail-fast preserves operator intent). Implementation: `apps_rg/runtime/section_cli_preflight.py`.

### Auto-restart on host reboot (added 2026-05-06)

Restart policy is `unless-stopped`. This means:

- After a Windows host reboot, when Docker Desktop comes back up, the
  container starts automatically — no manual `docker start local-qwen-vllm`
  needed.
- A user-initiated `docker stop local-qwen-vllm` is honored: a stopped
  container stays stopped across reboot until explicitly started again.
- A container crash (OOM, kernel kill, model-load failure) triggers
  Docker's restart loop with exponential backoff.

**Verify**: `docker inspect local-qwen-vllm --format '{{.HostConfig.RestartPolicy.Name}}'` → `unless-stopped`.

**Change policy** (e.g. to disable auto-restart while debugging):

    docker update --restart no local-qwen-vllm

**Restore default**:

    docker update --restart unless-stopped local-qwen-vllm

### apps_rg opt-in pre-run container restart (added 2026-05-18)

Unconditional `docker restart` before every run is **discouraged**: it hides
intermittent health issues, costs a full model reload, and races other clients
on the same endpoint. Prefer **probe-first** restart:

| Env | Role |
|-----|------|
| `APPS_RG_QWEN_VLLM_DOCKER_RESTART=1` | Master switch (default off). |
| `APPS_RG_QWEN_VLLM_DOCKER_RESTART_MODE=if_unhealthy` | Default — restart only when `GET /v1/models` probe fails. |
| `APPS_RG_QWEN_VLLM_DOCKER_RESTART_MODE=always` | Restart even when healthy (operator workaround only). |
| `APPS_RG_QWEN_VLLM_CONTAINER_NAME` | Override container name (default `local-qwen-vllm`). |

Implementation: `apps_rg/runtime/qwen_vllm_docker_restart.py`, invoked from
`python -m apps_rg` after `--dry-run` handling. Skipped for offline stub,
`APPS_RG_L2_FORCE_STUB`, `APPS_RG_L2_PROVIDER_MODE=stub_only`, and section lanes
with `--provider mock`.

### Post-restart readiness validation (W4, 2026-05-18)

When `APPS_RG_QWEN_VLLM_DOCKER_RESTART=1`, **ready** means: Docker restart succeeded (when invoked),
**and** an HTTP `GET /v1/models` parsed successfully with **at least one** non-empty model `id` containing
`APPS_RG_QWEN_EXPECTED_MODEL_SUBSTRING` (default **`Qwen`**; legacy alias `APPS_RG_QWEN_VLLM_MODEL_READY_SUBSTRING`).
TCP reachability or “HTTP 200 with empty `data`” is **not** ready. Wrong-model-only lists fail closed
(`readiness_status=model_mismatch`). After CLI startup, when `--artifact-dir` is set, a redacted
`qwen_vllm_docker_restart_readiness.json` is written there (no headers, secrets, or prompts).

### apps_rg live transport — failure taxonomy (2026-05-18)

For **live** `qwen_vllm` runs, failures are classified (see
`apps_rg/runtime/qwen_transport_diag.py` and `ProviderResult` paths) so
operators can distinguish **TCP** issues from **HTTP probe** vs **chat**
failures:

| Category | Typical cause |
| --- | --- |
| **TCP / connect failure** | Host down, port closed, DNS failure, TLS handshake (reported as URL/connection errors on the client). |
| **`/v1/models` HTTP probe failure** | Non-200, timeout, or unreadable models response on `GET …/v1/models` (preflight before first live chat POST). |
| **Wrong / missing model id** | HTTP `GET /v1/models` ok but no model id contains the expected substring (`APPS_RG_QWEN_EXPECTED_MODEL_SUBSTRING`, else legacy `APPS_RG_QWEN_VLLM_MODEL_READY_SUBSTRING`, default **Qwen**), or empty / invalid ids. |
| **Chat completion timeout** | `chat/completions` POST exceeded `APPS_RG_QWEN_TIMEOUT_SECONDS` (or payload `timeout_seconds`). |
| **Chat 5xx** | Upstream vLLM/OpenAI-compatible server error on POST. |
| **Chat non-retryable 4xx** | Client or server rejected the request (4xx) — not treated as a silent success. |
| **Malformed response** | Empty `choices`, invalid JSON, or JSON that cannot be parsed as chat completions. |

### apps_rg chat/completions — bounded transient retries (W3, 2026-05-18)

After HTTP `/v1/models` preflight succeeds, **`POST …/chat/completions`** may retry **transient transport**
failures only: timeouts, narrow **5xx** (`502`, `503`, `504`, plus `408` / `429`), connection reset/refused
and similar `URLError` / `OSError` patterns. **No retry** for `4xx`, wrong model id / `STUBBED`
classification, malformed body after HTTP success, or offline contract stub. **No** change to **base_url** or
**model** between attempts; bounded attempts and backoff via `APPS_RG_QWEN_TRANSPORT_*` env vars (see
`qwen_transport_diag.py`). On failure or on **REAL_LLM** success after retries, `qwen_transport_diagnostic.json`
can record `attempt_count`, `attempts[]`, `retry_reasons[]`, and policy metadata (`retried`, policy name/version).

On failure, apps_rg may persist a redacted sidecar
`qwen_transport_diagnostic.json` under the section run artifact directory (no
headers, secrets, or prompt text). Live runs print a greppable banner
`APPS_RG_QWEN_LIVE` with redacted `base_url`, docker-restart disposition, and
probe result.

### Operator checklist (apps_rg live Qwen)

| Variable | Purpose |
| --- | --- |
| `VLLM_BASE_URL` | OpenAI-compatible root (e.g. `http://localhost:8000/v1`). Drives probe URL and chat endpoint. |
| `APPS_RG_QWEN_TIMEOUT_SECONDS` | Chat POST timeout budget (default in `qwen_vllm_provider`). |
| `APPS_RG_QWEN_TRANSPORT_MAX_ATTEMPTS` | Total chat attempts (initial + retries); capped (default 3). |
| `APPS_RG_QWEN_TRANSPORT_RETRY_BACKOFF_BASE_S` | Base backoff seconds before retry after transient failure. |
| `APPS_RG_QWEN_TRANSPORT_RETRY_BACKOFF_CAP_S` | Max backoff cap per sleep. |
| `APPS_RG_COMPETENCIES_VLLM_PREFLIGHT_TIMEOUT_SECONDS` | Bounded timeout for competencies-only HTTP models preflight (capped, see `competencies_live_provider_gate`). |
| `APPS_RG_COMPETENCIES_VLLM_PREFLIGHT_DISABLE` | If set, competencies lane skips HTTP preflight in the slice (**not recommended** for unattended runs); banner shows `probe=not_run`. |
| `APPS_RG_QWEN_EXPECTED_MODEL_SUBSTRING` | Primary substring for model id readiness on `GET /v1/models` (default **Qwen**). |
| `APPS_RG_QWEN_VLLM_MODEL_READY_SUBSTRING` | Legacy alias when the above is unset. |
| `APPS_RG_QWEN_VLLM_DOCKER_RESTART` | **Opt-in** only — master switch for probe-first container restart (never unconditional). |
| `APPS_RG_QWEN_VLLM_DOCKER_RESTART_MODE` | `if_unhealthy` (default) vs `always` — see table under “apps_rg opt-in pre-run container restart”. |
| `APPS_RG_QWEN_VLLM_CONTAINER_NAME` | Override Docker container name (default `local-qwen-vllm`). |
| `APPS_RG_QWEN_OFFLINE_CONTRACT_STUB` | Deterministic stub for contract/offline runs — **must not** satisfy live proof; pair with tests using `APPS_RG_QWEN_DISABLE_OFFLINE_STUB` when exercising real transport. |

### W5 — Operator infra guidance (docs-only, 2026-05-18)

This subsection is **guidance only** for operators and reviewers. It does not change runtime code. It aligns with apps_rg transport/restart behavior documented above (W3 transient retries, W4 HTTP+model readiness, opt-in Docker restart).

#### Docker Compose `healthcheck` (HTTP `/v1/models`)

A process **listening on the port** (TCP open) is **not** sufficient readiness: vLLM can bind before the served model is load-ready, or `/v1/models` can error while the port accepts connections. Prefer an **HTTP** check against **`GET /v1/models`** with a bounded timeout.

`healthcheck` **cannot** read apps_rg env vars; embed the same **host**/**port** (or in-container URL) your compose service uses. Where possible, assert the **expected model id substring** in the JSON body (operator choice: `grep`, `jq`, or a tiny script) so “HTTP 200 + empty `data`” or “wrong model only” does not pass.

Illustrative `compose` fragment (adjust port, path, and substring to match your stack):

```yaml
services:
  qwen-vllm:
    # image: vllm/vllm-openai:<PINNED_TAG_OR_DIGEST>   # see "Image tag and digest pinning" below
    healthcheck:
      # In-container: hit the same port vLLM binds (example 8000). Use HTTP, not raw TCP.
      test:
        [
          "CMD-SHELL",
          "curl -fsS --max-time 8 http://127.0.0.1:8000/v1/models | grep -q Qwen",
        ]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 420s
```

Notes:

- **`start_period`**: model load can take minutes; set generously on first boot or after image upgrades.
- **`retries` / `timeout`**: short probes that flap on slow GPUs produce false “unhealthy”; tune for your hardware.
- **Substring**: keep in sync with `APPS_RG_QWEN_EXPECTED_MODEL_SUBSTRING` (default **Qwen**) where you validate id text.

#### Image tag and digest pinning

| Practice | Rationale |
| --- | --- |
| **Do not rely on `:latest` for proof or release-style runs** | The digest behind `latest` moves without warning; regressions become non-reproducible. |
| **Record tag and digest in operator notes** | E.g. from `docker inspect <container> --format '{{.Image}}'` or `docker image inspect --format '{{json .RepoDigests}}'`. Paste into run logs or an internal manifest. |
| **Isolate experimental image bumps** | Try new vLLM images on a throwaway container or compose project; avoid swapping the proof lane image mid-baseline. |
| **After any inference image / vLLM major version change** | Re-run the repo’s **W0–W4 targeted pytest slice** (see manifest `docs/reports/apps_rg/qwen_vllm_reliability_w5_test_manifest.json`) before treating transport/restart baselines as current. |

Floating `latest` remains acceptable for **local experimentation** only—not as a silent assumption for structured proof.

#### Operator runbook (pre-flight)

1. **`VLLM_BASE_URL`**: Must be the OpenAI-compatible root actually serving chat (e.g. `http://localhost:8000/v1`). Mismatch here breaks probe URL and chat URL construction.
2. **`APPS_RG_QWEN_TIMEOUT_SECONDS`**: Chat POST budget used by `qwen_vllm_provider`; too low causes false failures on slow hardware.
3. **`APPS_RG_QWEN_EXPECTED_MODEL_SUBSTRING`**: Must match the model id you intend to gate on for `/v1/models` readiness (default **Qwen**); legacy `APPS_RG_QWEN_VLLM_MODEL_READY_SUBSTRING` applies when the new variable is unset.
4. **`APPS_RG_QWEN_VLLM_DOCKER_RESTART`**: **Disabled by default** (unset or falsy). Do **not** treat enabling restart as normal operations—it reloads the model and can hide drift.
5. **When opt-in restart is acceptable**: Workstation recovery after Docker Desktop restart, known `if_unhealthy` probe failures, or an explicit operator workaround with `APPS_RG_QWEN_VLLM_DOCKER_RESTART_MODE=always`—never as a blanket CI default.
6. **Readiness artifact**: When you run `python -m apps_rg … --artifact-dir <path>`, a redacted **`qwen_vllm_docker_restart_readiness.json`** is written under that directory **if** Docker-restart audit ran on that invocation (opt-in path). It contains no headers, secrets, or prompts.

#### Proof boundary: W0–W5 scope vs product claims

The **W0–W5** work in this topology path documents and tests **apps_rg Qwen/vLLM transport and operator infra discipline**:

| In scope for W0–W5 | **Not** claimed by W0–W5 |
| --- | --- |
| Diagnostics, HTTP `/v1/models` preflight semantics, bounded **transient-only** chat retries (W3) | **Live** model output quality, resume narrative quality, or “production suitability” |
| Post-restart **HTTP + model substring** readiness when restart is opt-in (W4) | **X3 ALLOW** or any final disposition |
| Opt-in Docker restart behavior and infra guidance (W5) | Full **apps_rg** pytest tree green; full end-to-end resume generation certified |
| Targeted pytest slice listed in wave manifests | **Release certification**, Fort Knox, or any compliance sign-off |

W0–W5 **does not** weaken X2/X3, does not modify gate logic, and does **not** substitute for product-level evaluation.

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
removed from the repo at commit `c4970b6ddb` and briefly held in a local-only
gitignored `archives/` folder; the local archive was deleted 2026-05-06 (W5
of plan apps-rg-vllm-deferred-followup-f7d3a9) since the topology details
captured here are sufficient retrieval. The WSL2-side `~/.vllm_env` venv
(~9.7 GB) and `/home/amita/.config/systemd/user/vllm.service` were removed.
The model weights at `~/models/Qwen2.5-32B-Instruct-AWQ` (~20 GB) were
preserved as a cheap-to-keep fallback artifact.

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
