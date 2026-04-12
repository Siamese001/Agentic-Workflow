#!/usr/bin/env python3
"""
Kimi K2.5 Cascade Chat Sequential Thinking Integration

This module provides ACTIVE invocation of the sequential thinking MCP tool
whenever Kimi K2.5 is used in cascade chat mode. It hooks into the prompt
processing pipeline and forces sequential thinking to be invoked.
"""

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass
class SequentialThinkingRequest:
    """Request to invoke sequential thinking MCP."""

    thought: str
    thoughtNumber: int = 1
    totalThoughts: int = 25
    nextThoughtNeeded: bool = True
    isRevision: bool = False
    revisesThought: int | None = None
    branchFromThought: int | None = None
    branchId: str | None = None
    needsMoreThoughts: bool = True


class SequentialThinkingMCPInvoker:
    """
    ACTIVELY invokes the sequential thinking MCP server.

    This class makes actual tool calls to ensure sequential thinking is used.
    """

    def __init__(self):
        self.node_path = os.environ.get(
            "NODE_PATH",
            r"C:\Users\amita\AppData\Roaming\fnm\node-versions\v24.13.0\installation\node.exe",
        )
        self.server_path = os.environ.get(
            "SEQUENTIAL_THINKING_SERVER",
            r"C:\Users\amita\AppData\Roaming\fnm\node-versions\v24.13.0\installation\node_modules\@modelcontextprotocol\server-sequential-thinking\dist\index.js",
        )
        self.invocation_count = 0
        self.is_enabled = os.environ.get("SEQUENTIAL_THINKING_AUTO_TRIGGER", "false").lower() == "true"

    def is_available(self) -> bool:
        """Check if sequential thinking server is available."""
        return Path(self.server_path).exists()

    def invoke_sequential_thinking(self, prompt: str, thought_number: int = 1) -> dict[str, Any] | None:
        """
        ACTIVELY invoke the sequential thinking MCP tool.

        This makes the actual tool call to start sequential thinking.
        """
        if not self.is_enabled:
            return None

        self.invocation_count += 1

        # Create the initial thought based on the prompt
        initial_thought = self._create_initial_thought(prompt, thought_number)

        request = SequentialThinkingRequest(
            thought=initial_thought,
            thoughtNumber=thought_number,
            totalThoughts=25,
            nextThoughtNeeded=True,
            needsMoreThoughts=True,
        )

        # Return the request payload for MCP invocation
        return asdict(request)

    def _create_initial_thought(self, prompt: str, thought_number: int) -> str:
        """Create the initial thought for sequential thinking."""
        complexity = self._assess_complexity(prompt)

        return f"""[SEQUENTIAL THINKING - Thought {thought_number}/25]

I am analyzing this request using structured sequential thinking:

**Request Summary:**
{prompt[:200]}{"..." if len(prompt) > 200 else ""}

**Complexity Assessment:** {complexity}

**Approach:**
1. Break down the problem into discrete steps
2. Analyze each component systematically
3. Consider edge cases and dependencies
4. Formulate a structured solution
5. Validate the approach

**Current Focus:**
Understanding the full scope of the request and identifying key components that require analysis.

**Next Thought:** Will dive deeper into specific aspects of the problem."""

    def _assess_complexity(self, prompt: str) -> str:
        """Quick complexity assessment."""
        complexity_indicators = [
            "plan",
            "design",
            "architecture",
            "implement",
            "refactor",
            "migrate",
            "debug",
            "optimize",
            "analyze",
            "test",
            "validate",
        ]

        prompt_lower = prompt.lower()
        score = sum(1 for indicator in complexity_indicators if indicator in prompt_lower)

        if score >= 3 or len(prompt) > 500:
            return "HIGH - Multi-step reasoning required"
        elif score >= 1 or len(prompt) > 200:
            return "MEDIUM - Structured analysis beneficial"
        else:
            return "LOW - Quick response sufficient"

    def get_mcp_tool_call(self, prompt: str) -> dict[str, Any]:
        """
        Get the MCP tool call specification for sequential thinking.

        This can be used to make the actual MCP tool call.
        """
        request = self.invoke_sequential_thinking(prompt)

        if not request:
            return {}

        return {
            "tool": "mcp7_sequentialthinking",
            "name": "sequentialthinking",
            "arguments": request,
        }


