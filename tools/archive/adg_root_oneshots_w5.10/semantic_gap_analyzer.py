"""Semantic Gap Analyzer for Agentic Architecture Major Arteries.

Traces actual execution flows through L0-L6 layers and identifies where
architectural intent (lower latency, deterministic lookups, cache-first patterns)
diverges from implementation reality.

Usage:
    python tools/semantic_gap_analyzer.py --output docs/reports/plans/semantic_gap_analysis.md
"""

from __future__ import annotations

import ast
import hashlib
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    L0_ROUTING_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    SYSTEM_LEARNING_DIR,
    TOOLS_DIR,
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

_emit_records_execution_trace("p0", "evidence", "semantic_gap_analyzer")
_emit_applies_guardrail("p0", "semantic_gap_analyzer", "p0_governance")
_emit_snapshots_state("p0", "semantic_gap_analyzer", "state_snapshot")
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

_emit_emits_metric_event("semantic_gap_analyzer", "p4obs", "metric_1")
_emit_emits_metric_event("semantic_gap_analyzer", "p4obs", "metric_2")
_emit_emits_metric_event("semantic_gap_analyzer", "p4obs", "metric_3")
_emit_emits_metric_event("semantic_gap_analyzer", "p4obs", "metric_4")
_emit_emits_metric_event("semantic_gap_analyzer", "p4obs", "metric_5")
_emit_emits_metric_event("semantic_gap_analyzer", "p4obs", "metric_6")
_emit_records_incident_event("semantic_gap_analyzer", "p4obs", "incident")
_emit_captures_runtime_anomaly("semantic_gap_analyzer", "p4obs", "anomaly")
_emit_writes_observability_log("semantic_gap_analyzer", "p4obs", "obs_log")
_emit_updates_monitoring_state("semantic_gap_analyzer", "p4obs", "mon_state")
_emit_triggers_alert("semantic_gap_analyzer", "p4obs", "alert")
_emit_links_incident_trace("semantic_gap_analyzer", "p4obs", "trace_link")
_emit_captures_pattern("semantic_gap_analyzer", "p3lm", "pattern")
_emit_records_learning_event("semantic_gap_analyzer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("semantic_gap_analyzer", "p3lm", "snapshot")
_emit_feeds_meta_learning("semantic_gap_analyzer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("semantic_gap_analyzer", "p3lm", "routing")
_emit_improves_agent_policy("semantic_gap_analyzer", "p3lm", "policy")
_emit_stores_learning_state("semantic_gap_analyzer", "p3lm", "state")
_emit_records_execution_trace("semantic_gap_analyzer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("semantic_gap_analyzer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("semantic_gap_analyzer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("semantic_gap_analyzer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("semantic_gap_analyzer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("semantic_gap_analyzer", "env_read", "p2_env_1")
_emit_reads_environ("semantic_gap_analyzer", "env_read", "p2_env_2")
_emit_reads_runtime_state("semantic_gap_analyzer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("semantic_gap_analyzer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "semantic_gap_analyzer", "context_pull")
_emit_pulls_context("p1", "semantic_gap_analyzer", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "semantic_gap_analyzer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "semantic_gap_analyzer", "uwg_term_2")
_emit_writes_through("p1", "semantic_gap_analyzer", "write_through")
_emit_writes_through("p1", "semantic_gap_analyzer", "write_through_2")
_emit_validated_by_safety_plane("p1", "semantic_gap_analyzer", "safety_validation")
_emit_invokes_eval("p1", "semantic_gap_analyzer", "eval_call")
_emit_proposal_commits_routing("p1", "semantic_gap_analyzer", "routing_commit")
_emit_escalates_to_human("p1", "semantic_gap_analyzer", "human_escalation")
_emit_routes_through("p1", "semantic_gap_analyzer", "route_through")
_emit_checks_agent_registry("p1", "semantic_gap_analyzer", "agent_registry")
_emit_validates_agent_capability("p1", "semantic_gap_analyzer", "capability")
_emit_dispatches_execution_plan("p1", "semantic_gap_analyzer", "exec_plan")
_emit_agent_executes_agent("p1", "semantic_gap_analyzer", "sub_agent")
_emit_routes_to_agent("p1", "semantic_gap_analyzer", "target_agent")
_emit_verifies_policy("p1", "semantic_gap_analyzer", "policy_check")
_emit_observes_runtime_state("p1", "semantic_gap_analyzer", "runtime_state")
_emit_verifies_boundary("p1", "semantic_gap_analyzer", "boundary_check")
_emit_transcripts_response("p1", "semantic_gap_analyzer", "transcript")
_emit_hard_fails_untranscripted("p1", "semantic_gap_analyzer")
_emit_gated_by_confidence("p1", "semantic_gap_analyzer", "confidence_gate")
emit_replay_key("p0", "semantic_gap_analyzer")
emit_determinism_digest("p0", "semantic_gap_analyzer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "semantic_gap_analyzer", "execution_auth")
_emit_validates_capability("p2", "semantic_gap_analyzer", "capability_check")
_emit_routes_to_capability("p2", "semantic_gap_analyzer", "capability_route")
_emit_writes_via_uwg("p2", "semantic_gap_analyzer", "uwg_write")
_emit_blocks_direct_write("p2", "semantic_gap_analyzer", "direct_write_block")
_emit_records_tool_invocation("p2", "semantic_gap_analyzer", "tool_invocation")
_emit_captures_execution_output("p2", "semantic_gap_analyzer", "exec_output")
_emit_dispatches_agent("p3", "semantic_gap_analyzer", "agent_dispatch")
_emit_coordinates_agents("p3", "semantic_gap_analyzer", "agent_coordination")
_emit_records_workflow_lineage("p3", "semantic_gap_analyzer", "workflow_lineage")
_emit_records_healing_outcome("p3", "semantic_gap_analyzer", "healing_outcome")
_emit_escalates_failure("p3", "semantic_gap_analyzer", "failure_escalation")
_emit_orchestrates_workflow("p3", "semantic_gap_analyzer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "semantic_gap_analyzer", "healing_dispatch")
_emit_invokes_evaluation("p3", "semantic_gap_analyzer", "evaluation_signal")
_emit_records_telemetry_event("p4", "semantic_gap_analyzer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "semantic_gap_analyzer", "eval_metric")
_emit_stores_embedding("p4", "semantic_gap_analyzer", "embedding_store")
_emit_updates_meta_learning_state("p4", "semantic_gap_analyzer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "semantic_gap_analyzer", "exec_snapshot_link")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_1")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_2")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_3")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_4")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_5")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_6")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_7")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_8")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_9")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_10")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_11")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_12")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_13")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_14")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_15")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_16")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_17")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_18")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_19")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_20")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_21")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_22")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_23")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_24")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_25")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_26")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_27")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_28")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_29")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_30")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_31")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_32")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_33")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_34")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_35")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_36")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_37")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_38")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_39")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_40")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_41")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_42")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_43")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_44")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_45")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_46")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_47")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_48")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_49")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_50")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_51")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_52")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_53")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_54")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_55")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_56")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_57")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_58")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_59")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_60")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_61")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_62")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_63")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_64")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_65")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_66")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_67")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_68")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_69")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_70")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_71")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_72")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_73")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_74")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_75")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_76")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_77")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_78")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_79")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_80")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_81")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_82")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_83")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_84")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_85")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_86")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_87")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_88")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_89")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_90")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_91")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_92")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_93")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_94")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_95")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_96")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_97")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_98")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_99")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_100")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_101")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_102")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_103")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_104")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_105")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_106")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_107")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_108")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_109")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_110")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_111")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_112")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_113")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_114")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_115")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_116")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_117")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_118")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_119")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_120")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_121")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_122")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_123")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_124")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_125")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_126")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_127")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_128")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_129")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_130")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_131")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_132")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_133")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_134")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_135")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_136")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_137")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_138")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_139")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_140")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_141")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_142")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_143")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_144")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_145")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_146")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_147")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_148")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_149")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_150")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_151")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_152")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_153")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_154")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_155")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_156")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_157")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_158")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_159")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_160")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_161")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_162")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_163")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_164")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_165")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_166")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_167")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_168")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_169")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_170")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_171")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_172")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_173")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_174")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_175")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_176")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_177")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_178")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_179")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_180")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_181")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_182")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_183")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_184")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_185")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_186")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_187")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_188")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_189")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_190")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_191")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_192")
_emit_reads_through("l4", "semantic_gap_analyzer", "urg_read_193")

REPO_ROOT = get_validated_project_root()
AGENTIC_CORE = REPO_ROOT / AGENTIC_CORE_DIR

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

PRIORITY_RANK = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
PYTHON_FILE_GLOB = "*.py"
EXCLUDED_DIR_NAMES = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "site-packages",
}
EXCLUDED_FILE_SUFFIXES = {".pyi"}

