"""Delete all extracted agent files from surgical extraction."""
import json
from pathlib import Path
from agentic_core.utils.file_utils import safe_read_file, safe_write_file

log_path = Path('surgical_extraction_log.json')
with open(log_path) as f:
    log = json.load(f)

files = [e['new_file'] for e in log['extractions'].values()]
deleted = 0
errors = 0

print(f"Deleting {len(files)} extracted files...")
for f in files:
    p = Path(f)
    try:
        if p.exists():
            p.unlink()
            deleted += 1
            print(f"  ✓ Deleted: {f}")
        else:
            print(f"  - Already gone: {f}")
    except Exception as e:
        errors += 1
        print(f"  ✗ Error deleting {f}: {e}")

print()
print(f"Summary: Deleted {deleted}/{len(files)} files ({errors} errors)")
