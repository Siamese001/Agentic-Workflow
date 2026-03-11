"""Strict Import Mode Activation Criteria — Definition Only.

Defines the thresholds at which IMPORT_STRICT_MODE can be fully activated
(i.e., ``continue-on-error`` removed from CI canary and strict mode becomes
a blocking gate).

These constants are consumed by the guardian report summary fields:
  - ``total_unresolved``  -> ``max_total_unresolved``
  - ``healing_count``     -> ``max_healing_unresolved``
  - ``runtime_count``     -> ``max_runtime_unresolved``

No enforcement logic lives here. This is a definition-only module.
Enforcement will be added when the debt is reduced to meet these thresholds.
"""

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

STRICT_MODE_ACTIVATION_CRITERIA: dict[str, int] = {
    "max_total_unresolved": 50,
    "max_healing_unresolved": 0,
    "max_runtime_unresolved": 0,
}
