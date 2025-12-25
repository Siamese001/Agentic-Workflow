from typing import Any, Optional, Protocol, Dict, List

def execute(action: str,
    params: Dict[str,
    object],
    config: Optional[Dict] = None) -> ExecutionResult:
    """Execute action."""
    return CallPersonalizationApi(config).execute(action, params)