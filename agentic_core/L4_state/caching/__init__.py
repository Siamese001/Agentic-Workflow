"""
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace  # noqa: E402
from agentic_core.runtime.lifecycle_trace_contract import _emit_applies_guardrail  # noqa: E402
from agentic_core.runtime.lifecycle_trace_contract import _emit_signs_execution_trace  # noqa: E402
from agentic_core.runtime.lifecycle_trace_contract import _emit_snapshots_state  # noqa: E402
_emit_snapshots_state("p0", "__init__", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "__init__", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "__init__")
L4 State Caching Module

TOMBSTONED: SovereignRedisMCPClient and get_redis_client have been removed.
Use agentic_core.cache.get_hot_cache() or agentic_core.cache.get_coordination_cache()
for all Redis caching needs.
"""

__all__: list[str] = []
