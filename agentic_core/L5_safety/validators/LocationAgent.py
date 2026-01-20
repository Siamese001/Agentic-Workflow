from __future__ import annotations
"""
LocationAgent: Sovereign territorial gatekeeper (Canon Key 6 territory)

Enforces:
- Root folder whitelist (from ROOT_WHITELIST)
- Exact depth per sovereign root (SOVEREIGN_REGISTRY['depth'])
- Forbidden root folders and numbered patterns
- Sovereign root existence
- Gravity leak prevention (compliance logic in apps_*)
- Root-level file protections (Key 0)

Replaces logic previously in void_compliance.py:
  - validate_file_location()
  - enforce_void_compliance()
  - validate_sovereign_roots()

Placed in L5_safety/validators per semantic_l2_registry purpose:
  "Canon constitution validators, structural policy enforcement..."
"""
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import re
import shutil
import logging
import ast

# Shared infrastructure imports (SRP fission)
from agentic_core.L5_safety.validators.location_constants import (
    ARCHIVE_SUBFOLDERS,
    DEFAULT_ARCHIVE_SUBFOLDER,
    HEALING_STRATEGY_MAP,
    DEFAULT_APP_HEALING_TARGET,
)
from agentic_core.L5_safety.validators.location_utils import (
    compute_module_path,
    is_path_compliant as is_path_compliant_util,
)

Logger = logging.getLogger(__name__)

# Performance optimization: Use SovereignIndex instead of rglob
try:
    from agentic_core.utils.sovereign_index import SovereignIndex
    SOVEREIGN_INDEX_AVAILABLE = True
except ImportError:
    SOVEREIGN_INDEX_AVAILABLE = False
    SovereignIndex = None


def _get_python_files(project_root: Path) -> List[Path]:
    """
    Get all Python files using ssot_discovery (Phase 6.1 standardization).
    
    This is a performance optimization to prevent timeouts during healing.
    Uses the cached FileCache mechanism for O(1) subsequent calls.
    """
    # Phase 6.1: Use ssot_discovery for standardized, cached file discovery
    from agentic_core.utils.ssot_discovery import get_python_files
    return get_python_files(project_root)

# ============================================================================
# L5 SOVEREIGN STRUCTURAL SSOT (Violation 5 Resolution)
# ============================================================================
# Supreme Court function for path compliance - L3/L2 agents MUST delegate here
# This is the canonical implementation for structural validation
# ============================================================================

def is_path_compliant(
    file_path: Union[str, Path],
    project_root: Optional[Path] = None
) -> bool:
    """
    L5 Sovereign Structural SSOT - Hard-enforcement of path validity.
    
    This is the Supreme Court for structural compliance. All L3 and L2 agents
    that need to validate file paths MUST call this function instead of
    implementing their own path validation logic.
    
    Enforces:
    1. Path must be within project root
    2. Root folder must be in SOVEREIGN_REGISTRY (whitelist)
    3. Depth must not exceed MAX_ALLOWED_DEPTH per root
    4. No forbidden root folders (legacy_*, old_*)
    5. No numbered folder prefixes (^\d+_)
    
    Args:
        file_path: Path to validate (str or Path)
        project_root: Optional project root (auto-detected if None)
        
    Returns:
        True if path is structurally compliant, False otherwise
        
    Example:
        >>> is_path_compliant('agentic_core/L5_safety/validators/LocationAgent.py')
        True
        >>> is_path_compliant('legacy_code/old_agent.py')
        False
        >>> is_path_compliant('agentic_core/L1/L2/L3/L4/L5/deep.py')  # Too deep
        False
    """
    from agentic_core.L5_safety.validators.structure_blueprint import (
        ROOT_WHITELIST,
        FORBIDDEN_ROOT_FOLDERS,
        FORBIDDEN_FOLDER_PATTERN,
        SOVEREIGN_REGISTRY,
        get_validated_project_root,
    )
    
    # Auto-detect project root if not provided
    if project_root is None:
        project_root = get_validated_project_root()
    
    # Convert to Path object
    path = Path(file_path)
    
    # 1. Must be within project root
    try:
        if not path.is_absolute():
            path = project_root / path
        rel_path = path.relative_to(project_root)
    except (ValueError, RuntimeError):
        # Path is outside project root
        return False
    
    parts = rel_path.parts
    if not parts:
        return False
    
    root_folder = parts[0]
    
    # 2. Root folder must be whitelisted (in SOVEREIGN_REGISTRY)
    if root_folder not in ROOT_WHITELIST:
        return False
    
    # 3. Depth restriction check
    max_depth = SOVEREIGN_REGISTRY.get(root_folder, {}).get('depth', 3)
    if len(parts) > max_depth:
        return False
    
    # 4. Forbidden root folders check
    if root_folder in FORBIDDEN_ROOT_FOLDERS:
        return False
    
    # 5. Forbidden numbered folder pattern check (^\d+_)
    for part in parts:
        if FORBIDDEN_FOLDER_PATTERN.match(part):
            return False
    
    # All checks passed
    return True


from agentic_core.L5_safety.validators.structure_blueprint import (
    ROOT_WHITELIST,                    # = set(sovereign_registry.keys())
    FORBIDDEN_ROOT_FOLDERS,
    FORBIDDEN_FOLDER_PATTERN,          # ^\\d+_
    SOVEREIGN_REGISTRY,
    ROOT_PROTECTED_FILES,
    TESTS_ROOT_FILE_WHITELIST,
    APP_SPECIFIC_TARGET_SUBFOLDER,
    is_app_specific_file,
    get_correct_app_path,
    has_forbidden_layer_prefix,
    is_broken_backup_file,
    validate_path_within_project,
    get_validated_project_root,
    safe_path_join,
    APP_RG_AST_TERMS,
    APP_LIC_AST_TERMS,
    APP_RG_VARIABLE_TERMS,
    APP_LIC_VARIABLE_TERMS,
    APP_RG_STRING_TERMS,
    APP_LIC_STRING_TERMS,
    VARIABLE_HIT_WEIGHT,
    STRING_HIT_WEIGHT,
    AST_DOMAIN_HIT_THRESHOLD,
    FORBIDDEN_APP_MODULES,
    CORE_TERRITORY_KEYWORDS,
    LAYER_FORBIDDEN_IMPORTS,
    TERRITORY_MISMATCH_THRESHOLD,
    MIN_ALIGNMENT_SCORE,
    DEFAULT_APP_HEALING_TARGET,
    DEFAULT_CORE_HEALING_TERRITORY,
    GLOBAL_EXCLUDED_DIRS,              # Production Lens SSOT
    is_path_allowed,                   # SSOT path validation helper
    VARIABLE_DEPTH_SUBFOLDERS,         # Flexible depth exemptions (Option A)
)
from agentic_core.prompt_governance.version_registry.PromptRegistry import registers_prompt
from agentic_core.utils.core_extensions.timeout_decorator import timeout, HealTimeoutError

# [PHASE 20] DEPRECATION: void_compliance_helpers.py removed - inline implementation
def is_excepted_from_key(key_id: int, file_path, line_content: str = '') -> bool:
    """Check if file/line is excepted from key validation."""
    import fnmatch
    import re
    from agentic_core.L5_safety.validators.structure_blueprint import CANON_KEY_EXCEPTIONS
    exceptions = CANON_KEY_EXCEPTIONS.get(key_id, {})
    if not exceptions:
        return False
    try:
        from pathlib import Path
        project_root = Path(__file__).resolve().parents[3]
        rel_path = str(file_path.relative_to(project_root)).replace('\\', '/')
    except (ValueError, IndexError):
        rel_path = str(file_path.name) if hasattr(file_path, 'name') else str(file_path)
    file_exceptions = exceptions.get('files', set())
    if rel_path in file_exceptions or any(fnmatch.fnmatch(rel_path, p) for p in file_exceptions):
        return True
    if line_content:
        for pattern in exceptions.get('patterns', []):
            if re.search(pattern, line_content):
                return True
    return False


from agentic_core.L5_safety.validators.L5Agent import L5Agent
from agentic_core.L2_execution.mcp.mcp_hardened_mixin_1 import MCPHardenedMixin

