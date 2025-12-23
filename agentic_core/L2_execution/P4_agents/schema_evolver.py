"""
⚛️ Schema Evolver - The Structural Guard

Monitors Pydantic models and database schemas to prevent Schema Drift.
Runs forward-propagation checks when SystemArchitect proposes structural changes.

Mission: Eliminate "Breaking Change" bottleneck in multi-stage pipelines
Strategy: Automated data contract management with transformation mappings

Prevents: Type Sprawl, Schema Drift, Breaking Changes between HOP stages
Enables: Independent stage deployment with consistent data contracts
"""
from typing import Any, Optional, Protocol, Dict, List
import re


import ast
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set

from agentic_core.base import SubAtomicAgent

logger = logging.getLogger(__name__)


@dataclass
class SchemaDefinition:
    """Represents a Pydantic model or database schema."""
    name: str
    file_path: str
    fields: Dict[str, str]  # field_name: type_annotation
    base_classes: List[str]
    line_number: int
    is_pydantic: bool


@dataclass
class SchemaChange:
    """Represents a proposed schema change."""
    schema_name: str
    change_type: str  # "add_field", "remove_field", "modify_field", "rename_field"
    field_name: str
    old_value: Optional[str]
    new_value: Optional[str]
    file_path: str


@dataclass
class ImpactAnalysis:
    """Analysis of schema change impact."""
    change: SchemaChange
    affected_files: List[str]
    breaking_change: bool
    severity: str  # "low", "medium", "high", "critical"
    transformation_mapping: Optional[str]
    recommendations: List[str]


@dataclass
class SchemaRegistry:
    """Registry of all schemas in the codebase."""
    schemas: Dict[str, SchemaDefinition] = field(default_factory=dict)
    dependencies: Dict[str, Set[str]] = field(default_factory=dict)  # schema -> files using it
    reverse_deps: Dict[str, Set[str]] = field(default_factory=dict)  # file -> schemas used


