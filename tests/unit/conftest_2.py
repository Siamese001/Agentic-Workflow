import sys
from pathlib import Path

# Define a global ROOT path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

# Inject KeySource for L2 tests
try:
    from agentic_core.L2_execution.enforcement.key_source import TestKeySource, inject_key_source

    inject_key_source(TestKeySource())
except ImportError:
    pass  # Allow tests to run that don't have this dependency
