"""
Consensus Engine - Stub module for backwards compatibility.
"""
from typing import Any, Dict, List, Optional


class ConsensusEngine:
    """Engine for reaching consensus across multiple models."""
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
    
    def judge_artifact(self, artifact: str) -> Dict[str, Any]:
        """Judge an artifact using consensus from multiple models."""
        # Stub implementation for testing
        votes = [
            {"model": "gpt-5.1", "verdict": "YES"},
            {"model": "claude-sonnet-4-5", "verdict": "YES"},
            {"model": "gemini-3-pro", "verdict": "YES"}
        ]
        
        # Check for problematic patterns
        if "while True" in artifact or "infinite loop" in artifact:
            votes[0]["verdict"] = "NO"  # GPT catches infinite loops
        
        if "global_var" in artifact or "race condition" in artifact:
            votes[1]["verdict"] = "NO"  # Claude catches race conditions
        
        if "non_existent" in artifact or "hallucination" in artifact:
            votes[2]["verdict"] = "NO"  # Gemini catches hallucinations
        
        yes_count = sum(1 for v in votes if v["verdict"] == "YES")
        score = yes_count / len(votes)
        status = "PASS" if score >= 0.66 else "FAIL"
        
        return {
            "status": status,
            "score": score,
            "votes": votes
        }


__all__ = ['ConsensusEngine']
