"""Temporal Knowledge Graph Injection for V6 System

Provides temporal reasoning and knowledge graph integration
for enhanced context awareness and temporal planning.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone, UTC, timedelta
from enum import Enum

from l1.instructional_injection_v6 import InstructionalExtension, ExtensionContent


class TemporalRelation(str, Enum):
    """Types of temporal relationships between facts."""
    
    BEFORE = "before"
    AFTER = "after"
    DURING = "during"
    OVERLAPS = "overlaps"
    CONTAINS = "contains"
    PRECEDES = "precedes"
    SUCCEEDS = "succeeds"


@dataclass
class TemporalFact:
    """A fact with temporal context."""
    
    fact_id: str
    content: str
    timestamp: datetime
    confidence: float = 1.0
    source: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_valid_at(self, time: datetime) -> bool:
        """Check if this fact is valid at the given time."""
        # Simple validity check - facts are valid if not too old
        max_age = timedelta(days=365)  # 1 year default
        return (time - self.timestamp) <= max_age
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "fact_id": self.fact_id,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "confidence": self.confidence,
            "source": self.source,
            "metadata": self.metadata
        }


@dataclass
class TemporalFactRelation:
    """Relationship between temporal facts."""
    
    relation_id: str
    source_fact_id: str
    target_fact_id: str
    relation_type: TemporalRelation
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class TemporalKnowledgeGraph:
    """Manages temporal facts and relationships for enhanced reasoning."""
    
    def __init__(self) -> None:
        """Initialize the temporal knowledge graph."""
        self._facts: Dict[str, TemporalFact] = {}
        self._relations: List[TemporalRelation] = []
        self._fact_index: Dict[str, List[str]] = {}  # Content keyword index
    
    def add_fact(self, fact: TemporalFact) -> None:
        """Add a temporal fact to the knowledge graph."""
        self._facts[fact.fact_id] = fact
        
        # Update content index for quick lookup
        words = fact.content.lower().split()
        for word in words:
            if word not in self._fact_index:
                self._fact_index[word] = []
            self._fact_index[word].append(fact.fact_id)
    
    def add_relation(self, relation: TemporalRelation) -> None:
        """Add a temporal relation between facts."""
        self._relations.append(relation)
    
    def get_facts_at_time(self, time: datetime, max_facts: int = 10) -> List[TemporalFact]:
        """Get all facts valid at the given time."""
        valid_facts = [
            fact for fact in self._facts.values()
            if fact.is_valid_at(time)
        ]
        
        # Sort by confidence and timestamp
        valid_facts.sort(key=lambda f: (f.confidence, f.timestamp), reverse=True)
        return valid_facts[:max_facts]
    
    def search_facts(self, query: str, time: Optional[datetime] = None) -> List[TemporalFact]:
        """Search for facts matching the query."""
        query_words = query.lower().split()
        matching_fact_ids = set()
        
        for word in query_words:
            if word in self._fact_index:
                matching_fact_ids.update(self._fact_index[word])
        
        facts = [self._facts[fact_id] for fact_id in matching_fact_ids]
        
        # Filter by time if specified
        if time:
            facts = [f for f in facts if f.is_valid_at(time)]
        
        return sorted(facts, key=lambda f: f.confidence, reverse=True)
    
    def get_temporal_context(self, query: str, current_time: Optional[datetime] = None) -> str:
        """Get temporal context formatted for prompts."""
        if current_time is None:
            current_time = datetime.now(UTC)
        
        relevant_facts = self.search_facts(query, current_time)
        
        if not relevant_facts:
            return ""
        
        sections = ["## TEMPORAL KNOWLEDGE GRAPH", ""]
        sections.append(f"**Current Time:** {current_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        sections.append("")
        
        for fact in relevant_facts[:5]:  # Limit to top 5 facts
            sections.append(f"**Fact {fact.fact_id}:** {fact.content}")
            sections.append(f"**Timestamp:** {fact.timestamp.strftime('%Y-%m-%d')}")
            sections.append(f"**Confidence:** {fact.confidence:.2f}")
            sections.append("")
        
        return "\n".join(sections)


class TemporalInjectionProvider:
    """Provides temporal knowledge graph injection for V6 prompts."""
    
    def __init__(self, kg: Optional[TemporalKnowledgeGraph] = None) -> None:
        """Initialize the temporal injection provider."""
        self.kg = kg or TemporalKnowledgeGraph()
        self._initialize_default_facts()
    
    def _initialize_default_facts(self) -> None:
        """Initialize with some default temporal facts."""
        # Add career-related temporal facts
        default_facts = [
            TemporalFact(
                fact_id="tech_trends_2024",
                content="AI and machine learning skills are in high demand in 2024",
                timestamp=datetime(2024, 1, 1),
                confidence=0.9,
                source="industry_analysis"
            ),
            TemporalFact(
                fact_id="remote_work_2024",
                content="Remote work opportunities remain strong in tech sector",
                timestamp=datetime(2024, 3, 1),
                confidence=0.8,
                source="market_research"
            ),
            TemporalFact(
                fact_id="cloud_demand_2024",
                content="Cloud computing skills (AWS, Azure, GCP) are essential for modern roles",
                timestamp=datetime(2024, 2, 1),
                confidence=0.95,
                source="job_market_analysis"
            ),
        ]
        
        for fact in default_facts:
            self.kg.add_fact(fact)
    
    def add_temporal_extension(
        self,
        prompt_extensions: Dict[InstructionalExtension, ExtensionContent],
        query: str,
        current_time: Optional[datetime] = None
    ) -> Dict[InstructionalExtension, ExtensionContent]:
        """
        Add temporal knowledge graph as a V6 extension.
        
        Args:
            prompt_extensions: Existing prompt extensions
            query: Query to find relevant temporal facts
            current_time: Current time for context
            
        Returns:
            Updated extensions with temporal context
        """
        temporal_context = self.kg.get_temporal_context(query, current_time)
        
        if temporal_context:
            temporal_extension = ExtensionContent(
                extension=InstructionalExtension.TEMPORAL_REASONING,
                content=temporal_context
            )
            prompt_extensions[InstructionalExtension.TEMPORAL_REASONING] = temporal_extension
        
        return prompt_extensions
    
    def inject_temporal_facts(self, ctx: Any, query: str) -> List[TemporalFact]:
        """
        Inject relevant temporal facts into execution context.
        
        Args:
            ctx: Execution context
            query: Query for finding relevant facts
            
        Returns:
            List of relevant temporal facts
        """
        current_time = datetime.now(timezone.utc)
        relevant_facts = self.kg.search_facts(query, current_time)
        
        # Store in context for downstream use
        if hasattr(ctx, 'temporal_kg_facts'):
            ctx.temporal_kg_facts.extend(relevant_facts)
        else:
            ctx.temporal_kg_facts = relevant_facts
        
        return relevant_facts


def create_temporal_injection_provider() -> TemporalInjectionProvider:
    """Create a temporal injection provider."""
    return TemporalInjectionProvider()


__all__ = [
    'TemporalRelation',
    'TemporalFact',
    'TemporalKnowledgeGraph',
    'TemporalInjectionProvider',
    'create_temporal_injection_provider',
]



