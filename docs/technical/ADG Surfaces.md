SYSTEM (software platform)                                         library building
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│EXECUTION SURFACE                                                                                                                                              │
│calls                               librarian asking another librarian to perform a task                                                                     │
│invokes_eval                        librarian reading instructions from a paper and executing them                                                           │
│invokes_dynamic                     librarian inventing a procedure on the fly                                                                                │
│invokes_getattr_dynamic (2883)      librarian improvising tasks not listed in the catalog                                                                    │
│(code execution begins here)        librarians begin performing work for readers                                                                             │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                           │ execution may change system state
                                           ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│WRITE SURFACE                                                                                                                                                  │
│writes_to (4659)                    librarian placing a book directly onto a shelf                                                                            │
│writes_through (61)                 librarian required to go through the circulation desk                                                                     │
│execution_terminates_at_uwg (25)    librarian finalizing the update at the official records desk                                                              │
│(system state changes here)         librarians updating bookshelves or catalog entries                                                                       │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                           │ writes require authorization
                                           ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│GOVERNANCE SURFACE                                                                                                                                             │
│references_policy_hash (92)         librarian checking the official rulebook                                                                                  │
│applies_guardrail                   librarian verifying the action follows library policy                                                                    │
│gated_by_confidence                 librarian checking confidence rating before approving                                                                    │
│requires_human_review               senior librarian approval                                                                                                 │
│escalates_to_human                  calling the head librarian for a decision                                                                                 │
│validated_by_registry               verifying the action against the central catalog                                                                         │
│validated_by_llm_gateway            verifying the request through the central intake desk                                                                    │
│(rules enforced here)               librarians ensuring procedures follow the library rulebook                                                               │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                           │ execution may depend on runtime signals
                                           ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│DETERMINISM SURFACE                                                                                                                                            │
│uses_wall_clock (834)               librarian checking the wall clock                                                                                         │
│reads_env (783)                     librarian reading a sticky note left on the desk                                                                         │
│reads_runtime_state (438)           librarian checking the current circulation ledger                                                                        │
│uses_random                         librarian flipping a coin                                                                                                 │
│seeds_rng                           librarian resetting the coin-flip rule                                                                                   │
│patches_time                        librarian adjusting the wall clock                                                                                       │
│guards_replay (28)                  librarian recording every action in the official logbook                                                                 │
│emits_determinism_digest            librarian stamping the log entry with a verification seal                                                                │
│records_execution_trace             librarian writing the full sequence of actions in the archive ledger                                                    │
│(reproducibility risks appear here) librarians relying on clocks, notes, or random choices                                                                   │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                           │ system may access restricted information
                                           ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│SECURITY SURFACE                                                                                                                                               │
│reads_secret (110)                  librarian opening a locked archive cabinet                                                                               │
│accesses_credential (346)           librarian retrieving a master key from the vault                                                                         │
│instruction_injection_source        reader attempting to influence the librarian's instructions                                                              │
│external_http_call                  librarian contacting another library branch                                                                              │
│(sensitive access occurs here)      librarians handling restricted records or external communications                                                        │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
