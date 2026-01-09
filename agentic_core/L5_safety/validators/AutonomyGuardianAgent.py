from __future__ import annotations
"""
Autonomy Guardian Agent - Autonomy Meta-Enforcement (Canon Key 51)
HARDENED: Pure L5 Validation & Enforcement. 
Reporting logic and discovery are delegated to the L6 Modular Engine to ensure Logic Sovereignty.
"""
from datetime import date
from pathlib import Path
from typing import List, Dict, Any, Set, Optional, Tuple
import ast
import logging
import importlib.util

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.timeout_decorator import timeout
from agentic_core.utils.core_extensions.redis_cache_mixin import RedisCacheMixin
from agentic_core.utils.core_extensions.pinecone_vector_mixin import PineconeVectorMixin
from agentic_core.L6_observability.dashboards.data_generator import DashboardDataGenerator
from agentic_core.L6_observability.dashboards.renderer import DashboardRenderer

log = logging.getLogger(__name__)

class AutonomyGuardianAgent(HealerMixin, MCPHardenedMixin, RedisCacheMixin, PineconeVectorMixin):
    """
    Sovereign guardian for agent autonomy enforcement.
    
    Responsibilities:
    1. Validate agents meet Canon Key 51 (heal_repository requirement).
    2. Detect and purge forbidden external runner scripts.
    3. Delegate high-complexity reporting to L6 Observability engine.
    """
    
    _cache_prefix: str = "guardian_compliance"
    _namespace: str = "l5_compliance"
    
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.required_methods = ["heal_repository"]
        self.forbidden_dirs = ["scripts/healing", "scripts/tools", "scripts/runners"]
        self.forbidden_patterns = ["heal", "runner", "launcher", "driver"]
        self.exclude_patterns = ["test_", "example_", "mock_", "stub_", "legacy", "deprecated"]
        
        # Resolve modular discovery engine
        smart_module_path = self.project_root / "scripts" / "smart_discovery.py"
        if not smart_module_path.exists():
            raise FileNotFoundError(f"smart_discovery.py not found at {smart_module_path}")
        spec = importlib.util.spec_from_file_location("smart_discovery", smart_module_path)
        self.smart_discovery = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.smart_discovery)
        
        # Sovereign Territory definitions (Synced with L6 engine)
        self.territories = {
            "L5_safety/base_class": ("L5", "Critical"),
            "L5_safety/validators": ("L5", "Critical"),
            "L5_safety/guardrails": ("L5", "Critical"),
            "L4_state/core": ("L4", "High"),
            "L3_orchestration/core": ("L3", "High"),
            "L2_execution/core": ("L2", "High"),
            "L1_cognition/core": ("L1", "Medium"),
            "L0_maintenance/core": ("L0", "Medium"),
            "observability/metrics": ("observability", "High"),
            "tests": ("tests", "Medium"),
        }

    def validate_agent_autonomy(self, agent_file: Path) -> List[str]:
        """AST-based check for required autonomy methods."""
        violations = []
        try:
            content = agent_file.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(content)
            method_names = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
            for req_method in self.required_methods:
                if req_method not in method_names:
                    violations.append(req_method)
        except Exception:
            violations = list(self.required_methods)
        return violations

    def run(self) -> List[Tuple[Path, str]]:
        """Scan repository for autonomy and script violations."""
        violations = []
        # Runner script check
        for dir_path in self.forbidden_dirs:
            dir_obj = self.project_root / dir_path
            if dir_obj.exists():
                for py_file in dir_obj.rglob("*.py"):
                    if any(p in py_file.stem.lower() for p in self.forbidden_patterns):
                        violations.append((py_file, "FORBIDDEN_RUNNER_SCRIPT"))
        
        # Agent autonomy check
        registry = DashboardDataGenerator(self.project_root, self.territories).load_registry()
        for entry in registry:
            agent_path = self.project_root / entry.get("path", "")
            if agent_path.exists() and not any(p in agent_path.name for p in self.exclude_patterns):
                missing = self.validate_agent_autonomy(agent_path)
                for m in missing:
                    violations.append((agent_path, f"MISSING_METHOD:{m}"))
        return violations

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[Set[str]] = None) -> Dict[str, int]:
        """Meta-healing: Purge forbidden scripts and report missing methods."""
        super().heal_repository(dry_run, execute, depth, max_depth, _call_path)
        actual_execute = execute and not dry_run
        violations = self.run()
        counts = {"scripts_purged": 0, "autonomy_violations": 0, "errors": 0}

        for file_path, reason in violations:
            if "FORBIDDEN_RUNNER_SCRIPT" in reason:
                if actual_execute:
                    try:
                        file_path.unlink()
                        counts["scripts_purged"] += 1
                    except Exception:
                        counts["errors"] += 1
            else:
                counts["autonomy_violations"] += 1
        return counts

    def generate_compliance_report(self, markdown: bool = True, context: dict = None) -> None:
        """Sovereign Orchestrator: Delegates processing to L6 Modular Engine."""
        today = date.today().strftime("%B %d, %Y")
        self.smart_discovery.ensure_fresh_discovery()
        
        # Shared L6 Logic for SSOT
        data_generator = DashboardDataGenerator(self.project_root, self.territories)
        dashboard_rows, total_row = data_generator.generate_full_report_data()
        
        if markdown:
            self._save_modular_markdown_report(today, total_row, dashboard_rows)
        
        self._generate_dashboard_v2_with_rows(today, dashboard_rows, total_row)

    def _save_modular_markdown_report(self, today: str, total_row: Dict[str, Any], dashboard_rows: List[Dict[str, Any]]) -> None:
        """Passive Markdown renderer consuming pre-computed L6 rows."""
        report_path = self.project_root / "agentic_core" / "L6_observability" / "reports" / "autonomy_compliance_report.md"
        md = f"# Autonomy Compliance SSOT Report — {today}\n\n"
        md += f"System Health: {total_row['Health']:.1f}% | Risk: {total_row['Risk']}\n\n"
        md += "| Territory | Total | % Heal Cap | % Heal Inv | % Test | CC | Health |\n|---|---|---|---|---|---|---|\n"
        for row in dashboard_rows:
            md += "| {Territory} | {Total} | {Heal Cap %} | {Heal Invocation %} | {Test %} | {Avg CC} | {Health} |\n".format(**row)
        md += "| **TOTAL** | **{Total}** | **{Heal Cap %}** | **** | **{Test %}** | **{Avg CC}** | **{Health}** |\n".format(**total_row)
        report_path.write_text(md, encoding="utf-8")

    def _generate_dashboard_v2_with_rows(self, today: str, dashboard_rows: List[Dict[str, Any]], total_row: Dict[str, Any]) -> None:
        """L6 Interactive Dashboard generation consuming pre-computed unified rows."""
        renderer = DashboardRenderer(self.project_root)
        recs = renderer.generate_recommendations(total_row, dashboard_rows)
        questions = renderer.generate_interview_questions(total_row, dashboard_rows)
        gauge_data = renderer.generate_gauge_data(total_row)
        html = renderer.render(dashboard_rows, recs, questions, gauge_data, today)
        renderer.save(html)
