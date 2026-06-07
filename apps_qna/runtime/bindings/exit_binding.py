"""Exit binding — adapts AppIngressRunner sealed artifact to apps_qna exit stage.

AppIngressRunner calls:
    result = exit(sealed, target_company, target_role, output_directory, writeback_policy)
Then reads: result.disposition

Consumes: SealedQnaArtifact from qna_l2
Emits:    QnaExitResult — wrapper with .disposition (an X3Disposition enum value
          from apps_qna.types.spine_contracts, NOT the core X3Disposition dataclass)

The apps_qna exit stage uses apps_qna.exit_wiring.emit_exit_review which
returns an ExitReviewPacket with .x3_disposition (enum). AppIngressRunner
reads result.disposition and returns it to the caller.

After W1, this is the ONLY place that calls emit_exit_review on the spine path.

Plan: docs/archive/windsurf/legacy-tree/plans/one-spine-qna-rfp-migration-d2e8f1.md W1.P1
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class QnaExitResult:
    """Wrapper over ExitReviewPacket that exposes .disposition for AppIngressRunner."""

    exit_packet: Any  # ExitReviewPacket
    disposition: Any  # apps_qna X3Disposition enum value


def qna_exit(
    sealed: Any,
    target_company: str,
    target_role: str,
    output_directory: Any,
    writeback_policy: Any,
) -> QnaExitResult:
    """Exit stage binding for apps_qna.

    Calls apps_qna.exit_wiring.emit_exit_review() with the sealed artifact
    and returns a QnaExitResult whose .disposition is the X3Disposition enum.

    Args:
        sealed: SealedQnaArtifact from qna_l2.
        target_company: Passed by AppIngressRunner; not used by apps_qna exit.
        target_role: Passed by AppIngressRunner; not used by apps_qna exit.
        output_directory: Passed by AppIngressRunner; not used by apps_qna exit.
        writeback_policy: Passed by AppIngressRunner; not used by apps_qna exit.

    Returns:
        QnaExitResult with .disposition set to X3Disposition enum value.
    """
    from apps_qna.exit_wiring import emit_exit_review

    manifest = getattr(sealed, "manifest", None)
    evidence_contract: dict[str, Any] = getattr(sealed, "evidence_contract", {}) or {}
    build_valid: bool = getattr(sealed, "build_valid", False)
    interview_slug: str = getattr(sealed, "interview_slug", "") or ""

    _LOGGER.debug(
        "qna_exit: slug=%s build_valid=%s manifest_cards=%s",
        interview_slug,
        build_valid,
        len(getattr(manifest, "cards", ())) if manifest else 0,
    )

    if manifest is None:
        # L2 validation failed — emit a minimal abstain manifest
        from apps_qna.types.spine_contracts import CardPackManifestExtended
        manifest = CardPackManifestExtended(
            interview_slug=interview_slug,
            built_at="",
            builder_version="0.1.0",
            template_set_version="v2",
            cards=(),
            routes_covered=(),
            interviewers=(),
            pasted_cards=(),
            paste_exceeds_chatgpt_limit=False,
            evidence_refs=(),
            tiering={},
            card_hashes={},
            source_register=(),
        )

    exit_packet = emit_exit_review(
        manifest=manifest,
        evidence_contract=evidence_contract,
        build_valid=build_valid,
    )

    return QnaExitResult(
        exit_packet=exit_packet,
        disposition=exit_packet.x3_disposition,
    )


__all__ = ["QnaExitResult", "qna_exit"]
