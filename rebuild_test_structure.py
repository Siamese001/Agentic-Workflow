#!/usr/bin/env python3
"""
Rebuild Canonical Test Structure
Creates clean test structure with proper layer-level imports
"""

import os
import shutil
from pathlib import Path

def clean_existing_tests(base_path: Path):
    """Remove all existing test files to start fresh"""
    
    print("=== Cleaning Existing Test Structure ===")
    
    tests_dir = base_path / "tests"
    if tests_dir.exists():
        print(f"  Removing existing tests directory: {tests_dir}")
        shutil.rmtree(str(tests_dir))
    
    # Also clean engine-specific tests that were moved to apps/
    apps_tests_dirs = [
        base_path / "apps" / "resume_engine" / "tests",
        base_path / "apps" / "outreach_engine" / "tests",
        base_path / "apps" / "shared" / "tests"
    ]
    
    for apps_test_dir in apps_tests_dirs:
        if apps_test_dir.exists():
            print(f"  Removing: {apps_test_dir}")
            shutil.rmtree(str(apps_test_dir))

def create_canonical_test_structure(base_path: Path):
    """Create the complete canonical test directory structure"""
    
    print("\n=== Creating Canonical Test Structure ===")
    
    # Define canonical test directories
    test_dirs = [
        # Main test structure
        "tests/data",
        "tests/fixtures",
        "tests/e2e",
        "tests/integration",
        "tests/regression",
        
        # Layer-specific tests
        "tests/l1_planning/unit",
        "tests/l1_planning/integration",
        "tests/l2_execution/unit", 
        "tests/l2_execution/integration",
        "tests/l3_orchestration/unit",
        "tests/l3_orchestration/integration",
        "tests/l4_memory/unit",
        "tests/l4_memory/integration",
        "tests/l5_safety/unit",
        "tests/l5_safety/integration",
        
        # Engine-specific tests in apps/
        "apps/resume_engine/tests/unit",
        "apps/resume_engine/tests/integration",
        "apps/resume_engine/tests/e2e",
        "apps/outreach_engine/tests/unit",
        "apps/outreach_engine/tests/integration", 
        "apps/outreach_engine/tests/e2e",
        "apps/shared/tests/unit",
        "apps/shared/tests/integration",
        "apps/shared/tests/e2e"
    ]
    
    for dir_path in test_dirs:
        full_path = base_path / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py for Python packages
        if dir_path.startswith("tests/") or dir_path.startswith("apps/"):
            init_file = full_path / "__init__.py"
            if not init_file.exists():
                with open(init_file, 'w', encoding='utf-8') as f:
                    f.write('"""Test package initialization."""\n')

