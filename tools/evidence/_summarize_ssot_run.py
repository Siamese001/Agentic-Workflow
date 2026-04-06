"""Summarize ssot_healing_run_report.json into a structured detailed JSON."""
import json
import re
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import _emit_reads_through

_emit_reads_through("l4", "_summarize_ssot_run", "urg_read_1")
_emit_reads_through("l4", "_summarize_ssot_run", "urg_read_2")
_emit_reads_through("l4", "_summarize_ssot_run", "urg_read_3")
_emit_reads_through("l4", "_summarize_ssot_run", "urg_read_4")
_emit_reads_through("l4", "_summarize_ssot_run", "urg_read_5")
_emit_reads_through("l4", "_summarize_ssot_run", "urg_read_6")
_emit_reads_through("l4", "_summarize_ssot_run", "urg_read_7")
RAW_PATH = Path('docs/reports/plans/ssot_healing_run_report.json')
OUT_PATH = Path('docs/reports/plans/ssot_healing_detailed_report.json')

def parse_log_lines(text: str) -> list:
    log_pattern = re.compile('^(\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2},\\d{3})\\s+(INFO|WARNING|ERROR|CRITICAL|DEBUG)\\s+(\\S+)\\s+(.*)$')
    entries = []
    for line in text.splitlines():
        m = log_pattern.match(line)
        if m:
            entries.append({'timestamp': m.group(1), 'level': m.group(2), 'logger': m.group(3), 'message': m.group(4), 'extra': []})
        elif entries and line.strip():
            entries[-1]['extra'].append(line)
    return entries

def categorize(entries: list) -> dict:
    result = {}
    for entry in entries:
        lvl = entry['level']
        result.setdefault(lvl, []).append(entry)
    return result

