NORMAL EXECUTION                      ERROR CASE (PROGRAM CRASH)            BROAD SWALLOW (EXCEPT EXCEPTION)      NARROW PATTERN (PRECISE EXCEPTIONS)
================                      ==========================            ================================      ===================================

try:                                  try:                                  try:                                  try:
  run operation                         run operation                         run operation                         run operation
  (system performing task               (system performing task               (system performing task               (system performing task
   │ librarian retrieving book)          │ librarian retrieving book)          │ librarian retrieving book)          │ librarian retrieving book)
   │                                     │                                     │                                     │
   ▼                                     ▼                                     ▼                                     ▼
operation runs                        error occurs                          error occurs                          error occurs
   │                                  (FileNotFound / KeyError)             (Multiple error types possible)       (Multiple error types possible)
   ▼                                     │                                     │                                     │
SUCCESS (HAPPY PATH)                     ▼                                     │                                     │
(system continues)                    NO EXCEPTION HANDLER                     │                                     │
(librarian finds book                 (no catch exists                         │                                     │
 and gives it to reader)               │ no desk receives incident)            ▼                                     ▼
   │                                   ▼                                ┌─────────────────────────────────┐   ┌─────────────────────────────────┐
   │                                  PROGRAM CRASH                     │       EXCEPTION HANDLING        │   │       EXCEPTION HANDLING        │
   │                                  (system stops execution           │     (Detection & Catching)      │   │      (Detection & Routing)      │
   │                                   librarian hits a problem         ├─────────────────────────────────┤   ├─────────────────────────────────┤
   │                                   and desk shuts down)             │ except Exception:               │   │ except (ImportError, KeyError,  │
   │                                                                    │                                 │   │         FileNotFoundError):     │
   │                                                                    │ (librarian catches incident     │   │ (librarian catches incident     │
   │                                                                    │  but treats all as equal)       │   │  and identifies specific type)  │
   │                                                                    └────────────────┬────────────────┘   └────────────────┬────────────────┘
   │                                                                                     │                                     │
   │                                                                                     ▼                                     ▼
   │                                                                    ┌─────────────────────────────────┐   ┌─────────────────────────────────┐
   │                                                                    │         ERROR HANDLING          │   │         ERROR HANDLING          │
   │                                                                    │    (Reaction & Suppressing)     │   │     (Resolution & Recovery)     │
   │                                                                    ├─────────────────────────────────┤   ├─────────────────────────────────┤
   │                                                                    │ generic pass / log.error()      │   │ ├─ ImportError → log missing    │
   │                                                                    │                                 │   │ ├─ KeyError → bad catalog entry │
   │                                                                    │ (librarian suppresses the       │   │ ├─ FileNotFound → empty shelf   │
   │                                                                    │  issue, throws in generic bin)  │   │ └─ TimeoutError → retry lookup  │
   │                                                                    └────────────────┬────────────────┘   └────────────────┬────────────────┘
   │                                                                                     │                                     │
   ▼                                                                                     ▼                                     ▼
CONTINUE PROGRAM                                                        CONTINUE PROGRAM (UNSAFE STATE)       CONTINUE PROGRAM (SAFE STATE)
(system continues normally                                              (system continues as a zombie         (system recovers appropriately
 librarian continues assisting                                           library report shows 0 errors         librarian tracks distinct events
 patrons seamlessly)                                                     but reader never got book)            and resolves them properly)
