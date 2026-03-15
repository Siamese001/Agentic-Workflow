"""Talent Signal Enhancer - Transform Management into Talent Attraction.

This module enhances resume bullets to emphasize talent attraction capabilities,
highlighting team pedigree and leveraging network as a strategic asset for
AI leadership roles.
"""

import logging
import re
from typing import Any

from pydantic import BaseModel, Field, validator
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

logger = logging.getLogger(__name__)


class TalentMetrics(BaseModel):
    """Metrics describing talent acquisition and management capabilities."""

    team_size: int = Field(..., ge=0, description="Size of team managed")
    pedigree_keywords: list[str] = Field(default_factory=list, description="Prestige markers in team")
    retention_rate: str | None = Field(None, description="Team retention rate")
    hiring_velocity: str | None = Field(None, description="Hiring speed metric")

    @validator("pedigree_keywords")
    def validate_pedigree(cls, v):
        """Ensure pedigree keywords are prestigious markers."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "TalentMetrics.validate_pedigree")

        prestigious_terms = {
            "phd",
            "masters",
            "ex-google",
            "ex-meta",
            "ex-amazon",
            "ex-apple",
            "ex-microsoft",
            "ex-netflix",
            "researchers",
            "contributors",
            "senior",
            "principal",
            "staff",
            "founding engineer",
            "top-tier",
            "fortune 500",
            "ivy league",
            "stanford",
            "mit",
            "cmu",
            "berkeley",
            "open-source",
            "github",
            "kaggle",
        }
        filtered = [kw for kw in v if any(term in kw.lower() for term in prestigious_terms)]
        return filtered


class TalentSignalEnhancer:
    """Enhances talent signals in resume content and generates network hooks."""

    def __init__(self, candidate_background: dict[str, Any]):
        """Initialize the talent signal enhancer.

        Args:
            candidate_background: Candidate's professional background
        """
        self.candidate_background = candidate_background
        self.management_history = candidate_background.get("management_history", [])
        self.network_size = candidate_background.get("network_size", {})
        self.has_management_experience = len(self.management_history) > 0
        self.pedigree_patterns = {
            "education": [
                "phd",
                "masters?",
                "msc",
                "mba",
                "ivy league",
                "stanford",
                "mit",
                "cmu",
                "berkeley",
                "carnegie mellon",
            ],
            "experience": [
                "ex-(google|meta|amazon|apple|microsoft|netflix|faang)",
                "former (google|meta|amazon|apple|microsoft|netflix)",
                "previously at (google|meta|amazon|apple|microsoft|netflix)",
                "big tech",
                "fortune 500",
                "top-tier",
            ],
            "seniority": [
                "senior",
                "principal",
                "staff",
                "founding engineer",
                "lead",
                "head of",
                "director",
                "vp",
            ],
            "achievement": [
                "researcher",
                "contributor",
                "open-source",
                "github",
                "kaggle",
                "published",
                "patented",
            ],
        }
        logger.info(
            f"Initialized TalentSignalEnhancer with management experience: {self.has_management_experience}"
        )

    def enhance_management_bullet(self, bullet_text: str) -> str:
        """Enhance a management bullet with talent signals.

        Args:
            bullet_text: Original management bullet

        Returns:
            Enhanced bullet with talent attraction focus
        """
        try:
            team_size = self._extract_team_size(bullet_text)
            pedigree = self._detect_pedigree(bullet_text)
            hiring_metric = self._extract_hiring_metric(bullet_text)
            retention_metric = self._extract_retention_metric(bullet_text)
            enhanced = bullet_text
            if team_size > 0:
                if pedigree:
                    pedigree_str = ", ".join(pedigree[:3])
                    enhanced = enhanced.replace(
                        f"team of {team_size}", f"team of {team_size} (including **{pedigree_str}**)"
                    )
                else:
                    enhanced = enhanced.replace(
                        f"team of {team_size}", f"high-performance team of {team_size}"
                    )
            if hiring_metric:
                if "hired" in enhanced.lower():
                    enhanced = enhanced.replace("hired", f"recruited **{hiring_metric}**")
            if retention_metric:
                enhanced += f", achieving **{retention_metric} retention**"
            if not pedigree and (not hiring_metric) and (not retention_metric):
                enhanced = self._strengthen_generic_bullet(enhanced, team_size)
            logger.debug(f"Enhanced bullet: {bullet_text[:50]}... -> {enhanced[:50]}...")
            return enhanced
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Error enhancing management bullet: {str(e)}")
            return bullet_text

    def generate_network_hook(self, target_role: str) -> str | None:
        """Generate a P.S. hook leveraging network as asset.

        Args:
            target_role: Role being targeted (e.g., "Senior AI Engineer")

        Returns:
            Network hook string or None if no management experience
        """
        try:
            if not self.has_management_experience:
                logger.debug("No management experience, skipping network hook")
                return None
            role_network = self.network_size.get(target_role.lower(), 0)
            if role_network < 5:
                return None
            hook = f"P.S. I have a specialized network of {role_network} {target_role}s who often follow me to new ventures. I could likely fill your open {target_role} roles within 60 days."
            logger.info(f"Generated network hook for {target_role} with network size {role_network}")
            return hook
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Error generating network hook: {str(e)}")
            return None

    def get_hyde_context(self, job_description: str) -> str | None:
        """Get HyDE context if JD is hiring-heavy.

        Args:
            job_description: Job description text

        Returns:
            "Recruiting" context if hiring focus detected
        """
        try:
            hiring_keywords = [
                "hire",
                "hiring",
                "recruit",
                "build team",
                "scale team",
                "grow team",
                "talent acquisition",
                "team building",
            ]
            jd_lower = job_description.lower()
            hiring_count = sum(1 for keyword in hiring_keywords if keyword in jd_lower)
            if hiring_count >= 3:
                return "Recruiting"
            return None
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Error getting HyDE context: {str(e)}")
            return None

    def _detect_pedigree(self, text: str) -> list[str]:
        """Detect prestige markers in text.

        Args:
            text: Text to scan for pedigree markers

        Returns:
            List of detected prestige markers
        """
        try:
            text_lower = text.lower()
            detected = []
            for category, patterns in self.pedigree_patterns.items():
                for pattern in patterns:
                    matches = re.findall(pattern, text_lower)
                    for match in matches:
                        if category == "experience":
                            formatted = f"Ex-{match.title()}"
                        elif category == "education":
                            formatted = match.title()
                        else:
                            formatted = match.title()
                        if formatted not in detected:
                            detected.append(formatted)
            if not detected and any(term in text_lower for term in ["senior", "lead", "principal"]):
                detected.append("Senior Talent")
            return detected[:5]
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Error detecting pedigree: {str(e)}")
            return []

    def _extract_team_size(self, text: str) -> int:
        """Extract team size from text.

        Args:
            text: Text containing team size

        Returns:
            Team size number
        """
        try:
            patterns = [
                "team of (\\d+)",
                "(\\d+) (?:people|engineers|developers|members)",
                "managed (\\d+)",
                "led (\\d+)",
                "built a team of (\\d+)",
            ]
            for pattern in patterns:
                match = re.search(pattern, text.lower())
                if match:
                    return int(match.group(1))
            return 0
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Error extracting team size: {str(e)}")
            return 0

    def _extract_hiring_metric(self, text: str) -> str | None:
        """Extract hiring velocity from text.

        Args:
            text: Text containing hiring information

        Returns:
            Hiring velocity string or None
        """
        try:
            patterns = [
                "hired (\\d+) in (\\d+) months?",
                "recruited (\\d+) within (\\d+) months?",
                "built team from (\\d+) to (\\d+) in (\\d+) months?",
            ]
            for pattern in patterns:
                match = re.search(pattern, text.lower())
                if match:
                    groups = match.groups()
                    if len(groups) == 2:
                        return f"{groups[0]} in <{groups[1]} months"
                    elif len(groups) == 3:
                        growth = int(groups[1]) - int(groups[0])
                        return f"{growth} in <{groups[2]} months"
            return None
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Error extracting hiring metric: {str(e)}")
            return None

    def _extract_retention_metric(self, text: str) -> str | None:
        """Extract retention rate from text.

        Args:
            text: Text containing retention information

        Returns:
            Retention rate string or None
        """
        try:
            patterns = ["(\\d+)% retention", "retention of (\\d+)%", "retained (\\d+)%"]
            for pattern in patterns:
                match = re.search(pattern, text.lower())
                if match:
                    return f"{match.group(1)}%"
            if any(phrase in text.lower() for phrase in ["no attrition", "zero turnover", "100% retained"]):
                return "100%"
            return None
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Error extracting retention metric: {str(e)}")
            return None

    def _strengthen_generic_bullet(self, bullet: str, team_size: int) -> str:
        """Strengthen generic management bullet.

        Args:
            bullet: Original bullet
            team_size: Detected team size

        Returns:
            Strengthened bullet
        """
        try:
            if team_size > 0:
                if team_size >= 20:
                    bullet = bullet.replace(
                        f"team of {team_size}", f"team of {team_size} **senior engineers**"
                    )
                elif team_size >= 10:
                    bullet = bullet.replace(
                        f"team of {team_size}", f"team of {team_size} **high-caliber engineers**"
                    )
                else:
                    bullet = bullet.replace(
                        f"team of {team_size}", f"team of {team_size} **specialized engineers**"
                    )
            if "managed" in bullet.lower():
                bullet = bullet.replace("managed", "built and led")
            return bullet
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Error strengthening generic bullet: {str(e)}")
            return bullet


def create_talent_signal_enhancer(candidate_background: dict[str, Any]) -> TalentSignalEnhancer:
    """Create a TalentSignalEnhancer instance.

    Args:
        candidate_background: Candidate's professional background

    Returns:
        Configured TalentSignalEnhancer
    """
    return TalentSignalEnhancer(candidate_background)


def enhance_talent_signals(
    bullets: list[str], candidate_background: dict[str, Any]
) -> tuple[list[str], str | None]:
    """Quickly enhance talent signals in bullets.

    Args:
        bullets: List of management bullets
        candidate_background: Candidate background

    Returns:
        Tuple of (enhanced bullets, network hook)
    """
    enhancer = create_talent_signal_enhancer(candidate_background)
    enhanced = [enhancer.enhance_management_bullet(b) for b in bullets]
    hook = None
    if enhancer.has_management_experience:
        hook = enhancer.generate_network_hook("Senior AI Engineer")
    return (enhanced, hook)
