from __future__ import annotations
"""
AutonomyGuardianAgent - Sovereign Blueprint/Template (Historical Snapshot)

Pre-2026 reference implementation for scaffolding new guardian agents.
DO NOT edit directly — use as copy-paste starting point only.

Renamed on 2026-01-05 to eliminate filename conflict with active canonical version:
    agentic_core/L5_safety/validators/AutonomyGuardianAgent.py

Original docstring:
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
        # Ordered: L5 first (most critical), then L4-L0 with subcategories for granularity
        self.territories = {
            # L5 Safety - Most Critical (Top Priority)
            "L5_safety/validators": ("L5", "Critical"),
            "L5_safety/guardrails": ("L5", "Critical"),
            "L5_safety/gravity": ("L5", "High"),
            "L5_safety/red_teaming": ("L5", "High"),
            
            # L4 State - Subcategories for granularity
            "L4_state/ValidationContext": ("L4", "High"),  # ValidationContext subfolder (capitalized)
            "L4_state/validation_context": ("L4", "High"),  # validation_context subfolder (lowercase)
            
            # L3 Orchestration - Subcategories
            "L3_orchestration/workflow_engines": ("L3", "High"),
            "L3_orchestration/meta_learning": ("L3", "Medium"),
            
            # L2 Execution - Subcategories
            "L2_execution/action_handlers": ("L2", "High"),
            "L2_execution/mcp": ("L2", "High"),
            
            # L1 Cognition - Subcategories
            "L1_cognition/intent_analysis": ("L1", "Medium"),
            "L1_cognition/thought_engine": ("L1", "Medium"),
            
            # L0 Maintenance
            "L0_maintenance": ("L0", "Medium"),
            
            # Apps - Broken down by domain/engines for higher signal
            "apps_lic/domain": ("apps_lic", "High"),
            "apps_lic/engines": ("apps_lic", "High"),
            "apps_lic/core": ("apps_lic", "Medium"),
            "apps_rg/domain": ("apps_rg", "High"),
            "apps_rg/engines": ("apps_rg", "High"),
            "apps_shared": ("apps_shared", "Medium"),
            
            # Cross-cutting concerns
            "observability/metrics": ("observability", "High"),
            "observability/compliance": ("observability", "High"),
            "observability/telemetry": ("observability", "Medium"),
            
            # Utils - Broken down for higher signal
            "utils/core_extensions": ("utils", "Medium"),
            "utils/general_helpers": ("utils", "Low"),
            
            "tests": ("tests", "Medium"),
        }
    
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
        super().heal_repository(dry_run, execute, depth, max_depth, _call_path)
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
        """Get agents for a specific territory."""
        if territory_key.startswith("L5_safety"):
            # Special handling for L5 subfolders (validators, guardrails, gravity, red_teaming)
            subfolder = territory_key.split("/")[1]
            return [
                p for p in all_agents
                if path_to_layer.get(str(p)) == "L5" and subfolder in str(p).replace("\\", "/")
            ]
        elif territory_key.startswith("L4_state/"):
            # L4 subcategories (ValidationContext or validation_context)
            subfolder = territory_key.split("/")[1]
            return [
                p for p in all_agents
                if path_to_layer.get(str(p)) == "L4" and subfolder in str(p).replace("\\", "/")
            ]
        elif territory_key.startswith("L3_orchestration/"):
            # L3 subcategories
            subfolder = territory_key.split("/")[1]
            return [
                p for p in all_agents
                if path_to_layer.get(str(p)) == "L3" and subfolder in str(p).replace("\\", "/").lower()
            ]
        elif territory_key.startswith("L2_execution/"):
            # L2 subcategories
            subfolder = territory_key.split("/")[1]
            return [
                p for p in all_agents
                if path_to_layer.get(str(p)) == "L2" and subfolder in str(p).replace("\\", "/").lower()
            ]
        elif territory_key.startswith("L1_cognition/"):
            # L1 subcategories
            subfolder = territory_key.split("/")[1]
            return [
                p for p in all_agents
                if path_to_layer.get(str(p)) == "L1" and subfolder in str(p).replace("\\", "/").lower()
            ]
        elif territory_key.startswith("apps_lic/") or territory_key.startswith("apps_rg/"):
            # Apps subcategories (domain, engines, core)
            parts = territory_key.split("/")
            app_name = parts[0]
            subfolder = parts[1] if len(parts) > 1 else None
            if subfolder:
                return [
                    p for p in all_agents
                    if app_name in str(p).replace("\\", "/").lower() and subfolder in str(p).replace("\\", "/").lower()
                ]
            else:
                return [
                    p for p in all_agents
                    if app_name in str(p).replace("\\", "/").lower()
                ]
        elif territory_key.startswith("observability/"):
            # Observability subcategories
            subfolder = territory_key.split("/")[1]
            return [
                p for p in all_agents
                if "observability" in str(p).replace("\\", "/").lower() and subfolder in str(p).replace("\\", "/").lower()
            ]
        elif territory_key.startswith("utils/"):
            # Utils subcategories
            subfolder = territory_key.split("/")[1]
            return [
                p for p in all_agents
                if "utils" in str(p).replace("\\", "/").lower() and subfolder in str(p).replace("\\", "/").lower()
            ]
        elif territory_key in ["observability", "knowledge"]:
            # Path-based filtering for non-layer territories (fallback for observability without subfolder)
            return [
                p for p in all_agents
                if territory_key in str(p).replace("\\", "/").lower()
            ]
        else:
            # Standard layer matching (L0, tests, apps_shared, etc.)
            return [
                p for p in all_agents
                if path_to_layer.get(str(p)) == layer_filter or layer_filter in str(p).replace("\\", "/").lower()
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
            "total": 0, "compliant": 0, "hardened": 0, "healing_cap": 0, "healing_invoke": 0,
            "tests": 0, "loc": 0, "cc_sum": 0, "max_cc": 0, "typed": 0,
            "documented": 0, "observable": 0, "used": 0
        }

    def _initialize_metrics(self, total: int) -> Dict[str, Any]:
        """Base metrics structure."""
        return {
            "total": total,
            "compliant": 0, "hardened": 0, "healing_cap": 0, "healing_invoke": 0,
            "tests": 0, "loc": 0, "cc_sum": 0, "max_cc": 0, "typed": 0,
            "documented": 0, "observable": 0, "used": 0
        }

    def _analyze_single_agent(
        self, agent: Path, atomic_threshold: int, global_violations: List[Tuple[int, str, str]]
    ) -> Dict[str, Any]:
        """Per-agent analysis — isolated AST + checks."""
        file_metrics = {
            "loc": 0, "compliant": 0, "hardened": 0, "healing_cap": 0, "healing_invoke": 0,
            "tests": 0, "cc_sum": 0, "max_cc": 0, "typed": 0, "documented": 0, "observable": 0
        }
        
        try:
            content = agent.read_text(errors="ignore")
            lines = content.splitlines()
            file_metrics["loc"] = len([l for l in lines if l.strip() and not l.strip().startswith("#")])

            # Phase 1a: AST parsing and compliance checks
            try:
                tree = ast.parse(content)
                
                # MCP hardening detection
                file_metrics["hardened"] = self._detect_mcp_hardening(tree)
                
                # Healing invocation detection
                file_metrics["healing_invoke"] = self._detect_healing_invocation(tree)
                
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
                file_metrics["max_cc"] = 999
            
            # Phase 1d: Observability detection
            file_metrics["observable"] = 100 if any(imp in content for imp in ["import logging", "from logging", "logger.", "log."]) else 0
                
        except Exception:
            pass

        return file_metrics

    def _detect_mcp_hardening(self, tree: ast.AST) -> int:
        """Check for MCPShield mixin or @hardened decorator."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if any("MCPShield" in (b.id if isinstance(b, ast.Name) else str(b)) for b in node.bases):
                    return 1
                if any(isinstance(d, ast.Name) and d.id == "hardened" for d in node.decorator_list):
                    return 1
        return 0

    def _detect_healing_invocation(self, tree: ast.AST) -> int:
        """Count actual super().heal_repository() calls."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if (hasattr(node.func, "attr") and node.func.attr == "heal_repository" and
                    isinstance(node.func.value, ast.Call) and
                    isinstance(node.func.value.func, ast.Name) and
                    node.func.value.func.id == "super"):
                    return 1
        return 0

    def _detect_healing_capability(self, tree: ast.AST, content: str) -> int:
        """Check for HealerMixin or healing-related methods."""
        if "HealerMixin" in content:
            return 1
        if any(isinstance(node, ast.FunctionDef) and node.name in ["run", "validate", "auto_heal"] for node in ast.walk(tree)):
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
        metrics["healing_cap"] += file_metrics["healing_cap"]
        metrics["healing_invoke"] += file_metrics["healing_invoke"]
        metrics["tests"] += file_metrics["tests"]
        metrics["loc"] += file_metrics["loc"]
        metrics["cc_sum"] += file_metrics["cc_sum"]
        metrics["max_cc"] = max(metrics["max_cc"], file_metrics["max_cc"])
        metrics["typed"] += file_metrics["typed"]
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
            "compliant": 0, "hardened": 0, "healing_cap": 0, "healing_invoke": 0,
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
                for func_node in functions:
                    visitor = _CCVisitor()
                    visitor.visit(func_node)
                    cc = visitor.cc
                    
                    if cc > atomic_threshold:
                        file_path = str(agent.relative_to(self.project_root))
                        global_violations.append((cc, file_path, func_node.name))
                    
                    metrics["cc_sum"] += cc
                    metrics["max_cc"] = max(metrics["max_cc"], cc)

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
                metrics["max_cc"] = max(metrics["max_cc"], 999)
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
        infrastructure_territories = {"observability", "knowledge"}  # Infrastructure - separate section
        
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
            perc_healing_cap = round(metrics["healing_cap"] / total * 100, 1) if total else 0
            perc_healing_invoke = round(metrics["healing_invoke"] / total * 100, 1) if total else 0
            perc_tests = round(metrics["tests"] / total * 100, 1) if total else 0
            perc_typed = round(metrics["typed"] / total, 1) if total else 0
            perc_documented = round(metrics["documented"] / total, 1) if total else 0
            perc_observable = round(metrics["observable"] / total, 1) if total else 0
            perc_used = round(metrics["used"] / total * 100, 1) if total else 0
            
            avg_loc = round(metrics["loc"] / total, 1) if total else 0
            avg_cc = round(metrics["cc_sum"] / max(total, 1), 1)
            
            # Calculate health and risk
            # New formula: (Heal Cap + Invocation + Tests + Observability + Inverted CC) / 5
            # Inverted CC: normalize to 0-100 scale where lower CC = higher score
            cc_health_component = max(0, min(100, 100 - (avg_cc * 2)))  # CC of 0 = 100%, CC of 50 = 0%
            health = round((perc_healing_cap + perc_healing_invoke + perc_tests + perc_observable + cc_health_component) / 5, 1)
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
            
            # Mark infrastructure territories
            is_infrastructure = territory_key in infrastructure_territories
            
            # Add to dashboard data (agents array will be added after collection below)
            row = {
                "Territory": territory_name,
                "Total": total,
                "Compliant": metrics["compliant"],
                "Compliance %": perc_compliant,
                "Heal Cap %": perc_healing_cap,
                "Invocation %": perc_healing_invoke,
                "Hardened %": perc_hardened,
                "Test %": perc_tests,
                "Observable %": perc_observable,  # Now a column for all territories
                "Avg CC": avg_cc,
                "Typed %": perc_typed,
                "Criticality": criticality,
                "Health": health,
                "Risk": risk,
                "Used %": perc_used,
                "Priority": priority,
                "IsInfrastructure": is_infrastructure  # Flag for UI rendering
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
                agent_typed_pct = 0
                agent_complexity = 0
                
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
                    
                    # MCP Hardening flags detection
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
                    
                    # Proxy metrics from territory-level (can be refined per-agent if needed)
                    has_tests = perc_tests > 0
                    agent_typed_pct = round(perc_typed, 1)
                    agent_complexity = round(avg_cc, 1)
                    
                except Exception:
                    pass  # Graceful fallback for unparseable files
                
                territory_agents.append({
                    "rel": rel_str,
                    "abs_file": abs_str,
                    "abs_class": f"{abs_str}:{class_line}",
                    "class_line": class_line,
                    "has_mixin": has_mixin,
                    "invocation": invocation_status,
                    "has_tests": has_tests,
                    "typed_pct": agent_typed_pct,
                    "complexity": agent_complexity,
                    "obs_logging": obs_logging,
                    "obs_metrics": obs_metrics,
                    "obs_tracing": obs_tracing,
                    "obs_summary": obs_summary,
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
        
        # Add TOTAL row (excluding infrastructure territories)
        if len(dashboard_rows) > 0:
            # Filter out infrastructure territories for TOTAL calculation
            non_infrastructure_rows = [r for r in dashboard_rows if not r.get("IsInfrastructure", False)]
            
            if len(non_cross_cutting_rows) > 0:
                total_agents = sum(r["Total"] for r in non_cross_cutting_rows)
                total_compliant = sum(r["Compliant"] for r in non_cross_cutting_rows)
                total_perc = round(total_compliant / total_agents * 100, 1) if total_agents else 0
                
                # Compute weighted averages
                total_healing_cap = round(sum(r["Heal Cap %"] * r["Total"] for r in non_cross_cutting_rows) / total_agents, 1) if total_agents else 0
                total_healing_invoke = round(sum(r["Invocation %"] * r["Total"] for r in non_cross_cutting_rows) / total_agents, 1) if total_agents else 0
                total_hardened = round(sum(r["Hardened %"] * r["Total"] for r in non_cross_cutting_rows) / total_agents, 1) if total_agents else 0
                total_tests = round(sum(r["Test %"] * r["Total"] for r in non_cross_cutting_rows) / total_agents, 1) if total_agents else 0
                total_cc = round(sum(r["Avg CC"] * r["Total"] for r in non_cross_cutting_rows) / total_agents, 1) if total_agents else 0
                total_typed = round(sum(r["Typed %"] * r["Total"] for r in non_cross_cutting_rows) / total_agents, 1) if total_agents else 0
                total_observable = round(sum(r["Observable %"] * r["Total"] for r in non_cross_cutting_rows) / total_agents, 1) if total_agents else 0
                total_used = round(sum(r["Used %"] * r["Total"] for r in non_cross_cutting_rows) / total_agents, 1) if total_agents else 0
            else:
                total_agents = total_compliant = total_perc = total_healing_cap = total_healing_invoke = 0
                total_hardened = total_tests = total_cc = total_typed = total_observable = total_used = 0
            # Calculate total health with new formula
            total_cc_health = max(0, min(100, 100 - (total_cc * 2)))
            total_health = round((total_healing_cap + total_healing_invoke + total_tests + total_observable + total_cc_health) / 5, 1)
            
            total_row = {
                "Territory": "TOTAL",
                "Total": total_agents,
                "Compliant": total_compliant,
                "Compliance %": total_perc,
                "Heal Cap %": total_healing_cap,
                "Invocation %": total_healing_invoke,
                "Hardened %": total_hardened,
                "Test %": total_tests,
                "Avg CC": total_cc,
                "Typed %": total_typed,
                "Observable %": total_observable,
                "Criticality": 75,
                "Health": total_health,
                "Risk": "HIGH",
                "Used %": total_used,
                "Priority": "ALL"
            }
            dashboard_rows.insert(0, total_row)
        
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
        
        # === 5. HIGH USAGE + LOW HEALTH CORRELATION ===
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
        
        # Prepend holistic recommendations to top of list
        recommendations = holistic_recs + recommendations
        recommendations.sort(key=lambda r: r["score"], reverse=True)
        top_recommendations = recommendations[:10]
        
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
