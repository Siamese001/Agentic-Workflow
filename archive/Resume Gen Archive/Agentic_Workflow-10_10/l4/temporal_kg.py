"""
Stores and retrieves time-stamped career facts for accurate résumé timeline presentation.

Improves résumé chronology by maintaining precise dates, job transitions, and career progression data.
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

logger = logging.getLogger(__name__)


@dataclass
class TemporalFact:
    """
    Represents a time-stamped career fact like job changes, skill acquisitions, or promotions.

    Improves résumé accuracy by storing precise career events with dates and confidence levels.
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
        """
        Converts career fact data to storage format for database persistence and retrieval.

        Improves résumé data management by enabling reliable storage of job achievements and career events.
        """
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
    Defines searches for career facts within specific time periods and date ranges.

    Improves résumé analysis by enabling precise retrieval of job experiences and skills from relevant career stages.
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
    Manages time-stamped career data storage and retrieval for accurate résumé timeline presentation.

    Improves résumé chronology by maintaining precise dates, job transitions, and career progression information.
    """
    
    def __init__(self, pinecone_adapter: Any):
        """
        Sets up career timeline storage system with time-stamped fact management capabilities.

        Improves résumé data organization by configuring specialized storage for chronological career information.
        """
        self.adapter = pinecone_adapter
        self.namespace_prefix = "temporal_kg"
        
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
        """
        Stores career event with timestamp for accurate résumé timeline and job progression tracking.

        Improves résumé chronology by maintaining precise records of job changes, promotions, and skill acquisitions.
        """
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
        """
        Stores multiple career events efficiently for comprehensive résumé timeline management.

        Improves résumé processing speed by batch-adding job changes, skills, and achievements with timestamps.
        """
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
        """
        Retrieves career events within specific time periods for targeted résumé analysis.

        Improves résumé relevance by finding job experiences and skills from relevant career stages.
        """
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
        """
        Retrieves recent career activities for current résumé relevance and job matching.

        Improves résumé freshness by highlighting recent job experiences, skills, and career developments.
        """
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
        """
        Retrieves chronological career progression for comprehensive résumé timeline presentation.

        Improves résumé storytelling by showing skill development and career growth over time.
        """
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
        """
        Removes outdated career facts to maintain résumé accuracy and relevance.

        Improves résumé quality by eliminating obsolete job information and keeping career data current.
        """
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
    
    def _build_namespace(self, user_id: Optional[str]) -> str:
        """Build namespace for temporal KG storage."""
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
    """
    Creates a time-stamped skill acquisition record for résumé skill presentation.

    Improves résumé credibility by documenting when and at what level skills were acquired.
    """
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
    """
    Creates a time-stamped work experience record for résumé job history presentation.

    Improves résumé employment verification by documenting exact dates and roles for each company.
    """
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
    """
    Creates a time-stamped job application record for résumé job seeking activity tracking.

    Improves résumé job search documentation by maintaining accurate records of application timelines.
    """
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



