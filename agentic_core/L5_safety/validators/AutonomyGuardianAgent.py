from __future__ import annotations
"""
Autonomy Guardian Agent - Autonomy Meta-Enforcement
Ensures all domain agents have heal_repository() and no external scripts.
This is the sovereign guardian for agent autonomy across the repository.
"""
from datetime import date
from pathlib import Path
from typing import List, Dict, Any, Set, Optional
import ast
import json
import re

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.timeout_decorator import timeout, HealTimeoutError


class _CCVisitor(ast.NodeVisitor):
    """Cyclomatic Complexity visitor for AST analysis."""
    def __init__(self):
        self.cc = 1  # Base complexity
    
    def visit_If(self, node):
        self.cc += 1
        self.generic_visit(node)
    
    def visit_For(self, node):
        self.cc += 1
        self.generic_visit(node)
    
    def visit_While(self, node):
        self.cc += 1
        self.generic_visit(node)
    
    def visit_ExceptHandler(self, node):
        self.cc += 1
        self.generic_visit(node)
    
    def visit_With(self, node):
        self.cc += 1
        self.generic_visit(node)
    
    def visit_BoolOp(self, node):
        self.cc += len(node.values) - 1
        self.generic_visit(node)
    
    def visit_comprehension(self, node):
        self.cc += 1
        self.generic_visit(node)


