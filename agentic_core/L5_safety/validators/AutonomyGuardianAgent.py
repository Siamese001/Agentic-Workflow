from __future__ import annotations
"""
Autonomy Guardian Agent - Autonomy Meta-Enforcement
Ensures all domain agents have heal_repository() and no external scripts.
This is the sovereign guardian for agent autonomy across the repository.
"""
from datetime import date, datetime
from pathlib import Path
from typing import List, Dict, Any, Set, Optional, Tuple
import ast
import json
import re
import webbrowser

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.timeout_decorator import timeout, HealTimeoutError


class _CCVisitor(ast.NodeVisitor):
    """Cyclomatic Complexity visitor for AST analysis."""
    def __init__(self) -> None:
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
    
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.required_methods = ["heal_repository"]
        self.forbidden_dirs = ["scripts/healing", "scripts/tools", "scripts/runners"]
        self.forbidden_patterns = ["heal", "runner", "launcher", "driver"]
        self.exclude_patterns = ["test_", "example_", "mock_", "stub_", "legacy", "deprecated"]
        
        # Load agents from authoritative JSON (agent_discovery_full.json)
        self._agent_registry_cache = None
        
        # Territory definitions for compliance report - map to JSON layers
        # IMPORTANT: Use layer-based matching to avoid double-counting
        # Each territory maps to exactly one layer from agent_discovery_full.json
        self.territories = {
            # L5 Safety - Most Critical (Top Priority) - distinct subfolders
            "L5_safety/validators": ("L5", "Critical"),
            "L5_safety/guardrails": ("L5", "Critical"),
            "L5_safety/gravity": ("L5", "High"),
            "L5_safety/red_teaming": ("L5", "High"),
            
            # L4-L0 Layers - single territory per layer to avoid double-counting
            "L4_state": ("L4", "High"),
            "L3_orchestration": ("L3", "High"),
            "L2_execution": ("L2", "High"),
            "L1_cognition": ("L1", "Medium"),
            "L0_maintenance": ("L0", "Medium"),
            
            # Apps - single territory per app to avoid double-counting
            "apps_lic": ("apps_lic", "High"),
            "apps_rg": ("apps_rg", "High"),
            "apps_shared": ("apps_shared", "Medium"),
            
            # Tests
            "tests": ("tests", "Medium"),
        }
        
        # Infrastructure path patterns - agents matching these are annotated as infrastructure
        # but still counted in their layer territory (no double-counting)
        self.infrastructure_path_patterns = {"observability", "config/validators"}
        
        # Phase 5: Layer base class mapping (SSOT - sync with pre-commit hook)
        self.LAYER_BASE_MAP = {
            "L0": "MaintenanceBaseAgent",
            "L1": "L1CognitionBaseAgent",
            "L2": "L2ExecutionBaseAgent",
            "L3": "OrchestrationBaseAgent",
            "L4": "StateBaseAgent",
            "L5": "SafetyBaseAgent",
        }
    
    def _detect_layer(self, file_path: str) -> str:
        """Detect L0-L5 layer from path."""
        path = Path(file_path)
        for part in path.parts:
            if part.startswith("L") and len(part) == 2 and part[1].isdigit():
                return part
        return "UNKNOWN"
    
    def _get_base_names(self, node: ast.ClassDef) -> list:
        """Extract base class names."""
        bases = []
        for base in node.bases:
            if hasattr(base, "id"):
                bases.append(base.id)
            elif hasattr(base, "attr"):
                bases.append(base.attr)
        return bases
    
    def _check_base_class_compliance(self, file_path: str) -> tuple:
        """Phase 5: Verify agent inherits from correct layer base class."""
        layer = self._detect_layer(file_path)
        if layer not in self.LAYER_BASE_MAP:
            return True, "Non-agent file"
        
        expected = self.LAYER_BASE_MAP[layer]
        
        try:
            tree = ast.parse(Path(file_path).read_text(encoding="utf-8"))
        except Exception as e:
            return False, f"Parse error: {e}"
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name.endswith("Agent"):
                bases = self._get_base_names(node)
                if expected not in bases:
                    return False, f"Missing {expected} (found {bases})"
        
        return True, "Compliant"
    
    def _generate_sparkline(self, values: List[float]) -> List[float]:
        """Return raw values for sparkline rendering (last 10 max)."""
        if len(values) < 2:
            return []  # Insufficient data
        
        return values[-10:]  # Last 10 runs max
    
    def _load_agent_registry(self) -> List[Dict[str, Any]]:
        """Load agents from agent_discovery_full.json (authoritative AST scan)."""
        if self._agent_registry_cache is not None:
            return self._agent_registry_cache
        
        json_path = self.project_root / "agent_discovery_full.json"
        legacy_json_path = self.project_root / "agent_discovery_full.json"
        if not json_path.exists() and legacy_json_path.exists():
            json_path = legacy_json_path

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
        """Get all agent file paths from the authoritative JSON registry (deduplicated)."""
        registry = self._load_agent_registry()
        seen_paths = set()
        paths = []
        for agent in registry:
            path_str = agent.get("path", "").replace("\\", "/")
            if path_str and path_str not in seen_paths:
                seen_paths.add(path_str)
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
    
    def _detect_documentation_coverage(self, source_code: str) -> float:
        """Calculate percentage of definitions (functions/classes/methods) with docstrings."""
        try:
            tree = ast.parse(source_code)
            defs = [node for node in ast.walk(tree) 
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
            
            if not defs:
                return 100.0  # No defs = trivially documented
            
            documented = 0
            for node in defs:
                docstring = ast.get_docstring(node)
                if docstring and docstring.strip():  # Non-empty after strip
                    documented += 1
            
            return round(documented / len(defs) * 100, 1)
        except Exception:
            return 0.0  # Parse error = 0% documented
    
    def _count_source_loc(self, source_code: str) -> int:
        """Count non-blank, non-comment physical source lines of code (SLOC)."""
        lines = source_code.splitlines()
        sloc = 0
        for line in lines:
            stripped = line.strip()
            if not stripped:  # Blank line
                continue
            if stripped.startswith('#'):  # Single-line comment
                continue
            sloc += 1
        return sloc
    
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
            self._print_markdown_header()

        # Initialize data structures
        totals = self._initialize_totals()
        registry = self._load_agent_registry()
        all_agents, path_to_layer = self._process_agent_registry(registry)
        used_stems = self._compute_global_usage(all_agents)
        
        # Global sub-atomic violation tracking (across all territories)
        global_sub_atomic_violations = []  # List of (cc, file_path, method_name)
        
        print(f"Loaded {len(all_agents)} agents from agent_discovery_full.json\n")

        # Process territories and generate report
        classified_paths = self._process_territories(
            all_agents, path_to_layer, used_stems, totals, markdown, global_sub_atomic_violations
        )

        # Process unclassified agents and generate final report
        unclassified_agents = [a for a in all_agents if a not in classified_paths]
        if unclassified_agents and markdown:
            self._process_unclassified_agents(unclassified_agents, used_stems, totals)
            
        if markdown:
            today = date.today().strftime("%B %d, %Y")
            self._save_markdown_report(today, totals, all_agents, classified_paths, used_stems, path_to_layer)
            
            # === Self-Contained Interactive Dashboard Generation ===
            self._generate_self_contained_dashboard(today, all_agents, classified_paths, used_stems, path_to_layer)

        # Portfolio-wide top violations — sub-atomic refactor backlog
        if global_sub_atomic_violations:
            print("\n**Portfolio Top 10 Sub-Atomic Violations (CC >10 — prioritize for decomposition):**")
            top_violations = sorted(global_sub_atomic_violations, reverse=True)[:10]
            for cc, path, method in top_violations:
                print(f"  - {cc:3} | {path}:{method}() → Extract to primitives")
            if len(global_sub_atomic_violations) > 10:
                print(f"  ... and {len(global_sub_atomic_violations) - 10} more — full list per territory above")
            print("  → Impact: Enables true sub-atomic reuse/orchestration across agents\n")

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

            # Calculate total metrics with improved distribution
            total_health = round((total_tests + total_healing_invoke + total_observable) / 3, 1)
            
            # Total criticality: weighted average of usage, compliance gap, and system size
            total_usage_factor = min(40, total_used * 0.4)
            total_compliance_gap = max(0, 80 - total_perc) * 0.3
            total_size_factor = min(20, t['agents'] * 0.05)  # Scale down for total agents
            total_criticality = round((total_usage_factor + total_compliance_gap + total_size_factor) * 1.2, 1)
            
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
        """High-level orchestrator for report generation — linear chain with early exits."""
        report_path = self.project_root / "reports" / "autonomy_compliance_report.md"
        csv_path = self.project_root / "reports" / "autonomy_compliance_data.csv"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Phase 1: Calculate global metrics
        global_metrics = self._calculate_global_metrics(totals)
        
        # Phase 2: Build header and initialize collections
        md = self._build_report_header(today, global_metrics)
        csv_data = []
        csv_headers = ["Territory", "Total", "Compliant", "Heal_Cap_Pct", "Heal_Inv_Pct", "MCP_Pct", "Test_Pct", "Avg_CC", "Typed_Pct", "Obs_Pct", "Criticality", "Health", "Risk", "Used_Pct", "Priority"]
        
        high_priority_territories = []
        medium_priority_territories = []
        low_priority_territories = []
        
        # Phase 3: Process classified territories
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
            terr_healing_invoke = sum(1 for a in agents if "super().heal_repository()" in a.read_text(errors="ignore"))
            terr_hardened = sum(1 for a in agents if "MCPHardenedMixin" in a.read_text(errors="ignore"))
            # Healing capabilities: ONLY count agents that inherit HealerMixin or have heal_repository method
            terr_healing_cap = sum(1 for a in agents if "HealerMixin" in a.read_text(errors="ignore") or "def heal_repository" in a.read_text(errors="ignore"))
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
            
            # Calculate high-signal metrics with better distribution
            layer_multiplier = {"L0": 1.3, "L1": 1.2, "L2": 1.1, "L3": 1.0, "L4": 0.9, "L5": 1.4, "unknown": 0.8}.get(layer_filter, 1.0)
            priority_multiplier = {"CRITICAL": 1.5, "HIGH": 1.3, "MEDIUM": 1.1, "LOW": 0.9}.get(priority, 1.0)
            
            # Business criticality: usage + compliance gap + size impact
            usage_factor = min(40, perc_used * 0.4)  # Max 40 points from usage
            compliance_gap = max(0, 80 - perc_comp) * 0.3  # Gap penalty, max 24 points
            size_factor = min(20, terr_total * 0.5)  # Size impact, max 20 points
            
            base_criticality = usage_factor + compliance_gap + size_factor
            criticality = round(base_criticality * layer_multiplier * priority_multiplier, 1)
            
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
            terr_healing_invoke = sum(1 for a in unclassified if "super().heal_repository()" in a.read_text(errors="ignore"))
            terr_hardened = sum(1 for a in unclassified if "MCPHardenedMixin" in a.read_text(errors="ignore"))
            # Healing capabilities: ONLY count agents that inherit HealerMixin or have heal_repository method
            terr_healing_cap = sum(1 for a in unclassified if "HealerMixin" in a.read_text(errors="ignore") or "def heal_repository" in a.read_text(errors="ignore"))
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
        csv_data.append([
            "TOTAL", global_metrics['agents'], global_metrics['compliant'], global_metrics['total_healing_cap'], global_metrics['total_healing_invoke'],
            global_metrics['total_hardened'], global_metrics['tests'], global_metrics['overall_avg_cc'], global_metrics['total_typed'], global_metrics['total_observable'], global_metrics['overall_criticality'], global_metrics['overall_health'], global_metrics['overall_risk'], global_metrics['total_used'], "ALL"
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

    def _print_markdown_header(self) -> None:
        """Print markdown table header for compliance report."""
        header = (
            "| Territory / Layer                          | Total | Compliant | % Heal Cap | % Heal Inv | % MCP | % Test | Avg CC | % Typed | % Obs | Criticality | Health | Risk | % Used | Priority |\n"
            "|--------------------------------------------|-------|-----------|------------|-------------|-------|--------|--------|---------|-------|-------------|--------|------|--------|----------|\n"
        )
        print(header)

    def _initialize_totals(self) -> Dict[str, int]:
        """Initialize totals accumulator for compliance metrics."""
        return {
            "agents": 0, "compliant": 0, "hardened": 0,
            "healing_cap": 0, "healing_invoke": 0, "tests": 0, "loc": 0, "used": 0,
            "cc_sum": 0, "typed": 0, "documented": 0, "observable": 0, "max_cc": 0
        }

    def _process_agent_registry(self, registry: List[Dict]) -> Tuple[List[Path], Dict[str, str]]:
        """Process agent registry to extract paths and layer mappings."""
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
                    
        return all_agents, path_to_layer

    def _compute_global_usage(self, all_agents: List[Path]) -> set:
        """Compute which agents are used/imported elsewhere."""
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
        return used_stems

    def _process_territories(
        self, all_agents: List[Path], path_to_layer: Dict[str, str], 
        used_stems: set, totals: Dict[str, int], markdown: bool,
        global_sub_atomic_violations: List[Tuple[int, str, str]]
    ) -> set:
        """Process all territories and track sub-atomic violations."""
        classified_paths = set()
        atomic_threshold = 10  # CC threshold for sub-atomic violations
        cross_cutting_territories = {"observability", "knowledge"}  # Don't count in totals
        
        for territory_key, (layer_filter, priority) in self.territories.items():
            agents = self._get_territory_agents(territory_key, layer_filter, all_agents, path_to_layer)
            
            # Only add to classified_paths if not cross-cutting (to avoid double-counting in totals)
            if territory_key not in cross_cutting_territories:
                classified_paths.update(agents)

            if len(agents) == 0:
                continue

            # Compute territory metrics and track violations
            metrics = self._compute_territory_metrics_with_violations(
                agents, used_stems, atomic_threshold, global_sub_atomic_violations
            )
            
            # Only update totals for non-cross-cutting territories
            if territory_key not in cross_cutting_territories:
                self._update_totals(totals, metrics)

            if markdown:
                self._print_territory_row(territory_key, metrics, priority)
                
                # Phase 4: Detect invocation gaps (has method but no super() chain)
                invocation_gaps = []
                for agent in agents:
                    try:
                        content = agent.read_text(errors="ignore")
                        has_method = "def heal_repository(self" in content
                        has_invocation = "super().heal_repository(" in content
                        if has_method and not has_invocation:
                            rel_path = str(agent.relative_to(self.project_root))
                            invocation_gaps.append(f"  - {rel_path}")
                    except Exception:
                        pass
                
                if invocation_gaps:
                    territory_name = territory_key.replace("_", " ").title()
                    print(f"\n**Healing Invocation Gap in {territory_name} (add super() chain):**")
                    for gap in sorted(invocation_gaps)[:20]:
                        print(gap)
                    if len(invocation_gaps) > 20:
                        print(f"  ... {len(invocation_gaps) - 20} more — full grep recommended")
                    print("  → Impact: Enables shared healing chain — +60% potential invocation boost\n")
                
        return classified_paths

    def _get_territory_agents(
        self, territory_key: str, layer_filter: str, 
        all_agents: List[Path], path_to_layer: Dict[str, str]
    ) -> List[Path]:
        """Get agents for a specific territory using layer-based matching.
        
        Uses the 'layer' field from agent_discovery_full.json to ensure
        each agent is counted in exactly one territory (no double-counting).
        """
        if territory_key.startswith("L5_safety/"):
            # L5 has distinct subfolders (validators, guardrails, gravity, red_teaming)
            subfolder = territory_key.split("/")[1]

            def is_red_team_agent_file(p: Path) -> bool:
                s = str(p).replace("\\", "/").lower()
                if "/l5_safety/red_teaming/" in s:
                    return True
                if "/l5_safety/guardrails/" in s:
                    fname = p.name.lower()
                    return any(t in fname for t in ("redteam", "redteamer", "promptinjection", "adversarial"))
                return False

            if subfolder == "red_teaming":
                return [
                    p for p in all_agents
                    if path_to_layer.get(str(p)) == "L5" and is_red_team_agent_file(p)
                ]

            if subfolder == "guardrails":
                return [
                    p for p in all_agents
                    if path_to_layer.get(str(p)) == "L5"
                    and subfolder in str(p).replace("\\", "/")
                    and not is_red_team_agent_file(p)
                ]

            return [
                p for p in all_agents
                if path_to_layer.get(str(p)) == "L5" and subfolder in str(p).replace("\\", "/")
            ]
        else:
            # All other territories: match by layer field from JSON
            # This ensures each agent is counted exactly once
            return [
                p for p in all_agents
                if path_to_layer.get(str(p)) == layer_filter
            ]

    def _compute_territory_metrics_with_violations(
        self, agents: List[Path], used_stems: set, 
        atomic_threshold: int, global_violations: List[Tuple[int, str, str]]
    ) -> Dict[str, Any]:
        """Metric computation orchestrator — linear phase chain."""
        if not agents:
            return self._empty_metrics()

        metrics = self._initialize_metrics(len(agents))
        
        # Phase 1: Analyze each agent
        for agent in agents:
            file_metrics = self._analyze_single_agent(agent, atomic_threshold, global_violations)
            self._aggregate_file_metrics(metrics, file_metrics)
        
        # Phase 2: Finalize and track usage
        self._finalize_metrics(metrics, agents, used_stems)
        return metrics

    def _empty_metrics(self) -> Dict[str, Any]:
        """Handle empty territory edge case."""
        return {
            "total": 0, "compliant": 0, "hardened": 0, "mcp_capable": 0, "healing_cap": 0, "healing_invoke": 0,
            "tests": 0, "loc": 0, "cc_sum": 0, "max_cc": 0, "typed": 0,
            "documented": 0, "observable": 0, "used": 0
        }

    def _initialize_metrics(self, total: int) -> Dict[str, Any]:
        """Base metrics structure."""
        return {
            "total": total,
            "compliant": 0, "hardened": 0, "mcp_capable": 0, "healing_cap": 0, "healing_invoke": 0,
            "tests": 0, "loc": 0, "cc_sum": 0, "max_cc": 0, "typed": 0,
            "documented": 0, "observable": 0, "used": 0
        }

    def _analyze_single_agent(
        self, agent: Path, atomic_threshold: int, global_violations: List[Tuple[int, str, str]]
    ) -> Dict[str, Any]:
        """Per-agent analysis — isolated AST + checks."""
        file_metrics = {
            "loc": 0, "compliant": 0, "hardened": 0, "mcp_capable": 0, "healing_cap": 0, "healing_invoke": 0,
            "tests": 0, "cc_sum": 0, "max_cc": 0, "typed": 0, "documented": 0, "observable": 0
        }
        
        try:
            content = agent.read_text(errors="ignore")
            lines = content.splitlines()
            file_metrics["loc"] = len([l for l in lines if l.strip() and not l.strip().startswith("#")])

            # Phase 1a: AST parsing and compliance checks
            try:
                tree = ast.parse(content)
                
                # MCP hardening detection (security)
                file_metrics["hardened"] = self._detect_mcp_hardening(tree, content)
                
                # MCP capability detection (uses MCP servers)
                file_metrics["mcp_capable"] = self._detect_mcp_capability(content)
                
                # Healing invocation detection
                file_metrics["healing_invoke"] = self._detect_healing_invocation(tree, content)
                
                # Healing capability detection
                file_metrics["healing_cap"] = self._detect_healing_capability(tree, content)
                
                # Compliance: has heal_repository method
                file_metrics["compliant"] = self._detect_heal_repository(tree)
                
            except (SyntaxError, Exception):
                pass
            
            # Phase 1b: Test detection
            file_metrics["tests"] = self._detect_tests(agent, content)
            
            # Phase 1c: AST metrics (CC, typing, docs, observability)
            try:
                tree = ast.parse(content)
                self._compute_ast_metrics(tree, file_metrics, agent, atomic_threshold, global_violations)
            except (SyntaxError, Exception):
                # Don't inflate max_cc with arbitrary high value for errors
                pass
            
            # Phase 1d: Observability detection
            file_metrics["observable"] = 100 if any(imp in content for imp in ["import logging", "from logging", "logger.", "log."]) else 0
                
        except Exception:
            pass

        return file_metrics

    def _detect_mcp_capability(self, content: str) -> int:
        """Check if agent uses MCP client to call external MCP servers."""
        mcp_imports = [
            "from mcp import",
            "import mcp",
            "ClientSession",
            "mcp.types",
            "mcp_client",
            "from mcp.client",
            "MCPClient"
        ]
        return 1 if any(pattern in content for pattern in mcp_imports) else 0
    
    def _detect_mcp_hardening(self, tree: ast.AST, content: str) -> int:
        """Check for MCPHardenedMixin, MCPShield mixin, or @hardened decorator (security protection)."""
        # Fast string check first (most common pattern)
        if "MCPHardenedMixin" in content or "MCPShield" in content:
            return 1
        # AST check for decorators
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if any(isinstance(d, ast.Name) and d.id == "hardened" for d in node.decorator_list):
                    return 1
        return 0

    def _detect_healing_invocation(self, tree: ast.AST, content: str) -> int:
        """Detect super().heal_repository() calls using string matching (more reliable)."""
        # String-based detection catches all patterns
        if "super().heal_repository()" in content:
            return 1
        # Also catch super(ClassName, self).heal_repository() pattern
        if "super(" in content and ".heal_repository()" in content:
            return 1
        return 0

    def _detect_healing_capability(self, tree: ast.AST, content: str) -> int:
        """Check for HealerMixin or heal_repository method (precise detection)."""
        if "HealerMixin" in content:
            return 1
        if "def heal_repository" in content:
            return 1
        return 0

    def _detect_heal_repository(self, tree: ast.AST) -> int:
        """Check for heal_repository method definition."""
        if any(isinstance(node, ast.FunctionDef) and node.name == "heal_repository" for node in ast.walk(tree)):
            return 1
        return 0

    def _detect_tests(self, agent: Path, content: str) -> int:
        """Detect test presence via multiple indicators."""
        has_external_test = (agent.parent / "tests" / f"test_{agent.stem}.py").exists()
        has_self_test = "_run_self_tests" in content or "SubatomicTestingMixin" in content
        has_delegation = "L0DelegationTestingMixin" in content or "_delegate_tests" in content
        has_inline_tests = "def test_" in content or "import pytest" in content
        return 1 if (has_external_test or has_self_test or has_delegation or has_inline_tests) else 0

    def _compute_ast_metrics(
        self, tree: ast.AST, file_metrics: Dict[str, Any], agent: Path,
        atomic_threshold: int, global_violations: List[Tuple[int, str, str]]
    ) -> None:
        """Compute CC, typing, documentation, and violation tracking."""
        functions = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]

        # CC calculation and violation tracking
        for func_node in functions:
            visitor = _CCVisitor()
            visitor.visit(func_node)
            cc = visitor.cc
            
            if cc > atomic_threshold:
                file_path = str(agent.relative_to(self.project_root))
                global_violations.append((cc, file_path, func_node.name))
            
            file_metrics["cc_sum"] += cc
            file_metrics["max_cc"] = max(file_metrics["max_cc"], cc)

        # Typing coverage
        if functions:
            typed = sum(1 for f in functions if f.returns or any(arg.annotation for arg in f.args.args if arg.arg != "self"))
            file_metrics["typed"] = (typed / len(functions)) * 100

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
            file_metrics["documented"] = (doc_count / total_targets) * 100

    def _aggregate_file_metrics(self, metrics: Dict[str, Any], file_metrics: Dict[str, Any]) -> None:
        """Aggregate per-file results — simple increments."""
        metrics["compliant"] += file_metrics["compliant"]
        metrics["hardened"] += file_metrics["hardened"]
        metrics["mcp_capable"] += file_metrics["mcp_capable"]
        metrics["healing_cap"] += file_metrics["healing_cap"]
        metrics["healing_invoke"] += file_metrics["healing_invoke"]
        metrics["tests"] += file_metrics["tests"]
        metrics["loc"] += file_metrics["loc"]  # Sum LOC for average calculation
        metrics["cc_sum"] += file_metrics["cc_sum"]
        metrics["max_cc"] = max(metrics["max_cc"], file_metrics["max_cc"])
        metrics["typed"] += file_metrics["typed"]
        # Documentation %: Sum per-agent coverage for average calculation (granular signal)
        # Changed from threshold-based to reward partial documentation
        metrics["documented"] += file_metrics["documented"]
        metrics["observable"] += file_metrics["observable"]

    def _finalize_metrics(self, metrics: Dict[str, Any], agents: List[Path], used_stems: set) -> None:
        """Final calculations and usage tracking."""
        metrics["used"] = sum(1 for a in agents if a.stem in used_stems)

    def _old_compute_territory_metrics_with_violations(
        self, agents: List[Path], used_stems: set, 
        atomic_threshold: int, global_violations: List[Tuple[int, str, str]]
    ) -> Dict[str, Any]:
        """DEPRECATED: Old implementation kept for reference during transition."""
        metrics = {
            "total": len(agents),
            "compliant": 0, "hardened": 0, "mcp_capable": 0, "healing_cap": 0, "healing_invoke": 0,
            "tests": 0, "loc": 0, "cc_sum": 0, "max_cc": 0, "typed": 0,
            "documented": 0, "observable": 0, "used": 0
        }

        for agent in agents:
            try:
                content = agent.read_text(errors="ignore")
                lines = content.splitlines()
                loc = len([l for l in lines if l.strip() and not l.strip().startswith("#")])
                metrics["loc"] += loc

                # Enhanced compliance checks with robust AST parsing
                try:
                    tree = ast.parse(content)
                    
                    # Robust MCP hardening detection: check for MCPShield mixin or @hardened decorator
                    has_mcp_hardening = False
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            # Check for MCPShield in bases
                            if any("MCPShield" in (b.id if isinstance(b, ast.Name) else str(b)) for b in node.bases):
                                has_mcp_hardening = True
                                break
                            # Check for @hardened decorator
                            if any(isinstance(d, ast.Name) and d.id == "hardened" for d in node.decorator_list):
                                has_mcp_hardening = True
                                break
                    
                    if has_mcp_hardening:
                        metrics["hardened"] += 1
                    
                    # Accurate healing invocation: count actual super().heal_repository() calls
                    invocation_count = 0
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Call):
                            # Check for super().heal_repository() pattern
                            if (hasattr(node.func, "attr") and node.func.attr == "heal_repository" and
                                isinstance(node.func.value, ast.Call) and
                                isinstance(node.func.value.func, ast.Name) and
                                node.func.value.func.id == "super"):
                                invocation_count += 1
                    
                    if invocation_count > 0:
                        metrics["healing_invoke"] += 1
                    
                    # Healing capability: check for HealerMixin or healing-related methods
                    has_healing_cap = "HealerMixin" in content or any(
                        isinstance(node, ast.FunctionDef) and node.name in ["run", "validate", "auto_heal"]
                        for node in ast.walk(tree)
                    )
                    if has_healing_cap:
                        metrics["healing_cap"] += 1
                    
                    # Compliance: has heal_repository method defined
                    has_heal_repo = any(
                        isinstance(node, ast.FunctionDef) and node.name == "heal_repository"
                        for node in ast.walk(tree)
                    )
                    if has_heal_repo:
                        metrics["compliant"] += 1
                        
                except SyntaxError:
                    # Graceful error handling: skip syntax errors
                    pass
                except Exception:
                    # Graceful error handling: skip other parsing errors
                    pass
                    
                # Test detection
                has_external_test = (agent.parent / "tests" / f"test_{agent.stem}.py").exists()
                has_self_test = "_run_self_tests" in content or "SubatomicTestingMixin" in content
                has_delegation = "L0DelegationTestingMixin" in content or "_delegate_tests" in content
                has_inline_tests = "def test_" in content or "import pytest" in content
                if has_external_test or has_self_test or has_delegation or has_inline_tests:
                    metrics["tests"] += 1

                # AST-based metrics and sub-atomic violation tracking
                tree = ast.parse(content)
                functions = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]

                # Track sub-atomic violations (high CC methods)
                # FIX: Use max method CC per file (not sum) - rewards decomposition
                file_max_cc = 0
                for func_node in functions:
                    visitor = _CCVisitor()
                    visitor.visit(func_node)
                    cc = visitor.cc
                    
                    if cc > atomic_threshold:
                        file_path = str(agent.relative_to(self.project_root))
                        global_violations.append((cc, file_path, func_node.name))
                    
                    file_max_cc = max(file_max_cc, cc)
                    metrics["max_cc"] = max(metrics["max_cc"], cc)
                
                # Use max method CC for avg calculation (rewards well-decomposed files)
                metrics["cc_sum"] += file_max_cc

                # Typing coverage
                if functions:
                    typed = sum(1 for f in functions if f.returns or any(arg.annotation for arg in f.args.args if arg.arg != "self"))
                    metrics["typed"] += (typed / len(functions)) * 100

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
                    metrics["documented"] += (doc_count / total_targets) * 100

                # Observability (logging)
                if any(imp in content for imp in ["import logging", "from logging", "logger.", "log."]):
                    metrics["observable"] += 100
                    
            except SyntaxError:
                # Don't inflate max_cc with arbitrary high value for syntax errors
                pass
            except Exception:
                pass

        # Usage tracking
        metrics["used"] = sum(1 for a in agents if a.stem in used_stems)
        
        return metrics

    def _update_totals(self, totals: Dict[str, int], metrics: Dict[str, Any]) -> None:
        """Update territory totals with metrics."""
        totals["agents"] += metrics["total"]
        totals["compliant"] += metrics["compliant"]
        totals["hardened"] += metrics["hardened"]
        totals["healing_cap"] += metrics["healing_cap"]
        totals["healing_invoke"] += metrics["healing_invoke"]
        totals["tests"] += metrics["tests"]
        totals["loc"] += metrics["loc"]
        totals["used"] += metrics["used"]
        totals["cc_sum"] += metrics["cc_sum"]
        totals["typed"] += metrics["typed"]
        totals["documented"] += metrics["documented"]
        totals["observable"] += metrics["observable"]
        totals["max_cc"] = max(totals["max_cc"], metrics["max_cc"])

    def _print_territory_row(self, territory_key: str, metrics: Dict[str, Any], priority: str) -> None:
        """Print territory row in markdown format."""
        m = metrics
        total = m["total"]
        if total == 0:
            return
            
        # Calculate percentages
        perc_compliant = round(m["compliant"] / total * 100, 1)
        perc_hardened = round(m["hardened"] / total * 100, 1)
        perc_healing_cap = round(m["healing_cap"] / total * 100, 1)
        perc_healing_invoke = round(m["healing_invoke"] / total * 100, 1)
        perc_tests = round(m["tests"] / total * 100, 1)
        perc_typed = round(m["typed"] / total, 1) if total else 0
        perc_documented = round(m["documented"] / total, 1) if total else 0
        perc_observable = round(m["observable"] / total, 1) if total else 0
        perc_used = round(m["used"] / total * 100, 1) if total else 0
        
        avg_loc = round(m["loc"] / total, 1) if total else 0
        avg_cc = round(m["cc_sum"] / max(total, 1), 1)
        
        # Calculate health and risk
        health = round((perc_tests + perc_healing_invoke + perc_observable) / 3, 1)
        risk_score = 0
        if avg_cc > 10: risk_score += 3
        if perc_tests < 50: risk_score += 3
        if perc_compliant < 80: risk_score += 4
        risk = "HIGH" if risk_score >= 6 else "MED" if risk_score >= 3 else "LOW"
        
        # Calculate criticality
        layer_multiplier = {"L0": 1.3, "L1": 1.2, "L2": 1.1, "L3": 1.0, "L4": 0.9, "L5": 1.4, "unknown": 0.8}.get(priority, 1.0)
        priority_multiplier = {"CRITICAL": 1.5, "HIGH": 1.3, "MEDIUM": 1.1, "LOW": 0.9}.get(priority, 1.0)
        usage_factor = min(40, perc_used * 0.4)
        compliance_gap = max(0, 80 - perc_compliant) * 0.3
        size_factor = min(20, total * 0.5)
        base_criticality = usage_factor + compliance_gap + size_factor
        criticality = round(base_criticality * layer_multiplier * priority_multiplier, 1)
        
        territory_name = territory_key.replace("_", " ").title()[:20]
        row = (
            f"| {territory_name:<42} | {total:5} | {m['compliant']:9} "
            f"| {perc_healing_cap:5}% | {perc_healing_invoke:5}% | {perc_hardened:4}% | {perc_tests:5}% "
            f"| {avg_cc:6} | {perc_typed:5}% | {perc_observable:4}% | {criticality:5.0f} | {health:5.1f} | {risk:4} | {perc_used:4}% | {priority:8} |"
        )
        print(row)

    def _process_unclassified_agents(self, unclassified_agents: List[Path], used_stems: set, totals: Dict[str, int]) -> None:
        """Process unclassified agents and add to totals."""
        if not unclassified_agents:
            return
            
        # Simple metrics for unclassified agents
        metrics = {
            "total": len(unclassified_agents),
            "compliant": 0, "hardened": 0, "healing_cap": 0, "healing_invoke": 0,
            "tests": 0, "loc": 0, "cc_sum": 0, "max_cc": 0, "typed": 0, 
            "documented": 0, "observable": 0, "used": 0
        }
        
        for agent in unclassified_agents:
            try:
                content = agent.read_text(errors="ignore")
                if "def heal_repository(self" in content:
                    metrics["compliant"] += 1
                    metrics["healing_invoke"] += 1
                if "MCPHardenedMixin" in content:
                    metrics["hardened"] += 1
                if "HealerMixin" in content:
                    metrics["healing_cap"] += 1
                if (agent.parent / "tests" / f"test_{agent.stem}.py").exists():
                    metrics["tests"] += 1
                if agent.stem in used_stems:
                    metrics["used"] += 1
            except:
                pass
                
        self._update_totals(totals, metrics)

    def _generate_self_contained_dashboard(
        self, today: str, all_agents: List[Path], classified_paths: set, 
        used_stems: set, path_to_layer: Dict[str, str]
    ) -> None:
        """Generate self-contained interactive dashboard with embedded data and recommendations."""
        # Build dashboard data rows from territories
        dashboard_rows = []
        territory_stats = []
        # Use class attribute for infrastructure territory keys
        
        for territory_key, (layer_filter, priority) in self.territories.items():
            agents = self._get_territory_agents(territory_key, layer_filter, all_agents, path_to_layer)
            if len(agents) == 0:
                continue
            
            # Compute metrics for this territory
            metrics = self._compute_territory_metrics_with_violations(agents, used_stems, 10, [])
            
            # Calculate percentages
            total = metrics["total"]
            perc_compliant = round(metrics["compliant"] / total * 100, 1) if total else 0
            perc_hardened = round(metrics["hardened"] / total * 100, 1) if total else 0
            perc_mcp_capable = round(metrics["mcp_capable"] / total * 100, 1) if total else 0
            perc_healing_cap = round(metrics["healing_cap"] / total * 100, 1) if total else 0
            perc_healing_invoke = round(metrics["healing_invoke"] / total * 100, 1) if total else 0
            perc_tests = round(metrics["tests"] / total * 100, 1) if total else 0
            perc_typed = round(metrics["typed"] / total, 1) if total else 0
            # Documentation %: Average per-agent docstring coverage (granular signal, not threshold-based)
            perc_documented = round(metrics["documented"] / total, 1) if total else 0
            perc_observable = round(metrics["observable"] / total, 1) if total else 0
            perc_used = round(metrics["used"] / total * 100, 1) if total else 0
            
            avg_loc = round(metrics["loc"] / total, 1) if total else 0
            avg_cc = round(metrics["cc_sum"] / max(total, 1), 1)
            
            # Calculate health and risk
            # Health Score v2.1 (Added Typing Weight)
            # Changes from v2:
            # - Added perc_typing @ 10%: reduces runtime errors, strong quality signal
            # - Reduced complexity weight to 5% to keep total 100%
            # Rationale: Empirical evidence shows typed code has ~50-70% fewer bugs
            cc_health_component = max(0, min(100, 100 - (avg_cc * 2)))  # CC of 0 = 100%, CC of 50 = 0%
            # Health Score v2.2 - Fixed weights to sum to 100%
            # Previous v2.1 had weights summing to 105% (bug)
            health = round((
                perc_healing_invoke * 0.25 +   # Proven L5 autonomy in production (25%)
                perc_hardened * 0.18 +         # Critical security control (18%, was 20%)
                perc_tests * 0.18 +            # Regression prevention (18%, was 20%)
                perc_healing_cap * 0.14 +      # Foundational capability (14%, was 15%)
                perc_observable * 0.10 +       # Visibility (10%)
                cc_health_component * 0.05 +   # Maintainability (5%)
                perc_typed * 0.10              # Runtime safety via type hints (10%)
            ), 1)  # Total: 25+18+18+14+10+5+10 = 100%
            
            # Code Quality Score v1.1 (new separate metric)
            # Focuses on static/maintainability quality, independent of operational health
            # Weights: Typing (35%), MCP Capable (25%), Complexity Health (20%), Documentation (20%)
            # Rationale: Decouple modernization and code hygiene from runtime autonomy signals
            code_quality = round((
                perc_typed * 0.35 +              # Runtime safety via type hints (reduced)
                perc_mcp_capable * 0.25 +        # Modernization / external tool integration (reduced)
                cc_health_component * 0.20 +     # Structural maintainability (reduced)
                perc_documented * 0.20           # Self-documenting code (NEW)
            ), 1)
            
            risk_score = 0
            if avg_cc > 10: risk_score += 3
            if perc_tests < 50: risk_score += 3
            if perc_compliant < 80: risk_score += 4
            risk = "HIGH" if risk_score >= 6 else "MED" if risk_score >= 3 else "LOW"
            
            # Calculate criticality
            layer_multiplier = {"L0": 1.3, "L1": 1.2, "L2": 1.1, "L3": 1.0, "L4": 0.9, "L5": 1.4, "unknown": 0.8}.get(priority, 1.0)
            priority_multiplier = {"CRITICAL": 1.5, "HIGH": 1.3, "MEDIUM": 1.1, "LOW": 0.9}.get(priority, 1.0)
            usage_factor = min(40, perc_used * 0.4)
            compliance_gap = max(0, 80 - perc_compliant) * 0.3
            size_factor = min(20, total * 0.5)
            base_criticality = usage_factor + compliance_gap + size_factor
            criticality = round(base_criticality * layer_multiplier * priority_multiplier, 1)
            
            territory_name = territory_key.replace("_", " ").title()
            
            # Count infrastructure agents in this territory (agents in observability paths)
            # These are still counted in their layer but annotated for separate tracking
            infra_agent_count = sum(
                1 for agent in agents 
                if any(pattern in str(agent).replace("\\", "/").lower() 
                       for pattern in self.infrastructure_path_patterns)
            ) if agents else 0
            is_infrastructure = False  # Territory-level flag not used; we track per-agent
            
            # Phase 5: Check base class compliance for this territory
            proper_base_count = 0
            for agent in agents:
                ok, _ = self._check_base_class_compliance(str(agent))
                if ok:
                    proper_base_count += 1
            perc_proper_base = round(proper_base_count / total * 100, 1) if total else 0
            
            # Add to dashboard data (agents array will be added after collection below)
            row = {
                "Territory": territory_name,
                "Total": total,
                "Compliant": metrics["compliant"],
                "Compliance %": perc_compliant,
                "Heal Cap %": perc_healing_cap,
                "Invocation %": perc_healing_invoke,
                "Hardened %": perc_hardened,
                "MCP Capable %": perc_mcp_capable,
                "Test %": perc_tests,
                "Observable %": perc_observable,  # Now a column for all territories
                "Avg CC": avg_cc,
                "Avg LOC": round(avg_loc),  # Medium-Term #2: Average source lines of code
                "Typed %": perc_typed,
                "Documented %": perc_documented,  # NEW: Documentation coverage
                "Proper Base %": perc_proper_base,  # Phase 5: Base class compliance
                "Complexity Health": cc_health_component,  # Inverted CC health (higher = better)
                "Code Quality Score": code_quality,  # Weighted composite quality metric
                "Criticality": criticality,
                "Health": health,
                "Risk": risk,
                "Used %": perc_used,
                "Priority": priority,
                "IsInfrastructure": is_infrastructure,  # Territory-level flag
                "InfraAgentCount": infra_agent_count  # Count of infrastructure agents in this territory
            }
            
            # Collect per-agent diagnostics with detailed metrics
            territory_agents = []
            for agent in agents:
                rel_str = str(agent.relative_to(self.project_root))
                abs_str = agent.resolve().as_posix()
                class_line = 1
                has_mixin = False
                invocation_status = "Unknown"
                has_tests = False
                compliant = False
                agent_typed_pct = 0
                agent_complexity = 0
                obs_logging = obs_metrics = obs_tracing = False
                obs_summary = "Logging: ✗ | Metrics: ✗ | Tracing: ✗"
                has_mcp_capability = False
                has_mcpshield = has_hardened_decorator = False
                mcp_safe_overrides = True
                mcp_summary = "Shield: ✗ | @hardened: ✗ | Safe: ✓"
                typed_init = False
                typed_methods_ratio = return_annotated_ratio = overall_typed_pct = 0.0
                typing_summary = "Init: ✗ | Methods: 0% | Returns: 0%"
                
                try:
                    with open(agent, "r", encoding="utf-8") as f:
                        source = f.read()
                    tree = ast.parse(source, filename=rel_str)
                    
                    # Detect HealerMixin in class bases
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            if class_line == 1:
                                class_line = node.lineno
                            # Check for HealerMixin in bases
                            for base in node.bases:
                                if isinstance(base, ast.Name) and base.id == "HealerMixin":
                                    has_mixin = True
                                elif isinstance(base, ast.Attribute) and base.attr == "HealerMixin":
                                    has_mixin = True
                    
                    # Detect heal_repository invocation
                    invocation_status = "Inherited"  # Default if no override
                    heal_methods = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "heal_repository"]
                    if heal_methods:
                        compliant = True
                        # Check if super().heal_repository() is called
                        has_super_call = False
                        for node in ast.walk(heal_methods[0]):
                            if isinstance(node, ast.Call):
                                if isinstance(node.func, ast.Attribute) and node.func.attr == "heal_repository":
                                    if isinstance(node.func.value, ast.Call):
                                        if isinstance(node.func.value.func, ast.Name) and node.func.value.func.id == "super":
                                            has_super_call = True
                                            break
                        invocation_status = "Yes" if has_super_call else "No (missing super)"

                    # Test presence should be evaluated per-agent (not per-territory)
                    has_tests = bool(self._detect_tests(agent, source))
                    
                    # Observability flags detection
                    obs_logging = False
                    obs_metrics = False
                    obs_tracing = False
                    
                    # Check for logging imports
                    imports_logging = any(
                        (isinstance(node, ast.Import) and any(alias.name == "logging" for alias in node.names)) or
                        (isinstance(node, ast.ImportFrom) and node.module and "logging" in node.module)
                        for node in ast.walk(tree)
                    )
                    imports_obs = any(
                        isinstance(node, ast.ImportFrom) and node.module and "observability" in node.module
                        for node in ast.walk(tree)
                    )
                    
                    # Check for observability call patterns
                    calls_structured = sum(
                        1 for node in ast.walk(tree) 
                        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "structured_log"
                    )
                    calls_metric = sum(
                        1 for node in ast.walk(tree)
                        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "log_metric"
                    )
                    calls_trace = any(
                        isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in ["trace", "start_span"]
                        for node in ast.walk(tree)
                    )
                    imports_otel = any(
                        isinstance(node, ast.ImportFrom) and node.module and "opentelemetry" in node.module
                        for node in ast.walk(tree)
                    )
                    
                    # Set flags
                    obs_logging = imports_logging or imports_obs or calls_structured > 0
                    obs_metrics = calls_metric > 0 or calls_structured > 0  # structured_log often dual-use
                    obs_tracing = calls_trace or imports_otel
                    
                    obs_summary = f"Logging: {'✓' if obs_logging else '✗'} | Metrics: {'✓' if obs_metrics else '✗'} | Tracing: {'✓' if obs_tracing else '✗'}"
                    
                    # MCP Capable detection (uses MCP client to call external MCP servers)
                    has_mcp_capability = False
                    mcp_imports = [
                        "from mcp import",
                        "import mcp",
                        "ClientSession",
                        "mcp.types",
                        "mcp_client",
                        "from mcp.client",
                        "MCPClient"
                    ]
                    for pattern in mcp_imports:
                        if pattern in content:
                            has_mcp_capability = True
                            break
                    
                    # MCP Hardening flags detection (security protection)
                    has_mcpshield = False
                    has_hardened_decorator = False
                    mcp_safe_overrides = True  # Innocent until proven guilty
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            # Check for MCPShield in bases
                            for base in node.bases:
                                if isinstance(base, ast.Name) and base.id == "MCPShield":
                                    has_mcpshield = True
                                elif isinstance(base, ast.Attribute) and base.attr == "MCPShield":
                                    has_mcpshield = True
                            
                            # Check for @hardened decorator on class or methods
                            for decorator in node.decorator_list:
                                if isinstance(decorator, ast.Name) and decorator.id == "hardened":
                                    has_hardened_decorator = True
                                elif isinstance(decorator, ast.Attribute) and decorator.attr == "hardened":
                                    has_hardened_decorator = True
                        
                        if isinstance(node, ast.FunctionDef):
                            # Check for @hardened on methods
                            for decorator in node.decorator_list:
                                if isinstance(decorator, ast.Name) and decorator.id == "hardened":
                                    has_hardened_decorator = True
                                elif isinstance(decorator, ast.Attribute) and decorator.attr == "hardened":
                                    has_hardened_decorator = True
                        
                        # Unsafe patterns detection (direct os/subprocess without guards)
                        if isinstance(node, ast.Call):
                            func = node.func
                            if isinstance(func, ast.Attribute):
                                # Check for unsafe os calls
                                if func.attr in ["system", "popen", "spawn"]:
                                    if isinstance(func.value, ast.Name) and func.value.id == "os":
                                        mcp_safe_overrides = False
                                # Check for unsafe subprocess calls
                                if func.attr in ["run", "Popen", "call", "check_call"]:
                                    if isinstance(func.value, ast.Name) and func.value.id == "subprocess":
                                        mcp_safe_overrides = False
                    
                    mcp_summary = f"Shield: {'✓' if has_mcpshield else '✗'} | @hardened: {'✓' if has_hardened_decorator else '✗'} | Safe: {'✓' if mcp_safe_overrides else '✗'}"
                    
                    # Typing flags detection
                    typed_init = False
                    typed_methods_ratio = 0.0
                    return_annotated_ratio = 0.0
                    total_methods = 0
                    typed_methods = 0
                    annotated_returns = 0
                    
                    class_nodes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
                    if class_nodes:
                        primary_class = class_nodes[0]  # First class = main agent
                        methods = [n for n in primary_class.body if isinstance(n, ast.FunctionDef)]
                        total_methods = len(methods)
                        
                        # Check __init__ typing
                        init_node = next((n for n in methods if n.name == "__init__"), None)
                        if init_node:
                            params_typed = all(arg.annotation is not None for arg in init_node.args.args if arg.arg != "self")
                            return_typed = init_node.returns is not None
                            typed_init = params_typed and return_typed
                        
                        # Check method typing
                        for method in methods:
                            params_typed = all(arg.annotation is not None for arg in method.args.args if arg.arg != "self")
                            if params_typed:
                                typed_methods += 1
                            if method.returns is not None:
                                annotated_returns += 1
                        
                        if total_methods > 0:
                            typed_methods_ratio = typed_methods / total_methods
                            return_annotated_ratio = annotated_returns / total_methods
                    
                    overall_typed_pct = round(perc_typed, 1)
                    typing_summary = f"Init: {'✓' if typed_init else '✗'} | Methods: {typed_methods_ratio:.0%} | Returns: {return_annotated_ratio:.0%}"
                    
                    # Documentation coverage detection
                    agent_documented_pct = self._detect_documentation_coverage(source)
                    
                    # Proxy metrics from territory-level (can be refined per-agent if needed)
                    agent_typed_pct = round(perc_typed, 1)
                    agent_complexity = round(avg_cc, 1)
                    
                except Exception:
                    pass  # Graceful fallback for unparseable files
                
                territory_agents.append({
                    "rel": rel_str,
                    "abs_file": abs_str,
                    "abs_class": f"{abs_str}:{class_line}",
                    "class_line": class_line,
                    "compliant": compliant,
                    "has_mixin": has_mixin,
                    "invocation": invocation_status,
                    "has_tests": has_tests,
                    "typed_pct": agent_typed_pct,
                    "complexity": agent_complexity,
                    "obs_logging": obs_logging,
                    "obs_metrics": obs_metrics,
                    "obs_tracing": obs_tracing,
                    "obs_summary": obs_summary,
                    "has_mcp_capability": has_mcp_capability,
                    "has_mcpshield": has_mcpshield,
                    "has_hardened_decorator": has_hardened_decorator,
                    "mcp_safe_overrides": mcp_safe_overrides,
                    "mcp_summary": mcp_summary,
                    "typed_init": typed_init,
                    "typed_methods_ratio": round(typed_methods_ratio * 100, 1),
                    "return_annotated_ratio": round(return_annotated_ratio * 100, 1),
                    "overall_typed_pct": overall_typed_pct,
                    "typing_summary": typing_summary
                })
            
            # Sort: gap-first (mixin → invocation → observability → MCP → typing → alphabetical)
            territory_agents.sort(key=lambda x: (
                not x["has_mixin"],  # No mixin first (needs adding)
                x["invocation"] != "Yes" and x["invocation"] != "Inherited",  # Missing super() second
                not (x["obs_logging"] or x["obs_metrics"] or x["obs_tracing"]),  # No observability third
                not x["has_mcpshield"],  # No MCP shield fourth
                not x["mcp_safe_overrides"],  # Unsafe patterns fifth
                x["typed_methods_ratio"] < 70,  # Weak typing sixth
                x["rel"]  # Alphabetical for ties
            ))
            
            # Legacy file_links for backward compatibility
            file_links = [{
                "rel": a["rel"],
                "abs_file": a["abs_file"],
                "abs_class": a["abs_class"],
                "class_line": a["class_line"]
            } for a in territory_agents]
            
            # Add agents array to dashboard row
            row["agents"] = territory_agents
            dashboard_rows.append(row)
            
            # Store for recommendations
            territory_stats.append({
                "name": territory_name,
                "key": territory_key,
                "total": total,
                "priority": priority,
                "healing_cap": perc_healing_cap,
                "invocation": perc_healing_invoke,
                "tests": perc_tests,
                "used": perc_used,
                "compliant": perc_compliant,
                "health": health,
                "file_links": file_links
            })
        
        # Add TOTAL row
        if len(dashboard_rows) > 0:
            # Sum infrastructure agents across all territories using InfraAgentCount
            infra_total_agents = sum(r.get("InfraAgentCount", 0) for r in dashboard_rows)
            # List territories that contain infrastructure agents
            infra_territories = [r.get("Territory", "") for r in dashboard_rows if r.get("InfraAgentCount", 0) > 0]

            if len(dashboard_rows) > 0:
                total_agents = sum(r["Total"] for r in dashboard_rows)
                total_compliant = sum(r["Compliant"] for r in dashboard_rows)
                total_perc = round(total_compliant / total_agents * 100, 1) if total_agents else 0
                
                # Compute weighted averages
                total_healing_cap = round(sum(r["Heal Cap %"] * r["Total"] for r in dashboard_rows) / total_agents, 1) if total_agents else 0
                total_healing_invoke = round(sum(r["Invocation %"] * r["Total"] for r in dashboard_rows) / total_agents, 1) if total_agents else 0
                total_hardened = round(sum(r["Hardened %"] * r["Total"] for r in dashboard_rows) / total_agents, 1) if total_agents else 0
                total_mcp_capable = round(sum(r["MCP Capable %"] * r["Total"] for r in dashboard_rows) / total_agents, 1) if total_agents else 0
                total_tests = round(sum(r["Test %"] * r["Total"] for r in dashboard_rows) / total_agents, 1) if total_agents else 0
                total_cc = round(sum(r["Avg CC"] * r["Total"] for r in dashboard_rows) / total_agents, 1) if total_agents else 0
                total_loc = round(sum(r.get("Avg LOC", 0) * r["Total"] for r in dashboard_rows) / total_agents) if total_agents else 0
                total_typed = round(sum(r["Typed %"] * r["Total"] for r in dashboard_rows) / total_agents, 1) if total_agents else 0
                # Portfolio-average documentation coverage (granular signal, not threshold-based)
                total_documented = round(sum(r.get("Documented %", 0) * r["Total"] for r in dashboard_rows) / total_agents, 1) if total_agents else 0
                total_proper_base = round(sum(r.get("Proper Base %", 0) * r["Total"] for r in dashboard_rows) / total_agents, 1) if total_agents else 0
                total_observable = round(sum(r["Observable %"] * r["Total"] for r in dashboard_rows) / total_agents, 1) if total_agents else 0
                total_used = round(sum(r["Used %"] * r["Total"] for r in dashboard_rows) / total_agents, 1) if total_agents else 0
            else:
                infra_total_agents = 0
                infra_territories = []
                total_agents = total_compliant = total_perc = total_healing_cap = total_healing_invoke = 0
                total_hardened = total_mcp_capable = total_tests = total_cc = total_loc = total_typed = total_documented = total_proper_base = total_observable = total_used = 0
            # Calculate total health with new formula (v2.2 with fixed weights)
            total_cc_health = max(0, min(100, 100 - (total_cc * 2)))
            total_health = round((
                total_healing_invoke * 0.25 +   # Proven L5 autonomy in production (25%)
                total_hardened * 0.18 +         # Critical security control (18%)
                total_tests * 0.18 +            # Regression prevention (18%)
                total_healing_cap * 0.14 +      # Foundational capability (14%)
                total_observable * 0.10 +       # Visibility (10%)
                total_cc_health * 0.05 +        # Maintainability (5%)
                total_typed * 0.10              # Runtime safety via type hints (10%)
            ), 1)  # Total: 25+18+18+14+10+5+10 = 100%
            
            # Portfolio-wide Code Quality Score v1.1
            total_code_quality = round((
                total_typed * 0.35 +
                total_mcp_capable * 0.25 +
                total_cc_health * 0.20 +
                total_documented * 0.20
            ), 1)
            
            # Health Score component breakdown for dashboard transparency (v2.2 weights)
            total_breakdown = [
                {"component": "Healing Invocation", "raw": total_healing_invoke, "weight": 0.25, "points": round(total_healing_invoke * 0.25, 1)},
                {"component": "MCP Hardened",       "raw": total_hardened,       "weight": 0.18, "points": round(total_hardened * 0.18, 1)},
                {"component": "Test Coverage",      "raw": total_tests,          "weight": 0.18, "points": round(total_tests * 0.18, 1)},
                {"component": "Healing Capability", "raw": total_healing_cap,    "weight": 0.14, "points": round(total_healing_cap * 0.14, 1)},
                {"component": "Observability",      "raw": total_observable,     "weight": 0.10, "points": round(total_observable * 0.10, 1)},
                {"component": "Typing",             "raw": total_typed,          "weight": 0.10, "points": round(total_typed * 0.10, 1)},
                {"component": "Complexity Health",  "raw": total_cc_health,      "weight": 0.05, "points": round(total_cc_health * 0.05, 1)},
            ]
            
            total_row = {
                "Territory": "TOTAL",
                "Total": total_agents,
                "Compliant": total_compliant,
                "Compliance %": total_perc,
                "Heal Cap %": total_healing_cap,
                "Invocation %": total_healing_invoke,
                "Hardened %": total_hardened,
                "MCP Capable %": total_mcp_capable,
                "Test %": total_tests,
                "Avg CC": total_cc,
                "Avg LOC": total_loc,  # Medium-Term #2: Average source lines of code
                "Typed %": total_typed,
                "Documented %": total_documented,
                "Proper Base %": total_proper_base,  # Phase 5: Base class compliance
                "Observable %": total_observable,
                "Criticality": 75,
                "Health": total_health,
                "Health Breakdown": total_breakdown,
                "Code Quality Score": total_code_quality,
                "Complexity Health": total_cc_health,
                "Risk": "HIGH",
                "Used %": total_used,
                "Priority": "ALL",
                "Infrastructure Total": infra_total_agents,
                "Infrastructure Territories": infra_territories
            }
            dashboard_rows.insert(0, total_row)
        else:
            # No rows - create empty total_row to prevent UnboundLocalError
            total_row = {
                "Territory": "TOTAL",
                "Total": 0,
                "Compliant": 0,
                "Health": 0,
                "Code Quality Score": 0,
                "Invocation %": 0,
                "Hardened %": 0,
                "Test %": 0,
                "Heal Cap %": 0,
                "Observable %": 0,
                "Typed %": 0,
                "Avg CC": 0,
            }
        
        # === Historical Trending: Portfolio + Per-Territory Deltas & Sparklines ===
        history_file = self.project_root / "reports" / "autonomy_history.json"
        current_date = date.today().isoformat()  # "2026-01-03"
        
        # Portfolio snapshot - track key metrics for sparklines
        portfolio_snapshot = {
            "health_score": total_row.get("Health", 0),
            "code_quality_score": total_row.get("Code Quality Score", 0),
            "invocation": total_row.get("Invocation %", 0),
            "mcp_hardened": total_row.get("Hardened %", 0),
            "tests": total_row.get("Test %", 0),
            "heal_cap": total_row.get("Heal Cap %", 0),
            "observable": total_row.get("Observable %", 0),
            "typing": total_row.get("Typed %", 0),
            "complexity": total_row.get("Avg CC", 0),
        }
        
        # Per-territory snapshots
        territory_snapshots = {}
        for row in dashboard_rows:
            if row.get("Territory") != "TOTAL":
                territory_snapshots[row["Territory"]] = {
                    "health_score": row.get("Health", 0),
                    "code_quality_score": row.get("Code Quality Score", 0),
                    "invocation": row.get("Invocation %", 0),
                    "mcp_hardened": row.get("Hardened %", 0),
                    "tests": row.get("Test %", 0),
                    "heal_cap": row.get("Heal Cap %", 0),
                    "observable": row.get("Observable %", 0),
                    "typing": row.get("Typed %", 0),
                    "complexity": row.get("Avg CC", 0),
                }
        
        current_full_snapshot = {
            "date": current_date,
            "portfolio": portfolio_snapshot,
            "territories": territory_snapshots,
        }
        
        # Load history
        history = []
        if history_file.exists():
            try:
                with open(history_file, "r") as f:
                    history = json.load(f)
            except:
                history = []
        
        # Compute trends
        has_previous = len(history) > 0
        total_trends = {"has_previous": has_previous}
        territory_trends = {}
        max_points = 10
        
        if has_previous:
            previous = history[-1]
            prev_portfolio = previous.get("portfolio", {})
            prev_territories = previous.get("territories", {})
            
            # Portfolio deltas
            for key in portfolio_snapshot:
                curr = portfolio_snapshot[key]
                prev = prev_portfolio.get(key, curr)
                delta = round(curr - prev, 1)
                direction = "up" if delta > 0 else "down" if delta < 0 else "flat"
                total_trends[f"{key}_delta"] = delta
                total_trends[f"{key}_direction"] = direction
            
            # Territory deltas
            for row in dashboard_rows:
                if row.get("Territory") != "TOTAL":
                    t_name = row["Territory"]
                    curr_t = territory_snapshots.get(t_name, {})
                    prev_t = prev_territories.get(t_name, {})
                    
                    t_trend = {"has_previous": t_name in prev_territories}
                    if t_trend["has_previous"]:
                        for key in curr_t:
                            c_val = curr_t[key]
                            p_val = prev_t.get(key, c_val)
                            delta = round(c_val - p_val, 1)
                            direction = "up" if delta > 0 else "down" if delta < 0 else "flat"
                            t_trend[f"{key}_delta"] = delta
                            t_trend[f"{key}_direction"] = direction
                    else:
                        for key in curr_t:
                            t_trend[f"{key}_delta"] = None
                            t_trend[f"{key}_direction"] = "flat"
                    
                    territory_trends[t_name] = t_trend
        else:
            # First run: no deltas
            for key in portfolio_snapshot:
                total_trends[f"{key}_delta"] = None
                total_trends[f"{key}_direction"] = "flat"
            
            for row in dashboard_rows:
                if row.get("Territory") != "TOTAL":
                    t_name = row["Territory"]
                    t_trend = {"has_previous": False}
                    for key in territory_snapshots.get(t_name, {}):
                        t_trend[f"{key}_delta"] = None
                        t_trend[f"{key}_direction"] = "flat"
                    territory_trends[t_name] = t_trend
        
        # Collect historical series for sparklines - track all key metrics
        metric_keys = ["health_score", "code_quality_score", "invocation", "mcp_hardened", "tests", "heal_cap", "observable", "typing", "complexity"]
        portfolio_history = {key: [] for key in metric_keys}
        
        for entry in history[-max_points:]:
            # Handle both old format (direct keys) and new format (nested under "portfolio")
            if "portfolio" in entry:
                for key in metric_keys:
                    portfolio_history[key].append(entry["portfolio"].get(key, 0))
            else:
                # Old format compatibility
                for key in metric_keys:
                    portfolio_history[key].append(entry.get(key, 0))
        
        total_sparklines = {key: self._generate_sparkline(portfolio_history[key]) for key in metric_keys}
        
        # Per-territory sparklines
        territory_sparklines = {}
        for row in dashboard_rows:
            if row.get("Territory") != "TOTAL":
                t_name = row["Territory"]
                t_history = {key: [] for key in metric_keys}
                
                for entry in history[-max_points:]:
                    t_data = entry.get("territories", {}).get(t_name)
                    if t_data:
                        for key in metric_keys:
                            t_history[key].append(t_data.get(key, 0))
                
                territory_sparklines[t_name] = {key: self._generate_sparkline(t_history[key]) for key in metric_keys}
        
        # Append & save
        history.append(current_full_snapshot)
        history_file.parent.mkdir(parents=True, exist_ok=True)
        with open(history_file, "w") as f:
            json.dump(history, f, indent=2)
        
        # Add trends and sparklines to total_row for dashboard display
        total_row["trends"] = total_trends
        total_row["sparklines"] = total_sparklines
        
        # === Compute Prioritized Recommendations ===
        # Layer hierarchy multiplier: L5 (Critical) > L4 > L3 > L2 > L1 > L0
        layer_hierarchy_weights = {
            "L5": 10.0,  # L5 Safety - top priority (gravity, validators, guardrails)
            "L4": 5.0,   # L4 State - high priority
            "L3": 3.0,   # L3 Orchestration - medium-high priority
            "L2": 2.0,   # L2 Execution - medium priority
            "L1": 1.5,   # L1 Cognition - lower priority
            "L0": 1.0,   # L0 Maintenance - lowest priority
            "apps": 2.5, # Apps - medium priority
            "observability": 1.2, # Observability - cross-cutting, lower priority
            "utils": 0.8, # Utils - lowest priority
            "tests": 0.5  # Tests - very low priority
        }
        
        priority_weights = {"CRITICAL": 1.8, "HIGH": 1.4, "MEDIUM": 1.0, "LOW": 0.6}
        recommendations = []
        
        for stat in territory_stats:
            # Determine layer from territory name
            territory_lower = stat["name"].lower()
            layer_weight = 1.0
            if territory_lower.startswith("l5"):
                layer_weight = layer_hierarchy_weights["L5"]
            elif territory_lower.startswith("l4"):
                layer_weight = layer_hierarchy_weights["L4"]
            elif territory_lower.startswith("l3"):
                layer_weight = layer_hierarchy_weights["L3"]
            elif territory_lower.startswith("l2"):
                layer_weight = layer_hierarchy_weights["L2"]
            elif territory_lower.startswith("l1"):
                layer_weight = layer_hierarchy_weights["L1"]
            elif territory_lower.startswith("l0"):
                layer_weight = layer_hierarchy_weights["L0"]
            elif "apps" in territory_lower:
                layer_weight = layer_hierarchy_weights["apps"]
            elif "observability" in territory_lower:
                layer_weight = layer_hierarchy_weights["observability"]
            elif "utils" in territory_lower:
                layer_weight = layer_hierarchy_weights["utils"]
            elif "tests" in territory_lower:
                layer_weight = layer_hierarchy_weights["tests"]
            
            healing_cap_gap = max(0, 100 - stat.get("healing_cap", 0))
            healing_invoke_gap = max(0, 100 - stat["invocation"])
            tests_gap = max(0, 100 - stat["tests"])
            
            # Score = gap severity × usage × priority × LAYER HIERARCHY
            score = healing_invoke_gap * tests_gap * (stat["used"] / 100) * priority_weights.get(stat["priority"], 1.0) * layer_weight
            
            # Build impact-first rationale with clear business consequences
            territory_display = stat["name"]
            total_agents = stat["total"]
            usage_pct = stat["used"]
            
            # Calculate actual agent counts for clarity
            agents_with_healing = int(total_agents * stat.get("healing_cap", 0) / 100)
            agents_invoking = int(total_agents * stat["invocation"] / 100)
            agents_with_tests = int(total_agents * stat["tests"] / 100)
            agents_without_invocation = total_agents - agents_invoking
            agents_without_tests = total_agents - agents_with_tests
            
            # Determine primary gap with negative consequence framing
            if healing_invoke_gap > 70:
                # High invocation gap = production errors cascade
                impact = f"⚠️ {agents_without_invocation} of {total_agents} agents fail silently when errors occur → Production issues cascade unhandled, requiring manual intervention and causing downtime"
                action = "Add super().heal_repository() calls to enable autonomous error recovery"
            elif healing_cap_gap > 50:
                # No healing capability = no error recovery
                impact = f"⚠️ {total_agents - agents_with_healing} of {total_agents} agents lack self-repair infrastructure → Errors propagate unchecked, breaking workflows and blocking autonomous operation"
                action = "Add HealerMixin to enable self-repair infrastructure"
            elif tests_gap > 60:
                # Low tests = regression risk
                impact = f"⚠️ {agents_without_tests} of {total_agents} agents have no test coverage → Changes break production silently, regressions go undetected until customer impact"
                action = "Add test coverage to protect against regressions"
            else:
                # Multiple gaps
                impact = f"⚠️ {agents_without_invocation} agents fail without recovery, {agents_without_tests} lack regression protection → System fragility causes frequent outages and manual firefighting"
                action = "Add healing invocation + test coverage for production safety"
            
            # Build clear, actionable rationale
            rationale = f"🎯 {territory_display}: {impact}\n💡 Action: {action}\n📊 Impact: {usage_pct:.0f}% of portfolio uses this {stat['priority'].lower()}-priority territory"
            
            # Simplified gaps display
            gaps = f"{agents_invoking}/{total_agents} self-heal • {agents_with_tests}/{total_agents} tested • {usage_pct:.0f}% portfolio usage"
            
            # Collect file links with class line detection
            file_links = stat.get("file_links", [])
            
            # Targeted guidance based on primary gap
            if healing_invoke_gap > 70:
                guidance = "**Quick Fix (5 min per agent):**\n"
                guidance += "```diff\n"
                guidance += " class YourAgent(..., HealerMixin):\n"
                guidance += "     def execute_task(self, task):\n"
                guidance += "         try:\n"
                guidance += "             result = self._process(task)\n"
                guidance += "+         except Exception as e:\n"
                guidance += "+             super().heal_repository()  # Auto-fix errors\n"
                guidance += "+             raise\n"
                guidance += "```\n"
                guidance += f"**Impact:** Enables {agents_without_invocation} agents to self-repair instead of failing silently."
            elif healing_cap_gap > 50:
                guidance = "**Add Healing Capability:**\n"
                guidance += "```diff\n"
                guidance += "+ from agentic_core.L5_safety.healing import HealerMixin\n"
                guidance += "- class YourAgent(BaseAgent):\n"
                guidance += "+ class YourAgent(BaseAgent, HealerMixin):\n"
                guidance += "      def execute_task(self, task):\n"
                guidance += "+         super().heal_repository()  # Enable self-repair\n"
                guidance += "```\n"
                guidance += f"**Impact:** Gives {total_agents - agents_with_healing} agents autonomous error recovery."
            else:
                guidance = "**Add Test Coverage:**\n"
                guidance += "```python\n"
                guidance += "# tests/test_your_agent.py\n"
                guidance += "def test_healing_on_error():\n"
                guidance += "    agent = YourAgent()\n"
                guidance += "    with pytest.raises(Error):\n"
                guidance += "        agent.execute_task(bad_input)\n"
                guidance += "    assert agent.healing_triggered  # Verify recovery\n"
                guidance += "```\n"
                guidance += f"**Impact:** Protects {agents_without_tests} agents from regressions during healing."
            
            recommendations.append({
                "territory": stat["name"],
                "priority": stat["priority"],
                "total": stat["total"],
                "used": stat["used"],
                "rationale": rationale,
                "gaps": gaps,
                "guidance": guidance,
                "score": round(score, 1),
                "file_links": file_links
            })
        
        # Force unclassified to top if exists
        unclassified = [a for a in all_agents if a not in classified_paths]
        if unclassified:
            # Collect unclassified file links with class line detection
            unclass_files = []
            for a in unclassified:
                rel_str = str(a.relative_to(self.project_root))
                abs_str = a.resolve().as_posix()
                class_line = 1
                try:
                    with open(a, "r", encoding="utf-8") as f:
                        source = f.read()
                    tree = ast.parse(source, filename=rel_str)
                    for node in ast.iter_child_nodes(tree):
                        if isinstance(node, ast.ClassDef):
                            class_line = node.lineno
                            break
                except Exception:
                    pass
                unclass_files.append({
                    "rel": rel_str,
                    "abs_file": abs_str,
                    "abs_class": f"{abs_str}:{class_line}",
                    "class_line": class_line
                })
            unclass_files.sort(key=lambda x: x["rel"])
            
            unclass_rec = {
                "territory": "Unclassified Agents",
                "priority": "Critical",
                "total": len(unclassified),
                "used": 0.0,
                "rationale": "Unclassified agents distort portfolio metrics and block accurate healing coverage",
                "gaps": "Metrics unknown — categorization required",
                "guidance": "1. Review paths in text report subdir breakdown\n"
                           "2. Identify pattern (e.g., 'config/')\n"
                           "3. Add to territories dict:\n"
                           "```python\n"
                           "self.territories['config'] = ('Config Agents', 'Low')\n"
                           "```\n"
                           "4. Re-run --report → unclassified disappears from dashboard",
                "score": 100.0,
                "file_links": unclass_files
            }
            recommendations.append(unclass_rec)
        
        recommendations.sort(key=lambda r: r["score"], reverse=True)
        
        # === Add Holistic Portfolio-Level Recommendations ===
        holistic_recs = []
        
        # Build comprehensive territory metrics for holistic analysis
        territory_counts = {stat["name"]: stat["total"] for stat in territory_stats}
        territory_healing_cap = {stat["name"]: stat.get("healing_cap", 0) for stat in territory_stats}
        territory_invocation = {stat["name"]: stat["invocation"] for stat in territory_stats}
        territory_tests = {stat["name"]: stat["tests"] for stat in territory_stats}
        territory_usage = {stat["name"]: stat["used"] for stat in territory_stats}
        territory_health = {stat["name"]: stat["health"] for stat in territory_stats}
        total_classified = sum(territory_counts.values())
        
        # === 1. PORTFOLIO-WIDE HEALING GAP ANALYSIS ===
        # Calculate overall: X% have toolkits but only Y% use master checklist
        total_with_capability = sum(int(territory_counts[t] * territory_healing_cap[t] / 100) for t in territory_counts)
        total_invoking = sum(int(territory_counts[t] * territory_invocation[t] / 100) for t in territory_counts)
        if total_with_capability > 0 and total_classified > 0:
            cap_pct = (total_with_capability / total_classified) * 100
            invoke_pct = (total_invoking / total_classified) * 100
            healing_gap = cap_pct - invoke_pct
            if healing_gap > 30:  # Significant gap between capability and invocation
                workers_not_using_checklist = total_with_capability - total_invoking
                holistic_recs.append({
                    "territory": "🏭 Factory-Wide Healing Gap",
                    "priority": "Critical",
                    "total": total_classified,
                    "used": 100.0,
                    "rationale": f"⚠️ {total_with_capability} workers have personal toolkits ({cap_pct:.0f}%) but only {total_invoking} consult master safety checklist ({invoke_pct:.0f}%) → {workers_not_using_checklist} workers fix problems in isolation without coordinated factory-wide recovery\n💡 Action: Mandate super().heal_repository() calls in all agents with HealerMixin\n📊 Impact: {workers_not_using_checklist} agents currently fail silently, causing production cascades and manual firefighting",
                    "gaps": f"{invoke_pct:.0f}% using master checklist vs {cap_pct:.0f}% with toolkits • {healing_gap:.0f}% coordination gap",
                    "guidance": f"**Factory-Wide Coordination Fix:**\n1. Audit all {total_with_capability} agents with HealerMixin\n2. Add super().heal_repository() in error handlers\n3. Target: 80%+ invocation rate\n4. Current gap: {workers_not_using_checklist} workers ignoring master checklist",
                    "score": healing_gap * 3,  # High priority
                    "file_links": []
                })
        
        # === 2. TEST COVERAGE DISPARITY ===
        # Find territories with vastly different test coverage
        if territory_tests:
            max_test_territory = max(territory_tests.items(), key=lambda x: x[1])
            min_test_territory = min(territory_tests.items(), key=lambda x: x[1])
            test_disparity = max_test_territory[1] - min_test_territory[1]
            if test_disparity > 50:  # 50%+ disparity
                holistic_recs.append({
                    "territory": "🔬 Quality Control Disparity",
                    "priority": "High",
                    "total": total_classified,
                    "used": 100.0,
                    "rationale": f"⚠️ {max_test_territory[0]} has {max_test_territory[1]:.0f}% quality inspections vs {min_test_territory[0]} with only {min_test_territory[1]:.0f}% → Inconsistent verification standards across factory\n💡 Action: Raise {min_test_territory[0]} test coverage to match factory standards\n📊 Impact: Changes to {min_test_territory[0]} break production silently while {max_test_territory[0]} catches regressions",
                    "gaps": f"{test_disparity:.0f}% test coverage disparity between territories",
                    "guidance": f"**Standardize Quality Control:**\n1. Target minimum 60% test coverage across all territories\n2. Priority: Add tests to {min_test_territory[0]} ({min_test_territory[1]:.0f}% → 60%)\n3. Copy testing patterns from {max_test_territory[0]}\n4. Enforce pre-merge test requirements",
                    "score": test_disparity * 1.5,
                    "file_links": []
                })
        
        # === 3. COMPLEXITY HOTSPOTS ===
        # Find territories with dangerously high complexity
        high_cc_territories = [(stat["name"], stat.get("cc_avg", 0), stat["total"]) 
                               for stat in territory_stats 
                               if stat.get("cc_avg", 0) > 30]
        if not high_cc_territories:
            # Fallback: check dashboard rows for Avg CC
            high_cc_territories = [(r["Territory"], r.get("Avg CC", 0), r["Total"]) 
                                   for r in dashboard_rows 
                                   if r.get("Avg CC", 0) > 30 and r["Territory"] != "TOTAL"]
        for territory, cc, count in high_cc_territories[:2]:  # Top 2 complexity hotspots
            holistic_recs.append({
                "territory": "🔥 Complexity Hotspot",
                "priority": "High",
                "total": count,
                "used": territory_usage.get(territory, 50),
                "rationale": f"⚠️ {territory} has average complexity of {cc:.0f} (target ≤10) → Tangled assembly lines blocking safe modifications\n💡 Action: Refactor high-complexity agents into smaller, focused units\n📊 Impact: High complexity causes bugs during healing, blocks feature additions, increases maintenance cost",
                "gaps": f"Avg CC {cc:.0f} • Target ≤10 • {cc / 10:.1f}x over threshold",
                "guidance": f"**Untangle Assembly Lines:**\n1. Identify agents with CC > 20 in {territory}\n2. Extract helper functions and sub-agents\n3. Apply single-responsibility principle\n4. Target: Reduce average CC to ≤15",
                "score": cc * 2,
                "file_links": []
            })
        
        # === 4. MCP HARDENING GAPS IN CRITICAL TERRITORIES ===
        # Check for 0% hardening in high-usage or L5 territories
        for stat in territory_stats:
            hardened_pct = 0  # Get from dashboard rows
            for row in dashboard_rows:
                if row["Territory"] == stat["name"]:
                    hardened_pct = row.get("Hardened %", 0)
                    break
            if hardened_pct == 0 and (stat["used"] > 70 or stat["name"].startswith("L5")):
                holistic_recs.append({
                    "territory": "🛡️ Safety Harness Gap",
                    "priority": "Critical" if stat["name"].startswith("L5") else "High",
                    "total": stat["total"],
                    "used": stat["used"],
                    "rationale": f"⚠️ {stat['name']} has 0% MCP hardening → {stat['total']} workers lack safety harnesses for dangerous operations\n💡 Action: Add MCPShield mixin and @hardened decorators to all agents\n📊 Impact: Unsafe operations can break factory, no protection against malicious inputs",
                    "gaps": f"0/{stat['total']} agents hardened • {stat['used']:.0f}% portfolio usage",
                    "guidance": f"**Add Safety Harnesses:**\n1. Add MCPShield to class bases\n2. Decorate critical methods with @hardened\n3. Audit for unsafe os/subprocess calls\n4. Target: 100% hardening for L5 Safety",
                    "score": 80 if stat["name"].startswith("L5") else 50,
                    "file_links": []
                })
        
        # === 5. MCP ADOPTION GAP (NEW) ===
        # Analyze MCP capability adoption across portfolio
        total_mcp_capable = sum(r.get("MCP Capable %", 0) * r["Total"] for r in dashboard_rows if r["Territory"] != "TOTAL") / max(total_classified, 1) if total_classified > 0 else 0
        
        if total_mcp_capable < 15:  # Less than 15% portfolio-wide MCP adoption
            territories_without_mcp = [(r["Territory"], r["Total"], r.get("MCP Capable %", 0)) 
                                       for r in dashboard_rows 
                                       if r.get("MCP Capable %", 0) == 0 and r["Territory"] != "TOTAL"]
            
            if len(territories_without_mcp) > 0:
                top_territories = sorted(territories_without_mcp, key=lambda x: x[1], reverse=True)[:3]
                territory_names = ", ".join([t[0] for t in top_territories])
                total_agents_without = sum([t[1] for t in top_territories])
                
                holistic_recs.append({
                    "territory": "🔌 MCP Adoption Gap",
                    "priority": "Medium",
                    "total": total_agents_without,
                    "used": 100.0,
                    "rationale": f"⚠️ Portfolio-wide MCP adoption: {total_mcp_capable:.1f}% → Missing modernization opportunity\n💡 Action: {total_agents_without} agents in {len(top_territories)} territories lack MCP client capabilities\n📊 Impact: Agents cannot leverage external tools (Brave Search, GitHub, Figma) for enhanced functionality",
                    "gaps": f"{total_agents_without} agents without MCP • {len(territories_without_mcp)} territories at 0%",
                    "guidance": f"**MCP Integration Roadmap:**\n1. Add MCP client imports to high-value agents\n2. Connect to relevant MCP servers (search, code, design)\n3. Target territories: {territory_names}\n4. Goal: 30%+ portfolio adoption within 2 quarters",
                    "score": 30,
                    "file_links": []
                })
        
        # === 6. HIGH USAGE + LOW HEALTH CORRELATION ===
        # Find territories that are heavily used but poorly maintained
        for stat in territory_stats:
            if stat["used"] > 70 and stat["health"] < 40:
                risk_score = stat["used"] * (100 - stat["health"]) / 100
                holistic_recs.append({
                    "territory": "⚡ High-Risk Territory",
                    "priority": "Critical",
                    "total": stat["total"],
                    "used": stat["used"],
                    "rationale": f"⚠️ {stat['name']}: {stat['used']:.0f}% portfolio usage but only {stat['health']:.0f}% health → Critical production risk\n💡 Action: Immediate windsurf focus - this territory drives your business but lacks safety infrastructure\n📊 Impact: High-traffic + low-health = frequent production issues, customer-facing outages",
                    "gaps": f"{stat['used']:.0f}% usage • {stat['health']:.0f}% health • {risk_score:.0f} risk score",
                    "guidance": f"**Emergency Stabilization:**\n1. Add healing invocation to all {stat['total']} agents\n2. Add minimum test coverage (60%+)\n3. Enable observability (logging, metrics)\n4. Target: Raise health to 60%+ within 2 sprints",
                    "score": risk_score * 2,
                    "file_links": []
                })
        
        # === 6. OVER-CONCENTRATION (existing) ===
        for territory, count in territory_counts.items():
            if count > 0 and total_classified > 0:
                pct = (count / total_classified) * 100
                if pct > 30:
                    holistic_recs.append({
                        "territory": "📊 Portfolio Imbalance",
                        "priority": "Medium",
                        "total": count,
                        "used": 100.0,
                        "rationale": f"⚠️ {territory} has {count} agents ({pct:.0f}% of portfolio) → Over-concentration increases maintenance burden\n💡 Action: Consolidate overlapping agents or redistribute responsibilities\n📊 Impact: Too many agents in one area = duplication, confusion, higher maintenance cost",
                        "gaps": f"{count} agents in one territory • {pct:.0f}% concentration",
                        "guidance": f"**Consolidation Strategy:**\n1. Review {territory} agents for overlapping functionality\n2. Identify 3-5 core responsibilities\n3. Merge similar agents into unified implementations\n4. Target: Reduce to ~{int(count * 0.7)} agents while maintaining coverage",
                        "score": pct * 1.5,
                        "file_links": []
                    })
        
        # === 7. CRITICAL UNDER-RESOURCING (existing) ===
        critical_territories = {
            "L5 Safety/Gravity": ("gravity enforcement", 2),
            "L5 Safety/Red Teaming": ("adversarial testing", 3),
            "L5 Safety/Validators": ("compliance validation", 15)
        }
        for territory_key, (purpose, min_threshold) in critical_territories.items():
            actual_count = territory_counts.get(territory_key, 0)
            if actual_count < min_threshold:
                gap = min_threshold - actual_count
                holistic_recs.append({
                    "territory": "📉 Under-Resourced Territory",
                    "priority": "Critical",
                    "total": actual_count,
                    "used": 100.0,
                    "rationale": f"⚠️ {territory_key} has only {actual_count} agents → Under-resourced for {purpose}\n💡 Action: Add {gap} specialized agents to strengthen {purpose} coverage\n📊 Impact: Critical safety function understaffed, increasing production risk",
                    "gaps": f"{actual_count}/{min_threshold} agents • {gap} needed",
                    "guidance": f"**Expansion Strategy:**\n1. Identify {gap} key {purpose} scenarios not covered\n2. Create specialized agents for each scenario\n3. Add comprehensive test coverage\n4. Integrate into compliance pipeline",
                    "score": (gap / max(min_threshold, 1)) * 80,
                    "file_links": []
                })
        
        # === 8. L5 SAFETY SUB-TERRITORY BALANCE (existing) ===
        l5_territories = {k: v for k, v in territory_counts.items() if k.startswith("L5 Safety/")}
        if len(l5_territories) > 1:
            l5_counts = list(l5_territories.values())
            max_l5 = max(l5_counts) if l5_counts else 0
            min_l5 = min(l5_counts) if l5_counts else 1
            if max_l5 > min_l5 * 5 and min_l5 > 0:  # 5x imbalance
                max_territory = max(l5_territories.items(), key=lambda x: x[1])
                min_territory = min(l5_territories.items(), key=lambda x: x[1])
                holistic_recs.append({
                    "territory": "⚖️ L5 Safety Imbalance",
                    "priority": "High",
                    "total": sum(l5_counts),
                    "used": 100.0,
                    "rationale": f"⚠️ {max_territory[0]} has {max_territory[1]} agents vs {min_territory[0]} with {min_territory[1]} → Uneven safety coverage\n💡 Action: Rebalance L5 Safety investments across gravity, validators, and red teaming\n📊 Impact: Over-investment in one safety area while others remain vulnerable",
                    "gaps": f"{max_territory[1]} vs {min_territory[1]} agents • {max_territory[1] / max(min_territory[1], 1):.1f}x imbalance",
                    "guidance": f"**Rebalancing Strategy:**\n1. Audit {max_territory[0]} for consolidation opportunities\n2. Strengthen {min_territory[0]} with 2-3 new agents\n3. Ensure each L5 sub-territory has minimum viable coverage\n4. Target ratio: Validators 60%, Gravity 20%, Red Teaming 20%",
                    "score": (max_territory[1] / max(min_territory[1], 1)) * 8,
                    "file_links": []
                })
        
        # === STRATEGIC ARCHITECTURAL RECOMMENDATIONS ===
        
        # === 9. RED TEAMING CAPABILITY GAP ===
        red_team_count = territory_counts.get("L5 Safety/Red Teaming", 0)
        if red_team_count < 5:
            holistic_recs.append({
                "territory": "🎯 Strategic: Red Teaming Capability",
                "priority": "Critical",
                "total": red_team_count,
                "used": 100.0,
                "rationale": f"⚠️ Only {red_team_count} red teaming agents → Critical adversarial testing gap\n💡 Action: Build dedicated red team with 5-8 specialized adversarial agents\n📊 Impact: Without adversarial testing, vulnerabilities in healing/MCP go undetected until production failure",
                "gaps": f"{red_team_count}/5 minimum • Need prompt injection, chaos engineering, boundary testing agents",
                "guidance": "**Red Team Expansion:**\n1. **PromptInjectionAgent** - Tests LLM prompt boundaries\n2. **ChaosEngineeringAgent** - Simulates failures at scale\n3. **BoundaryTestAgent** - Tests edge cases and limits\n4. **AdversarialInputAgent** - Malformed/malicious inputs\n5. **RegressionHunterAgent** - Finds healing regressions",
                "score": 95,  # Very high priority
                "file_links": []
            })
        
        # === 10. VALIDATOR CONSOLIDATION OPPORTUNITY ===
        validator_count = territory_counts.get("L5 Safety/Validators", 0)
        if validator_count > 15:
            holistic_recs.append({
                "territory": "🔧 Strategic: Validator Consolidation",
                "priority": "High",
                "total": validator_count,
                "used": 100.0,
                "rationale": f"⚠️ {validator_count} validation agents → Potential overlap and maintenance burden\n💡 Action: Consolidate into unified validation pipeline with pluggable rules\n📊 Impact: Reduce duplication, simplify compliance flow, lower maintenance cost",
                "gaps": f"{validator_count} validators • Target: 8-12 core validators with composable rules",
                "guidance": "**Consolidation Strategy:**\n1. Audit validators for overlapping responsibilities\n2. Create **UnifiedValidationOrchestrator** with rule plugins\n3. Merge: Location+Hierarchy → StructureValidator\n4. Merge: Naming+KeyMapping → ConventionValidator\n5. Extract shared logic to ValidationRuleEngine",
                "score": 70,
                "file_links": []
            })
        
        # === 11. LAYER ORCHESTRATION ARCHITECTURE ===
        l3_count = sum(v for k, v in territory_counts.items() if k.startswith("L3"))
        if l3_count > 20:
            holistic_recs.append({
                "territory": "🏗️ Strategic: Orchestration Simplification",
                "priority": "High",
                "total": l3_count,
                "used": 100.0,
                "rationale": f"⚠️ {l3_count} L3 orchestration agents → Complex workflow coordination\n💡 Action: Implement centralized workflow engine with declarative pipelines\n📊 Impact: Reduce orchestration complexity, enable visual workflow design, improve debuggability",
                "gaps": f"{l3_count} orchestrators • Target: Unified workflow engine + 10-15 specialized coordinators",
                "guidance": "**Orchestration Redesign:**\n1. Create **WorkflowEngine** with declarative YAML pipelines\n2. Implement **AgentRegistry** for dynamic agent discovery\n3. Add **WorkflowVisualizer** for debugging complex flows\n4. Consolidate redundant MCP routers into single sovereign\n5. Enable hot-reload of workflow definitions",
                "score": 65,
                "file_links": []
            })
        
        # === 12. OBSERVABILITY INFRASTRUCTURE ===
        obs_territories = {k: v for k, v in territory_counts.items() if "observability" in k.lower()}
        total_obs = sum(obs_territories.values()) if obs_territories else 0
        avg_observable_pct = sum(r.get("Observable %", 0) for r in dashboard_rows if r["Territory"] != "TOTAL") / max(len(dashboard_rows) - 1, 1)
        if avg_observable_pct < 50:
            holistic_recs.append({
                "territory": "📊 Strategic: Observability Platform",
                "priority": "High",
                "total": total_obs,
                "used": 100.0,
                "rationale": f"⚠️ {avg_observable_pct:.0f}% avg observability → Blind spots in production monitoring\n💡 Action: Build unified observability platform with auto-instrumentation\n📊 Impact: Enable proactive issue detection, reduce MTTR, support autonomous healing decisions",
                "gaps": f"{avg_observable_pct:.0f}% observable • Target: 80%+ with structured logging, metrics, traces",
                "guidance": "**Observability Platform:**\n1. **AutoInstrumentAgent** - Auto-add logging to all agents\n2. **MetricsAggregatorAgent** - Centralized metrics collection\n3. **TracingCorrelatorAgent** - Distributed trace correlation\n4. **AlertingOrchestratorAgent** - Intelligent alerting rules\n5. Deploy OpenTelemetry SDK across all layers",
                "score": 75,
                "file_links": []
            })
        
        # === 13. STATE MANAGEMENT MATURITY ===
        l4_count = sum(v for k, v in territory_counts.items() if k.startswith("L4"))
        if l4_count < 10:
            holistic_recs.append({
                "territory": "💾 Strategic: State Management",
                "priority": "Medium",
                "total": l4_count,
                "used": 100.0,
                "rationale": f"⚠️ Only {l4_count} L4 state agents → Potential state management gaps\n💡 Action: Build robust state layer with caching, persistence, and recovery\n📊 Impact: Improve system resilience, enable stateful workflows, support long-running operations",
                "gaps": f"{l4_count} state agents • Target: 15-20 for mature state management",
                "guidance": "**State Layer Expansion:**\n1. **StateSnapshotAgent** - Point-in-time state capture\n2. **StateRecoveryAgent** - Rollback to known-good state\n3. **StateSyncAgent** - Multi-node state synchronization\n4. **CacheInvalidationAgent** - Smart cache management\n5. **CheckpointAgent** - Long-running workflow checkpoints",
                "score": 45,
                "file_links": []
            })
        
        # === 14. COGNITIVE LAYER ENHANCEMENT ===
        l1_count = sum(v for k, v in territory_counts.items() if k.startswith("L1"))
        l1_health = sum(territory_health.get(k, 0) for k in territory_counts if k.startswith("L1")) / max(len([k for k in territory_counts if k.startswith("L1")]), 1)
        if l1_count > 5 and l1_health < 40:
            holistic_recs.append({
                "territory": "🧠 Strategic: Cognitive Enhancement",
                "priority": "Medium",
                "total": l1_count,
                "used": 100.0,
                "rationale": f"⚠️ {l1_count} L1 cognition agents at {l1_health:.0f}% health → Under-maintained reasoning layer\n💡 Action: Strengthen cognitive infrastructure for better decision-making\n📊 Impact: Improve agent reasoning quality, reduce hallucinations, enable meta-learning",
                "gaps": f"{l1_count} cognitive agents • {l1_health:.0f}% health • Target: 60%+ health",
                "guidance": "**Cognitive Enhancement:**\n1. **ReasoningChainAgent** - Explicit CoT reasoning\n2. **ContextWindowAgent** - Intelligent context management\n3. **MemoryConsolidationAgent** - Long-term knowledge retention\n4. **UncertaintyQuantifierAgent** - Confidence scoring\n5. Integrate with RAG for knowledge grounding",
                "score": 50,
                "file_links": []
            })
        
        # === 15. CROSS-CUTTING CONCERNS ===
        # Check for missing critical infrastructure agents
        critical_infra = [
            ("CircuitBreakerAgent", "Prevent cascade failures", 85),
            ("RateLimiterAgent", "Protect against resource exhaustion", 80),
            ("RetryOrchestratorAgent", "Intelligent retry with backoff", 75),
            ("FeatureFlagAgent", "Safe rollout of new capabilities", 60),
            ("ConfigHotReloadAgent", "Dynamic configuration updates", 55),
        ]
        
        # Simple check - recommend if we have many agents but likely missing these patterns
        if total_classified > 100:
            holistic_recs.append({
                "territory": "🔌 Strategic: Cross-Cutting Infrastructure",
                "priority": "High",
                "total": 5,
                "used": 100.0,
                "rationale": f"⚠️ {total_classified} agents but missing critical cross-cutting infrastructure\n💡 Action: Add resilience patterns (circuit breakers, rate limiters, feature flags)\n📊 Impact: Prevent cascade failures, enable safe deployments, improve system stability",
                "gaps": "Missing: Circuit breakers, rate limiters, retry logic, feature flags",
                "guidance": "**Infrastructure Agents to Add:**\n1. **CircuitBreakerAgent** - Open circuit on repeated failures\n2. **RateLimiterAgent** - Token bucket rate limiting\n3. **RetryOrchestratorAgent** - Exponential backoff + jitter\n4. **FeatureFlagAgent** - Gradual rollout control\n5. **ConfigHotReloadAgent** - Zero-downtime config updates",
                "score": 72,
                "file_links": []
            })
        
        # Prepend holistic recommendations to top of list
        recommendations = holistic_recs + recommendations
        recommendations.sort(key=lambda r: r["score"], reverse=True)
        
        # For "Top Recommendations" display: ONLY show macro-level (holistic) recommendations
        # Filter to show only strategic/architectural recommendations, not metric-focused ones
        top_recommendations = [r for r in holistic_recs if r["territory"].startswith(("🎯", "🔧", "🏗️", "📊", "💾", "🧠", "🔌"))][:10]
        
        # If not enough macro recommendations, pad with top holistic ones
        if len(top_recommendations) < 3:
            top_recommendations = holistic_recs[:10]
        
        # === Generate Self-Contained HTML ===
        # Template now lives with agent code (package resource)
        template_path = Path(__file__).parent / "dashboard_template.html"
        output_path = self.project_root / "reports" / "autonomy_dashboard.html"
        
        if not template_path.exists():
            print("\n⚠️  Warning: dashboard_template.html not found in validators package.")
            print(f"   Expected location: {template_path}")
            print("   Dashboard generation skipped.")
            return
        
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                template = f.read()
        except Exception as e:
            print(f"\n⚠️  Error reading dashboard template: {e}")
            return
        
        # Calculate gauge metrics from non-cross-cutting rows
        cross_cutting_territories = {"Observability", "Knowledge"}
        gauge_rows = [r for r in dashboard_rows if r["Territory"] not in cross_cutting_territories]
        
        if gauge_rows:
            total_agents = sum(r["Total"] for r in gauge_rows)
            gauge_healing_cap = round(sum(r["Heal Cap %"] * r["Total"] for r in gauge_rows) / total_agents, 1) if total_agents else 0
            gauge_compliance = round(sum(r["Compliant"] for r in gauge_rows) / total_agents * 100, 1) if total_agents else 0
            gauge_health = round(sum(r["Health"] * r["Total"] for r in gauge_rows) / total_agents, 1) if total_agents else 0
        else:
            gauge_healing_cap = gauge_compliance = gauge_health = 0
        
        # Prepare data for embedding
        data_json = json.dumps(dashboard_rows)
        recommendations_json = json.dumps(top_recommendations)
        last_updated = f"Last updated: {today} at {datetime.now().strftime('%H:%M:%S')}"
        gauge_data = json.dumps({
            "healing_cap": gauge_healing_cap,
            "compliance": gauge_compliance,
            "health": gauge_health
        })
        
        # Inject data into template with validation
        html = template.replace('const dashboardData = [];', f'const dashboardData = {data_json};')
        html = html.replace('const recommendationsData = [];', f'const recommendationsData = {recommendations_json};')
        html = html.replace('const lastUpdatedStr = "";', f'const lastUpdatedStr = "{last_updated}";')
        html = html.replace('const gaugeData = {};', f'const gaugeData = {gauge_data};')
        
        # Validate injection succeeded
        if 'const dashboardData = [];' in html or 'const recommendationsData = [];' in html:
            print("\n⚠️  Warning: Data injection may have failed - template variables not found.")
            print("   Dashboard may display with empty data.")
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Atomic write: write to temp file, then rename
        temp_path = output_path.with_suffix('.tmp')
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(html)
            temp_path.replace(output_path)
        except Exception as e:
            print(f"\n⚠️  Error writing dashboard: {e}")
            if temp_path.exists():
                temp_path.unlink()
            return
        
        print(f"\n### ✅ Self-Contained Interactive Dashboard Generated")
        print(f"→ File: {output_path}")
        print(f"→ Open directly in browser (double-click or file:// – no server/CORS issues)")
        print(f"   Includes gauges, risk matrix, healing gaps, observability, complexity, and compliance charts.")
        print(f"   → Executive Dashboard: Large health & compliance gauges + top 3 recommendations")
        print(f"   → Interview Prep: 15 prioritized questions with analogies (top 5 based on weak signals)")
        print(f"   → Prioritized Recommendations: Top {len(top_recommendations)} actions with IDE diff guidance")
        print("   → Clickable file links with line-specific anchors to class definitions")
        print("     VS Code: one-click jump directly to class def → add HealerMixin to bases")
        print("   → Production-quality metrics:")
        print("     - Robust MCP hardening detection (MCPShield mixin + @hardened decorator)")
        print("     - Accurate healing invocation counting (super().heal_repository() calls)")
        print("     - Coverage Score KPI (composite: tests + invocation + observability)")
        print("     - Didactic tooltips with non-technical analogies for interview prep\n")


