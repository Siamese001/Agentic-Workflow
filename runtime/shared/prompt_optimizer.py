"""
Prompt Optimizer - Advanced Prompt Engineering
Ported from legacy_engines/goal_alignment_engine.py

Optimizes prompts for clarity, specificity, structure,
and constraint application to improve output quality.
"""

import logging
import re
import time
from typing import Dict, List, object, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class OptimizationStrategy(Enum):
    """Strategies for prompt optimization"""
    CLARITY = "clarity"
    SPECIFICITY = "specificity"
    STRUCTURE = "structure"
    CONSTRAINTS = "constraints"
    COMPREHENSIVE = "comprehensive"


class OptimizationLevel(Enum):
    """Levels of optimization intensity"""
    LIGHT = "light"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


@dataclass
class OptimizationConfig:
    """Configuration for prompt optimization"""
    strategy: OptimizationStrategy = OptimizationStrategy.COMPREHENSIVE
    level: OptimizationLevel = OptimizationLevel.MODERATE
    max_length: Optional[int] = None
    preserve_formatting: bool = True
    add_examples: bool = False


@dataclass
class OptimizationResult:
    """Result of prompt optimization"""
    original_prompt: str
    optimized_prompt: str
    strategies_applied: List[str]
    improvements: List[str]
    optimization_score: float
    length_change: int
    processing_time_ms: int


