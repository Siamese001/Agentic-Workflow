"""apps_rfp cert-path utilities.

Plan: ``.windsurf/plans/apps-rfp-c0-fec-producer-wiring-b9d4f1.md`` W1.P1.
"""

from __future__ import annotations

from apps_shared.cert.fec_producer import register_producer

from apps_rfp.cert.fec_producer import produce_fec

register_producer("apps_rfp", produce_fec)

__all__ = ["produce_fec"]
