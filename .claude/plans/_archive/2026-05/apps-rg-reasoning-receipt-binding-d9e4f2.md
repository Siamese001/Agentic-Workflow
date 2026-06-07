---
plan_id: apps-rg-reasoning-receipt-binding-d9e4f2
plan_type: governance
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# apps_rg: reasoning receipt binding (child of governed reasoning plane)

Wire the **canonical apps_rg Qwen HTTP path** through a **thin app-local adapter** that delegates to `agentic_core.runtime.reasoning`, record **stripped / unsupported** controls deterministically, and **propagate** `_reasoning_execution_receipt` into normalized **`exec_trace`** (and/or sealed handoff) so **X1D consumes the ledger without manual producer copy**.

> **plan_id discipline:** Filename stem `apps-rg-reasoning-receipt-binding-d9e4f2` matches `plan_id` and Notion slug.  
> **Parent (closed generic track):** `reasoning-execution-control-plane-f4e9a2` — OPEN carry-forward: APPS_RG_RUNTIME_BINDING + SEALED_PACKET_PROPAGATION.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W0
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-05-16

---

## Context (SCQA)

| | |
|--|--|
| **Situation** | Generic reasoning control plane is **PASS** on `SovereignLLMGateway` + resolver + X1D cap when receipt is embedded in `exec_trace`. |
| **Complication** | **apps_rg** production Qwen calls can **bypass** the gateway; **`reasoning_execution_receipt`** is not auto-filled upstream of Exit normalization. |
| **Question** | How do we bind the **canonical apps_rg** outbound model path so declared controls → resolver → receipt → **ExitReviewPacket.exec_trace** without widening core authority? |
| **Answer** | **App-local adapter** calls generic `build_execution_plan` / `resolve_gateway_receipt` (+ optional `enforce_blocked` policy), merges primitive into **`exec_trace["reasoning_execution_receipt"]`** at the seal / packet-build seam. |

---

## Status Tables

### Wave Summary

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|-------------------|
| W1 | W1.1–W1.2 | Locate Qwen ingress/egress; map where `exec_trace` is built | ~8k | Canonical path = `apps_rg/runtime/providers/qwen_vllm_provider.py` + dispatch callers | 🔲 TODO | Written matrix CONTROL→callsite→carrier; adapter seam chosen |
| W2 | W2.1–W2.2 | Implement adapter + post-call receipt merge + transport observation hook | ~12k | HTTP JSON shape stable; caps from duck-typed provider surface | 🔲 TODO | Receipt primitive matches gateway schema; no silent kwargs drop |
| W3 | W3.1–W3.2 | Seal / normalize propagation + tests + grep proofs | ~10k | `normalize_to_packet` or L2 envelope has single choke point | 🔲 TODO | X1D test path receives receipt **without hand-built** `exec_trace` in test doubles beyond fixture builder |

### Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|-----------------|-------------|-------------|--------|
| W1.1 | Call graph audit | `qwen_vllm_provider.py`, `section_qwen_slice.py`, `canonical_dispatch.py`, bindings | Hidden alternate Qwen callers | ~4k | 🔲 TODO |
| W1.2 | Carrier map | sealed/L2 envelope apps_rg adapters, exit normalization entry | Duplicate trace dict builders | ~4k | 🔲 TODO |
| W2.1 | Adapter module | **new** `apps_rg/runtime/reasoning/` (or sibling) delegating to core resolver | Duplicate logic vs gateway | ~6k | 🔲 TODO |
| W2.2 | Merge + governance | Raise/record `ReasoningGovernanceError` where product policy mirrors gateway | Semantic mismatch vs CLI tolerance | ~6k | 🔲 TODO |
| W3.1 | Propagate into exec_trace | One choke point attaching `reasoning_execution_receipt` | Schema freeze on sealed types | ~5k | 🔲 TODO |
| W3.2 | Proof slice | `_apps_contract` or `tests/unit/apps_rg` narrow | PYTHONPATH/plugins | ~5k | 🔲 TODO |

### Wave Progress (hook-maintained mirror)

| Wave | Focus | Status | Tests Added | Files Changed |
|------|-------|--------|-------------|---------------|
| W1 | Audit + seam map | 🔲 TODO | — | — |
| W2 | Adapter + resolver merge | 🔲 TODO | — | — |
| W3 | Propagation + pytest | 🔲 TODO | — | — |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Call graph audit | 🔲 TODO |
| W1.2 | Carrier map | 🔲 TODO |
| W2.1 | Adapter module | 🔲 TODO |
| W2.2 | Merge + governance | 🔲 TODO |
| W3.1 | exec_trace attach | 🔲 TODO |
| W3.2 | Proof slice | 🔲 TODO |

---

## Out Of Scope

