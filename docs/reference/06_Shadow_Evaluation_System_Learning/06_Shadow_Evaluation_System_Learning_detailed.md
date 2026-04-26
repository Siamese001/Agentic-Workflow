████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
██ ◄─────────────────────────────────────── R U N T I M E   B O U N D A R Y ───────────────────────────────────► ██
████████████████████████████████████████████████████████████████████████████████████████████████████████████████████

                                                   │
                                                   │
                                                   │  [ CURRENT RUN IS OVER ]
                                                   │  [ all live disposition decisions already made by Exit / HITL / UWG ]
                                                   │  [ L6 receives only sealed exhaust from completed runs ]
                                                   │
                                                   ▼

                               [ ASYNC RUNTIME EXHAUST FROM COMPLETED RUNS ONLY ]
                               - sealed traces
                               - L2 artifacts
                               - route contracts
                               - prompt envelopes
                               - retrieval contracts
                               - exit dispositions
                               - HITL packets
                               - policy grades
                               - sandbox receipts
                               - tool/model invocation receipts
                               - commit receipts
                               - denial/reroute/escalation reason codes
                               - replay keys
                               - policy hashes
                               - source lineage
                               - cost / latency / token telemetry
                               - evaluator outputs
                               - human calibration signals

                                                   │
                                                   ▼

===================================================================================================================
6. L6 SHADOW EVALUATION -> FUTURE-RUN LEARNING  v7
   Library Persona: 🌙 Night Shift + 🧾 Tape Reviewer + 🧠 Board Meeting + 🧪 Proving Lab + 🖋️ Master Clerk

   MISSION:
   Read completed runtime evidence, normalize it, evaluate it, calibrate the graders, detect drift,
   isolate root causes, draft safe improvements, prove those improvements under replay/regression,
   and promote only approved future-run updates through UWG into L4.

   WHAT L6 IS:
   - after-hours reviewer
   - shadow evaluator
   - root-cause investigator
   - calibration system
   - learning proposal factory
   - regression proving lab
   - future-run improvement pipeline

   WHAT L6 IS NOT:
   - not a live router
   - not a live executor
   - not a current-run rescuer
   - not a direct L4 writer
   - not a prompt mutator
   - not a hidden policy changer
   - not an ungated memory updater
   - not a judge allowed to invent certainty

   CORE FIREWALL:
   [!] EVAL MUST PRECEDE LEARNING:
       meta-learning amplifies whatever it is fed.
       Therefore raw traces must be evaluated, scored, calibrated, and lineage-bound before RCA,
       pattern synthesis, rule drafting, or promotion can occur.

   SEQUENCE LAW:
       Observe -> Normalize -> Evaluate -> Calibrate -> Fuse -> RCA -> Draft -> Prove -> Approve -> UWG Commit -> Future Run

   NEVER:
       Observe -> Mutate Live Run
       Observe -> Promote Raw Signal
       Trace -> Draft Without Eval
       Human Preference -> Policy Without Calibration
       Failed Run -> Silent Prompt Patch
       L6 Proposal -> Direct L4 Write

   CONSTRAINTS:
   - No live patron impact
   - Future visits only
   - Read / grade first
   - Raw telemetry is not learning yet
   - Propose only until gauntlet approval
   - No completed-run rescue
   - No silent promotion
   - No partial bypass
   - No unscored rule drafting
   - No grader certainty when rubric says Unknown
   - No stale eval on write
   - No disconnected evidence
   - No direct L6 write
   - UWG is the sole ink path into L4

   HEALTH DEFINITION:
   The pipeline is healthy only when ingest freshness, eval coverage, calibration freshness,
   replay localization, RCA lead time, false-promote rate, stale-rubric saturation, evidence lineage,
   and UWG uniqueness are all green together.
===================================================================================================================

                                                   │
                                                   │ [ sealed traces / exits / artifacts / HITL packets / policy grades ]
                                                   ▼

 ┌──────────────────────────────┐   ┌──────────────────────────────┐   ┌──────────────────────────────┐   ┌──────────────────────────────┐
 │ 6A. INGEST                   │──►│ 6B. EVALUATE                 │──►│ 6C. RCA / SYNTH               │──►│ 6D. PROMOTE / UPDATE          │
 │ The Tape Room                │   │ The Grading Bench            │   │ The Board Investigation       │   │ The Approval + Ink Gate       │
 │                              │   │                              │   │                              │   │                              │
 │ Reads completed runtime      │   │ Converts raw evidence into   │   │ Turns evaluated signals into  │   │ Tests, approves, and commits  │
 │ exhaust and normalizes it    │   │ scored judgments. This is    │   │ root causes, clusters, and    │   │ future-run changes only       │
 │ into replayable evidence.    │   │ mandatory before learning.   │   │ proposal packets.             │   │ through UWG -> L4.            │
 │                              │   │                              │   │                              │   │                              │
 │ HARD LAW:                    │   │ HARD LAW:                    │   │ HARD LAW:                    │   │ HARD LAW:                    │
 │ read-only observer path.     │   │ no 6C / 6D without 6B.       │   │ propose only, no ink.         │   │ no UWG receipt, no promote.   │
 │                              │   │                              │   │                              │   │                              │
 │ ACCEPTS:                     │   │ ACCEPTS:                     │   │ ACCEPTS:                     │   │ ACCEPTS:                     │
 │ sealed completed-run exhaust │   │ normalized evidence records  │   │ evaluated signal bundles      │   │ approved proposal packets     │
 │                              │   │                              │   │                              │   │                              │
 │ OUTPUTS:                     │   │ OUTPUTS:                     │   │ OUTPUTS:                     │   │ OUTPUTS:                     │
 │ normalized evidence bundle   │   │ eval records + calibration   │   │ RCA + draft proposal packet   │   │ durable future-run update     │
 └──────────────┬───────────────┘   └──────────────┬───────────────┘   └──────────────┬───────────────┘   └──────────────┬───────────────┘
                │                                  │                                  │                                  │
                ▼                                  ▼                                  ▼                                  ▼

===================================================================================================================
                                      6A INGEST: THE TAPE ROOM
                         read completed runtime exhaust | preserve lineage | no mutation
