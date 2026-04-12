# vLLM HTTP Seam Decision Packet

**Generated:** 2026-04-11
**Author:** Cascade (decision-prep pass — no code changes)
**Implemented:** 2026-04-11 — Path A APPROVED and executed
**ADG Snapshot:** `adg_indexed_04112026_1604.sqlite`
**Findings source:** `docs/reports/plans/infra_wiring_findings.md` §E-1 + §FC
**Tier:** T2 — scoped, single subsystem, no cross-layer writes
**Status: IMPLEMENTED ✅** — `optimized_vllm_client.py` added to `_APPROVED_ADAPTER_PATHS`, APPROVED in `SANCTIONED_ADAPTER_FILES`, seam contract comment block added. `v_p1_raw_http_outside_seam = 0`. Scan passes P0=0 P1=0.

---

## A. Executive Summary

`optimized_vllm_client.py` manages a full production-grade `aiohttp` HTTP session directly inside
L3 Orchestration. It was tagged `UNDER_REVIEW` in `SANCTIONED_ADAPTER_FILES` pending this decision. Two paths were
available: (A) formally approve the existing seam with a minimal contract, or (B) migrate to an
existing approved HTTP seam.

**Decision: Path A — APPROVED and implemented (2026-04-11).**

The client implements five concurrent capabilities (connection pooling, keep-alive, batching,
semaphore-controlled concurrency, in-process response caching) that are tightly coupled to the
`asyncio` event loop shared by all L3 inference callers. Neither `enhanced_http_server.py` nor
`api_gateway_integration.py` can replicate these semantics without a multi-file, high-risk
rewrite. The blast radius of Path B is 6+ files, non-trivial throughput regression risk, and
loss of caching behavior. Path A requires only a one-line registry reclassification and a four-line
contract annotation.

---

## B. Current-State Wiring and Caller Map

### B.1 — `optimized_vllm_client.py` anatomy

**Location:** `agentic_core/L3_orchestration/inference/qwen_vllm/engines/optimized_vllm_client.py`
**Layer:** L3 Orchestration
**ADG status:** Not indexed (ADG is blind to `aiohttp` as an external package node; confirmed by
`v_p1_raw_http_outside_seam = 0` even after rebuild)
**Current registry status:** `SANCTIONED_ADAPTER_FILES` with `UNDER_REVIEW`

#### HTTP session details (lines 107–133)
```python
aiohttp.TCPConnector(
    limit=20,           # max total connections
    limit_per_host=10,  # max connections per host
    keepalive_timeout=30,
    enable_cleanup_closed=True,
    force_close=False,
)
aiohttp.ClientSession(
    connector=...,
    timeout=ClientTimeout(total=300, connect=10, sock_read=60),
    headers={"Content-Type": "application/json", "Connection": "keep-alive"},
)
```

#### Concurrency and batching (lines 61–90)
| Feature | Implementation | Parameters |
|---|---|---|
| Connection pool | `aiohttp.TCPConnector` | 20 total / 10 per host |
| Keep-alive | `keepalive_timeout=30` | 30 s |
| Concurrency gate | `asyncio.Semaphore(max_concurrent)` | default 8 |
| Request batching | `asyncio.Queue` + background `_batch_task` | batch_size=4, timeout=50 ms |
| Response cache | `dict[str, VLLMResponse]` (LRU-style) | 1000 entries |
| Timeouts | total=300 s, connect=10 s, read=60 s | hard-coded in `start()` |

#### Singleton management (file-level)
```python
_vllm_client: OptimizedVLLMClient | None = None

async def get_vllm_client(...) -> OptimizedVLLMClient: ...
async def close_vllm_client() -> None: ...
```

### B.2 — Direct import callers

| File | Import path | Usage |
|---|---|---|
| `engines/hardened_vllm_client.py` | `from .optimized_vllm_client import OptimizedVLLMClient, VLLMRequest, VLLMResponse` | Wraps in circuit-breaker + retry layer |
| `reasoning/qwen_inference_gateway.py` | `from ...engines.optimized_vllm_client import OptimizedVLLMClient, VLLMRequest, VLLMResponse` | Constructs `OptimizedVLLMClient` directly in `_ensure_initialized()` |
| `engines/__init__.py` | Re-exports `OptimizedVLLMClient`, `VLLMRequest`, `VLLMResponse`, `get_vllm_client`, `close_vllm_client` | Surface export |
| `qwen_vllm/__init__.py` | Re-exports the full surface via `engines` package | Top-level package export |

