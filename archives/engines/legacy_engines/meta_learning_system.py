"""
Simplified Meta-Learning System for 10_12
LT-02: Meta-Learning System (10_12-Native Implementation)

Lightweight meta-learning system that captures core value of
continuous improvement without over-engineered complexity.
Focuses on feedback collection, pattern recognition, and
adaptive parameter tuning.
"""

import logging
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import hashlib
import pickle

logger = logging.getLogger(__name__)


class FeedbackType(Enum):
    """Types of feedback for meta-learning"""
    QUALITY = "quality"
    RELEVANCE = "relevance"
    COMPLETENESS = "completeness"
    USER_SATISFACTION = "user_satisfaction"
    PERFORMANCE = "performance"


class LearningMode(Enum):
    """Meta-learning modes"""
    PASSIVE = "passive"  # Just collect feedback
    ACTIVE = "active"    # Learn and adapt
    PREDICTIVE = "predictive"  # Predict and prevent issues


@dataclass
class FeedbackSignal:
    """Individual feedback signal"""
    task_id: str
    feedback_type: FeedbackType
    score: float  # 0.0 to 1.0
    context: Dict[str, Any]
    timestamp: float
    source: str  # user, system, automated
    metadata: Dict[str, Any]


@dataclass
class LearningPattern:
    """Detected learning pattern"""
    pattern_id: str
    pattern_type: str
    confidence: float
    frequency: int
    last_seen: float
    impact_score: float
    description: str


@dataclass
class AdaptationResult:
    """Result of learning adaptation"""
    adaptation_type: str
    parameters_changed: Dict[str, Any]
    expected_improvement: float
    confidence: float
    applied_at: float