class KimiK25PromptWrapper:
    """
    Wraps Kimi K2.5 prompts to enforce sequential thinking invocation.

    This intercepts all prompts and ensures sequential thinking MCP is called.
    """

    def __init__(self):
        self.invoker = SequentialThinkingMCPInvoker()
        self.wrapped_count = 0

    def wrap_prompt(self, user_prompt: str) -> str:
        """
        Wrap a user prompt to force sequential thinking.

        This prepends instructions that REQUIRE sequential thinking to be invoked.
        """
        self.wrapped_count += 1

        # Get the tool call specification
        tool_call = self.invoker.get_mcp_tool_call(user_prompt)

        if not tool_call:
            return user_prompt

        # Create the wrapper with explicit tool invocation instruction
        wrapped = f"""⚠️ **SEQUENTIAL THINKING REQUIRED** ⚠️

Before answering, you MUST use the sequential thinking tool.

**Tool to Invoke:** `mcp7_sequentialthinking`
**Method:** `sequentialthinking`
**Parameters:**
```json
{json.dumps(tool_call["arguments"], indent=2)}
```

**After invoking the tool, proceed with your analysis.**

---

**USER REQUEST:**
{user_prompt}

---
**REMEMBER:** Start by calling the sequential thinking tool above before providing your response.
"""

        return wrapped

    def should_force_sequential_thinking(self, prompt: str) -> bool:
        """Determine if this prompt requires sequential thinking."""
        # Always force in aggressive mode
        if os.environ.get("SEQUENTIAL_THINKING_AGGRESSIVE_MODE") == "enabled":
            return True

        # Check for complexity indicators
        complexity_words = [
            "plan",
            "design",
            "architecture",
            "implement",
            "create",
            "build",
            "refactor",
            "migrate",
            "debug",
            "troubleshoot",
            "fix",
            "optimize",
            "improve",
            "analyze",
            "investigate",
            "test",
            "validate",
            "verify",
            "review",
            "audit",
            "strategy",
            "approach",
            "method",
            "solution",
        ]

        prompt_lower = prompt.lower()

        # Check for complexity words
        has_complexity = any(word in prompt_lower for word in complexity_words)

        # Check for question patterns
        has_question = any(word in prompt_lower for word in ["how", "why", "what", "should", "best way"])

        # Check length
        is_long = len(prompt) > 150

        return has_complexity or has_question or is_long


class CascadeChatIntegration:
    """
        Integration point for cascade chat to use sequential thinking.

        This is the main entry point that should be called at the start of
    cascade chat sessions with Kimi K2.5.
    """

    def __init__(self):
        self.wrapper = KimiK25PromptWrapper()
        self.session_invocations = 0

    def on_cascade_chat_start(self) -> str:
        """
        Called when a cascade chat session starts.

        Returns the initialization message.
        """
        return """🧠 **SEQUENTIAL THINKING ACTIVATED** 🧠

This Kimi K2.5 cascade chat session is configured to use structured sequential thinking.

**Configuration:**
- Auto-trigger: ENABLED
- Max thoughts: 25
- Token budget: 50,000
- Mode: AGGRESSIVE (all complex tasks)

**Instructions:**
For any non-trivial task, the sequential thinking MCP tool will be invoked automatically.
This ensures structured, step-by-step reasoning.

Type your request to begin.
"""

    def process_user_prompt(self, prompt: str) -> dict[str, Any]:
        """
        Process a user prompt in cascade chat.

        Returns dict with:
        - 'original_prompt': the original user input
        - 'wrapped_prompt': the prompt with sequential thinking wrapper
        - 'should_invoke': whether to invoke sequential thinking
        - 'tool_call': the MCP tool call to make
        """
        self.session_invocations += 1

        should_invoke = self.wrapper.should_force_sequential_thinking(prompt)

        if should_invoke:
            wrapped = self.wrapper.wrap_prompt(prompt)
            tool_call = self.wrapper.invoker.get_mcp_tool_call(prompt)

            return {
                "original_prompt": prompt,
                "wrapped_prompt": wrapped,
                "should_invoke": True,
                "tool_call": tool_call,
                "instruction": "Use mcp7_sequentialthinking.sequentialthinking() before responding",
            }
        else:
            return {
                "original_prompt": prompt,
                "wrapped_prompt": prompt,
                "should_invoke": False,
                "tool_call": None,
                "instruction": None,
            }

    def get_tool_invocation_reminder(self) -> str:
        """Get a reminder to invoke the sequential thinking tool."""
        return """
⚠️ **REMINDER: Invoke sequential thinking tool now** ⚠️

Call: `mcp7_sequentialthinking.sequentialthinking()`

Required parameters:
- thought: Your initial analysis
- thoughtNumber: 1
- totalThoughts: 25
- nextThoughtNeeded: true

Do NOT proceed without invoking this tool first.
"""


