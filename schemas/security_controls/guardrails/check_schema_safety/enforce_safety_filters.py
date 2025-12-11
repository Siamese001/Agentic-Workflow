"""Schema Safety Filters Enforcement - Enforces safety filters on schema operations.

This module provides safety filter enforcement for schema operations,
including schema validation, content filtering, and security controls.
Follows the functional component pattern with proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Set, Pattern
import logging
import re
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class SchemaFilterType(Enum):
    """Types of schema safety filters."""
    FIELD_NAME_FILTER = "field_name_filter"
    DATA_TYPE_FILTER = "data_type_filter"
    CONSTRAINT_FILTER = "constraint_filter"
    SENSITIVE_DATA_FILTER = "sensitive_data_filter"
    VALIDATION_FILTER = "validation_filter"


class FilterAction(Enum):
    """Actions to take when filter is triggered."""
    BLOCK = "block"
    WARN = "warn"
    REDACT = "redact"
    FLAG = "flag"
    LOG = "log"


@dataclass
class SchemaSafetyFilter:
    """Definition of a schema safety filter."""
    id: str
    name: str
    filter_type: SchemaFilterType
    patterns: List[str]
    action: FilterAction
    enabled: bool = True
    severity: str = "medium"
    description: str = ""
    keywords: List[str] = field(default_factory=list)


@dataclass
class SchemaFilterMatch:
    """Record of a schema filter match."""
    filter_id: str
    filter_name: str
    filter_type: SchemaFilterType
    action: FilterAction
    matched_content: str
    field_name: Optional[str] = None
    confidence: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SchemaFilterResult:
    """Result of schema safety filtering."""
    safe: bool
    filtered_schema: Optional[Dict[str, Any]] = None
    matches: List[SchemaFilterMatch] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    blocked_fields: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SchemaSafetyFiltersConfig:
    """Configuration for schema safety filters enforcement."""
    enabled_filters: List[SchemaFilterType] = field(default_factory=lambda: [
        SchemaFilterType.FIELD_NAME_FILTER, SchemaFilterType.SENSITIVE_DATA_FILTER
    ])
    default_action: FilterAction = FilterAction.WARN
    strict_mode: bool = False
    auto_redact: bool = True
    custom_filters: List[SchemaSafetyFilter] = field(default_factory=list)
    allowed_domains: Set[str] = field(default_factory=set)
    log_level: str = "INFO"


class SchemaSafetyFiltersEnforcer:
    """Main class for schema safety filters enforcement."""

    def __init__(self, config: Optional[SchemaSafetyFiltersConfig] = None):
        self.config = config or SchemaSafetyFiltersConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.config.log_level)
        self._filters = []
        self._compiled_patterns = {}
        self._load_default_filters()

    def enforce_filters(self, schema: Dict[str, Any]) -> SchemaFilterResult:
        """Enforce safety filters on schema.
        
        Args:
            schema: Schema to filter
            
        Returns:
            SchemaFilterResult: Filter enforcement results
        """
        self.logger.info(f"Enforcing safety filters on schema")
        
        matches = []
        warnings = []
        blocked_fields = []
        filtered_schema = schema.copy()
        
        try:
            # Extract fields from schema
            fields = self._extract_fields(schema)
            
            # Apply each enabled filter
            for filter_type in self.config.enabled_filters:
                type_filters = [f for f in self._filters if f.filter_type == filter_type and f.enabled]
                
                for safety_filter in type_filters:
                    filter_matches = self._apply_filter(safety_filter, schema, fields)
                    matches.extend(filter_matches)
            
            # Apply custom filters
            for safety_filter in self.config.custom_filters:
                if safety_filter.enabled:
                    filter_matches = self._apply_filter(safety_filter, schema, fields)
                    matches.extend(filter_matches)
            
            # Process matches based on actions
            for match in matches:
                if match.action == FilterAction.BLOCK and match.field_name:
                    blocked_fields.append(match.field_name)
                    # Remove blocked field from schema
                    filtered_schema = self._remove_field_from_schema(filtered_schema, match.field_name)
                elif match.action == FilterAction.WARN:
                    warnings.append(f"Warning: {match.filter_name} detected in field {match.field_name}")
                elif match.action == FilterAction.REDACT and self.config.auto_redact and match.field_name:
                    filtered_schema = self._redact_field_in_schema(filtered_schema, match.field_name)
            
            # Determine if schema is safe
            safe = not any(m.action == FilterAction.BLOCK for m in matches)
            
            result = SchemaFilterResult(
                safe=safe,
                filtered_schema=filtered_schema if filtered_schema != schema else None,
                matches=matches,
                warnings=warnings,
                blocked_fields=blocked_fields,
                metadata={
                    "filtered_at": datetime.utcnow().isoformat(),
                    "total_fields": len(fields),
                    "filters_applied": len(self._filters) + len(self.config.custom_filters),
                    "enforcer": "SchemaSafetyFiltersEnforcer"
                }
            )
            
            self.logger.info(
                f"Schema filter enforcement completed: {'safe' if safe else 'unsafe'} "
                f"({len(matches)} matches, {len(blocked_fields)} blocked)"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Schema filter enforcement failed: {str(e)}")
            return SchemaFilterResult(
                safe=False,
                matches=[SchemaFilterMatch(
                    filter_id="system_error",
                    filter_name="System Error",
                    filter_type=SchemaFilterType.FIELD_NAME_FILTER,
                    action=FilterAction.BLOCK,
                    matched_content=str(e),
                    confidence=1.0
                )],
                metadata={"error": str(e)}
            )

    def _apply_filter(self, safety_filter: SchemaSafetyFilter, schema: Dict[str, Any], fields: List[Dict[str, Any]]) -> List[SchemaFilterMatch]:
        """Apply a single safety filter to schema."""
        matches = []
        
        try:
            # Get compiled patterns for this filter
            patterns = self._compiled_patterns.get(safety_filter.id, [])
            
            # Check each field
            for field in fields:
                field_name = field.get("name", "")
                field_description = field.get("description", "")
                
                # Check field name patterns
                for pattern in patterns:
                    if pattern.search(field_name):
                        matches.append(SchemaFilterMatch(
                            filter_id=safety_filter.id,
                            filter_name=safety_filter.name,
                            filter_type=safety_filter.filter_type,
                            action=safety_filter.action,
                            matched_content=field_name,
                            field_name=field_name,
                            confidence=0.9
                        ))
                
                # Check field description patterns
                for pattern in patterns:
                    if field_description and pattern.search(field_description):
                        matches.append(SchemaFilterMatch(
                            filter_id=safety_filter.id,
                            filter_name=safety_filter.name,
                            filter_type=safety_filter.filter_type,
                            action=safety_filter.action,
                            matched_content=field_description[:100],
                            field_name=field_name,
                            confidence=0.8
                        ))
                
                # Check keywords
                for keyword in safety_filter.keywords:
                    if keyword.lower() in field_name.lower():
                        matches.append(SchemaFilterMatch(
                            filter_id=safety_filter.id,
                            filter_name=safety_filter.name,
                            filter_type=safety_filter.filter_type,
                            action=safety_filter.action,
                            matched_content=keyword,
                            field_name=field_name,
                            confidence=0.8
                        ))
            
        except Exception as e:
            self.logger.warning(f"Filter {safety_filter.id} failed: {str(e)}")
        
        return matches

    def _extract_fields(self, schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract field definitions from schema."""
        fields = []
        
        # Handle different schema formats
        if "properties" in schema:
            # JSON Schema format
            for field_name, field_def in schema["properties"].items():
                fields.append({
                    "name": field_name,
                    "type": field_def.get("type", "unknown"),
                    "description": field_def.get("description", ""),
                    "enum": field_def.get("enum", []),
                    "required": field_name in schema.get("required", [])
                })
        
        elif "fields" in schema:
            # Custom schema format
            for field_def in schema["fields"]:
                fields.append(field_def)
        
        elif isinstance(schema, dict):
            # Simple key-value format
            for key, value in schema.items():
                if isinstance(value, dict):
                    fields.append({
                        "name": key,
                        "type": value.get("type", "unknown"),
                        "description": value.get("description", ""),
                        "enum": value.get("enum", []),
                        "required": value.get("required", False)
                    })
        
        return fields

    def _remove_field_from_schema(self, schema: Dict[str, Any], field_name: str) -> Dict[str, Any]:
        """Remove a field from schema."""
        filtered_schema = schema.copy()
        
        if "properties" in filtered_schema:
            if field_name in filtered_schema["properties"]:
                del filtered_schema["properties"][field_name]
                # Remove from required list if present
                if "required" in filtered_schema and field_name in filtered_schema["required"]:
                    filtered_schema["required"].remove(field_name)
        
        elif "fields" in filtered_schema:
            filtered_schema["fields"] = [f for f in filtered_schema["fields"] if f.get("name") != field_name]
        
        elif field_name in filtered_schema:
            del filtered_schema[field_name]
        
        return filtered_schema

    def _redact_field_in_schema(self, schema: Dict[str, Any], field_name: str) -> Dict[str, Any]:
        """Redact a field in schema."""
        filtered_schema = schema.copy()
        
        if "properties" in filtered_schema:
            if field_name in filtered_schema["properties"]:
                filtered_schema["properties"][field_name]["description"] = "[REDACTED]"
                # Clear enum values if present
                if "enum" in filtered_schema["properties"][field_name]:
                    filtered_schema["properties"][field_name]["enum"] = []
        
        elif "fields" in filtered_schema:
            for field in filtered_schema["fields"]:
                if field.get("name") == field_name:
                    field["description"] = "[REDACTED]"
                    if "enum" in field:
                        field["enum"] = []
        
        elif field_name in filtered_schema and isinstance(filtered_schema[field_name], dict):
            filtered_schema[field_name]["description"] = "[REDACTED]"
        
        return filtered_schema

    def _load_default_filters(self) -> None:
        """Load default safety filters."""
        # Field name filter
        field_name_filter = SchemaSafetyFilter(
            id="field_name_filter",
            name="Field Name Filter",
            filter_type=SchemaFilterType.FIELD_NAME_FILTER,
            patterns=[
                r'.*password.*',
                r'.*secret.*',
                r'.*token.*',
                r'.*key.*',
                r'.*credential.*'
            ],
            action=FilterAction.WARN,
            severity="high",
            description="Filters sensitive field names"
        )
        self._filters.append(field_name_filter)
        
        # Sensitive data filter
        sensitive_data_filter = SchemaSafetyFilter(
            id="sensitive_data_filter",
            name="Sensitive Data Filter",
            filter_type=SchemaFilterType.SENSITIVE_DATA_FILTER,
            patterns=[
                r'.*ssn.*',
                r'.*social_security.*',
                r'.*credit_card.*',
                r'.*bank_account.*',
                r'.*personal_info.*'
            ],
            action=FilterAction.REDACT,
            severity="critical",
            description="Filters and redacts sensitive data fields"
        )
        self._filters.append(sensitive_data_filter)
        
        # Data type filter
        data_type_filter = SchemaSafetyFilter(
            id="data_type_filter",
            name="Data Type Filter",
            filter_type=SchemaFilterType.DATA_TYPE_FILTER,
            patterns=[],
            keywords=["binary", "blob", "raw", "executable"],
            action=FilterAction.FLAG,
            severity="medium",
            description="Flags potentially unsafe data types"
        )
        self._filters.append(data_type_filter)
        
        # Constraint filter
        constraint_filter = SchemaSafetyFilter(
            id="constraint_filter",
            name="Constraint Filter",
            filter_type=SchemaFilterType.CONSTRAINT_FILTER,
            patterns=[],
            keywords=["unlimited", "infinite", "no_limit"],
            action=FilterAction.WARN,
            severity="medium",
            description="Warnings for unconstrained fields"
        )
        self._filters.append(constraint_filter)
        
        # Compile all patterns
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Compile regex patterns for all filters."""
        for safety_filter in self._filters:
            compiled = []
            for pattern in safety_filter.patterns:
                try:
                    compiled.append(re.compile(pattern, re.IGNORECASE))
                except re.error as e:
                    self.logger.warning(f"Invalid regex pattern in {safety_filter.id}: {str(e)}")
            self._compiled_patterns[safety_filter.id] = compiled

    def add_filter(self, safety_filter: SchemaSafetyFilter) -> None:
        """Add a custom safety filter.
        
        Args:
            safety_filter: Filter to add
        """
        self.logger.info(f"Adding safety filter: {safety_filter.id}")
        self.config.custom_filters.append(safety_filter)
        
        # Compile patterns for new filter
        compiled = []
        for pattern in safety_filter.patterns:
            try:
                compiled.append(re.compile(pattern, re.IGNORECASE))
            except re.error as e:
                self.logger.warning(f"Invalid regex pattern in {safety_filter.id}: {str(e)}")
        self._compiled_patterns[safety_filter.id] = compiled

    def remove_filter(self, filter_id: str) -> bool:
        """Remove a safety filter.
        
        Args:
            filter_id: ID of filter to remove
            
        Returns:
            bool: True if filter was removed
        """
        # Remove from default filters
        original_length = len(self._filters)
        self._filters = [f for f in self._filters if f.id != filter_id]
        
        # Remove from custom filters
        self.config.custom_filters = [f for f in self.config.custom_filters if f.id != filter_id]
        
        # Remove compiled patterns
        if filter_id in self._compiled_patterns:
            del self._compiled_patterns[filter_id]
        
        return len(self._filters) < original_length

    def get_filter_summary(self) -> Dict[str, Any]:
        """Get summary of filter configuration.
        
        Returns:
            Dict: Filter configuration summary
        """
        return {
            "enabled_filters": [f.value for f in self.config.enabled_filters],
            "total_filters": len(self._filters) + len(self.config.custom_filters),
            "default_action": self.config.default_action.value,
            "strict_mode": self.config.strict_mode,
            "auto_redact": self.config.auto_redact
        }


# Factory function for easy instantiation
def create_schema_safety_filters_enforcer(
    enabled_filters: List[str] = None,
    default_action: str = "warn",
    strict_mode: bool = False,
    **kwargs
) -> SchemaSafetyFiltersEnforcer:
    """Create a configured schema safety filters enforcer."""
    config = SchemaSafetyFiltersConfig(
        enabled_filters=[SchemaFilterType(f) for f in (enabled_filters or ["field_name_filter", "sensitive_data_filter"])],
        default_action=FilterAction(default_action),
        strict_mode=strict_mode,
        **kwargs
    )
    return SchemaSafetyFiltersEnforcer(config)


# Convenience function for direct usage
def enforce_safety_filters(
    schema: Dict[str, Any],
    filters: List[str] = None,
    strict_mode: bool = False,
    auto_redact: bool = True,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Enforce safety filters on schema.
    
    Args:
        schema: Schema to filter
        filters: List of filter types to apply
        strict_mode: Whether to use strict mode
        auto_redact: Whether to automatically redact content
        config: Optional enforcer configuration
        
    Returns:
        Dict: Filter enforcement results
    """
    # Create enforcer and execute
    enforcer_config = SchemaSafetyFiltersConfig(
        enabled_filters=[SchemaFilterType(f) for f in (filters or ["field_name_filter", "sensitive_data_filter"])],
        strict_mode=strict_mode,
        auto_redact=auto_redact,
        **config or {}
    )
    enforcer = SchemaSafetyFiltersEnforcer(enforcer_config)
    result = enforcer.enforce_filters(schema)
    
    # Convert result to dict for JSON serialization
    return {
        "safe": result.safe,
        "filtered_schema": result.filtered_schema,
        "matches": [
            {
                "filter_id": m.filter_id,
                "filter_name": m.filter_name,
                "filter_type": m.filter_type.value,
                "action": m.action.value,
                "matched_content": m.matched_content,
                "field_name": m.field_name,
                "confidence": m.confidence,
                "timestamp": m.timestamp.isoformat()
            }
            for m in result.matches
        ],
        "warnings": result.warnings,
        "blocked_fields": result.blocked_fields,
        "metadata": result.metadata
    }
