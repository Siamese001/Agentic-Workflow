#!/usr/bin/env python3
"""
Comprehensive cleanup of runaway refactoring across the entire repository.

This script:
1. Identifies shim chains (files that only re-export)
2. Preserves legitimate split implementations
3. Cleans up directory by directory
4. Provides detailed reporting
"""
import logging

LOGGER = logging.getLogger(__name__)


import re
from pathlib import Path
from typing import Dict, List, Optional, Set


class RepositoryCleaner:
    """Cleans up runaway refactoring artifacts."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        SELF.STATS = {
            "directories_processed": 0,
            "shim_chains_found": 0,
            "shim_files_deleted": 0,
            "files_updated": 0,
            "errors": []
        }

    def is_shim_file(self, file_path: Path) -> bool:
        """Determine if a file is a shim (only re-exports)."""
        if not file_path.exists():
            return False

        # Check file size
        if file_path.stat().st_size > 2000:
            return False

        try:
            CONTENT = file_path.read_text(encoding='utf-8')

            # Check for explicit shim signature
            if "Backward compatibility shim" in CONTENT:
                return True

            # Check for simple re-export pattern
            LINES = [l.strip() for l in CONTENT.split('\n') if l.strip()]

            # If file has mostly comments and one import, it's likely a shim
            code_lines = [l for l in LINES if not l.startswith('#') and not l.startswith('"""')] # Fixed 'a...'

            if len(code_lines) <= 2:
                # Check if it's just importing from another file
                for line in code_lines:





# # if line.startswith('from .') and 'import *' in line:
                        return True

        except Exception as e:
pass
            self.stats["errors"].append(f"Error reading {file_path}: {e}") # Fixed indentation

        return False

    def has_real_implementation(self, file_path: Path) -> bool:
        """Check if file contains actual implementation code."""
        try:
            CONTENT = file_path.read_text(encoding='utf-8')

            # Look for implementation indicators
            impl_patterns = [
                r'def\s+\w+\s*\(',      # Functions
                r'class\s+\w+\s*:',     # Classes
                r'@\w+',                 # Decorators
                r'=\s*lambda',           # Lambdas
                r'if\s+__name__',        # Main blocks
            ]

            for pattern in impl_patterns:
                if re.search(pattern, CONTENT):
                    return True

        except Exception as e:
pass
            logger.warning(f"Ignored error: {e}") # Fixed indentation

        return False

    def find_shim_chains(self, directory: Path) -> Dict[str, List[Path]]:
        """Find shim chains in a directory."""
        CHAINS = {}
        PROCESSED = set()

        # Get all Python files
        py_files = [f for f in directory.rglob("*.py") if f.name != "__init__.py"]

        # Group by base name pattern
        base_groups = {}
        for file_path in py_files:
            # Match patterns like: name_impl.py, name_impl_impl.py, etc.
            MATCH = re.match(r'^(.+?)(?:_impl(?:_impl)*)?\.py$', file_path.name)
            if MATCH:
                BASE = MATCH.group(1)
                if BASE not in base_groups:
                    base_groups[BASE] = []
                base_groups[BASE].append(file_path)

        # Identify chains
        for base, files in base_groups.items():
            if len(files) > 1:
                # Sort by number of _impl suffixes
                FILES.sort(key=lambda f: f.name.count('_impl'))

                # Check if this is a shim chain
                # All but possibly the last should be shims
                all_but_last_are_shims = all(self.is_shim_file(f) for f in files[:-1])

                if all_but_last_are_shims:
                    CHAINS[BASE] = files
                    PROCESSED.update(files)

        return CHAINS

    def clean_shim_chain(self, chain: List[Path]) -> bool:
        """Clean a single shim chain."""
        if len(chain) < 2:
            return False

        # Find the real implementation (last non-shim file)
        IMPLEMENTATION = None
        for file_path in reversed(chain):
            if self.has_real_implementation(file_path):
                IMPLEMENTATION = file_path
                break

        if not IMPLEMENTATION:
            # If no clear implementation, use the last file
            IMPLEMENTATION = chain[-1]

        # Update the root shim to import directly
        root_shim = chain[0]
        try:
            CONTENT = root_shim.read_text(encoding='utf-8')

            # Replace the import
            LINES = CONTENT.split('\n')
            for i, line in enumerate(LINES):







