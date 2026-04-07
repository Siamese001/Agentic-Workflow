#!/usr/bin/env python3
"""
Sequential Thinking Auto-Invoker for Kimi K2.5 Cascade Chat

This module actively invokes the sequential thinking MCP tool at the start of
complex conversations to ensure structured reasoning is always used.
"""

import os
import re
from dataclasses import dataclass
from typing import Any


@dataclass
class SequentialThinkingContext:
    """Context for sequential thinking invocation."""
    thought_number: int = 1
    total_thoughts: int = 1
    next_thought_needed: bool = True
    thought: str = ""
    is_revision: bool = False
    revises_thought: int | None = None
    branch_from_thought: int | None = None
    branch_id: str | None = None
    needs_more_thoughts: bool = True


class SequentialThinkingAutoInvoker:
    """
    Auto-invokes sequential thinking MCP for all complex Kimi K2.5 operations.

    This class ensures sequential thinking is ALWAYS invoked at the start of:
    - Planning phases
    - Code analysis tasks
    - Multi-step reasoning
    - Architecture decisions
    - Problem-solving workflows
    """

    # Patterns that indicate complex reasoning is needed
    COMPLEXITY_PATTERNS = [
        r'plan|design|architect',
        r'analyze|investigate|debug',
        r'implement|create|build',
        r'refactor|restructure|migrate',
        r'test|validate|verify',
        r'optimize|improve|enhance',
        r'fix|resolve|troubleshoot',
        r'review|audit|assess',
        r'compare|evaluate|decide',
        r'strategize|approach|method',
    ]

    # Always trigger for these task types
    ALWAYS_TRIGGER = [
        'create plan',
        'design architecture',
        'implement feature',
        'refactor code',
        'debug issue',
        'analyze codebase',
        'write tests',
        'optimize performance',
        'review code',
        'migrate system',
    ]

    def __init__(self):
        self.enabled = os.environ.get('SEQUENTIAL_THINKING_AUTO_TRIGGER', 'false').lower() == 'true'
        self.aggressive_mode = os.environ.get('SEQUENTIAL_THINKING_AGGRESSIVE_MODE', 'false').lower() == 'enabled'
        self.min_complexity = os.environ.get('SEQUENTIAL_THINKING_MIN_COMPLEXITY', 'medium')
        self.max_thoughts = int(os.environ.get('SEQUENTIAL_THINKING_MAX_THOUGHTS', '25'))
        self.token_budget = int(os.environ.get('SEQUENTIAL_THINKING_TOKEN_BUDGET', '50000'))
        self.invocation_count = 0

    def should_trigger(self, prompt: str) -> bool:
        """Determine if sequential thinking should be triggered for this prompt."""
        if not self.enabled:
            return False

        prompt_lower = prompt.lower()

        # AGGRESSIVE: Always trigger in aggressive mode
        if self.aggressive_mode:
            return True

        # Check always-trigger patterns
        for trigger in self.ALWAYS_TRIGGER:
            if trigger in prompt_lower:
                return True

        # Check complexity patterns
        for pattern in self.COMPLEXITY_PATTERNS:
            if re.search(pattern, prompt_lower):
                return True

        # Check for question/problem indicators
        if any(word in prompt_lower for word in ['how', 'why', 'what', 'when', 'should', 'best', 'approach']):
            return True

        # Check prompt length (longer prompts likely need structured thinking)
        if len(prompt) > 200:
            return True

        return False

    def generate_initial_thought(self, prompt: str) -> str:
        """Generate the initial thought structure for sequential thinking."""
        self.invocation_count += 1

        # Create structured initial thought
        thought = f"""Analyzing request with sequential structured thinking:

**Task Understanding:**
- Request: {prompt[:150]}...
- Complexity: {self._assess_complexity(prompt)}
- Approach: Systematic step-by-step analysis

**Initial Assessment:**
- This task requires structured reasoning
- Breaking down into manageable thought steps
- Will use up to {self.max_thoughts} sequential thoughts if needed

**Next Steps:**
1. Understand the problem scope
2. Identify key components and dependencies
3. Develop solution approach
4. Execute with validation at each step

Proceeding with thought {self.invocation_count} of structured analysis."""

        return thought

    def _assess_complexity(self, prompt: str) -> str:
        """Assess the complexity of the prompt."""
        complexity_score = 0
        prompt_lower = prompt.lower()

        # Score based on keywords
        if any(word in prompt_lower for word in ['architecture', 'design', 'system']):
            complexity_score += 3
        if any(word in prompt_lower for word in ['implement', 'create', 'build']):
            complexity_score += 2
        if any(word in prompt_lower for word in ['debug', 'fix', 'troubleshoot']):
            complexity_score += 2
        if any(word in prompt_lower for word in ['optimize', 'refactor', 'migrate']):
            complexity_score += 3
        if any(word in prompt_lower for word in ['test', 'validate', 'verify']):
            complexity_score += 1

        # Score based on length
        if len(prompt) > 1000:
            complexity_score += 2
        elif len(prompt) > 500:
            complexity_score += 1

        # Return complexity level
        if complexity_score >= 6:
            return "HIGH"
        elif complexity_score >= 3:
            return "MEDIUM"
        else:
            return "LOW"

    def create_sequential_thinking_payload(self, prompt: str) -> dict[str, Any]:
        """Create the payload for sequential thinking tool invocation."""
        thought = self.generate_initial_thought(prompt)

        return {
            "thought": thought,
            "thoughtNumber": 1,
            "totalThoughts": self.max_thoughts,
            "nextThoughtNeeded": True,
            "isRevision": False,
            "revisesThought": None,
            "branchFromThought": None,
            "branchId": None,
            "needsMoreThoughts": True,
        }

    def get_invocation_prompt(self, original_prompt: str) -> str:
        """
        Get the modified prompt that includes sequential thinking invocation.

        This prepends instructions to ensure sequential thinking is used.
        """
        if not self.should_trigger(original_prompt):
            return original_prompt

        # Create the invocation header
        invocation_header = f"""[SEQUENTIAL_THINKING_AUTO_INVOKED - Thought 1/{self.max_thoughts}]

I will use structured sequential thinking to analyze and solve this problem:

---

**Original Request:**
{original_prompt}

---

**Structured Analysis:**

"""

        return invocation_header


