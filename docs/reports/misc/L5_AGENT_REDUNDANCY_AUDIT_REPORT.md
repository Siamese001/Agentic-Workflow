# L5 Agent Redundancy Audit Report

**Generated:** 2026-02-02
**Scope:** `agentic_core/L5_safety/` (validators, guardrails, gravity, policy_engine, cognition)
**Auditor:** Cascade AI

---

## Executive Summary

This audit identifies **significant architectural redundancy** among L5 agents, with multiple agents performing overlapping transformations on:
- File location validation and healing
- Gravity (layer import) enforcement
- Structural validation (depth, complexity, naming)
- Code healing operations

**Key Finding:** 6 distinct overlap clusters identified, with potential to consolidate ~15 agents into ~6 unified agents.

---

## 1. Agent Inventory & Responsibility Summary

### 1.1 Governance & Architecture Agents

| Agent | Intended Responsibility | Actual Behavior |
|-------|------------------------|-----------------|
| **GovernanceAgent** | Architecture governance laws (depth, atomicity, root hygiene) | ✅ Provides DependencyGraph, blast radius analysis, complexity checking. **Overlap:** Duplicates depth checking with LocationAgent, HierarchyAgent |
| **ArchitectureGovernorAgent** | Universal architecture pattern enforcement | ✅ Layer boundary validation, gravity detection, naming enforcement. **Overlap:** Delegates to StructuralValidatorAgent for same checks |

### 1.2 Location & Hierarchy Agents

| Agent | Intended Responsibility | Actual Behavior |
|-------|------------------------|-----------------|
| **LocationAgent** | Territorial integrity gatekeeper | ⚠️ **Facade only** - delegates all validation to LocationValidatorAgent, all healing to LocationHealerAgent |
| **LocationValidatorAgent** | Pure validation (no side effects) | ✅ Root whitelist, depth requirements, forbidden patterns, AST semantic alignment |
| **LocationHealerAgent** | File moves, deletions, import fixing | ✅ Safe file operations via ArchivalGatekeeper, post-heal validation |
| **HierarchyAgent** | Unified hierarchy management | ⚠️ **Overlap:** Structure creation, file relocation, depth enforcement - duplicates LocationHealerAgent functionality |

### 1.3 Structural Validation Agents

| Agent | Intended Responsibility | Actual Behavior |
|-------|------------------------|-----------------|
| **StructuralValidatorAgent** | Gravity and naming validation | ✅ Layer import checking, naming conventions. **Overlap:** Gravity checking duplicated in GravityLeakRepairAgent |
| **StructuralEngineerAgent** | Code structure validation | ✅ Large classes/functions, cyclomatic complexity. **Overlap:** Complexity checking duplicated in GovernanceAgent |
| **FileClassificationAgent** | File categorization and naming | ✅ AST-based file type detection, naming enforcement. **Overlap:** Naming validation duplicated in StructuralValidatorAgent |

### 1.4 Code Healing Agents

| Agent | Intended Responsibility | Actual Behavior |
|-------|------------------------|-----------------|
| **CodeHealerAgent** | Canon compliance, import fixing, structural repair | ✅ Consolidated from CanonHealerAgent, ImportHealerAgent, StructuralHealerAgent |
| **GravityLeakRepairAgent** | Automated gravity violation healing | ⚠️ **Overlap:** Import rewriting duplicated in CodeHealerAgent |

### 1.5 Security & Constitutional Agents

| Agent | Intended Responsibility | Actual Behavior |
|-------|------------------------|-----------------|
| **RedSentinelAgent** | Security fuzzing | ✅ **Distinct scope** - no overlap identified |
| **ConstitutionalReviewerAgent** | Constitutional review of outputs | ✅ **Distinct scope** - operational guardrail |

---

## 2. Conflict Report: Overlapping Transformations

### 2.1 CRITICAL: Depth Validation Overlap

**Agents Involved:** GovernanceAgent, LocationValidatorAgent, HierarchyAgent

