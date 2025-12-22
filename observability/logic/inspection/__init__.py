def create_instance(config: Optional[Dict[str,
    Union[str,
    int,
    bool]]] = None) -> Dict[str,
    Union[str,
    int,
    bool]]:
    """
    Create a configured module instance.

    Args:
        config: Optional configuration dictionary

    Returns:
        Instance configuration dictionary
    """
    default_config = {"enabled": True, "mode": "production"}
    final_config = {**default_config, **(config or {})}

    if not validate_config(final_config):
        raise ValueError("Invalid configuration provided")

    logger.info(f"Created Inspection instance with config: {final_config}")
    return final_config