class CascadeChatInterceptor:
    """
    Intercepts cascade chat messages and injects sequential thinking invocation.

    This ensures sequential thinking MCP is ALWAYS called before processing
    complex requests in Kimi K2.5 cascade chat.
    """

    def __init__(self):
        self.invoker = SequentialThinkingAutoInvoker()
        self.intercepted_count = 0

    def intercept_prompt(self, prompt: str, user_context: dict | None = None) -> dict[str, Any]:
        """
        Intercept a prompt and prepare sequential thinking invocation.

        Returns a dict with:
        - 'should_invoke': bool - whether to invoke sequential thinking
        - 'modified_prompt': str - the modified prompt with invocation header
        - 'payload': dict - the sequential thinking payload if invoking
        """
        should_invoke = self.invoker.should_trigger(prompt)

        if should_invoke:
            self.intercepted_count += 1
            modified_prompt = self.invoker.get_invocation_prompt(prompt)
            payload = self.invoker.create_sequential_thinking_payload(prompt)

            return {
                'should_invoke': True,
                'modified_prompt': modified_prompt,
                'payload': payload,
                'tool_name': 'sequential-thinking',
                'tool_method': 'sequentialthinking',
            }
        else:
            return {
                'should_invoke': False,
                'modified_prompt': prompt,
                'payload': None,
                'tool_name': None,
                'tool_method': None,
            }

    def get_invocation_instruction(self) -> str:
        """Get the instruction to force sequential thinking invocation."""
        return """
CRITICAL INSTRUCTION: Before processing this request, you MUST invoke the sequential_thinking tool.

Use the mcp7_sequentialthinking tool with these parameters:
- thought: Your initial analysis of the problem
- thoughtNumber: 1
- totalThoughts: 25
- nextThoughtNeeded: true
- isRevision: false

This is MANDATORY for all complex reasoning tasks with Kimi K2.5.
Do NOT proceed with analysis until sequential thinking is invoked.
"""


# Global interceptor instance
cascade_interceptor = CascadeChatInterceptor()


def force_sequential_thinking(prompt: str) -> str:
    """
    Force sequential thinking invocation by modifying the prompt.

    Use this function to wrap any prompt that should use sequential thinking.
    """
    interceptor = CascadeChatInterceptor()
    result = interceptor.intercept_prompt(prompt)

    if result['should_invoke']:
        # Add explicit tool invocation instruction
        return result['modified_prompt'] + "\n\n" + interceptor.get_invocation_instruction()
    else:
        return prompt


def get_sequential_thinking_payload(prompt: str) -> dict[str, Any] | None:
    """Get the payload for sequential thinking invocation if it should be triggered."""
    interceptor = CascadeChatInterceptor()
    result = interceptor.intercept_prompt(prompt)
    return result.get('payload')


# Environment setup for automatic invocation
def setup_auto_invocation():
    """Setup environment for automatic sequential thinking invocation."""
    env_vars = {
        'SEQUENTIAL_THINKING_AUTO_TRIGGER': 'true',
        'SEQUENTIAL_THINKING_AGGRESSIVE_MODE': 'enabled',
        'SEQUENTIAL_THINKING_MIN_COMPLEXITY': 'minimal',
        'SEQUENTIAL_THINKING_MAX_THOUGHTS': '25',
        'SEQUENTIAL_THINKING_TOKEN_BUDGET': '50000',
        'MCP_FORCE_SEQUENTIAL_THINKING': 'true',
        'KIMI_K2_5_SEQUENTIAL_THINKING_REQUIRED': 'true',
    }

    for key, value in env_vars.items():
        os.environ[key] = value

    print("=" * 60)
    print("SEQUENTIAL THINKING AUTO-INVOCATION ENABLED")
    print("=" * 60)
    print("All complex prompts will trigger sequential thinking MCP")
    print(f"Max thoughts: {env_vars['SEQUENTIAL_THINKING_MAX_THOUGHTS']}")
    print(f"Token budget: {env_vars['SEQUENTIAL_THINKING_TOKEN_BUDGET']}")
    print(f"Aggressive mode: {env_vars['SEQUENTIAL_THINKING_AGGRESSIVE_MODE']}")
    print("=" * 60)


if __name__ == '__main__':
    # Test the auto-invoker
    setup_auto_invocation()

    test_prompts = [
        "Create a plan for implementing the new feature",
        "Debug this error in the code",
        "What is 2+2?",  # Should NOT trigger
        "Analyze the architecture and suggest improvements",
        "How should I approach this refactoring?",
    ]

    print("\nTest Results:")
    for prompt in test_prompts:
        result = cascade_interceptor.intercept_prompt(prompt)
        status = "INVOKING" if result['should_invoke'] else "SKIPPING"
        print(f"  [{status}] {prompt[:50]}...")