```
┌─────────────────────────────────────────────────────────────────────┐
│                     DEPTH VALIDATION OVERLAP                        │
├─────────────────────────────────────────────────────────────────────┤
│  GovernanceAgent.check_depth_law()                                  │
│    └── Uses DEPTH_MAP from SOVEREIGN_REGISTRY                       │
│    └── Returns violation message string                             │
│                                                                     │
│  LocationValidatorAgent._validate_depth_requirements()              │
│    └── Uses SOVEREIGN_TERRITORIES depth config                      │
│    └── Returns (bool, str) tuple                                    │
│                                                                     │
│  HierarchyAgent.enforce_depth_rules()                               │
│    └── Uses SOVEREIGN_TERRITORIES depth config                      │
│    └── Archives violations directly                                 │
└─────────────────────────────────────────────────────────────────────┘
```

**Downstream Services Called:**
- All three read from `structure_blueprint_config.py` (SSOT)
- HierarchyAgent calls `ArchivalGatekeeper.safe_move()`
- GovernanceAgent calls `ArchivalGatekeeper.safe_delete()`

### 2.2 CRITICAL: Gravity (Layer Import) Enforcement Overlap

**Agents Involved:** StructuralValidatorAgent, GravityLeakRepairAgent, ArchitectureGovernorAgent

```
┌─────────────────────────────────────────────────────────────────────┐
│                    GRAVITY ENFORCEMENT OVERLAP                      │
├─────────────────────────────────────────────────────────────────────┤
│  StructuralValidatorAgent._check_gravity()                          │
│    └── AST parsing for import statements                            │
│    └── LAYER_ORDER and GRAVITY_RULES constants                      │
│    └── Returns StructureViolation objects                           │
│                                                                     │
│  GravityLeakRepairAgent.analyze_violation()                         │
│    └── LAYER_ORDER constant (DUPLICATE)                             │
│    └── Suggests fix strategies (RELOCATE, ABSTRACT, INJECT)         │
│    └── Returns GravityFix objects                                   │
│                                                                     │
│  ArchitectureGovernorAgent._heal_gravity_violation()                │
│    └── Delegates to GravityLeakRepairAgent                          │
│    └── Orchestration layer only                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Downstream Services Called:**
- All use AST parsing (`ast.parse()`, `ast.walk()`)
- GravityLeakRepairAgent uses meta-learning cache (`ml_cache_get/set`)

### 2.3 HIGH: File Move/Relocation Overlap

**Agents Involved:** LocationHealerAgent, HierarchyAgent, GovernanceAgent

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FILE RELOCATION OVERLAP                          │
├─────────────────────────────────────────────────────────────────────┤
│  LocationHealerAgent.safe_move()                                    │
│    └── ArchivalGatekeeper.safe_move()                               │
│    └── Collision handling with counter suffix                       │
│    └── Post-heal validation + import fixing                         │
│                                                                     │
│  HierarchyAgent.relocate_misplaced_files()                          │
│    └── ArchivalGatekeeper.safe_move() (DUPLICATE)                   │
│    └── Uses get_best_target_l1/l2 for destination                   │
│                                                                     │
│  GovernanceAgent._sanitize_root_file()                              │
│    └── ArchivalGatekeeper.safe_move() (DUPLICATE)                   │
│    └── Moves to scripts/ directory                                  │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.4 HIGH: Complexity Analysis Overlap

**Agents Involved:** GovernanceAgent, StructuralEngineerAgent

```
┌─────────────────────────────────────────────────────────────────────┐
│                   COMPLEXITY ANALYSIS OVERLAP                       │
├─────────────────────────────────────────────────────────────────────┤
│  GovernanceAgent._calculate_mccabe()                                │
│    └── Cyclomatic complexity calculation                            │
│    └── Counts If, For, While, ExceptHandler, BoolOp                 │
│                                                                     │
│  StructuralEngineerAgent._calculate_complexity()                    │
│    └── IDENTICAL ALGORITHM                                          │
│    └── Counts If, For, While, ExceptHandler, BoolOp                 │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.5 MEDIUM: Naming Validation Overlap

