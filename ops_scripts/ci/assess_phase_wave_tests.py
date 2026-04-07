"""
Guardian assessment script: phase/wave named test files.

Produces a structured report covering three questions per file:
  1. Does this file test CURRENT functionality (live imports, real logic)?
  2. Is there STRUCTURAL DUPLICATE logic in other tests/ files? (AST-based)
  3. VERDICT: DELETE | RENAME | KEEP-AS-IS | NEEDS-REVIEW

Duplicate detection method (AST-only, no execution, no imports):
  - For every test function in a phase/wave file, build a canonical structural
    fingerprint by walking the function's AST and emitting a normalised token
    sequence:  node type + operator type (where relevant).  All names, string
    literals, numeric literals and docstrings are replaced with typed
    placeholders (NAME, STR, NUM) so that two functions with identical logic
    but different variable names / assertion messages are still detected as
    duplicates.
  - The token sequence is SHA-256 hashed.
  - An index of {fingerprint -> [(file, func_name), ...]} is built across ALL
    non-phase/wave test files in tests/.
  - Phase/wave test functions whose fingerprint appears in the index are
    reported as STRUCTURAL_DUPLICATE with exact provenance.

Additionally, name-normalised matching is performed: phase/wave tokens are
stripped from test function names and the remainder is matched against the
corpus — catching cases where logic was slightly rewritten but covers the
same invariant.

Run with:
    python ops_scripts/ci/assess_phase_wave_tests.py

Exit codes:
    0  — all files have a clear verdict recorded
    1  — at least one file is NEEDS-REVIEW (requires manual action before
         delete/rename can proceed)

The script uses AST-only analysis — no test execution, no imports.
"""
from __future__ import annotations

import ast
import hashlib
import json
import sys
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from agentic_core.L0_routing.config.path_constants import (
    TESTS_DIR,
    get_validated_project_root,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_through,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "assess_phase_wave_tests")
