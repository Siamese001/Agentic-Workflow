"""W3 Resurfacing Logic Tests

Integration tests for signal detection and trigger→wake mapping.
"""

import pytest
from datetime import datetime, timezone, timedelta
from pathlib import Path


class TestW3P1SignalTypes:
    """Test W3.P1: Signal type definitions."""
    
    def test_signal_type_enum_exists(self):
        """Verify SignalType enum with all expected values."""
        from apps_lic.signals.types import SignalType
        
        # Check hiring signals
        assert SignalType.HIRING_SURGE.value == "hiring_surge"
        assert SignalType.EXEC_ROLE_OPEN.value == "exec_role_open"
        assert SignalType.TEAM_EXPANSION.value == "team_expansion"
        
        # Check funding signals
        assert SignalType.FUNDING_ROUND.value == "funding_round"
        assert SignalType.IPO_ANNOUNCEMENT.value == "ipo_announcement"
        assert SignalType.ACQUISITION.value == "acquisition"
        
        # Check competitive signals
        assert SignalType.COMPETITOR_LAUNCH.value == "competitor_launch"
        assert SignalType.MARKET_SHIFT.value == "market_shift"
        assert SignalType.REGULATORY_CHANGE.value == "regulatory_change"
        
        # Check engagement signals
        assert SignalType.PROFILE_VIEW.value == "profile_view"
        assert SignalType.CONTENT_ENGAGEMENT.value == "content_engagement"
    
    def test_signal_strength_enum(self):
        """Verify SignalStrength enum values."""
        from apps_lic.signals.types import SignalStrength
        
        assert SignalStrength.STRONG.value == "strong"
        assert SignalStrength.MODERATE.value == "moderate"
        assert SignalStrength.WEAK.value == "weak"
    
    def test_signal_source_enum(self):
        """Verify SignalSource enum values."""
        from apps_lic.signals.types import SignalSource
        
        assert SignalSource.LINKEDIN.value == "linkedin"
        assert SignalSource.CRUNCHBASE.value == "crunchbase"
        assert SignalSource.RESEARCH.value == "research"
        assert SignalSource.MANUAL.value == "manual"
    
    def test_resurfacing_signal_creation(self):
        """Verify ResurfacingSignal dataclass creation."""
        from apps_lic.signals.types import (
            ResurfacingSignal, SignalType, SignalStrength, SignalSource
        )
        
        signal = ResurfacingSignal(
            signal_id="sig-001",
            signal_type=SignalType.FUNDING_ROUND,
            strength=SignalStrength.STRONG,
            source=SignalSource.CRUNCHBASE,
            detected_at=datetime.now(timezone.utc),
            company_id="acme-corp",
            recipient_id="john-doe",
            raw_text="Acme Corp raised $50M Series B",
            metadata={"amount": "$50M", "series": "B"},
        )
        
        assert signal.signal_id == "sig-001"
        assert signal.signal_type == SignalType.FUNDING_ROUND
        assert signal.strength == SignalStrength.STRONG
        assert signal.metadata["amount"] == "$50M"
    
    def test_signal_strength_to_confidence_mapping(self):
        """Verify strength maps to confidence correctly."""
        from apps_lic.signals.types import (
            ResurfacingSignal, SignalType, SignalStrength, SignalSource
        )
        
        strong = ResurfacingSignal(
            "s1", SignalType.FUNDING_ROUND, SignalStrength.STRONG,
            SignalSource.CRUNCHBASE, datetime.now(timezone.utc),
        )
        moderate = ResurfacingSignal(
            "s2", SignalType.FUNDING_ROUND, SignalStrength.MODERATE,
            SignalSource.CRUNCHBASE, datetime.now(timezone.utc),
        )
        weak = ResurfacingSignal(
            "s3", SignalType.FUNDING_ROUND, SignalStrength.WEAK,
            SignalSource.CRUNCHBASE, datetime.now(timezone.utc),
        )
        
        assert strong._strength_to_confidence() == 0.9
        assert moderate._strength_to_confidence() == 0.7
        assert weak._strength_to_confidence() == 0.4
    
    def test_signal_should_boost_cadence(self):
        """Verify cadence boost logic."""
        from apps_lic.signals.types import (
            ResurfacingSignal, SignalType, SignalStrength, SignalSource
        )
        
        # Strong funding should boost
        funding = ResurfacingSignal(
            "s1", SignalType.FUNDING_ROUND, SignalStrength.STRONG,
            SignalSource.CRUNCHBASE, datetime.now(timezone.utc),
        )
        assert funding.should_boost_cadence() is True
        
        # Weak funding should not boost
        weak_funding = ResurfacingSignal(
            "s2", SignalType.FUNDING_ROUND, SignalStrength.WEAK,
            SignalSource.CRUNCHBASE, datetime.now(timezone.utc),
        )
        assert weak_funding.should_boost_cadence() is False
        
        # Profile view should not boost even if strong
        profile = ResurfacingSignal(
            "s3", SignalType.PROFILE_VIEW, SignalStrength.STRONG,
            SignalSource.LINKEDIN, datetime.now(timezone.utc),
        )
        assert profile.should_boost_cadence() is False
    
    def test_signal_to_wake_trigger_conversion(self):
        """Verify signal converts to wake trigger format."""
        from apps_lic.signals.types import (
            ResurfacingSignal, SignalType, SignalStrength, SignalSource
        )
        
        signal = ResurfacingSignal(
            "s1", SignalType.EXEC_ROLE_OPEN, SignalStrength.MODERATE,
            SignalSource.LINKEDIN, datetime.now(timezone.utc),
            metadata={"role": "CTO"},
        )
        
        trigger = signal.to_wake_trigger()
        
        assert trigger["trigger_signal"] == "exec_role_open"
        assert trigger["trigger_confidence"] == 0.7
        assert trigger["trigger_source"] == "linkedin"
        assert trigger["trigger_metadata"]["role"] == "CTO"
    
    def test_signal_detection_result(self):
        """Verify SignalDetectionResult structure."""
        from apps_lic.signals.types import (
            SignalDetectionResult, ResurfacingSignal,
            SignalType, SignalStrength, SignalSource
        )
        
        signal = ResurfacingSignal(
            "s1", SignalType.HIRING_SURGE, SignalStrength.STRONG,
            SignalSource.CRUNCHBASE, datetime.now(timezone.utc),
        )
        
        result = SignalDetectionResult(
            target_id="acme-corp",
            signals=[signal],
            sources_checked=[SignalSource.CRUNCHBASE, SignalSource.RESEARCH],
        )
        
        assert result.target_id == "acme-corp"
        assert len(result.signals) == 1
        assert result.has_strong_signals is True
        assert result.strongest_signal.signal_type == SignalType.HIRING_SURGE


