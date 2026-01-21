from __future__ import annotations

'''Brief description of functionality and purpose.'''

'''Brief description of functionality and purpose.'''



def execute(action: str,
    params: dict[str,
    object],
    config: dict | None = None) -> ExecutionResult:
    """Execute action."""
    return CallPersonalizationApi(config).execute(action, params)