class AutonomyGuardianAgent(HealerMixin, MCPHardenedMixin):
    """
    Sovereign guardian for agent autonomy enforcement (Canon Key 51).
    
    Responsibilities:
    1. Detect agents missing heal_repository() method
    2. Detect forbidden external runner scripts
    3. Report violations for manual or auto-healing
    
    This agent is itself autonomous — no external scripts needed.
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.required_methods = ["heal_repository"]
        self.forbidden_dirs = ["scripts/healing", "scripts/tools", "scripts/runners"]
        self.forbidden_patterns = ["heal", "runner", "launcher", "driver"]
        self.exclude_patterns = ["test_", "example_", "mock_", "stub_", "legacy", "deprecated"]
        
        # Load agents from authoritative JSON (agent_discovery_full.json)
        self._agent_registry_cache = None
        
        # Territory definitions for compliance report - map to JSON layers
        self.territories = {
            "L0_maintenance": ("L0", "Medium"),
            "L1_cognition": ("L1", "Medium"),
            "L2_execution": ("L2", "High"),
            "L3_orchestration": ("L3", "High"),
            "L4_state": ("L4", "Medium"),
            "L5_safety/validators": ("L5", "Critical"),  # Will filter by validators subfolder
            "L5_safety/guardrails": ("L5", "Critical"),  # Will filter by guardrails subfolder  
            "L5_safety/gravity": ("L5", "High"),        # Will filter by gravity subfolder
            "utils": ("utils", "Medium"),
            "observability": ("observability", "Low"),
            "knowledge": ("knowledge", "Low"),
            "apps_lic": ("apps_lic", "High"),
            "apps_rg": ("apps_rg", "High"),
            "apps_shared": ("apps_shared", "Medium"),
        }
    
    def _load_agent_registry(self) -> List[Dict[str, Any]]:
        """Load agents from agent_discovery_full.json (authoritative AST scan)."""
        if self._agent_registry_cache is not None:
            return self._agent_registry_cache
        
        json_path = self.project_root / "agent_discovery_full.json"
        if json_path.exists():
            try:
                self._agent_registry_cache = json.loads(json_path.read_text(encoding="utf-8"))
                return self._agent_registry_cache
            except Exception as e:
                print(f"Error loading agent registry: {e}")
                import traceback
                traceback.print_exc()
        
        # Fallback to empty list if JSON not found
        self._agent_registry_cache = []
        return self._agent_registry_cache
    
    def _get_all_agent_paths(self) -> List[Path]:
        """Get all agent file paths from the authoritative JSON registry."""
        registry = self._load_agent_registry()
        paths = []
        for agent in registry:
            path_str = agent.get("path", "").replace("\\", "/")
            if path_str:
                full_path = self.project_root / path_str
                if full_path.exists():
                    paths.append(full_path)
        return paths
    
    def _is_domain_agent(self, agent_file: Path) -> bool:
        """Check if file is a domain agent (not test/example)."""
        stem = agent_file.stem.lower()
        name = agent_file.name.lower()
        
        # Exclude test/example/mock/stub agents
        if any(pattern in stem or pattern in name for pattern in self.exclude_patterns):
            return False
        
        # Exclude specific test files
        if 'test' in name and name.startswith('test'):
            return False
            
        return True
    
    def validate_agent_autonomy(self, agent_file: Path) -> List[str]:
        """
        AST-based check for required autonomy methods.
        
        Args:
            agent_file: Path to agent file
            
        Returns:
            List of missing method names
        """
        violations = []
        try:
            content = agent_file.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(content)
            
            # Find all method names in file
            method_names = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    method_names.add(node.name)
            
            # Check for required methods
            for req_method in self.required_methods:
                if req_method not in method_names:
                    violations.append(req_method)
                    
        except SyntaxError:
            # File has syntax errors — skip
            pass
        except Exception:
            # Other errors — assume missing
            violations = list(self.required_methods)
            
        return violations
    
    def _detect_runner_script_violations(self) -> List[Path]:
        """Detect forbidden external runner scripts."""
        violations = []
        
        for dir_path in self.forbidden_dirs:
            dir_obj = self.project_root / dir_path
            if dir_obj.exists():
                for py_file in dir_obj.rglob("*.py"):
                    stem_lower = py_file.stem.lower()
                    if any(pattern in stem_lower for pattern in self.forbidden_patterns):
                        violations.append(py_file)
        
        return violations
    
    def run(self) -> List[tuple]:
        """
        Scan repository for autonomy violations using agent_discovery_full.json.
        
        Returns:
            List of (file_path, violation_reason) tuples
        """
        violations = []
        
        # Check for runner script violations
        script_violations = self._detect_runner_script_violations()
        for script in script_violations:
            violations.append((script, "FORBIDDEN_RUNNER_SCRIPT"))
        
        # Check all agent files from JSON registry for missing methods
        all_agents = self._get_all_agent_paths()
        for agent_file in all_agents:
            if not self._is_domain_agent(agent_file):
                continue
            
            missing_methods = self.validate_agent_autonomy(agent_file)
            for method in missing_methods:
                violations.append((agent_file, f"MISSING_METHOD:{method}"))
        
        return violations
    
    def auto_heal_proposal(self, file_path: Path, dry_run: bool = True) -> Dict[str, Any]:
        """
        Generate proposal for healing autonomy violation.
        
        Args:
            file_path: Path to file with violation
            dry_run: If True, only propose without executing
            
        Returns:
            Dict with status and details
        """
        result = {
            "file_path": str(file_path),
            "status": "skipped",
            "action": None,
            "error": None
        }
        
        # Handle runner script violations
        if "scripts" in str(file_path):
            result["action"] = "delete_forbidden_script"
            if dry_run:
                result["status"] = "proposed"
            else:
                try:
                    file_path.unlink()
                    result["status"] = "deleted"
                except Exception as e:
                    result["status"] = "error"
                    result["error"] = str(e)
            return result
        
        # Handle missing method violations
        result["action"] = "add_heal_repository"
        result["status"] = "requires_manual" if dry_run else "skipped"
        result["message"] = f"Add heal_repository() method to {file_path.name}"
        
        return result
    
    @timeout(300)
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: Optional[Set[str]] = None,
    ) -> Dict[str, int]:
        """
        Meta-healing: Enforce autonomy across all agents.
        
        Args:
            dry_run: If True, only propose changes
            execute: Must be explicitly True to perform changes
            depth: Current recursion depth
            max_depth: Maximum recursion depth
            _call_path: Set of agent names in current call path (cycle detection)
            
        Returns:
            Summary dict with counts
        """
        # Initialize call path on first call
        if _call_path is None:
            _call_path = set()
        
        agent_name = self.__class__.__name__
        
        # CYCLE DETECTION
        if agent_name in _call_path:
            print(f"  [!] HEALING CYCLE DETECTED: {agent_name} already in path → stopping")
            return {"scripts_found": 0, "agents_missing_method": 0, "healed": 0, "errors": 0, "cycle_detected": True}
        
        # DEPTH LIMIT
        if depth > max_depth:
            print(f"  [!] RECURSION DEPTH LIMIT REACHED ({depth}/{max_depth}) → stopping")
            return {"scripts_found": 0, "agents_missing_method": 0, "healed": 0, "errors": 0, "depth_limited": True}
        
        # Add self to path
        _call_path.add(agent_name)
        
        if execute and dry_run:
            raise ValueError("execute and dry_run cannot both be True")
        
        actual_execute = execute and not dry_run
        
        print(f"\n[AUTONOMY GUARDIAN @ depth {depth}] Enforcing Canon Key 51 across repository")
        
        violations = self.run()
        
        counts = {
            "scripts_found": 0,
            "agents_missing_method": 0,
            "healed": 0,
            "errors": 0
        }
        
        for file_path, reason in violations:
            if "FORBIDDEN_RUNNER_SCRIPT" in reason:
                counts["scripts_found"] += 1
                print(f"  [!] FORBIDDEN SCRIPT: {file_path.relative_to(self.project_root)}")
                
                if actual_execute:
                    try:
                        file_path.unlink()
                        counts["healed"] += 1
                        print(f"      [+] DELETED")
                    except Exception as e:
                        counts["errors"] += 1
                        print(f"      [!] DELETE FAILED: {e}")
                        
            elif "MISSING_METHOD" in reason:
                counts["agents_missing_method"] += 1
                method = reason.split(":")[1]
                print(f"  [!] MISSING {method}: {file_path.name}")
        
        print(f"\n[AUTONOMY GUARDIAN SUMMARY] "
              f"Scripts: {counts['scripts_found']} | "
              f"Missing heal_repository(): {counts['agents_missing_method']} | "
              f"Healed: {counts['healed']} | "
              f"Errors: {counts['errors']}")
        
        # Remove self from path
        _call_path.discard(agent_name)
        
        return counts


    def generate_compliance_report(self, markdown: bool = True) -> None:
        """
        Final high-signal autonomy compliance dashboard — exhaustive, on-demand.
        All territories + unclassified, full prioritization columns.
        """
        today = date.today().strftime("%B %d, %Y")
        print(f"### Autonomy Compliance Report — {today}\n")

        if markdown:
            header = (
                "| Territory / Layer                          | Total | Compliant | % Heal Cap | % Heal Inv | % MCP | % Test | Avg CC | % Typed | % Obs | Criticality | Health | Risk | % Used | Priority |\n"
                "|--------------------------------------------|-------|-----------|------------|-------------|-------|--------|--------|---------|-------|-------------|--------|------|--------|----------|\n"
            )
            print(header)

        # Accumulators for totals
        totals = {
            "agents": 0, "compliant": 0, "hardened": 0,
            "healing_cap": 0, "healing_invoke": 0, "tests": 0, "loc": 0, "used": 0,
            "cc_sum": 0, "typed": 0, "documented": 0, "observable": 0, "max_cc": 0
        }

        # Step 1: Load agents from authoritative JSON (agent_discovery_full.json)
        registry = self._load_agent_registry()
        all_agents = []
        path_to_layer = {}  # Map path -> layer for territory classification
        for agent in registry:
            path_str = agent.get("path", "")
            if path_str:
                # Convert JSON path to actual file path
                full_path = self.project_root / path_str
                if full_path.exists():
                    all_agents.append(full_path)
                    # Store both forward and backslash versions for matching
                    path_fwd = str(full_path).replace("\\", "/")
                    path_back = str(full_path)
                    path_to_layer[path_fwd] = agent.get("layer", "unknown")
                    path_to_layer[path_back] = agent.get("layer", "unknown")
        
        print(f"Loaded {len(all_agents)} agents from agent_discovery_full.json\n")

        # Step 2: Compute global usage (which agents are imported elsewhere)
        used_stems = set()
        for py_file in self.project_root.rglob("*.py"):
            if py_file in all_agents:
                continue
            try:
                content = py_file.read_text(errors="ignore")
                for agent in all_agents:
                    if agent.stem in content:
                        used_stems.add(agent.stem)
            except:
                pass

        # Step 3: Process defined territories using path_to_layer lookup
        classified_paths = set()

        for territory_key, (layer_filter, priority) in self.territories.items():
            # Get agents based on layer from lookup
            if territory_key.startswith("L5_safety"):
                # Special handling for L5 subfolders (validators, guardrails, gravity)
                subfolder = territory_key.split("/")[1]
                agents = [
                    p for p in all_agents
                    if path_to_layer.get(str(p)) == "L5" and subfolder in str(p).replace("\\", "/")
                ]
            else:
                # Standard layer matching
                agents = [
                    p for p in all_agents
                    if path_to_layer.get(str(p)) == layer_filter
                ]
            classified_paths.update(agents)

            terr_total = len(agents)
            if terr_total == 0:
                continue

            # Basic detections
            terr_compliant = terr_hardened = terr_healing_cap = terr_healing_invoke = terr_tests = 0
            terr_loc = terr_cc_sum = terr_max_cc = 0
            terr_typed = terr_documented = terr_observable = 0

            for a in agents:
                try:
                    content = a.read_text(errors="ignore")
                    lines = content.splitlines()
                    loc = len([l for l in lines if l.strip() and not l.strip().startswith("#")])
                    terr_loc += loc

                    # Basic checks
                    if "def heal_repository(self" in content:
                        terr_compliant += 1
                        terr_healing_invoke += 1
                    if "MCPHardenedMixin" in content:
                        terr_hardened += 1
                    # Healing capabilities: either inherits HealerMixin OR has healing logic
                    if "HealerMixin" in content or any(ind in content for ind in ["run(", "validate_", "auto_"]):
                        terr_healing_cap += 1
                    # Count tests: external test file OR self-tests OR delegation OR pytest/unittest
                    has_external_test = (a.parent / "tests" / f"test_{a.stem}.py").exists()
                    has_self_test = "_run_self_tests" in content or "SubatomicTestingMixin" in content or "SubatomicAgent" in content
                    has_delegation = "L0DelegationTestingMixin" in content or "L0DelegationMixin" in content or "TestSovereigntyAgent" in content or "_delegate_tests" in content or "delegate_on_failure" in content
                    has_inline_tests = "def test_" in content or "import pytest" in content or "import unittest" in content
                    if has_external_test or has_self_test or has_delegation or has_inline_tests:
                        terr_tests += 1
                    if a.stem in used_stems:
                        terr_used += 1

                    # AST-based metrics
                    tree = ast.parse(content)
                    functions = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                    classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]

                    # Cyclomatic Complexity
                    for func in functions:
                        visitor = _CCVisitor()
                        visitor.visit(func)
                        terr_cc_sum += visitor.cc
                        terr_max_cc = max(terr_max_cc, visitor.cc)

                    # Typing coverage
                    if functions:
                        typed = sum(1 for f in functions if f.returns or any(arg.annotation for arg in f.args.args if arg.arg != "self"))
                        terr_typed += (typed / len(functions)) * 100

                    # Documentation coverage
                    doc_count = 0
                    for cls in classes:
                        if cls.body and isinstance(cls.body[0], ast.Expr) and isinstance(getattr(cls.body[0].value, 's', None), str):
                            doc_count += 1
                        elif cls.body and isinstance(cls.body[0], ast.Expr) and isinstance(cls.body[0].value, ast.Constant):
                            doc_count += 1
                    for f in functions:
                        if f.body and isinstance(f.body[0], ast.Expr):
                            val = f.body[0].value
                            if isinstance(getattr(val, 's', None), str) or isinstance(val, ast.Constant):
                                doc_count += 1
                    total_targets = len(classes) + len(functions)
                    if total_targets:
                        terr_documented += (doc_count / total_targets) * 100

                    # Observability (logging)
                    if any(imp in content for imp in ["import logging", "from logging", "logger.", "log."]):
                        terr_observable += 100

                except SyntaxError:
                    terr_max_cc = max(terr_max_cc, 999)
                except Exception:
                    pass

            # Calculate averages
            avg_loc = round(terr_loc / terr_total, 1) if terr_total else 0
            avg_cc = round(terr_cc_sum / max(terr_total, 1), 1)
            perc_typed = round(terr_typed / terr_total, 1) if terr_total else 0
            perc_documented = round(terr_documented / terr_total, 1) if terr_total else 0
            perc_observable = round(terr_observable / terr_total, 1) if terr_total else 0
            terr_used = sum(1 for a in agents if a.stem in used_stems)
            perc_used = round(terr_used / terr_total * 100, 1) if terr_total else 0

            # Percentages
            perc_compliant = round(terr_compliant / terr_total * 100, 1)
            perc_hardened = round(terr_hardened / terr_total * 100, 1)
            perc_healing_cap = round(terr_healing_cap / terr_total * 100, 1)
            perc_healing_invoke = round(terr_healing_invoke / terr_total * 100, 1)
            perc_tests = round(terr_tests / terr_total * 100, 1)

            # Accumulate
            totals["agents"] += terr_total
            totals["compliant"] += terr_compliant
            totals["hardened"] += terr_hardened
            totals["healing_cap"] += terr_healing_cap
            totals["healing_invoke"] += terr_healing_invoke
            totals["tests"] += terr_tests
            totals["loc"] += terr_loc
            totals["used"] += terr_used
            totals["cc_sum"] += terr_cc_sum
            totals["typed"] += terr_typed
            totals["documented"] += terr_documented
            totals["observable"] += terr_observable
            totals["max_cc"] = max(totals["max_cc"], terr_max_cc)

            # Calculate new high-signal metrics
            layer_weight = {"L0": 5, "L1": 4, "L2": 3, "L3": 2, "L4": 1, "L5": 3, "unknown": 0}.get(layer_filter, 0)
            priority_weight = {"CRITICAL": 10, "HIGH": 7, "MEDIUM": 5, "LOW": 2}.get(priority, 0)
            criticality = min(100, (perc_used * 2) + layer_weight + priority_weight)
            
            health = round((perc_tests + perc_healing_invoke + perc_observable) / 3, 1)
            
            risk_score = 0
            if avg_cc > 10: risk_score += 3
            if perc_tests < 50: risk_score += 3
            if perc_compliant < 80: risk_score += 4
            risk = "HIGH" if risk_score >= 6 else "MED" if risk_score >= 3 else "LOW"

            # Display
            territory_name = territory_key.replace("_", " ").title()[:20]
            row = (
                f"| {territory_name:<42} | {terr_total:5} | {terr_compliant:9} "
                f"| {perc_healing_cap:5}% | {perc_healing_invoke:5}% | {perc_hardened:4}% | {perc_tests:5}% "
                f"| {avg_cc:6} | {perc_typed:5}% | {perc_observable:4}% | {criticality:5.0f} | {health:5.1f} | {risk:4} | {perc_used:4}% | {priority:8} |"
            )
            print(row)

        # Step 4: Unclassified row (exhaustive coverage)
        unclassified = [a for a in all_agents if a not in classified_paths]
        if unclassified:
            terr_total = len(unclassified)
            terr_compliant = terr_hardened = terr_healing_cap = terr_healing_invoke = terr_tests = 0
            terr_loc = terr_cc_sum = terr_max_cc = 0
            terr_typed = terr_documented = terr_observable = 0

            for a in unclassified:
                try:
                    content = a.read_text(errors="ignore")
                    lines = content.splitlines()
                    terr_loc += len([l for l in lines if l.strip() and not l.strip().startswith("#")])
                    
                    if "def heal_repository(self" in content: 
                        terr_compliant += 1
                        terr_healing_invoke += 1
                    if "MCPHardenedMixin" in content: terr_hardened += 1
                    # Healing capabilities: either inherits HealerMixin OR has healing logic
                    if "HealerMixin" in content or any(ind in content for ind in ["run(", "validate_", "auto_"]): terr_healing_cap += 1
                    # Count tests: external test file OR self-tests OR delegation OR pytest/unittest
                    has_ext = (a.parent / "tests" / f"test_{a.stem}.py").exists()
                    has_self = "_run_self_tests" in content or "SubatomicTestingMixin" in content or "SubatomicAgent" in content
                    has_deleg = "L0DelegationTestingMixin" in content or "L0DelegationMixin" in content or "TestSovereigntyAgent" in content or "_delegate_tests" in content or "delegate_on_failure" in content
                    has_inline = "def test_" in content or "import pytest" in content or "import unittest" in content
                    if has_ext or has_self or has_deleg or has_inline: terr_tests += 1
                    
                    tree = ast.parse(content)
                    functions = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                    classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
                    
                    for func in functions:
                        visitor = _CCVisitor()
                        visitor.visit(func)
                        terr_cc_sum += visitor.cc
                        terr_max_cc = max(terr_max_cc, visitor.cc)
                    
                    if functions:
                        typed = sum(1 for f in functions if f.returns or any(arg.annotation for arg in f.args.args if arg.arg != "self"))
                        terr_typed += (typed / len(functions)) * 100
                    
                    doc_count = sum(1 for cls in classes if cls.body and isinstance(cls.body[0], ast.Expr))
                    doc_count += sum(1 for f in functions if f.body and isinstance(f.body[0], ast.Expr))
                    if classes or functions:
                        terr_documented += (doc_count / (len(classes) + len(functions))) * 100
                    
                    if any(imp in content for imp in ["import logging", "from logging", "logger.", "log."]):
                        terr_observable += 100
                except:
                    pass

            avg_loc = round(terr_loc / terr_total, 1)
            avg_cc = round(terr_cc_sum / max(terr_total, 1), 1)
            terr_used = sum(1 for a in unclassified if a.stem in used_stems)
            perc_used = round(terr_used / terr_total * 100, 1)
            perc_compliant = round(terr_compliant / terr_total * 100, 1)
            perc_healing_cap = round(terr_healing_cap / terr_total * 100, 1)
            perc_healing_invoke = round(terr_healing_invoke / terr_total * 100, 1)
            perc_hardened = round(terr_hardened / terr_total * 100, 1)
            perc_tests = round(terr_tests / terr_total * 100, 1)
            perc_typed = round(terr_typed / terr_total, 1)
            perc_documented = round(terr_documented / terr_total, 1)
            perc_observable = round(terr_observable / terr_total, 1)

            totals["agents"] += terr_total
            totals["compliant"] += terr_compliant
            totals["hardened"] += terr_hardened
            totals["healing_cap"] += terr_healing_cap
            totals["healing_invoke"] += terr_healing_invoke
            totals["tests"] += terr_tests
            totals["loc"] += terr_loc
            totals["used"] += terr_used
            totals["cc_sum"] += terr_cc_sum
            totals["typed"] += terr_typed
            totals["documented"] += terr_documented
            totals["observable"] += terr_observable
            totals["max_cc"] = max(totals["max_cc"], terr_max_cc)

            # Calculate metrics for unclassified
            unclass_health = round((perc_tests + perc_healing_invoke + perc_observable) / 3, 1)
            unclass_criticality = min(100, (perc_used * 2) + 5)  # Default medium priority
            
            unclass_risk_score = 0
            if avg_cc > 10: unclass_risk_score += 3
            if perc_tests < 50: unclass_risk_score += 3
            if perc_compliant < 80: unclass_risk_score += 4
            unclass_risk = "HIGH" if unclass_risk_score >= 6 else "MED" if unclass_risk_score >= 3 else "LOW"

            row = (
                f"| **OTHER/UNCLASSIFIED**                     | {terr_total:5} | {terr_compliant:9} "
                f"| {perc_healing_cap:5}% | {perc_healing_invoke:5}% | {perc_hardened:4}% | {perc_tests:5}% "
                f"| {avg_cc:6} | {perc_typed:5}% | {perc_observable:4}% | {unclass_criticality:5.0f} | {unclass_health:5.1f} | {unclass_risk:4} | {perc_used:4}% | Review   |"
            )
            print(row)

        # Grand total
        if totals["agents"] > 0:
            t = totals
            total_perc = round(t["compliant"] / t["agents"] * 100, 1)
            total_hardened = round(t["hardened"] / t["agents"] * 100, 1)
            total_healing_cap = round(t["healing_cap"] / t["agents"] * 100, 1)
            total_healing_invoke = round(t["healing_invoke"] / t["agents"] * 100, 1)
            total_tests = round(t["tests"] / t["agents"] * 100, 1)
            overall_avg_loc = round(t["loc"] / t["agents"], 1)
            overall_avg_cc = round(t["cc_sum"] / t["agents"], 1)
            total_typed = round(t["typed"] / t["agents"], 1)
            total_documented = round(t["documented"] / t["agents"], 1)
            total_observable = round(t["observable"] / t["agents"], 1)
            total_used = round(t["used"] / t["agents"] * 100, 1)

            # Calculate total metrics
            total_health = round((total_tests + total_healing_invoke + total_observable) / 3, 1)
            total_criticality = min(100, (total_used * 2) + 30)  # Weighted average
            
            total_risk_score = 0
            if overall_avg_cc > 10: total_risk_score += 3
            if total_tests < 50: total_risk_score += 3
            if total_perc < 80: total_risk_score += 4
            total_risk = "HIGH" if total_risk_score >= 6 else "MED" if total_risk_score >= 3 else "LOW"

            total_row = (
                f"| **TOTAL**                                  | **{t['agents']}** | **{t['compliant']}** "
                f"| **{total_healing_cap}%** | **{total_healing_invoke}%** | **{total_hardened}%** | **{total_tests}%** "
                f"| **{overall_avg_cc}** | **{total_typed}%** | **{total_observable}%** | **{total_criticality:.0f}** | **{total_health:.1f}** | **{total_risk}** | **{total_used}%** | **ALL** |"
            )
            print(total_row)

            print(f"\n**Quick Stats:** {t['compliant']}/{t['agents']} compliant — {t['healing_cap']}/{t['agents']} with healing capabilities — {t['healing_invoke']}/{t['agents']} with healing invocation — {t['hardened']}/{t['agents']} MCP hardened — {t['used']}/{t['agents']} used elsewhere")
            print(f"**Quality:** Avg CC={overall_avg_cc} | Max CC={t['max_cc']} | {total_typed}% typed | {total_documented}% documented | {total_observable}% observable")

            # Save markdown report to file
            self._save_markdown_report(today, totals, all_agents, classified_paths, used_stems, path_to_layer)

    def _save_markdown_report(self, today: str, totals: dict, all_agents: list, classified_paths: set, used_stems: set, path_to_layer: dict) -> None:
        """Save compliance report as Windsurf-readable format with structured sections."""
        report_path = self.project_root / "reports" / "autonomy_compliance_report.md"
        csv_path = self.project_root / "reports" / "autonomy_compliance_data.csv"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        t = totals
        total_perc = round(t["compliant"] / t["agents"] * 100, 1) if t["agents"] else 0
        total_hardened = round(t["hardened"] / t["agents"] * 100, 1) if t["agents"] else 0
        total_healing_cap = round(t["healing_cap"] / t["agents"] * 100, 1) if t["agents"] else 0
        total_healing_invoke = round(t["healing_invoke"] / t["agents"] * 100, 1) if t["agents"] else 0
        total_tests = round(t["tests"] / t["agents"] * 100, 1) if t["agents"] else 0
        overall_avg_loc = round(t["loc"] / t["agents"], 1) if t["agents"] else 0
        overall_avg_cc = round(t["cc_sum"] / t["agents"], 1) if t["agents"] else 0
        total_typed = round(t["typed"] / t["agents"], 1) if t["agents"] else 0
        total_documented = round(t["documented"] / t["agents"], 1) if t["agents"] else 0
        total_observable = round(t["observable"] / t["agents"], 1) if t["agents"] else 0
        total_used = round(t["used"] / t["agents"] * 100, 1) if t["agents"] else 0
        
        # Calculate overall health and criticality
        overall_health = round((total_tests + total_healing_invoke + total_observable) / 3, 1)
        overall_criticality = min(100, (total_used * 2) + 30)
        
        overall_risk_score = 0
        if overall_avg_cc > 10: overall_risk_score += 3
        if total_tests < 50: overall_risk_score += 3
        if total_perc < 80: overall_risk_score += 4
        overall_risk = "HIGH" if overall_risk_score >= 6 else "MED" if overall_risk_score >= 3 else "LOW"

        md = f"""# Autonomy Compliance Report

