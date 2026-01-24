#!/usr/bin/env python3
"""
AST-Based Sovereign Structural Audit for apps_rg/
Classifies files into: engines, tools, types, legacy
"""

import ast
import json
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple


@dataclass
class FileAnalysis:
    """Analysis result for a single Python file."""
    path: str
    has_classes: bool = False
    class_names: List[str] = field(default_factory=list)
    has_stateful_methods: bool = False
    stateful_methods: List[str] = field(default_factory=list)
    has_standalone_functions: bool = False
    function_names: List[str] = field(default_factory=list)
    inherits_from: List[str] = field(default_factory=list)
    is_enum: bool = False
    is_basemodel: bool = False
    is_typeddict: bool = False
    is_dataclass: bool = False
    has_only_static_class_methods: bool = False
    is_legacy: bool = False
    legacy_reason: str = ""
    imports: List[str] = field(default_factory=list)
    imported_by: List[str] = field(default_factory=list)
    classification: str = "unknown"
    classification_reason: str = ""


STATEFUL_METHOD_NAMES = {
    'execute', 'process', 'run', 'heal', 'heal_repository',
    'analyze', 'generate', 'orchestrate', 'dispatch', 'invoke',
    'evaluate', 'validate', 'transform', 'compute', 'build',
    '__call__', 'step', 'act', 'decide', 'reason', 'plan'
}

LEGACY_PATTERNS = [
    r'_old', r'_v1', r'_backup', r'_tmp', r'_deprecated',
    r'backup', r'legacy', r'archive', r'test_'
]

PASSIVE_TYPE_BASES = {'Enum', 'IntEnum', 'StrEnum', 'BaseModel', 'TypedDict'}


def analyze_file(filepath: Path) -> Optional[FileAnalysis]:
    """Perform AST analysis on a single Python file."""
    try:
        content = filepath.read_text(encoding='utf-8')
        tree = ast.parse(content)
    except (SyntaxError, UnicodeDecodeError) as e:
        return FileAnalysis(
            path=str(filepath),
            classification="error",
            classification_reason=f"Parse error: {e}"
        )
    
    analysis = FileAnalysis(path=str(filepath))
    
    # Check for legacy patterns in filename
    filename = filepath.stem.lower()
    for pattern in LEGACY_PATTERNS:
        if re.search(pattern, filename, re.IGNORECASE):
            analysis.is_legacy = True
            analysis.legacy_reason = f"Filename matches legacy pattern: {pattern}"
            break
    
    # Collect imports
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                analysis.imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                analysis.imports.append(node.module)
    
    # Analyze top-level definitions
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            analysis.has_classes = True
            analysis.class_names.append(node.name)
            
            # Check inheritance
            for base in node.bases:
                base_name = ""
                if isinstance(base, ast.Name):
                    base_name = base.id
                elif isinstance(base, ast.Attribute):
                    base_name = base.attr
                
                if base_name:
                    analysis.inherits_from.append(base_name)
                    if base_name in PASSIVE_TYPE_BASES:
                        if base_name == 'Enum' or base_name.endswith('Enum'):
                            analysis.is_enum = True
                        elif base_name == 'BaseModel':
                            analysis.is_basemodel = True
                        elif base_name == 'TypedDict':
                            analysis.is_typeddict = True
            
            # Check for dataclass decorator
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Name) and decorator.id == 'dataclass':
                    analysis.is_dataclass = True
                elif isinstance(decorator, ast.Call):
                    if isinstance(decorator.func, ast.Name) and decorator.func.id == 'dataclass':
                        analysis.is_dataclass = True
            
            # Analyze methods
            static_only = True
            for item in node.body:
                if isinstance(item, ast.FunctionDef) or isinstance(item, ast.AsyncFunctionDef):
                    method_name = item.name
                    
                    # Check if static/class method
                    is_static = any(
                        isinstance(d, ast.Name) and d.id in ('staticmethod', 'classmethod')
                        for d in item.decorator_list
                    )
                    
                    if not is_static and not method_name.startswith('_'):
                        static_only = False
                    
                    # Check for stateful methods
                    if method_name in STATEFUL_METHOD_NAMES or method_name.startswith('execute'):
                        analysis.has_stateful_methods = True
                        analysis.stateful_methods.append(method_name)
            
            if static_only and analysis.has_classes:
                analysis.has_only_static_class_methods = True
        
        elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            analysis.has_standalone_functions = True
            analysis.function_names.append(node.name)
    
    # Classification logic
    analysis = classify_file(analysis)
    
    return analysis


