====================================================================================================
                                 STUB vs SHIM vs FACADE
====================================================================================================

STUB = fake stand-in for a dependency
SHIM = interface translator between real systems

┌────────────── STUB ──────────────┐   ┌────────────── SHIM ──────────────┐
│ Fake dependency for testing      │   │ Adapter between real systems     │
│                                  │   │                                  │
│  Your Code                       │   │  System A                        │
│      │                           │   │      │                           │
│      ▼                           │   │      ▼                           │
│  ┌───────────┐                   │   │  ┌───────────┐                   │
│  │ Function  │                   │   │  │   SHIM    │                   │
│  │  Under    │                   │   │  │-----------│                   │
│  │   Test    │                   │   │  │translate  │                   │
│  └─────┬─────┘                   │   │  │getUser(id)│                   │
│        │                         │   │  │     ↓     │                   │
│        ▼                         │   │  │fetch_user │                   │
│  ┌───────────────┐               │   │  │(user_id)  │                   │
│  │     STUB      │               │   │  └─────┬─────┘                   │
│  │---------------│               │   │        │                         │
│  │fake response  │               │   │        ▼                         │
│  │return test    │               │   │     System B                     │
│  │data only      │               │   │                                  │
│  └───────────────┘               │   │Both systems are real; shim       │
│        │                         │   │only adapts the interface         │
│   (real system                   │   │                                  │
│    not used)                     │   │Example translation:              │
│        ▼                         │   │getUser(id) → fetch_user(user_id) │
│     Database                     │   │                                  │
└──────────────────────────────────┘   └──────────────────────────────────┘

----------------------------------------------------------------------------------------------------
                               VALID STUB vs INVALID STUB
----------------------------------------------------------------------------------------------------
RULE OF THUMB: If the real world would say "no" sometimes, your stub must also say "no".

┌──────────────────── VALID STUB ────────────────────┐   ┌────────────────── INVALID STUB ──────────────────┐
│ Pretends to be the real service correctly          │   │ Pretends badly and hides problems                │
│                                                    │   │                                                  │
│ REAL WORLD                                         │   │ REAL WORLD                                       │
│ Asking a library if a book exists                  │   │ Asking a library if a book exists                │
│                                                    │   │                                                  │
│ STUB BEHAVIOR                                      │   │ STUB BEHAVIOR                                    │
│                                                    │   │                                                  │
│ ask("Moby Dick")                                   │   │ ask("Moby Dick")                                 │
│ → "Book found"                                     │   │ → "Book found"                                   │
│                                                    │   │                                                  │
│ ask("Random Book")                                 │   │ ask("Random Book")                               │
│ → "Not found"                                      │   │ → "Book found"                                   │
│                                                    │   │                                                  │
│ RESULT                                             │   │ RESULT                                           │
│ Program learns how to handle both cases            │   │ Program never learns how to handle missing books │
│ Tests reflect real behavior                        │   │ Tests pass but reality will break                │
└────────────────────────────────────────────────────┘   └──────────────────────────────────────────────────┘

----------------------------------------------------------------------------------------------------
                     ARCHITECTURAL EVOLUTION: SHIMS vs FACADES
----------------------------------------------------------------------------------------------------

ORIGINAL (single location)                 TEMP SHIM (remove later)                    PERMANENT FACADE (keep)
───────────────────────────               ────────────────────────────                 ────────────────────────────

callers                                   callers                                     many subsystems
import L5_safety.decorators_util           import L5_safety.decorators_util            import safety.api
        │                                           │                                           │
        ▼                                           ▼                                           ▼
L5_safety.decorators_util                  L5_safety.decorators_util                    safety/api.py
(real implementation)                      (SHIM: re-export only)                      (stable public interface)
                                           from base_agents.decorators                  defines approved surface
                                                    │                                           │
                                                    ▼                                           ▼
                                           base_agents.decorators                        internal implementations
                                           (real implementation)                         base_agents.decorators
                                                                                         utils.decorators
                                                                                         other internals


END STATE:                                 END STATE:                                   END STATE:
Single module holds logic                  Migrate callers → delete shim                Keep facade stable
                                                                                        Swap internals safely
====================================================================================================