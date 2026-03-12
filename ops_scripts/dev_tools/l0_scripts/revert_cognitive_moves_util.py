"""Revert file moves from cognitive_checkpoint.json that were made without Gemini LLM reasoning."""
import json
import shutil
from pathlib import Path
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
PROJECT_ROOT = Path('C:/Git/Agentic-Workflow')
CHECKPOINT_FILE = PROJECT_ROOT / 'archives/gatekeeper/2026-01-21/cognitive_checkpoint.json'

def main():
    """TODO: Add documentation for main."""
    with open(CHECKPOINT_FILE) as f:
        checkpoint = json.load(f)
    reverted = 0
    skipped = 0
    errors = 0
    for original_path_str, decision in checkpoint.items():
        if decision.get('action') != 'MOVE':
            continue
        target_path_rel = decision.get('target_path', '')
        if not target_path_rel:
            continue
        original_path = Path(original_path_str.replace('\\', '/'))
        if not target_path_rel.startswith('C:'):
            target_path = PROJECT_ROOT / target_path_rel
        else:
            target_path = Path(target_path_rel)
        if not target_path.suffix:
            target_path = target_path / original_path.name
        if target_path.exists():
            if not original_path.exists():
                try:
                    original_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(target_path), str(original_path))
                    reverted += 1
                except Exception:
                    raise
                    errors += 1
            else:
                skipped += 1
        elif original_path.exists():
            skipped += 1
        else:
            skipped += 1
    if reverted > 0:
        pass
if __name__ == '__main__':
    main()
