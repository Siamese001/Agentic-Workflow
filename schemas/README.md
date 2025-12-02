# Schema Structure Conventions

This document outlines the conventions used for schema definitions across all layers and phases.

## File Structure

- Each `.py` file contains only type definitions and data models
- No execution logic, business rules, or implementation code
- Files are organized by layer and phase following the directory structure

## Code Conventions

### Enums

- All enum values use snake_case strings
- Enum classes have descriptive docstrings
- Example: `class SafetyLevel(Enum): PERMISSIVE = "permissive"`

### Dataclasses

- All fields have proper type hints
- Optional fields use `Optional[Type]` annotation
- Default values provided where appropriate
- Example: `@dataclass class SchemaConfig: name: str; version: Optional[str] = None`

### Imports

- Standard imports: `from dataclasses import dataclass`
- Type imports: `from typing import Optional, Dict, Any, List, Union`
- Enum imports: `from enum import Enum`

### Field Types

- String fields: `str`
- Numeric fields: `int`, `float`
- Collections: `List[Type]`, `Dict[str, Type]`
- Optional fields: `Optional[Type]`
- Complex types: `Union[Type1, Type2]`

### Naming Patterns

- Classes use PascalCase
- Fields use snake_case
- Enum values use snake_case strings
- ID fields end with `_id` (e.g., `schema_id`, `task_id`)

### Validation

- All files compile without syntax errors
- Proper type annotations throughout
- Consistent structure across all files

## Layers Covered

- `mem-layer`: Memory-based schema operations
- `safe-layer`: Safety and policy enforcement
- `plan-layer`: Planning and orchestration operations
- `orc-layer`: Orchestration-level operations

## Phases Implemented

- `retrieve-phase`: Schema retrieval and context
- `safety-phase`: Safety validation and enforcement
- `plan-phase`: Planning and preparation
- `expand-phase`: Content expansion and embedding
- `refine-phase`: Result refinement and optimization
- `validate-phase`: Structure validation and compliance
- `act-phase`: Action execution and tool usage
- `inspect-phase`: Problem detection and diagnostics
- `agg-phase`: State aggregation and consolidation

This ensures consistent, maintainable schema definitions across the entire system.
