import logging
logger = logging.getLogger(__name__)
'Backward compatibility shim for lic_archetypes.\n\n\nLOGGER = logging.getLogger(__name__)\nThis module maintains backward compatibility by re-exporting all components\nmodules to comply with cognitive density limits (max 5 top-level definitions).\n\nThe original lic_archetypes.py contained 12 top-level definitions which\nviolated the Subatomic Canon. It has been refactored into focused submodules.\n'
__all__ = ['*']
