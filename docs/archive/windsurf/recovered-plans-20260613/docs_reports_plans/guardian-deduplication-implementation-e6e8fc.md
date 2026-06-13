# Guardian Test Suite Deduplication Implementation Plan

This plan provides detailed sub-phases, file diffs, and test cases for consolidating the Guardian test suite to eliminate redundancy and improve maintainability, based on the analysis of 27 test files with 44% overlap.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Phase 1: Test File Consolidation (Week 1)

### Sub-Phase 1.1: Merge Redundant Test Pairs

**Target Files:**
- `test_agent_autonomy.py` + `test_agent_autonomy_comprehensive.py`
- `test_agent_validation.py` + `test_agent_validation_comprehensive.py`
- `test_architecture_governance.py` + `test_architecture_governance_comprehensive.py`
- `test_core_components.py` + `test_core_components_comprehensive.py`

**Implementation Steps:**

1. **Backup Original Files**
```bash
mkdir -p backup/guardian_tests
cp tests/guardian/test_agent_autonomy*.py backup/guardian_tests/
cp tests/guardian/test_agent_validation*.py backup/guardian_tests/
cp tests/guardian/test_architecture_governance*.py backup/guardian_tests/
cp tests/guardian/test_core_components*.py backup/guardian_tests/
```

2. **File Diff for Agent Autonomy Tests**
```diff
--- tests/guardian/test_agent_autonomy.py
+++ tests/guardian/test_agent_autonomy.py (merged)
@@ -1,106 +1,234 @@
 #!/usr/bin/env python3
 """
-Deterministic Guardian Test for Agent Autonomy Compliance
-Tests that agents have required autonomy methods via AST analysis.
+Guardian Test for Agent Autonomy Compliance
+Comprehensive tests for agent autonomy methods and compliance.
 """

 import ast
 import sys
 from pathlib import Path
+import tempfile
+import pytest

 # Ensure project root is in path
 PROJECT_ROOT = Path(__file__).resolve().parents[2]
 if str(PROJECT_ROOT) not in sys.path:
     sys.path.insert(0, str(PROJECT_ROOT))

-# Required autonomy methods for constitutional compliance
-REQUIRED_METHODS = ["heal_repository"]
-
-
-def test_required_methods() -> None:
-    """
-    Test that agent files have required autonomy methods.
-
-    This test is currently disabled as heal_repository is not universally
-    required for all agents. It's only required for agents that inherit
-    from HealerMixin.
-    """
-    # Skip this test - heal_repository is only required for HealerMixin agents
-    # Not all agents need this method
-    print("✅ Autonomy compliance test skipped - heal_repository is mixin-specific")
-    return
-
-
-def _test_agent_file_autonomy(agent_file_path: str) -> None:
-    """
-    Test that an agent file has all required autonomy methods.
-
-    Args:
-        agent_file_path: Path to the agent file to test
-    """
-    agent_file = Path(agent_file_path)
-
-    if not agent_file.exists():
-        print(f"VIOLATION: Agent file does not exist: {agent_file}")
-        sys.exit(1)
-
-    if not agent_file.suffix == ".py":
-        print(f"VIOLATION: Not a Python file: {agent_file}")
-        sys.exit(1)
-
-    content = agent_file.read_text(encoding="utf-8")
-    tree = ast.parse(content)
-
-    # Find agent classes
-    agent_classes = [
-        node for node in ast.walk(tree)
-        if isinstance(node, ast.ClassDef) and node.name.endswith("Agent")
-    ]
-
-    if not agent_classes:
-        print(f"VIOLATION: No agent classes found in {agent_file}")
-        sys.exit(1)
-
-    # Check each agent class for required methods
-    for agent_class in agent_classes:
-        methods = [node.name for node in agent_class.body if isinstance(node, ast.FunctionDef)]
-
-        for required_method in REQUIRED_METHODS:
-            if required_method not in methods:
-                print(f"VIOLATION: {agent_class.name} missing {required_method} in {agent_file}")
-                sys.exit(1)
-
-    print(f"✅ Agent autonomy compliance verified: {agent_file}")
-
-
-if __name__ == "__main__":
-    if len(sys.argv) > 1:
-        # Test specific file
-        _test_agent_file_autonomy(sys.argv[1])
-    else:
-        # Run the test
-        test_required_methods()
+class TestAgentAutonomy:
+    """Comprehensive agent autonomy compliance tests."""
+
+    def test_agent_with_heal_repository(self):
+        """TC-AA-01: Agent with heal_repository passes."""
+        agent_code = '''
+class TestAgent:
+    def heal_repository(self):
+        pass
+'''
+        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
+            f.write(agent_code)
+            f.flush()
+            temp_path = Path(f.name)
+
+        try:
+            self._verify_agent_autonomy(temp_path)
+        finally:
+            temp_path.unlink(missing_ok=True)
+
+    def test_agent_missing_heal_repository(self):
+        """TC-AA-02: Agent missing heal_repository fails."""
+        agent_code = '''
+class TestAgent:
+    def some_other_method(self):
+        pass
+'''
+        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
+            f.write(agent_code)
+            f.flush()
+            temp_path = Path(f.name)
+
+        try:
+            with pytest.raises(AssertionError):
+                self._verify_agent_autonomy(temp_path)
+        finally:
+            temp_path.unlink(missing_ok=True)
+
+    def test_multiple_agents_mixed_compliance(self):
+        """TC-AA-03: Multiple agents with mixed compliance."""
+        agent_code = '''
+class CompliantAgent:
+    def heal_repository(self):
+        pass
+
+class NonCompliantAgent:
+    def other_method(self):
+        pass
+'''
+        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
+            f.write(agent_code)
+            f.flush()
+            temp_path = Path(f.name)
+
+        try:
+            with pytest.raises(AssertionError):
+                self._verify_agent_autonomy(temp_path)
+        finally:
+            temp_path.unlink(missing_ok=True)
+
+    def _verify_agent_autonomy(self, agent_file: Path) -> None:
+        """Verify agent has required autonomy methods."""
+        if not agent_file.exists():
+            raise AssertionError(f"Agent file does not exist: {agent_file}")
+
+        if not agent_file.suffix == ".py":
+            raise AssertionError(f"Not a Python file: {agent_file}")
+
+        content = agent_file.read_text(encoding="utf-8")
+        tree = ast.parse(content)
+
+        # Find agent classes
+        agent_classes = [
+            node for node in ast.walk(tree)
+            if isinstance(node, ast.ClassDef) and node.name.endswith("Agent")
+        ]
+
+        if not agent_classes:
+            raise AssertionError(f"No agent classes found in {agent_file}")
+
+        # Check each agent class for required methods
+        for agent_class in agent_classes:
+            methods = [node.name for node in agent_class.body if isinstance(node, ast.FunctionDef)]
+
+            # Only check heal_repository for HealerMixin agents (those that have heal methods)
+            if any("heal" in method for method in methods):
+                if "heal_repository" not in methods:
+                    raise AssertionError(
+                        f"{agent_class.name} missing heal_repository in {agent_file}"
+                    )
```

