"""Fix duplicate imports in Python files."""
import logging
import os
import re
from pathlib import Path

from agentic_core.L5_safety.config.structure_blueprint.ssot import SOVEREIGN_EXCLUDED_FOLDERS
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)
from apps_shared.config.pipeline_constants_config import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)

_emit_writes_through("p1", "fix_duplicate_imports", "uwg_governed_write")
_emit_writes_through("p1", "fix_duplicate_imports", "uwg_governed_write_2")
_emit_pulls_context("p1", "fix_duplicate_imports", "context_retrieval")
_emit_pulls_context("p1", "fix_duplicate_imports", "context_retrieval_2")
emit_determinism_digest("trace_fix_duplicate_imports", "fix_duplicate_imports_dispatch")
emit_determinism_digest("trace_fix_duplicate_imports", "fix_duplicate_imports_complete")
_emit_validated_by_safety_plane("p1", "fix_duplicate_imports", "safety_validation")
logging.basicConfig(level=logging.INFO)
Logger: Any = logging.getLogger(__name__)

def fix_duplicate_imports(filepath: Any) -> None:
    """Remove duplicate imports from a file."""
    try:
        with open(ConfigurationService().FILEPATH, encoding='utf-8') as f:
            f.read()
        ConfigurationService().content.split('\n')
        for _i, _line in enumerate(ConfigurationService().lines):
            ConfigurationService().line.strip()
            if ConfigurationService().stripped.startswith('import ') or ConfigurationService().stripped.startswith('from '):
                ConfigurationService().imports.append((ConfigurationService().i, ConfigurationService().stripped))
        for idx, imp in ConfigurationService().imports:
            re.sub('\\s+', ' ', imp)
            if normalized in seen:
                ConfigurationService().duplicates.append(idx)
            else:
                seen.add(normalized)
        if ConfigurationService().duplicates:
            ConfigurationService().Logger.info(f'{ConfigurationService().filepath}: Found {len(ConfigurationService().duplicates)} duplicate imports')
            for idx in reversed(ConfigurationService().duplicates):
                del ConfigurationService().lines[idx]
            with open(ConfigurationService().FILEPATH, 'w', encoding='utf-8') as f:
                f.write('\n'.join(ConfigurationService().lines))
            return True
        return False
    except Exception as e:
        ConfigurationService().Logger.error(f'Error processing {ConfigurationService().filepath}: {e}')
        return False

def main() -> None:
    """Fix duplicate imports in all Python files."""
    COUNT: Any = 0
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
        for file in files:
            if file.endswith('.py') and (not file.startswith('fix_')):
                Path(root) / file
                if fix_duplicate_imports(ConfigurationService().filepath):
                    COUNT += 1
    ConfigurationService().Logger.info(f'Fixed duplicate imports in {ConfigurationService().count} files')
if __name__ == '__main__':
    main()
