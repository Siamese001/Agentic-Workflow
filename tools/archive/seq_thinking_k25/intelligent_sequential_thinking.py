#!/usr/bin/env python3
"""
Intelligent Sequential Thinking Trigger for Kimi K2.5

Analyzes task complexity and automatically invokes the sequential thinking MCP
only when structured reasoning is actually needed.
"""

import json
import os
import re
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any


class ComplexityLevel(Enum):
    TRIVIAL = "trivial"      # No reasoning needed
    SIMPLE = "simple"        # Simple reasoning
    MODERATE = "moderate"    # Some structure helpful
    COMPLEX = "complex"      # Sequential thinking recommended
    CRITICAL = "critical"    # Sequential thinking required


@dataclass
class TaskAnalysis:
    """Analysis of a task to determine if sequential thinking is needed."""
    complexity: ComplexityLevel
    confidence: float  # 0.0 to 1.0
    reasoning_required: bool
    suggested_thoughts: int  # How many thoughts to use (0 if not needed)
    factors: list[str]  # Why this decision was made


class TaskComplexityAnalyzer:
    """
    Analyzes task complexity to determine when sequential thinking is needed.

    Scoring system:
    - Trivial tasks (score 0-2): Simple chat response
    - Simple tasks (score 3-5): Brief reasoning
    - Moderate tasks (score 6-9): Sequential thinking with 10-15 thoughts
    - Complex tasks (score 10-14): Sequential thinking with 20-25 thoughts
    - Critical tasks (score 15+): Full sequential thinking required
    """

    # Complexity indicators with scores
    COMPLEXITY_INDICATORS = {
        # Architecture & Design (high complexity)
        'architecture': 5, 'design': 4, 'system': 3, 'structure': 3,
        'pattern': 3, 'framework': 3, 'infrastructure': 4,

        # Implementation (medium-high complexity)
        'implement': 4, 'create': 3, 'build': 3, 'develop': 3,
        'feature': 3, 'module': 3, 'component': 3, 'service': 3,

        # Refactoring (high complexity)
        'refactor': 4, 'restructure': 4, 'migrate': 4, 'modernize': 3,
        'rewrite': 4, 'redesign': 4, 'consolidate': 3,

        # Debugging (medium complexity)
        'debug': 3, 'troubleshoot': 3, 'investigate': 3, 'diagnose': 3,
        'fix': 2, 'resolve': 2, 'error': 2, 'bug': 2,

        # Analysis (medium-high complexity)
        'analyze': 3, 'analysis': 3, 'evaluate': 3, 'assess': 3,
        'review': 3, 'audit': 4, 'inspect': 2,

        # Planning (high complexity)
        'plan': 4, 'strategy': 4, 'roadmap': 4, 'approach': 3,
        'organize': 3, 'coordinate': 3, 'orchestrate': 4,

        # Optimization (medium complexity)
        'optimize': 3, 'improve': 2, 'enhance': 2, 'performance': 3,
        'efficient': 2, 'scale': 3, 'benchmark': 2,

        # Testing (medium complexity)
        'test': 2, 'validate': 2, 'verify': 2, 'testcase': 2,
        'coverage': 2, 'regression': 3, 'e2e': 3,

        # Decision making (medium complexity)
        'decide': 3, 'choose': 2, 'select': 2, 'compare': 2,
        'tradeoff': 4, 'prioritize': 3, 'balance': 2,

        # Multi-step indicators (high complexity)
        'step': 1, 'phase': 2, 'stage': 2, 'iteration': 2,
        'workflow': 3, 'pipeline': 3, 'process': 2,

        # Dependencies (high complexity)
        'dependency': 3, 'dependent': 3, 'coupling': 4, 'integration': 3,
        'interface': 2, 'contract': 2, 'api': 1,

        # Risk/Safety (high complexity)
        'risk': 3, 'safety': 4, 'security': 3, 'compliance': 4,
        'governance': 4, 'violation': 3, 'critical': 3,
    }

    # Trivial patterns - no reasoning needed
    TRIVIAL_PATTERNS = [
        r'^what is\s+\d+\s*\+\s*\d+',  # Simple math
        r'^\d+\s*\+\s*\d+',  # Just numbers
        r'^hello|^hi$|^hey$',  # Greetings
        r'^thank|^thanks$|^ok$|^okay$',  # Acknowledgments
        r'^yes$|^no$|^maybe$',  # Simple responses
        r'^(what|how) (is|are|was|were)\s+\w+\s*$',  # Simple definitions
    ]

    # Always use sequential thinking for these
    ALWAYS_REASONING = [
        r'plan|design|architecture|strategy|roadmap',
        r'refactor|migrate|rewrite|restructure',
        r'debug.*system|investigate.*issue|troubleshoot.*complex',
        r'optimize.*performance|improve.*architecture',
        r'test.*coverage|validate.*design|audit.*code',
        r'compare.*approaches|evaluate.*options|decide.*between',
        r'complex|multi-step|multi-phase|comprehensive',
    ]

    def analyze(self, prompt: str) -> TaskAnalysis:
        """
        Analyze a prompt to determine complexity and reasoning needs.
        """
        prompt_lower = prompt.lower()

        # Check if trivial
        if self._is_trivial(prompt_lower):
            return TaskAnalysis(
                complexity=ComplexityLevel.TRIVIAL,
                confidence=0.9,
                reasoning_required=False,
                suggested_thoughts=0,
                factors=["Trivial task - no structured reasoning needed"],
            )

        # Check if always requires reasoning
        if self._always_requires_reasoning(prompt_lower):
            return TaskAnalysis(
                complexity=ComplexityLevel.CRITICAL,
                confidence=0.95,
                reasoning_required=True,
                suggested_thoughts=25,
                factors=["Task type requires structured reasoning"],
            )

        # Calculate complexity score
        score, factors = self._calculate_complexity(prompt_lower)

        # Determine complexity level
        if score <= 2:
            complexity = ComplexityLevel.TRIVIAL
            reasoning_required = False
            suggested_thoughts = 0
        elif score <= 5:
            complexity = ComplexityLevel.SIMPLE
            reasoning_required = False
            suggested_thoughts = 0
        elif score <= 9:
            complexity = ComplexityLevel.MODERATE
            reasoning_required = True
            suggested_thoughts = 15
        elif score <= 14:
            complexity = ComplexityLevel.COMPLEX
            reasoning_required = True
            suggested_thoughts = 20
        else:
            complexity = ComplexityLevel.CRITICAL
            reasoning_required = True
            suggested_thoughts = 25

        # Calculate confidence based on factor count
        confidence = min(0.95, 0.5 + (len(factors) * 0.1))

        return TaskAnalysis(
            complexity=complexity,
            confidence=confidence,
            reasoning_required=reasoning_required,
            suggested_thoughts=suggested_thoughts,
            factors=factors,
        )

    def _is_trivial(self, prompt: str) -> bool:
        """Check if prompt is trivial (no reasoning needed)."""
        # Check trivial patterns
        for pattern in self.TRIVIAL_PATTERNS:
            if re.search(pattern, prompt, re.IGNORECASE):
                return True

        # Very short prompts are often trivial
        if len(prompt) < 30 and not any(c in prompt for c in ['?', 'how', 'why', 'explain']):
            return True

        return False

    def _always_requires_reasoning(self, prompt: str) -> bool:
        """Check if this type of task always requires reasoning."""
        for pattern in self.ALWAYS_REASONING:
            if re.search(pattern, prompt, re.IGNORECASE):
                return True
        return False

    def _calculate_complexity(self, prompt: str) -> tuple[int, list[str]]:
        """Calculate complexity score and return factors."""
        score = 0
        factors = []

        # Score based on keyword matches
        for keyword, points in self.COMPLEXITY_INDICATORS.items():
            if keyword in prompt:
                score += points
                factors.append(f"'{keyword}' detected (+{points})")

        # Length bonus
        if len(prompt) > 500:
            score += 3
            factors.append(f"Long prompt ({len(prompt)} chars) (+3)")
        elif len(prompt) > 200:
            score += 1
            factors.append(f"Medium prompt ({len(prompt)} chars) (+1)")

        # Question complexity
        if 'how' in prompt and ('should' in prompt or 'would' in prompt or 'could' in prompt):
            score += 2
            factors.append("Complex 'how' question (+2)")

        if 'why' in prompt:
            score += 1
            factors.append("'Why' question requires explanation (+1)")

        # Multiple questions
        question_count = prompt.count('?')
        if question_count > 2:
            score += 2
            factors.append(f"Multiple questions ({question_count}) (+2)")

        # Conjunctions indicate complexity
        conjunctions = ['and', 'but', 'or', 'however', 'therefore', 'because']
        conj_count = sum(1 for c in conjunctions if c in prompt)
        if conj_count > 3:
            score += 2
            factors.append("Complex sentence structure (+2)")

        return score, factors