- Refactoring **`SovereignLLMGateway`** behavior beyond fixes required by shared types (prefer none).
- New **`apps_*` literals inside `agentic_core`** or provider-specific branching in generic core.
- Full **`tests/_apps_contract`** sweep; Fort Knox bundle promotion.
- **Direct L4 / UWG** writes.

---

## Hard constraints

1. **`agentic_core` remains generic** — all **apps_rg** wiring lives under `apps_rg/` (adapter imports core only downward).
2. **No silent ignore** of required controls — ledger must surface **UNSUPPORTED / IGNORED** where kwargs are stripped.
3. **`scratchpad` never** on outbound HTTP transport payloads (reuse core scratch guard semantics).
4. **Targeted pytest only** for this plan’s proof rows.

---

## Wave 1 — Audit + carrier map

WAVE_ID: W1  
WAVE_STATUS: TODO  
WAVE_COMPLETE: NO  
AUTHORIZATION_STATUS: NOT_REQUIRED  
CHECKPOINT: A

**Phases**:
- **W1.1** — Narrow call graph for `call_qwen_vllm` / HTTP provider | ~4k tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.2** — Identify single best attach point for `exec_trace["reasoning_execution_receipt"]` | ~4k tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- Matrix: declared reasoning kwargs/sources → outbound payload fields → ledger proof source.
- Explicit list of files touched in W2/W3 with rationale.

---

## Wave 2 — App adapter + resolver merge

WAVE_ID: W2  
WAVE_STATUS: TODO  
WAVE_COMPLETE: NO  
AUTHORIZATION_STATUS: NOT_REQUIRED  
CHECKPOINT: B

**Phases**:
- **W2.1** — Thin adapter: `TransportCapabilities`/observed payload from HTTP request body | ~6k | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.2** — After provider response: attach primitive to in-memory trace dict; decide `enforce_blocked` for product tiers | ~6k | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- Unit tests: resolver determinism on fixture intents; stripped control ≠ APPLIED.
- Adapter imports only from `agentic_core.runtime.reasoning.*` (+ local apps types).

---

## Wave 3 — Propagation + exit-visible proof

WAVE_ID: W3  
WAVE_STATUS: TODO  
WAVE_COMPLETE: NO  
AUTHORIZATION_STATUS: NOT_REQUIRED  
CHECKPOINT: C

**Phases**:
- **W3.1** — Wire merged trace into normalization / sealed packet builder used by RG dispatch | ~5k | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.2** — Integration-style test: build packet via real normalizer/fixture pipeline; assert **`eval_x1d`** observes quality cap when ledger denies cert | ~5k | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- Grep:** `apps_rg` adapter path has **zero** requirement to paste receipt manually into tests that simulate production normalizer output (fixture may simulate **one** internal helper that production uses).
- `rg`/bounded scan: new **`agentic_core/runtime/reasoning`** files unchanged by this plan (child is apps_rg).

---

## Gap Register

**GAP-1: Multiple Qwen entrypoints** — If audits find >1 canonical caller, pick one spine for MVP binding and ticket the rest DEFERRED.

**GAP-2: Async vs sync HTTP** — Adapter must mirror existing call pattern (no new event loop requirements).

---

## Definition of Done

| Item | Verification | Deferred? |
|------|--------------|-----------|
| Adapter exists under `apps_rg/` | File list in PR + import graph | No |
| Receipt on `exec_trace` in prod path | One integration test + trace assert | No |
| X1D quality cap triggered end-to-end | `eval_x1d` WARN on denying receipt | No |
| No core apps literals added | Bounded grep unchanged for generic package | No |
| No L4 writes | Scoped grep under changed files | No |

DoD-1: Receipt present when reasoning kwargs passed — Evidence: targeted pytest ledger non-empty coherent strip - Status: TODO

DoD-2: Smoke normalization attaches receipt without caller dict surgery - Evidence: narrow pytest selector exits 0 - Status: TODO

DoD-3: eval_x1d WARN REASONING_QUALITY_NOT_CERTIFIABLE when cert denied via normalized packet - Evidence: pytest captured output - Status: TODO

DoD-4: No silent strip required transport omission yields non-APPLIED ledger row - Evidence: pytest asserts ReceiptState - Status: TODO

DoD-5: Child closure note on disk linked from completion report - Evidence: markdown under docs/reports - Status: TODO

---

## Marker Quick Reference

```
WAVE_START: plan=apps-rg-reasoning-receipt-binding-d9e4f2 wave=<N>
WAVE_COMPLETE: plan=apps-rg-reasoning-receipt-binding-d9e4f2 wave=<N> note="+N tests, N files, scope=<summary>"
PLAN_COMPLETE: plan=apps-rg-reasoning-receipt-binding-d9e4f2 note="<outcome>"
```
