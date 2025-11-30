from typing import Any, Dict, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class HighSignalScore:
    """Represents a high signal score with metadata."""
    item_id: str
    score: float
    confidence: float
    timestamp: datetime
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def process(self, *args, **kwargs) -> Any:
        """Process high signal score with validation."""
        return {
            "item_id": self.item_id,
            "score": self.score,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
            "processed": True
        }

class HighSignalScorer:
    """Minimal functional high signal scorer implementation."""

    def __init__(self, threshold: float = 0.7):
        self.threshold = threshold

    def process(self, *args, **kwargs) -> Any:
        """Process high signal scoring on items."""
        items = kwargs.get("items", [])
        if not items:
            return {"high_signal_items": [], "processed": True}

        high_signal_items = self.score_items(items)
        return {
            "high_signal_items": [
                {
                    "item_id": item.item_id,
                    "score": item.score,
                    "confidence": item.confidence
                } for item in high_signal_items
            ],
            "processed": True,
            "total_items": len(items),
            "high_signal_count": len(high_signal_items)
        }

    def score_items(self, items: List[Dict[str, Any]]) -> List[HighSignalScore]:
        """Score items and return high signal ones."""
        high_signal_items = []

        for item in items:
            score = self._calculate_signal_score(item)
            confidence = self._calculate_confidence(item, score)

            if score >= self.threshold:
                high_signal_items.append(HighSignalScore(
                    item_id=item.get("id", str(len(high_signal_items))),
                    score=score,
                    confidence=confidence,
                    timestamp=datetime.now(),
                    metadata=item.get("metadata", {})
                ))

        return sorted(high_signal_items, key=lambda x: x.score, reverse=True)

    def _calculate_signal_score(self, item: Dict[str, Any]) -> float:
        """Calculate signal score for an item."""
        # Simple scoring based on item properties
        score = 0.5  # Base score

        # Boost for text length (more content = higher signal)
        text = item.get("text", "")
        if len(text) > 100:
            score += 0.2
        elif len(text) > 50:
            score += 0.1

        # Boost for keywords
        keywords = item.get("keywords", [])
        if keywords:
            score += min(0.2, len(keywords) * 0.05)

        # Boost for recency
        timestamp = item.get("timestamp")
        if timestamp:
            try:
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                days_old = (datetime.now() - timestamp).days
                if days_old < 7:
                    score += 0.1
            except:
                pass

        return min(1.0, score)

    def _calculate_confidence(self, item: Dict[str, Any], score: float) -> float:
        """Calculate confidence based on item properties and score."""
        confidence = 0.5  # Base confidence

        # Higher confidence for higher scores
        confidence += score * 0.3

        # Boost for complete metadata
        if item.get("metadata"):
            confidence += 0.1

        # Boost for source reliability
        source = item.get("source", "")
        if source in ["verified", "official", "trusted"]:
            confidence += 0.1

        return min(1.0, confidence)

    def set_threshold(self, threshold: float) -> None:
        """Update signal threshold."""
        if 0.0 <= threshold <= 1.0:
            self.threshold = threshold
