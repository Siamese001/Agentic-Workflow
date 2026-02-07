from dataclasses import dataclass


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
