from dataclasses import dataclass

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "ledger_retention_config", "L4")
_emit_routes_through("p1", "ledger_retention_config", "L4")
_emit_escalates_to_human("p1", "ledger_retention_config", "L4")
_emit_reads_policy_state("p1", "ledger_retention_config", "L4")

_emit_snapshots_state("p0", "ledger_retention_config", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "ledger_retention_config", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "ledger_retention_config")


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants


@dataclass
class LedgerRetentionConfig:
    """
    L4 Configuration: Ledger & Audit Policies.
    Controls how long the truth is kept and how it is verified.
    """

    # Audit Trail
    AUDIT_RETENTION_DAYS: int = 90
    ENABLE_HASH_CHAINING: bool = True  # Cryptographic linkage

    # Telemetry
    TRACE_SAMPLING_RATE: float = 1.0  # 1.0 = Capture 100% of traces
    MAX_TRACE_DEPTH: int = 64

    # Genealogy (Provenance)
    TRACK_FILE_LINEAGE: bool = True
    MAX_GENEALOGY_GENERATIONS: int = 20


ledger_config = LedgerRetentionConfig()