class IntelligentSequentialThinker:
    """
    Intelligently decides when to invoke sequential thinking.

    Usage:
        thinker = IntelligentSequentialThinker()
        result = thinker.process_prompt("Design the architecture")

        if result['invoke_sequential_thinking']:
            # Call the MCP tool with result['tool_arguments']
            pass
    """

    def __init__(self):
        self.analyzer = TaskComplexityAnalyzer()
        self.invocation_count = 0
        self.auto_invoke = os.environ.get('SEQUENTIAL_THINKING_AUTO_TRIGGER', 'true').lower() == 'true'
        self.threshold = os.environ.get('SEQUENTIAL_THINKING_COMPLEXITY_THRESHOLD', 'moderate')

    def process_prompt(self, prompt: str) -> dict[str, Any]:
        """
        Process a prompt and determine if sequential thinking should be invoked.

        Returns dict with:
        - invoke_sequential_thinking: bool
        - tool_arguments: dict (if invoke is True)
        - analysis: TaskAnalysis
        - reasoning: str (explanation of decision)
        """
        # Analyze the task
        analysis = self.analyzer.analyze(prompt)

        # Determine if we should invoke
        should_invoke = self._should_invoke(analysis)

        result = {
            'invoke_sequential_thinking': should_invoke,
            'analysis': asdict(analysis),
            'reasoning': self._explain_decision(analysis, should_invoke),
        }

        if should_invoke:
            self.invocation_count += 1
            result['tool_arguments'] = self._create_tool_arguments(prompt, analysis)
            result['tool_name'] = 'mcp7_sequentialthinking'
            result['method'] = 'sequentialthinking'

        return result

    def _should_invoke(self, analysis: TaskAnalysis) -> bool:
        """Determine if sequential thinking should be invoked."""
        if not self.auto_invoke:
            return False

        # Always invoke for critical complexity
        if analysis.complexity == ComplexityLevel.CRITICAL:
            return True

        # Invoke based on threshold
        threshold_map = {
            'trivial': ComplexityLevel.TRIVIAL,
            'simple': ComplexityLevel.SIMPLE,
            'moderate': ComplexityLevel.MODERATE,
            'complex': ComplexityLevel.COMPLEX,
            'critical': ComplexityLevel.CRITICAL,
        }

        threshold_level = threshold_map.get(self.threshold, ComplexityLevel.MODERATE)

        complexity_order = [
            ComplexityLevel.TRIVIAL,
            ComplexityLevel.SIMPLE,
            ComplexityLevel.MODERATE,
            ComplexityLevel.COMPLEX,
            ComplexityLevel.CRITICAL,
        ]

        # Invoke if task complexity >= threshold
        task_index = complexity_order.index(analysis.complexity)
        threshold_index = complexity_order.index(threshold_level)

        return task_index >= threshold_index and analysis.reasoning_required

    def _explain_decision(self, analysis: TaskAnalysis, will_invoke: bool) -> str:
        """Generate explanation for the decision."""
        factors_str = '\n'.join(f'  - {f}' for f in analysis.factors)

        if will_invoke:
            return f"""Sequential thinking will be invoked.

Complexity: {analysis.complexity.value.upper()}
Confidence: {analysis.confidence:.0%}
Suggested thoughts: {analysis.suggested_thoughts}

Factors:
{factors_str}"""
        else:
            return f"""Sequential thinking NOT needed.

Complexity: {analysis.complexity.value}
Confidence: {analysis.confidence:.0%}
Reason: Task is simple enough for direct response.

Factors:
{factors_str}"""

    def _create_tool_arguments(self, prompt: str, analysis: TaskAnalysis) -> dict[str, Any]:
        """Create the tool arguments for sequential thinking invocation."""
        return {
            'thought': f"Starting structured analysis of: {prompt[:200]}{'...' if len(prompt) > 200 else ''}",
            'thoughtNumber': 1,
            'totalThoughts': analysis.suggested_thoughts,
            'nextThoughtNeeded': True,
            'isRevision': False,
            'revisesThought': None,
            'branchFromThought': None,
            'branchId': None,
            'needsMoreThoughts': True,
        }

    def wrap_prompt_if_needed(self, prompt: str) -> tuple[str, bool]:
        """
        Wrap a prompt with sequential thinking instruction if needed.

        Returns (modified_prompt, was_wrapped)
        """
        result = self.process_prompt(prompt)

        if result['invoke_sequential_thinking']:
            wrapped = f"""{result['reasoning']}

Please invoke sequential thinking now using:
Tool: {result['tool_name']}
Method: {result['method']}
Arguments: ```json
{json.dumps(result['tool_arguments'], indent=2)}
```

Then proceed with the task:

---

{prompt}"""
            return wrapped, True
        else:
            return prompt, False


