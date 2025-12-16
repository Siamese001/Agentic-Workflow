#!/usr/bin/env python3
"""
Dirty Data Simulator - Stress-tests the CanonValidator pipeline
Feeds duplicates, variations, and new data to ensure proper filtering.
"""

import logging
import time

from dotenv import load_dotenv

# Import the connectivity-hardened modules
from agent_logic_connectivity import CanonValidator

# Configure clean output logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("DirtyDataSim")  # GLOBAL: Review if this should be constant


def print_section(title: str) -> None:
    """Print a formatted section header."""
    # print(f"\n{'='*60}\n🔸 {title}\n{'='*60}")  # [Security Fix]


def run_simulation() -> None:
    """Run the dirty data simulation scenarios."""
    load_dotenv()
    print_section("INITIALIZING CANON VALIDATOR")

    # Initialize the validator (connects to Redis/Pinecone)
    validator = CanonValidator()

    # Define our "Gold Standard" or Anchor Truth
    anchor_text = '''
def validate_cognitive_action_separation():
    """Separate cognitive plane from action plane to prevent hallucinations."""
    cognitive_state = "thinking"
    action_state = "doing"

    if cognitive_state == "thinking":
        return "Cognitive Plane Active"
    elif action_state == "doing":
        return "Action Plane Active"
    else:
        return "Planes Separated"
'''

    # print(f"📌 ANCHOR TRUTH: '{anchor_text}'")  # [Security Fix]

    # ---------------------------------------------------------
    # SCENARIO 1: THE SEED (New Unique Knowledge)
    # ---------------------------------------------------------
    print_section("TEST 1: INGESTING ANCHOR TRUTH (Should Succeed)")

    result_1 = validator.check_and_learn(anchor_text, {"type": "anchor"})
    # print(f"Result: {result_1}")  # [Security Fix]

    if result_1.get('is_valid') and result_1.get('source') == 'no_match':
        # print("✅ PASS: Anchor truth ingested successfully.")  # [Security Fix]
        pass
    else:
        # print(f"❌ FAIL: Anchor truth was rejected. Reason: {result_1}")  # [Security Fix]
        return  # Stop if we can't seed

    # Wait for Pinecone indexing consistency (crucial for next tests)
    # print("⏳ Waiting 5s for consistency...")  # [Security Fix]
    time.sleep(5)

    # ---------------------------------------------------------
    # SCENARIO 2: THE CLONE (Exact Duplicate)
    # ---------------------------------------------------------
    print_section("TEST 2: EXACT DUPLICATE (Should be blocked by L1/Hash)")

    # Same content, different ID
    result_2 = validator.check_and_learn(anchor_text, {"type": "clone"})
    # print(f"Result: {result_2}")  # [Security Fix]

    # We expect a match in L1 or L2 for duplicates
    if result_2.get('source') in ['l1_match', 'l2_match']:
        # print("✅ PASS: Exact duplicate was correctly filtered.")  # [Security Fix]
        pass
    else:
        # print(f"⚠️ WARNING: Duplicate was ingested. (Did L1 Cache miss?)")  # [Security Fix]
        pass

        # ---------------------------------------------------------
        # SCENARIO 3: THE MIMIC (Semantic Duplicate)
        # ---------------------------------------------------------
    print_section(
        "TEST 3: SEMANTIC VARIATION (Should be blocked by L2/Vector)")

    # Different words, identical meaning
    mimic_text = '''
def prevent_hallucination_loops():
    """Split thinking layer from doing layer to avoid hallucinations."""
    thinking_layer = "cognitive"
    doing_layer = "action"

    if thinking_layer == "cognitive":
        return "Thinking Active"
    elif doing_layer == "action":
        return "Doing Active"
    else:
        return "Layers Split"
'''

    result_3 = validator.check_and_learn(mimic_text, {"type": "mimic"})
    # print(f"Result: {result_3}")  # [Security Fix]

    # If cosine similarity is working, this should be flagged as similar
    if result_3.get('source') in ['l1_match', 'l2_match']:
        # print("✅ PASS: Semantic duplicate was correctly identified via Vectors.")  # [Security Fix]
        pass
    else:
        # print(f"⚠️ WARNING: Semantic duplicate was treated as new. (Threshold might be too high?)")  # [Security Fix]
        pass

        # ---------------------------------------------------------
        # SCENARIO 4: THE NOVELTY (Completely New)
        # ---------------------------------------------------------
    print_section("TEST 4: NOVEL DATA (Should be Ingested)")

    novel_text = '''
def get_tuesday_menu():
    """Return the cafeteria menu for Tuesday."""
    menu = {
        "main": "Taco Bar",
        "sides": ["chips", "salsa", "guacamole"],
        "drinks": ["soda", "water", "juice"]
    }
    return menu
'''

    result_4 = validator.check_and_learn(novel_text, {"type": "novelty"})
    # print(f"Result: {result_4}")  # [Security Fix]

    if result_4.get('is_valid') and result_4.get('source') == 'no_match':
        # print("✅ PASS: Novel data was correctly ingested.")  # [Security Fix]
        pass
    else:
        # print(f"❌ FAIL: Novel data was rejected.")  # [Security Fix]
        pass

    print_section("SIMULATION COMPLETE")


if __name__ == "__main__":
    run_simulation()

