# L2 Coverage Matrix — Evidence Audit

Cross-checks every PASS / DOC_ONLY classification in `COVERAGE_MATRIX.md` against seven weak-evidence patterns. A flagged row is not necessarily wrong — it is a row whose PASS verdict the matrix builder cannot defend rigorously.

## Summary

| Gap class | Count | Severity | Meaning |
|---|---:|:---:|---|
| G1 shared-evidence collision | 71 | medium | one line covers ≥5 reqs |
| G2 generic-identifier match | 22 | high | PASS via stop-listed token |
| G3 FAIL_CLOSED no test | 0 | high | invariant has no exercising test |
| G4 TEST function missing | 0 | high | spec demands a named test, missing |
| G5 STATE without test | 12 | medium | state-machine req has no test binding |
| G6 SPAN registered but unemitted | 4 | medium | declared in registry, no producer |
| G7 DOC_ONLY but code-bindable | 7 | low | matrix downgraded a real binding |

## G1 — Shared-evidence collisions (≥5 reqs per line)

| Evidence line | Req count | First few req_ids |
|---|---:|---|
| `agentic_core/L2_execution/enforcement/anti_bypass_guards.py:87` | 9 | `04.0_L2_Sequencer_Orchestrator_Contract#STATE#023`, `04.1_L2_Execution_Entry_Authority_and_Packet_Intake#POLICY_DENY#004`, `04.2_L2_E1_Prep_Frozen_Execution_Room#POLICY_DENY#004`, … |
| `tests/unit/agentic_core/L2_execution/test_l2_anti_bypass.py:45` | 9 | `04.0_L2_Sequencer_Orchestrator_Contract#STATE#023`, `04.1_L2_Execution_Entry_Authority_and_Packet_Intake#POLICY_DENY#004`, `04.2_L2_E1_Prep_Frozen_Execution_Room#POLICY_DENY#004`, … |
| `agentic_core/L2_execution/enforcement/agent_seal_helper.py:104` | 9 | `04.0_L2_Sequencer_Orchestrator_Contract#CONTRACT#050`, `04.1_L2_Execution_Entry_Authority_and_Packet_Intake#POLICY_DENY#023`, `04.2_L2_E1_Prep_Frozen_Execution_Room#POLICY_DENY#023`, … |
| `agentic_core/L2_execution/enforcement/anti_bypass_guards.py:247` | 9 | `04.0_L2_Sequencer_Orchestrator_Contract#CONTRACT#050`, `04.1_L2_Execution_Entry_Authority_and_Packet_Intake#POLICY_DENY#023`, `04.2_L2_E1_Prep_Frozen_Execution_Room#POLICY_DENY#023`, … |
| `tests/unit/agentic_core/L2_execution/test_agent_seal_helper.py:57` | 9 | `04.0_L2_Sequencer_Orchestrator_Contract#CONTRACT#050`, `04.1_L2_Execution_Entry_Authority_and_Packet_Intake#POLICY_DENY#023`, `04.2_L2_E1_Prep_Frozen_Execution_Room#POLICY_DENY#023`, … |
| `tests/unit/agentic_core/L2_execution/test_exemplar_agents.py:80` | 9 | `04.0_L2_Sequencer_Orchestrator_Contract#CONTRACT#050`, `04.1_L2_Execution_Entry_Authority_and_Packet_Intake#POLICY_DENY#023`, `04.2_L2_E1_Prep_Frozen_Execution_Room#POLICY_DENY#023`, … |
| `agentic_core/L2_execution/enforcement/agent_seal_helper.py:28` | 9 | `04.0_L2_Sequencer_Orchestrator_Contract#WORKSTEP#017`, `04.1_L2_Execution_Entry_Authority_and_Packet_Intake#POLICY_DENY#022`, `04.2_L2_E1_Prep_Frozen_Execution_Room#POLICY_DENY#022`, … |
| `agentic_core/L2_execution/orchestration/l2_phase_pipeline.py:506` | 9 | `04.0_L2_Sequencer_Orchestrator_Contract#WORKSTEP#017`, `04.1_L2_Execution_Entry_Authority_and_Packet_Intake#POLICY_DENY#022`, `04.2_L2_E1_Prep_Frozen_Execution_Room#POLICY_DENY#022`, … |
| `tests/unit/agentic_core/L2_execution/test_agent_seal_helper.py:19` | 9 | `04.0_L2_Sequencer_Orchestrator_Contract#WORKSTEP#017`, `04.1_L2_Execution_Entry_Authority_and_Packet_Intake#POLICY_DENY#022`, `04.2_L2_E1_Prep_Frozen_Execution_Room#POLICY_DENY#022`, … |
| `tests/unit/agentic_core/L2_execution/test_exemplar_agents.py:28` | 9 | `04.0_L2_Sequencer_Orchestrator_Contract#WORKSTEP#017`, `04.1_L2_Execution_Entry_Authority_and_Packet_Intake#POLICY_DENY#022`, `04.2_L2_E1_Prep_Frozen_Execution_Room#POLICY_DENY#022`, … |
| `agentic_core/L2_execution/orchestration/l2_phase_pipeline.py:110` | 9 | `04.0_L2_Sequencer_Orchestrator_Contract#FAIL_CLOSED#008`, `04.1_L2_Execution_Entry_Authority_and_Packet_Intake#POLICY_DENY#021`, `04.2_L2_E1_Prep_Frozen_Execution_Room#POLICY_DENY#021`, … |
| `agentic_core/L2_execution/orchestration/l2_sequencer_adapter.py:22` | 9 | `04.0_L2_Sequencer_Orchestrator_Contract#FAIL_CLOSED#008`, `04.1_L2_Execution_Entry_Authority_and_Packet_Intake#POLICY_DENY#021`, `04.2_L2_E1_Prep_Frozen_Execution_Room#POLICY_DENY#021`, … |
| `tests/unit/agentic_core/L2_execution/test_l2_anti_bypass.py:267` | 9 | `04.0_L2_Sequencer_Orchestrator_Contract#FAIL_CLOSED#008`, `04.1_L2_Execution_Entry_Authority_and_Packet_Intake#POLICY_DENY#021`, `04.2_L2_E1_Prep_Frozen_Execution_Room#POLICY_DENY#021`, … |
| `tests/unit/agentic_core/L2_execution/test_l2_doctrine_edge_cases.py:966` | 9 | `04.0_L2_Sequencer_Orchestrator_Contract#FAIL_CLOSED#008`, `04.1_L2_Execution_Entry_Authority_and_Packet_Intake#POLICY_DENY#021`, `04.2_L2_E1_Prep_Frozen_Execution_Room#POLICY_DENY#021`, … |
| `agentic_core/L2_execution/enforcement/anti_bypass_guards.py:12` | 8 | `04.1_L2_Execution_Entry_Authority_and_Packet_Intake#POLICY_DENY#001`, `04.2_L2_E1_Prep_Frozen_Execution_Room#POLICY_DENY#001`, `04.3_L2_E2_Valid_Work_Order_and_Gate_Check#POLICY_DENY#001`, … |
| `tests/unit/agentic_core/L2_execution/test_l2_anti_bypass.py:42` | 8 | `04.1_L2_Execution_Entry_Authority_and_Packet_Intake#POLICY_DENY#001`, `04.2_L2_E1_Prep_Frozen_Execution_Room#POLICY_DENY#001`, `04.3_L2_E2_Valid_Work_Order_and_Gate_Check#POLICY_DENY#001`, … |
| `tests/unit/agentic_core/L2_execution/test_l2_doctrine_exhaustive.py:894` | 8 | `04.1_L2_Execution_Entry_Authority_and_Packet_Intake#POLICY_DENY#001`, `04.2_L2_E1_Prep_Frozen_Execution_Room#POLICY_DENY#001`, `04.3_L2_E2_Valid_Work_Order_and_Gate_Check#POLICY_DENY#001`, … |
| `agentic_core/L2_execution/enforcement/anti_bypass_guards.py:85` | 8 | `04.1_L2_Execution_Entry_Authority_and_Packet_Intake#POLICY_DENY#002`, `04.2_L2_E1_Prep_Frozen_Execution_Room#POLICY_DENY#002`, `04.3_L2_E2_Valid_Work_Order_and_Gate_Check#POLICY_DENY#002`, … |
| `agentic_core/L2_execution/enforcement/capability_chokepoint.py:5` | 8 | `04.1_L2_Execution_Entry_Authority_and_Packet_Intake#POLICY_DENY#002`, `04.2_L2_E1_Prep_Frozen_Execution_Room#POLICY_DENY#002`, `04.3_L2_E2_Valid_Work_Order_and_Gate_Check#POLICY_DENY#002`, … |
| `tests/unit/agentic_core/L2_execution/test_l2_anti_bypass.py:43` | 8 | `04.1_L2_Execution_Entry_Authority_and_Packet_Intake#POLICY_DENY#002`, `04.2_L2_E1_Prep_Frozen_Execution_Room#POLICY_DENY#002`, `04.3_L2_E2_Valid_Work_Order_and_Gate_Check#POLICY_DENY#002`, … |
| `tests/unit/agentic_core/L2_execution/test_l2_doctrine_exhaustive.py:895` | 8 | `04.1_L2_Execution_Entry_Authority_and_Packet_Intake#POLICY_DENY#002`, `04.2_L2_E1_Prep_Frozen_Execution_Room#POLICY_DENY#002`, `04.3_L2_E2_Valid_Work_Order_and_Gate_Check#POLICY_DENY#002`, … |
| `agentic_core/L2_execution/enforcement/anti_bypass_guards.py:86` | 8 | `04.1_L2_Execution_Entry_Authority_and_Packet_Intake#POLICY_DENY#003`, `04.2_L2_E1_Prep_Frozen_Execution_Room#POLICY_DENY#003`, `04.3_L2_E2_Valid_Work_Order_and_Gate_Check#POLICY_DENY#003`, … |
| `tests/unit/agentic_core/L2_execution/test_l2_anti_bypass.py:44` | 8 | `04.1_L2_Execution_Entry_Authority_and_Packet_Intake#POLICY_DENY#003`, `04.2_L2_E1_Prep_Frozen_Execution_Room#POLICY_DENY#003`, `04.3_L2_E2_Valid_Work_Order_and_Gate_Check#POLICY_DENY#003`, … |
| `tests/unit/agentic_core/L2_execution/test_l2_sequencer_contract.py:208` | 8 | `04.1_L2_Execution_Entry_Authority_and_Packet_Intake#POLICY_DENY#003`, `04.2_L2_E1_Prep_Frozen_Execution_Room#POLICY_DENY#003`, `04.3_L2_E2_Valid_Work_Order_and_Gate_Check#POLICY_DENY#003`, … |
| `agentic_core/L2_execution/enforcement/anti_bypass_guards.py:88` | 8 | `04.1_L2_Execution_Entry_Authority_and_Packet_Intake#POLICY_DENY#005`, `04.2_L2_E1_Prep_Frozen_Execution_Room#POLICY_DENY#005`, `04.3_L2_E2_Valid_Work_Order_and_Gate_Check#POLICY_DENY#005`, … |

