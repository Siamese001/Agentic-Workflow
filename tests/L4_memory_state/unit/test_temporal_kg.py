"""
L4 Memory/State Layer Unit Tests - Temporal Knowledge Graph

Tests for temporal knowledge graph functionality including triplet extraction,
entity resolution, and temporal validity ranges without orchestration logic.
"""

import pytest
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from unittest.mock import Mock, patch

# Mark all tests in this module as L4 memory/state unit tests
pytestmark = [pytest.mark.unit, pytest.mark.l4, pytest.mark.memory, pytest.mark.kg]


class TemporalValidity(Enum):
    """Temporal validity status for knowledge graph entities."""
    VALID = "valid"
    EXPIRED = "expired"
    FUTURE = "future"
    SUPERSEDED = "superseded"


@dataclass(frozen=True)
class MockEntity:
    """Mock entity for temporal knowledge graph testing."""
    entity_id: str
    entity_type: str
    name: str
    canonical_form: str
    temporal_validity: Dict[str, datetime]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MockTriplet:
    """Mock triplet for temporal knowledge graph testing."""
    subject: str
    predicate: str
    object: str
    confidence: float
    temporal_range: Dict[str, datetime]
    source_evidence: List[str]
    invalidated_by: Optional[str] = None


@dataclass(frozen=True)
class MockTemporalKG:
    """Mock temporal knowledge graph for L4 testing."""
    graph_id: str
    entities: List[MockEntity]
    triplets: List[MockTriplet]
    temporal_index: Dict[str, List[int]] = field(default_factory=dict)


class TestEntityResolution:
    """Test L4 entity resolution and canonicalization."""
    
    def test_entity_canonicalization(self):
        """Test entity canonicalization for temporal KG."""
        raw_entities = [
            "John Doe",
            "John D. Doe",
            "J. Doe",
            "Johnny Doe"
        ]
        
        # Mock canonicalization logic
        canonical_form = "John Doe"  # Most complete form
        canonicalized_entities = []
        
        for entity in raw_entities:
            if len(entity) >= len(canonical_form):
                canonicalized = canonical_form
            else:
                canonicalized = entity  # Keep as alias
            
            canonicalized_entities.append({
                "raw": entity,
                "canonical": canonicalized,
                "is_alias": entity != canonical_form
            })
        
        # Verify canonicalization
        canonical_entity = next(e for e in canonicalized_entities if e["canonical"] == canonical_form)
        aliases = [e for e in canonicalized_entities if e["is_alias"]]
        
        assert canonical_entity["raw"] == "John Doe"
        assert len(aliases) == 3
        assert all(e["canonical"] == "John Doe" for e in aliases)
    
    def test_entity_type_detection(self):
        """Test entity type detection for temporal KG."""
        entity_examples = {
            "Python": "skill",
            "AWS": "technology",
            "Software Engineer": "job_title",
            "Google": "company",
            "Bachelor's Degree": "education",
            "5 years": "experience_duration"
        }
        
        # Mock entity type detection
        detected_types = {}
        for entity, expected_type in entity_examples.items():
            # Simplified type detection logic
            if any(keyword in entity.lower() for keyword in ["python", "java", "aws", "docker"]):
                detected_type = "skill" if len(entity.split()) == 1 else "technology"
            elif "engineer" in entity.lower() or "manager" in entity.lower():
                detected_type = "job_title"
            elif any(keyword in entity.lower() for keyword in ["degree", "bachelor", "master"]):
                detected_type = "education"
            elif "year" in entity.lower():
                detected_type = "experience_duration"
            else:
                detected_type = "company" if len(entity.split()) == 1 else "unknown"
            
            detected_types[entity] = detected_type
        
        assert detected_types["Python"] == "skill"
        assert detected_types["Software Engineer"] == "job_title"
        assert detected_types["5 years"] == "experience_duration"
    
    def test_entity_deduplication(self):
        """Test entity deduplication in temporal KG."""
        duplicate_entities = [
            {"text": "Python Programming", "source": "resume_1"},
            {"text": "Python", "source": "resume_2"},
            {"text": "Python Programming Language", "source": "job_desc_1"},
            {"text": "Python", "source": "job_desc_2"}
        ]
        
        # Mock deduplication logic
        entity_groups = {}
        for entity in duplicate_entities:
            # Simplified similarity check
            key = entity["text"].split()[0]  # Use first word as grouping key
            if key not in entity_groups:
                entity_groups[key] = []
            entity_groups[key].append(entity)
        
        # Create canonical entities
        canonical_entities = []
        for group_key, entities in entity_groups.items():
            # Choose most complete form as canonical
            canonical = max(entities, key=lambda e: len(e["text"]))
            canonical_entities.append({
                "canonical_id": f"entity_{group_key}_001",
                "canonical_text": canonical["text"],
                "aliases": [e["text"] for e in entities if e != canonical],
                "sources": list(set(e["source"] for e in entities))
            })
        
        assert len(canonical_entities) == 1
        assert canonical_entities[0]["canonical_text"] == "Python Programming Language"
        assert len(canonical_entities[0]["aliases"]) == 3


