"""tools.ledgers — Intelligence-capture ledger infrastructure.

Implements the W0 shared framework for the 10-ledger rollout
(see .cursor/plans/_archive/windsurf_legacy_plans/intelligence-ledgers-ten-a7c3e2.md).

Public surface:
    - LedgerWriter   : thread-safe idempotent row writer
    - LedgerConsulter: precedent lookup with strong/suggestive/none verdict
    - LEDGER_REGISTRY: authoritative registry of all known ledgers
    - apply_schema   : idempotent migration entrypoint

Design rules:
    - stdlib only (sqlite3); no third-party deps in the writer path
    - writer never raises to its caller on non-fatal errors (fail-soft)
    - consulter is pure-read; no side effects beyond optional FTS warm
"""

from tools.ledgers.schema_registry import LEDGER_REGISTRY, LedgerSpec
from tools.ledgers.writer import LedgerWriter, writer_for
from tools.ledgers.consulter import LedgerConsulter, PrecedentVerdict

__all__ = [
    "LEDGER_REGISTRY",
    "LedgerSpec",
    "LedgerWriter",
    "LedgerConsulter",
    "PrecedentVerdict",
    "writer_for",
]
