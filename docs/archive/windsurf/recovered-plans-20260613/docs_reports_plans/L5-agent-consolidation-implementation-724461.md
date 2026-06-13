# L5 Agent Consolidation Implementation Plan

This plan consolidates 15+ redundant L5 agents into 6 unified agents through a 4-phase approach that extracts shared utilities to L4, maintains backwards compatibility, and provides concrete file diffs for each implementation step.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Phase 1: Extract Shared Utilities (Week 1)

### Subphase 1.1: Create L4 Utils Infrastructure
**Goal:** Establish shared utility layer for common functionality

**Files to Create:**
- `agentic_core/L4_state/utils/complexity_analyzer.py`
- `agentic_core/L4_state/utils/layer_gravity.py`
- `agentic_core/L4_state/utils/depth_validator.py`
- `agentic_core/L4_state/utils/__init__.py`

**Implementation Diffs:**
```diff
--- /dev/null
+++ b/agentic_core/L4_state/utils/complexity_analyzer.py
@@ -0,0 +1,35 @@
+"""
+Shared complexity analysis utilities.
+
+SSOT for cyclomatic complexity calculation.
+Used by: GovernanceAgent, StructuralEngineerAgent
+"""
+import ast
+from typing import Any
+
+
+def calculate_mccabe_complexity(node: ast.AST) -> int:
+    """
+    Calculate cyclomatic complexity of an AST node.
+
+    Complexity = 1 + number of decision points (if, for, while, and, or, except)
+
+    Args:
+        node: AST node to analyze (typically FunctionDef)
+
+    Returns:
+        Cyclomatic complexity score
+    """
+    complexity = 1
+    for child in ast.walk(node):
+        if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
+            complexity += 1
+        elif isinstance(child, ast.BoolOp):
+            complexity += len(child.values) - 1
+    return complexity
+
+
+def check_function_complexity(node: ast.AST, max_complexity: int = 10) -> tuple[bool, int]:
+    """Check if function exceeds complexity threshold."""
+    complexity = calculate_mccabe_complexity(node)
+    return complexity <= max_complexity, complexity
```

```diff
--- /dev/null
+++ b/agentic_core/L4_state/utils/layer_gravity.py
@@ -0,0 +1,52 @@
+"""
+Shared layer gravity constants and validation.
+
+SSOT for layer hierarchy and gravity rules.
+Used by: StructuralValidatorAgent, GravityLeakRepairAgent, ArchitectureGovernorAgent
+"""
+from pathlib import Path
+
+# Layer hierarchy - lower index = higher authority (can be imported by higher layers)
+LAYER_ORDER = {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4, "L5": 5, "L6": 6}
+
+# Gravity rules: L(N) can only import from L(0..N)
+GRAVITY_RULES = {
+    "L0": {"L0"},
+    "L1": {"L0", "L1"},
+    "L2": {"L0", "L1", "L2"},
+    "L3": {"L0", "L1", "L2", "L3"},
+    "L4": {"L0", "L1", "L2", "L3", "L4"},
+    "L5": {"L0", "L1", "L2", "L3", "L4", "L5"},
+    "L6": {"L0", "L1", "L2", "L3", "L4", "L5", "L6"},
+}
+
+
+def extract_layer_from_path(path: Path) -> str | None:
+    """Extract layer identifier from file path."""
+    path_str = str(path)
+    for layer in LAYER_ORDER.keys():
+        if f"/{layer}_" in path_str or f"\\{layer}_" in path_str:
+            return layer
+    return None
+
+
+def extract_layer_from_module(module: str) -> str | None:
+    """Extract layer identifier from module path."""
+    for layer in LAYER_ORDER.keys():
+        if f".{layer}_" in module or module.startswith(f"{layer}_") or f"_{layer}_" in module:
+            return layer
+    return None
+
+
+def is_gravity_violation(source_layer: str, target_layer: str) -> bool:
+    """
+    Check if importing target_layer from source_layer violates gravity.
+
+    Args:
+        source_layer: Layer of the importing file (e.g., "L3")
+        target_layer: Layer being imported (e.g., "L5")
+
+    Returns:
+        True if this is a gravity violation (upward import)
+    """
+    allowed = GRAVITY_RULES.get(source_layer, set())
+    return target_layer not in allowed
```

