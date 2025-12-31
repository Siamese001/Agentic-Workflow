"""
Test suite for AST-based file placement in NamingAgent.

Tests the enhanced placement logic that uses AST signals to determine
the correct L1/L2 subfolder for files based on their content.
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from agentic_core.utils.core_extensions.NamingAgent import (
    NamingAgent, PlacementResult
)
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    AST_PLACEMENT_SIGNALS, PLACEMENT_CONFIDENCE
)


class TestASTPlacement:
    """Test AST-based file placement logic."""
    
    @pytest.fixture
    def temp_project_root(self):
        """Create a temporary project root for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        # Create basic agentic_core structure
        (temp_dir / "agentic_core").mkdir()
        for l1 in ["L1_cognition", "L2_execution", "L3_orchestration", 
                   "L4_state", "L5_safety", "utils", "schemas", "prompt_governance"]:
            (temp_dir / "agentic_core" / l1).mkdir()
        
        yield temp_dir
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def naming_agent(self, temp_project_root):
        """Create NamingAgent instance for testing."""
        return NamingAgent(temp_project_root)
    
    def test_placement_result_dataclass(self):
        """Test PlacementResult dataclass structure."""
        result = PlacementResult(
            full_path="agentic_core/L5_safety/validators",
            l1_folder="L5_safety",
            l2_subfolder="validators",
            confidence=0.85,
            confidence_level="HIGH",
            signals_matched=["class:TestValidator~.*Validator$", "keyword:validator"],
            reasoning="Matched 2 signals: class:TestValidator~.*Validator$, keyword:validator",
            alternative_paths=["agentic_core/L5_safety/guardrails"]
        )
        
        assert result.full_path == "agentic_core/L5_safety/validators"
        assert result.l1_folder == "L5_safety"
        assert result.l2_subfolder == "validators"
        assert result.confidence == 0.85
        assert result.confidence_level == "HIGH"
        assert len(result.signals_matched) == 2
        assert "class:TestValidator" in result.reasoning
    
    def test_thought_engine_placement(self, naming_agent):
        """Test placement of thought engine files."""
        content = '''
class ReasoningNode(BaseNode):
    """A node for reasoning tasks."""
    
    def think(self, input_data):
        """Process the input through reasoning."""
        pass

@thought_node
class DecompositionNode(ThoughtNode):
    """Decomposes complex tasks."""
    
    def decompose_task(self, task):
        """Break down task into subtasks."""
        pass
'''
        
        result = naming_agent.get_placement_guidance_v2(content)
        
        assert isinstance(result, PlacementResult)
        assert result.full_path == "agentic_core/L1_cognition/thought_engine"
        assert result.l1_folder == "L1_cognition"
        assert result.l2_subfolder == "thought_engine"
        assert result.confidence >= PLACEMENT_CONFIDENCE["HIGH"]
        assert any("class:ReasoningNode" in signal for signal in result.signals_matched)
        assert any("decorator:@thought_node" in signal for signal in result.signals_matched)
    
    def test_workflow_engine_placement(self, naming_agent):
        """Test placement of workflow engine files."""
        content = '''
from agentic_core.L3_orchestration.workflow_engines import BaseEngine

class MissionOrchestrator(WorkflowEngine):
    """Orchestrates mission execution."""
    
    def orchestrate_mission(self, mission):
        """Coordinate mission execution."""
        pass

@workflow
class TaskCoordinator(BaseEngine):
    """Coordinates task execution."""
    
    def coordinate_tasks(self, tasks):
        """Coordinate multiple tasks."""
        pass
'''
        
        result = naming_agent.get_placement_guidance_v2(content)
        
        assert result.full_path == "agentic_core/L3_orchestration/workflow_engines"
        assert result.l1_folder == "L3_orchestration"
        assert result.l2_subfolder == "workflow_engines"
        assert result.confidence >= PLACEMENT_CONFIDENCE["HIGH"]
        assert any("class:MissionOrchestrator" in signal for signal in result.signals_matched)
        assert any("inherits:WorkflowEngine" in signal for signal in result.signals_matched)
    
    def test_guardrails_placement(self, naming_agent):
        """Test placement of guardrail files."""
        content = '''
from agentic_core.L5_safety.guardrails import BaseGuardrail

@rate_limit
class RateLimitGuardrail(BaseGuardrail):
    """Limits API request rates."""
    
    def guard_request(self, request):
        """Guard against rate limit violations."""
        pass

class MutationGuardrail(BaseGuardrail):
    """Prevents destructive mutations."""
    
    def limit_mutations(self, operation):
        """Limit mutation operations."""
        pass
'''
        
        result = naming_agent.get_placement_guidance_v2(content)
        
        assert result.full_path == "agentic_core/L5_safety/guardrails"
        assert result.l1_folder == "L5_safety"
        assert result.l2_subfolder == "guardrails"
        assert result.confidence >= PLACEMENT_CONFIDENCE["HIGH"]
        assert any("class:RateLimitGuardrail" in signal for signal in result.signals_matched)
        assert any("decorator:@rate_limit" in signal for signal in result.signals_matched)
    
    def test_memory_placement(self, naming_agent):
        """Test placement of memory-related files."""
        content = '''
import pinecone
import redis

class VectorMemory(MemoryStore):
    """Vector-based memory storage."""
    
    def store_embedding(self, key, vector):
        """Store embedding in vector database."""
        pinecone.index_upsert(key, vector)
    
    def retrieve_vectors(self, query):
        """Retrieve similar vectors."""
        return pinecone.query(query)

class RedisCache(CacheManager):
    """Redis-based cache."""
    
    def cache_data(self, key, value):
        """Cache data in Redis."""
        redis.set(key, value)
'''
        
        result = naming_agent.get_placement_guidance_v2(content)
        
        assert result.full_path == "agentic_core/L4_state/memory"
        assert result.l1_folder == "L4_state"
        assert result.l2_subfolder == "memory"
        assert result.confidence >= PLACEMENT_CONFIDENCE["HIGH"]
        assert any("import:pinecone" in signal for signal in result.signals_matched)
        assert any("import:redis" in signal for signal in result.signals_matched)
    
    def test_mcp_placement(self, naming_agent):
        """Test placement of MCP client files."""
        content = '''
from mcp import fetch_client
import model_context_protocol

class MCPClient:
    """Model Context Protocol client."""
    
    def connect_to_server(self, endpoint):
        """Connect to MCP server."""
        pass
    
    def fetch_data(self, request):
        """Fetch data using MCP."""
        return fetch_client(request)
'''
        
        result = naming_agent.get_placement_guidance_v2(content)
        
        assert result.full_path == "agentic_core/L2_execution/mcp"
        assert result.l1_folder == "L2_execution"
        assert result.l2_subfolder == "mcp"
        assert result.confidence >= PLACEMENT_CONFIDENCE["MEDIUM"]
        assert any("import:mcp" in signal for signal in result.signals_matched)
    
    def test_schema_model_placement(self, naming_agent):
        """Test placement of schema/model files."""
        content = '''
from pydantic import BaseModel
from dataclasses import dataclass

@dataclass
class ConfigSchema:
    """Configuration schema."""
    param1: str
    param2: int

class UserModel(BaseModel):
    """User data model."""
    
    name: str
    email: str
    age: int
'''
        
        result = naming_agent.get_placement_guidance_v2(content)
        
        assert result.full_path == "agentic_core/schemas/models"
        assert result.l1_folder == "schemas"
        assert result.l2_subfolder == "models"
        assert result.confidence >= PLACEMENT_CONFIDENCE["HIGH"]
        assert any("import:pydantic" in signal for signal in result.signals_matched)
        assert any("decorator:@dataclass" in signal for signal in result.signals_matched)
    
    def test_low_confidence_fallback(self, naming_agent):
        """Test fallback for low confidence signals."""
        content = '''
class SomeRandomClass:
    """A class with no strong signals."""
    
    def do_something(self):
        """Do something generic."""
        pass
'''
        
        result = naming_agent.get_placement_guidance_v2(content)
        
        assert result.confidence < PLACEMENT_CONFIDENCE["LOW"]
        assert result.confidence_level == "LOW"
        assert "fallback:keyword_heuristic" in result.signals_matched
        assert result.full_path == "agentic_core/L1_cognition/thought_engine"  # Default fallback
    
    def test_alternative_paths_suggestion(self, naming_agent):
        """Test that alternative paths are provided."""
        content = '''
class ValidationEngine(BaseEngine):
    """Could be in L5_safety or L3_orchestration."""
    
    def validate_data(self, data):
        """Validate data."""
        pass
'''
        
        result = naming_agent.get_placement_guidance_v2(content)
        
        assert isinstance(result.alternative_paths, list)
        assert len(result.alternative_paths) <= 3  # Should provide up to 3 alternatives
        # The primary should be L3_orchestration due to "Engine" pattern
        assert result.full_path == "agentic_core/L3_orchestration/workflow_engines"
    
    def test_validate_current_placement_correct(self, naming_agent, temp_project_root):
        """Test validation of correctly placed files."""
        # Create a file in the correct location
        test_file = temp_project_root / "agentic_core/L5_safety/validators/TestValidator.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        
        content = '''
class TestValidator(BaseValidator):
    """A test validator."""
    
    def validate_something(self, data):
        """Validate something."""
        pass
'''
        
        test_file.write_text(content)
        
        is_valid, suggested = naming_agent.validate_current_placement(test_file)
        
        assert is_valid == True
        assert suggested.full_path == "agentic_core/L5_safety/validators"
    
    def test_validate_current_placement_incorrect(self, naming_agent, temp_project_root):
        """Test validation of incorrectly placed files."""
        # Create a file in the wrong location
        test_file = temp_project_root / "agentic_core/L1_cognition/TestValidator.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        
        content = '''
class TestValidator(BaseValidator):
    """A test validator."""
    
    def validate_something(self, data):
        """Validate something."""
        pass
'''
        
        test_file.write_text(content)
        
        is_valid, suggested = naming_agent.validate_current_placement(test_file)
        
        assert is_valid == False
        assert suggested.full_path == "agentic_core/L5_safety/validators"
        assert suggested.confidence >= PLACEMENT_CONFIDENCE["HIGH"]
    
    def test_move_to_canonical_location(self, naming_agent, temp_project_root):
        """Test moving file to canonical location."""
        # Create a file in the wrong location
        test_file = temp_project_root / "agentic_core/L1_cognition/TestGuardrail.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        
        content = '''
class TestGuardrail(BaseGuardrail):
    """A test guardrail."""
    
    def guard_something(self, data):
        """Guard something."""
        pass
'''
        
        test_file.write_text(content)
        
        # Test dry run
        result = naming_agent.move_to_canonical_location(test_file, dry_run=True)
        
        assert result['moved'] == False
        assert 'L5_safety/guardrails' in result['new_path']
        assert result['error'] is None
        
        # Test actual move
        result = naming_agent.move_to_canonical_location(test_file, dry_run=False)
        
        assert result['moved'] == True
        assert Path(result['new_path']).exists()
        assert not test_file.exists()
    
    def test_move_low_confidence_skipped(self, naming_agent, temp_project_root):
        """Test that low confidence files are not moved."""
        test_file = temp_project_root / "agentic_core/L1_cognition/RandomFile.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        
        content = '''
class RandomClass:
    """Random class with no signals."""
    pass
'''
        
        test_file.write_text(content)
        
        result = naming_agent.move_to_canonical_location(test_file, dry_run=False)
        
        assert result['moved'] == False
        assert 'Low confidence' in result['error']
        assert test_file.exists()  # File should not be moved


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
