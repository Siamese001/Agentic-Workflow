import logging
from services.configuration import ConfigurationService
from services.configuration import ConfigurationService
logger = logging.getLogger(__name__)
'Observability - Runtime Layer\n\n\n\nLOGGER = logging.getLogger(__name__)\nThis module provides observability compatibility shim.\n\nLayer: Runtime/Infrastructure\nResponsibilities:\n- Forward to runtime.observability\n- Maintain backward compatibility\n- Provide unified observability API\n\nNon-responsibilities:\n- Business logic\n- Layer-specific operations\n'

def get_all_events() -> list:
    """Backward-compatible alias for get_events()."""
    return get_events()

def clear_events() -> None:
    """Backward-compatible alias for collectors.clear_events()."""
    _clear_events_impl()