"""Temporal Knowledge Graph - Time-aware fact storage and retrieval

This module implements temporal knowledge graph functionality for storing
and retrieving time-stamped facts about candidates, jobs, and workflows.

Phase F: Temporal KG Integration
- Store time-stamped facts
- Retrieve facts by time range
- Track fact evolution over time
- Support temporal reasoning

Layer: L4 (State & Memory)
Responsibilities:
- Store temporal facts in vector store
- Retrieve facts by time range
- Track fact versions and updates
- Provide temporal context for planning

Non-responsibilities:
- Planning (L1)
- Execution (L2)
- Orchestration (L3)
- Policy enforcement (L5)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
import hashlib
import json


@dataclass
class TemporalFact:
    """A time-stamped fact in the knowledge graph."""
    
    id: str
    subject: str  # e.g., "user_123", "job_456"
    predicate: str  # e.g., "has_skill", "worked_at", "applied_to"
    object: str  # e.g., "Python", "Google", "job_789"
    timestamp: datetime
    confidence: float = 1.0
    source: str = "system"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_text(self) -> str:
        """Convert fact to natural language text."""
        return f"{self.subject} {self.predicate} {self.object} (at {self.timestamp.isoformat()})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert fact to dictionary for storage."""
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
    """Query for temporal facts."""
    
    subject: Optional[str] = None
    predicate: Optional[str] = None
    object: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    min_confidence: float = 0.0
    limit: int = 100


class TemporalKG:
    """Temporal Knowledge Graph backed by Pinecone."""
    
    def __init__(self, pinecone_adapter: Any):
        """Initialize with Pinecone adapter.
        
        Args:
            pinecone_adapter: L4 PineconeAdapter instance
        """
        self.adapter = pinecone_adapter
        self.namespace_prefix = "temporal_kg"
    
    def add_fact(
        self,
        fact: TemporalFact,
        user_id: Optional[str] = None,
    ) -> None:
        """Add a temporal fact to the knowledge graph.
        
        Args:
            fact: Temporal fact to add
            user_id: Optional user ID for namespace isolation
        """
        namespace = self._build_namespace(user_id)
        
        # Convert fact to text for embedding
        fact_text = fact.to_text()
        
        # Build metadata
        metadata = {
            "subject": fact.subject,
            "predicate": fact.predicate,
            "object": fact.object,
            "timestamp": fact.timestamp.isoformat(),
            "confidence": fact.confidence,
            "source": fact.source,
            "text": fact_text,
            **fact.metadata,
        }
        
        # Upsert to Pinecone
        self.adapter.upsert_text_records(
            texts=[fact_text],
            namespace=namespace,
            ids=[fact.id],
            metadata_list=[metadata],
        )
    
    def add_facts(
        self,
        facts: List[TemporalFact],
        user_id: Optional[str] = None,
    ) -> None:
        """Add multiple temporal facts in batch.
        
        Args:
            facts: List of temporal facts to add
            user_id: Optional user ID for namespace isolation
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
                **f.metadata,
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
    
    def query_facts(
        self,
        query: TemporalQuery,
        user_id: Optional[str] = None,
    ) -> List[TemporalFact]:
        """Query temporal facts from the knowledge graph.
        
        Args:
            query: Temporal query specification
            user_id: Optional user ID for namespace isolation
            
        Returns:
            List of matching temporal facts
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
                        timestamp=datetime.fromisoformat(r.metadata.get("timestamp", datetime.utcnow().isoformat())),
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
        days: int = 90,
        user_id: Optional[str] = None,
    ) -> List[TemporalFact]:
        """Get recent facts about a subject.
        
        Args:
            subject: Subject to query (e.g., "user_123")
            days: Number of days to look back
            user_id: Optional user ID for namespace isolation
            
        Returns:
            List of recent temporal facts
        """
        from datetime import timedelta
        
        end_time = datetime.utcnow()
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
        """Get the history of a specific fact over time.
        
        Args:
            subject: Subject of the fact
            predicate: Predicate of the fact
            user_id: Optional user ID for namespace isolation
            
        Returns:
            List of temporal facts sorted by timestamp (ascending)
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
        """Delete temporal facts by ID.
        
        Args:
            fact_ids: List of fact IDs to delete
            user_id: Optional user ID for namespace isolation
        """
        if not fact_ids:
            return
        
        namespace = self._build_namespace(user_id)
        
        try:
            self.adapter.delete_records(
                ids=fact_ids,
                namespace=namespace,
            )
        except Exception:
            pass
    
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
    """Create a skill fact."""
    if timestamp is None:
        timestamp = datetime.utcnow()
    
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
    """Create an experience fact."""
    if timestamp is None:
        timestamp = datetime.utcnow()
    
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
    """Create an application fact."""
    if timestamp is None:
        timestamp = datetime.utcnow()
    
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
