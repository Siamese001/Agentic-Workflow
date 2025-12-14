"""Enum types for invoke_observability_tool."""
import logging



logger = logging.getLogger(__name__)
class InvocationType(Enum):
    """Types of tool invocation."""
    DIRECT = 'direct'
    PROXY = 'proxy'
    ASYNC = 'async'
    BATCH = 'batch'

class ResponseFormat(Enum):
    """Response format types."""
    JSON = 'json'
    PROTOBUF = 'protobuf'
    XML = 'xml'
    BINARY = 'binary'