**Test-only callers (not production):**
- `tests/performance/test_hardened_vllm.py`
- `tests/unit/agentic_core/L3_orchestration/inference/qwen_vllm/test_engines.py`
- `tests/performance/test_qwen_vllm_performance.py`
- `tests/performance/benchmark_runner.py`

### B.3 — Instantiation pattern in `qwen_inference_gateway.py`

```python
async def _ensure_initialized(self) -> None:
    if not self._initialized:
        self._vllm_client = OptimizedVLLMClient(
            base_url=self.base_url,
            model=self.model_id,
            max_concurrent=self.max_concurrent,
            batch_size=self.batch_size,
        )
        await self._vllm_client.start()   # <-- creates aiohttp session here
        self._initialized = True
```

`start()` is the lifecycle entry point for the aiohttp session. `close()` is the teardown. Both
are async. The client is meant to live for the duration of the gateway's lifetime, not per-request.

### B.4 — Layer classification

The client sits entirely within the `qwen_vllm` subtree of L3 Orchestration. It does not reach
into `infrastructure/sdks_mcps`, `apps_*`, or L0/L1. Its only cross-module surface is the types
`VLLMRequest` / `VLLMResponse` and the singleton accessors, all exported via the engines package
`__init__.py`.

---

## C. Path A — Approve Current Seam

### What approval means

Formally reclassify `optimized_vllm_client.py` from `UNDER_REVIEW` to a named, compliant
`SANCTIONED_ADAPTER` within L3. Define the narrowest approval contract below, add it to
`_APPROVED_ADAPTER_PATHS`, and set the `v_p1_raw_http_outside_seam` CI ratchet ceiling to 1
(from ADG-blind / informational).

### Approval contract (minimum required)

| Constraint | Value |
|---|---|
| Approved target hosts | `localhost` or `127.0.0.1` only (vLLM runs locally) |
| Approved port range | `8000–8099` (vLLM OpenAI-compat API) |
| Session lifecycle | Must call `start()` before first request; `close()` on shutdown |
| Max connections | Must not exceed `limit=20` total, `limit_per_host=10` |
| Approved callers | `qwen_inference_gateway.py`, `hardened_vllm_client.py`, and test harnesses only |
| Prohibited usage | Must not be imported from `apps_*` or any layer outside L3 |
| ADG enforcement | Enforced by file scanner (ADG-blind for aiohttp external node); ratchet ceiling 1 |

### Scorecard / registry consequences

1. `SANCTIONED_ADAPTER_FILES`: remove `UNDER_REVIEW` flag, add approval comment.
2. `_APPROVED_ADAPTER_PATHS`: add `agentic_core/L3_orchestration/inference/qwen_vllm/engines/optimized_vllm_client.py`.
3. CI ratchet `v_p1_raw_http_outside_seam`: set ceiling to `1` (was informational; now formally asserted at 1).
4. `infra_wiring_scorecard.json`: compliance score increases (1 UNDER_REVIEW resolved).

### Risk assessment

| Dimension | Score | Notes |
|---|---|---|
| Risk | **LOW** | No code change. Registry-only. Zero chance of runtime regression. |
| Blast radius | **1 file** | Registry/scorecard only. |
| Performance impact | **None** | No change to aiohttp session config. |
| Architectural cleanliness | **Medium** | Raw aiohttp in L3 is a mild violation of the "no external SDK in core" preference, but the client is fully isolated within the qwen_vllm subtree and doesn't escape to apps_*. |
| Required follow-up | **Low** | Add approval contract comment to file header; register in `_APPROVED_ADAPTER_PATHS`. |
| Reversibility | **Fully reversible** | Flip back to UNDER_REVIEW or escalate to P1 at any future point. |

### What this path cannot fix

- ADG will remain blind to the `aiohttp` import edge. The file scanner remains the only CI enforcement.
- If a future caller in `apps_*` imports from this seam, the scanner must catch it; ADG cannot.

---

## D. Path B — Migrate to Existing or New Approved HTTP Seam

### D.1 — Can `enhanced_http_server.py` host this traffic?

**Answer: No — not without non-trivial rewrite of the callers.**

