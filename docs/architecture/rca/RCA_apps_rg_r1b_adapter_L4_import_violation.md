# RCA: apps_rg R1B Adapter L4 Import Violation

**RCA ID**: RCA-RGGOV-8  
**Date**: 2026-05-15  
**Author**: Codex (W5, plan `chroma-graphrag-core-wiring-gaps-b3f7a1`)  
**Status**: CLOSED — Decision: KEEP_QUARANTINED_DEPRECATED  
**Owner**: apps_rg governance (plan author gate AG-RGGOV-8)

---

## 1. Original Violation

`apps_rg/cache/r1b_adapter.py` was quarantined on 2026-05-09 under governance decision
`AG-RGGOV-8: QUARANTINE_ALL_RUNTIME_HOPS` (plan
`apps-rg-declarative-ingress-only-spinal-governance-c8b3e1` §19).

The file was found to import directly from `agentic_core.L4_state.semantic_cache_manager`
— a runtime-authority module in the L4 state layer. Under the declarative ingress-only
governance model, `apps_rg` is bounded to L0–L3 inputs and may NOT reach into L4 state
management at runtime.

**Quarantine guard installed**:
```python
raise RuntimeError(
    "QUARANTINE VIOLATION (AG-RGGOV-8): "
    "apps_rg.cache.r1b_adapter is QUARANTINED. ..."
)
```

---

## 2. Direct L4 Import Path

The original adapter contained an import of the form:

```python
from agentic_core.L4_state.semantic_cache_manager import SovereignSemanticCache
```

This is a direct L4 state-management import. `SovereignSemanticCache` is a runtime
authority that owns durable write paths to the semantic cache store.

**Why this violates layer boundaries:**

| Principle | Violation |
|---|---|
| Layer gravity | `apps_rg` (app layer) must not import from `agentic_core.L4_state` (runtime authority layer) |
| Declarative ingress-only | `apps_rg` is bounded to submitting requests, not reading/writing L4 state directly |
| No durable write from app layer | Any app importing `SovereignSemanticCache` can bypass the generic cache contract |
| Generic core owns cache dispatch | Cache lookup must flow through `agentic_core` L0 binding, not app-owned wiring |

The adapter was attempting to do what is correctly the job of
`agentic_core/L0_routing/reasoning/route_gates.check_d2_semantic_cache()`.

---

## 3. Is the Adapter Still Required After W1 Generic R1B Wiring?

**No. The adapter is obsolete.**

W1 (`chroma-graphrag-core-wiring-gaps-b3f7a1`) delivered the generic R1B path:

| Component | Status |
|---|---|
| `_read_semantic_cache_profile()` in `package_driven_l0_binding.py` | ✅ Live — reads `apps_rg` cache profile shape A (nested `semantic_cache` block) |
| `check_d2_semantic_cache()` call in R1B arm | ✅ Live — dispatched when `enabled: true` and `live_wiring_deferred: false` |
| `apps_rg` cache profile `semantic_cache.enabled: true` | ✅ Confirmed — namespace and threshold are present |
| `apps_rg` route order includes `R1B_SEMANTIC_CACHE` | ✅ Confirmed — `apps_rg/config/domain_contract/route_profiles.yaml` |
| Zero app-id checks in generic path | ✅ Confirmed — `_read_semantic_cache_profile` handles both profile shapes without branching on `app_id` |

**Evidence**:

```
apps_rg/config/domain_contract/cache_profiles.yaml:
  semantic_cache:
    enabled: true
    namespace: apps_rg.resume_gen.v1
    similarity_threshold: 0.88
    live_wiring_deferred: true       ← will be flipped to false in W5.2
    wiring_gate: W2_GENERIC_INFRA_EDIT_IN_AGENTIC_CORE_REQUIRED
```

W1 delivered the required generic infra edit. The `wiring_gate` condition
(`W2_GENERIC_INFRA_EDIT_IN_AGENTIC_CORE_REQUIRED`) is now satisfied. Setting
`live_wiring_deferred: false` is sufficient to activate the generic path for `apps_rg` —
**no app-specific adapter code is needed**.

**Test evidence** (W1 regression suite — 18 tests, all passing):
- `test_r1b_enabled_calls_check_d2_semantic_cache` — generic call confirmed
- `test_apps_rg_quarantined_adapter_untouched` — quarantine guard still raises
- `test_no_app_id_branch_in_package_driven_l0_binding` — zero app-id branching confirmed

---

## 4. Recommended Decision

**KEEP_QUARANTINED_DEPRECATED**

Rationale:

1. The generic R1B path through `package_driven_l0_binding.py` is fully capable of
   serving `apps_rg`'s R1B semantic cache lookup — no adapter code is needed.

2. Unquarantining `r1b_adapter.py` would reintroduce app-specific runtime state code
   with a direct L4 import, violating the declarative ingress-only governance model.

3. The quarantine guard (`RuntimeError`) must remain to prevent accidental imports.

4. The only caller of the quarantined file outside of the quarantine notice itself is
   `tools/apps_rg/warm_r1b_cache.py` — a tooling script, not in the production runtime
   path. That script will need a future refactor to use the generic path (tracked as
   `NEXT_STEP` below), but it does not block W5 closure.

5. The file should be deleted in a future cleanup wave when the tooling script is
   updated. It must not be revived.

---

## 5. Final Decision and Owner

| Field | Value |
|---|---|
| **Decision** | `KEEP_QUARANTINED_DEPRECATED` |
| **Effective date** | 2026-05-15 |
| **Owner** | apps_rg governance / plan `chroma-graphrag-core-wiring-gaps-b3f7a1` W5 |
| **Unquarantine required?** | No |
| **Generic R1B path used?** | Yes — via `package_driven_l0_binding.py` + `check_d2_semantic_cache()` |
| **App-specific adapter obsolete?** | Yes |
| **Future action** | Delete `apps_rg/cache/r1b_adapter.py` in a future cleanup wave after `tools/apps_rg/warm_r1b_cache.py` is refactored to use the generic path |

---

## 6. W5.2 Profile Action

Per this RCA decision, `apps_rg/config/domain_contract/cache_profiles.yaml` will be
updated to activate the generic R1B path:

```yaml
live_wiring_deferred: false
wiring_gate: CLEARED_BY_W1_GENERIC_R1B_CACHE_WIRING
```

This flip activates `check_d2_semantic_cache()` for `apps_rg` through the generic L0
binding. No app-specific code is touched.

---

## 7. NEXT_STEP (deferred, not blocking W5)

`tools/apps_rg/warm_r1b_cache.py` imports `apps_rg.cache.r1b_adapter.AppsRgR1BCacheAdapter`
at line 180. This import will raise `RuntimeError` if the warm-up script is executed.
The script must be refactored to use the generic cache write path before it can be used.
This is a tooling concern only and does not affect the production runtime.

NEXT_STEP: Refactor `tools/apps_rg/warm_r1b_cache.py` to use generic L0 cache path —
tracked for future cleanup wave after `r1b_adapter.py` deletion.