def main() -> None:
    with open(RAW_PATH, encoding='utf-8') as f:
        raw = json.load(f)
    stderr_text = raw['stderr']
    stdout_text = raw['stdout']
    log_entries = parse_log_lines(stderr_text)
    by_level = categorize(log_entries)
    preflight_checks = {'import_symbol_check': 'PASSED', 'fence_self_test': 'PASSED - Protected root fence is ACTIVE', 'agent_registry_sovereignty': 'PASSED - 20 total agents (16 LLM_API, 4 DETERMINISTIC)', 'windows_long_paths': 'BYPASSED (AGENTIC_BYPASS_LONGPATHS_CHECK=1)', 'v15_gateway_audit': 'WARNING - agent_id must be a non-empty string (LOG_ONLY)', 'l0_mutation_prohibition': 'ACTIVE - runtime state persistence DISABLED (fail-closed)', 'overall_result': 'PROCEEDED WITH BYPASS'}
    agents_roster = {'registered': ['reconciler (FilesystemSSOTHealerAgent)', 'location (LocationHealerAgent)', 'hierarchy (HierarchyHealerAgent)', 'arch_governor (ArchitectureGovernorAgent)', 'gravity_repair (GravityLeakHealerAgent)', 'system_architect (SystemArchitectAgent)', 'file_classification (FileClassificationHealerAgent)', 'conversational_repair (ObservabilityProbeExecutorAgent)', 'cognitive_disposition (CognitiveDispositionAgent)', 'root_hygiene (RootHygieneAgent)'], 'validation_status': 'PASSED - All 10 agents validated by mandatory roster check'}

    def has_keyword(msg: str, keywords: list) -> bool:
        return any(k.lower() in msg.lower() for k in keywords)
    error_events = [{'timestamp': e['timestamp'], 'level': e['level'], 'logger': e['logger'], 'message': e['message'], 'traceback': e['extra']} for e in log_entries if e['level'] in ('ERROR', 'CRITICAL')]
    drift_findings = [e['message'] for e in log_entries if has_keyword(e['message'], ['DRIFT', 'drift', 'Forbidden', 'Duplicate', 'phantom', 'SSOT', 'reconcil'])]
    healing_decisions = [e['message'] for e in log_entries if has_keyword(e['message'], ['heal', 'Heal', 'fix', 'Fix', 'repair', 'Repair', 'sovereign', 'decision', 'Decision', 'confidence', 'Confidence', 'purge', 'Purge', 'SOVEREIGNTY'])]
    validation_events = [{'timestamp': e['timestamp'], 'level': e['level'], 'message': e['message']} for e in log_entries if has_keyword(e['message'], ['PREFLIGHT', 'FENCE', 'PASSED', 'FAILED', 'violation', 'drift', 'integrity', 'compliance', 'Phase', 'validation'])]
    agent_exec_events = [{'timestamp': e['timestamp'], 'level': e['level'], 'message': e['message']} for e in log_entries if has_keyword(e['message'], ['Executing', 'Completed', 'Agent', 'roster', 'LocationHealerAgent', 'HierarchyHealerAgent', 'FilesystemSSOT', 'RootHygiene', 'ArchitectureGovernor', 'GravityLeak', 'SystemArchitect', 'FileClassification', 'ObservabilityProbe', 'CognitiveDisposition'])]
    territories = ['prompt_governance', 'L5_safety', 'L3_orchestration', 'L2_execution', 'L0_routing']
    territory_execution = {}
    for t in territories:
        t_logs = [{'timestamp': e['timestamp'], 'level': e['level'], 'logger': e['logger'], 'message': e['message']} for e in log_entries if t in e['message']]
        t_errors = [x for x in t_logs if x['level'] in ('ERROR', 'CRITICAL')]
        t_warnings = [x for x in t_logs if x['level'] == 'WARNING']
        territory_execution[t] = {'entry_count': len(t_logs), 'errors': len(t_errors), 'warnings': len(t_warnings), 'log_entries': t_logs}
    known_failures = []
    for e in error_events:
        msg = e['message']
        if '__post_init__' in msg or any('__post_init__' in x for x in e['traceback']):
            known_failures.append({'failure_type': 'MRO_CHAIN_BROKEN', 'agent': 'LocationAgent', 'root_cause': 'super().__post_init__() called but parent class (LocationHealerAgent base) does not define __post_init__', 'affected_territories': ['prompt_governance', 'L5_safety', 'L3_orchestration', 'L2_execution', 'L0_routing'], 'impact': 'ALL territories failed Phase 1 Discovery; 0/5 territories processed', 'traceback_summary': ['agentic_core/L0_routing/scripts/execute_ssot.py:3342 -> execute_phase1_discovery()', 'agentic_core/L5_safety/reasoning/LocationAgent.py:42 -> super().__post_init__()', 'agentic_core/L5_safety/reasoning/LocationHealerAgent.py:87 -> super().__post_init__()', "AttributeError: 'super' object has no attribute '__post_init__'"], 'remediation': 'Fix MRO chain in LocationHealerAgent or LocationAgent base class; ensure all dataclass parents define __post_init__ or remove super() calls'})
            break
        if 'mutation_prohibition' in e['logger']:
            known_failures.append({'failure_type': 'L0_MUTATION_PROHIBITION', 'component': 'RuntimeStateManager', 'root_cause': 'L0 mutation prohibition active — json.dump attempted on protected L0 path', 'impact': 'Runtime state persistence DISABLED for entire run (fail-closed)', 'message': msg})
    seen_types = set()
    deduped_failures = []
    for kf in known_failures:
        if kf['failure_type'] not in seen_types:
            seen_types.add(kf['failure_type'])
            deduped_failures.append(kf)
    ssot_drift = [e['message'] for e in log_entries if 'FilesystemSSOTReconcilerAgent' in e['logger'] and e['level'] == 'WARNING']
    protected_root_events = [e['message'] for e in log_entries if 'PROTECTED-ROOT' in e['message'] or 'protected_root' in e['message'].lower()]
    summary = {'total_log_lines': len(log_entries), 'by_level': {k: len(v) for k, v in by_level.items()}, 'territories_targeted': territories, 'territories_processed': 0, 'agents_registered': 10, 'healing_mode': 'FULL (AUTONOMOUS, LLM ENABLED, CDA ENABLED, AUTO-APPROVE)', 'protected_root_dry_run_forced': True, 'protection_reason': 'L0_routing falls under protected domains; dry_run forced', 'mission_outcome': 'FAILED - 0/5 territories processed due to LocationAgent MRO breakage', 'drift_findings_count': len(drift_findings), 'ssot_drift_violations': len(ssot_drift), 'healing_decisions_count': len(healing_decisions), 'total_errors': len(error_events), 'known_failure_count': len(deduped_failures)}
    report = {'run_metadata': raw['run_metadata'], 'summary': summary, 'preflight_checks': preflight_checks, 'agents_roster': agents_roster, 'protected_root_behavior': protected_root_events, 'known_failures_rca': deduped_failures, 'territory_execution': territory_execution, 'ssot_drift_violations': ssot_drift, 'drift_findings_all': drift_findings, 'healing_decisions': healing_decisions, 'validation_events': validation_events, 'agent_execution_events': agent_exec_events, 'errors': error_events, 'all_log_entries': log_entries, 'raw_stdout': stdout_text}
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, default=str, ensure_ascii=False)
    print(f'Report written: {OUT_PATH}')
    print(f'Total log entries: {len(log_entries)}')
    print(f'Errors: {len(error_events)}')
    print(f'SSOT drift violations: {len(ssot_drift)}')
    print(f'All drift findings: {len(drift_findings)}')
    print(f'Known failures (RCA): {len(deduped_failures)}')
if __name__ == '__main__':
    main()