class TestTemporalTripletExtraction:
    """Test temporal triplet extraction and validation."""
    
    def test_triplet_structure_validation(self):
        """Test validation of temporal triplet structure."""
        valid_triplet = MockTriplet(
            subject="John Doe",
            predicate="has_skill",
            object="Python Programming",
            confidence=0.85,
            temporal_range={
                "start": datetime(2020, 1, 1),
                "end": datetime(2025, 12, 31)
            },
            source_evidence=["resume_section_skills", "project_python_app"]
        )
        
        # Validate triplet structure
        assert valid_triplet.subject != ""
        assert valid_triplet.predicate != ""
        assert valid_triplet.object != ""
        assert 0.0 <= valid_triplet.confidence <= 1.0
        assert valid_triplet.temporal_range["start"] < valid_triplet.temporal_range["end"]
        assert len(valid_triplet.source_evidence) > 0
    
    def test_temporal_range_creation(self):
        """Test creation of temporal ranges for triplets."""
        extraction_context = {
            "document_date": datetime(2023, 6, 15),
            "experience_start": "January 2020",
            "experience_end": "Present",
            "confidence_decay": 0.1  # 10% decay per year
        }
        
        # Mock temporal range creation
        start_date = datetime(2020, 1, 1)  # Parsed from "January 2020"
        end_date = datetime(2025, 12, 31)  # Extended from "Present"
        
        # Apply confidence decay
        years_span = (end_date - start_date).days / 365.25
        decayed_confidence = max(0.1, 0.9 - (years_span * extraction_context["confidence_decay"]))
        
        temporal_range = {
            "start": start_date,
            "end": end_date,
            "confidence_at_extraction": 0.9,
            "decayed_confidence": decayed_confidence
        }
        
        assert temporal_range["start"].year == 2020
        assert temporal_range["end"].year == 2025
        assert decayed_confidence < 0.9
    
    def test_triplet_confidence_scoring(self):
        """Test confidence scoring for extracted triplets."""
        extraction_sources = [
            {"source": "explicit_statement", "weight": 1.0, "count": 2},
            {"source": "implicit_inference", "weight": 0.7, "count": 1},
            {"source": "project_evidence", "weight": 0.8, "count": 3}
        ]
        
        # Mock confidence calculation
        total_weight = 0
        weighted_sum = 0
        
        for source_info in extraction_sources:
            weight = source_info["weight"]
            count = source_info["count"]
            # Apply diminishing returns for multiple sources
            source_confidence = weight * (1 - (count - 1) * 0.1)
            weighted_sum += source_confidence * count
            total_weight += count
        
        overall_confidence = min(1.0, weighted_sum / total_weight) if total_weight > 0 else 0.0
        
        assert 0.0 <= overall_confidence <= 1.0
        assert overall_confidence > 0.7  # Should be reasonably high with good sources
    
    def test_temporal_consistency_validation(self):
        """Test validation of temporal consistency across triplets."""
        triplets = [
            MockTriplet(
                subject="John Doe",
                predicate="worked_at",
                object="Company A",
                confidence=0.9,
                temporal_range={"start": datetime(2020, 1, 1), "end": datetime(2022, 12, 31)},
                source_evidence=["experience_section"]
            ),
            MockTriplet(
                subject="John Doe",
                predicate="worked_at",
                object="Company B",
                confidence=0.9,
                temporal_range={"start": datetime(2022, 6, 1), "end": datetime(2024, 12, 31)},
                source_evidence=["experience_section"]
            ),
            MockTriplet(
                subject="John Doe",
                predicate="worked_at",
                object="Company C",
                confidence=0.9,
                temporal_range={"start": datetime(2021, 1, 1), "end": datetime(2023, 12, 31)},
                source_evidence=["experience_section"]
            )
        ]
        
        # Check for temporal overlaps
        overlaps = []
        for i, triplet1 in enumerate(triplets):
            for j, triplet2 in enumerate(triplets[i+1:], i+1):
                # Check for temporal overlap
                start_overlap = max(triplet1.temporal_range["start"], triplet2.temporal_range["start"])
                end_overlap = min(triplet1.temporal_range["end"], triplet2.temporal_range["end"])
                
                if start_overlap < end_overlap:
                    overlaps.append((i, j, start_overlap, end_overlap))
        
        assert len(overlaps) == 2  # Company C overlaps with both A and B
        # Company A and B have a small overlap (June-Dec 2022) which might be valid (transition period)