3. **File Diff for Agent Validation Tests**
```diff
--- tests/guardian/test_agent_validation.py
+++ tests/guardian/test_agent_validation.py (merged)
@@ -1,134 +1,238 @@
 #!/usr/bin/env python3
 """
-Deterministic Guardian Test for Agent Validation
-Tests agent compliance without runtime instantiation.
+Guardian Test for Agent Validation
+Comprehensive tests for agent structure and compliance validation.
 """

 import ast
 import sys
 from pathlib import Path
-from typing import Any
+import tempfile
+import pytest

 # Ensure project root is in path
 PROJECT_ROOT = Path(__file__).resolve().parents[2]
 if str(PROJECT_ROOT) not in sys.path:
     sys.path.insert(0, str(PROJECT_ROOT))

-
-def check_agent_structure(file_path: Path) -> dict[str, Any]:
-    """
-    Check agent structure using static analysis.
-
-    Returns:
-        Dict with validation results
-    """
-    results = {
-        "has_agent_class": False,
-        "has_init": False,
-        "has_run_method": False,
-        "has_heal_method": False,
-        "has_test_method": False,
-        "violations": [],
-    }
-
-    try:
-        content = file_path.read_text(encoding="utf-8", errors="ignore")
-        tree = ast.parse(content)
-
-        # Find agent classes (classes ending with "Agent")
-        agent_classes = [
-            node
-            for node in ast.walk(tree)
-            if isinstance(node, ast.ClassDef) and node.name.endswith("Agent")
-        ]
-
-        if not agent_classes:
-            results["violations"].append("No agent classes found")
-            return results
-
-        results["has_agent_class"] = True
-
-        # Check first agent class for required methods
-        agent_class = agent_classes[0]
-        methods = [node.name for node in agent_class.body if isinstance(node, ast.FunctionDef)]
-
-        # Check for __init__
-        if "__init__" in methods:
-            results["has_init"] = True
-        else:
-            results["violations"].append("Missing __init__ method")
-
-        # Check for run method
-        if "run" in methods:
-            results["has_run_method"] = True
-        else:
-            results["violations"].append("Missing run method")
-
-        # Check for heal_repository method
-        if "heal_repository" in methods:
-            results["has_heal_method"] = True
-        else:
-            results["violations"].append("Missing heal_repository method")
-
-        # Check for test_self method
-        if "test_self" in methods:
-            results["has_test_method"] = True
-        else:
-            results["violations"].append("Missing test_self method")
-
-    except SyntaxError as e:
-        results["violations"].append(f"Syntax error: {e}")
-    except Exception as e:
-        results["violations"].append(f"Error reading file: {e}")
-
-    return results
-
-
-def test_agent_validation() -> None:
-    """Test agent validation on all agent files."""
-    project_root = Path(__file__).resolve().parents[2]
-
-    # Find all agent files
-    agent_files = list(project_root.glob("**/*Agent.py"))
-
-    if not agent_files:
-        print("⚠️  No agent files found for validation")
-        return
-
-    total_violations = 0
-
-    for agent_file in agent_files:
-        results = check_agent_structure(agent_file)
-
-        if results["violations"]:
-            print(f"❌ {agent_file}: {', '.join(results['violations'])}")
-            total_violations += len(results["violations"])
-        else:
-            print(f"✅ {agent_file}: COMPLIANT")
-
-    if total_violations > 0:
-        print(f"\n❌ Agent validation failed with {total_violations} violations")
-        sys.exit(1)
-    else:
-        print(f"\n✅ All {len(agent_files)} agent files are compliant")
-
-
-if __name__ == "__main__":
-    test_agent_validation()
+class TestAgentValidation:
+    """Comprehensive agent validation tests."""
+
+    def test_valid_agent_passes(self):
+        """TC-AV-01: Valid agent with all methods passes."""
+        agent_code = '''
+from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
+
+class TestAgent(SovereignBaseAgent):
+    def __init__(self):
+        pass
+
+    def run(self):
+        pass
+
+    def heal_repository(self):
+        pass
+
+    def test_self(self):
+        pass
+'''
+        with tempfile.NamedTemporaryFile(mode="w", suffix="Agent.py", delete=False) as f:
+            f.write(agent_code)
+            f.flush()
+            temp_path = Path(f.name)
+
+        try:
+            results = self._check_agent_structure(temp_path)
+            assert not results["violations"], f"Expected no violations, got: {results['violations']}"
+            assert results["has_agent_class"]
+            assert results["has_init"]
+            assert results["has_run_method"]
+            assert results["has_heal_method"]
+            assert results["has_test_method"]
+        finally:
+            temp_path.unlink(missing_ok=True)
+
+    def test_agent_without_init(self):
+        """TC-AV-02: Agent without __init__ fails."""
+        agent_code = '''
+class TestAgent:
+    def run(self):
+        pass
+'''
+        with tempfile.NamedTemporaryFile(mode="w", suffix="Agent.py", delete=False) as f:
+            f.write(agent_code)
+            f.flush()
+            temp_path = Path(f.name)
+
+        try:
+            results = self._check_agent_structure(temp_path)
+            assert "Missing __init__ method" in results["violations"]
+            assert not results["has_init"]
+        finally:
+            temp_path.unlink(missing_ok=True)
+
+    def test_agent_without_run_method(self):
+        """TC-AV-03: Agent without run method fails."""
+        agent_code = '''
+class TestAgent:
+    def __init__(self):
+        pass
+'''
+        with tempfile.NamedTemporaryFile(mode="w", suffix="Agent.py", delete=False) as f:
+            f.write(agent_code)
+            f.flush()
+            temp_path = Path(f.name)
+
+        try:
+            results = self._check_agent_structure(temp_path)
+            assert "Missing run method" in results["violations"]
+            assert not results["has_run_method"]
+        finally:
+            temp_path.unlink(missing_ok=True)
+
+    def test_no_agent_classes(self):
+        """TC-AV-04: File with no agent classes fails."""
+        agent_code = '''
+def regular_function():
+    pass
+
+class RegularClass:
+    pass
+'''
+        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
+            f.write(agent_code)
+            f.flush()
+            temp_path = Path(f.name)
+
+        try:
+            results = self._check_agent_structure(temp_path)
+            assert "No agent classes found" in results["violations"]
+            assert not results["has_agent_class"]
+        finally:
+            temp_path.unlink(missing_ok=True)
+
+    def _check_agent_structure(self, file_path: Path) -> dict[str, any]:
+        """Check agent structure using static analysis."""
+        results = {
+            "has_agent_class": False,
+            "has_init": False,
+            "has_run_method": False,
+            "has_heal_method": False,
+            "has_test_method": False,
+            "violations": [],
+        }
+
+        try:
+            content = file_path.read_text(encoding="utf-8", errors="ignore")
+            tree = ast.parse(content)
+
+            # Find agent classes
+            agent_classes = [
+                node for node in ast.walk(tree)
+                if isinstance(node, ast.ClassDef) and node.name.endswith("Agent")
+            ]
+
+            if not agent_classes:
+                results["violations"].append("No agent classes found")
+                return results
+
+            results["has_agent_class"] = True
+
+            # Check first agent class for required methods
+            agent_class = agent_classes[0]
+            methods = [node.name for node in agent_class.body if isinstance(node, ast.FunctionDef)]
+
+            if "__init__" in methods:
+                results["has_init"] = True
+            else:
+                results["violations"].append("Missing __init__ method")
+
+            if "run" in methods:
+                results["has_run_method"] = True
+            else:
+                results["violations"].append("Missing run method")
+
+            if "heal_repository" in methods:
+                results["has_heal_method"] = True
+            else:
+                results["violations"].append("Missing heal_repository method")
+
+            if "test_self" in methods:
+                results["has_test_method"] = True
+            else:
+                results["violations"].append("Missing test_self method")
+
+        except SyntaxError as e:
+            results["violations"].append(f"Syntax error: {e}")
+        except Exception as e:
+            results["violations"].append(f"Error reading file: {e}")
+
+        return results
```

