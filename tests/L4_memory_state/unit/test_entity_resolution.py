"""
L4 Memory/State Layer Unit Tests - Entity Resolution

Tests for entity resolution and disambiguation without planning logic.
Focuses on entity linking, canonicalization, and relationship inference.
"""

import pytest
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from unittest.mock import Mock, patch, AsyncMock
import asyncio
import time
import uuid

# Mark all tests in this module as L4 memory/state unit tests
pytestmark = [pytest.mark.unit, pytest.mark.l4, pytest.mark.memory_state]


class EntityType(Enum):
    """Types of entities in the knowledge graph."""
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    SKILL = "skill"
    JOB_TITLE = "job_title"
    EDUCATION = "education"
    CERTIFICATION = "certification"


class EntityStatus(Enum):
    """Status of entities in resolution process."""
    CANDIDATE = "candidate"
    CONFIRMED = "confirmed"
    MERGED = "merged"
    DISCARDED = "discarded"


@dataclass(frozen=True)
class MockEntity:
    """Mock entity for resolution testing."""
    entity_id: str
    entity_type: EntityType
    name: str
    aliases: List[str]
    attributes: Dict[str, Any]
    confidence: float
    source: str
    status: EntityStatus
    metadata: Dict[str, Any]


@dataclass(frozen=True)
class MockEntityMention:
    """Mock entity mention for linking."""
    mention_id: str
    text: str
    context: str
    start_pos: int
    end_pos: int
    candidate_entities: List[str]
    linked_entity: Optional[str]


