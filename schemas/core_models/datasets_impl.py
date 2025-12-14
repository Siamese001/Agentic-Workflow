import logging
from services.configuration import ConfigurationService
logger = logging.getLogger(__name__)
'Backward compatibility shim for datasets_impl.\n\n\nLOGGER = logging.getLogger(__name__)\nThis module maintains backward compatibility by re-exporting all components\nmodules to comply with cognitive density limits (max 5 top-level definitions).\n\nThe original datasets_impl.py contained 6 top-level definitions which\nviolated the Subatomic Canon. It has been refactored into focused submodules.\n'
__all__ = ['*']