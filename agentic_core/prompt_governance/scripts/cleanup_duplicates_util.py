from __future__ import annotations

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""
One-time cleanup utility to collapse duplicate entries in registry.json.

Usage:
    python -m agentic_core.prompt_governance.version_registry.cleanup_duplicates

This script:
- Loads the current registry via get_prompt_registry() for consistency
- Deduplicates entries based on key fields (version, purpose, author, content_hash, territory)
- Keeps only the most recent entry for each unique combination
- Ensures only one active version per template
- Saves the cleaned registry atomically
"""

import logging
from typing import Any

from agentic_core.prompt_governance.version_registry.prompt_registry_config import (
    get_prompt_registry,
)

Logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


def collapse_duplicates():
    """
    Collapse duplicate entries in registry.json.

    Deduplication strategy:
    1. Group entries by (version, purpose, author, content_hash, territory)
    2. Keep only the newest entry per group (by registered_date or list order)
    3. Ensure single active version per template
    4. Use same DUPLICATE_KEY_FIELDS logic as register_prompt()
    """
    # Load registry via get_prompt_registry() for consistency
    registry = get_prompt_registry()

    print(f"[CLEANUP] Loading registry from {registry.REGISTRY_FILE}")
    Logger.info(f"Starting duplicate cleanup for {registry.REGISTRY_FILE}")

    original_count = sum(len(entries) for entries in registry.registry.values())

    print(f"[CLEANUP] Original entries: {original_count}")
    Logger.info(f"Original entry count: {original_count}")

    # Define key fields for deduplication (matches register_prompt() logic)

    # Clean each template's entries
    total_removed = 0

    for template_name, entries in list(registry.registry.items()):
        # Deduplicate by key fields - keep newest (last in reversed list)
        seen_keys: set[tuple] = set()
        unique_entries: list[dict[str, Any]] = []

        # Process in reverse to preserve latest entries first
        for entry in reversed(entries):
            # Create key from DUPLICATE_KEY_FIELDS
            key = tuple(
                entry.get(field) for field in ["version", "purpose", "author", "content_hash", "territory"]
            )

            if key not in seen_keys:
                seen_keys.add(key)
                unique_entries.append(entry)

        # Reverse back to original order
        unique_entries.reverse()

        removed = len(entries) - len(unique_entries)
        total_removed += removed

        if removed > 0:
            print(f"   [{template_name}] Removed {removed} duplicate(s)")
            Logger.info(f"Template '{template_name}': removed {removed} duplicates")

        # Ensure only one active version (keep first active, deactivate rest)
        active_seen = False
        for entry in unique_entries:
            if entry.get("active"):
                if active_seen:
                    entry["active"] = False
                    total_removed += 1
                    Logger.debug(f"Deactivated duplicate active entry in {template_name}")
                else:
                    active_seen = True

        registry.registry[template_name] = unique_entries

    # Save using registry's atomic save method
    registry._save_registry()

    final_count = sum(len(entries) for entries in registry.registry.values())

    print("[CLEANUP] Complete!")
    print(f"   Original entries: {original_count}")
    print(f"   Final entries: {final_count}")
    print(f"   Removed: {total_removed} duplicate(s)")
    if original_count > 0:
        print(f"   Reduction: {100 * total_removed / original_count:.1f}%")

    Logger.info(f"Cleanup complete: {original_count} → {final_count} entries ({total_removed} removed)")


if __name__ == "__main__":
    collapse_duplicates()
