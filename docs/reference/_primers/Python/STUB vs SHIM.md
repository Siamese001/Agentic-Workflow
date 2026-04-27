====================================================================================================
                            SOFTWARE ABSTRACTION: STUB vs SHIM vs FACADE
====================================================================================================

[STUB] : CONTROLLABLE STAND-IN
Purpose: Replace a volatile dependency to ensure deterministic test environments.
Key Trait: Provides canned, hardcoded responses. Does not trigger real side effects.

[SHIM] : COMPATIBILITY BRIDGE
Purpose: Transparently intercept and redirect calls between two incompatible interfaces.
Key Trait: Structural. It adapts "How to call" without changing "What is done."

┌─────────────── STUB (Testing) ───────────────┐   ┌─────────────── SHIM (Runtime) ───────────────┐
│ System Isolation & Determinism               │   │ API Translation & Interoperability           │
│                                              │   │                                              │
│  [ Your Logic ]                              │   │  [ System A (Caller) ]                       │
│        │                                     │   │          │                                   │
│        ▼ (Interface Call)                    │   │          ▼ (Expected Interface)               │
│  ┌─────────────┐                             │   │  ┌───────────────┐                           │
│  │    STUB     │                             │   │  │     SHIM      │                           │
│  │-------------│                             │   │  │---------------│                           │
│  │ If ID=1:    │                             │   │  │ Map:          │                           │
│  │   Return OK │                             │   │  │ getUser(id)   │                           │
│  │ Else:       │                             │   │  │      ↓        │                           │
│  │   Return ER │                             │   │  │ fetch_user(id)│                           │
│  └─────────────┘                             │   │  └───────────────┘                           │
│        │                                     │   │          │                                   │
│  (Real system  )                             │   │          ▼ (Actual Interface)                │
│  (never touched)                             │   │  [ System B (Provider) ]                     │
│        X                                     │   │                                              │
│    [Database]                                │   │ Both systems are live; shim is the glue.     │
└──────────────────────────────────────────────┘   └──────────────────────────────────────────────┘

----------------------------------------------------------------------------------------------------
                                  BEHAVIORAL FIDELITY: STUBBING
----------------------------------------------------------------------------------------------------
CRITICAL RULE: A stub must mirror the *Contract*, not just the *Success Path*. 
If a stub cannot simulate failure, the code depending on it cannot prove resilience.

┌────────────── VALID STUB ✅ ───────────────┐   ┌────────────── INVALID STUB ❌ ─────────────┐
│ High Fidelity / Handles Edge Cases         │   │ Low Fidelity / Masks Weakness              │
│                                            │   │                                            │
│ SCENARIO: Querying Library Catalog         │   │ SCENARIO: Querying Library Catalog         │
│                                            │   │                                            │
│ Stub Call: find("Valid_Book")              │   │ Stub Call: find("Valid_Book")              │
│ Result: { status: 200, data: [...] }       │   │ Result: { status: 200, data: [...] }       │
│                                            │   │                                            │
│ Stub Call: find("Missing_Book")            │   │ Stub Call: find("Missing_Book")            │
│ Result: { status: 404, error: "None" }     │   │ Result: { status: 200, data: [...] }       │
│                                            │   │                                            │
│ OUTCOME:                                   │   │ OUTCOME:                                   │
│ Logic is forced to handle null/errors.     │   │ Logic assumes data is always present.      │
│ System is "Hardened."                      │   │ System crashes in Production.              │
└────────────────────────────────────────────┘   └────────────────────────────────────────────┘

----------------------------------------------------------------------------------------------------
                     ARCHITECTURAL EVOLUTION: SHIMS vs FACADES
----------------------------------------------------------------------------------------------------
While a SHIM maps 1-to-1 to maintain compatibility, a FACADE simplifies many-to-1 to manage complexity.

  1. ORIGINAL STATE             2. MIGRATION (SHIM)            3. TARGET STATE (FACADE)
  -----------------             -------------------            ------------------------
  [ Callers ]                   [ Callers ]                    [ Callers ]
       │                             │                              │
       ▼                             ▼                              ▼
  [L5_Safety Module]            [L5_Safety SHIM]               [ Unified API FACADE ]
  (Logic lives here)            (Logic moved; shim redirects)  (Stable Entry Point)
                                     │                              │
                                     ▼                              ▼
                                [Base_Agents]                  [Base_Agents] + [Util_Lib]
                                (New Home of Logic)            (Internal complexity hidden)

  STRATEGY:                     STRATEGY:                      STRATEGY:
  Direct coupling.              Temporary bridge.              Abstraction layer. 
  Hard to refactor.             Used to avoid breaking API.    Used to decouple and simplify.
  "Technical Debt"              "Migration Path"               "Architectural Health"
====================================================================================================