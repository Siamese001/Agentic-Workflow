"""
L4 temporal knowledge graph for resume job alignment workflows.

Stores time-stamped career facts for accurate resume timeline enhancement.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime, UTC
import hashlib
import logging

try:
    from graph_store_neo4j import Neo4jGraphStore as _Neo4jGraphStore
    _NEO4J_AVAILABLE = True
except ImportError:
    _Neo4jGraphStore = object  # type: ignore
    _NEO4J_AVAILABLE = False

# Import L4 temporal components for orchestration
from .temporal_fusion import TemporalRankFusion
from .high_signal import HighSignalScorer

logger = logging.getLogger(__name__)


@dataclass
class TemporalNodeMetadata:
    """Metadata for temporal knowledge graph nodes."""
    timestamp: datetime
    source: str
    weight: float
    hop_distance: int
    recency_days: Optional[int] = None
    within_window: bool = False


@dataclass
class TemporalFact:
    """
    Represents time-stamped career fact for resume job alignment.

    Improves resume accuracy by storing precise career events with dates.
    """
    
    id: str
    subject: str  # e.g., "user_123", "job_456"
    predicate: str  # e.g., "has_skill", "worked_at", "applied_to"
    object: str  # e.g., "Python", "Google", "job_789"
    timestamp: datetime
    confidence: float = 1.0
    source: str = "system"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_text(self) -> str:
        """
        Converts career fact data to readable text for résumé bullet point presentation.

        Improves résumé readability by presenting structured career data as natural language achievements.
        """
        return f"{self.subject} {self.predicate} {self.object} (at {self.timestamp.isoformat()})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Converts career fact data to storage format for resume processing."""
        return {
            "id": self.id,
            "subject": self.subject,
            "predicate": self.predicate,
            "object": self.object,
            "timestamp": self.timestamp.isoformat(),
            "confidence": self.confidence,
            "source": self.source,
            "metadata": self.metadata,
        }


@dataclass
class TemporalQuery:
    """
    Defines searches for career facts within time periods for resume alignment.

    Enables precise retrieval of job experiences and skills for resume enhancement.
    """
    
    subject: Optional[str] = None
    predicate: Optional[str] = None
    object: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    min_confidence: float = 0.0
    limit: int = 100


