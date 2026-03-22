====================================================================================================================================
                 THE ACTUAL PTC VALUE PROP: INFERENCE BATCHING & CONTEXT ISOLATION
====================================================================================================================================

       [ LEFT: TRADITIONAL TOOL CALLING ]              [ RIGHT: PROGRAMMATIC TOOL CALLING (PTC) WITH HITL ADG ]
       (3 Tools = 3 Inference Passes)                (3 Tools = 1 Inference Pass via Script + Safety Gates)
   =======================================        ==================================================================================

   [ L1/L3: INFERENCE PASS 1 ]                    [ L1/L3: SINGLE INFERENCE PASS ]
   - Model requests Tool 1                        - Model writes complete Python/Bash Script
   (Analogy: Researcher asks for 1 book)          (Analogy: Researcher writes a detailed memo of all 3 books needed)
         |                                              | [ gated_by_confidence=37 | routes_path=183 ]
         v                                              | -> IF Low Confidence/Policy-Ambiguous:
   [ L2.2: EXECUTION ]                                  |      route to human (requires_human_review=5)
   - API 1 Executes                                     |      (Analogy: Head Librarian reviews the request memo)
         | (Raw data hits context)                      | -> IF Human Modified (MODIFY_DIFF):
         | (Analogy: Book 1 lands on desk)              |      re-clear via L5 (reenters_safety=11)
         v                                              v
   [ L1/L3: INFERENCE PASS 2 ]                    +======[ L2.2: PTC SANDBOX EXECUTION ]===========================================+
   - Model requests Tool 2                        | [ Lifecycle: enters_sandbox=39 -> freezes_context=5 ]                          |
   (Analogy: Researcher asks for book 2)          | - Python Script Executed Locally                                               |
         |                                        | (Analogy: Librarian goes to a private back-room to find and summarize)         |
         v                                        |                                                                                |
   [ L2.2: EXECUTION ]                            |   -> await query_database(sql_1)                                               |
   - API 2 Executes                               |   -> await query_database(sql_2)                                               |
         | (Raw data hits context)                |   -> await query_database(sql_3)                                               |
         | (Analogy: Desk gets more cluttered)     |                                                                                |
         v                                        |   -> filter + aggregate results                                                |
   [ L1/L3: INFERENCE PASS 3 ]                    |   -> print(summary)                                                            |
   - Model requests Tool 3                        |                                                                                |
   (Analogy: Researcher asks for book 3)          | [ Fail-Closed: Un-transcripted I/O or cap violation triggers                   |
         |                                        |   immediate halt -> escalates_to_human=1182 ]                                  |
         v                                        +================================================================================+
   [ L2.2: EXECUTION ]                                           |
   - API 3 Executes                                              | [ Lifecycle: unfreezes_context=2 ]
         | (Raw data hits context)                               | (ONLY stdout summary sent back)
         | (Analogy: Desk is buried in paper)                    | (Analogy: Librarian returns with only a single index card of notes)
         v                                                       v
   [ L1/L3: FINAL ANSWER ]                        [ L1/L3: FINAL ANSWER ]
   - Generates response based on mess             - Generates response based on summary index card
         |                                                       | [ Learning linkage: builds_dpo_batch=43 ]
         v                                                       | [ produces_preference_pair=13 ]
                                                                 v
   [ TOKEN COST: HIGH ]                           [ VALUE PROP: ~37% LOWER TOKEN COST & HARDENED EXECUTION ]
   - All 3 raw responses pollute context          - Raw tool results stay trapped in L2 Sandbox
   (Analogy: Researcher struggles to read         - Constrained surface enforces freeze -> decision -> re-clear
    through the mountain of books on desk)        - L1 Context window remains unpolluted
                                                  - 1 Inference pass instead of 3
                                                  (Analogy: Researcher’s desk stays clean; only the answer is present)
====================================================================================================================================