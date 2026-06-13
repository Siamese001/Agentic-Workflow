# RCA — H2: `optimized_vllm_client.py` Uses Raw aiohttp

**Plan reference:** `.windsurf/plans/routing-followups-7a2c91.md` (Phase F3.1)
**Parent gap:** `.windsurf/plans/routing-unification-qwen-abe735.md` §6 H2
**Status:** RCA — documentation only; no code change in this phase
**Date:** 2026-04-21

---

## 1. Observed State

File: `@c:\Git\Agentic-Workflow\agentic_core\L3_orchestration\inference\qwen_vllm\engines\optimized_vllm_client.py`

Imports (lines 29–30) raw `aiohttp` directly:

```python
import aiohttp
import aiohttp.client_exceptions
```

This makes the client **ADG-blind** for the purposes of routing enforcement. `aiohttp.ClientSession.post(...)` calls cannot be traced by the dependency graph as L3→provider edges because:

1. The ADG extracts `flows_to` / `emits_side_effect` edges from gateway methods. `aiohttp` is a third-party library — the graph layer does not classify raw-aiohttp calls as provider invocations.
2. The canonical provider seam is `agentic_core/interfaces/gateway.py` (`GenerationRequest` + `BaseGateway`). `SovereignLLMGateway` wraps this seam with provider registration, secret-key resolution, and OTEL span emission.
3. Bypassing the gateway means:
   - No provider-choice audit trail
   - No cost tracking for W6 P6.2 budget signal
   - No unified OTEL span for W F2 schema unification
   - No gate-0 replay guard

## 2. Impact

| ADG Surface | Violation |
|---|---|
| Execution | ✅ — direct HTTP execution bypasses gateway |
| Write | N/A |
| Security | ⚠️ — secret-key resolution skipped |
| State | N/A |
| Observability | ✅ — no OTEL span emission; telemetry invisible |

Per `adg-canonical-invariants.md` §3, this is a **SAFETY_GATEKEEPER** archetype violation when combined with §F2 (no unified telemetry): failures at the vLLM endpoint are swallowed without structured OTEL emission.

## 3. Root Cause

Historical: `optimized_vllm_client.py` predates the `SovereignLLMGateway` abstraction. It was a performance experiment (HTTP/2 keepalive, connection-pool tuning) that ran standalone during the pre-routing-unification era. Nobody migrated it when the gateway landed.

## 4. Recommended Fix (separate plan, NOT executed here)

A dedicated infra-wiring plan should:

1. **ADG fan-in scan** — `adg_edge_fanin(tgt_id=<optimized_vllm_client>, relation_type="imports")` to enumerate callers. Do NOT grep for this.
2. **Port to gateway** — replace `aiohttp.ClientSession` calls with `SovereignLLMGateway.route_generation(GenerationRequest(provider="qwen", ...))`.
3. **Preserve the perf optimizations** — HTTP/2 pool tuning should move into the gateway's transport layer, not be lost in the port.
4. **OTEL span parity** — emit `heal_router.v1.provider_call` spans (once F2 lands).
5. **Test migration** — existing `optimized_vllm_client` tests must pass against the gateway-backed replacement.

Estimated size: 8k tokens. Blocked by F2.2 (unified OTEL schema ADR) for span names.

## 5. Blast Radius Pre-Estimate

ADG fan-in (to be confirmed during plan execution): expected 2–4 direct callers in `qwen_vllm/engines/`. Low blast radius.

## 6. Non-Goals in the Eventual Fix

- Not introducing a new gateway type — `SovereignLLMGateway` is the SSOT
- Not deleting `optimized_vllm_client.py` — port in place, keep the class name for caller compat
- Not refactoring HTTP/2 pool behavior — pure wiring change

## 7. Next Action

Open a new execution plan at `.windsurf/plans/optimized-vllm-client-migration-<hash>.md` when F2.2 lands. Reference this RCA from §1 of that plan.

## 8. Provenance

ADG Provenance: backend=sqlite (fan-in not yet queried), evidence=grep match line 29–30 of source file
Constitutional compliance: §22 (ADG fan-in required before code); this RCA satisfies the analysis phase.
