"""Batch campaign orchestration compatibility layer for apps_lic.

The orchestrator stays side-effect free except for the injected ``run_fn`` and
optional ``uwg_submit`` callback. It never aborts the batch because of a single
recipient failure.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable

_CONFIG_PATH = Path(__file__).parent.parent / "config" / "campaign_batch_policy.yaml"


def _utc_ms() -> float:
    return time.time() * 1000.0


@lru_cache(maxsize=1)
def _load_config() -> dict[str, Any]:
    try:
        import yaml  # type: ignore[import]

        with open(_CONFIG_PATH, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    except Exception:  # noqa: BLE001
        # guardian: allow-broad-except -- optional config; fall through to defaults.
        return {}


@dataclass(frozen=True)
class BatchRecipientRequest:
    """A single recipient entry in a batch campaign request."""

    recipient_id: str
    campaign_request: Any
    manifest_hash: str


@dataclass(frozen=True)
class BatchCampaignRequest:
    """Batch request wrapper passed to the campaign orchestrator."""

    batch_id: str
    sender_id: str
    entries: tuple[BatchRecipientRequest, ...]


@dataclass(frozen=True)
class BatchAdmissionReceipt:
    """Receipt emitted after batch orchestration completes."""

    batch_id: str
    sender_id: str
    total_requested: int
    total_dispatched: int
    total_failed: int
    admitted: bool
    dispatch_duration_ms: float
    entry_results: tuple[dict[str, Any], ...] = field(default_factory=tuple)


class CampaignBatchOrchestrator:
    """Dispatch a batch of campaign requests and submit one batch receipt."""

    def __init__(
        self,
        run_fn: Callable[[Any], Any],
        *,
        uwg_submit: Callable[[BatchAdmissionReceipt], Any] | None = None,
        config: dict[str, Any] | None = None,
    ) -> None:
        self._run_fn = run_fn
        self._uwg_submit = uwg_submit
        self._config = _load_config() if config is None else config
        self._max_recipients_per_batch = int(
            self._config.get("max_recipients_per_batch", 50)
        )

    def dispatch(self, batch_request: BatchCampaignRequest) -> BatchAdmissionReceipt:
        """Run each entry in the batch and submit one aggregate receipt."""
        start_ms = _utc_ms()
        entries = tuple(batch_request.entries or ())
        total_requested = len(entries)
        entry_results: list[dict[str, Any]] = []
        total_dispatched = 0
        total_failed = 0

        for entry in entries[: self._max_recipients_per_batch]:
            try:
                run_result = self._run_fn(entry.campaign_request)
            except Exception as exc:  # noqa: BLE001
                # guardian: allow-broad-except -- one failing entry must not abort the batch
                total_failed += 1
                entry_results.append(
                    {
                        "recipient_id": entry.recipient_id,
                        "manifest_hash": entry.manifest_hash,
                        "status": "failed",
                        "reason": f"{type(exc).__name__}: {exc}",
                    }
                )
                continue

            total_dispatched += 1
            entry_results.append(
                {
                    "recipient_id": entry.recipient_id,
                    "manifest_hash": entry.manifest_hash,
                    "status": "dispatched",
                    "run_id": str(getattr(run_result, "run_id", "") or ""),
                }
            )

        if total_requested > self._max_recipients_per_batch:
            overflow = entries[self._max_recipients_per_batch :]
            total_failed += len(overflow)
            for entry in overflow:
                entry_results.append(
                    {
                        "recipient_id": entry.recipient_id,
                        "manifest_hash": entry.manifest_hash,
                        "status": "rate_limited",
                        "reason": "RATE_LIMITED",
                    }
                )

        receipt = BatchAdmissionReceipt(
            batch_id=batch_request.batch_id,
            sender_id=batch_request.sender_id,
            total_requested=total_requested,
            total_dispatched=total_dispatched,
            total_failed=total_failed,
            admitted=total_failed == 0,
            dispatch_duration_ms=_utc_ms() - start_ms,
            entry_results=tuple(entry_results),
        )

        if self._uwg_submit is not None:
            try:
                self._uwg_submit(receipt)
            except Exception:  # noqa: BLE001
                # guardian: allow-broad-except -- UWG submission must never abort the batch
                pass

        return receipt


__all__ = [
    "BatchAdmissionReceipt",
    "BatchCampaignRequest",
    "BatchRecipientRequest",
    "CampaignBatchOrchestrator",
]
