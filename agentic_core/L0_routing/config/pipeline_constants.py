"""Generic pipeline constants — canonical SSOT at L0.

Single source of truth for module-level pipeline constants that have no
business semantics tying them to any particular app. Lives at L0 so every
higher layer (L1..L6, apps_*, system_learning, tools) can import from it
without violating layer gravity.

Plan: ``adg-p0-wave1-protected-plane-fixes`` — closes Group A of the W1
Wave plan in ``artifacts/adg/issues/p0_remediation_wave_plan_*.md``. Five
``agentic_core/*`` modules previously imported these constants from
``apps_shared.config.pipeline_constants_config``, which is at L_APP and
therefore higher than the importers' layers — a P0 layer violation.

The old location at ``apps_shared/config/pipeline_constants_config.py``
is now a re-export shim that imports from this module, preserving the
~30 ``apps_*`` callsites without a flag-day rename.

Constants
---------
``MAX_RETRIES`` (int)
    Default retry count for any unbounded retry loop. 3 is the empirical
    sweet spot — enough to ride out a transient network blip, not enough
    to mask a real outage.

``DEFAULT_SLEEP`` (float)
    Default backoff (seconds) between retries.

``THRESHOLD`` (float)
    Default similarity / confidence threshold (0..1). Used as a generic
    ceiling for routing/match acceptance.

``BUFFER_SIZE`` (int)
    Default chunk size (bytes) for streaming I/O. 8 KiB matches OS
    default page size and stdio block size.

``BATCH_SIZE`` (int)
    Default batch size for bulk operations.

``MAX_DEPTH`` (int)
    Default recursion / traversal depth.

``MAX_FILES`` (int)
    Default per-pass file count for batch scanners.

``DEFAULT_TIMEOUT`` (int)
    Default subprocess / network timeout (seconds). Five minutes is the
    floor for any agent-driven I/O — anything tighter risks aborting
    legitimate long-running planner calls.
"""

MAX_RETRIES: int = 3
DEFAULT_SLEEP: float = 1.0
THRESHOLD: float = 0.95
BUFFER_SIZE: int = 8192
BATCH_SIZE: int = 32
MAX_DEPTH: int = 6
MAX_FILES: int = 1000
DEFAULT_TIMEOUT: int = 300  # 5 minutes

__all__ = [
    "MAX_RETRIES",
    "DEFAULT_SLEEP",
    "THRESHOLD",
    "BUFFER_SIZE",
    "BATCH_SIZE",
    "MAX_DEPTH",
    "MAX_FILES",
    "DEFAULT_TIMEOUT",
]