**Generated:** {today}  
**Source:** `agent_discovery_full.json` (canonical AST scan)

## 🎯 Executive Summary

**System Health:** {overall_health:.1f}/100 | **Risk Level:** {overall_risk} | **Criticality:** {overall_criticality:.0f}/100

### Key Metrics
- **Total Agents:** {t['agents']}
- **Compliant:** {t['compliant']} ({total_perc}%) {'✅' if total_perc >= 80 else '⚠️' if total_perc >= 60 else '❌'}
- **Healing Capabilities:** {t['healing_cap']} ({total_healing_cap}%) {'✅' if total_healing_cap >= 80 else '⚠️' if total_healing_cap >= 60 else '❌'}
- **Healing Invocation:** {t['healing_invoke']} ({total_healing_invoke}%) {'✅' if total_healing_invoke >= 80 else '⚠️' if total_healing_invoke >= 60 else '❌'}
- **With Tests:** {t['tests']} ({total_tests}%) {'✅' if total_tests >= 80 else '⚠️' if total_tests >= 60 else '❌'}
- **Avg Complexity:** {overall_avg_cc} {'✅' if overall_avg_cc <= 10 else '⚠️' if overall_avg_cc <= 15 else '❌'}

## 📊 Territory Analysis

**Note:** Table data available in CSV format for better readability in spreadsheet tools.

