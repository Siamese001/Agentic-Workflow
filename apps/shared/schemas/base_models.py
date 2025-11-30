"""
Shared Base Models
LEVEL 5 - Foundation Pydantic models shared across engines
"""

from pydantic import BaseModel as PydanticBaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import uuid4, UUID
import json

class BaseModel(PydanticBaseModel):
    """Base model with common configuration and methods"""
    
    class Config:
        """Pydantic configuration"""
        allow_population_by_field_name = True
        validate_assignment = True
        use_enum_values = True
        extra = "forbid"
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return self.dict(exclude_none=True)
    
    def to_json(self) -> str:
        """Convert model to JSON string"""
        return self.json(exclude_none=True, indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseModel":
        """Create model from dictionary"""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> "BaseModel":
        """Create model from JSON string"""
        data = json.loads(json_str)
        return cls(**data)

class TimestampedModel(BaseModel):
    """Model with timestamp fields"""
    
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the record was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the record was last updated"
    )
    
    @validator("updated_at", pre=True, always=True)
    def update_timestamp_on_change(cls, v, values):
        """Automatically update updated_at when model changes"""
        return datetime.utcnow()
    
    def touch(self):
        """Update the updated_at timestamp"""
        self.updated_at = datetime.utcnow()

class IdentifiableModel(BaseModel):
    """Model with identification fields"""
    
    id: Optional[UUID] = Field(
        default_factory=uuid4,
        description="Unique identifier for the record"
    )
    external_id: Optional[str] = Field(
        None,
        description="External system identifier"
    )
    
    @validator("external_id")
    def validate_external_id(cls, v):
        """Validate external ID format"""
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                return None
            if len(v) > 255:
                raise ValueError("External ID cannot exceed 255 characters")
        return v

class AuditableModel(TimestampedModel, IdentifiableModel):
    """Model with audit fields"""
    
    created_by: Optional[str] = Field(
        None,
        description="User or system that created the record"
    )
    updated_by: Optional[str] = Field(
        None,
        description="User or system that last updated the record"
    )
    version: int = Field(
        default=1,
        description="Version number of the record"
    )
    
    def increment_version(self):
        """Increment the version number"""
        self.version += 1
        self.touch()

class MetadataModel(BaseModel):
    """Model with flexible metadata"""
    
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional metadata as key-value pairs"
    )
    tags: Optional[list[str]] = Field(
        default_factory=list,
        description="Tags for categorization and search"
    )
    
    @validator("metadata")
    def validate_metadata(cls, v):
        """Validate metadata structure"""
        if v is None:
            return {}
        
        # Ensure all keys are strings
        if not all(isinstance(k, str) for k in v.keys()):
            raise ValueError("All metadata keys must be strings")
        
        # Limit metadata size
        if len(str(v)) > 10000:  # 10KB limit
            raise ValueError("Metadata size exceeds 10KB limit")
        
        return v
    
    @validator("tags")
    def validate_tags(cls, v):
        """Validate tags"""
        if v is None:
            return []
        
        # Ensure all tags are strings
        if not all(isinstance(tag, str) for tag in v):
            raise ValueError("All tags must be strings")
        
        # Remove duplicates and empty tags
        cleaned_tags = [tag.strip() for tag in v if tag.strip()]
        return list(dict.fromkeys(cleaned_tags))  # Preserve order, remove duplicates
    
    def add_tag(self, tag: str):
        """Add a tag if it doesn't exist"""
        if tag and tag.strip() and tag.strip() not in self.tags:
            self.tags.append(tag.strip())
    
    def remove_tag(self, tag: str):
        """Remove a tag if it exists"""
        if tag in self.tags:
            self.tags.remove(tag)
    
    def set_metadata(self, key: str, value: Any):
        """Set a metadata value"""
        if not isinstance(key, str) or not key.strip():
            raise ValueError("Metadata key must be a non-empty string")
        
        if self.metadata is None:
            self.metadata = {}
        
        self.metadata[key.strip()] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get a metadata value"""
        if self.metadata is None:
            return default
        return self.metadata.get(key, default)

class StatusModel(BaseModel):
    """Model with status tracking"""
    
    status: str = Field(
        default="active",
        description="Current status of the record"
    )
    status_reason: Optional[str] = Field(
        None,
        description="Reason for current status"
    )
    
    @validator("status")
    def validate_status(cls, v):
        """Validate status value"""
        valid_statuses = {
            "active", "inactive", "pending", "completed", 
            "failed", "cancelled", "archived", "draft"
        }
        
        if v.lower() not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        
        return v.lower()
    
    def set_status(self, status: str, reason: Optional[str] = None):
        """Update status with optional reason"""
        self.status = status.lower()
        self.status_reason = reason

class SearchableModel(MetadataModel):
    """Model optimized for search operations"""
    
    search_text: Optional[str] = Field(
        None,
        description="Concatenated text for full-text search"
    )
    search_vector: Optional[Dict[str, float]] = Field(
        None,
        description="Search vector for similarity matching"
    )
    
    def update_search_text(self, *text_fields):
        """Update search text from provided fields"""
        text_parts = []
        for field in text_fields:
            if field:
                if isinstance(field, list):
                    text_parts.extend(str(item) for item in field)
                else:
                    text_parts.append(str(field))
        
        self.search_text = " ".join(text_parts).lower()
    
    def update_search_vector(self, vector: Dict[str, float]):
        """Update search vector"""
        self.search_vector = vector

class ConfigurableModel(BaseModel):
    """Model with configuration support"""
    
    config: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Configuration parameters"
    )
    
    @validator("config")
    def validate_config(cls, v):
        """Validate configuration"""
        if v is None:
            return {}
        
        # Ensure all keys are strings
        if not all(isinstance(k, str) for k in v.keys()):
            raise ValueError("All configuration keys must be strings")
        
        return v
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set_config(self, key: str, value: Any):
        """Set configuration value"""
        if self.config is None:
            self.config = {}
        self.config[key] = value
    
    def update_config(self, config_dict: Dict[str, Any]):
        """Update multiple configuration values"""
        if self.config is None:
            self.config = {}
        self.config.update(config_dict)

# Combined base models for common use cases
class StandardModel(TimestampedModel, IdentifiableModel, MetadataModel):
    """Standard model with most common fields"""
    pass

class FullModel(AuditableModel, MetadataModel, StatusModel):
    """Full model with all common fields"""
    pass

class SearchableStandardModel(StandardModel, SearchableModel):
    """Standard model with search capabilities"""
    pass

class ConfigurableStandardModel(StandardModel, ConfigurableModel):
    """Standard model with configuration support"""
    pass
