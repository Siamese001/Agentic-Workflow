+================================+================================+================================+
| LLM-AS-JUDGE                   | ENSEMBLE MODEL                 | HYBRID                         |
| Eval / Exit Criteria           | Separate LLMs, Pick Best       | Ensemble + Judge Exit          |
+================================+================================+================================+
| CORE QUESTION                  | CORE QUESTION                  | CORE QUESTION                  |
| "Can this output leave?"       | "Which model answer is best?"  | "Which answer is best, and    |
|                                |                                | can it safely leave?"          |
+--------------------------------+--------------------------------+--------------------------------+
| PRIMARY ROLE                   | PRIMARY ROLE                   | PRIMARY ROLE                   |
| Evaluation / governance.       | Generation diversity.          | Generation diversity plus      |
| Checks candidate against       | Produces multiple candidate    | governed evaluation.           |
| rubric, evidence, safety,      | answers from different models  |                                |
| schema, policy, citations,     | or model configs.              |                                |
| and false confidence.          |                                |                                |
+--------------------------------+--------------------------------+--------------------------------+
| FLOWCHART                      | FLOWCHART                      | FLOWCHART                      |
|                                |                                |                                |
| [L2 candidate output]          | [Same task / prompt]           | [Same task / prompt]           |
|          |                     |          |                     |          |                     |
|          v                     |          v                     |          v                     |
| [Evidence + rubric + schema]   | +--------+--------+--------+   | +--------+--------+--------+   |
|          |                     | |Model A |Model B |Model C |   | |Model A |Model B |Model C |   |
|          v                     | +--------+--------+--------+   | +--------+--------+--------+   |
| [LLM Judge at Exit Eval]       |          |                     |          |                     |
|          |                     |          v                     |          v                     |
|          v                     | [Candidate A/B/C outputs]      | [Candidate A/B/C outputs]      |
| [Scorecard / verdict]          |          |                     |          |                     |
|          |                     |          v                     |          v                     |
|          v                     | [Selector / ranker]            | [Selector / ranker]            |
| [X3 disposition]               |          |                     |          |                     |
|          |                     |          v                     |          v                     |
|  +-------+-------+             | [Winner selected]              | [Winner selected]              |
|  |   |   |   |   |             |          |                     |          |                     |
|  v   v   v   v   v             |          v                     |          v                     |
|ALLOW REVISE DENY HITL ABSTAIN  | [Return or pass downstream]    | [Evidence + rubric + schema]   |
|                                |                                |          |                     |
|                                |                                |          v                     |
|                                |                                | [LLM Judge at Exit Eval]       |
|                                |                                |          |                     |
|                                |                                |          v                     |
|                                |                                | [X3 disposition]               |
|                                |                                |          |                     |
|                                |                                |  +-------+-------+             |
|                                |                                |  |   |   |   |   |             |
|                                |                                |  v   v   v   v   v             |
|                                |                                |ALLOW REVISE DENY HITL ABSTAIN  |
+--------------------------------+--------------------------------+--------------------------------+
| WHERE IT BELONGS               | WHERE IT BELONGS               | WHERE IT BELONGS               |
| Exit Eval / X1D / X2 / X3.     | L2 generation or pre-Exit      | L2 generation first, then      |
| Judge evaluates sealed output. | selection.                     | Exit Eval as final authority.  |
+--------------------------------+--------------------------------+--------------------------------+
| WHAT IT MUST NOT DO            | WHAT IT MUST NOT DO            | WHAT IT MUST NOT DO            |
| Must not retrieve new evidence.| Must not become final Exit.    | Must not let selector bypass   |
| Must not execute tools.        | Must not treat majority vote   | Judge / X3.                    |
| Must not write L4.             | as truth.                      | Must not hide losing outputs.  |
| Must not override X3.          | Must not silently swap models. | Must not blur selector vs Exit.|
+--------------------------------+--------------------------------+--------------------------------+
| OUTPUT ARTIFACT                | OUTPUT ARTIFACT                | OUTPUT ARTIFACT                |
| judge_scorecard                | ensemble_selection_record      | ensemble_selection_record      |
| gate_verdict                   | candidate_outputs[]            | candidate_outputs[]            |
| reason_codes[]                 | candidate_hashes[]             | candidate_hashes[]             |
| evidence_refs[]                | selector_rationale             | selector_rationale             |
| confidence                     | winning_candidate_id           | judge_scorecard                |
| abstain_flag                   | loser_retention_refs           | gate_verdict                   |
| remediation_hint               | cost_latency_metrics           | X3 disposition                 |
| X3 disposition                 |                                | full audit trail               |
+--------------------------------+--------------------------------+--------------------------------+
| FAILURE MODE                   | FAILURE MODE                   | FAILURE MODE                   |
| Rubber-stamp judge.            | Polished wrong answer wins.    | Expensive, slow, and messy     |
| UNKNOWN treated as PASS.       | Majority vote amplifies bias.  | unless authority is clean.     |
| Judge invents missing facts.   | Selector hides weak evidence.  | Selector and Judge conflict.   |
+--------------------------------+--------------------------------+--------------------------------+
| BEST USE                       | BEST USE                       | BEST USE                       |
| Groundedness, faithfulness,    | Creative variance, difficult  | High-value outputs where both |
| safety, schema, citation,      | synthesis, model comparison,   | answer quality and governed   |
| policy, completeness checks.   | uncertainty reduction.         | release control matter.        |
+--------------------------------+--------------------------------+--------------------------------+
| SIMPLE MENTAL MODEL            | SIMPLE MENTAL MODEL            | SIMPLE MENTAL MODEL            |
| Court inspector.               | Three consultants draft        | Three consultants draft, then |
| Decides whether work can leave.| answers, then one is picked.   | court inspector decides if    |
|                                |                                | the winner can leave.          |
+================================+================================+================================+