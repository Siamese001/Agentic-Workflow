"""Runtime evidence ledger — REQ Coverage Exemplar Ledger.

Records per-(REQ_ID, trace_id, layer, edge_kind) exemplars from OTEL spans,
in OpenTelemetry exemplar style: each row links a REQ-coverage aggregate to
a specific runtime instance.

See: .windsurf/plans/runtime-evidence-foundation-54ad39.md
"""

from tools.runtime_evidence.ledger_writer import (
    DEFAULT_LEDGER_PATH,
    LedgerWriter,
    ensure_schema,
    write_emissions,
)

__all__ = [
    "DEFAULT_LEDGER_PATH",
    "LedgerWriter",
    "ensure_schema",
    "write_emissions",
]