_Showing first 25 of 71._


## G2 — Generic-identifier PASS matches (high severity)

| req_id | identifier | bullet |
|---|---|---|
| `04.0_L2_Sequencer_Orchestrator_Contract#STATE#021` | `(none)` | any L2 state -> L0 route selection |
| `04.0_L2_Sequencer_Orchestrator_Contract#STATE#022` | `(none)` | any L2 state -> C0 retrieval unless pre-authorized as the current bounded tool/read action |
| `04.0_L2_Sequencer_Orchestrator_Contract#STATE#023` | `HITL` | any L2 state -> direct HITL request |
| `04.0_L2_Sequencer_Orchestrator_Contract#STATE#024` | `(none)` | any L2 state -> L4 write |
| `04.0_L2_Sequencer_Orchestrator_Contract#STATE#025` | `(none)` | any L2 state -> L6 learning mutation |
| `04.0_L2_Sequencer_Orchestrator_Contract#WORKSTEP#004` | `(none)` | E1 must freeze execution context before validation or execution. |
| `04.0_L2_Sequencer_Orchestrator_Contract#WORKSTEP#006` | `PASS` | E2 must return PASS before any model/tool/script/action lane is invoked. |
| `04.0_L2_Sequencer_Orchestrator_Contract#WORKSTEP#007` | `Seal` | If E2 fails, sequencer sends rejection to E5 Seal without calling E3. |
| `04.0_L2_Sequencer_Orchestrator_Contract#WORKSTEP#008` | `(none)` | E3 may run only one bounded attempt. |
| `04.0_L2_Sequencer_Orchestrator_Contract#FAIL_CLOSED#003` | `PASS` | E2 PASS missing before E3. |
| `04.0_L2_Sequencer_Orchestrator_Contract#FAIL_CLOSED#009` | `Exit` | L2 tries to emit Exit disposition or UWG commit request. |
| `04.10_L2_Verify_Then_Execute_Local_Critique#POLICY_ALLOW#001` | `High` | High-cost or high-risk model/tool/script invocation. |
| `04.10_L2_Verify_Then_Execute_Local_Critique#POLICY_ALLOW#004` | `Tool` | Tool argument construction where wrong args would create side effects. |
| `04.1_L2_Execution_Entry_Authority_and_Packet_Intake#POLICY_DENY#002` | `DENY` | DENY |
| `04.2_L2_E1_Prep_Frozen_Execution_Room#POLICY_DENY#002` | `DENY` | DENY |
| `04.3_L2_E2_Valid_Work_Order_and_Gate_Check#POLICY_DENY#002` | `DENY` | DENY |
| `04.4_L2_E3_Exec_Attempt_Lanes_and_Sandbox_Run#POLICY_DENY#002` | `DENY` | DENY |
| `04.5_L2_E4_Heal_Same_Authority_Repair_Governor#POLICY_DENY#002` | `DENY` | DENY |
| `04.6_L2_E5_Seal_Artifact_and_Dispatch#POLICY_DENY#002` | `DENY` | DENY |
| `04.7_L2_Programmatic_Tool_Calling_PTC_Sandbox#POLICY_DENY#002` | `DENY` | DENY |
| `04.8_L2_Observability_Replay_Anti_Bypass_Tests#POLICY_DENY#002` | `DENY` | DENY |
| `04.9_L2_StateDiffCandidate_and_Mutation_Intent#HANDOFF#002` | `Exit` | 05 Exit may consume candidate refs to evaluate X1J write eligibility. |

