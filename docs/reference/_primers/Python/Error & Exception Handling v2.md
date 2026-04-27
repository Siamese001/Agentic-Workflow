NORMAL / LAZY EXECUTION                ERROR CASE (PROGRAM CRASH)             BROAD SWALLOW (SILENT SWALLOWER)       INVALID STUB (MASKED ERROR)            NARROW PATTERN (PRECISE EXCEPTIONS)   
====================================== ====================================== ====================================== ====================================== ======================================
[ TIMING: "When do I work?" ]          [ NO HANDLER: "Unprotected" ]          [ TRUTH: "Did it work?" ]              [ TEST: "Can I fail?" ]                [ RECOVERY: "How do I fix it?" ]      
[ GUARDIAN: none usually ]             [ GUARDIAN: not applicable ]           [ GUARDIAN: risky, rare HITL use ]     [ GUARDIAN: avoid / weak fit ]         [ GUARDIAN: best fit for approval ]   
[ APPROVAL FIT: no exemption ]         [ APPROVAL FIT: missing handling ]     [ APPROVAL FIT: only if justified ]    [ APPROVAL FIT: usually not valid ]    [ APPROVAL FIT: preferred pattern ]   
[ FORMAT: no comment needed ]          [ FORMAT: cannot bless a crash ]       [ FORMAT: allow-<type> + why ]         [ FORMAT: comment does not fix lie ]   [ FORMAT: allow-<type> + why ]        
[ TRUTH: preserved by default ]        [ TRUTH: lost in crash ]               [ TRUTH: often suppressed ]            [ TRUTH: falsified by stub ]           [ TRUTH: preserved and routed ]       
[ HITL: not needed ]                   [ HITL: not relevant ]                 [ HITL: required before adding ]       [ HITL: even approval is weak ]        [ HITL: required before adding ]      

try: (The Request)                     try: (No handler defined)              try:                                   try:                                   try:                                  
  if not loaded:                         run operation                          run operation                          run operation                          run operation                       
     load_resource()                     (system performing task                (system performing task                (system performing task                (system performing task             
  (librarian only fetches                 │ librarian fetching book)             │ librarian fetching book)             │ librarian fetching book)             │ librarian fetching book)         
   book upon request)                     │                                      │                                      │                                      │                                  
   │                                      ▼                                      ▼                                      ▼                                      ▼                                  
   ▼                                  error occurs                           error occurs                           error occurs                           error occurs                       
operation runs                        (Shelf is broken/missing)              (Manuscript is moldy/destroyed)        (Book is missing)                      (Multiple error types possible)    
(Resource is cached)                      │                                      │                                      │                                      │                                  
   ▼                                      ▼                                      │                                      │                                      │                                  
