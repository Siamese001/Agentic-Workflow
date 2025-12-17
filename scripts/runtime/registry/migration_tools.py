"""Migration Tools - Utilities for transitioning from K-nodes to functional roles.

This module provides tools to help migrate existing code and configurations
"""

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List

LOGGER = logging.getLogger(__name__)


class KNodeScanner:
    """Scans codebase for legacy K-node references."""

    # Patterns to find K-node references
    PATTERNS = [
        r'\bK\.?\d+\b',  # K.2, K2, K.3, etc.
        r'\bk_node_\w+',  # k_node_researcher, etc.
        r'\bK\d+[A-Za-z]*\b',  # K3_agent, K5_validator, etc.
        r'"[^"]*K\.?\d+[^"]*"',  # Strings containing K-nodes
        r'\'[^\']*K\.?\d+[^\']*\'',  # Single quotes
    ]

    def __init__(self, root_path: Path):
        """Initialize scanner.

        Args:
            root_path: Root directory to scan
        """
        self.root_path = root_path
        self.findings: List[Dict[str, Any]] = []

    def scan_directory(self, extensions: List[str] = None) -> Dict[str, Any]:
        """Scan directory for K-node references.

        Args:
            extensions: File extensions to scan (default: .py, .md, .json)

        Returns:
            Scan results
        """
        if extensions is None:
            EXTENSIONS = ['.py', '.md', '.json', '.yaml', '.yml']
        else:
            EXTENSIONS = extensions

        RESULTS = {
            "total_files": 0,
            "files_with_references": 0,
            "total_references": 0,
            "files": []
        }

        for ext in EXTENSIONS:
            for file_path in self.root_path.rglob(f"*{ext}"):
                # Skip certain directories
                if any(skip in str(file_path) for skip in ['.git', '__pycache__', '.venv']):
                    continue

                file_results = self.scan_file(file_path)
                if file_results["references"]:
                    RESULTS["files"].append(file_results)
                    RESULTS["files_with_references"] += 1
                    RESULTS["total_references"] += len(file_results["references"])

                RESULTS["total_files"] += 1

        return RESULTS

    def scan_file(self, file_path: Path) -> Dict[str, Any]:
        """Scan a single file for K-node references.

        Args:
            file_path: File to scan

        Returns:
            Scan results for the file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                CONTENT = f.read()
        except Exception as e:
LOGGER.error(f"Failed to read {file_path}: {e}")
            return {"path": str(file_path), "references": [], "error": str(e)}

        REFERENCES = []
        line_number = 1

        for line in CONTENT.split('\n'):
            for pattern in self.PATTERNS:
                MATCHES = re.finditer(pattern, line, re.IGNORECASE)
                for match in MATCHES:
                    # Check if it's actually a K-node reference
                    TEXT = match.group()
                    if self._is_knode_reference(TEXT):
                        REFERENCES.append({
                            "line": line_number,
                            "column": match.start() + 1,
                            "text": TEXT,
                            "context": line.strip()
                        })
            line_number += 1

        return {
            "path": str(file_path),
            "references": REFERENCES
        }

    def _is_knode_reference(self, text: str) -> bool:
        """Check if text is actually a K-node reference.

        Args:
            text: Text to check

        Returns:
            True if K-node reference
        """
        # Remove quotes
        TEXT = text.strip('"\'')

        # Check patterns
        if re.match(r'^K\.?\d+$', TEXT):
            return True

        if re.match(r'^k_node_', TEXT, re.IGNORECASE):
            return True

        if re.match(r'^K\d+[A-Za-z]*$', TEXT):
            return True

        return False


# Dummy LEGACY_MAPPING and role.value for testing purposes
LEGACY_MAPPING = {
    "K1": "AgentRole.RESEARCHER",
    "K2": "AgentRole.WRITER",
    "K4": "AgentRole.CRITIC"
}

class AgentRole:
    RESEARCHER = "researcher"
    WRITER = "writer"
    CRITIC = "critic"

class KNodeMigrator:
    """Migrates K-node references to functional roles."""

    def __init__(self):
        """Initialize migrator."""
        self.REPLACEMENTS = self._build_replacement_map()

    def _build_replacement_map(self) -> Dict[str, str]:
        """Build replacement map for migration.

        Returns:
            Dictionary mapping legacy references to functional roles
        """
        REPLACEMENTS = {}

        # Direct mappings
        for legacy, role_enum_str in LEGACY_MAPPING.items():
            # Assuming role_enum_str is like "AgentRole.RESEARCHER"
            # We need to extract the actual value. This is a simplification.
            try:
                module_name, attr_name = role_enum_str.split('.')
                role_value = getattr(globals()[module_name], attr_name)
            except (ValueError, KeyError, AttributeError):
# Fallback if parsing fails, or use a default
                role_value = role_enum_str.split('.')[-1] # e.g., "RESEARCHER"

            REPLACEMENTS[legacy] = role_value
            REPLACEMENTS[legacy.lower()] = role_value
            REPLACEMENTS[legacy.upper()] = role_value

        # Common variations
        REPLACEMENTS.update({
            "K.2": "context_gatherer",
            "K2": "context_gatherer",
            "K.3": "content_drafter",
            "K3": "content_drafter",
            "K.5": "quality_critic",
            "K5": "quality_critic",
            "k_node_researcher": "context_gatherer",
            "k_node_writer": "content_drafter",
            "k_node_critic": "quality_critic",
            "K3_agent": "content_drafter",
            "K5_validator": "quality_critic"
        })

        return REPLACEMENTS

    def migrate_file(self, file_path: Path, backup: bool = True) -> bool:
        """Migrate a file from K-nodes to functional roles.

        Args:
            file_path: File to migrate
            backup: Whether to create backup

        Returns:
            True if migration successful
        """
        try:
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                CONTENT = f.read()

            # Create backup
            backup_path = None
            if backup:
                backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(CONTENT)

            # Apply replacements
            migrated_content = CONTENT
            changes_made = False

            for legacy, functional in self.REPLACEMENTS.items():
                if legacy in migrated_content:
                    migrated_content = migrated_content.replace(legacy, functional)
                    changes_made = True
                    LOGGER.info(f"Replaced {legacy} with {functional} in {file_path}")

            # Write migrated content
            if changes_made:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(migrated_content)
                return True
            else:
                # No changes needed, remove backup
                if backup and backup_path and backup_path.exists():
                    backup_path.unlink()
                return False

        except Exception as e:
LOGGER.error(f"Failed to migrate {file_path}: {e}")
            return False

    def migrate_configuration(self, config_path: Path) -> bool:
        """Migrate configuration files.

        Args:
            config_path: Path to configuration file

        Returns:
            True if migration successful
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                CONFIG = json.load(f)

            # Track changes
            changes_made = False

            # Recursively migrate
            def migrate_dict(d: Dict, path: str = "") -> None:
                """Recursively migrate dictionary values."""
                nonlocal changes_made

                for key, value in d.items():
                    current_path = f"{path}.{key}" if path else key

                    if isinstance(value, str):
                        for legacy, functional in self.REPLACEMENTS.items():
                            if legacy in value:
                                d[key] = value.replace(legacy, functional)
                                changes_made = True
                                LOGGER.info(f"Migrated config value at {current_path}")
                    elif isinstance(value, dict):
                        migrate_dict(value, current_path)
                    elif isinstance(value, list):
                        for i, item in enumerate(value):
                            if isinstance(item, str):
                                for legacy, functional in self.REPLACEMENTS.items():
                                    if legacy in item:
                                        d[key][i] = item.replace(legacy, functional)
                                        changes_made = True
                                        LOGGER.info(f"Migrated config list item at {current_path}[{i}]")

            migrate_dict(CONFIG)

            # Write back if changed
            if changes_made:
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(CONFIG, f, indent=2)
                return True

            return False

        except Exception as e:
LOGGER.error(f"Failed to migrate configuration {config_path}: {e}")
            return False


class MigrationValidator:
    """Validates that migration was successful."""

    def __init__(self):
        """Initialize validator."""
        self.SCANNER = KNodeScanner(Path("."))

    def validate_migration(self, root_path: Path) -> Dict[str, Any]:
        """Validate that all K-node references have been migrated.

        Args:
            root_path: Root path to validate

        Returns:
            Validation results
        """
        LOGGER.info("Validating migration...")

        # Scan for remaining references
        RESULTS = self.SCANNER.scan_directory()

        # Analyze results
        VALIDATION = {
            "is_valid": RESULTS["total_references"] == 0,
            "remaining_references": RESULTS["total_references"],
            "files_with_issues": RESULTS["files_with_references"],
            "problem_files": []
        }

        # Categorize issues
        for file_result in RESULTS["files"]:
            ISSUES = []
            for ref in file_result["references"]:
                # Check if it's a false positive
                TEXT = ref["text"]
                if not self._is_false_positive(TEXT, file_result["path"]):
                    ISSUES.append(ref)

            if ISSUES:
                VALIDATION["problem_files"].append({
                    "path": file_result["path"],
                    "issues": ISSUES
                })

        return VALIDATION

    def _is_false_positive(self, text: str, file_path: str) -> bool:
        """Check if a reference is a false positive.

        Args:
            text: The reference text
            file_path: Path of the file containing the reference

        Returns:
            True if false positive
        """
        # Skip test files
        if "test" in file_path.lower():
            if "K.3" in text or "K5" in text:
                # Test files might be testing the legacy system
                return True

        # Skip comments that explain the legacy system
        if "//" in text or "#" in text:
            if "legacy" in text.lower() or "old" in text.lower():
                return True

        # Skip documentation about the migration
        if "migration" in file_path.lower():
            return True

        return False