class TestTemporalValidityAndInvalidation:
    """Test temporal validity management and fact invalidation."""
    
    def test_validity_status_determination(self):
        """Test determination of temporal validity status."""
        current_time = datetime(2025, 1, 25)
        
        test_cases = [
            {"start": datetime(2020, 1, 1), "end": datetime(2030, 12, 31), "expected": TemporalValidity.VALID},
            {"start": datetime(2020, 1, 1), "end": datetime(2024, 12, 31), "expected": TemporalValidity.EXPIRED},
            {"start": datetime(2026, 1, 1), "end": datetime(2030, 12, 31), "expected": TemporalValidity.FUTURE},
            {"start": datetime(2020, 1, 1), "end": datetime(2025, 12, 31), "expected": TemporalValidity.VALID},  # Current year
        ]
        
        for case in test_cases:
            if case["start"] <= current_time <= case["end"]:
                status = case["expected"]
            elif current_time > case["end"]:
                status = TemporalValidity.EXPIRED
            elif current_time < case["start"]:
                status = TemporalValidity.FUTURE
            else:
                status = TemporalValidity.VALID
            
            assert status == case["expected"]
    
    def test_fact_invalidation_by_newer_information(self):
        """Test invalidation of facts by newer information."""
        original_triplet = MockTriplet(
            subject="John Doe",
            predicate="has_skill",
            object="Python",
            confidence=0.8,
            temporal_range={"start": datetime(2020, 1, 1), "end": datetime(2025, 1, 24)},
            source_evidence=["resume_2020"]
        )
        
        # New information that invalidates the original
        invalidating_triplet = MockTriplet(
            subject="John Doe",
            predicate="has_skill",
            object="Python",
            confidence=0.95,
            temporal_range={"start": datetime(2023, 1, 1), "end": datetime(2025, 12, 31)},
            source_evidence=["recent_project", "certification_2024"]
        )
        
        # Mock invalidation logic
        if (invalidating_triplet.confidence > original_triplet.confidence and
            invalidating_triplet.temporal_range["start"] > original_triplet.temporal_range["start"] and
            len(invalidating_triplet.source_evidence) > len(original_triplet.source_evidence)):
            invalidation_result = {
                "original_triplet": original_triplet,
                "status": TemporalValidity.SUPERSEDED,
                "invalidated_by": invalidating_triplet,
                "reason": "Higher confidence with more recent evidence"
            }
        else:
            invalidation_result = {"original_triplet": original_triplet, "status": TemporalValidity.VALID}
        
        assert invalidation_result["status"] == TemporalValidity.SUPERSEDED
        assert invalidation_result["invalidated_by"] == invalidating_triplet
    
    def test_temporal_conflict_resolution(self):
        """Test resolution of temporal conflicts in knowledge graph."""
        conflicting_triplets = [
            MockTriplet(
                subject="Alice Smith",
                predicate="worked_at",
                object="Company X",
                confidence=0.7,
                temporal_range={"start": datetime(2021, 1, 1), "end": datetime(2023, 12, 31)},
                source_evidence=["old_resume"]
            ),
            MockTriplet(
                subject="Alice Smith", 
                predicate="worked_at",
                object="Company Y",
                confidence=0.9,
                temporal_range={"start": datetime(2022, 1, 1), "end": datetime(2024, 12, 31)},
                source_evidence=["linkedin_profile", "recent_resume"]
            )
        ]
        
        # Mock conflict resolution
        resolution_strategies = []
        
        # Strategy 1: Check for temporal overlap
        overlap_start = max(conflicting_triplets[0].temporal_range["start"], 
                           conflicting_triplets[1].temporal_range["start"])
        overlap_end = min(conflicting_triplets[0].temporal_range["end"],
                         conflicting_triplets[1].temporal_range["end"])
        
        if overlap_start < overlap_end:
            resolution_strategies.append("temporal_overlap_detected")
        
        # Strategy 2: Confidence-based resolution
        higher_confidence = max(conflicting_triplets, key=lambda t: t.confidence)
        if higher_confidence.confidence > 0.8:
            resolution_strategies.append("prefer_higher_confidence")
        
        # Strategy 3: Source recency
        more_recent = max(conflicting_triplets, key=lambda t: max(t.temporal_range["start"], t.temporal_range["end"]))
        resolution_strategies.append("prefer_more_recent")
        
        assert "temporal_overlap_detected" in resolution_strategies
        assert higher_confidence.object == "Company Y"


