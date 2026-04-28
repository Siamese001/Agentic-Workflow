"""Runtime trace contract validation surface.

Loads and validates runtime trace contracts from
``config/runtime_trace/contracts/`` and validates collected OTEL span graphs
against them.

See:
    - config/runtime_trace/README.md   (registry layout)
    - config/runtime_trace/contracts/canary_lic_v1.yaml   (example)
    - agentic_core/L6_observability/runtime_trace/contract.py   (this surface)
    - ops_scripts/ci/check_runtime_trace_contract.py   (CI gate consumer)
    - scripts/proof/run_runtime_trace_proof.py   (canary runner)
"""

from agentic_core.L6_observability.runtime_trace.canary_emitter import (
    build_canary_lic_spans,
)
from agentic_core.L6_observability.runtime_trace.contract import (
    ContractValidationError,
    RuntimeTraceContract,
    ValidationResult,
    Violation,
    load_contract,
    validate_trace,
)
from agentic_core.L6_observability.runtime_trace.snapshot_adapter import (
    snapshot_to_spans,
)

__all__ = [
    "ContractValidationError",
    "RuntimeTraceContract",
    "ValidationResult",
    "Violation",
    "build_canary_lic_spans",
    "load_contract",
    "snapshot_to_spans",
    "validate_trace",
]
