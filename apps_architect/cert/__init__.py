"""apps_architect cert-path utilities.

Plan: ``.codex/plans/apps-architect-pattern-hardening-d7e4f9.md`` W1.P2.
"""

from __future__ import annotations

from apps_shared.cert.fec_producer import register_producer

from apps_architect.cert.fec_producer import produce_fec

register_producer("apps_architect", produce_fec)

__all__ = ["produce_fec"]
