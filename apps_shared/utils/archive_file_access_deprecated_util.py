"""Fallback shim to replace deprecated archive imports."""

# This file serves as a fallback to break import chains into the immutable archives/
# Any import from archives/ should be replaced with this shim to prevent Python
# from loading archived files during validation.


class ARCHIVE_FILE_ACCESS_DEPRECATED:
    """Fallback class for deprecated archive imports."""

    pass


# Common fallback objects that might be imported
ContextBudget = ARCHIVE_FILE_ACCESS_DEPRECATED
ReasoningMode = ARCHIVE_FILE_ACCESS_DEPRECATED
Hypothesis = ARCHIVE_FILE_ACCESS_DEPRECATED
AgentMessage = ARCHIVE_FILE_ACCESS_DEPRECATED
AgentRole = ARCHIVE_FILE_ACCESS_DEPRECATED
StateAdapter = ARCHIVE_FILE_ACCESS_DEPRECATED
SafetyGateway = ARCHIVE_FILE_ACCESS_DEPRECATED
ConstitutionalEngine = ARCHIVE_FILE_ACCESS_DEPRECATED
GraphSearchTool = ARCHIVE_FILE_ACCESS_DEPRECATED
AsyncBulletCritiqueAgent = ARCHIVE_FILE_ACCESS_DEPRECATED
BiasDetectorAgent = ARCHIVE_FILE_ACCESS_DEPRECATED

# Add more as needed during the import replacement process
