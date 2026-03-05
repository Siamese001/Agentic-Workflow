STUB vs SHIM

┌────────────── STUB ──────────────┐   ┌────────────── SHIM ──────────────┐
│ Fake dependency for testing      │   │ Adapter between real systems    │
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

STUB = fake stand-in for a dependency
SHIM = interface translator between real systems

VALID STUB vs INVALID STUB (SIMPLE EXAMPLE)

┌──────────────────── VALID STUB ────────────────────┐   ┌────────────────── INVALID STUB ──────────────────┐
│ Pretends to be the real service correctly          │   │ Pretends badly and hides problems                │
│                                                     │   │                                                   │
│ REAL WORLD                                         │   │ REAL WORLD                                       │
│ Asking a library if a book exists                  │   │ Asking a library if a book exists                │
│                                                     │   │                                                   │
│ STUB BEHAVIOR                                      │   │ STUB BEHAVIOR                                    │
│                                                     │   │                                                   │
│ ask("Moby Dick")                                   │   │ ask("Moby Dick")                                 │
│ → "Book found"                                     │   │ → "Book found"                                   │
│                                                     │   │                                                   │
│ ask("Random Book")                                 │   │ ask("Random Book")                               │
│ → "Not found"                                      │   │ → "Book found"                                   │
│                                                     │   │                                                   │
│ RESULT                                             │   │ RESULT                                           │
│ Program learns how to handle both cases            │   │ Program never learns how to handle missing books │
│ Tests reflect real behavior                        │   │ Tests pass but reality will break                │
└─────────────────────────────────────────────────────┘   └──────────────────────────────────────────────────┘


RULE OF THUMB

If the real world would say "no" sometimes,
your stub must also say "no".
