NORMAL / LAZY EXECUTION               ERROR CASE (PROGRAM CRASH)            BROAD SWALLOW (SILENT SWALLOWER)      NARROW PATTERN (PRECISE EXCEPTIONS)
=======================               ==========================            ================================      ===================================
[ TIMING: "When do I work?" ]         [ NO HANDLER: "Unprotected" ]         [ TRUTH: "Did it work?" ]             [ RECOVERY: "How do I fix it?" ]

try: (The Request)                    try: (No handler defined)             try:                                  try:
  if not loaded:                        run operation                         run operation                         run operation
     load_resource()                    (system performing task               (system performing task               (system performing task
  (librarian only fetches                │ librarian fetching book)            │ librarian fetching book)            │ librarian fetching book)
   book upon request)                    │                                     │                                     │
   │                                     ▼                                     ▼                                     ▼
   ▼                                  error occurs                          error occurs                          error occurs
operation runs                        (Shelf is broken/missing)             (Manuscript is moldy/destroyed)       (Multiple error types possible)
(Resource is cached)                     │                                     │                                     │
   ▼                                     ▼                                     │                                     │
SUCCESS (HAPPY PATH)                  NO EXCEPTION HANDLER                     │                                     │
(system continues)                    (No "Help Desk" exists;                  │                                     │
(librarian finds book                  no one is trained to                    │                                     │
 and gives it to reader)               receive an incident report)             ▼                                     ▼
   │                                     ▼                                  ┌─────────────────────────────────┐   ┌─────────────────────────────────┐
   │                                  PROGRAM CRASH                         │       EXCEPTION HANDLING        │   │       EXCEPTION HANDLING        │
   │                                  (Librarian has no desk to             │     (Detection & Catching)      │   │      (Detection & Routing)      │
   │                                   report to; they panic and            ├─────────────────────────────────┤   ├─────────────────────────────────┤
   │                                   the entire library shuts             │ except Exception:               │   │ except (ImportError, KeyError,  │
   │                                   down in a total failure)             │                                 │   │         FileNotFoundError):     │
   │                                                                        │ (librarian catches incident     │   │ (librarian catches incident     │
   │                                                                        │  but hides the TRUTH to avoid   │   │  and identifies EXACT problem)  │
   │                                                                        │  consequences or extra work)    │   │                                 │
   │                                                                        └────────────────┬────────────────┘   └────────────────┬────────────────┘
   │                                                                                         │                                     │
   │                                                                                         ▼                                     ▼
   │                                                                        ┌─────────────────────────────────┐   ┌─────────────────────────────────┐
   │                                                                        │         ERROR HANDLING          │   │         ERROR HANDLING          │
   │                                                                        │    (Reaction & Suppressing)     │   │     (Resolution & Recovery)     │
   │                                                                        ├─────────────────────────────────┤   ├─────────────────────────────────┤
   │                                     [ THE "FAILED LAZY" LEAK ]         │ The "Silent Swallow" (pass)     │   │ ├─ ImportError → flag sys admin │
   │                                   ┌───────────────────────────────────►│                                 │   │ ├─ KeyError → fix catalog index │
   │                                   │ (Librarian finds mold but          │                                 │   │ ├─ FileNotFound → order new book│
   │                                   │  returns empty-handed and          │ (librarian covers their eyes,   │   │ └─ TimeoutError → retry aisle   │
   │                                   │  silent; "Truth" is buried)        │  shreds the complaint form,     │   │                                 │
   │                                   └───────────────────────────────────┤  and silently ignores patron)   │   │ (librarian consults specific    │
   │                                                                        │               ▲                 │   │  manuals for each issue, fixing │
   │                                                                        │               │                 │   │  the root cause & aiding reader)│
   │                                                                        └───────────────┼─────────────────┘   └────────────────┬────────────────┘
   │                                                                                        │                                      │
   │                                                                                        │     [ THE "LEAKY" REGRESSION ]       │
   │                                                                                        └────◄─────────────────────────────────┘
   │                                                                                              (If Column 4 defines "Precise"
   │                                                                                               too broadly, it behaves like C3)
   ▼                                                                                         ▼                                     ▼
CONTINUE PROGRAM                                                            CONTINUE PROGRAM (UNSAFE STATE)       CONTINUE PROGRAM (SAFE STATE)
(system continues normally                                                  (system continues as a zombie         (system recovers appropriately
 librarian continues assisting                                               library report shows "0 errors"       librarian informs the reader,
 patrons seamlessly)                                                         but resource is 'ghosted')            safely assists next patron)