class SchemaEvolver(SubAtomicAgent):
    """
    The Structural Guard - Schema Evolution Agent
    
    Monitors all Pydantic definitions and database schemas.
    Runs forward-propagation checks to prevent breaking changes.
    
    Capabilities:
    1. Schema Discovery - Find all Pydantic models and DB schemas
    2. Dependency Tracking - Map which files use which schemas
    3. Change Detection - Identify proposed schema modifications
    4. Impact Analysis - Forward-propagate changes to find breaks
    5. Transformation Mapping - Suggest migration strategies
    
    Integration:
    - Runs before SystemArchitect applies structural changes
    - Blocks breaking changes or suggests transformations
    - Maintains data contract consistency across HOP stages
    """
    
    def __init__(self, ctx):
        """
        Initialize Schema Evolver.
        
        Args:
            ctx: ValidationContext
        """
        super().__init__(ctx)
        self.registry = SchemaRegistry()
        self.schema_dirs = [
            "agentic_core/schemas",
            "agentic_core/domain",
            "apps_shared/schemas"
        ]
    
    async def execute(self):
        """
        Execute schema evolution monitoring.
        
        Discovers schemas, tracks dependencies, and analyzes changes.
        """
        logger.info("🛡️  Schema Evolver: Monitoring data contracts...")
        
        # Discover all schemas
        self._discover_schemas()
        
        # Track dependencies
        self._track_dependencies()
        
        # Check for pending changes
        if hasattr(self.ctx, 'pending_schema_changes'):
            for change in self.ctx.pending_schema_changes:
                impact = self._analyze_impact(change)
                self._report_impact(impact)
        
        logger.info(f"   Monitored {len(self.registry.schemas)} schemas")
        logger.info(f"   Tracked {sum(len(deps) for deps in self.registry.dependencies.values())} dependencies")
    
    def _discover_schemas(self):
        """Discover all Pydantic models and database schemas."""
        for schema_dir in self.schema_dirs:
            schema_path = Path(schema_dir)
            if not schema_path.exists():
                continue
            
            for py_file in schema_path.rglob("*.py"):
                self._scan_file_for_schemas(str(py_file))
    
    def _scan_file_for_schemas(self, file_path: str):
        """Scan a file for Pydantic model definitions."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
        except Exception as e:
            logger.warning(f"Could not read {file_path}: {e}")
            return
        
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if it's a Pydantic model
                is_pydantic = any(
                    base.id in ['BaseModel', 'BaseSettings'] if isinstance(base, ast.Name) else False
                    for base in node.bases
                )
                
                if is_pydantic or 'Schema' in node.name or 'Model' in node.name:
                    schema = self._extract_schema_definition(node, file_path, is_pydantic)
                    self.registry.schemas[schema.name] = schema
    
    def _extract_schema_definition(self, node: ast.ClassDef, file_path: str, is_pydantic: bool) -> SchemaDefinition:
        """Extract schema definition from AST node."""
        fields = {}
        
        for item in node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                # Extract field name and type
                field_name = item.target.id
                type_annotation = ast.unparse(item.annotation) if hasattr(ast, 'unparse') else str(item.annotation)
                fields[field_name] = type_annotation
        
        base_classes = [
            base.id if isinstance(base, ast.Name) else ast.unparse(base) if hasattr(ast, 'unparse') else str(base)
            for base in node.bases
        ]
        
        return SchemaDefinition(
            name=node.name,
            file_path=file_path,
            fields=fields,
            base_classes=base_classes,
            line_number=node.lineno,
            is_pydantic=is_pydantic
        )
    
    def _track_dependencies(self):
        """Track which files depend on which schemas."""
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    source = f.read()
            except Exception:
                continue
            
            try:
                tree = ast.parse(source)
            except SyntaxError:
                continue
            
            # Find schema usages
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    if node.id in self.registry.schemas:
                        # This file uses this schema
                        if node.id not in self.registry.dependencies:
                            self.registry.dependencies[node.id] = set()
                        self.registry.dependencies[node.id].add(file_path)
                        
                        if file_path not in self.registry.reverse_deps:
                            self.registry.reverse_deps[file_path] = set()
                        self.registry.reverse_deps[file_path].add(node.id)
    
    def _analyze_impact(self, change: SchemaChange) -> ImpactAnalysis:
        """
        Analyze impact of a schema change.
        
        Performs forward-propagation to find all affected files.
        """
        schema_name = change.schema_name
        affected_files = list(self.registry.dependencies.get(schema_name, set()))
        
        # Determine if breaking
        breaking_change = change.change_type in ['remove_field', 'modify_field']
        
        # Calculate severity
        if breaking_change and len(affected_files) > 10:
            severity = "critical"
        elif breaking_change and len(affected_files) > 5:
            severity = "high"
        elif breaking_change:
            severity = "medium"
        else:
            severity = "low"
        
        # Generate transformation mapping
        transformation_mapping = self._generate_transformation_mapping(change)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(change, affected_files)
        
        return ImpactAnalysis(
            change=change,
            affected_files=affected_files,
            breaking_change=breaking_change,
            severity=severity,
            transformation_mapping=transformation_mapping,
            recommendations=recommendations
        )
    
    def _generate_transformation_mapping(self, change: SchemaChange) -> Optional[str]:
        """Generate transformation mapping for schema change."""
        if change.change_type == "remove_field":
            return f"Migration: Remove all references to '{change.field_name}' or provide default value"
        
        elif change.change_type == "modify_field":
            return f"Migration: Convert '{change.field_name}' from {change.old_value} to {change.new_value}"
        
        elif change.change_type == "rename_field":
            return f"Migration: Rename '{change.old_value}' to '{change.new_value}' in all usages"
        
        elif change.change_type == "add_field":
            return f"Migration: Add '{change.field_name}' with default value or make optional"
        
        return None
    
    def _generate_recommendations(self, change: SchemaChange, affected_files: List[str]) -> List[str]:
        """Generate recommendations for handling schema change."""
        recommendations = []
        
        if change.change_type == "remove_field":
            recommendations.append(f"Consider deprecation period before removing '{change.field_name}'")
            recommendations.append(f"Add migration script to handle existing data")
            recommendations.append(f"Update {len(affected_files)} dependent files")
        
        elif change.change_type == "modify_field":
            recommendations.append(f"Ensure type compatibility: {change.old_value} → {change.new_value}")
            recommendations.append(f"Add validation for new type")
            recommendations.append(f"Test all {len(affected_files)} dependent files")
        
        elif change.change_type == "rename_field":
            recommendations.append(f"Use alias for backward compatibility")
            recommendations.append(f"Update {len(affected_files)} files in single commit")
        
        elif change.change_type == "add_field":
            recommendations.append(f"Make field optional or provide default")
            recommendations.append(f"Document new field in schema")
        
        return recommendations
    
    def _report_impact(self, impact: ImpactAnalysis):
        """Report impact analysis to user."""
        change = impact.change
        
        logger.info(f"\n{'='*80}")
        logger.info(f"🛡️  SCHEMA CHANGE IMPACT ANALYSIS")
        logger.info(f"{'='*80}")
        logger.info(f"Schema: {change.schema_name}")
        logger.info(f"Change: {change.change_type} - {change.field_name}")
        logger.info(f"File: {change.file_path}")
        logger.info(f"")
        logger.info(f"Impact:")
        logger.info(f"  Affected Files: {len(impact.affected_files)}")
        logger.info(f"  Breaking Change: {'YES' if impact.breaking_change else 'NO'}")
        logger.info(f"  Severity: {impact.severity.upper()}")
        
        if impact.breaking_change:
            logger.warning(f"\n[!]  BREAKING CHANGE DETECTED")
        
        if impact.transformation_mapping:
            logger.info(f"\nTransformation Mapping:")
            logger.info(f"  {impact.transformation_mapping}")
        
        if impact.recommendations:
            logger.info(f"\nRecommendations:")
            for i, rec in enumerate(impact.recommendations, 1):
                logger.info(f"  {i}. {rec}")
        
        if impact.affected_files:
            logger.info(f"\nAffected Files (showing first 10):")
            for file_path in impact.affected_files[:10]:
                logger.info(f"  - {file_path}")
            if len(impact.affected_files) > 10:
                logger.info(f"  ... and {len(impact.affected_files) - 10} more")
        
        logger.info(f"{'='*80}\n")
    
    def propose_schema_change(self, schema_name: str, change_type: str,
                            field_name: str, old_value: Optional[str] = None,
                            new_value: Optional[str] = None,
                            file_path: str = "") -> ImpactAnalysis:
        """
        Propose a schema change and get impact analysis.
        
        Args:
            schema_name: Name of schema to change
            change_type: Type of change
            field_name: Field being changed
            old_value: Old value (for modify/rename)
            new_value: New value (for modify/rename/add)
            file_path: File containing schema
            
        Returns:
            Impact analysis
        """
        change = SchemaChange(
            schema_name=schema_name,
            change_type=change_type,
            field_name=field_name,
            old_value=old_value,
            new_value=new_value,
            file_path=file_path
        )
        
        return self._analyze_impact(change)
    
    def get_schema_dependencies(self, schema_name: str) -> Set[str]:
        """Get all files that depend on a schema."""
        return self.registry.dependencies.get(schema_name, set())
    
    def get_file_schemas(self, file_path: str) -> Set[str]:
        """Get all schemas used by a file."""
        return self.registry.reverse_deps.get(file_path, set())
    
    def generate_drift_report(self) -> str:
        """Generate schema drift report."""
        lines = [
            "🛡️  SCHEMA DRIFT REPORT",
            "=" * 80,
            f"Total Schemas: {len(self.registry.schemas)}",
            f"Total Dependencies: {sum(len(deps) for deps in self.registry.dependencies.values())}",
            "",
            "Schema Usage:"
        ]
        
        # Sort schemas by usage count
        usage_counts = [(name, len(deps)) for name, deps in self.registry.dependencies.items()]
        usage_counts.sort(key=lambda x: x[1], reverse=True)
        
        for schema_name, count in usage_counts[:10]:
            lines.append(f"  {schema_name}: {count} files")
        
        if len(usage_counts) > 10:
            lines.append(f"  ... and {len(usage_counts) - 10} more schemas")
        
        lines.extend([
            "",
            "=" * 80
        ])
        
        return "\n".join(lines)


# Singleton instance
_schema_evolver = None

def get_schema_evolver(ctx) -> SchemaEvolver:
    """Get or create global Schema Evolver instance."""
    global _schema_evolver
    if _schema_evolver is None:
        _schema_evolver = SchemaEvolver(ctx)
    return _schema_evolver
