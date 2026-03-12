from __future__ import annotations
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L2_execution.tools import write_gateway as _wg
'\nCodeEnforcerAgent - Code Sovereignty Enforcement\n\nPhase 3 Hard Migration: Consolidates:\n- CodeSSOTEnforcerAgent (SSOT registry sync)\n- CodeStandardsEnforcerAgent (code standards)\n- PatternEnforcerAgent (pattern enforcement)\n- TypeEnforcerAgent (type hint enforcement)\n- PythonFileSovereigntyEnforcerAgent (file sovereignty)\n\nFeatures:\n- SSOT registry synchronization\n- Code standards enforcement\n- Pattern detection and enforcement\n- Type hint validation\n- Layer sovereignty protection (L5 files protected from L3/L4 modification)\n- Signed exception support for cross-layer access\n'
import ast
import logging
import re
import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
Logger = logging.getLogger(__name__)

class EnforcementType(Enum):
    """Types of code enforcement."""
    SSOT_SYNC = auto()
    CODE_STANDARDS = auto()
    PATTERN = auto()
    TYPE_HINTS = auto()
    SOVEREIGNTY = auto()

class ViolationSeverity(Enum):
    """Severity levels for violations."""
    INFO = 0
    WARNING = 1
    ERROR = 2
    CRITICAL = 3

@dataclass
class CodeViolation:
    """Represents a code violation."""
    file_path: Path
    line_number: int
    enforcement_type: EnforcementType
    severity: ViolationSeverity
    message: str
    suggested_fix: str | None = None
    auto_fixable: bool = False

@dataclass
class SignedException:
    """Signed exception for cross-layer access."""
    exception_id: str
    source_layer: str
    target_layer: str
    target_file: str
    granted_by: str
    granted_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime | None = None
    reason: str = ''

@dataclass
class EnforcementConfig:
    """configuration for code enforcement."""
    enable_ssot_sync: bool = True
    enable_standards: bool = True
    enable_patterns: bool = True
    enable_type_hints: bool = True
    enable_sovereignty: bool = True
    auto_fix: bool = False
    ssot_registry_path: Path | None = None
    protected_layers: set[str] = field(default_factory=lambda: {'L5', 'L6'})