`enhanced_http_server.py` is an **MCP server process** (`tools/mcp/`). It:
- Runs as a standalone `stdio_server` process, not as an importable Python library.
- Has `BLOCKED_HOSTNAMES = {"localhost", "internal", ...}` — it **blocks** `localhost` by design
  (line 55–60). vLLM runs at `http://localhost:8000`. This is a hard blocker.
- Creates a new `aiohttp.ClientSession` per request (no persistent pooling, no keep-alive).
- Has no batching, no in-process cache, no semaphore concurrency control.
- Returns `CallToolResult` objects, not typed `VLLMResponse` dataclasses.
- Cannot be called `await session.post(...)` from within the same asyncio loop.

To use it, callers would need to: (1) speak MCP stdio protocol, (2) give up all five
performance primitives, (3) route to a process boundary on every inference call. This is
architecturally backwards for a latency-sensitive inference path.

### D.2 — Can `api_gateway_integration.py` host this traffic?

**Answer: No — it is a tracing/header injection layer, not an HTTP client.**

`api_gateway_integration.py` (`agentic_core/gateway/`) is:
- A **gateway abstraction** for Kong, Ambassador, Envoy, AWS API Gateway — not a direct HTTP client.
- Its `KongGatewayClient.health_check()` uses synchronous `requests.get(...)`, incompatible with
  async vLLM inference.
- Contains no connection pooling for inference traffic, no request queue, no caching, no semaphore.
- Its purpose is tracing header injection and service registration, not inference request execution.
- Lives in `agentic_core/gateway/` — a different subtree from L3 Orchestration. Routing inference
  through it would create a new cross-subtree dependency.

### D.3 — New seam option: create a `create_vllm_http_session()` in `infrastructure/sdks_mcps`

This would add a factory function that returns a configured `aiohttp.ClientSession`, similar to
`create_openai_client()`. Assessment:

| Dimension | Score | Notes |
|---|---|---|
| Risk | **HIGH** | Requires touching `optimized_vllm_client.py`, `hardened_vllm_client.py`, `qwen_inference_gateway.py`, `infrastructure/sdks_mcps/__init__.py`, registry, scorecard, tests — 6+ files. |
| Blast radius | **6+ files** | Cross-layer (L3 → infrastructure). New guardian exemption needed. |
| Performance impact | **Medium risk** | Batching queue and semaphore are tied to the client instance lifecycle. Extracting session creation without disrupting the batch processor requires careful surgery. |
| Architectural cleanliness | **High** | Would align with the seam pattern used for OpenAI, Vertex. |
| Required follow-up | **High** | New seam function, guardian exemption, registry update, 4 file edits, test suite updates. |
| Reversibility | **Low** | Once callers depend on the new seam, rolling back requires re-touching all 6 files. |

**Behavior that would be lost or at risk during migration:**
- `_batch_task` is launched inside `OptimizedVLLMClient.start()`. If session creation moves out,
  the batch processor initialization sequence must be preserved — not automatic.
- In-process `_cache` dict is coupled to the `OptimizedVLLMClient` instance. A pure session-factory
  seam does not help with caching; caching logic would remain in the same file regardless.
- The new factory seam solves only the session creation concern — it does not eliminate the
  `aiohttp` import from `optimized_vllm_client.py`, since batching, pooling, semaphore, and caching
  all still reference `aiohttp` types directly.

---

## E. Recommendation

**Path A — Approve the current seam.**

### Rationale

1. **Path B provides no architectural benefit proportional to its cost.** The `aiohttp` import
   cannot be removed from `optimized_vllm_client.py` regardless of which migration variant is
   chosen, because batching, pooling, and caching reference `aiohttp` types directly. A new
   `create_vllm_http_session()` factory in `infrastructure/sdks_mcps` would reduce the raw SDK
   exposure only for session creation, while leaving all other `aiohttp` references in place.
   The surface reduction is marginal.

2. **The seam is genuinely isolated.** The client lives entirely within the `qwen_vllm` subtree of
   L3. It does not reach into `apps_*`. Its public surface (`VLLMRequest`, `VLLMResponse`,
   `get_vllm_client`, `close_vllm_client`) contains no `aiohttp` types — callers never touch
   `aiohttp` directly. This is the definition of a contained seam.

