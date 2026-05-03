"""apps_exec cert-path utilities.

Importing this package auto-registers the apps_exec FEC producer with the
shared registry.

Plan: ``.windsurf/plans/apps-exec-c0-fec-producer-wiring-c2e8a5.md`` W1.P1.
"""

from __future__ import annotations

from apps_shared.cert.fec_producer import register_producer

from apps_exec.cert.fec_producer import produce_fec

register_producer("apps_exec", produce_fec)

__all__ = ["produce_fec"]