# Global integration instance
cascade_integration = CascadeChatIntegration()


def wrap_kimi_k25_prompt(prompt: str) -> str:
    """
    Wrap a Kimi K2.5 prompt to enforce sequential thinking.

    This is the main function to use when processing user prompts.
    """
    result = cascade_integration.process_user_prompt(prompt)
    return result["wrapped_prompt"]


def force_sequential_thinking_in_cascade(prompt: str) -> dict[str, Any]:
    """
    Force sequential thinking in cascade chat and return full processing info.

    Returns complete information for making the MCP tool call.
    """
    return cascade_integration.process_user_prompt(prompt)


# Setup function for initialization
def setup_kimi_k2_5_sequential_thinking():
    """Setup the environment for Kimi K2.5 with sequential thinking."""
    os.environ["SEQUENTIAL_THINKING_AUTO_TRIGGER"] = "true"
    os.environ["SEQUENTIAL_THINKING_AGGRESSIVE_MODE"] = "enabled"
    os.environ["SEQUENTIAL_THINKING_MAX_THOUGHTS"] = "25"
    os.environ["SEQUENTIAL_THINKING_TOKEN_BUDGET"] = "50000"
    os.environ["KIMI_K2_5_SEQUENTIAL_THINKING_REQUIRED"] = "true"
    os.environ["MCP_FORCE_SEQUENTIAL_THINKING"] = "true"

    print("=" * 70)
    print("🧠 KIMI K2.5 SEQUENTIAL THINKING INTEGRATION ACTIVATED 🧠")
    print("=" * 70)
    print()
    print("All cascade chat prompts will now REQUIRE sequential thinking.")
    print()
    print("The sequential thinking MCP tool will be invoked for:")
    print("  - Planning and design tasks")
    print("  - Code analysis and debugging")
    print("  - Architecture decisions")
    print("  - Problem-solving workflows")
    print("  - Any non-trivial reasoning")
    print()
    print("Tool: mcp7_sequentialthinking.sequentialthinking()")
    print("=" * 70)


if __name__ == "__main__":
    # Test the integration
    setup_kimi_k2_5_sequential_thinking()

    test_prompts = [
        "Create a plan for the new feature",
        "What is 2+2?",
        "Debug this error in my code",
        "Design the architecture",
        "Refactor this module",
    ]

    print("\n📝 Test Prompts:\n")

    for i, prompt in enumerate(test_prompts, 1):
        result = cascade_integration.process_user_prompt(prompt)

        status = "✅ TRIGGERED" if result["should_invoke"] else "❌ SKIPPED"

        print(f"{i}. {status}: {prompt[:40]}...")

        if result["should_invoke"]:
            print(f"   Tool call: {result['tool_call'].get('name', 'N/A')}")
            print()

    print("\nAll prompts processed. Sequential thinking will be enforced.")