3. **`enhanced_http_server.py` is architecturally incompatible.** The `localhost` block is a hard
   incompatibility with zero workaround that doesn't require modifying the MCP server itself.

4. **Throughput regression risk is real for Path B.** The five performance primitives (pooling,
   keep-alive, batching, semaphore, cache) are load-bearing for Qwen inference throughput. Any
   migration that disrupts the `start()` / `_batch_task` lifecycle sequence risks silent
   performance regression. Path A carries zero such risk.

5. **Approval is fully reversible.** If a future audit requires migration to a different seam,
   the registry can be reverted and a P1 can be filed. No code is locked in.

---

## F. Required Follow-Up Changes If Approved (Path A)

These are the only changes needed. All are registry/annotation — zero runtime code changes.

| # | Action | File | Change |
|---|---|---|---|
| 1 | Remove `UNDER_REVIEW` flag | `SANCTIONED_ADAPTER_FILES` registry | Reclassify to approved |
| 2 | Add to approved adapter paths | `_APPROVED_ADAPTER_PATHS` | Add the full file path |
| 3 | Set CI ratchet ceiling | `infra_wiring_scan.py` or CI gate config | `v_p1_raw_http_outside_seam = 1` |
| 4 | Add contract comment to file | `optimized_vllm_client.py` line 1–20 | Add approved seam header comment |
| 5 | Update scorecard | `artifacts/infra_wiring_scorecard.json` | Increment compliance score |

**Total files touched: 4–5 (registry, scan config, scorecard, one annotation in client file).**
No test changes. No import changes. No ADG rebuild required (ADG already blind to this node).

---

## G. Exact Next Implementation Prompt

```
## SR_INTAKE
Objective: Formally approve optimized_vllm_client.py as the sanctioned L3 vLLM HTTP seam.
This is a registry-and-annotation-only wave. No runtime code changes.
Tier: T1 (≤5 files, single layer concern)

Constraints:
- Do NOT change optimized_vllm_client.py logic or imports.
- Do NOT touch hardened_vllm_client.py, qwen_inference_gateway.py, or any test file.
- Do NOT touch enhanced_http_server.py or api_gateway_integration.py.
- Do NOT run ADG rebuild (not needed; ADG is blind to this node regardless).

Steps:
1. In the SANCTIONED_ADAPTER_FILES registry (wherever it lives — likely infra_wiring_scan.py
   or a dedicated config), find the entry for optimized_vllm_client.py and change its status
   from UNDER_REVIEW to APPROVED. If the structure is a dict, set approved=True.

2. In _APPROVED_ADAPTER_PATHS (same file or separate config), add the canonical path:
     agentic_core/L3_orchestration/inference/qwen_vllm/engines/optimized_vllm_client.py

3. In the CI ratchet configuration for v_p1_raw_http_outside_seam, set ceiling = 1.
   (Currently set to 0 or informational; raise to 1 to formally assert that exactly 1
   approved raw-http seam exists in L3.)

4. Add an approval contract comment block at the top of optimized_vllm_client.py (lines 3–10),
   immediately after the module docstring, with this exact content:
   # SANCTIONED SEAM — approved L3 vLLM HTTP adapter.
   # Approved hosts: localhost / 127.0.0.1 port 8000-8099 only.
   # Approved callers: qwen_inference_gateway.py, hardened_vllm_client.py, test harnesses.
   # Must NOT be imported from apps_* or layers outside L3.
   # Lifecycle: call start() before first request, close() on shutdown.
   # ADG enforcement: file-scanner only (aiohttp is external; ADG edge invisible).

5. Update artifacts/infra_wiring_scorecard.json: set the UNDER_REVIEW count for
   optimized_vllm_client.py to resolved, and update compliance_score accordingly.

6. Verify with: python ops_scripts/ci/infra_wiring_scan.py
   Expected: v_p1_raw_http_outside_seam = 0 (ADG) or 1 (if scanner detects the
   approved seam correctly under the new ceiling). No new violations.

Success criteria:
- optimized_vllm_client.py status = APPROVED in registry.
- CI scan exits 0 with raw_http ceiling satisfied.
- No test regressions (no test changes needed; test imports are unchanged).
- Scorecard compliance_score >= pre-approval value.
```

---

*Decision packet complete. No code was changed in this pass. §FC ambiguity from
`infra_wiring_findings.md` is resolved: formal approval of Path A.*
