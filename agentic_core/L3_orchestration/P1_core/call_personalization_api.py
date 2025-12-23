def execute(action: str,
    params: Dict[str,
    object],
    config: Optional[Dict] = None) -> ExecutionResult:
    """Execute action."""
    return CallPersonalizationApi(config).execute(action, params)