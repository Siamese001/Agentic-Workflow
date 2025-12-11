"""
RAG Components - Semantic Caching, Self-RAG, Episodic Memory, Knowledge Graph, Few-Shot
Ported from legacy_engines/enhanced_semantic_cache.py, lic_rag.py

Comprehensive RAG enhancement components for improved retrieval
and context injection.
"""

import logging
import time
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


# ============================================================================
# Semantic Cache
# ============================================================================

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: object
    embedding: Optional[List[float]]
    created_at: datetime
    accessed_at: datetime
    access_count: int = 0
    ttl_seconds: int = 3600


@dataclass
class CacheSufficiencyResult:
    """Result of cache sufficiency evaluation"""
    is_sufficient: bool
    coverage_score: float
    freshness_score: float
    similarity_score: float
    missing_targets: List[str]
    cached_data: Optional[Any] = None


class SemanticCache:
    """
    Enhanced Semantic Caching with Vector Similarity
    
    Extends basic caching with vector similarity scoring
    to reduce redundant research by 30-50%.
    """
    
    def __init__(
        self,
        max_entries: int = 1000,
        default_ttl: int = 3600,
        similarity_threshold: float = 0.85,
        freshness_threshold_days: int = 30
    ):
        """
        Initialize semantic cache.
        
        Args:
            max_entries: Maximum cache entries
            default_ttl: Default TTL in seconds
            similarity_threshold: Minimum similarity for cache hit
            freshness_threshold_days: Days before data is stale
        """
        self.max_entries = max_entries
        self.default_ttl = default_ttl
        self.similarity_threshold = similarity_threshold
        self.freshness_threshold_days = freshness_threshold_days
        
        self.cache: Dict[str, CacheEntry] = {}
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0
        }
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key not in self.cache:
            self.stats['misses'] += 1
            return None
        
        entry = self.cache[key]
        
        # Check TTL
        if self._is_expired(entry):
            del self.cache[key]
            self.stats['misses'] += 1
            return None
        
        # Update access metadata
        entry.accessed_at = datetime.now()
        entry.access_count += 1
        self.stats['hits'] += 1
        
        return entry.value
    
    def set(
        self,
        key: str,
        value: object,
        embedding: Optional[List[float]] = None,
        ttl: Optional[int] = None
    ) -> None:
        """Set value in cache."""
        # Evict if at capacity
        if len(self.cache) >= self.max_entries:
            self._evict_lru()
        
        entry = CacheEntry(
            key=key,
            value=value,
            embedding=embedding,
            created_at=datetime.now(),
            accessed_at=datetime.now(),
            ttl_seconds=ttl or self.default_ttl
        )
        
        self.cache[key] = entry
    
    def evaluate_sufficiency(
        self,
        query: str,
        required_targets: List[str],
        existing_data: Optional[Dict[str, object]] = None
    ) -> CacheSufficiencyResult:
        """
        Evaluate if cached data is sufficient for query.
        
        Args:
            query: Current query
            required_targets: Required data targets
            existing_data: Existing cached data to evaluate
            
        Returns:
            CacheSufficiencyResult with evaluation
        """
        if not existing_data:
            return CacheSufficiencyResult(
                is_sufficient=False,
                coverage_score=0.0,
                freshness_score=0.0,
                similarity_score=0.0,
                missing_targets=required_targets
            )
        
        # Calculate coverage
        covered_targets = []
        missing_targets = []
        
        for target in required_targets:
            if target in existing_data and existing_data[target]:
                covered_targets.append(target)
            else:
                missing_targets.append(target)
        
        coverage_score = len(covered_targets) / len(required_targets) if required_targets else 0.0
        
        # Calculate freshness
        freshness_score = self._calculate_freshness(existing_data)
        
        # Calculate similarity (simplified)
        similarity_score = self._calculate_similarity(query, existing_data)
        
        # Determine sufficiency
        is_sufficient = (
            coverage_score >= 0.8 and
            freshness_score >= 0.7 and
            similarity_score >= self.similarity_threshold
        )
        
        return CacheSufficiencyResult(
            is_sufficient=is_sufficient,
            coverage_score=coverage_score,
            freshness_score=freshness_score,
            similarity_score=similarity_score,
            missing_targets=missing_targets,
            cached_data=existing_data if is_sufficient else None
        )
    
    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if cache entry is expired."""
        elapsed = (datetime.now() - entry.created_at).total_seconds()
        return elapsed > entry.ttl_seconds
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if not self.cache:
            return
        
        lru_key = min(self.cache, key=lambda k: self.cache[k].accessed_at)
        del self.cache[lru_key]
        self.stats['evictions'] += 1
    
    def _calculate_freshness(self, data: Dict[str, object]) -> float:
        """Calculate data freshness score."""
        timestamp = data.get('timestamp') or data.get('cached_at')
        
        if not timestamp:
            return 0.5
        
        try:
            if isinstance(timestamp, str):
                data_date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            elif isinstance(timestamp, datetime):
                data_date = timestamp
            else:
                return 0.5
            
            days_old = (datetime.now() - data_date).days
            
            if days_old <= 0:
                return 1.0
            elif days_old >= self.freshness_threshold_days:
                return 0.0
            else:
                return 1.0 - (days_old / self.freshness_threshold_days)
        
        except (ValueError, TypeError):
            return 0.5
    
    def _calculate_similarity(self, query: str, data: Dict[str, object]) -> float:
        """Calculate query-data similarity (simplified)."""
        # basic word overlap for demonstration
        query_words = set(query.lower().split())
        
        data_text = ' '.join(str(v) for v in data.values() if isinstance(v, str))
        data_words = set(data_text.lower().split())
        
        if not query_words or not data_words:
            return 0.5
        
        overlap = len(query_words & data_words)
        return min(overlap / len(query_words), 1.0)
    
    def get_stats(self) -> Dict[str, object]:
        """Get cache statistics."""
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = self.stats['hits'] / total_requests if total_requests > 0 else 0.0
        
        return {
            **self.stats,
            'entries': len(self.cache),
            'hit_rate': round(hit_rate, 3),
            'max_entries': self.max_entries
        }
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
        logger.info("Semantic cache cleared")


# ============================================================================
# Self-RAG engine
# ============================================================================

class GapType(Enum):
    """Types of knowledge gaps"""
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    LOW_RELEVANCE = "low_relevance"
    OUTDATED_INFO = "outdated_info"
    LOW_AUTHORITY = "low_authority"
    MISSING_CONTEXT = "missing_context"


@dataclass
class KnowledgeGap:
    """Detected knowledge gap"""
    gap_type: GapType
    description: str
    severity: float
    suggested_query: str


@dataclass
class SelfRAGResult:
    """Result of Self-RAG processing"""
    original_query: str
    gaps_detected: List[KnowledgeGap]
    refined_queries: List[str]
    iterations_performed: int
    improvement_score: float


class SelfRAGProcessor:
    """
    Self-RAG Gap Detection and Closure
    
    Detects knowledge gaps in retrieval results and
    generates refined queries to close them.
    """
    
    def __init__(
        self,
        max_iterations: int = 3,
        min_evidence_count: int = 3,
        relevance_threshold: float = 0.6
    ):
        """
        Initialize Self-RAG engine.
        
        Args:
            max_iterations: Maximum refinement iterations
            min_evidence_count: Minimum evidence items required
            relevance_threshold: Minimum relevance score
        """
        self.max_iterations = max_iterations
        self.min_evidence_count = min_evidence_count
        self.relevance_threshold = relevance_threshold
    
    def detect_gaps(
        self,
        query: str,
        evidence: List[Dict[str, object]]
    ) -> List[KnowledgeGap]:
        """
        Detect knowledge gaps in evidence.
        
        Args:
            query: Original query
            evidence: Retrieved evidence
            
        Returns:
            List of detected gaps
        """
        gaps = []
        
        # Check for insufficient evidence
        if len(evidence) < self.min_evidence_count:
            gaps.append(KnowledgeGap(
                gap_type=GapType.INSUFFICIENT_EVIDENCE,
                description=f"Only {len(evidence)} evidence items found",
                severity=0.8,
                suggested_query=f"{query} comprehensive detailed"
            ))
        
        # Check for low relevance
        if evidence:
            avg_relevance = sum(e.get('relevance_score', 0.5) for e in evidence) / len(evidence)
            if avg_relevance < self.relevance_threshold:
                gaps.append(KnowledgeGap(
                    gap_type=GapType.LOW_RELEVANCE,
                    description=f"Average relevance {avg_relevance:.2f} below threshold",
                    severity=0.7,
                    suggested_query=f"{query} specific targeted"
                ))
        
        # Check for outdated info
        old_count = sum(1 for e in evidence if e.get('recency_score', 0.5) < 0.5)
        if old_count > len(evidence) // 2:
            gaps.append(KnowledgeGap(
                gap_type=GapType.OUTDATED_INFO,
                description=f"{old_count} evidence items are outdated",
                severity=0.6,
                suggested_query=f"{query} recent 2024 current"
            ))
        
        # Check for low authority
        low_auth_count = sum(1 for e in evidence if e.get('authority_score', 0.5) < 0.6)
        if low_auth_count > len(evidence) // 2:
            gaps.append(KnowledgeGap(
                gap_type=GapType.LOW_AUTHORITY,
                description=f"{low_auth_count} evidence items have low authority",
                severity=0.5,
                suggested_query=f"{query} official sources expert"
            ))
        
        return gaps
    
    def generate_refined_queries(
        self,
        original_query: str,
        gaps: List[KnowledgeGap]
    ) -> List[str]:
        """Generate refined queries to close gaps."""
        refined = []
        
        for gap in gaps:
            if gap.suggested_query and gap.suggested_query not in refined:
                refined.append(gap.suggested_query)
        
        return refined[:self.max_iterations]
    
    def process(
        self,
        query: str,
        evidence: List[Dict[str, object]]
    ) -> SelfRAGResult:
        """
        Process query with Self-RAG.
        
        Args:
            query: Original query
            evidence: Retrieved evidence
            
        Returns:
            SelfRAGResult with gaps and refined queries
        """
        gaps = self.detect_gaps(query, evidence)
        refined_queries = self.generate_refined_queries(query, gaps)
        
        # Calculate improvement potential
        if gaps:
            improvement_score = sum(g.severity for g in gaps) / len(gaps)
        else:
            improvement_score = 0.0
        
        logger.info(f"Self-RAG: {len(gaps)} gaps detected, {len(refined_queries)} refined queries")
        
        return SelfRAGResult(
            original_query=query,
            gaps_detected=gaps,
            refined_queries=refined_queries,
            iterations_performed=len(refined_queries),
            improvement_score=improvement_score
        )


# ============================================================================
# Episodic Memory
# ============================================================================

@dataclass
class Episode:
    """Memory episode"""
    episode_id: str
    content: str
    context: Dict[str, object]
    timestamp: datetime
    relevance: float
    episode_type: str


@dataclass
class EpisodicMemoryResult:
    """Result of episodic memory retrieval"""
    episodes: List[Episode]
    context_enrichment: Dict[str, object]
    retrieval_time_ms: int


class EpisodicMemory:
    """
    Episodic Memory for Context Retrieval
    
    Retrieves relevant past interactions and context
    for improved personalization.
    """
    
    def __init__(self, max_episodes: int = 100):
        """
        Initialize episodic memory.
        
        Args:
            max_episodes: Maximum episodes to retain
        """
        self.max_episodes = max_episodes
        self.episodes: Dict[str, List[Episode]] = defaultdict(list)
    
    def store(
        self,
        user_id: str,
        content: str,
        context: Dict[str, object],
        episode_type: str = "interaction"
    ) -> Episode:
        """
        Store an episode in memory.
        
        Args:
            user_id: User identifier
            content: Episode content
            context: Episode context
            episode_type: Type of episode
            
        Returns:
            Created Episode
        """
        episode = Episode(
            episode_id=f"ep_{int(time.time())}_{len(self.episodes[user_id])}",
            content=content,
            context=context,
            timestamp=datetime.now(),
            relevance=1.0,
            episode_type=episode_type
        )
        
        self.episodes[user_id].append(episode)
        
        # Trim if over limit
        if len(self.episodes[user_id]) > self.max_episodes:
            self.episodes[user_id] = self.episodes[user_id][-self.max_episodes:]
        
        return episode
    
    def retrieve(
        self,
        user_id: str,
        query: Optional[str] = None,
        episode_type: Optional[str] = None,
        limit: int = 5
    ) -> EpisodicMemoryResult:
        """
        Retrieve relevant episodes.
        
        Args:
            user_id: User identifier
            query: Optional query for relevance filtering
            episode_type: Optional type filter
            limit: Maximum episodes to return
            
        Returns:
            EpisodicMemoryResult with episodes
        """
        start_time = time.time()
        
        user_episodes = self.episodes.get(user_id, [])
        
        # Filter by type if specified
        if episode_type:
            user_episodes = [e for e in user_episodes if e.episode_type == episode_type]
        
        # Score by relevance if query provided
        if query:
            for episode in user_episodes:
                episode.relevance = self._calculate_relevance(query, episode)
            user_episodes.sort(key=lambda e: e.relevance, reverse=True)
        else:
            # Sort by recency
            user_episodes.sort(key=lambda e: e.timestamp, reverse=True)
        
        selected = user_episodes[:limit]
        
        # Build context enrichment
        context_enrichment = self._build_context_enrichment(selected)
        
        retrieval_time = int((time.time() - start_time) * 1000)
        
        return EpisodicMemoryResult(
            episodes=selected,
            context_enrichment=context_enrichment,
            retrieval_time_ms=retrieval_time
        )
    
    def _calculate_relevance(self, query: str, episode: Episode) -> float:
        """Calculate episode relevance to query."""
        query_words = set(query.lower().split())
        content_words = set(episode.content.lower().split())
        
        if not query_words or not content_words:
            return 0.5
        
        overlap = len(query_words & content_words)
        return min(overlap / len(query_words), 1.0)
    
    def _build_context_enrichment(self, episodes: List[Episode]) -> Dict[str, object]:
        """Build context enrichment from episodes."""
        if not episodes:
            return {}
        
        return {
            'episode_count': len(episodes),
            'types': list(set(e.episode_type for e in episodes)),
            'date_range': {
                'earliest': min(e.timestamp for e in episodes).isoformat(),
                'latest': max(e.timestamp for e in episodes).isoformat()
            },
            'avg_relevance': sum(e.relevance for e in episodes) / len(episodes)
        }


# ============================================================================
# Knowledge Graph Injector
# ============================================================================

@dataclass
class KGRelationship:
    """Knowledge graph relationship"""
    source: str
    target: str
    relationship_type: str
    weight: float
    metadata: Dict[str, object] = field(default_factory=dict)


@dataclass
class KGContext:
    """Knowledge graph context"""
    relationships: List[KGRelationship]
    shared_entities: List[str]
    context_summary: str


class KnowledgeGraphInjector:
    """
    Knowledge Graph Context Injection
    
    Injects relationship context from knowledge graph
    for improved personalization.
    """
    
    def __init__(self):
        """Initialize knowledge graph injector."""
        self.relationships: Dict[str, List[KGRelationship]] = defaultdict(list)
    
    def add_relationship(
        self,
        source: str,
        target: str,
        relationship_type: str,
        weight: float = 1.0
    ) -> KGRelationship:
        """Add a relationship to the graph."""
        rel = KGRelationship(
            source=source,
            target=target,
            relationship_type=relationship_type,
            weight=weight
        )
        
        self.relationships[source].append(rel)
        
        return rel
    
    def inject_context(
        self,
        sender_id: str,
        recipient_id: str
    ) -> KGContext:
        """
        Inject knowledge graph context.
        
        Args:
            sender_id: Sender identifier
            recipient_id: Recipient identifier
            
        Returns:
            KGContext with relationships
        """
        # Find relationships involving both parties
        sender_rels = self.relationships.get(sender_id, [])
        recipient_rels = self.relationships.get(recipient_id, [])
        
        # Find shared connections
        sender_targets = set(r.target for r in sender_rels)
        recipient_targets = set(r.target for r in recipient_rels)
        shared = list(sender_targets & recipient_targets)
        
        # Combine relevant relationships
        relevant_rels = [r for r in sender_rels if r.target in shared or r.target == recipient_id]
        relevant_rels.extend([r for r in recipient_rels if r.target in shared or r.target == sender_id])
        
        # Build context summary
        summary = self._build_summary(shared, relevant_rels)
        
        return KGContext(
            relationships=relevant_rels,
            shared_entities=shared,
            context_summary=summary
        )
    
    def _build_summary(
        self,
        shared: List[str],
        relationships: List[KGRelationship]
    ) -> str:
        """Build context summary."""
        parts = []
        
        if shared:
            parts.append(f"Shared connections: {', '.join(shared[:3])}")
        
        if relationships:
            rel_types = list(set(r.relationship_type for r in relationships))
            parts.append(f"Relationship types: {', '.join(rel_types[:3])}")
        
        return "; ".join(parts) if parts else "No shared context found"


# ============================================================================
# Few-Shot Injector
# ============================================================================

@dataclass
class FewShotExample:
    """Few-shot example"""
    example_id: str
    input_text: str
    output_text: str
    category: str
    quality_score: float


@dataclass
class FewShotInjectionResult:
    """Result of few-shot injection"""
    examples: List[FewShotExample]
    injection_text: str
    example_count: int


class FewShotInjector:
    """
    Few-Shot Example Injection
    
    Injects relevant few-shot examples for improved
    output quality.
    """
    
    def __init__(self):
        """Initialize few-shot injector."""
        self.examples: Dict[str, List[FewShotExample]] = defaultdict(list)
        self._load_default_examples()
    
    def add_example(
        self,
        category: str,
        input_text: str,
        output_text: str,
        quality_score: float = 0.8
    ) -> FewShotExample:
        """Add a few-shot example."""
        example = FewShotExample(
            example_id=f"ex_{category}_{len(self.examples[category])}",
            input_text=input_text,
            output_text=output_text,
            category=category,
            quality_score=quality_score
        )
        
        self.examples[category].append(example)
        
        return example
    
    def inject(
        self,
        category: str,
        count: int = 3
    ) -> FewShotInjectionResult:
        """
        Inject few-shot examples.
        
        Args:
            category: Example category
            count: Number of examples to inject
            
        Returns:
            FewShotInjectionResult with examples
        """
        category_examples = self.examples.get(category, [])
        
        # Sort by quality and select top examples
        sorted_examples = sorted(category_examples, key=lambda e: e.quality_score, reverse=True)
        selected = sorted_examples[:count]
        
        # Build injection text
        injection_parts = ["[EXAMPLES]"]
        for i, ex in enumerate(selected, 1):
            injection_parts.append(f"\nExample {i}:")
            injection_parts.append(f"Input: {ex.input_text}")
            injection_parts.append(f"Output: {ex.output_text}")
        injection_parts.append("\n[END EXAMPLES]")
        
        injection_text = "\n".join(injection_parts)
        
        return FewShotInjectionResult(
            examples=selected,
            injection_text=injection_text,
            example_count=len(selected)
        )
    
    def _load_default_examples(self) -> None:
        """Load default few-shot examples."""
        # Executive outreach examples
        self.add_example(
            "executive",
            "Write outreach to CTO about cloud migration",
            "I noticed your company's recent expansion into cloud infrastructure. My experience leading enterprise cloud migrations could help accelerate your roadmap while reducing risk.",
            0.9
        )
        
        # Technical outreach examples
        self.add_example(
            "technical",
            "Write outreach to senior engineer about microservices",
            "Your work with microservices architecture is impressive. I've built similar systems handling 10M+ requests daily and would love to share patterns that improved our reliability.",
            0.85
        )
        
        # Recruiter outreach examples
        self.add_example(
            "recruiter",
            "Write outreach to recruiter about engineering role",
            "I see you're focused on technical talent acquisition. With my background leading engineering teams, I can provide valuable context on assessing technical skills and culture fit.",
            0.8
        )


# ============================================================================
# builder Functions
# ============================================================================

def create_semantic_cache(
    max_entries: int = 1000,
    similarity_threshold: float = 0.85
) -> SemanticCache:
    """Create semantic cache instance."""
    return SemanticCache(max_entries=max_entries, similarity_threshold=similarity_threshold)


def create_self_rag_processor(max_iterations: int = 3) -> SelfRAGProcessor:
    """Create Self-RAG engine instance."""
    return SelfRAGProcessor(max_iterations=max_iterations)


def create_episodic_memory(max_episodes: int = 100) -> EpisodicMemory:
    """Create episodic memory instance."""
    return EpisodicMemory(max_episodes=max_episodes)


def create_kg_injector() -> KnowledgeGraphInjector:
    """Create knowledge graph injector instance."""
    return KnowledgeGraphInjector()


def create_few_shot_injector() -> FewShotInjector:
    """Create few-shot injector instance."""
    return FewShotInjector()
