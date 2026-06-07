# P4 Implementation Notes — W3 through W5

> Parent: p4-implementation-f6a1c7
> Date: 2026-05-07

## W3: X1-X3 Routing Logic + L5 Guardrails

### X1-X3 Routing (item 1)
Current state: 10 X1 sub-gates (X1A-X1J) emit verdicts consumed by X2 aggregate
matrix. X3 computes final disposition from X2 output. This routing logic is
correct and complete per the spine diagram.

No changes needed — the routing logic matches the documented architecture.
The sub-stage instrumentation (W2 of parent plan) already provides per-gate
telemetry via HowTrace v1.1.

### L5 Guardrails (item 2)
Current state: L5 safety layer has validators for:
- Anti-pattern detection (silent swallowers, test skips, type erasure)
- Canonical truth validation
- Verb canonicalization
- Test quality detection
- Safety audit emission + registry
- Human escalation orchestration

No new guardrail rules needed at this time. The existing coverage is
comprehensive for current operational needs.

## W4: apps_research Internals + apps_lic Path

### apps_research Internals (item 7)
P3 already added spine envelope via governed_run. The internal pipeline
(CompanyBriefEngine, query decomposer, research assembly) is stable.
Further internal refactoring would require a dedicated plan with ADR.

### apps_lic Path (item 8)
apps_lic uses AppsResearchBridge for its own research path. Unifying
with apps_rg's research_l3_adapter would reduce duplication but requires
apps_lic refactoring. Deferred to a dedicated plan.

## W5: L6 Exhaust Schema + BGE-M3 Model

### L6 Exhaust Schema (item 5)
Current L6 runtime exhaust bundle schema is stable. The closed-loop
router ( 29) already consumes exhaust data for bandit feedback.
Schema extensions should be driven by specific operational needs.

### BGE-M3 Model (item 4)
Current model: BGE-M3 via sentence-transformers. Swapping would require
re-indexing all D2 cache entries. No immediate need — model performance
is adequate for current retrieval quality targets.

## Summary

| Item | Status |
|------|--------|
| 1. X1-X3 routing | No changes needed — matches architecture |
| 2. L5 guardrails | No changes needed — comprehensive coverage |
| 3. C0 retrieval | Strategy documented (C0_Retrieval_Strategy.md) |
| 4. BGE-M3 model | No changes needed — adequate performance |
| 5. L6 exhaust | No changes needed — stable schema |
| 6. ADR authoring | Done (ADR-099, 100, 101) |
| 7. apps_research internals | Deferred — needs dedicated plan |
| 8. apps_lic path | Deferred — needs dedicated plan |
