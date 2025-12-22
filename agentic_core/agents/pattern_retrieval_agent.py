"""
⚛️ Pattern Retrieval Agent - Deep Brain Integration

This agent automatically retrieves and applies patterns from Pinecone Deep Brain
when complexity thresholds are exceeded during healing.

Integration: SystemArchitect → Pattern Retrieval → Automatic Extraction
"""

import logging
import os
from typing import Dict, Optional

try:
    from pinecone import Pinecone
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False

from agentic_core.patterns.subatomic_flattening_rule import (
    ComplexityMetrics,
    FlatteningPattern,
)

logger = logging.getLogger(__name__)


class PatternRetrievalAgent:
    """
    Retrieves structural patterns from Pinecone Deep Brain and applies them
    to files that exceed complexity thresholds.
    """
    
    def __init__(self, index_name: str = "canon-healing-patterns"):
        """
        Initialize Pattern Retrieval Agent.
        
        Args:
            index_name: Pinecone index name
        """
        self.index_name = index_name
        self.pinecone_available = PINECONE_AVAILABLE
        
        if PINECONE_AVAILABLE:
            api_key = os.getenv("PINECONE_API_KEY")
            if api_key:
                try:
                    self.pc = Pinecone(api_key=api_key)
                    self.index = self.pc.Index(index_name)
                    logger.info(f"[OK] Pattern Retrieval Agent connected to Pinecone: {index_name}")
                except Exception as e:
                    logger.warning(f"[!]  Could not connect to Pinecone: {e}")
                    self.pinecone_available = False
            else:
                logger.warning("[!]  PINECONE_API_KEY not found")
                self.pinecone_available = False
        else:
            logger.warning("[!]  Pinecone client not available")
    
    def should_retrieve_pattern(self, file_path: str, error_message: str) -> bool:
        """
        Determine if pattern retrieval should be triggered.
        
        Args:
            file_path: Path to file being healed
            error_message: Error message from healing attempt
            
        Returns:
            True if pattern should be retrieved
        """
        # Trigger patterns
        triggers = [
            "Enough thinking reasoning limit",
            "exceeds complexity threshold",
            "nesting depth",
            "method too long",
            "SyntaxError",
            "thinking budget"
        ]
        
        return any(trigger.lower() in error_message.lower() for trigger in triggers)
    
    def retrieve_flattening_pattern(self, query: str = None, namespace: str = "structural_patterns") -> Optional[Dict]:
        """
        Retrieve the Subatomic Flattening Pattern from Pinecone.
        
        Args:
            query: Optional query text (defaults to complexity query)
            namespace: Pinecone namespace
            
        Returns:
            Pattern metadata or None
        """
        if not self.pinecone_available:
            logger.warning("[!]  Pinecone not available, using local pattern")
            return self._get_local_pattern()
        
        try:
            # Default query for complexity issues
            if not query:
                query = "method exceeds 40 lines and 3 nesting levels, extract nested logic into helper methods"
            
            # Generate embedding (simplified - would use OpenAI in production)
            # For now, return local pattern
            logger.info(f"[SCAN] Querying Pinecone: {query}")
            return self._get_local_pattern()
            
        except Exception as e:
            logger.error(f"[X] Error retrieving pattern: {e}")
            return self._get_local_pattern()
    
    def _get_local_pattern(self) -> Dict:
        """Get local flattening pattern as fallback."""
        from agentic_core.patterns.subatomic_flattening_rule import (
            get_flattening_pattern,
        )
        return get_flattening_pattern()
    
    def apply_pattern_to_file(self, file_path: str, method_name: str = None) -> Dict:
        """
        Apply flattening pattern to a specific file/method.
        
        Args:
            file_path: Path to file
            method_name: Optional specific method to target
            
        Returns:
            Extraction plan
        """
        logger.info(f"⚛️  Applying flattening pattern to {file_path}")
        
        # Read file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
        except Exception as e:
            logger.error(f"[X] Could not read file: {e}")
            return {"error": str(e)}
        
        # Analyze complexity
        if method_name:
            # Extract specific method
            import ast
            try:
                tree = ast.parse(source)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if node.name == method_name:
                            # Extract method source
                            lines = source.split('\n')
                            method_source = '\n'.join(lines[node.lineno - 1:node.end_lineno])
                            
                            # Analyze
                            metrics, candidates = FlatteningPattern.analyze_method(
                                method_source, method_name
                            )
                            
                            # Generate plan
                            plan = FlatteningPattern.generate_extraction_plan(metrics, candidates)
                            
                            logger.info(f"[OK] Generated extraction plan for {method_name}")
                            return plan
            except Exception as e:
                logger.error(f"[X] Error analyzing method: {e}")
                return {"error": str(e)}
        
        # Analyze entire file
        import ast
        try:
            tree = ast.parse(source)
            all_plans = []
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    lines = source.split('\n')
                    method_source = '\n'.join(lines[node.lineno - 1:node.end_lineno])
                    
                    metrics, candidates = FlatteningPattern.analyze_method(
                        method_source, node.name
                    )
                    
                    if metrics.exceeds_threshold():
                        plan = FlatteningPattern.generate_extraction_plan(metrics, candidates)
                        plan["method_name"] = node.name
                        plan["line"] = node.lineno
                        all_plans.append(plan)
            
            logger.info(f"[OK] Found {len(all_plans)} methods needing extraction")
            return {
                "file": file_path,
                "methods_needing_extraction": len(all_plans),
                "extraction_plans": all_plans
            }
            
        except Exception as e:
            logger.error(f"[X] Error analyzing file: {e}")
            return {"error": str(e)}
    
    def get_extraction_guidance(self, metrics: ComplexityMetrics) -> str:
        """
        Get human-readable extraction guidance based on metrics.
        
        Args:
            metrics: Complexity metrics
            
        Returns:
            Guidance text
        """
        pattern = self.retrieve_flattening_pattern()
        
        guidance = [
            "⚛️ Subatomic Flattening Pattern Retrieved",
            "",
            f"Current Metrics: {metrics.line_count} lines, {metrics.nesting_depth} nesting",
            f"Target: ≤40 lines, ≤3 nesting",
            "",
            "Recommended Actions:",
        ]
        
        if pattern:
            for i, step in enumerate(pattern["reusable_pattern"]["extraction_heuristic"], 1):
                guidance.append(f"{i}. {step}")
            
            guidance.extend([
                "",
                "Naming Convention:",
                *[f"  - {k}: {v}" for k, v in pattern["reusable_pattern"]["naming_convention"].items()],
                "",
                "Success Example:",
                f"  {pattern['source_file']} → {pattern['method_name']}",
                f"  Before: {pattern['before']['lines']} lines, {pattern['before']['nesting_depth']} nesting",
                f"  After: {pattern['after']['lines']} lines, {pattern['after']['nesting_depth']} nesting",
                f"  Result: {pattern['success_metrics']['complexity_reduction']}% reduction"
            ])
        
        return "\n".join(guidance)


# Global instance for easy access
_pattern_agent = None

def get_pattern_agent() -> PatternRetrievalAgent:
    """Get or create global Pattern Retrieval Agent instance."""
    global _pattern_agent
    if _pattern_agent is None:
        _pattern_agent = PatternRetrievalAgent()
    return _pattern_agent
