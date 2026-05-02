====================================================================================================================
                    LLM-AS-JUDGE vs ENSEMBLE LLMs vs HYBRID
                    ONE-PAGE HIGH-SIGNAL FLOWCHART
====================================================================================================================

BOTTOM LINE
LLM-as-Judge is semantic quality control.
Ensemble LLMs are candidate generation.
Hybrid uses both, but Exit still owns final authority.


====================================================================================================================
                                       THREE-LANE VIEW
====================================================================================================================

┌──────────────────────────────────┐   ┌──────────────────────────────────┐   ┌──────────────────────────────────┐
│ 1. LLM-AS-JUDGE                  │   │ 2. ENSEMBLE LLMs                 │   │ 3. HYBRID                         │
│ Semantic evaluator               │   │ Multiple generators              │   │ Ensemble + semantic judge          │
└──────────────────────────────────┘   └──────────────────────────────────┘   └──────────────────────────────────┘

Core question:                         Core question:                         Core question:
"Does this satisfy the rubric,          "Can multiple models produce better     "Which candidate is strongest,
evidence, policy, schema, and           candidate answers than one model?"      and can it pass governed review?"
safety requirements?"

        │                                      │                                      │
        ▼                                      ▼                                      ▼

┌──────────────────────────────────┐   ┌──────────────────────────────────┐   ┌──────────────────────────────────┐
│ Candidate output / packet        │   │ Same task / same prompt           │   │ Same task / same prompt           │
│                                  │   │                                  │   │                                  │
│ Example:                         │   │ Sent to:                         │   │ Sent to:                         │
│ - answer draft                   │   │ - Model A                        │   │ - Model A                        │
│ - tool result                    │   │ - Model B                        │   │ - Model B                        │
│ - evidence packet                │   │ - Model C                        │   │ - Model C                        │
│ - prompt artifact                │   │                                  │   │                                  │
└──────────────────────────────────┘   └──────────────────────────────────┘   └──────────────────────────────────┘
        │                                      │                                      │
        ▼                                      ▼                                      ▼

┌──────────────────────────────────┐   ┌──────────────────────────────────┐   ┌──────────────────────────────────┐
│ Deterministic checks first       │   │ Candidate generation              │   │ Candidate generation              │
│                                  │   │                                  │   │                                  │
│ Checks hard invariants:          │   │ Outputs:                         │   │ Outputs:                         │
│ - schema valid                   │   │ - candidate_outputs[]             │   │ - candidate_outputs[]             │
│ - required fields present        │   │ - candidate_hashes[]              │   │ - candidate_hashes[]              │
│ - hashes match                   │   │ - model_ids[]                     │   │ - model_ids[]                     │
│ - policy refs valid              │   │ - prompt_hash                     │   │ - prompt_hash                     │
│ - registry refs valid            │   │ - cost_latency_metrics            │   │ - cost_latency_metrics            │
│ - citation IDs resolve           │   │                                  │   │ - loser_retention_refs[]          │
│ - capability scope valid         │   │                                  │   │                                  │
│ - no direct L4 write             │   │                                  │   │                                  │
└──────────────────────────────────┘   └──────────────────────────────────┘   └──────────────────────────────────┘
        │                                      │                                      │
        ▼                                      ▼                                      ▼

┌──────────────────────────────────┐   ┌──────────────────────────────────┐   ┌──────────────────────────────────┐
│ LLM-as-Judge                     │   │ Selector / ranker                 │   │ Selector / ranker                 │
│                                  │   │                                  │   │                                  │
│ Evaluates meaning:               │   │ Picks strongest draft.            │   │ Picks strongest draft.            │
│ - groundedness                   │   │                                  │   │                                  │
│ - faithfulness                   │   │ Must record:                     │   │ Must record:                     │
│ - completeness                   │   │ - winning_candidate_id            │   │ - winning_candidate_id            │
│ - contradiction handling         │   │ - selector_rationale              │   │ - selector_rationale              │
│ - false confidence               │   │ - loser_retention_refs[]          │   │ - loser_retention_refs[]          │
│ - citation support               │   │                                  │   │                                  │
│ - safety fit                     │   │ Critical:                         │   │ Critical:                         │
│ - repairability                  │   │ Selector is not Judge.            │   │ Selector is not Judge.            │
│                                  │   │ Majority vote is not truth.       │   │ Majority vote is not truth.       │
└──────────────────────────────────┘   └──────────────────────────────────┘   └──────────────────────────────────┘
        │                                      │                                      │
        ▼                                      ▼                                      ▼