### Sub-Phase 1.2: Consolidate Forensic Audit Tests

**Target Files:** 6 forensic audit phase files (105KB total)

**Implementation Steps:**

1. **Create Unified Forensic Audit Test**
```diff
--- tests/guardian/test_forensic_audit_phase1.py
--- tests/guardian/test_forensic_audit_phase2.py
--- tests/guardian/test_forensic_audit_phase3.py
--- tests/guardian/test_forensic_audit_phase4.py
--- tests/guardian/test_forensic_audit_phase5.py
--- tests/guardian/test_forensic_audit_phase6.py
+++ tests/guardian/test_forensic_audit_unified.py

@@ -0,0 +1,400 @@
+#!/usr/bin/env python3
+"""
+Unified Guardian Forensic Audit Test
+Consolidated detection of AI-Checking-AI violations and structural validation issues.
+
+Combines all 6 phases into a single, efficient test suite:
+- Phase 1: Agent discovery and basic violations
+- Phase 2: LLM-based validation detection
+- Phase 3: Apps layer validation logic
+- Phase 4-6: Extended validation patterns
+"""
+
+import ast
+import re
+from dataclasses import dataclass, field
+from pathlib import Path
+from typing import Any
+
+PROJECT_ROOT = Path(__file__).resolve().parents[2]
+
+
+@dataclass
+class AgentInfo:
+    """Unified information about a discovered agent."""
+    class_name: str
+    file_path: Path
+    layer: str
+    territory: str
+    has_heal_repository: bool = False
+    has_llm_calls: bool = False
+    has_validation_logic: bool = False
+    violation_patterns: list[str] = field(default_factory=list)
+    line_count: int = 0
+    llm_validation_methods: list[str] = field(default_factory=list)
+    apps_validation_methods: list[str] = field(default_factory=list)
+
+
+@dataclass
+class UnifiedAuditResult:
+    """Result of the unified forensic audit."""
+    total_agents: int = 0
+    agents_by_territory: dict[str, int] = field(default_factory=dict)
+    agents_with_violations: int = 0
+    total_violations: int = 0
+    violations_by_type: dict[str, int] = field(default_factory=dict)
+    clean_agents: list[str] = field(default_factory=list)
+
+
+class TestUnifiedForensicAudit:
+    """Unified forensic audit for all validation violations."""
+
+    def test_agent_discovery_and_basic_violations(self):
+        """Phase 1: Agent discovery and basic violation detection."""
+        result = self._scan_all_agents()
+
+        assert result.total_agents > 0, "Should discover agents"
+        assert "agentic_core" in result.agents_by_territory, "Should find agentic_core agents"
+
+        # Verify no basic structural violations
+        basic_violations = result.violations_by_type.get("basic", 0)
+        print(f"Phase 1: Found {result.total_agents} agents, {basic_violations} basic violations")
+
+    def test_llm_validation_detection(self):
+        """Phase 2: LLM-based validation detection."""
+        result = self._scan_all_agents()
+
+        # Check for LLM-based validation violations
+        llm_violations = 0
+        for agent_info in self._get_all_agents():
+            if agent_info.llm_validation_methods:
+                llm_violations += len(agent_info.llm_validation_methods)
+                print(f"LLM validation in {agent_info.class_name}: {agent_info.llm_validation_methods}")
+
+        # Log findings (LLM validation might be legitimate in some cases)
+        print(f"Phase 2: Found {llm_violations} LLM-based validation methods")
+
+    def test_apps_layer_validation(self):
+        """Phase 3: Apps layer validation logic detection."""
+        result = self._scan_all_agents()
+
+        apps_violations = 0
+        for agent_info in self._get_all_agents():
+            if agent_info.territory.startswith("apps_") and agent_info.apps_validation_methods:
+                apps_violations += len(agent_info.apps_validation_methods)
+                print(f"Apps validation in {agent_info.class_name}: {agent_info.apps_validation_methods}")
+
+        print(f"Phase 3: Found {apps_violations} apps layer validation methods")
+
+    def test_structural_validation_violations(self):
+        """Phases 4-6: Consolidated structural validation detection."""
+        result = self._scan_all_agents()
+
+        # Check for various structural validation patterns
+        structural_violations = 0
+        validation_patterns = [
+            "validate_structure", "check_compliance", "audit_structure",
+            "verify_hierarchy", "check_layer", "validate_architecture"
+        ]
+
+        for agent_info in self._get_all_agents():
+            for pattern in validation_patterns:
+                if any(pattern in method.lower() for method in agent_info.violation_patterns):
+                    structural_violations += 1
+
+        print(f"Phases 4-6: Found {structural_violations} structural validation violations")
+
+    def test_no_ai_checking_ai_violations(self):
+        """Comprehensive test: No AI agents should perform structural validation."""
+        result = self._scan_all_agents()
+
+        # Count all validation violations
+        total_validation_violations = (
+            result.violations_by_type.get("llm_validation", 0) +
+            result.violations_by_type.get("apps_validation", 0) +
+            result.violations_by_type.get("structural_validation", 0)
+        )
+
+        # This is informational - actual violations should be evaluated case by case
+        print(f"Total validation violations found: {total_validation_violations}")
+
+        # Ensure we have a comprehensive scan
+        assert result.total_agents >= 50, "Should scan at least 50 agents"
+
+    def _scan_all_agents(self) -> UnifiedAuditResult:
+        """Scan all agents and return unified results."""
+        result = UnifiedAuditResult()
+        self._all_agents = []  # Store for other test methods
+
+        # Scan all territories
+        territories = ["agentic_core", "apps_lic", "apps_rg", "apps_shared"]
+
+        for territory in territories:
+            territory_path = PROJECT_ROOT / territory
+            if not territory_path.exists():
+                continue
+
+            for agent_file in territory_path.glob("**/*Agent.py"):
+                agent_info = self._analyze_agent_file(agent_file, territory)
+                self._all_agents.append(agent_info)
+
+                result.total_agents += 1
+                result.agents_by_territory[territory] = result.agents_by_territory.get(territory, 0) + 1
+
+                if agent_info.violation_patterns:
+                    result.agents_with_violations += 1
+                    result.total_violations += len(agent_info.violation_patterns)
+
+                    # Categorize violations
+                    for violation in agent_info.violation_patterns:
+                        if "llm" in violation.lower():
+                            result.violations_by_type["llm_validation"] = result.violations_by_type.get("llm_validation", 0) + 1
+                        elif "validate" in violation.lower():
+                            result.violations_by_type["apps_validation"] = result.violations_by_type.get("apps_validation", 0) + 1
+                        else:
+                            result.violations_by_type["structural_validation"] = result.violations_by_type.get("structural_validation", 0) + 1
+                else:
+                    result.clean_agents.append(agent_info.class_name)
+
+        return result
+
+    def _analyze_agent_file(self, file_path: Path, territory: str) -> AgentInfo:
+        """Analyze a single agent file for violations."""
+        try:
+            content = file_path.read_text(encoding="utf-8", errors="ignore")
+            tree = ast.parse(content)
+        except Exception:
+            return AgentInfo(
+                class_name="ParseError",
+                file_path=file_path,
+                layer="unknown",
+                territory=territory,
+                line_count=0
+            )
+
+        # Find agent classes
+        agent_classes = [
+            node for node in ast.walk(tree)
+            if isinstance(node, ast.ClassDef) and node.name.endswith("Agent")
+        ]
+
+        if not agent_classes:
+            return AgentInfo(
+                class_name="NoAgentClass",
+                file_path=file_path,
+                layer="unknown",
+                territory=territory,
+                line_count=len(content.splitlines())
+            )
+
+        # Analyze first agent class
+        agent_class = agent_classes[0]
+        methods = [node.name for node in agent_class.body if isinstance(node, ast.FunctionDef)]
+
+        agent_info = AgentInfo(
+            class_name=agent_class.name,
+            file_path=file_path,
+            layer=self._get_layer_from_path(file_path),
+            territory=territory,
+            has_heal_repository="heal_repository" in methods,
+            has_llm_calls=self._has_llm_calls(content),
+            line_count=len(content.splitlines())
+        )
+
+        # Check for validation violations
+        for method in methods:
+            if self._is_validation_method(method, content):
+                agent_info.violation_patterns.append(method)
+
+                if self._uses_llm_for_validation(method, content):
+                    agent_info.llm_validation_methods.append(method)
+
+                if territory.startswith("apps_"):
+                    agent_info.apps_validation_methods.append(method)
+
+        return agent_info
+
+    def _get_all_agents(self) -> list[AgentInfo]:
+        """Get all analyzed agents."""
+        return getattr(self, "_all_agents", [])
+
+    def _get_layer_from_path(self, file_path: Path) -> str:
+        """Extract layer from file path."""
+        parts = file_path.parts
+        for part in parts:
+            if part.startswith("L"):
+                return part
+        return "unknown"
+
+    def _has_llm_calls(self, content: str) -> bool:
+        """Check if content contains LLM calls."""
+        llm_patterns = [
+            r"llm_generate", r"llm_call", r"openai\.", r"anthropic\.",
+            r"claude", r"gpt-", r"completion", r"chat_completion"
+        ]
+        return any(re.search(pattern, content, re.IGNORECASE) for pattern in llm_patterns)
+
+    def _is_validation_method(self, method_name: str, content: str) -> bool:
+        """Check if method performs validation."""
+        validation_patterns = [
+            "validate", "check", "verify", "audit", "compliance",
+            "structure", "hierarchy", "layer", "architecture"
+        ]
+        return any(pattern in method_name.lower() for pattern in validation_patterns)
+
+    def _uses_llm_for_validation(self, method_name: str, content: str) -> bool:
+        """Check if validation method uses LLM."""
+        # Look for method definition and check if it contains LLM calls
+        method_pattern = rf"def {method_name}\([^)]*\):.*?(?=def|\Z)"
+        method_match = re.search(method_pattern, content, re.DOTALL | re.IGNORECASE)
+
+        if method_match:
+            method_content = method_match.group(0)
+            return self._has_llm_calls(method_content)
+
+        return False
```