# Singleton accessor
    def _calculate_global_metrics(self, totals: dict) -> dict:
        """Phase 1: Calculate all global metrics from totals — isolated for low CC."""
        t = totals
        total_perc = round(t["compliant"] / t["agents"] * 100, 1) if t["agents"] else 0
        total_hardened = round(t["hardened"] / t["agents"] * 100, 1) if t["agents"] else 0
        total_healing_cap = round(t["healing_cap"] / t["agents"] * 100, 1) if t["agents"] else 0
        total_healing_invoke = round(t["healing_invoke"] / t["agents"] * 100, 1) if t["agents"] else 0
        total_tests = round(t["tests"] / t["agents"] * 100, 1) if t["agents"] else 0
        overall_avg_cc = round(t["cc_sum"] / t["agents"], 1) if t["agents"] else 0
        total_typed = round(t["typed"] / t["agents"], 1) if t["agents"] else 0
        total_documented = round(t["documented"] / t["agents"], 1) if t["agents"] else 0
        total_observable = round(t["observable"] / t["agents"], 1) if t["agents"] else 0
        total_used = round(t["used"] / t["agents"] * 100, 1) if t["agents"] else 0
        
        overall_health = round((total_tests + total_healing_invoke + total_observable) / 3, 1)
        overall_criticality = min(100, (total_used * 2) + 30)
        
        overall_risk_score = 0
        if overall_avg_cc > 10: overall_risk_score += 3
        if total_tests < 50: overall_risk_score += 3
        if total_perc < 80: overall_risk_score += 4
        overall_risk = "HIGH" if overall_risk_score >= 6 else "MED" if overall_risk_score >= 3 else "LOW"
        
        return {
            "total_perc": total_perc, "total_hardened": total_hardened, "total_healing_cap": total_healing_cap,
            "total_healing_invoke": total_healing_invoke, "total_tests": total_tests, "overall_avg_cc": overall_avg_cc,
            "total_typed": total_typed, "total_documented": total_documented, "total_observable": total_observable,
            "total_used": total_used, "overall_health": overall_health, "overall_criticality": overall_criticality,
            "overall_risk": overall_risk, "agents": t["agents"], "compliant": t["compliant"],
            "healing_cap": t["healing_cap"], "healing_invoke": t["healing_invoke"], "tests": t["tests"]
        }

    def _build_report_header(self, today: str, metrics: dict) -> str:
        """Phase 2: Build markdown header with global metrics — simple string formatting."""
        m = metrics
        md = f"""# Autonomy Compliance Report

**Generated:** {today}  
**Source:** `agent_discovery_full.json` (canonical AST scan)

## 🎯 Executive Summary

**System Health:** {m['overall_health']:.1f}/100 | **Risk Level:** {m['overall_risk']} | **Criticality:** {m['overall_criticality']:.0f}/100

### Key Metrics
- **Total Agents:** {m['agents']}
- **Compliant:** {m['compliant']} ({m['total_perc']}%) {'✅' if m['total_perc'] >= 80 else '⚠️' if m['total_perc'] >= 60 else '❌'}
- **Healing Capabilities:** {m['healing_cap']} ({m['total_healing_cap']}%) {'✅' if m['total_healing_cap'] >= 80 else '⚠️' if m['total_healing_cap'] >= 60 else '❌'}
- **Healing Invocation:** {m['healing_invoke']} ({m['total_healing_invoke']}%) {'✅' if m['total_healing_invoke'] >= 80 else '⚠️' if m['total_healing_invoke'] >= 60 else '❌'}
- **With Tests:** {m['tests']} ({m['total_tests']}%) {'✅' if m['total_tests'] >= 80 else '⚠️' if m['total_tests'] >= 60 else '❌'}
- **Avg Complexity:** {m['overall_avg_cc']} {'✅' if m['overall_avg_cc'] <= 10 else '⚠️' if m['overall_avg_cc'] <= 15 else '❌'}

## 📊 Territory Analysis

**Note:** Table data available in CSV format for better readability in spreadsheet tools.

### High Priority Territories (Criticality > 70)
"""
        return md


_autonomy_guardian: Optional[AutonomyGuardianAgent] = None


def get_autonomy_guardian(project_root: Path) -> AutonomyGuardianAgent:
    """Get singleton instance of AutonomyGuardianAgent."""
    global _autonomy_guardian
    if _autonomy_guardian is None:
        _autonomy_guardian = AutonomyGuardianAgent(project_root)
    return _autonomy_guardian
