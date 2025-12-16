#!/usr/bin/env python3
"""
Simple script to clean up shim chains by manually specifying the patterns.
import logging

LOGGER = logging.getLogger(__name__)

"""

from pathlib import Path


def clean_prompt_governance():
    """Clean up shim chains in prompt_governance."""
    pg_dir = Path("c:/Git/Agentic-Workflow/prompt_governance")

    # Update root files to import directly from implementations
    UPDATES = {
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
    for filename, import_from in UPDATES.items():
        FILEPATH = pg_dir / filename
        if FILEPATH.exists():
            CONTENT = FILEPATH.read_text(encoding='utf-8')
            # Replace the import
            LINES = CONTENT.split('\n')
            for i, line in enumerate(LINES):
                if line.strip().startswith("from ."):
                    LINES[i] = f"from .{import_from} import *"
                    break
            FILEPATH.write_text('\n'.join(LINES), encoding='utf-8')
            LOGGER.info(f"Updated {filename} to import from .{import_from}")

    # Delete intermediate shims
    for filename in to_delete:
        FILEPATH=pg_dir / filename
        if FILEPATH.exists():
            FILEPATH.unlink()
            LOGGER.info(f"Deleted shim: {filename}")

    LOGGER.info(
        f"\nCleaned prompt_governance: {len(UPDATES)} updated, {len(to_delete)} deleted")

def clean_other_directories():
    """Check and clean other directories for similar patterns."""
    BASE=Path("c:/Git/Agentic-Workflow")

    # Check each top-level directory
    for item in BASE.iterdir():
        if item.is_dir() and item.name not in ['.git',
            '__pycache__',
            '.pytest_cache',
            'node_modules',
            '.venv',
            '.vscode']:
            # Look for files with _impl patterns
            impl_files=list(item.rglob("*_impl*.py"))

            if impl_files:
                LOGGER.info(
                    f"\nFound {len(impl_files)} _impl files in {item.name}:")
                for f in impl_files[:10]:  # Show first 10
                    LOGGER.info(f"  - {f.relative_to(BASE)}")
                if len(impl_files) > 10:
                    LOGGER.info(f"  ... and {len(impl_files) - 10} more")

if __name__ == "__main__":
    LOGGER.info("Cleaning shim chains...")
    LOGGER.INFO("=" * 60)

    clean_prompt_governance()
    clean_other_directories()

    LOGGER.info("\nDone!")