class PromptOptimizer:
    """
    Advanced Prompt Engineering Optimizer
    
    Optimizes prompts for clarity, specificity, structure,
    and constraint application to improve output quality.
    """
    
    def __init__(self, config: Optional[OptimizationConfig] = None):
        """
        Initialize prompt optimizer.
        
        Args:
            config: Optimization configuration
        """
        self.config = config or OptimizationConfig()
        self.optimization_history: List[OptimizationResult] = []
    
    def optimize(
        self,
        prompt: str,
        context: Optional[Dict[str, object]] = None,
        config: Optional[OptimizationConfig] = None
    ) -> OptimizationResult:
        """
        Optimize a prompt for better output quality.
        
        Args:
            prompt: Original prompt
            context: Additional context
            config: Override configuration
            
        Returns:
            OptimizationResult with optimized prompt
        """
        start_time = time.time()
        config = config or self.config
        context = context or {}
        
        optimized = prompt
        strategies_applied = []
        improvements = []
        
        # Apply optimization based on strategy
        if config.strategy == OptimizationStrategy.COMPREHENSIVE:
            # Apply all strategies
            optimized, clarity_improvements = self._optimize_clarity(optimized, config)
            improvements.extend(clarity_improvements)
            if clarity_improvements:
                strategies_applied.append("clarity")
            
            optimized, specificity_improvements = self._optimize_specificity(optimized, context, config)
            improvements.extend(specificity_improvements)
            if specificity_improvements:
                strategies_applied.append("specificity")
            
            optimized, structure_improvements = self._optimize_structure(optimized, config)
            improvements.extend(structure_improvements)
            if structure_improvements:
                strategies_applied.append("structure")
            
            optimized, constraint_improvements = self._apply_constraints(optimized, context, config)
            improvements.extend(constraint_improvements)
            if constraint_improvements:
                strategies_applied.append("constraints")
        
        elif config.strategy == OptimizationStrategy.CLARITY:
            optimized, improvements = self._optimize_clarity(optimized, config)
            strategies_applied.append("clarity")
        
        elif config.strategy == OptimizationStrategy.SPECIFICITY:
            optimized, improvements = self._optimize_specificity(optimized, context, config)
            strategies_applied.append("specificity")
        
        elif config.strategy == OptimizationStrategy.STRUCTURE:
            optimized, improvements = self._optimize_structure(optimized, config)
            strategies_applied.append("structure")
        
        elif config.strategy == OptimizationStrategy.CONSTRAINTS:
            optimized, improvements = self._apply_constraints(optimized, context, config)
            strategies_applied.append("constraints")
        
        # Apply length constraints if specified
        if config.max_length and len(optimized) > config.max_length:
            optimized = self._truncate_intelligently(optimized, config.max_length)
            improvements.append(f"Truncated to {config.max_length} characters")
        
        # Calculate optimization score
        optimization_score = self._calculate_optimization_score(prompt, optimized, improvements)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        result = OptimizationResult(
            original_prompt=prompt,
            optimized_prompt=optimized,
            strategies_applied=strategies_applied,
            improvements=improvements,
            optimization_score=optimization_score,
            length_change=len(optimized) - len(prompt),
            processing_time_ms=processing_time
        )
        
        self.optimization_history.append(result)
        
        logger.info(f"Prompt optimization complete: {len(improvements)} improvements, score={optimization_score:.2f}")
        
        return result
    
    def _optimize_clarity(
        self,
        prompt: str,
        config: OptimizationConfig
    ) -> tuple[str, List[str]]:
        """Optimize prompt for clarity."""
        improvements = []
        optimized = prompt
        
                original_len = len(optimized)
        optimized = re.sub(r'\s+', ' ', optimized).strip()
        if len(optimized) < original_len:
            improvements.append("Removed redundant whitespace")
        
        # Fix shared clarity issues
        clarity_fixes = [
            (r'\bplease\s+please\b', 'please'),
            (r'\bvery\s+very\b', 'very'),
            (r'\breally\s+really\b', 'really'),
            (r'\bjust\s+just\b', 'just'),
            (r'\s+,', ','),
            (r'\s+\.', '.'),
            (r'\s+\?', '?'),
            (r'\s+!', '!'),
        ]
        
        for pattern, replacement in clarity_fixes:
            if re.search(pattern, optimized, re.IGNORECASE):
                optimized = re.sub(pattern, replacement, optimized, flags=re.IGNORECASE)
                improvements.append(f"Fixed clarity issue: {pattern}")
        
        # Ensure proper sentence endings
        if optimized and not optimized[-1] in '.?!':
            optimized += '.'
            improvements.append("Added proper sentence ending")
        
                if config.level == OptimizationLevel.AGGRESSIVE:
            filler_words = [
                r'\bjust\b', r'\breally\b', r'\bactually\b', r'\bbasically\b',
                r'\bliterally\b', r'\bsimply\b', r'\bobviously\b'
            ]
            for filler in filler_words:
                if re.search(filler, optimized, re.IGNORECASE):
                    optimized = re.sub(filler + r'\s*', '', optimized, flags=re.IGNORECASE)
                    improvements.append(f"Removed filler word")
        
        return optimized, improvements
    
    def _optimize_specificity(
        self,
        prompt: str,
        context: Dict[str, object],
        config: OptimizationConfig
    ) -> tuple[str, List[str]]:
        """Optimize prompt for specificity."""
        improvements = []
        optimized = prompt
        
        # Add context-specific details
        if context.get('target_role'):
            if context['target_role'].lower() not in optimized.lower():
                optimized = f"For the role of {context['target_role']}: {optimized}"
                improvements.append("Added target role context")
        
        if context.get('industry'):
            if context['industry'].lower() not in optimized.lower():
                optimized += f" Focus on {context['industry']} industry context."
                improvements.append("Added industry context")
        
        # Add output format specifications if missing
        format_keywords = ['format', 'structure', 'output', 'return', 'provide']
        has_format_spec = any(kw in optimized.lower() for kw in format_keywords)
        
        if not has_format_spec and config.level in [OptimizationLevel.MODERATE, OptimizationLevel.AGGRESSIVE]:
            optimized += " Provide a clear, structured response."
            improvements.append("Added output format specification")
        
        # Add quality expectations
        quality_keywords = ['quality', 'accurate', 'precise', 'detailed', 'thorough']
        has_quality_spec = any(kw in optimized.lower() for kw in quality_keywords)
        
        if not has_quality_spec and config.level == OptimizationLevel.AGGRESSIVE:
            optimized += " Ensure accuracy and completeness."
            improvements.append("Added quality expectations")
        
        return optimized, improvements
    
    def _optimize_structure(
        self,
        prompt: str,
        config: OptimizationConfig
    ) -> tuple[str, List[str]]:
        """Optimize prompt structure."""
        improvements = []
        optimized = prompt
        
        # Check if prompt is too long without structure
        if len(optimized) > 300 and '\n' not in optimized:
            # Add paragraph breaks
            sentences = re.split(r'(?<=[.!?])\s+', optimized)
            
            if len(sentences) > 3:
                # Group sentences into paragraphs
                paragraphs = []
                current_para = []
                
                for sentence in sentences:
                    current_para.append(sentence)
                    if len(current_para) >= 3:
                        paragraphs.append(' '.join(current_para))
                        current_para = []
                
                if current_para:
                    paragraphs.append(' '.join(current_para))
                
                optimized = '\n\n'.join(paragraphs)
                improvements.append("Added paragraph structure")
        
        # Add section markers for very long prompts
        if len(optimized) > 500 and config.level == OptimizationLevel.AGGRESSIVE:
            # Check if already has sections
            if not re.search(r'\[.*?\]|#|##', optimized):
                # Add basic section markers
                parts = optimized.split('\n\n')
                if len(parts) >= 2:
                    parts[0] = "[CONTEXT]\n" + parts[0]
                    parts[-1] = "[TASK]\n" + parts[-1]
                    optimized = '\n\n'.join(parts)
                    improvements.append("Added section markers")
        
        return optimized, improvements
    
    def _apply_constraints(
        self,
        prompt: str,
        context: Dict[str, object],
        config: OptimizationConfig
    ) -> tuple[str, List[str]]:
        """Apply constraints to prompt."""
        improvements = []
        optimized = prompt
        
        constraints = context.get('constraints', [])
        
        if constraints:
            constraint_section = "\n\n[CONSTRAINTS]\n"
            for constraint in constraints[:5]:  # Limit to 5 constraints
                constraint_section += f"- {constraint}\n"
            
            optimized += constraint_section
            improvements.append(f"Added {len(constraints[:5])} constraints")
        
        # Add implicit constraints based on context
        if context.get('max_length'):
            optimized += f"\n\nLimit response to approximately {context['max_length']} words."
            improvements.append("Added length constraint")
        
        if context.get('tone'):
            optimized += f"\n\nUse a {context['tone']} tone."
            improvements.append("Added tone constraint")
        
        if context.get('audience'):
            optimized += f"\n\nTarget audience: {context['audience']}."
            improvements.append("Added audience constraint")
        
        return optimized, improvements
    
    def _truncate_intelligently(self, text: str, max_length: int) -> str:
        """Truncate text at sentence boundary."""
        if len(text) <= max_length:
            return text
        
        # Find last sentence boundary before max_length
        truncated = text[:max_length]
        
        # Look for sentence endings
        last_period = truncated.rfind('.')
        last_question = truncated.rfind('?')
        last_exclaim = truncated.rfind('!')
        
        last_boundary = max(last_period, last_question, last_exclaim)
        
        if last_boundary > max_length * 0.7:  # At least 70% of content
            return text[:last_boundary + 1]
        
        # Fallback to word boundary
        last_space = truncated.rfind(' ')
        if last_space > max_length * 0.8:
            return text[:last_space] + '...'
        
        return truncated + '...'
    
    def _calculate_optimization_score(
        self,
        original: str,
        optimized: str,
        improvements: List[str]
    ) -> float:
        """Calculate optimization quality score."""
        if original == optimized:
            return 0.5 if not improvements else 0.6
        
        # foundation score
        score = 0.6
        
        # Improvement count bonus
        score += min(len(improvements) * 0.05, 0.2)
        
        # Structure improvement bonus
        if '\n' in optimized and '\n' not in original:
            score += 0.1
        
        # Length efficiency (slight increase is good, large increase may be bad)
        length_ratio = len(optimized) / max(len(original), 1)
        if 1.0 <= length_ratio <= 1.3:
            score += 0.1
        elif length_ratio > 1.5:
            score -= 0.1
        
        return round(min(max(score, 0.0), 1.0), 3)
    
    def get_optimization_stats(self) -> Dict[str, object]:
        """Get optimization statistics."""
        if not self.optimization_history:
            return {}
        
        recent = self.optimization_history[-20:]
        
        return {
            'total_optimizations': len(self.optimization_history),
            'recent_optimizations': len(recent),
            'avg_optimization_score': sum(r.optimization_score for r in recent) / len(recent),
            'avg_improvements_per_optimization': sum(len(r.improvements) for r in recent) / len(recent),
            'avg_length_change': sum(r.length_change for r in recent) / len(recent),
            'avg_processing_time_ms': sum(r.processing_time_ms for r in recent) / len(recent)
        }


# builder functions
def create_prompt_optimizer(config: Optional[OptimizationConfig] = None) -> PromptOptimizer:
    """Create prompt optimizer instance."""
    return PromptOptimizer(config)


def optimize_prompt(
    prompt: str,
    strategy: OptimizationStrategy = OptimizationStrategy.COMPREHENSIVE,
    level: OptimizationLevel = OptimizationLevel.MODERATE
) -> OptimizationResult:
    """Convenience function to optimize a prompt."""
    config = OptimizationConfig(strategy=strategy, level=level)
    optimizer = PromptOptimizer(config)
    return optimizer.optimize(prompt)


def create_optimization_config(
    strategy: OptimizationStrategy = OptimizationStrategy.COMPREHENSIVE,
    level: OptimizationLevel = OptimizationLevel.MODERATE,
    max_length: Optional[int] = None
) -> OptimizationConfig:
    """Create optimization configuration."""
    return OptimizationConfig(strategy=strategy, level=level, max_length=max_length)
