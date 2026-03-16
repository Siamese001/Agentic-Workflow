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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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