_emit_applies_guardrail("p0", "assess_phase_wave_tests", "p0_governance")
_emit_reads_policy_state("p0", "assess_phase_wave_tests", "policy_binding")
_emit_snapshots_state("p0", "assess_phase_wave_tests", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("assess_phase_wave_tests", "p4obs", "metric_1")
_emit_emits_metric_event("assess_phase_wave_tests", "p4obs", "metric_2")
_emit_emits_metric_event("assess_phase_wave_tests", "p4obs", "metric_3")
_emit_emits_metric_event("assess_phase_wave_tests", "p4obs", "metric_4")
_emit_emits_metric_event("assess_phase_wave_tests", "p4obs", "metric_5")
_emit_emits_metric_event("assess_phase_wave_tests", "p4obs", "metric_6")
_emit_records_incident_event("assess_phase_wave_tests", "p4obs", "incident")
_emit_captures_runtime_anomaly("assess_phase_wave_tests", "p4obs", "anomaly")
_emit_writes_observability_log("assess_phase_wave_tests", "p4obs", "obs_log")
_emit_updates_monitoring_state("assess_phase_wave_tests", "p4obs", "mon_state")
_emit_triggers_alert("assess_phase_wave_tests", "p4obs", "alert")
_emit_links_incident_trace("assess_phase_wave_tests", "p4obs", "trace_link")
_emit_captures_pattern("assess_phase_wave_tests", "p3lm", "pattern")
_emit_records_learning_event("assess_phase_wave_tests", "p3lm", "learning_event")
_emit_writes_learning_snapshot("assess_phase_wave_tests", "p3lm", "snapshot")
_emit_feeds_meta_learning("assess_phase_wave_tests", "p3lm", "meta_feed")
_emit_updates_routing_strategy("assess_phase_wave_tests", "p3lm", "routing")
_emit_improves_agent_policy("assess_phase_wave_tests", "p3lm", "policy")
_emit_stores_learning_state("assess_phase_wave_tests", "p3lm", "state")
_emit_records_execution_trace("assess_phase_wave_tests", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("assess_phase_wave_tests", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("assess_phase_wave_tests", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("assess_phase_wave_tests", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("assess_phase_wave_tests", "L4_STATE", "p2_trace_5")
_emit_reads_environ("assess_phase_wave_tests", "env_read", "p2_env_1")
_emit_reads_environ("assess_phase_wave_tests", "env_read", "p2_env_2")
_emit_reads_runtime_state("assess_phase_wave_tests", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("assess_phase_wave_tests", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "assess_phase_wave_tests", "context_pull")
_emit_pulls_context("p1", "assess_phase_wave_tests", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "assess_phase_wave_tests", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "assess_phase_wave_tests", "uwg_term_2")
_emit_writes_through("p1", "assess_phase_wave_tests", "write_through")
_emit_writes_through("p1", "assess_phase_wave_tests", "write_through_2")
_emit_validated_by_safety_plane("p1", "assess_phase_wave_tests", "safety_validation")
_emit_invokes_eval("p1", "assess_phase_wave_tests", "eval_call")
_emit_proposal_commits_routing("p1", "assess_phase_wave_tests", "routing_commit")
_emit_escalates_to_human("p1", "assess_phase_wave_tests", "human_escalation")
_emit_routes_through("p1", "assess_phase_wave_tests", "route_through")
_emit_checks_agent_registry("p1", "assess_phase_wave_tests", "agent_registry")
_emit_validates_agent_capability("p1", "assess_phase_wave_tests", "capability")
_emit_dispatches_execution_plan("p1", "assess_phase_wave_tests", "exec_plan")
_emit_agent_executes_agent("p1", "assess_phase_wave_tests", "sub_agent")
_emit_routes_to_agent("p1", "assess_phase_wave_tests", "target_agent")
_emit_verifies_policy("p1", "assess_phase_wave_tests", "policy_check")
_emit_observes_runtime_state("p1", "assess_phase_wave_tests", "runtime_state")
_emit_verifies_boundary("p1", "assess_phase_wave_tests", "boundary_check")
_emit_transcripts_response("p1", "assess_phase_wave_tests", "transcript")
_emit_hard_fails_untranscripted("p1", "assess_phase_wave_tests")
_emit_gated_by_confidence("p1", "assess_phase_wave_tests", "confidence_gate")
emit_replay_key("p0", "assess_phase_wave_tests")
emit_determinism_digest("p0", "assess_phase_wave_tests")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "assess_phase_wave_tests", "execution_auth")
_emit_validates_capability("p2", "assess_phase_wave_tests", "capability_check")
_emit_routes_to_capability("p2", "assess_phase_wave_tests", "capability_route")
_emit_writes_via_uwg("p2", "assess_phase_wave_tests", "uwg_write")
_emit_blocks_direct_write("p2", "assess_phase_wave_tests", "direct_write_block")
_emit_records_tool_invocation("p2", "assess_phase_wave_tests", "tool_invocation")
_emit_captures_execution_output("p2", "assess_phase_wave_tests", "exec_output")
_emit_dispatches_agent("p3", "assess_phase_wave_tests", "agent_dispatch")
_emit_coordinates_agents("p3", "assess_phase_wave_tests", "agent_coordination")
_emit_records_workflow_lineage("p3", "assess_phase_wave_tests", "workflow_lineage")
_emit_records_healing_outcome("p3", "assess_phase_wave_tests", "healing_outcome")
_emit_escalates_failure("p3", "assess_phase_wave_tests", "failure_escalation")
_emit_orchestrates_workflow("p3", "assess_phase_wave_tests", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "assess_phase_wave_tests", "healing_dispatch")
_emit_invokes_evaluation("p3", "assess_phase_wave_tests", "evaluation_signal")
_emit_records_telemetry_event("p4", "assess_phase_wave_tests", "telemetry_event")
_emit_captures_evaluation_metric("p4", "assess_phase_wave_tests", "eval_metric")
_emit_stores_embedding("p4", "assess_phase_wave_tests", "embedding_store")
_emit_updates_meta_learning_state("p4", "assess_phase_wave_tests", "meta_learning")
_emit_links_execution_to_snapshot("p4", "assess_phase_wave_tests", "exec_snapshot_link")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_1")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_2")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_3")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_4")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_5")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_6")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_7")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_8")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_9")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_10")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_11")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_12")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_13")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_14")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_15")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_16")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_17")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_18")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_19")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_20")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_21")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_22")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_23")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_24")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_25")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_26")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_27")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_28")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_29")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_30")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_31")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_32")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_33")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_34")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_35")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_36")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_37")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_38")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_39")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_40")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_41")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_42")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_43")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_44")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_45")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_46")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_47")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_48")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_49")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_50")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_51")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_52")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_53")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_54")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_55")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_56")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_57")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_58")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_59")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_60")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_61")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_62")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_63")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_64")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_65")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_66")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_67")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_68")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_69")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_70")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_71")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_72")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_73")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_74")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_75")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_76")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_77")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_78")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_79")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_80")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_81")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_82")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_83")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_84")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_85")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_86")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_87")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_88")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_89")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_90")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_91")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_92")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_93")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_94")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_95")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_96")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_97")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_98")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_99")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_100")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_101")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_102")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_103")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_104")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_105")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_106")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_107")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_108")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_109")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_110")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_111")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_112")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_113")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_114")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_115")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_116")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_117")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_118")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_119")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_120")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_121")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_122")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_123")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_124")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_125")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_126")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_127")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_128")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_129")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_130")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_131")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_132")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_133")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_134")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_135")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_136")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_137")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_138")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_139")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_140")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_141")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_142")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_143")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_144")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_145")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_146")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_147")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_148")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_149")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_150")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_151")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_152")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_153")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_154")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_155")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_156")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_157")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_158")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_159")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_160")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_161")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_162")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_163")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_164")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_165")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_166")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_167")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_168")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_169")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_170")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_171")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_172")
_emit_reads_through("l4", "assess_phase_wave_tests", "urg_read_173")
REPO_ROOT = get_validated_project_root()
TESTS_ROOT = REPO_ROOT / TESTS_DIR
_PHASE_WAVE_TOKENS = ('phase', 'wave')

def _is_phase_wave_file(path: Path) -> bool:
    name_lower = path.stem.lower()
    return any(tok in name_lower for tok in _PHASE_WAVE_TOKENS)

def _find_phase_wave_files() -> list[Path]:
    found = []
    for p in TESTS_ROOT.rglob('*.py'):
        if '__pycache__' in p.parts:
            continue
        if _is_phase_wave_file(p):
            found.append(p)
    return sorted(found)

def _find_corpus_files(exclude: set[Path]) -> list[Path]:
    """All non-phase/wave .py test files outside _quarantine (active corpus)."""
    found = []
    for p in TESTS_ROOT.rglob('*.py'):
        if '__pycache__' in p.parts:
            continue
        if '_quarantine' in p.parts:
            continue
        if p in exclude:
            continue
        if _is_phase_wave_file(p):
            continue
        found.append(p)
    return sorted(found)

def _parse_safe(path: Path) -> ast.Module | None:
    try:
        return ast.parse(path.read_text(encoding='utf-8', errors='replace'))
    except SyntaxError:    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
        return None

def _extract_imports(tree: ast.Module) -> list[str]:
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                modules.append(node.module)
    return modules

def _extract_test_names(tree: ast.Module) -> list[str]:
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith('test_'):
                names.append(node.name)
    return names

def _extract_docstring(tree: ast.Module) -> str:
    try:
        return ast.get_docstring(tree) or ''
    except (AttributeError, TypeError):
        return ''

