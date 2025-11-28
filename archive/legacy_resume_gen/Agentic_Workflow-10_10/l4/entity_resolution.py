"""Entity Resolution - Entity Linking and Disambiguation

This module implements entity resolution for the Temporal Knowledge Graph,
handling entity linking, deduplication, and canonical form management.

Layer: L4 (State & Memory)
Responsibilities:
- Maintain canonical entity registry
- Link entity mentions to canonical forms
- Track entity aliases and variants
- Support entity merging and splitting

Non-responsibilities:
- Named Entity Recognition (L2)
- Resolution planning (L1)
- Orchestration (L3)
- Policy enforcement (L5)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from datetime import datetime, UTC
from enum import Enum
import hashlib
import re


class EntityType(str, Enum):
    """Types of entities in the knowledge graph."""
    PERSON = "person"
    ORGANIZATION = "organization"
    SKILL = "skill"
    ROLE = "role"
    LOCATION = "location"
    EDUCATION = "education"
    CERTIFICATION = "certification"
    PROJECT = "project"
    UNKNOWN = "unknown"


@dataclass
class CanonicalEntity:
    """A canonical entity in the knowledge graph."""
    
    id: str
    canonical_name: str
    entity_type: EntityType
    
    # Aliases and variants
    aliases: Set[str] = field(default_factory=set)
    normalized_forms: Set[str] = field(default_factory=set)
    
    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    source: str = "system"
    confidence: float = 1.0
    
    # Relationships
    same_as: Set[str] = field(default_factory=set)  # Links to external KBs
    part_of: Optional[str] = None  # Parent entity ID
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_alias(self, alias: str) -> None:
        """Add an alias for this entity."""
        self.aliases.add(alias)
        self.normalized_forms.add(self._normalize(alias))
        self.updated_at = datetime.now(UTC)
    
    def matches(self, mention: str) -> bool:
        """Check if a mention matches this entity."""
        normalized = self._normalize(mention)
        if normalized == self._normalize(self.canonical_name):
            return True
        return normalized in self.normalized_forms
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "canonical_name": self.canonical_name,
            "entity_type": self.entity_type.value,
            "aliases": list(self.aliases),
            "normalized_forms": list(self.normalized_forms),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "source": self.source,
            "confidence": self.confidence,
            "same_as": list(self.same_as),
            "part_of": self.part_of,
            "metadata": self.metadata,
        }
    
    @staticmethod
    def _normalize(text: str) -> str:
        """Normalize text for matching."""
        # Lowercase, remove punctuation, normalize whitespace
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        text = ' '.join(text.split())
        return text


@dataclass
class EntityMention:
    """A mention of an entity in text."""
    
    id: str
    text: str
    entity_type: EntityType
    
    # Resolution
    resolved_entity_id: Optional[str] = None
    resolution_confidence: float = 0.0
    resolution_method: str = "unresolved"
    
    # Context
    source_document_id: Optional[str] = None
    start_offset: int = 0
    end_offset: int = 0
    context: str = ""
    
    # Metadata
    extracted_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResolutionResult:
    """Result of entity resolution."""
    
    mention: EntityMention
    resolved_entity: Optional[CanonicalEntity]
    confidence: float
    method: str
    candidates: List[Tuple[CanonicalEntity, float]] = field(default_factory=list)


class EntityRegistry:
    """Registry for canonical entities with resolution capabilities."""
    
    def __init__(self):
        """Initialize empty entity registry."""
        self._entities: Dict[str, CanonicalEntity] = {}
        self._name_index: Dict[str, Set[str]] = {}  # normalized_name -> entity_ids
        self._type_index: Dict[EntityType, Set[str]] = {}
        
        # Pre-populate common skill entities
        self._init_common_entities()
    
    def _init_common_entities(self) -> None:
        """Initialize common entities (skills, technologies)."""
        common_skills = [
            ("python", "Python", EntityType.SKILL),
            ("javascript", "JavaScript", EntityType.SKILL),
            ("typescript", "TypeScript", EntityType.SKILL),
            ("java", "Java", EntityType.SKILL),
            ("aws", "Amazon Web Services", EntityType.SKILL),
            ("azure", "Microsoft Azure", EntityType.SKILL),
            ("gcp", "Google Cloud Platform", EntityType.SKILL),
            ("docker", "Docker", EntityType.SKILL),
            ("kubernetes", "Kubernetes", EntityType.SKILL),
            ("react", "React", EntityType.SKILL),
            ("machine_learning", "Machine Learning", EntityType.SKILL),
            ("deep_learning", "Deep Learning", EntityType.SKILL),
            ("nlp", "Natural Language Processing", EntityType.SKILL),
            ("sql", "SQL", EntityType.SKILL),
            ("postgresql", "PostgreSQL", EntityType.SKILL),
            ("mongodb", "MongoDB", EntityType.SKILL),
        ]
        
        for entity_id, name, entity_type in common_skills:
            entity = CanonicalEntity(
                id=entity_id,
                canonical_name=name,
                entity_type=entity_type,
                source="system_init",
            )
            # Add common aliases
            entity.add_alias(name.lower())
            entity.add_alias(entity_id)
            self.register_entity(entity)
    
    def register_entity(self, entity: CanonicalEntity) -> str:
        """Register a canonical entity.
        
        Args:
            entity: Entity to register
            
        Returns:
            Entity ID
        """
        self._entities[entity.id] = entity
        
        # Index by normalized name
        normalized = CanonicalEntity._normalize(entity.canonical_name)
        self._add_to_index(self._name_index, normalized, entity.id)
        
        # Index aliases
        for alias in entity.aliases:
            normalized_alias = CanonicalEntity._normalize(alias)
            self._add_to_index(self._name_index, normalized_alias, entity.id)
        
        # Index by type
        if entity.entity_type not in self._type_index:
            self._type_index[entity.entity_type] = set()
        self._type_index[entity.entity_type].add(entity.id)
        
        return entity.id
    
    def get_entity(self, entity_id: str) -> Optional[CanonicalEntity]:
        """Get entity by ID.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            Entity or None
        """
        return self._entities.get(entity_id)
    
    def resolve(
        self,
        mention: EntityMention,
        threshold: float = 0.5,
    ) -> ResolutionResult:
        """Resolve an entity mention to a canonical entity.
        
        Args:
            mention: Entity mention to resolve
            threshold: Minimum confidence threshold
            
        Returns:
            Resolution result with candidates
        """
        candidates: List[Tuple[CanonicalEntity, float]] = []
        normalized = CanonicalEntity._normalize(mention.text)
        
        # Exact match lookup
        if normalized in self._name_index:
            for entity_id in self._name_index[normalized]:
                entity = self._entities.get(entity_id)
                if entity:
                    # Boost confidence for type match
                    confidence = 0.95
                    if mention.entity_type != EntityType.UNKNOWN and entity.entity_type == mention.entity_type:
                        confidence = 1.0
                    candidates.append((entity, confidence))
        
        # Fuzzy matching if no exact match
        if not candidates:
            candidates = self._fuzzy_match(mention, threshold)
        
        # Sort by confidence
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        # Build result
        resolved_entity = None
        confidence = 0.0
        method = "unresolved"
        
        if candidates and candidates[0][1] >= threshold:
            resolved_entity = candidates[0][0]
            confidence = candidates[0][1]
            method = "exact_match" if confidence >= 0.95 else "fuzzy_match"
        
        return ResolutionResult(
            mention=mention,
            resolved_entity=resolved_entity,
            confidence=confidence,
            method=method,
            candidates=candidates[:5],  # Top 5 candidates
        )
    
    def _fuzzy_match(
        self,
        mention: EntityMention,
        threshold: float,
    ) -> List[Tuple[CanonicalEntity, float]]:
        """Perform fuzzy matching for entity resolution.
        
        Args:
            mention: Entity mention
            threshold: Minimum confidence
            
        Returns:
            List of (entity, confidence) tuples
        """
        candidates = []
        mention_normalized = CanonicalEntity._normalize(mention.text)
        mention_tokens = set(mention_normalized.split())
        
        # Filter by type if specified
        entity_ids = self._type_index.get(mention.entity_type, set()) if mention.entity_type != EntityType.UNKNOWN else set(self._entities.keys())
        
        for entity_id in entity_ids:
            entity = self._entities.get(entity_id)
            if not entity:
                continue
            
            # Token overlap similarity
            entity_normalized = CanonicalEntity._normalize(entity.canonical_name)
            entity_tokens = set(entity_normalized.split())
            
            if not entity_tokens:
                continue
            
            # Jaccard similarity
            intersection = len(mention_tokens & entity_tokens)
            union = len(mention_tokens | entity_tokens)
            similarity = intersection / union if union > 0 else 0
            
            # Substring matching bonus
            if mention_normalized in entity_normalized or entity_normalized in mention_normalized:
                similarity = max(similarity, 0.7)
            
            if similarity >= threshold:
                candidates.append((entity, similarity))
        
        return candidates
    
    def merge_entities(
        self,
        primary_id: str,
        secondary_id: str,
        reason: str = "duplicate",
    ) -> Optional[CanonicalEntity]:
        """Merge two entities into one.
        
        Args:
            primary_id: ID of entity to keep
            secondary_id: ID of entity to merge into primary
            reason: Reason for merge
            
        Returns:
            Merged entity or None if invalid
        """
        primary = self._entities.get(primary_id)
        secondary = self._entities.get(secondary_id)
        
        if not primary or not secondary:
            return None
        
        # Merge aliases
        primary.aliases.update(secondary.aliases)
        primary.aliases.add(secondary.canonical_name)
        primary.normalized_forms.update(secondary.normalized_forms)
        
        # Merge same_as links
        primary.same_as.update(secondary.same_as)
        primary.same_as.add(f"merged:{secondary_id}")
        
        # Update metadata
        primary.metadata["merged_from"] = primary.metadata.get("merged_from", [])
        primary.metadata["merged_from"].append({
            "entity_id": secondary_id,
            "canonical_name": secondary.canonical_name,
            "reason": reason,
            "merged_at": datetime.now(UTC).isoformat(),
        })
        
        # Remove secondary from registry
        del self._entities[secondary_id]
        
        # Update indexes
        self._rebuild_indexes()
        
        return primary
    
    def get_entities_by_type(self, entity_type: EntityType) -> List[CanonicalEntity]:
        """Get all entities of a specific type.
        
        Args:
            entity_type: Type of entities to retrieve
            
        Returns:
            List of entities
        """
        entity_ids = self._type_index.get(entity_type, set())
        return [self._entities[eid] for eid in entity_ids if eid in self._entities]
    
    def search(
        self,
        query: str,
        entity_type: Optional[EntityType] = None,
        limit: int = 10,
    ) -> List[Tuple[CanonicalEntity, float]]:
        """Search for entities by name.
        
        Args:
            query: Search query
            entity_type: Optional type filter
            limit: Maximum results
            
        Returns:
            List of (entity, score) tuples
        """
        mention = EntityMention(
            id="search",
            text=query,
            entity_type=entity_type or EntityType.UNKNOWN,
        )
        result = self.resolve(mention, threshold=0.1)
        return result.candidates[:limit]
    
    def _rebuild_indexes(self) -> None:
        """Rebuild all indexes."""
        self._name_index.clear()
        self._type_index.clear()
        
        for entity in self._entities.values():
            # Name index
            normalized = CanonicalEntity._normalize(entity.canonical_name)
            self._add_to_index(self._name_index, normalized, entity.id)
            for alias in entity.aliases:
                normalized_alias = CanonicalEntity._normalize(alias)
                self._add_to_index(self._name_index, normalized_alias, entity.id)
            
            # Type index
            if entity.entity_type not in self._type_index:
                self._type_index[entity.entity_type] = set()
            self._type_index[entity.entity_type].add(entity.id)
    
    @staticmethod
    def _add_to_index(index: Dict[str, Set[str]], key: str, value: str) -> None:
        """Add value to index."""
        if key not in index:
            index[key] = set()
        index[key].add(value)
    
    def count(self) -> int:
        """Get count of registered entities."""
        return len(self._entities)


# =============================================================================
# Entity Creation Helpers
# =============================================================================

def create_entity(
    name: str,
    entity_type: EntityType,
    aliases: Optional[List[str]] = None,
    source: str = "extraction",
    metadata: Optional[Dict[str, Any]] = None,
) -> CanonicalEntity:
    """Create a new canonical entity.
    
    Args:
        name: Canonical name
        entity_type: Entity type
        aliases: Optional list of aliases
        source: Source of entity
        metadata: Additional metadata
        
    Returns:
        New CanonicalEntity
    """
    # Generate deterministic ID
    id_input = f"{entity_type.value}:{name.lower()}"
    entity_id = hashlib.sha256(id_input.encode()).hexdigest()[:16]
    
    entity = CanonicalEntity(
        id=entity_id,
        canonical_name=name,
        entity_type=entity_type,
        source=source,
        metadata=metadata or {},
    )
    
    # Add aliases
    if aliases:
        for alias in aliases:
            entity.add_alias(alias)
    
    return entity


def create_mention(
    text: str,
    entity_type: EntityType = EntityType.UNKNOWN,
    source_document_id: Optional[str] = None,
    context: str = "",
) -> EntityMention:
    """Create an entity mention.
    
    Args:
        text: Mention text
        entity_type: Entity type hint
        source_document_id: Source document
        context: Surrounding context
        
    Returns:
        New EntityMention
    """
    mention_id = hashlib.sha256(
        f"{text}:{source_document_id}:{datetime.now(UTC).isoformat()}".encode()
    ).hexdigest()[:16]
    
    return EntityMention(
        id=mention_id,
        text=text,
        entity_type=entity_type,
        source_document_id=source_document_id,
        context=context,
    )


__all__ = [
    "EntityType",
    "CanonicalEntity",
    "EntityMention",
    "ResolutionResult",
    "EntityRegistry",
    "create_entity",
    "create_mention",
]