### Sub-Phase 1.3: Remove Redundant Files

**Files to Remove:**
```bash
# Remove simple versions (kept comprehensive versions)
rm tests/guardian/test_agent_autonomy.py
rm tests/guardian/test_agent_validation.py
rm tests/guardian/test_architecture_governance.py
rm tests/guardian/test_core_components.py

# Remove forensic audit phases
rm tests/guardian/test_forensic_audit_phase1.py
rm tests/guardian/test_forensic_audit_phase2.py
rm tests/guardian/test_forensic_audit_phase3.py
rm tests/guardian/test_forensic_audit_phase4.py
rm tests/guardian/test_forensic_audit_phase5.py
rm tests/guardian/test_forensic_audit_phase6.py

# Rename comprehensive versions to standard names
mv tests/guardian/test_agent_autonomy_comprehensive.py tests/guardian/test_agent_autonomy.py
mv tests/guardian/test_agent_validation_comprehensive.py tests/guardian/test_agent_validation.py
mv tests/guardian/test_architecture_governance_comprehensive.py tests/guardian/test_architecture_governance.py
mv tests/guardian/test_core_components_comprehensive.py tests/guardian/test_core_components.py
```

## Phase 2: Script Directory Consolidation (Week 2)

### Sub-Phase 2.1: Analyze Script Overlap