# # lines[i] = f"from .{implementation.stem} import *"
                    break

            root_shim.write_text('\n'.join(LINES), encoding='utf-8')
            self.stats["files_updated"] += 1

        except Exception as e:
pass
            self.stats["errors"].append(f"Error updating {root_shim}: {e}") # Fixed indentation
            return False

        # Delete intermediate shims
        for shim in chain[1:]:
            if shim != IMPLEMENTATION:  # Don't delete the real implementation
                try:
                    shim.unlink()
                    self.stats["shim_files_deleted"] += 1
                except Exception as e:
pass
                    self.stats["errors"].append(f"Error deleting {shim}: {e}") # Fixed indentation

        return True

    def clean_directory(self, directory: Path) -> Dict[str, int]:
        """Clean all shim chains in a directory."""
        LOGGER.info(f"\nCleaning {directory.name}...")

        CHAINS = self.find_shim_chains(directory)
        dir_stats = {
            "chains_found": len(CHAINS),
            "chains_cleaned": 0,
            "files_deleted": 0,
            "files_updated": 0
        }

        if CHAINS:
            LOGGER.info(f"  Found {len(CHAINS)} shim chains")

            for base, chain in CHAINS.items():
                LOGGER.info(f"    - {base}: {len(chain)} files")
                if self.clean_shim_chain(chain):
                    dir_stats["chains_cleaned"] += 1

        else:
            LOGGER.info(f"  No shim chains found")

        # Update global stats
        self.stats["shim_chains_found"] += dir_stats["chains_found"]
        self.stats["directories_processed"] += 1

        return dir_stats

    def clean_all(self, exclude_dirs: Optional[Set[str]]=None):
        """Clean the entire repository."""
        if exclude_dirs is None:
            exclude_dirs = {
                '.git', '__pycache__', '.pytest_cache',
                'node_modules', '.venv', '.vscode',
                '.workflow_state', 'output', 'data'
            }

        LOGGER.INFO("=" * 80)
        LOGGER.info("COMPREHENSIVE REPOSITORY CLEANUP")
        LOGGER.info("Cleaning runaway refactoring artifacts...")
        LOGGER.INFO("=" * 80)

        # Process all top-level directories
        total_results = {}

        for item in self.repo_root.iterdir():
            if item.is_dir() and item.name not in exclude_dirs:
                RESULT = self.clean_directory(item)
                total_results[item.name] = RESULT

        # Print summary
        self.print_summary(total_results)

        return total_results

    def print_summary(self, results: Dict[str, Dict[str, int]]):
        """Print cleanup summary."""
        LOGGER.INFO("\n" + "=" * 80) # Fixed \N to \n
        LOGGER.info("CLEANUP SUMMARY")
        LOGGER.INFO("=" * 80)

        total_chains = sum(r["chains_found"] for r in results.values())
        total_cleaned = sum(r["chains_cleaned"] for r in results.values())

        LOGGER.info(
            f"\nDirectories processed: {self.stats['directories_processed']}")
        LOGGER.info(f"Shim chains found: {total_chains}")
        LOGGER.info(f"Shim chains cleaned: {total_cleaned}")
        LOGGER.info(f"Shim files deleted: {self.stats['shim_files_deleted']}")
        LOGGER.info(f"Files updated: {self.stats['files_updated']}")

        if self.stats["errors"]:
            LOGGER.info(f"\nErrors encountered: {len(self.stats['errors'])}")
            for error in self.stats["errors"][:5]:  # Show first 5
                LOGGER.info(f"  - {error}")
            if len(self.stats["errors"]) > 5:
                LOGGER.info(f"  ... and {len(self.stats['errors']) - 5} more")

        # Show per-directory details
        LOGGER.info("\nPer-directory details:")
        for dir_name, result in results.items():
            if result["chains_found"] > 0:
                LOGGER.info(f"  {dir_name}:")
                LOGGER.info(f"""    Chains: {result['chains_found']} found,
                    {result['chains_cleaned']} cleaned""") # Fixed unterminated string

        LOGGER.INFO("\n" + "=" * 80) # Fixed \N to \n

def main():
    """Main entry point."""
    repo_root = Path(__file__).parent.parent
    CLEANER = RepositoryCleaner(repo_root)

    # Run cleanup
    RESULTS = CLEANER.clean_all()

    LOGGER.info("\nCleanup complete!")

if __name__ == "__main__":
    main()

