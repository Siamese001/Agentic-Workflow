"""LIC Cache Critique - L4 cache sufficiency evaluation for LIC research.

Implements nuclear prompt requirements for deterministic cache critique:
- Decide whether existing LIC research cache is "good enough" vs re-running research
- L4 only: read existing signals, decide sufficiency
- Check coverage of signal targets and staleness based on timestamps
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class LICCacheCritiqueResult:
    """Result of cache critique evaluation."""
    is_good_enough: bool                  # whether cache is sufficient
    missing_targets: List[str]            # targets that are not adequately covered
    coverage_score: float                 # overall coverage score [0, 1]
    freshness_score: float                # freshness/staleness score [0, 1]
    metadata: Dict[str, Any] = field(default_factory=dict)


class LICCacheCritique:
    """L4 cache evaluator for LIC research sufficiency.
    
    Evaluates whether existing research cache covers required targets
    and is fresh enough to avoid re-running research.
    """
    
    def __init__(self, telemetry_bus: Optional[Any] = None) -> None:
        """Initialize LIC cache critique evaluator."""
        self.telemetry_bus = telemetry_bus
        
        # Required signal targets for complete coverage
        self.required_targets = {
            "funding",           # funding rounds, financial information
            "strategy",          # strategic initiatives, company direction
            "product",           # product information, roadmap
            "personnel",         # hiring, leadership changes
            "market",            # market position, competition
        }
        
        # Freshness thresholds (in days)
        self.freshness_thresholds = {
            "funding": 90,      # 3 months for funding info
            "strategy": 60,     # 2 months for strategy
            "product": 30,      # 1 month for product info
            "personnel": 30,    # 1 month for personnel changes
            "market": 60,       # 2 months for market info
        }
        
        # Coverage thresholds
        self.min_coverage_threshold = 0.7  # 70% of targets must be covered
        self.min_freshness_threshold = 0.5  # 50% average freshness
    
    def evaluate(
        self,
        *,
        existing_signals: Dict[str, Any],
        targets: List[str],
    ) -> LICCacheCritiqueResult:
        """Evaluate whether existing cache is good enough.
        
        Args:
            existing_signals: Existing research signals by type
            targets: List of required targets to check coverage for
            
        Returns:
            Cache critique result with sufficiency determination
        """
        # 1. Analyze coverage of required targets
        coverage_analysis = self._analyze_target_coverage(existing_signals, targets)
        
        # 2. Evaluate freshness of signals
        freshness_analysis = self._evaluate_freshness(existing_signals)
        
        # 3. Determine overall sufficiency
        is_good_enough = self._determine_sufficiency(
            coverage_analysis, freshness_analysis
        )
        
        # 4. Identify missing targets
        missing_targets = self._identify_missing_targets(coverage_analysis, targets)
        
        # 5. Build metadata
        metadata = {
            "evaluated_targets": targets,
            "signal_types_found": list(existing_signals.keys()),
            "total_signals": sum(len(signals) for signals in existing_signals.values()),
            "evaluation_timestamp": datetime.now().isoformat(),
        }
        
        # 6. Create critique result
        result = LICCacheCritiqueResult(
            is_good_enough=is_good_enough,
            missing_targets=missing_targets,
            coverage_score=coverage_analysis["overall_score"],
            freshness_score=freshness_analysis["overall_score"],
            metadata=metadata,
        )
        
        # 7. Record telemetry (best-effort)
        self._safe_record_telemetry(result)
        
        return result
    
    def _analyze_target_coverage(self, existing_signals: Dict[str, Any], targets: List[str]) -> Dict[str, Any]:
        """Analyze coverage of required targets in existing signals."""
        coverage_scores = {}
        covered_targets = set()
        
        for target in targets:
            target_lower = target.lower()
            score = 0.0
            signal_count = 0
            
            # Check each signal type for target coverage
            for signal_type, signals in existing_signals.items():
                if not isinstance(signals, list):
                    continue
                
                for signal in signals:
                    if not isinstance(signal, dict):
                        continue
                    
                    # Check signal metadata and content for target indicators
                    signal_text = signal.get("text", "").lower()
                    signal_metadata = signal.get("metadata", {})
                    
                    # Direct target match in metadata
                    if signal_metadata.get("target_type", "").lower() == target_lower:
                        score += 1.0
                        signal_count += 1
                        covered_targets.add(target)
                    
                    # Content-based target detection
                    elif self._content_matches_target(signal_text, target_lower):
                        score += 0.5  # Partial credit for content match
                        signal_count += 1
            
            # Normalize score for this target
            if signal_count > 0:
                coverage_scores[target] = min(score / signal_count, 1.0)
            else:
                coverage_scores[target] = 0.0
        
        # Calculate overall coverage score
        if targets:
            overall_score = sum(coverage_scores.get(t, 0.0) for t in targets) / len(targets)
        else:
            overall_score = 0.0
        
        return {
            "target_scores": coverage_scores,
            "covered_targets": covered_targets,
            "overall_score": overall_score,
        }
    
    def _content_matches_target(self, text: str, target: str) -> bool:
        """Check if signal content matches a target type."""
        target_keywords = {
            "funding": ["funding", "investment", "round", "raise", "capital", "venture", "series"],
            "strategy": ["strategy", "strategic", "initiative", "direction", "vision", "plan"],
            "product": ["product", "feature", "release", "launch", "roadmap", "development"],
            "personnel": ["hire", "hiring", "team", "employee", "staff", "leadership", "role"],
            "market": ["market", "competition", "competitor", "industry", "sector", "share"],
        }
        
        keywords = target_keywords.get(target, [])
        return any(keyword in text for keyword in keywords)
    
    def _evaluate_freshness(self, existing_signals: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate freshness of existing signals."""
        freshness_scores = {}
        total_age_days = 0
        signal_count = 0
        
        for signal_type, signals in existing_signals.items():
            if not isinstance(signals, list):
                continue
            
            type_freshness_scores = []
            
            for signal in signals:
                if not isinstance(signal, dict):
                    continue
                
                # Get timestamp from signal
                timestamp_str = signal.get("timestamp", signal.get("date", ""))
                age_days = self._calculate_signal_age(timestamp_str)
                
                # Calculate freshness score for this signal
                threshold = self.freshness_thresholds.get(signal_type, 60)
                if age_days <= threshold:
                    freshness_score = 1.0 - (age_days / threshold) * 0.5
                else:
                    freshness_score = 0.1  # Minimum score for old content
                
                type_freshness_scores.append(freshness_score)
                total_age_days += age_days
                signal_count += 1
            
            # Average freshness for this signal type
            if type_freshness_scores:
                freshness_scores[signal_type] = sum(type_freshness_scores) / len(type_freshness_scores)
            else:
                freshness_scores[signal_type] = 0.0
        
        # Calculate overall freshness score
        if signal_count > 0:
            overall_score = sum(freshness_scores.values()) / len(freshness_scores)
            avg_age_days = total_age_days / signal_count
        else:
            overall_score = 0.0
            avg_age_days = 0
        
        return {
            "type_scores": freshness_scores,
            "overall_score": overall_score,
            "avg_age_days": avg_age_days,
        }
    
    def _calculate_signal_age(self, timestamp_str: str) -> int:
        """Calculate age of signal in days from timestamp."""
        if not timestamp_str:
            return 999  # Very old for missing timestamps
        
        try:
            # Parse timestamp (handle various formats)
            if isinstance(timestamp_str, str):
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                except ValueError:
                    timestamp = datetime.strptime(timestamp_str[:10], '%Y-%m-%d')
            else:
                timestamp = timestamp_str
            
            age_days = (datetime.now() - timestamp).days
            return max(0, age_days)
        
        except Exception:
            logger.debug(f"Failed to parse timestamp: {timestamp_str}")
            return 999  # Assume very old for parsing errors
    
    def _determine_sufficiency(
        self,
        coverage_analysis: Dict[str, Any],
        freshness_analysis: Dict[str, Any],
    ) -> bool:
        """Determine if cache is sufficient based on coverage and freshness."""
        coverage_score = coverage_analysis["overall_score"]
        freshness_score = freshness_analysis["overall_score"]
        
        # Cache is good enough if both coverage and freshness meet thresholds
        coverage_sufficient = coverage_score >= self.min_coverage_threshold
        freshness_sufficient = freshness_score >= self.min_freshness_threshold
        
        return coverage_sufficient and freshness_sufficient
    
    def _identify_missing_targets(self, coverage_analysis: Dict[str, Any], targets: List[str]) -> List[str]:
        """Identify targets that are not adequately covered."""
        missing_targets = []
        target_scores = coverage_analysis["target_scores"]
        
        for target in targets:
            score = target_scores.get(target, 0.0)
            if score < 0.5:  # Less than 50% coverage is considered missing
                missing_targets.append(target)
        
        return missing_targets
    
    def _safe_record_telemetry(self, result: LICCacheCritiqueResult) -> None:
        """Record telemetry event safely without breaking evaluation."""
        if not self.telemetry_bus:
            return
        
        try:
            self.telemetry_bus.record_event(
                "lic_cache_critique_completed",
                layer="L4",
                payload={
                    "is_good_enough": result.is_good_enough,
                    "coverage_score": result.coverage_score,
                    "freshness_score": result.freshness_score,
                    "missing_targets_count": len(result.missing_targets),
                },
            )
        except Exception:
            # Telemetry failures should never break evaluation logic
            logger.debug("Failed to record telemetry for LIC cache critique")