class TestW3P1SignalDetector:
    """Test W3.P1: Signal detection integration."""
    
    def test_signal_detector_creation(self):
        """Verify SignalDetector can be instantiated."""
        from apps_lic.signals.detector import SignalDetector, SignalDetectorConfig
        from apps_lic.signals.types import SignalSource
        
        config = SignalDetectorConfig(
            enabled_sources=[SignalSource.RESEARCH],
            min_strength=SignalStrength.MODERATE,
        )
        detector = SignalDetector(config)
        
        assert detector is not None
        assert detector.get_config().min_strength == SignalStrength.MODERATE
    
    def test_signal_detector_default_config(self):
        """Verify default detector configuration."""
        from apps_lic.signals.detector import SignalDetector
        
        detector = SignalDetector()
        config = detector.get_config()
        
        assert len(config.enabled_sources) >= 1
        assert config.max_signals_per_check <= 10
    
    def test_signal_detection_returns_result(self):
        """Verify detect_signals returns SignalDetectionResult."""
        from apps_lic.signals.detector import SignalDetector
        from apps_lic.signals.types import SignalDetectionResult
        
        detector = SignalDetector()
        result = detector.detect_signals(company_id="test-company")
        
        assert isinstance(result, SignalDetectionResult)
        assert result.target_id == "test-company"
    
    def test_signal_detection_respects_resurfacing_enabled(self):
        """Verify detector returns empty when RESURFACING_ENABLED not set."""
        from apps_lic.signals.detector import SignalDetector
        
        detector = SignalDetector()
        result = detector.detect_signals(company_id="test-company")
        
        # Should return empty/error when env var not set
        assert result.error is not None or len(result.signals) == 0