def classify_file(analysis: FileAnalysis) -> FileAnalysis:
    """Classify file based on AST analysis results."""
    
    # Priority 1: Legacy files
    if analysis.is_legacy:
        analysis.classification = "legacy"
        analysis.classification_reason = analysis.legacy_reason
        return analysis
    
    # Priority 2: Passive data types (Enum, BaseModel, TypedDict)
    if analysis.is_enum or analysis.is_basemodel or analysis.is_typeddict:
        analysis.classification = "types"
        type_kind = "Enum" if analysis.is_enum else ("BaseModel" if analysis.is_basemodel else "TypedDict")
        analysis.classification_reason = f"Inherits from {type_kind} - passive data type"
        return analysis
    
    # Priority 3: True Sovereign Agents (Classes with stateful methods)
    if analysis.has_classes and analysis.has_stateful_methods:
        analysis.classification = "engine"
        analysis.classification_reason = f"Class with stateful methods: {', '.join(analysis.stateful_methods[:3])}"
        return analysis
    
    # Priority 4: Stateless tools (only standalone functions OR only static methods)
    if analysis.has_standalone_functions and not analysis.has_classes:
        analysis.classification = "tool"
        analysis.classification_reason = "Contains only standalone functions (no classes)"
        return analysis
    
    if analysis.has_classes and analysis.has_only_static_class_methods:
        analysis.classification = "tool"
        analysis.classification_reason = "Class contains only @staticmethod/@classmethod"
        return analysis
    
    # Priority 5: Classes without stateful methods - likely tools or configs
    if analysis.has_classes and not analysis.has_stateful_methods:
        # Check if it's a config/constants class
        if any('config' in c.lower() for c in analysis.class_names):
            analysis.classification = "tool"
            analysis.classification_reason = "Configuration class without stateful methods"
        elif analysis.is_dataclass:
            analysis.classification = "types"
            analysis.classification_reason = "Dataclass - passive data structure"
        else:
            analysis.classification = "unknown"
            analysis.classification_reason = "Class without recognized stateful methods"
        return analysis
    
    # Default: unknown
    analysis.classification = "unknown"
    analysis.classification_reason = "Could not determine classification"
    return analysis


def analyze_dependencies(analyses: List[FileAnalysis], base_dir: Path) -> Dict[str, List[str]]:
    """Analyze which files import which other files."""
    # Build a map of module names to file paths
    module_map = {}
    for a in analyses:
        p = Path(a.path)
        # apps_rg.engines.SomeAgent -> SomeAgent
        module_name = p.stem
        module_map[module_name] = a.path
        # Also map full module path
        rel_path = p.relative_to(base_dir.parent.parent)
        full_module = str(rel_path.with_suffix('')).replace('\\', '.').replace('/', '.')
        module_map[full_module] = a.path
    
    # Now check imports
    dependency_map = {a.path: [] for a in analyses}
    
    for a in analyses:
        for imp in a.imports:
            # Check if this import refers to another file in apps_rg
            parts = imp.split('.')
            for i in range(len(parts), 0, -1):
                partial = '.'.join(parts[:i])
                if partial in module_map and module_map[partial] != a.path:
                    dependency_map[module_map[partial]].append(a.path)
                    break
                # Also check just the last part (module name)
                if parts[-1] in module_map and module_map[parts[-1]] != a.path:
                    dependency_map[module_map[parts[-1]]].append(a.path)
                    break
    
    return dependency_map


def check_external_imports(analyses: List[FileAnalysis]) -> List[Tuple[str, str]]:
    """Find imports from apps_lic or other domains (namespace violations)."""
    violations = []
    for a in analyses:
        for imp in a.imports:
            if 'apps_lic' in imp:
                violations.append((a.path, imp))
    return violations


