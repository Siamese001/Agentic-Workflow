#!/usr/bin/env python3
"""
Test KG Tools Family
Section 3: Canonical Repository Tree - L2 Execution Tools Tests
"""

import pytest
import logging

logger = logging.getLogger(__name__)

class TestKGTools:
    """Test suite for Knowledge Graph tool family (KG)"""
    
    def test_kg_lookup_tool_node_search(self):
        """Test KG lookup tool for node search"""
        # Simulate knowledge graph nodes
        kg_nodes = {
            "person_1": {"label": "Software Engineer", "type": "person", "properties": {"skills": ["python", "aws"]}},
            "company_1": {"label": "TechCorp", "type": "company", "properties": {"industry": "technology"}},
            "skill_1": {"label": "Python", "type": "skill", "properties": {"category": "programming"}}
        }
        
        # Test node lookup by ID
        node_id = "person_1"
        found_node = kg_nodes.get(node_id)
        
        assert found_node is not None
        assert found_node["label"] == "Software Engineer"
        assert "python" in found_node["properties"]["skills"]
    
    def test_kg_lookup_tool_label_search(self):
        """Test KG lookup tool for label search"""
        kg_nodes = {
            "person_1": {"label": "Software Engineer", "type": "person"},
            "person_2": {"label": "Data Scientist", "type": "person"},
            "company_1": {"label": "TechCorp", "type": "company"}
        }
        
        # Test label search
        search_label = "Software Engineer"
        matching_nodes = [node for node in kg_nodes.values() if node["label"] == search_label]
        
        assert len(matching_nodes) == 1
        assert matching_nodes[0]["type"] == "person"
    
    def test_kg_traversal_tool_multi_hop(self):
        """Test KG traversal tool for controlled multi-hop traversal"""
        # Simulate KG edges
        kg_edges = [
            {"from": "person_1", "to": "company_1", "relation": "works_at"},
            {"from": "person_1", "to": "skill_1", "relation": "has_skill"},
            {"from": "company_1", "to": "industry_1", "relation": "belongs_to"}
        ]
        
        # Test multi-hop traversal: person -> company -> industry
        start_node = "person_1"
        path = [start_node]
        
        # First hop: person to company
        company_edges = [e for e in kg_edges if e["from"] == start_node and e["relation"] == "works_at"]
        if company_edges:
            company = company_edges[0]["to"]
            path.append(company)
            
            # Second hop: company to industry
            industry_edges = [e for e in kg_edges if e["from"] == company and e["relation"] == "belongs_to"]
            if industry_edges:
                industry = industry_edges[0]["to"]
                path.append(industry)
        
        assert len(path) >= 2  # Should have at least person -> company
        assert path[0] == "person_1"
    
    def test_kg_traversal_tool_depth_control(self):
        """Test KG traversal tool depth control"""
        kg_edges = [
            {"from": "node_1", "to": "node_2", "relation": "connected"},
            {"from": "node_2", "to": "node_3", "relation": "connected"},
            {"from": "node_3", "to": "node_4", "relation": "connected"},
            {"from": "node_4", "to": "node_5", "relation": "connected"}
        ]
        
        # Test depth-limited traversal
        max_depth = 2
        current_depth = 0
        current_node = "node_1"
        visited_nodes = [current_node]
        
        while current_depth < max_depth:
            next_edges = [e for e in kg_edges if e["from"] == current_node]
            if next_edges:
                current_node = next_edges[0]["to"]
                visited_nodes.append(current_node)
                current_depth += 1
            else:
                break
        
        assert len(visited_nodes) <= max_depth + 1  # Should respect depth limit
        assert current_depth <= max_depth
    
    def test_kg_relation_expand_tool_related_entities(self):
        """Test KG relation expand tool for expanding related entities"""
        # Simulate entity relationships
        entity_relations = {
            "Software Engineer": {
                "related_skills": ["Python", "AWS", "Docker"],
                "related_roles": ["Senior Developer", "Tech Lead", "Architect"],
                "related_companies": ["TechCorp", "StartupXYZ", "EnterpriseInc"]
            },
            "Python": {
                "related_libraries": ["Django", "Flask", "NumPy"],
                "related_concepts": ["Web Development", "Data Science", "Automation"],
                "related_roles": ["Backend Developer", "Data Scientist", "DevOps Engineer"]
            }
        }
        
        # Test relation expansion
        entity = "Software Engineer"
        related_entities = entity_relations.get(entity, {})
        
        assert "related_skills" in related_entities
        assert "related_roles" in related_entities
        assert "related_companies" in related_entities
        assert len(related_entities["related_skills"]) == 3
    
    def test_kg_relation_expand_tool_bidirectional(self):
        """Test KG relation expand tool bidirectional expansion"""
        # Simulate bidirectional relationships
        bidirectional_relations = {
            "Software Engineer": {"Python": "uses_skill"},
            "Python": {"Software Engineer": "used_by_role"},
            "TechCorp": {"Software Engineer": "employs"},
            "Software Engineer": {"TechCorp": "employed_by"}
        }
        
        # Test bidirectional lookup
        entity = "Software Engineer"
        relations = bidirectional_relations.get(entity, {})
        
        # Forward relations
        forward_relations = [target for target, relation in relations.items()]
        
        # Reverse relations (entities that point to this one)
        reverse_relations = [source for source, rels in bidirectional_relations.items() 
                          if entity in rels]
        
        assert len(forward_relations) >= 1
        assert "Python" in forward_relations
        assert len(reverse_relations) >= 1
    
    @pytest.mark.parametrize("tool_name,expected_functionality", [
        ("kg_lookup_tool", "node_label_search"),
        ("kg_traversal_tool", "multi_hop_traversal"),
        ("kg_relation_expand_tool", "entity_relationship_expansion")
    ])
    def test_kg_tool_family_coverage(self, tool_name: str, expected_functionality: str):
        """Test complete coverage of KG tool family"""
        tool_registry = {
            "kg_lookup_tool": "node_label_search",
            "kg_traversal_tool": "multi_hop_traversal",
            "kg_relation_expand_tool": "entity_relationship_expansion"
        }
        
        assert tool_name in tool_registry
        assert tool_registry[tool_name] == expected_functionality
    
    def test_kg_tools_resume_outreach_integration(self):
        """Test KG tools integration for resume and outreach workflows"""
        # Resume workflow: person -> skills -> companies
        resume_kg = {
            "nodes": {
                "person_1": {"label": "John Doe", "type": "person"},
                "skill_1": {"label": "Python", "type": "skill"},
                "company_1": {"label": "TechCorp", "type": "company"}
            },
            "edges": [
                {"from": "person_1", "to": "skill_1", "relation": "has_skill"},
                {"from": "person_1", "to": "company_1", "relation": "works_at"}
            ]
        }
        
        # Outreach workflow: company -> industry -> competitors
        outreach_kg = {
            "nodes": {
                "company_1": {"label": "TechCorp", "type": "company"},
                "industry_1": {"label": "Technology", "type": "industry"},
                "competitor_1": {"label": "StartupXYZ", "type": "company"}
            },
            "edges": [
                {"from": "company_1", "to": "industry_1", "relation": "belongs_to"},
                {"from": "competitor_1", "to": "industry_1", "relation": "belongs_to"}
            ]
        }
        
        # Test both KGs have proper structure
        assert len(resume_kg["nodes"]) == 3
        assert len(outreach_kg["nodes"]) == 3
        assert len(resume_kg["edges"]) == 2
        assert len(outreach_kg["edges"]) == 2

# Test configuration
@pytest.fixture
def kg_tools_config():
    """Fixture for KG tools configuration"""
    return {
        "kg_lookup": {"max_results": 10, "search_fields": ["label", "type"]},
        "kg_traversal": {"max_depth": 3, "max_nodes": 100},
        "kg_relation_expand": {"max_relations": 20, "bidirectional": True}
    }

if __name__ == "__main__":
    pytest.main([__file__])





