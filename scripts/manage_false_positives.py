#!/usr/bin/env python3
"""
Human-in-the-Loop False Positive Management
Allows humans to review and mark violations as false positives
"""

import json
import sys
from datetime import datetime
from pathlib import Path


def load_review_log():
    """Load the review log."""
    review_path = Path("cache/review_log.json")
    if not review_path.exists():
        print("No review log found. Run the validator first.")
        return []

    with open(review_path, "r") as f:
        return json.load(f)

def load_false_positives():
    """Load known false positives."""
    fp_path = Path("cache/false_positives.json")
    if fp_path.exists():
        with open(fp_path, "r") as f:
            return json.load(f)
    return {"false_positives": [], "last_updated": None}

def save_false_positives(fp_data):
    """Save false positives."""
    fp_path = Path("cache/false_positives.json")
    with open(fp_path, "w") as f:
        json.dump(fp_data, f, indent=2)

def show_pending_reviews():
    """Show unreviewed violations."""
    log = load_review_log()
    pending = [entry for entry in log if not entry["reviewed"]]

    if not pending:
        print("✅ No pending reviews!")
        return

    print(f"\n📋 Pending Reviews ({len(pending)}):")
    print("-" * 80)

    for i, entry in enumerate(pending, 1):
        print(f"\n{i}. [{entry['agent']}] Key {entry['key']}")
        print(f"   Time: {entry['timestamp'][:19]}")
        print(f"   Details: {entry['details']}")
        print(f"   ID: {entry['agent']}_{entry['key']}")

def mark_false_positive(agent_key):
    """Mark a violation as false positive."""
    # Parse agent_key (e.g., "SafetyInspector_4")
    parts = agent_key.split("_")
    if len(parts) < 2:
        print("Invalid format. Use: AgentName_KeyNumber")
        return

    agent = "_".join(parts[:-1])
    key = int(parts[-1])

    # Update review log
    log = load_review_log()
    for entry in log:
        if entry["agent"] == agent and entry["key"] == key and not entry["reviewed"]:
            entry["reviewed"] = True
            entry["is_false_positive"] = True
            entry["review_time"] = datetime.now().isoformat()
            break

    # Save updated log
    with open("cache/review_log.json", "w") as f:
        json.dump(log, f, indent=2)

    # Update false positives list
    fp_data = load_false_positives()
    if agent_key not in fp_data["false_positives"]:
        fp_data["false_positives"].append(agent_key)
        fp_data["last_updated"] = datetime.now().isoformat()
        save_false_positives(fp_data)

    print(f"✅ Marked {agent_key} as false positive")

def mark_valid_violation(agent_key):
    """Mark a violation as valid (not false positive)."""
    parts = agent_key.split("_")
    if len(parts) < 2:
        print("Invalid format. Use: AgentName_KeyNumber")
        return

    agent = "_".join(parts[:-1])
    key = int(parts[-1])

    # Update review log
    log = load_review_log()
    for entry in log:
        if entry["agent"] == agent and entry["key"] == key and not entry["reviewed"]:
            entry["reviewed"] = True
            entry["is_false_positive"] = False
            entry["review_time"] = datetime.now().isoformat()
            break

    # Save updated log
    with open("cache/review_log.json", "w") as f:
        json.dump(log, f, indent=2)

    print(f"✅ Marked {agent_key} as valid violation")

def show_stats():
    """Show review statistics."""
    log = load_review_log()
    load_false_positives()

    total = len(log)
    reviewed = sum(1 for e in log if e["reviewed"])
    false_positives = sum(1 for e in log if e["is_false_positive"] == True)
    valid = sum(1 for e in log if e["is_false_positive"] == False)
    pending = total - reviewed

    print("\n📊 Review Statistics:")
    print(f"   Total violations: {total}")
    print(f"   Reviewed: {reviewed}")
    print(f"   Pending: {pending}")
    print(f"   False positives: {false_positives}")
    print(f"   Valid violations: {valid}")
    print(f"   False positive rate: {false_positives/max(1, reviewed):.1%}")

def main():
    """Main CLI interface."""
    if len(sys.argv) < 2:
        print("Usage: python manage_false_positives.py <command>")
        print("\nCommands:")
        print("  show     - Show pending reviews")
        print("  fp <id>  - Mark as false positive")
        print("  valid <id> - Mark as valid violation")
        print("  stats    - Show statistics")
        print("\nExample:")
        print("  python manage_false_positives.py show")
        print("  python manage_false_positives.py fp SafetyInspector_4")
        return

    command = sys.argv[1]

    if command == "show":
        show_pending_reviews()
    elif command == "fp" and len(sys.argv) == 3:
        mark_false_positive(sys.argv[2])
    elif command == "valid" and len(sys.argv) == 3:
        mark_valid_violation(sys.argv[2])
    elif command == "stats":
        show_stats()
    else:
        print("Invalid command or missing arguments.")

if __name__ == "__main__":
    main()
