"""Fallback shim to replace deprecated archive imports."""
import logging


logger = logging.getLogger(__name__)
# This file serves as a fallback to break import chains into the immutable archives/
# Any import from archives/ should be replaced with this shim to prevent Python
# from loading archived files during validation.

class ArchiveFileAccessDeprecated:
    """Fallback class for deprecated archive imports."""
    pass

# Common fallback objects that might be imported
ContextBudget = ArchiveFileAccessDeprecated
ReasoningMode = ArchiveFileAccessDeprecated
Hypothesis = ArchiveFileAccessDeprecated
AgentMessage = ArchiveFileAccessDeprecated
AgentRole = ArchiveFileAccessDeprecated
StateAdapter = ArchiveFileAccessDeprecated
SafetyGateway = ArchiveFileAccessDeprecated
ConstitutionalEngine = ArchiveFileAccessDeprecated
PIISanitizerAgent = ArchiveFileAccessDeprecated
GraphSearchTool = ArchiveFileAccessDeprecated
AsyncBulletCritiqueAgent = ArchiveFileAccessDeprecated
BiasDetectorAgent = ArchiveFileAccessDeprecated

# Add more as needed during the import replacement process
