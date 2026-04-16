======================================================================================================================================
[6] SHADOW EVALUATION + FUTURE-RUN LEARNING
[6] THE BOARD MEETING | AFTER-HOURS REVIEW
======================================================================================================================================
- An asynchronous post-run process that observes sealed outputs, grades outcomes and trajectories, aggregates signals, performs RCA,
  drafts changes, and promotes approved future-run updates through the sole write path.
- The library board meets after hours, reads the complaint box and desk footage, decides what should change for tomorrow, and updates
  the manuals only through the master clerk.

[ CROSS-CUTTING AUTHORITY ]  COMMANDANT = Approver  |  CLERK = Sole Ink Write  |  CLOCK = Evidence Only  |  FLOOR STAFF = Propose Only
[ MUTATION CONSTRAINTS ]     NO Live Patron Impact  |  Future Visits Only      |  Never Bypasses Ledger Clerk

                                                                   │ [ ingest ]
                                                                   ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ TODAY'S VISITOR LOGS + SEALED FOLDERS                                                                                              │
│ completed answers / exit outcomes / sealed outputs / traces / telemetry / HITL packets / commit receipts / human feedback          │
└──────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────┘
                                                                   │ [ observe ]
                                                                   ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ S1 OBSERVABILITY / WATCHING THE TAPES                                                                                              │
│ ┌──────────────────────────────┐ ┌──────────────────────────────┐ ┌──────────────────────────────┐ ┌─────────────────────────────┐ │
│ │ S1A GATHER LOGS              │ │ S1B NORMALIZE EVIDENCE       │ │ S1C REVIEW BUNDLE            │ │ S1D STRICT OBSERVER RULE    │ │
│ │ - telemetry intake           │ │ - align formats              │ │ - seal async eval packet     │ │ - evidence only             │ │
│ │ - exit outcomes              │ │ - preserve lineage           │ │ - no live mutation           │ │ - no patron impact          │ │
│ │ - trace capture              │ │ - correlate dispositions     │ │ - future-run only            │ │ - reads only                │ │
│ └──────────────┬───────────────┘ └──────────────┬───────────────┘ └──────────────┬───────────────┘ └──────────────┬──────────────┘ │
│             [seal]                          [packet]                          [emit]                           [rule]              │
└──────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────┘
                                                                   │ [ grade ]
                                                                   ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ S2 ASYNC EVALUATION / GRADING THE STAFF + FINDING FLAWS                                                                            │
│ ┌──────────────────────────────┐ ┌──────────────────────────────┐ ┌──────────────────────────────┐ ┌─────────────────────────────┐ │
│ │ S2A OUTCOME EVALS            │ │ S2B TRAJECTORY EVALS         │ │ S2C GOVERNANCE REGRESSIONS   │ │ S2D HUMAN CALIBRATION       │ │
│ │ - task completion            │ │ - tool selection / ordering  │ │ - exact match drift          │ │ - SME adjudication          │ │
│ │ - groundedness               │ │ - arg correctness            │ │ - schema / state drift       │ │ - spot checks               │ │
│ │ - citation support           │ │ - retry thrash / budget      │ │ - API drift                  │ │ - grader calibration        │ │
│ │ - abstain correctness        │ │ - policy compliance          │ │ - rubric / grader drift      │ │ - calibrate B/C/D above     │ │
│ │ - escalation correctness     │ │ - trajectory integrity       │ │ - gate regression            │ │                             │ │
│ │ - answer relevance           │ │                              │ │                              │ │                             │ │
│ └──────────────┬───────────────┘ └──────────────┬───────────────┘ └──────────────┬───────────────┘ └──────────────┬──────────────┘ │
│             [score]                          [score]                          [merge]                         [calib]              │
└──────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────┘
                                                                   │ [ cluster ]
                                                                   ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ S3 SIGNAL AGGREGATION / FINDING PATTERNS                                                                                           │