class TemporalKG:
    """
    Manages time-stamped career data for resume job alignment workflows.

    Improves resume chronology by maintaining precise career progression data.
    """
    
    def __init__(self, pinecone_adapter: Any):
        """Sets up career timeline storage for resume job alignment processing."""
        self.adapter = pinecone_adapter
        self.namespace_prefix = "temporal_kg"
        
        # Initialize temporal components for orchestration
        self.temporal_fusion = TemporalRankFusion()
        self.high_signal_scorer = HighSignalScorer()
        
        # Initialize Neo4j graph store if available
        self.neo4j = None
        if _NEO4J_AVAILABLE:
            try:
                self.neo4j = _Neo4jGraphStore()
            except Exception as e:
                logger.warning(f"Failed to initialize Neo4j graph store: {e}")
                self.neo4j = None
    
    def add_fact(
        self,
        fact: TemporalFact,
        user_id: Optional[str] = None,
    ) -> None:
        """Stores career event with timestamp for resume timeline enhancement."""
        namespace = self._build_namespace(user_id)
        fact_dict = fact.to_dict()
        
        # Store in primary datastore
        self.adapter.upsert_text_records(
            texts=[fact.to_text()],
            namespace=namespace,
            ids=[fact.id],
            metadata_list=[fact_dict],
        )
        
        # Mirror to Neo4j if available
        if self.neo4j is not None:
            try:
                # Extract subject, predicate, object from fact
                # This assumes the fact content follows "subject predicate object" format
                parts = fact.to_text().split()
                if len(parts) >= 3:
                    subject = parts[0]
                    predicate = parts[1]
                    obj = ' '.join(parts[2:])
                    
                    # Upsert subject entity
                    self.neo4j.upsert_entity(
                        entity_id=f"{subject}_{user_id or 'global'}",
                        etype="PERSON" if user_id else "ENTITY",
                        name=subject,
                        metadata={"source": "temporal_kg", "user_id": user_id or "global"}
                    )
                    
                    # Upsert object entity
                    self.neo4j.upsert_entity(
                        entity_id=f"{obj}_{user_id or 'global'}",
                        etype=predicate.upper() if predicate.upper() in ["SKILL", "COMPANY", "ROLE"] else "ENTITY",
                        name=obj,
                        metadata={"source": "temporal_kg", "user_id": user_id or "global"}
                    )
                    
                    # Create relationship
                    self.neo4j.upsert_relation(
                        rel_id=fact.id,
                        subject_id=f"{subject}_{user_id or 'global'}",
                        predicate=predicate.upper(),
                        object_id=f"{obj}_{user_id or 'global'}",
                        valid_at=fact.timestamp.isoformat() if hasattr(fact, 'timestamp') else None,
                        invalid_at=None,  # Will be set on invalidation
                        attrs={
                            "confidence": fact.confidence,
                            "source": fact.source,
                            **fact.metadata
                        }
                    )
            except Exception as e:
                logger.error(f"Failed to mirror fact to Neo4j: {e}", exc_info=True)
    
    def add_facts(
        self,
        facts: List[TemporalFact],
        user_id: Optional[str] = None,
    ) -> None:
        """Stores multiple career events efficiently for resume processing."""
        if not facts:
            return
        
        namespace = self._build_namespace(user_id)
        
        # Convert facts to texts and metadata
        texts = [f.to_text() for f in facts]
        ids = [f.id for f in facts]
        metadata_list = [
            {
                "subject": f.subject,
                "predicate": f.predicate,
                "object": f.object,
                "timestamp": f.timestamp.isoformat(),
                "confidence": f.confidence,
                "source": f.source,
                "text": f.to_text(),
                **f.metadata
            }
            for f in facts
        ]
        
        # Batch upsert
        self.adapter.upsert_text_records(
            texts=texts,
            namespace=namespace,
            ids=ids,
            metadata_list=metadata_list,
        )
        
        # Mirror to Neo4j if available
        if self.neo4j is not None:
            for fact in facts:
                try:
                    # Extract subject, predicate, object from fact
                    parts = fact.to_text().split()
                    if len(parts) >= 3:
                        subject = parts[0]
                        predicate = parts[1]
                        obj = ' '.join(parts[2:])
                        
                        # Upsert subject entity
                        self.neo4j.upsert_entity(
                            entity_id=f"{subject}_{user_id or 'global'}",
                            etype="PERSON" if user_id else "ENTITY",
                            name=subject,
                            metadata={"source": "temporal_kg", "user_id": user_id or "global"}
                        )
                        
                        # Upsert object entity
                        self.neo4j.upsert_entity(
                            entity_id=f"{obj}_{user_id or 'global'}",
                            etype=predicate.upper() if predicate.upper() in ["SKILL", "COMPANY", "ROLE"] else "ENTITY",
                            name=obj,
                            metadata={"source": "temporal_kg", "user_id": user_id or "global"}
                        )
                        
                        # Create relationship
                        self.neo4j.upsert_relation(
                            rel_id=fact.id,
                            subject_id=f"{subject}_{user_id or 'global'}",
                            predicate=predicate.upper(),
                            object_id=f"{obj}_{user_id or 'global'}",
                            valid_at=fact.timestamp.isoformat() if hasattr(fact, 'timestamp') else None,
                            invalid_at=None,  # Will be set on invalidation
                            attrs={
                                "confidence": fact.confidence,
                                "source": fact.source,
                                **fact.metadata
                            }
                        )
                except Exception as e:
                    logger.error(f"Failed to mirror fact to Neo4j: {e}", exc_info=True)
    
    def query_facts(
        self,
        query: TemporalQuery,
        user_id: Optional[str] = None,
    ) -> List[TemporalFact]:
        """Retrieves career events within time periods for resume analysis."""
        namespace = self._build_namespace(user_id)
        
        # Build search query text
        query_parts = []
        if query.subject:
            query_parts.append(query.subject)
        if query.predicate:
            query_parts.append(query.predicate)
        if query.object:
            query_parts.append(query.object)
        
        query_text = " ".join(query_parts) if query_parts else "temporal facts"
        
        # Build metadata filter
        filter_dict: Dict[str, Any] = {}
        
        if query.subject:
            filter_dict["subject"] = {"$eq": query.subject}
        if query.predicate:
            filter_dict["predicate"] = {"$eq": query.predicate}
        if query.object:
            filter_dict["object"] = {"$eq": query.object}
        if query.min_confidence > 0:
            filter_dict["confidence"] = {"$gte": query.min_confidence}
        
        # Add temporal filter
        if query.start_time and query.end_time:
            filter_dict["timestamp"] = {
                "$gte": query.start_time.isoformat(),
                "$lte": query.end_time.isoformat(),
            }
        elif query.start_time:
            filter_dict["timestamp"] = {"$gte": query.start_time.isoformat()}
        elif query.end_time:
            filter_dict["timestamp"] = {"$lte": query.end_time.isoformat()}
        
        # Execute query
        try:
            results = self.adapter.query_by_text(
                query_text=query_text,
                namespace=namespace,
                top_k=query.limit,
                filter_dict=filter_dict if filter_dict else None,
            )
            
            # Convert results to TemporalFacts
            facts = []
            for r in results:
                try:
                    fact = TemporalFact(
                        id=r.id,
                        subject=r.metadata.get("subject", ""),
                        predicate=r.metadata.get("predicate", ""),
                        object=r.metadata.get("object", ""),
                        timestamp=datetime.fromisoformat(r.metadata.get("timestamp", datetime.now(UTC).isoformat())),
                        confidence=r.metadata.get("confidence", 1.0),
                        source=r.metadata.get("source", "system"),
                        metadata={k: v for k, v in r.metadata.items() if k not in ["subject", "predicate", "object", "timestamp", "confidence", "source", "text"]},
                    )
                    facts.append(fact)
                except Exception:
                    continue
            
            return facts
        except Exception:
            return []
    
    def get_recent_facts(
        self,
        subject: str,
        days: int = 30,
        user_id: Optional[str] = None,
    ) -> List[TemporalFact]:
        """Retrieves recent career activities for resume job alignment."""
        from datetime import timedelta
        
        end_time = datetime.now(UTC)
        start_time = end_time - timedelta(days=days)
        
        query = TemporalQuery(
            subject=subject,
            start_time=start_time,
            end_time=end_time,
        )
        
        return self.query_facts(query, user_id)
    
    def get_fact_history(
        self,
        subject: str,
        predicate: str,
        user_id: Optional[str] = None,
    ) -> List[TemporalFact]:
        """Retrieves chronological career progression for resume timeline."""
        query = TemporalQuery(
            subject=subject,
            predicate=predicate,
        )
        
        facts = self.query_facts(query, user_id)
        
        # Sort by timestamp (ascending)
        facts.sort(key=lambda f: f.timestamp)
        
        return facts
    
    def delete_facts(
        self,
        fact_ids: List[str],
        user_id: Optional[str] = None,
    ) -> None:
        """Removes outdated career facts to maintain resume accuracy."""
        if not fact_ids:
            return
        
        namespace = self._build_namespace(user_id)
        
        # Delete from primary datastore
        self.adapter.delete_records(
            ids=fact_ids,
            namespace=namespace,
        )
        
        # Mark as invalid in Neo4j if available
        if self.neo4j is not None:
            for fact_id in fact_ids:
                try:
                    self.neo4j.update_relation_invalidity(
                        rel_id=fact_id,
                        invalid_at=datetime.now(UTC).isoformat(),
                        invalidated_by=f"user_{user_id or 'system'}"
                    )
                except Exception as e:
                    logger.error(f"Failed to invalidate fact in Neo4j: {e}", exc_info=True)
    
    def compute_temporal_weight(self, timestamp: datetime) -> float:
        """Compute temporal weight based on age of the timestamp."""
        from datetime import timedelta
        
        now = datetime.now(UTC)
        age_days = (now - timestamp).days
        
        if age_days <= 30:
            return 1.0
        elif age_days <= 90:
            return 0.6
        elif age_days <= 180:
            return 0.2
        else:
            return 0.05
    
    def apply_hop_distance_penalty(self, base_weight: float, hop_distance: int) -> float:
        """Apply hop distance penalty to temporal weight."""
        if hop_distance == 0:
            return base_weight
        elif hop_distance == 1:
            return base_weight * 0.8
        elif hop_distance == 2:
            return base_weight * 0.6
        elif hop_distance == 3:
            return base_weight * 0.4
        else:
            return base_weight * 0.2  # Maximum penalty for >3 hops
    
    def search_temporal(self, query: str, hops: int = 1, user_id: Optional[str] = None) -> List[TemporalNodeMetadata]:
        """
        Search temporal KG with multi-hop traversal.
        
        Args:
            query: Search query string
            hops: Number of hops to traverse (1-3)
            user_id: Optional user ID for namespace isolation
            
        Returns:
            List of TemporalNodeMetadata objects
        """
        if hops < 1 or hops > 3:
            logger.warning(f"Invalid hop count {hops}, using 1")
            hops = 1
        
        # Create temporal query for base search
        temporal_query = TemporalQuery(
            object=query,  # Search for query in object field
            limit=50  # Limit results for performance
        )
        
        # Get base facts
        base_facts = self.query_facts(temporal_query, user_id)
        
        # Convert to TemporalNodeMetadata
        results = []
        for fact in base_facts:
            # Compute temporal weight
            temporal_weight = self.compute_temporal_weight(fact.timestamp)
            
            # Apply hop distance penalty
            adjusted_weight = self.apply_hop_distance_penalty(temporal_weight, hops - 1)
            
            metadata = TemporalNodeMetadata(
                timestamp=fact.timestamp,
                source=fact.source,
                weight=adjusted_weight,
                hop_distance=hops - 1
            )
            
            results.append(metadata)
        
        # Sort by weight (descending) and timestamp (descending for ties)
        results.sort(key=lambda m: (m.weight, m.timestamp), reverse=True)
        
        return results[:20]  # Return top 20 results
    
    def execute_temporal_retrieval(self, query: str, hybrid_results: Optional[List[str]] = None, 
                                  temporal_window_days: Optional[int] = None, 
                                  max_results: int = 10) -> Dict[str, Any]:
        """
        Execute complete temporal retrieval orchestration extracted from RAGEngine.
        
        This method extracts the temporal logic orchestration from RAGEngine._execute_retrieval()
        to provide L4 purity and modular temporal processing.
        
        Args:
            query: Search query string
            hybrid_results: Optional list of hybrid search result texts
            temporal_window_days: Optional temporal window constraint
            max_results: Maximum number of results to return
            
        Returns:
            Dictionary with fused scores, metadata, and temporal analysis
        """
        try:
            # Initialize result containers
            hybrid_scores = []
            kg_scores = []
            temporal_scores = []
            results_text = []
            metadata_list = []
            
            # Process hybrid search results if provided
            if hybrid_results:
                results_text = hybrid_results
                # Generate mock hybrid scores (in real implementation, would come from hybrid search)
                hybrid_scores = [0.8 - (i * 0.05) for i in range(len(hybrid_results))]
                
                # Create metadata for each result
                for i, text in enumerate(hybrid_results):
                    metadata_list.append({
                        'source': 'hybrid',
                        'timestamp': datetime.now(UTC),
                        'index': i
                    })
            
            # Search temporal KG with recency filtering
            temporal_metadata = self.search_temporal(
                query=query,
                hops=1,
                user_id=None
            )
            
            # Apply temporal window filtering if specified
            if temporal_window_days:
                now = datetime.now(UTC)
                filtered_metadata = []
                for metadata in temporal_metadata:
                    # Handle None timestamps gracefully
                    if metadata.timestamp is None:
                        metadata.recency_days = None
                        metadata.within_window = False
                        continue
                    
                    age_days = (now - metadata.timestamp).days
                    metadata.recency_days = age_days
                    metadata.within_window = age_days <= temporal_window_days
                    if metadata.within_window:
                        filtered_metadata.append(metadata)
                temporal_metadata = filtered_metadata
            else:
                # Set recency metadata even without window
                now = datetime.now(UTC)
                for metadata in temporal_metadata:
                    # Handle None timestamps gracefully
                    if metadata.timestamp is None:
                        metadata.recency_days = None
                        metadata.within_window = False
                    else:
                        metadata.recency_days = (now - metadata.timestamp).days
                        metadata.within_window = True
            
            # Extract KG scores from temporal metadata
            kg_scores = [m.weight for m in temporal_metadata]
            
            # Compute high-signal scores for all results
            temporal_scores = []
            for text in results_text:
                signal_score = self.high_signal_scorer.compute_signal_score(text)
                temporal_scores.append(signal_score.score)
            
            # Apply TemporalRankFusion with tie-break rules
            # Only apply fusion when we have actual KG temporal facts (not just signal scores)
            fusion_applied = False
            if hybrid_scores and len(kg_scores) > 0:
                # Create enhanced metadata for tie-breaking
                enhanced_metadata = []
                for i, meta in enumerate(metadata_list):
                    # Add temporal score to metadata if available
                    if i < len(temporal_scores):
                        meta['temporal_score'] = temporal_scores[i]
                    enhanced_metadata.append(meta)
                
                try:
                    # Use tie-break fusion for deterministic results
                    fused_results = self.temporal_fusion.fuse_with_tiebreak(
                        hybrid_scores, kg_scores, temporal_scores, enhanced_metadata
                    )
                    fused_scores = [item['score'] for item in fused_results]
                    final_metadata = [item['metadata'] for item in fused_results]
                    fusion_applied = True
                except Exception as fusion_error:
                    logger.warning(f"Temporal fusion failed: {fusion_error}")
                    # Fallback to hybrid scores only
                    fused_scores = hybrid_scores
                    final_metadata = metadata_list
                    fusion_applied = False
            else:
                # Fallback to hybrid scores only
                fused_scores = hybrid_scores
                final_metadata = metadata_list
                fusion_applied = False
            
            # Create enriched results
            enriched_results = []
            for i, text in enumerate(results_text):
                if i < len(fused_scores):
                    result = {
                        'text': text,
                        'score': fused_scores[i],
                        'metadata': final_metadata[i] if i < len(final_metadata) else {},
                        'temporal_analysis': {
                            'has_temporal_signal': i < len(temporal_scores) and temporal_scores[i] > 0.7,
                            'recency_available': i < len(final_metadata) and 'timestamp' in final_metadata[i],
                            'signal_score': temporal_scores[i] if i < len(temporal_scores) else 0.0
                        }
                    }
                    enriched_results.append(result)
            
            return {
                'results': enriched_results[:max_results],
                'fusion_applied': fusion_applied,
                'temporal_window_applied': temporal_window_days is not None,
                'temporal_facts_found': len(temporal_metadata),
                'high_signal_count': sum(1 for score in temporal_scores if score > 0.7)
            }
            
        except Exception as e:
            logger.warning(f"Temporal retrieval orchestration failed: {e}")
            # Safe fallback for negative path testing
            return {
                'results': [],
                'fusion_applied': False,
                'temporal_window_applied': False,
                'temporal_facts_found': 0,
                'high_signal_count': 0,
                'error': str(e)
            }
    
    def _build_namespace(self, user_id: Optional[str]) -> str:
        """Builds namespace for resume workflow temporal KG storage."""
        if user_id:
            return f"{self.namespace_prefix}_{user_id}"
        return self.namespace_prefix


