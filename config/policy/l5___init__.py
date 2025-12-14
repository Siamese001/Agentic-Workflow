import logging
from services.configuration import ConfigurationService
logger = logging.getLogger(__name__)
'Backward compatibility shim for l5___init__.\n\n\nLOGGER = logging.getLogger(__name__)\nThis module maintains backward compatibility by re-exporting all components\nmodules to comply with cognitive density limits (max 5 top-level definitions).\n\nThe original l5___init__.py contained 7 top-level definitions which\nviolated the Subatomic Canon. It has been refactored into focused submodules.\n'
__all__ = ['*']