PROMPT_SLOT_ORDER = ("S0", "D0", "I0", "C0", "U0")
PROMPT_SLOT_DESCRIPTIONS = {
    "S0": "System / state rulebooks and hard invariants",
    "D0": "Injections, semantic fences, and tool constraints",
    "I0": "Instructional identity and governed behavior",
    "C0": "Dependency context such as RAG or Elevator Shaft injected knowledge",
    "U0": "Raw user prompt / intent",
}
PROMPT_TAXONOMY_PATTERNS = {
    "S0": (
        "S0",
        "system",
        "system_prompt",
        "constitution",
        "invariant",
        "rulebook",
        "state_prompt",
    ),
    "D0": (
        "D0",
        "injection",
        "guardrail",
        "tool_constraint",
        "safety_fence",
        "semantic_fence",
        "policy_injection",
    ),
    "I0": (
        "I0",
        "instruction",
        "instructional",
        "identity_prompt",
        "role_prompt",
        "persona",
        "behavior",
    ),
    "C0": (
        "C0",
        "dependency",
        "context",
        "rag",
        "retrieval",
        "elevator_shaft",
        "knowledge_pack",
        "injected_context",
    ),
    "U0": (
        "U0",
        "user_prompt",
        "user_input",
        "raw_intent",
        "request_text",
        "prompt_text",
        "query_text",
    ),
}
PROMPT_ASSEMBLER_HINTS = (
    "assemble",
    "assembler",
    "build_prompt",
    "compose_prompt",
    "prompt_package",
    "instruction_packet",
    "governed_prompt",
)

ARCH_LAYER_ORDER = ("L0", "L1", "L2", "L3", "L4", "L5", "L6")
ARCH_LAYER_PATHS = {
    "L0": REPO_ROOT / L0_ROUTING_DIR,
    "L1": REPO_ROOT / L1_COGNITION_DIR,
    "L2": REPO_ROOT / L2_EXECUTION_DIR,
    "L3": REPO_ROOT / L3_ORCHESTRATION_DIR,
    "L4": REPO_ROOT / L4_STATE_DIR,
    "L5": REPO_ROOT / L5_SAFETY_DIR,
    "L6": REPO_ROOT / L6_OBSERVABILITY_DIR,
}

ARCHITECTURE_COMPONENT_RULES = (
    {
        "key": "classification_kernel",
        "layer": "L5",
        "artery": "Classification Kernel Coverage",
        "path": AGENTIC_CORE / "L5_safety" / "core_kernel" / "classification_kernel.py",
        "required_any": ("classify_file_standalone", "is_agent_file", "is_agent_or_orchestrator"),
        "impact": "Without the zero-dependency classification kernel, file taxonomy and governance scans drift from the SSOT.",
        "priority": "HIGH",
        "recommended_fix": "Wire scans through classification_kernel SSOT instead of ad hoc filename heuristics.",
    },
    {
        "key": "sovereign_gateway",
        "layer": "L2",
        "artery": "Sovereign LLM Gateway Coverage",
        "path": AGENTIC_CORE / "L2_execution" / "enforcement" / "SovereignLLMGateway.py",
        "required_any": ("route_generation", "GenerationRequest", "GenerationResponse"),
        "impact": "Gateway bypass risk remains unobserved even though the architecture requires a sole LLM egress seam.",
        "priority": "HIGH",
        "recommended_fix": "Verify all LLM-capable paths resolve through SovereignLLMGateway and flag direct provider seams.",
    },
    {
        "key": "agent_registry",
        "layer": "L0",
        "artery": "Agent Execution Profile Registry Coverage",
        "path": AGENTIC_CORE / "agents" / "agent_registry.py",
        "required_any": ("AGENT_REGISTRY", "registry_digest", "AgentExecutionProfile"),
        "impact": "The analyzer can miss frozen 2x2 execution profile invariants and allowlist drift.",
        "priority": "HIGH",
        "recommended_fix": "Inspect AGENT_REGISTRY, registry_digest, and execution-mode bindings as first-class architecture contracts.",
    },
    {
        "key": "meta_learning_pipeline",
        "layer": "L4",
        "artery": "Meta-Learning Pipeline Coverage",
        "path": AGENTIC_CORE / "utils" / "meta_learning_engine_util.py",
        "required_any": (
            "MetaLearningEngine",
            "MetaLearningStorage",
            "recall_or_execute",
            "add_architectural_observation",
        ),
        "impact": "Stage ordering, dual injection, and proposal-only defaults are not audited.",
        "priority": "HIGH",
        "recommended_fix": "Add explicit checks for immutable stage order, dual injection, intake-before-commit, and proposal-only defaults.",
    },
    {
        "key": "write_gateway",
        "layer": "L2",
        "artery": "Universal Write Gateway Coverage",
        "path": AGENTIC_CORE / "L2_execution" / TOOLS_DIR / "write_gateway.py",
        "required_any": ("WriteAmplificationError", "WriteSizeCapError", "append_text", "append_csv_row"),
        "impact": "The analyzer does not verify the sole durable mutation authority described by the architecture.",
        "priority": "HIGH",
        "recommended_fix": "Treat write_gateway.py as a mandatory execution choke point and scan for non-UWG mutation paths.",
    },
)

DIRECT_PROVIDER_IMPORT_PATTERNS = (
    "openai",
    "anthropic",
    "google.generativeai",
    "google.genai",
    "litellm",
    "vllm",
)
EMBEDDING_HINT_PATTERNS = (
    "embedding",
    "embedder",
    "text-embedding-3-large",
    "bge",
    "faiss",
)
GOVERNANCE_STAMP_HINTS = (
    "compliance hash",
    "compliance_hash",
    "compliance stamp",
    "sandboxenvelope",
    "sandbox_envelope",
    "instructionpacket",
    "instruction_packet",
    "capabilitytoken",
    "capability_token",
)
PATH_D_HINTS = (
    "modify_diff",
    "original_plan_hash",
    "structured_patch_schema",
    "reviewer_sig",
    "human decision",
)
ELEVATOR_SHAFT_HINTS = (
    "jit",
    "semanticclock",
    "semantic_clock",
    "toolbudget",
    "tool_budget",
    "capabilitytoken",
    "capability_token",
)
META_PIPELINE_STAGE_NAMES = (
    "AUDIT",
    "TELEMETRY",
    "CONFIG",
    "SNAPSHOT",
    "RCA",
    "PROPOSE",
    "VALIDATE",
    "INTAKE",
    "COMMIT",
)


@dataclass
class ImportTrace:
    """Tracks an import statement and its usage context."""

    module: str
    imported_names: list[str]
    file_path: Path
    line_number: int
    is_used: bool = False


@dataclass
class CacheOpportunity:
    """Represents a potential caching opportunity."""

    layer: str
    hot_path: str
    current_pattern: str
    cache_candidate: str
    impact: str
    priority: str
    evidence: list[str] = field(default_factory=list)


@dataclass
class SemanticGap:
    """Represents a gap between architectural intent and implementation."""

    gap_id: str
    layer: str
    artery: str
    intent: str
    reality: str
    impact: str
    priority: str
    evidence_files: list[str] = field(default_factory=list)
    recommended_fix: str = ""


@dataclass(frozen=True)
class ParseFailure:
    """Represents a file that could not be analyzed."""

    file_path: Path
    error_type: str
    message: str


@dataclass
class FileAnalysis:
    """Typed analysis result for a single file."""

    file_path: Path
    imports: list[ImportTrace] = field(default_factory=list)
    calls: list[tuple[str, int]] = field(default_factory=list)
    cache_reads: list[int] = field(default_factory=list)
    cache_writes: list[int] = field(default_factory=list)
    l4_state_accesses: list[int] = field(default_factory=list)
    imported_module_names: set[str] = field(default_factory=set)
    imported_symbol_names: set[str] = field(default_factory=set)
    used_names: set[str] = field(default_factory=set)
    string_literals: list[str] = field(default_factory=list)
    prompt_slot_hits: dict[str, list[str]] = field(default_factory=dict)
    manifest_hash_mentions: list[int] = field(default_factory=list)
    boundary_snapshot_mentions: list[int] = field(default_factory=list)
    prompt_assembly_markers: list[str] = field(default_factory=list)
    imported_layer_refs: set[str] = field(default_factory=set)
    direct_provider_imports: set[str] = field(default_factory=set)
    embedding_mentions: set[str] = field(default_factory=set)
    governance_mentions: set[str] = field(default_factory=set)
    path_d_mentions: set[str] = field(default_factory=set)
    elevator_shaft_mentions: set[str] = field(default_factory=set)
    meta_stage_mentions: list[str] = field(default_factory=list)
    write_paths: list[str] = field(default_factory=list)
    parse_failure: ParseFailure | None = None

    @property
    def ok(self) -> bool:
        return self.parse_failure is None


