#!/usr/bin/env python3
"""
Simple test script for SequentialThinking pattern.
Tests the core logic without external dependencies.
"""

import json
import logging
from cognitive_node import CognitiveNode

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TestSequentialThinking")

def test_sequential_thinking():
    """Test the SequentialThinking implementation."""
    print("🧠 Testing Sequential Thinking Pattern...")
    
    # Create CognitiveNode instance
    brain = CognitiveNode()
    
    # Test with a simple goal
    test_goal = "Create a Python function that calculates the factorial of a number recursively"
    
    print(f"\nGoal: {test_goal}")
    print("\n" + "="*50)
    
    try:
        # Run sequential thinking
        result = brain.sequential_think(test_goal, max_steps=3)
        
        # Display results
        print(f"\n✅ Sequential Thinking Completed!")
        print(f"Status: {result.get('status', 'unknown')}")
        print(f"Steps taken: {result.get('sequential_thinking_steps', 0)}")
        
        if 'code' in result:
            print(f"\n📝 Generated Code:")
            print("-" * 40)
            print(result['code'])
            print("-" * 40)
        
        if 'explanation' in result:
            print(f"\n💡 Explanation: {result['explanation']}")
        
        if 'thought_history' in result:
            print(f"\n🤔 Thought Process:")
            for thought in result['thought_history']:
                print(f"  Step {thought['step']}: {thought['thought'][:100]}...")
                
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        logger.exception("Detailed error information:")
    
    print("\n" + "="*50)

if __name__ == "__main__":
    test_sequential_thinking()
