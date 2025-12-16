import logging

logger = logging.getLogger(__name__)  # GLOBAL: Review if this should be constant
'Backward compatibility shim for message_refinement_adjust_scores.\n\n\nLOGGER = logging.getLogger(__name__)\nThis module maintains backward compatibility by re-exporting all components\nmodules to comply with cognitive density limits (max 5 top-level definitions).\n\nThe original message_refinement_adjust_scores.py contained 6 top-level definitions which\nviolated the Subatomic Canon. It has been refactored into focused submodules.\n'
__all__ = ['*']