===================================================================================================================

 ┌──────────────────────────────┐
 │ S1A. GATHER EXHAUST          │
 │ "Collect the night tapes"    │
 ├──────────────────────────────┤
 │ INPUTS                       │
 │ - OTel spans                 │
 │ - sealed L2 artifacts        │
 │ - L0 RouteContract           │
 │ - L1 PlanContract            │
 │ - C0 EvidenceContract        │
 │ - PromptEnvelope / HMAC      │
 │ - tool invocation receipts   │
 │ - model invocation receipts  │
 │ - sandbox envelopes          │
 │ - exit dispositions          │
 │ - deny / reroute reasons     │
 │ - escalation reason codes    │
 │ - HITL packets               │
 │ - commit receipts            │
 │ - policy / safety outcomes   │
 │ - cost / token / latency     │
 │ - replay digests             │
 │ - provider metadata          │
 │ - artifact hashes            │
 │                              │
 │ MUST PRESERVE                │
 │ - trace_id                   │
 │ - span_id                    │
 │ - parent_span_id             │
 │ - run_id                     │
 │ - session_id                 │
 │ - request_id                 │
 │ - route_id                   │
 │ - step_id                    │
 │ - attempt_id                 │
 │ - replay_key                 │
 │ - blueprint_hash             │
 │ - policy_hash                │
 │ - prompt_hash                │
 │ - context_hash               │
 │ - model_id                   │
 │ - tool_id                    │
 │ - provider_lane              │
 │ - source lineage             │
 │ - artifact digest            │
 │ - L4 snapshot ref            │
 │ - UWG receipt ref            │
 │                              │
 │ MUST DETECT                  │
 │ - missing trace link         │
 │ - orphan artifact            │
 │ - unsealed span              │
 │ - impossible stage order     │
 │ - policy hash mismatch       │
 │ - missing replay key         │
 │ - non-deterministic metadata │
 │ - duplicate run identity     │
 │ - incomplete invocation log  │
 │ - unbound HITL input         │
 │ - unknown provider fallback  │
 │                              │
 │ OUTPUT                       │
 │ RuntimeExhaustBundle         │
 │ - raw_evidence_refs          │
 │ - lineage_manifest           │
 │ - stage_map                  │
 │ - artifact_inventory         │
 │ - gap_report                 │
 │ - ingest_quality_score       │
 │                              │
 │ KPI                          │
 │ trace-ingest freshness       │
 │ green: newest span <= 10 min │
 └──────────────┬───────────────┘
                │
                ▼

 ┌──────────────────────────────┐
 │ S1B. NORMALIZE EVIDENCE      │
 │ "Make the tapes comparable"  │
 ├──────────────────────────────┤
 │ NORMALIZES                   │
 │ - event formats              │
 │ - provider trace formats     │
 │ - tool return formats        │
 │ - model metadata             │
 │ - token accounting           │
 │ - latency fields             │
 │ - cost fields                │
 │ - retry counters             │
 │ - error codes                │
 │ - route reason codes         │
 │ - policy reason codes        │
 │ - HITL verdict shapes        │
 │ - exit disposition schemas   │
 │ - eval-ready records         │
 │                              │
 │ BINDS                        │
 │ - replay links               │
 │ - source IDs                 │
 │ - parent artifacts           │
 │ - child artifacts            │
 │ - L4 snapshot refs           │
 │ - route contract refs        │
 │ - prompt envelope refs       │
 │ - evidence contract refs     │
 │ - policy version refs        │
 │ - rubric version refs        │
 │ - UWG receipts               │
 │                              │
 │ STRATIFIES                   │
 │ - normal success             │
 │ - degraded success           │
 │ - safe abstain               │
 │ - denied unsafe request      │
 │ - rerouted request           │
 │ - HITL escalated             │
 │ - tool failure               │
 │ - model failure              │
 │ - grounding failure          │
 │ - policy failure             │
 │ - replay failure             │
 │ - schema failure             │
 │ - unresolved unknown         │
 │                              │
 │ HARD NO                      │
 │ - no mutation                │
 │ - no summarizing away lineage│
 │ - no dropping contradictions │
 │ - no rewriting traces        │
 │ - no score fabrication       │
 │ - no filling missing evidence│
 │ - no hidden retry collapse   │
 │                              │
 │ OUTPUT                       │
 │ NormalizedEvidenceRecord     │
 │ - canonical fields           │
 │ - lineage-preserved payload  │
 │ - evidence gaps              │
 │ - normalization warnings     │
 │ - eval readiness             │
 │                              │
 │ KPI                          │
 │ normalization completeness   │
 │ green: >= 99% required fields│
 └──────────────┬───────────────┘
                │
                ▼

 ┌──────────────────────────────┐
 │ S1C. OBSERVER LAW            │
 │ "Watch only, never steer"    │
 ├──────────────────────────────┤
 │ MUST ONLY READ               │
 │ - runtime traces             │
 │ - artifacts                  │
 │ - prompts                    │
 │ - evidence contracts         │
 │ - route contracts            │
 │ - HITL dispositions          │
 │ - exit decisions             │
 │ - commit receipts            │
 │ - policy outcomes            │
 │ - eval outputs               │
 │                              │
 │ MUST NOT                     │
 │ - write to L4                │
 │ - publish to BUS U           │
 │ - mutate prompt / policy     │
 │ - mutate rubric              │
 │ - mutate retrieval profiles  │
 │ - rescue current run         │
 │ - alter live thresholds      │
 │ - change route decisions     │
 │ - change exit decisions      │
 │ - change HITL decisions      │
 │ - feedback into runtime path │
 │ - regrade current disposition│
 │                              │
 │ ENFORCED BY                  │
 │ - surface isolation validator│
 │ - stage barrier enforcer     │
 │ - read-only credential scope │
 │ - no-write token             │
 │ - immutable evidence storage │
 │ - audit-only event producer  │
 │                              │
 │ VIOLATION RESPONSE           │
 │ - stop ingest lane           │
 │ - freeze suspect packet      │
 │ - classify sovereignty breach│
 │ - emit L6-OBSERVER-FAIL      │
 │ - require C4/UWG audit       │
 │                              │
 │ OUTPUT                       │
 │ ObserverComplianceReceipt    │
 │ - read-only proof            │
 │ - touched surfaces           │
 │ - denied write attempts      │
 │ - isolation status           │
 └──────────────┬───────────────┘
                │
                ▼

 ┌──────────────────────────────┐
 │ S1D. EVIDENCE READINESS GATE │
 │ "Can this be graded?"        │
 ├──────────────────────────────┤
 │ CHECKS                       │
 │ - trace completeness         │
 │ - artifact integrity         │
 │ - replay key present         │
 │ - policy hash present        │
 │ - route contract present     │
 │ - prompt hash present        │
 │ - source lineage present     │
 │ - terminal status present    │
 │ - evaluator inputs available │
 │                              │
 │ DECIDES                      │
 │ - READY_FOR_6B               │
 │ - PARTIAL_BUT_SCORABLE       │
 │ - HOLD_FOR_MISSING_EVIDENCE  │
 │ - NON_EVALUABLE_PACKET       │
 │                              │
 │ FAILURE HANDLING             │
 │ - do not infer missing facts │
 │ - attach missing evidence map│
 │ - mark coverage gap          │
 │ - route to telemetry repair  │
 │ - exclude from learning      │
 │   until evaluable            │
 │                              │
 │ OUTPUT                       │
 │ EvalReadinessReceipt         │
 └──────────────┬───────────────┘
                │
                ▼

===================================================================================================================
                                      6B EVALUATE: THE GRADING BENCH
                     outcome eval | trajectory eval | governance eval | calibration
