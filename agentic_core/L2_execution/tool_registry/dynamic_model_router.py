"""
⚛️ Dynamic Model Router - The Throttler

Complexity-based model selection to prevent "Enough Thinking" wall.
Analyzes AST complexity before healing and routes to appropriate model.

Mission: Stop "Retry Loop Death" by matching model power to task
Strategy: Right-Sized Intelligence for optimal token usage

Models:
- Gemini 2.5 Flash: Simple linting, syntax fixes (cheap, fast)
- Gemini 2.5 Flash (extended): Medium complexity refactoring
- Gemini 3.0 Deep Think: High-nesting refactoring, complex logic

Complexity-to-Budget Ratio ensures reasoning tokens never wasted on trivial tasks.
"""
import ast
import logging
import re
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Protocol

from agentic_core.L2_execution.tool_registry.base import SubAtomicAgent

logger = logging.getLogger(__name__)

class ModelTier(str, Enum):
    """Model tiers based on capability and cost."""
    FLASH_BASIC = "gemini-2.5-flash"  # 8K thinking budget, cheap
    FLASH_EXTENDED = "gemini-2.5-flash"  # 16K thinking budget, moderate
    DEEP_THINK = "gemini-3.0-deep-think"  # 24K+ thinking budget, expensive


@dataclass
class RoutingDecision:
    """Model routing decision with rationale."""
    model_tier: ModelTier
    thinking_budget: int
    temperature: float
    rationale: str
    estimated_tokens: int
    complexity_score: float


@dataclass
class ComplexityProfile:
    """Comprehensive complexity profile for routing."""
    file_path: str
    total_lines: int
    max_nesting: int
    function_count: int
    max_function_lines: int
    cyclomatic_complexity: int
    import_count: int
    class_count: int
    complexity_score: float  # 0-100


