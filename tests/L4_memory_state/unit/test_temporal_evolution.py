"""
L4 Memory/State Layer Unit Tests - Temporal Evolution

Tests for temporal knowledge graph evolution and history without planning logic.
Focuses on temporal relationships, fact evolution, and historical tracking.
"""

import pytest
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from unittest.mock import Mock, patch, AsyncMock
import asyncio
import time
import uuid
from datetime import datetime, timedelta

# Mark all tests in this module as L4 memory/state unit tests
pytestmark = [pytest.mark.unit, pytest.mark.l4, pytest.mark.memory_state]


class TemporalRelation(Enum):
    """Types of temporal relationships."""
    BEFORE = "before"
    AFTER = "after"
    DURING = "during"
    OVERLAPS = "overlaps"
    PRECEDES = "precedes"
    SUCCEEDS = "succeeds"


class FactStatus(Enum):
    """Status of facts in temporal KG."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUPERSEDED = "superseded"
    EXPIRED = "expired"


@dataclass(frozen=True)
class MockTemporalFact:
    """Mock temporal fact for testing."""
    fact_id: str
    subject: str
    predicate: str
    object: str
    valid_from: datetime
    valid_until: Optional[datetime]
    confidence: float
    source: str
    status: FactStatus
    metadata: Dict[str, Any]


@dataclass(frozen=True)
class MockTemporalTriplet:
    """Mock temporal triplet for KG testing."""
    triplet_id: str
    subject: str
    relation: str
    object: str
    timestamp: datetime
    temporal_relation: Optional[TemporalRelation]
    expires_at: Optional[datetime]


class TestTemporalRelationships:
    """Test temporal relationship modeling and inference."""
    
    def test_temporal_relation_classification(self):
        """Test classification of temporal relationships between facts."""
        
        # Mock temporal relation classifier
        class TemporalRelationClassifier:
            @staticmethod
            def classify_relation(fact1: MockTemporalFact, fact2: MockTemporalFact) -> Optional[TemporalRelation]:
                """Classify temporal relationship between two facts."""
                f1_start, f1_end = fact1.valid_from, fact1.valid_until
                f2_start, f2_end = fact2.valid_from, fact2.valid_until
                
                # Handle open-ended intervals
                f1_end = f1_end or datetime.max
                f2_end = f2_end or datetime.max
                
                # Classify relationships
                if f1_end < f2_start:
                    return TemporalRelation.BEFORE
                elif f2_end < f1_start:
                    return TemporalRelation.AFTER
                elif f1_start <= f2_start and f1_end >= f2_end:
                    return TemporalRelation.DURING
                elif f1_start < f2_end and f2_start < f1_end:
                    return TemporalRelation.OVERLAPS
                elif f1_end <= f2_start:
                    return TemporalRelation.PRECEDES
                elif f2_end <= f1_start:
                    return TemporalRelation.SUCCEEDS
                
                return None
        
        classifier = TemporalRelationClassifier()
        
        # Create test facts with different temporal relationships
        base_time = datetime(2024, 1, 1)
        
        facts = [
            MockTemporalFact(
                "fact_1", "person_A", "worked_at", "company_X",
                base_time, base_time + timedelta(days=365), 0.9, "source_1",
                FactStatus.ACTIVE, {}
            ),
            MockTemporalFact(
                "fact_2", "person_A", "worked_at", "company_Y", 
                base_time + timedelta(days=400), base_time + timedelta(days=800), 0.9, "source_2",
                FactStatus.ACTIVE, {}
            ),
            MockTemporalFact(
                "fact_3", "person_A", "studied_at", "university_Z",
                base_time - timedelta(days=200), base_time - timedelta(days=50), 0.9, "source_3",
                FactStatus.ACTIVE, {}
            ),
            MockTemporalFact(
                "fact_4", "person_A", "lived_in", "city_B",
                base_time + timedelta(days=100), base_time + timedelta(days=600), 0.9, "source_4",
                FactStatus.ACTIVE, {}
            )
        ]
        
        # Test relationship classification
        test_cases = [
            (facts[0], facts[1], TemporalRelation.BEFORE),  # fact_1 before fact_2
            (facts[1], facts[0], TemporalRelation.AFTER),   # fact_2 after fact_1
            (facts[3], facts[0], TemporalRelation.OVERLAPS), # fact_4 overlaps fact_1
            (facts[0], facts[3], TemporalRelation.OVERLAPS), # fact_1 overlaps fact_4
            (facts[2], facts[0], TemporalRelation.BEFORE),  # fact_3 before fact_1
            (facts[0], facts[2], TemporalRelation.AFTER),   # fact_0 after fact_3
        ]
        
        classification_results = []
        for fact1, fact2, expected_relation in test_cases:
            classified_relation = classifier.classify_relation(fact1, fact2)
            classification_results.append({
                "fact1_id": fact1.fact_id,
                "fact2_id": fact2.fact_id,
                "expected": expected_relation,
                "actual": classified_relation,
                "correct": classified_relation == expected_relation
            })
        
        # Validate classification accuracy
        assert all(result["correct"] for result in classification_results)
        
        # Validate specific relationships
        before_result = next(r for r in classification_results if r["expected"] == TemporalRelation.BEFORE)
        assert before_result["actual"] == TemporalRelation.BEFORE
    
    def test_temporal_inference_chain(self):
        """Test inference of temporal relationships across fact chains."""
        
        class TemporalInferenceEngine:
            def __init__(self):
                self.facts = {}
                self.inferred_relations = {}
            
            def add_fact(self, fact: MockTemporalFact):
                """Add fact to knowledge base."""
                self.facts[fact.fact_id] = fact
            
            def infer_transitive_relations(self, start_fact_id: str, end_fact_id: str) -> List[TemporalRelation]:
                """Infer transitive temporal relations between facts."""
                if start_fact_id not in self.facts or end_fact_id not in self.facts:
                    return []
                
                # Build temporal graph
                graph = self._build_temporal_graph()
                
                # Find all paths from start to end
                paths = self._find_paths(graph, start_fact_id, end_fact_id)
                
                # Infer relations from paths
                inferred_relations = []
                for path in paths:
                    relation = self._infer_relation_from_path(path)
                    if relation:
                        inferred_relations.append(relation)
                
                return inferred_relations
            
            def _build_temporal_graph(self) -> Dict[str, List[str]]:
                """Build directed graph of temporal relationships."""
                graph = {}
                
                for fact_id, fact in self.facts.items():
                    graph[fact_id] = []
                    
                    for other_id, other_fact in self.facts.items():
                        if fact_id == other_id:
                            continue
                        
                        relation = self._classify_direct_relation(fact, other_fact)
                        if relation in [TemporalRelation.BEFORE, TemporalRelation.PRECEDES]:
                            graph[fact_id].append(other_id)
                
                return graph
            
            def _classify_direct_relation(self, fact1: MockTemporalFact, fact2: MockTemporalFact) -> Optional[TemporalRelation]:
                """Classify direct temporal relation."""
                f1_end = fact1.valid_until or datetime.max
                f2_start = fact2.valid_from
                
                if f1_end < f2_start:
                    return TemporalRelation.BEFORE
                elif f1_end <= f2_start:
                    return TemporalRelation.PRECEDES
                
                return None
            
            def _find_paths(self, graph: Dict[str, List[str]], start: str, end: str, 
                          path: List[str] = None) -> List[List[str]]:
                """Find all paths from start to end in graph."""
                if path is None:
                    path = []
                
                path = path + [start]
                
                if start == end:
                    return [path]
                
                if start not in graph:
                    return []
                
                paths = []
                for node in graph[start]:
                    if node not in path:  # Avoid cycles
                        new_paths = self._find_paths(graph, node, end, path)
                        for new_path in new_paths:
                            paths.append(new_path)
                
                return paths
            
            def _infer_relation_from_path(self, path: List[str]) -> Optional[TemporalRelation]:
                """Infer overall relation from a path of relations."""
                if len(path) < 2:
                    return None
                
                # If there's a direct path, the overall relation is BEFORE/PRECEDES
                return TemporalRelation.BEFORE
        
        # Create temporal inference engine
        engine = TemporalInferenceEngine()
        
        # Add facts in chronological sequence
        base_time = datetime(2024, 1, 1)
        facts = [
            MockTemporalFact("education", "person", "studied", "university",
                          base_time - timedelta(days=1000), base_time - timedelta(days=500), 0.9, "source",
                          FactStatus.ACTIVE, {}),
            MockTemporalFact("job1", "person", "worked", "company_a",
                          base_time, base_time + timedelta(days=400), 0.9, "source",
                          FactStatus.ACTIVE, {}),
            MockTemporalFact("job2", "person", "worked", "company_b",
                          base_time + timedelta(days=450), base_time + timedelta(days=900), 0.9, "source",
                          FactStatus.ACTIVE, {}),
            MockTemporalFact("job3", "person", "worked", "company_c",
                          base_time + timedelta(days=950), base_time + timedelta(days=1400), 0.9, "source",
                          FactStatus.ACTIVE, {})
        ]
        
        for fact in facts:
            engine.add_fact(fact)
        
        # Test transitive inference
        inference_cases = [
            ("education", "job1", [TemporalRelation.BEFORE]),
            ("education", "job2", [TemporalRelation.BEFORE]),
            ("education", "job3", [TemporalRelation.BEFORE]),
            ("job1", "job3", [TemporalRelation.BEFORE]),
            ("job1", "job2", [TemporalRelation.BEFORE])
        ]
        
        inference_results = []
        for start_id, end_id, expected_relations in inference_cases:
            inferred = engine.infer_transitive_relations(start_id, end_id)
            inference_results.append({
                "start": start_id,
                "end": end_id,
                "expected": expected_relations,
                "actual": inferred,
                "success": any(rel in inferred for rel in expected_relations)
            })
        
        # Validate inference results
        assert all(result["success"] for result in inference_results)
        
        # Validate specific inferences
        education_to_job3 = next(r for r in inference_results if r["start"] == "education" and r["end"] == "job3")
        assert TemporalRelation.BEFORE in education_to_job3["actual"]
    
    def test_temporal_consistency_validation(self):
        """Test validation of temporal consistency in knowledge graph."""
        
        class TemporalConsistencyValidator:
            def __init__(self):
                self.violations = []
            
            def validate_consistency(self, facts: List[MockTemporalFact]) -> List[Dict[str, Any]]:
                """Validate temporal consistency across facts."""
                self.violations = []
                
                # Check for overlapping contradictory facts
                self._check_contradictions(facts)
                
                # Check for impossible temporal sequences
                self._check_impossible_sequences(facts)
                
                # Check for circular dependencies
                self._check_circular_temporal_dependencies(facts)
                
                return self.violations
            
            def _check_contradictions(self, facts: List[MockTemporalFact]):
                """Check for contradictory facts with overlapping time periods."""
                # Group facts by subject-predicate combinations
                fact_groups = {}
                
                for fact in facts:
                    key = (fact.subject, fact.predicate)
                    if key not in fact_groups:
                        fact_groups[key] = []
                    fact_groups[key].append(fact)
                
                # Check each group for contradictions
                for (subject, predicate), group_facts in fact_groups.items():
                    if len(group_facts) < 2:
                        continue
                    
                    # Sort by start time
                    sorted_facts = sorted(group_facts, key=lambda f: f.valid_from)
                    
                    for i in range(len(sorted_facts)):
                        for j in range(i + 1, len(sorted_facts)):
                            fact1, fact2 = sorted_facts[i], sorted_facts[j]
                            
                            # Check for overlap with different objects
                            if (fact1.object != fact2.object and 
                                self._intervals_overlap(fact1, fact2)):
                                self.violations.append({
                                    "type": "contradictory_facts",
                                    "fact1_id": fact1.fact_id,
                                    "fact2_id": fact2.fact_id,
                                    "description": f"Contradictory {predicate} facts for {subject}"
                                })
            
            def _check_impossible_sequences(self, facts: List[MockTemporalFact]):
                """Check for impossible temporal sequences."""
                # Look for facts that would require time travel
                for fact in facts:
                    if fact.valid_until and fact.valid_until < fact.valid_from:
                        self.violations.append({
                            "type": "impossible_sequence",
                            "fact_id": fact.fact_id,
                            "description": "Fact valid_until is before valid_from"
                        })
            
            def _check_circular_temporal_dependencies(self, facts: List[MockTemporalFact]):
                """Check for circular temporal dependencies."""
                # This would be more complex in a real implementation
                # For now, just check for basic patterns
                pass
            
            def _intervals_overlap(self, fact1: MockTemporalFact, fact2: MockTemporalFact) -> bool:
                """Check if two fact intervals overlap."""
                f1_end = fact1.valid_until or datetime.max
                f2_end = fact2.valid_until or datetime.max
                
                return not (f1_end <= fact2.valid_from or f2_end <= fact1.valid_from)
        
        # Test consistency validation
        validator = TemporalConsistencyValidator()
        
        # Create facts with various consistency issues
        base_time = datetime(2024, 1, 1)
        test_facts = [
            # Consistent facts
            MockTemporalFact("fact_1", "person_A", "worked_at", "company_X",
                          base_time, base_time + timedelta(days=365), 0.9, "source_1",
                          FactStatus.ACTIVE, {}),
            
            # Contradictory fact (same person working at two companies simultaneously)
            MockTemporalFact("fact_2", "person_A", "worked_at", "company_Y",
                          base_time + timedelta(days=100), base_time + timedelta(days=200), 0.9, "source_2",
                          FactStatus.ACTIVE, {}),
            
            # Impossible sequence
            MockTemporalFact("fact_3", "person_B", "lived_in", "city_Z",
                          base_time + timedelta(days=500), base_time + timedelta(days=400), 0.9, "source_3",
                          FactStatus.ACTIVE, {})  # valid_until before valid_from
        ]
        
        violations = validator.validate_consistency(test_facts)
        
        # Validate violation detection
        assert len(violations) >= 2  # Should detect contradiction and impossible sequence
        
        # Check specific violation types
        contradiction_violations = [v for v in violations if v["type"] == "contradictory_facts"]
        sequence_violations = [v for v in violations if v["type"] == "impossible_sequence"]
        
        assert len(contradiction_violations) == 1
        assert len(sequence_violations) == 1
        
        # Validate violation details
        contradiction = contradiction_violations[0]
        assert "person_A" in contradiction["description"]
        assert "worked_at" in contradiction["description"]
        
        sequence_violation = sequence_violations[0]
        assert sequence_violation["fact_id"] == "fact_3"


class TestFactEvolution:
    """Test evolution and versioning of facts over time."""
    
    def test_fact_supersession(self):
        """Test supersession of facts by newer information."""
        
        class FactEvolutionManager:
            def __init__(self):
                self.facts = {}
                self.evolution_history = {}
            
            def add_fact(self, fact: MockTemporalFact):
                """Add fact and handle evolution."""
                self.facts[fact.fact_id] = fact
                
                # Check for supersession opportunities
                self._handle_supersession(fact)
            
            def _handle_supersession(self, new_fact: MockTemporalFact):
                """Handle fact supersession."""
                # Find potentially superseded facts
                candidates = self._find_supersession_candidates(new_fact)
                
                for candidate in candidates:
                    if self._should_supersede(candidate, new_fact):
                        self._supersede_fact(candidate, new_fact)
            
            def _find_supersession_candidates(self, fact: MockTemporalFact) -> List[MockTemporalFact]:
                """Find facts that could be superseded by new fact."""
                candidates = []
                
                for existing_fact in self.facts.values():
                    if existing_fact.fact_id == fact.fact_id:
                        continue
                    
                    # Same subject-predicate but different object
                    if (existing_fact.subject == fact.subject and 
                        existing_fact.predicate == fact.predicate and
                        existing_fact.object != fact.object):
                        candidates.append(existing_fact)
                
                return candidates
            
            def _should_supersede(self, old_fact: MockTemporalFact, new_fact: MockTemporalFact) -> bool:
                """Determine if new fact should supersede old fact."""
                # Higher confidence wins
                if new_fact.confidence > old_fact.confidence:
                    return True
                
                # More recent source wins
                if new_fact.source > old_fact.source:  # Assuming source strings are comparable
                    return True
                
                return False
            
            def _supersede_fact(self, old_fact: MockTemporalFact, new_fact: MockTemporalFact):
                """Supersede old fact with new fact."""
                # Update old fact status
                updated_old_fact = old_fact._replace(status=FactStatus.SUPERSEDED)
                self.facts[old_fact.fact_id] = updated_old_fact
                
                # Record evolution
                if old_fact.fact_id not in self.evolution_history:
                    self.evolution_history[old_fact.fact_id] = []
                
                self.evolution_history[old_fact.fact_id].append({
                    "action": "superseded_by",
                    "new_fact_id": new_fact.fact_id,
                    "timestamp": datetime.now(),
                    "reason": "higher_confidence_or_newer_source"
                })
            
            def get_evolution_chain(self, fact_id: str) -> List[Dict[str, Any]]:
                """Get evolution chain for a fact."""
                return self.evolution_history.get(fact_id, [])
        
        # Test fact supersession
        evolution_manager = FactEvolutionManager()
        
        base_time = datetime(2024, 1, 1)
        
        # Add initial fact
        initial_fact = MockTemporalFact(
            "fact_1", "person_A", "skill_level", "intermediate",
            base_time, base_time + timedelta(days=180), 0.7, "source_1",
            FactStatus.ACTIVE, {}
        )
        evolution_manager.add_fact(initial_fact)
        
        # Add superseding fact with higher confidence
        superseding_fact = MockTemporalFact(
            "fact_2", "person_A", "skill_level", "advanced",
            base_time + timedelta(days=90), base_time + timedelta(days=270), 0.9, "source_2",
            FactStatus.ACTIVE, {}
        )
        evolution_manager.add_fact(superseding_fact)
        
        # Validate supersession
        old_fact = evolution_manager.facts["fact_1"]
        new_fact = evolution_manager.facts["fact_2"]
        
        assert old_fact.status == FactStatus.SUPERSEDED
        assert new_fact.status == FactStatus.ACTIVE
        
        # Validate evolution history
        evolution_chain = evolution_manager.get_evolution_chain("fact_1")
        assert len(evolution_chain) == 1
        assert evolution_chain[0]["action"] == "superseded_by"
        assert evolution_chain[0]["new_fact_id"] == "fact_2"
    
    def test_fact_expiration(self):
        """Test automatic expiration of facts based on temporal validity."""
        
        class FactExpirationManager:
            def __init__(self):
                self.facts = {}
                self.expiration_log = []
            
            def add_fact(self, fact: MockTemporalFact):
                """Add fact with expiration handling."""
                self.facts[fact.fact_id] = fact
                
                # Check if fact should be expired immediately
                if self._is_expired(fact):
                    self._expire_fact(fact)
            
            def check_expirations(self, current_time: datetime):
                """Check and expire facts that are no longer valid."""
                for fact in self.facts.values():
                    if fact.status == FactStatus.ACTIVE and self._is_expired_at(fact, current_time):
                        self._expire_fact(fact)
            
            def _is_expired(self, fact: MockTemporalFact) -> bool:
                """Check if fact is expired (relative to current time)."""
                return self._is_expired_at(fact, datetime.now())
            
            def _is_expired_at(self, fact: MockTemporalFact, check_time: datetime) -> bool:
                """Check if fact is expired at specific time."""
                if fact.valid_until is None:
                    return False  # No expiration date
                
                return check_time > fact.valid_until
            
            def _expire_fact(self, fact: MockTemporalFact):
                """Mark fact as expired."""
                if fact.status != FactStatus.EXPIRED:
                    expired_fact = fact._replace(status=FactStatus.EXPIRED)
                    self.facts[fact.fact_id] = expired_fact
                    
                    self.expiration_log.append({
                        "fact_id": fact.fact_id,
                        "expired_at": datetime.now(),
                        "valid_until": fact.valid_until
                    })
            
            def get_active_facts(self) -> List[MockTemporalFact]:
                """Get all currently active facts."""
                return [fact for fact in self.facts.values() if fact.status == FactStatus.ACTIVE]
        
        # Test fact expiration
        expiration_manager = FactExpirationManager()
        
        base_time = datetime(2024, 1, 1)
        
        # Create facts with different expiration times
        facts = [
            MockTemporalFact("fact_1", "person_A", "worked_at", "company_X",
                          base_time, base_time + timedelta(days=100), 0.9, "source_1",
                          FactStatus.ACTIVE, {}),
            MockTemporalFact("fact_2", "person_A", "worked_at", "company_Y",
                          base_time + timedelta(days=150), base_time + timedelta(days=300), 0.9, "source_2",
                          FactStatus.ACTIVE, {}),
            MockTemporalFact("fact_3", "person_A", "skill_level", "expert",
                          base_time, None, 0.9, "source_3",  # No expiration
                          FactStatus.ACTIVE, {}),
            MockTemporalFact("fact_4", "person_A", "lived_in", "city_Z",
                          base_time, base_time - timedelta(days=50), 0.9, "source_4",  # Already expired
                          FactStatus.ACTIVE, {})
        ]
        
        # Add facts
        for fact in facts:
            expiration_manager.add_fact(fact)
        
        # Check initial state
        active_facts = expiration_manager.get_active_facts()
        assert len(active_facts) == 2  # fact_1, fact_2, fact_3 should be active, fact_4 expired
        
        # Check expiration at specific time
        check_time = base_time + timedelta(days=120)
        expiration_manager.check_expirations(check_time)
        
        active_facts = expiration_manager.get_active_facts()
        assert len(active_facts) == 2  # fact_1 expired, fact_2 and fact_3 still active
        
        # Check expiration log
        assert len(expiration_manager.expiration_log) >= 2  # fact_4 and fact_1 should be expired
    
    def test_fact_conflict_resolution(self):
        """Test resolution of conflicting facts."""
        
        class FactConflictResolver:
            def __init__(self):
                self.facts = {}
                self.conflict_resolutions = []
            
            def add_fact(self, fact: MockTemporalFact):
                """Add fact and resolve conflicts."""
                self.facts[fact.fact_id] = fact
                self._resolve_conflicts_for_fact(fact)
            
            def _resolve_conflicts_for_fact(self, new_fact: MockTemporalFact):
                """Resolve conflicts for newly added fact."""
                conflicts = self._find_conflicts(new_fact)
                
                for conflict in conflicts:
                    resolution = self._resolve_conflict(new_fact, conflict)
                    self.conflict_resolutions.append(resolution)
            
            def _find_conflicts(self, fact: MockTemporalFact) -> List[MockTemporalFact]:
                """Find facts that conflict with given fact."""
                conflicts = []
                
                for existing_fact in self.facts.values():
                    if existing_fact.fact_id == fact.fact_id:
                        continue
                    
                    # Check for direct contradictions
                    if (existing_fact.subject == fact.subject and
                        existing_fact.predicate == fact.predicate and
                        existing_fact.object != fact.object and
                        self._temporal_overlap(existing_fact, fact)):
                        conflicts.append(existing_fact)
                
                return conflicts
            
            def _temporal_overlap(self, fact1: MockTemporalFact, fact2: MockTemporalFact) -> bool:
                """Check if two facts have temporal overlap."""
                f1_end = fact1.valid_until or datetime.max
                f2_end = fact2.valid_until or datetime.max
                
                return not (f1_end <= fact2.valid_from or f2_end <= fact1.valid_from)
            
            def _resolve_conflict(self, fact1: MockTemporalFact, fact2: MockTemporalFact) -> Dict[str, Any]:
                """Resolve conflict between two facts."""
                # Resolution strategy: keep fact with higher confidence
                if fact1.confidence > fact2.confidence:
                    winner, loser = fact1, fact2
                elif fact2.confidence > fact1.confidence:
                    winner, loser = fact2, fact1
                else:
                    # Equal confidence: keep more recent
                    winner, loser = (fact1, fact2) if fact1.valid_from > fact2.valid_from else (fact2, fact1)
                
                # Mark loser as inactive
                updated_loser = loser._replace(status=FactStatus.INACTIVE)
                self.facts[loser.fact_id] = updated_loser
                
                return {
                    "winner_id": winner.fact_id,
                    "loser_id": loser.fact_id,
                    "resolution_strategy": "higher_confidence",
                    "timestamp": datetime.now()
                }
            
            def get_conflict_resolutions(self) -> List[Dict[str, Any]]:
                """Get all conflict resolutions."""
                return self.conflict_resolutions
        
        # Test conflict resolution
        resolver = FactConflictResolver()
        
        base_time = datetime(2024, 1, 1)
        
        # Add conflicting facts
        fact1 = MockTemporalFact("fact_1", "person_A", "skill_level", "intermediate",
                               base_time, base_time + timedelta(days=180), 0.7, "source_1",
                               FactStatus.ACTIVE, {})
        
        fact2 = MockTemporalFact("fact_2", "person_A", "skill_level", "advanced",
                               base_time + timedelta(days=30), base_time + timedelta(days=210), 0.9, "source_2",
                               FactStatus.ACTIVE, {})
        
        fact3 = MockTemporalFact("fact_3", "person_A", "skill_level", "expert",
                               base_time + timedelta(days=60), base_time + timedelta(days=240), 0.8, "source_3",
                               FactStatus.ACTIVE, {})
        
        # Add facts and resolve conflicts
        resolver.add_fact(fact1)
        resolver.add_fact(fact2)  # Should conflict with fact1
        resolver.add_fact(fact3)  # Should conflict with fact2
        
        # Validate conflict resolution
        resolutions = resolver.get_conflict_resolutions()
        assert len(resolutions) == 2
        
        # Check final status
        final_facts = list(resolver.facts.values())
        active_facts = [f for f in final_facts if f.status == FactStatus.ACTIVE]
        inactive_facts = [f for f in final_facts if f.status == FactStatus.INACTIVE]
        
        assert len(active_facts) == 1  # Only one should remain active
        assert len(inactive_facts) == 2  # Two should be marked inactive
        
        # The highest confidence fact should win
        winner = active_facts[0]
        assert winner.confidence == 0.9  # fact2 should win
        assert winner.object == "advanced"


class TestHistoricalTracking:
    """Test historical tracking and querying of temporal knowledge."""
    
    def test_temporal_query_interface(self):
        """Test querying knowledge graph at specific points in time."""
        
        class TemporalQueryInterface:
            def __init__(self):
                self.facts = []
            
            def add_fact(self, fact: MockTemporalFact):
                """Add fact to temporal knowledge base."""
                self.facts.append(fact)
            
            def query_at_time(self, query_time: datetime, subject: Optional[str] = None,
                            predicate: Optional[str] = None, object: Optional[str] = None) -> List[MockTemporalFact]:
                """Query facts valid at specific time."""
                results = []
                
                for fact in self.facts:
                    # Check temporal validity
                    if not self._is_valid_at_time(fact, query_time):
                        continue
                    
                    # Check filters
                    if subject and fact.subject != subject:
                        continue
                    if predicate and fact.predicate != predicate:
                        continue
                    if object and fact.object != object:
                        continue
                    
                    results.append(fact)
                
                return results
            
            def query_temporal_range(self, start_time: datetime, end_time: datetime,
                                   subject: Optional[str] = None, predicate: Optional[str] = None) -> List[MockTemporalFact]:
                """Query facts valid within temporal range."""
                results = []
                
                for fact in self.facts:
                    # Check if fact overlaps with query range
                    if not self._overlaps_with_range(fact, start_time, end_time):
                        continue
                    
                    # Check filters
                    if subject and fact.subject != subject:
                        continue
                    if predicate and fact.predicate != predicate:
                        continue
                    
                    results.append(fact)
                
                return results
            
            def get_fact_evolution(self, fact_id: str) -> List[MockTemporalFact]:
                """Get evolution history of a specific fact."""
                return [fact for fact in self.facts if fact.fact_id == fact_id]
            
            def _is_valid_at_time(self, fact: MockTemporalFact, query_time: datetime) -> bool:
                """Check if fact is valid at specific time."""
                if fact.status not in [FactStatus.ACTIVE, FactStatus.SUPERSEDED]:
                    return False
                
                if query_time < fact.valid_from:
                    return False
                
                if fact.valid_until and query_time > fact.valid_until:
                    return False
                
                return True
            
            def _overlaps_with_range(self, fact: MockTemporalFact, start_time: datetime, end_time: datetime) -> bool:
                """Check if fact overlaps with temporal range."""
                fact_end = fact.valid_until or datetime.max
                
                return not (fact_end <= start_time or fact.valid_from >= end_time)
        
        # Test temporal querying
        query_interface = TemporalQueryInterface()
        
        base_time = datetime(2024, 1, 1)
        
        # Add facts with different temporal ranges
        facts = [
            MockTemporalFact("fact_1", "person_A", "worked_at", "company_X",
                          base_time, base_time + timedelta(days=365), 0.9, "source_1",
                          FactStatus.ACTIVE, {}),
            MockTemporalFact("fact_2", "person_A", "worked_at", "company_Y",
                          base_time + timedelta(days=400), base_time + timedelta(days=800), 0.9, "source_2",
                          FactStatus.ACTIVE, {}),
            MockTemporalFact("fact_3", "person_A", "skill_level", "intermediate",
                          base_time - timedelta(days=100), base_time + timedelta(days=200), 0.9, "source_3",
                          FactStatus.ACTIVE, {}),
            MockTemporalFact("fact_4", "person_A", "skill_level", "advanced",
                          base_time + timedelta(days=250), base_time + timedelta(days=600), 0.9, "source_4",
                          FactStatus.ACTIVE, {})
        ]
        
        for fact in facts:
            query_interface.add_fact(fact)
        
        # Test point-in-time queries
        query_time_1 = base_time + timedelta(days=50)
        results_1 = query_interface.query_at_time(query_time_1, subject="person_A")
        
        assert len(results_1) == 2  # fact_1 and fact_3 should be valid
        assert set(f.fact_id for f in results_1) == {"fact_1", "fact_3"}
        
        query_time_2 = base_time + timedelta(days=500)
        results_2 = query_interface.query_at_time(query_time_2, subject="person_A")
        
        assert len(results_2) == 2  # fact_2 and fact_4 should be valid
        assert set(f.fact_id for f in results_2) == {"fact_2", "fact_4"}
        
        # Test range queries
        start_time = base_time + timedelta(days=300)
        end_time = base_time + timedelta(days=700)
        range_results = query_interface.query_temporal_range(start_time, end_time, subject="person_A")
        
        assert len(range_results) == 3  # fact_1, fact_2, fact_4 overlap with range
        
        # Test filtered queries
        skill_results = query_interface.query_at_time(query_time_2, subject="person_A", predicate="skill_level")
        assert len(skill_results) == 1
        assert skill_results[0].fact_id == "fact_4"
    
    def test_temporal_aggregation(self):
        """Test aggregation of facts over temporal periods."""
        
        class TemporalAggregator:
            def __init__(self):
                self.facts = []
            
            def add_fact(self, fact: MockTemporalFact):
                """Add fact for aggregation."""
                self.facts.append(fact)
            
            def aggregate_by_period(self, period: str, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
                """Aggregate facts by time period."""
                if period == "monthly":
                    return self._aggregate_monthly(start_time, end_time)
                elif period == "yearly":
                    return self._aggregate_yearly(start_time, end_time)
                else:
                    return {"error": "Unsupported period"}
            
            def _aggregate_monthly(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
                """Aggregate facts by month."""
                monthly_data = {}
                
                for fact in self.facts:
                    # Find months this fact covers
                    fact_months = self._get_months_covered(fact, start_time, end_time)
                    
                    for month_key in fact_months:
                        if month_key not in monthly_data:
                            monthly_data[month_key] = {
                                "fact_count": 0,
                                "subjects": set(),
                                "predicates": set(),
                                "avg_confidence": 0.0,
                                "total_confidence": 0.0
                            }
                        
                        monthly_data[month_key]["fact_count"] += 1
                        monthly_data[month_key]["subjects"].add(fact.subject)
                        monthly_data[month_key]["predicates"].add(fact.predicate)
                        monthly_data[month_key]["total_confidence"] += fact.confidence
                
                # Calculate averages
                for month_data in monthly_data.values():
                    if month_data["fact_count"] > 0:
                        month_data["avg_confidence"] = month_data["total_confidence"] / month_data["fact_count"]
                    month_data["subjects"] = list(month_data["subjects"])
                    month_data["predicates"] = list(month_data["predicates"])
                    del month_data["total_confidence"]
                
                return monthly_data
            
            def _get_months_covered(self, fact: MockTemporalFact, start_time: datetime, end_time: datetime) -> List[str]:
                """Get month keys covered by fact."""
                fact_start = max(fact.valid_from, start_time)
                fact_end = min(fact.valid_until or end_time, end_time)
                
                months = []
                current = fact_start.replace(day=1)
                
                while current <= fact_end:
                    month_key = current.strftime("%Y-%m")
                    months.append(month_key)
                    
                    # Move to next month
                    if current.month == 12:
                        current = current.replace(year=current.year + 1, month=1)
                    else:
                        current = current.replace(month=current.month + 1)
                
                return months
            
            def _aggregate_yearly(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
                """Aggregate facts by year."""
                # Similar to monthly but with yearly granularity
                return {"message": "Yearly aggregation not implemented in test"}
        
        # Test temporal aggregation
        aggregator = TemporalAggregator()
        
        base_time = datetime(2024, 1, 1)
        
        # Add facts spanning multiple months
        facts = [
            MockTemporalFact("fact_1", "person_A", "worked_at", "company_X",
                          base_time, base_time + timedelta(days=60), 0.9, "source_1",
                          FactStatus.ACTIVE, {}),
            MockTemporalFact("fact_2", "person_A", "skill_level", "intermediate",
                          base_time + timedelta(days=30), base_time + timedelta(days=120), 0.8, "source_2",
                          FactStatus.ACTIVE, {}),
            MockTemporalFact("fact_3", "person_A", "lived_in", "city_Y",
                          base_time + timedelta(days=90), base_time + timedelta(days=180), 0.7, "source_3",
                          FactStatus.ACTIVE, {})
        ]
        
        for fact in facts:
            aggregator.add_fact(fact)
        
        # Test monthly aggregation
        start_time = base_time
        end_time = base_time + timedelta(days=200)
        
        monthly_aggregation = aggregator.aggregate_by_period("monthly", start_time, end_time)
        
        # Validate aggregation results
        assert isinstance(monthly_aggregation, dict)
        assert len(monthly_aggregation) >= 3  # Should cover at least 3 months
        
        # Check specific month data
        jan_2024 = monthly_aggregation.get("2024-01")
        assert jan_2024 is not None
        assert jan_2024["fact_count"] >= 1
        assert "person_A" in jan_2024["subjects"]
        assert jan_2024["avg_confidence"] > 0
        
        feb_2024 = monthly_aggregation.get("2024-02")
        assert feb_2024 is not None
        assert feb_2024["fact_count"] >= 1
