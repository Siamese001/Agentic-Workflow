┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ THE PRECISION LADDER & LIBRARIAN ANALOGY                                                                               │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ THE LADDER:                                                                                                            │
│ [WORST]  Exception             -> Catches everything, hides real programming bugs.                                     │
│                                   Librarian: "Something went wrong somewhere."                                         │
│ [BETTER] broad tuple           -> Shrinks blast radius, but mixes different root causes.                               │
│                                   Librarian: "It was some kind of catalog/shelf/book issue."                           │
│ [BEST]   tight domain-specific -> Preserves TRUTH about what failed and enables the right recovery.                    │
│                                   Librarian: "The book is missing from shelf B7."                                      │
│                                                                                                                        │
│ MENTAL MODEL (WHY IT MATTERS):                                                                                         │
│ 1. Exception Handling asks: "What exactly failed?" (Shelf missing? Damaged book? Catalog wrong?)                       │
│ 2. Error Handling asks: "Given that exact failure, what should I do?" (Retry? Redirect? Escalate?)                     │
│ -> If the catch is too broad, the first answer is vague, making the recovery risky, fake, or weak.                     │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ FAILURE PATTERNS & INCIDENT RESPONSE MATRIX                                                                            │
├───────────────┬──────────────────────┬────────────────────────┬────────────────────────┬───────────────────────────────┤
│ STATE         │ PROGRAM CRASH        │ SILENT SWALLOW         │ INVALID STUB           │ NARROW PATTERN (BEST)         │
├───────────────┼──────────────────────┼────────────────────────┼────────────────────────┼───────────────────────────────┤
│ Concept       │ Unprotected / Panic  │ Covers eyes / Ignores  │ Pretends it works      │ Knows exactly what to fix     │
│ Handler       │ None                 │ except Exception: pass │ Test double masks code │ tight domain-specific catch   │
│ Truth Status  │ Lost in crash        │ Buried / Suppressed    │ Falsified (Lie)        │ Preserved and routed          │
│ Test Status   │ Fails                │ "Failed Lazy" (Leaks)  │ False Positive Pass    │ Precise & Provable            │
│ Recovery      │ Library shuts down   │ None (Ghosted)         │ Simulated fake fix     │ Exact fix applied (e.g.,      │
│               │                      │                        │                        │ KeyError -> fix index)        │
│ Guardian Fit  │ N/A (cannot bless)   │ Risky (HITL needed)    │ Weak (Don't bless a    │ BEST (allow-<type> + why)     │
│               │                      │                        │ mask over reality)     │                               │
└───────────────┴──────────────────────┴────────────────────────┴────────────────────────┴───────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ APPROVAL LOGIC, GUARDIANS & ACTUAL HARDENING DIFFS                                                                     │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ THE GUARDIAN RULE:                                                                                                     │
│ - Guardian exceptions (e.g., `# guardian: allow-broad-exception`) are governance approvals for risky patterns.         │
│   They are acceptable ONLY with exact file names, exact anti-patterns, justifications, and explicit HITL approval.     │
│ - Guardian paperwork over a lie (like an Invalid Stub) is NOT hardening.                                               │
│                                                                                                                        │
│ THE HARDENING PATH (THE FIX):                                                                                          │
│ - Best hardening move = push behavior rightward toward precise exceptions.                                             │
│ - Code diffs MUST show exception narrowing, NOT exemption tagging.                                                     │
│ - These must be semantic code changes to handlers, not just "add a guardian comment and keep the broad catch."         │
│                                                                                                                        │
│ REAL-WORLD HARDENING (VERIFIED REPLACEMENTS):                                                                          │
│ [OLD] except Exception as e:                                                                                           │
│ [NEW] except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as e:                            │
│                                                                                                                        │
│ Verified examples in changed files:                                                                                    │
│ - tools/adg/cache/redis_cache.py                                                                                       │
│ - infrastructure/utils/precision_distributed_state.py                                                                  │
│ - apps_shared/utils/metric_augmenter_util.py                                                                           │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