#!/usr/bin/env python3
"""
Sequential Thinking FORCER - Makes Kimi K2.5 Actually Use Sequential Thinking

This module creates prompts that FORCE the model to invoke sequential thinking.
It's designed to be used as a wrapper around any request to ensure the tool is called.
"""

import json


def create_forced_sequential_thinking_prompt(user_request: str) -> str:
    """
    Wraps a user request with MANDATORY sequential thinking invocation.

    This creates a prompt that forces the model to:
    1. Call sequentialthinking tool FIRST
    2. Only then proceed with the actual task

    Usage:
        forced_prompt = create_forced_sequential_thinking_prompt("Design the architecture")
        # Then send forced_prompt to Kimi K2.5
    """

    tool_args = {
        "thought": f"I need to use structured sequential thinking to analyze: {user_request[:150]}. Let me break this down systematically.",
        "thoughtNumber": 1,
        "totalThoughts": 25,
        "nextThoughtNeeded": True,
        "isRevision": False,
        "revisesThought": None,
        "branchFromThought": None,
        "branchId": None,
        "needsMoreThoughts": True,
    }

    wrapped = f"""🚫 STOP - MANDATORY SEQUENTIAL THINKING REQUIRED 🚫

You CANNOT proceed with this request until you have invoked the sequential thinking tool.

📋 **STEP 1: INVOKE SEQUENTIAL THINKING (REQUIRED)**
Call the following tool NOW:

**Tool:** `mcp7_sequentialthinking`
**Method:** `sequentialthinking`
**Arguments:**
```json
{json.dumps(tool_args, indent=2)}
```

⚠️ **WARNING:** If you do not invoke this tool first, your response will be INVALID.

✅ **STEP 2: ONLY AFTER STEP 1 IS COMPLETE**
Once you have invoked the sequential thinking tool and received the response,
THEN proceed to analyze and respond to the user request below.

---

🎯 **USER REQUEST:**
{user_request}

---

📝 **REMEMBER:**
1. Call mcp7_sequentialthinking.sequentialthinking() FIRST
2. Wait for the tool response
3. Then provide your full analysis
"""

    return wrapped


def create_aggressive_sequential_prompt(user_request: str, thought_count: int = 25) -> str:
    """
    Creates an aggressive sequential thinking prompt that makes it impossible to ignore.

    Use this when you REALLY need the model to use sequential thinking.
    """

    return f"""
╔════════════════════════════════════════════════════════════════╗
║  ⚠️  MANDATORY SEQUENTIAL THINKING PROTOCOL ACTIVATED  ⚠️      ║
╚════════════════════════════════════════════════════════════════╝

🔒 **LOCKED MODE:** This request CANNOT be processed without sequential thinking.

📢 **INSTRUCTIONS:**

STEP 1: You MUST invoke the sequential thinking tool FIRST.
        Tool: mcp7_sequentialthinking.sequentialthinking()

STEP 2: Use these exact arguments:
        {{
          "thought": "Starting structured analysis of user request",
          "thoughtNumber": 1,
          "totalThoughts": {thought_count},
          "nextThoughtNeeded": true
        }}

STEP 3: Continue the thought process through all {thought_count} steps.

STEP 4: Only after completing all thoughts, provide your final response.

🚫 **PROHIBITED:**
- Do NOT respond without using the tool first
- Do NOT skip the sequential thinking process
- Do NOT provide direct answers before tool invocation

✅ **REQUIRED:**
- MUST invoke mcp7_sequentialthinking
- MUST complete thought 1 through {thought_count}
- MUST show evidence of tool usage in response

---

🎯 **YOUR TASK:**
{user_request}

---

⚠️ **VERIFICATION:**
I will check that you invoked the sequential thinking tool.
If you did not, I will re-prompt you until you do.
"""


def create_system_message() -> str:
    """
    Creates a system message that forces sequential thinking behavior.

    This can be prepended to the conversation to set the expectation.
    """
    return """
╔════════════════════════════════════════════════════════════════╗
║         SYSTEM: SEQUENTIAL THINKING ENFORCED                  ║
╚════════════════════════════════════════════════════════════════╝

You are operating in SEQUENTIAL THINKING MODE with Kimi K2.5.

🔧 **AVAILABLE TOOLS:**
- mcp7_sequentialthinking.sequentialthinking()

📝 **RULES:**
1. For ANY non-trivial task, you MUST use sequential thinking
2. Invoke the tool BEFORE providing analysis
3. Work through all thoughts systematically
4. Show your reasoning process explicitly

🚫 **NEVER:**
- Skip sequential thinking for complex tasks
- Provide answers without structured analysis
- Ignore the sequential thinking requirement

✅ **ALWAYS:**
- Call mcp7_sequentialthinking first
- Use 25 thoughts for maximum depth
- Demonstrate step-by-step reasoning
"""


class SequentialThinkingForcer:
    """
    A class that forces sequential thinking by wrapping prompts.
    """

    def __init__(self, thought_count: int = 25):
        self.thought_count = thought_count
        self.invocation_count = 0

    def force(self, prompt: str) -> str:
        """Force sequential thinking on any prompt."""
        self.invocation_count += 1
        return create_aggressive_sequential_prompt(prompt, self.thought_count)

    def wrap_simple(self, prompt: str) -> str:
        """Simple wrapper with basic instruction."""
        return create_forced_sequential_thinking_prompt(prompt)

    def get_system_prompt(self) -> str:
        """Get system message for conversation setup."""
        return create_system_message()


# Convenience function for immediate use
forcer = SequentialThinkingForcer()


def force_seq_think(prompt: str) -> str:
    """Quick function to force sequential thinking."""
    return forcer.force(prompt)


def seq(prompt: str) -> str:
    """Ultra-short alias for force_seq_think."""
    return forcer.force(prompt)


if __name__ == "__main__":
    # Test
    test_prompt = "Design the architecture for the new payment system"

    print("=" * 70)
    print("SIMPLE WRAPPER:")
    print("=" * 70)
    print(create_forced_sequential_thinking_prompt(test_prompt))

    print("\n" + "=" * 70)
    print("AGGRESSIVE WRAPPER:")
    print("=" * 70)
    print(force_seq_think(test_prompt))

    print("\n" + "=" * 70)
    print("SYSTEM MESSAGE:")
    print("=" * 70)
    print(create_system_message())