### High Priority Territories (Criticality > 70)
"""
        # Create CSV data for spreadsheet viewing
        csv_data = []
        csv_headers = ["Territory", "Total", "Compliant", "Heal_Cap_Pct", "Heal_Inv_Pct", "MCP_Pct", "Test_Pct", "Avg_CC", "Typed_Pct", "Obs_Pct", "Criticality", "Health", "Risk", "Used_Pct", "Priority"]
        
        high_priority_territories = []
        medium_priority_territories = []
        low_priority_territories = []
        
        # Add territory rows using path_to_layer lookup
        for territory_key, (layer_filter, priority) in self.territories.items():
            # Get agents for this territory using path_to_layer
            if territory_key.startswith("L5_safety"):
                subfolder = territory_key.split("/")[1]
                agents = [p for p in all_agents if path_to_layer.get(str(p)) == "L5" and subfolder in str(p).replace("\\", "/")]
            else:
                agents = [p for p in all_agents if path_to_layer.get(str(p)) == layer_filter]
            
            if not agents:
                continue
            
            terr_total = len(agents)
            terr_compliant = sum(1 for a in agents if "def heal_repository(self" in a.read_text(errors="ignore"))
            terr_healing_invoke = sum(1 for a in agents if "def heal_repository(self" in a.read_text(errors="ignore"))
            terr_hardened = sum(1 for a in agents if "MCPHardenedMixin" in a.read_text(errors="ignore"))
            # Healing capabilities: either inherits HealerMixin OR has healing logic
            terr_healing_cap = sum(1 for a in agents if "HealerMixin" in a.read_text(errors="ignore") or any(ind in a.read_text(errors="ignore") for ind in ["run(", "validate_", "auto_"]))
            terr_tests = sum(1 for a in agents if any(p in a.read_text(errors="ignore") for p in ["_run_self_tests", "SubatomicTestingMixin", "SubatomicAgent", "L0DelegationTestingMixin", "L0DelegationMixin", "TestSovereigntyAgent", "_delegate_tests", "delegate_on_failure", "def test_", "import pytest", "import unittest"]))
            terr_used = sum(1 for a in agents if a.stem in used_stems)
            
            # Calculate basic percentages
            perc_comp = round(terr_compliant / terr_total * 100, 1) if terr_total else 0
            perc_heal_cap = round(terr_healing_cap / terr_total * 100, 1) if terr_total else 0
            perc_heal_inv = round(terr_healing_invoke / terr_total * 100, 1) if terr_total else 0
            perc_hard = round(terr_hardened / terr_total * 100, 1) if terr_total else 0
            perc_test = round(terr_tests / terr_total * 100, 1) if terr_total else 0
            perc_used = round(terr_used / terr_total * 100, 1) if terr_total else 0
            
            # Calculate detailed metrics
            terr_cc_sum = 0
            terr_typed = 0
            terr_observable = 0
            
            for a in agents:
                content = a.read_text(errors="ignore")
                # CC calculation
                try:
                    tree = ast.parse(content)
                    functions = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                    for func in functions:
                        visitor = _CCVisitor()
                        visitor.visit(func)
                        terr_cc_sum += visitor.cc
                except:
                    pass
                
                # Type/obs detection
                if "typing" in content or "from typing" in content or "import typing" in content:
                    terr_typed += 1
                if "logging" in content or "log" in content or "Logger" in content:
                    terr_observable += 1
            
            avg_cc = round(terr_cc_sum / terr_total, 1) if terr_total else 0
            perc_typed = round(terr_typed / terr_total * 100, 1) if terr_total else 0
            perc_obs = round(terr_observable / terr_total * 100, 1) if terr_total else 0
            
            # Calculate high-signal metrics
            layer_weight = {"L0": 5, "L1": 4, "L2": 3, "L3": 2, "L4": 1, "L5": 3, "unknown": 0}.get(layer_filter, 0)
            priority_weight = {"CRITICAL": 10, "HIGH": 7, "MEDIUM": 5, "LOW": 2}.get(priority, 0)
            criticality = min(100, (perc_used * 2) + layer_weight + priority_weight)
            
            health = round((perc_test + perc_heal_inv + perc_obs) / 3, 1)
            
            risk_score = 0
            if avg_cc > 10: risk_score += 3
            if perc_test < 50: risk_score += 3
            if perc_comp < 80: risk_score += 4
            risk = "HIGH" if risk_score >= 6 else "MED" if risk_score >= 3 else "LOW"
            
            # Add to CSV data
            csv_data.append([
                territory_key.replace("_", " ").title(), terr_total, terr_compliant, perc_heal_cap, perc_heal_inv,
                perc_hard, perc_test, avg_cc, perc_typed, perc_obs, criticality, health, risk, perc_used, priority
            ])
            
            # Categorize territory
            territory_info = {
                "name": territory_key.replace("_", " ").title(),
                "total": terr_total,
                "compliant": terr_compliant,
                "health": health,
                "risk": risk,
                "criticality": criticality,
                "heal_gap": perc_heal_cap - perc_heal_inv
            }
            
            if criticality > 70:
                high_priority_territories.append(territory_info)
            elif criticality > 40:
                medium_priority_territories.append(territory_info)
            else:
                low_priority_territories.append(territory_info)

        # Add territory summaries to markdown
        for territory_list, title in [(high_priority_territories, "High Priority"), (medium_priority_territories, "Medium Priority"), (low_priority_territories, "Low Priority")]:
            if territory_list:
                md += f"\n### {title} Territories\n\n"
                for t in sorted(territory_list, key=lambda x: x['criticality'], reverse=True):
                    status_icon = "🔥" if t['risk'] == "HIGH" else "⚠️" if t['risk'] == "MED" else "✅"
                    heal_gap_note = f" | Heal Gap: {t['heal_gap']:.1f}%" if abs(t['heal_gap']) > 10 else ""
                    md += f"- {status_icon} **{t['name']}**: {t['compliant']}/{t['total']} compliant | Health: {t['health']:.1f}% | Risk: {t['risk']}{heal_gap_note}\n"

        # Handle unclassified agents
        unclassified = [a for a in all_agents if a not in classified_paths]
        if unclassified:
            terr_total = len(unclassified)
            terr_compliant = sum(1 for a in unclassified if "def heal_repository(self" in a.read_text(errors="ignore"))
            terr_healing_invoke = sum(1 for a in unclassified if "def heal_repository(self" in a.read_text(errors="ignore"))
            terr_hardened = sum(1 for a in unclassified if "MCPHardenedMixin" in a.read_text(errors="ignore"))
            # Healing capabilities: either inherits HealerMixin OR has healing logic
            terr_healing_cap = sum(1 for a in unclassified if "HealerMixin" in a.read_text(errors="ignore") or any(ind in a.read_text(errors="ignore") for ind in ["run(", "validate_", "auto_"]))
            terr_tests = sum(1 for a in unclassified if any(p in a.read_text(errors="ignore") for p in ["_run_self_tests", "SubatomicTestingMixin", "SubatomicAgent", "L0DelegationTestingMixin", "L0DelegationMixin", "TestSovereigntyAgent", "_delegate_tests", "delegate_on_failure", "def test_", "import pytest", "import unittest"]))
            terr_used = sum(1 for a in unclassified if a.stem in used_stems)
            
            # Calculate unclassified metrics quickly
            terr_cc_sum = 0
            terr_typed = 0
            terr_observable = 0
            
            for a in unclassified:
                content = a.read_text(errors="ignore")
                try:
                    tree = ast.parse(content)
                    functions = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                    for func in functions:
                        visitor = _CCVisitor()
                        visitor.visit(func)
                        terr_cc_sum += visitor.cc
                except:
                    pass
                
                if "typing" in content or "from typing" in content:
                    terr_typed += 1
                if "logging" in content or "log" in content:
                    terr_observable += 1
            
            avg_cc = round(terr_cc_sum / terr_total, 1) if terr_total else 0
            perc_comp = round(terr_compliant / terr_total * 100, 1) if terr_total else 0
            perc_heal_cap = round(terr_healing_cap / terr_total * 100, 1) if terr_total else 0
            perc_heal_inv = round(terr_healing_invoke / terr_total * 100, 1) if terr_total else 0
            perc_hard = round(terr_hardened / terr_total * 100, 1) if terr_total else 0
            perc_test = round(terr_tests / terr_total * 100, 1) if terr_total else 0
            perc_typed = round(terr_typed / terr_total * 100, 1) if terr_total else 0
            perc_obs = round(terr_observable / terr_total * 100, 1) if terr_total else 0
            perc_used = round(terr_used / terr_total * 100, 1) if terr_total else 0
            
            # Calculate unclassified metrics
            unclass_health = round((perc_test + perc_heal_inv + perc_obs) / 3, 1)
            unclass_criticality = min(100, (perc_used * 2) + 5)
            unclass_risk_score = 0
            if avg_cc > 10: unclass_risk_score += 3
            if perc_test < 50: unclass_risk_score += 3  
            if perc_comp < 80: unclass_risk_score += 4
            unclass_risk = "HIGH" if unclass_risk_score >= 6 else "MED" if unclass_risk_score >= 3 else "LOW"
            
            # Add to CSV
            csv_data.append([
                "OTHER/UNCLASSIFIED", terr_total, terr_compliant, perc_heal_cap, perc_heal_inv,
                perc_hard, perc_test, avg_cc, perc_typed, perc_obs, unclass_criticality, unclass_health, unclass_risk, perc_used, "Review"
            ])
            
            # Add to markdown
            md += f"\n### Unclassified Agents\n\n"
            md += f"- ❓ **Unclassified**: {terr_compliant}/{terr_total} compliant | Health: {unclass_health:.1f}% | Risk: {unclass_risk} | Heal Gap: {perc_heal_cap - perc_heal_inv:.1f}%\n"

        # Add CSV totals
        total_agents = t.get('agents', 0)
        total_compliant = t.get('compliant', 0)
        csv_data.append([
            "TOTAL", total_agents, total_compliant, total_healing_cap, total_healing_invoke,
            total_hardened, total_tests, overall_avg_cc, total_typed, total_observable, overall_criticality, overall_health, overall_risk, total_used, "ALL"
        ])

        # Finish markdown report
        md += f"""

