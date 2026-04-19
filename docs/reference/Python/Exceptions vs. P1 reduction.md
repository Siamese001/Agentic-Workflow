================================================================================
||                      P1 REDUCTION TRADEOFF COMPARISON                      ||
================================================================================
+----------------------------------+----------------------------------+
| Path A: P1 FIXED (ROOT CAUSE)    | Path B: P1 EXEMPTED (EXCEPTION)  |
+----------------------------------+----------------------------------+
| [CORE ACTION]                    | [CORE ACTION]                   |
| - Remove anti-pattern            | - Keep pattern, document why    |
| - Redesign flow, tighten bounds   | - Suppress violation from       |
| - Add proper handling/control    |   acting like a failure         |
|                                  |                                  |
| => TRUE CODE IMPROVEMENT         | => METRIC ONLY IMPROVEMENT      |
+----------------------------------+----------------------------------+
| [QUALITY IMPACT]                 | [QUALITY IMPACT]                |
| [CLEANER] Cleaner architecture   | [RISKY] Code still risky        |
| [EASIER] Easier maintenance       | [DEBT] Same debt stays          |
| [FEWER] Fewer defects (future)   | [HARDER] Harder to audit        |
| [LESS] Less reviewer burden      | [MORE] Exception inventory grows |
+----------------------------------+----------------------------------+
| [RISK & VALUE SIGNAL]            | [RISK & VALUE SIGNAL]           |
| [STRONG] Real engineering progress| [WEAK] Policy override, not fix |
|                                  | [UNCLEAR] Reclassification?     |
|                                  | [HIGH] Risk unchanged or hidden  |
+----------------------------------+----------------------------------+
| [MENTAL MODEL]                   | [MENTAL MODEL]                  |
| ? "Did we remove bad patterns?"  | ? "Did we allow more bad        |
|   => YES! (Strong Signal)        |   patterns to stay?"            |
|                                  |   => YES! (Weak Signal)         |
+----------------------------------+----------------------------------+
||                   KEY TRADEOFF SIGNALS                           ||
================================================================================
 P1 DOWN + EXC FLAT/DOWN = Strongest signal of true quality improvement.
 P1 DOWN + EXC UP LGT   = Maybe mixed, needs proof.
 P1 DOWN + EXC UP SIM   = Likely reclassification, not clean progress.
 P1 FLAT + EXC UP       = Quality likely not improving.
================================================================================
||              BEST SCOREBOARD FOR ACTUAL QUALITY                      ||
================================================================================
 P1 FIXED                       -> True Engineering Improvement
 P1 EXEMPTED                    -> Allowed Debt
 P1 RECLASSIFIED                -> Reporting Change
 TEMP EXCEPTIONS RETIRED        -> Strong Positive Signal
 RECURRING EXCS BY MODULE       -> Structural Weakness Signal
 P0 NEW/RESOLVED                -> Critical Safety Signal
================================================================================