## G3 — FAIL_CLOSED requirements without test evidence (high severity)

_None._


## G4 — TEST requirements with no matching test function (high severity)

_None._


## G5 — STATE requirements without test binding (medium severity)

| req_id | bullet |
|---|---|
| `04.0_L2_Sequencer_Orchestrator_Contract#STATE#005` | LOCAL_REPAIR_EVALUATION |
| `04.0_L2_Sequencer_Orchestrator_Contract#STATE#007` | SEALING_SUCCESS |
| `04.0_L2_Sequencer_Orchestrator_Contract#STATE#008` | SEALING_DEGRADED_SUCCESS |
| `04.0_L2_Sequencer_Orchestrator_Contract#STATE#009` | SEALING_NEEDS_HELP |
| `04.0_L2_Sequencer_Orchestrator_Contract#STATE#015` | EXECUTING -> SUCCESS -> SEALING_SUCCESS |
| `04.0_L2_Sequencer_Orchestrator_Contract#STATE#016` | EXECUTING -> DEGRADED_SUCCESS -> SEALING_DEGRADED_SUCCESS |
| `04.0_L2_Sequencer_Orchestrator_Contract#STATE#017` | EXECUTING -> SOFT_REPAIRABLE -> LOCAL_REPAIR_EVALUATION |
| `04.0_L2_Sequencer_Orchestrator_Contract#STATE#018` | LOCAL_REPAIR_EVALUATION -> E4_HEAL -> RETRYING_SAME_AUTHORITY or SEALING_NEEDS_HELP or SE… |
| `04.0_L2_Sequencer_Orchestrator_Contract#STATE#021` | any L2 state -> L0 route selection |
| `04.0_L2_Sequencer_Orchestrator_Contract#STATE#022` | any L2 state -> C0 retrieval unless pre-authorized as the current bounded tool/read action |
| `04.0_L2_Sequencer_Orchestrator_Contract#STATE#024` | any L2 state -> L4 write |
| `04.0_L2_Sequencer_Orchestrator_Contract#STATE#025` | any L2 state -> L6 learning mutation |

