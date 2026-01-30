#!/usr/bin/env python3
from __future__ import annotations

"""
LocationValidatorAgent: Pure validation agent for territorial compliance

Responsibility: Validate file locations against sovereign structure rules
- NO healing or file operations
- NO side effects
- Pure validation logic only

Extracted from LocationAgent.py as part of SRP fission.
"""


import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.base_agents.subatomic_testing_mixin import SubatomicTestingMixin


@dataclass
class LocationValidatorAgent(SovereignBaseAgent, SubatomicTestingMixin):
    """
    Pure validation agent for territorial compliance.

    Validates:
    - Root folder whitelist compliance
    - Depth requirements per sovereign root
    - Forbidden patterns and numbered folders
    - AST-based semantic alignment
    - Import layer violations
    - App-specific file placement

    Does NOT perform:
    - File moves or deletions
    - Automated healing
    - Backup operations

    Use LocationHealerAgent for remediation.
    """

    project_root: Path = field(default=None)

    def __post_init__(self):
        """Initialize validator with project root validation."""
        super().__post_init__()
        self.project_root = self.project_root.resolve()
        # Validation-only initialization
        # No backup dirs, no healing state

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        [HEALER PROTOCOL] Standardized healing interface for location violations.
        
        Note: LocationValidatorAgent is validation-only and does not perform healing.
        Use LocationHealerAgent for actual remediation.
        
        Args:
            violation: Violation dict with keys: type, file, message, etc.
            
        Returns:
            Dict with keys: status, details, artifacts, errors
        """
        return {
            "status": "skipped",
            "details": "LocationValidatorAgent is validation-only. Use LocationHealerAgent for healing.",
            "artifacts": [],
            "errors": [],
        }

    def run(self) -> dict[str, Any]:
        """
        Execute validation-only scan.

        Returns:
            Dict with violations list, no healing actions
        """
        # TODO: Implement validation orchestration
        # This will be populated during migration phase
        return {
            "violations": [],
            "total_files_scanned": 0,
            "compliant_files": 0,
            "status": "NOT_IMPLEMENTED",
        }

    # ========================================================================
    # MIGRATED VALIDATION METHODS (Phase 3 Batch 1)
    # ========================================================================

    def validate_sovereign_roots(self) -> list[tuple[Path, str]]:
        """Ensure all required sovereign roots exist and are directories."""
        from agentic_core.L5_safety.validators.structure_blueprint import ROOT_WHITELIST

        violations: list[tuple[Path, str]] = []
        for root_name in ROOT_WHITELIST:
            root_path = self.project_root / root_name
            if not root_path.exists():
                violations.append((root_path, f"Missing sovereign root: {root_name}"))
            elif not root_path.is_dir():
                violations.append((root_path, f"Sovereign root is not a directory: {root_name}"))
        return violations

    def validate_file_location(self, file_path: Path) -> tuple[bool, str]:
        """Per-file location validation with correct forbidden-check ordering."""
        try:
            rel_path = file_path.relative_to(self.project_root)
            parts = rel_path.parts
            root_folder = parts[0]
        except ValueError:
            return False, "VOID VIOLATION: File outside project root"

        # Early validation chain - exit on first violation
        result = self._validate_forbidden_patterns(parts, root_folder)
        if not result[0]:
            return result

        result = self._validate_root_whitelist(root_folder, rel_path)
        if not result[0]:
            return result

        result = self._validate_depth_requirements(parts, root_folder, rel_path)
        if not result[0]:
            return result

        # Continue validation chain
        result = self._validate_app_specific_files(root_folder, file_path)
        if not result[0]:
            return result

        result = self._validate_filename_patterns(file_path)
        if not result[0]:
            return result

        # Final validation checks
        result = self._validate_final_checks(root_folder, file_path, parts)
        if not result[0]:
            return result

        return True, f"Location compliant in sovereign territory: {root_folder}"

    def _validate_forbidden_patterns(self, parts: tuple, root_folder: str) -> tuple[bool, str]:
        """Validate forbidden folder patterns and numbered roots."""
        from agentic_core.L5_safety.validators.structure_blueprint import (
            FORBIDDEN_FOLDER_PATTERN,
            FORBIDDEN_ROOT_FOLDERS,
        )

        # Check all parts for forbidden folders
        for part in parts:
            if part in FORBIDDEN_ROOT_FOLDERS:
                return False, f"VOID VIOLATION: Forbidden folder '{part}' at any depth"

            # Check for regex pattern match if applicable
            if hasattr(FORBIDDEN_FOLDER_PATTERN, "match"):
                if FORBIDDEN_FOLDER_PATTERN.match(part):
                    return False, f"VOID VIOLATION: Numbered folder pattern '{part}' forbidden"

        # Numbered root folders (e.g., 08_scripts) forbidden
        if len(root_folder) >= 3 and root_folder[:2].isdigit() and root_folder[2:3] == "_":
            return False, f"VOID VIOLATION: Numbered root folder '{root_folder}' not approved"

        return True, "OK"

    def _validate_root_whitelist(self, root_folder: str, rel_path: Path = None) -> tuple[bool, str]:
        """Validate path is within an allowed sovereign territory using SSOT helper."""
        from agentic_core.L5_safety.validators.structure_blueprint import (
            ROOT_WHITELIST,
            is_path_allowed,
        )

        # Use is_path_allowed for nested path validation (SSOT fix)
        if rel_path is not None:
            if not is_path_allowed(str(rel_path)):
                return False, f"VOID VIOLATION: Path '{rel_path}' not in sovereign territory"

        # Special Semantic Check for scripts/ vs L0_maintenance
        if root_folder == "scripts" and rel_path is not None:
            file_path = self.project_root / rel_path
            is_compliant, reason = self._validate_scripts_isolation(file_path)
            if not is_compliant:
                return False, reason

        # Root whitelist check
        if rel_path is not None:
            return True, "OK"

        # Fallback to root-only check
        if root_folder not in ROOT_WHITELIST:
            return False, f"VOID VIOLATION: Unapproved root folder '{root_folder}'"
        return True, "OK"

    def _validate_scripts_isolation(self, file_path: Path) -> tuple[bool, str]:
        """
        Enforces strict isolation for root scripts.

        Root scripts (`scripts/`) are for standalone utilities/setup only.
        They MUST NOT import from `agentic_core`.

        If a script imports `agentic_core`, it is part of the system
        and belongs in `agentic_core/L0_maintenance/scripts/`.
        """
        from agentic_core.L5_safety.validators.structure_blueprint import (
            SCRIPTS_PLACEMENT_RULES,
        )

        if not file_path.exists() or file_path.suffix != ".py":
            return True, "OK"

        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content)

            forbidden_prefixes = SCRIPTS_PLACEMENT_RULES.get("root_scripts", {}).get(
                "forbidden_imports", []
            )

            for node in ast.walk(tree):
                # Check 'import x'
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        for prefix in forbidden_prefixes:
                            if alias.name.startswith(prefix):
                                return False, (
                                    f"SEMANTIC VIOLATION: Root script imports '{alias.name}'. "
                                    f"Files importing '{prefix}' belong in agentic_core/L0_maintenance/scripts/"
                                )

                # Check 'from x import y'
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        for prefix in forbidden_prefixes:
                            if node.module.startswith(prefix):
                                return False, (
                                    f"SEMANTIC VIOLATION: Root script imports from '{node.module}'. "
                                    f"Files importing '{prefix}' belong in agentic_core/L0_maintenance/scripts/"
                                )

        except SyntaxError:
            pass  # Unparseable Python is a different issue
        except Exception:
            pass  # Non-blocking for other errors

        return True, "OK"

    def _validate_depth_requirements(
        self, parts: tuple, root_folder: str, rel_path: Path
    ) -> tuple[bool, str]:
        """Validate depth requirements from sovereign registry.

        SSOT FIX: Allow variable depth for certain subfolders that legitimately
        have deeper structures (e.g., utils/core_extensions/, config/blueprint_sovereign/).
        """
        from agentic_core.L5_safety.validators.structure_blueprint import (
            SOVEREIGN_TERRITORIES,
            VARIABLE_DEPTH_SUBFOLDERS,
        )

        expected_depth = SOVEREIGN_TERRITORIES.get(root_folder, {}).get("depth")
        actual_depth = len(parts) - 1

        # Check if this is a variable-depth subfolder (exempt from strict depth check)
        if root_folder == "agentic_core" and len(parts) > 1:
            subfolder = parts[1]
            if subfolder in VARIABLE_DEPTH_SUBFOLDERS:
                # Allow any depth >= 2 for variable-depth subfolders
                if actual_depth >= 2:
                    return True, "OK"

        # Standard depth validation (non-variable subfolders)
        if expected_depth is not None and actual_depth != expected_depth:
            reason = "SHALLOW" if actual_depth < expected_depth else "DEEP"
            return (
                False,
                f"{reason} VIOLATION ({root_folder}): depth {actual_depth} != {expected_depth}",
            )

        return True, "OK"

    def _validate_app_specific_files(self, root_folder: str, file_path: Path) -> tuple[bool, str]:
        """Validate app-specific files are not in core."""
        from agentic_core.L5_safety.validators.structure_blueprint import (
            get_correct_app_path,
            is_app_specific_file,
        )

        if root_folder == "agentic_core" and is_app_specific_file(file_path.name):
            correct_path = get_correct_app_path(file_path.name) or "appropriate apps_* folder"
            return False, (
                f"APP-SPECIFIC IN CORE VIOLATION: '{file_path.name}' is application-specific "
                f"and must not live in agentic_core. Move to '{correct_path}/'."
            )
        return True, "OK"

    def _validate_filename_patterns(self, file_path: Path) -> tuple[bool, str]:
        """Validate filename patterns for forbidden prefixes and backup files."""
        from agentic_core.L5_safety.validators.structure_blueprint import (
            check_forbidden_signals,
            has_forbidden_layer_prefix,
        )

        # Forbidden layer prefixes
        forbidden_prefix = has_forbidden_layer_prefix(file_path.name)
        if forbidden_prefix:
            return (
                False,
                f"LAYER PREFIX VIOLATION: Filename has forbidden prefix '{forbidden_prefix}'",
            )

        # Broken backup files
        if file_path.name.endswith((".bak", ".backup", ".old", ".tmp")):
            return False, "BROKEN BACKUP FILE: Remove stale backup file"

        # ARTIFACT ROUTING NEGATIVE LOGIC CHECK
        # Check forbidden_extensions and forbidden_keywords from ARTIFACT_ROUTING_MAP
        # This prevents code files from being misclassified as reports/logs/data
        try:
            content = None
            if file_path.exists() and file_path.is_file():
                # Only read content for small files to avoid performance issues
                if file_path.stat().st_size < 1_000_000:  # 1MB limit
                    try:
                        content = file_path.read_text(encoding="utf-8", errors="ignore")
                    except Exception:
                        pass  # Content check is optional

            rejection_reason = check_forbidden_signals(file_path.name, content)
            if rejection_reason:
                return (
                    False,
                    f"ARTIFACT ROUTING VIOLATION: {rejection_reason}",
                )
        except Exception:
            pass  # Non-blocking - routing check is supplementary

        return True, "OK"

    def _validate_final_checks(
        self, root_folder: str, file_path: Path, parts: tuple
    ) -> tuple[bool, str]:
        """Final validation checks for root-level files and gravity leaks."""
        from agentic_core.L5_safety.validators.structure_blueprint import (
            ROOT_PROTECTED_FILES,
        )

        # Root-level file protections (Key 0)
        if len(parts) == 1 and file_path.suffix == ".py":
            if file_path.name not in ROOT_PROTECTED_FILES:
                return (
                    False,
                    f"VOID VIOLATION: Unapproved root-level Python file '{file_path.name}'",
                )

        return True, "OK"

    # ========================================================================
    # MIGRATED AST/SEMANTIC VALIDATION METHODS (Phase 3 Batch 2)
    # ========================================================================

    def _validate_ast_violations(
        self, root_folder: str, file_path: Path, rel_path: Path
    ) -> tuple[bool, str]:
        """Validate AST-based violations for agentic_core Python files."""
        if root_folder != "agentic_core" or file_path.suffix != ".py":
            return True, "OK"

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

            # Check for forbidden imports
            result = self._check_forbidden_imports(tree, current_l1, rel_path)
            if not result[0]:
                return result

            # Check semantic alignment
            result = self._check_semantic_alignment(tree, current_territory, rel_path)
            if not result[0]:
                return result

        except Exception:
            pass  # AST parsing failures are non-blocking

        return True, "OK"

    def _check_forbidden_imports(
        self, tree: Any, current_l1: str, rel_path: Path
    ) -> tuple[bool, str]:
        """Check for forbidden app imports and layer violations."""

        forbidden_app_import, forbidden_layer_import = self._scan_imports_for_violations(
            tree, current_l1
        )

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

        return True, "OK"

    def _scan_imports_for_violations(self, tree: Any, current_l1: str) -> tuple[bool, str | None]:
        """Scan AST for forbidden imports and return violation flags."""
        import ast

        for node in ast.walk(tree):
            if isinstance(node, ast.Import | ast.ImportFrom):
                modules = self._extract_modules_from_node(node)

                for module in modules:
                    if self._is_forbidden_app_import(module):
                        return True, None

                    layer_violation = self._check_layer_import_violation(module, current_l1)
                    if layer_violation:
                        return False, layer_violation

        return False, None

    def _extract_modules_from_node(self, node: Any) -> list[str]:
        """Extract module names from import node."""
        import ast

        if isinstance(node, ast.Import):
            return [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            return [node.module]
        return []

    def _is_forbidden_app_import(self, module: str) -> bool:
        """Check if module is a forbidden app import."""
        from agentic_core.L5_safety.validators.structure_blueprint import FORBIDDEN_APP_MODULES

        return module.startswith(("apps_rg.", "apps_lic.")) or module in FORBIDDEN_APP_MODULES

    def _check_layer_import_violation(self, module: str, current_l1: str) -> str | None:
        """Check for layer import violations and return violation description.

        [RECONCILED 2026-01-27] Now enforces:
        1. Core layer gravity (L1-L5 import direction)
        2. App-layer horizontal isolation (apps_shared independence)
        """
        from agentic_core.L5_safety.validators.structure_blueprint import LAYER_FORBIDDEN_IMPORTS

        if not current_l1:
            return None

        # Check agentic_core layer imports
        if module.startswith("agentic_core.") and len(module.split(".")) > 2:
            imported_l1 = module.split(".")[1]
            if imported_l1 in LAYER_FORBIDDEN_IMPORTS.get(current_l1, set()):
                return f"{current_l1} → {imported_l1}"

        # [SHARED GRAVITY] Check app-layer horizontal isolation
        # apps_shared MUST NOT import from apps_rg or apps_lic
        if current_l1 == "apps_shared":
            if module.startswith(("apps_rg.", "apps_lic.")):
                imported_app = module.split(".")[0]
                return f"apps_shared → {imported_app} (HORIZONTAL ISOLATION VIOLATION)"

        # Apps cannot import from each other
        if current_l1 == "apps_rg" and module.startswith("apps_lic."):
            return "apps_rg → apps_lic (HORIZONTAL ISOLATION VIOLATION)"
        if current_l1 == "apps_lic" and module.startswith("apps_rg."):
            return "apps_lic → apps_rg (HORIZONTAL ISOLATION VIOLATION)"

        return None

    def _check_semantic_alignment(
        self, tree: Any, current_territory: str, rel_path: Path
    ) -> tuple[bool, str]:
        """Check semantic alignment between file location and content."""
        if not current_territory:
            return True, "OK"

        # Calculate semantic scores
        app_rg_score, app_lic_score, territory_scores = self._calculate_semantic_scores(tree)

        # Check for app-specific violations
        result = self._check_app_domain_violation(app_rg_score, app_lic_score, rel_path)
        if not result[0]:
            return result

        # Check territory alignment
        return self._check_territory_alignment(current_territory, territory_scores, rel_path)

    def _calculate_semantic_scores(self, tree: Any) -> tuple[float, float, dict[str, float]]:
        """Calculate semantic scores for app and territory alignment."""
        import ast

        from agentic_core.L5_safety.validators.structure_blueprint import (
            APP_LIC_AST_TERMS,
            APP_RG_AST_TERMS,
            CORE_TERRITORY_KEYWORDS,
        )

        app_rg_score = 0.0
        app_lic_score = 0.0
        territory_scores: dict[str, float] = dict.fromkeys(CORE_TERRITORY_KEYWORDS, 0.0)

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef | ast.FunctionDef):
                name = node.name.lower()
                if any(t in name for t in APP_RG_AST_TERMS):
                    app_rg_score += 1.0
                if any(t in name for t in APP_LIC_AST_TERMS):
                    app_lic_score += 1.0
                for terr, cats in CORE_TERRITORY_KEYWORDS.items():
                    for terms in cats.values():
                        if any(t in name for t in terms):
                            territory_scores[terr] += 1.0

        return app_rg_score, app_lic_score, territory_scores

    def _check_app_domain_violation(
        self, app_rg_score: float, app_lic_score: float, rel_path: Path
    ) -> tuple[bool, str]:
        """
        [HARDENED] Detects cross-contamination AND Global Candidates for apps_shared.
        [SSOT 2026-01-27] Implements the 'Shared Vacuum' logic.
        """
        current_root = rel_path.parts[0]

        # 1. GLOBAL CANDIDATE DETECTION (Vacuum to apps_shared)
        # If file is in an app folder but has near-ZERO domain DNA (Resume or LinkedIn)
        if current_root in ["apps_rg", "apps_lic"]:
            # Threshold: < 0.5 indicates purely generic utility logic (e.g., date_helper.py)
            if app_rg_score < 0.5 and app_lic_score < 0.5:
                # Disqualify files that already carry explicit app-specific prefixes
                filename = rel_path.name
                if not filename.startswith(("rg_", "lic_", "resume_", "outreach_")):
                    # Violation triggers move to apps_shared/utils (Weight 95)
                    return (
                        False,
                        "GLOBAL CANDIDATE DETECTED: Low domain signals - belongs in apps_shared/utils",
                    )

        # 2. CROSS-CONTAMINATION CHECK (App vs App)
        if current_root == "apps_rg" and app_lic_score > app_rg_score * 2.0:
            return (
                False,
                f"APP DOMAIN VIOLATION: Strong apps_lic signals ({app_lic_score:.1f} vs {app_rg_score:.1f})",
            )

        if current_root == "apps_lic" and app_rg_score > app_lic_score * 2.0:
            return (
                False,
                f"APP DOMAIN VIOLATION: Strong apps_rg signals ({app_rg_score:.1f} vs {app_lic_score:.1f})",
            )

        return True, ""

    def _check_territory_alignment(
        self, current_territory: str, territory_scores: dict[str, float], rel_path: Path
    ) -> tuple[bool, str]:
        """Check territory alignment between file location and content."""
        from agentic_core.L5_safety.validators.structure_blueprint import (
            MIN_ALIGNMENT_SCORE,
            TERRITORY_MISMATCH_THRESHOLD,
        )

        if not territory_scores:
            return True, "OK"

        current_score = territory_scores.get(current_territory, 0.0)
        best_territory = max(territory_scores, key=territory_scores.get)
        max_other = max(
            (s for t, s in territory_scores.items() if t != current_territory), default=0.0
        )

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

        return True, "OK"

    # AST scoring utility methods (used by semantic alignment)
    def _collect_ast_increments(
        self, tree: Any, territory_keywords: dict[str, Any]
    ) -> list[tuple[str, float]]:
        """Collect AST-based scoring increments."""
        import ast

        increments = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef | ast.FunctionDef):
                for terr, cats in territory_keywords.items():
                    for terms in cats.values():
                        if any(t in node.name.lower() for t in terms):
                            increments.append((terr, 1.0))

        return increments

    def _aggregate_ast_increments(self, increments: list[tuple[str, float]]) -> dict[str, float]:
        """Aggregate scoring increments into territory scores."""
        scores: dict[str, float] = {}
        for terr, score in increments:
            scores[terr] = scores.get(terr, 0.0) + score
        return scores

    def _recompute_ast_scores(
        self, tree: Any, territory_keywords: dict[str, Any]
    ) -> tuple[float, float, dict[str, float]]:
        """Recompute AST scores (wrapper for _calculate_semantic_scores)."""
        return self._calculate_semantic_scores(tree)

    def _score_identifier(self, name: str, territory_keywords: dict[str, Any]) -> float:
        """Score an identifier name against territory keywords."""
        score = 0.0
        name_lower = name.lower()
        for _terr, cats in territory_keywords.items():
            for terms in cats.values():
                if any(t in name_lower for t in terms):
                    score += 1.0
        return score

    def _score_string(self, value: str, territory_keywords: dict[str, Any]) -> float:
        """Score a string value against territory keywords."""
        return self._score_identifier(value, territory_keywords)

    def _score_variable(self, name: str, territory_keywords: dict[str, Any]) -> float:
        """Score a variable name against territory keywords."""
        return self._score_identifier(name, territory_keywords)

    def _score_assignments(self, node: Any, territory_keywords: dict[str, Any]) -> float:
        """Score assignment nodes."""
        import ast

        score = 0.0
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    score += self._score_identifier(target.id, territory_keywords)
        return score

    def _score_arguments(self, node: Any, territory_keywords: dict[str, Any]) -> float:
        """Score function arguments."""
        import ast

        score = 0.0
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            for arg in node.args.args:
                score += self._score_identifier(arg.arg, territory_keywords)
        return score

    # Naming convention validation (used by validation chain)
    def _check_naming_conventions(self, file_path: Path) -> list[str]:
        """Check naming conventions for file."""
        violations = []

        # Check for forbidden prefixes
        from agentic_core.L5_safety.validators.structure_blueprint import has_forbidden_layer_prefix

        forbidden_prefix = has_forbidden_layer_prefix(file_path.name)
        if forbidden_prefix:
            violations.append(f"Forbidden layer prefix: {forbidden_prefix}")

        # Check for backup file patterns
        if file_path.name.endswith((".bak", ".backup", ".old", ".tmp")):
            violations.append("Backup file pattern detected")

        return violations

    # Validation orchestration
    def run(self, target_territory: str | None = None) -> dict[str, Any]:
        """
        Execute validation-only scan across sovereign territories.

        Args:
            target_territory: If provided, restricts scan to this domain (Strict Targeting).

        Phase 4.1 Upgrade: Universal root scanning using SOVEREIGN_TERRITORIES.
        """
        from agentic_core.L5_safety.validators.structure_blueprint import SOVEREIGN_TERRITORIES

        violations = []
        compliant_files = 0
        total_files = 0
        roots_scanned = []

        # [STRICT SCOPE] Target specific roots or all
        if target_territory:
            target_roots = (
                [target_territory]
                if target_territory in SOVEREIGN_TERRITORIES
                else ["agentic_core"]
            )
        else:
            target_roots = list(SOVEREIGN_TERRITORIES.keys())

        # Scan targeted roots
        for root_name in target_roots:
            root_path = self.project_root / root_name
            if not root_path.exists():
                continue

            roots_scanned.append(root_name)

            # Scan Python files in this root
            for py_file in root_path.rglob("*.py"):
                # Skip common ignore patterns
                if any(
                    skip in py_file.parts
                    for skip in [
                        "__pycache__",
                        ".git",
                        "archives",
                        ".venv",
                        ".sovereign_healing_backup",
                        "node_modules",
                    ]
                ):
                    continue

                total_files += 1
                is_valid, reason = self.validate_file_location(py_file)

                if is_valid:
                    compliant_files += 1
                else:
                    violations.append({"file": str(py_file), "reason": reason})

        return {
            "violations": violations,
            "total_files_scanned": total_files,
            "compliant_files": compliant_files,
            "roots_scanned": roots_scanned,
            "status": "COMPLETE",
        }