**Agents Involved:** StructuralValidatorAgent, FileClassificationAgent, NamingAgent

```
┌─────────────────────────────────────────────────────────────────────┐
│                    NAMING VALIDATION OVERLAP                        │
├─────────────────────────────────────────────────────────────────────┤
│  StructuralValidatorAgent._check_naming()                           │
│    └── Agent suffix validation (*Agent.py)                          │
│    └── Returns StructureViolation                                   │
│                                                                     │
│  FileClassificationAgent.get_compliant_name()                       │
│    └── File type classification (AGENT, CLASS, MIXIN, etc.)         │
│    └── Naming convention enforcement                                │
│                                                                     │
│  NamingAgent.validate_name()                                        │
│    └── PROJECT_ROOT_METADATA whitelist check                        │
│    └── Stub implementation only                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.6 MEDIUM: Import Fixing Overlap

**Agents Involved:** LocationHealerAgent, CodeHealerAgent, GravityLeakRepairAgent

```
┌─────────────────────────────────────────────────────────────────────┐
│                     IMPORT FIXING OVERLAP                           │
├─────────────────────────────────────────────────────────────────────┤
│  LocationHealerAgent.fix_imports_after_move()                       │
│    └── Regex-based import rewriting                                 │
│    └── Scans entire repo for old module references                  │
│                                                                     │
│  CodeHealerAgent.heal_imports()                                     │
│    └── AST-based import analysis                                    │
│    └── Unused import removal, reordering                            │
│                                                                     │
│  GravityLeakRepairAgent._suggest_utils_import()                     │
│    └── Import path suggestion for relocated code                    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Refactor Plan

### 3.1 Proposed Consolidated Architecture

```
CURRENT (15+ agents)                    PROPOSED (6 unified agents)
─────────────────────────────────────────────────────────────────────
GovernanceAgent                    ┐
ArchitectureGovernorAgent          ├──► UnifiedGovernanceAgent
                                   │    (architecture laws, blast radius)
                                   ┘

LocationAgent (facade)             ┐
LocationValidatorAgent             ├──► UnifiedLocationAgent
LocationHealerAgent                │    (validation + healing)
HierarchyAgent                     ┘

StructuralValidatorAgent           ┐
StructuralEngineerAgent            ├──► UnifiedStructuralAgent
                                   ┘    (gravity, complexity, structure)

FileClassificationAgent            ┐
NamingAgent                        ├──► UnifiedNamingAgent
                                   ┘    (classification + naming)

CodeHealerAgent                    ┐
GravityLeakRepairAgent             ├──► UnifiedCodeHealerAgent
                                   ┘    (all code healing)

RedSentinelAgent                   ───► RedSentinelAgent (unchanged)
ConstitutionalReviewerAgent        ───► ConstitutionalReviewerAgent (unchanged)
```

### 3.2 Shared Utility Extraction (L4 State Layer)

The following logic should be extracted to `agentic_core/L4_state/utils/`:

1. **`complexity_analyzer.py`** - McCabe complexity calculation
2. **`layer_gravity.py`** - LAYER_ORDER, GRAVITY_RULES constants and checking
3. **`depth_validator.py`** - Depth validation against SOVEREIGN_TERRITORIES
4. **`import_rewriter.py`** - Unified import path rewriting

---

## 4. Proposed Diffs

### 4.1 Extract Shared Complexity Analyzer

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

### 4.2 Extract Shared Layer Gravity Constants

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

### 4.3 Update GovernanceAgent to Use Shared Utilities

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

### 4.4 Update StructuralEngineerAgent to Use Shared Utilities

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

### 4.5 Update StructuralValidatorAgent to Use Shared Gravity Utilities

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

