"""
Integration tests for KG Pipeline
Tests knowledge graph construction, querying, and reasoning
"""
import pytest
from typing import Dict, Any, List
from unittest.mock import Mock
from datetime import datetime

# Import actual KG components when available
try:
    from agentic_core.l4_memory.providers.kg_provider import KGProvider
    from agentic_core.l4_memory.mappings.schema_mapper import SchemaMapper
    from agentic_core.l4_memory.temporal.temporal_store import TemporalStore
except ImportError:
    KGProvider = SchemaMapper = TemporalStore = Mock


class TestKGPipelineIntegration:
    """Test KG pipeline integration contracts"""
    
    def test_kg_graph_schema_valid_contract(self):
        """Test KG pipeline has valid graph schema"""
        if KGProvider is Mock:
            pytest.skip("KGProvider not implemented")
        
        kg_provider = KGProvider({})
        schema = kg_provider.get_schema()
        
        # Contract: schema should define valid entities and relations
        assert "entities" in schema
        assert "relations" in schema
        assert "properties" in schema
        
        # Should have core entity types
        entities = schema["entities"]
        assert "Person" in entities or "User" in entities or "UserProfile" in entities
        assert "Company" in entities or "Organization" in entities
        assert "Position" in entities or "Job" in entities or "Role" in entities
        
        # Should have core relation types
        relations = schema["relations"]
        assert any("works_at" in rel or "employed_by" in rel for rel in relations)
        assert any("has_skill" in rel or "skilled_in" in rel for rel in relations)
        assert any("located_in" in rel or "based_in" in rel for rel in relations)
        
        # Should validate schema structure
        assert kg_provider.validate_schema(schema) is True
    
    def test_kg_entity_construction_contract(self):
        """Test KG pipeline constructs entities correctly"""
        if KGProvider is Mock:
            pytest.skip("KGProvider not implemented")
        
        kg_provider = KGProvider({})
        
        # Test person entity construction
        person_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "skills": ["Python", "Machine Learning"],
            "experience": "5 years"
        }
        
        person_entity = kg_provider.create_entity("Person", person_data)
        
        assert person_entity["type"] == "Person"
        assert "id" in person_entity
        assert "properties" in person_entity
        assert person_entity["properties"]["name"] == "John Doe"
        assert isinstance(person_entity["properties"]["skills"], list)
        
        # Test company entity construction
        company_data = {
            "name": "TechCorp",
            "industry": "Software",
            "size": "100-500"
        }
        
        company_entity = kg_provider.create_entity("Company", company_data)
        
        assert company_entity["type"] == "Company"
        assert company_entity["properties"]["name"] == "TechCorp"
        assert company_entity["properties"]["industry"] == "Software"
    
    def test_kg_relation_creation_contract(self):
        """Test KG pipeline creates relations correctly"""
        if KGProvider is Mock:
            pytest.skip("KGProvider not implemented")
        
        kg_provider = KGProvider({})
        
        # Create test entities
        person = kg_provider.create_entity("Person", {"name": "Alice"})
        company = kg_provider.create_entity("Company", {"name": "DataInc"})
        skill = kg_provider.create_entity("Skill", {"name": "Python"})
        
        # Create relations
        works_at_relation = kg_provider.create_relation(
            person["id"], "works_at", company["id"],
            {"title": "Data Scientist", "start_date": "2023-01"}
        )
        
        has_skill_relation = kg_provider.create_relation(
            person["id"], "has_skill", skill["id"],
            {"proficiency": "expert", "years": 3}
        )
        
        # Validate relations
        assert works_at_relation["subject"] == person["id"]
        assert works_at_relation["predicate"] == "works_at"
        assert works_at_relation["object"] == company["id"]
        assert "properties" in works_at_relation
        
        assert has_skill_relation["subject"] == person["id"]
        assert has_skill_relation["predicate"] == "has_skill"
        assert has_skill_relation["object"] == skill["id"]
    
    def test_kg_query_reasoning_contract(self):
        """Test KG pipeline performs reasoning queries"""
        if KGProvider is Mock:
            pytest.skip("KGProvider not implemented")
        
        kg_provider = KGProvider({})
        
        # Build test graph
        person = kg_provider.create_entity("Person", {"name": "Bob", "experience": "3 years"})
        company1 = kg_provider.create_entity("Company", {"name": "TechCorp", "industry": "AI"})
        company2 = kg_provider.create_entity("Company", {"name": "DataInc", "industry": "ML"})
        skill = kg_provider.create_entity("Skill", {"name": "Machine Learning"})
        
        kg_provider.create_relation(person["id"], "works_at", company1["id"])
        kg_provider.create_relation(person["id"], "has_skill", skill["id"])
        kg_provider.create_relation(company1["id"], "uses_technology", skill["id"])
        kg_provider.create_relation(company2["id"], "uses_technology", skill["id"])
        
        # Test reasoning query: Find companies where person's skills are used
        query_result = kg_provider.query_reasoning({
            "type": "path_query",
            "start": person["id"],
            "path": ["has_skill", "used_by"],
            "target_type": "Company"
        })
        
        assert "results" in query_result
        assert len(query_result["results"]) >= 1
        
        # Should find TechCorp through skill connection
        company_ids = [result["id"] for result in query_result["results"]]
        assert company1["id"] in company_ids
    
    def test_kg_temporal_integration_contract(self):
        """Test KG integrates with temporal memory"""
        if all(cls is Mock for cls in [KGProvider, TemporalStore]):
            pytest.skip("KG components not implemented")
        
        kg_provider = KGProvider({})
        temporal_store = TemporalStore({})
        
        # Create temporal entity
        person_data = {
            "name": "Carol",
            "position": "Senior Engineer",
            "company": "StartupXYZ"
        }
        
        temporal_event = {
            "entity_id": "person_carol",
            "event_type": "employment_change",
            "data": person_data,
            "valid_at": datetime.utcnow(),
            "invalid_at": None
        }
        
        # Store in temporal memory
        stored_event = temporal_store.store_event(temporal_event)
        
        # Create KG entity from temporal data
        kg_entity = kg_provider.create_entity_from_temporal(stored_event)
        
        assert kg_entity["type"] == "Person"
        assert kg_entity["properties"]["name"] == "Carol"
        assert "temporal_metadata" in kg_entity
        assert kg_entity["temporal_metadata"]["valid_at"] == stored_event["valid_at"]
    
    def test_kg_schema_mapping_contract(self):
        """Test KG integrates with schema mapping"""
        if all(cls is Mock for cls in [KGProvider, SchemaMapper]):
            pytest.skip("KG components not implemented")
        
        kg_provider = KGProvider({})
        schema_mapper = SchemaMapper({})
        
        # Define source and target schemas
        source_schema = {
            "type": "object",
            "properties": {
                "user_name": {"type": "string"},
                "tech_stack": {"type": "array"},
                "years_exp": {"type": "integer"}
            }
        }
        
        target_schema = {
            "type": "object", 
            "properties": {
                "name": {"type": "string"},
                "skills": {"type": "array"},
                "experience": {"type": "integer"}
            }
        }
        
        # Map data
        source_data = {
            "user_name": "David",
            "tech_stack": ["Python", "React"],
            "years_exp": 4
        }
        
        mapped_data = schema_mapper.map_data(source_data, {
            "name": "user_name",
            "skills": "tech_stack", 
            "experience": "years_exp"
        })
        
        # Create KG entity from mapped data
        kg_entity = kg_provider.create_entity("Person", mapped_data)
        
        assert kg_entity["properties"]["name"] == "David"
        assert kg_entity["properties"]["skills"] == ["Python", "React"]
        assert kg_entity["properties"]["experience"] == 4
    
    def test_kg_invalid_relation_detected_contract(self):
        """Test KG detects and handles invalid relations"""
        if KGProvider is Mock:
            pytest.skip("KGProvider not implemented")
        
        kg_provider = KGProvider({})
        
        # Create test entities
        person = kg_provider.create_entity("Person", {"name": "Eve"})
        company = kg_provider.create_entity("Company", {"name": "TestCorp"})
        
        # Test invalid relation attempts
        invalid_relations = [
            {
                "subject": person["id"],
                "predicate": "invalid_relation",  # Not in schema
                "object": company["id"]
            },
            {
                "subject": "non_existent_id",  # Invalid subject
                "predicate": "works_at",
                "object": company["id"]
            },
            {
                "subject": person["id"],
                "predicate": "works_at",
                "object": "non_existent_id"  # Invalid object
            }
        ]
        
        for invalid_rel in invalid_relations:
            try:
                result = kg_provider.create_relation(
                    invalid_rel["subject"],
                    invalid_rel["predicate"], 
                    invalid_rel["object"]
                )
                
                # Should return error or validation failure
                assert "error" in result or result is None
                
            except (ValueError, KeyError):
                # Expected for invalid relations
                pass
    
    def test_kg_performance_contract(self):
        """Test KG operations meet performance requirements"""
        if KGProvider is Mock:
            pytest.skip("KGProvider not implemented")
        
        kg_provider = KGProvider({})
        
        # Create test data
        entities = []
        for i in range(100):
            entity = kg_provider.create_entity("Person", {
                "name": f"Person_{i}",
                "skill": f"Skill_{i % 10}"
            })
            entities.append(entity)
        
        # Test query performance
        import time
        start_time = time.time()
        
        query_result = kg_provider.query({
            "type": "entity_query",
            "entity_type": "Person",
            "limit": 50
        })
        
        elapsed_time = time.time() - start_time
        
        # Should complete quickly
        assert elapsed_time < 2.0  # 2 seconds for query
        assert "results" in query_result
        assert len(query_result["results"]) <= 50
    
    def test_kg_deterministic_behavior_contract(self):
        """Test KG behavior is deterministic"""
        if KGProvider is Mock:
            pytest.skip("KGProvider not implemented")
        
        kg_provider = KGProvider({})
        
        # Create same entities multiple times
        data = {"name": "Frank", "skill": "Python"}
        
        entity1 = kg_provider.create_entity("Person", data.copy())
        entity2 = kg_provider.create_entity("Person", data.copy())
        
        # Should generate consistent IDs and structure
        assert entity1["type"] == entity2["type"]
        assert entity1["properties"] == entity2["properties"]
        
        # Queries should be deterministic
        query = {"type": "entity_query", "entity_type": "Person"}
        result1 = kg_provider.query(query)
        result2 = kg_provider.query(query)
        
        assert len(result1["results"]) == len(result2["results"])
    
    def test_kg_graph_consistency_contract(self):
        """Test KG maintains graph consistency"""
        if KGProvider is Mock:
            pytest.skip("KGProvider not implemented")
        
        kg_provider = KGProvider({})
        
        # Create entities and relations
        person = kg_provider.create_entity("Person", {"name": "Grace"})
        company = kg_provider.create_entity("Company", {"name": "ConsistencyCorp"})
        
        relation = kg_provider.create_relation(
            person["id"], "works_at", company["id"]
        )
        
        # Verify graph consistency
        graph_stats = kg_provider.get_graph_statistics()
        
        assert graph_stats["entity_count"] >= 2
        assert graph_stats["relation_count"] >= 1
        assert graph_stats["is_consistent"] is True
        
        # Verify no orphan relations
        all_relations = kg_provider.get_all_relations()
        for rel in all_relations:
            assert kg_provider.entity_exists(rel["subject"]) is True
            assert kg_provider.entity_exists(rel["object"]) is True