===================================================================================================================

 ┌──────────────────────────────┐
 │ S2A. OUTCOME EVALS           │
 │ "Did the answer work?"       │
 ├──────────────────────────────┤
 │ GRADES                       │
 │ - task completion            │
 │ - answer correctness         │
 │ - groundedness               │
 │ - citation support           │
 │ - source coverage            │
 │ - evidence sufficiency       │
 │ - abstain correctness        │
 │ - refusal correctness        │
 │ - format / schema fit        │
 │ - user constraint adherence  │
 │ - scope discipline           │
 │ - final answer usefulness    │
 │ - artifact validity          │
 │ - factual claim support      │
 │ - unsupported inference risk │
 │                              │
 │ REQUIRED RECORD              │
 │ - eval_id                    │
 │ - rubric_hash                │
 │ - rubric_version             │
 │ - grader_version             │
 │ - grader_model_id            │
 │ - eval_prompt_hash           │
 │ - evidence_snapshot_hash     │
 │ - score vector               │
 │ - support rationale          │
 │ - confidence band            │
 │ - Unknown when uncertain     │
 │ - appeal / review marker     │
 │                              │
 │ MUST ALLOW                   │
 │ - UNKNOWN                    │
 │ - PARTIAL_SUPPORT            │
 │ - CONFLICTED_SUPPORT         │
 │ - NOT_ENOUGH_EVIDENCE        │
 │                              │
 │ MUST NOT                     │
 │ - force binary certainty     │
 │ - reward unsupported fluency │
 │ - hide missing citations     │
 │ - count style as correctness │
 │ - grade beyond evidence      │
 │                              │
 │ OUTPUT                       │
 │ OutcomeEvalRecord            │
 │ - scores                     │
 │ - rationale                  │
 │ - unsupported_claims         │
 │ - support map                │
 │ - uncertainty markers        │
 │                              │
 │ KPI                          │
 │ eval coverage of runs        │
 │ green: >= 98% in 24h         │
 └──────────────┬───────────────┘
                │
                ▼

 ┌──────────────────────────────┐
 │ S2B. TRAJECTORY EVALS        │
 │ "Was the path sane?"         │
 ├──────────────────────────────┤
 │ GRADES                       │
 │ - route fit                  │
 │ - tool order / choice        │
 │ - model lane selection       │
 │ - argument correctness       │
 │ - retrieval use              │
 │ - prompt assembly correctness│
 │ - fallback depth             │
 │ - retry thrash               │
 │ - loop productivity          │
 │ - budget behavior            │
 │ - latency behavior           │
 │ - cost behavior              │
 │ - HITL trigger fit           │
 │ - sandbox scope fit          │
 │ - write request legitimacy   │
 │ - evidence preservation      │
 │                              │
 │ MUST DETECT                  │
 │ - route thrash               │
 │ - silent fallback            │
 │ - tool misuse                │
 │ - tool overreach             │
 │ - hidden scope growth        │
 │ - unbounded loop             │
 │ - skipped C0 grounding       │
 │ - skipped prompt validation  │
 │ - premature answer           │
 │ - stale cache reuse          │
 │ - excessive model escalation │
 │ - non-replayable behavior    │
 │ - unnecessary HITL           │
 │ - missing HITL               │
 │                              │
 │ OUTPUT                       │
 │ TrajectoryEvalRecord         │
 │ - path_score                 │
 │ - span_fault_candidates      │
 │ - route_quality              │
 │ - tool_quality               │
 │ - retry_quality              │
 │ - cost_quality               │
 │ - budget_quality             │
 │ - evidence_path_integrity    │
 │                              │
 │ KPI                          │
 │ saturation watch             │
 │ green: <= 10% static >=30d   │
 └──────────────┬───────────────┘
                │
                ▼

 ┌──────────────────────────────┐
 │ S2C. GOVERNANCE REGRESSION   │
 │ "Did guardrails drift?"      │
 ├──────────────────────────────┤
 │ CHECKS                       │
 │ - exact-match drift          │
 │ - policy drift               │
 │ - schema / API drift         │
 │ - model behavior drift       │
 │ - tool behavior drift        │
 │ - provider behavior drift    │
 │ - guardrail failures         │
 │ - refusal / abstain drift    │
 │ - citation support drift     │
 │ - prompt drift               │
 │ - retrieval-profile drift    │
 │ - sandbox escape signals     │
 │ - HITL threshold drift       │
 │ - UWG receipt drift          │
 │ - replay digest drift        │
 │                              │
 │ RUBRIC INTEGRITY             │
 │ - rubric_hash required       │
 │ - version bump on change     │
 │ - calibration before promote │
 │ - golden-set comparison      │
 │ - regression pack link       │
 │ - Unknown option required    │
 │ - disagreement captured      │
 │                              │
 │ DETECTS                      │
 │ - guard became too loose     │
 │ - guard became too strict    │
 │ - eval no longer measures    │
 │ - stale baseline             │
 │ - hidden policy mismatch     │
 │ - rubrics rewarding wrong    │
 │                              │
 │ OUTPUT                       │
 │ GovernanceRegressionRecord   │
 │ - drift_flags                │
 │ - impacted surfaces          │
 │ - severity                   │
 │ - suspected cause            │
 │ - required review            │
 │                              │
 │ KPI                          │
 │ judge unknown-budget comply  │
 │ green: >= 95%                │
 └──────────────┬───────────────┘
                │
                ▼

 ┌──────────────────────────────┐
 │ S2D. HUMAN CALIBRATION       │
 │ "Tune the graders"          │
 ├──────────────────────────────┤
 │ USES                         │
 │ - SME spot checks            │
 │ - HITL decision logs         │
 │ - golden set comparisons     │
 │ - judge disagreement review  │
 │ - scorer drift bounds        │
 │ - appeal outcomes            │
 │ - red-team labels            │
 │ - postmortem labels          │
 │ - production incident labels │
 │                              │
 │ CALIBRATES                   │
 │ - rubric thresholds          │
 │ - Unknown budget             │
 │ - severity classes           │
 │ - escalation thresholds      │
 │ - false positive tolerance   │
 │ - false negative tolerance   │
 │ - refusal correctness        │
 │ - abstain correctness        │
 │ - citation precision scoring │
 │                              │
 │ OUTPUTS                      │
 │ - calibrated rubric version  │
 │ - judge reliability signal   │
 │ - κ / agreement score        │
 │ - disagreement clusters      │
 │ - reviewer notes             │
 │ - escalation threshold update│
 │   proposal only              │
 │                              │
 │ HARD NO                      │
 │ - human preference is not    │
 │   automatically policy       │
 │ - single reviewer does not   │
 │   silently override rubric   │
 │ - calibration is not commit  │
 │                              │
 │ KPI                          │
 │ judge-human κ freshness      │
 │ green: <= 7 days per rubric  │
 └──────────────┬───────────────┘
                │
                ▼

 ┌──────────────────────────────┐
 │ S2E. EVAL RECORD SEAL        │
 │ "Freeze the grade sheet"     │
 ├──────────────────────────────┤
 │ SEALS                        │
 │ - outcome eval               │
 │ - trajectory eval            │
 │ - governance eval            │
 │ - human calibration link     │
 │ - rubric hash                │
 │ - grader version             │
 │ - evidence snapshot hash     │
 │ - uncertainty markers        │
 │ - reviewer overrides         │
 │ - support rationale          │
 │                              │
 │ OUTPUT                       │
 │ CompletedEvalRecord          │
 │ - eval_record_id             │
 │ - immutable score bundle     │
 │ - lineage bound evidence     │
 │ - allowed downstream use     │
 │                              │
 │ GATE                         │
 │ 6C cannot consume anything   │
 │ not sealed here.             │
 └──────────────┬───────────────┘
                │
                ▼

