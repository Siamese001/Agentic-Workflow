"""Old Schema Type Transformer - Converts legacy schema types to Pydantic models.

This module handles conversion of legacy schema types, including old Python 2/3
compatibility formats, to modern Pydantic models for backward compatibility.
Follows the functional component pattern with proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Type, get_type_hints
import logging
from datetime import datetime
from enum import Enum
import inspect

logger = logging.getLogger(__name__)


class LegacyType(Enum):
    """Legacy schema types."""
    DICT_MODEL = "dict_model"
    CLASS_MODEL = "class_model"
    NAMED_TUPLE = "namedtuple"
    TUPLE = "tuple"
    CUSTOM = "custom"


@dataclass
class LegacyFieldDefinition:
    """Definition of a legacy field."""
    field_name: str
    field_type: str
    required: bool = True
    default_value: Any = None
    validators: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LegacySchemaDefinition:
    """Definition of a legacy schema."""
    schema_name: str
    schema_type: LegacyType
    version: str
    fields: List[LegacyFieldDefinition] = field(default_factory=list)
    base_classes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TransformationConfig:
    """Configuration for schema transformation."""
    preserve_optional: bool = True
    convert_types: bool = True
    add_validators: bool = True
    generate_docstrings: bool = True
    strict_mode: bool = False


class OldSchemaTypeTransformer:
    """Transformer for legacy schema types to Pydantic models."""
    
    def __init__(self, config: Optional[TransformationConfig] = None):
        self.config = config or TransformationConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._type_mapping = {
            "str": "str",
            "int": "int",
            "float": "float",
            "bool": "bool",
            "list": "List",
            "dict": "Dict",
            "datetime": "datetime",
            "unicode": "str",  # Python 2 unicode to Python 3 str
            "long": "int",  # Python 2 long to Python 3 int
            "basestring": "str",  # Python 2 basestring to Python 3 str
        }
    
    def transform_dict_model(self, schema_dict: Dict[str, Any]) -> str:
        """Transform a dictionary-based model to Pydantic model.
        
        Args:
            schema_dict: Dictionary model definition
            
        Returns:
            str: Pydantic model code
        """
        self.logger.info("Transforming dictionary model to Pydantic")
        
        schema_name = schema_dict.get("__class__", "DynamicModel")
        fields = schema_dict.get("_fields", {})
        
        # Parse field definitions
        field_definitions = []
        for field_name, field_info in fields.items():
            if isinstance(field_info, dict):
                field_def = LegacyFieldDefinition(
                    field_name=field_name,
                    field_type=field_info.get("type", "str"),
                    required=field_info.get("required", True),
                    default_value=field_info.get("default"),
                    validators=field_info.get("validators", [])
                )
                field_definitions.append(field_def)
        
        # Generate Pydantic model
        return self._generate_pydantic_model(schema_name, field_definitions)
    
    def transform_class_model(self, model_class: Type) -> str:
        """Transform a class-based model to Pydantic model.
        
        Args:
            model_class: Legacy model class
            
        Returns:
            str: Pydantic model code
        """
        self.logger.info(f"Transforming class model {model_class.__name__} to Pydantic")
        
        # Get class annotations
        type_hints = get_type_hints(model_class)
        
        # Get field definitions from class
        field_definitions = []
        
        # Check for __annotations__ (Python 3.6+)
        if hasattr(model_class, "__annotations__"):
            for field_name, field_type in model_class.__annotations__.items():
                field_def = LegacyFieldDefinition(
                    field_name=field_name,
                    field_type=self._get_type_string(field_type),
                    required=True  # Assume required unless default exists
                )
                field_definitions.append(field_def)
        
        # Check for class attributes with defaults
        for attr_name in dir(model_class):
            if not attr_name.startswith("_"):
                attr_value = getattr(model_class, attr_name)
                if not inspect.ismethod(attr_value) and not inspect.isfunction(attr_value):
                    # Check if field already exists
                    existing = next((f for f in field_definitions if f.field_name == attr_name), None)
                    if existing:
                        existing.default_value = attr_value
                        existing.required = False
                    else:
                        field_def = LegacyFieldDefinition(
                            field_name=attr_name,
                            field_type=type(attr_value).__name__,
                            required=False,
                            default_value=attr_value
                        )
                        field_definitions.append(field_def)
        
        # Generate Pydantic model
        return self._generate_pydantic_model(model_class.__name__, field_definitions)
    
    def transform_namedtuple(self, namedtuple_type: type) -> str:
        """Transform a namedtuple to Pydantic model.
        
        Args:
            namedtuple_type: NamedTuple type
            
        Returns:
            str: Pydantic model code
        """
        self.logger.info(f"Transforming namedtuple {namedtuple_type.__name__} to Pydantic")
        
        field_definitions = []
        
        # Get fields from namedtuple
        if hasattr(namedtuple_type, "_fields"):
            for field_name in namedtuple_type._fields:
                field_def = LegacyFieldDefinition(
                    field_name=field_name,
                    field_type="Any",  # NamedTuple doesn't store type info
                    required=True
                )
                field_definitions.append(field_def)
        
        # Generate Pydantic model
        return self._generate_pydantic_model(namedtuple_type.__name__, field_definitions)
    
    def transform_legacy_schema(self, schema_def: LegacySchemaDefinition) -> str:
        """Transform a legacy schema definition to Pydantic model.
        
        Args:
            schema_def: Legacy schema definition
            
        Returns:
            str: Pydantic model code
        """
        self.logger.info(f"Transforming legacy schema {schema_def.schema_name}")
        
        if schema_def.schema_type == LegacyType.DICT_MODEL:
            return self._generate_pydantic_model(schema_def.schema_name, schema_def.fields)
        elif schema_def.schema_type == LegacyType.CLASS_MODEL:
            return self._generate_pydantic_model(schema_def.schema_name, schema_def.fields)
        elif schema_def.schema_type == LegacyType.NAMED_TUPLE:
            return self._generate_pydantic_model(schema_def.schema_name, schema_def.fields)
        else:
            raise ValueError(f"Unsupported schema type: {schema_def.schema_type}")
    
    def _generate_pydantic_model(self, model_name: str, 
                                fields: List[LegacyFieldDefinition]) -> str:
        """Generate Pydantic model code.
        
        Args:
            model_name: Name of the model
            fields: List of field definitions
            
        Returns:
            str: Generated Pydantic model code
        """
        lines = []
        
        # Add imports
        lines.append("from pydantic import BaseModel, Field")
        lines.append("from typing import Optional, List, Dict, Any")
        lines.append("from datetime import datetime")
        lines.append("")
        
        # Add class definition
        lines.append(f"class {model_name}(BaseModel):")
        
        # Add docstring if enabled
        if self.config.generate_docstrings:
            lines.append('    """')
            lines.append(f'    {model_name} model.')
            lines.append('    """')
            lines.append("")
        
        # Add fields
        for field in fields:
            field_type = self._convert_type(field.field_type)
            
            if field.required:
                if field.default_value is not None:
                    line = f"    {field.field_name}: {field_type} = Field(default={repr(field.default_value)})"
                else:
                    line = f"    {field.field_name}: {field_type}"
            else:
                if self.config.preserve_optional:
                    line = f"    {field.field_name}: Optional[{field_type}] = Field(default={repr(field.default_value)})"
                else:
                    line = f"    {field.field_name}: {field_type} = Field(default={repr(field.default_value)})"
            
            lines.append(line)
        
        # Add class config
        lines.append("")
        lines.append("    class Config:")
        lines.append('        """Pydantic configuration."""')
        lines.append("        use_enum_values = True")
        lines.append("        validate_assignment = True")
        
        if self.config.strict_mode:
            lines.append("        extra = 'forbid'")
        else:
            lines.append("        extra = 'allow'")
        
        return "\n".join(lines)
    
    def _convert_type(self, old_type: str) -> str:
        """Convert legacy type to modern type.
        
        Args:
            old_type: Legacy type string
            
        Returns:
            str: Modern type string
        """
        if not self.config.convert_types:
            return old_type
        
        # Handle generic types
        if old_type.startswith("List["):
            inner_type = old_type[5:-1]
            return f"List[{self._convert_type(inner_type)}]"
        elif old_type.startswith("Dict["):
            parts = old_type[5:-1].split(",")
            if len(parts) == 2:
                key_type = self._convert_type(parts[0].strip())
                value_type = self._convert_type(parts[1].strip())
                return f"Dict[{key_type}, {value_type}]"
        elif old_type.startswith("Optional["):
            inner_type = old_type[9:-1]
            return f"Optional[{self._convert_type(inner_type)}]"
        
        # Handle simple types
        return self._type_mapping.get(old_type, old_type)
    
    def _get_type_string(self, field_type: Type) -> str:
        """Get string representation of type.
        
        Args:
            field_type: Python type
            
        Returns:
            str: Type string
        """
        if hasattr(field_type, "__origin__"):
            # Generic type
            origin = field_type.__origin__
            if origin is list:
                return f"List[{self._get_type_string(field_type.__args__[0])}]"
            elif origin is dict:
                return f"Dict[{self._get_type_string(field_type.__args__[0])}, {self._get_type_string(field_type.__args__[1])}]"
            elif origin is Union:
                args = field_type.__args__
                if len(args) == 2 and type(None) in args:
                    # Optional
                    non_none_type = args[0] if args[1] is type(None) else args[1]
                    return f"Optional[{self._get_type_string(non_none_type)}]"
        
        return field_type.__name__


# Factory function for easy instantiation
def create_schema_transformer(
    preserve_optional: bool = True,
    convert_types: bool = True,
    **kwargs
) -> OldSchemaTypeTransformer:
    """Create a configured schema transformer."""
    config = TransformationConfig(
        preserve_optional=preserve_optional,
        convert_types=convert_types,
        **kwargs
    )
    return OldSchemaTypeTransformer(config)


# Convenience function for direct transformation
def transform_legacy_dict_to_pydantic(model_dict: Dict[str, Any]) -> str:
    """Transform legacy dictionary model to Pydantic.
    
    Args:
        model_dict: Legacy model dictionary
        
    Returns:
        str: Generated Pydantic model code
    """
    transformer = create_schema_transformer()
    return transformer.transform_dict_model(model_dict)