### Subphase 1.2: Add Unit Tests for Shared Utilities
**Files to Create:**
- `tests/unit/test_shared_complexity_analyzer.py`
- `tests/unit/test_shared_layer_gravity.py`
- `tests/unit/test_shared_depth_validator.py`

**Implementation Diffs:**
```diff
--- /dev/null
+++ b/tests/unit/test_shared_complexity_analyzer.py
@@ -0,0 +1,67 @@
+"""Unit tests for shared complexity analyzer."""
+import ast
+import pytest
+from agentic_core.L4_state.utils.complexity_analyzer import (
+    calculate_mccabe_complexity,
+    check_function_complexity,
+)
+
+
+class TestMcCabeComplexity:
+    """Tests for McCabe complexity calculation."""
+
+    def test_simple_function_complexity_1(self):
+        """Simple function with no branches should have complexity 1."""
+        code = "def simple(): return 1"
+        tree = ast.parse(code)
+        func = tree.body[0]
+        assert calculate_mccabe_complexity(func) == 1
+
+    def test_if_statement_adds_complexity(self):
+        """Each if statement adds 1 to complexity."""
+        code = """
+def with_if(x):
+    if x > 0:
+        return 1
+    return 0
+"""
+        tree = ast.parse(code)
+        func = tree.body[0]
+        assert calculate_mccabe_complexity(func) == 2
+
+    def test_nested_loops_add_complexity(self):
+        """Nested loops each add to complexity."""
+        code = """
+def nested(items):
+    for i in items:
+        for j in items:
+            if i == j:
+                continue
+"""
+        tree = ast.parse(code)
+        func = tree.body[0]
+        assert calculate_mccabe_complexity(func) == 4  # 1 + for + for + if
+
+    def test_boolean_operators_add_complexity(self):
+        """Boolean operators add n-1 to complexity."""
+        code = """
+def bool_ops(a, b, c):
+    if a and b and c:
+        return True
+"""
+        tree = ast.parse(code)
+        func = tree.body[0]
+        assert calculate_mccabe_complexity(func) == 4  # 1 + if + (and + and)
+
+    def test_check_function_complexity_pass(self):
+        """Function under threshold should pass."""
+        code = "def simple(): return 1"
+        tree = ast.parse(code)
+        func = tree.body[0]
+        passed, complexity = check_function_complexity(func, max_complexity=10)
+        assert passed is True
+        assert complexity == 1
+
+    def test_check_function_complexity_fail(self):
+        """Function over threshold should fail."""
+        code = """
+def complex_func(x):
+    if x > 0:
+        if x > 10:
+            if x > 100:
+                return "big"
+"""
+        tree = ast.parse(code)
+        func = tree.body[0]
+        passed, complexity = check_function_complexity(func, max_complexity=2)
+        assert passed is False
+        assert complexity == 4
```

## Phase 2: Update Agents to Use Shared Utilities (Week 2)

### Subphase 2.1: Update Complexity Analysis Users
**Goal:** Replace duplicate complexity code with shared utility

**Files to Modify:**
- `agentic_core/L5_safety/validators/GovernanceAgent.py`
- `agentic_core/L5_safety/validators/structural_engineer_agent.py`

**Implementation Diffs:**
```diff
--- a/agentic_core/L5_safety/validators/GovernanceAgent.py
+++ b/agentic_core/L5_safety/validators/GovernanceAgent.py
@@ -50,6 +50,9 @@ import ast
 import logging
 from dataclasses import dataclass

+# [SSOT] Use shared complexity analyzer
+from agentic_core.L4_state.utils.complexity_analyzer import calculate_mccabe_complexity
+

 class GovernanceAgent(SubatomicTestingMixin, SovereignBaseAgent):
     """
@@ -644,19 +647,8 @@ class GovernanceAgent(SubatomicTestingMixin, SovereignBaseAgent):

     def _calculate_mccabe(self, node: ast.AST) -> int:
         """
-        Calculate cyclomatic complexity for an AST node.
-
-        Args:
-            node: AST node to analyze
-
-        Returns:
-            Cyclomatic complexity score
+        DEPRECATED: Use agentic_core.L4_state.utils.complexity_analyzer.calculate_mccabe_complexity
         """
-        complexity = 1
-        for child in ast.walk(node):
-            if isinstance(child, ast.If | ast.For | ast.While | ast.ExceptHandler):
-                complexity += 1
-            elif isinstance(child, ast.BoolOp):
-                complexity += len(child.values) - 1
-        return complexity
+        return calculate_mccabe_complexity(node)
```