class DynamicModelRouter(SubAtomicAgent):
    """
    The Throttler - Dynamic Model Router
    
    Analyzes file complexity before healing and routes to appropriate model.
    Prevents "Enough Thinking" wall by matching model power to task complexity.
    
    Routing Strategy:
    - Complexity Score 0-30: Flash Basic (8K budget)
    - Complexity Score 31-60: Flash Extended (16K budget)
    - Complexity Score 61-100: Deep Think (24K budget)
    
    Factors:
    - File size (lines)
    - Nesting depth
    - Function complexity
    - Cyclomatic complexity
    - Import dependencies
    """
    
    def __init__(self, ctx):
        """
        Initialize Dynamic Model Router.
        
        Args:
            ctx: ValidationContext
        """
        super().__init__(ctx)
        # Initialize shared Sub-Atomic Engine components via dependency injection from ctx.
        # The ValidationContext is expected to provide these pre-initialized components.
        # If they are not present in ctx, they will be None, and a warning will be logged.
        
        self.engine = getattr(self.ctx, 'subatomic_engine', None)
        self.safety = getattr(self.ctx, 'safety_guardrail', None)
        self.fission = getattr(self.ctx, 'fission_manager', None)

        # Log a warning if any are missing, similar to the original try-except's intent.
        # The original code had a single try-except for all three.
        # If any of the three were not successfully initialized and provided by ctx,
        # we log a warning and ensure all related attributes are None to match original behavior.
        if not (self.engine and self.safety and self.fission):
            logger.warning("One or more Sub-Atomic Engine components (engine, safety, fission) "
                           "were not found in ValidationContext. DynamicModelRouter will operate without them.")
            self.engine = None
            self.safety = None
            self.fission = None
        
        # Routing thresholds
        self.BASIC_THRESHOLD = 30
        self.EXTENDED_THRESHOLD = 60
        
        # Budget allocation
        self.BUDGETS = {
            ModelTier.FLASH_BASIC: 8000,
            ModelTier.FLASH_EXTENDED: 16000,
            ModelTier.DEEP_THINK: 24576
        }
        
        # Temperature settings
        self.TEMPERATURES = {
            ModelTier.FLASH_BASIC: 0.1,  # Low for deterministic fixes
            ModelTier.FLASH_EXTENDED: 0.2,  # Moderate for refactoring
            ModelTier.DEEP_THINK: 0.3  # Higher for creative solutions
        }
    
    async def execute(self):
        """
        Execute model routing analysis.
        
        This is called before healing to determine optimal model.
        """
        logger.info("🎯 Dynamic Model Router: Analyzing complexity for routing...")
        
        # Analyze all files in context
        for file_path in self.ctx.python_files:
            profile = self._analyze_file_complexity(file_path)
            decision = self._route_to_model(profile)
            
            # Store routing decision in context
            if not hasattr(self.ctx, 'routing_decisions'):
                self.ctx.routing_decisions = {}
            
            self.ctx.routing_decisions[file_path] = decision
            
            logger.info(f"   {file_path}: {decision.model_tier.value} "
                       f"(complexity: {profile.complexity_score:.1f}, "
                       f"budget: {decision.thinking_budget})")
    
    def _analyze_file_complexity(self, file_path: str) -> ComplexityProfile:
        """
        Analyze file complexity for routing decision.
        
        Args:
            file_path: Path to file
            
        Returns:
            Complexity profile
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
        except Exception as e:
            logger.warning(f"Could not read {file_path}: {e}")
            return self._create_default_profile(file_path)
        
        try:
            tree = ast.parse(source)
        except SyntaxError:
            # Syntax errors need basic model for fixing
            return ComplexityProfile(
                file_path=file_path,
                total_lines=len(source.split('\n')),
                max_nesting=0,
                function_count=0,
                max_function_lines=0,
                cyclomatic_complexity=0,
                import_count=0,
                class_count=0,
                complexity_score=20.0  # Low score for syntax fixes
            )
        
        # Calculate metrics
        total_lines = len([l for l in source.split('\n') if l.strip()])
        max_nesting = self._calculate_max_nesting(tree)
        functions = self._extract_functions(tree)
        function_count = len(functions)
        max_function_lines = max([f['lines'] for f in functions.values()], default=0)
        cyclomatic_complexity = self._calculate_cyclomatic_complexity(tree)
        import_count = sum(1 for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom)))
        class_count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
        
        # Calculate complexity score (0-100)
        complexity_score = self._calculate_complexity_score(
            total_lines, max_nesting, max_function_lines,
            cyclomatic_complexity, function_count
        )
        
        return ComplexityProfile(
            file_path=file_path,
            total_lines=total_lines,
            max_nesting=max_nesting,
            function_count=function_count,
            max_function_lines=max_function_lines,
            cyclomatic_complexity=cyclomatic_complexity,
            import_count=import_count,
            class_count=class_count,
            complexity_score=complexity_score
        )
    
    def _calculate_max_nesting(self, tree: ast.AST) -> int:
        """Calculate maximum nesting depth."""
        max_depth = 0
        
        def visit(node, depth=0):
            nonlocal max_depth
            max_depth = max(max_depth, depth)
            
            if isinstance(node, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                depth += 1
            
            for child in ast.iter_child_nodes(node):
                visit(child, depth)
        
        visit(tree)
        return max_depth
    
    def _extract_functions(self, tree: ast.AST) -> Dict:
        """Extract function metadata."""
        functions = {}
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                lines = (node.end_lineno or node.lineno) - node.lineno + 1
                functions[node.name] = {'lines': lines}
        
        return functions
    
    def _calculate_cyclomatic_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return complexity
    
    def _calculate_complexity_score(self, total_lines: int, max_nesting: int,
                                   max_function_lines: int, cyclomatic: int,
                                   function_count: int) -> float:
        """
        Calculate overall complexity score (0-100).
        
        Weighted factors:
        - File size: 20%
        - Nesting depth: 30%
        - Function size: 25%
        - Cyclomatic complexity: 15%
        - Function count: 10%
        """
        # Normalize each factor to 0-100
        size_score = min(100, (total_lines / 500) * 100)
        nesting_score = min(100, (max_nesting / 5) * 100)
        function_size_score = min(100, (max_function_lines / 100) * 100)
        cyclomatic_score = min(100, (cyclomatic / 20) * 100)
        function_count_score = min(100, (function_count / 20) * 100)
        
        # Weighted average
        complexity_score = (
            size_score * 0.20 +
            nesting_score * 0.30 +
            function_size_score * 0.25 +
            cyclomatic_score * 0.15 +
            function_count_score * 0.10
        )
        
        return complexity_score
    
    def _route_to_model(self, profile: ComplexityProfile) -> RoutingDecision:
        """
        Route to appropriate model based on complexity.
        
        Args:
            profile: Complexity profile
            
        Returns:
            Routing decision
        """
        score = profile.complexity_score
        
        if score <= self.BASIC_THRESHOLD:
            # Simple file - use basic Flash
            model_tier = ModelTier.FLASH_BASIC
            rationale = f"Low complexity ({score:.1f}/100) - simple linting/syntax fixes"
            
        elif score <= self.EXTENDED_THRESHOLD:
            # Medium complexity - use extended Flash
            model_tier = ModelTier.FLASH_EXTENDED
            rationale = f"Medium complexity ({score:.1f}/100) - refactoring needed"
        else:
            # High complexity - use Deep Think
            model_tier = ModelTier.DEEP_THINK
            rationale = f"High complexity ({score:.1f}/100) - deep reasoning required"
        
        # Get budget and temperature
        thinking_budget = self.BUDGETS[model_tier]
        temperature = self.TEMPERATURES[model_tier]
        
        # Estimate token usage (rough heuristic)
        estimated_tokens = int(profile.total_lines * 10 * (score / 100))
        
        return RoutingDecision(
            model_tier=model_tier,
            thinking_budget=thinking_budget,
            temperature=temperature,
            rationale=rationale,
            estimated_tokens=estimated_tokens,
            complexity_score=score
        )
    
    def _create_default_profile(self, file_path: str) -> ComplexityProfile:
        """Create default profile for unreadable files."""
        return ComplexityProfile(
            file_path=file_path,
            total_lines=0,
            max_nesting=0,
            function_count=0,
            max_function_lines=0,
            cyclomatic_complexity=0,
            import_count=0,
            class_count=0,
            complexity_score=30.0  # Medium default
        )
    
    def get_routing_for_file(self, file_path: str) -> Optional[RoutingDecision]:
        """
        Get routing decision for a specific file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Routing decision or None
        """
        if not hasattr(self.ctx, 'routing_decisions'):
            return None
        
        return self.ctx.routing_decisions.get(file_path)
    
    def generate_routing_report(self) -> str:
        """Generate routing report for all files."""
        if not hasattr(self.ctx, 'routing_decisions'):
            return "No routing decisions available"
        
        decisions = self.ctx.routing_decisions
        
        # Group by model tier
        by_tier = {
            ModelTier.FLASH_BASIC: [],
            ModelTier.FLASH_EXTENDED: [],
            ModelTier.DEEP_THINK: []
        }
        
        for file_path, decision in decisions.items():
            by_tier[decision.model_tier].append((file_path, decision))
        
        # Generate report
        lines = [
            "🎯 DYNAMIC MODEL ROUTING REPORT",
            "=" * 80,
            f"Total Files: {len(decisions)}",
            f"  Flash Basic: {len(by_tier[ModelTier.FLASH_BASIC])} files",
            f"  Flash Extended: {len(by_tier[ModelTier.FLASH_EXTENDED])} files",
            f"  Deep Think: {len(by_tier[ModelTier.DEEP_THINK])} files",
            "",
            "Estimated Token Usage:",
            f"  Flash Basic: {sum(d.estimated_tokens for _, d in by_tier[ModelTier.FLASH_BASIC])} tokens",
            f"  Flash Extended: {sum(d.estimated_tokens for _, d in by_tier[ModelTier.FLASH_EXTENDED])} tokens",
            f"  Deep Think: {sum(d.estimated_tokens for _, d in by_tier[ModelTier.DEEP_THINK])} tokens",
            "",
            "=" * 80
        ]
        
        return "\n".join(lines)


# Singleton instance
_model_router = None

def get_model_router(ctx) -> DynamicModelRouter:
    """Get or create global Model Router instance."""
    global _model_router
    if _model_router is None:
        _model_router = DynamicModelRouter(ctx)
    return _model_router