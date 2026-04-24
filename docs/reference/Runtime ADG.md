Bottom line: **OTEL is the breadcrumb stream, but runtime ADG also needs identity, topology, state, evidence, policy, replay, cost, and commit concepts to become a real execution graph.**

```text id="mcp0m7"
┌──────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                         RUNTIME ADG CONCEPTS BEYOND OTEL SPANS                                      │
│                                                                                                      │
│ OTEL tells you: "what happened, when, and under which traceID?"                                      │
│ Runtime ADG also asks: "what was allowed, connected, read, written, proven, retried, and learned?"  │
└──────────────────────────────────────────────────────────────────────────────────────────────────────┘

[ LIVE AGENTIC RUN ]
        │
        ▼
┌──────────────────────┐
│ 1. RUN IDENTITY       │
│ run_id                │
│ session_id            │
│ request_id            │
│ trace_id              │
│ replay_key            │
└──────────┬───────────┘
           │
           │ answers: "Which execution is this?"
           ▼
┌──────────────────────┐
│ 2. TOPOLOGY           │
│ node_id               │
│ parent_id             │
│ edge_type             │
│ step_order            │
│ branch / join         │
└──────────┬───────────┘
           │
           │ answers: "How did runtime steps connect?"
           ▼
┌──────────────────────┐
│ 3. LAYER / AGENT MAP  │
│ U0 / L1 / L0 / L3     │
│ C0 / PA / L2 / Exit   │
│ UWG / L4 / L6         │
│ agent_name            │
│ component_name        │
└──────────┬───────────┘
           │
           │ answers: "Which layer or agent did the work?"
           ▼
┌──────────────────────┐
│ 4. ROUTE CONTRACT     │
│ selected_route        │
│ reason_codes          │
│ confidence            │
│ risk_tier             │
│ freshness class       │
└──────────┬───────────┘
           │
           │ answers: "Why did L0 choose this path?"
           ▼
┌──────────────────────┐
│ 5. STEP CONTRACT      │
│ task_spec             │
│ tool_spec             │
│ input_schema          │
│ output_schema         │
│ success_condition     │
│ max_turns / budget    │
└──────────┬───────────┘
           │
           │ answers: "What was this step allowed to do?"
           ▼
┌──────────────────────┐
│ 6. CAPABILITY STATE   │
│ capability_token      │
│ allowed_tools         │
│ allowed_models        │
│ sandbox_scope         │
│ network_scope         │
│ fs_scope              │
└──────────┬───────────┘
           │
           │ answers: "What powers were granted?"
           ▼
┌──────────────────────┐
│ 7. DATA LINEAGE       │
│ source_ids            │
│ chunk_ids             │
│ evidence_ids          │
│ artifact_ids          │
│ prompt_hash           │
│ output_hash           │
└──────────┬───────────┘
           │
           │ answers: "What did it read or produce?"
           ▼
┌──────────────────────┐
│ 8. RETRIEVAL STATE    │
│ query_vec id          │
│ index_version         │
│ retrieval_mode        │
│ top_k / threshold     │
│ rerank score          │
│ support score         │
└──────────┬───────────┘
           │
           │ answers: "How did C0 find evidence?"
           ▼
┌──────────────────────┐
│ 9. MODEL INVOCATION   │
│ model_id              │
│ provider              │
│ temperature           │
│ prompt_tokens         │
│ output_tokens         │
│ latency_ms            │
│ stop_reason           │
└──────────┬───────────┘
           │
           │ answers: "Which model ran and how?"
           ▼
┌──────────────────────┐
│ 10. TOOL INVOCATION   │
│ tool_name             │
│ args_hash             │
│ return_code           │
│ stdout_hash           │
│ stderr_hash           │
│ side_effect_class     │
└──────────┬───────────┘
           │
           │ answers: "Which tool ran and what happened?"
           ▼
┌──────────────────────┐
│ 11. MUTATION INTENT   │
│ proposed_diff         │
│ mutation_type         │
│ write_target          │
│ write_auth            │
│ commit_request_id     │
└──────────┬───────────┘
           │
           │ answers: "Was this trying to change state?"
           ▼
┌──────────────────────┐
│ 12. UWG / L4 COMMIT   │
│ commit_id             │
│ ledger_hash           │
│ before_hash           │
│ after_hash            │
│ rollback_ref          │
│ alias_swap            │
└──────────┬───────────┘
           │
           │ answers: "Did real ink hit the archive?"
           ▼
┌──────────────────────┐
│ 13. POLICY EVIDENCE   │
│ policy_hash           │
│ compliance_hash       │
│ guardrail_result      │
│ violation_code        │
│ HITL_required         │
│ HITL_decision         │
└──────────┬───────────┘
           │
           │ answers: "Was this allowed?"
           ▼
┌──────────────────────┐
│ 14. REPLAY SURFACE    │
│ snapshot_id           │
│ seed                  │
│ deterministic_clock   │
│ environment_hash      │
│ dependency_versions   │
│ replay_digest         │
└──────────┬───────────┘
           │
           │ answers: "Can we reproduce this run?"
           ▼
┌──────────────────────┐
│ 15. ERROR / HEALING   │
│ error_code            │
│ retry_count           │
│ repair_count          │
│ healing_tier          │
│ parent_attempt_id     │
│ terminal_class        │
└──────────┬───────────┘
           │
           │ answers: "What broke, was it repaired, and how?"
           ▼
┌──────────────────────┐
│ 16. EVAL SIGNALS      │
│ groundedness          │
│ citation_support      │
│ task_completion       │
│ trajectory_score      │
│ drift_flags           │
│ abstain_correctness   │
└──────────┬───────────┘
           │
           │ answers: "Was the outcome good?"
           ▼
┌──────────────────────┐
│ 17. COST / BUDGET     │
│ token_cost            │
│ tool_cost             │
│ wall_time_ms          │
│ budget_remaining      │
│ timeout_status        │
│ throttle_status       │
└──────────┬───────────┘
           │
           │ answers: "Was it efficient and within budget?"
           ▼
┌──────────────────────┐
│ 18. LEARNING SIGNAL   │
│ RCA_id                │
│ pattern_id            │
│ promotion_candidate   │
│ approved_update_id    │
│ future_run_only flag  │
└──────────┬───────────┘
           │
           │ answers: "What should improve next time?"
           ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    RUNTIME ADG RECORD                                                 │
│                                                                                                      │
│ node = agent/component/step/artifact/policy/evidence/commit                                           │
│ edge = calls / reads / routes_to / emits / validates / proposes / commits / blocks / retries / learns │
│                                                                                                      │
│ OTEL span is one source of runtime graph edges.                                                       │
│ Runtime ADG is the richer graph built from spans + contracts + artifacts + policy + replay + commits.│
└──────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

A compact way to say it:

```text
OTEL span        = execution breadcrumb
traceID          = runtime thread
runtime ADG node = meaningful runtime object
runtime ADG edge = relationship between runtime objects
runtime ADG      = reconstructed execution graph with proof, policy, lineage, and replay
```

The key distinction: **OTEL is observability data. Runtime ADG is operational truth reconstruction.**