class TestW3P2TriggerWakeMapper:
    """Test W3.P2: Trigger→Wake mapping."""
    
    def test_trigger_wake_mapper_creation(self):
        """Verify TriggerWakeMapper can be instantiated."""
        from apps_lic.signals.trigger_wake_mapper import TriggerWakeMapper
        
        mapper = TriggerWakeMapper()
        assert mapper is not None
    
    def test_funding_signal_maps_to_wake(self):
        """Verify strong funding signal triggers wake."""
        from apps_lic.signals.trigger_wake_mapper import TriggerWakeMapper
        from apps_lic.signals.types import (
            ResurfacingSignal, SignalType, SignalStrength, SignalSource
        )
        
        mapper = TriggerWakeMapper()
        
        signal = ResurfacingSignal(
            "s1", SignalType.FUNDING_ROUND, SignalStrength.STRONG,
            SignalSource.CRUNCHBASE, datetime.now(timezone.utc),
        )
        
        decision = mapper.map_signal_to_wake(
            signal=signal,
            touch_sequence=2,
        )
        
        assert decision.should_wake is True
        assert decision.wake_at is not None
        assert decision.priority <= 2  # High priority
        assert decision.cadence_boost_hours >= 48  # Strong funding = 48h+ boost
    
    def test_weak_signal_does_not_wake(self):
        """Verify weak signal below confidence threshold."""
        from apps_lic.signals.trigger_wake_mapper import TriggerWakeMapper
        from apps_lic.signals.types import (
            ResurfacingSignal, SignalType, SignalStrength, SignalSource
        )
        
        mapper = TriggerWakeMapper()
        
        signal = ResurfacingSignal(
            "s1", SignalType.CONTENT_ENGAGEMENT, SignalStrength.WEAK,
            SignalSource.LINKEDIN, datetime.now(timezone.utc),
        )
        
        decision = mapper.map_signal_to_wake(
            signal=signal,
            touch_sequence=2,
        )
        
        # Weak signals (0.4 confidence) are below MIN_WAKE_CONFIDENCE (0.5)
        assert decision.should_wake is False
    
    def test_signal_priority_mapping(self):
        """Verify different signal types have appropriate priorities."""
        from apps_lic.signals.trigger_wake_mapper import TriggerWakeMapper
        from apps_lic.signals.types import (
            ResurfacingSignal, SignalType, SignalStrength, SignalSource
        )
        
        mapper = TriggerWakeMapper()
        
        # Funding should be higher priority than hiring
        funding = ResurfacingSignal(
            "s1", SignalType.FUNDING_ROUND, SignalStrength.STRONG,
            SignalSource.CRUNCHBASE, datetime.now(timezone.utc),
        )
        hiring = ResurfacingSignal(
            "s2", SignalType.HIRING_SURGE, SignalStrength.STRONG,
            SignalSource.CRUNCHBASE, datetime.now(timezone.utc),
        )
        
        funding_decision = mapper.map_signal_to_wake(funding, touch_sequence=2)
        hiring_decision = mapper.map_signal_to_wake(hiring, touch_sequence=2)
        
        assert funding_decision.priority < hiring_decision.priority
    
    def test_cadence_boost_calculation(self):
        """Verify cadence boost calculation."""
        from apps_lic.signals.trigger_wake_mapper import TriggerWakeMapper
        from apps_lic.signals.types import (
            ResurfacingSignal, SignalType, SignalStrength, SignalSource
        )
        
        mapper = TriggerWakeMapper()
        
        signal = ResurfacingSignal(
            "s1", SignalType.EXEC_ROLE_OPEN, SignalStrength.STRONG,
            SignalSource.LINKEDIN, datetime.now(timezone.utc),
        )
        
        boosted = mapper.calculate_boosted_cadence(7, signal)  # 7 days base
        
        # Strong exec role = 24h base + 12h bonus = 36h = 1.5 days
        # 7 - 1.5 = 5.5 → rounded to 5 or 6
        assert boosted < 7
        assert boosted >= 5
    
    def test_select_best_signal_prioritizes_correctly(self):
        """Verify best signal selection logic."""
        from apps_lic.signals.trigger_wake_mapper import TriggerWakeMapper
        from apps_lic.signals.types import (
            ResurfacingSignal, SignalType, SignalStrength, SignalSource
        )
        
        mapper = TriggerWakeMapper()
        
        signals = [
            ResurfacingSignal("s1", SignalType.HIRING_SURGE, SignalStrength.MODERATE,
                           SignalSource.CRUNCHBASE, datetime.now(timezone.utc)),
            ResurfacingSignal("s2", SignalType.FUNDING_ROUND, SignalStrength.STRONG,
                           SignalSource.CRUNCHBASE, datetime.now(timezone.utc) - timedelta(hours=1)),
            ResurfacingSignal("s3", SignalType.PROFILE_VIEW, SignalStrength.STRONG,
                           SignalSource.LINKEDIN, datetime.now(timezone.utc)),
        ]
        
        best = mapper.select_best_signal_for_wake(signals)
        
        # Funding has highest priority (1) despite being older
        assert best.signal_type == SignalType.FUNDING_ROUND
    
    def test_create_schedule_request(self):
        """Verify schedule request creation from signal."""
        from apps_lic.signals.trigger_wake_mapper import TriggerWakeMapper
        from apps_lic.signals.types import (
            ResurfacingSignal, SignalType, SignalStrength, SignalSource
        )
        from apps_lic.coordination.touch_scheduler import ScheduleTouchRequest
        
        mapper = TriggerWakeMapper()
        
        signal = ResurfacingSignal(
            "s1", SignalType.FUNDING_ROUND, SignalStrength.STRONG,
            SignalSource.CRUNCHBASE, datetime.now(timezone.utc),
        )
        
        request = mapper.create_schedule_request(
            signal=signal,
            touch_id="touch-001",
            recipient_hash="hash123",
            campaign_id="camp-001",
            touch_sequence=2,
        )
        
        assert isinstance(request, ScheduleTouchRequest)
        assert request.touch_id == "touch-001"
        assert request.trigger_signal == "funding_round"
        assert request.trigger_confidence >= 0.9


