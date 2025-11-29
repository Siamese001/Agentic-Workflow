#!/usr/bin/env python3
"""
KG Relation Expand Tool
Section 5: Tool Contracts - KG tool family
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class KGRelationExpandTool:
    """Expand related entities/edges in knowledge graph"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.max_relations = self.config.get("max_relations", 20)
        self.bidirectional = self.config.get("bidirectional", True)
    
    def expand_relations(self, entity: str, relation_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Expand relations for a given entity"""
        try:
            # Simulate entity relations
            entity_relations = {
                "Software Engineer": {
                    "Python": {"relation": "uses_skill", "confidence": 0.9},
                    "AWS": {"relation": "has_experience", "confidence": 0.8},
                    "TechCorp": {"relation": "employed_by", "confidence": 1.0}
                },
                "Python": {
                    "Software Engineer": {"relation": "used_by_role", "confidence": 0.9},
                    "Django": {"relation": "has_framework", "confidence": 0.8},
                    "Data Science": {"relation": "used_in_field", "confidence": 0.7}
                }
            }
            
            relations = entity_relations.get(entity, {})
            
            # Filter by relation types if specified
            if relation_types:
                relations = {
                    target: rel_data for target, rel_data in relations.items()
                    if rel_data["relation"] in relation_types
                }
            
            # Format results
            expanded_relations = []
            for target, rel_data in relations.items():
                expanded_relations.append({
                    "source_entity": entity,
                    "target_entity": target,
                    "relation": rel_data["relation"],
                    "confidence": rel_data["confidence"]
                })
            
            # Sort by confidence and limit results
            expanded_relations.sort(key=lambda x: x["confidence"], reverse=True)
            
            logger.info(f"Expanded {len(expanded_relations)} relations for entity '{entity}'")
            return expanded_relations[:self.max_relations]
            
        except Exception as e:
            logger.error(f"KG relation expansion failed: {e}")
            return []
    
    def bidirectional_expand(self, entity: str) -> Dict[str, List[Dict[str, Any]]]:
        """Perform bidirectional relation expansion"""
        try:
            forward_relations = self.expand_relations(entity)
            
            if not self.bidirectional:
                return {"forward": forward_relations, "reverse": []}
            
            # Get reverse relations (entities that point to this one)
            reverse_relations = []
            all_entities = ["Software Engineer", "Python", "AWS", "TechCorp", "Django", "Data Science"]
            
            for other_entity in all_entities:
                if other_entity != entity:
                    other_relations = self.expand_relations(other_entity)
                    for rel in other_relations:
                        if rel["target_entity"] == entity:
                            reverse_relations.append({
                                "source_entity": rel["target_entity"],
                                "target_entity": rel["source_entity"],
                                "relation": f"reverse_{rel['relation']}",
                                "confidence": rel["confidence"]
                            })
            
            logger.info(f"Bidirectional expansion: {len(forward_relations)} forward, {len(reverse_relations)} reverse")
            return {
                "forward": forward_relations,
                "reverse": reverse_relations[:self.max_relations]
            }
            
        except Exception as e:
            logger.error(f"Bidirectional expansion failed: {e}")
            return {"forward": [], "reverse": []}
    
    def find_related_entities(self, entity: str, max_hops: int = 2) -> List[Dict[str, Any]]:
        """Find related entities within specified hops"""
        try:
            visited = set()
            queue = [(entity, 0, [])]  # (entity, hops, path)
            related_entities = []
            
            while queue and len(related_entities) < self.max_relations:
                current_entity, hops, path = queue.pop(0)
                
                if current_entity in visited or hops > max_hops:
                    continue
                
                visited.add(current_entity)
                
                if hops > 0:  # Don't include the starting entity
                    related_entities.append({
                        "entity": current_entity,
                        "hops": hops,
                        "path": path + [current_entity]
                    })
                
                # Get neighbors
                relations = self.expand_relations(current_entity)
                for rel in relations:
                    neighbor = rel["target_entity"]
                    if neighbor not in visited:
                        queue.append((neighbor, hops + 1, path + [current_entity]))
            
            logger.info(f"Found {len(related_entities)} related entities within {max_hops} hops")
            return related_entities
            
        except Exception as e:
            logger.error(f"Related entity search failed: {e}")
            return []

def create_kg_relation_expand_tool(config: Optional[Dict[str, Any]] = None) -> KGRelationExpandTool:
    """Factory function to create KG relation expand tool instance"""
    return KGRelationExpandTool(config)

# Re-export components
__all__ = [
    'KGRelationExpandTool', 'create_kg_relation_expand_tool'
]
