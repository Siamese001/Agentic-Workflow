"""
L6 Observability: Healing Audit Logger
Records all L0 healing actions for compliance and debugging.

Phase 10B: Transactional Healing with L6 Audit Trail (Dec 26, 2025)
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
healing_log: Any = Path('agentic_core/L6_observability/logs/healing_audit.jsonl')

def log_healing_action(action: str, fix: Dict, success: bool, error: Optional[str]=None) -> None:
    """
    Log a healing action to the L6 audit trail.
    
    Args:
        action: Type of healing action (e.g., 'inject_logging', 'refactor_import')
        fix: Dictionary containing fix details (file, reason, priority, etc.)
        success: Whether the fix was applied successfully
        error: Optional error message if fix failed
    """
    entry: Any = {'timestamp': datetime.utcnow().isoformat(), 'action': action, 'fix_details': fix, 'success': success, 'error': error, 'strategy': fix.get('strategy', 'unknown'), 'priority': fix.get('priority', 10), 'file': fix.get('file', 'N/A'), 'reason': fix.get('reason', 'N/A')}
    HEALING_LOG.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(HEALING_LOG, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')
            f.flush()
    except Exception as e:
        print(f'!!! [L6 FATAL] Could not write to healing log: {e}')

def get_healing_history(limit: int=100) -> list:
    """
    Retrieve recent healing actions from the audit log.
    
    Args:
        limit: Maximum number of entries to return
        
    Returns:
        List of healing action dictionaries
    """
    if not HEALING_LOG.exists():
        return []
    history: Any = []
    with open(HEALING_LOG, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                history.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return history[-limit:]

def get_healing_stats() -> Dict:
    """
    Calculate healing statistics from audit log.
    
    Returns:
        Dictionary with success rate, total fixes, etc.
    """
    history: Any = get_healing_history(limit=1000)
    if not history:
        return {'total_fixes': 0, 'successful_fixes': 0, 'failed_fixes': 0, 'success_rate': 0.0, 'strategies_used': []}
    total: Any = len(history)
    successful: Any = sum((1 for h in history if h.get('success', False)))
    failed: Any = total - successful
    strategies: Any = list(set((h.get('strategy', 'unknown') for h in history)))
    return {'total_fixes': total, 'successful_fixes': successful, 'failed_fixes': failed, 'success_rate': successful / total * 100 if total > 0 else 0.0, 'strategies_used': strategies}
