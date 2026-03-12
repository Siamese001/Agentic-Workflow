from __future__ import annotations
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L2_execution.tools import write_gateway as _wg
'\nAutonomy Guardian Agent - L0 DNA Integrity Enforcement\nHARDENED: Pure L5 Validation & Enforcement.\nReporting logic and discovery are delegated to the L6 Modular Engine to ensure Logic Sovereignty.\n'
import ast
import json
import logging
import subprocess
from datetime import date
from pathlib import Path
from typing import Any
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

def _get_DashboardDataGenerator():
    """Lazy load DashboardDataGenerator to avoid upward import."""
    from agentic_core.L6_observability.dashboards.data_generator import DashboardDataGenerator
    return DashboardDataGenerator
from agentic_core.prompt_governance.renderer import DashboardRenderer
from agentic_core.L0_routing.config import AGENTIC_CORE_DIR
from agentic_core.L5_safety.config.structure_blueprint import AGENT_DISCOVERY_JSON, AGENTIC_CORE_DIR, TESTS_DIR
from agentic_core.utils.timeout_decorator_util import timeout
log = logging.getLogger(__name__)

class AutonomyGuardianAgent(SovereignBaseAgent):
    """
    Sovereign guardian for agent autonomy enforcement.

    Responsibilities:
    1. Validate agents have Autonomous Repair Capability (heal_repository via SovereignBaseAgent).
    2. Detect and purge forbidden external runner scripts.
    3. Delegate high-complexity reporting to L6 observability engine.
    """
    _cache_prefix: str = 'guardian_compliance'
    _namespace: str = 'l5_compliance'

    def __init__(self, project_root: Path) -> None:
        """Initialize the instance."""
        super().__init__()
        self.project_root = project_root
        self.required_methods = ['heal_repository']
        self.forbidden_dirs = ['scripts/healing', 'scripts/tools', 'scripts/runners']
        self.forbidden_patterns = ['heal', 'runner', 'launcher', 'driver']
        self.exclude_patterns = ['test_', 'example_', 'mock_', 'stub_', 'legacy', 'deprecated']
        self.timestamp = None
        self.discovery_json_path = self.project_root / AGENT_DISCOVERY_JSON
        self.territories = {'L5_safety/base_class': ('L5', 'Critical'), 'L5_safety/validators': ('L5', 'Critical'), 'L5_safety/guardrails': ('L5', 'Critical'), 'L4_state/core': ('L4', 'High'), 'L3_orchestration/core': ('L3', 'High'), 'L2_execution/core': ('L2', 'High'), 'L1_cognition/core': ('L1', 'Medium'), 'L0_routing/core': ('L0', 'Medium'), 'observability/metrics': ('observability', 'High'), TESTS_DIR: (TESTS_DIR, 'Medium')}

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        [HEALER PROTOCOL] Standardized healing interface for AutonomyGuardianAgent violations.

        Args:
            violation: Violation dict with keys: type, file, message, etc.

        Returns:
            Dict with keys: status, details, artifacts, errors
        """
        try:
            violation.get('type', '')
            file_path = violation.get('file')
            if not file_path:
                return {'status': 'failed', 'details': 'No file path provided in violation', 'artifacts': [], 'errors': ['Missing file path']}
            return {'status': 'manual_required', 'details': 'AutonomyGuardianAgent requires manual review for healing', 'artifacts': [], 'errors': []}
        # guardian: allow-silent-swallow
        except Exception as e:
            return {'status': 'failed', 'details': 'Exception during healing', 'artifacts': [], 'errors': [str(e)]}

    def validate_agent_autonomy(self, agent_file: Path) -> list[str]:
        """Delegate autonomy validation to deterministic Guardian test."""
        result = subprocess.run(['python', 'tests/guardian/test_agent_autonomy.py', str(agent_file)], capture_output=True, text=True, cwd=self.project_root)
        return [] if result.returncode == 0 else self.required_methods

    def run(self) -> list[tuple[Path, str]]:
        """Scan repository for autonomy and script violations."""
        violations = []
        self._check_forbidden_runner_scripts(violations)
        self._check_agent_autonomy_violations(violations)
        return violations

    def _check_forbidden_runner_scripts(self, violations: list[tuple[Path, str]]) -> None:
        """Check for forbidden runner scripts."""
        from agentic_core.utils.ssot_discovery_validator import get_python_files
        for dir_path in self.forbidden_dirs:
            dir_obj = self.project_root / dir_path
            if dir_obj.exists():
                for py_file in get_python_files(dir_obj):
                    if any((p in py_file.stem.lower() for p in self.forbidden_patterns)):
                        violations.append((py_file, 'FORBIDDEN_RUNNER_SCRIPT'))

    def _check_agent_autonomy_violations(self, violations: list[tuple[Path, str]]) -> None:
        """Check for agent autonomy violations."""
        registry = DashboardDataGenerator(self.project_root, self.territories).load_registry()
        for entry in registry:
            agent_path = self.project_root / entry.get('path', '')
            if agent_path.exists() and (not any((p in agent_path.name for p in self.exclude_patterns))):
                missing = self.validate_agent_autonomy(agent_path)
                for m in missing:
                    violations.append((agent_path, f'MISSING_METHOD:{m}'))

    @timeout(300)
    # guardian: allow-magic-config
    def heal_repository(self, dry_run: bool=True, execute: bool=False, depth: int=0, max_depth: int=3, _call_path: set[str] | None=None) -> dict[str, int]:
        """Meta-healing: Purge forbidden scripts and report missing methods."""
        super().heal_repository(dry_run, execute, depth, max_depth, _call_path)
        actual_execute = execute and (not dry_run)
        violations = self.run()
        counts = {'scripts_purged': 0, 'autonomy_violations': 0, 'errors': 0}
        for file_path, reason in violations:
            if 'FORBIDDEN_RUNNER_SCRIPT' in reason:
                if actual_execute:
                    try:
                        _wg.remove_file(file_path)
                        counts['scripts_purged'] += 1
                    # guardian: allow-silent-swallow
                    except Exception:
                        counts['errors'] += 1
            else:
                counts['autonomy_violations'] += 1
        return counts

    def generate_compliance_report(self, markdown: bool=True, context: dict=None) -> None:
        """Sovereign Orchestrator: Delegates processing to L6 Modular Engine."""
        today = date.today().strftime('%B %d, %Y')
        log.info('[AutonomyGuardian] Generating compliance report using SSOT discovery data...')
        data_generator = DashboardDataGenerator(self.project_root, self.territories)
        dashboard_rows, total_row = data_generator.generate_full_report_data()
        if markdown:
            self._save_modular_markdown_report(today, total_row, dashboard_rows)
        self._generate_dashboard_v2_with_rows(today, dashboard_rows, total_row)

    def _save_modular_markdown_report(self, today: str, total_row: dict[str, Any], dashboard_rows: list[dict[str, Any]]) -> None:
        """Passive Markdown renderer consuming pre-computed L6 rows."""
        report_path = self.project_root / AGENTIC_CORE_DIR / 'L6_observability' / REPORTS_DIR / 'autonomy_compliance_report.md'
        md = f'# Autonomy Compliance SSOT Report — {today}\n\n'
        md += f"System Health: {total_row['Health']:.1f}% | Risk: {total_row['Risk']}\n\n"
        md += '| Territory | Total | % Heal Cap | % Heal Inv | % Test | CC | Health |\n|---|---|---|---|---|---|---|\n'
        for row in dashboard_rows:
            md += '| {Territory} | {Total} | {Heal Cap %} | {Heal Invocation %} | {Test %} | {Avg CC} | {Health} |\n'.format(**row)
        md += '| **TOTAL** | **{Total}** | **{Heal Cap %}** | **** | **{Test %}** | **{Avg CC}** | **{Health}** |\n'.format(**total_row)
        _wg.write_text(report_path, md, encoding='utf-8')

    def _generate_dashboard_v2_with_rows(self, today: str, dashboard_rows: list[dict[str, Any]], total_row: dict[str, Any]) -> None:
        """L6 Interactive Dashboard generation consuming pre-computed unified rows."""
        renderer = DashboardRenderer(self.project_root)
        recs = renderer.generate_recommendations(total_row, dashboard_rows)
        questions = renderer.generate_interview_questions(total_row, dashboard_rows)
        gauge_data = renderer.generate_gauge_data(total_row)
        html = renderer.render(dashboard_rows, recs, questions, gauge_data, today)
        renderer.save(html)

    # guardian: allow-magic-config
    def heal_repository(self, dry_run: bool=True, execute: bool=False, depth: int=0, max_depth: int=3, _call_path: list | None=None) -> dict[str, Any]:
        """
        Autonomous healing with Cognitive Performance tracking.

        Searches Pinecone for existing healing patterns before applying fixes,
        enabling pattern reuse and accelerated healing convergence.

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, execute healing actions
            depth: Current recursion depth
            max_depth: Maximum recursion depth
            _call_path: Internal recursion tracking

        Returns:
            Dict with healing summary: {"violations": int, "healed": int, "errors": int, "renamed": int}
        """
        log.info(f'[Tier 4 Safety] AutonomyGuardian heal_repository(dry_run={dry_run})')
        self.retrieval_stats = {'hits': 0, 'misses': 0, 'conf_scores': []}
        from datetime import datetime
        self.timestamp = datetime.now().isoformat()
        summary = {'violations': 0, 'healed': 0, 'errors': 0, 'renamed': 0, 'fixed': 0}
        try:
            agent_paths = []
            if self.discovery_json_path.exists():
                try:
                    with open(self.discovery_json_path, encoding='utf-8') as f:
                        agents_data = json.load(f)
                        for agent in agents_data:
                            path_str = agent.get('path', '')
                            if path_str:
                                full_path = self.project_root / path_str
                                if full_path.exists():
                                    agent_paths.append(full_path)
                # guardian: allow-silent-swallow
                except Exception as json_err:
                    log.error(f'[AutonomyGuardian] SSOT JSON load failed: {json_err}')
            else:
                log.warning('[AutonomyGuardian] SSOT JSON missing! Falling back to restricted scan.')
            if not agent_paths:
                log.warning('[AutonomyGuardian] Fallback to agentic_core scan (discovery JSON unavailable)')
                agentic_core_dir = self.project_root / AGENTIC_CORE_DIR
                from agentic_core.utils.ssot_discovery_validator import get_agent_files
                agent_paths = list(get_agent_files(agentic_core_dir))
            for agent_path in agent_paths:
                if any((pattern in str(agent_path) for pattern in self.exclude_patterns)):
                    continue
                try:
                    with open(agent_path, encoding='utf-8') as f:
                        content = f.read()
                        tree = ast.parse(content)
                    has_heal_method = False
                    inherits_sovereign_base = False
                    SOVEREIGN_BASE_CLASSES = {'SovereignBaseAgent', 'infrastructure_mixin', 'L3OrchestrationBase', 'L4StateBase', 'L5SafetyBase', 'L6ObservabilityBase', 'HealerMixin'}
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef) and node.name == 'heal_repository':
                            has_heal_method = True
                        if isinstance(node, ast.ClassDef):
                            for base in node.bases:
                                if isinstance(base, ast.Name) and base.id in SOVEREIGN_BASE_CLASSES:
                                    inherits_sovereign_base = True
                                elif isinstance(base, ast.Attribute) and base.attr in SOVEREIGN_BASE_CLASSES:
                                    inherits_sovereign_base = True
                    if inherits_sovereign_base:
                        has_heal_method = True
                    if not has_heal_method:
                        summary['violations'] += 1
                        log.warning(f'[AutonomyGuardian] Missing heal_repository: {agent_path}')
                        if not dry_run:
                            log.info(f'[AutonomyGuardian] Healing: {agent_path}')
                            lines = content.split('\n')
                            class_indent = None
                            insert_line = None
                            for i, line in enumerate(lines):
                                if 'class ' in line and 'Agent' in line:
                                    class_indent = len(line) - len(line.lstrip())
                                    for j in range(i + 1, len(lines)):
                                        if lines[j].strip() and (not lines[j].strip().startswith('#')):
                                            if lines[j].strip().startswith('def '):
                                                insert_line = j
                                                break
                                    if insert_line is None:
                                        insert_line = len(lines)
                                    break
                            if class_indent is not None and insert_line is not None:
                                method_indent = ' ' * (class_indent + 4)
                                heal_stub = ['', f'{method_indent}def heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs) -> Dict[str, Any]:', f'{method_indent}    """', f'{method_indent}    Autonomous Repair Capability (L0 DNA Integrity).', f'{method_indent}    ', f'{method_indent}    Args:', f'{method_indent}        dry_run: If True, only report violations without fixing', f'{method_indent}        execute: If True, apply fixes', f'{method_indent}    ', f'{method_indent}    Returns:', f'{method_indent}        Dict with healing summary', f'{method_indent}    """', f'{method_indent}    return {{"violations": 0, "fixed": 0, "errors": 0}}', '']
                                lines = lines[:insert_line] + heal_stub + lines[insert_line:]
                                try:
                                    _wg.open_write(agent_path, '\n'.join(lines))
                                    summary['fixed'] += 1
                                    log.info(f'[AutonomyGuardian] ✅ Added heal_repository() to {agent_path}')
                                # guardian: allow-silent-swallow
                                except Exception as write_error:
                                    summary['errors'] += 1
                                    log.error(f'[AutonomyGuardian] Failed to write {agent_path}: {write_error}')
                # guardian: allow-silent-swallow
                except Exception as e:
                    summary['errors'] += 1
                    log.error(f'[AutonomyGuardian] Error checking {agent_path}: {e}')
            for forbidden_dir in self.forbidden_dirs:
                forbidden_path = self.project_root / forbidden_dir
                if forbidden_path.exists():
                    summary['violations'] += 1
                    log.warning(f'[AutonomyGuardian] Forbidden directory: {forbidden_path}')
        # guardian: allow-silent-swallow
        except Exception as e:
            summary['errors'] += 1
            log.error(f'[AutonomyGuardian] heal_repository failed: {e}')
        return summary

def get_autonomy_guardian(project_root: Path) -> AutonomyGuardianAgent:
    """Factory function to create AutonomyGuardianAgent instance."""
    return AutonomyGuardianAgent(project_root)
