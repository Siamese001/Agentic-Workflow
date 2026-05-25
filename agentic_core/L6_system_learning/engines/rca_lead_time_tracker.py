"""V6 KPI tracker for RCA_TO_PROPOSAL_LEAD_TIME.

This module holds a rolling list of lead-time samples (incident-close
epoch -> proposal-emitted epoch) and computes the p95 on demand. It lives
outside both ``rca_engine`` and ``rule_drafting_engine`` because the v6
KPI measures the *gap* between them — neither end owns the metric alone.

Usage
-----
At orchestration time:

.. code-block:: python

    tracker = RCALeadTimeTracker()
    # ... when an incident closes:
    tracker.mark_incident_closed(incident_id="inc-123", epoch=t0)
    # ... when a proposal is emitted for that incident:
    tracker.mark_proposal_emitted(incident_id="inc-123", epoch=t1)
    # ... periodically:
    tracker.publish_kpi_sample(board)

If a proposal is recorded for an incident with no prior closure, the
sample is silently dropped (RCA may have skipped the close step in test
fixtures or replay scenarios).
"""

from __future__ import annotations

import logging
import math
from typing import Any

logger = logging.getLogger(__name__)


class RCALeadTimeTracker:
    """Holds incident-close timestamps and computes lead-time samples.

    The tracker stores at most ``max_samples`` recent (incident_id,
    lead_time_seconds) tuples to bound memory.
    """

    DEFAULT_MAX_SAMPLES: int = 1024

    def __init__(self, *, max_samples: int | None = None) -> None:
        self._max_samples: int = max_samples or self.DEFAULT_MAX_SAMPLES
        # incident_id -> close epoch
        self._open_incidents: dict[str, float] = {}
        # rolling list of (incident_id, lead_time_seconds)
        self._samples: list[tuple[str, float]] = []

    def mark_incident_closed(self, *, incident_id: str, epoch: float) -> None:
        """Record that an incident closed at ``epoch``."""
        if not incident_id:
            return
        self._open_incidents[incident_id] = float(epoch)

    def mark_proposal_emitted(self, *, incident_id: str, epoch: float) -> float | None:
        """Record proposal emission and compute the lead time.

        Returns the lead time in seconds, or ``None`` if no closure was
        previously recorded for ``incident_id``.
        """
        if not incident_id:
            return None
        closed_epoch = self._open_incidents.pop(incident_id, None)
        if closed_epoch is None:
            return None
        lead = max(0.0, float(epoch) - closed_epoch)
        self._samples.append((incident_id, lead))
        # bound memory
        if len(self._samples) > self._max_samples:
            overflow = len(self._samples) - self._max_samples
            self._samples = self._samples[overflow:]
        return lead

    @property
    def sample_count(self) -> int:
        return len(self._samples)

    @property
    def open_incident_count(self) -> int:
        return len(self._open_incidents)

    def reset(self) -> None:
        self._open_incidents.clear()
        self._samples.clear()

    def p95_lead_time_seconds(self) -> float:
        """Return the p95 lead time across current samples.

        Returns ``0.0`` when no samples are available (the v6 zero-sample
        convention is "we have no data to flag").
        """
        if not self._samples:
            return 0.0
        leads = sorted(s for _, s in self._samples)
        # nearest-rank p95 (no interpolation — deterministic and small-set
        # safe per v6 reproducibility discipline).
        rank = max(0, math.ceil(0.95 * len(leads)) - 1)
        return float(leads[rank])

    def publish_kpi_sample(self, board: Any) -> None:
        """Publish RCA_TO_PROPOSAL_LEAD_TIME (p95 seconds) to ``board``.

        Lazy-imports the producer helper. Never raises.
        """
        try:
            from .v6_kpi_producers import (  # noqa: PLC0415
                record_rca_to_proposal_lead_time,
            )

            record_rca_to_proposal_lead_time(
                board,
                p95_seconds=self.p95_lead_time_seconds(),
                sample_size=len(self._samples),
            )
        except (ImportError, AttributeError, RuntimeError) as exc:  # guardian: allow-log-and-swallow -- KPI must not break orchestration
            logger.warning("v6_kpi_rca_lead_time_publish_failed: %s", exc)


__all__ = ["RCALeadTimeTracker"]
