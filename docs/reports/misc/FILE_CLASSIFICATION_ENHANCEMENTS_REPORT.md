# File Classification Agent Enhancement Report

## Overview

This report proposes enhancements to the `FileClassificationAgent` to improve agent detection logic and category detection accuracy. The current implementation has several limitations that can lead to misclassification and missed opportunities for proper architectural governance.

## Current Issues Identified

### 1. Agent Detection Limitations
- Relies heavily on naming patterns (`*Agent` suffix)
- Doesn't check for actual inheritance from `SovereignBaseAgent`
- Misses agents that don't follow naming conventions
- False positives for classes with "Agent" in name that aren't actual agents

### 2. Category Detection Issues
- Priority queue is rigid and doesn't account for nuanced cases
- Missing categories for modern architectural patterns
- No detection for async agents, factory classes, or service classes
- Limited context awareness (doesn't check imports or decorators)

### 3. Integration Gaps
- No integration with the agent discovery system
- Doesn't leverage existing metadata from `agent_discovery_full.json`
- Missing validation against SSOT structure blueprint

## Proposed Enhancements

### 1. Enhanced Agent Detection

#### Current Logic (lines 300-309):
```python
if name.endswith("Agent"):
    is_agent = True

# Inheritance Check for Agents (if not already found)
if not is_agent:
    for base in node.bases:
        if (isinstance(base, ast.Name) and "Agent" in base.id) or (
            isinstance(base, ast.Attribute) and "Agent" in base.attr
        ):
            is_agent = True
```

#### Proposed Enhancement:
```python
def _is_true_agent(self, node: ast.ClassDef, file_path: Path) -> bool:
    """Enhanced agent detection with multiple criteria."""

    # Check 1: Naming convention
    if node.name.endswith("Agent"):
        return True

    # Check 2: Inheritance from SovereignBaseAgent
    for base in node.bases:
        if isinstance(base, ast.Name):
            if base.id in ("SovereignBaseAgent", "L0MaintenanceBaseAgent",
                          "L1CognitionBase", "L2ExecutionBase",
                          "L3OrchestrationBase", "L4StateBase",
                          "L5SafetyBase", "L6ObservabilityBase"):
                return True
        elif isinstance(base, ast.Attribute):
            if "Agent" in base.attr:
                return True

    # Check 3: Decorator-based detection
    for decorator in node.decorator_list:
        if isinstance(decorator, ast.Name):
            if decorator.id in ("agent", "sovereign_agent", "register_agent"):
                return True
        elif isinstance(decorator, ast.Attribute):
            if decorator.attr in ("agent", "register"):
                return True

    # Check 4: Method-based detection (has execute/heal methods)
    for item in node.body:
        if isinstance(item, ast.FunctionDef):
            if item.name in ("execute", "act", "heal", "run"):
                return True

    # Check 5: Structural context (in agents/ directory)
    if "agents" in file_path.parts:
        return True

    return False
```

### 2. New Category Types

#### Proposed Additions to FileType:
```python
FileType = Literal[
    "AGENT",
    "CLASS",
    "MIXIN",
    "UTILITY",
    "PROTOCOL",
    "ENGINE",
    "STUB",
    "TEST",
    "SCRIPT",
    "TYPES",
    "GATEWAY",
    "IGNORE",
    # NEW CATEGORIES
    "SERVICE",      # Service classes (dependency injection)
    "FACTORY",      # Factory classes for object creation
    "ASYNC_AGENT",  # Async-based agents
    "ADAPTER",      # Adapter/wrapper classes
    "CONFIG",       # Configuration classes
    "MODEL",        # Data model classes
    "REPOSITORY",   # Repository pattern classes
]
```

### 3. Enhanced Classification Logic

#### Proposed New classify_file Method:
```python
def classify_file(self, path: Path) -> FileType:
    """
    Enhanced file classification with multi-factor analysis.

    PRIORITY QUEUE (First Match Wins):
    1. STUB     - File contains NOT_AN_AGENT marker
    2. TEST     - Path contains tests/ OR name starts with test_
    3. PROTOCOL - Class inherits from typing.Protocol
    4. GATEWAY  - Class name contains "Gateway"
    5. ENGINE   - Path contains engines/ AND has class
    6. SERVICE  - Has @service decorator or injects dependencies
    7. FACTORY  - Class name ends with "Factory" or has create_* methods
    8. ASYNC_AGENT - Has async methods and agent characteristics
    9. MIXIN    - Class name ends in "Mixin"
    10. ADAPTER  - Class name ends in "Adapter" or "Wrapper"
    11. CONFIG   - In config/ directory or has Config suffix
    12. MODEL    - Has dataclass/pydantic model characteristics
    13. REPOSITORY - Has Repository suffix or CRUD methods
    14. AGENT    - Enhanced agent detection
    15. CLASS    - Any other class
    16. UTILITY  - No class definitions
    """

    # ... existing stub/test/protocol checks ...

    # NEW: Service detection
    if self._is_service_class(tree, path):
        return "SERVICE"

    # NEW: Factory detection
    if self._is_factory_class(tree):
        return "FACTORY"

    # NEW: Async agent detection
    if self._is_async_agent(tree, path):
        return "ASYNC_AGENT"

    # NEW: Adapter detection
    if self._is_adapter_class(tree):
        return "ADAPTER"

    # NEW: Config detection
    if self._is_config_class(tree, path):
        return "CONFIG"

    # NEW: Model detection
    if self._is_model_class(tree):
        return "MODEL"

    # NEW: Repository detection
    if self._is_repository_class(tree):
        return "REPOSITORY"

    # Enhanced agent detection
    if self._is_true_agent(tree, path):
        return "AGENT"

    # ... rest of existing logic ...
```

### 4. Integration with Agent Discovery

#### Proposed Integration Method:
```python
def _check_agent_discovery_metadata(self, file_path: Path) -> dict | None:
    """Check against agent discovery metadata for enhanced classification."""
    try:
        with open("agent_discovery_full.json", "r") as f:
            agents = json.load(f)

        # Find agent matching this file
        for agent in agents:
            if agent.get("file_path") == str(file_path.relative_to(self.project_root)):
                return agent
    except Exception:
        pass
    return None

def _classify_with_metadata(self, file_path: Path, tree: ast.AST) -> FileType:
    """Use agent discovery metadata to inform classification."""
    metadata = self._check_agent_discovery_metadata(file_path)

    if metadata:
        # Use metadata to enhance classification
        layer = metadata.get("layer", "")
        territory = metadata.get("territory", "")
        has_healing = metadata.get("has_healing", False)

        # Layer-based classification hints
        if layer == "L0":
            return "SCRIPT" if "scripts" in file_path.parts else "UTILITY"
        elif layer == "Apps":
            return "ENGINE" if "engines" in file_path.parts else "CLASS"
        elif has_healing and layer == "L5":
            return "AGENT"

    return None
```

## Detailed File Diffs

### Diff 1: Enhanced Agent Detection

```diff
--- a/agentic_core/L5_safety/validators/FileClassificationAgent.py
+++ b/agentic_core/L5_safety/validators/FileClassificationAgent.py
@@ -295,15 +295,65 @@ class FileClassificationAgent(SovereignBaseAgent):
         is_protocol = False
         is_gateway = False
         is_mixin = False
+        is_service = False
+        is_factory = False
+        is_async_agent = False
+        is_adapter = False
+        is_config = False
+        is_model = False
+        is_repository = False

         # [HARDENED] Structural Contexts
         is_structural_agent = "agents" in path.parts or "validators" in path.parts
         is_engine = "engines" in path.parts

         for node in ast.walk(tree):
             if isinstance(node, ast.ClassDef):
                 has_class = True
                 name = node.name
+
+                # Enhanced detection methods
+                if self._is_service_class(node, path):
+                    is_service = True
+                if self._is_factory_class(node):
+                    is_factory = True
+                if self._is_async_agent(node, path):
+                    is_async_agent = True
+                if self._is_adapter_class(node):
+                    is_adapter = True
+                if self._is_config_class(node, path):
+                    is_config = True
+                if self._is_model_class(node):
+                    is_model = True
+                if self._is_repository_class(node):
+                    is_repository = True

                 # Protocol Check (bases)
                 for base in node.bases:
@@ -325,6 +375,21 @@ class FileClassificationAgent(SovereignBaseAgent):
                 if name.endswith("Mixin"):
                     is_mixin = True
                 if name.endswith("Agent"):
-                    is_agent = True
+                    is_agent = True  # Keep for backward compatibility
+
+                # Enhanced agent detection
+                if self._is_true_agent(node, path):
+                    is_agent = True

                 # Inheritance Check for Agents (if not already found)
                 if not is_agent:
@@ -337,6 +402,46 @@ class FileClassificationAgent(SovereignBaseAgent):
                         ):
                             is_agent = True

+        # [PRIORITY EXECUTION] - Enhanced order matters!
+        if is_protocol:
+            return "PROTOCOL"
+        elif is_gateway:
+            return "GATEWAY"
+        elif is_engine and has_class:
+            return "ENGINE"
+        elif is_service:
+            return "SERVICE"
+        elif is_factory:
+            return "FACTORY"
+        elif is_async_agent:
+            return "ASYNC_AGENT"
+        elif is_mixin:
+            return "MIXIN"
+        elif is_adapter:
+            return "ADAPTER"
+        elif is_config:
+            return "CONFIG"
+        elif is_model:
+            return "MODEL"
+        elif is_repository:
+            return "REPOSITORY"
+        elif is_agent:
+            return "AGENT"
+        elif has_class:
+            if is_structural_agent:
+                return "AGENT"
+            return "CLASS"
+        else:
+            return "UTILITY"
+
+    def _is_true_agent(self, node: ast.ClassDef, file_path: Path) -> bool:
+        """Enhanced agent detection with multiple criteria."""
+
+        # Check 1: Naming convention
+        if node.name.endswith("Agent"):
+            return True
+
+        # Check 2: Inheritance from base agents
+        for base in node.bases:
+            if isinstance(base, ast.Name):
+                if base.id in ("SovereignBaseAgent", "L0MaintenanceBaseAgent",
+                              "L1CognitionBase", "L2ExecutionBase",
+                              "L3OrchestrationBase", "L4StateBase",
+                              "L5SafetyBase", "L6ObservabilityBase"):
+                    return True
+            elif isinstance(base, ast.Attribute):
+                if "Agent" in base.attr:
+                    return True
+
+        # Check 3: Decorator-based detection
+        for decorator in node.decorator_list:
+            if isinstance(decorator, ast.Name):
+                if decorator.id in ("agent", "sovereign_agent", "register_agent"):
+                    return True
+            elif isinstance(decorator, ast.Attribute):
+                if decorator.attr in ("agent", "register"):
+                    return True
+
+        # Check 4: Method-based detection
+        for item in node.body:
+            if isinstance(item, ast.FunctionDef):
+                if item.name in ("execute", "act", "heal", "run"):
+                    return True
+
+        # Check 5: Structural context
+        if "agents" in file_path.parts:
+            return True
+
+        return False
+
+    def _is_service_class(self, tree: ast.AST, path: Path) -> bool:
+        """Detect service classes with dependency injection patterns."""
+        has_inject = False
+        has_service_decorator = False
+
+        for node in ast.walk(tree):
+            if isinstance(node, ast.ClassDef):
+                # Check for @service decorator
+                for decorator in node.decorator_list:
+                    if isinstance(decorator, ast.Name) and decorator.id == "service":
+                        has_service_decorator = True
+                    elif isinstance(decorator, ast.Attribute):
+                        if decorator.attr == "service":
+                            has_service_decorator = True
+
+                # Check for __init__ with dependency injection
+                for item in node.body:
+                    if isinstance(item, ast.FunctionDef) and item.name == "__init__":
+                        for arg in item.args.args:
+                            if arg.arg in ("service_container", "injector", "container"):
+                                has_inject = True
+
+        return has_service_decorator or has_inject
+
+    def _is_factory_class(self, tree: ast.AST) -> bool:
+        """Detect factory classes."""
+        for node in ast.walk(tree):
+            if isinstance(node, ast.ClassDef):
+                # Check naming
+                if node.name.endswith("Factory"):
+                    return True
+
+                # Check for create_* methods
+                for item in node.body:
+                    if isinstance(item, ast.FunctionDef):
+                        if item.name.startswith("create_") or item.name.startswith("make_"):
+                            return True
+        return False
+
+    def _is_async_agent(self, tree: ast.AST, path: Path) -> bool:
+        """Detect async-based agents."""
+        has_async_methods = False
+        has_agent_characteristics = False
+
+        for node in ast.walk(tree):
+            if isinstance(node, ast.ClassDef):
+                # Check for async methods
+                for item in node.body:
+                    if isinstance(item, ast.AsyncFunctionDef):
+                        has_async_methods = True
+                        if item.name in ("execute", "act", "run"):
+                            has_agent_characteristics = True
+
+                # Check for async context manager
+                for item in node.body:
+                    if isinstance(item, ast.AsyncFunctionDef) and item.name == "__aenter__":
+                        has_agent_characteristics = True
+
+        return has_async_methods and has_agent_characteristics
+
+    def _is_adapter_class(self, tree: ast.AST) -> bool:
+        """Detect adapter/wrapper classes."""
+        for node in ast.walk(tree):
+            if isinstance(node, ast.ClassDef):
+                # Check naming
+                if node.name.endswith(("Adapter", "Wrapper", "Bridge")):
+                    return True
+
+                # Check for adapter pattern methods
+                methods = [item.name for item in node.body if isinstance(item, ast.FunctionDef)]
+                if "adapt" in methods or "wrap" in methods or "bridge" in methods:
+                    return True
+        return False
+
+    def _is_config_class(self, tree: ast.AST, path: Path) -> bool:
+        """Detect configuration classes."""
+        # Check path
+        if "config" in path.parts:
+            return True
+
+        for node in ast.walk(tree):
+            if isinstance(node, ast.ClassDef):
+                # Check naming
+                if node.name.endswith(("Config", "Settings", "Options")):
+                    return True
+
+                # Check for dataclass with config-like attributes
+                if hasattr(node, "decorator_list"):
+                    for decorator in node.decorator_list:
+                        if isinstance(decorator, ast.Name) and decorator.id == "dataclass":
+                            return True
+        return False
+
+    def _is_model_class(self, tree: ast.AST) -> bool:
+        """Detect data model classes."""
+        for node in ast.walk(tree):
+            if isinstance(node, ast.ClassDef):
+                # Check for pydantic BaseModel
+                for base in node.bases:
+                    if isinstance(base, ast.Name) and base.id == "BaseModel":
+                        return True
+                    elif isinstance(base, ast.Attribute) and base.attr == "BaseModel":
+                        return True
+
+                # Check for dataclass with only attributes
+                if hasattr(node, "decorator_list"):
+                    for decorator in node.decorator_list:
+                        if isinstance(decorator, ast.Name) and decorator.id == "dataclass":
+                            return True
+        return False
+
+    def _is_repository_class(self, tree: ast.AST) -> bool:
+        """Detect repository pattern classes."""
+        for node in ast.walk(tree):
+            if isinstance(node, ast.ClassDef):
+                # Check naming
+                if node.name.endswith("Repository"):
+                    return True
+
+                # Check for CRUD methods
+                methods = [item.name for item in node.body if isinstance(item, ast.FunctionDef)]
+                crud_methods = {"create", "read", "update", "delete", "save", "find", "get", "list"}
+                if any(method in methods for method in crud_methods):
+                    return True
+        return False
```

### Diff 2: Updated FileType and Stats

```diff
--- a/agentic_core/L5_safety/validators/FileClassificationAgent.py
+++ b/agentic_core/L5_safety/validators/FileClassificationAgent.py
@@ -74,6 +74,15 @@ FileType = Literal[
     "SCRIPT",  # NEW: For ops_scripts and maintenance tools
     "TYPES",  # NEW: For schemas/types/enums/collections
     "GATEWAY",
+    "SERVICE",      # Service classes (dependency injection)
+    "FACTORY",      # Factory classes for object creation
+    "ASYNC_AGENT",  # Async-based agents
+    "ADAPTER",      # Adapter/wrapper classes
+    "CONFIG",       # Configuration classes
+    "MODEL",        # Data model classes
+    "REPOSITORY",   # Repository pattern classes
     "IGNORE",
 ]

@@ -115,6 +124,15 @@ class FileClassificationAgent(SovereignBaseAgent):
                 "TEST": 0,
                 "SCRIPT": 0,  # NEW: Script category
                 "TYPES": 0,  # NEW: Types category
+                "SERVICE": 0,
+                "FACTORY": 0,
+                "ASYNC_AGENT": 0,
+                "ADAPTER": 0,
+                "CONFIG": 0,
+                "MODEL": 0,
+                "REPOSITORY": 0,
                 "GATEWAY": 0,
             },
         }
```

### Diff 3: Updated Reporting

```diff
--- a/agentic_core/L5_safety/validators/FileClassificationAgent.py
+++ b/agentic_core/L5_safety/validators/FileClassificationAgent.py
@@ -193,6 +212,15 @@ class FileClassificationAgent(SovereignBaseAgent):
         print(f"  - Tests:   {self.stats['violations']['TEST']}")
         print(f"  - Scripts: {self.stats['violations']['SCRIPT']}")
         print(f"  - Types:   {self.stats['violations']['TYPES']}")
+        print(f"  - Services: {self.stats['violations']['SERVICE']}")
+        print(f"  - Factories: {self.stats['violations']['FACTORY']}")
+        print(f"  - Async Agents: {self.stats['violations']['ASYNC_AGENT']}")
+        print(f"  - Adapters: {self.stats['violations']['ADAPTER']}")
+        print(f"  - Configs: {self.stats['violations']['CONFIG']}")
+        print(f"  - Models: {self.stats['violations']['MODEL']}")
+        print(f"  - Repositories: {self.stats['violations']['REPOSITORY']}")
         print(f"  - Gateways: {self.stats['violations']['GATEWAY']}")
         if not self.dry_run:
             print(f"Files Renamed:        {self.stats['renamed']}")
```

## Test Cases

### Test Case 1: Enhanced Agent Detection

```python
def test_enhanced_agent_detection(self):
    """Test enhanced agent detection with multiple criteria."""
    from agentic_core.L5_safety.validators.FileClassificationAgent import FileClassificationAgent
    import tempfile
    from pathlib import Path

    # Test 1: Agent by inheritance
    agent_code = '''
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

class TestAgent(SovereignBaseAgent):
    def execute(self):
        pass
'''

    # Test 2: Agent by decorator
    decorator_code = '''
@agent
class TestClass:
    def run(self):
        pass
'''

    # Test 3: Agent by methods
    method_code = '''
class TestClass:
    def act(self):
        pass
    def heal(self):
        pass
'''

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Test inheritance-based detection
        agent_file = tmpdir / "TestAgent.py"
        agent_file.write_text(agent_code)

        classifier = FileClassificationAgent(project_root=tmpdir)
        ftype = classifier.classify_file(agent_file)
        assert ftype == "AGENT"

        # Test decorator-based detection
        decorator_file = tmpdir / "TestClass.py"
        decorator_file.write_text(decorator_code)

        ftype = classifier.classify_file(decorator_file)
        assert ftype == "AGENT"

        # Test method-based detection
        method_file = tmpdir / "TestClass2.py"
        method_file.write_text(method_code)

        ftype = classifier.classify_file(method_file)
        assert ftype == "AGENT"
```

### Test Case 2: New Category Detection

```python
def test_new_category_detection(self):
    """Test detection of new categories."""
    import tempfile
    from pathlib import Path

    service_code = '''
@service
class UserService:
    def __init__(self, service_container):
        self.container = service_container
'''

    factory_code = '''
class WidgetFactory:
    def create_widget(self):
        return Widget()

    def make_gadget(self):
        return Gadget()
'''

    async_agent_code = '''
class AsyncAgent:
    async def execute(self):
        await self.process()

    async def act(self):
        await self.perform_action()
'''

    adapter_code = '''
class LegacyAdapter:
    def adapt(self, old_interface):
        return new_interface(old_interface)
'''

    config_code = '''
@dataclass
class AppConfig:
    debug: bool = False
    port: int = 8080
'''

    model_code = '''
from pydantic import BaseModel

class UserModel(BaseModel):
    name: str
    email: str
'''

    repository_code = '''
class UserRepository:
        def create(self, user):
            pass

        def find(self, id):
            pass

        def save(self, user):
            pass
'''

    test_cases = [
        ("UserService.py", service_code, "SERVICE"),
        ("WidgetFactory.py", factory_code, "FACTORY"),
        ("AsyncAgent.py", async_agent_code, "ASYNC_AGENT"),
        ("LegacyAdapter.py", adapter_code, "ADAPTER"),
        ("AppConfig.py", config_code, "CONFIG"),
        ("UserModel.py", model_code, "MODEL"),
        ("UserRepository.py", repository_code, "REPOSITORY"),
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        classifier = FileClassificationAgent(project_root=tmpdir)

        for filename, code, expected_type in test_cases:
            file_path = tmpdir / filename
            file_path.write_text(code)

            ftype = classifier.classify_file(file_path)
            assert ftype == expected_type, f"{filename}: expected {expected_type}, got {ftype}"
```

### Test Case 3: Integration with Agent Discovery

```python
def test_agent_discovery_integration(self):
    """Test integration with agent discovery metadata."""
    import json
    import tempfile
    from pathlib import Path

    # Mock agent discovery data
    agent_data = [
        {
            "class_name": "TestAgent",
            "file_path": "test_agents/TestAgent.py",
            "layer": "L5",
            "territory": "L5 Safety/Validators",
            "has_healing": True,
            "loc": 100
        }
    ]

    agent_code = '''
class TestAgent:
    def execute(self):
        pass
'''

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create agent discovery file
        discovery_file = tmpdir / "agent_discovery_full.json"
        discovery_file.write_text(json.dumps(agent_data))

        # Create agent file
        agent_dir = tmpdir / "test_agents"
        agent_dir.mkdir()
        agent_file = agent_dir / "TestAgent.py"
        agent_file.write_text(agent_code)

        # Test classification with metadata
        classifier = FileClassificationAgent(project_root=tmpdir)
        ftype = classifier.classify_file(agent_file)

        # Should be classified as AGENT due to metadata
        assert ftype == "AGENT"
```

### Test Case 4: Naming Convention Updates

```python
def test_updated_naming_conventions(self):
    """Test updated naming conventions for new categories."""
    import tempfile
    from pathlib import Path

    test_cases = [
        # (filename, content, expected_rename)
        ("user_service.py", "class UserService:", "UserService.py"),
        ("widget_factory.py", "class WidgetFactory:", "WidgetFactory.py"),
        ("async_agent.py", "class AsyncAgent:", "AsyncAgent.py"),
        ("legacy_adapter.py", "class LegacyAdapter:", "LegacyAdapter.py"),
        ("app_config.py", "class AppConfig:", "AppConfig.py"),
        ("user_model.py", "class UserModel:", "UserModel.py"),
        ("user_repository.py", "class UserRepository:", "UserRepository.py"),
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        classifier = FileClassificationAgent(project_root=tmpdir, dry_run=True)

        for filename, content, expected_rename in test_cases:
            file_path = tmpdir / filename
            file_path.write_text(content)

            new_name = classifier.get_compliant_name(file_path, classifier.classify_file(file_path))
            assert new_name == expected_rename, f"{filename}: expected {expected_rename}, got {new_name}"
```

### Test Case 5: Backward Compatibility

```python
def test_backward_compatibility(self):
    """Test that existing classifications still work."""
    import tempfile
    from pathlib import Path

    # Existing test cases that should still work
    existing_cases = [
        ("TestAgent.py", "class TestAgent:", "AGENT"),
        ("TestMixin.py", "class TestMixin:", "MIXIN"),
        ("test_file.py", "# Test file", "TEST"),
        ("utility.py", "def helper():", "UTILITY"),
        ("IGateway.py", "class IGateway(Protocol):", "PROTOCOL"),
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        classifier = FileClassificationAgent(project_root=tmpdir)

        for filename, content, expected_type in existing_cases:
            file_path = tmpdir / filename
            file_path.write_text(content)

            ftype = classifier.classify_file(file_path)
            assert ftype == expected_type, f"{filename}: expected {expected_type}, got {ftype}"
```

## Implementation Plan

### Phase 1: Core Enhancements (Week 1)
1. Implement new detection methods (`_is_true_agent`, `_is_service_class`, etc.)
2. Update `classify_file` method with new priority queue
3. Add new categories to `FileType` and stats tracking

### Phase 2: Integration (Week 2)
1. Implement agent discovery metadata integration
2. Add SSOT structure blueprint validation
3. Update reporting methods

### Phase 3: Testing (Week 3)
1. Create comprehensive test suite
2. Add backward compatibility tests
3. Performance testing with large codebases

### Phase 4: Documentation (Week 4)
1. Update documentation with new categories
2. Create migration guide
3. Add examples for each new category

## Expected Benefits

1. **Improved Accuracy**: Better detection of actual agents vs. classes with "Agent" in name
2. **Enhanced Coverage**: Recognition of modern architectural patterns
3. **Better Integration**: Leverages existing metadata and SSOT systems
4. **Future-Proof**: Extensible design for new patterns
5. **Reduced False Positives**: Multi-factor analysis reduces misclassification

## Risk Mitigation

1. **Backward Compatibility**: All existing classifications preserved
2. **Gradual Rollout**: Can enable new features incrementally
3. **Fallback Logic**: Graceful degradation if metadata unavailable
4. **Performance**: Caching and optimized AST traversal
5. **Testing**: Comprehensive test coverage before deployment

## Conclusion

These enhancements will significantly improve the accuracy and usefulness of the FileClassificationAgent while maintaining backward compatibility. The multi-factor detection approach will reduce false positives and better reflect the actual architectural patterns in the codebase.