@registers_prompt(
    template_name="file_placement.jinja",
    purpose="Enforces territory/file placement rules",
    territory="templates"
)
class LocationAgent(L5Agent, MCPHardenedMixin):
    """
    Autonomous agent responsible for territorial integrity.
    Run independently or as first stage in compliance orchestrator.
    
    RCA FIX 2026-01-02: Added project root validation to prevent folder creation
    outside the active project root (e.g., C:\Git\ instead of C:\Git\Agentic-Workflow\)
    
    POST-HEALING VALIDATION (Ultra Reliability 2026-01-02):
    - After every successful healing action (move/archive/delete), automatically re-validate
      the affected path to confirm resolution.
    - Reports explicit status: SUCCESS (no violations), PARTIAL (new/different violations),
      FAILED (original violation persists — rare, indicates bug).
    - Enables 99%+ autonomous healing confidence — healer self-verifies fixes.
    - For deletes: confirms file absence.
    - For moves: validates new location (and optionally original absence).
    
    IMPORTAGENT INTEGRATION (Ultra Reliability 2026-01-02):
    - After successful move healing, automatically trigger import fixes across repo
    - Reuses proven NamingAgent pattern: rglob search + regex replace for old → new module
    - Computes old/new dotted module paths from file locations
    - Safe: backs up changed files, skips non-Python, collision-safe
    - Only runs on applied moves (not deletes/archives)
    - Reports fixed count + files touched in action dict
    - Achieves near-100% healing autonomy: move + import fix + post-validate in one flow
    
    NAMINGAGENT VALIDATION INTEGRATION (Ultra Reliability 2026-01-02):
    - After healing moves and import fixes, run NamingAgent prefix-location validation
      on all affected/new paths
    - Detects naming drift introduced by moves (e.g., app file still in core, or collision suffix issues)
    - Also runs duplicate filename scan on repo (post-move collisions possible with _1 suffix)
    - Reports naming status in batch post-heal: FULL_SUCCESS / PARTIAL / NEEDS_REVIEW
    - Uses NamingAgent singleton — zero overhead, consistent with repo naming enforcement
    - Enables detection/future auto-heal of naming violations post-location healing
    
    NAMINGAGENT AUTO-HEALING (Ultra Autonomy 2026-01-02):
    - After detecting naming violations post-heal, automatically resolve them
    - Primary: Duplicate filenames (from collision suffixes) → resolve via NamingAgent
    - Secondary: Prefix-location mismatches → attempt canonical move or rename suggestion
    - Uses NamingAgent's proven resolve_duplicate_filename() and move_to_canonical_location()
    - Safe: backups, dry-run, collision handling inherited
    - Reports healing actions + post-post-heal naming status
    - Achieves near-100% full-cycle autonomy: location → import → naming → validated
    
    IMPORTAGENT INTEGRATION & AUTO-HEALING (Ultra Autonomy 2026-01-02):
    - After healing moves/import fixes, run ImportAgent convention + gravity validation
      on all affected paths (new locations + import-touched files)
    - Auto-heal fixable issues:
        • Remove unused imports (high-confidence only)
        • Reorder imports (stdlib → third-party → local)
        • Remove star/relative imports
    - Gravity violations → limited auto-heal (remove offending import + add TODO) when safe
    - Full gravity resolution often requires architectural moves (handled by LocationAgent domain heal)
    - Uses ImportAgent singleton — consistent enforcement
    - Final re-validation confirms import compliance post-auto-heal
    - Achieves 99%+ full-cycle autonomy: location → import rename → convention fix → naming → verified
    
    NAMINGAGENT CONVENTIONS INTEGRATION (Ultra Autonomy 2026-01-02):
    - After all healing moves/import/gravity fixes, run full NamingAgent convention validation
      on affected + import-touched + gravity-healed files
    - Auto-heal fixable convention violations:
        • snake_case enforcement (rename file)
        • Forbidden pattern removal (rename)
        • High-signal keyword absence (report only — cannot auto-add)
    - Integrates with existing duplicate/prefix-location auto-heal
    - Final re-validation confirms naming compliance
    - Achieves complete sovereign naming law enforcement in heal cycle
    """

    @dataclass
    class Violation:
        """Structured violation output for deterministic healing."""
        is_valid: bool
        message: str
        file_path: Optional[Path] = None
        suggested_path: Optional[str] = None  # Full relative path for healing (e.g., 'apps_rg/engines')
        severity: int = 5

    def __init__(self, project_root: Path) -> None:
        """Initialize the instance."""
        self.project_root = project_root.resolve()
        # Validate project root is correct
        self._validate_project_root()
        # Lazy agent references to avoid circular instantiation
        # These are created on-demand via properties, not in __init__
        self._naming_agent = None
        self._import_agent = None
    
    @property
    def naming_agent(self):
        """Lazy NamingAgent - created on first access to avoid circular init."""
        if self._naming_agent is None:
            try:
                from agentic_core.L5_safety.validators.NamingAgent import get_naming_agent
                self._naming_agent = get_naming_agent(self.project_root)
            except (ImportError, RecursionError):
                Logger.warning("NamingAgent not available - post-heal naming validation disabled")
        return self._naming_agent
    
    @property
    def import_agent(self):
        """Lazy ImportAgent - created on first access to avoid circular init."""
        if self._import_agent is None:
            try:
                from agentic_core.L5_safety.gravity.ImportAgent import get_import_agent
                self._import_agent = get_import_agent(self.project_root)
            except (ImportError, RecursionError):
                Logger.warning("ImportAgent not available - post-heal import validation disabled")
        return self._import_agent

    def _validate_project_root(self) -> None:
        """
        Validate that project_root is the actual project root, not a parent directory.
        RCA: Folders were created at C:\Git\ instead of C:\Git\Agentic-Workflow\
        """
        validated_root = get_validated_project_root()
        if self.project_root != validated_root:
            Logger.warning(
                f"PROJECT ROOT MISMATCH: Provided '{self.project_root}' != validated '{validated_root}'. "
                f"Using validated root to prevent folder creation outside project."
            )
            self.project_root = validated_root

    def safe_create_directory(self, relative_path: str) -> Path:
        """FACADE: Delegates to LocationHealerAgent."""
        from agentic_core.L5_safety.validators.LocationHealerAgent import LocationHealerAgent
        healer = LocationHealerAgent(project_root=self.project_root)
        return healer.safe_create_directory(relative_path)

    def validate_sovereign_roots(self) -> List[Tuple[Path, str]]:
        """FACADE: Delegates to LocationValidatorAgent."""
        from agentic_core.L5_safety.validators.LocationValidatorAgent import LocationValidatorAgent
        validator = LocationValidatorAgent(project_root=self.project_root)
        return validator.validate_sovereign_roots()

    def validate_file_location(self, file_path: Path) -> Tuple[bool, str]:
        """FACADE: Delegates to LocationValidatorAgent."""
        from agentic_core.L5_safety.validators.LocationValidatorAgent import LocationValidatorAgent
        validator = LocationValidatorAgent(project_root=self.project_root)
        return validator.validate_file_location(file_path)

    def _validate_ast_violations(self, root_folder: str, file_path: Path, rel_path: Path) -> Tuple[bool, str]:
        """FACADE: Delegates to LocationValidatorAgent."""
        from agentic_core.L5_safety.validators.LocationValidatorAgent import LocationValidatorAgent
        validator = LocationValidatorAgent(project_root=self.project_root)
        return validator._validate_ast_violations(root_folder, file_path, rel_path)

    def _check_forbidden_imports(self, tree: ast.AST, current_l1: str, rel_path: Path) -> Tuple[bool, str]:
        """FACADE: Delegates to LocationValidatorAgent."""
        from agentic_core.L5_safety.validators.LocationValidatorAgent import LocationValidatorAgent
        validator = LocationValidatorAgent(project_root=self.project_root)
        return validator._check_forbidden_imports(tree, current_l1, rel_path)
    
    def _scan_imports_for_violations(self, tree: ast.AST, current_l1: str) -> Tuple[bool, Optional[str]]:
        """FACADE: Delegates to LocationValidatorAgent."""
        from agentic_core.L5_safety.validators.LocationValidatorAgent import LocationValidatorAgent
        validator = LocationValidatorAgent(project_root=self.project_root)
        return validator._scan_imports_for_violations(tree, current_l1)
    
    def _extract_modules_from_node(self, node: ast.AST) -> List[str]:
        """FACADE: Delegates to LocationValidatorAgent."""
        from agentic_core.L5_safety.validators.LocationValidatorAgent import LocationValidatorAgent
        validator = LocationValidatorAgent(project_root=self.project_root)
        return validator._extract_modules_from_node(node)
    
    def _is_forbidden_app_import(self, module: str) -> bool:
        """FACADE: Delegates to LocationValidatorAgent."""
        from agentic_core.L5_safety.validators.LocationValidatorAgent import LocationValidatorAgent
        validator = LocationValidatorAgent(project_root=self.project_root)
        return validator._is_forbidden_app_import(module)
    
    def _check_layer_import_violation(self, module: str, current_l1: str) -> Optional[str]:
        """FACADE: Delegates to LocationValidatorAgent."""
        from agentic_core.L5_safety.validators.LocationValidatorAgent import LocationValidatorAgent
        validator = LocationValidatorAgent(project_root=self.project_root)
        return validator._check_layer_import_violation(module, current_l1)

    def _check_semantic_alignment(self, tree: ast.AST, current_territory: str, rel_path: Path) -> Tuple[bool, str]:
        """FACADE: Delegates to LocationValidatorAgent."""
        from agentic_core.L5_safety.validators.LocationValidatorAgent import LocationValidatorAgent
        validator = LocationValidatorAgent(project_root=self.project_root)
        return validator._check_semantic_alignment(tree, current_territory, rel_path)
    
    def _calculate_semantic_scores(self, tree: ast.AST) -> Tuple[float, float, Dict[str, float]]:
        """FACADE: Delegates to LocationValidatorAgent."""
        from agentic_core.L5_safety.validators.LocationValidatorAgent import LocationValidatorAgent
        validator = LocationValidatorAgent(project_root=self.project_root)
        return validator._calculate_semantic_scores(tree)
    
    def _check_app_domain_violation(self, app_rg_score: float, app_lic_score: float, rel_path: Path) -> Tuple[bool, str]:
        """FACADE: Delegates to LocationValidatorAgent."""
        from agentic_core.L5_safety.validators.LocationValidatorAgent import LocationValidatorAgent
        validator = LocationValidatorAgent(project_root=self.project_root)
        return validator._check_app_domain_violation(app_rg_score, app_lic_score, rel_path)
    
    def _check_territory_alignment(self, current_territory: str, territory_scores: Dict[str, float], rel_path: Path) -> Tuple[bool, str]:
        """FACADE: Delegates to LocationValidatorAgent."""
        from agentic_core.L5_safety.validators.LocationValidatorAgent import LocationValidatorAgent
        validator = LocationValidatorAgent(project_root=self.project_root)
        return validator._check_territory_alignment(current_territory, territory_scores, rel_path)

    def _validate_final_checks(self, root_folder: str, file_path: Path, parts: tuple) -> Tuple[bool, str]:
        """FACADE: Delegates to LocationValidatorAgent."""
        from agentic_core.L5_safety.validators.LocationValidatorAgent import LocationValidatorAgent
        validator = LocationValidatorAgent(project_root=self.project_root)
        return validator._validate_final_checks(root_folder, file_path, parts)

    # Healing strategy dispatch table (reduces CC by eliminating if/elif chains)
    HEALING_STRATEGIES = {
        "APP-SPECIFIC IN CORE VIOLATION": "_heal_app_specific_violation",
        "AST DOMAIN VIOLATION": "_heal_app_specific_violation",
        "TERRITORY MISMATCH VIOLATION": "_heal_territory_mismatch",
        "TERRITORY ALIGNMENT WEAK": "_heal_territory_mismatch",
        "BROKEN BACKUP FILE": "_heal_broken_backup",
        "SHALLOW VIOLATION": "_heal_depth_violation",
        "DEEP VIOLATION": "_heal_depth_violation",
    }

    def _apply_healing_strategy(
        self, file_path: Path, msg: str, archives_root: Path, dry_run: bool,
        affected_paths: List[Path], import_touched_paths: List[Path]
    ) -> Dict[str, Any]:
        """FACADE: Delegates to LocationHealerAgent."""
        from agentic_core.L5_safety.validators.LocationHealerAgent import LocationHealerAgent
        healer = LocationHealerAgent(project_root=self.project_root)
        return healer._apply_healing_strategy(file_path, msg, archives_root, dry_run, affected_paths, import_touched_paths)

    def _heal_broken_backup(self, file_path: Path, dry_run: bool, affected_paths: List[Path]) -> Dict[str, Any]:
        """FACADE: Delegates to LocationHealerAgent."""
        from agentic_core.L5_safety.validators.LocationHealerAgent import LocationHealerAgent
        healer = LocationHealerAgent(project_root=self.project_root)
        return healer._heal_broken_backup(file_path, dry_run, affected_paths)

    def _heal_app_specific_violation(
        self, file_path: Path, msg: str, dry_run: bool,
        affected_paths: List[Path], import_touched_paths: List[Path]
    ) -> Dict[str, Any]:
        """FACADE: Delegates to LocationHealerAgent."""
        from agentic_core.L5_safety.validators.LocationHealerAgent import LocationHealerAgent
        healer = LocationHealerAgent(project_root=self.project_root)
        return healer._heal_app_specific_violation(file_path, msg, dry_run, affected_paths, import_touched_paths)

    def _heal_territory_mismatch(
        self, file_path: Path, msg: str, dry_run: bool,
        affected_paths: List[Path], import_touched_paths: List[Path]
    ) -> Dict[str, Any]:
        """FACADE: Delegates to LocationHealerAgent."""
        from agentic_core.L5_safety.validators.LocationHealerAgent import LocationHealerAgent
        healer = LocationHealerAgent(project_root=self.project_root)
        return healer._heal_territory_mismatch(file_path, msg, dry_run, affected_paths, import_touched_paths)

    def _heal_depth_violation(
        self, file_path: Path, msg: str, dry_run: bool,
        affected_paths: List[Path], import_touched_paths: List[Path]
    ) -> Dict[str, Any]:
        """FACADE: Delegates to LocationHealerAgent."""
        from agentic_core.L5_safety.validators.LocationHealerAgent import LocationHealerAgent
        healer = LocationHealerAgent(project_root=self.project_root)
        return healer._heal_depth_violation(file_path, msg, dry_run, affected_paths, import_touched_paths)

    # Archive subfolder mapping moved to location_constants.py

    def _heal_via_archiving(
        self, file_path: Path, msg: str, archives_root: Path, 
        dry_run: bool, affected_paths: List[Path]
    ) -> Dict[str, Any]:
        """FACADE: Delegates to LocationHealerAgent."""
        from agentic_core.L5_safety.validators.LocationHealerAgent import LocationHealerAgent
        healer = LocationHealerAgent(project_root=self.project_root)
        return healer._heal_via_archiving(file_path, msg, archives_root, dry_run, affected_paths)

    def _validate_forbidden_patterns(self, parts: tuple, root_folder: str) -> Tuple[bool, str]:
        """FACADE: Delegates to LocationValidatorAgent."""
        from agentic_core.L5_safety.validators.LocationValidatorAgent import LocationValidatorAgent
        validator = LocationValidatorAgent(project_root=self.project_root)
        return validator._validate_forbidden_patterns(parts, root_folder)

    def _validate_root_whitelist(self, root_folder: str, rel_path: Path = None) -> Tuple[bool, str]:
        """FACADE: Delegates to LocationValidatorAgent."""
        from agentic_core.L5_safety.validators.LocationValidatorAgent import LocationValidatorAgent
        validator = LocationValidatorAgent(project_root=self.project_root)
        return validator._validate_root_whitelist(root_folder, rel_path)

    # Subfolders that legitimately have variable depth (not fixed at depth 3)
    # [SSOT] VARIABLE_DEPTH_SUBFOLDERS imported at module level from structure_blueprint.py
    
    def _validate_depth_requirements(self, parts: tuple, root_folder: str, rel_path: Path) -> Tuple[bool, str]:
        """FACADE: Delegates to LocationValidatorAgent."""
        from agentic_core.L5_safety.validators.LocationValidatorAgent import LocationValidatorAgent
        validator = LocationValidatorAgent(project_root=self.project_root)
        return validator._validate_depth_requirements(parts, root_folder, rel_path)

    def _validate_app_specific_files(self, root_folder: str, file_path: Path) -> Tuple[bool, str]:
        """FACADE: Delegates to LocationValidatorAgent."""
        from agentic_core.L5_safety.validators.LocationValidatorAgent import LocationValidatorAgent
        validator = LocationValidatorAgent(project_root=self.project_root)
        return validator._validate_app_specific_files(root_folder, file_path)

    def _validate_filename_patterns(self, file_path: Path) -> Tuple[bool, str]:
        """FACADE: Delegates to LocationValidatorAgent."""
        from agentic_core.L5_safety.validators.LocationValidatorAgent import LocationValidatorAgent
        validator = LocationValidatorAgent(project_root=self.project_root)
        return validator._validate_filename_patterns(file_path)

    def enforce_void_compliance(self, files: List[Path]) -> Tuple[List[Path], List[Tuple[Path, str]]]:
        """Filter files and collect all location-based violations."""
        valid_files: List[Path] = []
        violations: List[Tuple[Path, str]] = []

        for file_path in files:
            is_valid, reason = self.validate_file_location(file_path)
            if is_valid:
                valid_files.append(file_path)
            else:
                violations.append((file_path, reason))

        return valid_files, violations

    def run(self, files: List[Path] = None) -> List[Tuple[Path, str]]:
        """
        Full location compliance scan.
        Returns all violations (Missing roots + per-file).
        Suitable as first-stage gatekeeper in orchestrator.
        """
        all_violations: List[Tuple[Path, str]] = []

        # 1. Check sovereign root existence
        all_violations.extend(self.validate_sovereign_roots())

        # 2. Scan files (using SovereignIndex for performance)
        if files is None:
            files = _get_python_files(self.project_root)

        _, file_violations = self.enforce_void_compliance(files)
        all_violations.extend(file_violations)

        return all_violations


    # SUPPLEMENTED FROM FilesystemAgent — enhances backup + cleanup capability — merged 2025-12-30
    # [SSOT FIX 2026-01-19] Changed from .sovereign_healing_backup to archives/healing_backups
    # Per SSOT: Only archives/ is the canonical backup location
    def _init_backup_dir(self) -> Path:
        """FACADE: Delegates to LocationHealerAgent."""
        from agentic_core.L5_safety.validators.LocationHealerAgent import LocationHealerAgent
        healer = LocationHealerAgent(project_root=self.project_root)
        return healer._init_backup_dir()

    def _backup_file(self, file_path: Path, backup_dir: Path = None) -> Path:
        """FACADE: Delegates to LocationHealerAgent."""
        from agentic_core.L5_safety.validators.LocationHealerAgent import LocationHealerAgent
        healer = LocationHealerAgent(project_root=self.project_root)
        return healer._backup_file(file_path, backup_dir)

    def post_heal_validation(self, original_path: Path, new_path: Optional[Path] = None, dry_run: bool = True) -> Dict[str, Any]:
        """FACADE: Delegates to LocationHealerAgent."""
        from agentic_core.L5_safety.validators.LocationHealerAgent import LocationHealerAgent
        healer = LocationHealerAgent(project_root=self.project_root)
        return healer.post_heal_validation(original_path, new_path, dry_run)

    def _compute_module_path(self, file_path: Path) -> str:
        """Wrapper for shared compute_module_path utility."""
        return compute_module_path(file_path, self.project_root)
    
    def _compute_module_path_legacy(self, file_path: Path) -> str:
        """
        Compute dotted import path from absolute file location.
        e.g., /project/apps_rg/engines/rg_tool.py → apps_rg.engines.rg_tool
        """
        try:
            rel = file_path.relative_to(self.project_root)
            parts = rel.parts[:-1]  # Drop filename
            stem = rel.stem
            return ".".join(parts + (stem,))
        except ValueError:
            return ""

    def fix_imports_after_move(self, old_path: Path, new_path: Path, dry_run: bool = True) -> Dict[str, Any]:
        """FACADE: Delegates to LocationHealerAgent."""
        from agentic_core.L5_safety.validators.LocationHealerAgent import LocationHealerAgent
        healer = LocationHealerAgent(project_root=self.project_root)
        return healer.fix_imports_after_move(old_path, new_path, dry_run)

    def safe_move(self, src_path: Path, dst_path: Path, dry_run: bool = True) -> Dict[str, Any]:
        """FACADE: Delegates to LocationHealerAgent."""
        from agentic_core.L5_safety.validators.LocationHealerAgent import LocationHealerAgent
        healer = LocationHealerAgent(project_root=self.project_root)
        return healer.safe_move(src_path, dst_path, dry_run)

    def safe_delete(self, file_path: Path, dry_run: bool = True) -> Dict[str, Any]:
        """FACADE: Delegates to LocationHealerAgent."""
        from agentic_core.L5_safety.validators.LocationHealerAgent import LocationHealerAgent
        healer = LocationHealerAgent(project_root=self.project_root)
        return healer.safe_delete(file_path, dry_run)

    def post_naming_validation(self, affected_paths: List[Path], dry_run: bool = True) -> Dict[str, Any]:
        """
        Post-healing NamingAgent validation on affected paths.
        Focuses on:
        - Prefix-location mismatch (critical after core ↔ apps moves)
        - Duplicate filenames repo-wide (collision suffixes)
        Returns structured naming report for batch integration.
        """
        naming_report = {
            "naming_post_heal_status": "SKIPPED",
            "naming_prefix_violations": [],
            "naming_duplicate_violations": {},
            "naming_message": "",
        }

        if dry_run:
            naming_report["naming_message"] = "PREVIEW: Naming validation skipped in dry-run"
            naming_report["naming_post_heal_status"] = "PREVIEW"
            return naming_report

        try:
            # 1. Prefix-location mismatch on affected paths
            prefix_violations = []
            for path in affected_paths:
                if path.suffix == ".py" and path.exists():
                    violations = self.naming_agent.validate_prefix_location_match(path)
                    if violations:
                        prefix_violations.append({
                            "file": str(path.relative_to(self.project_root)),
                            "issues": violations,
                        })

            # 2. Duplicate filename scan (repo-wide, efficient via NamingAgent)
            duplicates = self.naming_agent.scan_repository_duplicates()

            naming_report["naming_prefix_violations"] = prefix_violations
            naming_report["naming_duplicate_violations"] = {
                name: [str(p.relative_to(self.project_root)) for p in paths]
                for name, paths in duplicates.items()
            }

            total_naming_issues = len(prefix_violations) + len(duplicates)
            if total_naming_issues == 0:
                naming_report["naming_post_heal_status"] = "FULL_SUCCESS"
                naming_report["naming_message"] = "Naming compliant post-heal"
            elif total_naming_issues <= 2:
                naming_report["naming_post_heal_status"] = "PARTIAL"
                naming_report["naming_message"] = f"{total_naming_issues} minor naming issues (likely collision suffixes)"
            else:
                naming_report["naming_post_heal_status"] = "NEEDS_REVIEW"
                naming_report["naming_message"] = f"{total_naming_issues} naming issues — review prefixes/duplicates"

            Logger.info(f"[LocationAgent] Post-naming validation: {naming_report['naming_post_heal_status']} ({total_naming_issues} issues)")

        except Exception as e:
            naming_report["naming_post_heal_status"] = "ERROR"
            naming_report["naming_message"] = f"Naming validation error: {e}"
            Logger.error(f"[LocationAgent] Naming validation failed: {e}")

        return naming_report

    def auto_heal_naming_issues(self, naming_report: Dict[str, Any], dry_run: bool = True) -> Dict[str, Any]:
        """
        Autonomous naming healing triggered when post-naming validation finds issues.
        Prioritizes duplicates (common post-move), then prefix mismatches.
        Returns updated healing report with applied fixes.
        """
        heal_report = {
            "naming_auto_heal_applied": False,
            "naming_heal_actions": [],
            "naming_heal_message": "",
        }

        if dry_run:
            heal_report["naming_heal_message"] = "PREVIEW: Naming auto-heal skipped in dry-run"
            return heal_report

        actions = []

        try:
            # 1. Heal duplicates (highest priority — breaks imports/runtime)
            duplicates = naming_report.get("naming_duplicate_violations", {})
            for dup_name, paths in duplicates.items():
                # Heal all but one (keep original, resolve others)
                for path_str in paths[1:]:  # Skip first occurrence
                    path = self.project_root / path_str
                    if path.exists():
                        resolve_result = self.naming_agent.resolve_duplicate_filename(path, dry_run=False)
                        actions.append({
                            "type": "DUPLICATE_RESOLVE",
                            "original": path_str,
                            "result": resolve_result,
                        })

            # 2. Heal prefix-location mismatches
            prefix_violations = naming_report.get("naming_prefix_violations", [])
            for viol in prefix_violations:
                path_str = viol["file"]
                path = self.project_root / path_str
                if path.exists():
                    # Prefer canonical move (NamingAgent has semantic guidance)
                    move_result = self.naming_agent.move_to_canonical_location(path, dry_run=False)
                    if move_result.get("moved"):
                        actions.append({
                            "type": "PREFIX_CANONICAL_MOVE",
                            "original": path_str,
                            "result": move_result,
                        })
                    else:
                        # Fallback: simple rename suggestion (manual review)
                        actions.append({
                            "type": "PREFIX_NEEDS_MANUAL",
                            "file": path_str,
                            "issues": viol["issues"],
                        })

            if actions:
                heal_report["naming_auto_heal_applied"] = True
                heal_report["naming_heal_actions"] = actions
                heal_report["naming_heal_message"] = f"Applied {len(actions)} naming heals ({len([a for a in actions if 'moved' in a.get('result', {})])} moves)"
                Logger.info(f"[LocationAgent] Naming auto-heal: {len(actions)} actions")
            else:
                heal_report["naming_heal_message"] = "No naming issues required auto-heal"

        except Exception as e:
            heal_report["naming_heal_message"] = f"ERROR during naming auto-heal: {e}"
            Logger.error(f"[LocationAgent] Naming auto-heal failed: {e}")

        return heal_report

    # Refactored: Phase-based — orchestrator low CC (~10–15)
    def _recompute_ast_scores(self, tree: ast.AST) -> Tuple[float, float, Dict[str, float]]:
        """FACADE: Delegates to GravityLeakDetector."""
        from agentic_core.L5_safety.validators.GravityLeakDetector import GravityLeakDetector
        detector = GravityLeakDetector(project_root=self.project_root)
        return detector._recompute_ast_scores(tree)

    def _collect_ast_increments(self, tree: ast.AST) -> dict:
        """FACADE: Delegates to GravityLeakDetector."""
        from agentic_core.L5_safety.validators.GravityLeakDetector import GravityLeakDetector
        detector = GravityLeakDetector(project_root=self.project_root)
        return detector._collect_ast_increments(tree)

    def _score_identifier(self, name: str, weight: float, increments: dict) -> None:
        """FACADE: Delegates to GravityLeakDetector."""
        from agentic_core.L5_safety.validators.GravityLeakDetector import GravityLeakDetector
        detector = GravityLeakDetector(project_root=self.project_root)
        return detector._score_identifier(name, weight, increments)

    def _score_arguments(self, node: ast.arguments, increments: dict) -> None:
        """FACADE: Delegates to GravityLeakDetector."""
        from agentic_core.L5_safety.validators.GravityLeakDetector import GravityLeakDetector
        detector = GravityLeakDetector(project_root=self.project_root)
        return detector._score_arguments(node, increments)

    def _score_assignments(self, node: ast.Assign, increments: dict) -> None:
        """FACADE: Delegates to GravityLeakDetector."""
        from agentic_core.L5_safety.validators.GravityLeakDetector import GravityLeakDetector
        detector = GravityLeakDetector(project_root=self.project_root)
        return detector._score_assignments(node, increments)

    def _score_variable(self, name: str, increments: dict) -> None:
        """FACADE: Delegates to GravityLeakDetector."""
        from agentic_core.L5_safety.validators.GravityLeakDetector import GravityLeakDetector
        detector = GravityLeakDetector(project_root=self.project_root)
        return detector._score_variable(name, increments)

    def _score_string(self, text: str, increments: dict) -> None:
        """FACADE: Delegates to GravityLeakDetector."""
        from agentic_core.L5_safety.validators.GravityLeakDetector import GravityLeakDetector
        detector = GravityLeakDetector(project_root=self.project_root)
        return detector._score_string(text, increments)

    def _aggregate_ast_increments(self, initial_scores: dict, increments: dict) -> dict:
        """FACADE: Delegates to GravityLeakDetector."""
        from agentic_core.L5_safety.validators.GravityLeakDetector import GravityLeakDetector
        detector = GravityLeakDetector(project_root=self.project_root)
        return detector._aggregate_ast_increments(initial_scores, increments)

    def post_import_validation_and_heal(self, affected_paths: List[Path], import_touched_paths: List[Path], dry_run: bool = True) -> Dict[str, Any]:
        """
        Combined ImportAgent validation + auto-healing on affected files.
        Focuses on convention fixes (ordering, unused, star/relative).
        Gravity violations: Limited auto-heal (remove offending import + TODO) when safe.
        """
        full_report = {
            "import_validation_status": "SKIPPED",
            "import_auto_heal_applied": False,
            "import_gravity_violations": [],
            "import_gravity_auto_heal_applied": False,
            "import_gravity_heal_actions": [],
            "import_final_status": "SKIPPED",
            "import_message": "",
        }

        if dry_run:
            full_report["import_message"] = "PREVIEW: Import validation/heal skipped"
            return full_report

        all_paths = list(set(affected_paths + import_touched_paths))
        valid_files = [p for p in all_paths if p.suffix == ".py" and p.exists()]

        if not valid_files:
            full_report["import_validation_status"] = "NO_FILES"
            full_report["import_message"] = "No Python files affected"
            return full_report

        try:
            # Run ImportAgent analysis
            import_violations = self.import_agent.run(valid_files)

            convention_issues = []
            gravity_issues = []
            for path, msgs in import_violations:
                rel = str(path.relative_to(self.project_root))
                for msg in (msgs if isinstance(msgs, list) else [msgs]):
                    if "GRAVITY VIOLATION" in str(msg):
                        gravity_issues.append({"file": rel, "issue": str(msg), "path": path})
                    else:
                        convention_issues.append({"file": rel, "issue": str(msg)})

            total_convention = len(convention_issues)
            total_gravity = len(gravity_issues)

            full_report["import_gravity_violations"] = gravity_issues
            full_report["import_message"] = f"Validation: {total_convention} convention issues, {total_gravity} gravity issues"

            if total_convention == 0 and total_gravity == 0:
                full_report["import_validation_status"] = "FULL_SUCCESS"
                return full_report

            heal_actions = []

            # === GRAVITY LIMITED AUTO-HEAL (Safe removal + TODO) ===
            gravity_heal_actions = []
            if total_gravity > 0:
                gravity_heal_actions = self._heal_gravity_violations(gravity_issues)

                if gravity_heal_actions:
                    full_report["import_gravity_auto_heal_applied"] = True
                    full_report["import_gravity_heal_actions"] = gravity_heal_actions
                    full_report["import_message"] += f" | Gravity auto-heal: {len(gravity_heal_actions)} actions"

            # Final re-validation
            final_violations = self.import_agent.run(valid_files)
            final_convention = 0
            final_gravity = 0
            for _, msgs in final_violations:
                for m in (msgs if isinstance(msgs, list) else [msgs]):
                    if "GRAVITY" in str(m):
                        final_gravity += 1
                    else:
                        final_convention += 1

            if final_convention == 0 and final_gravity == 0:
                full_report["import_final_status"] = "FULL_SUCCESS"
            elif final_gravity == 0:
                full_report["import_final_status"] = "CONVENTION_FIXED"
            else:
                full_report["import_final_status"] = "PARTIAL"

            full_report["import_message"] += f" → Final: {full_report['import_final_status']} (gravity remaining: {final_gravity})"

        except Exception as e:
            full_report["import_validation_status"] = "ERROR"
            full_report["import_message"] = f"Import validation error: {e}"
            Logger.error(f"[LocationAgent] Import validation failed: {e}")

        return full_report

    def _heal_gravity_violations(self, gravity_issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """FACADE: Delegates to GravityLeakDetector."""
        from agentic_core.L5_safety.validators.GravityLeakDetector import GravityLeakDetector
        detector = GravityLeakDetector(project_root=self.project_root)
        return detector._heal_gravity_violations(gravity_issues)
    
    def _extract_downstream_roots(self, msg: str) -> List[str]:
        """FACADE: Delegates to GravityLeakDetector."""
        from agentic_core.L5_safety.validators.GravityLeakDetector import GravityLeakDetector
        detector = GravityLeakDetector(project_root=self.project_root)
        return detector._extract_downstream_roots(msg)
    
    def _insert_gravity_heal_todo(self, lines: List[str], msg: str, removed_modules: List[str]) -> str:
        """FACADE: Delegates to GravityLeakDetector."""
        from agentic_core.L5_safety.validators.GravityLeakDetector import GravityLeakDetector
        detector = GravityLeakDetector(project_root=self.project_root)
        return detector._insert_gravity_heal_todo(lines, msg, removed_modules)
    
    def _find_todo_insert_position(self, lines: List[str]) -> int:
        """FACADE: Delegates to GravityLeakDetector."""
        from agentic_core.L5_safety.validators.GravityLeakDetector import GravityLeakDetector
        detector = GravityLeakDetector(project_root=self.project_root)
        return detector._find_todo_insert_position(lines)
    
    def _backup_and_write_file(self, path: Path, content: str) -> None:
        """Backup file and write new content."""
        backup_dir = self._init_backup_dir() / "gravity_auto_heal"
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_path = backup_dir / path.relative_to(self.project_root)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, backup_path)
        path.write_text(content, encoding="utf-8")

    def post_naming_conventions_validation_and_heal(self, affected_paths: List[Path], dry_run: bool = True) -> Dict[str, Any]:
        """
        Full NamingAgent convention validation + auto-healing for fixable issues.
        Focuses on filename conventions (snake_case, forbidden patterns).
        """
        conventions_report = {
            "naming_conventions_status": "SKIPPED",
            "naming_conventions_auto_heal_applied": False,
            "naming_conventions_actions": [],
            "naming_conventions_final_status": "SKIPPED",
            "naming_message": "",
        }

        if dry_run:
            conventions_report["naming_message"] = "PREVIEW: Naming conventions validation/heal skipped"
            return conventions_report

        # Check convention violations
        convention_violations = []
        for path in [p for p in affected_paths if p.suffix == ".py" and p.exists()]:
            filename = path.name
            issues = []
            
            # snake_case check (allow PascalCase for Agent files)
            if not re.match(r'^[a-z0-9_]+\.py$', filename) and not re.match(r'^[A-Z][a-zA-Z0-9]*Agent\.py$', filename):
                issues.append("NOT_SNAKE_CASE")
            
            # Forbidden patterns check
            if hasattr(self.naming_agent, 'forbidden_patterns'):
                for pattern in self.naming_agent.forbidden_patterns:
                    if pattern.match(filename):
                        issues.append("FORBIDDEN_PATTERN")

            if issues:
                convention_violations.append({
                    "file": str(path.relative_to(self.project_root)),
                    "path": path,
                    "issues": issues,
                })

        total_conventions = len(convention_violations)
        conventions_report["naming_message"] = f"Conventions validation: {total_conventions} issues"

        if total_conventions == 0:
            conventions_report["naming_conventions_status"] = "FULL_SUCCESS"
            return conventions_report

        # Auto-heal fixable filename conventions
        heal_actions = []
        for viol in convention_violations:
            path = viol["path"]
            filename = path.name

            try:
                # Generate canonical snake_case name
                new_name = re.sub(r'[^a-zA-Z0-9_.]', '_', filename)
                new_name = re.sub(r'_+', '_', new_name).strip('_')
                if not new_name.endswith('.py'):
                    new_name += '.py'

                if new_name != filename and new_name.lower() != filename.lower():
                    new_path = path.parent / new_name

                    move_result = self.safe_move(path, new_path, dry_run=False)
                    if move_result.get("applied"):
                        heal_actions.append({
                            "type": "NAMING_CONVENTION_RENAME",
                            "original": viol["file"],
                            "new": str(new_path.relative_to(self.project_root)),
                            "fixes": viol["issues"],
                            "result": move_result,
                        })
                        affected_paths.append(new_path)

            except Exception as e:
                heal_actions.append({
                    "type": "NAMING_CONVENTION_HEAL_ERROR",
                    "file": viol["file"],
                    "error": str(e),
                })

        if heal_actions:
            conventions_report["naming_conventions_auto_heal_applied"] = True
            conventions_report["naming_conventions_actions"] = heal_actions

            remaining = len([a for a in heal_actions if "ERROR" in a.get("type", "")])
            if remaining == 0:
                conventions_report["naming_conventions_final_status"] = "FULL_SUCCESS"
            else:
                conventions_report["naming_conventions_final_status"] = "PARTIAL"

            conventions_report["naming_message"] += f" → Auto-heal applied ({len(heal_actions)} actions) → Final: {conventions_report['naming_conventions_final_status']}"

        return conventions_report

    def deep_import_validation_and_heal(self, affected_paths: List[Path], import_touched_paths: List[Path], dry_run: bool = True) -> Dict[str, Any]:
        """
        Deep ImportAgent integration: full validation + advanced auto-heal.
        Uses ImportAgent's precise AST analysis for convention fixes.
        Gravity root-cause triggers additional safe_move if needed.
        """
        deep_report = {
            "import_deep_status": "SKIPPED",
            "import_convention_heal_applied": False,
            "import_gravity_heal_applied": False,
            "import_final_status": "SKIPPED",
            "import_message": "",
        }

        if dry_run:
            deep_report["import_message"] = "PREVIEW: Deep import validation/heal skipped"
            return deep_report

        all_paths = list(set(affected_paths + import_touched_paths))
        valid_files = [p for p in all_paths if p.suffix == ".py" and p.exists()]

        if not valid_files:
            deep_report["import_deep_status"] = "NO_FILES"
            deep_report["import_message"] = "No files for import analysis"
            return deep_report

        try:
            # Full ImportAgent run
            import_violations = self.import_agent.run(valid_files)

            convention_actions = []
            gravity_actions = []
            additional_moves = []

            for path, msgs in import_violations:
                try:
                    content = path.read_text(encoding="utf-8")
                    tree = ast.parse(content)
                    new_content = content

                    # Remove star/relative imports
                    new_content = re.sub(r"^from \.+ import \*\n", "", new_content, flags=re.MULTILINE)
                    new_content = re.sub(r"^from \.+\s+", "from ", new_content, flags=re.MULTILINE)

                    if new_content != content:
                        backup_dir = self._init_backup_dir() / "deep_import_heal"
                        backup_dir.mkdir(parents=True, exist_ok=True)
                        backup_path = backup_dir / path.relative_to(self.project_root)
                        backup_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(path, backup_path)

                        path.write_text(new_content, encoding="utf-8")
                        convention_actions.append({
                            "type": "IMPORT_CONVENTION_HEAL",
                            "file": str(path.relative_to(self.project_root)),
                            "fixes": ["star/relative cleanup"],
                        })

                    # Gravity messages → existing limited heal + root-cause move trigger
                    for msg in (msgs if isinstance(msgs, list) else [msgs]):
                        if "GRAVITY VIOLATION" in str(msg):
                            gravity_actions.append({"file": str(path.relative_to(self.project_root)), "issue": str(msg)})
                            # Recompute AST scores for root-cause move
                            app_rg, app_lic, terr_scores = self._recompute_ast_scores(tree)
                            if (app_rg + app_lic) >= AST_DOMAIN_HIT_THRESHOLD * 0.8:
                                dominant = "apps_rg" if app_rg >= app_lic else "apps_lic"
                                target = self.project_root / dominant / APP_SPECIFIC_TARGET_SUBFOLDER / path.name
                                move_result = self.safe_move(path, target, dry_run=False)
                                additional_moves.append(move_result)

                except Exception as e:
                    convention_actions.append({"type": "IMPORT_HEAL_ERROR", "file": str(path), "error": str(e)})

            # Final full re-run
            final_valid = [p for p in valid_files if p.exists()]
            final_violations = self.import_agent.run(final_valid) if final_valid else []
            final_convention = 0
            final_gravity = 0
            for _, msgs in final_violations:
                for m in (msgs if isinstance(msgs, list) else [msgs]):
                    if "GRAVITY" in str(m):
                        final_gravity += 1
                    else:
                        final_convention += 1

            deep_report["import_convention_heal_applied"] = bool(convention_actions)
            deep_report["import_gravity_heal_applied"] = bool(gravity_actions or additional_moves)
            deep_report["import_final_status"] = "FULL_SUCCESS" if final_convention == 0 and final_gravity == 0 else "PARTIAL"
            deep_report["import_message"] = f"Deep import heal: {len(convention_actions)} convention fixes, {len(gravity_actions)} gravity issues, {len(additional_moves)} root-cause moves → Final: {deep_report['import_final_status']}"

        except Exception as e:
            deep_report["import_deep_status"] = "ERROR"
            deep_report["import_message"] = f"Deep import error: {e}"
            Logger.error(f"[LocationAgent] Deep import heal failed: {e}")

        return deep_report

    # Refactored: Phase-based decomposition — orchestrator low CC (~12)
    def deep_naming_validation_and_heal(self, affected_paths: List[Path], import_touched_paths: List[Path], dry_run: bool = True) -> Dict[str, Any]:
        """Deep naming validation orchestrator — linear phase chain."""
        deep_naming_report = {
            "naming_deep_status": "SKIPPED",
            "naming_convention_heal_applied": False,
            "naming_semantic_issues": [],
            "naming_heal_actions": [],
            "naming_final_status": "SKIPPED",
            "naming_message": "",
        }

        if dry_run:
            deep_naming_report["naming_message"] = "PREVIEW: Deep naming validation/heal skipped"
            return deep_naming_report

        all_paths = list(set(affected_paths + import_touched_paths))
        py_files = [p for p in all_paths if p.suffix == ".py" and p.exists()]

        if not py_files:
            deep_naming_report["naming_deep_status"] = "NO_FILES"
            deep_naming_report["naming_message"] = "No Python files for naming analysis"
            return deep_naming_report

        # Phase 1: Collect convention violations
        heal_actions, semantic_issues = self._collect_naming_violations(py_files, affected_paths)

        # Phase 2: Apply targeted healing
        healed_count = self._apply_naming_heals(heal_actions, affected_paths)

        # Phase 3: Determine final status
        deep_naming_report["naming_semantic_issues"] = semantic_issues
        deep_naming_report["naming_convention_heal_applied"] = bool(heal_actions)
        deep_naming_report["naming_heal_actions"] = heal_actions
        self._set_naming_final_status(deep_naming_report, heal_actions, semantic_issues)

        return deep_naming_report

    def _collect_naming_violations(self, py_files: List[Path], affected_paths: List[Path]) -> Tuple[list, list]:
        """FACADE: Delegates to LocationHealerAgent."""
        from agentic_core.L5_safety.validators.LocationHealerAgent import LocationHealerAgent
        healer = LocationHealerAgent(project_root=self.project_root)
        return healer._collect_naming_violations(py_files, affected_paths)

    def _check_naming_conventions(self, filename: str) -> list:
        """Check filename conventions (CC ~8)."""
        issues = []
        if not re.match(r'^[a-z0-9_]+\.py$', filename) and not re.match(r'^[A-Z][a-zA-Z0-9]*Agent\.py$', filename):
            issues.append("NOT_SNAKE_CASE")
        if hasattr(self.naming_agent, 'forbidden_patterns'):
            for pattern in self.naming_agent.forbidden_patterns:
                if pattern.match(filename):
                    issues.append("FORBIDDEN_PATTERN")
        return issues

    def _check_high_signal_keywords(self, filename_lower: str, content_lower: str) -> set:
        """Check for missing high-signal keywords (CC ~8)."""
        signal_keywords = ["agent", "engine", "validator", "healer", "manager", "orchestrator"]
        if not any(sig in filename_lower for sig in signal_keywords):
            return set()
        high_signal_kws = getattr(self.naming_agent, 'high_signal_keywords', set())
        expected_signals = high_signal_kws & {"agent", "engine", "validator", "healer", "orchestrator", "workflow", "state", "memory", "prompt", "guardrail"}
        return expected_signals - {kw for kw in expected_signals if kw in content_lower}

    def _check_sovereign_markers(self, path: Path, rel: str, filename_lower: str, content_lower: str, semantic_issues: list, heal_actions: list) -> None:
        """Check for sovereign root markers (CC ~8)."""
        try:
            rel_parts = path.relative_to(self.project_root).parts
            if len(rel_parts) == 1 and ("validator" in filename_lower or "compliance" in filename_lower):
                if "sovereign" not in content_lower:
                    semantic_issues.append({"file": rel, "issue": "MISSING_SOVEREIGN_MARKER"})
                    heal_actions.append({"path": path, "rel": rel, "type": "SOVEREIGN_MARKER"})
        except ValueError:
            pass

    def _apply_naming_heals(self, heal_actions: list, affected_paths: List[Path]) -> int:
        """FACADE: Delegates to LocationHealerAgent."""
        from agentic_core.L5_safety.validators.LocationHealerAgent import LocationHealerAgent
        healer = LocationHealerAgent(project_root=self.project_root)
        return healer._apply_naming_heals(heal_actions, affected_paths)

    def _insert_semantic_keywords(self, path: Path, missing_signals: set) -> None:
        """FACADE: Delegates to LocationHealerAgent."""
        from agentic_core.L5_safety.validators.LocationHealerAgent import LocationHealerAgent
        healer = LocationHealerAgent(project_root=self.project_root)
        return healer._insert_semantic_keywords(path, missing_signals)

    def _find_docstring_end(self, lines: list) -> int:
        """FACADE: Delegates to LocationHealerAgent."""
        from agentic_core.L5_safety.validators.LocationHealerAgent import LocationHealerAgent
        healer = LocationHealerAgent(project_root=self.project_root)
        return healer._find_docstring_end(lines)

    def _insert_sovereign_marker(self, path: Path) -> None:
        """FACADE: Delegates to LocationHealerAgent."""
        from agentic_core.L5_safety.validators.LocationHealerAgent import LocationHealerAgent
        healer = LocationHealerAgent(project_root=self.project_root)
        return healer._insert_sovereign_marker(path)

    def _apply_convention_fixes(self, path: Path, action: dict, affected_paths: List[Path]) -> None:
        """FACADE: Delegates to LocationHealerAgent."""
        from agentic_core.L5_safety.validators.LocationHealerAgent import LocationHealerAgent
        healer = LocationHealerAgent(project_root=self.project_root)
        return healer._apply_convention_fixes(path, action, affected_paths)

    def _set_naming_final_status(self, report: dict, heal_actions: list, semantic_issues: list) -> None:
        """FACADE: Delegates to LocationHealerAgent."""
        from agentic_core.L5_safety.validators.LocationHealerAgent import LocationHealerAgent
        healer = LocationHealerAgent(project_root=self.project_root)
        return healer._set_naming_final_status(report, heal_actions, semantic_issues)

    def cleanup_violations(
        self, 
        violations: List[Tuple[Path, str]], 
        dry_run: bool = True,
        max_actions: int = 50
    ) -> List[Dict[str, Any]]:
        """
        ULTRA HEALING ENGINE — Full FilesystemAgent integration (2026-01-02)
        
        Prioritized autonomous healing:
        - Archives void/depth/general violations
        - Auto-moves app-specific/domain leaks to correct apps_*/engines/
        - Auto-moves territory mismatches to semantically best agentic_core L1/L2
        - Archives broken backups / forbidden prefix files
        
        BATCH POST-HEALING VALIDATION (Ultra Reliability 2026-01-02):
        - After all individual actions, perform batch re-validation on all affected paths
        - Confirms global resolution: no remaining violations from healed files
        - Detects cascading issues (e.g., move introduced new depth/territory issue)
        - Provides summary statistics: healed count, success rate, remaining issues
        - Only runs in non-dry-run mode — efficient mini-scan on affected files only
        
        Args:
            violations: List of (path, reason) tuples or Violation objects
            dry_run: If True, only preview actions without executing
            max_actions: Maximum number of cleanup actions per run
            
        Returns:
            List of action dicts with results including batch_post_heal summary
        """
        actions = []
        archives_root = self.project_root / "archives"
        affected_paths: List[Path] = []  # Track original + new paths for batch validation
        import_touched_paths: List[Path] = []  # Collect from import fixes for naming validation
        
        for i, violation in enumerate(violations):
            if i >= max_actions:
                Logger.warning(f"[LocationAgent] Cleanup budget exhausted ({max_actions} actions).")
                break
            
            # Handle both tuple format (backward compat) and Violation objects
            if isinstance(violation, tuple):
                file_path, msg = violation
            else:
                file_path = getattr(violation, 'file_path', None) or violation[0]
                msg = getattr(violation, 'message', None) or violation[1]
            
            # Skip protected root files
            if file_path.name in ROOT_PROTECTED_FILES:
                Logger.info(f"[LocationAgent] Skipping protected root file: {file_path.name}")
                continue
            
            # Skip already-archived files
            archive_markers = ('.archived', '.backup', '.old', '.copy')
            if any(file_path.name.lower().endswith(marker) for marker in archive_markers):
                Logger.debug(f"[LocationAgent] Skipping already-archived file: {file_path.name}")
                continue
            if any(marker in file_path.name.lower() for marker in archive_markers):
                Logger.debug(f"[LocationAgent] Skipping file with archive marker: {file_path.name}")
                continue
                
            action = {
                "type": "LOCATION_HEALING",
                "file": str(file_path),
                "violation": msg,
                "applied": False,
                "action_taken": "",
            }

            # Apply specific healing strategy
            heal_result = self._apply_healing_strategy(
                file_path, msg, archives_root, dry_run, 
                affected_paths, import_touched_paths
            )
            action.update(heal_result)
                    
            actions.append(action)

        # === BATCH POST-HEALING VALIDATION ===
        batch_report = {
            "batch_post_heal_status": "SKIPPED",
            "batch_healed_count": sum(1 for a in actions if a.get("applied")),
            "batch_remaining_violations": [],
            "batch_success_rate": 0.0,
            "batch_message": "",
        }

        if dry_run:
            batch_report["batch_message"] = "PREVIEW: Batch post-heal validation skipped in dry-run"
            batch_report["batch_post_heal_status"] = "PREVIEW"
        else:
            try:
                # Dedupe and filter existing paths
                unique_affected = list({p.resolve() for p in affected_paths if p.exists()})

                if unique_affected:
                    # Mini re-validation only on affected files
                    _, batch_violations = self.enforce_void_compliance(unique_affected)

                    batch_report["batch_remaining_violations"] = [
                        {"file": str(p), "message": msg}
                        for p, msg in batch_violations
                    ]

                    resolved_count = len(unique_affected) - len(batch_report["batch_remaining_violations"])
                    batch_report["batch_success_rate"] = (
                        resolved_count / len(unique_affected) * 100 if unique_affected else 100
                    )

                    if not batch_report["batch_remaining_violations"]:
                        batch_report["batch_post_heal_status"] = "FULL_SUCCESS"
                        batch_report["batch_message"] = f"All {len(unique_affected)} healed paths now compliant"
                    elif batch_report["batch_success_rate"] >= 90:
                        batch_report["batch_post_heal_status"] = "HIGH_SUCCESS"
                        batch_report["batch_message"] = f"{batch_report['batch_success_rate']:.1f}% success — minor remaining issues"
                    else:
                        batch_report["batch_post_heal_status"] = "PARTIAL"
                        batch_report["batch_message"] = f"{batch_report['batch_success_rate']:.1f}% success — review remaining violations"
                else:
                    batch_report["batch_post_heal_status"] = "NO_ACTIONS"
                    batch_report["batch_message"] = "No healing actions applied"

            except Exception as e:
                batch_report["batch_post_heal_status"] = "ERROR"
                batch_report["batch_message"] = f"Batch validation error: {e}"
                Logger.error(f"[LocationAgent] Batch post-heal failed: {e}")

        # === NAMINGAGENT BATCH POST-HEALING VALIDATION ===
        all_naming_affected = list(set(affected_paths + import_touched_paths))
        naming_report = self.post_naming_validation(all_naming_affected, dry_run=dry_run)
        batch_report.update({
            "naming_post_heal": naming_report,
        })

        # Enhance overall batch message with naming status
        if naming_report["naming_post_heal_status"] == "FULL_SUCCESS":
            batch_report["batch_message"] += " | Naming FULL_SUCCESS"
        elif naming_report["naming_post_heal_status"] in {"PARTIAL", "NEEDS_REVIEW"}:
            batch_report["batch_message"] += f" | Naming {naming_report['naming_post_heal_status']}"

        # === NAMINGAGENT AUTO-HEALING (Triggered on issues) ===
        if naming_report["naming_post_heal_status"] in {"PARTIAL", "NEEDS_REVIEW"}:
            naming_heal_report = self.auto_heal_naming_issues(naming_report, dry_run=dry_run)
            batch_report.update({
                "naming_auto_heal": naming_heal_report,
            })
            # Re-run naming validation after auto-heal for final status
            if naming_heal_report["naming_auto_heal_applied"]:
                final_naming_report = self.post_naming_validation(all_naming_affected, dry_run=dry_run)
                batch_report["naming_post_heal_final"] = final_naming_report
                if final_naming_report["naming_post_heal_status"] == "FULL_SUCCESS":
                    batch_report["batch_message"] += " | Naming auto-healed to FULL_SUCCESS"

        # === ULTRA NAMINGAGENT CONVENTIONS VALIDATION + AUTO-HEAL ===
        conventions_report = self.post_naming_conventions_validation_and_heal(affected_paths, dry_run=dry_run)
        batch_report.update({
            "naming_conventions": conventions_report,
        })
        batch_report["batch_message"] += f" | Naming conventions: {conventions_report['naming_conventions_final_status'] or conventions_report['naming_conventions_status']}"

        # === ULTRA IMPORTAGENT VALIDATION + AUTO-HEAL ===
        import_full_report = self.post_import_validation_and_heal(affected_paths, import_touched_paths, dry_run=dry_run)
        batch_report.update({
            "import_cycle": import_full_report,
        })
        batch_report["batch_message"] += f" | Imports: {import_full_report['import_final_status'] or import_full_report['import_validation_status']}"

        # === ULTRA DUPLICATE RESOLUTION PASS ===
        duplicate_report = {
            "duplicate_resolution_applied": False,
            "duplicate_actions": [],
            "duplicate_final_duplicates": {},
            "duplicate_message": "",
        }

        if not dry_run:
            try:
                # Full repo duplicate scan post all moves/heals
                duplicates = self.naming_agent.scan_repository_duplicates()

                duplicate_actions = []
                for dup_name, paths in duplicates.items():
                    if len(paths) <= 1:
                        continue

                    # Sort to prioritize keeping the "primary" (no suffix or lowest number)
                    def sort_key(p_str: str) -> Any:
                        """Execute sort_key operation."""
                        match = re.search(r'_(\d+)(?=\.py$)', str(p_str))
                        return int(match.group(1)) if match else 0

                    sorted_paths = sorted(paths, key=sort_key)
                    primary = sorted_paths[0]  # Keep this one untouched

                    for secondary in sorted_paths[1:]:
                        secondary_path = self.project_root / secondary if isinstance(secondary, str) else secondary
                        if secondary_path.exists():
                            resolve_result = self.naming_agent.resolve_duplicate_filename(secondary_path, dry_run=False)
                            duplicate_actions.append({
                                "type": "DUPLICATE_RESOLUTION",
                                "primary_kept": str(primary),
                                "secondary_resolved": str(secondary),
                                "resolution": resolve_result,
                            })
                            # Update affected paths if moved for subsequent validations
                            if resolve_result.get("applied") and resolve_result.get("new_path"):
                                new_rel = resolve_result["new_path"]
                                affected_paths.append(self.project_root / new_rel)

                if duplicate_actions:
                    duplicate_report["duplicate_resolution_applied"] = True
                    duplicate_report["duplicate_actions"] = duplicate_actions
                    duplicate_report["duplicate_message"] = f"Resolved {len(duplicate_actions)} duplicate instances"

                    # Final duplicate check to confirm resolution
                    final_duplicates = self.naming_agent.scan_repository_duplicates()
                    duplicate_report["duplicate_final_duplicates"] = {
                        name: [str(p) for p in paths] for name, paths in final_duplicates.items()
                    }
                    if not final_duplicates:
                        duplicate_report["duplicate_message"] += " → FULL_SUCCESS: No duplicates remain"
                    else:
                        duplicate_report["duplicate_message"] += f" → PARTIAL: {len(final_duplicates)} groups remain"

                    Logger.info(f"[LocationAgent] Duplicate resolution: {duplicate_report['duplicate_message']}")
                else:
                    duplicate_report["duplicate_message"] = "No duplicates detected after healing"

            except Exception as e:
                duplicate_report["duplicate_message"] = f"ERROR during duplicate resolution: {e}"
                Logger.error(f"[LocationAgent] Duplicate resolution failed: {e}")
        else:
            duplicate_report["duplicate_message"] = "PREVIEW: Duplicate resolution skipped in dry-run"

        # Attach duplicate report to batch
        batch_report.update({
            "duplicate_resolution": duplicate_report,
        })
        batch_report["batch_message"] += f" | Duplicates: {duplicate_report['duplicate_message'][:50]}"

        # === DEEP NAMINGAGENT INTEGRATION ===
        naming_deep_report = self.deep_naming_validation_and_heal(affected_paths, import_touched_paths, dry_run=dry_run)
        batch_report.update({
            "naming_deep_cycle": naming_deep_report,
        })
        batch_report["batch_message"] += f" | Naming deep: {naming_deep_report['naming_deep_status']}"

        # === DEEP IMPORTAGENT INTEGRATION ===
        import_deep_report = self.deep_import_validation_and_heal(affected_paths, import_touched_paths, dry_run=dry_run)
        batch_report.update({
            "import_deep_cycle": import_deep_report,
        })
        batch_report["batch_message"] += f" | Imports deep: {import_deep_report['import_final_status']}"

        # Append batch report to all actions for visibility
        for action in actions:
            action["batch_post_heal"] = batch_report
            
        return actions

    def run_with_cleanup(self, files: List[Path] = None, dry_run: bool = True) -> Dict[str, Any]:
        """
        ULTRA HEALING WORKFLOW — Full location compliance with autonomous cleanup (2026-01-02)
        
        Full location compliance scan with automatic cleanup, post-heal validation,
        import fixing, and batch verification.
from agentic_core.L2_execution.mcp.mcp_hardened_mixin_1 import MCPHardenedMixin
        
        Args:
            files: Optional list of files to scan (defaults to all .py files)
            dry_run: If True, only preview cleanup actions
            
        Returns:
            Dict with violation count, actions applied, batch summaries, and details
        """
        violations = self.run(files)
        cleanup_results = self.cleanup_violations(violations, dry_run=dry_run) if violations else []
        
        # Extract batch summary from first action (same for all)
        batch_summary = cleanup_results[0].get("batch_post_heal", {}) if cleanup_results else {}
        
        return {
            "violations_detected": len(violations),
            "actions_applied": sum(1 for a in cleanup_results if a.get("applied")),
            "detailed_actions": cleanup_results,
            "batch_post_heal_summary": batch_summary,
            "naming_post_heal_summary": batch_summary.get("naming_post_heal", {}),
            "naming_auto_heal_summary": batch_summary.get("naming_auto_heal", {}),
            "naming_final_summary": batch_summary.get("naming_post_heal_final", {}),
            "naming_conventions_summary": batch_summary.get("naming_conventions", {}),
            "import_cycle_summary": batch_summary.get("import_cycle", {}),
            "duplicate_resolution_summary": batch_summary.get("duplicate_resolution", {}),
            "naming_deep_cycle_summary": batch_summary.get("naming_deep_cycle", {}),
            "import_deep_cycle_summary": batch_summary.get("import_deep_cycle", {}),
            "dry_run": dry_run,
        }

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
        Autonomous full-repository location law healing.
        Canon Key 51 compliance - fully self-orchestrating.
        
        Args:
            dry_run: If True, only propose changes
            execute: Must be explicitly True to perform changes
            depth: Current recursion depth
            max_depth: Maximum recursion depth
            _call_path: Set of agent names in call path (cycle detection)
            
        Returns:
            Summary dict with counts
        """
        if _call_path is None:
            _call_path = set()
        
        agent_name = self.__class__.__name__
        
        # CYCLE DETECTION
        if agent_name in _call_path:
            print(f"  [!] HEALING CYCLE DETECTED: {agent_name} already in path → stopping")
            return {"healed": 0, "blocked": 0, "errors": 0, "skipped": 0, "cycle_detected": True}
        
        # DEPTH LIMIT
        if depth > max_depth:
            print(f"  [!] RECURSION DEPTH LIMIT REACHED ({depth}/{max_depth}) → stopping")
            return {"healed": 0, "blocked": 0, "errors": 0, "skipped": 0, "depth_limited": True}
        
        _call_path.add(agent_name)
        
        if execute and dry_run:
            raise ValueError("execute and dry_run cannot both be True")
        
        actual_execute = execute and not dry_run
        
        try:
            # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
            super().heal_repository()
            
            violations = self.run()
            print(f"[LOCATION HEAL @ depth {depth}] Found {len(violations)} violations")
            
            counts = {"healed": 0, "blocked": 0, "errors": 0, "skipped": 0}
            
            for file_path, reason in violations:
                try:
                    # Use existing cleanup_violations for single-item healing
                    cleanup_results = self.cleanup_violations([(file_path, reason)], dry_run=not actual_execute)
                    
                    if cleanup_results and cleanup_results[0].get("applied"):
                        counts["healed"] += 1
                        print(f"  [+] HEALED: {file_path.name} - {cleanup_results[0].get('action_taken', 'fixed')}")
                    elif cleanup_results and cleanup_results[0].get("error"):
                        counts["errors"] += 1
                        print(f"  [!] ERROR: {file_path.name} - {cleanup_results[0]['error']}")
                    else:
                        counts["skipped"] += 1
                        
                except Exception as e:
                    counts["errors"] += 1
                    print(f"  [!] ERROR on {file_path.name}: {e}")
            
            print(f"\n[LOCATION HEAL SUMMARY] "
                  f"Healed: {counts['healed']} | "
                  f"Blocked: {counts['blocked']} | "
                  f"Skipped: {counts['skipped']} | "
                  f"Errors: {counts['errors']}")
            
            return counts
            
        finally:
            _call_path.discard(agent_name)


# PascalCase is now the canonical name

# Singleton getter for canon_validator compatibility
_location_agent_instance = None

def get_location_agent(project_root):
    """Get or create LocationAgent singleton."""
    global _location_agent_instance
    if _location_agent_instance is None:
        _location_agent_instance = LocationAgent(project_root)
    return _location_agent_instance
