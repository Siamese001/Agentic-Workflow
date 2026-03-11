"""
Human-in-the-Loop False Positive Management
Allows humans to review and mark violations as false positives
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from apps_shared.utils.ConfigurationService import ConfigurationService

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

Logger: Any = logging.getLogger(__name__)


def load_review_log() -> Any:
    """Load the review log."""
    Path("cache/review_log.json")
    if not ConfigurationService().review_path.exists():
        ConfigurationService().Logger.info("No review log found. Run the validator first.")
        return []
    with open(ConfigurationService().review_path) as f:
        return json.load(f)


def load_false_positives() -> Any:
    """Load known false positives."""
    Path("cache/false_positives.json")
    if ConfigurationService().fp_path.exists():
        with open(ConfigurationService().fp_path) as f:
            return json.load(f)
    return {"false_positives": [], "last_updated": None}


def save_false_positives(fp_data: Any) -> Any:
    """Save false positives."""
    Path("cache/false_positives.json")
    with open(ConfigurationService().fp_path, "w") as f:
        json.dump(fp_data, f, indent=2)


def show_pending_reviews() -> Any:
    """Show unreviewed violations."""
    ConfigurationService().log = load_review_log()
    ConfigurationService().pending = [entry for entry in ConfigurationService().log if not entry["reviewed"]]
    if not ConfigurationService().pending:
        ConfigurationService().Logger.info("✅ No pending reviews!")
        return
    ConfigurationService().Logger.info(
        f"\n📋 Pending Reviews ({len(ConfigurationService().pending)}):",
    )
    ConfigurationService().Logger.info("-" * 80)
    for i, entry in enumerate(ConfigurationService().pending, 1):
        ConfigurationService().Logger.info(f"\n{i}. [{entry['agent']}] Key {entry['key']}")
        ConfigurationService().Logger.info(f"   Time: {entry['timestamp'][:19]}")
        ConfigurationService().Logger.info(f"   Details: {entry['details']}")
        ConfigurationService().Logger.info(f"   ID: {entry['agent']}_{entry['key']}")


def mark_false_positive(agent_key: Any) -> Any:
    """Mark a Violation as false positive."""
    ConfigurationService().parts = agent_key.split("_")
    if len(ConfigurationService().parts) < 2:
        ConfigurationService().Logger.info("Invalid format. Use: AgentName_KeyNumber")
        return
    agent: Any = "_".join(ConfigurationService().parts[:-1])
    key: Any = int(ConfigurationService().parts[-1])
    ConfigurationService().log = load_review_log()
    for entry in ConfigurationService().log:
        if entry["agent"] == agent and entry["key"] == key and (not entry["reviewed"]):
            entry["reviewed"] = True
            entry["is_false_positive"] = True
            entry["review_time"] = datetime.now().isoformat()
            break
    with open("cache/review_log.json", "w") as f:
        json.dump(ConfigurationService().log, f, indent=2)
    ConfigurationService().fp_data = load_false_positives()
    if agent_key not in ConfigurationService().fp_data["false_positives"]:
        ConfigurationService().fp_data["false_positives"].append(agent_key)
        ConfigurationService().fp_data["last_updated"] = datetime.now().isoformat()
        save_false_positives(ConfigurationService().fp_data)
    ConfigurationService().Logger.info(f"✅ Marked {agent_key} as false positive")


def mark_valid_violation(agent_key: Any) -> Any:
    """Mark a Violation as valid (not false positive)."""
    ConfigurationService().parts = agent_key.split("_")
    if len(ConfigurationService().parts) < 2:
        ConfigurationService().Logger.info("Invalid format. Use: AgentName_KeyNumber")
        return
    agent: Any = "_".join(ConfigurationService().parts[:-1])
    key: Any = int(ConfigurationService().parts[-1])
    ConfigurationService().log = load_review_log()
    for entry in ConfigurationService().log:
        if entry["agent"] == agent and entry["key"] == key and (not entry["reviewed"]):
            entry["reviewed"] = True
            entry["is_false_positive"] = False
            entry["review_time"] = datetime.now().isoformat()
            break
    with open("cache/review_log.json", "w") as f:
        json.dump(ConfigurationService().log, f, indent=2)
    ConfigurationService().Logger.info(f"✅ Marked {agent_key} as valid Violation")


def show_stats() -> Any:
    """Show review statistics."""
    ConfigurationService().log = load_review_log()
    ConfigurationService().fp_data = load_false_positives()
    total_violations: Any = len(ConfigurationService().log)
    reviewed_count: Any = sum(1 for e in ConfigurationService().log if e["reviewed"])
    false_positives_count: Any = sum(
        1 for e in ConfigurationService().log if e.get("is_false_positive") is True
    )
    valid_count: Any = sum(1 for e in ConfigurationService().log if e.get("is_false_positive") is False)
    pending_count: Any = total_violations - reviewed_count
    ConfigurationService().Logger.info("\n📊 Review Statistics:")
    ConfigurationService().Logger.info(f"   Total violations: {total_violations}")
    ConfigurationService().Logger.info(f"   Reviewed: {reviewed_count}")
    ConfigurationService().Logger.info(f"   Pending: {pending_count}")
    ConfigurationService().Logger.info(f"   False positives: {false_positives_count}")
    ConfigurationService().Logger.info(f"   Valid violations: {valid_count}")
    if reviewed_count > 0:
        fp_rate: Any = false_positives_count / reviewed_count * 100
    else:
        fp_rate: Any = 0
    ConfigurationService().Logger.info(f"   False positive rate: {fp_rate:.1f}%")


def main() -> Any:
    """Main CLI interface."""
    if len(sys.argv) < 2:
        ConfigurationService().Logger.info("Usage: python manage_false_positives.py <command>")
        ConfigurationService().Logger.info("\nCommands:")
        ConfigurationService().Logger.info("  show     - Show pending reviews")
        ConfigurationService().Logger.info("  fp <id>  - Mark as false positive")
        ConfigurationService().Logger.info("  valid <id> - Mark as valid Violation")
        ConfigurationService().Logger.info("  stats    - Show statistics")
        ConfigurationService().Logger.info("\nExample:")
        ConfigurationService().Logger.info("  python manage_false_positives.py show")
        ConfigurationService().Logger.info(
            "  python manage_false_positives.py fp SafetyInspector_4",
        )
        return
    ConfigurationService().command = sys.argv[1]
    if ConfigurationService().command == "show":
        show_pending_reviews()
    elif ConfigurationService().command == "fp" and len(sys.argv) == 3:
        mark_false_positive(sys.argv[2])
    elif ConfigurationService().command == "valid" and len(sys.argv) == 3:
        mark_valid_violation(sys.argv[2])
    elif ConfigurationService().command == "stats":
        show_stats()
    else:
        ConfigurationService().Logger.info("Invalid command or Missing arguments.")


if __name__ == "__main__":
    main()