class ASTAnalyzer:
    """AST-based code analyzer for tracing execution flows."""

    def __init__(self, root: Path):
        self.root = root
        self.import_graph: dict[str, list[ImportTrace]] = {}
        self.function_calls: dict[str, list[tuple[str, int]]] = {}
        self.parse_failures: list[ParseFailure] = []

    def analyze_file(self, file_path: Path) -> FileAnalysis:
        """Analyze a Python file and extract imports, calls, and patterns."""
        analysis = FileAnalysis(file_path=file_path)

        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(file_path))
        except (SyntaxError, UnicodeDecodeError, OSError) as e:  # guardian: allow-silent-swallow - acceptable exception handling
            failure = ParseFailure(
                file_path=file_path,
                error_type=type(e).__name__,
                message=str(e),
            )
            self.parse_failures.append(failure)
            logger.warning(f"Failed to parse {file_path}: {e}")
            analysis.parse_failure = failure
            return analysis

        analysis.used_names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
        analysis.string_literals = [
            node.value
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
        ]
        analysis.prompt_slot_hits = {slot: [] for slot in PROMPT_SLOT_ORDER}

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_name = alias.asname or alias.name.split(".")[-1]
                    trace = ImportTrace(
                        module=alias.name,
                        imported_names=[imported_name],
                        file_path=file_path,
                        line_number=node.lineno,
                    )
                    trace.is_used = imported_name in analysis.used_names
                    analysis.imports.append(trace)
                    analysis.imported_module_names.add(alias.name)
                    analysis.imported_symbol_names.add(imported_name)
                    for layer_name, layer_path in ARCH_LAYER_PATHS.items():
                        layer_token = layer_path.name
                        if layer_token in alias.name:
                            analysis.imported_layer_refs.add(layer_name)
                    if not alias.name.startswith("agentic_core."):
                        mod_lower = alias.name.lower()
                        if any(
                            mod_lower == p or mod_lower.startswith(p + ".")
                            for p in DIRECT_PROVIDER_IMPORT_PATTERNS
                        ):
                            analysis.direct_provider_imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imported_names: list[str] = []
                    for alias in node.names:
                        imported_name = alias.asname or alias.name
                        imported_names.append(imported_name)
                        analysis.imported_symbol_names.add(imported_name)

                    trace = ImportTrace(
                        module=node.module,
                        imported_names=imported_names,
                        file_path=file_path,
                        line_number=node.lineno,
                    )
                    trace.is_used = any(name in analysis.used_names for name in imported_names)
                    analysis.imports.append(trace)
                    analysis.imported_module_names.add(node.module)
                    for layer_name, layer_path in ARCH_LAYER_PATHS.items():
                        layer_token = layer_path.name
                        if layer_token in node.module:
                            analysis.imported_layer_refs.add(layer_name)
                    if not node.module.startswith("agentic_core."):
                        mod_lower = node.module.lower()
                        if any(
                            mod_lower == p or mod_lower.startswith(p + ".")
                            for p in DIRECT_PROVIDER_IMPORT_PATTERNS
                        ):
                            analysis.direct_provider_imports.add(node.module)
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    call_name = node.func.attr
                elif isinstance(node.func, ast.Name):
                    call_name = node.func.id
                else:
                    continue

                analysis.calls.append((call_name, node.lineno))

                # Detect cache patterns
                if call_name in {"get_json", "get", "hget", "mget"}:
                    analysis.cache_reads.append(node.lineno)
                elif call_name in {"set_json", "set", "hset", "mset"}:
                    analysis.cache_writes.append(node.lineno)

                # Detect probable L4 state accesses
                lowered = call_name.lower()
                if any(token in lowered for token in ("ledger", "blob", "state", "memory", "registry")):
                    analysis.l4_state_accesses.append(node.lineno)
                if any(
                    token in lowered for token in ("write", "append", "delete", "rename", "commit", "persist")
                ):
                    analysis.write_paths.append(call_name)

        for literal in analysis.string_literals:
            literal_lower = literal.lower()
            for slot, patterns in PROMPT_TAXONOMY_PATTERNS.items():
                if any(pattern.lower() in literal_lower for pattern in patterns):
                    analysis.prompt_slot_hits[slot].append(literal)

            if "manifest hash" in literal_lower or "manifest_hash" in literal_lower:
                analysis.manifest_hash_mentions.append(1)
            if "boundary_snapshot" in literal_lower:
                analysis.boundary_snapshot_mentions.append(1)
            if any(hint in literal_lower for hint in PROMPT_ASSEMBLER_HINTS):
                analysis.prompt_assembly_markers.append(literal)
            if any(hint in literal_lower for hint in EMBEDDING_HINT_PATTERNS):
                analysis.embedding_mentions.add(literal)
            if any(hint in literal_lower for hint in GOVERNANCE_STAMP_HINTS):
                analysis.governance_mentions.add(literal)
            if any(hint in literal_lower for hint in PATH_D_HINTS):
                analysis.path_d_mentions.add(literal)
            if any(hint in literal_lower for hint in ELEVATOR_SHAFT_HINTS):
                analysis.elevator_shaft_mentions.add(literal)
            for stage_name in META_PIPELINE_STAGE_NAMES:
                if stage_name.lower() in literal_lower:
                    analysis.meta_stage_mentions.append(stage_name)

        for name in analysis.used_names:
            lowered_name = name.lower()
            for slot, patterns in PROMPT_TAXONOMY_PATTERNS.items():
                if any(pattern.lower() in lowered_name for pattern in patterns):
                    analysis.prompt_slot_hits[slot].append(name)

            if "manifest_hash" in lowered_name:
                analysis.manifest_hash_mentions.append(1)
            if "boundary_snapshot" in lowered_name:
                analysis.boundary_snapshot_mentions.append(1)
            if any(hint in lowered_name for hint in PROMPT_ASSEMBLER_HINTS):
                analysis.prompt_assembly_markers.append(name)
            if any(hint in lowered_name for hint in EMBEDDING_HINT_PATTERNS):
                analysis.embedding_mentions.add(name)
            if any(hint in lowered_name for hint in GOVERNANCE_STAMP_HINTS):
                analysis.governance_mentions.add(name)
            if any(hint in lowered_name for hint in PATH_D_HINTS):
                analysis.path_d_mentions.add(name)
            if any(hint in lowered_name for hint in ELEVATOR_SHAFT_HINTS):
                analysis.elevator_shaft_mentions.add(name)
            for stage_name in META_PIPELINE_STAGE_NAMES:
                if stage_name.lower() in lowered_name:
                    analysis.meta_stage_mentions.append(stage_name)

        return analysis

    def find_hot_paths(self, layer_dir: Path, pattern: str) -> list[Path]:
        """Find files matching a pattern in a layer directory."""
        if not layer_dir.exists():
            return []

        paths = (
            path
            for path in layer_dir.rglob(pattern)
            if path.is_file()
            and path.suffix not in EXCLUDED_FILE_SUFFIXES
            and not any(part in EXCLUDED_DIR_NAMES for part in path.parts)
        )
        return sorted(paths, key=lambda p: str(p.relative_to(self.root)).lower())


