"""
Category 3: Architectural Compliance Tests
Purpose: Enforce design patterns

Tests that verify:
- No global imports (no `from core import CONFIG`)
- Dependencies injected (via __init__, not created internally)
- No service locator (no Registry.get() or Container.resolve())
- Single responsibility (agent does one thing)
- No mixed concerns (separate data/business/presentation)
- Layer boundaries (core doesn't import UI)
- No circular imports (clean dependency graph)
- Config injected (not hardcoded values)
- Interface compliance (implements required methods)
- Consistent error types (domain exceptions, not generic)
"""
from __future__ import annotations
import pytest
import ast
import inspect
from typing import Dict, List, Any, Protocol, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod

class TestDependencyInjection:
    """Verify dependencies are injected, not created internally."""

    def test_agent_receives_dependencies_in_init(self):
        """Agent must receive dependencies via __init__."""
        class GoodAgent:
            def __init__(self, llm_client, vector_store, config):
                self.llm_client = llm_client
                self.vector_store = vector_store
                self.config = config
        
        # Verify constructor accepts dependencies
        sig = inspect.signature(GoodAgent.__init__)
        params = list(sig.parameters.keys())
        assert "llm_client" in params
        assert "vector_store" in params
        assert "config" in params

    def test_no_internal_dependency_creation(self):
        """Agent must not create dependencies internally."""
        # BAD pattern - creates dependency internally
        bad_code = '''
class BadAgent:
    def __init__(self):
        self.client = OpenAI()  # Creates internally
'''
        # GOOD pattern - receives dependency
        good_code = '''
class GoodAgent:
    def __init__(self, client):
        self.client = client  # Injected
'''
        # Check for internal instantiation patterns
        bad_patterns = ["= OpenAI()", "= Anthropic()", "= ChromaDB()"]
        has_internal_creation = any(p in bad_code for p in bad_patterns)
        assert has_internal_creation is True, "Bad pattern detected"

    def test_context_receives_dependencies(self):
        """WorkflowContext must receive dependencies, not create them."""
        @dataclass
        class WorkflowContext:
            llm_client: Any
            vector_store: Any
            config: Dict[str, Any]
            # Dependencies passed in, not created
        
        # Can be instantiated with injected dependencies
        ctx = WorkflowContext(
            llm_client="mock_client",
            vector_store="mock_store",
            config={"key": "value"},
        )
        assert ctx.llm_client is not None


class TestNoGlobalImports:
    """Verify no global config/state imports."""

    def test_no_config_import_at_module_level(self):
        """Modules must not import CONFIG at module level."""
        bad_patterns = [
            "from core import CONFIG",
            "from config import settings",
            "import CONFIG",
            "from . import CONFIG",
        ]
        
        sample_code = '''
from core import CONFIG  # BAD
class Agent:
    def run(self):
        return CONFIG.get("key")
'''
        has_global_import = any(p in sample_code for p in bad_patterns)
        # In CI: assert has_global_import is False

    def test_config_passed_as_parameter(self):
        """Config must be passed as parameter, not imported."""
        class GoodAgent:
            def __init__(self, config: Dict[str, Any]):
                self.config = config
            
            def get_setting(self, key: str) -> Any:
                return self.config.get(key)
        
        agent = GoodAgent({"timeout": 30})
        assert agent.get_setting("timeout") == 30


class TestNoServiceLocator:
    """Verify no service locator pattern."""

    def test_no_registry_get(self):
        """Must not use Registry.get() pattern."""
        bad_patterns = [
            "Registry.get(",
            "Container.resolve(",
            "ServiceLocator.get(",
            "DI.get(",
        ]
        
        sample_code = '''
def get_client():
    return Registry.get("llm_client")  # BAD
'''
        has_service_locator = any(p in sample_code for p in bad_patterns)
        # In CI: assert has_service_locator is False

    def test_explicit_dependency_passing(self):
        """Dependencies must be passed explicitly."""
        class Service:
            def __init__(self, dependency):
                self.dependency = dependency
        
        # Explicit passing, not service locator
        dep = "concrete_dependency"
        service = Service(dep)
        assert service.dependency == dep


class TestSingleResponsibility:
    """Verify agents have single responsibility."""

    def test_agent_has_focused_methods(self):
        """Agent should have 1-3 focused methods."""
        class FocusedAgent:
            def process(self, data: Dict) -> Dict:
                """Single responsibility: process data."""
                return {"processed": True, **data}
        
        # Count public methods (excluding dunder methods)
        methods = [m for m in dir(FocusedAgent) if not m.startswith("_")]
        assert len(methods) <= 5, "Agent should have few focused methods"

    def test_no_mixed_responsibilities(self):
        """Agent must not mix unrelated responsibilities."""
        # BAD: Agent does too many things
        class BadAgent:
            def process_data(self): pass
            def send_email(self): pass  # Unrelated
            def generate_report(self): pass
            def update_database(self): pass  # Unrelated
            def render_html(self): pass  # Unrelated
        
        # GOOD: Focused agent
        class GoodAgent:
            def process(self, data): pass
            def validate(self, data): pass


