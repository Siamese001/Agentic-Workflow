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
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "cst_transformers_types_util")
_emit_applies_guardrail("p0", "cst_transformers_types_util", "p0_governance")
_emit_snapshots_state("p0", "cst_transformers_types_util", "state_snapshot")