===================================================================================================================
                                  6C RCA / SYNTH: THE BOARD INVESTIGATION
                fused evaluated signals | root cause isolation | pattern synthesis | proposal drafting
===================================================================================================================

 ┌──────────────────────────────┐
 │ S3A. SIGNAL FUSION            │
 │ "What is the real signal?"    │
 ├──────────────────────────────┤
 │ FUSES                         │
 │ - BUS P preference grades     │
 │ - BUS T telemetry / traces    │
 │ - outcome evals               │
 │ - trajectory evals            │
 │ - governance regressions      │
 │ - human calibration signals   │
 │ - drift / anomaly signals     │
 │ - HITL outcomes               │
 │ - denial / reroute reasons    │
 │ - replay failures             │
 │ - incident reports            │
 │ - red-team failures           │
 │ - production support reports  │
 │                              │
 │ NORMALIZES SIGNAL WEIGHT      │
 │ - source reliability          │
 │ - evaluator reliability       │
 │ - sample size                 │
 │ - severity                    │
 │ - confidence                  │
 │ - recency                     │
 │ - reproducibility             │
 │ - user impact                 │
 │ - policy criticality          │
 │                              │
 │ MUST OUTPUT                   │
 │ - fused_signal_bundle         │
 │ - severity_class              │
 │ - confidence_band             │
 │ - drift_cluster_candidates    │
 │ - affected_surface_candidates │
 │ - recommended investigation   │
 │                              │
 │ HARD NO                      │
 │ - no learning from raw traces │
 │ - no promoting popularity     │
 │ - no treating preferences as  │
 │   correctness without rubric  │
 │                              │
 │ KPI                          │
 │ RCA-to-proposal lead time     │
 │ green: p95 <= 24h             │
 └──────────────┬───────────────┘
                │
                ▼

 ┌──────────────────────────────┐
 │ S3B. INCIDENT RCA             │
 │ "Why did this happen?"        │
 ├──────────────────────────────┤
 │ ISOLATES                      │
 │ - first failing span          │
 │ - bad route                   │
 │ - bad cache reuse             │
 │ - bad retrieval               │
 │ - bad rerank                  │
 │ - bad prompt assembly         │
 │ - bad model selection         │
 │ - bad tool selection          │
 │ - bad tool args               │
 │ - bad policy decision         │
 │ - missing HITL                │
 │ - unnecessary HITL            │
 │ - schema / API drift          │
 │ - provider drift              │
 │ - rubric drift                │
 │ - stale baseline              │
 │ - weak evidence               │
 │ - contradiction ignored       │
 │ - replay nondeterminism       │
 │ - budget exhaustion           │
 │ - sandbox over/under scope    │
 │                              │
 │ ROOT CAUSE CLASSES            │
 │ - ROUTE_MISS                  │
 │ - CACHE_FALSE_HIT             │
 │ - RETRIEVAL_RECALL_GAP        │
 │ - RERANK_PRECISION_GAP        │
 │ - GRAPH_CONTEXT_GAP           │
 │ - PROMPT_SLOT_ORDER_ERROR     │
 │ - INSTRUCTION_CONFLICT        │
 │ - TOOL_ARG_SCHEMA_ERROR       │
 │ - PROVIDER_DRIFT              │
 │ - POLICY_THRESHOLD_ERROR      │
 │ - RUBRIC_CALIBRATION_ERROR    │
 │ - HITL_GATE_ERROR             │
 │ - UWG_SCOPE_ERROR             │
 │ - REPLAY_INTEGRITY_ERROR      │
 │ - EVIDENCE_LINEAGE_LOSS       │
 │ - UNKNOWN_ROOT_CAUSE          │
 │                              │
 │ BUILDS                        │
 │ - incident_id                 │
 │ - failure_chain               │
 │ - first_bad_span              │
 │ - root_cause_class            │
 │ - drift_cluster_map           │
 │ - affected_surfaces           │
 │ - proposed fix surface        │
 │ - evidence links              │
 │ - confidence / uncertainty    │
 │                              │
 │ OUTPUT                        │
 │ RCA packet                    │
 │ with evidence + reason_codes  │
 └──────────────┬───────────────┘
                │
                ▼

 ┌──────────────────────────────┐
 │ S3C. PATTERN SYNTHESIS       │
 │ "Is this one-off or systemic?"│
 ├──────────────────────────────┤
 │ CLUSTERS                     │
 │ - repeated failures          │
 │ - similar route misses       │
 │ - similar retrieval gaps     │
 │ - recurring policy friction  │
 │ - repeated tool misuse       │
 │ - prompt confusion patterns  │
 │ - false cache hits           │
 │ - HITL disagreement clusters │
 │ - citation support failures  │
 │ - abstain/refusal drift      │
 │ - provider-specific failures │
 │                              │
 │ DISTINGUISHES                │
 │ - one-off incident           │
 │ - small local defect         │
 │ - systemic rule gap          │
 │ - training/eval gap          │
 │ - documentation gap          │
 │ - policy ambiguity           │
 │ - tool/provider drift        │
 │ - data/index freshness issue │
 │                              │
 │ OUTPUT                       │
 │ PatternSynthesisRecord       │
 │ - pattern_id                 │
 │ - examples                   │
 │ - counterexamples            │
 │ - affected surfaces          │
 │ - blast radius estimate      │
 │ - confidence band            │
 │ - proposed action class      │
 └──────────────┬───────────────┘
                │
                ▼

 ┌──────────────────────────────┐
 │ S3D. RULE DRAFTING            │
 │ "Draft tomorrow's correction" │
 ├──────────────────────────────┤
 │ MAY DRAFT                     │
 │ - prompt updates              │
 │ - policy tweaks               │
 │ - rubric changes              │
 │ - config changes              │
 │ - retrieval-profile updates   │
 │ - semantic cache thresholds   │
 │ - rerank profile updates      │
 │ - exemplar candidates         │
 │ - reason priors               │
 │ - HITL threshold adjustments  │
 │ - tool schema validations     │
 │ - provider lane constraints   │
 │ - sandbox scope defaults      │
 │ - golden-set additions        │
 │                              │
 │ MUST INCLUDE                  │
 │ - target surface              │
 │ - problem statement           │
 │ - evidence link               │
 │ - completed eval_record_id    │
 │ - RCA packet ID               │
 │ - expected effect             │
 │ - rollback plan               │
 │ - blast-radius statement      │
 │ - affected tests              │
 │ - migration notes             │
 │ - owner / signer identity     │
 │ - expiration / review TTL     │
 │                              │
 │ DRAFT TYPES                   │
 │ - LOCAL_PATCH                 │
 │ - THRESHOLD_CHANGE            │
 │ - RUBRIC_UPDATE               │
 │ - PROMPT_UPDATE               │
 │ - RETRIEVAL_PROFILE_UPDATE    │
 │ - POLICY_CLARIFICATION        │
 │ - EXEMPLAR_ADDITION           │
 │ - GOLDEN_SET_ADDITION         │
 │ - TOOL_CONTRACT_TIGHTENING    │
 │ - HOLD_FOR_MORE_EVIDENCE      │
 │                              │
 │ HARD LAW                     │
 │ Floor staff propose only.     │
 │ Board drafts are not commits. │
 │                              │
 │ OUTPUT                       │
 │ DraftProposalPacket           │
 └──────────────┬───────────────┘
                │
                ▼

 ┌──────────────────────────────┐
 │ S3E. PROPOSAL ADMISSION GATE │
 │ "Is this ready to prove?"    │
 ├──────────────────────────────┤
 │ REQUIRED                     │
 │ - completed 6B eval record   │
 │ - RCA packet                 │
 │ - target surface             │
 │ - proposed diff              │
 │ - blast radius               │
 │ - rollback plan              │
 │ - test plan                  │
 │ - owner / signer             │
 │ - freshness check            │
 │ - no open blocker            │
 │                              │
 │ DECIDES                      │
 │ - ADMIT_TO_GAUNTLET          │
 │ - HOLD_FOR_MORE_EVIDENCE     │
 │ - REJECT_WEAK_PROPOSAL       │
 │ - REQUIRE_SME_REVIEW         │
 │                              │
 │ HARD NO                      │
 │ - no direct 6D entry         │
 │ - no eval-less proposal      │
 │ - no unclear blast radius    │
 │ - no missing rollback plan   │
 └──────────────┬───────────────┘
                │
                ▼

