
# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: guardrail, healer, orchestrator, prompt, state, validator, workflow
# This boosts alignment detection — review and integrate appropriately

from __future__ import annotations
"""
Adaptive Learning Engine - L1 Cognition Enhancement

Learns from healing patterns to predict and prevent violations before they occur.
Uses pattern recognition and predictive analytics to make agents more autonomous.
"""
import asyncio
import json
import logging
import os
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
Logger: Any = logging.getLogger(__name__)

@dataclass
class HealingPattern:
    """Represents a learned healing pattern."""
    violation_key: int
    violation_signature: str
    fix_strategy: str
    success_count: int = 0
    failure_count: int = 0
    avg_rounds_to_fix: float = 0.0
    last_used: Optional[datetime] = None
    confidence_score: float = 0.0
    file_patterns: List[str] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        total: Any = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.0

    def update_confidence(self) -> Any:
        """Update confidence score based on success rate and usage."""
        base_confidence: Any = self.success_rate
        usage_factor: Any = min(1.0, (self.success_count + self.failure_count) / 10)
        recency_factor: Any = 1.0
        if self.last_used:
            days_since: Any = (datetime.now() - self.last_used).days
            recency_factor: Any = max(0.5, 1.0 - days_since / 30)
        self.confidence_score = base_confidence * usage_factor * recency_factor

@dataclass
class ViolationPrediction:
    """Prediction of potential Violation."""
    file_path: str
    violation_key: int
    confidence: float
    recommended_pattern: Optional[HealingPattern]
    reasoning: str