## G6 — OTEL spans registered but never emitted (medium severity)

| req_id | span | bullet |
|---|---|---|
| `04.2_L2_E1_Prep_Frozen_Execution_Room#SPAN#002` | `l2.e1.prep.authority_bind` | l2.e1.prep.authority_bind |
| `04.2_L2_E1_Prep_Frozen_Execution_Room#SPAN#003` | `l2.e1.prep.environment_freeze` | l2.e1.prep.environment_freeze |
| `04.8_L2_Observability_Replay_Anti_Bypass_Tests#SPAN#002` | `l2.e1.prep.authority_bind` | l2.e1.prep.authority_bind |
| `04.8_L2_Observability_Replay_Anti_Bypass_Tests#SPAN#003` | `l2.e1.prep.environment_freeze` | l2.e1.prep.environment_freeze |

## G7 — DOC_ONLY rows that should bind to code (low severity)

| req_id | identifier | bullet |
|---|---|---|
| `04.0_L2_Sequencer_Orchestrator_Contract#OWNERSHIP_NEG#001` | `Route` | Route choice, route re-entry, or workflow expansion. |
| `04.0_L2_Sequencer_Orchestrator_Contract#OWNERSHIP_NEG#002` | `Retrieval` | Retrieval, prompt assembly, or final output approval. |
| `04.0_L2_Sequencer_Orchestrator_Contract#OWNERSHIP_NEG#003` | `Runtime` | Runtime Gate law or final X3 disposition. |
| `04.1_L2_Execution_Entry_Authority_and_Packet_Intake#OWNERSHIP_NEG#008` | `Assembly` | Prompt Assembly |
| `04.3_L2_E2_Valid_Work_Order_and_Gate_Check#OWNERSHIP_NEG#005` | `Runtime` | Runtime Gate final disposition |
| `04.8_L2_Observability_Replay_Anti_Bypass_Tests#OWNERSHIP_NEG#002` | `Runtime` | Runtime Gate G01-G29 definitions |
| `04.9_L2_StateDiffCandidate_and_Mutation_Intent#OWNERSHIP_NEG#003` | `Write` | Write lock acquisition. |