SUCCESS (HAPPY PATH)                  NO EXCEPTION HANDLER                       │                                      │                                      │                                  
(system continues)                    (No "Help Desk" exists;                    │                                      │                                      │                                  
(librarian finds book                  no one is trained to                      │                                      │                                      │                                  
 and gives it to reader)               receive an incident report)               ▼                                      ▼                                      ▼                                  
   │                                      ▼                                  ┌────────────────────────────────────┐ ┌────────────────────────────────────┐ ┌────────────────────────────────────┐
   │                                  PROGRAM CRASH                          │         EXCEPTION HANDLING         │ │          STUB SIMULATION           │ │         EXCEPTION HANDLING         │
   │                                  (Librarian has no desk to              │       (Detection & Catching)       │ │       (Test Double Response)       │ │       (Detection & Routing)        │
   │                                   report to; they panic and             ├────────────────────────────────────┤ ├────────────────────────────────────┤ ├────────────────────────────────────┤
   │                                   the entire library shuts              │ except Exception:                  │ │ def find_book(id):                 │ │ except (ImportError, KeyError,     │
   │                                   down in a total failure)              │                                    │ │   if id == "valid":                │ │           FileNotFoundError):      │
   │                                                                         │ (librarian catches incident        │ │     return {status: 200}           │ │ (librarian catches incident        │
   │                                                                         │  but hides the TRUTH to avoid      │ │   else:                            │ │  and identifies EXACT problem)     │
   │                                                                         │  consequences or extra work)       │ │     return {status: 200} ❌        │ │                                    │
   │                                                                         └─────────────────┬──────────────────┘ │ (ALWAYS returns success!)          │ └─────────────────┬──────────────────┘
   │                                                                                           │                    └─────────────────┬──────────────────┘                   │                    
   │                                                                                           ▼                                      ▼                                      ▼                    
   │                                                                         ┌────────────────────────────────────┐ ┌────────────────────────────────────┐ ┌────────────────────────────────────┐
   │                                                                         │           ERROR HANDLING           │ │           ERROR HANDLING           │ │           ERROR HANDLING           │
   │                                                                         │       (Reaction & Suppressing)     │ │       (Masked False Positive)      │ │      (Resolution & Recovery)       │
   │                                                                         ├────────────────────────────────────┤ ├────────────────────────────────────┤ ├────────────────────────────────────┤
   │                                      [ THE "FAILED LAZY" LEAK ]         │ The "Silent Swallow" (pass)        │ │ The "Invalid Stub" (always OK)     │ │ ├─ ImportError → flag sys admin    │
   │                                  ┌────────────────────────────────────► │                                    │ │                                    │ │ ├─ KeyError → fix catalog index    │
   │                                  │ (Librarian finds mold but            │ (librarian covers their eyes,      │ │ (Test pretends book exists         │ │ ├─ FileNotFound → order new book   │
   │                                  │  returns empty-handed and            │  shreds the complaint form,        │ │  even when it's missing)           │ │ └─ TimeoutError → retry aisle      │
   │                                  │  silent; "Truth" is buried)          │  and silently ignores patron)      │ │                                    │ │                                    │
   │                                  └────────────────────────────────────┤ │                                    │ │                                    │ │ (librarian consults specific       │
   │                                                                         └─────────────────┬──────────────────┘ └─────────────────┬──────────────────┘ │  manuals for each issue, fixing    │
   │                                                                                           │                                      │                    │  the root cause & aiding reader)   │
   │                                                                                           ▼                                      ▼                    └─────────────────┬──────────────────┘
   │                                                                         ┌────────────────────────────────────┐ ┌────────────────────────────────────┐                   │                    
   │                                                                         │         GUARDIAN EXCEPTION         │ │         GUARDIAN EXCEPTION         │                   ▼                    
   │                                                                         │      (Only with HITL approval)     │ │      (Comment cannot fix mask)     │ ┌────────────────────────────────────┐
   │                                                                         ├────────────────────────────────────┤ ├────────────────────────────────────┤ │         GUARDIAN EXCEPTION         │
   │                                                                         │ # guardian: allow-                 │ │ Even if a guardian comment         │ │      (Preferred approved form)     │
   │                                                                         │ broad-exception -- specific        │ │ exists here, the test still        │ ├────────────────────────────────────┤
   │                                                                         │ reason                             │ │ lies about reality                 │ │ # guardian: allow-                 │
   │                                                                         │                                    │ │                                    │ │ broad-exception -- chromadb        │
   │                                                                         │ # guardian: allow-                 │ │ Approval is a weak fit because     │ │ raises ValueError/KeyError         │
   │                                                                         │ silent-swallow -- specific         │ │ truth is masked, not routed        │ │ when collection absent             │
   │                                                                         │ reason                             │ │                                    │ │                                    │
   │                                                                         │                                    │ │ Guardian paperwork over a lie      │ │ or                                 │
   │                                                                         │ Only acceptable when:              │ │ is not hardening                   │ │                                    │
   │                                                                         │ - exact file named                 │ │                                    │ │ # guardian: allow-silent-          │
   │                                                                         │ - exact anti-pattern named         │ │ Better fix: make failure real      │ │ swallow -- parser must skip        │
   │                                                                         │ - specific justification           │ │ and testable                       │ │ unreadable non-Python files        │
   │                                                                         │ - alternatives rejected            │ │                                    │ │ during repository scan             │
   │                                                                         │ - explicit HITL approval           │ │                                    │ │                                    │
   │                                                                         │ - narrow scope only                │ │                                    │ │ Strong because:                    │
   │                                                                         │                                    │ │                                    │ │                                    │
   │                                                                         │ Still risky by default             │ │                                    │ │ - exact failure is known           │
   │                                                                         │                                    │ │                                    │ │ - truth stays visible              │
   │                                                                         │                                    │ │                                    │ │ - recovery path is defined         │
   │                                                                         └─────────────────┼──────────────────┘ └─────────────────┬──────────────────┘ │ - scope stays narrow               │
   │                                                                                           │                                      │                    │ - HITL approved                    │
   │                                                                               [ THE "LEAKY" REGRESSION ]             [ TEST MISLEADS DEVELOPER ]      └─────────────────┬──────────────────┘
   │                                                                         └────◄─────────────────────────────────┘ └────◄───────────────────────────────┘                   │                    
   │                                                                               (If "precise" is still                 (Developer thinks code handles                       ▼                    
   ▼                                                                                too broad, it acts                     errors, but tests never            CONTINUE PROGRAM (SAFE STATE)         
CONTINUE PROGRAM                                                                    like this column)                      proved it)                         (system recovers appropriately,       
(system continues normally                                                CONTINUE PROGRAM (UNSAFE STATE)        TEST PASSES (FALSE CONFIDENCE)         librarian informs the reader,         
 librarian continues assisting                                            (system continues as a zombie          (Test suite shows "all green"          safely assists next patron)           
 patrons seamlessly)                                                       library report shows "0 errors"        but production crashes on missing)                                          
                                                                           but resource is 'ghosted')                                                                                         

APPROVAL LOGIC INSIDE THE FLOW:
- Column 3 = guardian can sometimes approve a controlled exception, but it is still a compromise
- Column 4 = guardian comment is a poor fit because false success remains false success
- Column 5 = guardian is strongest here because exception type, truth, and recovery are all explicit

SIMPLE RULE:
Guardian exception = governance approval for a risky pattern
Best hardening move = push behavior rightward toward precise exceptions

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