class AdaptiveLearningEngine:
    """
    Learns from healing patterns to predict and prevent violations.

    Features:
    - Pattern recognition from successful healing attempts
    - Predictive Violation detection
    - Automatic fix suggestion based on learned patterns
    - Continuous learning from new healing attempts
    """

    def __init__(self, pattern_storage_path: Optional[str]=None, autonomous_mode: bool=True):
        """Initialize the adaptive learning engine."""
        from pathlib import Path
        self.pattern_storage_path = pattern_storage_path or os.path.join(os.getcwd(), '.canon_memory', 'healing_patterns.json')
        self.storage_path = Path(self.pattern_storage_path)
        self.backup_dir = Path('.canon_memory/backups')
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.autonomous_mode = autonomous_mode
        self._improvement_task = None
        self.patterns: Dict[int, List[HealingPattern]] = defaultdict(list)
        self.violation_history: Dict[str, List[Tuple[int, bool, datetime]]] = defaultdict(list)
        self.prediction_cache: Dict[str, List[ViolationPrediction]] = {}
        self._load_patterns()
        Logger.info('Adaptive Learning Engine initialized')

    def awaken(self) -> Any:
        """L1: Explicitly trigger the autonomous learning loop"""
        if self.autonomous_mode and (not self._improvement_task):
            self._improvement_task = asyncio.create_task(self.eternal_self_improvement())
            Logger.info('L1 Autonomous learning loop awakened')

    async def eternal_self_improvement(self) -> Any:
        """L1: Continuous self-improvement loop"""
        while self.autonomous_mode:
            try:
                await asyncio.sleep(300)
                for key in list(self.patterns.keys()):
                    self.patterns[key] = [p for p in self.patterns[key] if p.confidence_score > 0.3 or p.success_count + p.failure_count < 5]
                self._save_patterns()
                Logger.debug('L1 Self-improvement cycle completed')
            except Exception as e:
                Logger.error(f'L1 Self-improvement error: {e}')
                await asyncio.sleep(60)

    def _load_patterns(self):
        """Load learned patterns from storage."""
        if not os.path.exists(self.pattern_storage_path):
            Logger.info('No existing patterns found, starting fresh')
            return
        try:
            with open(self.pattern_storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for key_str, patterns_data in data.get('patterns', {}).items():
                key = int(key_str)
                for p_data in patterns_data:
                    pattern = HealingPattern(violation_key=p_data['violation_key'], violation_signature=p_data['violation_signature'], fix_strategy=p_data['fix_strategy'], success_count=p_data['success_count'], failure_count=p_data['failure_count'], avg_rounds_to_fix=p_data['avg_rounds_to_fix'], last_used=datetime.fromisoformat(p_data['last_used']) if p_data.get('last_used') else None, confidence_score=p_data['confidence_score'], file_patterns=p_data.get('file_patterns', []))
                    self.patterns[key].append(pattern)
            Logger.info(f'Loaded {sum((len(p) for p in self.patterns.values()))} healing patterns')
        except Exception as e:
            Logger.error(f'Failed to load patterns: {e}')

    def _save_patterns(self):
        """Save learned patterns to storage with versioned rotation (Keep Last 10)."""
        try:
            os.makedirs(os.path.dirname(self.pattern_storage_path), exist_ok=True)
            if self.storage_path.exists():
                backup = self.backup_dir / f"healing_patterns.{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
                import shutil
                shutil.copy2(self.storage_path, backup)
                # Sub-20: Use ssot_discovery instead of glob
                from agentic_core.utils.ssot_discovery import get_data_files
                all_files = get_data_files(self.backup_dir, extensions=['.json'])
                backups = sorted([f for f in all_files if 'healing_patterns.' in f.name], key=os.path.getmtime, reverse=True)
                while len(backups) > 10:
                    backups[0].unlink()
                    backups.pop(0)
            data = {'patterns': {}, 'last_updated': datetime.now().isoformat()}
            for key, patterns in self.patterns.items():
                data['patterns'][str(key)] = [{'violation_key': p.violation_key, 'violation_signature': p.violation_signature, 'fix_strategy': p.fix_strategy, 'success_count': p.success_count, 'failure_count': p.failure_count, 'avg_rounds_to_fix': p.avg_rounds_to_fix, 'last_used': p.last_used.isoformat() if p.last_used else None, 'confidence_score': p.confidence_score, 'file_patterns': p.file_patterns} for p in patterns]
            with open(self.pattern_storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            Logger.debug(f'Saved patterns to {self.pattern_storage_path}')
        except Exception as e:
            Logger.error(f'Failed to save patterns: {e}')

    def learn_from_healing(self, file_path: str, violation_key: int, violation_details: str, fix_code: str, success: bool, rounds_taken: int) -> Any:
        """
        Learn from a healing attempt.

        Args:
            file_path: Path to the healed file
            violation_key: Canon key that was fixed
            violation_details: Description of the Violation
            fix_code: The code that fixed the issue
            success: Whether healing succeeded
            rounds_taken: Number of rounds it took
        """
        signature: Any = self._create_violation_signature(violation_details, file_path)
        existing_pattern: Any = self._find_matching_pattern(violation_key, signature)
        if existing_pattern:
            if success:
                existing_pattern.success_count += 1
                old_avg: Any = existing_pattern.avg_rounds_to_fix
                total: Any = existing_pattern.success_count
                existing_pattern.avg_rounds_to_fix = (old_avg * (total - 1) + rounds_taken) / total
            else:
                existing_pattern.failure_count += 1
            existing_pattern.last_used = datetime.now()
            existing_pattern.update_confidence()
        else:
            new_pattern: Any = HealingPattern(violation_key=violation_key, violation_signature=signature, fix_strategy=fix_code[:500], success_count=1 if success else 0, failure_count=0 if success else 1, avg_rounds_to_fix=float(rounds_taken) if success else 0.0, last_used=datetime.now(), file_patterns=[self._extract_file_pattern(file_path)])
            new_pattern.update_confidence()
            self.patterns[violation_key].append(new_pattern)
        self.violation_history[file_path].append((violation_key, success, datetime.now()))
        self._save_patterns()
        Logger.info(f'Learned from healing: Key {violation_key}, Success: {success}')

    def _create_violation_signature(self, violation_details: str, file_path: str) -> str:
        """Create a signature for a Violation type."""
        file_type = os.path.splitext(file_path)[1]
        keywords = self._extract_keywords(violation_details)
        return f"{file_type}:{':'.join(sorted(keywords[:5]))}"

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract key terms from Violation details."""
        stopwords = {'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'is', 'are'}
        words = text.lower().split()
        return [w for w in words if len(w) > 3 and w not in stopwords]

    def _extract_file_pattern(self, file_path: str) -> str:
        """Extract pattern from file path."""
        parts = file_path.replace('\\', '/').split('/')
        if len(parts) >= 2:
            return f'{parts[-2]}/*.py'
        return '*.py'

    def _find_matching_pattern(self, violation_key: int, signature: str) -> Optional[HealingPattern]:
        """Find existing pattern matching the signature."""
        for pattern in self.patterns.get(violation_key, []):
            if pattern.violation_signature == signature:
                return pattern
        return None

    async def predict_violations(self, file_path: str, code: str) -> List[ViolationPrediction]:
        """
        Predict potential violations in a file before they occur.

        Args:
            file_path: Path to the file
            code: File contents

        Returns:
            List of predicted violations with confidence scores
        """
        cache_key: Any = f'{file_path}:{hash(code)}'
        if cache_key in self.prediction_cache:
            return self.prediction_cache[cache_key]
        predictions: Any = []
        file_history: Any = self.violation_history.get(file_path, [])
        recent_violations: Any = [v[0] for v in file_history[-5:] if not v[1]]
        for violation_key in set(recent_violations):
            patterns: Any = self.patterns.get(violation_key, [])
            high_confidence_patterns: Any = [p for p in patterns if p.confidence_score > 0.7]
            if high_confidence_patterns:
                best_pattern: Any = max(high_confidence_patterns, key=lambda p: p.confidence_score)
                predictions.append(ViolationPrediction(file_path=file_path, violation_key=violation_key, confidence=best_pattern.confidence_score, recommended_pattern=best_pattern, reasoning=f'File has history of Key {violation_key} violations'))
        for violation_key, patterns in self.patterns.items():
            if violation_key in recent_violations:
                continue
            for pattern in patterns:
                if pattern.confidence_score < 0.8:
                    continue
                file_pattern: Any = self._extract_file_pattern(file_path)
                if file_pattern in pattern.file_patterns:
                    predictions.append(ViolationPrediction(file_path=file_path, violation_key=violation_key, confidence=pattern.confidence_score * 0.8, recommended_pattern=pattern, reasoning=f'Similar files often have Key {violation_key} violations'))
        predictions.sort(key=lambda p: p.confidence, reverse=True)
        self.prediction_cache[cache_key] = predictions[:5]
        return predictions[:5]

    def get_recommended_fix(self, violation_key: int, violation_details: str, file_path: str) -> Optional[str]:
        """
        Get recommended fix based on learned patterns.

        Args:
            violation_key: Canon key
            violation_details: Violation description
            file_path: File path

        Returns:
            Recommended fix strategy or None
        """
        signature: Any = self._create_violation_signature(violation_details, file_path)
        pattern: Any = self._find_matching_pattern(violation_key, signature)
        if pattern and pattern.confidence_score > 0.7:
            return pattern.fix_strategy
        patterns: Any = self.patterns.get(violation_key, [])
        if patterns:
            best: Any = max(patterns, key=lambda p: p.confidence_score)
            if best.confidence_score > 0.6:
                return best.fix_strategy
        return None

    def get_statistics(self) -> Dict[str, Any]:
        """Get learning statistics."""
        total_patterns: Any = sum((len(p) for p in self.patterns.values()))
        high_confidence: Any = sum((1 for patterns in self.patterns.values() for p in patterns if p.confidence_score > 0.8))
        avg_success_rate: Any = 0.0
        if total_patterns > 0:
            avg_success_rate: Any = sum((p.success_rate for patterns in self.patterns.values() for p in patterns)) / total_patterns
        return {'total_patterns': total_patterns, 'high_confidence_patterns': high_confidence, 'average_success_rate': avg_success_rate, 'keys_with_patterns': len(self.patterns), 'total_healing_attempts': sum((p.success_count + p.failure_count for patterns in self.patterns.values() for p in patterns))}

def create_adaptive_learning_engine(storage_path: Optional[str]=None, autonomous_mode: bool=True) -> AdaptiveLearningEngine:
    """Factory function to create adaptive learning engine."""
    return AdaptiveLearningEngine(pattern_storage_path=storage_path, autonomous_mode=autonomous_mode)