===================================================================================================================
                                  6D PROMOTE / UPDATE: THE APPROVAL + INK GATE
                 deterministic gauntlet | approval | UWG commit | L4 materialization | future-run bus
===================================================================================================================

 ┌──────────────────────────────┐
 │ S4A. GAUNTLET                 │
 │ "Prove the fix is safe"       │
 ├──────────────────────────────┤
 │ TESTS                         │
 │ - deterministic shadow replay │
 │ - regression packs            │
 │ - golden-set comparisons      │
 │ - canary / rollback checks    │
 │ - SME safety signoff          │
 │ - replay divergence scoring   │
 │ - prompt compatibility        │
 │ - policy compatibility        │
 │ - retrieval replay check      │
 │ - cache pollution check       │
 │ - schema compatibility        │
 │ - API compatibility           │
 │ - latency/cost budget impact  │
 │ - false positive/negative     │
 │ - blast-radius test           │
 │ - rollback rehearsal          │
 │                              │
 │ REPLAY MODES                  │
 │ - same input / old surface    │
 │ - same input / new surface    │
 │ - known-good golden cases     │
 │ - known-bad guardrail cases   │
 │ - boundary / adversarial set  │
 │ - route-determinism replay    │
 │ - retrieval-contract replay   │
 │                              │
 │ MUST OUTPUT                   │
 │ - gauntlet_receipt            │
 │ - pass / fail / hold verdict  │
 │ - failing cases               │
 │ - rollout risk score          │
 │ - rollback plan validation    │
 │ - replay proof                │
 │ - signer identity             │
 │                              │
 │ KPI                          │
 │ replay divergence localization│
 │ green: >= 90% localized       │
 └──────────────┬───────────────┘
                │
                ▼

 ┌──────────────────────────────┐
 │ S4B. APPROVE / REJECT         │
 │ "Pass the packet or hold it"  │
 ├──────────────────────────────┤
 │ DECIDES                       │
 │ - approve                     │
 │ - reject                      │
 │ - hold for more evidence      │
 │ - require SME review          │
 │ - require rollback plan       │
 │ - require narrower scope      │
 │ - require ADR exception       │
 │                              │
 │ GATES                         │
 │ - completed 6B eval required  │
 │ - RCA packet required         │
 │ - gauntlet receipt required   │
 │ - eval freshness within TTL   │
 │ - calibration freshness OK    │
 │ - no partial bypass           │
 │ - no silent promotion         │
 │ - signer authority verified   │
 │ - rollback plan verified      │
 │ - blast radius accepted       │
 │                              │
 │ FAILURE RULE                  │
 │ If any required stage fails,  │
 │ reject or hold the proposal   │
 │ as a whole unless an explicit │
 │ ADR scopes a narrow exception.│
 │                              │
 │ OUTPUT                       │
 │ ApprovalDecisionRecord        │
 └──────────────┬───────────────┘
                │
                ▼

 ┌──────────────────────────────┐
 │ S4C. UWG MASTER CLERK         │
 │ "Only clerk with real ink"    │
 ├──────────────────────────────┤
 │ ONLY UWG MAY WRITE            │
 │ - prompts                     │
 │ - policies                    │
 │ - rubrics                     │
 │ - baselines                   │
 │ - retrieval profiles          │
 │ - semantic cache thresholds   │
 │ - rerank configs              │
 │ - approved exemplars          │
 │ - approved reason priors      │
 │ - golden sets                 │
 │ - rollout manifests           │
 │ - promotion receipts          │
 │                              │
 │ WRITE REQUIREMENTS            │
 │ - proposal_id                 │
 │ - approval_decision_id        │
 │ - gauntlet_receipt            │
 │ - content_hash                │
 │ - signer_identity             │
 │ - policy_hash                 │
 │ - target_surface              │
 │ - blast_radius                │
 │ - rollback_plan               │
 │ - durable audit entry         │
 │ - version bump                │
 │ - alias swap plan             │
 │ - cache refresh plan          │
 │                              │
 │ UWG CHECKS                    │
 │ - authority                   │
 │ - signature                   │
 │ - RBAC                        │
 │ - catalog scope               │
 │ - diff validity               │
 │ - lock availability           │
 │ - no duplicate promotion      │
 │ - no shadow writer            │
 │ - rollback addressability     │
 │                              │
 │ HARD LAW                     │
 │ No direct L2 / HITL / L6      │
 │ write path exists.            │
 └──────────────┬───────────────┘
                │
                ▼

 ┌──────────────────────────────┐
 │ S4D. LEDGER PROOF             │
 │ "Prove what changed"          │
 ├──────────────────────────────┤
 │ PRODUCES                      │
 │ - audit chain hashes          │
 │ - replay strictness record    │
 │ - rollout receipts            │
 │ - L4 version digest           │
 │ - alias swap receipt          │
 │ - cache refresh receipt       │
 │ - promotion manifest          │
 │ - rollback handle             │
 │ - previous version pointer    │
 │ - new version pointer         │
 │ - BUS U publish marker        │
 │                              │
 │ VALIDATES                     │
 │ - same input replay outcome   │
 │ - approved packet equality    │
 │ - no shadow writer detected   │
 │ - committed content hash      │
 │ - L4 version monotonicity     │
 │ - rollback reachable          │
 │ - no stale eval on write      │
 │                              │
 │ KPIs                         │
 │ UWG ink-path uniqueness = 0   │
 │ eval-freshness on write=100%  │
 └──────────────┬───────────────┘
                │
                ▼

 ┌──────────────────────────────┐
 │ S4E. FUTURE-RUN PUBLISH       │
 │ "Only tomorrow sees it"       │
 ├──────────────────────────────┤
 │ PUBLISHES TO BUS U            │
 │ - prompt version aliases      │
 │ - policy version aliases      │
 │ - rubric version aliases      │
 │ - retrieval profile aliases   │
 │ - approved exemplars          │
 │ - reason priors               │
 │ - baseline manifests          │
 │ - tool/model config manifests │
 │                              │
 │ ACTIVATION RULE               │
 │ - next run_start only         │
 │ - no completed-run mutation   │
 │ - no current-run rescue       │
 │ - no retroactive regrade      │
 │ - no hidden threshold change  │
 │                              │
 │ OUTPUT                       │
 │ FutureRunActivationReceipt    │
 └──────────────┬───────────────┘
                │
                ▼

