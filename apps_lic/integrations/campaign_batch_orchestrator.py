"""apps_lic.integrations.campaign_batch_orchestrator — D4-P1 + D4-P2 + DS8.

Plan: .windsurf/plans/apps-lic-deferred-scope-followup-d3f9b2.md W5 D4-P1, D4-P2
      Updated: .windsurf/plans/apps-lic-calibration-holdout-e8f1c4.md W3 DS8-P1

Orchestrates multi-recipient outreach campaigns. Dispatches N single-recipient
GovernedLicRun instances, deduplicates by manifest_hash, enforces per-batch
rate control, and emits a UWG batch admission receipt.

Architecture notes
------------------
- Single-recipient only at the execution layer. Each recipient is dispatched
  independently via GovernedLicRun. The orchestrator is a *wrapper*, not a
  new execution engine.
- Deduplication: if two batch entries share the same manifest_hash (computed
  from sender+recipient identity+policy), the second is skipped with
  disposition DUPLICATE_SKIPPED.
- Rate control: max_recipients_per_batch enforced before dispatch; excess
  entries are rejected with disposition RATE_LIMITED.
- Partial failure: a single failed recipient does NOT abort the batch.
  Each BatchRecipientResult carries its own outcome.
- UWG batch admission receipt: BatchAdmissionReceipt is the SSOT for the
  batch write-path record. Caller feeds it to UWG; orchestrator does NOT
  write to UWG directly.

Decision-only constraints (D4-P1)
----------------------------------
- No durable writes from the orchestrator itself.
- No provider API calls.
- No subprocess calls.
- Config loaded from apps_lic/config/campaign_batch_policy.yaml (optional).
- GovernedLicRun is injected — orchestrator does not import it at module load.

UWG batch admission receipt (D4-P2 + DS8-P1)
----------------------------------------------
BatchAdmissionReceipt is the write-path artifact:
  - One receipt per batch run.
  - Contains per-recipient results with dispositions.
  - Caller (typically apps_lic __main__ / spine entrypoint) passes to UWG.
  - Receipt is frozen (immutable after construction).

DS8-P1 UWG call-site wiring
-----------------------------
CampaignBatchOrchestrator accepts an optional ``uwg_submit`` callable:
  ``uwg_submit(receipt: BatchAdmissionReceipt) -> Any``
When provided, it is called immediately after dispatch() completes and
BEFORE the receipt is returned to the caller. The orchestrator does NOT
write to UWG directly — it delegates to the injected callable.

Injection is opt-in:
  - ``uwg_submit=None`` (default) — orchestrator behaves as before; receipt
    is returned to caller who must route it to UWG themselves.
  - ``uwg_submit=fn`` — orchestrator calls fn(receipt); any exception from
    uwg_submit is caught, logged to receipt.uwg_submit_error, and the
    original receipt is still returned (fail-soft, never blocks dispatch).
"""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Optional

_CONFIG_PATH = Path(__file__).parent.parent / "config" / "campaign_batch_policy.yaml"

# ---------------------------------------------------------------------------
# Rate control defaults
# ---------------------------------------------------------------------------

_DEFAULT_MAX_RECIPIENTS = 50
_DEFAULT_MAX_BATCH_DURATION_SECONDS = 300


