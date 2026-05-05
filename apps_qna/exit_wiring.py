"""Exit Wiring — wires L2 output to Exit v6, emits exactly one X3.

W0 thin-slice: minimal exit that produces an ExitReviewPacket with
a single X3 disposition. Full implementation lands in W4.2 with
FEC producer integration and X1/X2/X3 pipeline.

Plan: .windsurf/plans/apps-qna-spine-integration-e9c5b3.md W0.4
"""

from __future__ import annotations

from typing import Any

from apps_qna.types.spine_contracts import (
    CardPackManifestExtended,
    ExitReviewPacket,
    X3Disposition,
)


def emit_exit_review(
    *,
    manifest: CardPackManifestExtended,
    evidence_contract: dict[str, Any],
    build_valid: bool = True,
) -> ExitReviewPacket:
    """Emit exactly one X3 disposition for the completed build.

    Args:
        manifest: The sealed card pack manifest.
        evidence_contract: The evidence contract used.
        build_valid: Whether the build passed validation.

    Returns:
        An ExitReviewPacket with exactly one X3 disposition.
    """
    if not build_valid:
        return ExitReviewPacket(
            x3_disposition=X3Disposition.SAFE_ABSTAIN,
            final_evidence_contract=evidence_contract,
            manifest=manifest,
            reason_codes=("build_validation_failed",),
        )

    if not manifest.cards:
        return ExitReviewPacket(
            x3_disposition=X3Disposition.SAFE_ABSTAIN,
            final_evidence_contract=evidence_contract,
            manifest=manifest,
            reason_codes=("no_cards_rendered",),
        )

    evidence_sufficiency = evidence_contract.get("evidence_sufficiency", "empty")
    if evidence_sufficiency == "empty":
        return ExitReviewPacket(
            x3_disposition=X3Disposition.SAFE_ABSTAIN,
            final_evidence_contract=evidence_contract,
            manifest=manifest,
            reason_codes=("empty_evidence",),
        )

    return ExitReviewPacket(
        x3_disposition=X3Disposition.ALLOW_FINISH,
        final_evidence_contract=evidence_contract,
        manifest=manifest,
        reason_codes=(),
    )


__all__ = ["emit_exit_review"]
