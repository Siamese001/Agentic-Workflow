NORMAL / LAZY EXECUTION               ERROR CASE (PROGRAM CRASH)            BROAD SWALLOW (SILENT SWALLOWER)      INVALID STUB (MASKED ERROR)          NARROW PATTERN (PRECISE EXCEPTIONS)
=======================               ==========================            ================================      ===============================      ===================================
[ TIMING: "When do I work?" ]         [ NO HANDLER: "Unprotected" ]         [ TRUTH: "Did it work?" ]             [ TEST: "Can I fail?" ]             [ RECOVERY: "How do I fix it?" ]

try: (The Request)                    try: (No handler defined)             try:                                  try:                                  try:
  if not loaded:                        run operation                         run operation                         run operation                         run operation
     load_resource()                    (system performing task               (system performing task               (system performing task               (system performing task
  (librarian only fetches                │ librarian fetching book)            │ librarian fetching book)            │ librarian fetching book)            │ librarian fetching book)
   book upon request)                    │                                     │                                     │                                     │
   │                                     ▼                                     ▼                                     ▼                                     ▼
   ▼                                  error occurs                          error occurs                          error occurs                          error occurs
operation runs                        (Shelf is broken/missing)             (Manuscript is moldy/destroyed)       (Book is missing)                     (Multiple error types possible)
(Resource is cached)                     │                                     │                                     │                                     │
   ▼                                     ▼                                     │                                     │                                     │
SUCCESS (HAPPY PATH)                  NO EXCEPTION HANDLER                     │                                     │                                     │
(system continues)                    (No "Help Desk" exists;                  │                                     │                                     │
(librarian finds book                  no one is trained to                    │                                     │                                     │
 and gives it to reader)               receive an incident report)             ▼                                     ▼                                     ▼
   │                                     ▼                                  ┌─────────────────────────────────┐   ┌─────────────────────────────────┐   ┌─────────────────────────────────┐
   │                                  PROGRAM CRASH                         │       EXCEPTION HANDLING        │   │       STUB SIMULATION          │   │       EXCEPTION HANDLING        │
   │                                  (Librarian has no desk to             │     (Detection & Catching)      │   │     (Test Double Response)     │   │      (Detection & Routing)      │
   │                                   report to; they panic and            ├─────────────────────────────────┤   ├─────────────────────────────────┤   ├─────────────────────────────────┤
   │                                   the entire library shuts             │ except Exception:               │   │ def find_book(id):               │   │ except (ImportError, KeyError,  │
   │                                   down in a total failure)             │                                 │   │   if id == "valid":             │   │         FileNotFoundError):     │
   │                                                                        │ (librarian catches incident     │   │     return {status: 200}        │   │ (librarian catches incident     │
   │                                                                        │  but hides the TRUTH to avoid   │   │   else:                        │   │  and identifies EXACT problem)  │
   │                                                                        │  consequences or extra work)    │   │     return {status: 200} ❌     │   │                                 │
   │                                                                        └────────────────┬────────────────┘   │ (ALWAYS returns success!)       │   └────────────────┬────────────────┘
   │                                                                                         │                                     │                                     │
   │                                                                                         ▼                                     ▼                                     ▼
   │                                                                        ┌─────────────────────────────────┐   ┌─────────────────────────────────┐   ┌─────────────────────────────────┐
   │                                                                        │         ERROR HANDLING          │   │         ERROR HANDLING          │   │         ERROR HANDLING          │
   │                                                                        │    (Reaction & Suppressing)     │   │    (Masked False Positive)     │   │     (Resolution & Recovery)     │
   │                                                                        ├─────────────────────────────────┤   ├─────────────────────────────────┤   ├─────────────────────────────────┤
   │                                     [ THE "FAILED LAZY" LEAK ]         │ The "Silent Swallow" (pass)     │   │ The "Invalid Stub" (always OK) │   │ ├─ ImportError → flag sys admin │
   │                                   ┌───────────────────────────────────►│                                 │   │                                 │   │ ├─ KeyError → fix catalog index │
   │                                   │ (Librarian finds mold but          │                                 │   │ (Test pretends book exists      │   │ ├─ FileNotFound → order new book│
   │                                   │  returns empty-handed and          │ (librarian covers their eyes,   │   │  even when it's missing)        │   │ └─ TimeoutError → retry aisle   │
   │                                   │  silent; "Truth" is buried)        │  shreds the complaint form,     │   │                                 │   │                                 │
   │                                   └───────────────────────────────────┤  and silently ignores patron)   │   │                                 │   │ (librarian consults specific    │
   │                                                                        │               ▲                 │   │                                 │   │  manuals for each issue, fixing │
   │                                                                        │               │                 │   │                                 │   │  the root cause & aiding reader)│
   │                                                                        └───────────────┼─────────────────┘   └────────────────┬────────────────┘   └────────────────┬────────────────┘
   │                                                                                        │                                      │                                      │
   │                                                                                        │     [ THE "LEAKY" REGRESSION ]       │     [ TEST MISLEADS DEVELOPER ]     │
   │                                                                                        └────◄─────────────────────────────────┘     └────◄──────────────────────────┘
   │                                                                                              (If Column 4 defines "Precise"         (Developer thinks code handles
   │                                                                                               too broadly, it behaves like C3)          errors, but tests never proved it)
   ▼                                                                                         ▼                                     ▼                                     ▼
CONTINUE PROGRAM                                                            CONTINUE PROGRAM (UNSAFE STATE)       TEST PASSES (FALSE CONFIDENCE)       CONTINUE PROGRAM (SAFE STATE)
(system continues normally                                                  (system continues as a zombie         (Test suite shows "all green"         (system recovers appropriately
 librarian continues assisting                                               library report shows "0 errors"       but production crashes on missing)   librarian informs the reader,
 patrons seamlessly)                                                         but resource is 'ghosted')                                                      safely assists next patron)

MENTAL MODEL

PATRON REQUEST
    ↓
"Please get me this book"
    ↓
BOOK PROBLEM HAPPENS
    ↓
EXCEPTION HANDLING
"Ah, I see the exact problem"
(book missing, damaged, wrong catalog entry)
    ↓
ERROR HANDLING
"What should I do about it?"
(retry, reorder, redirect, escalate, stop safely)