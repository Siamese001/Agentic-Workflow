"""
SSOT Relocator - Automated Violation Remediation

Replaces 4 manual relocation scripts with a single, reusable library:
- phase2_gravity_relocation.py
- phase4_final_gravity_relocation.py
- phase4_final_observability_relocation.py
- phase4_perfection_absolute.py

Provides automated remediation for:
1. Drift violations (orphaned folders → archives)
2. Hierarchy violations (excessive depth → flattening)
3. Gravity violations (wrong layer → correct layer)
"""

from __future__ import annotations
import re
import shutil
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
from dataclasses import dataclass

from agentic_core.config.blueprint_sovereign.structure_blueprint_1 import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)

# Define ARCHIVES_DIR if not in structure_blueprint
try:
    from agentic_core.config.blueprint_sovereign.structure_blueprint_1 import ARCHIVES_DIR
except ImportError:
    ARCHIVES_DIR = Path("archives")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class RelocationResult:
    """Result of a single relocation operation."""
    source: str
    target: str
    success: bool
    action: str  # 'MOVED', 'ARCHIVED', 'FLATTENED', 'SKIPPED'
    error: Optional[str] = None
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class EnforcementReport:
    """Summary of enforcement operations."""
    total_operations: int = 0
    successful: int = 0
    failed: int = 0
    skipped: int = 0
    results: List[RelocationResult] = None
    
    def __post_init__(self):
        if self.results is None:
            self.results = []
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_operations == 0:
            return 100.0
        return (self.successful / self.total_operations) * 100