def main():
    """Main audit function."""
    apps_rg_dir = Path(r"c:\Git\Agentic-Workflow\apps_rg")
    engines_dir = apps_rg_dir / "engines"
    
    # Find all Python files
    py_files = list(engines_dir.glob("*.py"))
    print(f"Found {len(py_files)} Python files in apps_rg/engines/")
    
    # Analyze each file
    analyses = []
    for pf in py_files:
        if pf.name == "__init__.py":
            continue
        result = analyze_file(pf)
        if result:
            analyses.append(result)
    
    # Analyze dependencies
    dep_map = analyze_dependencies(analyses, engines_dir)
    for a in analyses:
        a.imported_by = dep_map.get(a.path, [])
    
    # Check for external imports (namespace violations)
    external_violations = check_external_imports(analyses)
    
    # Classify results
    engines = []
    tools = []
    types_files = []
    legacy = []
    unknown = []
    
    for a in analyses:
        rel_path = str(Path(a.path).relative_to(apps_rg_dir.parent))
        if a.classification == "engine":
            engines.append(rel_path)
        elif a.classification == "tool":
            tools.append(rel_path)
        elif a.classification == "types":
            types_files.append(rel_path)
        elif a.classification == "legacy":
            legacy.append(rel_path)
        else:
            unknown.append(rel_path)
    
    # Generate manifest
    manifest = {
        "engines": sorted(engines),
        "tools_to_migrate": sorted(tools),
        "types_to_rename": {t: Path(t).stem.replace('Agent', '') + "_types.py" for t in types_files},
        "legacy_archive": sorted(legacy),
        "unknown_require_review": sorted(unknown)
    }
    
    manifest_path = apps_rg_dir / "RG_AUDIT_MANIFEST.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    print(f"\nGenerated: {manifest_path}")
    
    # Print summary
    print(f"\n=== CLASSIFICATION SUMMARY ===")
    print(f"True Engines (Sovereign Agents): {len(engines)}")
    print(f"Tools (Stateless Utils): {len(tools)}")
    print(f"Types (Passive Data): {len(types_files)}")
    print(f"Legacy (Archive): {len(legacy)}")
    print(f"Unknown (Review Required): {len(unknown)}")
    
    # Print detailed analysis for report generation
    print("\n=== DETAILED ANALYSIS ===")
    for a in sorted(analyses, key=lambda x: x.classification):
        print(f"\n{Path(a.path).name}:")
        print(f"  Classification: {a.classification}")
        print(f"  Reason: {a.classification_reason}")
        if a.class_names:
            print(f"  Classes: {', '.join(a.class_names)}")
        if a.stateful_methods:
            print(f"  Stateful Methods: {', '.join(a.stateful_methods)}")
        if a.function_names:
            print(f"  Functions: {', '.join(a.function_names[:5])}")
        if a.inherits_from:
            print(f"  Inherits: {', '.join(a.inherits_from)}")
        dep_count = len(a.imported_by)
        print(f"  Dependency Count: {dep_count}")
        if dep_count > 0:
            print(f"  Imported By: {', '.join([Path(p).name for p in a.imported_by[:5]])}")
    
    # Save full analysis for report generation
    full_analysis = {
        "summary": {
            "total_files": len(analyses),
            "engines": len(engines),
            "tools": len(tools),
            "types": len(types_files),
            "legacy": len(legacy),
            "unknown": len(unknown),
            "sovereign_alignment_score": round(len(engines) / len(analyses) * 100, 1) if analyses else 0
        },
        "external_violations": [{"file": v[0], "import": v[1]} for v in external_violations],
        "files": [
            {
                "path": a.path,
                "relative_path": str(Path(a.path).relative_to(apps_rg_dir.parent)),
                "classification": a.classification,
                "reason": a.classification_reason,
                "classes": a.class_names,
                "stateful_methods": a.stateful_methods,
                "functions": a.function_names,
                "inherits_from": a.inherits_from,
                "dependency_count": len(a.imported_by),
                "imported_by": [str(Path(p).relative_to(apps_rg_dir.parent)) for p in a.imported_by],
                "imports": a.imports
            }
            for a in analyses
        ]
    }
    
    analysis_path = apps_rg_dir / "RG_AUDIT_FULL_ANALYSIS.json"
    with open(analysis_path, 'w') as f:
        json.dump(full_analysis, f, indent=2)
    print(f"\nGenerated: {analysis_path}")


if __name__ == "__main__":
    main()