===================================================================================================================
                                    6D WRITE / UPDATE MATERIALIZATION
===================================================================================================================

       ┌───────────────────────────────────────────────────────────────────────────────────────────────────────┐
       │ APPROVED PROMOTION PACKET                                                                             │
       │ - proposal_id                                                                                         │
       │ - approval_decision_id                                                                                │
       │ - target_surface: prompt | policy | rubric | baseline | retrieval_profile | exemplar | reason_prior   │
       │ - evidence_links: trace_id / run_id / replay_key / source lineage                                      │
       │ - eval_record: completed 6B outcome + trajectory + governance scores                                   │
       │ - calibration_record: human / SME / golden-set agreement if required                                   │
       │ - RCA packet: incident_id / first_bad_span / root_cause_class / failure_chain                         │
       │ - proposed_diff: exact change, not vague instruction                                                   │
       │ - gauntlet_receipt: replay + regression + SME signoff if required                                      │
       │ - rollout_plan: dark launch | canary | full activation | TTL review                                    │
       │ - rollback_plan                                                                                       │
       │ - blast_radius                                                                                        │
       │ - content_hash                                                                                        │
       │ - policy_hash                                                                                         │
       │ - signer_identity                                                                                     │
       │ - eval_freshness_proof                                                                                │
       │ - no_partial_bypass_proof                                                                             │
       └───────────────────────────────────────────────────────┬───────────────────────────────────────────────┘
                                                               │
                                                               │ [ commit request ]
                                                               ▼
       ┌───────────────────────────────────────────────────────────────────────────────────────────────────────┐
       │ 🖋️ UWG MASTER CLERK                                                                                    │
       │ - verifies authority, policy_hash, signature, and capability                                           │
       │ - checks catalog scope, RBAC, diff, and blast radius                                                   │
       │ - checks completed 6B eval exists and is fresh                                                         │
       │ - checks gauntlet receipt exists and matches proposed content_hash                                     │
       │ - checks rollback target exists                                                                       │
       │ - checks no conflicting promotion already landed                                                       │
       │ - claims write lock                                                                                    │
       │ - commits to L4                                                                                        │
       │ - appends hash-chain audit record                                                                      │
       │ - performs alias swap / cache refresh                                                                  │
       │ - emits rollout receipt                                                                                │
       │ - emits rollback handle                                                                                │
       └───────────────────────────────────────────────────────┬───────────────────────────────────────────────┘
                                                               │
                                                               │ [ durable future-run state ]
                                                               ▼
       ┌───────────────────────────────────────────────────────────────────────────────────────────────────────┐
       │ 🏛️ L4 ARCHIVE / CANONICAL STORE                                                                        │
       │ - updated prompts                                                                                      │
       │ - updated policies                                                                                     │
       │ - updated rubrics                                                                                      │
       │ - updated baselines                                                                                    │
       │ - updated retrieval profiles                                                                           │
       │ - updated cache thresholds                                                                             │
       │ - updated rerank profiles                                                                              │
       │ - updated tool/model access configs                                                                    │
       │ - approved exemplars                                                                                   │
       │ - approved reason priors                                                                               │
       │ - golden-set additions                                                                                 │
       │ - promotion receipts                                                                                   │
       │ - rollback handles                                                                                     │
       │ - audit chain                                                                                          │
       └───────────────────────────────────────────────────────┬───────────────────────────────────────────────┘
                                                               │
                                                               │ [ publish at next run_start only ]
                                                               ▼
       ┌───────────────────────────────────────────────────────────────────────────────────────────────────────┐
       │ 🚌 BUS U: FUTURE RUNTIME UPDATE BUS                                                                     │
       │ Pushes approved surfaces into future runs only:                                                         │
       │ - prompts                                                                                              │
       │ - policies                                                                                             │
       │ - baselines                                                                                            │
       │ - rubrics                                                                                              │
       │ - retrieval profiles                                                                                   │
       │ - cache thresholds                                                                                     │
       │ - rerank settings                                                                                      │
       │ - tool/model lane configs                                                                              │
       │ - approved reason priors                                                                               │
       │ - approved exemplars                                                                                   │
       │ - golden sets                                                                                          │
       │                                                                                                       │
       │ INVARIANT:                                                                                             │
       │ Learning signals inform next-run behavior only. They do not mutate, rescue, rewrite, re-grade,         │
       │ re-dispose, or retroactively justify the completed current run.                                        │
       └───────────────────────────────────────────────────────────────────────────────────────────────────────┘


===================================================================================================================
                                 V7 END-TO-END CONTROL FLOW
===================================================================================================================

 Completed runtime
        │
        │ sealed exhaust only
        ▼
 6A INGEST
        │
        ├─ S1A gather all traces / artifacts / decisions / receipts
        ├─ S1B normalize into canonical eval-ready records
        ├─ S1C enforce observer law
        └─ S1D decide eval readiness
        │
        ▼
 6B EVALUATE
        │
        ├─ S2A grade outcome quality
        ├─ S2B grade trajectory quality
        ├─ S2C detect governance / drift regressions
        ├─ S2D calibrate graders against humans / golden sets
        └─ S2E seal completed eval record
        │
        ▼
 6C RCA / SYNTH
        │
        ├─ S3A fuse evaluated signals only
        ├─ S3B isolate incident root cause
        ├─ S3C cluster systemic patterns
        ├─ S3D draft proposal packet
        └─ S3E admit only complete proposals to gauntlet
        │
        ▼
 6D PROMOTE / UPDATE
        │
        ├─ S4A run deterministic gauntlet
        ├─ S4B approve / reject / hold
        ├─ S4C send approved packet to UWG
        ├─ S4D produce ledger proof
        └─ S4E publish to future-run BUS U only
        │
        ▼
 Future runs receive approved updates at run_start only


