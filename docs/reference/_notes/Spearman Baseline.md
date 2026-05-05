SPEARMAN BASELINE IN YOUR AGENTIC CORE SPINE
"Do judge scores rank examples like humans do?"

RUNTIME PATH
============

[ U0 Intake ]
   |
   v
[ L1 Plan ]
   |
   v
[ L0 Route ]
   |
   v
[ C0 Evidence ] -> [ Prompt Assembly ] -> [ L2 Execute ]
                                             |
                                             v
                                      [ Exit / X3 ]
                                      current-run disposition
                                      may consume approved judge reliability
                                      does NOT compute Spearman
                                      does NOT train or promote judge
                                             |
                                             v
                                sealed runtime exhaust
                                             |
                                             v


L6 SHADOW EVALUATION -> FUTURE-RUN LEARNING
===========================================

+---------------------------+   +---------------------------+   +---------------------------+   +---------------------------+
| 6A. INGEST                |-->| 6B. EVALUATE              |-->| 6C. RCA / SYNTH           |-->| 6D. PROMOTE / UPDATE      |
|                           |   |                           |   |                           |   |                           |
| Read sealed exhaust       |   | SPEARMAN LIVES HERE       |   | Explain weak Spearman     |   | UWG-only promotion        |
|                           |   |                           |   |                           |   |                           |
| Inputs:                   |   | Inputs:                   |   | If Spearman is weak:      |   | Only if approved:         |
| - runtime traces          |   | - human-labeled holdout   |   | - diagnose judge drift    |   | - promote judge baseline  |
| - Exit / X3 receipts      |   | - judge scores            |   | - find heuristic mismatch |   | - store Spearman threshold|
| - L2 sealed artifacts     |   | - rubric version          |   | - draft rubric proposal   |   | - store calibration report|
| - HITL packets            |   | - judge version           |   | - draft judge update      |   | - store judge/rubric ver. |
| - UWG receipts            |   |                           |   | - no promotion yet        |   | - publish future-run refs |
|                           |   | Compute:                  |   |                           |   |                           |
| Output:                   |   | - human rank              |   | Output:                   |   | Output:                   |
| - normalized evidence     |   | - judge rank              |   | - RCA packet              |   | - L4 durable baseline     |
| - lineage map             |   | - Spearman correlation    |   | - proposed changes        |   | - rollout surface update  |
| - eval-ready bundle       |   |                           |   | - promotion candidate     |   | - next-run read surface   |
|                           |   | Output:                   |   |                           |   |                           |
| Does NOT compute          |   | - judge_reliability_signal|   | Does NOT write L4         |   | Does NOT affect current   |
| Spearman yet              |   | - calibration_report      |   | Does NOT mutate runtime   |   | completed run             |
|                           |   | - promotion/block rec.    |   |                           |   |                           |
+---------------------------+   +---------------------------+   +---------------------------+   +-------------+-------------+
                                                                                                             |
                                                                                                             v
                                                                                                      [ UWG -> L4 ]


SPEARMAN EXAMPLE INSIDE 6B
==========================

Human labels                    Judge scores
------------                    ------------
A = 0.95  rank 1                A = 0.90  rank 1
B = 0.80  rank 2                C = 0.75  rank 2
C = 0.60  rank 3                B = 0.70  rank 3
D = 0.20  rank 4                D = 0.10  rank 4

Compare ranks, not exact scores:

Human order:   A > B > C > D
Judge order:   A > C > B > D
                    ^   ^
                 B/C swapped

Spearman result:
+1.0  = perfect same ordering
 0.0  = no useful ranking relationship
-1.0  = opposite ordering

6B baseline answers:
"Is this judge good enough at ordering quality like a human?"


DURABLE PROMOTION PATH
======================

[ 6B Evaluate ]
   |
   | judge_reliability_signal
   | calibration_report
   | promotion_or_block_recommendation
   v
[ 6C RCA / Synth ]
   |
   | proposal only if change is needed
   v
[ 6D Promote / Update ]
   |
   | only approved promotion candidates
   v
[ UWG ]
   |
   | only durable write path
   v
[ L4 Durable State ]

L4 stores:
- approved judge baseline
- Spearman threshold
- calibration history
- holdout dataset metadata
- judge version / rubric version
- promotion record


NEXT RUN CONSUMPTION
====================

[ Runtime Gates / Exit ]
reads approved L4 judge reliability baseline

If judge reliability drops:
- mark degraded
- escalate HITL
- block promotion
- prevent judge from being trusted as sole evaluator


PLACEMENT RULE
==============

6A INGEST:
  collect and normalize sealed exhaust only

6B EVALUATE:
  compute Spearman and emit judge calibration signal

6C RCA / SYNTH:
  explain failures and draft proposals only

6D PROMOTE / UPDATE:
  route approved baseline/change through UWG to L4

05 EXIT:
  may consume approved reliability signal
  does NOT compute or recalibrate Spearman