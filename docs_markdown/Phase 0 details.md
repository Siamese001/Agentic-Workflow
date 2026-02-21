===================================================================================================
                  L0: CORE LOGIC & ROUTING — INGESTION DRILLDOWN
                  (THE AUTHORITY NODE: LOGIC, ARBITRATION & DISPATCH)
===================================================================================================

       [ INGRESS FROM L1 ]                               [ INGRESS FROM L6 ]
    (The Proposal: "I want to...")                    (The Signal: "System looks...")
              |                                                 |
              v                                                 v
+-----------------------------------+             +-----------------------------------+
| L1 INPUT STREAM                   |             | L6 INPUT STREAM                   |
|-----------------------------------|             |-----------------------------------|
| > intent_vector (Embedding)       |             | > anomaly_score (Float 0-1)       |
| > tool_candidates (List[Tools])   |             | > drift_metric (Delta)            |
| > est_complexity (Int)            |             | > injection_flag (Bool)           |
| > raw_reasoning (Chain-of-Thought)|             | > context_usage (%)               |
+-----------------------------------+             +-----------------------------------+
              |                                                 |
              +-----------------------+-------------------------+
                                      |
                                      v
==========================================================================================
  PHASE 1: CONTEXTUAL INGESTION & ENRICHMENT
==========================================================================================
+-------------------------------------------------------+    ( READ: Global Config )     +-------------------------------------------+
| CONTEXTUAL ROUTER (INGEST)                            | <============================> | L4: ROUTING STATE & CONFIG                |
|-------------------------------------------------------|    ( READ: Trace ID State )    |-------------------------------------------|
| 1. Assigns Immutable Trace_ID                         |                                | - Routing Weights / Rules                 |
| 2. Attaches Current "Policy Hash" (Version Control)   |                                | - Active Capability Inventory             |
| 3. Correlates (L1.Intent) with (L6.Anomaly)           |                                | - System Budget Status                    |
|                                                       |                                | - Global Stop-Switches                    |
| Output: Structured Context Object                     |                                |                                           |
+-------------------------------------------------------+                                | * Prevents routing to dead services       |
                 |                                                                       | * Enforces global system pauses           |
                 v                                                                       +-------------------------------------------+
==========================================================================================
  PHASE 2: ROUTER ELECTION (THE DECISION ENGINE)
==========================================================================================
+-------------------------------------------------------+                                                      ^
| ROUTER ELECTION ENGINE                                |                                                      |
|-------------------------------------------------------|                                                      |
| Determines *HOW* the decision is made based on data.  |                                                      |
|                                                       |                                                      |
|    [ OPTION A: DETERMINISTIC RULESET ]                |                                                      |
|    IF (L6.anomaly < 0.1) AND (L1.complexity < 3)      |                                                      |
|    THEN -> Force Path A (Fast Lane)                   |                                                      |
|                                                       |                                                      |
|    [ OPTION B: LEARNED ROUTER (ML) ]                  |                                                      |
|    IF (L1.ambiguity > 0.5) OR (L1.tools > 1)          |                                                      |
|    THEN -> Consult Routing Model (L4)                 |                                                      |
|                                                       |                                                      |
|    [ OPTION C: GUARDIAN INTERVENTION ]                |                                                      |
|    IF (L6.injection_flag == TRUE)                     |                                                      |
|    THEN -> Force Path D (Human Review / Block)        |                                                      |
+-------------------------------------------------------+                                                      |
                 |                                                                                             |
                 v                                                                                             |
==========================================================================================                     |
  PHASE 3: CAPABILITY ARBITRATION (RESOURCE CHECK)                                                             |
==========================================================================================                     |
+-------------------------------------------------------+                                                      |
| CAPABILITY ARBITRATION                                |                                                      |
|-------------------------------------------------------|                                                      |
| * Before dispatch, can we actually do this?           |                                                      |
|                                                       |                                                      |
| 1. Tool Inventory Check (Is L1.tool_list valid?)      |          ( READ: Tool Availability )                 |
| 2. Budget Forecasting (Cost vs Remaining Budget)      | <====================================================+
| 3. Rate Limit Check (Are we throttled?)               |
|                                                       |
| IF FAIL -> Reject to L1 (Retry/Replan)                |
| IF PASS -> Proceed to Dispatch                        |
+-------------------------------------------------------+
                 |
                 v
==========================================================================================
  PHASE 4: POLICY-AWARE DISPATCH
==========================================================================================
+-------------------------------------------------------+    ( WRITE: Routing Decisions )    +-------------------------------------------+
| DISPATCHER (FINAL HOP)                                | =================================> | L4: ROUTING TELEMETRY                     |
|-------------------------------------------------------|    ( WRITE: Rejection Metrics )    |-------------------------------------------|
| 1. Stamps Final "Route Mode" on Artifact              |                                    | - Decision Confidence Scores              |
| 2. Encrypts/Seals the Decision Object                 |                                    | - Route Distribution (A/B/C/D)            |
| 3. Emits to specific downstream queue                 |                                    | - Capability Failures                     |
|                                                       |                                    |                                           |
| Output: "Signed Execution Plan"                       |                                    | * Feeds RLHF for Router Improvement       |
+-------------------------------------------------------+                                    | * Tuning data for Budget Forecasting      |
        /           |            |           \                                               +-------------------------------------------+
       /            |            |            \
      v             v            v             v
+===========+ +===========+ +===========+ +===========+
| TO PATH A | | TO PATH B | | TO PATH C | | TO PATH D |
| (Read)    | | (Rules)   | | (Exec)    | | (Human)   |
+===========+ +===========+ +===========+ +===========+
