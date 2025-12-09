"""
Meta-Learning System - Continuous Improvement Through Feedback
Ported from legacy_engines/meta_learning_system.py

Lightweight meta-learning system that captures core value of
continuous improvement without over-engineered complexity.
Includes feedback collection, pattern recognition, and
adaptive parameter tuning.
"""

import logging
import time
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


class FeedbackType(Enum):
    """Types of feedback signals"""
    QUALITY = "quality"
    RELEVANCE = "relevance"
    COMPLETENESS = "completeness"
    USER_SATISFACTION = "user_satisfaction"
    PERFORMANCE = "performance"
    ACCURACY = "accuracy"
    LATENCY = "latency"


class PatternType(Enum):
    """Types of learning patterns"""
    QUALITY_DEGRADATION = "quality_degradation"
    CONTEXT_SPECIFIC = "context_specific"
    SOURCE_BIAS = "source_bias"
    TEMPORAL = "temporal"
    USER_PREFERENCE = "user_preference"
    PERFORMANCE_TREND = "performance_trend"


class LearningMode(Enum):
    """Learning modes"""
    ACTIVE = "active"  # Actively adjusts parameters
    PASSIVE = "passive"  # Only collects data
    DISABLED = "disabled"  # No learning


@dataclass
class FeedbackSignal:
    """Individual feedback signal"""
    task_id: str
    feedback_type: FeedbackType
    score: float  # 0-1
    context: Dict[str, Any]
    timestamp: datetime
    source: str = "system"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LearningPattern:
    """Detected learning pattern"""
    pattern_id: str
    pattern_type: PatternType
    confidence: float
    frequency: int
    last_seen: datetime
    impact_score: float
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AdaptationResult:
    """Result of parameter adaptation"""
    adaptation_type: str
    parameters_changed: Dict[str, Tuple[Any, Any]]  # param: (old, new)
    expected_improvement: float
    confidence: float
    applied_at: datetime


class FeedbackCollector:
    """
    Feedback Signal Collection
    
    Gathers various types of feedback for meta-learning.
    """
    
    def __init__(self, max_history: int = 1000):
        """
        Initialize feedback collector.
        
        Args:
            max_history: Maximum feedback signals to retain
        """
        self.max_history = max_history
        self.feedback_history: List[FeedbackSignal] = []
        self.feedback_by_type: Dict[FeedbackType, List[FeedbackSignal]] = defaultdict(list)
    
    def collect(
        self,
        task_id: str,
        feedback_type: FeedbackType,
        score: float,
        context: Optional[Dict[str, Any]] = None,
        source: str = "system"
    ) -> FeedbackSignal:
        """
        Collect a feedback signal.
        
        Args:
            task_id: ID of the task
            feedback_type: Type of feedback
            score: Feedback score (0-1)
            context: Additional context
            source: Source of feedback
            
        Returns:
            Created FeedbackSignal
        """
        signal = FeedbackSignal(
            task_id=task_id,
            feedback_type=feedback_type,
            score=min(max(score, 0.0), 1.0),
            context=context or {},
            timestamp=datetime.now(),
            source=source
        )
        
        self.feedback_history.append(signal)
        self.feedback_by_type[feedback_type].append(signal)
        
        # Trim history if needed
        if len(self.feedback_history) > self.max_history:
            removed = self.feedback_history.pop(0)
            self.feedback_by_type[removed.feedback_type].remove(removed)
        
        logger.debug(f"Collected feedback: {feedback_type.value}={score:.2f} for task {task_id}")
        
        return signal
    
    def get_recent_feedback(
        self,
        feedback_type: Optional[FeedbackType] = None,
        limit: int = 50
    ) -> List[FeedbackSignal]:
        """Get recent feedback signals."""
        if feedback_type:
            return self.feedback_by_type[feedback_type][-limit:]
        return self.feedback_history[-limit:]
    
    def get_average_score(
        self,
        feedback_type: FeedbackType,
        window: int = 20
    ) -> float:
        """Get average score for feedback type."""
        signals = self.feedback_by_type[feedback_type][-window:]
        if not signals:
            return 0.5
        return sum(s.score for s in signals) / len(signals)
    
    def get_feedback_summary(self) -> Dict[str, Any]:
        """Get summary of collected feedback."""
        summary = {
            'total_signals': len(self.feedback_history),
            'by_type': {}
        }
        
        for feedback_type in FeedbackType:
            signals = self.feedback_by_type[feedback_type]
            if signals:
                summary['by_type'][feedback_type.value] = {
                    'count': len(signals),
                    'avg_score': sum(s.score for s in signals) / len(signals),
                    'latest_score': signals[-1].score if signals else None
                }
        
        return summary