class TestEntityCanonicalization:
    """Test entity canonicalization and normalization."""
    
    def test_name_normalization(self):
        """Test normalization of entity names."""
        
        class EntityNormalizer:
            def __init__(self):
                self.normalization_rules = {
                    "lowercase": True,
                    "remove_punctuation": True,
                    "remove_extra_spaces": True,
                    "normalize_company_suffixes": True,
                    "normalize_person_titles": True
                }
            
            def normalize_name(self, name: str, entity_type: EntityType) -> str:
                """Normalize entity name based on type and rules."""
                normalized = name
                
                # Basic normalization
                if self.normalization_rules["lowercase"]:
                    normalized = normalized.lower()
                
                if self.normalization_rules["remove_punctuation"]:
                    import re
                    normalized = re.sub(r'[^\w\s]', ' ', normalized)
                
                if self.normalization_rules["remove_extra_spaces"]:
                    normalized = ' '.join(normalized.split())
                
                # Type-specific normalization
                if entity_type == EntityType.ORGANIZATION and self.normalization_rules["normalize_company_suffixes"]:
                    company_suffixes = ["inc", "llc", "ltd", "corp", "corporation", "co", "company"]
                    words = normalized.split()
                    words = [w for w in words if w not in company_suffixes]
                    normalized = ' '.join(words)
                
                elif entity_type == EntityType.PERSON and self.normalization_rules["normalize_person_titles"]:
                    person_titles = ["mr", "mrs", "ms", "dr", "prof", "sir", "madam"]
                    words = normalized.split()
                    words = [w for w in words if w not in person_titles]
                    normalized = ' '.join(words)
                
                return normalized.strip()
        
        normalizer = EntityNormalizer()
        
        # Test name normalization
        test_cases = [
            ("John Smith", EntityType.PERSON, "john smith"),
            ("Dr. John Smith", EntityType.PERSON, "john smith"),
            ("Acme Corporation Inc.", EntityType.ORGANIZATION, "acme corporation"),
            ("Tech Co., LLC", EntityType.ORGANIZATION, "tech co"),
            ("  Software  Developer  ", EntityType.JOB_TITLE, "software developer"),
            ("Python/Java Developer", EntityType.JOB_TITLE, "python java developer"),
            ("New York, NY", EntityType.LOCATION, "new york ny"),
            ("B.S. Computer Science", EntityType.EDUCATION, "bs computer science")
        ]
        
        normalization_results = []
        for original_name, entity_type, expected in test_cases:
            normalized = normalizer.normalize_name(original_name, entity_type)
            normalization_results.append({
                "original": original_name,
                "type": entity_type,
                "normalized": normalized,
                "expected": expected,
                "correct": normalized == expected
            })
        
        # Validate normalization results
        assert all(result["correct"] for result in normalization_results)
        
        # Validate specific normalizations
        corp_result = next(r for r in normalization_results if r["original"] == "Acme Corporation Inc.")
        assert corp_result["normalized"] == "acme corporation"
        
        title_result = next(r for r in normalization_results if r["original"] == "Dr. John Smith")
        assert title_result["normalized"] == "john smith"
    
    def test_alias_generation(self):
        """Test generation of entity aliases."""
        
        class AliasGenerator:
            def __init__(self):
                self.alias_patterns = {
                    EntityType.ORGANIZATION: ["full_name", "short_name", "acronym"],
                    EntityType.PERSON: ["full_name", "first_last", "initials"],
                    EntityType.SKILL: ["full_name", "abbreviated", "synonyms"]
                }
            
            def generate_aliases(self, entity: MockEntity) -> List[str]:
                """Generate aliases for entity based on type and patterns."""
                aliases = set()
                patterns = self.alias_patterns.get(entity.entity_type, [])
                
                for pattern in patterns:
                    generated = self._apply_pattern(entity, pattern)
                    if generated:
                        aliases.add(generated)
                
                return list(aliases)
            
            def _apply_pattern(self, entity: MockEntity, pattern: str) -> Optional[str]:
                """Apply specific alias generation pattern."""
                if pattern == "full_name":
                    return entity.name.lower()
                
                elif pattern == "short_name":
                    words = entity.name.split()
                    if len(words) >= 2:
                        return ' '.join(words[:2]).lower()
                
                elif pattern == "acronym" and entity.entity_type == EntityType.ORGANIZATION:
                    words = entity.name.split()
                    if len(words) >= 2:
                        return ''.join(word[0].upper() for word in words)
                
                elif pattern == "first_last" and entity.entity_type == EntityType.PERSON:
                    words = entity.name.split()
                    if len(words) >= 2:
                        return f"{words[0]} {words[-1]}".lower()
                
                elif pattern == "initials" and entity.entity_type == EntityType.PERSON:
                    words = entity.name.split()
                    if len(words) >= 2:
                        return ''.join(word[0].upper() for word in words)
                
                elif pattern == "abbreviated" and entity.entity_type == EntityType.SKILL:
                    words = entity.name.split()
                    if len(words) >= 2:
                        return f"{words[0]} {words[1][0].upper()}."
                
                return None
        
        generator = AliasGenerator()
        
        # Create test entities
        entities = [
            MockEntity("ent_1", EntityType.ORGANIZATION, "Advanced Technology Solutions", 
                      [], {}, 0.9, "source_1", EntityStatus.CANDIDATE, {}),
            MockEntity("ent_2", EntityType.PERSON, "John Michael Smith", 
                      [], {}, 0.9, "source_2", EntityStatus.CANDIDATE, {}),
            MockEntity("ent_3", EntityType.SKILL, "Machine Learning Engineering", 
                      [], {}, 0.9, "source_3", EntityStatus.CANDIDATE, {})
        ]
        
        # Generate aliases for each entity
        alias_results = []
        for entity in entities:
            aliases = generator.generate_aliases(entity)
            alias_results.append({
                "entity_id": entity.entity_id,
                "entity_type": entity.entity_type,
                "original_name": entity.name,
                "generated_aliases": aliases
            })
        
        # Validate alias generation
        for result in alias_results:
            assert len(result["generated_aliases"]) >= 2  # Should generate multiple aliases
        
        # Validate specific alias types
        org_result = next(r for r in alias_results if r["entity_type"] == EntityType.ORGANIZATION)
        assert "advanced technology solutions" in org_result["generated_aliases"]
        assert "ATS" in org_result["generated_aliases"]  # Acronym
        
        person_result = next(r for r in alias_results if r["entity_type"] == EntityType.PERSON)
        assert "john michael smith" in person_result["generated_aliases"]
        assert "john smith" in person_result["generated_aliases"]
        assert "JMS" in person_result["generated_aliases"]  # Initials
        
        skill_result = next(r for r in alias_results if r["entity_type"] == EntityType.SKILL)
        assert "machine learning engineering" in skill_result["generated_aliases"]
    
    def test_entity_deduplication(self):
        """Test deduplication of similar entities."""
        
        class EntityDeduplicator:
            def __init__(self, similarity_threshold: float = 0.8):
                self.similarity_threshold = similarity_threshold
                self.deduplication_log = []
            
            def deduplicate_entities(self, entities: List[MockEntity]) -> List[MockEntity]:
                """Deduplicate entities based on similarity."""
                if not entities:
                    return []
                
                # Sort by confidence (highest first)
                sorted_entities = sorted(entities, key=lambda e: e.confidence, reverse=True)
                
                deduplicated = [sorted_entities[0]]
                
                for entity in sorted_entities[1:]:
                    is_duplicate = False
                    
                    for existing in deduplicated:
                        similarity = self._calculate_similarity(entity, existing)
                        
                        if similarity >= self.similarity_threshold:
                            # Mark as duplicate and merge
                            self._merge_entities(existing, entity)
                            self.deduplication_log.append({
                                "action": "merged",
                                "kept_entity": existing.entity_id,
                                "removed_entity": entity.entity_id,
                                "similarity": similarity
                            })
                            is_duplicate = True
                            break
                    
                    if not is_duplicate:
                        deduplicated.append(entity)
                
                return deduplicated
            
            def _calculate_similarity(self, entity1: MockEntity, entity2: MockEntity) -> float:
                """Calculate similarity between two entities."""
                if entity1.entity_type != entity2.entity_type:
                    return 0.0
                
                # Name similarity (simple implementation)
                name1 = entity1.name.lower()
                name2 = entity2.name.lower()
                
                # Jaccard similarity on word sets
                words1 = set(name1.split())
                words2 = set(name2.split())
                
                if not words1 and not words2:
                    return 1.0
                if not words1 or not words2:
                    return 0.0
                
                intersection = len(words1 & words2)
                union = len(words1 | words2)
                
                name_similarity = intersection / union if union > 0 else 0.0
                
                # Attribute similarity
                attr_similarity = self._calculate_attribute_similarity(entity1, entity2)
                
                # Weighted combination
                overall_similarity = 0.7 * name_similarity + 0.3 * attr_similarity
                return overall_similarity
            
            def _calculate_attribute_similarity(self, entity1: MockEntity, entity2: MockEntity) -> float:
                """Calculate attribute similarity between entities."""
                common_attrs = set(entity1.attributes.keys()) & set(entity2.attributes.keys())
                
                if not common_attrs:
                    return 0.0
                
                matching_attrs = 0
                for attr in common_attrs:
                    if entity1.attributes[attr] == entity2.attributes[attr]:
                        matching_attrs += 1
                
                return matching_attrs / len(common_attrs)
            
            def _merge_entities(self, keep_entity: MockEntity, merge_entity: MockEntity):
                """Merge information from merge_entity into keep_entity."""
                # In a real implementation, this would update the entity
                # For testing, we just log the merge
                pass
        
        # Test entity deduplication
        deduplicator = EntityDeduplicator(similarity_threshold=0.7)
        
        # Create similar entities
        entities = [
            MockEntity("ent_1", EntityType.ORGANIZATION, "Advanced Technology Solutions", 
                      [], {"industry": "Technology", "size": "Large"}, 0.9, "source_1", 
                      EntityStatus.CANDIDATE, {}),
            MockEntity("ent_2", EntityType.ORGANIZATION, "Advanced Technology Solutions Inc.", 
                      [], {"industry": "Technology", "size": "Large"}, 0.8, "source_2", 
                      EntityStatus.CANDIDATE, {}),
            MockEntity("ent_3", EntityType.ORGANIZATION, "Tech Solutions Inc.", 
                      [], {"industry": "Technology", "size": "Medium"}, 0.7, "source_3", 
                      EntityStatus.CANDIDATE, {}),
            MockEntity("ent_4", EntityType.PERSON, "John Smith", 
                      [], {"role": "Developer"}, 0.9, "source_4", 
                      EntityStatus.CANDIDATE, {}),
            MockEntity("ent_5", EntityType.ORGANIZATION, "Completely Different Corp", 
                      [], {"industry": "Finance"}, 0.8, "source_5", 
                      EntityStatus.CANDIDATE, {})
        ]
        
        # Deduplicate entities
        deduplicated = deduplicator.deduplicate_entities(entities)
        
        # Validate deduplication results
        assert len(deduplicated) == 3  # Should merge ent_1 and ent_2, keep others
        
        # Check deduplication log
        assert len(deduplicator.deduplication_log) == 1  # Should have one merge
        
        merge_log = deduplicator.deduplication_log[0]
        assert merge_log["kept_entity"] == "ent_1"  # Higher confidence entity kept
        assert merge_log["removed_entity"] == "ent_2"
        assert merge_log["similarity"] >= 0.7
        
        # Validate remaining entities
        remaining_ids = {e.entity_id for e in deduplicated}
        assert remaining_ids == {"ent_1", "ent_4", "ent_5"}


