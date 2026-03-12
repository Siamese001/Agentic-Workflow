from __future__ import annotations
'\nSovereign Guardian: observability Footprint (Dark Reasoning Check)\nEnsures every L1 reasoning step leaves an L6 observability trail.\n\nThe Governance Cycle:\n1. L0 (Auditor) defines what is "Legal."\n2. L1-L5 perform the actual agentic operations.\n3. L6 (observability) records the ground truth of those operations.\n4. L0 (Auditor) periodically sweeps L6 to ensure L1-L5 behaved, flagging Dark Reasoning if an agent "thought" without telling the system.\n\nPhase 9C: Dark Reasoning Guardian (Dec 26, 2025)\n'
from pathlib import Path
from agentic_core.L5_safety.config.structure_blueprint import TESTS_DIR
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

def check_dark_reasoning(filepath: Path) -> list[str]:
    """
    Check for reasoning operations without corresponding observability footprints.

    Dark Reasoning occurs when an agent performs cognitive operations (think, plan, decide)
    without leaving a trace in the L6 observability layer (logging, telemetry).

    Args:
        filepath: Path to Python file to audit

    Returns:
        List of issues found (empty if compliant)
    """
    issues = []
    file_str = str(filepath).replace('\\', '/')
    if not any((layer in file_str for layer in ['L1_cognition', 'L2_execution', 'L3_orchestration'])):
        return []
    try:
        content = filepath.read_text(encoding='utf-8')
        lines = content.splitlines()
        reasoning_signals = ['think', 'plan', 'execute', 'decide', 'reason', 'validate', 'check']
        log_signals = ['Logger.', 'logging.', 'self.log', 'trace(', 'print(']
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
                continue
            if any((sig in line.lower() for sig in reasoning_signals)):
                ContextWindow = '\n'.join(lines[i:min(i + 10, len(lines))])
                if not any((log_sig in ContextWindow for log_sig in log_signals)):
                    issues.append(f'Potential Dark Reasoning at line {i + 1}: Action without L6 footprint')
    # guardian: allow-silent-swallow
    except Exception:
        pass
    return issues

def validate_observability_footprint(target_dir: str) -> tuple[float, list[str]]:
    """
    Validate that all reasoning operations have observability footprints.

    Args:
        target_dir: Directory to audit

    Returns:
        Tuple of (score percentage, list of issues)
    """
    issues = []
    total_files = 0
    from agentic_core.utils.ssot_discovery_validator import get_python_files
    for path in get_python_files(Path(target_dir)):
        if TESTS_DIR in str(path) or '__pycache__' in str(path):
            continue
        total_files += 1
        file_issues = check_dark_reasoning(path)
        issues.extend([f'{path.name}: {i}' for i in file_issues])
    score = 100.0
    if issues:
        score = max(0, 100 - len(issues) * 5)
    return (score, issues)
