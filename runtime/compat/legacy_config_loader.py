"""Legacy Config Loader - Configuration loader for old environment format.

This module handles loading and converting configurations from the old
environment format to the new configuration system for backward compatibility.
Follows the functional component pattern with proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
import logging
import os
import json
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ConfigFormat(Enum):
    """Legacy configuration formats."""
    JSON = "json"
    YAML = "yaml"
    ENV = "env"
    INI = "ini"
    PROPERTIES = "properties"


@dataclass
class LegacyConfigSection:
    """Legacy configuration section."""
    section_name: str
    properties: Dict[str, Any] = field(default_factory=dict)
    subsections: Dict[str, 'LegacyConfigSection'] = field(default_factory=dict)


@dataclass
class LegacyConfig:
    """Legacy configuration structure."""
    config_name: str
    version: str
    format: ConfigFormat
    sections: Dict[str, LegacyConfigSection] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConfigLoadOptions:
    """Options for configuration loading."""
    preserve_format: bool = True
    validate_schema: bool = True
    merge_sections: bool = False
    section_separator: str = "."


class LegacyConfigLoader:
    """Loader for legacy configuration formats."""
    
    def __init__(self, options: Optional[ConfigLoadOptions] = None):
        self.options = options or ConfigLoadOptions()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._format_handlers = {
            ConfigFormat.JSON: self._load_json,
            ConfigFormat.YAML: self._load_yaml,
            ConfigFormat.ENV: self._load_env,
            ConfigFormat.INI: self._load_ini,
            ConfigFormat.PROPERTIES: self._load_properties
        }
    
    def load_from_file(self, file_path: str, config_format: ConfigFormat) -> LegacyConfig:
        """Load configuration from file.
        
        Args:
            file_path: Path to configuration file
            config_format: Format of configuration file
            
        Returns:
            LegacyConfig: Loaded configuration
        """
        self.logger.info(f"Loading legacy config from {file_path}")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        handler = self._format_handlers.get(config_format)
        if not handler:
            raise ValueError(f"Unsupported config format: {config_format}")
        
        return handler(file_path)
    
    def load_from_string(self, config_string: str, 
                        config_format: ConfigFormat) -> LegacyConfig:
        """Load configuration from string.
        
        Args:
            config_string: Configuration content
            config_format: Format of configuration
            
        Returns:
            LegacyConfig: Loaded configuration
        """
        self.logger.info(f"Loading legacy config from string in {config_format} format")
        
        handler = self._format_handlers.get(config_format)
        if not handler:
            raise ValueError(f"Unsupported config format: {config_format}")
        
        return handler(config_string, from_string=True)
    
    def load_from_environment(self, prefix: str = "APP_") -> LegacyConfig:
        """Load configuration from environment variables.
        
        Args:
            prefix: Prefix for environment variables
            
        Returns:
            LegacyConfig: Loaded configuration
        """
        self.logger.info(f"Loading legacy config from environment with prefix {prefix}")
        
        config = LegacyConfig(
            config_name="environment",
            version="1.0",
            format=ConfigFormat.ENV
        )
        
        # Collect environment variables
        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower()
                self._set_nested_property(config, config_key, value)
        
        return config
    
    def convert_to_new_format(self, legacy_config: LegacyConfig) -> Dict[str, Any]:
        """Convert legacy config to new format.
        
        Args:
            legacy_config: Legacy configuration
            
        Returns:
            Dict: Configuration in new format
        """
        self.logger.info(f"Converting legacy config {legacy_config.config_name} to new format")
        
        new_config = {
            "name": legacy_config.config_name,
            "version": legacy_config.version,
            "format": legacy_config.format.value,
            "loaded_at": datetime.utcnow().isoformat(),
            "metadata": legacy_config.metadata
        }
        
        # Convert sections
        if self.options.merge_sections:
            new_config.update(self._flatten_sections(legacy_config.sections))
        else:
            new_config["sections"] = self._convert_sections(legacy_config.sections)
        
        return new_config
    
    def _load_json(self, source: str, from_string: bool = False) -> LegacyConfig:
        """Load JSON configuration."""
        if from_string:
            data = json.loads(source)
        else:
            with open(source, 'r') as f:
                data = json.load(f)
        
        config = LegacyConfig(
            config_name=data.get("name", "unknown"),
            version=data.get("version", "1.0"),
            format=ConfigFormat.JSON,
            metadata=data.get("metadata", {})
        )
        
        # Load sections
        for section_name, section_data in data.get("sections", {}).items():
            config.sections[section_name] = self._create_section(section_name, section_data)
        
        return config
    
    def _load_yaml(self, source: str, from_string: bool = False) -> LegacyConfig:
        """Load YAML configuration."""
        try:
            import yaml
        except ImportError:
            raise ImportError("PyYAML is required for YAML configuration loading")
        
        if from_string:
            data = yaml.safe_load(source)
        else:
            with open(source, 'r') as f:
                data = yaml.safe_load(f)
        
        config = LegacyConfig(
            config_name=data.get("name", "unknown"),
            version=data.get("version", "1.0"),
            format=ConfigFormat.YAML,
            metadata=data.get("metadata", {})
        )
        
        # Load sections
        for section_name, section_data in data.get("sections", {}).items():
            config.sections[section_name] = self._create_section(section_name, section_data)
        
        return config
    
    def _load_env(self, source: str, from_string: bool = False) -> LegacyConfig:
        """Load environment configuration."""
        # This is handled by load_from_environment
        return LegacyConfig(
            config_name="environment",
            version="1.0",
            format=ConfigFormat.ENV
        )
    
    def _load_ini(self, source: str, from_string: bool = False) -> LegacyConfig:
        """Load INI configuration."""
        import configparser
        
        parser = configparser.ConfigParser()
        
        if from_string:
            parser.read_string(source)
        else:
            parser.read(source)
        
        config = LegacyConfig(
            config_name="ini_config",
            version="1.0",
            format=ConfigFormat.INI
        )
        
        # Load sections
        for section_name in parser.sections():
            section = LegacyConfigSection(section_name=section_name)
            
            for key, value in parser[section_name].items():
                # Try to parse as JSON, otherwise keep as string
                try:
                    parsed_value = json.loads(value)
                except (json.JSONDecodeError, ValueError):
                    parsed_value = value
                
                section.properties[key] = parsed_value
            
            config.sections[section_name] = section
        
        return config
    
    def _load_properties(self, source: str, from_string: bool = False) -> LegacyConfig:
        """Load Java properties configuration."""
        config = LegacyConfig(
            config_name="properties",
            version="1.0",
            format=ConfigFormat.PROPERTIES
        )
        
        if from_string:
            lines = source.split('\n')
        else:
            with open(source, 'r') as f:
                lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#') or line.startswith('!'):
                continue
            
            # Parse property
            if '=' in line:
                key, value = line.split('=', 1)
            elif ':' in line:
                key, value = line.split(':', 1)
            else:
                continue
            
            key = key.strip()
            value = value.strip()
            
            # Remove quotes if present
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            
            self._set_nested_property(config, key, value)
        
        return config
    
    def _create_section(self, name: str, data: Dict[str, Any]) -> LegacyConfigSection:
        """Create a configuration section from data."""
        section = LegacyConfigSection(section_name=name)
        
        for key, value in data.items():
            if isinstance(value, dict):
                # Subsection
                section.subsections[key] = self._create_section(key, value)
            else:
                # Property
                section.properties[key] = value
        
        return section
    
    def _set_nested_property(self, config: LegacyConfig, key: str, value: Any) -> None:
        """Set nested property using dot notation."""
        parts = key.split(self.options.section_separator)
        current = config.sections
        
        # Navigate to parent section
        for part in parts[:-1]:
            if part not in current:
                current[part] = LegacyConfigSection(section_name=part)
            current = current[part].subsections
        
        # Set property
        final_key = parts[-1]
        if final_key not in current:
            current[final_key] = LegacyConfigSection(section_name=final_key)
        
        # Try to parse value
        parsed_value = self._parse_value(value)
        current[final_key].properties[final_key] = parsed_value
    
    def _parse_value(self, value: str) -> Any:
        """Parse string value to appropriate type."""
        # Try boolean
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # Try integer
        try:
            return int(value)
        except ValueError:
            pass
        
        # Try float
        try:
            return float(value)
        except ValueError:
            pass
        
        # Try JSON
        try:
            return json.loads(value)
        except (json.JSONDecodeError, ValueError):
            pass
        
        # Return as string
        return value
    
    def _convert_sections(self, sections: Dict[str, LegacyConfigSection]) -> Dict[str, Any]:
        """Convert sections to new format."""
        result = {}
        
        for name, section in sections.items():
            section_data = {
                "properties": section.properties
            }
            
            if section.subsections:
                section_data["subsections"] = self._convert_sections(section.subsections)
            
            result[name] = section_data
        
        return result
    
    def _flatten_sections(self, sections: Dict[str, LegacyConfigSection],
                         prefix: str = "") -> Dict[str, Any]:
        """Flatten sections to single level."""
        result = {}
        
        for name, section in sections.items():
            full_name = f"{prefix}{self.options.section_separator}{name}" if prefix else name
            
            # Add properties
            for key, value in section.properties.items():
                result[f"{full_name}{self.options.section_separator}{key}"] = value
            
            # Add subsections
            if section.subsections:
                result.update(self._flatten_sections(section.subsections, full_name))
        
        return result


# Factory function for easy instantiation
def create_legacy_config_loader(
    preserve_format: bool = True,
    validate_schema: bool = True,
    **kwargs
) -> LegacyConfigLoader:
    """Create a configured legacy config loader."""
    options = ConfigLoadOptions(
        preserve_format=preserve_format,
        validate_schema=validate_schema,
        **kwargs
    )
    return LegacyConfigLoader(options)


# Convenience function for direct loading
def load_legacy_config(file_path: str, config_format: str = "json") -> Dict[str, Any]:
    """Load legacy configuration file.
    
    Args:
        file_path: Path to configuration file
        config_format: Format of configuration
        
    Returns:
        Dict: Configuration in new format
    """
    loader = create_legacy_config_loader()
    legacy_config = loader.load_from_file(file_path, ConfigFormat(config_format))
    return loader.convert_to_new_format(legacy_config)
