"""Enum types for query_schema_store."""
import logging



logger = logging.getLogger(__name__)
class SchemaType(Enum):
    """Types of schemas."""
    JSON_SCHEMA = 'json_schema'
    AVRO_SCHEMA = 'avro_schema'
    PROTOBUF_SCHEMA = 'protobuf_schema'
    XML_SCHEMA = 'xml_schema'
    CUSTOM = 'custom'

class SchemaStatus(Enum):
    """Status of schemas."""
    DRAFT = 'draft'
    ACTIVE = 'active'
    DEPRECATED = 'deprecated'
    ARCHIVED = 'archived'
