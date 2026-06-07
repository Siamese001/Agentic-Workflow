"""apps_research cert-path utilities.

Plan: ``docs/archive/windsurf/legacy-tree/plans/apps-research-c0-fec-producer-wiring-e7a2c3.md`` W1.P1.
"""

from __future__ import annotations

from apps_shared.cert.fec_producer import register_producer

from apps_research.cert.fec_producer import produce_fec

register_producer("apps_research", produce_fec)

__all__ = ["produce_fec"]