class FeedbackCollector:
    """
    Feedback Collection and Storage
    
    Collects various types of feedback for meta-learning
    without complex infrastructure.
    """
    
    def __init__(self, max_signals: int = 10000):
        self.max_signals = max_signals
        self.feedback_signals: deque = deque(maxlen=max_signals)
        self.feedback_by_type: Dict[FeedbackType, deque] = {
            ft: deque(maxlen=max_signals // 5) for ft in FeedbackType
        }
    
    def add_feedback(
        self,
        task_id: str,
        feedback_type: FeedbackType,
        score: float,
        context: Dict[str, Any] = None,
        source: str = "system",
        metadata: Dict[str, Any] = None
    ) -> None:
        """
        Add feedback signal to the collection.
        
        Args:
            task_id: Unique identifier for the task
            feedback_type: Type of feedback
            score: Feedback score (0.0 to 1.0)
            context: Context information
            source: Feedback source
            metadata: Additional metadata
        """
        if not 0.0 <= score <= 1.0:
            raise ValueError("Feedback score must be between 0.0 and 1.0")
        
        signal = FeedbackSignal(
            task_id=task_id,
            feedback_type=feedback_type,
            score=score,
            context=context or {},
            timestamp=time.time(),
            source=source,
            metadata=metadata or {}
        )
        
        self.feedback_signals.append(signal)
        self.feedback_by_type[feedback_type].append(signal)
        
        logger.debug(f"Added {feedback_type.value} feedback: {score:.3f} for task {task_id}")
    
    def get_recent_feedback(
        self,
        feedback_type: Optional[FeedbackType] = None,
        hours: int = 24,
        limit: int = 100
    ) -> List[FeedbackSignal]:
        """
        Get recent feedback signals.
        
        Args:
            feedback_type: Optional type filter
            hours: Time window in hours
            limit: Maximum number of signals
            
        Returns:
            List of feedback signals
        """
        cutoff_time = time.time() - (hours * 3600)
        
        if feedback_type:
            signals = self.feedback_by_type[feedback_type]
        else:
            signals = self.feedback_signals
        
        recent_signals = [
            s for s in signals 
            if s.timestamp >= cutoff_time
        ]
        
        return recent_signals[-limit:] if limit > 0 else recent_signals
    
    def get_feedback_stats(self, feedback_type: Optional[FeedbackType] = None) -> Dict[str, float]:
        """Get statistics for feedback signals."""
        signals = self.get_recent_feedback(feedback_type)
        
        if not signals:
            return {}
        
        scores = [s.score for s in signals]
        
        return {
            'count': len(signals),
            'avg_score': sum(scores) / len(scores),
            'min_score': min(scores),
            'max_score': max(scores),
            'latest_timestamp': max(s.timestamp for s in signals)
        }


class PatternRecognizer:
    """
    Simple Pattern Recognition
    
    Identifies patterns in feedback without complex ML.
    Uses statistical analysis and heuristics.
    """
    
    def __init__(self, min_pattern_confidence: float = 0.7):
        self.min_confidence = min_pattern_confidence
        self.pattern_history: Dict[str, LearningPattern] = {}
    
    def recognize_patterns(self, feedback_signals: List[FeedbackSignal]) -> List[LearningPattern]:
        """
        Recognize patterns in feedback signals.
        
        Args:
            feedback_signals: List of feedback signals to analyze
            
        Returns:
            List of recognized patterns
        """
        patterns = []
        
        # Pattern 1: Quality degradation over time
        quality_pattern = self._detect_quality_trend(feedback_signals)
        if quality_pattern:
            patterns.append(quality_pattern)
        
        # Pattern 2: Context-specific performance
        context_pattern = self._detect_context_patterns(feedback_signals)
        if context_pattern:
            patterns.append(context_pattern)
        
        # Pattern 3: Source bias
        source_pattern = self._detect_source_bias(feedback_signals)
        if source_pattern:
            patterns.append(source_pattern)
        
        # Pattern 4: Temporal patterns
        temporal_pattern = self._detect_temporal_patterns(feedback_signals)
        if temporal_pattern:
            patterns.append(temporal_pattern)
        
        # Update pattern history
        for pattern in patterns:
            self.pattern_history[pattern.pattern_id] = pattern
        
        logger.info(f"Recognized {len(patterns)} patterns from {len(feedback_signals)} feedback signals")
        
        return patterns
    
    def _detect_quality_trend(self, signals: List[FeedbackSignal]) -> Optional[LearningPattern]:
        """Detect quality degradation or improvement trends."""
        quality_signals = [s for s in signals if s.feedback_type == FeedbackType.QUALITY]
        
        if len(quality_signals) < 5:
            return None
        
        # Sort by timestamp
        quality_signals.sort(key=lambda x: x.timestamp)
        
        # Calculate trend
        recent_scores = [s.score for s in quality_signals[-3:]]
        older_scores = [s.score for s in quality_signals[:-3]]
        
        if not older_scores:
            return None
        
        recent_avg = sum(recent_scores) / len(recent_scores)
        older_avg = sum(older_scores) / len(older_scores)
        
        trend_diff = recent_avg - older_avg
        
        if abs(trend_diff) < 0.1:  # No significant trend
            return None
        
        trend_type = "improvement" if trend_diff > 0 else "degradation"
        confidence = min(abs(trend_diff) * 2, 1.0)
        
        return LearningPattern(
            pattern_id=f"quality_trend_{trend_type}",
            pattern_type="quality_trend",
            confidence=confidence,
            frequency=len(quality_signals),
            last_seen=quality_signals[-1].timestamp,
            impact_score=abs(trend_diff),
            description=f"Quality {trend_type} detected: {trend_diff:.3f}"
        )
    
    def _detect_context_patterns(self, signals: List[FeedbackSignal]) -> Optional[LearningPattern]:
        """Detect context-specific performance patterns."""
        context_scores = defaultdict(list)
        
        for signal in signals:
            # Extract key context features
            context_key = signal.context.get('domain', 'unknown')
            context_scores[context_key].append(signal.score)
        
        # Find domains with consistently low/high performance
        significant_patterns = []
        
        for context, scores in context_scores.items():
            if len(scores) < 3:
                continue
            
            avg_score = sum(scores) / len(scores)
            
            if avg_score < 0.4:  # Poor performance
                significant_patterns.append((context, avg_score, "poor"))
            elif avg_score > 0.8:  # Excellent performance
                significant_patterns.append((context, avg_score, "excellent"))
        
        if not significant_patterns:
            return None
        
        # Return the most significant pattern
        context, score, perf_type = max(significant_patterns, key=lambda x: abs(x[1] - 0.5))
        
        return LearningPattern(
            pattern_id=f"context_performance_{context}_{perf_type}",
            pattern_type="context_performance",
            confidence=0.8,
            frequency=len(context_scores[context]),
            last_seen=time.time(),
            impact_score=abs(score - 0.5),
            description=f"{context.title()} domain showing {perf_type} performance: {score:.3f}"
        )
    
    def _detect_source_bias(self, signals: List[FeedbackSignal]) -> Optional[LearningPattern]:
        """Detect bias in feedback sources."""
        source_scores = defaultdict(list)
        
        for signal in signals:
            source_scores[signal.source].append(signal.score)
        
        # Check for significant differences between sources
        if len(source_scores) < 2:
            return None
        
        source_avgs = {source: sum(scores) / len(scores) for source, scores in source_scores.items()}
        max_diff = max(source_avgs.values()) - min(source_avgs.values())
        
        if max_diff < 0.3:  # No significant bias
            return None
        
        return LearningPattern(
            pattern_id="source_bias_detected",
            pattern_type="source_bias",
            confidence=0.7,
            frequency=len(signals),
            last_seen=max(s.timestamp for s in signals),
            impact_score=max_diff,
            description=f"Source bias detected with {max_diff:.3f} score difference"
        )
    
    def _detect_temporal_patterns(self, signals: List[FeedbackSignal]) -> Optional[LearningPattern]:
        """Detect temporal patterns in feedback."""
        if len(signals) < 10:
            return None
        
        # Group by hour of day
        hourly_scores = defaultdict(list)
        
        for signal in signals:
            hour = time.localtime(signal.timestamp).tm_hour
            hourly_scores[hour].append(signal.score)
        
        # Find hours with significant performance differences
        hourly_avgs = {hour: sum(scores) / len(scores) for hour, scores in hourly_scores.items()}
        
        if len(hourly_avgs) < 3:
            return None
        
        max_diff = max(hourly_avgs.values()) - min(hourly_avgs.values())
        
        if max_diff < 0.2:  # No significant temporal pattern
            return None
        
        best_hour = max(hourly_avgs, key=hourly_avgs.get)
        worst_hour = min(hourly_avgs, key=hourly_avgs.get)
        
        return LearningPattern(
            pattern_id="temporal_performance_pattern",
            pattern_type="temporal_pattern",
            confidence=0.6,
            frequency=len(signals),
            last_seen=time.time(),
            impact_score=max_diff,
            description=f"Performance varies by time: best at {best_hour}:00, worst at {worst_hour}:00"
        )


class AdaptiveParameterTuner:
    """
    Simple Adaptive Parameter Tuning
    
    Adjusts system parameters based on learning patterns
    without complex optimization algorithms.
    """
    
    def __init__(self):
        self.parameter_history: Dict[str, List[float]] = defaultdict(list)
        self.adaptation_log: List[AdaptationResult] = []
        
        # Default parameter ranges
        self.parameter_ranges = {
            'semantic_threshold': (0.5, 0.9),
            'retrieval_top_k': (5, 20),
            'tone_formality': (0.3, 1.0),
            'cache_freshness_hours': (12, 72),
            'bm25_weight': (0.3, 0.7)
        }
    
    def adapt_parameters(self, patterns: List[LearningPattern]) -> List[AdaptationResult]:
        """
        Adapt parameters based on recognized patterns.
        
        Args:
            patterns: List of learning patterns to address
            
        Returns:
            List of adaptation results
        """
        adaptations = []
        
        for pattern in patterns:
            if pattern.confidence < self.min_confidence:
                continue
            
            adaptation = self._create_adaptation_for_pattern(pattern)
            if adaptation:
                adaptations.append(adaptation)
                self.adaptation_log.append(adaptation)
        
        logger.info(f"Created {len(adaptations)} parameter adaptations")
        
        return adaptations
    
    def _create_adaptation_for_pattern(self, pattern: LearningPattern) -> Optional[AdaptationResult]:
        """Create parameter adaptation for a specific pattern."""
        if pattern.pattern_type == "quality_trend":
            return self._adapt_for_quality_trend(pattern)
        elif pattern.pattern_type == "context_performance":
            return self._adapt_for_context_performance(pattern)
        elif pattern.pattern_type == "temporal_pattern":
            return self._adapt_for_temporal_pattern(pattern)
        
        return None
    
    def _adapt_for_quality_trend(self, pattern: LearningPattern) -> AdaptationResult:
        """Adapt parameters for quality trends."""
        if "degradation" in pattern.pattern_id:
            # Quality decreasing - increase thresholds
            new_threshold = min(0.9, 0.7 + pattern.impact_score * 0.2)
            return AdaptationResult(
                adaptation_type="quality_improvement",
                parameters_changed={"semantic_threshold": new_threshold},
                expected_improvement=0.1,
                confidence=pattern.confidence,
                applied_at=time.time()
            )
        else:
            # Quality improving - can be more aggressive
            new_threshold = max(0.5, 0.7 - pattern.impact_score * 0.1)
            return AdaptationResult(
                adaptation_type="quality_optimization",
                parameters_changed={"semantic_threshold": new_threshold},
                expected_improvement=0.05,
                confidence=pattern.confidence,
                applied_at=time.time()
            )
    
    def _adapt_for_context_performance(self, pattern: LearningPattern) -> AdaptationResult:
        """Adapt parameters for context-specific performance."""
        if "poor" in pattern.pattern_id:
            # Poor performance - increase retrieval
            new_top_k = min(20, 10 + int(pattern.impact_score * 5))
            return AdaptationResult(
                adaptation_type="context_improvement",
                parameters_changed={"retrieval_top_k": new_top_k},
                expected_improvement=0.15,
                confidence=pattern.confidence,
                applied_at=time.time()
            )
        
        return None
    
    def _adapt_for_temporal_pattern(self, pattern: LearningPattern) -> AdaptationResult:
        """Adapt parameters for temporal patterns."""
        # Adjust cache freshness based on temporal patterns
        new_freshness = int(24 + pattern.impact_score * 24)
        return AdaptationResult(
            adaptation_type="temporal_optimization",
            parameters_changed={"cache_freshness_hours": new_freshness},
            expected_improvement=0.08,
            confidence=pattern.confidence,
            applied_at=time.time()
        )
    
    def get_current_parameters(self) -> Dict[str, Any]:
        """Get current adapted parameters."""
        # Start with defaults
        current_params = {
            'semantic_threshold': 0.7,
            'retrieval_top_k': 10,
            'tone_formality': 0.7,
            'cache_freshness_hours': 24,
            'bm25_weight': 0.5
        }
        
        # Apply recent adaptations
        recent_adaptations = self.adaptation_log[-10:]  # Last 10 adaptations
        for adaptation in recent_adaptations:
            current_params.update(adaptation.parameters_changed)
        
        return current_params


class MetaLearningSystem:
    """
    Simplified Meta-Learning System
    
    Lightweight meta-learning system that provides continuous
    improvement through feedback collection, pattern recognition,
    and adaptive parameter tuning.
    """
    
    def __init__(self, learning_mode: LearningMode = LearningMode.ACTIVE):
        self.learning_mode = learning_mode
        self.feedback_collector = FeedbackCollector()
        self.pattern_recognizer = PatternRecognizer()
        self.parameter_tuner = AdaptiveParameterTuner()
        
        self.is_learning = False
        self.learning_stats = {
            'total_feedback': 0,
            'patterns_detected': 0,
            'adaptations_applied': 0,
            'last_learning_cycle': 0.0
        }
    
    def add_feedback(
        self,
        task_id: str,
        feedback_type: FeedbackType,
        score: float,
        context: Dict[str, Any] = None,
        source: str = "system"
    ) -> None:
        """
        Add feedback to the meta-learning system.
        
        Args:
            task_id: Unique task identifier
            feedback_type: Type of feedback
            score: Feedback score (0.0 to 1.0)
            context: Context information
            source: Feedback source
        """
        self.feedback_collector.add_feedback(
            task_id=task_id,
            feedback_type=feedback_type,
            score=score,
            context=context,
            source=source
        )
        
        self.learning_stats['total_feedback'] += 1
        
        # Trigger learning cycle if in active mode
        if self.learning_mode == LearningMode.ACTIVE:
            self._trigger_learning_cycle()
    
    def learn_from_feedback(self, feedback_limit: int = 100) -> List[AdaptationResult]:
        """
        Learn from collected feedback and adapt parameters.
        
        Args:
            feedback_limit: Maximum number of feedback signals to analyze
            
        Returns:
            List of adaptation results
        """
        if self.learning_mode == LearningMode.PASSIVE:
            logger.info("Meta-learning in passive mode - no adaptations applied")
            return []
        
        # Get recent feedback
        recent_feedback = self.feedback_collector.get_recent_feedback(limit=feedback_limit)
        
        if len(recent_feedback) < 10:
            logger.info("Insufficient feedback for learning cycle")
            return []
        
        # Recognize patterns
        patterns = self.pattern_recognizer.recognize_patterns(recent_feedback)
        
        if not patterns:
            logger.info("No significant patterns detected")
            return []
        
        # Adapt parameters
        adaptations = self.parameter_tuner.adapt_parameters(patterns)
        
        # Update statistics
        self.learning_stats['patterns_detected'] += len(patterns)
        self.learning_stats['adaptations_applied'] += len(adaptations)
        self.learning_stats['last_learning_cycle'] = time.time()
        
        logger.info(f"Learning cycle completed: {len(patterns)} patterns, {len(adaptations)} adaptations")
        
        return adaptations
    
    def get_adapted_parameters(self) -> Dict[str, Any]:
        """Get current adapted parameters."""
        return self.parameter_tuner.get_current_parameters()
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Get insights about the learning process."""
        feedback_stats = self.feedback_collector.get_feedback_stats()
        
        return {
            'learning_mode': self.learning_mode.value,
            'learning_stats': self.learning_stats,
            'feedback_stats': feedback_stats,
            'recent_patterns': list(self.pattern_recognizer.pattern_history.values()),
            'recent_adaptations': self.parameter_tuner.adaptation_log[-5:]
        }
    
    def _trigger_learning_cycle(self) -> None:
        """Trigger learning cycle if conditions are met."""
        current_time = time.time()
        time_since_last = current_time - self.learning_stats['last_learning_cycle']
        
        # Trigger if enough time has passed (1 hour) or enough feedback collected (50)
        if time_since_last > 3600 or self.learning_stats['total_feedback'] % 50 == 0:
            self.learn_from_feedback()
    
    def save_learning_state(self, filepath: str) -> None:
        """Save learning state to file."""
        state = {
            'learning_stats': self.learning_stats,
            'patterns': {k: asdict(v) for k, v in self.pattern_recognizer.pattern_history.items()},
            'adaptations': [asdict(a) for a in self.parameter_tuner.adaptation_log],
            'current_parameters': self.get_adapted_parameters()
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
        
        logger.info(f"Saved learning state to {filepath}")
    
    def load_learning_state(self, filepath: str) -> None:
        """Load learning state from file."""
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)
            
            self.learning_stats = state['learning_stats']
            
            # Restore patterns
            for pattern_id, pattern_data in state['patterns'].items():
                self.pattern_recognizer.pattern_history[pattern_id] = LearningPattern(**pattern_data)
            
            # Restore adaptations
            for adaptation_data in state['adaptations']:
                self.parameter_tuner.adaptation_log.append(AdaptationResult(**adaptation_data))
            
            logger.info(f"Loaded learning state from {filepath}")
            
        except FileNotFoundError:
            logger.warning(f"Learning state file not found: {filepath}")
        except Exception as e:
            logger.error(f"Error loading learning state: {e}")


# Factory functions for easy integration
def create_meta_learning_system(learning_mode: LearningMode = LearningMode.ACTIVE) -> MetaLearningSystem:
    """Create meta-learning system instance."""
    return MetaLearningSystem(learning_mode)


def create_feedback_collector(max_signals: int = 10000) -> FeedbackCollector:
    """Create feedback collector instance."""
    return FeedbackCollector(max_signals)


def create_pattern_recognizer(min_confidence: float = 0.7) -> PatternRecognizer:
    """Create pattern recognizer instance."""
    return PatternRecognizer(min_confidence)
