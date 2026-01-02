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
from typing import List, Tuple, Dict, Any
from datetime import datetime
import re
import shutil
import logging
import ast

Logger = logging.getLogger(__name__)

from agentic_core.config.blueprint_sovereign.structure_blueprint import (
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
)
from agentic_core.prompt_governance.version_registry.PromptRegistry import registers_prompt

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


from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin

@registers_prompt(
    template_name="file_placement.jinja",
    purpose="Enforces territory/file placement rules",
    territory="templates"
)
class LocationAgent(HealerMixin, MCPHardenedMixin):
    """
    Autonomous agent responsible for territorial integrity.
    Run independently or as first stage in compliance orchestrator.
    
    RCA FIX 2026-01-02: Added project root validation to prevent folder creation
    outside the active project root (e.g., C:\Git\ instead of C:\Git\Agentic-Workflow\)
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()
        # Validate project root is correct
        self._validate_project_root()

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
        """
        Safely create a directory within the project root.
        Validates path is within project before creation.
        """
        target = safe_path_join(self.project_root, relative_path)
        if not target.exists():
            target.mkdir(parents=True, exist_ok=True)
            Logger.info(f"[LocationAgent] Created directory: {target}")
        return target

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

        # === APP-SPECIFIC FILE REJECTION (Post-migration hardening) ===
        # Block any file with app-specific prefix/pattern if placed in agentic_core
        if root_folder == "agentic_core" and is_app_specific_file(file_path.name):
            correct_path = get_correct_app_path(file_path.name) or "appropriate apps_* folder"
            return False, (
                f"APP-SPECIFIC IN CORE VIOLATION: '{file_path.name}' is application-specific "
                f"and must not live in agentic_core. Move to '{correct_path}/'."
            )

        # === FORBIDDEN LAYER PREFIX REJECTION ===
        # Filenames should NOT begin with l1_, l2_, P1_, etc. - layer info belongs in folders
        forbidden_prefix = has_forbidden_layer_prefix(file_path.name)
        if forbidden_prefix:
            return False, (
                f"LAYER PREFIX VIOLATION: '{file_path.name}' begins with forbidden prefix '{forbidden_prefix}'. "
                f"Layer/priority info belongs in folder structure, not filenames. "
                f"Rename to remove the '{forbidden_prefix}' prefix."
            )

        # === BROKEN BACKUP FILE REJECTION ===
        # Files like .bak.174742 break archiving logic and sit unused
        if is_broken_backup_file(file_path.name):
            return False, (
                f"BROKEN BACKUP FILE: '{file_path.name}' matches forbidden backup pattern (.bak.NNNNNN). "
                f"These files break archiving logic. Delete or properly archive this file."
            )

        # === ULTRA AST VIOLATION CHECK (2026-01-02 Comprehensive Hardening) ===
        # Single-parse multi-signal analysis:
        #   1. App-specific domain leak (RG/LIC) → highest priority
        #   2. Internal core gravity (layer import direction)
        #   3. Territory semantic alignment (folder vs content)
        if root_folder == "agentic_core" and file_path.suffix == ".py":
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                tree = ast.parse(content)

                # Territory inference from path
                try:
                    rel_parts = file_path.relative_to(self.project_root / "agentic_core").parts
                    current_l1 = rel_parts[0] if len(rel_parts) > 1 else None
                    current_l2 = rel_parts[1] if len(rel_parts) > 2 else None
                    current_territory = f"{current_l1}/{current_l2}" if current_l2 else current_l1
                except ValueError:
                    current_l1, current_l2, current_territory = None, None, None

                # Scoring containers
                app_rg_score = 0.0
                app_lic_score = 0.0
                territory_scores: Dict[str, float] = {t: 0.0 for t in CORE_TERRITORY_KEYWORDS}

                # --- Import Resolution (Apps + Internal Core Gravity) ---
                forbidden_app_import = False
                forbidden_layer_import = None
                for node in ast.walk(tree):
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        modules = []
                        if isinstance(node, ast.Import):
                            modules = [alias.name for alias in node.names]
                        elif isinstance(node, ast.ImportFrom) and node.module:
                            modules = [node.module]

                        for module in modules:
                            if module.startswith(("apps_rg.", "apps_lic.")) or module in FORBIDDEN_APP_MODULES:
                                forbidden_app_import = True
                            if current_l1 and module.startswith("agentic_core.") and len(module.split(".")) > 2:
                                imported_l1 = module.split(".")[1]
                                if imported_l1 in LAYER_FORBIDDEN_IMPORTS.get(current_l1, set()):
                                    forbidden_layer_import = f"{current_l1} → {imported_l1}"
                    if forbidden_app_import or forbidden_layer_import:
                        break

                if forbidden_app_import:
                    return False, (
                        f"GRAVITY VIOLATION (AST-resolved): Imports from apps_* modules forbidden in agentic_core. "
                        f"Move file to correct apps_*/engines/ folder. File: {rel_path}"
                    )
                if forbidden_layer_import:
                    return False, (
                        f"INTERNAL GRAVITY VIOLATION: {forbidden_layer_import} import direction forbidden. "
                        f"Refactor to respect layer gravity or move file. File: {rel_path}"
                    )

                # --- Multi-Signal Semantic Scoring ---
                for node in ast.walk(tree):
                    # Class/Function names — full weight
                    if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                        name = node.name.lower()
                        if any(t in name for t in APP_RG_AST_TERMS):
                            app_rg_score += 1.0
                        if any(t in name for t in APP_LIC_AST_TERMS):
                            app_lic_score += 1.0
                        for terr, cats in CORE_TERRITORY_KEYWORDS.items():
                            for terms in cats.values():
                                if any(t in name for t in terms):
                                    territory_scores[terr] += 1.0

                    # Arguments — medium weight
                    elif isinstance(node, ast.arguments):
                        for arg in node.args + getattr(node, "kwonlyargs", []) + getattr(node, "posonlyargs", []):
                            if arg.arg and arg.arg not in {"self", "cls"}:
                                a = arg.arg.lower()
                                if any(t in a for t in APP_RG_VARIABLE_TERMS):
                                    app_rg_score += VARIABLE_HIT_WEIGHT
                                if any(t in a for t in APP_LIC_VARIABLE_TERMS):
                                    app_lic_score += VARIABLE_HIT_WEIGHT
                                for terr, cats in CORE_TERRITORY_KEYWORDS.items():
                                    for terms in cats.values():
                                        if any(t in a for t in terms):
                                            territory_scores[terr] += VARIABLE_HIT_WEIGHT

                    # Assignment targets — medium weight
                    elif isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                v = target.id.lower()
                                if any(t in v for t in APP_RG_VARIABLE_TERMS):
                                    app_rg_score += VARIABLE_HIT_WEIGHT
                                if any(t in v for t in APP_LIC_VARIABLE_TERMS):
                                    app_lic_score += VARIABLE_HIT_WEIGHT
                                for terr, cats in CORE_TERRITORY_KEYWORDS.items():
                                    for terms in cats.values():
                                        if any(t in v for t in terms):
                                            territory_scores[terr] += VARIABLE_HIT_WEIGHT

                    # String literals — low weight
                    elif isinstance(node, ast.Constant) and isinstance(node.value, str) and len(node.value) > 8:
                        text = node.value.lower()
                        app_rg_score += sum(1 for t in APP_RG_STRING_TERMS if t in text) * STRING_HIT_WEIGHT
                        app_lic_score += sum(1 for t in APP_LIC_STRING_TERMS if t in text) * STRING_HIT_WEIGHT
                        for terr, cats in CORE_TERRITORY_KEYWORDS.items():
                            for terms in cats.values():
                                territory_scores[terr] += sum(1 for t in terms if t in text) * STRING_HIT_WEIGHT

                # --- App-Specific Violation (Highest Priority) ---
                total_app_score = app_rg_score + app_lic_score
                if total_app_score >= AST_DOMAIN_HIT_THRESHOLD:
                    dominant = "apps_rg" if app_rg_score >= app_lic_score else "apps_lic"
                    target = get_correct_app_path(file_path.name) or f"{dominant}/{APP_SPECIFIC_TARGET_SUBFOLDER}"
                    return False, (
                        f"AST DOMAIN VIOLATION (app score {total_app_score:.2f}): "
                        f"Strong application signals (RG: {app_rg_score:.2f}, LIC: {app_lic_score:.2f}). "
                        f"Move to '{target}/'. File: {rel_path}"
                    )

                # --- Core Territory Alignment Check ---
                if current_territory and territory_scores:
                    current_score = territory_scores.get(current_territory, 0.0)
                    best_territory = max(territory_scores, key=territory_scores.get) if territory_scores else None
                    max_other = max((s for t, s in territory_scores.items() if t != current_territory), default=0.0)

                    if current_score < MIN_ALIGNMENT_SCORE and max_other >= MIN_ALIGNMENT_SCORE:
                        return False, (
                            f"TERRITORY ALIGNMENT WEAK: Current '{current_territory}' score {current_score:.2f} < {MIN_ALIGNMENT_SCORE}. "
                            f"Lacks semantic signals — refactor or move to '{best_territory}'. File: {rel_path}"
                        )
                    if max_other > current_score + TERRITORY_MISMATCH_THRESHOLD:
                        return False, (
                            f"TERRITORY MISMATCH VIOLATION: Stronger signals for '{best_territory}' ({max_other:.2f}) "
                            f"vs current ({current_score:.2f}). Move to agentic_core/{best_territory}. File: {rel_path}"
                        )

            except SyntaxError:
                Logger.debug(f"[LocationAgent] Syntax error in {file_path}")
            except Exception as e:
                Logger.debug(f"[LocationAgent] AST failure in {file_path}: {e}")

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
        Returns all violations (Missing roots + per-file).
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
        Logger.info(f"[LocationAgent] Backed up: {rel}")
        return backup_path

    def cleanup_violations(
        self, 
        violations: List[Tuple[Path, str]], 
        dry_run: bool = True,
        max_actions: int = 50
    ) -> List[Dict[str, Any]]:
        """
        SUPPLEMENTED FROM FilesystemAgent — merged 2025-12-30
        ENHANCED 2026-01-02: Intelligent healing for app leaks & territory mismatches
        
        Execute autonomous cleanup of location violations.
        - Archives void/depth/general violations
        - Auto-moves app-specific/domain leaks to correct apps_*/engines/
        - Auto-moves territory mismatches to semantically best agentic_core L1/L2
        - Archives broken backups / forbidden prefix files
        
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
                Logger.warning(f"[LocationAgent] Cleanup budget exhausted ({max_actions} actions).")
                break
            
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

            # === APP-SPECIFIC / AST DOMAIN LEAK HEALING ===
            if "APP-SPECIFIC IN CORE VIOLATION" in msg or "AST DOMAIN VIOLATION" in msg:
                target_match = re.search(r"Move to '([^']+)'", msg)
                if target_match:
                    relative_target = target_match.group(1).rstrip("/")
                    target_path = self.project_root / relative_target / file_path.name

                    if dry_run:
                        action["applied"] = True
                        action["action_taken"] = f"PREVIEW: Would move to {target_path.relative_to(self.project_root)}"
                    else:
                        try:
                            target_path.parent.mkdir(parents=True, exist_ok=True)
                            self._backup_file(file_path, backup_dir)
                            # Collision handling
                            stem, suffix = target_path.stem, target_path.suffix
                            counter = 1
                            while target_path.exists():
                                target_path = target_path.parent / f"{stem}_{counter}{suffix}"
                                counter += 1
                            file_path.rename(target_path)
                            action["applied"] = True
                            action["action_taken"] = f"MOVED: {target_path.relative_to(self.project_root)}"
                            Logger.info(f"[LocationAgent] Healed app leak: {file_path} → {target_path}")
                        except Exception as e:
                            action["error"] = str(e)
                else:
                    action["action_taken"] = "SKIPPED: Could not parse target path"

            # === TERRITORY MISMATCH HEALING ===
            elif "TERRITORY MISMATCH VIOLATION" in msg or "TERRITORY ALIGNMENT WEAK" in msg:
                target_match = re.search(r"Move to agentic_core/([^\s.]+)", msg) or re.search(r"move to '([^']+)'", msg)
                if target_match:
                    territory = target_match.group(1)
                    target_path = self.project_root / "agentic_core" / territory / file_path.name

                    if dry_run:
                        action["applied"] = True
                        action["action_taken"] = f"PREVIEW: Would move to {target_path.relative_to(self.project_root)}"
                    else:
                        try:
                            target_path.parent.mkdir(parents=True, exist_ok=True)
                            self._backup_file(file_path, backup_dir)
                            stem, suffix = target_path.stem, target_path.suffix
                            counter = 1
                            while target_path.exists():
                                target_path = target_path.parent / f"{stem}_{counter}{suffix}"
                                counter += 1
                            file_path.rename(target_path)
                            action["applied"] = True
                            action["action_taken"] = f"MOVED: {target_path.relative_to(self.project_root)}"
                            Logger.info(f"[LocationAgent] Healed territory mismatch: {file_path} → {target_path}")
                        except Exception as e:
                            action["error"] = str(e)
                else:
                    action["action_taken"] = "SKIPPED: Could not parse target territory"

            # === FALLBACK ARCHIVING (Legacy behavior) ===
            else:
                if "VOID VIOLATION" in msg or "GRAVITY" in msg:
                    target_subdir = archives_root / "void_violations"
                elif "DEPTH VIOLATION" in msg:
                    target_subdir = archives_root / "depth_violations"
                elif "BROKEN BACKUP FILE" in msg or "LAYER PREFIX VIOLATION" in msg:
                    target_subdir = archives_root / "naming_violations"
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
                        if target_path.exists():
                            stem, suffix = target_path.stem, target_path.suffix
                            counter = 1
                            while target_path.exists():
                                target_path = target_subdir / f"{stem}_{counter}{suffix}"
                                counter += 1
                        file_path.rename(target_path)
                        action["applied"] = True
                        action["action_taken"] = f"ARCHIVED: {target_path.relative_to(self.project_root)}"
                        Logger.info(f"[LocationAgent] Archived: {file_path.name}")
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
            Dict with Violation count, actions applied, and details
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
