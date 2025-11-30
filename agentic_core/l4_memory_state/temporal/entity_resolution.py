"""Entity resolution for temporal knowledge graph operations."""
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class EntityType(Enum):
    """Entity type enumeration."""
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    SKILL = "skill"
    PROJECT = "project"
    TECHNOLOGY = "technology"
    CONCEPT = "concept"
    UNKNOWN = "unknown"

@dataclass
class Entity:
    """Knowledge graph entity with temporal metadata."""
    id: str = ""
    name: str = ""
    entity_type: EntityType = EntityType.UNKNOWN
    canonical_name: str = ""
    aliases: Set[str] = field(default_factory=set)
    properties: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.8
    source: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    valid_from: datetime = field(default_factory=datetime.now)
    valid_until: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.id:
            self.id = f"entity_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(self.name)}"
        if not self.canonical_name:
            self.canonical_name = self.name

@dataclass
class Mention:
    """Entity mention in text with temporal context."""
    id: str = ""
    entity_id: str = ""
    text: str = ""
    context: str = ""
    document_id: str = ""
    position: int = 0
    confidence: float = 0.8
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.id:
            self.id = f"mention_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(self.text)}"

class EntityRegistry:
    """Entity registry for temporal knowledge graph operations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize entity registry with configuration."""
        self.config = config or {}
        self.entities = {}
        self.mentions = {}
        self.name_index = {}
        self.alias_index = {}
        self.type_index = {}
        self.stats = {
            "total_entities": 0,
            "total_mentions": 0,
            "entities_by_type": {},
            "last_resolution_time": 0.0,
            "resolution_count": 0
        }
    
    def add_entity(self, entity: Entity) -> bool:
        """Add an entity to the registry."""
        if entity.id in self.entities:
            return False
        
        # Store entity
        self.entities[entity.id] = entity
        
        # Update indexes
        self._update_entity_indexes(entity, "add")
        
        # Update stats
        self.stats["total_entities"] += 1
        type_key = entity.entity_type.value
        self.stats["entities_by_type"][type_key] = self.stats["entities_by_type"].get(type_key, 0) + 1
        
        return True
    
    def register_entity(self, entity: Entity) -> bool:
        """Register an entity (alias for add_entity)."""
        return self.add_entity(entity)
    
    def add_mention(self, mention: Mention) -> bool:
        """Add a mention to the registry."""
        if mention.id in self.mentions:
            return False
        
        # Validate entity exists
        if mention.entity_id not in self.entities:
            return False
        
        # Store mention
        self.mentions[mention.id] = mention
        
        # Update stats
        self.stats["total_mentions"] += 1
        
        return True
    
    def resolve_entity(self, name: str, entity_type: Optional[EntityType] = None) -> Optional[Entity]:
        """Resolve an entity by name and optionally type."""
        start_time = datetime.now()
        
        # Try exact name match first
        if name in self.name_index:
            candidates = [self.entities[entity_id] for entity_id in self.name_index[name]]
            
            # Filter by type if specified
            if entity_type:
                candidates = [e for e in candidates if e.entity_type == entity_type]
            
            if candidates:
                # Return highest confidence candidate
                resolved = max(candidates, key=lambda e: e.confidence)
                self._update_resolution_stats(start_time)
                return resolved
        
        # Try alias matches
        if name in self.alias_index:
            candidates = [self.entities[entity_id] for entity_id in self.alias_index[name]]
            
            # Filter by type if specified
            if entity_type:
                candidates = [e for e in candidates if e.entity_type == entity_type]
            
            if candidates:
                # Return highest confidence candidate
                resolved = max(candidates, key=lambda e: e.confidence)
                self._update_resolution_stats(start_time)
                return resolved
        
        # No match found
        self._update_resolution_stats(start_time)
        return None
    
    def get_entity_by_id(self, entity_id: str) -> Optional[Entity]:
        """Get a specific entity by ID."""
        return self.entities.get(entity_id)
    
    def get_entities_by_type(self, entity_type: EntityType) -> List[Entity]:
        """Get all entities of a specific type."""
        if entity_type.value in self.type_index:
            return [self.entities[entity_id] for entity_id in self.type_index[entity_type.value]]
        return []
    
    def get_entity_mentions(self, entity_id: str) -> List[Mention]:
        """Get all mentions for a specific entity."""
        return [mention for mention in self.mentions.values() if mention.entity_id == entity_id]
    
    def _update_entity_indexes(self, entity: Entity, operation: str) -> None:
        """Update indexes when adding or removing entities."""
        if operation == "add":
            # Name index
            if entity.canonical_name not in self.name_index:
                self.name_index[entity.canonical_name] = set()
            self.name_index[entity.canonical_name].add(entity.id)
            
            # Alias index
            for alias in entity.aliases:
                if alias not in self.alias_index:
                    self.alias_index[alias] = set()
                self.alias_index[alias].add(entity.id)
            
            # Type index
            if entity.entity_type.value not in self.type_index:
                self.type_index[entity.entity_type.value] = set()
            self.type_index[entity.entity_type.value].add(entity.id)
    
    def _update_resolution_stats(self, start_time: datetime) -> None:
        """Update resolution statistics."""
        resolution_time = (datetime.now() - start_time).total_seconds()
        self.stats["last_resolution_time"] = resolution_time
        self.stats["resolution_count"] += 1

def create_entity(name: str, entity_type: EntityType = EntityType.UNKNOWN,
                 canonical_name: str = "", aliases: List[str] = None,
                 properties: Dict[str, Any] = None, confidence: float = 0.8,
                 source: str = "") -> Entity:
    """Factory function to create an entity."""
    return Entity(
        name=name,
        entity_type=entity_type,
        canonical_name=canonical_name or name,
        aliases=set(aliases or []),
        properties=properties or {},
        confidence=confidence,
        source=source
    )

def create_mention(entity_id: str = "", text: str = "", entity_type: EntityType = None,
                  context: str = "", document_id: str = "", position: int = 0,
                  confidence: float = 0.8) -> Mention:
    """Factory function to create a mention."""
    return Mention(
        entity_id=entity_id,
        text=text,
        context=context,
        document_id=document_id,
        position=position,
        confidence=confidence
    )

# Remove the duplicate create_mention class that was at the end
class create_mention:
    """create_mention implementation"""

    def __init__(self):
        pass

    def process(self, *args, **kwargs) -> Any:
        """Process method"""
        return {"processed": True}
