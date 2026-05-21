"""apps_lic.signals.detector — W3.P1

Signal Detection Integration

Integrates with existing signal sources to detect resurfacing opportunities:
- Company trigger extractor (from research)
- Resurfacing detector (from prior touches)
- External signal sources (LinkedIn, Crunchbase)

Provides unified signal detection interface for W3 resurfacing logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Callable
import os

from apps_lic.signals.types import (
    SignalType,
    SignalStrength,
    SignalSource,
    ResurfacingSignal,
    SignalDetectionResult,
    sort_signals_by_priority,
)


@dataclass
class SignalDetectorConfig:
    """Configuration for signal detection.
    
    Fields
    ------
    enabled_sources : list[SignalSource]
        Which sources to check
    min_strength : SignalStrength
        Minimum signal strength to report
    max_signals_per_check : int
        Maximum signals to return
    check_timeout_seconds : int
        Timeout for external source checks
    """
    
    enabled_sources: list[SignalSource] = field(default_factory=lambda: [
        SignalSource.RESEARCH,
        SignalSource.CRUNCHBASE,
    ])
    min_strength: SignalStrength = SignalStrength.WEAK
    max_signals_per_check: int = 5
    check_timeout_seconds: int = 30


class SignalDetector:
    """Detects resurfacing signals from multiple sources.
    
    Integrates with existing infrastructure:
    - Uses engines.company_trigger_extractor for company triggers
    - Uses engines.resurfacing_detector for touch-based signals
    - Can query external APIs (Crunchbase, LinkedIn) when configured
    
    Decision-only invariants (W3.P1):
    - No durable state reads. All context passed via parameters.
    - No durable writes.
    - External API calls only when explicitly enabled.
    - Config-gated: disabled when RESURFACING_ENABLED env var absent.
    """
    
    def __init__(self, config: Optional[SignalDetectorConfig] = None) -> None:
        self._config = config or SignalDetectorConfig()
        self._source_handlers: dict[SignalSource, Callable] = {}
        self._register_default_handlers()
    
    def _register_default_handlers(self) -> None:
        """Register default handlers for each signal source."""
        self._source_handlers[SignalSource.RESEARCH] = self._check_research_signals
        self._source_handlers[SignalSource.CRUNCHBASE] = self._check_crunchbase_signals
        self._source_handlers[SignalSource.LINKEDIN] = self._check_linkedin_signals
        self._source_handlers[SignalSource.MANUAL] = self._check_manual_signals
    
    def detect_signals(
        self,
        company_id: Optional[str] = None,
        recipient_id: Optional[str] = None,
        days_since_last_contact: Optional[float] = None,
        prior_response_received: bool = False,
        relationship_distance: str = "cold",
    ) -> SignalDetectionResult:
        """Detect signals for resurfacing opportunity.
        
        Parameters
        ----------
        company_id : Optional[str]
            Company to check for signals
        recipient_id : Optional[str]
            Specific recipient (if known)
        days_since_last_contact : Optional[float]
            Days since last touch (for resurfacing logic)
        prior_response_received : bool
            Whether recipient previously responded
        relationship_distance : str
            "cold" | "warm" | "known" | "referral"
        
        Returns
        -------
        SignalDetectionResult
            Detected signals with metadata
        """
        if not os.environ.get("RESURFACING_ENABLED"):
            return SignalDetectionResult(
                target_id=company_id or recipient_id or "unknown",
                signals=[],
                sources_checked=[],
                error="RESURFACING_ENABLED not set",
            )
        
        all_signals: list[ResurfacingSignal] = []
        sources_checked: list[SignalSource] = []
        
        # Check each enabled source
        for source in self._config.enabled_sources:
            handler = self._source_handlers.get(source)
            if handler:
                try:
                    signals = handler(
                        company_id=company_id,
                        recipient_id=recipient_id,
                    )
                    all_signals.extend(signals)
                    sources_checked.append(source)
                except Exception:  # guardian: allow-silent-swallow -- P2 burndown: fail-soft optional boundary  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
                    # Fail-soft: skip failed source, continue with others
                    pass
        
        # Also check internal resurfacing detector
        internal_signals = self._check_internal_resurfacing(
            days_since_last_contact=days_since_last_contact,
            prior_response_received=prior_response_received,
            relationship_distance=relationship_distance,
        )
        all_signals.extend(internal_signals)
        
        # Filter by minimum strength
        strength_order = {
            SignalStrength.STRONG: 3,
            SignalStrength.MODERATE: 2,
            SignalStrength.WEAK: 1,
        }
        min_strength_level = strength_order.get(self._config.min_strength, 1)
        
        filtered = [
            s for s in all_signals
            if strength_order.get(s.strength, 0) >= min_strength_level
        ]
        
        # Sort by priority and take top N
        sorted_signals = sort_signals_by_priority(filtered)
        final_signals = sorted_signals[:self._config.max_signals_per_check]
        
        return SignalDetectionResult(
            target_id=company_id or recipient_id or "unknown",
            signals=final_signals,
            sources_checked=sources_checked,
        )
    
    def _check_research_signals(
        self,
        company_id: Optional[str] = None,
        recipient_id: Optional[str] = None,
    ) -> list[ResurfacingSignal]:
        """Check internal research for company triggers."""
        signals = []
        
        try:
            from apps_lic.engines.company_trigger_extractor import (
                CompanyTriggerExtractor,
                CompanyTrigger,
            )
            
            if company_id:
                extractor = CompanyTriggerExtractor()
                triggers = extractor.extract_triggers(company_id=company_id)
                
                for trigger in triggers:
                    signal = self._company_trigger_to_signal(trigger)
                    if signal:
                        signals.append(signal)
        except Exception:  # guardian: allow-silent-swallow -- P2 burndown: fail-soft optional boundary  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
            # Fail-soft: research source unavailable
            pass
        
        return signals
    
    def _company_trigger_to_signal(
        self,
        trigger: Any,
    ) -> Optional[ResurfacingSignal]:
        """Convert CompanyTrigger to ResurfacingSignal."""
        # Map trigger types to signal types
        type_mapping = {
            "funding_round": SignalType.FUNDING_ROUND,
            "leadership": SignalType.EXEC_ROLE_OPEN,
            "product_launch": SignalType.COMPETITOR_LAUNCH,
            "acquisition": SignalType.ACQUISITION,
            "expansion": SignalType.TEAM_EXPANSION,
            "earnings": SignalType.MARKET_SHIFT,
        }
        
        signal_type = type_mapping.get(trigger.trigger_type)
        if not signal_type:
            return None
        
        # Map strength
        strength_mapping = {
            "strong": SignalStrength.STRONG,
            "moderate": SignalStrength.MODERATE,
            "weak": SignalStrength.WEAK,
        }
        strength = strength_mapping.get(trigger.strength, SignalStrength.WEAK)
        
        return ResurfacingSignal(
            signal_id=f"research:{trigger.source_id}",
            signal_type=signal_type,
            strength=strength,
            source=SignalSource.RESEARCH,
            detected_at=datetime.now(timezone.utc),
            raw_text=trigger.raw_excerpt[:500],
            metadata={
                "source_id": trigger.source_id,
                "matched_keyword": trigger.matched_keyword,
            },
        )
    
    def _check_crunchbase_signals(
        self,
        company_id: Optional[str] = None,
        recipient_id: Optional[str] = None,
    ) -> list[ResurfacingSignal]:
        """Check Crunchbase for funding/hiring signals."""
        # Placeholder: Crunchbase integration would go here
        # For now, return empty (will be populated when API integrated)
        return []
    
    def _check_linkedin_signals(
        self,
        company_id: Optional[str] = None,
        recipient_id: Optional[str] = None,
    ) -> list[ResurfacingSignal]:
        """Check LinkedIn for engagement signals."""
        signals = []
        
        # Check for profile views if recipient known
        if recipient_id:
            # Placeholder: LinkedIn API integration
            pass
        
        return signals
    
    def _check_manual_signals(
        self,
        company_id: Optional[str] = None,
        recipient_id: Optional[str] = None,
    ) -> list[ResurfacingSignal]:
        """Check for manually entered signals."""
        # Placeholder: Manual signal ingestion
        return []
    
    def _check_internal_resurfacing(
        self,
        days_since_last_contact: Optional[float] = None,
        prior_response_received: bool = False,
        relationship_distance: str = "cold",
    ) -> list[ResurfacingSignal]:
        """Check internal resurfacing detector for touch-based signals."""
        signals = []
        
        try:
            from apps_lic.engines.resurfacing_detector import (
                ResurfacingDetector,
                ResurfacingDecision,
            )
            
            detector = ResurfacingDetector()
            decision = detector.detect(
                days_since_last_contact=days_since_last_contact,
                prior_response_received=prior_response_received,
                relationship_distance=relationship_distance,
                trigger_event_detected=False,  # We'll set this based on other signals
            )
            
            # If resurfacing recommended, create a signal
            if decision.recommendation in ("recommended", "conditional"):
                signal_type = (
                    SignalType.PROFILE_VIEW 
                    if prior_response_received 
                    else SignalType.CONTENT_ENGAGEMENT
                )
                
                signal = ResurfacingSignal(
                    signal_id=f"internal:resurfacing:{datetime.now(timezone.utc).isoformat()}",
                    signal_type=signal_type,
                    strength=SignalStrength.MODERATE,
                    source=SignalSource.RESEARCH,
                    detected_at=datetime.now(timezone.utc),
                    raw_text=f"Resurfacing recommended: {decision.reason}",
                    metadata={
                        "recommendation": decision.recommendation,
                        "days_since_last_contact": str(days_since_last_contact),
                    },
                )
                signals.append(signal)
        
        except Exception:  # guardian: allow-silent-swallow -- P2 burndown: fail-soft optional boundary  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
            # Fail-soft: detector unavailable
            pass
        
        return signals
    
    def get_config(self) -> SignalDetectorConfig:
        """Get current detector configuration."""
        return self._config


__all__ = [
    "SignalDetector",
    "SignalDetectorConfig",
]
