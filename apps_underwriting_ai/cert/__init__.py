"""apps_underwriting_ai cert-path utilities.

Importing this package auto-registers the apps_underwriting_ai FEC producer
with the shared registry so cert entrypoints resolve a real producer without
explicit wiring at call sites.

Plan: ``.windsurf/plans/apps-underwriting-ai-c0-fec-producer-wiring-f6b3d9.md`` W1.P1.
"""

from __future__ import annotations

from apps_shared.cert.fec_producer import register_producer

from apps_underwriting_ai.cert.fec_producer import produce_fec

register_producer("apps_underwriting_ai", produce_fec)

__all__ = ["produce_fec"]
