import logging

logger = logging.getLogger(__name__)
'Backward compatibility shim for tools_utility_prepare_information.\n\n\nLOGGER = logging.getLogger(__name__)\nThis module maintains backward compatibility by re-exporting all components\nmodules to comply with cognitive density limits (max 5 top-level definitions).\n\nThe original tools_utility_prepare_information.py contained 6 top-level definitions which\nviolated the Subatomic Canon. It has been refactored into focused submodules.\n'
__all__ = ['*']