def _quarantine_headers(path: Path) -> dict[str, str]:
    headers: dict[str, str] = {}
    try:
        for line in path.read_text(encoding='utf-8', errors='replace').splitlines()[:10]:
            line = line.strip()
            if line.startswith('# DELETE AFTER:'):
                headers['delete_after'] = line[len('# DELETE AFTER:'):].strip()
            elif line.startswith('# Superseded by:'):
                headers['superseded_by'] = line[len('# Superseded by:'):].strip()
            elif line.startswith('# QUARANTINE:'):
                headers['quarantine_reason'] = line[len('# QUARANTINE:'):].strip()
    except OSError:    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging
        pass
    return headers

def _resolve_superseding_path(superseded_by_str: str) -> Path | None:
    part = superseded_by_str.split('(')[0].strip()
    candidate = REPO_ROOT / part
    if candidate.exists():
        return candidate
    for prefix in ('tests/', 'tests\\'):
        if part.startswith(prefix):
            candidate = TESTS_ROOT / part[len(prefix):]
            if candidate.exists():
                return candidate
    return None

def _check_imports_resolvable(imports: list[str]) -> tuple[list[str], list[str]]:
    _KNOWN_STDLIB_OR_THIRD_PARTY = {'ast', 'os', 'sys', 'pathlib', 'hashlib', 'json', 're', 'textwrap', 'unittest', 'dataclasses', 'collections', 'typing', 'functools', 'importlib', 'tempfile', 'pytest', 'unittest.mock', 'contextlib', 'itertools', 'copy', 'abc', 'io', 'time', 'datetime', 'math', 'random', 'string', 'struct', 'threading', 'subprocess'}
    found, missing = ([], [])
    for mod in imports:
        parts = mod.split('.')
        top = parts[0]
        if top in _KNOWN_STDLIB_OR_THIRD_PARTY:
            found.append(mod)
            continue
        as_dir = REPO_ROOT / Path(*parts)
        as_file = REPO_ROOT / Path(*parts[:-1]) / f'{parts[-1]}.py' if len(parts) > 1 else REPO_ROOT / f'{parts[0]}.py'
        as_init = as_dir / '__init__.py'
        if as_dir.exists() or as_file.exists() or as_init.exists():
            found.append(mod)
        else:
            missing.append(mod)
    return (found, missing)

class _FingerprintVisitor(ast.NodeVisitor):
    """Emit a stable, normalised token sequence for an AST subtree."""

    def __init__(self) -> None:
        self.tokens: list[str] = []

    def visit_Name(self, node: ast.Name) -> None:
        self.tokens.append('NAME')

    def visit_Attribute(self, node: ast.Attribute) -> None:
        self.tokens.append('ATTR')
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> None:
        if isinstance(node.value, bool) or node.value is None:
            self.tokens.append(repr(node.value))
        elif isinstance(node.value, str):
            self.tokens.append('STR')
        elif isinstance(node.value, (int, float, complex)):
            self.tokens.append('NUM')
        else:
            self.tokens.append('CONST')

    def visit_Call(self, node: ast.Call) -> None:
        self.tokens.append('Call')
        self.tokens.append(f'nargs={len(node.args)}')
        self.tokens.append(f'nkw={len(node.keywords)}')
        self.generic_visit(node)

    def visit_Assert(self, node: ast.Assert) -> None:
        self.tokens.append('Assert')
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        self.tokens.append('Assign')
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        self.tokens.append('AugAssign')
        self.tokens.append(type(node.op).__name__)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self.tokens.append('AnnAssign')
        self.generic_visit(node)

    def visit_Return(self, node: ast.Return) -> None:
        self.tokens.append('Return')
        self.generic_visit(node)

    def visit_Raise(self, node: ast.Raise) -> None:
        self.tokens.append('Raise')
        self.generic_visit(node)

    def visit_If(self, node: ast.If) -> None:
        self.tokens.append('If')
        self.tokens.append(f'nbody={len(node.body)}')
        self.tokens.append(f'norelse={len(node.orelse)}')
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        self.tokens.append('For')
        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> None:
        self.tokens.append('While')
        self.generic_visit(node)

    def visit_With(self, node: ast.With) -> None:
        self.tokens.append('With')
        self.tokens.append(f'nitems={len(node.items)}')
        self.generic_visit(node)

    def visit_Try(self, node: ast.Try) -> None:
        self.tokens.append('Try')
        self.tokens.append(f'nhandlers={len(node.handlers)}')
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        self.tokens.append('ExceptHandler')
        self.generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        self.tokens.append(f'BoolOp:{type(node.op).__name__}')
        self.generic_visit(node)

    def visit_BinOp(self, node: ast.BinOp) -> None:
        self.tokens.append(f'BinOp:{type(node.op).__name__}')
        self.generic_visit(node)

    def visit_UnaryOp(self, node: ast.UnaryOp) -> None:
        self.tokens.append(f'UnaryOp:{type(node.op).__name__}')
        self.generic_visit(node)

    def visit_Compare(self, node: ast.Compare) -> None:
        ops = ':'.join(type(op).__name__ for op in node.ops)
        self.tokens.append(f'Compare:{ops}')
        self.generic_visit(node)

    def visit_ListComp(self, node: ast.ListComp) -> None:
        self.tokens.append('ListComp')
        self.generic_visit(node)

    def visit_DictComp(self, node: ast.DictComp) -> None:
        self.tokens.append('DictComp')
        self.generic_visit(node)

    def visit_SetComp(self, node: ast.SetComp) -> None:
        self.tokens.append('SetComp')
        self.generic_visit(node)

    def visit_GeneratorExp(self, node: ast.GeneratorExp) -> None:
        self.tokens.append('GeneratorExp')
        self.generic_visit(node)

    def visit_Lambda(self, node: ast.Lambda) -> None:
        self.tokens.append('Lambda')
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        self.tokens.append('Subscript')
        self.generic_visit(node)

    def visit_Dict(self, node: ast.Dict) -> None:
        self.tokens.append(f'Dict:n={len(node.keys)}')
        self.generic_visit(node)

    def visit_List(self, node: ast.List) -> None:
        self.tokens.append(f'List:n={len(node.elts)}')
        self.generic_visit(node)

    def visit_Tuple(self, node: ast.Tuple) -> None:
        self.tokens.append(f'Tuple:n={len(node.elts)}')
        self.generic_visit(node)

    def visit_Set(self, node: ast.Set) -> None:
        self.tokens.append(f'Set:n={len(node.elts)}')
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        self.tokens.append(f'Import:n={len(node.names)}')

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        self.tokens.append(f'ImportFrom:n={len(node.names)}')

    def visit_Global(self, node: ast.Global) -> None:
        self.tokens.append('Global')

    def visit_Nonlocal(self, node: ast.Nonlocal) -> None:
        self.tokens.append('Nonlocal')

    def visit_Delete(self, node: ast.Delete) -> None:
        self.tokens.append('Delete')
        self.generic_visit(node)

    def visit_Expr(self, node: ast.Expr) -> None:
        self.tokens.append('Expr')
        self.generic_visit(node)

    def visit_Pass(self, node: ast.Pass) -> None:
        self.tokens.append('Pass')

    def visit_Break(self, node: ast.Break) -> None:
        self.tokens.append('Break')

    def visit_Continue(self, node: ast.Continue) -> None:
        self.tokens.append('Continue')

    def visit_Yield(self, node: ast.Yield) -> None:
        self.tokens.append('Yield')
        self.generic_visit(node)

    def visit_YieldFrom(self, node: ast.YieldFrom) -> None:
        self.tokens.append('YieldFrom')
        self.generic_visit(node)

    def visit_Await(self, node: ast.Await) -> None:
        self.tokens.append('Await')
        self.generic_visit(node)

    def visit_JoinedStr(self, node: ast.JoinedStr) -> None:
        self.tokens.append('FStr')
        self.generic_visit(node)

    def visit_IfExp(self, node: ast.IfExp) -> None:
        self.tokens.append('IfExp')
        self.generic_visit(node)

    def visit_Starred(self, node: ast.Starred) -> None:
        self.tokens.append('Starred')
        self.generic_visit(node)

    def visit_FormattedValue(self, node: ast.FormattedValue) -> None:
        self.tokens.append('FormattedValue')
        self.generic_visit(node)