class TestEntityLinking:
    """Test linking entity mentions to canonical entities."""
    
    def test_candidate_entity_selection(self):
        """Test selection of candidate entities for mentions."""
        
        class CandidateSelector:
            def __init__(self):
                self.entity_index = {}  # name -> list of entity_ids
                self.alias_index = {}   # alias -> list of entity_ids
            
            def index_entities(self, entities: List[MockEntity]):
                """Build search index for entities."""
                for entity in entities:
                    # Index by name
                    name_key = entity.name.lower()
                    if name_key not in self.entity_index:
                        self.entity_index[name_key] = []
                    self.entity_index[name_key].append(entity.entity_id)
                    
                    # Index by aliases
                    for alias in entity.aliases:
                        alias_key = alias.lower()
                        if alias_key not in self.alias_index:
                            self.alias_index[alias_key] = []
                        self.alias_index[alias_key].append(entity.entity_id)
            
            def find_candidates(self, mention_text: str, entity_type: EntityType) -> List[str]:
                """Find candidate entities for a mention."""
                candidates = set()
                mention_lower = mention_text.lower()
                
                # Direct name match
                if mention_lower in self.entity_index:
                    candidates.update(self.entity_index[mention_lower])
                
                # Alias match
                if mention_lower in self.alias_index:
                    candidates.update(self.alias_index[mention_lower])
                
                # Partial match (for longer names)
                for name_key in self.entity_index:
                    if mention_lower in name_key or name_key in mention_lower:
                        candidates.update(self.entity_index[name_key])
                
                return list(candidates)
            
            def rank_candidates(self, mention_text: str, candidates: List[str], 
                               entities: Dict[str, MockEntity]) -> List[Tuple[str, float]]:
                """Rank candidates by relevance to mention."""
                scored_candidates = []
                
                for candidate_id in candidates:
                    entity = entities[candidate_id]
                    score = self._calculate_candidate_score(mention_text, entity)
                    scored_candidates.append((candidate_id, score))
                
                # Sort by score (highest first)
                scored_candidates.sort(key=lambda x: x[1], reverse=True)
                return scored_candidates
            
            def _calculate_candidate_score(self, mention_text: str, entity: MockEntity) -> float:
                """Calculate relevance score for candidate entity."""
                mention_lower = mention_text.lower()
                entity_name_lower = entity.name.lower()
                
                # Exact match gets highest score
                if mention_lower == entity_name_lower:
                    return 1.0
                
                # Partial match based on overlap
                mention_words = set(mention_lower.split())
                entity_words = set(entity_name_lower.split())
                
                if not mention_words or not entity_words:
                    return 0.0
                
                intersection = len(mention_words & entity_words)
                union = len(mention_words | entity_words)
                
                overlap_score = intersection / union if union > 0 else 0.0
                
                # Boost by entity confidence
                final_score = overlap_score * entity.confidence
                return final_score
        
        # Test candidate selection
        selector = CandidateSelector()
        
        # Create test entities with aliases
        entities = [
            MockEntity("ent_1", EntityType.ORGANIZATION, "Advanced Technology Solutions", 
                      ["ATS", "Advanced Tech", "Tech Solutions"], 
                      {"industry": "Technology"}, 0.9, "source_1", EntityStatus.CONFIRMED, {}),
            MockEntity("ent_2", EntityType.ORGANIZATION, "Technology Solutions Inc.", 
                      ["TSI", "Tech Solutions"], 
                      {"industry": "Technology"}, 0.8, "source_2", EntityStatus.CONFIRMED, {}),
            MockEntity("ent_3", EntityType.SKILL, "Machine Learning", 
                      ["ML", "Machine Learning Engineering"], 
                      {"category": "Technical"}, 0.9, "source_3", EntityStatus.CONFIRMED, {})
        ]
        
        entity_dict = {e.entity_id: e for e in entities}
        selector.index_entities(entities)
        
        # Test candidate finding
        test_mentions = [
            ("Advanced Technology Solutions", EntityType.ORGANIZATION),
            ("ATS", EntityType.ORGANIZATION),
            ("Tech Solutions", EntityType.ORGANIZATION),
            ("Machine Learning", EntityType.SKILL),
            ("ML", EntityType.SKILL),
            ("Unknown Entity", EntityType.ORGANIZATION)
        ]
        
        selection_results = []
        for mention_text, entity_type in test_mentions:
            candidates = selector.find_candidates(mention_text, entity_type)
            ranked_candidates = selector.rank_candidates(mention_text, candidates, entity_dict)
            
            selection_results.append({
                "mention": mention_text,
                "candidates": candidates,
                "ranked_candidates": ranked_candidates,
                "top_candidate": ranked_candidates[0][0] if ranked_candidates else None
            })
        
        # Validate selection results
        ats_result = next(r for r in selection_results if r["mention"] == "Advanced Technology Solutions")
        assert "ent_1" in ats_result["candidates"]
        assert ats_result["top_candidate"] == "ent_1"
        
        acronym_result = next(r for r in selection_results if r["mention"] == "ATS")
        assert "ent_1" in acronym_result["candidates"]
        
        ambiguous_result = next(r for r in selection_results if r["mention"] == "Tech Solutions")
        assert len(ambiguous_result["candidates"]) >= 2  # Should match multiple entities
        
        unknown_result = next(r for r in selection_results if r["mention"] == "Unknown Entity")
        assert len(unknown_result["candidates"]) == 0  # Should have no candidates
    
    def test_context_aware_linking(self):
        """Test context-aware entity linking."""
        
        class ContextAwareLinker:
            def __init__(self):
                self.context_patterns = {
                    "work_experience": ["worked at", "employed by", "company", "organization"],
                    "skills": ["skilled in", "proficient in", "experience with", "knowledge of"],
                    "education": ["studied at", "graduated from", "university", "college"],
                    "location": ["located in", "based in", "city", "country"]
                }
            
            def disambiguate_with_context(self, mention: MockEntityMention, 
                                        candidates: List[Tuple[str, float]], 
                                        entities: Dict[str, MockEntity]) -> Optional[str]:
                """Disambiguate entity using context information."""
                if not candidates:
                    return None
                
                # If only one candidate, return it
                if len(candidates) == 1:
                    return candidates[0][0]
                
                # Use context to disambiguate
                context_type = self._classify_context(mention.context)
                context_boosted = self._apply_context_boost(candidates, context_type, entities)
                
                # Return highest scored candidate after context boost
                return context_boosted[0][0] if context_boosted else candidates[0][0]
            
            def _classify_context(self, context: str) -> str:
                """Classify the type of context."""
                context_lower = context.lower()
                
                for context_type, patterns in self.context_patterns.items():
                    for pattern in patterns:
                        if pattern in context_lower:
                            return context_type
                
                return "general"
            
            def _apply_context_boost(self, candidates: List[Tuple[str, float]], 
                                   context_type: str, entities: Dict[str, MockEntity]) -> List[Tuple[str, float]]:
                """Apply context-based scoring boost."""
                boosted_candidates = []
                
                for entity_id, score in candidates:
                    entity = entities[entity_id]
                    boost = self._calculate_context_boost(entity, context_type)
                    boosted_score = score * (1.0 + boost)
                    boosted_candidates.append((entity_id, boosted_score))
                
                # Sort by boosted score
                boosted_candidates.sort(key=lambda x: x[1], reverse=True)
                return boosted_candidates
            
            def _calculate_context_boost(self, entity: MockEntity, context_type: str) -> float:
                """Calculate context boost for entity."""
                boost_map = {
                    EntityType.ORGANIZATION: {"work_experience": 0.3, "general": 0.0},
                    EntityType.SKILL: {"skills": 0.3, "general": 0.0},
                    EntityType.EDUCATION: {"education": 0.3, "general": 0.0},
                    EntityType.LOCATION: {"location": 0.3, "general": 0.0}
                }
                
                entity_boosts = boost_map.get(entity.entity_type, {})
                return entity_boosts.get(context_type, 0.0)
        
        # Test context-aware linking
        linker = ContextAwareLinker()
        
        # Create entities
        entities = {
            "org_1": MockEntity("org_1", EntityType.ORGANIZATION, "Tech Corp", [], {}, 0.9, "source_1", EntityStatus.CONFIRMED, {}),
            "skill_1": MockEntity("skill_1", EntityType.SKILL, "Tech Corp", [], {}, 0.8, "source_2", EntityStatus.CONFIRMED, {}),  # Same name, different type
            "org_2": MockEntity("org_2", EntityType.ORGANIZATION, "University", [], {}, 0.9, "source_3", EntityStatus.CONFIRMED, {})
        }
        
        # Create test mentions with context
        mentions = [
            MockEntityMention("mention_1", "Tech Corp", "worked at Tech Corp as a developer", 10, 18, 
                            ["org_1", "skill_1"], None),
            MockEntityMention("mention_2", "Tech Corp", "skilled in Tech Corp programming", 12, 20, 
                            ["org_1", "skill_1"], None),
            MockEntityMention("mention_3", "University", "graduated from University with honors", 15, 24, 
                            ["org_2"], None)
        ]
        
        # Test context-aware disambiguation
        linking_results = []
        for mention in mentions:
            # Simulate candidate ranking (would come from candidate selector)
            if mention.text == "Tech Corp":
                candidates = [("org_1", 0.9), ("skill_1", 0.8)]
            else:
                candidates = [("org_2", 0.9)]
            
            linked_entity = linker.disambiguate_with_context(mention, candidates, entities)
            
            linking_results.append({
                "mention_text": mention.text,
                "context": mention.context,
                "linked_entity": linked_entity
            })
        
        # Validate context-aware linking
        work_context_result = next(r for r in linking_results if "worked at" in r["context"])
        assert work_context_result["linked_entity"] == "org_1"  # Should link to organization in work context
        
        skill_context_result = next(r for r in linking_results if "skilled in" in r["context"])
        assert skill_context_result["linked_entity"] == "skill_1"  # Should link to skill in skill context
        
        education_context_result = next(r for r in linking_results if "graduated from" in r["context"])
        assert education_context_result["linked_entity"] == "org_2"  # Should link to organization in education context