===================================================================================================================
                                 V7 KPI BOARD: WHAT "HEALTHY" MEANS
===================================================================================================================

┌──────────────────────────────────────┬──────────┬───────────────────────────────────────────────┬──────────────────────────────────────┐
│ KPI                                  │ PHASE    │ GREEN CONDITION                              │ FAILURE MEANS                        │
├──────────────────────────────────────┼──────────┼───────────────────────────────────────────────┼──────────────────────────────────────┤
│ Trace-ingest freshness               │ 6A       │ newest ingested span age <= 10 minutes        │ stale night tapes                    │
│ Evidence field completeness          │ 6A       │ >= 99% required normalized fields present     │ graders see broken packets           │
│ Orphan artifact rate                 │ 6A       │ <= 0.5% artifacts lack trace/run linkage      │ lineage is leaking                   │
│ Observer-law violation count         │ 6A       │ 0 writes / live mutations from L6             │ sovereignty breach                   │
│ Eval readiness coverage              │ 6A/6B    │ >= 98% runs evaluable within 24h              │ blind learning surface               │
│ Outcome eval coverage                │ 6B       │ >= 98% of last-24h runs have outcome eval     │ answer quality not measured          │
│ Trajectory eval coverage             │ 6B       │ >= 98% of non-RET executions graded           │ path quality not measured            │
│ Governance eval coverage             │ 6B       │ 100% high-risk / write / HITL paths checked   │ guardrail drift hidden               │
│ Judge unknown-budget compliance      │ 6B       │ >= 95% within rubric unknown_budget           │ judges forced false certainty        │
│ Judge-human κ freshness              │ 6B/S2D   │ latest calibration <= 7 days per rubric       │ grader drift not bounded             │
│ Golden-set regression pass rate      │ 6B/6D    │ >= 99% critical golden cases pass             │ proposed learning breaks basics      │
│ RCA-to-proposal lead time            │ 6C       │ p95 incident-close -> proposal <= 24 hours    │ system learns too slowly             │
│ Root-cause localization rate         │ 6C       │ >= 90% incidents have first_bad_span/class    │ RCA too vague to fix                 │
│ Proposal evidence completeness       │ 6C       │ 100% proposals link eval + RCA + evidence     │ proposal is opinion, not evidence    │
│ Held-proposal aging                  │ 6C       │ p95 hold age <= agreed TTL                    │ board backlog accumulating           │
│ Gauntlet false-promote rate          │ 6D       │ reverted promotions <= 1%                     │ unsafe promotion pressure            │
│ Replay divergence localization       │ 6D       │ >= 90% failed replays pinpoint a span         │ replay proof not diagnostic          │
│ Eval-freshness on write              │ 6D       │ 100% writes have fresh gating eval            │ stale eval allowed commit            │
│ UWG ink-path uniqueness              │ 6D       │ non-UWG writers detected = 0                  │ sovereignty breach                   │
│ Rollback reachability                │ 6D       │ 100% promotions have tested rollback handle   │ unsafe rollout                       │
│ BUS U activation correctness         │ 6D       │ 100% updates activate only at future run_start│ current-run mutation risk            │
│ Exemplar-hit rate                    │ cross    │ >= 20% eligible plans consult exemplar hit    │ learning not reused                  │
│ Saturation watch                     │ cross    │ <= 10% capability evals static >= 30 days     │ eval suite is aging                  │
│ Citation-support drift               │ cross    │ support precision stays within threshold      │ groundedness degrading               │
│ Abstain/refusal calibration drift    │ cross    │ false abstain/refusal within rubric band      │ safety/helpfulness imbalance         │
└──────────────────────────────────────┴──────────┴───────────────────────────────────────────────┴──────────────────────────────────────┘


===================================================================================================================
                                 V7 NORMATIVE INVARIANTS
===================================================================================================================

1. OBSERVER LAW
   - 6A may read completed runtime surfaces only.
   - 6A must not write L4, publish BUS U, alter prompts, alter policies, change rubrics, change thresholds,
     change routes, alter exit decisions, or feed back into the live runtime path.
   - Every normalized record must preserve trace_id, run_id, replay_key, policy_hash, prompt_hash,
     context_hash, source lineage, route_id, and artifact digest.

2. EVAL-BEFORE-LEARNING FIREWALL
   - 6C and 6D may not run against raw ingest.
   - Every RCA must reference a completed 6B evaluation record.
   - Every proposal must reference completed outcome, trajectory, and governance evaluations when applicable.
   - Bypass is forbidden because meta-learning amplifies whatever it is fed.

3. CALIBRATION BEFORE CONFIDENCE
   - Automated judges must be calibrated against SME / golden-set / HITL signals.
   - Rubrics must allow Unknown.
   - Low-confidence or contradictory evidence must remain visible downstream.
   - Human preference is signal, not sovereign policy.

4. RUBRIC INTEGRITY
   - Rubrics are content-addressed.
   - Rubric changes require version bump, calibration, golden-set comparison, and gauntlet proof.
   - Judge outputs must include support rationale and uncertainty markers.
   - A rubric that cannot decide must output Unknown rather than fabricating precision.

5. RCA MUST BE ACTIONABLE
   - RCA must identify affected surface, first failing span when possible, root_cause_class, and failure_chain.
   - "The model was bad" is not an actionable RCA.
   - Unknown root cause is allowed, but it must block promotion until enough evidence exists.

6. NO SILENT PROMOTE
   - No update may land without proposal_id, eval_record_id, RCA packet, gauntlet_receipt,
     content_hash, signer_identity, policy_hash, and rollback_plan.
   - A write without a receipt is a CI / governance failure.

7. NO PARTIAL BYPASS
   - If any required stage fails, the full promotion packet is rejected or held.
   - Partial promotion requires an explicit ADR-scoped exception with narrowed blast radius.

8. UWG SOLE INK PATH
   - L6 drafts and recommends.
   - UWG commits.
   - L4 stores canonical truth.
   - BUS U publishes only after approved durable commit.
   - No direct L2 / HITL / L6 write path exists.

9. FUTURE-RUN ONLY
   - Completed runs are historical facts.
   - Learning does not mutate completed runs.
   - Approved changes affect only future run_start surfaces.
   - Regrading history for analysis is allowed only as analysis, never as retroactive runtime disposition.