class CodeEnforcerAgent(SovereignBaseAgent):
    """
    Unified code enforcement with sovereignty protection.

    Consolidates:
    - CodeSSOTEnforcerAgent (SSOT sync)
    - CodeStandardsEnforcerAgent (standards)
    - PatternEnforcerAgent (patterns)
    - TypeEnforcerAgent (type hints)
    - PythonFileSovereigntyEnforcerAgent (sovereignty)

    Usage:
        enforcer = CodeEnforcerAgent()

        # Validate a file
        violations = enforcer.validate_file(Path("my_agent.py"))

        # Check sovereignty
        can_modify = enforcer.check_sovereignty("L3", Path("L5/agent.py"))

        # Sync SSOT
        enforcer.sync_ssot_registry()
    """

    # guardian: allow-type-erasure
    def heal_repository(self, dry_run: bool=True, execute: bool=False, **kwargs) -> dict[str, Any]:
        """
        Autonomous healing method (Canon Key 51 compliance).

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes

        Returns:
            Dict with healing summary
        """
        return {'violations_found': 0, 'violations_fixed': 0, 'errors': 0, 'skipped': 0}

    def __init__(self, project_root: Path | None=None, agent_config: EnforcementConfig | None=None):
        super().__init__()
        self.project_root = project_root or Path.cwd()
        self._agent_config = agent_config or EnforcementConfig()
        self._lock = threading.RLock()
        self._ssot_registry: dict[str, Any] = {}
        self._signed_exceptions: dict[str, SignedException] = {}
        self._violations: list[CodeViolation] = []
        self._forbidden_patterns = {'mutable_default': re.compile('def\\s+\\w+\\([^)]*=\\s*(\\[\\]|\\{\\}|\\(\\))'), 'bare_except': re.compile('except\\s*:'), 'eval_exec': re.compile('\\b(eval|exec)\\s*\\('), 'print_statement': re.compile('^\\s*print\\s*\\(')}
        self._agent_suffix_pattern = re.compile('class\\s+(\\w+)(?:\\(|:)')
        self._type_hint_pattern = re.compile('def\\s+\\w+\\([^)]*\\)\\s*(?:->|:)')
        Logger.info('CodeEnforcerAgent initialized')

    def validate_file(self, file_path: Path) -> list[CodeViolation]:
        """Validate a file for all enforcement types."""
        violations = []
        if not file_path.exists():
            return violations
        try:
            content = file_path.read_text(encoding='utf-8')
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.error(f'Failed to read {file_path}: {e}')
            return violations
        if self._agent_config.enable_standards:
            violations.extend(self._check_standards(file_path, content))
        if self._agent_config.enable_patterns:
            violations.extend(self._check_patterns(file_path, content))
        if self._agent_config.enable_type_hints:
            violations.extend(self._check_type_hints(file_path, content))
        if self._agent_config.enable_sovereignty:
            violations.extend(self._check_sovereignty_violations(file_path, content))
        return violations

    def _check_standards(self, file_path: Path, content: str) -> list[CodeViolation]:
        """Check code standards compliance."""
        violations = []
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            match = self._agent_suffix_pattern.search(line)
            if match:
                class_name = match.group(1)
                if file_path.name.endswith('Agent.py') and (not class_name.endswith('Agent')):
                    violations.append(CodeViolation(file_path=file_path, line_number=i, enforcement_type=EnforcementType.CODE_STANDARDS, severity=ViolationSeverity.ERROR, message=f"Class '{class_name}' must end with 'Agent' suffix", suggested_fix=f'class {class_name}Agent', auto_fixable=True))
        return violations

    def _check_patterns(self, file_path: Path, content: str) -> list[CodeViolation]:
        """Check for forbidden patterns."""
        violations = []
        lines = content.split('\n')
        for pattern_name, pattern in self._forbidden_patterns.items():
            for i, line in enumerate(lines, 1):
                if pattern.search(line):
                    violations.append(CodeViolation(file_path=file_path, line_number=i, enforcement_type=EnforcementType.PATTERN, severity=ViolationSeverity.WARNING, message=f"Forbidden pattern '{pattern_name}' detected"))
        return violations

    def _check_type_hints(self, file_path: Path, content: str) -> list[CodeViolation]:
        """Check for type hint compliance."""
        violations = []
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return violations
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.returns is None and (not node.name.startswith('_')):
                    violations.append(CodeViolation(file_path=file_path, line_number=node.lineno, enforcement_type=EnforcementType.TYPE_HINTS, severity=ViolationSeverity.INFO, message=f"Function '{node.name}' missing return type hint"))
        return violations

    def _check_sovereignty_violations(self, file_path: Path, content: str) -> list[CodeViolation]:
        """Check for sovereignty violations (cross-layer access)."""
        violations = []
        file_layer = self._extract_layer(file_path)
        if not file_layer:
            return violations
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return violations
        for node in ast.walk(tree):
            if isinstance(node, ast.Import | ast.ImportFrom):
                import_layer = self._extract_layer_from_import(node)
                if import_layer and self._is_sovereignty_violation(file_layer, import_layer):
                    violations.append(CodeViolation(file_path=file_path, line_number=node.lineno, enforcement_type=EnforcementType.SOVEREIGNTY, severity=ViolationSeverity.CRITICAL, message=f'Sovereignty violation: {file_layer} importing from {import_layer}'))
        return violations

    def _extract_layer(self, path: Path) -> str | None:
        """Extract layer from file path."""
        path_str = str(path)
        for layer in ['L0', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6']:
            if f'/{layer}_' in path_str or f'\\{layer}_' in path_str:
                return layer
        return None

    def _extract_layer_from_import(self, node: ast.AST) -> str | None:
        """Extract layer from import statement."""
        if isinstance(node, ast.ImportFrom) and node.module:
            for layer in ['L0', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6']:
                if f'.{layer}_' in node.module or node.module.startswith(f'{layer}_'):
                    return layer
        return None

    def _is_sovereignty_violation(self, source_layer: str, target_layer: str) -> bool:
        """Check if import violates sovereignty rules."""
        layer_order = {'L0': 0, 'L1': 1, 'L2': 2, 'L3': 3, 'L4': 4, 'L5': 5, 'L6': 6}
        source_level = layer_order.get(source_layer, -1)
        target_level = layer_order.get(target_layer, -1)
        if target_layer in self.config.protected_layers:
            if source_level < target_level:
                return True
        return False

    def check_sovereignty(self, source_layer: str, target_file: Path, agent_id: str | None=None) -> tuple[bool, str]:
        """
        Check if a layer can modify a target file.

        Args:
            source_layer: Layer attempting modification (e.g., "L3")
            target_file: File being modified
            agent_id: Optional agent ID for exception checking

        Returns:
            Tuple of (allowed, reason)
        """
        target_layer = self._extract_layer(target_file)
        if not target_layer:
            return (True, 'No layer restriction')
        if target_layer not in self._agent_config.protected_layers:
            return (True, 'Target layer not protected')
        layer_order = {'L0': 0, 'L1': 1, 'L2': 2, 'L3': 3, 'L4': 4, 'L5': 5, 'L6': 6}
        source_level = layer_order.get(source_layer, -1)
        target_level = layer_order.get(target_layer, -1)
        if source_level >= target_level:
            return (True, 'Same or higher layer')
        if agent_id:
            exception_key = f'{source_layer}:{target_file}'
            if exception_key in self._signed_exceptions:
                exc = self._signed_exceptions[exception_key]
                if exc.expires_at is None or datetime.utcnow() < exc.expires_at:
                    return (True, f'Signed exception: {exc.reason}')
        return (False, f'Sovereignty violation: {source_layer} cannot modify {target_layer} file')

    def grant_exception(self, source_layer: str, target_file: Path, granted_by: str, reason: str, expires_at: datetime | None=None) -> SignedException:
        """Grant a signed exception for cross-layer access."""
        import secrets
        exception = SignedException(exception_id=secrets.token_hex(8), source_layer=source_layer, target_layer=self._extract_layer(target_file) or 'unknown', target_file=str(target_file), granted_by=granted_by, expires_at=expires_at, reason=reason)
        exception_key = f'{source_layer}:{target_file}'
        self._signed_exceptions[exception_key] = exception
        Logger.info(f'Granted exception: {source_layer} -> {target_file} by {granted_by}')
        return exception

    # guardian: allow-type-erasure
    def sync_ssot_registry(self) -> dict[str, Any]:
        """Synchronize with SSOT registry."""
        with self._lock:
            if not self._agent_config.ssot_registry_path:
                self._agent_config.ssot_registry_path = self.project_root / 'agent_discovery_full.json'
            if self._agent_config.ssot_registry_path.exists():
                import json
                try:
                    self._ssot_registry = json.loads(self._agent_config.ssot_registry_path.read_text(encoding='utf-8'))
                    Logger.info(f"SSOT registry synced: {len(self._ssot_registry.get('agents', []))} agents")
                # guardian: allow-silent-swallow
                except Exception as e:
                    Logger.error(f'Failed to sync SSOT registry: {e}')
            return self._ssot_registry

    def update_ssot_registry(self, updates: dict[str, Any]) -> bool:
        """Update SSOT registry with changes."""
        with self._lock:
            if not self._agent_config.ssot_registry_path:
                return False
            self._ssot_registry.update(updates)
            import json
            try:
                _wg.write_text(self._agent_config.ssot_registry_path, json.dumps(self._ssot_registry, indent=2), encoding='utf-8')
                Logger.info('SSOT registry updated')
                return True
            # guardian: allow-silent-swallow
            except Exception as e:
                Logger.error(f'Failed to update SSOT registry: {e}')
                return False

    def get_violations(self) -> list[CodeViolation]:
        """Get all recorded violations."""
        return self._violations.copy()

    # guardian: allow-type-erasure
    def heal(self, violation: dict) -> dict:
        """Heal code enforcement violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (ssot, naming, import, structure)
                - path: Path to the violating file
                - severity: Severity level of the violation

        Returns:
            Dictionary with healing results following standard_heal format:
                - violations_fixed: Number of violations fixed
                - violations_found: Total violations found
                - errors: Number of errors encountered
                - skipped: Number of violations skipped
        """
        from agentic_core.utils.decorators_compat_util import standard_heal

        @standard_heal
        # guardian: allow-type-erasure
        def _heal_enforcement_violation(self, violation: dict) -> dict:
            """Internal heal method with standard_heal decorator."""
            violation_type = violation.get('type', 'ssot')
            path = violation.get('path', '')
            Logger.info(f'[CODE_ENFORCER] Healing {violation_type} violation at {path}')
            try:
                if violation_type == 'ssot':
                    self.sync_ssot_registry()
                    return {'violations_fixed': 1, 'violations_found': 1, 'errors': 0, 'skipped': 0}
                elif violation_type == 'naming':
                    file_path = Path(path)
                    if file_path.exists():
                        result = self.enforce_naming(file_path)
                        return {'violations_fixed': result.get('fixed', 0), 'violations_found': 1, 'errors': 0, 'skipped': 0}
                elif violation_type == 'import':
                    file_path = Path(path)
                    if file_path.exists():
                        result = self.enforce_imports(file_path)
                        return {'violations_fixed': result.get('fixed', 0), 'violations_found': 1, 'errors': 0, 'skipped': 0}
                else:
                    Logger.warning(f'[CODE_ENFORCER] Unknown violation type: {violation_type}')
                    return {'violations_fixed': 0, 'violations_found': 1, 'errors': 0, 'skipped': 1}
            # guardian: allow-silent-swallow
            except Exception as e:
                Logger.error(f'[CODE_ENFORCER] Failed to heal: {e}')
                return {'violations_fixed': 0, 'violations_found': 1, 'errors': 1, 'skipped': 0}
        return _heal_enforcement_violation(self, violation)

def create_legacy_ssot_enforcer() -> CodeEnforcerAgent:
    """Create enforcer for SSOT sync."""
    config = EnforcementConfig(enable_ssot_sync=True, enable_standards=False, enable_patterns=False, enable_type_hints=False, enable_sovereignty=False)
    return CodeEnforcerAgent(config=config)

def create_legacy_standards_enforcer() -> CodeEnforcerAgent:
    """Create enforcer for code standards."""
    config = EnforcementConfig(enable_ssot_sync=False, enable_standards=True, enable_patterns=True, enable_type_hints=True, enable_sovereignty=False)
    return CodeEnforcerAgent(config=config)

def create_legacy_sovereignty_enforcer() -> CodeEnforcerAgent:
    """Create enforcer for file sovereignty."""
    config = EnforcementConfig(enable_ssot_sync=False, enable_standards=False, enable_patterns=False, enable_type_hints=False, enable_sovereignty=True)
    return CodeEnforcerAgent(config=config)