# =============================================================================
# Convenience Functions
# =============================================================================


def create_skill_fact(
    user_id: str,
    skill: str,
    proficiency: str = "intermediate",
    timestamp: Optional[datetime] = None,
) -> TemporalFact:
    """Creates time-stamped skill acquisition record for resume enhancement."""
    if timestamp is None:
        timestamp = datetime.now(UTC)
    
    fact_id = hashlib.sha256(
        f"{user_id}_has_skill_{skill}_{timestamp.isoformat()}".encode()
    ).hexdigest()[:16]
    
    return TemporalFact(
        id=fact_id,
        subject=user_id,
        predicate="has_skill",
        object=skill,
        timestamp=timestamp,
        metadata={"proficiency": proficiency},
    )


def create_experience_fact(
    user_id: str,
    company: str,
    role: str,
    timestamp: Optional[datetime] = None,
) -> TemporalFact:
    """Creates time-stamped work experience record for resume enhancement."""
    if timestamp is None:
        timestamp = datetime.now(UTC)
    
    fact_id = hashlib.sha256(
        f"{user_id}_worked_at_{company}_{timestamp.isoformat()}".encode()
    ).hexdigest()[:16]
    
    return TemporalFact(
        id=fact_id,
        subject=user_id,
        predicate="worked_at",
        object=company,
        timestamp=timestamp,
        metadata={"role": role},
    )


def create_application_fact(
    user_id: str,
    job_id: str,
    status: str = "applied",
    timestamp: Optional[datetime] = None,
) -> TemporalFact:
    """Creates time-stamped job application record for resume enhancement."""
    if timestamp is None:
        timestamp = datetime.now(UTC)
    
    fact_id = hashlib.sha256(
        f"{user_id}_applied_to_{job_id}_{timestamp.isoformat()}".encode()
    ).hexdigest()[:16]
    
    return TemporalFact(
        id=fact_id,
        subject=user_id,
        predicate="applied_to",
        object=job_id,
        timestamp=timestamp,
        metadata={"status": status},
    )