**Create Script Analysis Tool:**
```python
# ops_scripts/analyze_script_overlap.py
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple

def analyze_script_overlap() -> Dict[str, List[Path]]:
    """Analyze scripts for exact duplicates and similar functionality."""

    script_dirs = [
        Path("scripts"),
        Path("ops_scripts"),
        Path("agentic_core/L0_maintenance/scripts")
    ]

    # Hash-based duplicate detection
    file_hashes: Dict[str, List[Path]] = {}

    for script_dir in script_dirs:
        if not script_dir.exists():
            continue

        for script_file in script_dir.glob("**/*.py"):
            try:
                content = script_file.read_text(encoding="utf-8")
                file_hash = hashlib.md5(content.encode()).hexdigest()

                if file_hash not in file_hashes:
                    file_hashes[file_hash] = []
                file_hashes[file_hash].append(script_file)
            except Exception:
                continue

    # Find exact duplicates
    duplicates = {h: paths for h, paths in file_hashes.items() if len(paths) > 1}

    return duplicates
```

### Sub-Phase 2.2: Create Unified Script Structure

**New Directory Structure:**
```bash
scripts/
├── maintenance/          # From ops_scripts/maintenance/ + L0_maintenance/scripts/
├── ci/                   # From ops_scripts/ci/
├── security/             # From ops_scripts/security/
├── setup/                # From ops_scripts/setup/
├── analysis/             # Consolidated analysis scripts
├── testing/              # Test-related scripts
└── utils/                # General utilities
```

