==================================================================================================
                 THE ACTUAL PTC VALUE PROP: INFERENCE BATCHING & CONTEXT ISOLATION
==================================================================================================

       [ LEFT: TRADITIONAL TOOL CALLING ]              [ RIGHT: PROGRAMMATIC TOOL CALLING (PTC) ]
       (3 Tools = 3 Inference Passes)                (3 Tools = 1 Inference Pass via Script)
   =======================================        ================================================

   [ L1/L3: INFERENCE PASS 1 ]                    [ L1/L3: SINGLE INFERENCE PASS ]
   - Model requests Tool 1                        - Model writes complete Python/Bash Script
          |                                              |
          v                                              v
   [ L2.2: EXECUTION ]                            +======[ L2.2: PTC SANDBOX EXECUTION ]=========+
   - API 1 Executes                               | - Python Script Executed Locally             |
          | (Raw data hits context)               |                                              |
          v                                       |   -> await query_database(sql_1)             |
   [ L1/L3: INFERENCE PASS 2 ]                    |   -> await query_database(sql_2)             |
   - Model requests Tool 2                        |   -> await query_database(sql_3)             |
          |                                       |                                              |
          v                                       |   -> filter + aggregate results              |
   [ L2.2: EXECUTION ]                            |   -> print(summary)                          |
   - API 2 Executes                               +==============================================+
          | (Raw data hits context)                              |
          v                                                      | (ONLY stdout summary sent back)
   [ L1/L3: INFERENCE PASS 3 ]                                   |
   - Model requests Tool 3                                       v
          |                                       [ L1/L3: FINAL ANSWER ]
          v                                       - Generates response based on summary
   [ L2.2: EXECUTION ]                                           |
   - API 3 Executes                                              v
          | (Raw data hits context)               [ VALUE PROP: ~37% LOWER TOKEN COST ]
          v                                       - Raw tool results stay trapped in L2 Sandbox
   [ L1/L3: FINAL ANSWER ]                        - L1 Context window remains unpolluted
          |                                       - 1 Inference pass instead of 3
          v
   [ TOKEN COST: HIGH ]
   - All 3 raw responses pollute context
