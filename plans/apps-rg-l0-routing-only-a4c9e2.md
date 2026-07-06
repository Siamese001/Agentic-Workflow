---
plan_id: apps-rg-l0-routing-only-a4c9e2
plan_format: v2
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
supersedes: []
---

# apps_rg L0 Routing Only

Implement apps_rg-only L0 route selection hardening so L0 emits deterministic, replayable, fail-closed RouteContract or terminal evidence without touching downstream execution layers.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: DONE
CURRENT_WAVE: W3
LAST_COMPLETED_WAVE: W3
LAST_UPDATED: 2026-07-05

---

## Context (SCQA)

- **Situation** — apps_rg already has L0 bindings, route evidence stamping, route profiles, and L0 contract tests.
- **Complication** — Current profiles mix app labels with canonical L0 branch vocabulary, managed workflow profiles are production-active by default, route signing can silently become unsigned outside pytest, and required gate UNKNOWN semantics are not consistently fail-closed.
- **Question** — How do we make apps_rg L0 select exactly one deterministic route and emit replayable, fail-closed evidence without crossing into downstream runtime stages?
- **Answer** — Keep route policy app-owned in apps_rg, normalize route vocabulary and activation metadata, harden digest/signing/gate semantics, add terminal/replay serialization evidence, and verify through an L0-only test target.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1, W1.2, W1.3 | Baseline and evidence | ~6K | User approved direct SQLite ADG fallback after MCP transport closed | ✅ DONE | Branch, plan, baseline tests, and characterization evidence captured |
| W2 | W2.1, W2.2, W2.3, W2.4 | Core L0 route hardening | ~16K | RouteContract can carry added evidence through existing default fields or app-local serializer without core changes | ✅ DONE | Digest/signing, schema, deterministic selection, and gate semantics are fail-closed |
| W3 | W3.1, W3.2, W3.3, W3.4 | Terminal/replay/boundary completion | ~16K | Terminal cache/fallback proof can be represented in L0 contract fields without invoking cache engines | ✅ DONE | Terminal packets, HITL annotation, boundary static checks, serializer round-trip, and L0 suite pass |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Create isolated worktree branch | ✅ DONE |
| W1.2 | Capture degraded ADG scope evidence | ✅ DONE |
| W1.3 | Run current L0 baseline and characterization test | ✅ DONE |
| W2.1 | Harden route digest and signing posture | ✅ DONE |
| W2.2 | Normalize route profile schema and activation metadata | ✅ DONE |
| W2.3 | Encode deterministic selection and ambiguity failures | ✅ DONE |
| W2.4 | Make required gate UNKNOWN/FAIL block progression | ✅ DONE |
| W3.1 | Emit terminal packet evidence for R1A/R1B/R5 | ✅ DONE |
| W3.2 | Keep HITL as annotation-only metadata | ✅ DONE |
| W3.3 | Validate apps/core L0 boundary | ✅ DONE |
| W3.4 | Add replay serializer and L0-only verification target | ✅ DONE |

---

## Out Of Scope

- C0 retrieval or graph traversal implementation changes.
- Prompt assembly, model execution, PA, L2, L3, Exit, UWG, L4, or L6 behavior changes.
- Model-backed lane or suite evals unless later work touches execution stages.
- agentic_core app-specific route literals or apps_rg-specific core branching.

---

## Wave 1 — Baseline And Scope

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: A

**Authorization**: APPROVED — User approved implementation on 2026-07-05.

**Phases**:
- **W1.1** — Create isolated worktree branch | ~1K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.2** — Capture degraded ADG scope evidence | ~2K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.3** — Run current L0 baseline and characterization test | ~3K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- Worktree branch `codex-apps-rg-l0-routing-only` exists from `origin/main`.
- Baseline command is captured before behavior edits.
- ADG provenance is explicit because MCP transport was closed.
- No downstream runtime behavior is changed.

---

## Wave 2 — Deterministic Fail-Closed L0 Selection

WAVE_ID: W2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: B

**Phases**:
- **W2.1** — Harden route digest and signing posture | ~4K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W2.2** — Normalize route profile schema and activation metadata | ~4K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W2.3** — Encode deterministic selection and ambiguity failures | ~4K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W2.4** — Make required gate UNKNOWN/FAIL block progression | ~4K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- No RouteContract leaves L0 without `route_digest`.
- Production signing secret absence fails closed; unsigned posture is explicit and test/dev-only.
- Route profiles expose canonical route ID, app route ID, route family, execution form, and activation metadata.
- Ambiguous or missing route profile matches fail closed.
- Required gate UNKNOWN/FAIL blocks progressing routes; optional inactive gates emit NOT_APPLICABLE.