class TestW3Integration:
    """Test W3 End-to-End: Detection → Mapping → Wake."""
    
    def test_full_signal_to_wake_flow(self):
        """Simulate complete signal detection to wake scheduling."""
        from apps_lic.signals.detector import SignalDetector
        from apps_lic.signals.trigger_wake_mapper import TriggerWakeMapper
        from apps_lic.signals.types import (
            ResurfacingSignal, SignalType, SignalStrength, SignalSource
        )
        
        # Step 1: Detect signals (simulated - RESURFACING_ENABLED may be off)
        detector = SignalDetector()
        
        # Step 2: Create a signal manually for testing
        signal = ResurfacingSignal(
            signal_id="sig-funding-001",
            signal_type=SignalType.FUNDING_ROUND,
            strength=SignalStrength.STRONG,
            source=SignalSource.CRUNCHBASE,
            detected_at=datetime.now(timezone.utc),
            company_id="acme-corp",
            raw_text="Acme Corp raised $50M Series B led by Andreessen Horowitz",
            metadata={"amount": "$50M", "series": "B"},
        )
        
        # Step 3: Map to wake decision
        mapper = TriggerWakeMapper()
        decision = mapper.map_signal_to_wake(
            signal=signal,
            prior_touch_sent_at=datetime.now(timezone.utc) - timedelta(days=5),
            touch_sequence=2,
            standard_cadence_days=5,
        )
        
        # Step 4: Verify wake scheduling
        assert decision.should_wake is True
        assert decision.wake_at is not None
        # Should be scheduled sooner than standard 5 days due to boost
        expected_wake = datetime.now(timezone.utc) + timedelta(days=3)
        assert decision.wake_at < expected_wake + timedelta(days=2)
    
    def test_multiple_signals_best_selected(self):
        """Verify best signal selected when multiple detected."""
        from apps_lic.signals.trigger_wake_mapper import TriggerWakeMapper
        from apps_lic.signals.types import (
            ResurfacingSignal, SignalType, SignalStrength, SignalSource
        )
        
        mapper = TriggerWakeMapper()
        
        signals = [
            ResurfacingSignal("s1", SignalType.PROFILE_VIEW, SignalStrength.MODERATE,
                           SignalSource.LINKEDIN, datetime.now(timezone.utc)),
            ResurfacingSignal("s2", SignalType.HIRING_SURGE, SignalStrength.STRONG,
                           SignalSource.CRUNCHBASE, datetime.now(timezone.utc)),
            ResurfacingSignal("s3", SignalType.FUNDING_ROUND, SignalStrength.STRONG,
                           SignalSource.CRUNCHBASE, datetime.now(timezone.utc) - timedelta(minutes=5)),
        ]
        
        best = mapper.select_best_signal_for_wake(signals)
        
        # Funding wins due to higher priority (1 vs 4)
        assert best.signal_type == SignalType.FUNDING_ROUND


class TestW3SpineWiring:
    """Test W3 components in spine wiring."""
    
    def test_spine_wiring_has_w3_components(self):
        """Verify spine wiring includes W3 verifiers."""
        wiring_path = Path("apps_lic/spine_wiring.py")
        content = wiring_path.read_text()
        
        assert "signal_types" in content
        assert "signal_detector" in content
        assert "trigger_wake_mapper" in content
    
    def test_signal_types_verifier_exists(self):
        """Verify _verify_signal_types method exists."""
        from apps_lic.spine_wiring import SpineWiringVerifier
        
        verifier = SpineWiringVerifier()
        assert hasattr(verifier, '_verify_signal_types')
    
    def test_signal_detector_verifier_exists(self):
        """Verify _verify_signal_detector method exists."""
        from apps_lic.spine_wiring import SpineWiringVerifier
        
        verifier = SpineWiringVerifier()
        assert hasattr(verifier, '_verify_signal_detector')
    
    def test_trigger_wake_mapper_verifier_exists(self):
        """Verify _verify_trigger_wake_mapper method exists."""
        from apps_lic.spine_wiring import SpineWiringVerifier
        
        verifier = SpineWiringVerifier()
        assert hasattr(verifier, '_verify_trigger_wake_mapper')
