"""Migration Tools - Utilities for transitioning from K-nodes to functional roles.

This module provides tools to help migrate existing code and configurations
from the legacy K-node system to the new functional role architecture.
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

from .agent_capabilities import AgentRole, LEGACY_MAPPING, LegacyCodeError

logger = logging.getLogger(__name__)


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
            extensions = ['.py', '.md', '.json', '.yaml', '.yml']

        results = {
            "total_files": 0,
            "files_with_references": 0,
            "total_references": 0,
            "files": []
        }

        for ext in extensions:
            for file_path in self.root_path.rglob(f"*{ext}"):
                # Skip certain directories
                if any(skip in str(file_path) for skip in ['.git', '__pycache__', '.venv']):
                    continue

                file_results = self.scan_file(file_path)
                if file_results["references"]:
                    results["files"].append(file_results)
                    results["files_with_references"] += 1
                    results["total_references"] += len(file_results["references"])

                results["total_files"] += 1

        return results

    def scan_file(self, file_path: Path) -> Dict[str, Any]:
        """Scan a single file for K-node references.

        Args:
            file_path: File to scan

        Returns:
            Scan results for the file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")
            return {"path": str(file_path), "references": [], "error": str(e)}

        references = []
        line_number = 1

        for line in content.split('\n'):
            for pattern in self.PATTERNS:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    # Check if it's actually a K-node reference
                    text = match.group()
                    if self._is_knode_reference(text):
                        references.append({
                            "line": line_number,
                            "column": match.start() + 1,
                            "text": text,
                            "context": line.strip()
                        })
            line_number += 1

        return {
            "path": str(file_path),
            "references": references
        }

    def _is_knode_reference(self, text: str) -> bool:
        """Check if text is actually a K-node reference.

        Args:
            text: Text to check

        Returns:
            True if K-node reference
        """
        # Remove quotes
        text = text.strip('"\'')

        # Check patterns
        if re.match(r'^K\.?\d+$', text):
            return True

        if re.match(r'^k_node_', text, re.IGNORECASE):
            return True

        if re.match(r'^K\d+[A-Za-z]*$', text):
            return True

        return False


class KNodeMigrator:
    """Migrates K-node references to functional roles."""

    def __init__(self):
        """Initialize migrator."""
        self.replacements = self._build_replacement_map()

    def _build_replacement_map(self) -> Dict[str, str]:
        """Build replacement map for migration.

        Returns:
            Dictionary mapping legacy references to functional roles
        """
        replacements = {}

        # Direct mappings
        for legacy, role in LEGACY_MAPPING.items():
            replacements[legacy] = role.value
            replacements[legacy.lower()] = role.value
            replacements[legacy.upper()] = role.value

        # Common variations
        replacements.update({
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

        return replacements

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
                content = f.read()

            # Create backup
            if backup:
                backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(content)

            # Apply replacements
            migrated_content = content
            changes_made = False

            for legacy, functional in self.replacements.items():
                if legacy in migrated_content:
                    migrated_content = migrated_content.replace(legacy, functional)
                    changes_made = True
                    logger.info(f"Replaced {legacy} with {functional} in {file_path}")

            # Write migrated content
            if changes_made:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(migrated_content)
                return True
            else:
                # No changes needed, remove backup
                if backup and backup_path.exists():
                    backup_path.unlink()
                return False

        except Exception as e:
            logger.error(f"Failed to migrate {file_path}: {e}")
            return False

    def migrate_configuration(self, config_path: Path) -> bool:
        """Migrate configuration files.

        Args:
            config_path: Path to configuration file

        Returns:
            True if migration successful
        """
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)

            # Track changes
            changes_made = False

            # Recursively migrate
            def migrate_dict(d: Dict, path: str = "") -> None:
                nonlocal changes_made

                for key, value in d.items():
                    current_path = f"{path}.{key}" if path else key

                    if isinstance(value, str):
                        for legacy, functional in self.replacements.items():
                            if legacy in value:
                                d[key] = value.replace(legacy, functional)
                                changes_made = True
                                logger.info(f"Migrated config value at {current_path}")
                    elif isinstance(value, dict):
                        migrate_dict(value, current_path)
                    elif isinstance(value, list):
                        for i, item in enumerate(value):
                            if isinstance(item, str):
                                for legacy, functional in self.replacements.items():
                                    if legacy in item:
                                        value[i] = item.replace(legacy, functional)
                                        changes_made = True
                                        logger.info(f"Migrated config list item at {current_path}[{i}]")

            migrate_dict(config)

            # Write back if changed
            if changes_made:
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=2)
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to migrate configuration {config_path}: {e}")
            return False


class MigrationValidator:
    """Validates that migration was successful."""

    def __init__(self):
        """Initialize validator."""
        self.scanner = KNodeScanner(Path("."))

    def validate_migration(self, root_path: Path) -> Dict[str, Any]:
        """Validate that all K-node references have been migrated.

        Args:
            root_path: Root path to validate

        Returns:
            Validation results
        """
        logger.info("Validating migration...")

        # Scan for remaining references
        results = self.scanner.scan_directory()

        # Analyze results
        validation = {
            "is_valid": results["total_references"] == 0,
            "remaining_references": results["total_references"],
            "files_with_issues": results["files_with_references"],
            "problem_files": []
        }

        # Categorize issues
        for file_result in results["files"]:
            issues = []
            for ref in file_result["references"]:
                # Check if it's a false positive
                text = ref["text"]
                if not self._is_false_positive(text, file_result["path"]):
                    issues.append(ref)

            if issues:
                validation["problem_files"].append({
                    "path": file_result["path"],
                    "issues": issues
                })

        return validation

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
    logger.info(f"Starting {'dry run ' if dry_run else ''}migration from {root_path}")

    results = {
        "scan": None,
        "migration": None,
        "validation": None,
        "success": False
    }

    # Step 1: Scan for references
    scanner = KNodeScanner(root_path)
    results["scan"] = scanner.scan_directory()

    logger.info(f"Found {results['scan']['total_references']} K-node references "
                f"in {results['scan']['files_with_references']} files")

    if dry_run:
        logger.info("Dry run complete - no changes made")
        results["success"] = True
        return results

    # Step 2: Migrate files
    migrator = KNodeMigrator()
    migrated_files = 0

    for file_result in results["scan"]["files"]:
        file_path = Path(file_result["path"])
        if migrator.migrate_file(file_path):
            migrated_files += 1

    results["migration"] = {
        "files_migrated": migrated_files,
        "total_files_with_refs": results["scan"]["files_with_references"]
    }

    logger.info(f"Migrated {migrated_files} files")

    # Step 3: Validate migration
    validator = MigrationValidator()
    results["validation"] = validator.validate_migration(root_path)

    if results["validation"]["is_valid"]:
        logger.info("Migration completed successfully!")
        results["success"] = True
    else:
        logger.warning(f"Migration incomplete: {results['validation']['remaining_references']} references remain")

    return results


# Convenience function
def migrate_project(root_path: str = ".", dry_run: bool = False) -> bool:
    """Migrate an entire project from K-nodes to functional roles.

    Args:
        root_path: Root path of the project
        dry_run: If True, only scan without changes

    Returns:
        True if migration successful
    """
    path = Path(root_path).resolve()
    results = run_full_migration(path, dry_run)

    return results["success"]
