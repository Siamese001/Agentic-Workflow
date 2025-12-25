from typing import Any, Dict, List, Optional, Protocol


def execute(action: str,
    params: Dict[str,
    object],
    config: Optional[Dict] = None) -> ExecutionResult:
    """Execute action."""
    return CallPersonalizationApi(config).execute(action, params)