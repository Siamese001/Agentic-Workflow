"""
P3.4 — apps_repo_brief C0 Normalization Adapter.

This adapter:
1. Accepts a normalized_repo_brief_task from U0/L1.
2. Builds the C0 retrieval plan (7 lanes) with depth-profile thresholds.
3. Declares the retrieval surface (repo_brief_docs).
4. Returns a C0RequestSpec for the core C0 Context Engine.

What this adapter does NOT do:
- Does NOT perform retrieval (C0 does that).
- Does NOT extract claims (C0 BM25/code-symbol/graph lanes do that).
- Does NOT build prompt slots (PA does that).
- Does NOT mint FinalEvidenceContract (C0 does that).

The CapabilityExtractionEngine from apps_exec has been REPLACED by the
C0 code-symbol + graph retrieval lanes. The logic for finding structured
capabilities from source docs is now a C0 retrieval function, not an
app-level engine. See plan §P3.4.

Plan: .windsurf/plans/apps-repo-brief-plan3-zero-loss-overwrite.md §P3.4, §7
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from apps_repo_brief.c0.repo_brief_final_contract import DepthProfile
from apps_repo_brief.c0.depth_profiles import DEPTH_PROFILE_THRESHOLDS


# C0 retrieval lanes used by apps_repo_brief (7 lanes per plan §7.2)
C0_RETRIEVAL_LANES = [
    "bm25_exact_phrase",    # policy names, route IDs, file paths, class names, hash fields
    "dense_semantic",       # concept discovery, exec narrative, governance language
    "metadata",             # source_type, audience, recency, policy/blueprint hash
    "graph",                # docs↔code↔tests↔proof linkage
    "code_symbol",          # implementation-backed claims, entrypoint validation
    "proof",                # tests, cert receipts, replay proof, OTEL spans
    "prior_artifact",       # prior briefs, claim maps (hints only unless snapshot-perfect)
]


@dataclass
class C0RequestSpec:
    """Normalized request spec that apps_repo_brief passes to C0."""
    retrieval_surface_id: str
    depth_profile: DepthProfile
    audience: str
    persona_schema_version: str
    emphasis_areas: list[str]
    retrieval_lanes: list[str]
    depth_thresholds: dict[str, Any]
    policy_hash: str
    blueprint_hash: str
    repo_snapshot_id: str
    replay_key: str
    trace_id: str
    normalized_request_hash: str


class RepoBriefC0Adapter:
    """
    Normalization adapter: apps_repo_brief task → C0 retrieval spec.

    Claim extraction (formerly CapabilityExtractionEngine) is now expressed
    as C0 retrieval lane configuration, not app-level logic.
    """

    def build_c0_request(
        self,
        normalized_task: dict[str, Any],
    ) -> C0RequestSpec:
        """
        Build the C0RequestSpec from a normalized_repo_brief_task.

        Args:
            normalized_task: dict produced by U0/L1 normalization adapter.
                Expected keys: depth_profile, audience, emphasis_areas,
                persona_schema_version, policy_hash, blueprint_hash,
                repo_snapshot_id, replay_key, trace_id,
                normalized_request_hash.

        Returns:
            C0RequestSpec ready for the core C0 Context Engine.
        """
        depth_profile_raw = normalized_task.get("depth_profile", "REPO_BRIEF_STANDARD")
        try:
            depth_profile = DepthProfile(depth_profile_raw)
        except ValueError:
            depth_profile = DepthProfile.REPO_BRIEF_STANDARD

        thresholds = DEPTH_PROFILE_THRESHOLDS.get(
            depth_profile, DEPTH_PROFILE_THRESHOLDS[DepthProfile.REPO_BRIEF_STANDARD]
        )

        return C0RequestSpec(
            retrieval_surface_id="repo_brief_docs",
            depth_profile=depth_profile,
            audience=normalized_task.get("audience", ""),
            persona_schema_version=normalized_task.get("persona_schema_version", ""),
            emphasis_areas=normalized_task.get("emphasis_areas", []),
            retrieval_lanes=list(C0_RETRIEVAL_LANES),
            depth_thresholds=thresholds,
            policy_hash=normalized_task.get("policy_hash", ""),
            blueprint_hash=normalized_task.get("blueprint_hash", ""),
            repo_snapshot_id=normalized_task.get("repo_snapshot_id", ""),
            replay_key=normalized_task.get("replay_key", ""),
            trace_id=normalized_task.get("trace_id", ""),
            normalized_request_hash=normalized_task.get("normalized_request_hash", ""),
        )

    def validate_fec(
        self,
        fec: Any,
        depth_profile: DepthProfile,
    ) -> list[str]:
        """
        Validate a FinalEvidenceContract against depth-profile thresholds.

        Returns list of violation strings (empty = valid).
        """
        from apps_repo_brief.c0.repo_brief_final_contract import (
            RepoBriefFinalEvidenceContract,
            EvidenceStatus,
        )
        violations: list[str] = []
        if not isinstance(fec, RepoBriefFinalEvidenceContract):
            violations.append("fec is not RepoBriefFinalEvidenceContract")
            return violations

        if not fec.authoritative:
            violations.append("FEC.authoritative must be True — only C0 mints the FEC")

        thresholds = DEPTH_PROFILE_THRESHOLDS.get(depth_profile, {})

        sp = fec.source_portfolio
        if sp is not None:
            min_sources = thresholds.get("min_sources", 0)
            if sp.total_sources < min_sources:
                violations.append(
                    f"source_portfolio.total_sources={sp.total_sources} < {min_sources} "
                    f"required for {depth_profile.value}"
                )

        bcm = fec.briefing_coverage_matrix
        if bcm is not None:
            min_coverage = thresholds.get("min_coverage_pct", 0.0)
            if bcm.overall_coverage_pct < min_coverage:
                violations.append(
                    f"coverage_pct={bcm.overall_coverage_pct:.1f}% < {min_coverage}% "
                    f"required for {depth_profile.value}"
                )

        stale_policy = thresholds.get("stale_source_policy", "caveat")
        if stale_policy == "block" and fec.freshness_report:
            if fec.freshness_report.stale_sources:
                violations.append(
                    f"{depth_profile.value} requires stale_source_policy=block "
                    f"but {len(fec.freshness_report.stale_sources)} stale sources present"
                )

        if depth_profile == DepthProfile.REPO_BRIEF_BOARD_DOSSIER:
            if not fec.board_gate_passed:
                violations.append(
                    "BOARD_DOSSIER depth profile requires board_gate_passed=True"
                )

        return violations