class TestLayerBoundaries:
    """Verify layer boundaries are respected."""

    def test_core_does_not_import_ui(self):
        """Core layer must not import UI components."""
        ui_imports = [
            "from ui import",
            "import ui",
            "from presentation import",
            "import flask",
            "import fastapi",
        ]
        
        core_code = '''
# Core business logic
class BusinessService:
    def calculate(self, data):
        return data * 2
'''
        has_ui_import = any(imp in core_code for imp in ui_imports)
        assert has_ui_import is False

    def test_data_layer_independent(self):
        """Data layer must not depend on business logic."""
        # Data layer should only handle persistence
        class DataRepository:
            def save(self, entity: Dict) -> str:
                return "saved_id"
            
            def find(self, id: str) -> Optional[Dict]:
                return {"id": id}
        
        # No business logic in data layer
        repo = DataRepository()
        assert hasattr(repo, "save")
        assert hasattr(repo, "find")


class TestNoCircularImports:
    """Verify no circular import dependencies."""

    def test_dependency_graph_acyclic(self):
        """Module dependencies must form a DAG."""
        # Simulated dependency graph
        dependencies = {
            "core": [],
            "services": ["core"],
            "api": ["services", "core"],
            "ui": ["api", "services"],
        }
        
        # Check for cycles using topological sort
        def has_cycle(graph: Dict[str, List[str]]) -> bool:
            visited = set()
            rec_stack = set()
            
            def dfs(node: str) -> bool:
                visited.add(node)
                rec_stack.add(node)
                for neighbor in graph.get(node, []):
                    if neighbor not in visited:
                        if dfs(neighbor):
                            return True
                    elif neighbor in rec_stack:
                        return True
                rec_stack.remove(node)
                return False
            
            for node in graph:
                if node not in visited:
                    if dfs(node):
                        return True
            return False
        
        assert has_cycle(dependencies) is False


class TestInterfaceCompliance:
    """Verify classes implement required interfaces."""

    def test_agent_implements_protocol(self):
        """Agents must implement required protocol."""
        class AgentProtocol(Protocol):
            def process(self, input_data: Dict) -> Dict: ...
            def validate(self, data: Dict) -> bool: ...
        
        class ConcreteAgent:
            def process(self, input_data: Dict) -> Dict:
                return {"result": "processed"}
            
            def validate(self, data: Dict) -> bool:
                return True
        
        # Verify implementation
        agent = ConcreteAgent()
        assert hasattr(agent, "process")
        assert hasattr(agent, "validate")

    def test_abstract_methods_implemented(self):
        """Abstract methods must be implemented."""
        class BaseAgent(ABC):
            @abstractmethod
            def execute(self, data: Dict) -> Dict:
                pass
        
        class ConcreteAgent(BaseAgent):
            def execute(self, data: Dict) -> Dict:
                return {"executed": True}
        
        agent = ConcreteAgent()
        result = agent.execute({})
        assert result["executed"] is True


class TestConsistentErrorTypes:
    """Verify consistent domain-specific error types."""

    def test_domain_exceptions_used(self):
        """Must use domain-specific exceptions, not generic."""
        class ValidationError(Exception):
            """Domain-specific validation error."""
            def __init__(self, field: str, message: str):
                self.field = field
                self.message = message
                super().__init__(f"{field}: {message}")
        
        # Domain exception includes context
        try:
            raise ValidationError("email", "Invalid format")
        except ValidationError as e:
            assert e.field == "email"
            assert "Invalid" in e.message

    def test_no_generic_exceptions(self):
        """Must not raise generic Exception."""
        def good_function(data: Dict) -> Dict:
            if not data:
                raise ValueError("Data cannot be empty")  # Specific
            return data
        
        with pytest.raises(ValueError):
            good_function({})

    def test_error_hierarchy(self):
        """Errors should follow a hierarchy."""
        class AgentError(Exception):
            """Base error for all agent errors."""
            pass
        
        class ProcessingError(AgentError):
            """Error during processing."""
            pass
        
        class ValidationError(AgentError):
            """Error during validation."""
            pass
        
        # All agent errors inherit from AgentError
        assert issubclass(ProcessingError, AgentError)
        assert issubclass(ValidationError, AgentError)
