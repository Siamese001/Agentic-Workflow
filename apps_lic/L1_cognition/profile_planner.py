"""Profile Planner - L1 planning for profile analysis and archetype inference.

Incorporated from L1 lic_profile_planner.py to provide deterministic profile
planning that maps LinkedIn/CRM profile fields to LIC archetypes, seniority
levels, and targeting parameters with confidence scoring.

This is a foundational L1 planning component that feeds into the hop-based
K1-K7 execution pipeline for profile-driven message generation.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

@dataclass
class ProfileSignal:
    """Individual signal extracted from profile analysis."""
    signal_type: str                     # e.g. "title_keywords", "company_size", "industry"
    value: str                           # raw signal value
    confidence: float                    # confidence in this signal [0, 1]
    metadata: Dict[str, object] = field(default_factory=dict)

@dataclass
class ProfilePlan:
    """Complete profile analysis plan for LIC targeting."""
    inferred_archetype: str              # "executive" | "senior_ta" | "recruiter" | "other"
    seniority_level: str                 # "C_LEVEL" | "VP" | "director" | "SR_MANAGER" | "IC"
    confidence_score: float              # overall confidence [0, 1]
    overrides: Dict[str, object]            # explicit overrides from outreach_context
    signals: List[ProfileSignal]         # individual profile signals
    company_size: str                    # "startup", "small", "medium", "large", "enterprise"
    industry_focus: str                  # primary industry classification
    decision_authority: str              # "high", "medium", "low"
    metadata: Dict[str, object] = field(default_factory=dict)

class ProfilePlanner:
    """L1 pure planner for profile analysis and archetype inference.

    Generates deterministic profile plans by analyzing LinkedIn/CRM fields
    and mapping them to LIC archetypes and seniority levels.
    """

    def __init__(self, telemetry_bus: Optional[Any] = None) -> None:
        """Initialize profile planner."""
        self.telemetry_bus = telemetry_bus

        # Archetype keyword mappings
        self.executive_keywords = {
            "ceo", "cto", "cfo", "ciso", "chief", "president", "founder", "co-founder",
            "vp", "vice president", "director", "head", "leader", "executive"
        }

        self.senior_ta_keywords = {
            "principal", "staff", "senior", "lead", "architect", "engineer", "developer",
            "technical", "software", "data", "infrastructure", "devops", "security"
        }

        self.recruiter_keywords = {
            "recruiter", "talent", "sourcer", "hiring", "hr", "human resources", "staffing"
        }

        # Seniority level mappings
        self.c_level_keywords = {"ceo", "cto", "cfo", "ciso", "chief", "president"}
        self.vp_keywords = {"vp", "vice president"}
        self.director_keywords = {"director", "head"}
        self.sr_manager_keywords = {"senior manager", "sr manager", "manager"}
        self.ic_keywords = {"engineer", "developer", "analyst", "specialist", "coordinator"}

        # Company size indicators
        self.company_size_patterns = {
            "startup": ["startup", "early stage", "seed", "series a", "series b"],
            "small": ["small business", "smb", "1-50", "50-100"],
            "medium": ["mid-size", "medium", "100-500", "500-1000"],
            "large": ["large", "enterprise", "1000-5000", "5000-10000"],
            "enterprise": ["fortune", "global", "multinational", "10000+"]
        }

        # Industry classifications
        self.industry_keywords = {
            "technology": ["software", "tech", "saas", "fintech", "biotech", "ai", "ml"],
            "finance": ["bank", "financial", "investment", "insurance", "fintech"],
            "healthcare": ["health", "medical", "pharma", "biotech", "hospital"],
            "consulting": ["consulting", "advisory", "services", "solutions"],
            "manufacturing": ["manufacturing", "production", "industrial", "automotive"],
            "retail": ["retail", "ecommerce", "consumer", "sales"],
            "education": ["education", "university", "academic", "learning"],
            "government": ["government", "public", "federal", "state", "municipal"]
        }

    def plan(
        self,
        *,
        recipient_profile: Dict[str, object],
        outreach_context: Dict[str, object] = None,
    ) -> ProfilePlan:
        """Generate a deterministic profile analysis plan.

        Args:
            recipient_profile: LinkedIn/CRM profile data
            outreach_context: Optional context with explicit overrides

        Returns:
            Complete profile plan with archetype, seniority, and signals
        """
        outreach_context = outreach_context or {}

        # 1. Extract signals from profile
        signals = self._extract_profile_signals(recipient_profile)

        # 2. Infer archetype from signals
        inferred_archetype = self._infer_archetype(signals)

        # 3. Determine seniority level
        seniority_level = self._determine_seniority(recipient_profile, signals)

        # 4. Analyze company characteristics
        company_size = self._analyze_company_size(recipient_profile, signals)
        industry_focus = self._classify_industry(recipient_profile, signals)
        decision_authority = self._assess_decision_authority(seniority_level,
            company_size,
            inferred_archetype)

        # 5. Apply explicit overrides
        overrides = outreach_context.get("overrides", {})
        final_archetype = overrides.get("archetype", inferred_archetype)
        final_seniority = overrides.get("seniority", seniority_level)

        # 6. Calculate confidence score
        confidence_score = self._calculate_confidence_score(signals,
            final_archetype,
            final_seniority)

        # 7. Build metadata
        metadata = {
            "profile_completeness": self._assess_profile_completeness(recipient_profile),
            "signal_count": len(signals),
            "has_overrides": len(overrides) > 0,
            "inferred_archetype": inferred_archetype,
            "final_archetype": final_archetype,
            "company_size": company_size,
            "industry_focus": industry_focus
        }

        # 8. Create profile plan
        plan = ProfilePlan(
            inferred_archetype=final_archetype,
            seniority_level=final_seniority,
            confidence_score=confidence_score,
            overrides=overrides,
            signals=signals,
            company_size=company_size,
            industry_focus=industry_focus,
            decision_authority=decision_authority,
            metadata=metadata,
        )

        # 9. Record telemetry (best-effort)
        self._safe_record_telemetry(plan)

        return plan

    def _extract_profile_signals(self, profile: Dict[str, object]) -> List[ProfileSignal]:
        """Extract individual signals from profile data."""
        signals = []

        # Title keywords signal
        title = profile.get("title", "").lower()
        if title:
            title_keywords = self._extract_title_keywords(title)
            signals.append(ProfileSignal(
                signal_type="title_keywords",
                value=", ".join(title_keywords),
                confidence=0.9,
                metadata={"original_title": profile.get("title", "")}
            ))

        # Company size signal
        company = profile.get("company", "").lower()
        if company:
            size_signals = self._extract_company_signals(company)
            signals.extend(size_signals)

        # Industry signal
        industry = profile.get("industry", "").lower()
        if industry:
            industry_classification = self._classify_industry_from_text(industry)
            if industry_classification:
                signals.append(ProfileSignal(
                    signal_type="industry",
                    value=industry_classification,
                    confidence=0.8,
                    metadata={"original_industry": profile.get("industry", "")}
                ))

        # Experience level signal
        experience = profile.get("experience", [])
        if experience:
            exp_signal = self._analyze_experience_level(experience)
            signals.append(exp_signal)

        # Skills signal
        skills = profile.get("skills", [])
        if skills:
            skills_signal = self._analyze_skills_profile(skills)
            signals.append(skills_signal)

        # Education signal
        education = profile.get("education", "")
        if education:
            edu_signal = self._analyze_education_level(education)
            signals.append(edu_signal)

        logger.debug(f"Extracted {len(signals)} profile signals")
        return signals

    def _extract_title_keywords(self, title: str) -> List[str]:
        """Extract archetype-relevant keywords from title."""
        keywords = []
        title_lower = title.lower()

        # Check for executive keywords
        for keyword in self.executive_keywords:
            if keyword in title_lower:
                keywords.append(keyword)

        # Check for technical keywords
        for keyword in self.senior_ta_keywords:
            if keyword in title_lower:
                keywords.append(keyword)

        # Check for recruiter keywords
        for keyword in self.recruiter_keywords:
            if keyword in title_lower:
                keywords.append(keyword)

        return keywords

    def _extract_company_signals(self, company: str) -> List[ProfileSignal]:
        """Extract company-related signals."""
        signals = []

        # Company size
        for size, patterns in self.company_size_patterns.items():
            for pattern in patterns:
                if pattern in company:
                    signals.append(ProfileSignal(
                        signal_type="company_size",
                        value=size,
                        confidence=0.7,
                        metadata={"pattern_matched": pattern}
                    ))
                    break

        return signals

    def _classify_industry_from_text(self, text: str) -> Optional[str]:
        """Classify industry from text."""
        text_lower = text.lower()

        for industry, keywords in self.industry_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return industry

        return "other"

    def _analyze_experience_level(self, experience: List[Any]) -> ProfileSignal:
        """Analyze experience level from experience list."""
        total_years = 0
        job_count = len(experience)

        # Simple heuristic for years of experience
        if job_count > 10:
            level = "senior"
            confidence = 0.7
        elif job_count > 5:
            level = "mid_level"
            confidence = 0.6
        elif job_count > 2:
            level = "junior"
            confidence = 0.5
        else:
            level = "entry"
            confidence = 0.3

        return ProfileSignal(
            signal_type="experience_level",
            value=level,
            confidence=confidence,
            metadata={"job_count": job_count}
        )

    def _analyze_skills_profile(self, skills: List[str]) -> ProfileSignal:
        """Analyze skills profile for technical vs business orientation."""
        if not skills:
            return ProfileSignal(
                signal_type="skills_orientation",
                value="unknown",
                confidence=0.0
            )

        skills_text = " ".join(skills).lower()

        technical_count = sum(1 for skill in skills if any(
            kw in skill.lower() for kw in ["software",
                "programming",
                "data",
                "engineering",
                "technical"]
        ))

        business_count = sum(1 for skill in skills if any(
            kw in skill.lower() for kw in ["management",
                "business",
                "strategy",
                "sales",
                "marketing"]
        ))

        if technical_count > business_count:
            orientation = "technical"
        elif business_count > technical_count:
            orientation = "business"
        else:
            orientation = "balanced"

        confidence = min(technical_count + business_count, 10) / 10.0

        return ProfileSignal(
            signal_type="skills_orientation",
            value=orientation,
            confidence=confidence,
            metadata={"technical_count": technical_count, "business_count": business_count}
        )

    def _analyze_education_level(self, education: str) -> ProfileSignal:
        """Analyze education level from education text."""
        edu_lower = education.lower()

        if any(degree in edu_lower for degree in ["phd", "doctorate", "doctor"]):
            level = "doctorate"
            confidence = 0.9
        elif any(degree in edu_lower for degree in ["master", "ms", "mba", "graduate"]):
            level = "masters"
            confidence = 0.8
        elif any(degree in edu_lower for degree in ["bachelor", "bs", "ba", "undergraduate"]):
            level = "bachelors"
            confidence = 0.7
        else:
            level = "unknown"
            confidence = 0.3

        return ProfileSignal(
            signal_type="education_level",
            value=level,
            confidence=confidence
        )

    def _score_keyword(self, keyword: str, confidence: float, scores: Dict[str, float]) -> None:
        """Score a keyword against archetype categories."""
        if keyword in self.executive_keywords:
            scores["executive"] += confidence
        elif keyword in self.senior_ta_keywords:
            scores["senior_ta"] += confidence
        elif keyword in self.recruiter_keywords:
            scores["recruiter"] += confidence

    def _determine_archetype_from_scores(self, scores: Dict[str, float]) -> str:
        """Determine archetype from scores."""
        if scores["executive"] >= scores["senior_ta"] and scores["executive"] >= scores["recruiter"]:
            return "executive"
        elif scores["senior_ta"] >= scores["recruiter"]:
            return "senior_ta"
        elif scores["recruiter"] > 0:
            return "recruiter"
        return "other"

    def _infer_archetype(self, signals: List[ProfileSignal]) -> str:
        """Infer archetype from profile signals."""
        scores = {"executive": 0, "senior_ta": 0, "recruiter": 0}

        for signal in signals:
            if signal.signal_type != "title_keywords":
                continue
            keywords = signal.value.lower().split(", ")
            for keyword in keywords:
                self._score_keyword(keyword, signal.confidence, scores)

        return self._determine_archetype_from_scores(scores)

    def _determine_seniority(self, profile: Dict[str, object], signals: List[ProfileSignal]) -> str:
        """Determine seniority level from profile and signals."""
        title = profile.get("title", "").lower()

        # Check title for seniority keywords
        if any(keyword in title for keyword in self.c_level_keywords):
            return "C_LEVEL"
        elif any(keyword in title for keyword in self.vp_keywords):
            return "VP"
        elif any(keyword in title for keyword in self.director_keywords):
            return "director"
        elif any(keyword in title for keyword in self.sr_manager_keywords):
            return "SR_MANAGER"
        elif any(keyword in title for keyword in self.ic_keywords):
            return "IC"

        # Fall back to experience level
        exp_signal = next((s for s in signals if s.signal_type == "experience_level"), None)
        if exp_signal:
            exp_level = exp_signal.value
            if exp_level == "senior":
                return "SR_MANAGER"
            elif exp_level == "mid_level":
                return "IC"
            else:
                return "IC"

        return "IC"  # Default

    def _analyze_company_size(self,
        profile: Dict[str,
        object],
        signals: List[ProfileSignal]) -> str:
        """Analyze company size from profile and signals."""
        # Check for explicit company size signal
        size_signal = next((s for s in signals if s.signal_type == "company_size"), None)
        if size_signal:
            return size_signal.value

        # Infer from company description
        company = profile.get("company", "").lower()
        if any(indicator in company for indicator in ["startup", "early stage", "seed"]):
            return "startup"
        elif any(indicator in company for indicator in ["fortune", "global", "multinational"]):
            return "enterprise"
        else:
            return "medium"  # Default

    def _classify_industry(self, profile: Dict[str, object], signals: List[ProfileSignal]) -> str:
        """Classify industry focus."""
        # Check for explicit industry signal
        industry_signal = next((s for s in signals if s.signal_type == "industry"), None)
        if industry_signal:
            return industry_signal.value

        # Fall back to profile industry field
        industry = profile.get("industry", "")
        if industry:
            return self._classify_industry_from_text(industry.lower())

        return "other"

    def _assess_decision_authority(self, seniority: str, company_size: str, archetype: str) -> str:
        """Assess decision authority based on seniority, company size, and archetype."""
        if seniority == "C_LEVEL":
            return "high"
        elif seniority in ["VP", "director"]:
            return "medium"
        elif archetype == "executive" and company_size in ["startup", "small"]:
            return "medium"
        else:
            return "low"

    def _calculate_confidence_score(self,
        signals: List[ProfileSignal],
        archetype: str,
        seniority: str) -> float:
        """Calculate overall confidence score."""
        if not signals:
            return 0.0

        # Base confidence from signal count and quality
        avg_signal_confidence = sum(s.confidence for s in signals) / len(signals)

        # Boost for clear archetype match
        archetype_boost = 0.2 if archetype != "other" else 0.0

        # Boost for specific seniority
        seniority_boost = 0.1 if seniority != "IC" else 0.0

        confidence = avg_signal_confidence + archetype_boost + seniority_boost
        return round(min(confidence, 1.0), 3)

    def _assess_profile_completeness(self, profile: Dict[str, object]) -> float:
        """Assess how complete the profile data is."""
        required_fields = ["title", "company", "industry"]
        optional_fields = ["experience", "skills", "education"]

        required_score = sum(1 for field in required_fields if profile.get(field)) / len(required_fields)
        optional_score = sum(1 for field in optional_fields if profile.get(field)) / len(optional_fields)

        completeness = (required_score * 0.7) + (optional_score * 0.3)
        return round(completeness, 3)

    def _safe_record_telemetry(self, plan: ProfilePlan) -> None:
        """Record telemetry data (best-effort)."""
        try:
            if self.telemetry_bus:
                self.telemetry_bus.record("profile_plan_created", {
                    "archetype": plan.inferred_archetype,
                    "seniority": plan.seniority_level,
                    "confidence": plan.confidence_score,
                    "signal_count": len(plan.signals)
                })
        except Exception as e:  # guardian: allow-broad-exception -- telemetry emission must not break planner flow; logger.debug records failure
            logger.debug(f"Failed to record telemetry: {e}")

    def get_profile_summary(self, plan: ProfilePlan) -> Dict[str, object]:
        """Get a summary of the profile plan for debugging/telemetry."""
        return {
            "plan_id": f"profile_{plan.inferred_archetype}_{plan.seniority_level}",
            "archetype": plan.inferred_archetype,
            "seniority": plan.seniority_level,
            "confidence": plan.confidence_score,
            "company_size": plan.company_size,
            "industry": plan.industry_focus,
            "decision_authority": plan.decision_authority,
            "signal_count": len(plan.signals),
            "has_overrides": len(plan.overrides) > 0,
            "profile_completeness": plan.metadata.get("profile_completeness", 0.0)
        }
