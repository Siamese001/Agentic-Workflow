#!/usr/bin/env python3
"""
Simplified Dirty Data Simulator - Demonstrates CanonValidator concepts
Uses in-memory storage with hash and semantic similarity for duplicate detection.
"""

import hashlib
import logging
import math
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List

# Configure clean output logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("DirtyDataSim")


def print_section(title: str) -> None:
    """Print a formatted section header."""
    # print(f"\n{'='*60}\n🔸 {title}\n{'='*60}")  # [Security Fix]


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    dot = sum(x*y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x*x for x in a))
    mag_b = math.sqrt(sum(x*x for x in b))
    return dot / (mag_a * mag_b) if mag_a and mag_b else 0


def mock_embedding(text: str) -> List[float]:
    """Generate a mock embedding based on text hash."""
    # Simple deterministic "embedding" based on text content
    hash_obj = hashlib.sha256(text.encode())
    hex_hash = hash_obj.hexdigest()

    # Convert hex to float values
    embedding = []
    for i in range(0, len(hex_hash), 2):
        hex_pair = hex_hash[i:i+2]
        val = int(hex_pair, 16) / 255.0  # Normalize to 0-1
        embedding.append(val)

    # Pad/trim to 384 dimensions
    while len(embedding) < 384:
        embedding.append(0.0)
    return embedding[:384]


class SimpleCanonValidator:
    """Simplified Canon Validator using in-memory storage."""

    def __init__(self):
        self.storage = {}  # id -> {hash, embedding, content, metadata}
        self.hash_index = {}  # hash -> id

    def check_and_learn(self, code: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Check for duplicates and store if unique."""
        start_time = datetime.utcnow()

        # Generate content hash for exact duplicate detection
        content_hash = hashlib.sha256(code.encode()).hexdigest()

        # Check for exact duplicate (L1)
        if content_hash in self.hash_index:
            stored_id = self.hash_index[content_hash]
            return {
                "is_valid": False,
                "confidence": 1.0,
                "source": "L1_Exact_Duplicate",
                "matched_pattern": stored_id,
                "recommendation": "Exact duplicate found - reject",
                "query_time_ms": (datetime.utcnow() - start_time).total_seconds() * 1000
            }

        # Generate embedding for semantic similarity (L2)
        embedding = mock_embedding(code)

        # Check for semantic duplicates
        for stored_id, data in self.storage.items():
            similarity = cosine_similarity(embedding, data['embedding'])
            if similarity > 0.85:  # High similarity threshold
                return {
                    "is_valid": False,
                    "confidence": similarity,
                    "source": "L2_Semantic_Duplicate",
                    "matched_pattern": stored_id,
                    "recommendation": f"Semantic duplicate found ({similarity:.2f} similarity) - reject",
                    "query_time_ms": (datetime.utcnow() - start_time).total_seconds() * 1000
                }

        # No duplicates found - store the new pattern
        pattern_id = str(uuid.uuid4())
        self.storage[pattern_id] = {
            "hash": content_hash,
            "embedding": embedding,
            "content": code,
            "metadata": context or {}
        }
        self.hash_index[content_hash] = pattern_id

        return {
            "is_valid": True,
            "confidence": 1.0,
            "source": "no_match",
            "matched_pattern": None,
            "recommendation": "New pattern - stored successfully",
            "pattern_id": pattern_id,
            "query_time_ms": (datetime.utcnow() - start_time).total_seconds() * 1000
        }


def run_simulation() -> None:
    """Run the dirty data simulation scenarios."""
    print_section("INITIALIZING SIMPLIFIED CANON VALIDATOR")

    # Initialize the validator
    validator = SimpleCanonValidator()

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

    # print(f"📌 ANCHOR TRUTH: Python function for cognitive/action separation")  # [Security Fix]

    # ---------------------------------------------------------
    # SCENARIO 1: THE SEED (New Unique Knowledge)
    # ---------------------------------------------------------
    print_section("TEST 1: INGESTING ANCHOR TRUTH (Should Succeed)")

    result_1 = validator.check_and_learn(anchor_text, {"type": "anchor"})
    # print(f"Result: {result_1}")  # [Security Fix]

    if result_1.get('is_valid') and result_1.get('source') == 'no_match':
        # print("✅ PASS: Anchor truth ingested successfully.")  # [Security Fix]
    else:
        # print(f"❌ FAIL: Anchor truth was rejected. Reason: {result_1}")  # [Security Fix]
        return  # Stop if we can't seed

    # Wait for consistency (demonstrates real-world delay)
    # print("⏳ Waiting 2s for consistency...")  # [Security Fix]
    time.sleep(2)

    # ---------------------------------------------------------
    # SCENARIO 2: THE CLONE (Exact Duplicate)
    # ---------------------------------------------------------
    print_section("TEST 2: EXACT DUPLICATE (Should be blocked by L1/Hash)")

    # Same content, different context
    result_2 = validator.check_and_learn(anchor_text, {"type": "clone"})
    # print(f"Result: {result_2}")  # [Security Fix]

    # We expect exact duplicate detection
    if result_2.get('source') == 'L1_Exact_Duplicate':
        # print("✅ PASS: Exact duplicate was correctly filtered by hash check.")  # [Security Fix]
    else:
        # print(f"⚠️ WARNING: Duplicate was not detected properly.")  # [Security Fix]

        # ---------------------------------------------------------
        # SCENARIO 3: THE MIMIC (Semantic Duplicate)
        # ---------------------------------------------------------
    print_section(
        "TEST 3: SEMANTIC VARIATION (Should be blocked by L2/Vector)")

    # Different code, similar logic
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

    # If semantic similarity is working, this should be flagged
    if result_3.get('source') == 'L2_Semantic_Duplicate':
        # print("✅ PASS: Semantic duplicate was correctly identified via similarity.")  # [Security Fix]
    else:
        # print(f"⚠️ WARNING: Semantic duplicate was treated as new (similarity too low).")  # [Security Fix]

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
    else:
        # print(f"❌ FAIL: Novel data was rejected.")  # [Security Fix]

        # Show final storage state
    print_section("FINAL STORAGE STATE")
    # print(f"Total patterns stored: {len(validator.storage)}")  # [Security Fix]
    for pid, data in validator.storage.items():
        # print(f"  - {pid[:8]}... ({data['metadata'].get('type', 'unknown')})")  # [Security Fix]

    print_section("SIMULATION COMPLETE")


if __name__ == "__main__":
    run_simulation()

