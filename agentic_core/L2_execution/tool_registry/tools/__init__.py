"""
Tools Package — Code Transformation and Analysis Tools

Phase 1: Code Transformation Engine (CTE)
- Deterministic AST-based code transformations
- Rename, extract, decorator operations
- No LLM overhead for simple fixes

Phase 2: Dependency Graph Analyzer (DGA) + Diff/Patch Generator (DPG)
- Import/call graph analysis
- Cycle detection, impact analysis
- Reviewable diff generation
"""

from AgenticCore.L2_execution.ToolRegistry.tools.code_transform import (
    CodeTransformArgs,
    TransformOperation,
    TransformResult,
    code_transform,
    rename_symbol,
    extract_function,
    add_decorator,
    remove_decorator,
    quick_rename,
    quick_extract,
)

from AgenticCore.L2_execution.ToolRegistry.tools.DependencyGraph import (
    DependencyGraphArgs,
    GraphOperation,
    DependencyGraph,
    GraphResult,
    DependencyGraph,
    build_graph,
    detect_cycles,
    ImpactAnalysis,
    find_unused_imports,
    quick_cycles,
    quick_impact,
    quick_unused,
)

from AgenticCore.L2_execution.ToolRegistry.tools.diff_generator import (
    DiffGeneratorArgs,
    DiffFormat,
    DiffResult,
    PatchResult,
    generate_diff,
    generate_unified_diff,
    generate_html_diff,
    apply_patch,
    validate_patch,
    quick_diff,
    quick_html_diff,
    diff_stats,
)

__all__ = [
    # CTE exports
    "CodeTransformArgs",
    "TransformOperation",
    "TransformResult",
    "code_transform",
    "rename_symbol",
    "extract_function",
    "add_decorator",
    "remove_decorator",
    "quick_rename",
    "quick_extract",
    # DGA exports
    "DependencyGraphArgs",
    "GraphOperation",
    "DependencyGraph",
    "GraphResult",
    "DependencyGraph",
    "build_graph",
    "detect_cycles",
    "ImpactAnalysis",
    "find_unused_imports",
    "quick_cycles",
    "quick_impact",
    "quick_unused",
    # DPG exports
    "DiffGeneratorArgs",
    "DiffFormat",
    "DiffResult",
    "PatchResult",
    "generate_diff",
    "generate_unified_diff",
    "generate_html_diff",
    "apply_patch",
    "validate_patch",
    "quick_diff",
    "quick_html_diff",
    "diff_stats",
]
