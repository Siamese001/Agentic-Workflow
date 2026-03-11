from dataclasses import dataclass


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
