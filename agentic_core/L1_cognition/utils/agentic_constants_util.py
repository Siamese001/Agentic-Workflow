from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "agentic_constants_util")
emit_determinism_digest("p0", "agentic_constants_util")

_emit_dispatches_healing_run("p1", "agentic_constants_util", "L1")
_emit_routes_through("p1", "agentic_constants_util", "L1")
_emit_escalates_to_human("p1", "agentic_constants_util", "L1")
_emit_reads_policy_state("p1", "agentic_constants_util", "L1")

_emit_snapshots_state("p0", "agentic_constants_util", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "agentic_constants_util", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "agentic_constants_util")

"\nConstants for the Agentic Core system.\n[SSOT] Structural constants derived from structure_blueprint.py\n\nContains all shared constants used across the agentic framework.\n"
from typing import Any

from agentic_core.L0_routing.config import ROOT_PROTECTED_FILES

max_complexity: Any = 10
max_func_lines: Any = 50
max_nesting_spaces: Any = 40
allowed_root_files: Any = ROOT_PROTECTED_FILES
few_shot_strategic: Any = '\nYou are the StrategicPlannerAgent, an expert in mission planning and coordination.\n\nYour role is to:\n1. Generate comprehensive mission plans\n2. Coordinate agent execution order\n3. Allocate resources efficiently\n4. Anticipate potential issues\n\nMission Plan Structure:\n{\n    "mission_id": "unique_identifier",\n    "cycle_id": 1,\n    "priority": "HIGH|MEDIUM|LOW",\n    "objective": "Clear mission objective",\n    "phases": [...],\n    "risk_assessment": {...}\n}\n'
few_shot_sherlock: Any = "\nYou are Sherlock, the debugging specialist.\n\nYour role is to:\n1. Analyze code issues systematically\n2. Identify root causes\n3. Propose targeted fixes\n4. Verify fix effectiveness\n\nDebugging Process:\n1. Gather evidence (logs, stack traces)\n2. Formulate hypotheses\n3. Test hypotheses\n4. Implement solution\n"
few_shot_concurrency: Any = "\nYou are the ConcurrencyGuardianAgent, an expert in managing concurrent operations.\n\nYour role is to:\n1. Prevent race conditions\n2. Manage resource locks\n3. Detect deadlocks\n4. Ensure thread safety\n\nLock Usage Pattern:\n1. Acquire lock with timeout\n2. Execute critical section\n3. Always release in finally block\n4. Use async/await for I/O operations\n"
max_phase_time: Any = 300
memory_threshold_mb: Any = 100
performance_degradation_threshold: Any = 0.5
default_lock_timeout: Any = 30
max_retry_attempts: Any = 3
retry_delay: Any = 0.5
max_snapshots: Any = 100
benchmark_history_size: Any = 1000
max_alerts_per_type: Any = 50
canon_remote_repo: Any = "CANON_REMOTE_REPO"
google_api_key: Any = "GOOGLE_API_KEY"
enable_fuzz: Any = "ENABLE_FUZZ"
additional_repo_roots: Any = "ADDITIONAL_REPO_ROOTS"
memory_dir: Any = "observability/memory"
alerts_dir: Any = "observability/alerts"
cache_dir: Any = "observability/cache"
