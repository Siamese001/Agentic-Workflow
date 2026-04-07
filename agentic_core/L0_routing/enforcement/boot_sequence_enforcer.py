from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_records_execution_trace,  # noqa: E402
)

from .boot_sequence import *

_emit_records_execution_trace("p0", "evidence", "boot_sequence_enforcer")
