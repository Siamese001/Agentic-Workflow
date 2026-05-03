"""apps_qna cert-path utilities.

Importing this package auto-registers the apps_qna FEC producer with the
shared registry so cert entrypoints resolve a real producer without needing
explicit wiring at call sites.

Plan: .windsurf/plans/apps-qna-c0-fec-producer-wiring-d4f1e8.md W1.P1.
"""

from __future__ import annotations

from apps_shared.cert.fec_producer import register_producer

from apps_qna.cert.fec_producer import produce_fec

register_producer("apps_qna", produce_fec)

__all__ = ["produce_fec"]
