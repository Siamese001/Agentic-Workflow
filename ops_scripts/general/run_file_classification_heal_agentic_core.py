"""
Run FileClassificationAgent on agentic_core with healing enabled.
Generates detailed JSON report of all healing activities.
"""
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
    get_validated_project_root,
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

_emit_records_execution_trace("p0", "evidence", "run_file_classification_heal_agentic_core")
_emit_applies_guardrail("p0", "run_file_classification_heal_agentic_core", "p0_governance")
_emit_reads_policy_state("p0", "run_file_classification_heal_agentic_core", "policy_binding")
_emit_snapshots_state("p0", "run_file_classification_heal_agentic_core", "state_snapshot")
emit_replay_key("p0", "run_file_classification_heal_agentic_core")
emit_determinism_digest("p0", "run_file_classification_heal_agentic_core")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
project_root = get_validated_project_root()
# guardian: allow-global-mutation
sys.path.insert(0, str(project_root))
from agentic_core.L5_safety.config.structure_blueprint.ssot import REPORTS_DIR
from agentic_core.L5_safety.reasoning.FileClassificationAgent import FileClassificationAgent


def run_healing_with_detailed_report():
    """Run FileClassificationAgent healing and generate detailed JSON report."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s', datefmt='%H:%M:%S')
    logger = logging.getLogger(__name__)
    agent = FileClassificationAgent(project_root=project_root, dry_run=False, validate_only=False)
    logger.info('=' * 70)
    logger.info('FILECLASSIFICATIONAGENT - HEALING RUN ON AGENTIC_CORE')
    logger.info('=' * 70)
    logger.info(f'Project Root: {project_root}')
    logger.info('Target: agentic_core')
    logger.info('Mode: HEALING ENABLED (dry_run=False)')
    logger.info('=' * 70)
    start_time = datetime.now()
    result = agent.heal_repository(dry_run=False, execute=True, target_territory=AGENTIC_CORE_DIR, auto_approve=True)
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    detailed_report = {'metadata': {'run_timestamp': start_time.isoformat(), 'duration_seconds': duration, 'target_folder': 'agentic_core', 'healing_mode': 'EXECUTE', 'dry_run': False, 'agent_version': 'v5.1-idempotence-hardened'}, 'summary': {'violations_found': result.get('violations_found', 0), 'violations_fixed': result.get('violations_fixed', 0), 'errors': result.get('errors', 0), 'skipped': result.get('skipped', 0)}, 'action_counters': result.get('action_counters', {'renames': 0, 'territory_moves': 0, 'import_fixes': 0, 'deep_refactors': 0, 'config_updates': 0}), 'idempotence_cache': {'paths_processed': len(agent.processed_paths), 'cache_was_cleared': True}, 'stats': agent.stats, 'file_classifications': {}, 'healing_actions': []}
    for path in agent.file_registry:
        try:
            rel_path = str(path.relative_to(project_root))
            file_type = agent.classify_file(path)
            detailed_report['file_classifications'][rel_path] = file_type
        except Exception:
            raise
            pass
    detailed_report['idempotence_verification'] = {'description': 'Second run should show zero actions if idempotent', 'recommendation': 'Re-run this script to verify zero violations_fixed'}
    output_path = project_root / 'docs' / REPORTS_DIR / 'file_classification_healing_agentic_core.json'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(detailed_report, f, indent=2, default=str)
    logger.info('=' * 70)
    logger.info('HEALING RUN COMPLETE')
    logger.info('=' * 70)
    logger.info(f'Duration: {duration:.2f}s')
    logger.info(f"Violations Found: {result.get('violations_found', 0)}")
    logger.info(f"Violations Fixed: {result.get('violations_fixed', 0)}")
    logger.info(f"Errors: {result.get('errors', 0)}")
    logger.info(f"Skipped: {result.get('skipped', 0)}")
    logger.info('-' * 70)
    logger.info('Action Counters:')
    for action, count in result.get('action_counters', {}).items():
        logger.info(f'  {action}: {count}')
    logger.info('-' * 70)
    logger.info(f'Detailed JSON report saved to: {output_path}')
    logger.info('=' * 70)
    print('\n' + '=' * 70)
    print('DETAILED HEALING REPORT (JSON)')
    print('=' * 70)
    print(json.dumps(detailed_report, indent=2, default=str))
    return detailed_report
if __name__ == '__main__':
    run_healing_with_detailed_report()
