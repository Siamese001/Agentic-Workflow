#!/usr/bin/env python3
"""
Simple test script for SequentialThinking pattern.
Tests the core logic without external dependencies.
"""

import logging

from cognitive_node import CognitiveNode

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TestSequentialThinking")


def test_sequential_thinking():
    """Test the SequentialThinking implementation."""
    # print("🧠 Testing Sequential Thinking Pattern...")  # [Security Fix]

    # Create CognitiveNode instance
    brain = CognitiveNode()

    # Test with a simple goal
    test_goal = "Create a Python function that calculates the factorial of a number recursively"

    # print(f"\nGoal: {test_goal}")  # [Security Fix]
    # print("\n" + "="*50)  # [Security Fix]

    try:
        # Run sequential thinking
        result = brain.sequential_think(test_goal, max_steps=3)

        # Display results
        # print(f"\n✅ Sequential Thinking Completed!")  # [Security Fix]
        # print(f"Status: {result.get('status', 'unknown')}")  # [Security Fix]
        # print(f"Steps taken: {result.get('sequential_thinking_steps', 0)}")  # [Security Fix]

        if 'code' in result:
            # print(f"\n📝 Generated Code:")  # [Security Fix]
            # print("-" * 40)  # [Security Fix]
            # print(result['code'])  # [Security Fix]
            # print("-" * 40)  # [Security Fix]

        if 'explanation' in result:
            # print(f"\n💡 Explanation: {result['explanation']}")  # [Security Fix]

        if 'thought_history' in result:
            # print(f"\n🤔 Thought Process:")  # [Security Fix]
            for thought in result['thought_history']:
                # print(  # [Security Fix]
                    f"  Step {thought['step']}: {thought['thought'][:100]}...")

    except Exception as e:
    pass
# print(f"\n❌ Test failed with error: {e}")  # [Security Fix]
        logger.exception("Detailed error information:")

    # print("\n" + "="*50)  # [Security Fix]


if __name__ == "__main__":
    test_sequential_thinking()

