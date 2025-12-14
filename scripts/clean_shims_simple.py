#!/usr/bin/env python3
"""
Simple script to clean up shim chains by manually specifying the patterns.
import logging

logger = logging.getLogger(__name__)

"""

from pathlib import Path


def clean_prompt_governance():
    """Clean up shim chains in prompt_governance."""
    pg_dir = Path("c:/Git/Agentic-Workflow/prompt_governance")

    # Update root files to import directly from implementations
    updates = {
        "prompts.py": "prompts_v7_impl",
        "prompts_final.py": "prompts_v7_impl",
        "prompts_impl.py": "prompts_v7_impl",
        "prompts_v5.py": "prompts_v7_impl",
        "prompts_v6.py": "prompts_v7_impl",
        "test_final.py": "test_v7",
        "test_layer_impl.py": "test_v7",
        "test_v5.py": "test_v7",
        "test_v6.py": "test_v7"
    }

    # Files to delete (intermediate shims)
    to_delete = [
        "prompts_final_impl.py",
        "prompts_final_impl_impl.py",
        "prompts_final_impl_impl_impl.py",
        "prompts_final_impl_impl_impl_impl.py",
        "prompts_impl_impl.py",
        "prompts_impl_impl_impl.py",
        "prompts_impl_impl_impl_impl.py",
        "prompts_impl_impl_impl_impl_impl.py",
        "prompts_v5_impl.py",
        "prompts_v5_impl_impl.py",
        "prompts_v5_impl_impl_impl.py",
        "prompts_v5_impl_impl_impl_impl.py",
        "prompts_v6_impl.py",
        "prompts_v6_impl_impl.py",
        "prompts_v6_impl_impl_impl.py",
        "prompts_v6_impl_impl_impl_impl.py",
        "test_final_impl.py",
        "test_final_impl_impl.py",
        "test_final_impl_impl_impl.py",
        "test_final_impl_impl_impl_impl.py",
        "test_layer_impl_impl.py",
        "test_layer_impl_impl_impl.py",
        "test_layer_impl_impl_impl_impl.py",
        "test_v5_impl.py",
        "test_v5_impl_impl.py",
        "test_v5_impl_impl_impl.py",
        "test_v5_impl_impl_impl_impl.py",
        "test_v6_impl.py",
        "test_v6_impl_impl.py",
        "test_v6_impl_impl_impl.py",
        "test_v6_impl_impl_impl_impl.py"
    ]

    # Update files
    for filename, import_from in updates.items():
        filepath = pg_dir / filename
        if filepath.exists():
            content = filepath.read_text(encoding='utf-8')
            # Replace the import
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('from .') and 'import *' in line:
                    lines[i] = f"from .{import_from} import *"
                    break
            filepath.write_text('\n'.join(lines), encoding='utf-8')
            logger.info(f# SQL query removed)

    # Delete intermediate shims
    for filename in to_delete:
        filepath = pg_dir / filename
        if filepath.exists():
            filepath.unlink()
            logger.info(f# SQL query removed)

    logger.info(f"\nCleaned prompt_governance: {len(updates)} updated, {len(to_delete)} deleted")

def clean_other_directories():
    """Check and clean other directories for similar patterns."""
    base = Path("c:/Git/Agentic-Workflow")

    # Check each top-level directory
    for item in base.iterdir():
        if item.is_dir() and item.name not in ['.git',
            '__pycache__',
            '.pytest_cache',
            'node_modules',
            '.venv',
            '.vscode']:
            # Look for files with _impl patterns
            impl_files = list(item.rglob("*_impl*.py"))

            if impl_files:
                logger.info(f"\nFound {len(impl_files)} _impl files in {item.name}:")
                for f in impl_files[:10]:  # Show first 10
                    logger.info(f"  - {f.relative_to(base)}")
                if len(impl_files) > 10:
                    logger.info(f"  ... and {len(impl_files) - 10} more")

if __name__ == "__main__":
    logger.info("Cleaning shim chains...")
    logger.info("=" * 60)

    clean_prompt_governance()
    clean_other_directories()

    logger.info("\nDone!")