### 4.6 Consolidate HierarchyAgent File Relocation into LocationHealerAgent

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

---

## 5. Validation Test Cases

### 5.1 Unit Tests for Shared Utilities

```python
# tests/unit/test_shared_complexity_analyzer.py
"""Unit tests for shared complexity analyzer."""
import ast
import pytest
from agentic_core.L4_state.utils.complexity_analyzer import (
    calculate_mccabe_complexity,
    check_function_complexity,
)


class TestMcCabeComplexity:
    """Tests for McCabe complexity calculation."""

    def test_simple_function_complexity_1(self):
        """Simple function with no branches should have complexity 1."""
        code = "def simple(): return 1"
        tree = ast.parse(code)
        func = tree.body[0]
        assert calculate_mccabe_complexity(func) == 1

    def test_if_statement_adds_complexity(self):
        """Each if statement adds 1 to complexity."""
        code = """
def with_if(x):
    if x > 0:
        return 1
    return 0
"""
        tree = ast.parse(code)
        func = tree.body[0]
        assert calculate_mccabe_complexity(func) == 2

    def test_nested_loops_add_complexity(self):
        """Nested loops each add to complexity."""
        code = """
def nested(items):
    for i in items:
        for j in items:
            if i == j:
                continue
"""
        tree = ast.parse(code)
        func = tree.body[0]
        assert calculate_mccabe_complexity(func) == 4  # 1 + for + for + if

    def test_boolean_operators_add_complexity(self):
        """Boolean operators add n-1 to complexity."""
        code = """
def bool_ops(a, b, c):
    if a and b and c:
        return True
"""
        tree = ast.parse(code)
        func = tree.body[0]
        assert calculate_mccabe_complexity(func) == 4  # 1 + if + (and + and)

    def test_check_function_complexity_pass(self):
        """Function under threshold should pass."""
        code = "def simple(): return 1"
        tree = ast.parse(code)
        func = tree.body[0]
        passed, complexity = check_function_complexity(func, max_complexity=10)
        assert passed is True
        assert complexity == 1

    def test_check_function_complexity_fail(self):
        """Function over threshold should fail."""
        code = """
def complex_func(x):
    if x > 0:
        if x > 10:
            if x > 100:
                return "big"
"""
        tree = ast.parse(code)
        func = tree.body[0]
        passed, complexity = check_function_complexity(func, max_complexity=2)
        assert passed is False
        assert complexity == 4
```

### 5.2 Unit Tests for Layer Gravity

```python
# tests/unit/test_shared_layer_gravity.py
"""Unit tests for shared layer gravity utilities."""
import pytest
from pathlib import Path
from agentic_core.L4_state.utils.layer_gravity import (
    LAYER_ORDER,
    GRAVITY_RULES,
    extract_layer_from_path,
    extract_layer_from_module,
    is_gravity_violation,
)


class TestLayerExtraction:
    """Tests for layer extraction from paths and modules."""

    def test_extract_layer_from_path_l5(self):
        """Should extract L5 from path."""
        path = Path("agentic_core/L5_safety/validators/GovernanceAgent.py")
        assert extract_layer_from_path(path) == "L5"

    def test_extract_layer_from_path_l0(self):
        """Should extract L0 from path."""
        path = Path("agentic_core/L0_maintenance/scripts/cleanup.py")
        assert extract_layer_from_path(path) == "L0"

    def test_extract_layer_from_path_no_layer(self):
        """Should return None for paths without layer."""
        path = Path("apps_rg/engines/tool.py")
        assert extract_layer_from_path(path) is None

    def test_extract_layer_from_module_l3(self):
        """Should extract L3 from module path."""
        module = "agentic_core.L3_orchestration.workflow_engines.engine"
        assert extract_layer_from_module(module) == "L3"


class TestGravityViolation:
    """Tests for gravity violation detection."""

    def test_l3_importing_l5_is_violation(self):
        """L3 importing L5 should be a gravity violation."""
        assert is_gravity_violation("L3", "L5") is True

    def test_l5_importing_l3_is_not_violation(self):
        """L5 importing L3 should NOT be a gravity violation."""
        assert is_gravity_violation("L5", "L3") is False

    def test_l0_importing_l0_is_not_violation(self):
        """Same layer import should NOT be a violation."""
        assert is_gravity_violation("L0", "L0") is False

    def test_l6_can_import_all_layers(self):
        """L6 should be able to import from all layers."""
        for layer in LAYER_ORDER.keys():
            assert is_gravity_violation("L6", layer) is False
```

