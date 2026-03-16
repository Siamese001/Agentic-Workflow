"""
CST transformer types - canonical re-export shim.

The implementation lives in agentic_core.L5_safety.types.cst_transformers_types.
This module re-exports for callers using relative imports inside
``agentic_core.L5_safety.utils.*``.
"""

from agentic_core.L5_safety.types.cst_transformers_types import *  # noqa: F401, F403
from agentic_core.L5_safety.types.cst_transformers_types import (  # noqa: F401
    BareExceptTarget,
    DocstringTarget,
    ImportTarget,
    StructuralTarget,
    SurgicalBareExceptFixer,
    SurgicalBlankLineNormalizer,
    SurgicalDocstringInserter,
    SurgicalFutureImportInserter,
    SurgicalImportRemover,
    SurgicalTrailingWhitespaceFixer,
    SurgicalTypeHintInserter,
    TypeHintTarget,
    create_bare_except_fixer,
    create_blank_line_normalizer,
    create_docstring_inserter,
    create_future_import_inserter,
    create_import_remover,
    create_trailing_whitespace_fixer,
    create_type_hint_inserter,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "cst_transformers_types_util")
emit_determinism_digest("p0", "cst_transformers_types_util")

_emit_dispatches_healing_run("p1", "cst_transformers_types_util", "L5")
_emit_routes_through("p1", "cst_transformers_types_util", "L5")
_emit_escalates_to_human("p1", "cst_transformers_types_util", "L5")
_emit_reads_policy_state("p1", "cst_transformers_types_util", "L5")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "cst_transformers_types_util")
_emit_applies_guardrail("p0", "cst_transformers_types_util", "p0_governance")
_emit_snapshots_state("p0", "cst_transformers_types_util", "state_snapshot")
_emit_authorize_and_execute("p2", "cst_transformers_types_util", "execution_auth")
_emit_validates_capability("p2", "cst_transformers_types_util", "capability_check")
_emit_routes_to_capability("p2", "cst_transformers_types_util", "capability_route")
_emit_writes_via_uwg("p2", "cst_transformers_types_util", "uwg_write")
_emit_blocks_direct_write("p2", "cst_transformers_types_util", "direct_write_block")
_emit_records_tool_invocation("p2", "cst_transformers_types_util", "tool_invocation")
_emit_captures_execution_output("p2", "cst_transformers_types_util", "exec_output")
_emit_dispatches_agent("p3", "cst_transformers_types_util", "agent_dispatch")
_emit_coordinates_agents("p3", "cst_transformers_types_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "cst_transformers_types_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "cst_transformers_types_util", "healing_outcome")
_emit_escalates_failure("p3", "cst_transformers_types_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "cst_transformers_types_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "cst_transformers_types_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "cst_transformers_types_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "cst_transformers_types_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "cst_transformers_types_util", "eval_metric")
_emit_stores_embedding("p4", "cst_transformers_types_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "cst_transformers_types_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "cst_transformers_types_util", "exec_snapshot_link")
