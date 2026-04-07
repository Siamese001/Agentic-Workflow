#!/usr/bin/env python3
"""
Cascade Chat Preprocessor - Forces Sequential Thinking Invocation

This preprocessor intercepts ALL cascade chat prompts and prepends
instructions that REQUIRE the sequential thinking MCP tool to be invoked.
"""

import os
from typing import Any


class SequentialThinkingPreProcessor:
    """
    Pre-processor that forces sequential thinking tool invocation.

    This ensures EVERY complex prompt with Kimi K2.5 starts with
    a sequential thinking tool call.
    """

    def __init__(self):
        self.enabled = True
        self.aggressive = os.environ.get('SEQUENTIAL_THINKING_AGGRESSIVE_MODE', 'enabled') == 'enabled'

    def preprocess(self, prompt: str, context: dict | None = None) -> dict[str, Any]:
        """
        Preprocess the prompt to inject sequential thinking invocation.

        Returns dict with:
        - modified_prompt: The prompt with invocation instructions
        - tool_invocation_required: Whether to force tool call
        - tool_call: The tool call spec
        """

        # Determine if this needs sequential thinking
        needs_thinking = self._needs_sequential_thinking(prompt)

        if not needs_thinking and not self.aggressive:
            return {
                'modified_prompt': prompt,
                'tool_invocation_required': False,
                'tool_call': None,
            }

        # Create the tool invocation instruction
        tool_call = self._create_tool_call(prompt)

        # Inject the instruction at the START of the prompt
        modified = f"""⚠️ MANDATORY: Invoke Sequential Thinking First ⚠️

You MUST call the sequential thinking tool BEFORE responding.

🔧 **TOOL CALL REQUIRED:**
```
Tool: mcp7_sequentialthinking
Method: sequentialthinking
Arguments: {{
  "thought": "I am analyzing this request using structured sequential thinking. Let me break down the problem...",
  "thoughtNumber": 1,
  "totalThoughts": 25,
  "nextThoughtNeeded": true,
  "isRevision": false,
  "revisesThought": null,
  "branchFromThought": null,
  "branchId": null,
  "needsMoreThoughts": true
}}
```

🚫 **DO NOT PROCEED** without making this tool call first.

---

**USER REQUEST:**
{prompt}

---

**AFTER** invoking the tool above, continue with your analysis using the structured thinking process.
"""

        return {
            'modified_prompt': modified,
            'tool_invocation_required': True,
            'tool_call': tool_call,
            'original_prompt': prompt,
        }

    def _needs_sequential_thinking(self, prompt: str) -> bool:
        """Check if prompt needs sequential thinking."""
        prompt_lower = prompt.lower()

        # Always trigger keywords
        trigger_words = [
            'plan', 'design', 'architecture', 'implement', 'create',
            'refactor', 'migrate', 'debug', 'fix', 'troubleshoot',
            'optimize', 'improve', 'analyze', 'investigate',
            'strategy', 'approach', 'how should', 'what is the best',
            'complex', 'difficult', 'multi-step',
        ]

        for word in trigger_words:
            if word in prompt_lower:
                return True

        # Length-based trigger
        if len(prompt) > 100:
            return True

        return False

    def _create_tool_call(self, prompt: str) -> dict[str, Any]:
        """Create the tool call specification."""
        return {
            'tool': 'mcp7_sequentialthinking',
            'method': 'sequentialthinking',
            'arguments': {
                'thought': f'Starting analysis of: {prompt[:100]}...',
                'thoughtNumber': 1,
                'totalThoughts': 25,
                'nextThoughtNeeded': True,
                'isRevision': False,
                'revisesThought': None,
                'branchFromThought': None,
                'branchId': None,
                'needsMoreThoughts': True,
            },
        }


# Global preprocessor instance
preprocessor = SequentialThinkingPreProcessor()


def preprocess_for_sequential_thinking(prompt: str) -> str:
    """
    Main entry point - preprocess prompt to force sequential thinking.

    Use this function to wrap ANY prompt before sending to Kimi K2.5.
    """
    result = preprocessor.preprocess(prompt)
    return result['modified_prompt']


def force_sequential_thinking_invocation(prompt: str) -> dict[str, Any]:
    """
    Force sequential thinking and return full processing info.
    """
    return preprocessor.preprocess(prompt)
