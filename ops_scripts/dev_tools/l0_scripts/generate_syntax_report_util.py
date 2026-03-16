"""
Generate detailed syntax error report with file paths and error details.
"""
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

_emit_records_execution_trace("p0", "evidence", "generate_syntax_report_util")
_emit_applies_guardrail("p0", "generate_syntax_report_util", "p0_governance")
_emit_reads_policy_state("p0", "generate_syntax_report_util", "policy_binding")
_emit_snapshots_state("p0", "generate_syntax_report_util", "state_snapshot")
emit_replay_key("p0", "generate_syntax_report_util")
emit_determinism_digest("p0", "generate_syntax_report_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# guardian: allow-global-mutation
sys.path.insert(0, str(Path(__file__).parent.parent))
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
from agentic_core.L5_safety.reasoning.CodeValidatorAgent import CodeValidatorAgent


def main():
    project_root = Path(__file__).parent.parent
    print('Generating comprehensive syntax error report...')
    print()
    agent = CodeValidatorAgent(project_root=project_root)
    results = agent.validate_repository()
    errors = results.get('syntax_errors', [])
    print(f'Total syntax errors: {len(errors)}')
    print()
    if len(errors) == 0:
        print('SUCCESS: All files are syntactically valid!')
        return 0
    by_layer = {}
    for e in errors:
        path_str = str(e.file_path)
        if 'L0_' in path_str:
            layer = 'L0'
        elif 'L1_' in path_str:
            layer = 'L1'
        elif 'L2_' in path_str:
            layer = 'L2'
        elif 'L3_' in path_str:
            layer = 'L3'
        elif 'L4_' in path_str:
            layer = 'L4'
        elif 'L5_' in path_str:
            layer = 'L5'
        elif 'config' in path_str:
            layer = 'Config'
        elif 'apps_' in path_str:
            layer = 'Apps'
        else:
            layer = 'Other'
        if layer not in by_layer:
            by_layer[layer] = []
        by_layer[layer].append(e)
    print('Errors by layer:')
    for layer in sorted(by_layer.keys()):
        print(f'  {layer}: {len(by_layer[layer])} errors')
    print()
    print('=' * 80)
    print('DETAILED ERROR REPORT')
    print('=' * 80)
    for layer in sorted(by_layer.keys()):
        print(f'\n### {layer} Layer ({len(by_layer[layer])} errors)')
        print('-' * 80)
        for e in by_layer[layer]:
            rel_path = e.file_path.relative_to(project_root)
            print(f'\nFile: {rel_path}')
            print(f'Line: {e.line_number}, Column: {e.column_number}')
            print(f'Error: {e.error_message}')
    print()
    print('=' * 80)
    return 1
if __name__ == '__main__':
    sys.exit(main())