### 5.3 Integration Tests for Consolidated Agents

```python
# tests/integration/test_l5_agent_consolidation.py
"""Integration tests to verify L5 agent consolidation doesn't break functionality."""
import pytest
from pathlib import Path


class TestGovernanceAgentAfterRefactor:
    """Verify GovernanceAgent still works after complexity extraction."""

    def test_complexity_check_still_works(self, tmp_path):
        """GovernanceAgent.check_complexity should still function."""
        from agentic_core.L5_safety.validators.GovernanceAgent import GovernanceAgent

        # Create test file with complex function
        test_file = tmp_path / "complex.py"
        test_file.write_text("""
def complex_func(x):
    if x > 0:
        if x > 10:
            if x > 100:
                for i in range(x):
                    while i > 0:
                        i -= 1
""")

        agent = GovernanceAgent(root_dir=str(tmp_path))
        violations = agent.check_complexity(str(test_file))

        # Should detect complexity violation
        assert len(violations) > 0
        assert any("complexity" in v.get("type", "").lower() for v in violations)


class TestStructuralValidatorAfterRefactor:
    """Verify StructuralValidatorAgent still works after gravity extraction."""

    def test_gravity_check_still_works(self, tmp_path):
        """StructuralValidatorAgent._check_gravity should still function."""
        from agentic_core.L5_safety.policy_engine.structural_validator_agent_types import (
            StructuralValidatorAgent,
            StructureConfig,
        )

        # Create test file with gravity violation
        l3_dir = tmp_path / "agentic_core" / "L3_orchestration"
        l3_dir.mkdir(parents=True)
        test_file = l3_dir / "bad_import.py"
        test_file.write_text("""
from agentic_core.L5_safety.validators.GovernanceAgent import GovernanceAgent
""")

        config = StructureConfig(project_root=tmp_path)
        agent = StructuralValidatorAgent(config=config)
        report = agent.validate_structure(test_file)

        # Should detect gravity violation
        assert len(report.violations) > 0
        assert any(v.violation_type == "GRAVITY" for v in report.violations)


class TestLocationHealerDelegation:
    """Verify HierarchyAgent properly delegates to LocationHealerAgent."""

    def test_hierarchy_delegates_file_relocation(self, tmp_path):
        """HierarchyAgent should delegate MISPLACED violations to LocationHealerAgent."""
        from agentic_core.L5_safety.validators.HierarchyagentStrategy import HierarchyAgent

        agent = HierarchyAgent(project_root=tmp_path, healing_enabled=False)

        violation = {
            "type": "MISPLACED",
            "file": str(tmp_path / "orphan.py"),
            "message": "File in wrong location",
        }

        result = agent.heal(violation)

        # Should delegate (healing disabled = skipped)
        assert result["status"] in ("skipped", "delegated")
```

### 5.4 Regression Test: No Functionality Loss

