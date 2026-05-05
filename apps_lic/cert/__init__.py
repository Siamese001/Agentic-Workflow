"""Certification package for apps_lic.

This package provides certification and Final Evidence Contract (FEC)
producers for apps_lic exit evaluation.

Pattern Source: apps-qna-c0-fec-producer-wiring-d4f1e8
"""

from __future__ import annotations

# Side-effect: Register FEC producer on import
from apps_lic.cert.fec_producer import register as _register_fec_producer
_register_fec_producer()

# Exports
from apps_lic.cert.fec_producer import produce_fec, PRODUCER_ID, FEC_SCHEMA_VERSION

__all__ = [
    "produce_fec",
    "PRODUCER_ID",
    "FEC_SCHEMA_VERSION",
]
