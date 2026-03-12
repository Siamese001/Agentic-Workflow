from __future__ import annotations
'\nOne-time cleanup utility to collapse duplicate entries in registry.json.\n\nUsage:\n    python -m agentic_core.prompt_governance.version_registry.cleanup_duplicates\n\nThis script:\n- Loads the current registry via get_prompt_registry() for consistency\n- Deduplicates entries based on key fields (version, purpose, author, content_hash, territory)\n- Keeps only the most recent entry for each unique combination\n- Ensures only one active version per template\n- Saves the cleaned registry atomically\n'
import logging
from typing import Any
from agentic_core.prompt_governance.version_registry.prompt_registry_config import get_prompt_registry
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
Logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def collapse_duplicates():
    """
    Collapse duplicate entries in registry.json.

    Deduplication strategy:
    1. Group entries by (version, purpose, author, content_hash, territory)
    2. Keep only the newest entry per group (by registered_date or list order)
    3. Ensure single active version per template
    4. Use same DUPLICATE_KEY_FIELDS logic as register_prompt()
    """
    registry = get_prompt_registry()
    print(f'[CLEANUP] Loading registry from {registry.REGISTRY_FILE}')
    Logger.info(f'Starting duplicate cleanup for {registry.REGISTRY_FILE}')
    original_count = sum((len(entries) for entries in registry.registry.values()))
    print(f'[CLEANUP] Original entries: {original_count}')
    Logger.info(f'Original entry count: {original_count}')
    total_removed = 0
    for template_name, entries in list(registry.registry.items()):
        seen_keys: set[tuple] = set()
        unique_entries: list[dict[str, Any]] = []
        for entry in reversed(entries):
            key = tuple((entry.get(field) for field in ['version', 'purpose', 'author', 'content_hash', 'territory']))
            if key not in seen_keys:
                seen_keys.add(key)
                unique_entries.append(entry)
        unique_entries.reverse()
        removed = len(entries) - len(unique_entries)
        total_removed += removed
        if removed > 0:
            print(f'   [{template_name}] Removed {removed} duplicate(s)')
            Logger.info(f"Template '{template_name}': removed {removed} duplicates")
        active_seen = False
        for entry in unique_entries:
            if entry.get('active'):
                if active_seen:
                    entry['active'] = False
                    total_removed += 1
                    Logger.debug(f'Deactivated duplicate active entry in {template_name}')
                else:
                    active_seen = True
        registry.registry[template_name] = unique_entries
    registry._save_registry()
    final_count = sum((len(entries) for entries in registry.registry.values()))
    print('[CLEANUP] Complete!')
    print(f'   Original entries: {original_count}')
    print(f'   Final entries: {final_count}')
    print(f'   Removed: {total_removed} duplicate(s)')
    if original_count > 0:
        print(f'   Reduction: {100 * total_removed / original_count:.1f}%')
    Logger.info(f'Cleanup complete: {original_count} → {final_count} entries ({total_removed} removed)')
if __name__ == '__main__':
    collapse_duplicates()
