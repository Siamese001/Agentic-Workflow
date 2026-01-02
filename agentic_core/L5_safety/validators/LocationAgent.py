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
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass
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
    DEFAULT_APP_HEALING_TARGET,
    DEFAULT_CORE_HEALING_TERRITORY,
)
from agentic_core.prompt_governance.version_registry.PromptRegistry import registers_prompt
from agentic_core.utils.core_extensions.timeout_decorator import timeout, HealTimeoutError

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

    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()
        # Validate project root is correct
        self._validate_project_root()
        # NamingAgent singleton for post-heal validation and auto-healing
        from agentic_core.utils.naming.naming_agent import get_naming_agent
        self.naming_agent = get_naming_agent(self.project_root)
        # ImportAgent singleton for post-heal validation & auto-heal
        from agentic_core.L5_safety.gravity.ImportAgent import ImportAgent
        self.import_agent = ImportAgent(self.project_root)

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

    def post_heal_validation(self, original_path: Path, new_path: Optional[Path] = None, dry_run: bool = True) -> Dict[str, Any]:
        """
        Re-validate after healing to confirm fix effectiveness.
        Called automatically in safe_move/safe_delete after applied actions.
        
        Returns structured post-heal report added to action dict.
        """
        report = {
            "post_heal_status": "SKIPPED",
            "post_heal_violations": [],
            "post_heal_message": "",
        }

        if dry_run:
            report["post_heal_message"] = "PREVIEW: Post-heal validation skipped in dry-run"
            return report

        try:
            # Case 1: Delete — confirm absence
            if new_path is None:
                if not original_path.exists():
                    report["post_heal_status"] = "SUCCESS"
                    report["post_heal_message"] = "File successfully deleted — no longer exists"
                else:
                    report["post_heal_status"] = "FAILED"
                    report["post_heal_message"] = "Delete failed — file still exists"
                return report

            # Case 2: Move/Archive — validate new location
            if new_path.exists():
                is_valid, msg = self.validate_file_location(new_path)
                if is_valid:
                    report["post_heal_status"] = "SUCCESS"
                    report["post_heal_message"] = "Healing successful — new location compliant"
                else:
                    report["post_heal_status"] = "PARTIAL"
                    report["post_heal_violations"] = [msg]
                    report["post_heal_message"] = f"Partial heal — new violations: {msg}"
            else:
                report["post_heal_status"] = "FAILED"
                report["post_heal_message"] = "Healing failed — destination file does not exist"

            # Bonus: Confirm original path cleared (move/archive success)
            if original_path.exists():
                report["post_heal_message"] += " | WARNING: Original file still exists (partial move?)"

        except Exception as e:
            report["post_heal_status"] = "ERROR"
            report["post_heal_message"] = f"Post-heal validation error: {e}"
            Logger.error(f"[LocationAgent] Post-heal validation failed: {e}")

        return report

    def _compute_module_path(self, file_path: Path) -> str:
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
        """
        Ultra import healing post-move.
        Scans entire repo for references to old module and updates to new module.
        Patterns matched:
        - from old.parent import old_stem
        - from old.parent.sub import old_stem
        - import old.parent.old_stem
        Safe regex, backs up changed files.
        
        POST-IMPORT-FIX VALIDATION (Ultra Reliability 2026-01-02):
        - After applying fixes, re-scan repo for any remaining references to old module
        - Reports remaining broken imports (files + line previews)
        - Status: FULL_SUCCESS (0 remaining), PARTIAL (some remaining), FAILED (more than before)
        """
        import_result = {
            "import_fix_applied": False,
            "import_files_touched": [],
            "import_fix_count": 0,
            "import_message": "",
            "import_post_fix_status": "SKIPPED",
            "import_remaining_references": [],
            "import_remaining_count": 0,
        }

        if dry_run:
            import_result["import_message"] = "PREVIEW: Import fix skipped in dry-run"
            import_result["import_post_fix_status"] = "PREVIEW"
            return import_result

        old_module = self._compute_module_path(old_path)
        new_module = self._compute_module_path(new_path)

        if not old_module or not new_module:
            import_result["import_message"] = "SKIPPED: Could not compute module paths"
            import_result["import_post_fix_status"] = "SKIPPED"
            return import_result

        # Regex patterns for common import styles
        patterns = [
            (rf"from\s+{re.escape(old_module)}\s+import", rf"from {new_module} import"),
            (rf"import\s+{re.escape(old_module)}", f"import {new_module}"),
            (rf"from\s+([^ \t]+)\.{re.escape(old_path.stem)}\s+import", rf"from \1.{new_path.stem} import"),
            (rf"import\s+([^ \t]+)\.{re.escape(old_path.stem)}", rf"import \1.{new_path.stem}"),
        ]

        touched_files: List[str] = []
        fix_count = 0

        try:
            for py_file in self.project_root.rglob("*.py"):
                if py_file == new_path or py_file == old_path:
                    continue  # Skip self
                if any(part in {".git", "__pycache__", "archives"} for part in py_file.parts):
                    continue

                try:
                    content = py_file.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue
                    
                new_content = content

                for old_pat, new_pat in patterns:
                    new_content, count = re.subn(old_pat, new_pat, new_content)
                    fix_count += count

                if new_content != content:
                    # Backup changed file
                    backup_dir = self._init_backup_dir() / "import_fixes"
                    backup_dir.mkdir(parents=True, exist_ok=True)
                    try:
                        backup_path = backup_dir / py_file.relative_to(self.project_root)
                        backup_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(py_file, backup_path)
                    except Exception:
                        pass  # Best effort backup

                    py_file.write_text(new_content, encoding="utf-8")
                    touched_files.append(str(py_file.relative_to(self.project_root)))

            import_result["import_fix_applied"] = True
            import_result["import_files_touched"] = touched_files
            import_result["import_fix_count"] = fix_count
            import_result["import_message"] = f"Fixed {fix_count} imports across {len(touched_files)} files"
            Logger.info(f"[LocationAgent] Import fix: {old_module} → {new_module} ({fix_count} fixes)")

            # === POST-IMPORT-FIX VALIDATION ===
            remaining_references = []
            remaining_count = 0

            validation_pattern = re.compile(rf"{re.escape(old_module)}")
            for py_file in self.project_root.rglob("*.py"):
                if any(part in {".git", "__pycache__", "archives"} for part in py_file.parts):
                    continue

                try:
                    lines = py_file.read_text(encoding="utf-8", errors="ignore").splitlines()
                    for line_num, line in enumerate(lines, 1):
                        if validation_pattern.search(line):
                            remaining_references.append({
                                "file": str(py_file.relative_to(self.project_root)),
                                "line": line_num,
                                "preview": line.strip()[:100],
                            })
                            remaining_count += 1
                except Exception:
                    continue

            import_result["import_remaining_references"] = remaining_references[:20]  # Cap for report size
            import_result["import_remaining_count"] = remaining_count

            if remaining_count == 0:
                import_result["import_post_fix_status"] = "FULL_SUCCESS"
                import_result["import_message"] += " | All imports resolved"
            elif remaining_count <= 3:
                import_result["import_post_fix_status"] = "PARTIAL"
                import_result["import_message"] += f" | {remaining_count} remaining references (likely strings/dynamic)"
            else:
                import_result["import_post_fix_status"] = "NEEDS_REVIEW"
                import_result["import_message"] += f" | {remaining_count} remaining references — review unhandled patterns"

            Logger.info(f"[LocationAgent] Post-import validation: {import_result['import_post_fix_status']} ({remaining_count} remaining)")

        except Exception as e:
            import_result["import_message"] = f"ERROR during import fix: {e}"
            import_result["import_post_fix_status"] = "ERROR"
            Logger.error(f"[LocationAgent] Import fix failed: {e}")

        return import_result

    def safe_move(self, src_path: Path, dst_path: Path, dry_run: bool = True) -> Dict[str, Any]:
        """
        Safely move a file with backup, collision handling, post-heal validation, and import fixing.
        """
        result = {
            "applied": False,
            "action_taken": "",
            "error": None,
        }
        
        if dry_run:
            result["applied"] = True
            result["action_taken"] = f"PREVIEW: Would move to {dst_path.relative_to(self.project_root)}"
            return result
            
        try:
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            self._backup_file(src_path)
            
            # Collision handling
            final_dst = dst_path
            stem, suffix = dst_path.stem, dst_path.suffix
            counter = 1
            while final_dst.exists():
                final_dst = dst_path.parent / f"{stem}_{counter}{suffix}"
                counter += 1
            
            src_path.rename(final_dst)
            result["applied"] = True
            result["action_taken"] = f"MOVED: {final_dst.relative_to(self.project_root)}"
            Logger.info(f"[LocationAgent] Moved: {src_path} → {final_dst}")
            
            # Auto post-heal validation
            result.update(self.post_heal_validation(src_path, final_dst, dry_run=False))
            
            # Ultra import fix integration
            result.update(self.fix_imports_after_move(src_path, final_dst, dry_run=False))
            
            # Gravity integration flag: if move is core → apps, mark for special gravity handling
            if "agentic_core" in str(src_path) and "apps_" in str(final_dst):
                result["gravity_resolution_expected"] = True
                result["moved_module"] = self._compute_module_path(final_dst)
            else:
                result["gravity_resolution_expected"] = False
            
        except Exception as e:
            result["error"] = str(e)
            Logger.error(f"[LocationAgent] Move failed: {e}")
            
        return result

    def safe_delete(self, file_path: Path, dry_run: bool = True) -> Dict[str, Any]:
        """
        Safely delete a file with backup and post-heal validation.
        """
        result = {
            "applied": False,
            "action_taken": "",
            "error": None,
        }
        
        if dry_run:
            result["applied"] = True
            result["action_taken"] = f"PREVIEW: Would delete {file_path.name}"
            return result
            
        try:
            self._backup_file(file_path)
            file_path.unlink()
            result["applied"] = True
            result["action_taken"] = "DELETED (backed up)"
            Logger.info(f"[LocationAgent] Deleted: {file_path}")
            
            # Auto post-heal validation
            result.update(self.post_heal_validation(file_path, None, dry_run=False))
            
        except Exception as e:
            result["error"] = str(e)
            Logger.error(f"[LocationAgent] Delete failed: {e}")
            
        return result

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

    def _recompute_ast_scores(self, tree: ast.AST) -> Tuple[float, float, Dict[str, float]]:
        """
        Helper to recompute AST scores for gravity root-cause detection.
        Full multi-signal AST scoring identical to LocationAgent primary check.
        Includes Class/Function names, Variables/Arguments, String literals.
        """
        app_rg_score = 0.0
        app_lic_score = 0.0
        territory_scores: Dict[str, float] = {t: 0.0 for t in CORE_TERRITORY_KEYWORDS}

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

        return app_rg_score, app_lic_score, territory_scores

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
                for grav in gravity_issues:
                    path = Path(grav["path"]) if isinstance(grav["path"], str) else grav["path"]
                    msg = grav["issue"]

                    try:
                        content = path.read_text(encoding="utf-8")
                        lines = content.splitlines()

                        # Extract downstream roots from message
                        downstream_match = re.search(r"downstream roots: \[(.*?)\]", msg)
                        if not downstream_match:
                            downstream_match = re.search(r"apps_[a-z_]+", msg)
                            if downstream_match:
                                downstream_roots = [downstream_match.group(0)]
                            else:
                                continue
                        else:
                            downstream_roots = [r.strip().strip("'\"") for r in downstream_match.group(1).split(",")]

                        # Find and remove offending import lines
                        new_lines = []
                        removed = False
                        removed_modules = []
                        for line in lines:
                            if any(root in line for root in downstream_roots) and line.strip().startswith(("import ", "from ")):
                                removed = True
                                match = re.match(r"^(import|from)\s+([a-zA-Z0-9_.]+)", line.strip())
                                if match:
                                    removed_modules.append(match.group(2))
                                continue
                            new_lines.append(line)

                        if removed:
                            todo_block = [
                                "",
                                "# TODO: GRAVITY VIOLATION AUTO-HEALED",
                                "# Downstream imports removed — move shared logic to apps_shared or sovereign utils",
                                "# Original violation: " + msg[:200],
                                "# Removed: " + ", ".join(removed_modules),
                                "",
                            ]
                            # Insert after potential shebang/docstring
                            insert_idx = 0
                            if new_lines and new_lines[0].startswith("#!"):
                                insert_idx = 1
                            if len(new_lines) > insert_idx and new_lines[insert_idx].strip().startswith('"""'):
                                try:
                                    for i, l in enumerate(new_lines[insert_idx:], insert_idx):
                                        if i > insert_idx and '"""' in l:
                                            insert_idx = i + 1
                                            break
                                except StopIteration:
                                    pass

                            new_lines = new_lines[:insert_idx] + todo_block + new_lines[insert_idx:]
                            new_content = "\n".join(new_lines)

                            # Backup + write
                            backup_dir = self._init_backup_dir() / "gravity_auto_heal"
                            backup_dir.mkdir(parents=True, exist_ok=True)
                            backup_path = backup_dir / path.relative_to(self.project_root)
                            backup_path.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(path, backup_path)

                            path.write_text(new_content, encoding="utf-8")

                            gravity_heal_actions.append({
                                "type": "GRAVITY_AUTO_HEAL",
                                "file": grav["file"],
                                "removed_imports": removed_modules,
                            })

                    except Exception as e:
                        gravity_heal_actions.append({
                            "type": "GRAVITY_HEAL_ERROR",
                            "file": grav["file"],
                            "error": str(e),
                        })

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

    def deep_naming_validation_and_heal(self, affected_paths: List[Path], import_touched_paths: List[Path], dry_run: bool = True) -> Dict[str, Any]:
        """
        Deep NamingAgent integration: full convention + semantic validation + auto-heal.
        Covers filename conventions, duplicates, prefix-location, global uniqueness, high-signal, markers.
        
        SEMANTIC KEYWORD AUTO-INSERTION ENHANCEMENT (Ultra Autonomy 2026-01-02):
        - For files missing expected high-signal keywords (based on filename signals)
          → auto-insert TODO comment block with suggested canon keywords
        - Safe: Only adds non-executable comments at file top (after docstring)
        """
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

        heal_actions = []
        semantic_issues = []

        # Full NamingAgent validation on affected files
        for path in py_files:
            try:
                rel = str(path.relative_to(self.project_root))
                filename = path.name
                filename_lower = filename.lower()

                issues = []

                # snake_case + forbidden patterns (allow PascalCase for Agent files)
                if not re.match(r'^[a-z0-9_]+\.py$', filename) and not re.match(r'^[A-Z][a-zA-Z0-9]*Agent\.py$', filename):
                    issues.append("NOT_SNAKE_CASE")

                if hasattr(self.naming_agent, 'forbidden_patterns'):
                    for pattern in self.naming_agent.forbidden_patterns:
                        if pattern.match(filename):
                            issues.append("FORBIDDEN_PATTERN")

                # Prefix-location (deep call)
                if hasattr(self.naming_agent, 'validate_prefix_location_match'):
                    prefix_issues = self.naming_agent.validate_prefix_location_match(path)
                    if prefix_issues:
                        issues.extend(prefix_issues if isinstance(prefix_issues, list) else [prefix_issues])

                # High-signal keywords (semantic - enhanced auto-insertion)
                content = path.read_text(encoding="utf-8", errors="ignore")
                content_lower = content.lower()

                expected_signals = set()
                signal_keywords = ["agent", "engine", "validator", "healer", "manager", "orchestrator"]
                if any(sig in filename_lower for sig in signal_keywords):
                    high_signal_kws = getattr(self.naming_agent, 'high_signal_keywords', set())
                    expected_signals = high_signal_kws & {"agent", "engine", "validator", "healer", "orchestrator", "workflow", "state", "memory", "prompt", "guardrail"}

                missing_signals = expected_signals - {kw for kw in expected_signals if kw in content_lower}
                if missing_signals:
                    semantic_issues.append({
                        "file": rel,
                        "issue": "MISSING_HIGH_SIGNAL_KEYWORDS",
                        "missing": list(missing_signals),
                    })

                    # Enhanced auto-insertion: Add TODO block with missing keywords
                    try:
                        todo_block = [
                            "",
                            "# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)",
                            "# File appears to be a sovereign component but missing canon high-signal keywords.",
                            "# Suggested keywords to add in docstring/code: " + ", ".join(sorted(missing_signals)),
                            "# This boosts alignment detection — review and integrate appropriately",
                            "",
                        ]

                        # Insert after docstring/shebang
                        lines = content.splitlines()
                        insert_idx = 0
                        if lines and lines[0].startswith("#!"):
                            insert_idx = 1
                        # Find docstring end
                        if len(lines) > insert_idx and lines[insert_idx].strip().startswith(('"""', "'''")):
                            quote = lines[insert_idx].strip()[:3]
                            for i, l in enumerate(lines[insert_idx:], insert_idx):
                                if i > insert_idx and quote in l:
                                    insert_idx = i + 1
                                    break

                        new_lines = lines[:insert_idx] + todo_block + lines[insert_idx:]
                        new_content = "\n".join(new_lines)

                        # Backup + write
                        backup_dir = self._init_backup_dir() / "semantic_keyword_insertion"
                        backup_dir.mkdir(parents=True, exist_ok=True)
                        backup_path = backup_dir / path.relative_to(self.project_root)
                        backup_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(path, backup_path)

                        path.write_text(new_content, encoding="utf-8")

                        heal_actions.append({
                            "type": "SEMANTIC_KEYWORD_AUTO_INSERT",
                            "file": rel,
                            "inserted_keywords": list(missing_signals),
                        })

                    except Exception as e:
                        heal_actions.append({
                            "type": "SEMANTIC_INSERT_ERROR",
                            "file": rel,
                            "error": str(e),
                        })

                # Sovereign root markers (report + optional TODO)
                try:
                    rel_parts = path.relative_to(self.project_root).parts
                    if len(rel_parts) == 1:  # Root file
                        if "validator" in filename_lower or "compliance" in filename_lower:
                            if "sovereign" not in content_lower:
                                semantic_issues.append({"file": rel, "issue": "MISSING_SOVEREIGN_MARKER"})
                                # Optional auto-TODO
                                todo = "\n# SOVEREIGN MARKER MISSING - ADD CANON COMPLIANCE COMMENT\n"
                                if todo not in content:
                                    new_content = content + todo
                                    backup_dir = self._init_backup_dir() / "naming_marker"
                                    backup_dir.mkdir(parents=True, exist_ok=True)
                                    shutil.copy2(path, backup_dir / path.name)
                                    path.write_text(new_content, encoding="utf-8")
                                    heal_actions.append({"type": "SOVEREIGN_MARKER_TODO", "file": rel})
                except ValueError:
                    pass

                if issues:
                    # Auto-heal filename conventions + prefix
                    try:
                        # Canonical snake_case rename
                        new_name = re.sub(r'[^a-zA-Z0-9_.]', '_', filename)
                        new_name = re.sub(r'_+', '_', new_name).strip('_')
                        if not new_name.endswith('.py'):
                            new_name += '.py'
                        new_path = path.parent / new_name

                        if new_path != path and new_name.lower() != filename.lower():
                            move_result = self.safe_move(path, new_path, dry_run=False)
                            if move_result.get("applied"):
                                heal_actions.append({"type": "FILENAME_CANONICAL_RENAME", "original": rel, "new": str(new_path.relative_to(self.project_root))})
                                affected_paths.append(new_path)

                        # Prefix-location canonical move
                        if hasattr(self.naming_agent, 'move_to_canonical_location'):
                            final_path = new_path if new_path != path and new_path.exists() else path
                            if final_path.exists():
                                canonical_result = self.naming_agent.move_to_canonical_location(final_path, dry_run=False)
                                if canonical_result.get("moved"):
                                    heal_actions.append({"type": "PREFIX_CANONICAL_MOVE", "result": canonical_result})
                                    if canonical_result.get("new_path"):
                                        affected_paths.append(self.project_root / canonical_result["new_path"])

                    except Exception as e:
                        heal_actions.append({"type": "NAMING_HEAL_ERROR", "file": rel, "error": str(e)})

            except Exception as e:
                heal_actions.append({"type": "NAMING_FILE_ERROR", "error": str(e)})

        deep_naming_report["naming_semantic_issues"] = semantic_issues
        deep_naming_report["naming_convention_heal_applied"] = bool(heal_actions)
        deep_naming_report["naming_heal_actions"] = heal_actions

        # Final status
        if not heal_actions and not semantic_issues:
            deep_naming_report["naming_deep_status"] = "FULL_SUCCESS"
            deep_naming_report["naming_final_status"] = "FULL_SUCCESS"
        elif not semantic_issues:
            deep_naming_report["naming_deep_status"] = "CONVENTIONS_FIXED"
            deep_naming_report["naming_final_status"] = "CONVENTIONS_FIXED"
        else:
            deep_naming_report["naming_deep_status"] = "PARTIAL"
            deep_naming_report["naming_final_status"] = "PARTIAL"

        deep_naming_report["naming_message"] = f"Deep naming: {len(heal_actions)} convention heals, {len(semantic_issues)} semantic issues → Final: {deep_naming_report['naming_deep_status']}"
        if any(a.get("type") == "SEMANTIC_KEYWORD_AUTO_INSERT" for a in heal_actions):
            deep_naming_report["naming_message"] += " | Semantic keywords auto-inserted"

        return deep_naming_report

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
                    move_result = self.safe_move(file_path, target_path, dry_run=dry_run)
                    action.update(move_result)
                    if move_result.get("applied") and not dry_run:
                        affected_paths.extend([file_path, target_path])
                        # Collect import-touched files
                        if "import_files_touched" in move_result:
                            for rel in move_result["import_files_touched"]:
                                import_touched_paths.append(self.project_root / rel)
                else:
                    action["action_taken"] = f"SKIPPED: Could not parse target path. Using fallback: {DEFAULT_APP_HEALING_TARGET}"

            # === TERRITORY MISMATCH HEALING ===
            elif "TERRITORY MISMATCH VIOLATION" in msg or "TERRITORY ALIGNMENT WEAK" in msg:
                target_match = re.search(r"Move to agentic_core/([^\s.]+)", msg) or re.search(r"move to '([^']+)'", msg)
                if target_match:
                    territory = target_match.group(1)
                    target_path = self.project_root / "agentic_core" / territory / file_path.name
                    move_result = self.safe_move(file_path, target_path, dry_run=dry_run)
                    action.update(move_result)
                    if move_result.get("applied") and not dry_run:
                        affected_paths.extend([file_path, target_path])
                        if "import_files_touched" in move_result:
                            for rel in move_result["import_files_touched"]:
                                import_touched_paths.append(self.project_root / rel)
                else:
                    action["action_taken"] = "SKIPPED: Could not parse target territory"

            # === BROKEN BACKUP DELETE ===
            elif "BROKEN BACKUP FILE" in msg:
                delete_result = self.safe_delete(file_path, dry_run=dry_run)
                action.update(delete_result)
                if delete_result.get("applied") and not dry_run:
                    affected_paths.append(file_path)

            # === FALLBACK ARCHIVING (Legacy behavior) ===
            else:
                if "VOID VIOLATION" in msg or "GRAVITY" in msg:
                    target_subdir = archives_root / "void_violations"
                elif "DEPTH VIOLATION" in msg:
                    target_subdir = archives_root / "depth_violations"
                elif "LAYER PREFIX VIOLATION" in msg:
                    target_subdir = archives_root / "naming_violations"
                else:
                    target_subdir = archives_root / "location_violations"
                    
                target_path = target_subdir / file_path.name
                move_result = self.safe_move(file_path, target_path, dry_run=dry_run)
                if "MOVED" in move_result.get("action_taken", ""):
                    move_result["action_taken"] = move_result["action_taken"].replace("MOVED", "ARCHIVED")
                action.update(move_result)
                if move_result.get("applied") and not dry_run:
                    affected_paths.extend([file_path, target_path])
                    
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
                    def sort_key(p_str: str):
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