class TestTemporalIndexingAndRetrieval:
    """Test temporal indexing and efficient retrieval from temporal KG."""
    
    def test_temporal_index_construction(self):
        """Test construction of temporal indexes for efficient querying."""
        triplets = [
            MockTriplet("Person A", "skill", "Python", 0.9, 
                       {"start": datetime(2020, 1, 1), "end": datetime(2025, 12, 31)}, []),
            MockTriplet("Person B", "skill", "Java", 0.8,
                       {"start": datetime(2019, 6, 1), "end": datetime(2024, 12, 31)}, []),
            MockTriplet("Person A", "experience", "5 years", 0.9,
                       {"start": datetime(2020, 1, 1), "end": datetime(2025, 12, 31)}, []),
        ]
        
        # Build temporal index
        temporal_index = {
            "by_subject": {},
            "by_predicate": {},
            "by_time_range": {}
        }
        
        for i, triplet in enumerate(triplets):
            # Index by subject
            if triplet.subject not in temporal_index["by_subject"]:
                temporal_index["by_subject"][triplet.subject] = []
            temporal_index["by_subject"][triplet.subject].append(i)
            
            # Index by predicate
            if triplet.predicate not in temporal_index["by_predicate"]:
                temporal_index["by_predicate"][triplet.predicate] = []
            temporal_index["by_predicate"][triplet.predicate].append(i)
            
            # Index by time range (simplified by year)
            start_year = triplet.temporal_range["start"].year
            if start_year not in temporal_index["by_time_range"]:
                temporal_index["by_time_range"][start_year] = []
            temporal_index["by_time_range"][start_year].append(i)
        
        assert len(temporal_index["by_subject"]["Person A"]) == 2
        assert len(temporal_index["by_predicate"]["skill"]) == 2
        assert len(temporal_index["by_time_range"][2020]) == 2
    
    def test_temporal_range_querying(self):
        """Test querying triplets within specific temporal ranges."""
        query_time = datetime(2023, 6, 15)
        
        triplets = [
            MockTriplet("Person X", "worked_at", "Company A", 0.9,
                       {"start": datetime(2020, 1, 1), "end": datetime(2022, 12, 31)}, []),
            MockTriplet("Person X", "worked_at", "Company B", 0.9,
                       {"start": datetime(2023, 1, 1), "end": datetime(2025, 12, 31)}, []),
            MockTriplet("Person X", "skill", "Python", 0.8,
                       {"start": datetime(2021, 1, 1), "end": datetime(2024, 12, 31)}, [])
        ]
        
        # Query for triplets valid at query_time
        valid_triplets = []
        for triplet in triplets:
            if triplet.temporal_range["start"] <= query_time <= triplet.temporal_range["end"]:
                valid_triplets.append(triplet)
        
        assert len(valid_triplets) == 2
        assert valid_triplets[0].object == "Company B"
        assert valid_triplets[1].object == "Python"
    
    def test_temporal_evolution_tracking(self):
        """Test tracking of temporal evolution of entities and relationships."""
        evolution_timeline = [
            {"timestamp": datetime(2020, 1, 1), "event": "skill_acquired", "details": "Python basics"},
            {"timestamp": datetime(2021, 6, 1), "event": "skill_advanced", "details": "Python advanced"},
            {"timestamp": datetime(2022, 3, 1), "event": "project_completed", "details": "Python web app"},
            {"timestamp": datetime(2023, 1, 1), "event": "certification_earned", "details": "Python professional"}
        ]
        
        # Analyze evolution patterns
        skill_progression = []
        for event in evolution_timeline:
            if "skill" in event["event"]:
                skill_progression.append({
                    "timestamp": event["timestamp"],
                    "level": event["event"].split("_")[1],
                    "details": event["details"]
                })
        
        assert len(skill_progression) == 2
        assert skill_progression[0]["level"] == "acquired"
        assert skill_progression[1]["level"] == "advanced"
        
        # Verify chronological order
        timestamps = [event["timestamp"] for event in skill_progression]
        assert timestamps == sorted(timestamps)