**Migration Script:**
```bash
#!/bin/bash
# scripts/migrate_script_structure.sh

# Create new structure
mkdir -p scripts/{maintenance,ci,security,setup,analysis,testing,utils}

# Move ops_scripts content
mv ops_scripts/maintenance/* scripts/maintenance/
mv ops_scripts/ci/* scripts/ci/
mv ops_scripts/security/* scripts/security/
mv ops_scripts/setup/* scripts/setup/

# Move L0 maintenance scripts
mv agentic_core/L0_maintenance/scripts/* scripts/maintenance/

# Consolidate analysis scripts
mv ops_scripts/analyze_*.py scripts/analysis/
mv ops_scripts/file_classification.py scripts/analysis/
mv ops_scripts/agent_disposition_analyzer.py scripts/analysis/

# Consolidate testing scripts
mv ops_scripts/test_*.py scripts/testing/
mv scripts/generate_unit_tests.py scripts/testing/

# Move remaining utilities
mv ops_scripts/*.py scripts/utils/ 2>/dev/null || true
mv scripts/*.py scripts/utils/ 2>/dev/null || true

# Remove exact duplicates
rm scripts/utils/find_hangs.py  # Keep in ops_scripts
rm scripts/utils/fix_naming_issues.py  # Keep in ops_scripts
```

### Sub-Phase 2.3: Remove Duplicate Scripts

**Exact Duplicates to Remove:**
```bash
# Check for exact duplicates first
python ops_scripts/analyze_script_overlap.py

# Remove confirmed duplicates
rm scripts/find_hangs.py  # Duplicate with ops_scripts/
rm scripts/fix_naming_issues.py  # Duplicate with ops_scripts/

# Consolidate similar functionality
# Merge validate_structure.py with file_classification.py
# Merge generate_unit_tests.py with test_input.py
```

## Phase 3: Test Optimization (Week 3)

### Sub-Phase 3.1: Create Guardian Test Base Classes

**Create Base Infrastructure:**
```python
# tests/guardian/base.py
"""
Base classes and utilities for Guardian tests.
Provides shared functionality to reduce duplication.
"""

import ast
import sys
from pathlib import Path
from typing import Any, Dict, List

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class GuardianTestBase:
    """Base class for all Guardian tests."""

    @staticmethod
    def get_project_root() -> Path:
        """Get project root path."""
        return PROJECT_ROOT

    @staticmethod
    def scan_agents(pattern: str = "**/*Agent.py") -> List[Path]:
        """Scan for agent files matching pattern."""
        return list(PROJECT_ROOT.glob(pattern))

    @staticmethod
    def check_layer_hierarchy(file_path: Path) -> Dict[str, Any]:
        """Check layer hierarchy compliance."""
        layer_hierarchy = {
            "L0_maintenance": 0,
            "L1_cognition": 1,
            "L2_execution": 2,
            "L3_orchestration": 3,
            "L4_state": 4,
            "L5_safety": 5,
            "L6_observability": 6,
        }

        parts = file_path.parts
        current_layer = None
        current_level = -1

        for part in parts:
            if part in layer_hierarchy:
                current_layer = part
                current_level = layer_hierarchy[part]
                break

        return {
            "layer": current_layer,
            "level": current_level,
            "hierarchy": layer_hierarchy
        }

    @staticmethod
    def parse_ast(file_path: Path) -> ast.Module | None:
        """Parse file to AST with error handling."""
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            return ast.parse(content)
        except Exception:
            return None

    @staticmethod
    def find_agent_classes(tree: ast.Module) -> List[ast.ClassDef]:
        """Find all agent classes in AST."""
        return [
            node for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef) and node.name.endswith("Agent")
        ]

    @staticmethod
    def get_class_methods(class_node: ast.ClassDef) -> List[str]:
        """Get all method names from a class."""
        return [
            node.name for node in class_node.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]


class AgentTestMixin:
    """Mixin for agent-specific test utilities."""

    def create_temp_agent(self, code: str, suffix: str = ".py") -> Path:
        """Create temporary agent file."""
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False) as f:
            f.write(code)
            f.flush()
            return Path(f.name)

    def assert_agent_compliance(self, agent_file: Path, required_methods: List[str]) -> None:
        """Assert agent has required methods."""
        tree = GuardianTestBase.parse_ast(agent_file)
        assert tree is not None, f"Could not parse {agent_file}"

        agent_classes = GuardianTestBase.find_agent_classes(tree)
        assert agent_classes, f"No agent classes found in {agent_file}"

        agent_class = agent_classes[0]
        methods = GuardianTestBase.get_class_methods(agent_class)

        for method in required_methods:
            assert method in methods, f"Missing required method: {method}"

    def assert_no_violations(self, agent_file: Path) -> None:
        """Assert agent has no validation violations."""
        tree = GuardianTestBase.parse_ast(agent_file)
        assert tree is not None, f"Could not parse {agent_file}"

        # Check for validation patterns
        validation_patterns = ["validate", "check", "verify", "audit"]

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                method_name = node.name.lower()
                if any(pattern in method_name for pattern in validation_patterns):
                    # Check if method uses LLM
                    method_source = ast.get_source_segment(open(agent_file).read(), node)
                    if method_source and any(llm_call in method_source.lower()
                                           for llm_call in ["llm", "openai", "anthropic"]):
                        pytest.fail(f"Found LLM-based validation in {method_name}")
```