class PatternRecognizer:
    """
    Pattern Recognition for Meta-Learning
    
    Identifies patterns in feedback data for adaptive learning.
    """
    
    def __init__(self, min_pattern_frequency: int = 5):
        """
        Initialize pattern recognizer.
        
        Args:
            min_pattern_frequency: Minimum occurrences to recognize pattern
        """
        self.min_pattern_frequency = min_pattern_frequency
        self.detected_patterns: Dict[str, LearningPattern] = {}
        self.pattern_history: List[LearningPattern] = []
    
    def analyze_feedback(
        self,
        feedback_signals: List[FeedbackSignal]
    ) -> List[LearningPattern]:
        """
        Analyze feedback signals for patterns.
        
        Args:
            feedback_signals: Feedback signals to analyze
            
        Returns:
            List of detected patterns
        """
        patterns = []
        
        if len(feedback_signals) < self.min_pattern_frequency:
            return patterns
        
        # Check for quality degradation
        quality_pattern = self._detect_quality_degradation(feedback_signals)
        if quality_pattern:
            patterns.append(quality_pattern)
        
        # Check for context-specific patterns
        context_patterns = self._detect_context_patterns(feedback_signals)
        patterns.extend(context_patterns)
        
        # Check for temporal patterns
        temporal_pattern = self._detect_temporal_patterns(feedback_signals)
        if temporal_pattern:
            patterns.append(temporal_pattern)
        
        # Check for source bias
        source_pattern = self._detect_source_bias(feedback_signals)
        if source_pattern:
            patterns.append(source_pattern)
        
        # Update detected patterns
        for pattern in patterns:
            self.detected_patterns[pattern.pattern_id] = pattern
            self.pattern_history.append(pattern)
        
        logger.info(f"Detected {len(patterns)} patterns from {len(feedback_signals)} signals")
        
        return patterns
    
    def _detect_quality_degradation(
        self,
        signals: List[FeedbackSignal]
    ) -> Optional[LearningPattern]:
        """Detect quality degradation pattern."""
        quality_signals = [s for s in signals if s.feedback_type == FeedbackType.QUALITY]
        
        if len(quality_signals) < self.min_pattern_frequency:
            return None
        
        # Check for declining trend
        recent = quality_signals[-10:]
        older = quality_signals[-20:-10] if len(quality_signals) >= 20 else quality_signals[:10]
        
        if not older:
            return None
        
        recent_avg = sum(s.score for s in recent) / len(recent)
        older_avg = sum(s.score for s in older) / len(older)
        
        if recent_avg < older_avg - 0.1:  # 10% decline threshold
            return LearningPattern(
                pattern_id=f"quality_degradation_{int(time.time())}",
                pattern_type=PatternType.QUALITY_DEGRADATION,
                confidence=min((older_avg - recent_avg) * 5, 1.0),
                frequency=len(quality_signals),
                last_seen=datetime.now(),
                impact_score=older_avg - recent_avg,
                description=f"Quality declined from {older_avg:.2f} to {recent_avg:.2f}"
            )
        
        return None
    
    def _detect_context_patterns(
        self,
        signals: List[FeedbackSignal]
    ) -> List[LearningPattern]:
        """Detect context-specific patterns."""
        patterns = []
        
        # Group by context keys
        context_groups: Dict[str, List[FeedbackSignal]] = defaultdict(list)
        
        for signal in signals:
            for key, value in signal.context.items():
                context_key = f"{key}:{value}"
                context_groups[context_key].append(signal)
        
        # Find contexts with significantly different scores
        overall_avg = sum(s.score for s in signals) / len(signals) if signals else 0.5
        
        for context_key, group_signals in context_groups.items():
            if len(group_signals) >= self.min_pattern_frequency:
                group_avg = sum(s.score for s in group_signals) / len(group_signals)
                
                if abs(group_avg - overall_avg) > 0.15:  # 15% difference threshold
                    pattern = LearningPattern(
                        pattern_id=f"context_{context_key}_{int(time.time())}",
                        pattern_type=PatternType.CONTEXT_SPECIFIC,
                        confidence=min(abs(group_avg - overall_avg) * 3, 1.0),
                        frequency=len(group_signals),
                        last_seen=datetime.now(),
                        impact_score=group_avg - overall_avg,
                        description=f"Context '{context_key}' shows {group_avg:.2f} vs overall {overall_avg:.2f}"
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def _detect_temporal_patterns(
        self,
        signals: List[FeedbackSignal]
    ) -> Optional[LearningPattern]:
        """Detect temporal patterns."""
        if len(signals) < self.min_pattern_frequency * 2:
            return None
        
        # Group by hour of day
        hour_groups: Dict[int, List[float]] = defaultdict(list)
        
        for signal in signals:
            hour = signal.timestamp.hour
            hour_groups[hour].append(signal.score)
        
        # Find hours with significantly different performance
        overall_avg = sum(s.score for s in signals) / len(signals)
        
        for hour, scores in hour_groups.items():
            if len(scores) >= 3:
                hour_avg = sum(scores) / len(scores)
                if abs(hour_avg - overall_avg) > 0.2:
                    return LearningPattern(
                        pattern_id=f"temporal_hour_{hour}_{int(time.time())}",
                        pattern_type=PatternType.TEMPORAL,
                        confidence=min(abs(hour_avg - overall_avg) * 2, 1.0),
                        frequency=len(scores),
                        last_seen=datetime.now(),
                        impact_score=hour_avg - overall_avg,
                        description=f"Hour {hour} shows {hour_avg:.2f} vs overall {overall_avg:.2f}"
                    )
        
        return None
    
    def _detect_source_bias(
        self,
        signals: List[FeedbackSignal]
    ) -> Optional[LearningPattern]:
        """Detect source bias patterns."""
        source_groups: Dict[str, List[float]] = defaultdict(list)
        
        for signal in signals:
            source_groups[signal.source].append(signal.score)
        
        if len(source_groups) < 2:
            return None
        
        # Compare sources
        source_avgs = {
            source: sum(scores) / len(scores)
            for source, scores in source_groups.items()
            if len(scores) >= 3
        }
        
        if len(source_avgs) < 2:
            return None
        
        max_source = max(source_avgs, key=source_avgs.get)
        min_source = min(source_avgs, key=source_avgs.get)
        
        diff = source_avgs[max_source] - source_avgs[min_source]
        
        if diff > 0.2:
            return LearningPattern(
                pattern_id=f"source_bias_{int(time.time())}",
                pattern_type=PatternType.SOURCE_BIAS,
                confidence=min(diff * 2, 1.0),
                frequency=sum(len(scores) for scores in source_groups.values()),
                last_seen=datetime.now(),
                impact_score=diff,
                description=f"Source '{max_source}' ({source_avgs[max_source]:.2f}) outperforms '{min_source}' ({source_avgs[min_source]:.2f})"
            )
        
        return None
    
    def get_active_patterns(self) -> List[LearningPattern]:
        """Get currently active patterns."""
        return list(self.detected_patterns.values())


class AdaptiveParameterTuner:
    """
    Adaptive Parameter Tuning
    
    Adjusts system parameters based on detected patterns.
    """
    
    def __init__(self, learning_rate: float = 0.1):
        """
        Initialize parameter tuner.
        
        Args:
            learning_rate: Rate of parameter adjustment
        """
        self.learning_rate = learning_rate
        self.current_parameters: Dict[str, Any] = self._get_default_parameters()
        self.adaptation_history: List[AdaptationResult] = []
    
    def adapt_parameters(
        self,
        patterns: List[LearningPattern]
    ) -> List[AdaptationResult]:
        """
        Adapt parameters based on detected patterns.
        
        Args:
            patterns: Detected learning patterns
            
        Returns:
            List of adaptation results
        """
        adaptations = []
        
        for pattern in patterns:
            if pattern.confidence < 0.5:
                continue  # Skip low-confidence patterns
            
            adaptation = self._adapt_for_pattern(pattern)
            if adaptation:
                adaptations.append(adaptation)
                self.adaptation_history.append(adaptation)
        
        logger.info(f"Applied {len(adaptations)} parameter adaptations")
        
        return adaptations
    
    def _adapt_for_pattern(self, pattern: LearningPattern) -> Optional[AdaptationResult]:
        """Adapt parameters for a specific pattern."""
        changes = {}
        
        if pattern.pattern_type == PatternType.QUALITY_DEGRADATION:
            # Increase quality thresholds
            old_threshold = self.current_parameters.get('quality_threshold', 0.7)
            new_threshold = min(old_threshold + self.learning_rate * 0.1, 0.95)
            
            if new_threshold != old_threshold:
                self.current_parameters['quality_threshold'] = new_threshold
                changes['quality_threshold'] = (old_threshold, new_threshold)
        
        elif pattern.pattern_type == PatternType.CONTEXT_SPECIFIC:
            # Adjust context weights
            context_key = pattern.description.split("'")[1] if "'" in pattern.description else "unknown"
            weight_key = f"context_weight_{context_key}"
            
            old_weight = self.current_parameters.get(weight_key, 1.0)
            adjustment = self.learning_rate * pattern.impact_score
            new_weight = max(0.5, min(old_weight + adjustment, 2.0))
            
            if new_weight != old_weight:
                self.current_parameters[weight_key] = new_weight
                changes[weight_key] = (old_weight, new_weight)
        
        elif pattern.pattern_type == PatternType.SOURCE_BIAS:
            # Adjust source weights
            old_weight = self.current_parameters.get('source_diversity_weight', 1.0)
            new_weight = min(old_weight + self.learning_rate * 0.2, 2.0)
            
            if new_weight != old_weight:
                self.current_parameters['source_diversity_weight'] = new_weight
                changes['source_diversity_weight'] = (old_weight, new_weight)
        
        if not changes:
            return None
        
        return AdaptationResult(
            adaptation_type=pattern.pattern_type.value,
            parameters_changed=changes,
            expected_improvement=pattern.impact_score * pattern.confidence,
            confidence=pattern.confidence,
            applied_at=datetime.now()
        )
    
    def _get_default_parameters(self) -> Dict[str, Any]:
        """Get default parameters."""
        return {
            'quality_threshold': 0.7,
            'relevance_threshold': 0.6,
            'semantic_threshold': 0.75,
            'retrieval_top_k': 5,
            'tone_formality': 0.5,
            'source_diversity_weight': 1.0
        }
    
    def get_current_parameters(self) -> Dict[str, Any]:
        """Get current parameters."""
        return self.current_parameters.copy()
    
    def set_parameter(self, key: str, value: Any) -> None:
        """Manually set a parameter."""
        self.current_parameters[key] = value


class MetaLearningSystem:
    """
    Complete Meta-Learning System
    
    Orchestrates feedback collection, pattern recognition,
    and adaptive parameter tuning for continuous improvement.
    """
    
    def __init__(
        self,
        mode: LearningMode = LearningMode.ACTIVE,
        learning_rate: float = 0.1
    ):
        """
        Initialize meta-learning system.
        
        Args:
            mode: Learning mode
            learning_rate: Rate of parameter adjustment
        """
        self.mode = mode
        self.feedback_collector = FeedbackCollector()
        self.pattern_recognizer = PatternRecognizer()
        self.parameter_tuner = AdaptiveParameterTuner(learning_rate)
        
        self.learning_stats = {
            'total_feedback': 0,
            'patterns_detected': 0,
            'adaptations_applied': 0,
            'last_learning_cycle': None
        }
    
    def record_feedback(
        self,
        task_id: str,
        feedback_type: FeedbackType,
        score: float,
        context: Optional[Dict[str, Any]] = None
    ) -> FeedbackSignal:
        """
        Record feedback and trigger learning if in active mode.
        
        Args:
            task_id: ID of the task
            feedback_type: Type of feedback
            score: Feedback score (0-1)
            context: Additional context
            
        Returns:
            Created FeedbackSignal
        """
        signal = self.feedback_collector.collect(task_id, feedback_type, score, context)
        self.learning_stats['total_feedback'] += 1
        
        # Trigger learning cycle periodically
        if self.mode == LearningMode.ACTIVE and self.learning_stats['total_feedback'] % 10 == 0:
            self.run_learning_cycle()
        
        return signal
    
    def run_learning_cycle(self) -> Dict[str, Any]:
        """
        Run a complete learning cycle.
        
        Returns:
            Learning cycle results
        """
        if self.mode == LearningMode.DISABLED:
            return {'status': 'disabled'}
        
        # Get recent feedback
        recent_feedback = self.feedback_collector.get_recent_feedback(limit=100)
        
        # Detect patterns
        patterns = self.pattern_recognizer.analyze_feedback(recent_feedback)
        self.learning_stats['patterns_detected'] += len(patterns)
        
        # Apply adaptations if in active mode
        adaptations = []
        if self.mode == LearningMode.ACTIVE and patterns:
            adaptations = self.parameter_tuner.adapt_parameters(patterns)
            self.learning_stats['adaptations_applied'] += len(adaptations)
        
        self.learning_stats['last_learning_cycle'] = datetime.now().isoformat()
        
        logger.info(f"Learning cycle complete: {len(patterns)} patterns, {len(adaptations)} adaptations")
        
        return {
            'status': 'completed',
            'patterns_detected': len(patterns),
            'adaptations_applied': len(adaptations),
            'current_parameters': self.parameter_tuner.get_current_parameters()
        }
    
    def get_current_parameters(self) -> Dict[str, Any]:
        """Get current adapted parameters."""
        return self.parameter_tuner.get_current_parameters()
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get learning statistics."""
        return {
            **self.learning_stats,
            'feedback_summary': self.feedback_collector.get_feedback_summary(),
            'active_patterns': len(self.pattern_recognizer.get_active_patterns()),
            'mode': self.mode.value
        }
    
    def set_mode(self, mode: LearningMode) -> None:
        """Set learning mode."""
        self.mode = mode
        logger.info(f"Meta-learning mode set to: {mode.value}")
    
    def save_state(self) -> Dict[str, Any]:
        """Save learning state for persistence."""
        return {
            'mode': self.mode.value,
            'parameters': self.parameter_tuner.get_current_parameters(),
            'stats': self.learning_stats,
            'patterns': [
                {
                    'pattern_id': p.pattern_id,
                    'pattern_type': p.pattern_type.value,
                    'confidence': p.confidence,
                    'description': p.description
                }
                for p in self.pattern_recognizer.get_active_patterns()
            ]
        }
    
    def load_state(self, state: Dict[str, Any]) -> None:
        """Load learning state from persistence."""
        if 'mode' in state:
            self.mode = LearningMode(state['mode'])
        
        if 'parameters' in state:
            for key, value in state['parameters'].items():
                self.parameter_tuner.set_parameter(key, value)
        
        if 'stats' in state:
            self.learning_stats.update(state['stats'])
        
        logger.info("Meta-learning state loaded")


# Factory functions
def create_meta_learning_system(
    mode: LearningMode = LearningMode.ACTIVE,
    learning_rate: float = 0.1
) -> MetaLearningSystem:
    """Create meta-learning system instance."""
    return MetaLearningSystem(mode, learning_rate)


def create_feedback_collector(max_history: int = 1000) -> FeedbackCollector:
    """Create feedback collector instance."""
    return FeedbackCollector(max_history)


def create_pattern_recognizer(min_frequency: int = 5) -> PatternRecognizer:
    """Create pattern recognizer instance."""
    return PatternRecognizer(min_frequency)


def record_feedback(
    task_id: str,
    feedback_type: FeedbackType,
    score: float,
    context: Optional[Dict[str, Any]] = None
) -> FeedbackSignal:
    """Convenience function to record feedback."""
    collector = FeedbackCollector()
    return collector.collect(task_id, feedback_type, score, context)
