"""L2 binding — adapts AppIngressRunner prompt_artifact to apps_qna L2 execution.

AppIngressRunner calls: sealed = l2(prompt_artifact)

The prompt_artifact is a QnaPromptArtifact produced by qna_pa. This binding
orchestrates the three apps_qna L2 sub-stages:
    E1: prep_workspace
    E2: validate_build_inputs
    E3: execute_build  (the card pack build)

On the canonical spine path, AppIngressRunner calls this binding after qna_pa;
it is the only current-run authority for E1/E2/E3 (no parallel orchestrator).

Consumes: QnaPromptArtifact from qna_pa
Emits:    SealedQnaArtifact — wrapper around CardPackManifestExtended that
          carries the build result for qna_exit.

Plan: docs/archive/windsurf/legacy-tree/plans/one-spine-qna-rfp-migration-d2e8f1.md W1.P1
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class SealedQnaArtifact:
    """Sealed card-pack artifact produced by qna_l2.

    Carries the CardPackManifestExtended and the validation state for
    qna_exit to produce the final X3 disposition.
    """

    manifest: Any  # CardPackManifestExtended
    evidence_contract: dict[str, Any]
    build_valid: bool
    interview_slug: str
    route_id: str
    validation_errors: tuple[str, ...] = ()


def qna_l2(prompt_artifact: Any) -> SealedQnaArtifact:
    """L2 stage binding for apps_qna.

    Runs the three L2 sub-stages (E1 prep, E2 validate, E3 execute) and
    returns a SealedQnaArtifact for the exit binding.

    Args:
        prompt_artifact: QnaPromptArtifact from qna_pa.

    Returns:
        SealedQnaArtifact with the built CardPackManifestExtended.

    Raises:
        RuntimeError: If E2 validation fails (fail-closed).
    """
    from apps_qna.l2.e1_prep import prep_workspace
    from apps_qna.l2.e2_valid import validate_build_inputs
    from apps_qna.l2.e3_exec import execute_build

    interview_slug: str = getattr(prompt_artifact, "interview_slug", "") or ""
    route_id: str = getattr(prompt_artifact, "route_id", "") or ""
    evidence_contract: dict[str, Any] = getattr(prompt_artifact, "evidence_contract", {}) or {}

    _LOGGER.debug("qna_l2: slug=%s route_id=%s", interview_slug, route_id)

    # E1: Prepare workspace
    workspace = prep_workspace(
        interview_slug=interview_slug,
        route_id=route_id,
    )

    # E2: Validate build inputs
    validation = validate_build_inputs(workspace, evidence_contract=evidence_contract)
    if not validation["valid"]:
        errors = tuple(validation.get("errors", ()))
        _LOGGER.warning("qna_l2: E2 validation failed slug=%s errors=%s", interview_slug, errors)
        return SealedQnaArtifact(
            manifest=None,
            evidence_contract=evidence_contract,
            build_valid=False,
            interview_slug=interview_slug,
            route_id=route_id,
            validation_errors=errors,
        )

    # E3: Execute build
    manifest = execute_build(workspace, evidence_contract=evidence_contract)

    return SealedQnaArtifact(
        manifest=manifest,
        evidence_contract=evidence_contract,
        build_valid=True,
        interview_slug=interview_slug,
        route_id=route_id,
    )


__all__ = ["SealedQnaArtifact", "qna_l2"]
