---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\p0-layer-violation-remediation-7c4e1a.md'
original_relative_path: 'p0-layer-violation-remediation-7c4e1a.md'
source_sha256: 5fd5c6cc48f8c3311d53d8feef6dcc55f1f7056b90e30e7e10c2a5654bd4eb03
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-04-17'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# P0 Layer Violation Remediation Plan

**ADG Snapshot:** `adg_indexed_04172026_0522.sqlite`
**Gate status:** SC-1 BLOCK mode active as of 2026-04-17
**Total P0 violations:** 100 across 56 files

---

## Wave Structure

| Wave | Hop Pattern | Count | Focus | Status |
|------|------------|-------|-------|--------|
| W1 | `L2->L0` | 39 | L2 execution importing L0 routing config/enforcement | TODO |
| W2 | `L6->L2` + `L2->L6` | 28 | L2 ↔ L6 observability bidirectional coupling | TODO |
| W3 | `L0->L2` + `L0->L6` | 14 | L0 routing importing execution/observability | TODO |
| W4 | `L1->L2` + `L1->L3` + `L1->L6` | 17 | L1 cognition bypassing L3 dispatch | TODO |
| W5 | `L2->L1` | 2 | L2 calling back into cognition | TODO |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|--------------|-------------|-------------|--------|
| W1-P1 | L2 path constant hops | `unsafe_io_detector.py`, `write_gateway.py` | Import path constants from L0; move to shared L0 types or duplicate in L2 | 800 | TODO |
| W1-P2 | L2 enforcement hops | `execution_guardrail_chokepoint.py`, `durable_write_wrapper.py`, `sovereign_filesystem_mcp.py` | Import `mutation_prohibition` from L0; introduce L2-owned interface | 1200 | TODO |
| W1-P3 | L2 remaining config hops | 12 remaining L2→L0 files (1 violation each) | Path constants and routing config; batch guardian exemption or extract shared module | 1500 | TODO |
| W2-P1 | L2→L6 top offenders | `execution_guardrail_chokepoint.py` (L6 observability recorder) | Invert: L2 fires events via protocol, L6 subscribes | 1000 | TODO |
| W2-P2 | L6→L2 cluster | `governed_handoff.py`, `observability_recorder.py`, `async_eval_packet.py` + 5 others | L6 calling L2 types; move shared types to `agentic_core/interfaces/` or `runtime/` | 1500 | TODO |
| W3-P1 | L0→L6 | `agentic_router.py` (performance_emitter) | Extract emitter call behind L0-owned telemetry stub | 600 | TODO |
| W3-P2 | L0→L2 | `agentic_router.py` (ExecutionProofEmitter), `execution_gateway.py`, 5 others | Move proof emission protocol to `runtime/contracts/` | 1000 | TODO |
| W4-P1 | L1→L2 | `meta_client.py` (InfrastructureDependencyError), `reasoning_chokepoint.py` | Move shared error types to `interfaces/` or `runtime/types/` | 800 | TODO |
| W4-P2 | L1→L3 + L1→L6 | `meta_client.py` (bmg_embed), `semantic_retriever.py`, `cognitive_engine.py` | L1 should not call L3 directly; route via interface contract | 1200 | TODO |
| W5-P1 | L2→L1 | `validation_orchestrator.py`, `adaptation_orchestrator.py` | L2 calling L1 cognition types; move to `runtime/types/` | 500 | TODO |

---

## Gap Register

| ID | Gap | Blocker? | Resolution |
|----|-----|----------|------------|
| G1 | Path constants (`AGENTIC_CORE_DIR`, `APPS_*_DIR`, `TOOLS_DIR`) owned by `L0_routing/config/` but needed in L2 | Yes | Duplicate in `agentic_core/runtime/constants.py` OR guardian-exempt as stable config boundary |
| G2 | `mutation_prohibition.enforce_protected_root` is L0 enforcement called by L2 write gate | Yes | Move to `runtime/contracts/` (layer-neutral) or guardian-exempt as intentional enforcement chain |
| G3 | `observability_recorder` is L6 but called inline by L2 chokepoint | Yes | Replace with event emission via `runtime/contracts/lifecycle_trace_contract` (already imported) |
| G4 | `InfrastructureDependencyError` defined in L2 but imported by L1 | Yes | Move to `agentic_core/interfaces/` or `runtime/types/` |
| G5 | `bmg_embed_text` is L3 healer called by L1 meta_client | Yes | Route via interface in `agentic_core/interfaces/` |

---

## Remediation Strategies Per Pattern

### L2→L0 (path constants, 22 violations)
**Root cause:** `L0_routing/config/path_constants.py` is the sole SSOT for repo paths but L2 modules need them.
**Fix options (in priority order):**
1. Move path constants to `agentic_core/runtime/constants.py` (layer-neutral) — all layers import from there
2. Guardian-exempt stable config references: `# guardian: allow-layer-violation -- path constants are build-time stable config, not routing logic`

### L2→L0 (enforcement, 17 violations)
**Root cause:** L2 write/guardrail gates call L0 enforcement primitives directly.
**Fix:** Move enforcement primitives to `agentic_core/runtime/contracts/` which is layer-neutral.

### L2↔L6 (observability, 28 violations)
**Root cause:** `execution_guardrail_chokepoint.py` calls `observability_recorder` directly (L6) instead of emitting via the lifecycle trace contract already in place.
**Fix:** Remove direct `L6_observability` imports; use `lifecycle_trace_contract._emit_*` functions already imported at line 81/170.

### L0→L2/L6 (14 violations)
**Root cause:** `agentic_router.py` imports `ExecutionProofEmitter` (L2) and `performance_emitter` (L6).
**Fix:** Move `ExecutionProofEmitter` protocol to `runtime/contracts/`; replace `performance_emitter` with L0-owned telemetry stub.

### L1→L2/L3/L6 (17 violations)
**Root cause:** L1 modules import execution error types and healer utilities directly.
**Fix:** Move shared types to `agentic_core/interfaces/` (already exists as the cross-layer contract boundary).

---

## Execution Order

```
W1-P1 → W1-P2 → W2-P1 (unblock top offenders, clear ~26 violations)
W1-P3 || W2-P2 (parallel — different file clusters)
W3-P1 || W3-P2 || W4-P1 (parallel)
W4-P2 → W5-P1 (sequential — W4-P2 may move types W5-P1 depends on)
Verification: run generate_full_adg.py → must exit 0
```

---

## Success Criteria

1. `generate_full_adg.py` exits 0 with `[PASS] SC-1`
2. `violations WHERE severity='P0'` count = 0 in new ADG SQLite
3. Redis hot cache refreshed with clean ADG
4. No new P1/P2 violations introduced

---

## ADG Evidence

- **Snapshot:** `artifacts/adg/adg_indexed_04172026_0522.sqlite`
- **Fan-out queries run:** nodes 297, 449, 451, 55, 149 (top 5 offenders)
- **Hop breakdown confirmed via:** `tools/diag/p0_wave_plan.py`
- **Gate confirmed blocking:** exit code 1, `[BLOCK] SC-1: 100 violation(s)`
