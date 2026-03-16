import sys
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "_sample_violations")
_emit_applies_guardrail("p0", "_sample_violations", "p0_governance")
_emit_reads_policy_state("p0", "_sample_violations", "policy_binding")
_emit_snapshots_state("p0", "_sample_violations", "state_snapshot")
emit_replay_key("p0", "_sample_violations")
emit_determinism_digest("p0", "_sample_violations")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# guardian: allow-global-mutation
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agentic_core.L0_routing.config.path_constants import get_validated_project_root

project_root = get_validated_project_root()
baseline = project_root / "ops_scripts/hooks/landmine_baseline.txt"

lines = [l.strip() for l in baseline.read_text(encoding='utf-8').splitlines() if l.strip()]

for cat in ['silent_swallower', 'magic_configuration', 'global_mutation']:
    cat_lines = [l for l in lines if f':{cat}:' in l]
    print(f'\n{cat} ({len(cat_lines)} total):')
    for s in cat_lines[:5]:
        print(f'  {s}')
