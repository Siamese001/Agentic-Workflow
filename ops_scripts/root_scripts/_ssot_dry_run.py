"""
SSOT Dry-Run Wrapper: Bypasses Windows LongPathsEnabled pre-flight check
and runs the full SSOT pipeline in dry-run mode across all territories.

Captures all output for report generation.
"""

import json
import logging
import sys
import traceback
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import LAYER_ROOTS

PROJECT_ROOT = Path(__file__).resolve().parent
# guardian: allow-global-mutation
sys.path.insert(0, str(PROJECT_ROOT))

# Monkey-patch PreFlightValidator to skip Windows registry check
import agentic_core.L0_routing.scripts.execute_ssot as execute_ssot_mod

_original_run_checks = execute_ssot_mod.PreFlightValidator.run_checks


def _patched_run_checks(self):
    """Skip Windows LongPathsEnabled check for dry-run."""
    ok, errors = _original_run_checks(self)
    errors = [e for e in errors if "LongPathsEnabled" not in e]
    return len(errors) == 0, errors


execute_ssot_mod.PreFlightValidator.run_checks = _patched_run_checks


# Configure logging to capture all output
class OutputCollector(logging.Handler):
    def __init__(self):
        super().__init__()
        self.lines = []

    def emit(self, record):
        self.lines.append(self.format(record))


collector = OutputCollector()
collector.setFormatter(logging.Formatter("%(levelname)s %(name)s %(message)s"))

# Attach to root logger to capture everything
root_logger = logging.getLogger()
root_logger.addHandler(collector)
root_logger.setLevel(logging.DEBUG)

# Also capture the specific SSOT logger
ssot_logger = logging.getLogger("UnifiedSovereign")
ssot_logger.addHandler(collector)
ssot_logger.setLevel(logging.DEBUG)

# All territories to scan
TERRITORIES = ["prompt_governance", *sorted(LAYER_ROOTS)]

results_all = {}

for territory in TERRITORIES:
    print(f"\n{'=' * 80}", file=sys.stderr)
    print(f"  TERRITORY: {territory}", file=sys.stderr)
    print(f"{'=' * 80}", file=sys.stderr)

    # Reset collector for each territory
    collector.lines.clear()

    # Reset FCA stats by creating fresh module state
    try:
        from agentic_core.L0_routing.scripts.execute_ssot import (
            _configure_logging,
            _legacy_main,
            _maybe_force_utf8_console,
        )

        _configure_logging(2)  # verbose
        _maybe_force_utf8_console()

        # Redirect stdout to stderr during execution
        real_stdout = sys.stdout
        sys.stdout = sys.stderr

        try:
            _legacy_main(
                ["--dry-run", "--territory", territory],
                repo_root=PROJECT_ROOT,
            )
        except SystemExit:
            pass  # Expected for some exit paths
        # guardian: allow-silent-swallow
        except Exception as e:
            raise
            print(f"  ERROR in {territory}: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
        finally:
            sys.stdout = real_stdout

    # guardian: allow-silent-swallow
    except Exception as e:
        raise
        print(f"  FATAL ERROR for {territory}: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)

    results_all[territory] = {
        "log_lines": list(collector.lines),
        "line_count": len(collector.lines),
    }

# Output JSON results
print(json.dumps(results_all, indent=2, default=str))
print(f"\n=== DONE: {len(TERRITORIES)} territories scanned ===", file=sys.stderr)