---

## Wave 3 — Replay, Terminal Evidence, And Boundary Closure

WAVE_ID: W3
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: GRANTED
CHECKPOINT: C

**Phases**:
- **W3.1** — Emit terminal packet evidence for R1A/R1B/R5 | ~4K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W3.2** — Keep HITL as annotation-only metadata | ~3K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W3.3** — Validate apps/core L0 boundary | ~3K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W3.4** — Add replay serializer and L0-only verification target | ~6K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- R1A/R1B/R5 terminal branches produce replayable L0 terminal evidence without downstream execution.
- HITL metadata cannot override deterministic branch selection.
- apps_rg owns route policy; agentic_core remains generic.
- Serialized L0 artifacts round-trip without route semantic loss.
- L0-only suite runs without writer, graders, embedder, C0, PA, L2, L3, Exit, UWG, L4, or L6.

---

## Execution Details

### W1.1 — Create Isolated Worktree Branch
**Scope**: Keep code edits out of the dirty primary checkout on `main`.

**Commands**:
```bash
git fetch origin
git worktree add C:\Git\Agentic-Workflow-FRESH-worktrees\codex-apps-rg-l0-routing-only -b codex-apps-rg-l0-routing-only origin/main
```

### W1.2 — Capture Degraded ADG Scope Evidence
**Scope**: Use direct SQLite only because the active Codex ADG MCP transport returned `Transport closed` and the user explicitly requested MCP ADG bypass.

**Evidence**:
```text
DEGRADED_FALLBACK: reason=user_directed_mcp_adg_bypass_after_transport_closed
ADG Provenance: backend=degraded_sqlite, snapshot=adg_indexed_07042026_1748.sqlite
```

### W1.3 — Run Baseline
**Scope**: Establish current L0 behavior before route hardening.

**Commands**:
```bash
pytest tests/_apps_contract/test_l0_execution_form.py tests/_apps_contract/test_l0_gate_verdicts.py tests/_apps_contract/test_apps_rg_l1_l0_w3_evidence.py -q
```

### W2.1 — Route Digest And Signing
**Scope**: Split mandatory deterministic digest from mandatory production signing, with explicit unsigned posture only in test/dev.

### W2.2 — Route Profile Normalization
**Scope**: Add canonical route vocabulary and activation metadata in apps_rg profile YAML and validate every row.

### W2.3 — Selection Policy
**Scope**: Encode deterministic route ordering and fail closed on multiple production matches or no default catch-all.

### W2.4 — Gate Semantics
**Scope**: Required gates PASS only to proceed; FAIL and UNKNOWN block. Optional inactive gates emit NOT_APPLICABLE.

### W3.1 — Terminal Packets
**Scope**: Populate terminal evidence for R1A/R1B/R5 without invoking downstream cache engines.

### W3.2 — HITL Annotation
**Scope**: Carry HITL posture as guard metadata, not route authority.

### W3.3 — Boundary Closure
**Scope**: Add/verify static tests so agentic_core does not gain apps_rg-specific route branches.

### W3.4 — Replay Serializer And L0 Suite
**Scope**: Add canonical serializer/round-trip test and document the L0-only pytest target.

---

## Gap Register

**GAP-1: ADG MCP transport unavailable**
- Detail: `mcp__adg_sqlite.adg_health` returned `Transport closed`; readiness reported `adg_sqlite` callability unproven.
- Impact: Structural evidence uses direct SQLite with explicit degraded provenance.

---

## Definition of Done

DoD-1: Deterministic L0 route selection is fail-closed.
- Evidence: L0 tests prove stable digest, changed input changes digest, ambiguity fails, and no-match fails.
- Status: DONE

DoD-2: Signing posture is explicit.
- Evidence: Tests prove production missing HMAC secret blocks and explicit test/dev unsigned posture is the only unsigned allowance.
- Status: DONE

DoD-3: Gate semantics cannot treat UNKNOWN as PASS.
- Evidence: Tests prove required UNKNOWN/FAIL blocks, optional inactive gates are NOT_APPLICABLE, and existing permissive G20 expectations are updated.
- Status: DONE

DoD-4: Terminal and replay evidence is complete.
- Evidence: Tests prove R1A/R1B/R5 terminal packets and serialized L0 artifacts round-trip with route semantics intact.
- Status: DONE

DoD-5: L0-only verification suite passes.
- Evidence: `pytest tests/_apps_contract/test_l0_* tests/_apps_contract/test_apps_rg_l1_l0_w3_evidence.py -q` exits 0.
- Status: DONE

---

## Supersedes

_None — net-new plan._
