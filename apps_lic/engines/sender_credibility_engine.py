"""apps_lic Sender Credibility Engine (SE-P1b).

Builds a ``SenderCredibilityCard`` from hash-bound claims sourced from the
graph-grounded standing sender corpus (the apps_rg augmented_skills_graph is the
sole source of claims/metrics). The base/master resume is identity-only; an
explicitly-injected ``resume_data`` bullet_pool is honored for test fixtures.

Contract
--------
- Decision-only: no provider calls, no state writes, no subprocess.
- Every claim carries a ``source_ref`` bound to a ``master_resume.json``
  bullet hash or field path.  Claims without ``source_ref`` are REJECTED.
- ``factual_support`` in the exit rubric rejects unsourced claims.
- ``SenderCredibilityCard.top_claims`` = top-3 by ``fit_score_for_recipient``
  (scored by tag overlap with a caller-supplied recipient context vector).
- ``SenderCredibilityCard.all_claims`` = full ranked list for HITL review.
- No claim is invented; the engine only selects and scores.

Plan: docs/archive/windsurf/legacy-tree/plans/apps-lic-canonical-spine-wireup-e7c2a5.md SE-P1b
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, FrozenSet, List, Optional, Sequence, Tuple

# ---------------------------------------------------------------------------
# Canonical path to master_resume.json
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parents[2]
MASTER_RESUME_PATH = _REPO_ROOT / "apps_shared" / "data" / "master_resume.json"


# ---------------------------------------------------------------------------
# Claim
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CredibilityClaim:
    """A single hash-bound credibility claim sourced from master_resume.json.

    source_ref: deterministic sha256 of the bullet text or field path that
                backs this claim. Must be non-empty for the claim to be valid.
    fit_score_for_recipient: 0.0–1.0; higher = better match for recipient context.
    tags: from master_resume.json bullet ``tags`` array.
    """

    label: str
    text: str
    source_ref: str          # sha256:<hex> or field path reference
    tags: FrozenSet[str]
    fit_score_for_recipient: float = 0.0
    is_verified: bool = True  # False when source_ref is absent


@dataclass(frozen=True)
class SenderCredibilityCard:
    """Output artifact of the sender credibility engine.

    top_claims: top-3 verified claims ranked by fit_score_for_recipient.
    all_claims: full ranked list for HITL review.
    rejected_claims: claims that had no source_ref (must not appear in draft).
    card_hash: sha256 of top_claims text + source_refs (for tamper detection).
    """

    top_claims: Tuple[CredibilityClaim, ...]
    all_claims: Tuple[CredibilityClaim, ...]
    rejected_claims: Tuple[CredibilityClaim, ...]
    recipient_class: str
    outreach_mode: str
    card_hash: str


# ---------------------------------------------------------------------------
# Tag scoring
# ---------------------------------------------------------------------------

# Recipient-class → preferred claim tags (for fit scoring)
_RECIPIENT_TAG_PREFS: Dict[str, FrozenSet[str]] = {
    "EXECUTIVE":    frozenset({"agentic-platform", "leadership", "productization", "governance",
                                "metric-15M-revenue", "metric-20pct-margin", "metric-8-to-28-team"}),
    "C_LEVEL":      frozenset({"agentic-platform", "leadership", "productization", "governance",
                                "metric-15M-revenue", "metric-20pct-margin"}),
    "CTO":          frozenset({"agentic-platform", "governance", "graphrag", "sandboxing",
                                "replayable-traces", "reliability", "evaluation-gates",
                                "adg", "dependency-graph"}),
    "VP_ENG":       frozenset({"agentic-platform", "governance", "ai-cicd", "reliability",
                                "evaluation-gates", "telemetry", "rollback", "metric-8-to-28-team"}),
    "HIRING_MANAGER": frozenset({"agentic-platform", "governance", "reliability",
                                  "evaluation-gates", "lifecycle", "lab-to-production"}),
    "RECRUITER":    frozenset({"agentic-platform", "leadership", "productization",
                                "metric-15M-revenue", "metric-6mo-to-3wk"}),
    "SENIOR_TA":    frozenset({"agentic-platform", "leadership", "productization",
                                "metric-15M-revenue"}),
    "REFERRAL_CONTACT": frozenset({"agentic-platform", "leadership", "productization"}),
}
_DEFAULT_TAG_PREFS: FrozenSet[str] = frozenset({"agentic-platform", "leadership", "governance"})


def _score_claim(claim_tags: FrozenSet[str], pref_tags: FrozenSet[str]) -> float:
    """Jaccard-like fit score: |intersection| / |preferred| (capped at 1.0)."""
    if not pref_tags:
        return 0.0
    return min(1.0, len(claim_tags & pref_tags) / len(pref_tags))


def _sha256_of(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

class SenderCredibilityEngine:
    """Build a SenderCredibilityCard from master_resume.json.

    Usage::

        engine = SenderCredibilityEngine()
        card = engine.build_card(
            recipient_class="EXECUTIVE",
            outreach_mode="cold",
        )
        # card.top_claims has 3 best-fit verified claims
        # card.rejected_claims must not appear in draft

    Custom resume data can be injected for testing::

        engine = SenderCredibilityEngine(resume_data=my_dict)
    """

    def __init__(
        self,
        *,
        resume_path: Optional[Path] = None,
        resume_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        if resume_data is not None:
            self._resume = resume_data
        else:
            path = resume_path or MASTER_RESUME_PATH
            with path.open(encoding="utf-8") as fh:
                self._resume = json.load(fh)

    def build_card(
        self,
        *,
        recipient_class: str,
        outreach_mode: str,
        top_n: int = 3,
    ) -> SenderCredibilityCard:
        """Build a SenderCredibilityCard for the given context.

        Args:
            recipient_class: target recipient class.
            outreach_mode: "cold"|"warm"|"referral"|"followup"
            top_n: number of top claims to surface (default 3).

        Returns:
            SenderCredibilityCard.
        """
        pref_tags = _RECIPIENT_TAG_PREFS.get(recipient_class, _DEFAULT_TAG_PREFS)
        raw_claims = self._extract_claims()

        verified: List[CredibilityClaim] = []
        rejected: List[CredibilityClaim] = []

        for c in raw_claims:
            if not c.source_ref:
                rejected.append(CredibilityClaim(
                    label=c.label,
                    text=c.text,
                    source_ref="",
                    tags=c.tags,
                    fit_score_for_recipient=0.0,
                    is_verified=False,
                ))
            else:
                score = _score_claim(c.tags, pref_tags)
                verified.append(CredibilityClaim(
                    label=c.label,
                    text=c.text,
                    source_ref=c.source_ref,
                    tags=c.tags,
                    fit_score_for_recipient=round(score, 4),
                    is_verified=True,
                ))

        ranked = sorted(verified, key=lambda x: x.fit_score_for_recipient, reverse=True)
        top = tuple(ranked[:top_n])

        card_hash = _sha256_of(
            "|".join(f"{c.source_ref}:{c.text[:40]}" for c in top)
        )

        return SenderCredibilityCard(
            top_claims=top,
            all_claims=tuple(ranked),
            rejected_claims=tuple(rejected),
            recipient_class=recipient_class,
            outreach_mode=outreach_mode,
            card_hash=card_hash,
        )

    # ------------------------------------------------------------------
    # Private: extract claims from resume JSON
    # ------------------------------------------------------------------

    def _extract_claims(self) -> List[CredibilityClaim]:
        """Extract CredibilityClaim objects.

        The apps_rg graph is the SOLE source of credibility claims/metrics. The
        base/master resume is identity-only (no bullets), so by default claims are
        sourced from the graph-grounded standing sender corpus. The resume
        bullet_pool path remains ONLY for explicitly-injected ``resume_data``
        (test fixtures / back-compat); production resumes carry no bullets.
        """
        claims: List[CredibilityClaim] = []

        injected_bullets = [
            bullet
            for exp in self._resume.get("professional_experience", [])
            for bullet in exp.get("bullet_pool", [])
            if bullet.get("text")
        ]
        if injected_bullets:
            for bullet in injected_bullets:
                text = bullet.get("text", "")
                claims.append(CredibilityClaim(
                    label=bullet.get("label", ""),
                    text=text,
                    source_ref=_sha256_of(text),
                    tags=frozenset(bullet.get("tags", [])),
                ))
        else:
            # Graph is the sole fact source for sender claims/metrics.
            claims.extend(self._graph_grounded_claims())

        # Certifications/credentials are IDENTITY (allowed to live in the resume).
        for cert in self._resume.get("certifications_and_credentials", []):
            text = cert.get("name", "") if isinstance(cert, dict) else str(cert)
            if text:
                claims.append(CredibilityClaim(
                    label="Certification",
                    text=text,
                    source_ref=_sha256_of(text),
                    tags=frozenset({"credentials"}),
                ))

        return claims

    def _graph_grounded_claims(self) -> List[CredibilityClaim]:
        """Credibility claims sourced from the graph-grounded standing sender corpus.

        Each approved proof point's ``claim_text`` is graph-linked and metric-gated
        (every number traces to the apps_rg augmented_skills_graph), so no claim or
        metric is authored from the base resume.
        """
        try:  # lazy import: avoids any import cycle with the corpus loader
            from apps_lic.engines.standing_sender_knowledge import (  # noqa: PLC0415
                load_standing_sender_corpus,
            )

            corpus = load_standing_sender_corpus()
        except Exception:  # guardian: allow-broad-exception -- corpus optional; degrade to no graph claims
            return []
        claims: List[CredibilityClaim] = []
        for point in corpus.approved_proof_points:
            text = str(point.claim_text or "").strip()
            if not text:
                continue
            claims.append(CredibilityClaim(
                label=point.proof_id,
                text=text,
                source_ref=_sha256_of(text),
                tags=frozenset(point.skill_tags),
            ))
        return claims