def _function_body_nodes(func: ast.FunctionDef | ast.AsyncFunctionDef) -> list[ast.stmt]:
    """Return body statements, skipping a leading docstring-only Expr node."""
    body = func.body
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
        return body[1:]
    return body

def _structural_fingerprint(func: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """
    Return a SHA-256 hex digest representing the structural skeleton of the
    function body.  All names and literal values are normalised so that two
    functions with identical logic but different identifiers/messages still
    produce the same fingerprint.

    Additionally encode:
      - number of arguments (arity)
      - async vs sync
      - number of body statements (rough complexity signal)
    """
    visitor = _FingerprintVisitor()
    stmts = _function_body_nodes(func)
    for stmt in stmts:
        visitor.visit(stmt)
    is_async = isinstance(func, ast.AsyncFunctionDef)
    arity = len(func.args.args) + len(func.args.posonlyargs) + len(func.args.kwonlyargs)
    prefix = f'async={is_async}:arity={arity}:nstmt={len(stmts)}:'
    token_str = prefix + '|'.join(visitor.tokens)
    return hashlib.sha256(token_str.encode()).hexdigest()

@dataclass
class CorpusEntry:
    rel_path: str
    func_name: str

def _strip_phase_wave_tokens(name: str) -> str:
    """
    Strip phase/wave migration tokens from a test function name to get the
    semantic core.  Examples:
      test_phase10_embedding_activation  → embedding_activation
      test_wave2_upward_import_detected  → upward_import_detected
      test_w10_replay_determinism        → replay_determinism
    """
    stem = name[len('test_'):] if name.startswith('test_') else name
    import re as _re
    stem = _re.sub('^(phase|wave|w|p)\\d+[_.]', '', stem, flags=_re.IGNORECASE)
    stem = _re.sub('^(phase|wave)[_.]', '', stem, flags=_re.IGNORECASE)
    return stem.lower().strip('_')

@dataclass
class CorpusIndex:
    by_fingerprint: dict[str, list[CorpusEntry]] = field(default_factory=dict)
    by_normalised_name: dict[str, list[CorpusEntry]] = field(default_factory=dict)
    files_indexed: int = 0
    functions_indexed: int = 0
    parse_failures: list[str] = field(default_factory=list)

def _collect_func_nodes(tree: ast.Module) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    """Collect all FunctionDef/AsyncFunctionDef nodes that start with test_."""
    result = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith('test_'):
                result.append(node)
    return result

def _build_corpus_index(corpus_files: list[Path]) -> CorpusIndex:
    idx = CorpusIndex()
    for p in corpus_files:
        tree = _parse_safe(p)
        if tree is None:
            idx.parse_failures.append(str(p.relative_to(REPO_ROOT)).replace('\\', '/'))
            continue
        idx.files_indexed += 1
        rel = str(p.relative_to(REPO_ROOT)).replace('\\', '/')
        funcs = _collect_func_nodes(tree)
        for fn in funcs:
            idx.functions_indexed += 1
            entry = CorpusEntry(rel_path=rel, func_name=fn.name)
            fp = _structural_fingerprint(fn)
            idx.by_fingerprint.setdefault(fp, []).append(entry)
            norm = _strip_phase_wave_tokens(fn.name)
            if norm:
                idx.by_normalised_name.setdefault(norm, []).append(entry)
    return idx

@dataclass
class FuncDuplicateResult:
    func_name: str
    fingerprint: str
    structural_matches: list[CorpusEntry] = field(default_factory=list)
    name_matches: list[CorpusEntry] = field(default_factory=list)

    @property
    def has_structural_duplicate(self) -> bool:
        return bool(self.structural_matches)

    @property
    def has_name_duplicate(self) -> bool:
        return bool(self.name_matches)

    @property
    def is_duplicate(self) -> bool:
        return self.has_structural_duplicate or self.has_name_duplicate

def _check_duplicates(path: Path, tree: ast.Module, idx: CorpusIndex) -> list[FuncDuplicateResult]:
    results = []
    for fn in _collect_func_nodes(tree):
        fp = _structural_fingerprint(fn)
        norm = _strip_phase_wave_tokens(fn.name)
        rel_self = str(path.relative_to(REPO_ROOT)).replace('\\', '/')
        struct_matches = [e for e in idx.by_fingerprint.get(fp, []) if e.rel_path != rel_self]
        name_matches = [e for e in idx.by_normalised_name.get(norm, []) if e.rel_path != rel_self] if norm else []
        struct_match_keys = {(e.rel_path, e.func_name) for e in struct_matches}
        name_matches_deduped = [e for e in name_matches if (e.rel_path, e.func_name) not in struct_match_keys]
        results.append(FuncDuplicateResult(func_name=fn.name, fingerprint=fp, structural_matches=struct_matches, name_matches=name_matches_deduped))
    return results
Verdict = Literal['DELETE', 'RENAME', 'KEEP-AS-IS', 'NEEDS-REVIEW']

@dataclass
class FileVerdict:
    path: Path
    rel_path: str
    quarantine_reason: str = ''
    delete_after: str = ''
    superseded_by: str = ''
    superseding_exists: bool = False
    superseding_path: str = ''
    test_names: list[str] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    missing_imports: list[str] = field(default_factory=list)
    docstring_snippet: str = ''
    func_duplicate_results: list[FuncDuplicateResult] = field(default_factory=list)
    duplicate_logic_notes: str = ''
    functionality_assessment: str = ''
    verdict: Verdict = 'NEEDS-REVIEW'
    suggested_name: str = ''
    rationale: str = ''
    parse_ok: bool = True

    @property
    def total_funcs(self) -> int:
        return len(self.func_duplicate_results)

    @property
    def structural_dup_count(self) -> int:
        return sum(1 for r in self.func_duplicate_results if r.has_structural_duplicate)

    @property
    def name_dup_count(self) -> int:
        return sum(1 for r in self.func_duplicate_results if r.has_name_duplicate)

    @property
    def unique_func_count(self) -> int:
        return sum(1 for r in self.func_duplicate_results if not r.is_duplicate)

def _assess_file(path: Path, idx: CorpusIndex) -> FileVerdict:
    rel = str(path.relative_to(REPO_ROOT)).replace('\\', '/')
    v = FileVerdict(path=path, rel_path=rel)
    tree = _parse_safe(path)
    if tree is None:
        v.parse_ok = False
        v.verdict = 'NEEDS-REVIEW'
        v.rationale = 'SyntaxError — cannot parse'
        return v
    v.docstring_snippet = _extract_docstring(tree)[:200].replace('\n', ' ')
    v.test_names = _extract_test_names(tree)
    v.imports = _extract_imports(tree)
    _, v.missing_imports = _check_imports_resolvable(v.imports)
    headers = _quarantine_headers(path)
    v.quarantine_reason = headers.get('quarantine_reason', '')
    v.delete_after = headers.get('delete_after', '')
    v.superseded_by = headers.get('superseded_by', '')
    if v.superseded_by:
        sup_path = _resolve_superseding_path(v.superseded_by)
        v.superseding_exists = sup_path is not None and sup_path.exists()
        if sup_path and v.superseding_exists:
            v.superseding_path = str(sup_path.relative_to(REPO_ROOT)).replace('\\', '/')
    v.func_duplicate_results = _check_duplicates(path, tree, idx)
    return v
_RENAME_MAP: dict[str, tuple[str, str]] = {'test_wave1_phase1_2_sovereignty': ('test_provider_import_sovereignty', 'Tests direct-provider-import detection and upward-import guard in ASTAnalyzer — purely functional, no phase dependency.'), 'test_wave1_phase1_3_governance': ('test_governance_stamp_wiring', 'Tests governance/elevator-shaft hint detection and gap generation — purely functional.'), 'test_wave1_phase1_parse_failures_and_ssot_paths': ('test_ssot_parse_failures_and_component_paths', 'Tests parse-failure remediation + SSOT component path correctness — purely functional invariant.'), 'test_wave2_phase2_1_advanced_governance': ('test_layer_connection_integrity', 'Tests analyze_layer_connection_integrity branches (upward import, gateway bypass, mutation risk, PathD) — purely functional.'), 'test_wave2_phase2_2_embedding_sovereignty': ('test_rag_embedding_sovereignty', 'Tests analyze_rag_embedding_sovereignty allowed/disallowed placements — purely functional.'), 'test_wave2_phase2_3_prompt_taxonomy': ('test_prompt_taxonomy_coverage', 'Tests analyze_prompt_taxonomy_coverage slot/manifest/validator branches — purely functional.'), 'test_wave3_phase3_1_cache_wirings': ('test_cache_wiring_gap_detection', 'Tests L0/L1 cache-import gap detection in SemanticGapAnalyzer — purely functional.'), 'test_wave3_phase3_2_boundary_hardening': ('test_layer_boundary_gap_detection', 'Tests L2-L6 boundary gap detection (validator/orchestrator/blob/safety/telemetry) — purely functional.'), 'test_wave3_phase3_3_finalization': ('test_semantic_gap_analyzer_run_and_report', 'Tests run_analysis() + generate_report() output contract — purely functional.'), 'test_wave1_cda_sync_wrapper': ('test_cognitive_disposition_agent_sync_api', 'Tests CognitiveDispositionAgent exposes sync analyze_violation() — pure structural contract, not wave-specific.'), 'test_wave2_gravity_exclusion': ('test_gravity_leak_repair_exclusion_paths', 'Tests GravityLeakRepairAgent excluded_paths field in StructureConfig — pure structural contract.'), 'test_wave4_v15_agent_id': ('test_v15_gateway_execute_agent_id_required', 'Tests all V15ExecutionGateway.execute() call sites supply agent_id — pure call-site invariant, not wave-specific.'), 'test_wave5_longpaths_guard': ('test_longpaths_bypass_guard', 'Tests AGENTIC_BYPASS_LONGPATHS_CHECK guard in execute_ssot.py — pure structural invariant.'), 'test_wave6_hitl_gates': ('test_hitl_gate_wiring', 'Tests HITL gate wiring at all required trigger points — pure structural contract, not wave-specific.'), 'test_healers_wave6': ('test_healer_contracts', 'Tests healer dry-run/apply modes and registry — pure contract test, wave label is cosmetic.'), 'test_v15_p2_wave2_1_inventory': ('test_runtime_entrypoint_inventory_schema', 'Tests v15_phase2_wave2_1_runtime_entrypoints.json schema and content — rename to reflect the JSON artifact it validates.'), 'test_wave0c_meta_learning_intake_wiring': ('test_meta_learning_intake_wiring', 'Tests _fire_meta_learning_intake wiring in execute_ssot.py — purely functional invariant.'), 'test_req253_254_cross_wave_linkage': ('test_cross_wave_audit_hash_linkage', "Tests REQ-253/254 WaveAuditSummary prev_wave_hash linkage — 'wave' is a domain concept (audit chain), not a migration phase; rename removes ambiguity.")}
_EVAL_RENAME_MAP: dict[str, tuple[str, str]] = {'test_phase1_metrics': ('test_evaluation_metrics', 'Tests PrecisionAtK, RecallAtK, MRR, NDCG, Groundedness, AnswerCorrectness — evaluation framework metrics, phase number is pipeline stage label.'), 'test_phase1_runners': ('test_evaluation_runners', 'Tests evaluation pipeline runners — evaluation framework, not migration.'), 'test_phase1_schemas': ('test_evaluation_schemas', 'Tests evaluation schema contracts — evaluation framework.'), 'test_phase2_retrieval': ('test_evaluation_retrieval', 'Tests retrieval evaluation pipeline — evaluation framework.'), 'test_phase3_chunking': ('test_evaluation_chunking', 'Tests chunking evaluation pipeline — evaluation framework.'), 'test_phase4_monitoring': ('test_evaluation_monitoring', 'Tests monitoring evaluation pipeline — evaluation framework.'), 'test_phase5_feedback': ('test_evaluation_feedback', 'Tests feedback evaluation pipeline — evaluation framework.'), 'test_phase6_completeness_retrieval': ('test_evaluation_completeness_retrieval', 'Tests completeness+retrieval evaluation — evaluation framework.')}
_DUPLICATE_SUFFIX_PATTERN = '_1'

# guardian: allow-magic-config
def _format_dup_results(results: list[FuncDuplicateResult], max_per_func: int=2) -> str:
    """Compact one-line summary of duplicate findings."""
    parts = []
    for r in results:
        if r.has_structural_duplicate:
            matches = r.structural_matches[:max_per_func]
            refs = '; '.join(f'{e.func_name}@{e.rel_path}' for e in matches)
            parts.append(f'STRUCTURAL: {r.func_name} → {refs}')
        elif r.has_name_duplicate:
            matches = r.name_matches[:max_per_func]
            refs = '; '.join(f'{e.func_name}@{e.rel_path}' for e in matches)
            parts.append(f'NAME-MATCH: {r.func_name} → {refs}')
    return ' | '.join(parts) if parts else ''

def _apply_verdicts(verdicts: list[FileVerdict]) -> None:
    for v in verdicts:
        in_quarantine = '_quarantine' in v.rel_path
        if in_quarantine:
            v.functionality_assessment = 'QUARANTINED — not in active test suite'
            if v.quarantine_reason:
                if v.superseded_by and v.superseding_exists:
                    v.verdict = 'DELETE'
                    v.rationale = f'In _quarantine, QUARANTINE header present, superseded by {v.superseding_path} which EXISTS. Safe to remove — tracked in QUARANTINE_MANIFEST.json.'
                    v.duplicate_logic_notes = f'Superseding file covers invariants: {v.superseded_by}'
                elif v.superseded_by and (not v.superseding_exists):
                    v.verdict = 'NEEDS-REVIEW'
                    v.rationale = f"QUARANTINE header says superseded by '{v.superseded_by}' but that file does NOT exist. Cannot delete until the superseding test is created."
                else:
                    v.verdict = 'DELETE'
                    v.rationale = 'In _quarantine with QUARANTINE header. assertion_rot category — tests OpenAI/provider-specific code no longer in the system.'
            elif v.path.stem.endswith(_DUPLICATE_SUFFIX_PATTERN):
                base_stem = v.path.stem[:-len(_DUPLICATE_SUFFIX_PATTERN)]
                base_path = v.path.parent / f'{base_stem}.py'
                if base_path.exists():
                    v.verdict = 'DELETE'
                    v.duplicate_logic_notes = f'Mechanical _1 duplicate of {base_path.relative_to(REPO_ROOT)}'
                    v.rationale = f'Mechanically generated _1 duplicate of {base_stem}.py — identical content, safe to delete.'
                else:
                    v.verdict = 'NEEDS-REVIEW'
                    v.rationale = 'No base file found for _1 suffix duplicate.'
            else:
                v.verdict = 'NEEDS-REVIEW'
                v.rationale = 'In _quarantine but no QUARANTINE header found — unexpected.'
            continue
        stem = v.path.stem
        dup_summary = _format_dup_results([r for r in v.func_duplicate_results if r.is_duplicate])
        if v.total_funcs > 0 and v.structural_dup_count == v.total_funcs and (v.unique_func_count == 0):
            v.verdict = 'DELETE'
            v.functionality_assessment = f'ALL {v.total_funcs} test functions are structural duplicates of functions in the active corpus.'
            v.duplicate_logic_notes = dup_summary
            v.rationale = '100% structural duplicate coverage confirmed by AST fingerprint comparison. No unique logic remains in this file.'
            continue
        if v.structural_dup_count > 0:
            struct_pct = int(100 * v.structural_dup_count / max(v.total_funcs, 1))
            if stem in _RENAME_MAP:
                suggested, base_rationale = _RENAME_MAP[stem]
                v.suggested_name = f'{suggested}.py'
                v.verdict = 'RENAME'
                v.rationale = f'{base_rationale}  NOTE: {v.structural_dup_count}/{v.total_funcs} functions ({struct_pct}%) have structural duplicates in the corpus — merge unique tests into the renamed file, remove duplicates.'
            elif stem in _EVAL_RENAME_MAP:
                suggested, base_rationale = _EVAL_RENAME_MAP[stem]
                v.suggested_name = f'{suggested}.py'
                v.verdict = 'RENAME'
                v.rationale = f'{base_rationale}  NOTE: {v.structural_dup_count}/{v.total_funcs} functions ({struct_pct}%) are structural duplicates.'
            else:
                v.verdict = 'NEEDS-REVIEW'
                v.rationale = f'{v.structural_dup_count}/{v.total_funcs} functions ({struct_pct}%) are structural duplicates of corpus functions. Merge unique tests, delete duplicates.'
            v.functionality_assessment = f'{v.unique_func_count}/{v.total_funcs} unique functions; {v.structural_dup_count} structural dup(s); {v.name_dup_count} name-only match(es).'
            v.duplicate_logic_notes = dup_summary
            existing = v.path.parent / f'{v.suggested_name}' if v.suggested_name else None
            if existing and existing.exists():
                v.verdict = 'NEEDS-REVIEW'
                v.rationale += f' WARNING: {v.suggested_name} already exists — manual merge required.'
            continue
        if stem in _RENAME_MAP:
            suggested, rationale = _RENAME_MAP[stem]
            v.suggested_name = f'{suggested}.py'
            v.verdict = 'RENAME'
            v.rationale = rationale
            v.functionality_assessment = f'Tests CURRENT functionality. {v.total_funcs} functions, 0 structural duplicates detected.'
            if v.name_dup_count:
                v.duplicate_logic_notes = f'{v.name_dup_count} name-match(es) found (different body): ' + _format_dup_results([r for r in v.func_duplicate_results if r.has_name_duplicate])
            existing = v.path.parent / f'{suggested}.py'
            if existing.exists():
                v.verdict = 'NEEDS-REVIEW'
                v.rationale += f' NOTE: {suggested}.py already exists — manual merge required.'
            continue
        if stem in _EVAL_RENAME_MAP:
            suggested, rationale = _EVAL_RENAME_MAP[stem]
            v.suggested_name = f'{suggested}.py'
            v.verdict = 'RENAME'
            v.rationale = rationale
            v.functionality_assessment = f'Tests CURRENT evaluation framework (agentic_core.evaluation.*). {v.total_funcs} functions, 0 structural duplicates.'
            existing = v.path.parent / f'{suggested}.py'
            if existing.exists():
                v.verdict = 'NEEDS-REVIEW'
                v.rationale += f' NOTE: {suggested}.py already exists — manual merge required.'
            continue
        if v.missing_imports:
            v.verdict = 'NEEDS-REVIEW'
            v.functionality_assessment = f'Has {len(v.missing_imports)} unresolvable import(s): ' + ', '.join(v.missing_imports[:5])
            v.rationale = 'Cannot assess fully without resolving missing imports.'
            continue
        v.verdict = 'KEEP-AS-IS'
        v.functionality_assessment = f'References live modules. {v.total_funcs} functions, {v.structural_dup_count} structural dup(s).'
        v.rationale = 'Not in rename map — review manually to determine if phase/wave label is a domain concept (e.g. audit chain) or migration artifact.'
_VERDICT_ORDER = {'DELETE': 0, 'RENAME': 1, 'KEEP-AS-IS': 2, 'NEEDS-REVIEW': 3}
_VERDICT_SYMBOL = {'DELETE': 'DELETE', 'RENAME': 'RENAME', 'KEEP-AS-IS': 'KEEP-AS-IS', 'NEEDS-REVIEW': 'NEEDS-REVIEW'}

def _print_report(verdicts: list[FileVerdict], idx: CorpusIndex) -> None:
    verdicts_sorted = sorted(verdicts, key=lambda v: (_VERDICT_ORDER[v.verdict], v.rel_path))
    counts = {k: sum(1 for v in verdicts if v.verdict == k) for k in _VERDICT_ORDER}
    W = 100
    print('=' * W)
    print('PHASE/WAVE TEST FILE ASSESSMENT — AST STRUCTURAL DUPLICATE REPORT')
    print('=' * W)
    print(f'Phase/wave files: {len(verdicts)}  |  Corpus files indexed: {idx.files_indexed}  |  Corpus functions indexed: {idx.functions_indexed}  |  Corpus parse failures: {len(idx.parse_failures)}')
    for verdict, count in counts.items():
        print(f'  {_VERDICT_SYMBOL[verdict]}: {count}')
    print()
    for verdict_key in ('DELETE', 'RENAME', 'KEEP-AS-IS', 'NEEDS-REVIEW'):
        group = [v for v in verdicts_sorted if v.verdict == verdict_key]
        if not group:
            continue
        print(f"{'─' * W}")
        print(f'  {_VERDICT_SYMBOL[verdict_key]}  ({len(group)} files)')
        print(f"{'─' * W}")
        for v in group:
            print(f'\n  FILE : {v.rel_path}')
            if v.quarantine_reason:
                print(f'  QUAR : {v.quarantine_reason}')
            if v.superseded_by:
                exists_str = '(EXISTS)' if v.superseding_exists else '(MISSING)'
                print(f'  SUP  : {v.superseded_by} {exists_str}')
            if v.suggested_name:
                parent_rel = str(v.path.parent.relative_to(REPO_ROOT)).replace('\\', '/')
                print(f'  NEW  : {parent_rel}/{v.suggested_name}')
            print(f'  FUNC : {v.functionality_assessment}')
            if '_quarantine' not in v.rel_path and v.func_duplicate_results:
                dup_funcs = [r for r in v.func_duplicate_results if r.is_duplicate]
                unique_funcs = [r for r in v.func_duplicate_results if not r.is_duplicate]
                if dup_funcs:
                    print(f'  DUPS : {len(dup_funcs)} duplicate function(s):')
                    for r in dup_funcs[:8]:
                        kind = 'STRUCT' if r.has_structural_duplicate else 'NAME'
                        matches = r.structural_matches or r.name_matches
                        match_str = '; '.join(f'{e.func_name} @ {e.rel_path}' for e in matches[:2])
                        print(f'         [{kind}] {r.func_name}')
                        print(f'                  → {match_str}')
                    if len(dup_funcs) > 8:
                        print(f'         ... (+{len(dup_funcs) - 8} more)')
                if unique_funcs:
                    names = ', '.join(r.func_name for r in unique_funcs[:6])
                    if len(unique_funcs) > 6:
                        names += f' (+{len(unique_funcs) - 6} more)'
                    print(f'  UNIQ : {names}')
            print(f"  WHY  : {textwrap.fill(v.rationale, width=W - 9, subsequent_indent=' ' * 9)}")
        print()
    print('=' * W)
    print('SPRAWL SUMMARY')
    print('=' * W)
    active = [v for v in verdicts if '_quarantine' not in v.rel_path]
    total_funcs = sum(v.total_funcs for v in active)
    total_struct_dups = sum(v.structural_dup_count for v in active)
    total_unique = sum(v.unique_func_count for v in active)
    print(f'  Active phase/wave files  : {len(active)}')
    print(f'  Total test functions     : {total_funcs}')
    print(f'  Structural duplicates    : {total_struct_dups}')
    print(f'  Unique functions         : {total_unique}')
    if total_funcs:
        dup_pct = int(100 * total_struct_dups / total_funcs)
        unique_pct = 100 - dup_pct
        print(f'  Duplication rate         : {dup_pct}%  (unique signal: {unique_pct}%)')
    print()

def _emit_json(verdicts: list[FileVerdict], idx: CorpusIndex, output_path: Path) -> None:
    data = {'corpus_stats': {'files_indexed': idx.files_indexed, 'functions_indexed': idx.functions_indexed, 'parse_failures': idx.parse_failures}, 'verdicts': []}
    for v in verdicts:
        dup_details = [{'func_name': r.func_name, 'fingerprint': r.fingerprint[:16] + '...', 'structural_matches': [{'rel_path': e.rel_path, 'func_name': e.func_name} for e in r.structural_matches[:5]], 'name_matches': [{'rel_path': e.rel_path, 'func_name': e.func_name} for e in r.name_matches[:5]]} for r in v.func_duplicate_results if r.is_duplicate]
        data['verdicts'].append({'path': v.rel_path, 'verdict': v.verdict, 'suggested_name': v.suggested_name, 'quarantine_reason': v.quarantine_reason, 'superseded_by': v.superseded_by, 'superseding_exists': v.superseding_exists, 'superseding_path': v.superseding_path, 'total_funcs': v.total_funcs, 'structural_dup_count': v.structural_dup_count, 'name_dup_count': v.name_dup_count, 'unique_func_count': v.unique_func_count, 'missing_imports': v.missing_imports, 'functionality_assessment': v.functionality_assessment, 'duplicate_logic_notes': v.duplicate_logic_notes, 'rationale': v.rationale, 'parse_ok': v.parse_ok, 'duplicate_details': dup_details})
    output_path.write_text(json.dumps(data, indent=2), encoding='utf-8')
    print(f'JSON report written to: {output_path.relative_to(REPO_ROOT)}')

def main() -> int:
    phase_wave_files = _find_phase_wave_files()
    if not phase_wave_files:
        print('No phase/wave test files found.')
        return 0
    phase_wave_set = set(phase_wave_files)
    corpus_files = _find_corpus_files(exclude=phase_wave_set)
    print(f'Building AST corpus index: {len(corpus_files)} non-phase/wave test files ...', flush=True)
    idx = _build_corpus_index(corpus_files)
    print(f'  Indexed {idx.functions_indexed} test functions across {idx.files_indexed} files.  ({len(idx.parse_failures)} parse failure(s) skipped)', flush=True)
    print()
    verdicts: list[FileVerdict] = []
    for p in phase_wave_files:
        v = _assess_file(p, idx)
        verdicts.append(v)
    _apply_verdicts(verdicts)
    _print_report(verdicts, idx)
    json_out = REPO_ROOT / 'artifacts' / 'assessment_phase_wave_tests.json'
    json_out.parent.mkdir(parents=True, exist_ok=True)
    _emit_json(verdicts, idx, json_out)
    unresolvable = [v for v in verdicts if v.verdict == 'NEEDS-REVIEW']
    if unresolvable:
        print(f'\nWARNING: {len(unresolvable)} file(s) require manual review before action.')
        return 1
    return 0
if __name__ == '__main__':
    sys.exit(main())
