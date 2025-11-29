"""LIC Persona Drift Controller - L3 orchestration for persona drift monitoring.

Implements nuclear prompt requirements for deterministic drift control:
- Monitor drafts across iterations and detect persona/tone drift vs LICPersonaPlan
- L3 only: orchestrational analysis, no LLM calls
- Compute drift score using simple heuristics and mark reason/metadata for meta-loop
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class LICPersonaDriftEvent:
    """Persona drift detection event."""
    archetype: str                       # target archetype
    drift_score: float                   # drift score in [0, 1]
    reason: str                          # reason for drift detection
    metadata: Dict[str, Any] = field(default_factory=dict)


class LICPersonaDriftController:
    """L3 orchestrator for persona drift monitoring and detection.
    
    Monitors message drafts across iterations to detect persona
    and tone drift compared to the original persona plan.
    """
    
    def __init__(self, telemetry_bus: Optional[Any] = None) -> None:
        """Initialize LIC persona drift controller."""
        self.telemetry_bus = telemetry_bus
        
        # Tone keywords for different styles
        self.tone_keywords = {
            "executive": ["concise", "strategic", "business", "professional", "direct"],
            "technical": ["technical", "detailed", "implementation", "architecture", "engineering"],
            "friendly": ["friendly", "approachable", "collaborative", "team", "culture"],
            "formal": ["formal", "respectful", "professional", "business", "corporate"],
            "casual": ["casual", "informal", "relaxed", "friendly", "approach"],
        }
        
        # Drift detection thresholds
        self.drift_thresholds = {
            "tone_shift": 0.3,           # threshold for tone keyword changes
            "length_change": 0.4,        # threshold for length changes
            "style_variance": 0.25,       # threshold for style variance
        }
    
    def compute_drift(
        self,
        persona_plan: Dict[str, Any],
        draft_history: List[str],
    ) -> LICPersonaDriftEvent:
        """Compute persona drift from draft history.
        
        Args:
            persona_plan: Original persona plan with target parameters
            draft_history: List of message drafts in chronological order
            
        Returns:
            Drift event with score, reason, and metadata
        """
        if not draft_history:
            return LICPersonaDriftEvent(
                archetype=persona_plan.get("archetype", "UNKNOWN"),
                drift_score=0.0,
                reason="No drafts to compare",
                metadata={"draft_count": 0},
            )
        
        if len(draft_history) < 2:
            return LICPersonaDriftEvent(
                archetype=persona_plan.get("archetype", "UNKNOWN"),
                drift_score=0.0,
                reason="Insufficient drafts for drift analysis",
                metadata={"draft_count": len(draft_history)},
            )
        
        try:
            # 1. Analyze tone keyword shifts
            tone_drift = self._analyze_tone_drift(persona_plan, draft_history)
            
            # 2. Analyze length changes
            length_drift = self._analyze_length_drift(draft_history)
            
            # 3. Analyze style variance
            style_drift = self._analyze_style_variance(persona_plan, draft_history)
            
            # 4. Compute overall drift score
            overall_drift = self._compute_overall_drift(tone_drift, length_drift, style_drift)
            
            # 5. Determine drift reason
            drift_reason = self._determine_drift_reason(tone_drift, length_drift, style_drift)
            
            # 6. Build metadata
            metadata = {
                "draft_count": len(draft_history),
                "tone_drift": tone_drift,
                "length_drift": length_drift,
                "style_drift": style_drift,
                "drift_threshold": persona_plan.get("drift_threshold", 0.3),
            }
            
            # 7. Create drift event
            drift_event = LICPersonaDriftEvent(
                archetype=persona_plan.get("archetype", "UNKNOWN"),
                drift_score=overall_drift,
                reason=drift_reason,
                metadata=metadata,
            )
            
            # 8. Record telemetry (best-effort)
            self._safe_record_telemetry(drift_event)
            
            return drift_event
            
        except Exception as e:
            logger.error(f"Drift computation failed: {e}")
            return LICPersonaDriftEvent(
                archetype=persona_plan.get("archetype", "UNKNOWN"),
                drift_score=1.0,  # Max drift on error
                reason=f"Drift computation error: {str(e)}",
                metadata={"error": str(e)},
            )
    
    def _analyze_tone_drift(self, persona_plan: Dict[str, Any], draft_history: List[str]) -> float:
        """Analyze tone keyword drift across drafts."""
        target_tone = persona_plan.get("tone_style", "neutral")
        archetype = persona_plan.get("archetype", "OTHER")
        
        # Get expected tone keywords based on persona
        expected_keywords = self._get_expected_tone_keywords(target_tone, archetype)
        
        if not expected_keywords:
            return 0.0
        
        # Analyze tone in each draft
        tone_scores = []
        for draft in draft_history:
            draft_lower = draft.lower()
            keyword_count = sum(1 for keyword in expected_keywords if keyword in draft_lower)
            total_words = len(draft.split())
            
            # Normalize tone score
            if total_words > 0:
                tone_score = keyword_count / total_words * 100  # Keywords per 100 words
            else:
                tone_score = 0.0
            
            tone_scores.append(tone_score)
        
        # Calculate drift as variance from initial tone
        if len(tone_scores) >= 2:
            initial_tone = tone_scores[0]
            latest_tone = tone_scores[-1]
            
            # Calculate percentage change
            if initial_tone > 0:
                tone_change = abs(latest_tone - initial_tone) / initial_tone
            else:
                tone_change = 0.0 if latest_tone == 0 else 1.0
            
            return min(tone_change, 1.0)
        
        return 0.0
    
    def _analyze_length_drift(self, draft_history: List[str]) -> float:
        """Analyze message length drift across drafts."""
        word_counts = [len(draft.split()) for draft in draft_history]
        
        if len(word_counts) < 2:
            return 0.0
        
        # Calculate length variance
        initial_length = word_counts[0]
        latest_length = word_counts[-1]
        
        if initial_length > 0:
            length_change = abs(latest_length - initial_length) / initial_length
        else:
            length_change = 1.0 if latest_length > 0 else 0.0
        
        # Cap at reasonable maximum
        return min(length_change, 1.0)
    
    def _analyze_style_variance(self, persona_plan: Dict[str, Any], draft_history: List[str]) -> float:
        """Analyze style variance across drafts."""
        target_detail = persona_plan.get("detail_level", "medium")
        target_risk = persona_plan.get("risk_tolerance", "medium")
        
        # Analyze detail level indicators
        detail_scores = []
        for draft in draft_history:
            detail_score = self._calculate_detail_score(draft)
            detail_scores.append(detail_score)
        
        # Analyze risk tolerance indicators
        risk_scores = []
        for draft in draft_history:
            risk_score = self._calculate_risk_score(draft)
            risk_scores.append(risk_score)
        
        # Calculate variance scores
        detail_variance = self._calculate_variance(detail_scores) if detail_scores else 0.0
        risk_variance = self._calculate_variance(risk_scores) if risk_scores else 0.0
        
        # Combine variances
        overall_variance = (detail_variance + risk_variance) / 2
        
        return min(overall_variance, 1.0)
    
    def _get_expected_tone_keywords(self, tone_style: str, archetype: str) -> List[str]:
        """Get expected tone keywords based on style and archetype."""
        keywords = []
        
        # Base keywords from tone style
        tone_lower = tone_style.lower()
        for style, style_keywords in self.tone_keywords.items():
            if style in tone_lower:
                keywords.extend(style_keywords)
        
        # Add archetype-specific keywords
        archetype_keywords = {
            "EXECUTIVE": ["strategic", "business", "leadership", "executive"],
            "SENIOR_TA": ["technical", "engineering", "implementation", "architecture"],
            "RECRUITER": ["team", "culture", "hiring", "recruitment"],
        }
        
        if archetype.upper() in archetype_keywords:
            keywords.extend(archetype_keywords[archetype.upper()])
        
        return list(set(keywords))
    
    def _calculate_detail_score(self, text: str) -> float:
        """Calculate detail level score for text."""
        detail_indicators = [
            "specifically", "detailed", "comprehensive", "thorough",
            "extensive", "in-depth", "meticulous", "precise"
        ]
        
        text_lower = text.lower()
        detail_count = sum(1 for indicator in detail_indicators if indicator in text_lower)
        word_count = len(text.split())
        
        if word_count > 0:
            return detail_count / word_count * 100
        return 0.0
    
    def _calculate_risk_score(self, text: str) -> float:
        """Calculate risk tolerance score for text."""
        conservative_indicators = [
            "carefully", "cautiously", "conservative", "traditional",
            "established", "proven", "reliable", "stable"
        ]
        
        aggressive_indicators = [
            "innovative", "breakthrough", "revolutionary", "disruptive",
            "cutting-edge", "pioneering", "groundbreaking", "bold"
        ]
        
        text_lower = text.lower()
        conservative_count = sum(1 for indicator in conservative_indicators if indicator in text_lower)
        aggressive_count = sum(1 for indicator in aggressive_indicators if indicator in text_lower)
        
        word_count = len(text.split())
        if word_count > 0:
            # Risk score: negative for conservative, positive for aggressive
            net_risk = (aggressive_count - conservative_count) / word_count * 100
            return max(-1.0, min(1.0, net_risk / 10))  # Normalize to [-1, 1]
        return 0.0
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of a list of values."""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        
        # Normalize variance (assuming reasonable range)
        return min(variance / 100, 1.0)
    
    def _compute_overall_drift(self, tone_drift: float, length_drift: float, style_drift: float) -> float:
        """Compute overall drift score from component drifts."""
        # Weight the components
        weights = {
            "tone": 0.4,
            "length": 0.3,
            "style": 0.3,
        }
        
        overall_drift = (
            tone_drift * weights["tone"] +
            length_drift * weights["length"] +
            style_drift * weights["style"]
        )
        
        return round(overall_drift, 3)
    
    def _determine_drift_reason(self, tone_drift: float, length_drift: float, style_drift: float) -> str:
        """Determine primary reason for drift detection."""
        drift_components = [
            ("tone", tone_drift),
            ("length", length_drift),
            ("style", style_drift),
        ]
        
        # Find the component with highest drift
        max_component = max(drift_components, key=lambda x: x[1])
        component_name, component_drift = max_component
        
        if component_drift < 0.1:
            return "Minimal drift detected"
        
        reasons = {
            "tone": f"Significant tone shift detected ({component_drift:.2f})",
            "length": f"Significant length change detected ({component_drift:.2f})",
            "style": f"Significant style variance detected ({component_drift:.2f})",
        }
        
        return reasons.get(component_name, f"Drift detected in {component_name}")
    
    def check_drift_threshold(self, drift_event: LICPersonaDriftEvent, persona_plan: Dict[str, Any]) -> bool:
        """Check if drift exceeds persona threshold.
        
        Args:
            drift_event: Drift event to check
            persona_plan: Original persona plan with threshold
            
        Returns:
            True if drift exceeds threshold, False otherwise
        """
        threshold = persona_plan.get("drift_threshold", 0.3)
        return drift_event.drift_score > threshold
    
    def _safe_record_telemetry(self, drift_event: LICPersonaDriftEvent) -> None:
        """Record telemetry event safely without breaking drift analysis."""
        if not self.telemetry_bus:
            return
        
        try:
            self.telemetry_bus.record_event(
                "lic_persona_drift_computed",
                layer="L3",
                payload={
                    "archetype": drift_event.archetype,
                    "drift_score": drift_event.drift_score,
                    "reason": drift_event.reason,
                    "metadata": drift_event.metadata,
                },
            )
        except Exception:
            # Telemetry failures should never break drift analysis
            logger.debug("Failed to record telemetry for LIC persona drift")
