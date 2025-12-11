"""Internal Memory Adapter - Adapter for old internal memory format/database.

This module provides an adapter to read/write from the old internal memory format
or database, ensuring backward compatibility with legacy data storage.
Follows the functional component pattern with proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, BinaryIO
import logging
from datetime import datetime
from enum import Enum
import pickle
import json

logger = logging.getLogger(__name__)


class MemoryFormat(Enum):
    """Legacy memory formats."""
    PICKLE = "pickle"
    JSON = "json"
    CUSTOM = "custom"
    DATABASE = "database"


@dataclass
class MemoryEntry:
    """Legacy memory entry."""
    key: str
    value: Any
    timestamp: Optional[datetime] = None
    ttl: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MemorySegment:
    """Legacy memory segment."""
    segment_id: str
    entries: Dict[str, MemoryEntry] = field(default_factory=dict)
    format: MemoryFormat = MemoryFormat.PICKLE
    size_limit: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AdapterConfig:
    """Configuration for memory adapter."""
    auto_migrate: bool = True
    preserve_timestamps: bool = True
    compression: bool = False
    encryption: bool = False
    cache_size: int = 1000


class InternalMemoryAdapter:
    """Adapter for legacy internal memory formats."""
    
    def __init__(self, config: Optional[AdapterConfig] = None):
        self.config = config or AdapterConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._segments: Dict[str, MemorySegment] = {}
        self._format_handlers = {
            MemoryFormat.PICKLE: self._handle_pickle,
            MemoryFormat.JSON: self._handle_json,
            MemoryFormat.CUSTOM: self._handle_custom,
            MemoryFormat.DATABASE: self._handle_database
        }
        self._cache: Dict[str, Any] = {}
    
    def read_from_legacy_format(self, source: Union[str, BinaryIO], 
                               format: MemoryFormat) -> Dict[str, Any]:
        """Read data from legacy memory format.
        
        Args:
            source: Data source (file path or file-like object)
            format: Legacy format type
            
        Returns:
            Dict: Converted data in new format
        """
        self.logger.info(f"Reading legacy memory format: {format}")
        
        handler = self._format_handlers.get(format)
        if not handler:
            raise ValueError(f"Unsupported memory format: {format}")
        
        return handler(source, mode="read")
    
    def write_to_legacy_format(self, data: Dict[str, Any], 
                              destination: Union[str, BinaryIO],
                              format: MemoryFormat) -> None:
        """Write data to legacy memory format.
        
        Args:
            data: Data to write
            destination: Write destination
            format: Legacy format type
        """
        self.logger.info(f"Writing legacy memory format: {format}")
        
        handler = self._format_handlers.get(format)
        if not handler:
            raise ValueError(f"Unsupported memory format: {format}")
        
        handler(destination, data, mode="write")
    
    def migrate_legacy_memory(self, legacy_source: Union[str, BinaryIO],
                             format: MemoryFormat) -> Dict[str, Any]:
        """Migrate legacy memory to new format.
        
        Args:
            legacy_source: Legacy memory source
            format: Legacy format type
            
        Returns:
            Dict: Migrated data
        """
        self.logger.info(f"Migrating legacy memory from {format}")
        
        # Read legacy data
        legacy_data = self.read_from_legacy_format(legacy_source, format)
        
        # Convert to new format
        migrated_data = {
            "version": "2.0",
            "migrated_at": datetime.utcnow().isoformat(),
            "source_format": format.value,
            "data": legacy_data
        }
        
        # Add migration metadata
        if self.config.preserve_timestamps:
            migrated_data["preserve_timestamps"] = True
        
        return migrated_data
    
    def create_memory_segment(self, segment_id: str, 
                             format: MemoryFormat = MemoryFormat.PICKLE) -> MemorySegment:
        """Create a memory segment.
        
        Args:
            segment_id: Segment identifier
            format: Memory format
            
        Returns:
            MemorySegment: Created segment
        """
        segment = MemorySegment(
            segment_id=segment_id,
            format=format
        )
        
        self._segments[segment_id] = segment
        self.logger.info(f"Created memory segment: {segment_id}")
        
        return segment
    
    def store_entry(self, segment_id: str, key: str, value: Any,
                   ttl: Optional[float] = None) -> None:
        """Store an entry in memory segment.
        
        Args:
            segment_id: Segment identifier
            key: Entry key
            value: Entry value
            ttl: Time to live
        """
        if segment_id not in self._segments:
            self.create_memory_segment(segment_id)
        
        segment = self._segments[segment_id]
        entry = MemoryEntry(
            key=key,
            value=value,
            timestamp=datetime.utcnow(),
            ttl=ttl
        )
        
        segment.entries[key] = entry
        
        # Update cache
        if len(self._cache) < self.config.cache_size:
            self._cache[f"{segment_id}:{key}"] = value
        
        self.logger.debug(f"Stored entry {key} in segment {segment_id}")
    
    def retrieve_entry(self, segment_id: str, key: str) -> Optional[Any]:
        """Retrieve an entry from memory segment.
        
        Args:
            segment_id: Segment identifier
            key: Entry key
            
        Returns:
            Optional[Any]: Entry value
        """
        # Check cache first
        cache_key = f"{segment_id}:{key}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Check segment
        if segment_id in self._segments:
            segment = self._segments[segment_id]
            if key in segment.entries:
                entry = segment.entries[key]
                
                # Check TTL
                if entry.ttl:
                    elapsed = (datetime.utcnow() - entry.timestamp).total_seconds()
                    if elapsed > entry.ttl:
                        del segment.entries[key]
                        return None
                
                return entry.value
        
        return None
    
    def _handle_pickle(self, source: Union[str, BinaryIO], 
                      data: Optional[Dict[str, Any]] = None,
                      mode: str = "read") -> Optional[Dict[str, Any]]:
        """Handle pickle format."""
        if mode == "read":
            if isinstance(source, str):
                with open(source, 'rb') as f:
                    return pickle.load(f)
            else:
                return pickle.load(source)
        
        elif mode == "write":
            if isinstance(source, str):
                with open(source, 'wb') as f:
                    pickle.dump(data, f)
            else:
                pickle.dump(data, source)
        
        return None
    
    def _handle_json(self, source: Union[str, BinaryIO],
                    data: Optional[Dict[str, Any]] = None,
                    mode: str = "read") -> Optional[Dict[str, Any]]:
        """Handle JSON format."""
        if mode == "read":
            if isinstance(source, str):
                with open(source, 'r') as f:
                    return json.load(f)
            else:
                return json.load(source)
        
        elif mode == "write":
            if isinstance(source, str):
                with open(source, 'w') as f:
                    json.dump(data, f, indent=2)
            else:
                json.dump(data, source, indent=2)
        
        return None
    
    def _handle_custom(self, source: Union[str, BinaryIO],
                      data: Optional[Dict[str, Any]] = None,
                      mode: str = "read") -> Optional[Dict[str, Any]]:
        """Handle custom format."""
        # Placeholder for custom format handling
        if mode == "read":
            return {"custom_format": True, "source": str(source)}
        
        elif mode == "write":
            self.logger.info("Custom format write not implemented")
        
        return None
    
    def _handle_database(self, source: Union[str, BinaryIO],
                        data: Optional[Dict[str, Any]] = None,
                        mode: str = "read") -> Optional[Dict[str, Any]]:
        """Handle database format."""
        # Placeholder for database format handling
        if mode == "read":
            return {
                "database_format": True,
                "connection": str(source),
                "tables": ["memory_table"],
                "data": {}
            }
        
        elif mode == "write":
            self.logger.info("Database format write not implemented")
        
        return None


# Factory function for easy instantiation
def create_internal_memory_adapter(
    auto_migrate: bool = True,
    preserve_timestamps: bool = True,
    **kwargs
) -> InternalMemoryAdapter:
    """Create a configured internal memory adapter."""
    config = AdapterConfig(
        auto_migrate=auto_migrate,
        preserve_timestamps=preserve_timestamps,
        **kwargs
    )
    return InternalMemoryAdapter(config)


# Convenience function for direct migration
def migrate_legacy_memory_file(file_path: str, 
                              format: str = "pickle") -> Dict[str, Any]:
    """Migrate legacy memory file to new format.
    
    Args:
        file_path: Path to legacy memory file
        format: Legacy format type
        
    Returns:
        Dict: Migrated data
    """
    adapter = create_internal_memory_adapter()
    return adapter.migrate_legacy_memory(file_path, MemoryFormat(format))