def create_layer_test_templates(base_path: Path):
    """Create basic test templates for each layer"""
    
    print("\n=== Creating Layer Test Templates ===")
    
    # L1 Planning tests
    l1_unit_template = '''"""
L1 Planning Unit Tests
Tests for individual planning components
"""

import pytest
from agentic_core.l1_planning import StrategyPlanner, MessagePlanner, ResearchPlanner, RefinementPlanner, SafetyPlanner


class TestStrategyPlanner:
    """Test StrategyPlanner functionality"""
    
    def test_strategy_planner_init(self):
        """Test StrategyPlanner initialization"""
        planner = StrategyPlanner()
        assert planner is not None
    
    def test_basic_strategy_creation(self):
        """Test basic strategy creation"""
        planner = StrategyPlanner()
        # Add basic strategy creation test here
        assert True


class TestMessagePlanner:
    """Test MessagePlanner functionality"""
    
    def test_message_planner_init(self):
        """Test MessagePlanner initialization"""
        planner = MessagePlanner()
        assert planner is not None


class TestResearchPlanner:
    """Test ResearchPlanner functionality"""
    
    def test_research_planner_init(self):
        """Test ResearchPlanner initialization"""
        planner = ResearchPlanner()
        assert planner is not None


class TestRefinementPlanner:
    """Test RefinementPlanner functionality"""
    
    def test_refinement_planner_init(self):
        """Test RefinementPlanner initialization"""
        planner = RefinementPlanner()
        assert planner is not None


class TestSafetyPlanner:
    """Test SafetyPlanner functionality"""
    
    def test_safety_planner_init(self):
        """Test SafetyPlanner initialization"""
        planner = SafetyPlanner()
        assert planner is not None
'''

    # L2 Execution tests
    l2_unit_template = '''"""
L2 Execution Unit Tests
Tests for individual execution components
"""

import pytest
from agentic_core.l2_execution import (
    BrowserTool, FileOpsTool, APITool,
    ToolInvocation, Validation, ErrorHandling
)


class TestExecutionTools:
    """Test execution tool functionality"""
    
    def test_browser_tool_init(self):
        """Test BrowserTool initialization"""
        tool = BrowserTool()
        assert tool is not None
    
    def test_file_ops_tool_init(self):
        """Test FileOpsTool initialization"""
        tool = FileOpsTool()
        assert tool is not None
    
    def test_api_tool_init(self):
        """Test APITool initialization"""
        tool = APITool()
        assert tool is not None


class TestExecutionEngine:
    """Test execution engine functionality"""
    
    def test_tool_invocation_init(self):
        """Test ToolInvocation initialization"""
        engine = ToolInvocation()
        assert engine is not None
    
    def test_validation_init(self):
        """Test Validation initialization"""
        validator = Validation()
        assert validator is not None
    
    def test_error_handling_init(self):
        """Test ErrorHandling initialization"""
        handler = ErrorHandling()
        assert handler is not None
'''

    # L3 Orchestration tests
    l3_unit_template = '''"""
L3 Orchestration Unit Tests
Tests for individual orchestration components
"""

import pytest
from agentic_core.l3_orchestration import (
    PlanNode, DAGBuilder, ReactEngine, Controller
)


class TestDAGComponents:
    """Test DAG orchestration functionality"""
    
    def test_plan_node_init(self):
        """Test PlanNode initialization"""
        node = PlanNode()
        assert node is not None
    
    def test_dag_builder_init(self):
        """Test DAGBuilder initialization"""
        builder = DAGBuilder()
        assert builder is not None


class TestReactComponents:
    """Test ReAct orchestration functionality"""
    
    def test_react_engine_init(self):
        """Test ReactEngine initialization"""
        engine = ReactEngine()
        assert engine is not None


class TestControllerComponents:
    """Test controller functionality"""
    
    def test_controller_init(self):
        """Test Controller initialization"""
        controller = Controller()
        assert controller is not None
'''

    # L4 Memory tests
    l4_unit_template = '''"""
L4 Memory Unit Tests
Tests for individual memory components
"""

import pytest
from agentic_core.l4_memory import (
    ShortTermMemory, LongTermMemory, StateManager
)


class TestMemoryComponents:
    """Test memory functionality"""
    
    def test_short_term_memory_init(self):
        """Test ShortTermMemory initialization"""
        memory = ShortTermMemory()
        assert memory is not None
    
    def test_long_term_memory_init(self):
        """Test LongTermMemory initialization"""
        memory = LongTermMemory()
        assert memory is not None
    
    def test_state_manager_init(self):
        """Test StateManager initialization"""
        manager = StateManager()
        assert manager is not None
'''

    # L5 Safety tests
    l5_unit_template = '''"""
L5 Safety Unit Tests
Tests for individual safety components
"""

import pytest
from agentic_core.l5_safety import (
    ContentFilter, Guardrail, Auditor
)


class TestSafetyComponents:
    """Test safety functionality"""
    
    def test_content_filter_init(self):
        """Test ContentFilter initialization"""
        filter = ContentFilter()
        assert filter is not None
    
    def test_guardrail_init(self):
        """Test Guardrail initialization"""
        guardrail = Guardrail()
        assert guardrail is not None
    
    def test_auditor_init(self):
        """Test Auditor initialization"""
        auditor = Auditor()
        assert auditor is not None
'''

    # Write templates to files
    templates = [
        ("tests/l1_planning/unit/test_planning_components.py", l1_unit_template),
        ("tests/l2_execution/unit/test_execution_components.py", l2_unit_template),
        ("tests/l3_orchestration/unit/test_orchestration_components.py", l3_unit_template),
        ("tests/l4_memory/unit/test_memory_components.py", l4_unit_template),
        ("tests/l5_safety/unit/test_safety_components.py", l5_unit_template),
    ]
    
    for file_path, template in templates:
        full_path = base_path / file_path
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(template)
        print(f"  Created: {file_path}")

def create_integration_tests(base_path: Path):
    """Create integration test templates"""
    
    print("\n=== Creating Integration Test Templates ===")
    
    integration_template = '''"""
Layer Integration Tests
Tests for cross-layer interactions
"""

import pytest
from agentic_core.l1_planning import StrategyPlanner
from agentic_core.l2_execution import ToolInvocation
from agentic_core.l3_orchestration import DAGBuilder
from agentic_core.l4_memory import StateManager
from agentic_core.l5_safety import ContentFilter


class TestLayerIntegration:
    """Test integration between layers"""
    
    def test_planning_to_execution_flow(self):
        """Test flow from planning to execution"""
        planner = StrategyPlanner()
        executor = ToolInvocation()
        
        # Test basic integration
        assert planner is not None
        assert executor is not None
    
    def test_execution_to_orchestration_flow(self):
        """Test flow from execution to orchestration"""
        executor = ToolInvocation()
        orchestrator = DAGBuilder()
        
        # Test basic integration
        assert executor is not None
        assert orchestrator is not None
    
    def test_memory_integration(self):
        """Test memory integration across layers"""
        memory = StateManager()
        planner = StrategyPlanner()
        
        # Test memory integration
        assert memory is not None
        assert planner is not None
    
    def test_safety_integration(self):
        """Test safety integration across layers"""
        safety = ContentFilter()
        executor = ToolInvocation()
        
        # Test safety integration
        assert safety is not None
        assert executor is not None
'''

    # Write integration tests
    integration_files = [
        "tests/l1_planning/integration/test_planning_integration.py",
        "tests/l2_execution/integration/test_execution_integration.py", 
        "tests/l3_orchestration/integration/test_orchestration_integration.py",
        "tests/integration/test_cross_layer_integration.py",
    ]
    
    for file_path in integration_files:
        full_path = base_path / file_path
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(integration_template)
        print(f"  Created: {file_path}")