def run_full_migration(root_path: Path, dry_run: bool = False) -> Dict[str, Any]:
    """Run the complete migration process.

    Args:
        root_path: Root path to migrate
        dry_run: If True, only scan without making changes

    Returns:
        Migration results
    """
    LOGGER.info(f"Starting {'dry run ' if dry_run else ''}migration from {root_path}")

    RESULTS = {
        "scan": None,
        "migration": None,
        "validation": None,
        "success": False
    }

    # Step 1: Scan for references
    SCANNER = KNodeScanner(root_path)
    RESULTS["scan"] = SCANNER.scan_directory()

    LOGGER.info(f"Found {RESULTS['scan']['total_references']} K-node references "
                f"in {RESULTS['scan']['files_with_references']} files")

    if dry_run:
        LOGGER.info("Dry run complete - no changes made")
        RESULTS["success"] = True
        return RESULTS

    # Step 2: Migrate files
    MIGRATOR = KNodeMigrator()
    migrated_files = 0

    for file_result in RESULTS["scan"]["files"]:
        file_path = Path(file_result["path"])
        if MIGRATOR.migrate_file(file_path):
            migrated_files += 1

    RESULTS["migration"] = {
        "files_migrated": migrated_files,
        "total_files_with_refs": RESULTS["scan"]["files_with_references"]
    }

    LOGGER.info(f"Migrated {migrated_files} files")

    # Step 3: Validate migration
    VALIDATOR = MigrationValidator()
    RESULTS["validation"] = VALIDATOR.validate_migration(root_path)

    if RESULTS["validation"]["is_valid"]:
        LOGGER.info("Migration completed successfully!")
        RESULTS["success"] = True
    else:
        LOGGER.warning(f"Migration incomplete: {RESULTS['validation']['remaining_references']} references remain")

    return RESULTS


# Convenience function
def migrate_project(root_path: str = ".", dry_run: bool = False) -> bool:
    """Migrate an entire project from K-nodes to functional roles.

    Args:
        root_path: Root path of the project
        dry_run: If True, only scan without changes

    Returns:
        True if migration successful
    """
    PATH = Path(root_path).resolve()
    RESULTS = run_full_migration(PATH, dry_run)

    return RESULTS["success"]

