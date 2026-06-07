"""apps_lic Repo Proof Linker (SE-P1c).

Evaluates whether verifiable proof is required, optional, or not applicable
for an outreach draft, scoped by recipient_class, channel, and technical
claim depth.

Contract
--------
- Decision-only: no provider calls, no state writes, no subprocess.
- NOT universally mandatory — requirement depends on recipient_class +
  technical claim depth + channel.
- Never forces proof into short messages where it would hurt channel fit
  (e.g. short LinkedIn messages).
- Proof formats: GitHub link, LinkedIn project link, resume metric,
  public artifact, briefing/deck reference.
- Returns ProofRequirement with verdict and rationale.

Proof requirement matrix (plan SE-P1c):
  REQUIRED:  EXEC/C_LEVEL/CTO/VP_ENG/HIRING_MANAGER
             + technical_claim_depth in ("high", "medium_high")
             + channel allows proof (email > linkedin short)
  OPTIONAL:  RECRUITER/SENIOR_TA
             unless strong technical claim depth present
  NOT_APPLICABLE: no technical claims in draft,
                  or short LinkedIn message (≤60 words)
                  where appending proof would breach channel fit

Plan: docs/archive/windsurf/legacy-tree/plans/apps-lic-canonical-spine-wireup-e7c2a5.md SE-P1c
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet, Optional, Tuple

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

EXEC_CLASSES:    FrozenSet[str] = frozenset({"EXECUTIVE", "C_LEVEL", "CTO", "VP_ENG"})
SENIOR_CLASSES:  FrozenSet[str] = frozenset({"HIRING_MANAGER"})
RECRUITER_CLASSES: FrozenSet[str] = frozenset({"RECRUITER", "SENIOR_TA"})

TECH_DEPTH_REQUIRING_PROOF: FrozenSet[str] = frozenset({"high", "medium_high"})
TECH_DEPTH_OPTIONAL_PROOF:  FrozenSet[str] = frozenset({"medium", "medium_low"})

PROOF_FORMATS: Tuple[str, ...] = (
    "github_link",
    "linkedin_project_link",
    "resume_metric",
    "public_artifact",
    "briefing_deck_reference",
)

# LinkedIn word-count threshold: at or below this, proof is not applicable
# (appending a URL would damage channel fit)
LINKEDIN_SHORT_THRESHOLD = 60


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------

VERDICT_REQUIRED        = "required"
VERDICT_OPTIONAL        = "optional"
VERDICT_NOT_APPLICABLE  = "not_applicable"


# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ProofRequirement:
    """Result of evaluating proof appropriateness for a draft context.

    verdict: "required" | "optional" | "not_applicable"
    proof_formats_allowed: tuple of format IDs that are acceptable for this context.
    is_fail_closed: True when verdict="required" AND no proof provided.
    rationale: human-readable explanation.
    evidence_ref: machine-readable evidence string.
    """

    verdict: str
    proof_formats_allowed: Tuple[str, ...]
    is_fail_closed: bool
    rationale: str
    evidence_ref: str


# ---------------------------------------------------------------------------
# Evaluator
# ---------------------------------------------------------------------------

class RepoProofLinker:
    """Evaluate proof appropriateness for an outreach draft.

    Usage::

        linker = RepoProofLinker()
        req = linker.evaluate(
            recipient_class="CTO",
            channel="email",
            technical_claim_depth="high",
            draft_word_count=120,
            proof_provided=False,
        )
        if req.is_fail_closed:
            # must supply proof before dispatch
            ...

    ``proof_provided=True`` suppresses is_fail_closed regardless of verdict.
    """

    def evaluate(
        self,
        *,
        recipient_class: str,
        channel: str,
        technical_claim_depth: str,
        draft_word_count: int,
        proof_provided: bool = False,
    ) -> ProofRequirement:
        """Evaluate proof requirement.

        Args:
            recipient_class: target recipient class.
            channel: "email"|"linkedin"|"text"
            technical_claim_depth: "high"|"medium_high"|"medium"|"medium_low"|"low"|"none"
            draft_word_count: current word count (used for channel-fit check).
            proof_provided: True if caller already supplies proof in draft.

        Returns:
            ProofRequirement.
        """
        verdict, rationale = self._resolve_verdict(
            recipient_class=recipient_class,
            channel=channel,
            technical_claim_depth=technical_claim_depth,
            draft_word_count=draft_word_count,
        )

        # Restrict proof formats for short channels
        allowed_formats = self._allowed_formats(channel, draft_word_count)

        is_fail_closed = (
            verdict == VERDICT_REQUIRED
            and not proof_provided
        )

        evidence_ref = (
            f"recipient_class={recipient_class} channel={channel} "
            f"technical_claim_depth={technical_claim_depth} "
            f"draft_word_count={draft_word_count} "
            f"proof_provided={proof_provided} "
            f"verdict={verdict} "
            f"is_fail_closed={is_fail_closed}"
        )

        return ProofRequirement(
            verdict=verdict,
            proof_formats_allowed=allowed_formats,
            is_fail_closed=is_fail_closed,
            rationale=rationale,
            evidence_ref=evidence_ref,
        )

    # ------------------------------------------------------------------
    # Verdict resolution
    # ------------------------------------------------------------------

    def _resolve_verdict(
        self,
        *,
        recipient_class: str,
        channel: str,
        technical_claim_depth: str,
        draft_word_count: int,
    ) -> Tuple[str, str]:
        """Return (verdict, rationale)."""

        # Not applicable: no technical claims
        if technical_claim_depth in ("none", "low"):
            return (
                VERDICT_NOT_APPLICABLE,
                f"technical_claim_depth={technical_claim_depth!r} — no proof needed without technical claims",
            )

        # Not applicable: short LinkedIn message (appending proof hurts channel fit)
        if channel == "linkedin" and draft_word_count <= LINKEDIN_SHORT_THRESHOLD:
            return (
                VERDICT_NOT_APPLICABLE,
                f"Short LinkedIn message ({draft_word_count} words ≤ {LINKEDIN_SHORT_THRESHOLD}) — "
                "appending proof URLs would exceed channel length ceiling; not applicable",
            )

        # Not applicable: text channel (too short for any proof format)
        if channel == "text":
            return (
                VERDICT_NOT_APPLICABLE,
                "Text channel too short to include proof; not applicable",
            )

        # Exec/senior + high tech depth → required
        if recipient_class in (EXEC_CLASSES | SENIOR_CLASSES):
            if technical_claim_depth in TECH_DEPTH_REQUIRING_PROOF:
                return (
                    VERDICT_REQUIRED,
                    f"{recipient_class} + technical_claim_depth={technical_claim_depth!r} "
                    "→ verifiable proof required",
                )
            # medium depth for exec/senior → optional
            return (
                VERDICT_OPTIONAL,
                f"{recipient_class} + technical_claim_depth={technical_claim_depth!r} "
                "→ proof optional but recommended",
            )

        # Recruiter classes
        if recipient_class in RECRUITER_CLASSES:
            # Only required when very strong technical claim
            if technical_claim_depth == "high":
                return (
                    VERDICT_OPTIONAL,
                    f"RECRUITER/SENIOR_TA with high technical claim depth — proof optional "
                    "(strong technical claim present but recruiters are not the primary evaluator)",
                )
            return (
                VERDICT_NOT_APPLICABLE,
                f"RECRUITER/SENIOR_TA + technical_claim_depth={technical_claim_depth!r} "
                "→ proof not required for recruiter outreach",
            )

        # REFERRAL and others → optional when tech depth medium+
        if technical_claim_depth in TECH_DEPTH_REQUIRING_PROOF:
            return (
                VERDICT_OPTIONAL,
                f"{recipient_class} + technical_claim_depth={technical_claim_depth!r} "
                "→ proof optional for this recipient class",
            )

        return (
            VERDICT_NOT_APPLICABLE,
            f"{recipient_class} + technical_claim_depth={technical_claim_depth!r} "
            "→ proof not applicable",
        )

    def _allowed_formats(self, channel: str, draft_word_count: int) -> Tuple[str, ...]:
        """Allowed proof formats given channel and word-count context."""
        if channel == "linkedin":
            # LinkedIn: avoid full GitHub URLs; prefer short resume metrics
            # and briefing references that don't waste character budget
            return ("resume_metric", "linkedin_project_link", "briefing_deck_reference")
        if channel == "text":
            return ()
        # Email: all formats allowed
        return PROOF_FORMATS
