"""Canonical entry-point: python -m tools.adg"""

import sys

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from tools.adg.react_chunking_graph_audit import main

_emit_records_execution_trace("p0", "evidence", "__main__")
_emit_applies_guardrail("p0", "__main__", "p0_governance")
_emit_reads_policy_state("p0", "__main__", "policy_binding")
_emit_snapshots_state("p0", "__main__", "state_snapshot")
emit_replay_key("p0", "__main__")
emit_determinism_digest("p0", "__main__")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

sys.exit(main())