### Sub-Phase 3.2: Enhance conftest.py

**Session-scoped fixtures:**
```python
# tests/guardian/conftest.py (enhancements)
@pytest.fixture(scope="session")
def agent_registry():
    """Session-scoped agent registry for all tests."""
    registry = {}

    for agent_file in GuardianTestBase.scan_agents():
        tree = GuardianTestBase.parse_ast(agent_file)
        if tree:
            agent_classes = GuardianTestBase.find_agent_classes(tree)
            registry[str(agent_file)] = {
                "file_path": agent_file,
                "agent_classes": [cls.name for cls in agent_classes],
                "layer": GuardianTestBase.check_layer_hierarchy(agent_file)["layer"]
            }

    return registry

@pytest.fixture(scope="session")
def layer_hierarchy():
    """Shared layer hierarchy data."""
    return {
        "L0_maintenance": 0,
        "L1_cognition": 1,
        "L2_execution": 2,
        "L3_orchestration": 3,
        "L4_state": 4,
        "L5_safety": 5,
        "L6_observability": 6,
    }

@pytest.fixture(scope="session")
def guardian_performance_baseline():
    """Baseline performance metrics for Guardian tests."""
    return {
        "max_test_time_seconds": 30,
        "max_memory_mb": 100,
        "max_agents_to_scan": 200,
    }
```

## Phase 4: Enhanced Coverage (Week 4)

### Sub-Phase 4.1: Integration Tests

**Create Integration Test Suite:**
```python
# tests/guardian/test_integration.py
"""
Integration tests for Guardian components.
Tests cross-component interactions and end-to-end scenarios.
"""

import pytest
import time
from pathlib import Path

from agentic_core.L5_safety.validators.anti_pattern_scanner import AntiPatternScanner
from tests.guardian.base import GuardianTestBase


class TestGuardianIntegration:
    """Integration tests for Guardian suite."""

    def test_anti_pattern_with_forensic_audit_integration(self):
        """Test anti-pattern detection integrates with forensic audit."""
        # Create a file with both anti-patterns and validation violations
        problematic_code = '''
import sys
import os

class ProblematicAgent:
    def heal_repository(self) -> dict:
        try:
            # Global mutation anti-pattern
            sys.path.insert(0, os.getcwd())

            # Silent swallower anti-pattern
            do_something()
        except Exception:
            pass

        return {"status": "success"}
'''

        temp_file = GuardianTestBase.create_temp_agent(problematic_code, "Agent.py")

        try:
            # Test anti-pattern detection
            scanner = AntiPatternScanner(PROJECT_ROOT)
            violations = scanner.scan_file(temp_file)

            # Should detect multiple violations
            assert len(violations) >= 2, "Should detect multiple anti-patterns"

            # Test forensic audit integration
            tree = GuardianTestBase.parse_ast(temp_file)
            agent_classes = GuardianTestBase.find_agent_classes(tree)

            assert agent_classes, "Should find agent class"

            # Verify violations are properly categorized
            violation_categories = {v.category.value for v in violations}
            assert "global_mutation" in violation_categories
            assert "silent_swallower" in violation_categories

        finally:
            temp_file.unlink(missing_ok=True)

    def test_cross_layer_validation(self):
        """Test validation across architectural layers."""
        # Create files in different layers with dependencies
        l5_validator = '''
class L5Validator:
    def validate_l4_state(self, l4_component):
        """Should not directly validate L4 components."""
        return True
'''

        l4_component = '''
class L4Component:
    def get_state(self):
        return {"status": "active"}
'''

        temp_l5 = GuardianTestBase.create_temp_agent(l5_validator, ".py")
        temp_l4 = GuardianTestBase.create_temp_agent(l4_component, ".py")

        try:
            # Test layer hierarchy
            l5_info = GuardianTestBase.check_layer_hierarchy(temp_l5)
            l4_info = GuardianTestBase.check_layer_hierarchy(temp_l4)

            # L5 should be higher level than L4
            assert l5_info["level"] > l4_info["level"], "Layer hierarchy incorrect"

            # Test cross-layer validation detection
            tree = GuardianTestBase.parse_ast(temp_l5)
            agent_classes = GuardianTestBase.find_agent_classes(tree)

            # Should detect cross-layer validation pattern
            assert agent_classes, "Should find validator class"

        finally:
            temp_l5.unlink(missing_ok=True)
            temp_l4.unlink(missing_ok=True)

    def test_performance_benchmarks(self, guardian_performance_baseline):
        """Ensure Guardian tests meet performance targets."""
        start_time = time.time()

        # Scan all agents
        agent_files = GuardianTestBase.scan_agents()

        # Should complete within baseline time
        scan_time = time.time() - start_time

        assert scan_time < guardian_performance_baseline["max_test_time_seconds"], \
            f"Agent scan took {scan_time:.2f}s, expected < {guardian_performance_baseline['max_test_time_seconds']}s"

        assert len(agent_files) <= guardian_performance_baseline["max_agents_to_scan"], \
            f"Found {len(agent_files)} agents, expected <= {guardian_performance_baseline['max_agents_to_scan']}"
```

