#!/usr/bin/env python3
"""
Serialization Tool
Section 5: Tool Contracts - INFRA tool family
"""

from typing import Dict, Any, List, Optional, Union
import logging
import json

logger = logging.getLogger(__name__)

class SerializationTool:
    """JSON/YAML serialize/deserialize"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.formats = self.config.get("formats", ["json", "yaml"])
        self.pretty_print = self.config.get("pretty_print", True)
        self.indent = self.config.get("indent", 2)
    
    def serialize_json(self, data: Any, pretty_print: Optional[bool] = None) -> str:
        """Serialize data to JSON"""
        try:
            use_pretty = pretty_print if pretty_print is not None else self.pretty_print
            
            if use_pretty:
                json_string = json.dumps(data, indent=self.indent, ensure_ascii=False)
            else:
                json_string = json.dumps(data, ensure_ascii=False)
            
            logger.debug(f"Data serialized to JSON: {len(json_string)} characters")
            return json_string
            
        except Exception as e:
            logger.error(f"JSON serialization failed: {e}")
            raise
    
    def deserialize_json(self, json_string: str) -> Any:
        """Deserialize JSON string to data"""
        try:
            data = json.loads(json_string)
            logger.debug(f"JSON deserialized: {type(data).__name__}")
            return data
            
        except Exception as e:
            logger.error(f"JSON deserialization failed: {e}")
            raise
    
    def serialize_yaml(self, data: Any) -> str:
        """Serialize data to YAML"""
        try:
            # Simple YAML serialization (placeholder - would use yaml library in production)
            if isinstance(data, dict):
                yaml_lines = []
                for key, value in data.items():
                    if isinstance(value, dict):
                        yaml_lines.append(f"{key}:")
                        for sub_key, sub_value in value.items():
                            yaml_lines.append(f"  {sub_key}: {sub_value}")
                    elif isinstance(value, list):
                        yaml_lines.append(f"{key}:")
                        for item in value:
                            yaml_lines.append(f"  - {item}")
                    else:
                        yaml_lines.append(f"{key}: {value}")
                
                yaml_string = "\n".join(yaml_lines)
            else:
                yaml_string = str(data)
            
            logger.debug(f"Data serialized to YAML: {len(yaml_string)} characters")
            return yaml_string
            
        except Exception as e:
            logger.error(f"YAML serialization failed: {e}")
            raise
    
    def deserialize_yaml(self, yaml_string: str) -> Any:
        """Deserialize YAML string to data"""
        try:
            # Simple YAML parsing (placeholder - would use yaml library in production)
            lines = yaml_string.strip().split('\n')
            data = {}
            
            for line in lines:
                if ':' in line and not line.startswith(' '):
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    data[key] = value
            
            logger.debug(f"YAML deserialized: {type(data).__name__}")
            return data
            
        except Exception as e:
            logger.error(f"YAML deserialization failed: {e}")
            raise
    
    def serialize(self, data: Any, format: str = "json", **kwargs) -> str:
        """Serialize data to specified format"""
        try:
            if format not in self.formats:
                raise ValueError(f"Unsupported format: {format}")
            
            if format == "json":
                return self.serialize_json(data, **kwargs)
            elif format == "yaml":
                return self.serialize_yaml(data, **kwargs)
            else:
                raise ValueError(f"Format {format} not implemented")
                
        except Exception as e:
            logger.error(f"Serialization failed: {e}")
            raise
    
    def deserialize(self, string_data: str, format: str = "json") -> Any:
        """Deserialize data from specified format"""
        try:
            if format not in self.formats:
                raise ValueError(f"Unsupported format: {format}")
            
            if format == "json":
                return self.deserialize_json(string_data)
            elif format == "yaml":
                return self.deserialize_yaml(string_data)
            else:
                raise ValueError(f"Format {format} not implemented")
                
        except Exception as e:
            logger.error(f"Deserialization failed: {e}")
            raise
    
    def batch_serialize(self, data_list: List[Any], format: str = "json") -> List[str]:
        """Serialize multiple data items"""
        try:
            results = []
            for data in data_list:
                serialized = self.serialize(data, format)
                results.append(serialized)
            
            logger.info(f"Batch serialized {len(results)} items to {format}")
            return results
            
        except Exception as e:
            logger.error(f"Batch serialization failed: {e}")
            raise
    
    def batch_deserialize(self, string_list: List[str], format: str = "json") -> List[Any]:
        """Deserialize multiple data items"""
        try:
            results = []
            for string_data in string_list:
                deserialized = self.deserialize(string_data, format)
                results.append(deserialized)
            
            logger.info(f"Batch deserialized {len(results)} items from {format}")
            return results
            
        except Exception as e:
            logger.error(f"Batch deserialization failed: {e}")
            raise
    
    def convert_format(self, string_data: str, from_format: str, to_format: str) -> str:
        """Convert data between formats"""
        try:
            # Deserialize from source format
            data = self.deserialize(string_data, from_format)
            
            # Serialize to target format
            converted = self.serialize(data, to_format)
            
            logger.info(f"Converted data from {from_format} to {to_format}")
            return converted
            
        except Exception as e:
            logger.error(f"Format conversion failed: {e}")
            raise
    
    def validate_json(self, json_string: str) -> Dict[str, Any]:
        """Validate JSON string"""
        try:
            data = json.loads(json_string)
            return {
                "is_valid": True,
                "data": data,
                "error": None
            }
        except Exception as e:
            return {
                "is_valid": False,
                "data": None,
                "error": str(e)
            }
    
    def get_format_info(self) -> Dict[str, Any]:
        """Get serialization tool information"""
        return {
            "supported_formats": self.formats,
            "default_format": "json",
            "pretty_print": self.pretty_print,
            "indent": self.indent
        }

def create_serialization_tool(config: Optional[Dict[str, Any]] = None) -> SerializationTool:
    """Factory function to create serialization tool instance"""
    return SerializationTool(config)

# Re-export components
__all__ = [
    'SerializationTool', 'create_serialization_tool'
]





