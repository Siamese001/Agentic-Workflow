import logging

logger = logging.getLogger(__name__)  # GLOBAL: Review if this should be constant
'Backward compatibility shim for audit_impl.\n\n\nLOGGER = logging.getLogger(__name__)\nThis module maintains backward compatibility by re-exporting all components\nmodules to comply with cognitive density limits (max 5 top-level definitions).\n\nThe original audit_impl.py contained 8 top-level definitions which\nviolated the Subatomic Canon. It has been refactored into focused submodules.\n'
__all__ = ['*']