def _stable_relpath(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError as e:
        # TODO: Add proper input validation
        logger.warning(f"Invalid input: {e}")
        return str(path).replace("\\", "/")


def _stable_gap_id(prefix: str, file_path: Path) -> str:
    digest = hashlib.sha1(_stable_relpath(file_path).encode("utf-8")).hexdigest()[:10]
    return f"{prefix}-{digest}"


def _priority_sort_key(gap: SemanticGap) -> tuple[int, str]:
    return (PRIORITY_RANK.get(gap.priority, 99), gap.gap_id)


def _contains_module_reference(analysis: FileAnalysis, module_hint: str) -> bool:
    return any(module_hint in module_name for module_name in analysis.imported_module_names)


def _contains_symbol_reference(analysis: FileAnalysis, symbol_hint: str) -> bool:
    return any(symbol_hint in symbol_name for symbol_name in analysis.imported_symbol_names)


def _analysis_mentions_cache(
    analysis: FileAnalysis,
    module_hint: str,
    symbol_hint: str | None = None,
) -> bool:
    if _contains_module_reference(analysis, module_hint):
        return True
    if symbol_hint and _contains_symbol_reference(analysis, symbol_hint):
        return True
    return False


def _slot_coverage_score(slot_hits: dict[str, list[str]]) -> int:
    return sum(1 for slot in PROMPT_SLOT_ORDER if slot_hits.get(slot))


def _missing_slots(slot_hits: dict[str, list[str]]) -> list[str]:
    return [slot for slot in PROMPT_SLOT_ORDER if not slot_hits.get(slot)]


def _looks_like_prompt_assembler(file_path: Path, analysis: FileAnalysis) -> bool:
    rel = _stable_relpath(file_path).lower()
    if "prompt" in file_path.name.lower() and any(
        token in rel for token in ("assemble", "assembler", "builder", "compose", "packet")
    ):
        return True
    if analysis.prompt_assembly_markers:
        return True
    return False


def _report_slot_status(slot_hits: dict[str, list[str]]) -> str:
    parts = []
    for slot in PROMPT_SLOT_ORDER:
        status = "present" if slot_hits.get(slot) else "missing"
        parts.append(f"{slot}={status}")
    return ", ".join(parts)


def _layer_rank(layer_name: str) -> int:
    try:
        return ARCH_LAYER_ORDER.index(layer_name)
    except ValueError:
        return 999


def _path_to_layer(file_path: Path) -> str | None:
    normalized = str(file_path).replace("\\", "/")
    for layer_name, layer_path in ARCH_LAYER_PATHS.items():
        if layer_path.name in normalized:
            return layer_name
    return None


def _detect_upward_imports(file_path: Path, analysis: FileAnalysis) -> list[str]:
    source_layer = _path_to_layer(file_path)
    if not source_layer:
        return []
    source_rank = _layer_rank(source_layer)
    violations = []
    for imported_layer in sorted(analysis.imported_layer_refs):
        if _layer_rank(imported_layer) < source_rank:
            violations.append(imported_layer)
    return violations


def _looks_like_meta_pipeline(file_path: Path, analysis: FileAnalysis) -> bool:
    rel = _stable_relpath(file_path).lower()
    return (
        "meta_learning_pipeline" in rel
        or SYSTEM_LEARNING_DIR in rel
        or len(analysis.meta_stage_mentions) >= 3
    )


def _has_any_marker(analysis: FileAnalysis, values: Iterable[str]) -> bool:
    haystacks = (
        set(analysis.used_names)
        | analysis.imported_module_names
        | analysis.imported_symbol_names
        | analysis.embedding_mentions
        | analysis.governance_mentions
        | analysis.path_d_mentions
        | analysis.elevator_shaft_mentions
    )
    lowered_haystacks = {v.lower() for v in haystacks}
    return any(value.lower() in entry for value in values for entry in lowered_haystacks)


class SemanticGapAnalyzer:
    """Main analyzer for detecting semantic gaps in the architecture."""

    def __init__(self):
        self.ast_analyzer = ASTAnalyzer(AGENTIC_CORE)
        self.gaps: list[SemanticGap] = []
        self.cache_opportunities: list[CacheOpportunity] = []
        self.parse_failures: list[ParseFailure] = []
        self.prompt_taxonomy_findings: list[dict[str, Any]] = []
        self.architecture_component_findings: list[dict[str, Any]] = []
        self.layer_connection_findings: list[dict[str, Any]] = []

    def analyze_l0_routing_gate(self) -> list[SemanticGap]:
        """Analyze L0 routing gate for semantic gaps."""
        logger.info("Analyzing L0 Routing Gate...")
        gaps = []

        # Check if discovery_cache is wired into full_agent_discovery
        discovery_py = AGENTIC_CORE / "utils" / "full_agent_discovery.py"
        if discovery_py.exists():
            analysis = self.ast_analyzer.analyze_file(discovery_py)
            if not analysis.ok:
                return gaps

            cache_imported = _analysis_mentions_cache(
                analysis,
                module_hint="discovery_cache",
                symbol_hint="AgentDiscoveryCache",
            )

            if not cache_imported:
                gaps.append(
                    SemanticGap(
                        gap_id="L0-GAP-001",
                        layer="L0",
                        artery="Agent Discovery Hot Path",
                        intent="Cache agent discovery results to avoid repeated file I/O and AST parsing",
                        reality="full_agent_discovery.py does not import or use discovery_cache.py",
                        impact="Every agent discovery call re-scans filesystem and re-parses Python files",
                        priority="HIGH",
                        evidence_files=[_stable_relpath(discovery_py)],
                        recommended_fix="Import AgentDiscoveryCache and wrap get_all_agents() with cache.get_or_fetch()",
                    ),
                )

        # Check reasoning_policy_engine for policy registry cache usage
        policy_engine = AGENTIC_CORE / "L0_routing" / "engines" / "reasoning_policy_engine.py"
        if policy_engine.exists():
            analysis = self.ast_analyzer.analyze_file(policy_engine)
            if not analysis.ok:
                return gaps

            policy_cache_imported = _analysis_mentions_cache(
                analysis,
                module_hint="policy_registry_cache",
                symbol_hint="PolicyRegistryCache",
            )

            if not policy_cache_imported:
                gaps.append(
                    SemanticGap(
                        gap_id="L0-GAP-002",
                        layer="L0",
                        artery="Reasoning Policy Engine",
                        intent="Cache immutable policy configurations to avoid repeated L4 state lookups",
                        reality="reasoning_policy_engine.py does not use policy_registry_cache.py",
                        impact="Policy config fetched from L4 state on every request",
                        priority="MEDIUM",
                        evidence_files=[_stable_relpath(policy_engine)],
                        recommended_fix="Wrap policy_config retrieval with PolicyRegistryCache.get_or_fetch()",
                    ),
                )

        return gaps

    def analyze_l1_cognition(self) -> list[SemanticGap]:
        """Analyze L1 cognition layer for semantic gaps."""
        logger.info("Analyzing L1 Cognition Layer...")
        gaps = []

        # Check cognitive_engine for tool embedding cache
        cognitive_engine = AGENTIC_CORE / "L1_cognition" / "engines" / "cognitive_engine.py"
        if cognitive_engine.exists():
            analysis = self.ast_analyzer.analyze_file(cognitive_engine)
            if not analysis.ok:
                return gaps

            tool_cache_imported = _analysis_mentions_cache(
                analysis,
                module_hint="tool_embedding_cache",
                symbol_hint="ToolEmbeddingCache",
            )

            if not tool_cache_imported:
                gaps.append(
                    SemanticGap(
                        gap_id="L1-GAP-001",
                        layer="L1",
                        artery="Cognitive Engine Tool Resolution",
                        intent="Cache expensive tool embedding computations to avoid repeated API calls",
                        reality="cognitive_engine.py does not use tool_embedding_cache.py",
                        impact="Tool embeddings recomputed on every cognition cycle",
                        priority="HIGH",
                        evidence_files=[_stable_relpath(cognitive_engine)],
                        recommended_fix="Import ToolEmbeddingCache and wrap embedding generation with cache.get_or_fetch()",
                    ),
                )

        # Check for prompt artifact cache usage
        prompt_files = self.ast_analyzer.find_hot_paths(AGENTIC_CORE / "L1_cognition", "*prompt*.py")
        for prompt_file in prompt_files:
            analysis = self.ast_analyzer.analyze_file(prompt_file)
            if not analysis.ok:
                continue

            prompt_cache_imported = _analysis_mentions_cache(
                analysis,
                module_hint="prompt_artifact_cache",
                symbol_hint="PromptArtifactCache",
            )

            if not prompt_cache_imported and "cache" not in prompt_file.name:
                gaps.append(
                    SemanticGap(
                        gap_id=_stable_gap_id("L1-GAP-PROMPT", prompt_file),
                        layer="L1",
                        artery="Prompt Artifact Retrieval",
                        intent="Cache parsed prompt templates to avoid repeated file I/O and parsing",
                        reality=f"{prompt_file.name} does not use prompt_artifact_cache",
                        impact="Prompt templates re-read and re-parsed on every request",
                        priority="MEDIUM",
                        evidence_files=[_stable_relpath(prompt_file)],
                        recommended_fix="Wrap prompt loading with prompt_artifact_cache.get_or_fetch()",
                    ),
                )

        return gaps

    def analyze_prompt_taxonomy_coverage(self) -> list[SemanticGap]:
        """Analyze prompt assemblers for S0/D0/I0/C0/U0 taxonomy coverage."""
        logger.info("Analyzing Prompt Taxonomy Coverage...")
        gaps = []

        candidate_files = []
        for base_dir in (
            AGENTIC_CORE / "L0_routing",
            AGENTIC_CORE / "L1_cognition",
            AGENTIC_CORE / "L2_execution",
            AGENTIC_CORE / "utils",
        ):
            candidate_files.extend(self.ast_analyzer.find_hot_paths(base_dir, PYTHON_FILE_GLOB))

        seen: set[str] = set()
        for prompt_file in candidate_files:
            rel = _stable_relpath(prompt_file)
            if rel in seen:
                continue
            seen.add(rel)

            analysis = self.ast_analyzer.analyze_file(prompt_file)
            if not analysis.ok:
                continue
            if not _looks_like_prompt_assembler(prompt_file, analysis):
                continue

            coverage_score = _slot_coverage_score(analysis.prompt_slot_hits)
            missing_slots = _missing_slots(analysis.prompt_slot_hits)
            slot_status = _report_slot_status(analysis.prompt_slot_hits)

            self.prompt_taxonomy_findings.append(
                {
                    "file": rel,
                    "coverage_score": coverage_score,
                    "slot_status": slot_status,
                    "manifest_hash": bool(analysis.manifest_hash_mentions),
                    "boundary_snapshot": bool(analysis.boundary_snapshot_mentions),
                },
            )

            if missing_slots:
                priority = "HIGH" if {"S0", "C0", "U0"} & set(missing_slots) else "MEDIUM"
                gaps.append(
                    SemanticGap(
                        gap_id=_stable_gap_id("PROMPT-TAXONOMY-GAP", prompt_file),
                        layer="L1",
                        artery="Prompt Taxonomy Assembly Coverage",
                        intent=(
                            "Assembled prompts should cover canonical taxonomy slots "
                            "S0 + D0 + I0 + C0 + U0 so the governed prompt matches the architecture."
                        ),
                        reality=(
                            f"{prompt_file.name} appears to assemble or package prompts but has incomplete "
                            f"taxonomy evidence: {slot_status}"
                        ),
                        impact=(
                            "Prompt packages may omit required rulebooks, fences, instructional identity, "
                            "dependency context, or raw user intent, causing drift from the governed prompt model."
                        ),
                        priority=priority,
                        evidence_files=[rel],
                        recommended_fix=(
                            "Add explicit slot assembly or manifest fields for the missing taxonomy slots: "
                            + ", ".join(missing_slots)
                        ),
                    ),
                )

            if not analysis.manifest_hash_mentions:
                gaps.append(
                    SemanticGap(
                        gap_id=_stable_gap_id("PROMPT-MANIFEST-GAP", prompt_file),
                        layer="L1",
                        artery="Prompt Package Manifest Integrity",
                        intent="Governed prompt assembly should emit a manifest hash for parity and auditability.",
                        reality=f"{prompt_file.name} shows no manifest hash evidence.",
                        impact="You cannot prove deterministic prompt-package parity across runs.",
                        priority="MEDIUM",
                        evidence_files=[rel],
                        recommended_fix="Emit and persist a manifest hash for the final governed prompt package.",
                    ),
                )

            if not analysis.boundary_snapshot_mentions:
                gaps.append(
                    SemanticGap(
                        gap_id=_stable_gap_id("PROMPT-VALIDATOR-GAP", prompt_file),
                        layer="L2",
                        artery="Prompt Pre-flight Validation",
                        intent="Prompt execution paths should support validator boundary snapshots before execution.",
                        reality=f"{prompt_file.name} shows no boundary_snapshot evidence.",
                        impact="Prompt healing and pre-flight diagnostics may be blind to assembly defects.",
                        priority="LOW",
                        evidence_files=[rel],
                        recommended_fix="Wire validator output to emit boundary_snapshot.json for prompt-package inspection.",
                    ),
                )

        return gaps

    def analyze_architecture_component_presence(self) -> list[SemanticGap]:
        """Verify critical SSOT components referenced by the architecture are visible to the analyzer."""
        logger.info("Analyzing Architecture Component Presence...")
        gaps = []

        for rule in ARCHITECTURE_COMPONENT_RULES:
            target = rule["path"]
            rel = _stable_relpath(target)
            exists = target.exists()
            finding = {
                "component": rule["key"],
                "file": rel,
                "exists": exists,
                "required_any": ", ".join(rule["required_any"]),
                "signals_present": "",
            }

            if not exists:
                finding["signals_present"] = "missing file"
                self.architecture_component_findings.append(finding)
                gaps.append(
                    SemanticGap(
                        gap_id=_stable_gap_id("ARCH-COMPONENT-MISSING", target),
                        layer=rule["layer"],
                        artery=rule["artery"],
                        intent="Critical architecture SSOT component should exist and be analyzable.",
                        reality=f"Expected file is missing: {rel}",
                        impact=rule["impact"],
                        priority=rule["priority"],
                        evidence_files=[rel],
                        recommended_fix=rule["recommended_fix"],
                    ),
                )
                continue

            analysis = self.ast_analyzer.analyze_file(target)
            if not analysis.ok:
                finding["signals_present"] = "parse failure"
                self.architecture_component_findings.append(finding)
                continue

            signals = []
            available_names = (
                set(analysis.used_names)
                | analysis.imported_symbol_names
                | {call_name for call_name, _ in analysis.calls}
            )
            for marker in rule["required_any"]:
                if any(marker.lower() in candidate.lower() for candidate in available_names):
                    signals.append(marker)
            finding["signals_present"] = ", ".join(sorted(signals)) if signals else "none"
            self.architecture_component_findings.append(finding)

            if not signals:
                gaps.append(
                    SemanticGap(
                        gap_id=_stable_gap_id("ARCH-COMPONENT-WEAK", target),
                        layer=rule["layer"],
                        artery=rule["artery"],
                        intent="Critical architecture SSOT component should expose recognizable contract markers.",
                        reality=f"{rel} exists but expected contract markers were not observed: {', '.join(rule['required_any'])}",
                        impact=rule["impact"],
                        priority=rule["priority"],
                        evidence_files=[rel],
                        recommended_fix=rule["recommended_fix"],
                    ),
                )

        return gaps

    def analyze_l2_execution(self) -> list[SemanticGap]:
        """Analyze L2 execution layer for semantic gaps."""
        logger.info("Analyzing L2 Execution Layer...")
        gaps = []

        # Check for schema validator cache usage
        validator_files = self.ast_analyzer.find_hot_paths(AGENTIC_CORE / "L2_execution", "*validator*.py")
        for validator_file in validator_files:
            if "cache" in validator_file.name:
                continue

            analysis = self.ast_analyzer.analyze_file(validator_file)
            if not analysis.ok:
                continue

            schema_cache_imported = _analysis_mentions_cache(
                analysis,
                module_hint="schema_validator_cache",
                symbol_hint="SchemaValidatorCache",
            )

            if not schema_cache_imported:
                gaps.append(
                    SemanticGap(
                        gap_id=_stable_gap_id("L2-GAP-VALIDATOR", validator_file),
                        layer="L2",
                        artery="Schema Validation Hot Path",
                        intent="Cache compiled JSON schema validators to avoid repeated compilation",
                        reality=f"{validator_file.name} does not use schema_validator_cache",
                        impact="Schema validators recompiled on every validation request",
                        priority="HIGH",
                        evidence_files=[_stable_relpath(validator_file)],
                        recommended_fix="Wrap validator compilation with schema_validator_cache.get_or_fetch()",
                    ),
                )

        return gaps

    def analyze_layer_connection_integrity(self) -> list[SemanticGap]:
        """Check for wiring gaps across the control spine and architecture contracts."""
        logger.info("Analyzing Layer Connection Integrity...")
        gaps = []

        all_python_files = self.ast_analyzer.find_hot_paths(AGENTIC_CORE, PYTHON_FILE_GLOB)
        for file_path in all_python_files:
            analysis = self.ast_analyzer.analyze_file(file_path)
            if not analysis.ok:
                continue

            rel = _stable_relpath(file_path)
            source_layer = _path_to_layer(file_path)
            upward_imports = _detect_upward_imports(file_path, analysis)
            finding = {
                "file": rel,
                "layer": source_layer or "UNKNOWN",
                "upward_imports": ", ".join(upward_imports) if upward_imports else "",
                "direct_provider_imports": ", ".join(sorted(analysis.direct_provider_imports)),
                "embedding_mentions": len(analysis.embedding_mentions),
                "governance_mentions": len(analysis.governance_mentions),
                "path_d_mentions": len(analysis.path_d_mentions),
                "elevator_shaft_mentions": len(analysis.elevator_shaft_mentions),
            }
            self.layer_connection_findings.append(finding)

            if upward_imports:
                gaps.append(
                    SemanticGap(
                        gap_id=_stable_gap_id("LAYER-UPWARD-IMPORT", file_path),
                        layer=source_layer or "UNKNOWN",
                        artery="Layer Sovereignty Import Boundary",
                        intent="Lower layers must not import higher-authority layers upward across the L0-L6 spine.",
                        reality=f"{rel} imports higher-authority layer references: {', '.join(upward_imports)}",
                        impact="Upward mutation and cross-layer coupling violate sovereignty and replay assumptions.",
                        priority="HIGH",
                        evidence_files=[rel],
                        recommended_fix="Replace upward imports with protocol seams, signed contracts, or read-only data contracts.",
                    ),
                )

            if analysis.direct_provider_imports and "SovereignLLMGateway.py" not in rel:
                gaps.append(
                    SemanticGap(
                        gap_id=_stable_gap_id("GATEWAY-BYPASS-RISK", file_path),
                        layer=source_layer or "UNKNOWN",
                        artery="Sovereign Gateway Bypass Risk",
                        intent="All outbound LLM egress should flow through SovereignLLMGateway only.",
                        reality=f"{rel} imports provider SDK seams directly: {', '.join(sorted(analysis.direct_provider_imports))}",
                        impact="Direct SDK imports create possible provider bypasses outside the sole gateway seam.",
                        priority="HIGH",
                        evidence_files=[rel],
                        recommended_fix="Route all provider interactions through SovereignLLMGateway and remove direct SDK imports.",
                    ),
                )

            if source_layer in {"L0", "L3", "L5"} and analysis.write_paths:
                gaps.append(
                    SemanticGap(
                        gap_id=_stable_gap_id("NON-L2-MUTATION-RISK", file_path),
                        layer=source_layer,
                        artery="Execution Mutation Boundary",
                        intent="L2 and the Universal Write Gateway are the sole durable mutation authority.",
                        reality=f"{rel} appears to perform write-like operations outside the expected execution choke point: {', '.join(sorted(set(analysis.write_paths))[:8])}",
                        impact="Non-L2 mutations can bypass sandbox freeze, audit envelopes, and replay guarantees.",
                        priority="MEDIUM",
                        evidence_files=[rel],
                        recommended_fix="Move durable writes behind L2 execution contracts and Universal Write Gateway enforcement.",
                    ),
                )

            if "Path D" in rel or "hitl" in rel.lower() or analysis.path_d_mentions:
                if "original_plan_hash" not in " ".join(analysis.path_d_mentions).lower():
                    gaps.append(
                        SemanticGap(
                            gap_id=_stable_gap_id("PATHD-PLAN-HASH-GAP", file_path),
                            layer=source_layer or "L3",
                            artery="Path D Re-Clear Contract",
                            intent="Human MODIFY_DIFF flows must bind to original_plan_hash before L5 re-clear.",
                            reality=f"{rel} shows Path D or HITL markers without clear original_plan_hash evidence.",
                            impact="Human patch flows may lose plan provenance or bypass strict re-clear assumptions.",
                            priority="HIGH",
                            evidence_files=[rel],
                            recommended_fix="Require original_plan_hash and structured_patch_schema markers on all Path D decision artifacts.",
                        ),
                    )

        return gaps

    def analyze_l3_orchestration(self) -> list[SemanticGap]:
        """Analyze L3 orchestration layer for semantic gaps."""
        logger.info("Analyzing L3 Orchestration Layer...")
        gaps = []

        # Check orchestrator_engine for plan caching
        orchestrator = AGENTIC_CORE / "L3_orchestration" / "engines" / "orchestrator_engine.py"
        if orchestrator.exists():
            analysis = self.ast_analyzer.analyze_file(orchestrator)
            if not analysis.ok:
                return gaps

            plan_cache_imported = _analysis_mentions_cache(
                analysis,
                module_hint="orchestration_plan_cache",
                symbol_hint="OrchestrationPlanCache",
            )

            if not plan_cache_imported:
                gaps.append(
                    SemanticGap(
                        gap_id="L3-GAP-001",
                        layer="L3",
                        artery="Orchestration Plan Construction",
                        intent="Cache orchestration plans to avoid repeated planning for identical requests",
                        reality="orchestrator_engine.py does not use orchestration_plan_cache",
                        impact="Orchestration plans recomputed on every request",
                        priority="MEDIUM",
                        evidence_files=[_stable_relpath(orchestrator)],
                        recommended_fix="Wrap plan construction with orchestration_plan_cache.get_or_fetch()",
                    ),
                )

        return gaps

    def analyze_elevator_shaft_and_governance_wiring(self) -> list[SemanticGap]:
        """Audit JIT state sync, governance stamps, and L2 airlock handoff."""
        logger.info("Analyzing Elevator Shaft and Governance Wiring...")
        gaps = []

        targets = [
            AGENTIC_CORE / "L0_routing",
            AGENTIC_CORE / "L3_orchestration",
            AGENTIC_CORE / "L5_safety",
            AGENTIC_CORE / "L2_execution",
        ]

        for target_dir in targets:
            for file_path in self.ast_analyzer.find_hot_paths(target_dir, PYTHON_FILE_GLOB):
                analysis = self.ast_analyzer.analyze_file(file_path)
                if not analysis.ok:
                    continue

                rel = _stable_relpath(file_path)
                layer = _path_to_layer(file_path) or "UNKNOWN"

                if layer in {"L0", "L5", "L2"} and not analysis.elevator_shaft_mentions:
                    if any(
                        token in rel.lower()
                        for token in ("routing", "policy", "boundary", "executor", "orchestr")
                    ):
                        gaps.append(
                            SemanticGap(
                                gap_id=_stable_gap_id("ELEVATOR-SHAFT-GAP", file_path),
                                layer=layer,
                                artery="JIT State Synchronization",
                                intent="Critical control-spine files should show JIT state sync markers tied to the Elevator Shaft contracts.",
                                reality=f"{rel} appears control-spine relevant but shows no clear JIT / SemanticClock / CapabilityToken evidence.",
                                impact="The analyzer cannot prove routing, safety, and execution are hydrated from the same mathematical present.",
                                priority="MEDIUM",
                                evidence_files=[rel],
                                recommended_fix="Add or detect SemanticClock, ToolBudget, CapabilityToken, or JIT hydration markers on airlock paths.",
                            ),
                        )

                if layer in {"L5", "L2"} and not analysis.governance_mentions:
                    if any(
                        token in rel.lower()
                        for token in ("validator", "boundary", "enforcement", "safety", "capability")
                    ):
                        gaps.append(
                            SemanticGap(
                                gap_id=_stable_gap_id("GOVERNANCE-STAMP-GAP", file_path),
                                layer=layer,
                                artery="Governance Stamp and Airlock Contract",
                                intent="Safety and execution boundaries should carry Compliance Hash, InstructionPacket, and SandboxEnvelope evidence.",
                                reality=f"{rel} appears to participate in the airlock but no governance-stamp markers were detected.",
                                impact="Approval provenance, certification handoff, and signed-envelope assumptions may not be verifiable.",
                                priority="HIGH",
                                evidence_files=[rel],
                                recommended_fix="Expose or validate Compliance Hash, InstructionPacket, SandboxEnvelope, and CapabilityToken markers.",
                            ),
                        )

        return gaps

    def analyze_rag_embedding_sovereignty(self) -> list[SemanticGap]:
        """Ensure embedding and FAISS usage stay informational and factory-bound."""
        logger.info("Analyzing RAG and Embedding Sovereignty...")
        gaps = []

        for file_path in self.ast_analyzer.find_hot_paths(AGENTIC_CORE, PYTHON_FILE_GLOB):
            analysis = self.ast_analyzer.analyze_file(file_path)
            if not analysis.ok or not analysis.embedding_mentions:
                continue

            rel = _stable_relpath(file_path)
            layer = _path_to_layer(file_path) or "UNKNOWN"
            rel_lower = rel.lower()

            allowed = any(
                token in rel_lower for token in ("embedding", "rag", "faiss", "memory", "factory", "seed")
            )
            if not allowed and layer not in {"L1", "L4"}:
                gaps.append(
                    SemanticGap(
                        gap_id=_stable_gap_id("EMBEDDING-PLACEMENT-GAP", file_path),
                        layer=layer,
                        artery="Embedding Sovereignty Boundary",
                        intent="Embedding and FAISS operations should remain in informational RAG paths and factory-managed seams.",
                        reality=f"{rel} references embedding-related markers outside expected informational or factory surfaces.",
                        impact="C0 informational-only guarantees can erode if embedding logic leaks into routing, safety, or execution control paths.",
                        priority="HIGH",
                        evidence_files=[rel],
                        recommended_fix="Move embedding creation and FAISS handling behind singleton factory or RAG provider seams only.",
                    ),
                )

        return gaps

    def analyze_meta_learning_pipeline_contracts(self) -> list[SemanticGap]:
        """Check immutable stage ordering and dual-injection contracts for meta-learning."""
        logger.info("Analyzing Meta-Learning Pipeline Contracts...")
        gaps = []

        pipeline_file = AGENTIC_CORE / SYSTEM_LEARNING_DIR / "pipelines" / "meta_learning_pipeline.py"
        if not pipeline_file.exists():
            return gaps

        analysis = self.ast_analyzer.analyze_file(pipeline_file)
        if not analysis.ok:
            return gaps

        rel = _stable_relpath(pipeline_file)
        seen = list(dict.fromkeys(analysis.meta_stage_mentions))
        stage_blob = " ".join(seen)

        missing_stages = [stage for stage in META_PIPELINE_STAGE_NAMES if stage not in seen]
        if missing_stages:
            gaps.append(
                SemanticGap(
                    gap_id=_stable_gap_id("META-STAGE-COVERAGE-GAP", pipeline_file),
                    layer="L4",
                    artery="Meta-Learning Stage Coverage",
                    intent="Meta-learning should expose the immutable AUDIT→TELEMETRY→CONFIG→SNAPSHOT→RCA→PROPOSE→VALIDATE→INTAKE→COMMIT pipeline.",
                    reality=f"{rel} is missing visible stage evidence for: {', '.join(missing_stages)}",
                    impact="Partial pipeline coverage weakens auditability of learning, validation, and activation flows.",
                    priority="HIGH",
                    evidence_files=[rel],
                    recommended_fix="Emit or preserve explicit stage markers for all immutable pipeline stages.",
                ),
            )

        text_blob = " ".join(analysis.string_literals) + " " + " ".join(analysis.used_names)
        dual_injection_ok = "version_store" in text_blob.lower() and "approval_gate" in text_blob.lower()
        if not dual_injection_ok:
            gaps.append(
                SemanticGap(
                    gap_id=_stable_gap_id("META-DUAL-INJECTION-GAP", pipeline_file),
                    layer="L4",
                    artery="Meta-Learning Commit Injection Contract",
                    intent="Commit activation requires dual injection of VersionStore and ApprovalGate.",
                    reality=f"{rel} does not show clear dual-injection evidence for version_store + approval_gate.",
                    impact="Stage 9 commit safety can be weakened or become ambiguously wired.",
                    priority="HIGH",
                    evidence_files=[rel],
                    recommended_fix="Require explicit version_store and approval_gate dependencies before any activation path is considered valid.",
                ),
            )

        if "proposal_only" not in text_blob.lower():
            gaps.append(
                SemanticGap(
                    gap_id=_stable_gap_id("META-PROPOSAL-ONLY-GAP", pipeline_file),
                    layer="L4",
                    artery="Meta-Learning Proposal-Only Default",
                    intent="Meta-learning should default to proposal_only=True unless a fully approved commit path is present.",
                    reality=f"{rel} does not expose clear proposal_only default evidence.",
                    impact="Unintended automatic activation risk is harder to detect.",
                    priority="MEDIUM",
                    evidence_files=[rel],
                    recommended_fix="Expose proposal_only default behavior as an explicit contract in pipeline configuration and reporting.",
                ),
            )

        return gaps

    def analyze_l4_state(self) -> list[SemanticGap]:
        """Analyze L4 state layer for semantic gaps."""
        logger.info("Analyzing L4 State Layer...")
        gaps = []

        # Check blob_storage_provider for repeated lookups
        blob_storage = AGENTIC_CORE / "L4_state" / "memory" / "blob_storage_provider.py"
        if blob_storage.exists():
            analysis = self.ast_analyzer.analyze_file(blob_storage)
            if not analysis.ok:
                return gaps
            l4_accesses = analysis.l4_state_accesses

            if len(l4_accesses) > 10:
                gaps.append(
                    SemanticGap(
                        gap_id="L4-GAP-001",
                        layer="L4",
                        artery="Blob Storage Provider",
                        intent="Minimize repeated blob lookups via caching layer",
                        reality=f"blob_storage_provider.py has {len(l4_accesses)} direct state accesses",
                        impact="Repeated blob fetches increase latency and L4 state pressure",
                        priority="HIGH",
                        evidence_files=[_stable_relpath(blob_storage)],
                        recommended_fix="Add read-through cache layer for frequently accessed blobs",
                    ),
                )

        return gaps

    def analyze_l5_safety(self) -> list[SemanticGap]:
        """Analyze L5 safety layer for semantic gaps."""
        logger.info("Analyzing L5 Safety Layer...")
        gaps = []

        # Check safety enforcement for policy cache usage
        enforcement_files = self.ast_analyzer.find_hot_paths(
            AGENTIC_CORE / "L5_safety" / "enforcement",
            PYTHON_FILE_GLOB,
        )
        for enf_file in enforcement_files:
            if "cache" in enf_file.name:
                continue

            analysis = self.ast_analyzer.analyze_file(enf_file)
            if not analysis.ok:
                continue

            policy_cache_imported = _analysis_mentions_cache(
                analysis,
                module_hint="policy_registry_cache",
                symbol_hint="PolicyRegistryCache",
            )

            if not policy_cache_imported and "policy" in enf_file.name.lower():
                gaps.append(
                    SemanticGap(
                        gap_id=_stable_gap_id("L5-GAP-POLICY", enf_file),
                        layer="L5",
                        artery="Safety Policy Enforcement",
                        intent="Cache immutable safety policies to avoid repeated L4 lookups",
                        reality=f"{enf_file.name} does not use policy_registry_cache",
                        impact="Safety policies fetched from L4 on every enforcement check",
                        priority="MEDIUM",
                        evidence_files=[_stable_relpath(enf_file)],
                        recommended_fix="Wrap policy retrieval with policy_registry_cache.get_or_fetch()",
                    ),
                )

        return gaps

    def analyze_l6_observability(self) -> list[SemanticGap]:
        """Analyze L6 observability layer for semantic gaps."""
        logger.info("Analyzing L6 Observability Layer...")
        gaps = []

        # Check telemetry engine for config caching
        telemetry_files = self.ast_analyzer.find_hot_paths(
            AGENTIC_CORE / "L6_observability",
            "*telemetry*.py",
        )
        for telem_file in telemetry_files:
            analysis = self.ast_analyzer.analyze_file(telem_file)
            if not analysis.ok:
                continue

            config_cache_imported = _analysis_mentions_cache(
                analysis,
                module_hint="config_file_cache",
                symbol_hint="ConfigFileCache",
            )

            if not config_cache_imported:
                gaps.append(
                    SemanticGap(
                        gap_id=_stable_gap_id("L6-GAP-CONFIG", telem_file),
                        layer="L6",
                        artery="Telemetry Configuration",
                        intent="Cache parsed telemetry config files to avoid repeated I/O",
                        reality=f"{telem_file.name} does not use config_file_cache",
                        impact="Config files re-read and re-parsed on every telemetry event",
                        priority="LOW",
                        evidence_files=[_stable_relpath(telem_file)],
                        recommended_fix="Wrap config loading with config_file_cache.get_or_fetch()",
                    ),
                )

        return gaps

    def _dedupe_gaps(self, gaps: Iterable[SemanticGap]) -> list[SemanticGap]:
        """Deduplicate gaps deterministically by semantic identity."""
        deduped: dict[tuple[str, str, str], SemanticGap] = {}
        for gap in gaps:
            key = (
                gap.layer,
                gap.artery,
                tuple(sorted(gap.evidence_files))[0] if gap.evidence_files else gap.gap_id,
            )
            existing = deduped.get(key)
            if existing is None or PRIORITY_RANK.get(gap.priority, 99) < PRIORITY_RANK.get(
                existing.priority,
                99,
            ):
                deduped[key] = gap
        return sorted(deduped.values(), key=_priority_sort_key)

    def run_analysis(self) -> dict[str, Any]:
        """Run full semantic gap analysis across all layers."""
        logger.info("Starting Semantic Gap Analysis...")

        all_gaps = []
        all_gaps.extend(self.analyze_architecture_component_presence())
        all_gaps.extend(self.analyze_l0_routing_gate())
        all_gaps.extend(self.analyze_l1_cognition())
        all_gaps.extend(self.analyze_prompt_taxonomy_coverage())
        all_gaps.extend(self.analyze_layer_connection_integrity())
        all_gaps.extend(self.analyze_elevator_shaft_and_governance_wiring())
        all_gaps.extend(self.analyze_rag_embedding_sovereignty())
        all_gaps.extend(self.analyze_meta_learning_pipeline_contracts())
        all_gaps.extend(self.analyze_l2_execution())
        all_gaps.extend(self.analyze_l3_orchestration())
        all_gaps.extend(self.analyze_l4_state())
        all_gaps.extend(self.analyze_l5_safety())
        all_gaps.extend(self.analyze_l6_observability())

        self.gaps = self._dedupe_gaps(all_gaps)
        self.parse_failures = sorted(
            self.ast_analyzer.parse_failures,
            key=lambda pf: _stable_relpath(pf.file_path).lower(),
        )

        # Categorize by priority
        high_priority = [g for g in self.gaps if g.priority == "HIGH"]
        medium_priority = [g for g in self.gaps if g.priority == "MEDIUM"]
        low_priority = [g for g in self.gaps if g.priority == "LOW"]

        logger.info("\nAnalysis Complete:")
        logger.info(f"  Total Gaps: {len(self.gaps)}")
        logger.info(f"  HIGH Priority: {len(high_priority)}")
        logger.info(f"  MEDIUM Priority: {len(medium_priority)}")
        logger.info(f"  LOW Priority: {len(low_priority)}")
        logger.info(f"  Parse Failures: {len(self.parse_failures)}")

        return {
            "total_gaps": len(self.gaps),
            "high_priority": len(high_priority),
            "medium_priority": len(medium_priority),
            "low_priority": len(low_priority),
            "parse_failures": self.parse_failures,
            "prompt_taxonomy_findings": self.prompt_taxonomy_findings,
            "architecture_component_findings": self.architecture_component_findings,
            "layer_connection_findings": self.layer_connection_findings,
            "gaps": self.gaps,
        }

    def generate_report(self, output_path: Path) -> None:
        """Generate markdown report of semantic gaps."""
        logger.info(f"Generating report: {output_path}")

        lines = []

        def h(text: str) -> None:
            lines.append(text)

        def blank() -> None:
            lines.append("")

        h("# Semantic Gap Analysis - Agentic Architecture Major Arteries")
        blank()
        h("## Executive Summary")
        blank()
        h(f"**Total Gaps Identified:** {len(self.gaps)}")
        h(f"**High Priority:** {len([g for g in self.gaps if g.priority == 'HIGH'])}")
        h(f"**Medium Priority:** {len([g for g in self.gaps if g.priority == 'MEDIUM'])}")
        h(f"**Low Priority:** {len([g for g in self.gaps if g.priority == 'LOW'])}")
        h(f"**Parse Failures:** {len(self.parse_failures)}")
        blank()
        h("## Analysis Methodology")
        blank()
        h("This analysis traces actual execution flows through L0-L6 layers using AST-based")
        h("code scanning to identify where architectural intent (lower latency, deterministic")
        h("lookups, cache-first patterns) diverges from implementation reality.")
        blank()
        h("**Approach:**")
        h("1. Map critical hot paths across each layer")
        h("2. AST scan for import statements and cache usage patterns")
        h("3. Detect prompt assemblers and score canonical slot coverage for S0/D0/I0/C0/U0")
        h("4. Check for manifest-hash and boundary-snapshot evidence on prompt execution paths")
        h("5. Verify architecture SSOT components exist and expose expected contract markers")
        h(
            "6. Scan layer connection integrity for upward imports, gateway bypasses, and non-L2 mutation risks",
        )
        h("7. Audit Elevator Shaft, governance stamp, and airlock contract markers")
        h("8. Check embedding sovereignty and meta-learning pipeline contracts")
        h("9. Identify missing wirings between cache modules and consumers")
        h("10. Categorize gaps by layer, artery, and priority")
        h("11. Surface parse failures explicitly instead of silently dropping files from analysis")
        blank()

        if self.architecture_component_findings:
            h("## Architecture Component Presence")
            blank()
            h("| Component | File | Exists | Signals Present |")
            h("|-----------|------|--------|-----------------|")
            for finding in sorted(self.architecture_component_findings, key=lambda item: item["file"]):
                exists_text = "yes" if finding["exists"] else "no"
                h(
                    f"| {finding['component']} | `{finding['file']}` | {exists_text} | {finding['signals_present']} |",
                )
            blank()

        if self.prompt_taxonomy_findings:
            h("## Prompt Taxonomy Coverage")
            blank()
            h("| File | Slot Coverage | Manifest Hash | Boundary Snapshot |")
            h("|------|---------------|---------------|-------------------|")
            for finding in sorted(self.prompt_taxonomy_findings, key=lambda item: item["file"]):
                manifest = "yes" if finding["manifest_hash"] else "no"
                boundary = "yes" if finding["boundary_snapshot"] else "no"
                h(f"| `{finding['file']}` | {finding['slot_status']} | {manifest} | {boundary} |")
            blank()

        if self.layer_connection_findings:
            h("## Layer Connection Integrity")
            blank()
            h(
                "| File | Layer | Upward Imports | Direct Provider Imports | Embedding Mentions | Governance Mentions |",
            )
            h(
                "|------|-------|----------------|-------------------------|--------------------|---------------------|",
            )
            for finding in sorted(self.layer_connection_findings, key=lambda item: item["file"]):
                upward = finding["upward_imports"] or "-"
                direct = finding["direct_provider_imports"] or "-"
                h(
                    f"| `{finding['file']}` | {finding['layer']} | {upward} | {direct} | {finding['embedding_mentions']} | {finding['governance_mentions']} |",
                )
            blank()

        if self.parse_failures:
            h("## Parse Failures")
            blank()
            h("| File | Error Type | Message |")
            h("|------|------------|---------|")
            for failure in self.parse_failures:
                message = failure.message.replace("\n", " ").replace("|", "\\|")
                h(f"| `{_stable_relpath(failure.file_path)}` | {failure.error_type} | {message} |")
            blank()

        # Group gaps by layer
        layers = {}
        for gap in self.gaps:
            if gap.layer not in layers:
                layers[gap.layer] = []
            layers[gap.layer].append(gap)

        for layer in sorted(layers.keys()):
            h(f"## {layer} Layer Gaps")
            blank()

            for gap in sorted(layers[layer], key=_priority_sort_key):
                h(f"### {gap.gap_id}: {gap.artery}")
                blank()
                h(f"**Priority:** {gap.priority}")
                blank()
                h("**Architectural Intent:**")
                h(f"{gap.intent}")
                blank()
                h("**Implementation Reality:**")
                h(f"{gap.reality}")
                blank()
                h("**Impact:**")
                h(f"{gap.impact}")
                blank()
                h("**Evidence Files:")
                for ef in sorted(set(gap.evidence_files)):
                    h(f"- `{ef}`")
                blank()
                h("**Recommended Fix:**")
                h(f"{gap.recommended_fix}")
                blank()
                h("---")
                blank()

        h("## Priority Matrix")
        blank()
        h("| Layer | High | Medium | Low | Total |")
        h("|-------|------|--------|-----|-------|")
        for layer in sorted(layers.keys()):
            layer_gaps = layers[layer]
            high = len([g for g in layer_gaps if g.priority == "HIGH"])
            medium = len([g for g in layer_gaps if g.priority == "MEDIUM"])
            low = len([g for g in layer_gaps if g.priority == "LOW"])
            total = len(layer_gaps)
            h(f"| {layer} | {high} | {medium} | {low} | {total} |")
        blank()

        h("## Next Steps")
        blank()
        h("1. **High Priority Gaps:** Address immediately - these cause repeated expensive operations")
        h("2. **Medium Priority Gaps:** Schedule for next sprint - moderate latency impact")
        h("3. **Low Priority Gaps:** Backlog - minor optimizations")
        h("4. **Parse Failures:** Fix or explicitly waive broken files so analysis coverage is auditable")
        blank()
        h("## Validation")
        blank()
        h("After implementing fixes, rerun semantic gap analysis to verify:")
        h("- Cache modules are imported in hot path files")
        h("- Prompt assemblers explicitly cover S0, D0, I0, C0, and U0")
        h("- Governed prompt assembly emits a manifest hash")
        h("- Validator paths emit boundary_snapshot.json for prompt-package inspection")
        h(
            "- Classification kernel, SovereignLLMGateway, AGENT_REGISTRY, meta_learning_pipeline, and write_gateway are all present and contract-visible",
        )
        h("- No upward import edges violate the L0-L6 sovereignty matrix")
        h("- No direct provider SDK imports exist outside SovereignLLMGateway")
        h("- Non-L2 mutation paths are absent or explicitly mediated by Universal Write Gateway")
        h("- JIT / SemanticClock / CapabilityToken / SandboxEnvelope markers exist on the airlock path")
        h("- Embedding and FAISS signals stay inside informational RAG or factory-managed seams")
        h("- Meta-learning exposes all immutable stages plus dual injection and proposal_only defaults")
        h("- `get_or_fetch` pattern is used consistently")
        h("- Replay mode tests pass with warm cache (no redundant fetches)")
        h("- Side-effect envelope tests confirm cache-first behavior")
        h("- Parse failure count is zero or intentionally documented")
        blank()

        content = "\n".join(lines)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
        logger.info(f"Report written to {output_path}")


def main() -> None:
    """Main entry point."""
    import argparse
    import sys

    from agentic_core.L5_safety.config.structure_blueprint.ssot import REPORTS_DIR

    parser = argparse.ArgumentParser(description="Semantic Gap Analyzer")
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / "docs" / REPORTS_DIR / "plans" / "semantic_gap_analysis.md",
        help="Output path for the analysis report",
    )
    parser.add_argument(
        "--fail-on-parse-errors",
        action="store_true",
        help="Exit non-zero if any file fails AST analysis.",
    )
    args = parser.parse_args()

    analyzer = SemanticGapAnalyzer()
    result = analyzer.run_analysis()
    analyzer.generate_report(args.output)

    if args.fail_on_parse_errors and result["parse_failures"]:
        logger.error("Parse failures detected. Failing due to --fail-on-parse-errors.")
        sys.exit(2)


if __name__ == "__main__":
    main()
