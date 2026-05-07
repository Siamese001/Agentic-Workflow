# Deferred Scope — agentic-spine-diagram-refinement-a3f7c2

> Auto-generated from plan completion. Items below were identified during
> execution but explicitly deferred. Do NOT implement without a new plan.

---

## Context

The parent plan (`agentic-spine-diagram-refinement-a3f7c2`) addressed 6 of 9
gaps (GAP-1 through GAP-4, GAP-8, GAP-9). Three gaps and several out-of-scope
items remain.

---

## Deferred Gaps

### GAP-5: `apps_qna` product mode (default `build`) runs OUTSIDE the spine

- `apps_qna/__main__.py` default path calls `run_qna.main()` → `spine_handoff.build_pack_via_spine()`. This emits only a `ValidatedRequest` envelope — no L0 route check, no L2 execution receipt, no Exit eval (X1/X2/X3), no L6 exhaust, no L7 HowTrace.
- The cert mode (`--apps-e2e-live`) IS fully wired via `apps_shared.spine_emission.governed_run`. The live interview mode (`--interview`) is partially wired.
- **Impact**: the spine diagram shows `apps_qna` as spine-connected but the normal product path is only partially connected (intake validation only).

### GAP-6: `apps_research` has no internal spine wiring

- No imports of `agentic_core` L-layer components found in `apps_research/`. It runs as a standalone pipeline with no U0 intake, no L0 routing, no Exit eval, no L7 audit.
- The `research_l3_adapter.py` (W5) wraps apps_research from the outside — but apps_research itself still has no internal spine envelope.
- **Impact**: research pipeline is invisible to the spine internally — no HowTrace, no exit disposition, no cache keys fed back to D1/D2.

### GAP-7: R1B / D2 semantic cache gated behind `SEMANTIC_CACHE_D2_ENABLED=1` env flag (disabled by default)

- `apps_rg/__main__.py` wraps both R1B recall and R1B store in `if os.environ.get("SEMANTIC_CACHE_D2_ENABLED", "0") == "1"`. In all normal runs the D2 path is dead code.
- W3 wired `learn()` in the R4 entrypoint, but the cache infrastructure itself (`_init_gptcache`) also gates on the same env flag.
- **Impact**: the spine diagram implies D2 semantic cache is an active layer; in practice it is opt-in and off by default for all apps.

---

## Out-Of-Scope Items (from parent plan)

These were declared out of scope for the parent plan and remain unaddressed:

1. **Changing the routing logic of X1–X3 gates** — diagram labels were added (W1), but no logic changes.
2. **Adding new guardrail rules to L5 safety** — not addressed.
3. **Modifying C0 grounding retrieval strategy** — not addressed.
4. **Retraining or swapping the BGE-M3 embedding model** — not addressed.
5. **Any change to L6 runtime exhaust or learning ledger schema** — not addressed.
6. **ADR authoring** — not addressed (observational plan only).
7. **Modifying `apps_research` internals** — adapter wraps public interface only (W5).
8. **Changing `apps_lic` → `apps_research` path** — only apps_rg path addressed (W5).

---

## Suggested Priority Order

| Priority | Item | Rationale |
|----------|------|-----------|
| P1 | GAP-7: Enable D2 by default or add auto-enable logic | ✅ DONE — `6c0bf44` |
| P2 | GAP-5: Wire apps_qna product mode into spine | ✅ DONE — `2c99705` |
| P3 | GAP-6: Add spine envelope inside apps_research | ✅ DONE — `984534a` |
| P4 | Out-of-scope items | Lower urgency, architectural decisions needed |

---

## Rules

- Do NOT implement any item in this document without a new plan at `.windsurf/plans/`.
- Each item may require its own Author-Gate decision (especially GAP-7 which changes default behavior).
- The parent plan is complete and closed. This document is a capture artifact only.