## 📈 Recommendations

### Immediate Actions (High Risk)
"""
        high_risk_territories = [t for t in high_priority_territories + medium_priority_territories if t['risk'] == 'HIGH']
        if high_risk_territories:
            for t in high_risk_territories:
                md += f"- **{t['name']}**: Focus on complexity reduction (CC={avg_cc:.1f}) and test coverage\n"
        else:
            md += "- No high-risk territories identified ✅\n"

        md += f"""
### Healing Gap Closure
"""
        healing_gaps = [(t['name'], t['heal_gap']) for t in high_priority_territories + medium_priority_territories if abs(t['heal_gap']) > 15]
        if healing_gaps:
            for name, gap in sorted(healing_gaps, key=lambda x: abs(x[1]), reverse=True):
                action = "Add heal_repository() methods" if gap > 0 else "Remove unused HealerMixin inheritance"
                md += f"- **{name}**: {action} (Gap: {gap:.1f}%)\n"
        else:
            md += "- Healing capabilities and invocation are well-aligned ✅\n"

        md += f"""

## 📊 Data Files

- **Detailed CSV**: `reports/autonomy_compliance_data.csv` (open in Excel/Sheets)
- **Summary Report**: This markdown file

---
*Report generated by AutonomyGuardianAgent | {today}*
"""
        
        # Write CSV file
        import csv
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(csv_headers)
            writer.writerows(csv_data)
        
        # Write markdown report
        report_path.write_text(md, encoding="utf-8")
        
        # Launch interactive dashboard
        dashboard_path = self.project_root / "reports" / "autonomy_dashboard.html"
        if dashboard_path.exists():
            print(f"\n[SAVED] Markdown: {report_path}")
            print(f"[SAVED] CSV Data: {csv_path}")
            print(f"[READY] Interactive Dashboard: {dashboard_path}")
            print(f"\n🚀 VIEW DASHBOARD:")
            print(f"   1. Install 'Live Server' extension in VS Code")
            print(f"   2. Right-click {dashboard_path.name} → 'Open with Live Server'")
            print(f"   3. Or open file directly in browser for static view")
        else:
            print(f"\n[SAVED] Markdown: {report_path}")
            print(f"[SAVED] CSV Data: {csv_path}")


# Singleton accessor
_autonomy_guardian: Optional[AutonomyGuardianAgent] = None


def get_autonomy_guardian(project_root: Path) -> AutonomyGuardianAgent:
    """Get singleton instance of AutonomyGuardianAgent."""
    global _autonomy_guardian
    if _autonomy_guardian is None:
        _autonomy_guardian = AutonomyGuardianAgent(project_root)
    return _autonomy_guardian
