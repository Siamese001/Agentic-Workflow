"""apps_qna runtime stage bindings — W1 one-spine migration.

Each module in this package contains exactly one stage binding function that
adapts the AppIngressRunner orchestrator's positional contract to the existing
apps_qna stage functions.

Binding signatures (dictated by AppIngressRunner._run_profile_stages):
    u0(envelope)                          -> ValidatedRequest
    l1(validated)                         -> L1PlanContract-like (with .grounding_required)
    l0(l1_plan)                           -> RouteSelection-like (with .grounding_required,
                                             .model_generation_required)
    c0(route, validated)                  -> FinalEvidenceContract-like dict
    pa(route, l1_plan, fec, validated)    -> prompt_artifact (with truthy value signals L2)
    l2(prompt_artifact)                   -> sealed (SealedQnaArtifact)
    exit(sealed, target_company, target_role, output_directory, writeback_policy)
                                          -> result with .disposition

Plan: .windsurf/plans/one-spine-qna-rfp-migration-d2e8f1.md W1
"""
from __future__ import annotations

from apps_qna.runtime.bindings.u0_binding import qna_u0
from apps_qna.runtime.bindings.l1_binding import qna_l1
from apps_qna.runtime.bindings.l0_binding import qna_l0
from apps_qna.runtime.bindings.c0_binding import qna_c0
from apps_qna.runtime.bindings.pa_binding import qna_pa
from apps_qna.runtime.bindings.l2_binding import qna_l2
from apps_qna.runtime.bindings.exit_binding import qna_exit

__all__ = [
    "qna_u0",
    "qna_l1",
    "qna_l0",
    "qna_c0",
    "qna_pa",
    "qna_l2",
    "qna_exit",
]
