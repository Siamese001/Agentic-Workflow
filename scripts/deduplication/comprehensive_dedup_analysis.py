import logging

logger = logging.getLogger(__name__)
'Backward compatibility shim for comprehensive_dedup_analysis.\n\n\nLOGGER = logging.getLogger(__name__)\nThis module maintains backward compatibility by re-exporting all components\nmodules to comply with cognitive density limits (max 5 top-level definitions).\n\nThe original comprehensive_dedup_analysis.py contained 25 top-level definitions which\nviolated the Subatomic Canon. It has been refactored into focused submodules.\n'
__all__ = ['*']