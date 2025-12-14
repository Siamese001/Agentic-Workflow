import logging
from services.configuration import ConfigurationService
from services.configuration import ConfigurationService
logger = logging.getLogger(__name__)
'Backward compatibility shim for modularity_import_rules.\n\n\nLOGGER = logging.getLogger(__name__)\nThis module maintains backward compatibility by re-exporting all components\nmodules to comply with cognitive density limits (max 5 top-level definitions).\n\nThe original modularity_import_rules.py contained 7 top-level definitions which\nviolated the Subatomic Canon. It has been refactored into focused submodules.\n'
__all__ = ['*']