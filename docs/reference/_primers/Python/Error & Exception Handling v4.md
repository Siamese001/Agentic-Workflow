NORMAL / LAZY EXECUTION                ERROR CASE (PROGRAM CRASH)             BROAD SWALLOW (SILENT SWALLOWER)       INVALID STUB (MASKED ERROR)            NARROW PATTERN (PRECISE EXCEPTIONS)   
====================================== ====================================== ====================================== ====================================== ================================================================

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ PRECISION LADDER                                                                                                                                                                                                       │
│ ================                                                                                                                                                                                                       │
│ Exception                <- worst                                                                                                                                                                                      │
│ broad tuple              <- better                                                                                                                                                                                     │
│ tight domain-specific    <- best                                                                                                                                                                                       │
│                                                                                                                                                                                                                        │
│ WHY:                                                                                                                                                                                                                   │
│ - "Exception" catches almost anything, including real programming bugs.                                                                                                                                                │
│ - "broad tuple" is an improvement because it shrinks the blast radius, but it can still mix together different root causes.                                                                                            │
│ - "tight domain-specific" is strongest because it preserves TRUTH about what failed and enables the right recovery.                                                                                                    │
│                                                                                                                                                                                                                        │
│ LIBRARY ANALOGY:                                                                                                                                                                                                       │
│ - Exception             = librarian says: "Something went wrong somewhere."                                                                                                                                            │
│ - broad tuple           = librarian says: "It was some kind of catalog/shelf/book issue."                                                                                                                              │
│ - tight domain-specific = librarian says: "The book is missing from shelf B7" or "the catalog card is wrong" or "the book is damaged."                                                                                 │
│                                                                                                                                                                                                                        │
│ CORE LESSON:                                                                                                                                                                                                           │
│ The more precisely you name the failure, the more safely you can decide what to do next.                                                                                                                               │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

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
   │                                      ▼                                  ┌────────────────────────────────────┐ ┌────────────────────────────────────┐ ┌────────────────────────────────────────────────────────────────┐
   │                                  PROGRAM CRASH                          │         EXCEPTION HANDLING         │ │          STUB SIMULATION           │ │              EXCEPTION HANDLING PRECISION LADDER               │
   │                                  (Librarian has no desk to              │       (Detection & Catching)       │ │       (Test Double Response)       │ ├────────────────────────────────────────────────────────────────┤
   │                                   report to; they panic and             ├────────────────────────────────────┤ ├────────────────────────────────────┤ │ WORST:                                                         │
   │                                   the entire library shuts              │ except Exception:                  │ │ def find_book(id):                 │ │ except Exception:                                              │
   │                                   down in a total failure)              │                                    │ │   if id == "valid":                │ │   (librarian says only: "something failed")                    │
   │                                                                         │ (librarian catches incident        │ │     return {status: 200}           │ │                                                                │
   │                                                                         │  but hides the TRUTH to avoid      │ │   else:                            │ │ BETTER:                                                        │
   │                                                                         │  consequences or extra work)       │ │     return {status: 200} ❌        │ │ except (ImportError, KeyError, FileNotFoundError):             │
   │                                                                         └─────────────────┬──────────────────┘ │ (ALWAYS returns success!)          │ │   (librarian says: "it was one of a few known library issues") │
   │                                                                                           │                    └─────────────────┬──────────────────┘ │                                                                │
   │                                                                                           │                                      │                    │ BEST:                                                          │
   │                                                                                           │                                      │                    │ except FileNotFoundError:                                      │
   │                                                                                           │                                      │                    │   (book missing from shelf)                                    │
   │                                                                                           │                                      │                    │ except KeyError:                                               │
   │                                                                                           │                                      │                    │   (catalog index entry missing)                                │
   │                                                                                           │                                      │                    │ except ImportError:                                            │
   │                                                                                           │                                      │                    │   (reference manual could not be loaded)                       │
   │                                                                                           │                                      │                    │                                                                │
   │                                                                                           │                                      │                    │ The closer we get to BEST, the more truth is preserved.        │
   │                                                                                           │                                      │                    └────────────────────────────────┬───────────────────────────────┘
   │                                                                                           ▼                                      ▼                                                     ▼                                

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                                WHY PRECISION MATTERS                                                                                                   │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Exception Handling asks: "What exactly failed?"                                                                                                                                                                        │
│ Error Handling asks: "Given that exact failure, what should I do now?"                                                                                                                                                 │
│                                                                                                                                                                                                                        │
│ If the catch is too broad, those two jobs get blurred. The librarian only knows "something is wrong," so the recovery becomes vague, risky, or fake.                                                                   │
│                                                                                                                                                                                                                        │
│ If the catch is precise, the librarian can choose the correct action for the exact problem.                                                                                                                            │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

   │                                                                                           │                                      │                                                     │                                
   │                                                                                           ▼                                      ▼                                                     ▼                                
   │                                                                         ┌────────────────────────────────────┐ ┌────────────────────────────────────┐ ┌────────────────────────────────────────────────────────────────┐
   │                                                                         │           ERROR HANDLING           │ │           ERROR HANDLING           │ │                         ERROR HANDLING                         │
   │                                                                         │       (Reaction & Suppressing)     │ │       (Masked False Positive)      │ │                     (Resolution & Recovery)                    │
   │                                                                         ├────────────────────────────────────┤ ├────────────────────────────────────┤ ├────────────────────────────────────────────────────────────────┤
   │                                      [ THE "FAILED LAZY" LEAK ]         │ The "Silent Swallow" (pass)        │ │ The "Invalid Stub" (always OK)     │ │ ├─ ImportError → flag sys admin                                │
   │                                  ┌────────────────────────────────────► │                                    │ │                                    │ │ ├─ KeyError → fix catalog index                                │
   │                                  │ (Librarian finds mold but            │ (librarian covers their eyes,      │ │ (Test pretends book exists         │ │ ├─ FileNotFound → order new book                               │
   │                                  │  returns empty-handed and            │  shreds the complaint form,        │ │  even when it's missing)           │ │ └─ TimeoutError → retry aisle                                  │
   │                                  │  silent; "Truth" is buried)          │  and silently ignores patron)      │ │                                    │ │                                                                │
   │                                  └────────────────────────────────────┤ │                                    │ │                                    │ │ (librarian consults specific manuals for each issue, fixing    │
   │                                                                         │ [ PRECISION CHECK ]                │ │                                    │ │  the root cause & aiding reader)                               │
   │                                                                         │ except Exception = catches nearly  │ │                                    │ │                                                                │
   │                                                                         │ everything.                        │ │                                    │ │ PRECISION EXAMPLE                                              │
   │                                                                         │                                    │ │                                    │ │                                                                │
   │                                                                         │ except (OSError, ValueError...) =  │ │                                    │ │ except Exception:                                              │
   │                                                                         │ better, but still a mixed bucket.  │ │                                    │ │   return False                                                 │
   │                                                                         │                                    │ │                                    │ │   -> "Something failed. I cannot tell what."                   │
   │                                                                         │ Meaning:                           │ │                                    │ │                                                                │
   │                                                                         │ The system has reduced the danger, │ │                                    │ │ except (OSError, ValueError, KeyError):                        │
   │                                                                         │ but it still may not know the      │ │                                    │ │   return False                                                 │
   │                                                                         │ exact failure story.               │ │                                    │ │   -> "It was likely one of these known categories."            │
   │                                                                         └─────────────────┬──────────────────┘ └─────────────────┬──────────────────┘ │                                                                │
   │                                                                                           │                                      │                    │ except FileNotFoundError:                                      │
   │                                                                                           ▼                                      ▼                    │   return fetch_from_backup()                                   │
   │                                                                         ┌────────────────────────────────────┐ ┌────────────────────────────────────┐ │ except PermissionError:                                        │
   │                                                                         │         GUARDIAN EXCEPTION         │ │         GUARDIAN EXCEPTION         │ │   return escalate_to_admin()                                   │
   │                                                                         │      (Only with HITL approval)     │ │      (Comment cannot fix mask)     │ │ except TimeoutError:                                           │
   │                                                                         ├────────────────────────────────────┤ ├────────────────────────────────────┤ │   return retry_once()                                          │
   │                                                                         │ # guardian: allow-                 │ │ Even if a guardian comment         │ │ except KeyError:                                               │
   │                                                                         │ broad-exception -- specific        │ │ exists here, the test still        │ │   return rebuild_index()                                       │
   │                                                                         │ reason                             │ │ lies about reality                 │ │                                                                │
   │                                                                         │                                    │ │                                    │ │ Meaning:                                                       │
   │                                                                         │ # guardian: allow-                 │ │ Approval is a weak fit because     │ │ - broad tuple is a step in the right direction                 │
   │                                                                         │ silent-swallow -- specific         │ │ truth is masked, not routed        │ │ - domain-specific exceptions are where recovery becomes truly  │
   │                                                                         │ reason                             │ │                                    │ │   intelligent                                                  │
   │                                                                         │                                    │ │ Guardian paperwork over a lie      │ └────────────────────────────────┬───────────────────────────────┘
   │                                                                         │ Only acceptable when:              │ │ is not hardening                   │                                  │
   │                                                                         │ - exact file named                 │ │                                    │                                  ▼
   │                                                                         │ - exact anti-pattern named         │ │ Better fix: make failure real      │ ┌────────────────────────────────────────────────────────────────┐
   │                                                                         │ - specific justification           │ │ and testable                       │ │                       GUARDIAN EXCEPTION                       │
   │                                                                         │ - alternatives rejected            │ │                                    │ │                   (Preferred approved form)                    │
   │                                                                         │ - explicit HITL approval           │ │                                    │ ├────────────────────────────────────────────────────────────────┤
   │                                                                         │ - narrow scope only                │ │                                    │ │ # guardian: allow-broad-exception -- chromadb raises           │
   │                                                                         │                                    │ │                                    │ │ ValueError/KeyError when collection absent                     │
   │                                                                         │ Still risky by default             │ │                                    │ │                                                                │
   │                                                                         │                                    │ │                                    │ │ or                                                             │
   │                                                                         │                                    │ │                                    │ │                                                                │
   │                                                                         └─────────────────┼──────────────────┘ └─────────────────┬──────────────────┘ │ # guardian: allow-silent-swallow -- parser must skip           │
   │                                                                                           │                                      │                    │ unreadable non-Python files during repository scan             │
   │                                                                               [ THE "LEAKY" REGRESSION ]             [ TEST MISLEADS DEVELOPER ]      │                                                                │
   │                                                                         └────◄─────────────────────────────────┘ └────◄───────────────────────────────┘ │ Strong because:                                                │
   │                                                                               (If "precise" is still                 (Developer thinks code handles   │ - exact failure is known                                       │
   ▼                                                                                too broad, it acts                     errors, but tests never         │ - truth stays visible                                          │
CONTINUE PROGRAM                                                                    like this column)                      proved it)                      │ - recovery path is defined                                     │
(system continues normally                                                CONTINUE PROGRAM (UNSAFE STATE)        TEST PASSES (FALSE CONFIDENCE)            │ - scope stays narrow                                           │
 librarian continues assisting                                            (system continues as a zombie          (Test suite shows "all green"             │ - HITL approved                                                │
 patrons seamlessly)                                                       library report shows "0 errors"        but production crashes on missing)       └────────────────────────────────┬───────────────────────────────┘
                                                                           but resource is 'ghosted')                                                                                       │
                                                                                                                                                                                            ▼
                                                                                                                                                                               CONTINUE PROGRAM (SAFE STATE)         
                                                                                                                                                                               (system recovers appropriately,       
                                                                                                                                                                                librarian informs the reader,         
                                                                                                                                                                                safely assists next patron)           

APPROVAL LOGIC INSIDE THE FLOW:
- Column 3 = guardian can sometimes approve a controlled exception, but it is still a compromise
- Column 4 = guardian comment is a poor fit because false success remains false success
- Column 5 = guardian is strongest here because exception type, truth, and recovery are all explicit

ANALOGY: THE LIBRARIAN INCIDENT REPORT

BAD REPORT:
"Library issue happened."
- no one knows whether the book is missing
- or the shelf label is wrong
- or the catalog system is down

BETTER REPORT:
"One of these happened: shelf issue, catalog issue, or book issue."
- useful, but still mixed

BEST REPORT:
"The book is missing from shelf B7."
"The catalog card for this title is missing."
"The archive door is locked."

The better the incident report,
the better the next action.

SIMPLE RULE:
Guardian exception = governance approval for a risky pattern

Best hardening move = push behavior rightward toward precise exceptions. Code diffs must show exception narrowing, not exemption tagging. These are semantic code changes to handlers, not "add guardian comment and keep broad catch."

REAL-WORLD HARDENING (VERIFIED REPLACEMENTS):
Actual replacements shift from the worst tier to better tiers:
except Exception as e:
  → except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as e:

Verified examples in changed files:
- tools/adg/cache/redis_cache.py
- infrastructure/utils/precision_distributed_state.py
- apps_shared/utils/metric_augmenter_util.py

Exception                <- worst
broad tuple              <- better
tight domain-specific    <- best

Why:
- worst = catches too much and hides real bugs
- better = reduces the blast radius
- best = preserves truth and enables the right recovery

MENTAL MODEL

PATRON REQUEST
    ↓
"Please get me this book"
    ↓
BOOK PROBLEM HAPPENS
    ↓
EXCEPTION HANDLING
"What exactly failed?"
- shelf missing book
- wrong catalog entry
- damaged book
- locked archive door
    ↓
ERROR HANDLING
"What should I do about that exact failure?"
- retry
- redirect
- repair index
- escalate
- stop safely

BOTTOM LINE

A broad catch is dangerous because it weakens the first question:
"What exactly failed?"

And when that first answer is vague,
the second answer becomes weak too.

So the hardening path is:

Exception                <- worst
broad tuple              <- better
tight domain-specific    <- best