10. REPLAY PROOF REQUIRED
   - Promotions must be replay-proven or explicitly marked as non-replayable with ADR-scoped rationale.
   - Replay divergence must localize to a span, surface, or configuration class when possible.
   - Same packet + same snapshot + same policy_hash must produce the same replay digest.

11. LINEAGE IS NOT OPTIONAL
   - Evidence may be summarized for humans, but machine contracts must preserve source lineage.
   - No citation, no source, no span, no promotion.

12. ROLLBACK IS PART OF THE CHANGE
   - Every promoted update must carry a rollback handle.
   - Rollback path must be tested before broad activation.
   - "We can manually fix it later" is not a rollback plan.


===================================================================================================================
                                 V7 CONTRACT OWNERSHIP MAP
===================================================================================================================

┌──────────────────────────────┬───────────────────────────────────────────────────────────────────────────────────┐
│ STEP                         │ AUTHORITATIVE CONTRACT / ENGINE FAMILY                                             │
├──────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────┤
│ S1A Gather Exhaust           │ telemetry consumer, historical ingestion, OTel store adapter, prompt tracer        │
│ S1B Normalize Evidence       │ trace feature extractor, meta-learning inbox, lineage binder, schema normalizer    │
│ S1C Observer Law             │ surface isolation validator, stage barrier enforcer, invariant checker            │
│ S1D Evidence Readiness Gate  │ eval-readiness classifier, evidence completeness checker, missing-field detector   │
│ S2A Outcome Evals            │ outcome evaluator, groundedness evaluator, citation/support scorer                 │
│ S2B Trajectory Evals         │ trajectory evaluator, trace rubric scorer, retry/thrash detector                   │
│ S2C Governance Regression    │ gate regression checker, prompt drift detector, shadow drift analyzer              │
│ S2D Human Calibration        │ human calibration engine, HITL decision logger, golden-set review                  │
│ S2E Eval Record Seal         │ eval record signer, rubric hash binder, immutable score bundle writer              │
│ S3A Signal Fusion            │ signal aggregator, signal grouping, BUS P / BUS T fusion                           │
│ S3B Incident RCA             │ RCA engine, cluster analyzer, pattern analysis, first-bad-span localizer           │
│ S3C Pattern Synthesis        │ pattern miner, drift clusterer, incident deduper, recurrence scorer                │
│ S3D Rule Drafting            │ prompt proposer, policy proposer, rubric/config/retrieval-profile proposer         │
│ S3E Proposal Admission Gate  │ proposal completeness checker, blast-radius reviewer, test-plan validator          │
│ S4A Gauntlet                 │ approval gauntlet, deterministic replay, regression runner, retrieval replay check │
│ S4B Approve / Reject         │ approval gate, system-learning admission gate, eval freshness gate                 │
│ S4C UWG Master Clerk         │ L4 state writer, L4 audit reader, L4 version store                                 │
│ S4D Ledger Proof             │ replay binding, state digest, startup integrity, rollout receipt generator          │
│ S4E Future-Run Publish       │ BUS U publisher, alias activator, future-run manifest distributor                   │
└──────────────────────────────┴───────────────────────────────────────────────────────────────────────────────────┘


===================================================================================================================
                                 V7 FAILURE MODES AND CONTAINMENT
===================================================================================================================

┌──────────────────────────────┬──────────────────────────────────────┬──────────────────────────────────────────────┐
│ FAILURE MODE                 │ WHAT IT LOOKS LIKE                    │ CONTAINMENT                                  │
├──────────────────────────────┼──────────────────────────────────────┼──────────────────────────────────────────────┤
│ Stale ingest                 │ traces arrive late                    │ mark stale, block learning until refreshed   │
│ Orphan evidence              │ artifact lacks trace/run link         │ hold, request telemetry repair               │
│ Eval gap                     │ run has no completed eval             │ block 6C/6D                                  │
│ Forced certainty             │ judge refuses Unknown                 │ calibration failure, block rubric            │
│ Preference overfitting       │ likes/dislikes become policy          │ require rubric + SME calibration             │
│ RCA vagueness                │ "model bad" with no surface           │ hold proposal                                │
│ False promote                │ gauntlet passes unsafe change         │ rollback, mark gauntlet regression           │
│ Shadow writer                │ non-UWG mutation detected             │ freeze, sovereignty incident                 │
│ Stale eval on write          │ old eval used for new commit          │ UWG reject                                   │
│ Partial bypass               │ one failed stage ignored              │ reject unless ADR exception                  │
│ Current-run mutation         │ learning changes live behavior        │ fatal invariant breach                       │
│ Rollback missing             │ promoted update cannot be reverted    │ reject promotion                             │
│ Cache contamination          │ bad exemplar/cache reused broadly     │ disable surface, purge cache, RCA            │
│ Rubric drift                 │ grader changes without calibration    │ hold evals, recalibrate                      │
│ Replay nonlocalization       │ replay fails but cannot isolate span  │ block promotion, improve instrumentation     │
└──────────────────────────────┴──────────────────────────────────────┴──────────────────────────────────────────────┘


===================================================================================================================
                                 V7 PROMOTION PACKET SCHEMA
===================================================================================================================

PromotionPacket
- proposal_id
- proposal_type
- target_surface
- target_version_current
- target_version_proposed
- proposed_diff
- content_hash
- signer_identity
- owner
- policy_hash
- eval_record_id
- outcome_eval_ref
- trajectory_eval_ref
- governance_eval_ref
- calibration_ref
- RCA_packet_id
- incident_ids[]
- pattern_ids[]
- evidence_links[]
  - trace_id
  - span_id
  - run_id
  - replay_key
  - artifact_hash
  - source_id
  - cited_span
- root_cause_class
- first_bad_span
- expected_effect
- affected_surfaces[]
- blast_radius
- regression_pack_ids[]
- golden_set_ids[]
- gauntlet_receipt
- rollout_plan
- rollback_plan
- activation_policy
  - future_run_only = true
  - activate_at = next_run_start
  - canary_scope
  - TTL_review_date
- approval_decision_id
- UWG_receipt_id
- L4_version_digest
- BUS_U_activation_receipt


===================================================================================================================
                                 V7 ONE-LINE MENTAL MODEL
===================================================================================================================

Runtime ends
   -> L6 reads the sealed tapes
   -> L6 normalizes the evidence
   -> L6 grades the outcome, path, and guardrails
   -> L6 calibrates graders against humans and golden sets
   -> L6 fuses evaluated signals
   -> L6 investigates root causes
   -> L6 drafts bounded fixes
   -> gauntlet proves safety
   -> approval gate accepts or holds the packet
   -> UWG commits approved changes
   -> L4 stores durable truth
   -> BUS U updates only future runs.

[!] FINAL INVARIANT:
    Observe -> Normalize -> Evaluate -> Calibrate -> RCA -> Propose -> Prove -> UWG Commit -> Future Run.
    Never: Observe -> Mutate Live Run.
===================================================================================================================