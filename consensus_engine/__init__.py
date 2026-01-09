"""
Consensus Engine - Stub module for backwards compatibility.
"""
from typing import Any, Dict, List, Optional


class ConsensusEngine:
    """Engine for reaching consensus."""
    def __init__(self):
        self._votes = []
    
    def vote(self, value: Any) -> None:
        self._votes.append(value)
    
    def get_consensus(self) -> Optional[Any]:
        if not self._votes:
            return None
        # Simple majority
        from collections import Counter
        counts = Counter(self._votes)
        return counts.most_common(1)[0][0]


__all__ = ['ConsensusEngine']
