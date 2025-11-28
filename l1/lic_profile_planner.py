"""LIC Profile Planner - L1 pure planning for profile analysis.

Implements nuclear prompt requirements for deterministic profile planning:
- Maps LinkedIn/CRM profile fields → LIC archetype + seniority + overrides + confidence
- Pure L1 planning with no external calls or execution
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class LICProfileSignal:
    """Individual signal extracted from profile analysis."""
    signal_type: str                     # e.g. "title_keywords", "company_size", "industry"
    value: str                           # raw signal value
    confidence: float                    # confidence in this signal [0, 1]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LICProfilePlan:
    """Complete profile analysis plan for LIC targeting."""
    inferred_archetype: str              # "EXECUTIVE" | "SENIOR_TA" | "RECRUITER" | "OTHER"
    seniority_level: str                 # "C_LEVEL" | "VP" | "DIRECTOR" | "SR_MANAGER" | "IC"
    confidence_score: float              # overall confidence [0, 1]
    overrides: Dict[str, Any]            # explicit overrides from outreach_context
    signals: List[LICProfileSignal]     # individual profile signals
    metadata: Dict[str, Any] = field(default_factory=dict)


class LICProfilePlanner:
    """L1 pure planner for profile analysis and archetype inference.
    
    Generates deterministic profile plans by analyzing LinkedIn/CRM fields
    and mapping them to LIC archetypes and seniority levels.
    """
    
    def __init__(self, telemetry_bus: Optional[Any] = None) -> None:
        """Initialize LIC profile planner."""
        self.telemetry_bus = telemetry_bus
        
        # Archetype keyword mappings
        self.executive_keywords = {
            "ceo", "cto", "cfo", "ciso", "chief", "president", "founder", "co-founder",
            "vp", "vice president", "director", "head", "leader", "executive"
        }
        
        self.recruiter_keywords = {
            "recruiter", "talent acquisition", "sourcer", "hiring manager",
            "hr", "human resources", "people", "recruitment"
        }
        
        self.technical_keywords = {
            "engineer", "developer", "architect", "technical", "software",
            "engineering", "devops", "sre", "data scientist", "ml engineer"
        }
        
        # Seniority level mappings
        self.c_level_keywords = {"ceo", "cto", "cfo", "ciso", "chief", "president"}
        self.vp_keywords = {"vp", "vice president"}
        self.director_keywords = {"director", "head"}
        self.sr_manager_keywords = {"senior manager", "sr manager", "lead"}
        self.ic_keywords = {"engineer", "developer", "analyst", "specialist"}
    
    def plan(
        self,
        *,
        profile_data: Dict[str, Any],
        outreach_context: Dict[str, Any],
    ) -> LICProfilePlan:
        """Generate a deterministic profile analysis plan.
        
        Args:
            profile_data: LinkedIn/CRM profile fields (title, company, industry, etc.)
            outreach_context: Context data including explicit overrides
            
        Returns:
            Complete profile plan with archetype, seniority, confidence, and signals
        """
        # 1. Extract signals from profile data
        signals = self._extract_profile_signals(profile_data)
        
        # 2. Apply explicit overrides from outreach_context
        overrides = self._extract_overrides(outreach_context)
        
        # 3. Infer archetype from signals and overrides
        inferred_archetype = self._infer_archetype(signals, overrides)
        
        # 4. Infer seniority level from title and signals
        seniority_level = self._infer_seniority_level(signals, overrides)
        
        # 5. Compute overall confidence score
        confidence_score = self._compute_confidence_score(signals, overrides)
        
        # 6. Build metadata
        metadata = {
            "signal_count": len(signals),
            "has_explicit_archetype_override": "archetype" in overrides,
            "has_explicit_seniority_override": "seniority_level" in overrides,
        }
        
        # 7. Create profile plan
        plan = LICProfilePlan(
            inferred_archetype=inferred_archetype,
            seniority_level=seniority_level,
            confidence_score=confidence_score,
            overrides=overrides,
            signals=signals,
            metadata=metadata,
        )
        
        # 8. Record telemetry (best-effort)
        self._safe_record_telemetry(plan)
        
        return plan
    
    def _extract_profile_signals(self, profile_data: Dict[str, Any]) -> List[LICProfileSignal]:
        """Extract individual signals from profile data."""
        signals = []
        
        # Extract title keywords signal
        title = profile_data.get("title", "").lower()
        if title:
            title_keywords = self._extract_title_keywords(title)
            signals.append(LICProfileSignal(
                signal_type="title_keywords",
                value=",".join(title_keywords),
                confidence=0.9,
                metadata={"raw_title": title},
            ))
        
        # Extract company size signal
        company_size = profile_data.get("company_size", "").lower()
        if company_size:
            signals.append(LICProfileSignal(
                signal_type="company_size",
                value=company_size,
                confidence=0.8,
                metadata={},
            ))
        
        # Extract industry signal
        industry = profile_data.get("industry", "").lower()
        if industry:
            signals.append(LICProfileSignal(
                signal_type="industry",
                value=industry,
                confidence=0.7,
                metadata={},
            ))
        
        # Extract experience years signal
        experience_years = profile_data.get("experience_years", 0)
        if experience_years > 0:
            signals.append(LICProfileSignal(
                signal_type="experience_years",
                value=str(experience_years),
                confidence=0.8,
                metadata={"years": experience_years},
            ))
        
        # Extract location signal
        location = profile_data.get("location", "").lower()
        if location:
            signals.append(LICProfileSignal(
                signal_type="location",
                value=location,
                confidence=0.6,
                metadata={},
            ))
        
        return signals
    
    def _extract_title_keywords(self, title: str) -> List[str]:
        """Extract relevant keywords from job title."""
        words = title.replace("-", " ").replace("/", " ").split()
        keywords = []
        
        for word in words:
            word_clean = word.strip("(),").lower()
            if word_clean in self.executive_keywords:
                keywords.append(word_clean)
            elif word_clean in self.recruiter_keywords:
                keywords.append(word_clean)
            elif word_clean in self.technical_keywords:
                keywords.append(word_clean)
        
        return list(set(keywords))
    
    def _extract_overrides(self, outreach_context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract explicit overrides from outreach context."""
        overrides = {}
        
        # Check for explicit archetype override
        if "archetype_override" in outreach_context:
            archetype = outreach_context["archetype_override"].upper()
            if archetype in ["EXECUTIVE", "SENIOR_TA", "RECRUITER", "OTHER"]:
                overrides["archetype"] = archetype
        
        # Check for explicit seniority override
        if "seniority_override" in outreach_context:
            seniority = outreach_context["seniority_override"].upper()
            if seniority in ["C_LEVEL", "VP", "DIRECTOR", "SR_MANAGER", "IC"]:
                overrides["seniority_level"] = seniority
        
        # Check for explicit confidence override
        if "confidence_override" in outreach_context:
            confidence = outreach_context["confidence_override"]
            if isinstance(confidence, (int, float)) and 0 <= confidence <= 1:
                overrides["confidence_score"] = confidence
        
        return overrides
    
    def _infer_archetype(self, signals: List[LICProfileSignal], overrides: Dict[str, Any]) -> str:
        """Infer archetype from signals, respecting overrides."""
        # Explicit override takes precedence
        if "archetype" in overrides:
            return overrides["archetype"]
        
        # Analyze title keywords
        title_signal = next((s for s in signals if s.signal_type == "title_keywords"), None)
        if title_signal:
            keywords = title_signal.value.split(",")
            
            # Check for recruiter keywords first (most specific)
            if any(kw in self.recruiter_keywords for kw in keywords):
                return "RECRUITER"
            
            # Check for executive keywords
            if any(kw in self.executive_keywords for kw in keywords):
                return "EXECUTIVE"
            
            # Check for technical keywords
            if any(kw in self.technical_keywords for kw in keywords):
                return "SENIOR_TA"
        
        # Fallback based on company size and experience
        company_size_signal = next((s for s in signals if s.signal_type == "company_size"), None)
        experience_signal = next((s for s in signals if s.signal_type == "experience_years"), None)
        
        if (company_size_signal and "large" in company_size_signal.value) or \
           (experience_signal and int(experience_signal.value) >= 15):
            return "EXECUTIVE"
        elif experience_signal and int(experience_signal.value) >= 8:
            return "SENIOR_TA"
        
        return "OTHER"
    
    def _infer_seniority_level(self, signals: List[LICProfileSignal], overrides: Dict[str, Any]) -> str:
        """Infer seniority level from signals, respecting overrides."""
        # Explicit override takes precedence
        if "seniority_level" in overrides:
            return overrides["seniority_level"]
        
        # Analyze title for seniority keywords
        title_signal = next((s for s in signals if s.signal_type == "title_keywords"), None)
        if title_signal:
            title = title_signal.metadata.get("raw_title", "")
            
            # Check for C-level
            if any(kw in title for kw in self.c_level_keywords):
                return "C_LEVEL"
            
            # Check for VP level
            if any(kw in title for kw in self.vp_keywords):
                return "VP"
            
            # Check for Director level
            if any(kw in title for kw in self.director_keywords):
                return "DIRECTOR"
            
            # Check for Senior Manager level
            if any(kw in title for kw in self.sr_manager_keywords):
                return "SR_MANAGER"
            
            # Check for IC level
            if any(kw in title for kw in self.ic_keywords):
                return "IC"
        
        # Fallback based on experience years
        experience_signal = next((s for s in signals if s.signal_type == "experience_years"), None)
        if experience_signal:
            years = int(experience_signal.value)
            if years >= 20:
                return "C_LEVEL"
            elif years >= 15:
                return "VP"
            elif years >= 10:
                return "DIRECTOR"
            elif years >= 5:
                return "SR_MANAGER"
            else:
                return "IC"
        
        return "IC"
    
    def _compute_confidence_score(self, signals: List[LICProfileSignal], overrides: Dict[str, Any]) -> float:
        """Compute overall confidence score based on signal agreement."""
        # Explicit override gives high confidence
        if "confidence_score" in overrides:
            return overrides["confidence_score"]
        
        if not signals:
            return 0.0
        
        # Base confidence from signal count and quality
        signal_confidences = [s.confidence for s in signals]
        avg_confidence = sum(signal_confidences) / len(signal_confidences)
        
        # Boost for explicit archetype/seniority overrides
        boost = 0.0
        if "archetype" in overrides:
            boost += 0.2
        if "seniority_level" in overrides:
            boost += 0.1
        
        # Boost for strong title signal
        title_signal = next((s for s in signals if s.signal_type == "title_keywords"), None)
        if title_signal and title_signal.confidence >= 0.9:
            boost += 0.1
        
        final_confidence = min(avg_confidence + boost, 1.0)
        return round(final_confidence, 2)
    
    def _safe_record_telemetry(self, plan: LICProfilePlan) -> None:
        """Record telemetry event safely without breaking planning."""
        if not self.telemetry_bus:
            return
        
        try:
            self.telemetry_bus.record_event(
                "lic_profile_plan_created",
                layer="L1",
                payload={
                    "inferred_archetype": plan.inferred_archetype,
                    "seniority_level": plan.seniority_level,
                    "confidence_score": plan.confidence_score,
                    "signal_count": len(plan.signals),
                    "has_overrides": len(plan.overrides) > 0,
                },
            )
        except Exception:
            # Telemetry failures should never break planning logic
            logger.debug("Failed to record telemetry for LIC profile plan")
