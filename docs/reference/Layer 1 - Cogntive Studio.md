███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
█  [ SYSTEM INGRESS / CHECK ] ── Pre-Layer Envelope Validation                                                                                            █
█  Ensures: Authentication │ Quota Verification │ Safety Guardrails │ Session State Hydration                                                             █
███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
                                    │
                                    ▼ (Validated Raw User Prompt + Session Context)
███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
█  [ LAYER 1: COGNITIVE STUDIO ] ── STRUCTURED PLANNER CONTROL PLANE                                                                                      █
█  DOMAINS: Strict Isolation │ ZERO Tool Execution │ ZERO Vector Retrieval Ownership │ Immutable Audit Trail                                              █
███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████

                                    [ CUMULATIVE CONTEXT BUS ] ──(State accumulation preventing isolated execution)──┐
                                    │                             │                                  │               │
  ┌─────────────────────────────────▼┐   ┌────────────────────────▼─────────┐   ┌────────────────────▼─────────────┐   ┌────────────────────▼─────────────┐
  │ [Phase 1] INGESTION & PRIMING    │   │ [Phase 2] INTENT EXTRACTION      │   │ [Phase 3] PLAN & TOOL BUDGET     │   │ [Phase 4] CONTEXT & ROUTE        │
  │ Role: Intake Librarian           │   │ Role: Classification Librarian   │   │ Role: Planner Librarian          │   │ Role: Emitter Librarian          │
  └────────────────┬─────────────────┘   └────────────────┬─────────────────┘   └────────────────┬─────────────────┘   └────────────────┬─────────────────┘
                   │                                      │                                      │                                      │
        [ Raw Request + Rules ]                [ P1 Output + New Rules ]              [ P2 Output + Tool Specs ]             [ P3 Output + Route Specs ]
                   │                                      │                                      │                                      │
  ╭────────────────▼─────────────────╮   ╭────────────────▼─────────────────╮   ╭────────────────▼─────────────────╮   ╭────────────────▼─────────────────╮
  │ ∇ Tokenize (Byte Pair Encoding)  │   │ ∇ Tokenize (Byte Pair Encoding)  │   │ ∇ Tokenize (Byte Pair Encoding)  │   │ ∇ Tokenize (Byte Pair Encoding)  │
  │ ∇ Embed (Continuous Vectors)     │   │ ∇ Embed (Continuous Vectors)     │   │ ∇ Embed (Continuous Vectors)     │   │ ∇ Embed (Continuous Vectors)     │
  ╰────────────────┬─────────────────╯   ╰────────────────┬─────────────────╯   ╰────────────────┬─────────────────╯   ╰────────────────┬─────────────────╯
                   │                                      │                                      │                                      │
  ╔════════════════▼═════════════════╗   ╔════════════════▼═════════════════╗   ╔════════════════▼═════════════════╗   ╔════════════════▼═════════════════╗
  ║ TRANSFORMER NEURAL NETWORK x N   ║   ║ TRANSFORMER NEURAL NETWORK x N   ║   ║ TRANSFORMER NEURAL NETWORK x N   ║   ║ TRANSFORMER NEURAL NETWORK x N   ║
  ║ ├─ Self-Attention (Query, Key,   ║   ║ ├─ Self-Attention (Query, Key,   ║   ║ ├─ Self-Attention (Query, Key,   ║   ║ ├─ Self-Attention (Query, Key,   ║
  ║ │                  Value)        ║   ║ │                  Value)        ║   ║ │                  Value)        ║   ║ │                  Value)        ║
  ║ └─ Feed-Forward Network          ║   ║ └─ Feed-Forward Network          ║   ║ └─ Feed-Forward Network          ║   ║ └─ Feed-Forward Network          ║
  ╚════════════════┬═════════════════╝   ╚════════════════┬═════════════════╝   ╚════════════════┬═════════════════╝   ╚════════════════┬═════════════════╝
                   │                                      │                                      │                                      │
  ╭────────────────▼─────────────────╮   ╭────────────────▼─────────────────╮   ╭────────────────▼─────────────────╮   ╭────────────────▼─────────────────╮
  │ Δ Decode (Probability Scores)    │   │ Δ Decode (Probability Scores)    │   │ Δ Decode (Probability Scores)    │   │ Δ Decode (Probability Scores)    │
  ╰────────────────┬─────────────────╯   ╰────────────────┬─────────────────╯   ╰────────────────┬─────────────────╯   ╰────────────────┬─────────────────╯
                   │                                      │                                      │                                      │
  ┌────────────────▼─────────────────┐   ┌────────────────▼─────────────────┐   ┌────────────────▼─────────────────┐   ┌────────────────▼─────────────────┐
  │ » Normalized Request             │══╗│ » Intent Core + Gaps             │══╗│ » Plan Step Matrix               │══╗│ » Downstream Route Specification │
  │ » Applied Constraints            │  ║│ » Context Scope Flags            │  ║│ » Latency/Tool Budgets           │  ║│ » Immutable Task Contract        │
  └──────────────────────────────────┘  ║└──────────────────────────────────┘  ║└──────────────────────────────────┘  ║└────────────────┬─────────────────┘
                                        ║                                      ║                                      ║                 │
     (Feeds Forward as Next State) ═════╝   (Feeds Forward as Next State) ═════╝  (Feeds Forward as Next State) ══════╝                 │
                                                                                                                                        │
                                                                                                          (Layer 1 Plan Contract JSON)  │
                                                                                                          [route_hint, query, task_spec]│
                                                                                                                                        ▼
███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
█  [ LAYER 0: EXECUTION / C0 CONTEXT ENGINE ] ── Core Runtime Loop                                                                                        █
█  DOMAINS: Tool Invocation │ C0 Vector Retrieval (Ref Desk) │ External APIs │ Code Execution │ Grounding & Fact Checking                                 █
███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████