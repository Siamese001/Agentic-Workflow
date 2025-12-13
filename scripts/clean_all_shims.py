#!/usr/bin/env python3
"""
Comprehensive script to clean up all shim chains across the repository.
import logging

logger = logging.getLogger(__name__)

"""

import re
from pathlib import Path

def find_shim_chains(directory: Path) -> Dict[str, List[Path]]:
    """Find all shim chains in a directory."""
    chains = {}

    # Get all Python files
    py_files = [f for f in directory.rglob("*.py") if f.name != "__init__.py"]

    # Group by base name (remove _impl suffixes)
    base_groups = {}
    for file_path in py_files:
        # Extract base name before any _impl
        match = re.match(r'^(.+?)(?:_impl(?:_impl)*)?\.py$', file_path.name)
        if match:
            base = match.group(1)
            if base not in base_groups:
                base_groups[base] = []
            base_groups[base].append(file_path)

    # Identify chains (multiple files with same base)
    for base, files in base_groups.items():
        if len(files) > 1:
            # Sort by number of _impl suffixes
            files.sort(key=lambda f: f.name.count('_impl'))
            chains[base] = files

    return chains

def is_shim_file(file_path: Path) -> bool:
    """Check if a file is a shim."""
    try:
        content = file_path.read_text(encoding='utf-8')

        # Check size
        if file_path.stat().st_size > 2000:
            return False

        # Check for shim signature
        if "Backward compatibility shim" in content and "re-export all components" in content:
            return True

        # Check for simple import structure
        lines = [l.strip() for l in content.split('\n') if l.strip() and not l.strip().startswith('#')]
        if len(lines) <= 3 and any('from .' in l and 'import *' in l for l in lines):
            return True

    except Exception:
        pass

    return False

def find_real_implementation(chain: List[Path]) -> Path:
    """Find the real implementation at the end of the chain."""
    for file_path in reversed(chain):
        if not is_shim_file(file_path):
            return file_path
    return chain[-1]  # Fallback to last file

def clean_directory(directory: Path, dry_run: bool = True) -> Dict[str, int]:
    """Clean all shim chains in a directory."""
    chains = find_shim_chains(directory)

    stats = {
        "chains_found": len(chains),
        "files_deleted": 0,
        "files_updated": 0
    }

    logger.info(f"\n{directory.name}:")
    logger.info(f"  Found {len(chains)} shim chains")

    for base, chain in chains.items():
        if len(chain) < 2:
            continue

        # Find real implementation
        impl = find_real_implementation(chain)

        # Root shim (first in chain)
        root = chain[0]

        # Intermediate shims to delete
        to_delete = chain[1:-1] if impl != chain[-1] else chain[1:]

        logger.info(f"    {base}: {len(chain)} files -> {impl.name}")

        if not dry_run:
            # Update root shim
            try:
                content = root.read_text(encoding='utf-8')
                # Replace import
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.startswith('from .') and 'import *' in line:
                        lines[i] = f"from .{impl.stem} import *"
                        break
                root.write_text('\n'.join(lines), encoding='utf-8')
                stats["files_updated"] += 1
            except Exception as e:
                logger.info(f"      Error updating {root}: {e}")

        # Always track files to be deleted
        stats["files_deleted"] += len(to_delete)

        if not dry_run:
            # Delete intermediate shims
            for shim in to_delete:
                try:
                    shim.unlink()
                except Exception as e:
                    logger.info(f"      Error deleting {shim}: {e}")

    return stats

def main():
    """Main entry point."""
    repo_root = Path("c:/Git/Agentic-Workflow")

    logger.info("Scanning for shim chains...")
    logger.info("=" * 60)

    # Directories to clean
    dirs_to_clean = [
        "apps_lic", "apps_rg", "apps_shared",
        "config", "observability", "prompt_governance",
        "schemas", "scripts", "shared"
    ]

    total_stats = {
        "chains_found": 0,
        "files_to_delete": 0,
        "files_to_update": 0
    }

    # First do a dry run
    logger.info("\nDRY RUN - No files will be modified:")
    logger.info("-" * 60)

    for dir_name in dirs_to_clean:
        dir_path = repo_root / dir_name
        if dir_path.exists():
            stats = clean_directory(dir_path, dry_run=True)
            for key in total_stats:
                total_stats[key] += stats[key]

    logger.info("\n" + "=" * 60)
    logger.info("DRY RUN SUMMARY:")
    logger.info(f"  Total chains found: {total_stats['chains_found']}")
    logger.info(f"  Files to delete: {total_stats['files_deleted']}")
    logger.info(f"  Files to update: {total_stats['files_updated']}")

    # Ask for confirmation
    response = input("\nProceed with cleanup? (y/N): ")
    if response.lower() != 'y':
        logger.info("Aborted.")
        return

    # Actual cleanup
    logger.info("\nEXECUTING CLEANUP:")
    logger.info("-" * 60)

    # Reset stats for actual run
    total_stats = {
        "chains_found": 0,
        "files_deleted": 0,
        "files_updated": 0
    }

    for dir_name in dirs_to_clean:
        dir_path = repo_root / dir_name
        if dir_path.exists():
            stats = clean_directory(dir_path, dry_run=False)
            # The clean_directory function returns files_to_delete for dry run
            # but files_deleted for actual run
            if "files_deleted" in stats:
                for key in total_stats:
                    if key in stats:
                        total_stats[key] += stats[key]
            else:
                # Handle case where it might still return old keys
                for key in total_stats:
                    total_stats[key] += stats.get(key, 0)

    logger.info("\n" + "=" * 60)
    logger.info("CLEANUP COMPLETE:")
    logger.info(f"  Total chains cleaned: {total_stats['chains_found']}")
    logger.info(f"  Files deleted: {total_stats['files_deleted']}")
    logger.info(f"  Files updated: {total_stats['files_updated']}")

if __name__ == "__main__":
    main()
