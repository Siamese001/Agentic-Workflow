"""apps_rg cert-path utilities.

Importing this package auto-registers the apps_rg FEC producer with the
shared registry so cert entrypoints resolve a real producer without needing
explicit wiring at call sites.

Plan: .windsurf/plans/dom007-fec-producers-followup-e9f3c1.md W3.P1.
Linked Author-Gate decision: dec_19dedd3f565173b7f (heuristic_split).
"""

from __future__ import annotations

from apps_shared.cert.fec_producer import register_producer

from apps_rg.cert.fec_producer import produce_fec

register_producer("apps_rg", produce_fec)

__all__ = ["produce_fec"]