# Convenience functions
_analyzer = TaskComplexityAnalyzer()
_thinker = IntelligentSequentialThinker()


def analyze_task(prompt: str) -> TaskAnalysis:
    """Quick function to analyze task complexity."""
    return _analyzer.analyze(prompt)


def should_use_sequential_thinking(prompt: str) -> bool:
    """Quick check if sequential thinking should be used."""
    result = _thinker.process_prompt(prompt)
    return result['invoke_sequential_thinking']


def intelligent_sequential_think(prompt: str) -> dict[str, Any]:
    """
    Main entry point - intelligently decides and prepares sequential thinking.

    Returns full result dict with invocation info if needed.
    """
    return _thinker.process_prompt(prompt)


if __name__ == '__main__':
    # Test the analyzer
    test_prompts = [
        "What is 2+2?",
        "Hi",
        "Create a plan for the new architecture",
        "Debug this complex issue with the database",
        "How should I refactor this module?",
        "What is the weather today?",
        "Design a microservices architecture for scalability",
        "Fix this bug",
        "Optimize the performance of the query",
        "Write a simple function",
    ]

    print("=" * 80)
    print("INTELLIGENT SEQUENTIAL THINKING ANALYZER")
    print("=" * 80)

    for prompt in test_prompts:
        result = intelligent_sequential_think(prompt)

        status = "🧠 INVOKE" if result['invoke_sequential_thinking'] else "💬 DIRECT"

        print(f"\n{status}: {prompt[:50]}...")
        print(f"  Complexity: {result['analysis']['complexity']}")
        print(f"  Confidence: {result['analysis']['confidence']:.0%}")

        if result['invoke_sequential_thinking']:
            print(f"  Thoughts: {result['tool_arguments']['totalThoughts']}")

    print("\n" + "=" * 80)
