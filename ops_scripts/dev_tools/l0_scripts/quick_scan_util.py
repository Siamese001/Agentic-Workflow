"""Quick test scanner with built-in progress indicator."""
import re
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "quick_scan_util")
_emit_applies_guardrail("p0", "quick_scan_util", "p0_governance")
_emit_reads_policy_state("p0", "quick_scan_util", "policy_binding")
_emit_snapshots_state("p0", "quick_scan_util", "state_snapshot")
emit_replay_key("p0", "quick_scan_util")
emit_determinism_digest("p0", "quick_scan_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
G = '\x1b[92m'
Y = '\x1b[93m'
R = '\x1b[91m'
B = '\x1b[94m'
C = '\x1b[96m'
X = '\x1b[0m'

def progress_bar(current, total, width=40):
    """Simple progress bar."""
    percent = current / total if total > 0 else 0
    filled = int(width * percent)
    bar = '█' * filled + '░' * (width - filled)
    color = G if percent > 0.7 else Y if percent > 0.3 else R
    sys.stdout.write(f'\r{color}[{bar}]{X} {current}/{total} ({percent * 100:.1f}%)')
    sys.stdout.flush()
from agentic_core.utils.ssot_discovery_validator import get_python_files

test_files = list(get_python_files(Path(TESTS_UNIT_DIR)))
skip_pattern = re.compile('@pytest\\.mark\\.skip')
total_files_with_skips = 0
total_skips = 0
print(f'{C}Scanning {len(test_files)} test files...{X}\n')
for i, py_file in enumerate(test_files, 1):
    progress_bar(i, len(test_files))
    try:
        content = py_file.read_text(encoding='utf-8')
        skip_count = len(skip_pattern.findall(content))
        if skip_count > 0:
            total_files_with_skips += 1
            total_skips += skip_count
    # guardian: allow-silent-swallow
    except:
        pass
print(f"\n\n{B}{'=' * 60}{X}")
print(f'{B}Results:{X}')
print(f"{B}{'=' * 60}{X}")
print(f'  Files with skips: {C}{total_files_with_skips}{X}')
color = G if total_skips < 200 else Y if total_skips < 400 else R
print(f'  Total skip marks: {color}{total_skips}{X}')
if total_skips < 200:
    print(f'  Status: {G}✓ EXCELLENT (<200){X}')
elif total_skips < 400:
    print(f'  Status: {Y}⚠ NEEDS WORK (200-400){X}')
else:
    print(f'  Status: {R}✗ CRITICAL (>400){X}')
print(f"{B}{'=' * 60}{X}")