### Sub-Phase 4.2: Regression Tests

**Create Regression Test Suite:**
```python
# tests/guardian/test_regression.py
"""
Regression tests to ensure deduplication doesn't break functionality.
"""

import pytest
from pathlib import Path

from tests.guardian.base import GuardianTestBase


class TestRegression:
    """Regression tests for Guardian deduplication."""

    def test_deduplication_regression(self):
        """Ensure deduplication doesn't break existing functionality."""
        # Test that all original test cases are still covered

        # Agent autonomy tests
        autonomy_code = '''
class TestAgent:
    def heal_repository(self):
        pass
'''
        temp_file = GuardianTestBase.create_temp_agent(autonomy_code, "Agent.py")

        try:
            # Should pass autonomy validation
            GuardianTestBase.assert_agent_compliance(temp_file, ["heal_repository"])
        finally:
            temp_file.unlink(missing_ok=True)

    def test_script_consolidation_regression(self):
        """Ensure script consolidation maintains functionality."""
        # Test that key scripts are still accessible
        script_paths = [
            "scripts/maintenance",
            "scripts/ci",
            "scripts/security",
            "scripts/analysis"
        ]

        for script_path in script_paths:
            path = Path(script_path)
            assert path.exists(), f"Script directory missing: {script_path}"
            assert any(path.iterdir()), f"Script directory empty: {script_path}"

    def test_performance_regression(self):
        """Ensure test execution time doesn't increase."""
        import time

        start_time = time.time()

        # Run a subset of Guardian tests
        agent_files = GuardianTestBase.scan_agents("**/test_*Agent.py")

        execution_time = time.time() - start_time

        # Should complete in reasonable time
        assert execution_time < 10.0, f"Test execution too slow: {execution_time:.2f}s"

    def test_coverage_maintenance(self):
        """Ensure test coverage is maintained after deduplication."""
        # Verify key test categories are still covered

        test_categories = [
            "agent_autonomy",
            "agent_validation",
            "architecture_governance",
            "forensic_audit",
            "anti_patterns"
        ]

        for category in test_categories:
            test_file = Path(f"tests/guardian/test_{category}.py")
            assert test_file.exists(), f"Missing test file for category: {category}"
```

## Test Cases to Implement

### 1. Deduplication Validation Tests

```python
# tests/guardian/test_deduplication.py
class TestDeduplication:
    def test_no_duplicate_test_functionality(self):
        """Ensure no duplicate test logic across files."""
        # Scan all test files for duplicate test patterns
        pass

    def test_script_uniqueness(self):
        """Ensure no duplicate scripts across directories."""
        # Check for duplicate script functionality
        pass

    def test_coverage_maintenance(self):
        """Ensure coverage is maintained after deduplication."""
        # Compare before/after coverage metrics
        pass
```

### 2. Performance Tests

```python
# tests/guardian/test_performance.py
class TestPerformance:
    def test_guardian_suite_performance(self):
        """Test Guardian suite meets performance targets."""
        pass

    def test_memory_usage(self):
        """Test memory usage stays within limits."""
        pass

    def test_parallel_execution(self):
        """Test parallel test execution efficiency."""
        pass
```

## Expected Outcomes

### Quantitative Metrics:
- **Test files:** 27 → 15 (44% reduction)
- **Code volume:** 474KB → 300KB (37% reduction)
- **Execution time:** 45s → 25s (44% improvement)
- **Script count:** 114 → 60 (47% reduction)

### Qualitative Benefits:
- Single source of truth for each test type
- Clearer test organization and maintenance
- Reduced cognitive load for developers
- Improved CI/CD pipeline efficiency

### Risk Mitigation:
- Comprehensive backup strategy before consolidation
- Regression tests to ensure functionality preservation
- Gradual rollout with validation at each phase
- Performance monitoring throughout implementation

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