┌──────────────────────────────────┐   ┌──────────────────────────────────┐   ┌──────────────────────────────────┐
│ Judge artifact                   │   │ Selected candidate                │   │ Deterministic checks              │
│                                  │   │                                  │   │                                  │
│ Emits:                           │   │ Can pass downstream, but          │   │ Checks hard invariants before     │
│ - judge_scorecard                │   │ this is not final governance.     │   │ semantic judging:                 │
│ - gate_verdict                   │   │                                  │   │ - schema                          │
│ - reason_codes[]                 │   │ Ensemble alone does not replace:  │   │ - hashes                          │
│ - evidence_refs[]                │   │ - Runtime Gates                   │   │ - citations                       │
│ - confidence                     │   │ - LLM-as-Judge                    │   │ - policy refs                     │
│ - abstain_flag                   │   │ - Exit                            │   │ - registry refs                   │
│ - remediation_hint               │   │                                  │   │ - no authority bypass             │
└──────────────────────────────────┘   └──────────────────────────────────┘   └──────────────────────────────────┘
        │                                      │                                      │
        ▼                                      ▼                                      ▼

┌──────────────────────────────────┐   ┌──────────────────────────────────┐   ┌──────────────────────────────────┐
│ Owning gate consumes judge       │   │ Downstream gate or Exit still     │   │ LLM-as-Judge                      │
│ evidence                         │   │ required if release/control       │   │                                  │
│                                  │   │ matters.                          │   │ Evaluates selected candidate:     │
│ Examples:                        │   │                                  │   │ - groundedness                    │
│ - 00C Runtime Gate               │   │ Ensemble output can be useful,    │   │ - evidence support                │
│ - C0 evidence gate               │   │ but it has no final authority.    │   │ - completeness                    │
│ - PA prompt gate                 │   │                                  │   │ - contradiction handling          │
│ - L2 repair gate                 │   │                                  │   │ - false confidence                │
│ - Exit final review              │   │                                  │   │ - citation support                │
│ - L6 shadow eval                 │   │                                  │   │ - safety fit                      │
└──────────────────────────────────┘   └──────────────────────────────────┘   └──────────────────────────────────┘
        │                                                                             │
        ▼                                                                             ▼

┌──────────────────────────────────┐                                      ┌──────────────────────────────────┐
│ If final-release path:            │                                      │ Judge artifact                   │
│ Exit consumes judge evidence      │                                      │                                  │
│ and emits exactly one X3.         │                                      │ Emits:                           │
│                                  │                                      │ - judge_scorecard                │
│ X3 options:                       │                                      │ - gate_verdict                   │
│ - ALLOW                           │                                      │ - reason_codes[]                 │
│ - DENY                            │                                      │ - evidence_refs[]                │
│ - REROUTE                         │                                      │ - confidence                     │
│ - ESCALATE_HITL                   │                                      │ - abstain_flag                   │
│ - COMMIT_REQUEST                  │                                      │ - remediation_hint               │
│ - SAFE_ABSTAIN                    │                                      └──────────────────────────────────┘
└──────────────────────────────────┘                                                   │
                                                                                       ▼
                                                                        ┌──────────────────────────────────┐
                                                                        │ If final-release path:            │
                                                                        │ Exit consumes judge evidence      │
                                                                        │ and emits exactly one X3.         │
                                                                        │                                  │
                                                                        │ X3 options:                       │
                                                                        │ - ALLOW                           │
                                                                        │ - DENY                            │
                                                                        │ - REROUTE                         │
                                                                        │ - ESCALATE_HITL                   │
                                                                        │ - COMMIT_REQUEST                  │
                                                                        │ - SAFE_ABSTAIN                    │
                                                                        └──────────────────────────────────┘


====================================================================================================================
                                      THE CONTROL SPLIT
====================================================================================================================

Deterministic scripts:
- Check objective invariants.
- Best for schema, hashes, required fields, registry refs, policy refs, citation existence, tool scope, no-write rules.

LLM-as-Judge:
- Checks semantic quality.
- Best for groundedness, faithfulness, completeness, contradiction handling, false confidence, citation support,
  safety fit, and repairability.

Ensemble:
- Creates multiple candidate answers.
- Best for generation diversity, hard synthesis, model comparison, and reducing single-model brittleness.

Selector:
- Picks a candidate.
- Does not prove truth.
- Does not replace Judge.
- Does not replace Runtime Gates.
- Does not replace Exit.

Exit:
- Final authority.
- Consumes deterministic checks, judge evidence, runtime gate evidence, and sealed artifacts.
- Emits exactly one X3 disposition.


====================================================================================================================
                                      NON-NEGOTIABLE RULES
====================================================================================================================

1. LLM-as-Judge is not an ensemble.
2. Ensemble is not governance.
3. Selector is not Judge.
4. Majority vote is not truth.
5. Judge can run at any semantic gate, not only Exit.
6. Judge must not retrieve, execute, write L4, or invent missing evidence.
7. UNKNOWN is never PASS.
8. Exit alone owns final X3.
9. Hybrid means: generate alternatives, select candidate, judge candidate, Exit decides.
10. Fort Knox pattern is deterministic checks first, semantic judge second, deterministic aggregation last.


====================================================================================================================
                                      ONE-LINE MEMORY HOOK
====================================================================================================================

Ensemble = more candidate answers.
Judge = semantic quality control.
Selector = chooses one candidate.
Exit = decides whether anything can leave.