```diff
--- a/agentic_core/L5_safety/validators/structural_engineer_agent.py
+++ b/agentic_core/L5_safety/validators/structural_engineer_agent.py
@@ -25,6 +25,9 @@ import ast
 import os
 from typing import Any

+# [SSOT] Use shared complexity analyzer
+from agentic_core.L4_state.utils.complexity_analyzer import calculate_mccabe_complexity
+

 @dataclass
 class StructuralEngineerAgent(SovereignBaseAgent, SubatomicTestingMixin, HealerMixin):
@@ -168,17 +171,8 @@ class StructuralEngineerAgent(SovereignBaseAgent, SubatomicTestingMixin, HealerM

     def _calculate_complexity(self, node: ast.AST) -> int:
         """
-        Calculate cyclomatic complexity of a function.
-
-        Complexity = 1 + number of decision points (if, for, while, and, or, except)
+        DEPRECATED: Use agentic_core.L4_state.utils.complexity_analyzer.calculate_mccabe_complexity
         """
-        complexity = 1
-        for child in ast.walk(node):
-            if isinstance(child, ast.If | ast.For | ast.While | ast.ExceptHandler):
-                complexity += 1
-            elif isinstance(child, ast.BoolOp):
-                complexity += len(child.values) - 1
-        return complexity
+        return calculate_mccabe_complexity(node)
```

### Subphase 2.2: Update Gravity Enforcement Users
**Goal:** Replace duplicate gravity constants and logic with shared utility

**Files to Modify:**
- `agentic_core/L5_safety/policy_engine/structural_validator_agent_types.py`
- `agentic_core/L5_safety/gravity/GravityLeakRepairAgent.py`

**Implementation Diffs:**
```diff
--- a/agentic_core/L5_safety/policy_engine/structural_validator_agent_types.py
+++ b/agentic_core/L5_safety/policy_engine/structural_validator_agent_types.py
@@ -27,6 +27,13 @@ from pathlib import Path
 from typing import Any

 from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
+# [SSOT] Use shared layer gravity utilities
+from agentic_core.L4_state.utils.layer_gravity import (
+    LAYER_ORDER,
+    GRAVITY_RULES,
+    extract_layer_from_path,
+    extract_layer_from_module,
+)


 class StructuralValidatorAgent(SovereignBaseAgent):
@@ -84,22 +91,6 @@ class StructuralValidatorAgent(SovereignBaseAgent):
     Hardened with Atomic Writes for auto-remediation.
     """

-    # Layer hierarchy (lower number = lower layer = higher authority)
-    LAYER_ORDER = {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4, "L5": 5, "L6": 6}
-
-    # Gravity rules: L(N) can only import from L(0..N)
-    GRAVITY_RULES = {
-        "L0": {"L0"},
-        "L1": {"L0", "L1"},
-        "L2": {"L0", "L1", "L2"},
-        "L3": {"L0", "L1", "L2", "L3"},
-        "L4": {"L0", "L1", "L2", "L3", "L4"},
-        "L5": {"L0", "L1", "L2", "L3", "L4", "L5"},
-        "L6": {"L0", "L1", "L2", "L3", "L4", "L5", "L6"},
-    }
+    # [SSOT] Constants moved to agentic_core.L4_state.utils.layer_gravity

     def _extract_layer(self, path: Path) -> str | None:
-        path_str = str(path)
-        for layer in self.LAYER_ORDER.keys():
-            if f"/{layer}_" in path_str or f"\\{layer}_" in path_str:
-                return layer
-        return None
+        return extract_layer_from_path(path)

     def _extract_layer_from_module(self, module: str) -> str | None:
-        for layer in self.LAYER_ORDER.keys():
-            if f".{layer}_" in module or module.startswith(f"{layer}_") or f"_{layer}_" in module:
-                return layer
-        return None
+        return extract_layer_from_module(module)
```

### Subphase 2.3: Update Depth Validation Users
**Goal:** Replace duplicate depth validation logic with shared utility