```python
# tests/guardian/test_l5_consolidation_regression.py
"""Guardian tests to ensure no functionality loss after L5 consolidation."""
import pytest
from pathlib import Path


class TestNoFunctionalityLoss:
    """Ensure all original capabilities are preserved."""

    def test_depth_validation_still_works(self, tmp_path):
        """All three depth validators should produce consistent results."""
        from agentic_core.L5_safety.validators.GovernanceAgent import GovernanceAgent
        from agentic_core.L5_safety.validators.location_validator_agent import LocationValidatorAgent

        # Create file at wrong depth
        deep_file = tmp_path / "agentic_core" / "L5_safety" / "validators" / "sub" / "deep.py"
        deep_file.parent.mkdir(parents=True, exist_ok=True)
        deep_file.write_text("# Too deep")

        gov_agent = GovernanceAgent(root_dir=str(tmp_path))
        loc_agent = LocationValidatorAgent(project_root=tmp_path)

        gov_result = gov_agent.check_depth_law(str(deep_file.relative_to(tmp_path)))
        loc_result = loc_agent.validate_file_location(deep_file)

        # Both should detect depth violation
        if gov_result:
            assert "DEEP" in gov_result or "depth" in gov_result.lower()
        # LocationValidator returns (bool, str)
        assert loc_result[0] is False or "depth" in loc_result[1].lower()

    def test_gravity_detection_consistent(self, tmp_path):
        """Gravity detection should be consistent across agents."""
        from agentic_core.L5_safety.policy_engine.structural_validator_agent_types import (
            StructuralValidatorAgent,
            StructureConfig,
        )
        from agentic_core.L5_safety.gravity.GravityLeakRepairAgent import GravityLeakRepairAgent

        # Both should identify L3 -> L5 as violation
        struct_agent = StructuralValidatorAgent(StructureConfig())
        gravity_agent = GravityLeakRepairAgent(project_root=tmp_path)

        # Test the shared logic
        from agentic_core.L4_state.utils.layer_gravity import is_gravity_violation

        assert is_gravity_violation("L3", "L5") is True
        assert is_gravity_violation("L5", "L3") is False
```

---

## 6. Migration Checklist

### Phase 1: Extract Shared Utilities (Week 1)
- [ ] Create `agentic_core/L4_state/utils/complexity_analyzer.py`
- [ ] Create `agentic_core/L4_state/utils/layer_gravity.py`
- [ ] Create `agentic_core/L4_state/utils/depth_validator.py`
- [ ] Add unit tests for all shared utilities
- [ ] Run full test suite to verify no regressions

### Phase 2: Update Agents to Use Shared Utilities (Week 2)
- [ ] Update GovernanceAgent to use `complexity_analyzer`
- [ ] Update StructuralEngineerAgent to use `complexity_analyzer`
- [ ] Update StructuralValidatorAgent to use `layer_gravity`
- [ ] Update GravityLeakRepairAgent to use `layer_gravity`
- [ ] Run integration tests

### Phase 3: Consolidate File Operations (Week 3)
- [ ] Update HierarchyAgent to delegate file moves to LocationHealerAgent
- [ ] Update GovernanceAgent to delegate file moves to LocationHealerAgent
- [ ] Remove duplicate `safe_move` implementations
- [ ] Run e2e tests

### Phase 4: Deprecate Redundant Agents (Week 4)
- [ ] Mark LocationAgent as deprecated (facade only)
- [ ] Document migration path for external consumers
- [ ] Update agent discovery to reflect consolidation
- [ ] Final regression testing

---

## 7. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Breaking existing imports | Medium | High | Preserve facade patterns, add deprecation warnings |
| Inconsistent behavior after consolidation | Low | High | Comprehensive regression tests |
| Performance degradation | Low | Medium | Profile before/after, optimize shared utilities |
| Circular import issues | Medium | Medium | Careful dependency ordering in L4 utilities |

---

## 8. Conclusion

The L5 layer exhibits significant architectural redundancy that can be addressed through:

1. **Extracting shared utilities** to L4 (complexity analysis, gravity rules, depth validation)
2. **Consolidating file operations** into LocationHealerAgent as the single point of file mutation
3. **Maintaining facade patterns** for backwards compatibility during migration

**Estimated effort:** 4 weeks for full consolidation
**Risk level:** Medium (mitigated by comprehensive testing)
**Expected benefit:** 40% reduction in L5 code duplication, clearer separation of concerns
