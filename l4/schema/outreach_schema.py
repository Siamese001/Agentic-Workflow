from dataclasses import dataclass
from typing import Any, Dict, Optional
from l4.hybrid_search import SearchResult
from datetime import datetime, timezone
import re

@dataclass
class OutreachRAGResult:
    """Unified outreach RAG result; preserves LIC semantics + adds signal metadata."""
    id: str
    score: float
    text: str
    company: str
    title: str
    source: str
    source_weight: float = 1.0
    age_days: int = 0
    signal_score: float = 0.0
    signal_type: Optional[str] = None
    is_signal_candidate: bool = False

def format_as_outreach_result(result: SearchResult) -> OutreachRAGResult:
    metadata = result.metadata or {}
    company = metadata.get("company", "N/A")
    title = metadata.get("title", "N/A")
    source = metadata.get("source", "unknown")
    source_weight = metadata.get("source_weight", 1.0)

    timestamp = metadata.get("timestamp")
    age_days = _compute_age_days(timestamp)

    signal_score = _compute_signal_score(result.text, metadata)
    signal_type = _classify_signal_type(result.text, metadata)
    is_signal_candidate = signal_score >= 0.7

    return OutreachRAGResult(
        id=result.id,
        score=result.fused_score,
        text=result.text,
        company=company,
        title=title,
        source=source,
        source_weight=source_weight,
        age_days=age_days,
        signal_score=signal_score,
        signal_type=signal_type,
        is_signal_candidate=is_signal_candidate
    )

def _compute_age_days(ts: Optional[str]) -> int:
    if not ts:
        return 365
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - dt).days
    except Exception:
        return 365

def _compute_signal_score(text: str, metadata: Dict[str, Any]) -> float:
    score = 0.5
    if re.search(r'\d+%|\$\d+|\d+x', text):
        score += 0.2
    if metadata.get("timestamp"):
        score += 0.1
    if metadata.get("named_entities"):
        score += 0.1
    if metadata.get("is_signal_candidate"):
        score += 0.1
    return min(score, 1.0)

def _classify_signal_type(text: str, metadata: Dict[str, Any]) -> Optional[str]:
    t = text.lower()
    if re.search(r'\d+%|\$\d+|\d+x|revenue|growth', t):
        return "quantitative"
    if re.search(r'strategy|vision|transform|initiative', t):
        return "strategic"
    if re.search(r'recently|just|announced|launched', t):
        return "recent_activity"
    return "general"
