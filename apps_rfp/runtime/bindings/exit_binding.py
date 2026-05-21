"""Exit binding — adapts AppIngressRunner sealed artifact to apps_rfp exit stage.

AppIngressRunner calls:
    result = exit(sealed, target_company, target_role, output_directory, writeback_policy)
Then reads: result.disposition

Consumes: SealedRfpArtifact from rfp_l2
Emits:    RfpExitResult — wrapper with .disposition for AppIngressRunner

The exit binding invokes _maybe_run_exit_hook() from apps_rfp/__main__.py logic
(moved here so governed_rfp_run can no longer own it as a current-run step),
and produces an ExitDispositionReceipt-compatible result.

governed_rfp_run is POST_RUN_RECEIPT only; it does not own execution here.

Plan: .windsurf/plans/one-spine-qna-rfp-migration-d2e8f1.md W2.P1
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

_LOGGER = logging.getLogger(__name__)

_RFP_DISPOSITION_COMPLETE = "complete"
_RFP_DISPOSITION_DRY_RUN = "dry_run"
_RFP_DISPOSITION_FAILED = "failed"


@dataclass(frozen=True)
class RfpExitResult:
    """Wrapper over proposal result that exposes .disposition for AppIngressRunner.

    .disposition is one of: 'complete', 'dry_run', 'failed'.
    """

    rfp_result: Any          # RfpResult from SealedRfpArtifact
    disposition: str         # one of the three exit disposition strings
    exit_receipt: dict       # serialised receipt for post-run decoration
    error: str = ""


def rfp_exit(
    sealed: Any,
    target_company: str = "",
    target_role: str = "",
    output_directory: Any = None,
    writeback_policy: Any = None,
) -> RfpExitResult:
    """Exit stage binding for apps_rfp.

    Reads the SealedRfpArtifact and determines the final disposition.
    Invokes the FEC/cert exit hook fail-soft.
    Returns RfpExitResult whose .disposition AppIngressRunner surfaces to the caller.

    Args:
        sealed:            SealedRfpArtifact from rfp_l2.
        target_company:    Forwarded by AppIngressRunner from validated payload.
        target_role:       Forwarded by AppIngressRunner (unused for rfp).
        output_directory:  Forwarded by AppIngressRunner (unused for rfp).
        writeback_policy:  Forwarded by AppIngressRunner (unused for rfp).

    Returns:
        RfpExitResult with .disposition set to 'complete', 'dry_run', or 'failed'.
    """
    execution_ok: bool = bool(getattr(sealed, "execution_ok", False))
    dry_run: bool = bool(getattr(sealed, "dry_run", False))
    rfp_result = getattr(sealed, "rfp_result", None)
    error: str = getattr(sealed, "error", "") or ""
    request_id: str = getattr(sealed, "request_id", "") or ""
    industry: str = getattr(sealed, "industry", "") or ""

    if dry_run:
        disposition = _RFP_DISPOSITION_DRY_RUN
    elif execution_ok:
        disposition = _RFP_DISPOSITION_COMPLETE
    else:
        disposition = _RFP_DISPOSITION_FAILED

    _LOGGER.debug(
        "rfp_exit: request_id=%s disposition=%s dry_run=%s execution_ok=%s",
        request_id,
        disposition,
        dry_run,
        execution_ok,
    )

    exit_receipt: dict = {
        "request_id": request_id,
        "app_id": "apps_rfp",
        "disposition": disposition,
        "industry": industry,
        "target_company": target_company or "",
        "execution_ok": execution_ok,
        "dry_run": dry_run,
        "error": error,
        "route_contract": {"route_id": "apps_rfp.proposal_assembly_v1"},
    }

    _run_exit_cert_hook_soft(exit_receipt)

    return RfpExitResult(
        rfp_result=rfp_result,
        disposition=disposition,
        exit_receipt=exit_receipt,
        error=error,
    )


def _run_exit_cert_hook_soft(receipts: dict) -> None:
    """Invoke apps_rfp FEC/cert exit hook fail-soft.

    Mirrors the _maybe_run_exit_hook() logic from __main__.py (which remains
    for the live-cert path only). This binding owns the exit hook on the
    governed AppIngressRunner spine path.
    """
    try:
        from apps_shared.cert import maybe_invoke_exit_eval

        cert_route_entry = {
            "route_id": "apps_rfp.proposal_assembly_v1",
            "invoke_exit_eval": False,
        }
        maybe_invoke_exit_eval(receipts, cert_route_entry)
    except (ImportError, OSError, ValueError, TypeError, AttributeError, RuntimeError) as exc:  # guardian: allow-log-and-swallow -- P2 burndown: fail-soft optional boundary
        _LOGGER.debug("rfp_exit: cert hook unavailable or skipped: %s", exc)


__all__ = ["RfpExitResult", "rfp_exit"]
