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
        
        for territory_key, (layer_filter, priority) in self.territories.items():
            agents = self._get_territory_agents(territory_key, layer_filter, all_agents, path_to_layer)
            classified_paths.update(agents)

            if len(agents) == 0:
                continue

            # Compute territory metrics and track violations
            metrics = self._compute_territory_metrics_with_violations(
                agents, used_stems, atomic_threshold, global_sub_atomic_violations
            )
            self._update_totals(totals, metrics)

            if markdown:
                self._print_territory_row(territory_key, metrics, priority)
                
        return classified_paths

    def _get_territory_agents(
        self, territory_key: str, layer_filter: str, 
        all_agents: List[Path], path_to_layer: Dict[str, str]
    ) -> List[Path]:
        """Get agents for a specific territory."""
        if territory_key.startswith("L5_safety"):
            # Special handling for L5 subfolders (validators, guardrails, gravity)
            subfolder = territory_key.split("/")[1]
            return [
                p for p in all_agents
                if path_to_layer.get(str(p)) == "L5" and subfolder in str(p).replace("\\", "/")
            ]
        else:
            # Standard layer matching
            return [
                p for p in all_agents
                if path_to_layer.get(str(p)) == layer_filter
            ]

    def _compute_territory_metrics_with_violations(
        self, agents: List[Path], used_stems: set, 
        atomic_threshold: int, global_violations: List[Tuple[int, str, str]]
    ) -> Dict[str, Any]:
        """Compute territory metrics and track sub-atomic violations."""
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

                # Basic compliance checks
                if "def heal_repository(self" in content:
                    metrics["compliant"] += 1
                    metrics["healing_invoke"] += 1
                if "MCPHardenedMixin" in content:
                    metrics["hardened"] += 1
                if "HealerMixin" in content or any(ind in content for ind in ["run(", "validate_", "auto_"]):
                    metrics["healing_cap"] += 1
                    
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


# Singleton accessor
_autonomy_guardian: Optional[AutonomyGuardianAgent] = None


def get_autonomy_guardian(project_root: Path) -> AutonomyGuardianAgent:
    """Get singleton instance of AutonomyGuardianAgent."""
    global _autonomy_guardian
    if _autonomy_guardian is None:
        _autonomy_guardian = AutonomyGuardianAgent(project_root)
    return _autonomy_guardian
