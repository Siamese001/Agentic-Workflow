====================================================================================================================================================================
                                      CONTEXT WINDOW DEGRADATION — THE LIFECYCLE OF MEMORY LOSS
====================================================================================================================================================================

[ ROOT CAUSE NARRATIVE ]
Longer chats do not equal infinite memory. They create token budget pressure, forcing the model to operate on a sliding, 
recency-skewed slice of history. This flowchart illustrates how structural truncation leads to perceived intelligence loss.

⬇ STAGE 1: TOKEN BUDGET PRESSURE & HARD TRUNCATION
│
│ As the conversation expands, early turns hit the context limit and are evicted. 
│ Like a library desk, older books must be returned to the shelf to make room for new ones.
│
├─▶ [ THE LIBRARY DESK / CHAT HISTORY ]
│   Dropped to Shelf (Invisible to Model)                                                Active Context Window (Reading Desk)
│   [ M1 ][ M2 ][ M3 ][ M4 ][ M5 ][ M6 ][ M7 ][ M8 ] ◀ ── HARD BOUNDARY ── ▶ [ M9 ][ M10 ][ M11 ][ M12 ][ M13 ][ M14 ][ M15 ][ M16 ]
│   ❌ Cannot be attended to                                                     ✅ Available for active synthesis
│   ❌ Cannot support chain-of-thought                                           ✅ Can participate in reasoning
│
⬇ STAGE 2: THE VISIBLE UNIVERSE & RECENCY BIAS
│
│ Even within the surviving "Active Context Window," the model's self-attention mechanisms are restricted.
│ Transformers cannot compute what isn't there, and they naturally overweight the most recent tokens.
│
├─▶ [ SELF-ATTENTION LIMITS ]                         ├─▶ [ ATTENTION PROFILE ON DESK ]
│   Missing forever: t1 through t8.                   │   Librarian's eye-line heavily favors the newest books.
│   Only kept tokens (t9-t16) interact:               │
│            t9  t10 t11 t12 t13 t14 t15 t16          │   Older-kept context ──────────────────────────────▶ Most recent
│          ┌─────────────────────────────────┐        │   M9      M10     M11     M12     M13     M14     M15     M16
│   t9     │ ■   ■   ■   ■   ■   ■   ■   ■ │        │   ▁▂▃     ▂▃▄     ▃▄▅     ▄▅▆     ▅▆▇     ▆▇█     ▇██     ███
│   t10    │ ■   ■   ■   ■   ■   ■   ■   ■ │        │    low       slightly stronger      stronger              highest
│   ...    │ ■   ■   ■   ■   ■   ■   ■   ■ │        │
│   t16    │ ■   ■   ■   ■   ■   ■   ■   ■ │        │   Result: Distant setup (M9-M11) is underused unless reintroduced.
│          └─────────────────────────────────┘        │
│
⬇ STAGE 3: INPUT DEGRADATION & REASONING FAILURE
│
│ Because early constraints (M1-M8) are gone, and mid-chat rules (M9-M11) have low attention weight,
│ cross-turn dependencies snap. Multi-step logic breaks.
│
└─▶ [ BROKEN REASONING CHAIN ]
    Ideal Full Chain:
    [Constraint A] ──▶ [Sub-step 1] ──▶ [Sub-step 2] ──▶ [Exception Rule] ──▶ [Final Synthesis]

    Actual State (After Long-Chat Window Loss):
    [Constraint A]     [Sub-step 1]     [Sub-step 2]     [Exception Rule] ──▶ [Final Synthesis]
          ✖                  ✖                 ✖

    Observed outcome:
    - The answer becomes locally plausible but globally inconsistent.
    - The model appears "dumber," but the reality is the input state is degraded.

====================================================================================================================================================================
TRUE CAUSE:  "The model is reasoning over a smaller, recency-skewed, partially degraded slice of history."

ONE-LINER:   Older books fall off the desk, newer books dominate attention, and reasoning chains break because missing 
             premises cannot be reconstructed from nothing.
====================================================================================================================================================================