**Files to Modify:**
- `agentic_core/L5_safety/validators/GovernanceAgent.py`
- `agentic_core/L5_safety/validators/location_validator_agent.py`
- `agentic_core/L5_safety/validators/HierarchyagentStrategy.py`

## Phase 3: Consolidate File Operations (Week 3)

### Subphase 3.1: Make LocationHealerAgent the Single File Mutation Point
**Goal:** Consolidate all file move operations into LocationHealerAgent

**Files to Modify:**
- `agentic_core/L5_safety/validators/HierarchyagentStrategy.py`
- `agentic_core/L5_safety/validators/GovernanceAgent.py`

**Implementation Diffs:**
```diff
--- a/agentic_core/L5_safety/validators/HierarchyagentStrategy.py
+++ b/agentic_core/L5_safety/validators/HierarchyagentStrategy.py
@@ -158,6 +158,10 @@ class HierarchyAgent(SovereignBaseAgent):
             elif violation_type == "MISPLACED" or violation_type == "ORPHAN":
                 # File relocation violations
+                # [CONSOLIDATION] Delegate to LocationHealerAgent for file operations
+                from agentic_core.L5_safety.validators.LocationHealerAgent import LocationHealerAgent
+                healer = LocationHealerAgent(project_root=self.project_root)
+                return healer.heal(violation)
-                if self.healing_enabled:
-                    results = self.relocate_misplaced_files()
-                    return {
-                        "status": "success"
-                        if results["violations_found"] == 0
-                        else "partial_success",
-                        "details": f"Relocated {results['files_relocated']} files",
-                        "artifacts": [file_path],
-                        "errors": results["errors"],
-                    }
```

### Subphase 3.2: Add Integration Tests for Consolidated Operations
**Files to Create:**
- `tests/integration/test_l5_consolidated_file_operations.py`

## Phase 4: Deprecate Redundant Agents (Week 4)

### Subphase 4.1: Mark LocationAgent as Facade-Only
**Goal:** Clearly document LocationAgent as a facade for backwards compatibility

**Files to Modify:**
- `agentic_core/L5_safety/validators/location_agent.py`

**Implementation Diffs:**
```diff
--- a/agentic_core/L5_safety/validators/location_agent.py
+++ b/agentic_core/L5_safety/validators/location_agent.py
@@ -1,5 +1,8 @@
 """
-LocationAgent - L5 sovereign territorial gatekeeper
+LocationAgent - L5 sovereign territorial gatekeeper (DEPRECATED FACADE)
+
+⚠️  DEPRECATED: This agent is now a facade only.
+   Use LocationValidatorAgent for validation and LocationHealerAgent for healing.

 Enforces root folder whitelists, depth restrictions, gravity leak prevention,
 and root-level protections. Acts as a facade delegating validation and healing
@@ -15,6 +18,11 @@ from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent


 class LocationAgent(SovereignBaseAgent):
+    """
+    DEPRECATED FACADE: Delegates to LocationValidatorAgent and LocationHealerAgent.
+
+    Migration: Use LocationValidatorAgent for validation, LocationHealerAgent for healing.
+    """
     """
     L5 sovereign territorial gatekeeper for file location compliance.

```

### Subphase 4.2: Update Agent Discovery and Documentation
**Files to Modify:**
- `agentic_core/L0_maintenance/agent_discovery_full.json`
- `README.md`

### Subphase 4.3: Final Regression Testing
**Files to Create:**
- `tests/guardian/test_l5_consolidation_regression.py`

## Success Criteria

1. **All tests pass** - Unit, integration, and regression tests
2. **No functionality loss** - All original capabilities preserved
3. **Reduced code duplication** - 40% reduction in L5 duplicate code
4. **Clear separation of concerns** - Each agent has unique responsibility
5. **Backwards compatibility** - Existing imports continue to work

## Risk Mitigation

1. **Preserve facade patterns** - Maintain backwards compatibility
2. **Comprehensive testing** - Unit + integration + regression tests
3. **Phased rollout** - Each phase validated before proceeding
4. **Rollback plan** - Keep original code in comments for easy revert
5. **Documentation updates** - Clear migration paths for consumers

## Rollback Plan

If any phase introduces regressions:
1. Revert the specific phase's changes using git
2. Run full test suite to verify rollback
3. Analyze failure and adjust approach
4. Re-implement with modified strategy

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

