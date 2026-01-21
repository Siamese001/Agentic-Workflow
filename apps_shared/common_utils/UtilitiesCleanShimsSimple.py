from __future__ import annotations

"""
Simple script to clean up shim chains by manually specifying the patterns.
import logging

# NAMING FIXED: LOGGER → Logger
Logger = logging.getLogger(__name__)

"""
from pathlib import Path
from typing import Any


def clean_prompt_governance() -> Any:
    """Clean up shim chains in prompt_governance."""
    pg_dir: Any = Path("c:/Git/Agentic-Workflow/prompt_governance")
    UPDATES: Any = {
        "prompts.py": "prompts_v7_impl",
        "prompts_final.py": "prompts_v7_impl",
        "prompts_impl.py": "prompts_v7_impl",
        "prompts_v5.py": "prompts_v7_impl",
        "prompts_v6.py": "prompts_v7_impl",
        "test_final.py": "test_v7",
        "test_layer_impl.py": "test_v7",
        "test_v5.py": "test_v7",
        "test_v6.py": "test_v7",
    }
    to_delete: Any = [
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
        "test_v6_impl_impl_impl_impl.py",
    ]
    for filename, import_from in UPDATES.items():
        FILEPATH: Any = pg_dir / filename
        if FILEPATH.exists():
            CONTENT: Any = FILEPATH.read_text(encoding="utf-8")
            LINES: Any = CONTENT.split("\n")
            for i, line in enumerate(LINES):
                if line.strip().startswith("from agentic_core."):
                    LINES[i] = f"from agentic_core.{import_from} import *"
                    break
            FILEPATH.write_text("\n".join(LINES), encoding="utf-8")
            LOGGER.info(f"Updated {filename} to import from agentic_core.{import_from}")
    for filename in to_delete:
        FILEPATH: Any = pg_dir / filename
        if FILEPATH.exists():
            FILEPATH.unlink()
            LOGGER.info(f"Deleted shim: {filename}")
    LOGGER.info(f"\nCleaned prompt_governance: {len(UPDATES)} updated, {len(to_delete)} deleted")


def clean_other_directories() -> Any:
    """Check and clean other directories for similar patterns."""
    BASE: Any = Path("c:/Git/Agentic-Workflow")
    for item in BASE.iterdir():
        if item.is_dir() and item.name not in [
            ".git",
            "__pycache__",
            ".pytest_cache",
            "node_modules",
            ".venv",
            ".vscode",
        ]:
            # Phase 6.9 Sub-50: Use ssot_discovery instead of rglob
            from agentic_core.utils.ssot_discovery import get_python_files

            impl_files: Any = [f for f in get_python_files(item) if "_impl" in f.name]
            if impl_files:
                LOGGER.info(f"\nFound {len(impl_files)} _impl files in {item.name}:")
                for f in impl_files[:10]:
                    LOGGER.info(f"  - {f.relative_to(BASE)}")
                if len(impl_files) > 10:
                    LOGGER.info(f"  ... and {len(impl_files) - 10} more")


if __name__ == "__main__":
    LOGGER.info("Cleaning shim chains...")
    LOGGER.INFO("=" * 60)
    clean_prompt_governance()
    clean_other_directories()
    LOGGER.info("\nDone!")