class SSOTRelocator:
    """
    Automated SSOT violation remediation with multi-layer safety checks.
    
    Provides reusable methods for fixing violations detected by UnifiedSSOTValidator:
    - relocate_orphans(): Move drift violations to archives
    - enforce_hierarchy(): Flatten folders exceeding depth limits
    - relocate_agents(): Move agents to correct layers
    
    Safety Features:
    - Protected path whitelist (knowledge, coordinators, L0_maintenance, SSOT)
    - Active dependency scanning before archival
    - Dry-run mode by default
    """
    
    # Protected paths that should never be archived
    PROTECTED_PATHS: Set[str] = {"knowledge", "coordinators", "L0_maintenance", "SSOT", "bases"}
    
    def __init__(
        self,
        project_root: Path,
        dry_run: bool = True,
        log_file: Optional[Path] = None
    ):
        """
        Initialize SSOT relocator.
        
        Args:
            project_root: Root directory of the project
            dry_run: If True, preview operations without executing
            log_file: Path to enforcement history log
        """
        self.project_root = project_root.resolve()
        self.dry_run = dry_run
        
        # Setup logging
        if log_file is None:
            log_dir = project_root / AGENTIC_CORE_DIR / 'L0_maintenance' / 'logs'
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / 'enforcement_history.log'
        
        self.log_file = log_file
        
        # Setup file handler for enforcement logging (UTF-8 encoding for Windows)
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        logger.addHandler(file_handler)
        
        # Archive root
        self.archive_root = project_root / ARCHIVES_DIR / 'unmapped_drift'
        if not dry_run:
            self.archive_root.mkdir(parents=True, exist_ok=True)
    
    def relocate_orphans(self, drift_violations: List[Any]) -> EnforcementReport:
        """
        Move orphaned folders (drift violations) to archives.
        
        Args:
            drift_violations: List of DriftViolation objects from validator
            
        Returns:
            EnforcementReport with operation results
        """
        report = EnforcementReport()
        
        logger.info(f"{'[DRY-RUN] ' if self.dry_run else ''}Starting orphan relocation")
        logger.info(f"Target violations: {len(drift_violations)}")
        
        for violation in drift_violations:
            source = self.project_root / violation.folder_path
            
            # Create timestamped archive path
            timestamp = datetime.now().strftime("%Y%m%d")
            archive_path = self.archive_root / timestamp / violation.folder_path
            
            result = self._relocate_folder(
                source=source,
                target=archive_path,
                action='ARCHIVED'
            )
            
            report.results.append(result)
            report.total_operations += 1
            
            if result.success:
                report.successful += 1
            elif result.action == 'SKIPPED':
                report.skipped += 1
            else:
                report.failed += 1
        
        logger.info(
            f"Orphan relocation complete: "
            f"{report.successful}/{report.total_operations} successful"
        )
        
        return report
    
    def enforce_hierarchy(self, hierarchy_violations: List[Any]) -> EnforcementReport:
        """
        Flatten folders exceeding depth limits.
        
        Moves files from deep folders to parent folders within depth limits.
        
        Args:
            hierarchy_violations: List of HierarchyViolation objects from validator
            
        Returns:
            EnforcementReport with operation results
        """
        report = EnforcementReport()
        
        logger.info(f"{'[DRY-RUN] ' if self.dry_run else ''}Starting hierarchy enforcement")
        logger.info(f"Target violations: {len(hierarchy_violations)}")
        
        for violation in hierarchy_violations:
            source = self.project_root / violation.folder_path
            
            if not source.exists():
                result = RelocationResult(
                    source=str(source),
                    target="N/A",
                    success=False,
                    action='SKIPPED',
                    error="Source does not exist"
                )
                report.results.append(result)
                report.total_operations += 1
                report.skipped += 1
                continue
            
            # Calculate target path (flatten to max depth)
            parts = Path(violation.folder_path).parts
            target_parts = parts[:violation.max_depth + 1]  # +1 for root folder
            target = self.project_root / Path(*target_parts)
            
            # Move contents to flattened location
            result = self._flatten_folder(
                source=source,
                target=target,
                max_depth=violation.max_depth
            )
            
            report.results.append(result)
            report.total_operations += 1
            
            if result.success:
                report.successful += 1
            elif result.action == 'SKIPPED':
                report.skipped += 1
            else:
                report.failed += 1
        
        logger.info(
            f"Hierarchy enforcement complete: "
            f"{report.successful}/{report.total_operations} successful"
        )
        
        return report
    
    def relocate_agents(
        self,
        gravity_violations: List[Any]
    ) -> EnforcementReport:
        """
        Move agents to their correct layers (gravity violation remediation).
        
        Args:
            gravity_violations: List of GravityViolation objects from validator
            
        Returns:
            EnforcementReport with operation results
        """
        report = EnforcementReport()
        
        logger.info(f"{'[DRY-RUN] ' if self.dry_run else ''}Starting agent relocation")
        logger.info(f"Target violations: {len(gravity_violations)}")
        
        for violation in gravity_violations:
            source = self.project_root / violation.file_path
            
            # Calculate target path (replace actual layer with assigned layer)
            target_path = violation.file_path.replace(
                f"/{violation.actual_layer}/",
                f"/{violation.assigned_layer}/"
            )
            target = self.project_root / target_path
            
            result = self._relocate_file(
                source=source,
                target=target,
                action='MOVED'
            )
            
            report.results.append(result)
            report.total_operations += 1
            
            if result.success:
                report.successful += 1
            elif result.action == 'SKIPPED':
                report.skipped += 1
            else:
                report.failed += 1
        
        logger.info(
            f"Agent relocation complete: "
            f"{report.successful}/{report.total_operations} successful"
        )
        
        return report
    
    def _relocate_file(
        self,
        source: Path,
        target: Path,
        action: str = 'MOVED'
    ) -> RelocationResult:
        """
        Relocate a single file with safety checks.
        
        Args:
            source: Source file path
            target: Target file path
            action: Action description
            
        Returns:
            RelocationResult with operation details
        """
        result = RelocationResult(
            source=str(source.relative_to(self.project_root)),
            target=str(target.relative_to(self.project_root)),
            success=False,
            action=action
        )
        
        # Safety checks
        if not source.exists():
            result.error = "Source file does not exist"
            result.action = 'SKIPPED'
            return result
        
        if target.exists():
            result.error = "Target file already exists"
            result.action = 'SKIPPED'
            return result
        
        # Execute or preview
        if self.dry_run:
            result.success = True
            result.action = f'{action} (DRY-RUN)'
            logger.info(f"[DRY-RUN] Would {action.lower()}: {result.source} → {result.target}")
        else:
            try:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(source), str(target))
                result.success = True
                logger.info(f"{action}: {result.source} → {result.target}")
                
                # Clean up empty parent directories
                self._cleanup_empty_dirs(source.parent)
            except Exception as e:
                result.error = str(e)
                logger.error(f"Failed to {action.lower()} {result.source}: {e}")
        
        return result
    
    def _relocate_folder(
        self,
        source: Path,
        target: Path,
        action: str = 'MOVED'
    ) -> RelocationResult:
        """
        Relocate an entire folder with multi-layer safety checks.
        
        Safety Layers:
        1. Whitelist Protection: Blocks protected system paths
        2. Active Dependency Scan: Checks for active imports
        3. Standard validation: Existence and conflict checks
        
        Args:
            source: Source folder path
            target: Target folder path
            action: Action description
            
        Returns:
            RelocationResult with operation details
        """
        result = RelocationResult(
            source=str(source.relative_to(self.project_root)),
            target=str(target.relative_to(self.project_root)),
            success=False,
            action=action
        )
        
        # Layer 1: Whitelist Protection
        folder_name = source.name
        normalized_path = str(source.relative_to(self.project_root)).replace("\\", "/").lower()
        
        if any(protected.lower() in normalized_path for protected in self.PROTECTED_PATHS):
            result.error = f"[SAFETY_BLOCK] Protected system path: {folder_name}"
            result.action = 'BLOCKED'
            logger.warning(f"[SAFETY_BLOCK] Refusing to archive protected path: {source}")
            return result
        
        # Layer 2: Active Dependency Scan (HARD BLOCKER - applies to ALL actions)
        if self._is_active_dependency(folder_name):
            result.error = (
                f"[SAFETY_BLOCK] Active imports detected for '{folder_name}'. "
                f"Cannot relocate folders with active dependencies. "
                f"Required steps: (1) Deprecate all imports, (2) Update dependent code, (3) Verify no imports remain, (4) Then archive."
            )
            result.action = 'BLOCKED'
            logger.error(
                f"[SAFETY_BLOCK] HARD BLOCK: '{folder_name}' has active imports in the codebase. "
                f"Relocation denied. Imports must be deprecated and removed before archival."
            )
            return result
        
        # Layer 3: Standard Safety checks
        if not source.exists():
            result.error = "Source folder does not exist"
            result.action = 'SKIPPED'
            return result
        
        if target.exists():
            result.error = "Target folder already exists"
            result.action = 'SKIPPED'
            return result
        
        # Execute or preview
        if self.dry_run:
            result.success = True
            result.action = f'{action} (DRY-RUN)'
            logger.info(f"[DRY-RUN] Would {action.lower()}: {result.source} → {result.target}")
        else:
            try:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(source), str(target))
                result.success = True
                logger.info(f"{action}: {result.source} → {result.target}")
            except Exception as e:
                result.error = str(e)
                logger.error(f"Failed to {action.lower()} {result.source}: {e}")
        
        return result
    
    def _flatten_folder(
        self,
        source: Path,
        target: Path,
        max_depth: int
    ) -> RelocationResult:
        """
        Flatten a folder by moving its contents to a shallower location.
        
        Args:
            source: Source folder path (too deep)
            target: Target folder path (within depth limit)
            max_depth: Maximum allowed depth
            
        Returns:
            RelocationResult with operation details
        """
        result = RelocationResult(
            source=str(source.relative_to(self.project_root)),
            target=str(target.relative_to(self.project_root)),
            success=False,
            action='FLATTENED'
        )
        
        if not source.exists():
            result.error = "Source folder does not exist"
            result.action = 'SKIPPED'
            return result
        
        # Execute or preview
        if self.dry_run:
            result.success = True
            result.action = 'FLATTENED (DRY-RUN)'
            logger.info(f"[DRY-RUN] Would flatten: {result.source} -> {result.target}")
        else:
            try:
                target.mkdir(parents=True, exist_ok=True)
                
                # Move all files from source to target
                for item in source.rglob('*'):
                    if item.is_file():
                        rel_path = item.relative_to(source)
                        target_file = target / rel_path.name  # Flatten structure
                        
                        if not target_file.exists():
                            target_file.parent.mkdir(parents=True, exist_ok=True)
                            shutil.move(str(item), str(target_file))
                
                # Remove empty source folder
                if source.exists() and not any(source.iterdir()):
                    source.rmdir()
                
                result.success = True
                logger.info(f"FLATTENED: {result.source} -> {result.target}")
            except Exception as e:
                result.error = str(e)
                logger.error(f"Failed to flatten {result.source}: {e}")
        
        return result
    
    def _is_active_dependency(self, module_name: str) -> bool:
        """
        Scan the entire workspace for Python files importing the specified module.
        
        Args:
            module_name: Name of the module/folder to check for imports
            
        Returns:
            True if active imports are found, False otherwise
        """
        # Search patterns for typical Python imports
        # Match both direct imports and full path imports
        escaped_name = re.escape(module_name)
        patterns = [
            # Direct import: import knowledge
            re.compile(rf"^\s*import\s+{escaped_name}\b", re.MULTILINE),
            # From import: from knowledge import ...
            re.compile(rf"^\s*from\s+{escaped_name}\b.*import", re.MULTILINE),
            # Full path import: from agentic_core.knowledge import ...
            re.compile(rf"^\s*from\s+\S*\.{escaped_name}\b.*import", re.MULTILINE),
            # Full path import: import agentic_core.knowledge
            re.compile(rf"^\s*import\s+\S*\.{escaped_name}\b", re.MULTILINE),
            # Nested path: from agentic_core.knowledge.something import ...
            re.compile(rf"^\s*from\s+\S*\.{escaped_name}\.\S+.*import", re.MULTILINE),
        ]
        
        root_dir = self.project_root
        checked_files = 0
        for py_file in root_dir.rglob("*.py"):
            # Skip the archive folder itself
            if "archives" in py_file.parts:
                continue
            
            checked_files += 1
            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                for pat in patterns:
                    if pat.search(content):
                        logger.debug(f"[DEP_FOUND] {module_name} is imported by {py_file}")
                        return True
            except Exception:
                continue
        
        logger.debug(f"[DEP_SCAN] Checked {checked_files} files for '{module_name}', no imports found")
        return False
    
    def _cleanup_empty_dirs(self, directory: Path) -> None:
        """
        Recursively remove empty parent directories.
        
        Args:
            directory: Directory to check and clean up
        """
        if not directory.exists() or not directory.is_dir():
            return
        
        try:
            # Check if directory is empty
            if not any(directory.iterdir()):
                directory.rmdir()
                logger.info(f"Cleaned up empty directory: {directory}")
                
                # Recursively clean parent
                self._cleanup_empty_dirs(directory.parent)
        except (OSError, PermissionError):
            # Directory not empty or permission denied
            pass
