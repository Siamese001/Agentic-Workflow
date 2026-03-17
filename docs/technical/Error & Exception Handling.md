NORMAL EXECUTION                      ERROR CASE (PROGRAM CRASH)            BROAD SWALLOW (EXCEPT EXCEPTION)      NARROW PATTERN (PRECISE EXCEPTIONS)
================                      ==========================            ================================      ===================================

try:                                  try: (No handler defined)             try:                                  try:
  run operation                         run operation                         run operation                         run operation
  (system performing task               (system performing task               (system performing task               (system performing task
   │ librarian fetching book)            │ librarian fetching book)            │ librarian fetching book)            │ librarian fetching book)
   │                                     │                                     │                                     │
   ▼                                     ▼                                     ▼                                     ▼
operation runs                        error occurs                          error occurs                          error occurs
   │                                  (Shelf is broken/missing)             (Multiple error types possible)       (Multiple error types possible)
   ▼                                     │                                     │                                     │
SUCCESS (HAPPY PATH)                     ▼                                     │                                     │
(system continues)                    NO EXCEPTION HANDLER                     │                                     │
(librarian finds book                 (No "Help Desk" exists;                  │                                     │
 and gives it to reader)               no one is trained to                    │                                     │
   │                                   receive an incident report)             ▼                                     ▼
   │                                     ▼                                  ┌─────────────────────────────────┐   ┌─────────────────────────────────┐
   │                                  PROGRAM CRASH                         │       EXCEPTION HANDLING        │   │       EXCEPTION HANDLING        │
   │                                  (Librarian has no desk to             │     (Detection & Catching)      │   │      (Detection & Routing)      │
   │                                   report to; they panic and            ├─────────────────────────────────┤   ├─────────────────────────────────┤
   │                                   the entire library shuts             │ except Exception:               │   │ except (ImportError, KeyError,  │
   │                                   down in a total failure)             │                                 │   │         FileNotFoundError):     │
   │                                                                        │ (librarian catches incident     │   │ (librarian catches incident     │
   │                                                                        │  but blindly treats ALL issues  │   │  and identifies EXACT problem)  │
   │                                                                        │  identically, avoiding work)    │   │                                 │
   │                                                                        └────────────────┬────────────────┘   └────────────────┬────────────────┘
   │                                                                                         │                                     │
   │                                                                                         ▼                                     ▼
   │                                                                        ┌─────────────────────────────────┐   ┌─────────────────────────────────┐
   │                                                                        │         ERROR HANDLING          │   │         ERROR HANDLING          │
   │                                                                        │    (Reaction & Suppressing)     │   │     (Resolution & Recovery)     │
   │                                                                        ├─────────────────────────────────┤   ├─────────────────────────────────┤
   │                                                                        │ generic pass / log.error()      │   │ ├─ ImportError → flag sys admin │
   │                                                                        │                                 │   │ ├─ KeyError → fix catalog index │
   │                                                                        │                                 │   │ ├─ FileNotFound → order new book│
   │                                                                        │ (librarian covers their eyes,   │   │ └─ TimeoutError → retry aisle   │
   │                                                                        │  shreds the complaint form,     │   │                                 │
   │                                                                        │  and ignores the patron)        │   │ (librarian consults specific    │
   │                                                                        │                                 │   │  manuals for each issue, fixing │
   │                                                                        │                                 │   │  the root cause & aiding reader)│
   │                                                                        └────────────────┬────────────────┘   └────────────────┬────────────────┘
   │                                                                                         │                                     │
   ▼                                                                                         ▼                                     ▼
CONTINUE PROGRAM                                                            CONTINUE PROGRAM (UNSAFE STATE)       CONTINUE PROGRAM (SAFE STATE)
(system continues normally                                                  (system continues as a zombie         (system recovers appropriately
 librarian continues assisting                                               library report shows "0 errors"       librarian informs the reader,
 patrons seamlessly)                                                         but reader waits eternally in         tracks distinct events, and
                                                                             the lobby for a missing book)         safely assists the next patron)