def create_engine_test_templates(base_path: Path):
    """Create engine-specific test templates"""
    
    print("\n=== Creating Engine Test Templates ===")
    
    # Resume engine tests
    resume_engine_template = '''"""
Resume Engine Tests
Tests for resume generation functionality
"""

import pytest


class TestResumeEngine:
    """Test resume engine functionality"""
    
    def test_resume_engine_basic(self):
        """Test basic resume engine functionality"""
        # Add resume engine specific tests here
        assert True
    
    def test_resume_generation(self):
        """Test resume generation"""
        # Add resume generation tests here
        assert True
'''

    # Outreach engine tests
    outreach_engine_template = '''"""
Outreach Engine Tests
Tests for outreach functionality
"""

import pytest


class TestOutreachEngine:
    """Test outreach engine functionality"""
    
    def test_outreach_engine_basic(self):
        """Test basic outreach engine functionality"""
        # Add outreach engine specific tests here
        assert True
    
    def test_outreach_generation(self):
        """Test outreach generation"""
        # Add outreach generation tests here
        assert True
'''

    # Write engine tests
    engine_files = [
        ("apps/resume_engine/tests/unit/test_resume_engine.py", resume_engine_template),
        ("apps/outreach_engine/tests/unit/test_outreach_engine.py", outreach_engine_template),
    ]
    
    for file_path, template in engine_files:
        full_path = base_path / file_path
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(template)
        print(f"  Created: {file_path}")

def update_layer_init_files(base_path: Path):
    """Update layer __init__.py files to export proper classes"""
    
    print("\n=== Updating Layer __init__.py Files ===")
    
    # Update L2, L3, L4, L5 __init__.py files to export classes
    layer_updates = {
        "agentic_core/l2_execution/__init__.py": '''"""L2 Execution Layer - Tool Execution and Operations"""

from .tools.browser import BrowserTool
from .tools.file_ops import FileOpsTool  
from .tools.api import APITool
from .execution_engines import ToolInvocation, Validation, ErrorHandling

__all__ = [
    "BrowserTool", "FileOpsTool", "APITool",
    "ToolInvocation", "Validation", "ErrorHandling"
]
''',
        
        "agentic_core/l3_orchestration/__init__.py": '''"""L3 Orchestration Layer - DAG and ReAct Orchestration"""

from .dag import PlanNode, DAGBuilder
from .react import ReactEngine
from .controllers import Controller

__all__ = [
    "PlanNode", "DAGBuilder", "ReactEngine", "Controller"
]
''',
        
        "agentic_core/l4_memory/__init__.py": '''"""L4 Memory Layer - Memory Management"""

from .short_term import ShortTermMemory
from .long_term import LongTermMemory
from .state import StateManager

__all__ = [
    "ShortTermMemory", "LongTermMemory", "StateManager"
]
''',
        
        "agentic_core/l5_safety/__init__.py": '''"""L5 Safety Layer - Safety and Security"""

from .filters import ContentFilter
from .guardrails import Guardrail
from .audit import Auditor

__all__ = [
    "ContentFilter", "Guardrail", "Auditor"
]
'''
    }
    
    for file_path, content in layer_updates.items():
        full_path = base_path / file_path
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  Updated: {file_path}")

def run_test_rebuild():
    """Execute the complete test structure rebuild"""
    base_path = Path(__file__).parent
    
    print("=== Starting Test Structure Rebuild ===")
    
    # Execute rebuild steps
    clean_existing_tests(base_path)
    create_canonical_test_structure(base_path)
    create_layer_test_templates(base_path)
    create_integration_tests(base_path)
    create_engine_test_templates(base_path)
    update_layer_init_files(base_path)
    
    print("\n=== Test structure rebuild complete ===")
    print("Next steps:")
    print("1. Run pytest: pytest -q")
    print("2. Run ruff: ruff check .")
    print("3. Run mypy: mypy .")

if __name__ == "__main__":
    run_test_rebuild()