│ ┌──────────────────────────────┐ ┌──────────────────────────────┐ ┌──────────────────────────────┐ ┌─────────────────────────────┐ │
│ │ S3A SCORE BUNDLE             │ │ S3B DECISION TAGS            │ │ S3C BASELINE TAGGING         │ │ S3D CLUSTERING              │ │
│ │ - qualitative metrics        │ │ - drift flags                │ │ - baseline ids               │ │ - repeated failure isolate  │ │
│ │ - quantitative metrics       │ │ - confidence variance        │ │ - data-source tags           │ │ - separate noise            │ │
│ │ - unified score packet       │ │ - severity class             │ │ - comparison anchors         │ │ - candidate patterns        │ │
│ └──────────────┬───────────────┘ └──────────────┬───────────────┘ └──────────────┬───────────────┘ └──────────────┬──────────────┘ │
│             [emit]                           [emit]                           [emit]                           [emit]              │
│                └────────────────────────────────┴───────────────┬────────────────┴────────────────────────────────┘                │
│                                                                 ▼                                                                  │
│                                BUS P: PREF / GRADES             │                BUS T: TELEM / TRACE                              │
└─────────────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────────────────┘
                                                                  │ [ evolve ]
                                                                  ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ S4 SYSTEM LEARNING PIPELINE / KNOWLEDGE EVOLUTION LOOP                                                                             │
│ 1-3. ARCHIVE FREEZE                                                                                                                │
│ - capture patron trails           - freeze rules / limits             - seal source state                                          │
│ - preserve evidence               - clock is evidence only            - produce sealed master archive payload                      │
│                                                                                                                                    │
│ 4. CASE FILE COMPILATION                                                                                                           │
│ - build incident id / time        - attach context / logs             - package RCA packet                                         │
│                                                                                                                                    │
│ 5. INCIDENT INVESTIGATION                                                                                                          │
│ - classify cause                  - map failure flow                  - separate weak signal from stable trend                     │
│                                                                                                                                    │
│ 6. RULE DRAFTING                                                                                                                   │
│ - derive fix target               - structure improvements            - controls / rollback                                        │
│ - floor staff propose only        - no live changes                   - destination class prepared                                 │
│                                                                                                                                    │
│ 7. COMMANDANT'S GAUNTLET                                                                                                           │
│ - shadow replay                   - regression checks                 - safety validation                                          │
│ - SME sign-off                    - promotion readiness               - sovereign approve / veto                                   │
│                                                                                                                                    │
│ 8. KNOWLEDGE EXTRACTION                                                                                                            │
│ - classify destination type       - route to rubric / desk rules / catalog / priors                                                │
│ - not every approved learning artifact goes to the same surface                                                                    │
└─────────────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────────────────┘
                                                                  │
                                           ┌──────────────────────┴──────────────────────┐
                                        [ hold ]                                    [ approve ]
                                           ▼                                             ▼
                            ┌──────────────────────────────┐              ┌──────────────────────────────────────────────────────────┐
                            │ OBSERVATION ONLY / REJECT    │              │ PROMOTION PACKET                                         │
                            │ - no future-run change       │              │ - versioned change / rationale / rollout metadata        │
                            │ - keep notes only            │              │ - edition_id / rollout band / destination class          │
                            └──────────────────────────────┘              └──────────────┬───────────────────────────────────────────┘
                                                                                         │ [ commit ]
                                                                                         ▼
┌────────────────────────────────────────────────────────────────────────────────────────┴───────────────────────────────────────────┐
│ MASTER LEDGER COMMIT / UNIVERSAL WRITE GATE                                                                                        │
│ - sole write path for future-run improvements                                                                                      │
│ - verify manager stamps / clerk gate / allowed promotion                                                                           │
│ - durable write into L4 archive                                                                                                    │
│ - read-surface materialization, alias swap, and overnight rollout                                                                  │
│ - publish BUS U evolution updates to rubric baselines, desk rules, catalog refs, and reason priors                                 │
│ invariant: subsequent runs only. The completed run remains untouched.                                                              │
└─────────────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────────────────┘
                                                                  │
                                                                  ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ PROOF OF LEDGER STANDARD                                                                                                           │
│ - audit chain requires: catalog_digest, staff_roster, desk_tools_hash, night_shift_protocol_hash                                   │
│ - knowledge_state_digest requires: rules_state_hash, catalog_state_hash, staff_prior_hash, rubric_baseline_hash                    │
│ - replay strictness: every historical catalog edit must be reconstructable from the sealed incident logbook envelope               │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