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
from typing import List, Tuple, Dict, Any
from datetime import datetime
import re
import shutil
import logging

logger = logging.getLogger(__name__)

from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    ROOT_WHITELIST,                    # = set(sovereign_registry.keys())
    FORBIDDEN_ROOT_FOLDERS,
    FORBIDDEN_FOLDER_PATTERN,          # ^\\d+_
    SOVEREIGN_REGISTRY,
    ROOT_PROTECTED_FILES,
    TESTS_ROOT_FILE_WHITELIST,
)
# [PHASE 20] DEPRECATION: void_compliance_helpers.py removed - inline implementation
def is_excepted_from_key(key_id: int, file_path, line_content: str = '') -> bool:
    """Check if file/line is excepted from key validation."""
    import fnmatch
    import re
    from agentic_core.config.blueprint_sovereign.structure_blueprint import CANON_KEY_EXCEPTIONS
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


class LocationAgent:
    """
    Autonomous agent responsible for territorial integrity.
    Run independently or as first stage in compliance orchestrator.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()

    def validate_sovereign_roots(self) -> List[Tuple[Path, str]]:
        """Ensure all required sovereign roots exist and are directories."""
        violations: List[Tuple[Path, str]] = []
        for root_name in ROOT_WHITELIST:
            root_path = self.project_root / root_name
            if not root_path.exists():
                violations.append((root_path, f"Missing sovereign root: {root_name}"))
            elif not root_path.is_dir():
                violations.append((root_path, f"Sovereign root is not a directory: {root_name}"))
        return violations

    def validate_file_location(self, file_path: Path) -> Tuple[bool, str]:
        """Per-file location validation with correct forbidden-check ordering."""
        try:
            rel_path = file_path.relative_to(self.project_root)
            parts = rel_path.parts
            root_folder = parts[0]
        except ValueError:
            return False, "VOID VIOLATION: File outside project root"

        # === EARLY FORBIDDEN PATTERN REJECTION (fixed original dead-code bug) ===
        for part in parts:
            if part in FORBIDDEN_ROOT_FOLDERS:
                return False, f"VOID VIOLATION: Forbidden folder '{part}' at any depth"
            
            # Check for regex pattern match if applicable
            if hasattr(FORBIDDEN_FOLDER_PATTERN, 'match'):
                if FORBIDDEN_FOLDER_PATTERN.match(part):
                    return False, f"VOID VIOLATION: Numbered folder pattern '{part}' forbidden"

        # Numbered root folders (e.g., 08_scripts) forbidden
        if len(root_folder) >= 3 and root_folder[:2].isdigit() and root_folder[2:3] == "_":
            return False, f"VOID VIOLATION: Numbered root folder '{root_folder}' not approved"

        # Root whitelist enforcement
        if root_folder not in ROOT_WHITELIST:
            return False, f"VOID VIOLATION: Unapproved root folder '{root_folder}'"

        # === DEPTH ENFORCEMENT FROM SSOT ===
        expected_depth = SOVEREIGN_REGISTRY.get(root_folder, {}).get("depth")
        actual_depth = len(parts) - 1  # exclude filename

        if expected_depth is not None and actual_depth != expected_depth:
            reason = "SHALLOW" if actual_depth < expected_depth else "DEEP"
            return False, f"{reason} VIOLATION ({root_folder}): depth {actual_depth} != {expected_depth}"

        # Special strict depth for agentic_core (Canon Key 3/12 hardening)
        if root_folder == "agentic_core":
            if len(parts) != 4:
                return False, f"AGENTIC_CORE DEPTH VIOLATION: {rel_path} has {len(parts)} parts (expected exactly 4: root/L1/L2/file.py)"

        # Root-level file protections (Key 0)
        if len(parts) == 1 and file_path.suffix == ".py":
            if file_path.name in ROOT_PROTECTED_FILES:
                return True, "Protected sovereign root file (Key 0 exempt)"
            if root_folder == "tests" and file_path.name in TESTS_ROOT_FILE_WHITELIST:
                return True, "Whitelisted tests root file"

        # Gravity leak: compliance/validation logic must not appear in downstream apps
        compliance_markers = {"validator", "compliance", "canon", "enforcer", "auditor"}
        if root_folder.startswith("apps_") and any(marker in file_path.stem.lower() for marker in compliance_markers):
            return False, f"GRAVITY ERROR: Sovereign compliance logic leaked into downstream '{root_folder}'"

        return True, f"Location compliant in sovereign territory: {root_folder}"

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
        Returns all violations (missing roots + per-file).
        Suitable as first-stage gatekeeper in orchestrator.
        """
        all_violations: List[Tuple[Path, str]] = []

        # 1. Check sovereign root existence
        all_violations.extend(self.validate_sovereign_roots())

        # 2. Scan files
        if files is None:
            files = list(self.project_root.rglob("*.py"))

        _, file_violations = self.enforce_void_compliance(files)
        all_violations.extend(file_violations)

        return all_violations


    # SUPPLEMENTED FROM FilesystemAgent — enhances backup + cleanup capability — merged 2025-12-30
    def _init_backup_dir(self) -> Path:
        """
        SUPPLEMENTED FROM FilesystemAgent — merged 2025-12-30
        Initialize backup directory for safe mutations.
        """
        backup_dir = self.project_root / ".sovereign_healing_backup" / "location" / datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir.mkdir(parents=True, exist_ok=True)
        return backup_dir

    def _backup_file(self, file_path: Path, backup_dir: Path = None) -> Path:
        """
        SUPPLEMENTED FROM FilesystemAgent — merged 2025-12-30
        Create a physical safety copy before mutation.
        
        Args:
            file_path: File to backup
            backup_dir: Optional backup directory (auto-created if None)
            
        Returns:
            Path to the backup file
        """
        if backup_dir is None:
            backup_dir = self._init_backup_dir()
            
        rel = file_path.relative_to(self.project_root)
        backup_path = backup_dir / rel
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, backup_path)
        logger.info(f"[LocationAgent] Backed up: {rel}")
        return backup_path

    def cleanup_violations(
        self, 
        violations: List[Tuple[Path, str]], 
        dry_run: bool = True,
        max_actions: int = 50
    ) -> List[Dict[str, Any]]:
        """
        SUPPLEMENTED FROM FilesystemAgent — merged 2025-12-30
        
        Execute autonomous cleanup of location violations.
        Relocates violating files to archives/ with proper categorization.
        
        Args:
            violations: List of (path, reason) tuples
            dry_run: If True, only preview actions without executing
            max_actions: Maximum number of cleanup actions per run
            
        Returns:
            List of action dicts with results
        """
        actions = []
        archives_root = self.project_root / "archives"
        backup_dir = None if dry_run else self._init_backup_dir()
        
        for i, (file_path, msg) in enumerate(violations):
            if i >= max_actions:
                logger.warning(f"[LocationAgent] Cleanup budget exhausted ({max_actions} actions).")
                break
                
            action = {
                "type": "LOCATION_CLEANUP",
                "file": str(file_path),
                "violation": msg,
                "applied": False,
                "action_taken": "",
            }
            
            # Determine archive target based on violation type
            if "VOID VIOLATION" in msg or "GRAVITY ERROR" in msg:
                target_subdir = archives_root / "void_violations"
            elif "DEPTH VIOLATION" in msg:
                target_subdir = archives_root / "depth_violations"
            else:
                target_subdir = archives_root / "location_violations"
                
            target_path = target_subdir / file_path.name
            
            if dry_run:
                action["applied"] = True
                action["action_taken"] = f"PREVIEW: Would archive to {target_path.relative_to(self.project_root)}"
            else:
                try:
                    target_subdir.mkdir(parents=True, exist_ok=True)
                    self._backup_file(file_path, backup_dir)
                    
                    # Handle collision
                    if target_path.exists():
                        stem = target_path.stem
                        suffix = target_path.suffix
                        counter = 1
                        while target_path.exists():
                            target_path = target_subdir / f"{stem}_{counter}{suffix}"
                            counter += 1
                    
                    file_path.rename(target_path)
                    action["applied"] = True
                    action["action_taken"] = f"ARCHIVED: {target_path.relative_to(self.project_root)}"
                    logger.info(f"[LocationAgent] Archived: {file_path.name}")
                except Exception as e:
                    action["error"] = str(e)
                    
            actions.append(action)
            
        return actions

    def run_with_cleanup(self, files: List[Path] = None, dry_run: bool = True) -> Dict[str, Any]:
        """
        SUPPLEMENTED FROM FilesystemAgent — merged 2025-12-30
        
        Full location compliance scan with automatic cleanup.
        
        Args:
            files: Optional list of files to scan (defaults to all .py files)
            dry_run: If True, only preview cleanup actions
            
        Returns:
            Dict with violation count, actions applied, and details
        """
        violations = self.run(files)
        cleanup_results = self.cleanup_violations(violations, dry_run=dry_run) if violations else []
        
        return {
            "violations_detected": len(violations),
            "actions_applied": sum(1 for a in cleanup_results if a.get("applied")),
            "detailed_actions": cleanup_results,
            "dry_run": dry_run,
        }


# PascalCase is now the canonical name