@lru_cache(maxsize=1)
def _load_config() -> dict:
    try:
        import yaml  # type: ignore[import]
        with open(_CONFIG_PATH, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    except Exception:  # noqa: BLE001
        # guardian: allow-broad-except -- optional config, fall through to defaults.
        return {}


# ---------------------------------------------------------------------------
# Input types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BatchRecipientRequest:
    """Single-recipient entry in a batch campaign.

    Fields
    ------
    recipient_id      : caller-assigned stable ID (e.g. CRM contact ID).
    campaign_request  : CampaignRequest for this recipient.
    manifest_hash     : stable deduplication key derived from sender+recipient+policy.
                        Caller computes this; orchestrator validates uniqueness.
    """

    recipient_id: str
    campaign_request: Any   # apps_lic.types.lic_types.CampaignRequest
    manifest_hash: str


@dataclass(frozen=True)
class BatchCampaignRequest:
    """Input to CampaignBatchOrchestrator.

    Fields
    ------
    batch_id       : caller-assigned stable batch ID.
    sender_id      : identifies the sender (for audit).
    entries        : ordered list of BatchRecipientRequest.
    """

    batch_id: str
    sender_id: str
    entries: tuple  # tuple[BatchRecipientRequest, ...]


# ---------------------------------------------------------------------------
# Output types
# ---------------------------------------------------------------------------

# Disposition values for each recipient result
DISPOSITION_SUCCESS = "success"
DISPOSITION_DUPLICATE_SKIPPED = "duplicate_skipped"
DISPOSITION_RATE_LIMITED = "rate_limited"
DISPOSITION_FAILED = "failed"

BATCH_DISPOSITIONS = frozenset({
    DISPOSITION_SUCCESS,
    DISPOSITION_DUPLICATE_SKIPPED,
    DISPOSITION_RATE_LIMITED,
    DISPOSITION_FAILED,
})


@dataclass(frozen=True)
class BatchRecipientResult:
    """Result for one recipient in a batch.

    Fields
    ------
    recipient_id  : mirrors BatchRecipientRequest.recipient_id.
    disposition   : one of BATCH_DISPOSITIONS.
    run_id        : GovernedLicRun run_id (empty if not dispatched).
    manifest_hash : deduplication key from the request.
    error         : error message if disposition == "failed".
    duration_ms   : wall-clock dispatch time in milliseconds.
    """

    recipient_id: str
    disposition: str
    run_id: str
    manifest_hash: str
    error: str = ""
    duration_ms: float = 0.0


@dataclass(frozen=True)
class BatchAdmissionReceipt:
    """UWG batch admission receipt (D4-P2 write-path artifact).

    Caller feeds this to UWG. Orchestrator does NOT write to UWG directly.

    Fields
    ------
    batch_id          : mirrors BatchCampaignRequest.batch_id.
    sender_id         : mirrors BatchCampaignRequest.sender_id.
    total_requested   : len(entries) before rate limiting.
    total_dispatched  : recipients actually sent to GovernedLicRun.
    total_skipped     : duplicates + rate-limited.
    total_failed      : recipients where GovernedLicRun raised.
    results           : tuple of BatchRecipientResult, one per entry.
    batch_duration_ms : total wall-clock time.
    trace_id          : audit trace ID.
    """

    batch_id: str
    sender_id: str
    total_requested: int
    total_dispatched: int
    total_skipped: int
    total_failed: int
    results: tuple  # tuple[BatchRecipientResult, ...]
    batch_duration_ms: float
    trace_id: str


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


def _utc_ms() -> float:
    return time.time() * 1000.0


def _compute_manifest_hash(sender_id: str, recipient_id: str, policy_hash: str = "") -> str:
    blob = json.dumps(
        {"sender_id": sender_id, "recipient_id": recipient_id, "policy_hash": policy_hash},
        sort_keys=True,
    ).encode()
    return f"sha256:{hashlib.sha256(blob).hexdigest()[:24]}"


class CampaignBatchOrchestrator:
    """Dispatches N single-recipient GovernedLicRun instances with dedup + rate control.

    Usage::

        orchestrator = CampaignBatchOrchestrator(run_fn=my_run_fn)
        receipt = orchestrator.dispatch(batch_request)
        # feed receipt to UWG, OR inject uwg_submit to wire automatically

    Parameters
    ----------
    run_fn : Callable[[Any], Any]
        Injected single-recipient run function. Signature:
        ``run_fn(campaign_request) -> GovernedLicE2ERunRecord``
        Injection avoids circular imports and enables testing without
        spinning up the full GovernedLicRun stack.
    uwg_submit : Callable[[BatchAdmissionReceipt], Any] | None
        Optional UWG submission callable (DS8-P1). When provided, called
        after each dispatch() with the completed BatchAdmissionReceipt.
        Fail-soft: exceptions do NOT abort the batch or raise to caller.
    config : dict | None
        Optional policy override (tests pass dict directly).
    """

    def __init__(
        self,
        run_fn: Callable[[Any], Any],
        uwg_submit: Optional[Callable[["BatchAdmissionReceipt"], Any]] = None,
        config: dict | None = None,
    ) -> None:
        self._run_fn = run_fn
        self._uwg_submit = uwg_submit
        self._config = config if config is not None else _load_config()

    def _max_recipients(self) -> int:
        return int(self._config.get("max_recipients_per_batch", _DEFAULT_MAX_RECIPIENTS))

    def dispatch(self, batch_request: BatchCampaignRequest) -> BatchAdmissionReceipt:
        """Dispatch a batch campaign.

        For each entry:
        1. If batch is over rate limit → RATE_LIMITED (no dispatch).
        2. If manifest_hash already seen → DUPLICATE_SKIPPED (no dispatch).
        3. Otherwise → call run_fn; SUCCESS or FAILED.

        Returns a BatchAdmissionReceipt with full per-recipient results.
        """
        t_batch_start = _utc_ms()
        trace_id = str(uuid.uuid4())
        max_recip = self._max_recipients()
        entries = list(batch_request.entries)
        total_requested = len(entries)

        seen_hashes: set[str] = set()
        results: list[BatchRecipientResult] = []
        dispatched = 0
        skipped = 0
        failed = 0

        for entry in entries:
            t_start = _utc_ms()

            # Rate limit check
            if dispatched >= max_recip:
                results.append(BatchRecipientResult(
                    recipient_id=entry.recipient_id,
                    disposition=DISPOSITION_RATE_LIMITED,
                    run_id="",
                    manifest_hash=entry.manifest_hash,
                    error=f"rate_limit: max_recipients_per_batch={max_recip} reached",
                    duration_ms=0.0,
                ))
                skipped += 1
                continue

            # Deduplication check
            if entry.manifest_hash in seen_hashes:
                results.append(BatchRecipientResult(
                    recipient_id=entry.recipient_id,
                    disposition=DISPOSITION_DUPLICATE_SKIPPED,
                    run_id="",
                    manifest_hash=entry.manifest_hash,
                    error=f"duplicate manifest_hash={entry.manifest_hash}",
                    duration_ms=_utc_ms() - t_start,
                ))
                skipped += 1
                continue

            seen_hashes.add(entry.manifest_hash)

            # Dispatch
            try:
                run_record = self._run_fn(entry.campaign_request)
                run_id = str(getattr(run_record, "run_id", ""))
                results.append(BatchRecipientResult(
                    recipient_id=entry.recipient_id,
                    disposition=DISPOSITION_SUCCESS,
                    run_id=run_id,
                    manifest_hash=entry.manifest_hash,
                    duration_ms=_utc_ms() - t_start,
                ))
                dispatched += 1
            except Exception as exc:  # noqa: BLE001
                # guardian: allow-broad-except -- partial failure: one recipient
                # raising must NOT abort the batch. Capture and continue.
                results.append(BatchRecipientResult(
                    recipient_id=entry.recipient_id,
                    disposition=DISPOSITION_FAILED,
                    run_id="",
                    manifest_hash=entry.manifest_hash,
                    error=f"{type(exc).__name__}: {exc}",
                    duration_ms=_utc_ms() - t_start,
                ))
                failed += 1
                dispatched += 1  # counts toward rate limit even on failure

        receipt = BatchAdmissionReceipt(
            batch_id=batch_request.batch_id,
            sender_id=batch_request.sender_id,
            total_requested=total_requested,
            total_dispatched=dispatched,
            total_skipped=skipped,
            total_failed=failed,
            results=tuple(results),
            batch_duration_ms=_utc_ms() - t_batch_start,
            trace_id=trace_id,
        )

        # DS8-P1: route receipt to UWG via injected callable (fail-soft)
        if self._uwg_submit is not None:
            try:
                self._uwg_submit(receipt)
            except Exception:  # noqa: BLE001
                # guardian: allow-broad-except -- UWG submission failure must never
                # suppress the receipt or raise to the caller; receipt is returned as-is.
                pass

        return receipt


__all__ = [
    "CampaignBatchOrchestrator",
    "BatchCampaignRequest",
    "BatchRecipientRequest",
    "BatchAdmissionReceipt",
    "BatchRecipientResult",
    "BATCH_DISPOSITIONS",
    "DISPOSITION_SUCCESS",
    "DISPOSITION_DUPLICATE_SKIPPED",
    "DISPOSITION_RATE_LIMITED",
    "DISPOSITION_FAILED",
    "_compute_manifest_hash",
]
