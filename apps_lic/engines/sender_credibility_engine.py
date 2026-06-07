"""apps_lic Sender Credibility Engine (SE-P1b).

Builds a ``SenderCredibilityCard`` from hash-bound claims sourced
exclusively from ``master_resume.json``.

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
        """Extract CredibilityClaim objects from master_resume.json."""
        claims: List[CredibilityClaim] = []

        # Extract from professional_experience bullet_pools
        for exp in self._resume.get("professional_experience", []):
            for bullet in exp.get("bullet_pool", []):
                label = bullet.get("label", "")
                text = bullet.get("text", "")
                tags = frozenset(bullet.get("tags", []))
                if not text:
                    continue
                source_ref = _sha256_of(text)
                claims.append(CredibilityClaim(
                    label=label,
                    text=text,
                    source_ref=source_ref,
                    tags=tags,
                ))

        # Extract from executive_summary as a single claim
        summary = self._resume.get("executive_summary", "")
        if summary:
            claims.append(CredibilityClaim(
                label="Executive Summary",
                text=summary[:200] + "..." if len(summary) > 200 else summary,
                source_ref=_sha256_of(summary),
                tags=frozenset({"leadership", "agentic-platform", "governance"}),
            ))

        # Extract from certifications if present
        for cert in self._resume.get("certifications", []):
            text = cert if isinstance(cert, str) else cert.get("name", "")
            if text:
                claims.append(CredibilityClaim(
                    label="Certification",
                    text=text,
                    source_ref=_sha256_of(text),
                    tags=frozenset({"credentials"}),
                ))

        return claims
