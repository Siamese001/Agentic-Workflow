SUB-ATOMIC LAYER PURITY: HOW “GRAVITYHEALER” STAYS ONE-LAYER
(while still using L4 state + L5 safety)

LEGEND
  [AGENT]        = a single agent (must belong to exactly ONE layer)
  (CAP#)         = capability focus (<= 2 per agent)
  {CONTRACT}     = narrow schema boundary (no cross-layer logic leakage)
  ─────────▶     = call / message / handoff (NOT shared ownership)

──────────────────────────────────────────────────────────────────────────────
BAD (VIOLATION): One agent “spans” L5 + L4 (owns both logics)
──────────────────────────────────────────────────────────────────────────────

   L5 SAFETY LAYER                          L4 STATE LAYER
┌───────────────────────┐              ┌───────────────────────┐
│ [GravityHealer AGENT]  │────────────▶│  writes state file     │
│ (CAP: detect+heal)     │◀────────────│  reads state file      │
│  - detects violations  │              │  - state semantics     │
│  - computes fingerprints│             │  - record validation   │
│  - defines record schema│             │  - locking/atomicity   │
│  - performs persistence │              └───────────────────────┘
└───────────────────────┘

WHY THIS FAILS:
- L5 agent owns L4 persistence semantics (layer bleed)
- One agent performs >1 layer’s sovereign responsibilities


──────────────────────────────────────────────────────────────────────────────
GOOD (COMPLIANT): GravityHealer is ONE L5 agent; L4 is a separate state agent
──────────────────────────────────────────────────────────────────────────────

   L5 SAFETY LAYER                                  L4 STATE LAYER
┌──────────────────────────────────┐        ┌─────────────────────────────────┐
│ [GravityHealer (L5) AGENT]        │        │ [GravityState (L4) AGENT]       │
│ (CAP#1: violation analysis)       │        │ (CAP#1: state persistence)      │
│ (CAP#2: fix proposal/apply)       │        │ (CAP#2: audit/history query)    │
│                                  │        │                                 │
│  1) Detect + analyze violation    │        │  A) Load/validate state         │
│  2) Propose/Apply fix (optional)  │        │  B) Lock + atomic write         │
│  3) Emit HealingEvent             │        │  C) Record HealingEvent         │
└───────────────┬──────────────────┘        └───────────────┬─────────────────┘
                │                                           │
                │   {HealingEventContract v1}               │
                └───────────────▶ (append-only event) ──────┘


KEY IDEA:
GravityHealer does NOT “operate on L4”; it only emits an event.
GravityState does NOT “operate on L5”; it only stores/serves events.


──────────────────────────────────────────────────────────────────────────────
STRICTEST FORM (EVEN CLEANER): Add an Orchestrator to avoid direct L5↔L4 calls
──────────────────────────────────────────────────────────────────────────────

          L0/L1 ORCHESTRATION (routing only; no domain logic)
┌─────────────────────────────────────────────────────────────────────┐
│ [GravityHealingOrchestrator]                                         │
│  - calls L5 to detect/propose/apply                                  │
│  - calls L4 to query/record                                          │
│  - enforces sequencing + locks + TOCTOU protection                   │
└───────────────┬───────────────────────────────┬─────────────────────┘
                │                               │
                │                               │
      L5 SAFETY │                               │ L4 STATE
┌───────────────▼───────────────┐    ┌──────────▼─────────────────────┐
│ [GravityHealer (L5) AGENT]     │    │ [GravityState (L4) AGENT]      │
│ (CAP: analyze+heal)            │    │ (CAP: persist+query)           │
└───────────────────────────────┘    └────────────────────────────────┘


HOW THIS SATISFIES YOUR RULES
1) “One layer per agent”
   - GravityHealer is purely L5 (safety: detect/repair)
   - GravityState is purely L4 (state: record/query)
   - Orchestrator is routing (no L4/L5 domain logic)

2) “<=2 capabilities per agent”
   - GravityHealer: (1) detect/analyze  (2) propose/apply fix
   - GravityState:  (1) persist/lock    (2) query/audit

3) “Cross-layer interaction is contract-only”
   - Only {HealingEventContract v1} crosses the boundary
   - No shared schema ownership in L5; validation/locking belongs to L4
