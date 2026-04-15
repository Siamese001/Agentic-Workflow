"""Metrics sidecar — exposes AGENTIC_REGISTRY on :8000/metrics.

Run alongside any apps_* worker that emits semantic-cache events.
Required for canary soak monitoring (PG-12, PG-18).

Usage:
    python ops_scripts/dev_tools/start_metrics_sidecar.py

The sidecar blocks until killed.  Port 8000 is the Prometheus scrape target
documented in docs/monitoring/semantic_cache_observability.md §1.
"""

from __future__ import annotations

import logging
import signal
import sys
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
_log = logging.getLogger("metrics_sidecar")

_PORT = 8000
_POLL_SECONDS = 30


def main() -> None:
    try:
        from prometheus_client import start_http_server
        from agentic_core.L6_observability.utils.metrics.prometheus_metrics import (
            AGENTIC_REGISTRY,
        )  # guardian: allow-layer-violation -- ops_scripts sidecar is an observability harness; L6 import is its sole purpose
    except ImportError as exc:
        _log.critical("Cannot import prometheus_client or AGENTIC_REGISTRY: %s", exc)
        sys.exit(1)

    start_http_server(port=_PORT, registry=AGENTIC_REGISTRY)
    _log.info("Metrics sidecar listening on :%d/metrics  (AGENTIC_REGISTRY)", _PORT)
    _log.info("Scrape with: curl -s http://localhost:%d/metrics | grep semantic_cache", _PORT)

    def _shutdown(sig: int, _frame: object) -> None:
        _log.info("Signal %d received — sidecar stopping", sig)
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    while True:
        time.sleep(_POLL_SECONDS)
        _log.debug("Sidecar alive — metrics still being served on :%d", _PORT)


if __name__ == "__main__":
    main()
