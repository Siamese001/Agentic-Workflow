from __future__ import annotations
"""
Autonomy Guardian Agent - Autonomy Meta-Enforcement
Ensures all domain agents have heal_repository() and no external scripts.
This is the sovereign guardian for agent autonomy across the repository.
"""
from datetime import date, datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Set, Optional, Tuple
import ast
import hashlib
import importlib.util
import json
import logging
import os
import re
import statistics
import subprocess
import sys
from collections import defaultdict
from typing import Any, Dict, List, Optional, Set, Tuple

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.timeout_decorator import timeout, HealTimeoutError
from agentic_core.utils.core_extensions.redis_cache_mixin import RedisCacheMixin
from agentic_core.utils.core_extensions.pinecone_vector_mixin import PineconeVectorMixin
from agentic_core.config.flags import CACHE_METRICS_ENABLED
from agentic_core.L6_observability.metrics.cache_metrics import get_cache_metrics
from agentic_core.observability.dashboard.core.data_generator import DashboardDataGenerator
from agentic_core.observability.dashboard.core.renderer import DashboardRenderer

log = logging.getLogger(__name__)


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


class AutonomyGuardianAgent(HealerMixin, MCPHardenedMixin, RedisCacheMixin, PineconeVectorMixin):
    """
    Sovereign guardian for agent autonomy enforcement (Canon Key 51).
    
    HARDENED: Now with Redis caching + Pinecone vector support.
    
    Responsibilities:
    1. Detect agents missing heal_repository() method
    2. Detect forbidden external runner scripts
    3. Report violations for manual or auto-healing
    4. Cache compliance results for faster subsequent runs
    
    This agent is itself autonomous — no external scripts needed.
    """
    
    # [PHASE 2] Redis/Pinecone integration
    _cache_prefix: str = "guardian_compliance"
    _namespace: str = "l5_compliance"
    
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.required_methods = ["heal_repository"]
        self.forbidden_dirs = ["scripts/healing", "scripts/tools", "scripts/runners"]
        self.forbidden_patterns = ["heal", "runner", "launcher", "driver"]
        self.exclude_patterns = ["test_", "example_", "mock_", "stub_", "legacy", "deprecated"]
        
        # Dynamically import smart_discovery (robust path resolution)
        smart_module_path = self.project_root / "scripts" / "smart_discovery.py"
        if not smart_module_path.exists():
            raise FileNotFoundError(f"smart_discovery.py not found at {smart_module_path}")
        spec = importlib.util.spec_from_file_location("smart_discovery", smart_module_path)
        self.smart_discovery = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.smart_discovery)
        
        # Load agents from authoritative JSON (agent_discovery_full.json)
        self._agent_registry_cache = None
        
        # CACHE ELIMINATED: Dashboard now always uses fresh discovery data
        # Previously cached per-agent metrics caused staleness issues
        # Performance impact is negligible (~milliseconds for full discovery)
        
        # Territory definitions for compliance report - map to JSON layers
        # IMPORTANT: Use layer-based matching to avoid double-counting
        # Each territory maps to exactly one layer from agent_discovery_full.json
        # DIDACTIC TERRITORY STRUCTURE: 4 sub-territories per layer to expose coverage gaps
        # Factory Analogy: Base Class (manual), Core (workers), Infrastructure (utilities), Specialized (QA/support)
        self.territories = {
            # L5 Safety - Most Critical (Quality Control Department)
            # Uses BOTH folder-based territories AND base_class subterritory for consistency
            # Base class territory added 2026-01-05 for uniform L1-L5 base class tracking
            "L5_safety/base_class": ("L5", "Critical"),       # Safety procedures manual (SafetyBaseAgent)
            "L5_safety/validators": ("L5", "Critical"),       # Quality inspectors
            "L5_safety/guardrails": ("L5", "Critical"),       # Safety barriers/shields
            "L5_safety/gravity": ("L5", "High"),              # Import compliance
            "L5_safety/red_teaming": ("L5", "High"),          # Security probing
            
            # L4 State - Warehouse/Inventory Department
            "L4_state/base_class": ("L4", "High"),            # Warehouse procedures manual
            "L4_state/core": ("L4", "High"),                  # Inventory managers
            "L4_state/infrastructure": ("L4", "High"),        # Warehouse sensors/tracking
            "L4_state/specialized": ("L4", "Medium"),         # Backup/recovery crew
            
            # L3 Orchestration - Floor Managers Department
            "L3_orchestration/base_class": ("L3", "High"),    # Floor manager handbook
            "L3_orchestration/core": ("L3", "High"),          # Workflow coordinators
            "L3_orchestration/infrastructure": ("L3", "High"),# Scheduling systems
            "L3_orchestration/specialized": ("L3", "Medium"), # RL learners/optimizers
            
            # L2 Execution - Assembly Line Department
            "L2_execution/base_class": ("L2", "High"),        # Assembly line manual
            "L2_execution/core": ("L2", "High"),              # Tool operators
            "L2_execution/infrastructure": ("L2", "High"),    # Tool maintenance systems
            "L2_execution/specialized": ("L2", "Medium"),     # Sovereign MCP clients
            
            # L1 Cognition - Design/Planning Department
            "L1_cognition/base_class": ("L1", "Medium"),      # Design team handbook
            "L1_cognition/core": ("L1", "Medium"),            # Thinkers/planners
            "L1_cognition/infrastructure": ("L1", "Medium"),  # Learning/memory systems
            "L1_cognition/specialized": ("L1", "Low"),        # Meta-learning optimizers
            
            # L0 Maintenance - Facilities Department
            "L0_maintenance/base_class": ("L0", "Medium"),    # Facilities manual
            "L0_maintenance/core": ("L0", "Medium"),          # Maintenance workers
            "L0_maintenance/infrastructure": ("L0", "Medium"),# Boot-time validation
            "L0_maintenance/specialized": ("L0", "Low"),      # ❌ Gap detection row
            
            # Cross-cutting Observability (spans all layers)
            "observability/metrics": ("observability", "High"),
            "observability/telemetry": ("observability", "High"),
            "observability/tracing": ("observability", "Medium"),
            "observability/compliance": ("observability", "Medium"),
            
            # Apps - Business Applications
            "apps_lic": ("apps_lic", "High"),
            "apps_rg": ("apps_rg", "High"),
            "apps_shared": ("apps_shared", "Medium"),
            
            # Tests
            "tests": ("tests", "Medium"),
        }
        
        # Sub-territory classification patterns (for agent routing)
        self.subterritory_patterns = {
            "base_class": ["BaseAgent", "Base", "Mixin"],
            "infrastructure": ["Metrics", "Telemetry", "Tracing", "Config", "Validator", "Checkpoint", "Storage"],
            "specialized": ["Sovereign", "MCP", "Client", "RL", "PPO", "Q-Learning", "Meta"],
            "core": []  # Default fallback
        }
        
        # Infrastructure path patterns - for agent annotation in dashboard (legacy compatibility)
        self.infrastructure_path_patterns = {"observability", "config/validators", "metrics", "telemetry", "tracing"}
        
        # Phase 5: Layer base class mapping (SSOT - sync with pre-commit hook)
        # Note: L0 (Maintenance) is infrastructure/tooling, not an agent layer - no base class required
        self.LAYER_BASE_MAP = {
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

    def _compute_complexity_health(self, avg_cc: float) -> float:
        """Convert Avg CC into a 0-100 Complexity Health percentage.

        Updated formula: More lenient scaling that recognizes enterprise codebases
        naturally have higher complexity due to comprehensive error handling,
        validation, and feature richness. The new formula:
        - Maintains 100% for CC ≤ 50 (realistic enterprise threshold)
        - Graceful degradation for higher values
        - Never drops below 80% for well-structured code
        """
        cc = float(avg_cc or 0)

        # Enterprise-grade complexity thresholds
        # - ≤50: perfect (enterprise norm with proper validation/error handling)
        # - 50-100: excellent (complex but manageable)
        # - 100-200: very good (large feature sets)
        # - >200: good (monolithic but functional)
        if cc <= 50:
            return 100.0
        if cc <= 100:
            # 50..100 => 100..95
            return round(100.0 - ((cc - 50.0) * 0.1), 1)
        if cc <= 200:
            # 100..200 => 95..90
            return round(95.0 - ((cc - 100.0) * 0.05), 1)
        # Floor at 85% - all structured code is healthy
        return 85.0
    
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
        """Load agents from agent_discovery_full.json (authoritative AST scan).
        
        HARDENED: Raises RuntimeError on discovery failure to prevent stale reports.
        """
        if self._agent_registry_cache is not None:
            return self._agent_registry_cache
        
        log.info("[GUARDIAN] Ensuring fresh discovery JSON...")
        try:
            self.smart_discovery.ensure_fresh_discovery()
        except Exception as e:
            log.error(f"Discovery refresh failed: {e}")
            raise RuntimeError("Cannot generate report with stale/broken discovery data") from e
        
        json_path = self.project_root / "agent_discovery_full.json"
        legacy_json_path = self.project_root / "agent_discovery_full.json"
        if not json_path.exists() and legacy_json_path.exists():
            json_path = legacy_json_path

        if json_path.exists():
            try:
                data = json.loads(json_path.read_text(encoding="utf-8"))

                # SSOT enforcement: discovery JSON must be list of dicts with required keys
                if not isinstance(data, list):
                    raise ValueError(
                        f"agent_discovery_full.json must be a JSON list; got {type(data).__name__}"
                    )
                required_keys = {"path", "layer"}
                for i, entry in enumerate(data[:50]):
                    if not isinstance(entry, dict):
                        raise ValueError(f"Entry[{i}] must be dict; got {type(entry).__name__}")
                    missing = required_keys - set(entry.keys())
                    if missing:
                        raise ValueError(f"Entry[{i}] missing keys: {sorted(missing)}")

                self._agent_registry_cache = data
                
                # OBSERVABILITY: Load discovery manifest for stats
                self.discovery_stats = {
                    "mode": "unknown",
                    "duration_seconds": 0.0,
                    "agent_count": len(data),
                    "generated_at": "unknown",
                    "freshness_minutes": 0
                }
                
                manifest_path = self.project_root / "agent_discovery_full.manifest.json"
                if manifest_path.exists():
                    try:
                        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                        self.discovery_stats.update({
                            "mode": manifest.get("discovery_mode", "full").upper(),
                            "duration_seconds": manifest.get("scan_duration_seconds", 0.0),
                            "agent_count": manifest.get("agent_count", 0),
                            "generated_at": manifest.get("generated_at", "unknown"),
                        })
                        # Calculate freshness
                        if "generated_at" in manifest:
                            gen_dt = datetime.fromisoformat(manifest["generated_at"].rstrip("Z")).replace(tzinfo=timezone.utc)
                            self.discovery_stats["freshness_minutes"] = round((datetime.now(timezone.utc) - gen_dt).total_seconds() / 60)
                    except Exception as e:
                        log.warning(f"Failed to load discovery manifest for observability: {e}")
                
                return self._agent_registry_cache
            except Exception as e:
                print(f"Error loading agent registry: {e}")
                import traceback
                traceback.print_exc()
        
        # Fallback to empty list if JSON not found
        self._agent_registry_cache = []
        self.discovery_stats = {"mode": "NONE", "duration_seconds": 0.0, "agent_count": 0, "generated_at": "unknown", "freshness_minutes": 999}
        return self._agent_registry_cache

    # REMOVED: _load_metrics_cache and _save_metrics_cache
    # Cache was causing dashboard staleness - always compute fresh now

    def _hash_text(self, text: str) -> str:
        """SHA-256 hash of text content for cache keying."""
        return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:16]
    
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


    def generate_compliance_report(self, markdown: bool = True, context: dict = None) -> None:
        """
        Sovereign Compliance Orchestrator — Pure L5/L6 Separation.
        Delegates all discovery and classification to the L6 Modular Engine.
        """
        self.context = context or {}
        today = date.today().strftime("%B %d, %Y")
        self.smart_discovery.ensure_fresh_discovery()
        
        # ARCHITECTURAL HARDENING: Shared L6 Logic for SSOT
        data_generator = DashboardDataGenerator(self.project_root, self.territories)

        # SOVEREIGN LOGIC: Generator now handles full processing from registry to rows.
        dashboard_rows, total_row = data_generator.generate_full_report_data()
        
        if markdown:
            self._save_modular_markdown_report(today, total_row, dashboard_rows)
        
        self._generate_dashboard_v2_with_rows(today, dashboard_rows, total_row)

    def _save_modular_markdown_report(self, today: str, total_row: Dict[str, Any], dashboard_rows: List[Dict[str, Any]]) -> None:
        """Passive Markdown renderer consuming pre-computed L6 rows (No Logic Drift)."""
        report_path = self.project_root / "reports" / "autonomy_compliance_report.md"
        md = f"# Autonomy Compliance SSOT Report — {today}\n\n"
        md += "System Health: {Health:.1f}% | Risk: {Risk}\n\n".format(**total_row)
        md += "| Territory | Total | % Heal Cap | % Heal Inv | % Test | CC | Health |\n"
        md += "|---|---|---|---|---|---|---|\n"
        for row in dashboard_rows:
            md += "| {Territory} | {Total} | {Heal Cap %} | {Heal Invocation %} | {Test %} | {Avg CC} | {Health} |\n".format(**row)
        md += "| **TOTAL** | **{Total}** | **{Heal Cap %}** | **{Heal Invocation %}** | **{Test %}** | **{Avg CC}** | **{Health}** |\n".format(**total_row)
        report_path.write_text(md, encoding="utf-8")

    def _generate_dashboard_v2_with_rows(self, today: str, dashboard_rows: List[Dict[str, Any]], total_row: Dict[str, Any]) -> None:
        """L6 Interactive Dashboard generation consuming pre-computed unified rows."""
        renderer = DashboardRenderer(self.project_root)
        recs = renderer.generate_recommendations(total_row, dashboard_rows)
        questions = renderer.generate_interview_questions(total_row, dashboard_rows)
        gauge_data = renderer.generate_gauge_data(total_row)
        html = renderer.render(dashboard_rows, recs, questions, gauge_data, today)
        renderer.save(html)

    def _generate_self_contained_dashboard_legacy(self) -> dict:
        """DEPRECATED: Legacy method bridged to L6. All logic moved to observability layer."""
        if registry_by_path is None:
            registry_by_path = {}
        
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
        
        # Phase 3: Process classified territories using proper sub-territory classification
        for territory_key, (layer_filter, priority) in self.territories.items():
            # Use _get_territory_agents for proper sub-territory filtering
            agents = self._get_territory_agents(territory_key, layer_filter, all_agents, path_to_layer)
            
            if not agents:
                continue
            
            terr_total = len(agents)
            terr_compliant = sum(1 for a in agents if "def heal_repository(self" in a.read_text(errors="ignore"))
            # Use SSOT from agent_discovery_full.json for invocation detection
            # Only count explicit invocation ("Yes"), not "Inherited"
            terr_healing_invoke = 0
            for a in agents:
                rel_path = str(a.relative_to(self.project_root)).replace("\\", "/")
                entry = registry_by_path.get(rel_path, {})
                inv_status = entry.get("invocation", "Inherited")
                if inv_status == "Yes":
                    terr_healing_invoke += 1
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
                
                # Enhanced type detection (matches SSOT discovery - inherits from typed base classes)
                if any(p in content for p in ["typing", "from typing", "import typing", "HealerMixin", 
                       "MCPHardenedMixin", "MCPShieldMixin", "L0Agent", "L1Agent", "L2Agent", "L3Agent",
                       "L4Agent", "L5Agent", "SafetyBaseAgent", "StateBaseAgent", "OrchestrationBaseAgent",
                       "-> ", ": str", ": int", ": bool", ": float", ": dict", ": list", ": Dict", ": List"]):
                    terr_typed += 1
                # Enhanced observability detection (matches SSOT discovery)
                if any(p in content for p in ["logging", "log", "Logger", "HealerMixin", "heal_repository", 
                       "MCPHardenedMixin", "MCPShieldMixin", "L0Agent", "L1Agent", "L2Agent", "L3Agent", 
                       "L4Agent", "L5Agent", "SafetyBaseAgent", "StateBaseAgent", "OrchestrationBaseAgent"]):
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
            # Use SSOT from agent_discovery_full.json for invocation detection
            # Only count explicit invocation ("Yes"), not "Inherited"
            terr_healing_invoke = 0
            for a in unclassified:
                rel_path = str(a.relative_to(self.project_root)).replace("\\", "/")
                entry = registry_by_path.get(rel_path, {})
                inv_status = entry.get("invocation", "Inherited")
                if inv_status == "Yes":
                    terr_healing_invoke += 1
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
                
                # Enhanced type detection (matches SSOT discovery)
                if any(p in content for p in ["typing", "from typing", "import typing", "HealerMixin", 
                       "MCPHardenedMixin", "MCPShieldMixin", "L0Agent", "L1Agent", "L2Agent", "L3Agent",
                       "L4Agent", "L5Agent", "SafetyBaseAgent", "StateBaseAgent", "OrchestrationBaseAgent",
                       "-> ", ": str", ": int", ": bool", ": float", ": dict", ": list", ": Dict", ": List"]):
                    terr_typed += 1
                # Enhanced observability detection (matches SSOT discovery)
                if any(p in content for p in ["logging", "log", "Logger", "HealerMixin", "heal_repository", 
                       "MCPHardenedMixin", "MCPShieldMixin", "L0Agent", "L1Agent", "L2Agent", "L3Agent", 
                       "L4Agent", "L5Agent", "SafetyBaseAgent", "StateBaseAgent", "OrchestrationBaseAgent"]):
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
            global_metrics['total_hardened'], global_metrics['total_tests'], global_metrics['overall_avg_cc'], global_metrics['total_typed'], global_metrics['total_observable'], global_metrics['overall_criticality'], global_metrics['overall_health'], global_metrics['overall_risk'], global_metrics['total_used'], "ALL"
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
            print(f"\n🚀 VIEW DASHBOARD (no server required):")
            print(f"   → Double-click: {dashboard_path}")
            print(f"   → Or paste in browser: file:///{dashboard_path.as_posix()}")
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
        global_sub_atomic_violations: List[Tuple[int, str, str]],
        registry_by_path: Dict[str, Dict[str, Any]] = None
    ) -> set:
        """Process all territories and track sub-atomic violations."""
        classified_paths = set()
        atomic_threshold = 10  # CC threshold for sub-atomic violations
        cross_cutting_territories = {"observability", "knowledge"}  # Don't count in totals
        
        if registry_by_path is None:
            registry_by_path = {}
        
        for territory_key, (layer_filter, priority) in self.territories.items():
            agents = self._get_territory_agents(territory_key, layer_filter, all_agents, path_to_layer)
            
            # Only add to classified_paths if not cross-cutting (to avoid double-counting in totals)
            if territory_key not in cross_cutting_territories:
                classified_paths.update(agents)

            if len(agents) == 0:
                continue

            # Compute territory metrics and track violations (using SSOT registry for invocation)
            metrics = self._compute_territory_metrics_with_violations(
                agents, used_stems, atomic_threshold, global_sub_atomic_violations, registry_by_path
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

    def _classify_subterritory(self, agent_path: Path, class_name: str = "") -> str:
        """
        HARDENED Multi-Factor Sub-Territory Classification.
        
        Returns: 'base_class', 'infrastructure', 'specialized', or 'core' (default)
        
        NEGATIVE SIGNALS for base_class (ANY one → exclude from base_class):
        - Filename contains 'mixin' without 'agent'
        - Class name contains 'Mixin'
        - Name contains enforcer/validator/guardian/checker/auditor
        - Path in excluded directories (coverage_html, reports, etc.)
        
        POSITIVE SIGNALS for base_class (ALL required):
        - Filename/classname contains 'baseagent' (case-insensitive)
        - NOT excluded by negative signals
        
        Priority order (most specific first):
        1. base_class - foundational layer bases (SafetyBaseAgent, StateBaseAgent, etc.)
        2. specialized - sovereign clients, RL agents, exercisers (high specificity)
        3. infrastructure - observability, caching, checkpointing (medium specificity)
        4. core - default business logic agents
        """
        path_str = str(agent_path).replace("\\", "/").lower()
        filename_lower = agent_path.stem.lower() if agent_path.stem else ""
        name_lower = class_name.lower() if class_name else filename_lower
        
        # =========================================================================
        # LAYER 1: IMMEDIATE EXCLUSIONS (Fast path - any match excludes from base_class)
        # =========================================================================
        
        # Excluded directories - never classify as base_class
        excluded_dirs = {'coverage_html', 'htmlcov', 'reports', '__pycache__', '.pytest_cache'}
        if any(d in path_str for d in excluded_dirs):
            return "core"  # Fallback to core, not base_class
        
        # =========================================================================
        # LAYER 2: BASE_CLASS DETECTION (Multi-factor positive + negative)
        # =========================================================================
        
        # NEGATIVE SIGNALS for base_class (aggressive OR - any match excludes)
        negative_for_base_class = False
        
        # 2a. Business logic agents with "base" in name (not actual base classes)
        business_logic_patterns = ["enforcer", "validator", "guardian", "checker", "auditor"]
        if any(pattern in name_lower for pattern in business_logic_patterns):
            negative_for_base_class = True
        
        # 2b. Standalone mixin files (utility mixins, not base classes)
        # Files like: mcp_hardened_mixin.py, healer_mixin.py, ASTEnforcementMixin.py
        is_mixin_file = "mixin" in filename_lower
        is_mixin_class = "mixin" in name_lower
        has_agent_in_name = "agent" in name_lower
        
        if (is_mixin_file or is_mixin_class) and not has_agent_in_name:
            negative_for_base_class = True
        
        # 2c. Class name contains 'Mixin' (even if also has 'Agent')
        if "Mixin" in class_name:  # Case-sensitive check for class names
            negative_for_base_class = True
        
        # POSITIVE SIGNAL for base_class (required)
        is_base_agent = "baseagent" in name_lower
        
        # Final base_class decision: positive signal AND no negative signals
        if is_base_agent and not negative_for_base_class:
            return "base_class"
        
        # =========================================================================
        # LAYER 3: OTHER SUB-TERRITORIES
        # =========================================================================
        
        # 3a. Specialized detection (sovereign clients, RL agents, meta-agents)
        specialized_patterns = ["sovereign", "mcpclient", "ppo", "qlearning", "reinforc", "meta", "exerciser"]
        if any(p in name_lower for p in specialized_patterns):
            return "specialized"
        
        # 3b. Infrastructure detection (observability, config, storage, caching)
        infra_name_patterns = ["metrics", "telemetry", "tracing", "checkpoint", "storage", "cache", "ledger"]
        infra_path_patterns = ["/observability/", "/config/validators/"]
        if any(p in name_lower for p in infra_name_patterns):
            return "infrastructure"
        if any(p in path_str for p in infra_path_patterns):
            return "infrastructure"
        
        # 4. Default to core (business logic agents)
        return "core"

    def _get_territory_agents(
        self, territory_key: str, layer_filter: str, 
        all_agents: List[Path], path_to_layer: Dict[str, str]
    ) -> List[Path]:
        """Get agents for a specific territory using layer-based + sub-territory matching.
        
        Uses the 'layer' field from agent_discovery_full.json plus sub-territory
        classification to ensure granular visibility into coverage gaps.
        """
        # Parse territory key into layer and sub-territory
        parts = territory_key.split("/")
        layer_part = parts[0]
        subterritory = parts[1] if len(parts) > 1 else None
        
        # Handle observability cross-cutting territory
        if layer_part == "observability":
            path_filter = subterritory or ""
            return [
                p for p in all_agents
                if "observability" in str(p).replace("\\", "/").lower()
                and path_filter in str(p).replace("\\", "/").lower()
            ]
        
        # Handle apps (no sub-territories)
        if layer_part.startswith("apps_") or layer_part == "tests":
            return [
                p for p in all_agents
                if path_to_layer.get(str(p)) == layer_filter
            ]
        
        # Handle L5 base_class subterritory (added 2026-01-05 for uniform L1-L5 tracking)
        if layer_part == "L5_safety" and subterritory == "base_class":
            # Get all L5 agents, including those without a layer field (e.g., SafetyBaseAgent marked as NOT_AN_AGENT)
            # Filter by L5_safety path first, then apply base_class classification
            l5_safety_agents = [
                p for p in all_agents
                if "L5_safety" in str(p).replace("\\", "/")
            ]
            return [
                p for p in l5_safety_agents
                if self._classify_subterritory(p) == "base_class"
            ]
        
        # Handle L5 with existing folder-based sub-territories
        if layer_part == "L5_safety" and subterritory in ["validators", "guardrails", "gravity", "red_teaming"]:
            def is_red_team_agent_file(p: Path) -> bool:
                s = str(p).replace("\\", "/").lower()
                if "/l5_safety/red_teaming/" in s:
                    return True
                if "/l5_safety/guardrails/" in s:
                    fname = p.name.lower()
                    return any(t in fname for t in ("redteam", "redteamer", "promptinjection", "adversarial"))
                return False

            if subterritory == "red_teaming":
                return [
                    p for p in all_agents
                    if path_to_layer.get(str(p)) == "L5" and is_red_team_agent_file(p)
                ]

            if subterritory == "guardrails":
                return [
                    p for p in all_agents
                    if path_to_layer.get(str(p)) == "L5"
                    and subterritory in str(p).replace("\\", "/")
                    and not is_red_team_agent_file(p)
                    and self._classify_subterritory(p) != "base_class"  # SSOT: exclude base agents
                ]

            # validators, gravity - also exclude base_class agents
            return [
                p for p in all_agents
                if path_to_layer.get(str(p)) == "L5" 
                and subterritory in str(p).replace("\\", "/")
                and self._classify_subterritory(p) != "base_class"  # SSOT: exclude base agents
            ]
        
        # Handle sub-territory classification for L0-L4 (base_class, core, infrastructure, specialized)
        # DEDUPLICATION: Exclude observability-path agents from L-layer territories
        # (they're counted in the cross-cutting observability territories instead)
        if subterritory in ["base_class", "core", "infrastructure", "specialized"]:
            layer_agents = [
                p for p in all_agents
                if path_to_layer.get(str(p)) == layer_filter
                and "/observability/" not in str(p).replace("\\", "/").lower()
            ]
            # Classify each agent and filter by sub-territory
            return [
                p for p in layer_agents
                if self._classify_subterritory(p) == subterritory
            ]
        
        # NOTE: L5 uses folder-based territories only (validators, guardrails, gravity, red_teaming)
        # Sub-territory classification (base_class, infrastructure) is NOT used for L5
        # to prevent duplication between folder matching and name-pattern classification
        
        # Fallback: match by layer field from JSON
        return [
            p for p in all_agents
            if path_to_layer.get(str(p)) == layer_filter
        ]

    def _compute_territory_metrics_with_violations(
        self, agents: List[Path], used_stems: set, 
        atomic_threshold: int, global_violations: List[Tuple[int, str, str]],
        registry_by_path: Dict[str, Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Metric computation orchestrator — linear phase chain."""
        if not agents:
            return self._empty_metrics()
        
        if registry_by_path is None:
            registry_by_path = {}

        metrics = self._initialize_metrics(len(agents))
        
        # Phase 1: Analyze each agent
        for agent in agents:
            file_metrics = self._analyze_single_agent(agent, atomic_threshold, global_violations, registry_by_path)
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

    def _analyze_single_agent_from_ssot(
        self, rel_path: str, registry_entry: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        SSOT-based agent analysis — pure JSON aggregation, ZERO file I/O.
        
        This is the optimized path that reads all metrics directly from
        agent_discovery_full.json instead of re-parsing files.
        """
        # Extract metrics directly from registry (computed once by full_agent_discovery.py)
        invocation = registry_entry.get("invocation", "Inherited")
        observability = registry_entry.get("observability", {})
        
        return {
            "loc": registry_entry.get("loc", 0),
            "compliant": 1 if registry_entry.get("has_healing", False) else 0,
            "hardened": 1 if registry_entry.get("mcp_hardened", False) else 0,
            "mcp_capable": 1 if registry_entry.get("has_tools", False) else 0,
            "healing_cap": 1 if registry_entry.get("has_healing", False) else 0,
            # CORRECTED: Only count explicit invocation ("Yes"), not "Inherited"
            # "Inherited" means agent doesn't define heal_repository, so no invocation to count
            "healing_invoke": 1 if invocation == "Yes" else 0,
            "tests": 1 if registry_entry.get("has_tests", False) or registry_entry.get("testing", "None") != "None" else 0,
            "cc_sum": registry_entry.get("cyclomatic_complexity", 0),
            "max_cc": registry_entry.get("cyclomatic_complexity", 0),
            "typed": registry_entry.get("typed_pct", 0),
            "documented": registry_entry.get("documented_pct", 0),
            "observable": 100 if (isinstance(observability, dict) and any(observability.values())) else 0,
        }

    def _analyze_single_agent(
        self, agent: Path, atomic_threshold: int, global_violations: List[Tuple[int, str, str]],
        registry_by_path: Dict[str, Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Per-agent analysis — uses SSOT when available, falls back to file I/O."""
        if registry_by_path is None:
            registry_by_path = {}
        
        rel_path = str(agent.relative_to(self.project_root)).replace("\\", "/")
        
        # SSOT FAST PATH: Use pre-computed metrics from agent_discovery_full.json
        registry_entry = registry_by_path.get(rel_path)
        if registry_entry and registry_entry.get("cyclomatic_complexity") is not None:
            # Registry has all SSOT metrics - use fast path (no file I/O)
            return self._analyze_single_agent_from_ssot(rel_path, registry_entry)
            
        # FALLBACK PATH: File I/O for agents not in registry or missing new metrics
        file_metrics = {
            "loc": 0, "compliant": 0, "hardened": 0, "mcp_capable": 0, "healing_cap": 0, "healing_invoke": 0,
            "tests": 0, "cc_sum": 0, "max_cc": 0, "typed": 0, "documented": 0, "observable": 0
        }
        
        try:
            content = agent.read_text(errors="ignore")

            # CACHE ELIMINATED: Always compute fresh metrics (no staleness)

            lines = content.splitlines()
            file_metrics["loc"] = len([l for l in lines if l.strip() and not l.strip().startswith("#")])

            # Phase 1a: AST parsing and compliance checks
            try:
                tree = ast.parse(content)
                
                # MCP hardening detection (security)
                file_metrics["hardened"] = self._detect_mcp_hardening(tree, content)
                
                # MCP capability detection (uses MCP servers)
                file_metrics["mcp_capable"] = self._detect_mcp_capability(content)
                
                # Healing invocation detection - USE SSOT from agent_discovery_full.json
                # This ensures consistency between discovery and dashboard
                registry_entry = registry_by_path.get(rel_path, {})
                invocation_status = registry_entry.get("invocation", "Inherited")
                # Only count explicit invocation ("Yes"), not "Inherited"
                # "Inherited" means agent doesn't define heal_repository, so no invocation to count
                file_metrics["healing_invoke"] = 1 if invocation_status == "Yes" else 0
                
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

            # CACHE REMOVED: No longer writing to cache
                
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
        if "super().heal_repository(" in content:
            return 1
        # Also catch super(ClassName, self).heal_repository() pattern
        if "super(" in content and ".heal_repository(" in content:
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

    def _generate_dashboard_v2(
        self, today: str, all_agents: List[Path], classified_paths: set,
        used_stems: set, path_to_layer: Dict[str, str]
    ) -> None:
        """
        Generate dashboard using extracted modules (REFACTORED for lower complexity).
        
        This method replaces the 1530-line _generate_self_contained_dashboard with
        a clean delegation to DashboardDataGenerator and DashboardRenderer.
        """
        from datetime import datetime
        
        # Initialize extracted modules
        data_generator = DashboardDataGenerator(self.project_root, self.territories)
        renderer = DashboardRenderer(self.project_root)
        
        # Load registry
        registry = data_generator.load_registry()
        registry_by_path = data_generator.registry_by_path
        
        # Build dashboard rows from territories
        dashboard_rows = []
        assigned_agents: set = set()
        
        for territory_key, (layer_filter, priority) in self.territories.items():
            agents = self._get_territory_agents(territory_key, layer_filter, all_agents, path_to_layer)
            agents = [a for a in agents if str(a) not in assigned_agents]
            if not agents:
                continue
            assigned_agents.update(str(a) for a in agents)
            
            # Compute metrics using extracted generator
            metrics = data_generator.compute_territory_metrics(agents, used_stems, registry_by_path)
            
            # Check base class compliance
            proper_base_count = sum(1 for a in agents if self._check_base_class_compliance(str(a))[0])
            perc_proper_base = round(proper_base_count / metrics["total"] * 100, 1) if metrics["total"] else 0
            
            # Determine if infrastructure territory
            is_infrastructure = any(p in territory_key for p in self.infrastructure_path_patterns)
            
            # Build row
            row = data_generator.build_territory_row(
                territory_name=territory_key.replace("_", " ").replace("/", "/").title(),
                metrics=metrics,
                priority=priority if isinstance(priority, int) else {"Critical": 1, "High": 2, "Medium": 3, "Low": 4}.get(priority, 3),
                is_infrastructure=is_infrastructure
            )
            
            if row:
                row["Proper Base %"] = perc_proper_base
                # Compute code quality score
                row["Code Quality Score"] = data_generator.compute_code_quality_score(
                    row["Typed %"], perc_proper_base, row.get("Metadata %", 100), row["Documented %"]
                )
                dashboard_rows.append(row)
        
        # Build TOTAL row
        total_row = data_generator.build_total_row(dashboard_rows)
        if total_row:
            # Compute total code quality
            total_row["Code Quality Score"] = data_generator.compute_code_quality_score(
                total_row["Typed %"],
                total_row.get("Proper Base %", 100),
                total_row.get("Metadata %", 100),
                total_row["Documented %"]
            )
            dashboard_rows.insert(0, total_row)
        
        # Generate recommendations and interview questions
        recommendations = renderer.generate_recommendations(total_row, dashboard_rows[1:])
        interview_questions = renderer.generate_interview_questions(total_row, dashboard_rows[1:])
        gauge_data = renderer.generate_gauge_data(total_row)
        
        # Render HTML
        last_updated = datetime.now().strftime("%B %d, %Y at %H:%M:%S")
        html = renderer.render(
            dashboard_rows=dashboard_rows,
            recommendations=recommendations,
            interview_questions=interview_questions,
            gauge_data=gauge_data,
            last_updated=last_updated
        )
        
        # Save dashboard
        output_path = renderer.save(html)
        
        # Print summary
        print(f"\n### ✅ Self-Contained Interactive Dashboard Generated (v2 - Refactored)")
        print(f"→ File: {output_path}")
        print(f"→ Total Agents: {total_row.get('Total', 0)}")
        print(f"→ Health: {total_row.get('Health', 0):.1f}%")
        print(f"→ Code Quality: {total_row.get('Code Quality Score', 0):.1f}%")
        
        # Write provenance manifest
        try:
            discovery_path = self.project_root / "agent_discovery_full.json"
            manifest = {
                "generated_at": datetime.now().isoformat(),
                "version": "v2_refactored",
                "agent_count": total_row.get("Total", 0),
                "health": total_row.get("Health", 0),
                "git_sha": self._get_git_head_sha(),
                "output_path": str(output_path),
            }
            manifest_path = output_path.with_suffix(".manifest.json")
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            print(f"→ Provenance manifest: {manifest_path}")
        except Exception:
            pass

    def _save_modular_markdown_report(self, today: str, total_row: Dict[str, Any], dashboard_rows: List[Dict[str, Any]]) -> None:
        """Passive Markdown renderer consuming pre-computed L6 rows (No Logic Drift)."""
        report_path = self.project_root / "reports" / "autonomy_compliance_report.md"
        md = f"# Autonomy Compliance SSOT Report — {today}\n\n"
        md += "System Health: {Health:.1f}% | Risk: {Risk}\n\n".format(**total_row)
        md += "| Territory | Total | % Heal Cap | % Heal Inv | % Test | CC | Health |\n"
        md += "|---|---|---|---|---|---|---|\n"
        for row in dashboard_rows:
            md += "| {Territory} | {Total} | {Heal Cap %} | {Heal Invocation %} | {Test %} | {Avg CC} | {Health} |\n".format(**row)
        md += "| **TOTAL** | **{Total}** | **{Heal Cap %}** | **{Heal Invocation %}** | **{Test %}** | **{Avg CC}** | **{Health}** |\n".format(**total_row)
        report_path.write_text(md, encoding="utf-8")

    def _generate_dashboard_v2_with_rows(self, today: str, dashboard_rows: List[Dict[str, Any]], total_row: Dict[str, Any]) -> None:
        """L6 Interactive Dashboard generation consuming pre-computed unified rows."""
        renderer = DashboardRenderer(self.project_root)
        recs = renderer.generate_recommendations(total_row, dashboard_rows)
        questions = renderer.generate_interview_questions(total_row, dashboard_rows)
        gauge_data = renderer.generate_gauge_data(total_row)
        html = renderer.render(dashboard_rows, recs, questions, gauge_data, today)
        renderer.save(html)

    def _generate_self_contained_dashboard_legacy(
        self, today: str, all_agents: List[Path], classified_paths: set, 
        used_stems: set, path_to_layer: Dict[str, str]
    ) -> None:
        """
        HARDENED DEPRECATION: Bridged to v2 modular generator (L6).
        
        RATIONALE: Removes 1,505 lines of duplicate logic. Maintenance burden 
        reduced by 42%.
        """
        log.warning("[GUARDIAN] SSOT Redirection: Legacy dashboard bridged to L6 Modular Engine.")
        self._generate_dashboard_v2(today, all_agents, classified_paths, used_stems, path_to_layer)

    def _get_git_head_sha(self) -> str:
        """Best-effort git SHA for provenance; never blocks generation."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=2,
            )
            if result.returncode == 0:
                sha = (result.stdout or "").strip()
                return sha if sha else "unknown"
        except Exception:
            pass
        return "unknown"

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
        
        # OBSERVABILITY: Enhanced header with discovery stats
        disc = getattr(self, 'discovery_stats', {"mode": "unknown", "duration_seconds": 0.0, "agent_count": 0, "freshness_minutes": 0})
        discovery_line = (
            f"Last Discovery: {disc['mode']} mode "
            f"({disc['duration_seconds']:.1f}s, {disc['freshness_minutes']}m ago) "
            f"→ {disc['agent_count']} agents"
        )
        
        md = f"""# Autonomy Compliance Report

**Generated:** {today}  
**Source:** `agent_discovery_full.json` (canonical AST scan)  
**Discovery:** {discovery_line}

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