class TestRelationshipInference:
    """Test inference of relationships between entities."""
    
    def test_relationship_extraction(self):
        """Test extraction of relationships from text."""
        
        class RelationshipExtractor:
            def __init__(self):
                self.relationship_patterns = {
                    "works_for": [r"(\w+)\s+(?:works at|is employed by|works for)\s+(\w+)", 
                                 r"(\w+(?:\s+\w+)*)\s+(?:works at|is employed by|works for)\s+(\w+(?:\s+\w+)*)"],
                    "located_in": [r"(\w+)\s+(?:is located in|is based in|located in)\s+(\w+)",
                                 r"(\w+(?:\s+\w+)*)\s+(?:is located in|is based in|located in)\s+(\w+(?:\s+\w+)*)"],
                    "has_skill": [r"(\w+)\s+(?:has|possesses|is skilled in)\s+(\w+)",
                                 r"(\w+(?:\s+\w+)*)\s+(?:has|possesses|is skilled in)\s+(\w+(?:\s+\w+)*)"],
                    "graduated_from": [r"(\w+)\s+(?:graduated from|studied at)\s+(\w+)",
                                      r"(\w+(?:\s+\w+)*)\s+(?:graduated from|studied at)\s+(\w+(?:\s+\w+)*)"]
                }
            
            def extract_relationships(self, text: str, entities: List[str]) -> List[Dict[str, Any]]:
                """Extract relationships from text given entity mentions."""
                relationships = []
                text_lower = text.lower()
                
                for relation_type, patterns in self.relationship_patterns.items():
                    for pattern in patterns:
                        import re
                        matches = re.finditer(pattern, text_lower)
                        
                        for match in matches:
                            entity1, entity2 = match.groups()
                            
                            # Check if entities are in our entity list
                            entity1_normalized = entity1.strip().title()
                            entity2_normalized = entity2.strip().title()
                            
                            if entity1_normalized in entities or entity2_normalized in entities:
                                relationships.append({
                                    "type": relation_type,
                                    "subject": entity1_normalized,
                                    "object": entity2_normalized,
                                    "confidence": 0.8,  # Fixed confidence for testing
                                    "source_text": text[match.start():match.end()]
                                })
                
                return relationships
        
        # Test relationship extraction
        extractor = RelationshipExtractor()
        
        # Test texts with relationships
        test_texts = [
            ("John works at Microsoft and is skilled in Python", ["John", "Microsoft", "Python"]),
            ("Sarah is located in New York and graduated from Harvard University", ["Sarah", "New York", "Harvard University"]),
            ("Tech Corp is based in San Francisco and employs many developers", ["Tech Corp", "San Francisco", "developers"])
        ]
        
        extraction_results = []
        for text, entities in test_texts:
            relationships = extractor.extract_relationships(text, entities)
            extraction_results.append({
                "text": text,
                "entities": entities,
                "extracted_relationships": relationships
            })
        
        # Validate extraction results
        assert len(extraction_results) == 3
        
        # Check first text
        first_result = extraction_results[0]
        assert len(first_result["extracted_relationships"]) >= 2
        
        relation_types = [rel["type"] for rel in first_result["extracted_relationships"]]
        assert "works_for" in relation_types
        assert "has_skill" in relation_types
        
        # Check relationship details
        works_for_rel = next(rel for rel in first_result["extracted_relationships"] if rel["type"] == "works_for")
        assert works_for_rel["subject"] == "John"
        assert works_for_rel["object"] == "Microsoft"
    
    def test_relationship_validation(self):
        """Test validation of extracted relationships."""
        
        class RelationshipValidator:
            def __init__(self):
                self.valid_relationships = {
                    EntityType.PERSON: {
                        "can_be_subject_of": ["works_for", "located_in", "has_skill", "graduated_from"],
                        "can_be_object_of": ["manages", "supervises"]
                    },
                    EntityType.ORGANIZATION: {
                        "can_be_subject_of": ["located_in", "employs", "founded"],
                        "can_be_object_of": ["works_for", "located_in"]
                    },
                    EntityType.LOCATION: {
                        "can_be_subject_of": ["contains", "borders"],
                        "can_be_object_of": ["located_in", "based_in"]
                    },
                    EntityType.SKILL: {
                        "can_be_subject_of": ["required_for"],
                        "can_be_object_of": ["has_skill", "requires"]
                    }
                }
            
            def validate_relationship(self, subject_type: EntityType, relation_type: str, 
                                    object_type: EntityType) -> bool:
                """Validate if relationship is valid between entity types."""
                subject_valid_rels = self.valid_relationships.get(subject_type, {})
                valid_subject_relations = subject_valid_rels.get("can_be_subject_of", [])
                
                return relation_type in valid_subject_relations
            
            def validate_relationship_chain(self, relationships: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
                """Validate a chain of relationships."""
                validation_results = []
                
                for rel in relationships:
                    subject_type = rel.get("subject_type")
                    object_type = rel.get("object_type")
                    relation_type = rel["type"]
                    
                    is_valid = self.validate_relationship(subject_type, relation_type, object_type)
                    
                    validation_results.append({
                        "relationship": rel,
                        "is_valid": is_valid,
                        "validation_reason": self._get_validation_reason(subject_type, relation_type, object_type, is_valid)
                    })
                
                return validation_results
            
            def _get_validation_reason(self, subject_type: EntityType, relation_type: str, 
                                     object_type: EntityType, is_valid: bool) -> str:
                """Get reason for validation result."""
                if is_valid:
                    return f"Valid: {subject_type.value} can be subject of {relation_type}"
                else:
                    return f"Invalid: {subject_type.value} cannot be subject of {relation_type}"
        
        # Test relationship validation
        validator = RelationshipValidator()
        
        # Create test relationships
        test_relationships = [
            {"type": "works_for", "subject": "John", "subject_type": EntityType.PERSON, 
             "object": "Microsoft", "object_type": EntityType.ORGANIZATION},
            {"type": "has_skill", "subject": "John", "subject_type": EntityType.PERSON, 
             "object": "Python", "object_type": EntityType.SKILL},
            {"type": "located_in", "subject": "Microsoft", "subject_type": EntityType.ORGANIZATION, 
             "object": "Seattle", "object_type": EntityType.LOCATION},
            {"type": "works_for", "subject": "Microsoft", "subject_type": EntityType.ORGANIZATION, 
             "object": "John", "object_type": EntityType.PERSON},  # Invalid: organization can't work for person
            {"type": "graduated_from", "subject": "Python", "subject_type": EntityType.SKILL, 
             "object": "University", "object_type": EntityType.EDUCATION}  # Invalid: skill can't graduate
        ]
        
        # Validate relationships
        validation_results = validator.validate_relationship_chain(test_relationships)
        
        # Validate validation results
        assert len(validation_results) == 5
        
        valid_results = [r for r in validation_results if r["is_valid"]]
        invalid_results = [r for r in validation_results if not r["is_valid"]]
        
        assert len(valid_results) == 3
        assert len(invalid_results) == 2
        
        # Check specific invalid relationships
        invalid_org_person = next(r for r in invalid_results if "Microsoft" in r["relationship"]["subject"])
        assert "cannot be subject of works_for" in invalid_org_person["validation_reason"]
        
        invalid_skill_university = next(r for r in invalid_results if "Python" in r["relationship"]["subject"])
        assert "cannot be subject of graduated_from" in invalid_skill_university["validation_reason"]
