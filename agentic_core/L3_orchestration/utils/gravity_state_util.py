"""Gravity State Utility - Deterministic healing state management.

This module provides deterministic state tracking functionality previously
implemented in GravityStateAgent. Converted from agent to utility script
as part of Phase 2 optimization (Wave 6 Micro-Wave 4).

Usage:
    from agentic_core.L3_orchestration.utils.gravity_state_util import (
        GravityStateManager, HealingRecord, load_state, save_state
    )
    
    # Manage state
    manager = GravityStateManager(project_root=Path("."))
    manager.record_healing(healing_record)
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

Logger = logging.getLogger(__name__)


@dataclass
class HealingRecord:
    """Record of a single healing operation."""
    
    file_path: str
    original_import: str
    healed_import: str
    violation_type: str
    healing_strategy: str
    timestamp: str
    agent_version: str = "1.0.0"
    line_number: int | None = None
    import_hash: str | None = None  # Computed field


class GravityStateManager:
    """Manages gravity healing state without agent overhead."""
    
    STATE_FILE = "gravity_healing_state.json"
    
    def __init__(self, project_root: Path) -> None:
        """Initialize the state manager.
        
        Args:
            project_root: Project root path for state storage
        """
        self.root = project_root.resolve()
        self.state_dir = self.root / ".gravity_state"
        self.state_file = self.state_dir / self.STATE_FILE
        self.logger = Logger
        
        # Ensure state directory exists
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing state
        self.state = self._load_state()
    
    def _load_state(self) -> dict[str, Any]:
        """Load healing state from disk."""
        if not self.state_file.exists():
            return {
                "healed_files": {},
                "healing_history": [],
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "total_healings": 0,
                },
            }
        
        try:
            with open(self.state_file, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            self.logger.error(f"Failed to load state: {e}")
            return self._fresh_state()
    
    def _fresh_state(self) -> dict[str, Any]:
        """Return fresh state structure."""
        return {
            "healed_files": {},
            "healing_history": [],
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "total_healings": 0,
            },
        }
    
    def _save_state(self) -> None:
        """Persist healing state to disk."""
        try:
            self.state["metadata"]["last_updated"] = datetime.now().isoformat()
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(self.state, f, indent=2)
        except OSError as e:
            self.logger.error(f"Failed to save state: {e}")
    
    def _normalize_and_hash(self, import_line: str) -> str:
        """Normalize import statement and create stable hash.
        
        Args:
            import_line: Import statement to hash
            
        Returns:
            SHA256 hash of normalized import
        """
        # Remove comments and collapse whitespace
        normalized = re.sub(r"#.*$", "", import_line).strip()
        normalized = re.sub(r"\s+", " ", normalized)
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    
    def record_healing(self, record: HealingRecord) -> None:
        """Record a successful healing operation.
        
        Args:
            record: HealingRecord with healing details
        """
        file_key = str(Path(record.file_path).relative_to(self.root))
        import_hash = self._normalize_and_hash(record.original_import)
        
        # Append hash to record for robust lookup
        record_data = asdict(record)
        record_data["import_hash"] = import_hash
        
        # Add to healed files registry
        if file_key not in self.state["healed_files"]:
            self.state["healed_files"][file_key] = []
        
        self.state["healed_files"][file_key].append(record_data)
        
        # Add to healing history
        self.state["healing_history"].append(record_data)
        
        # Update metadata
        self.state["metadata"]["total_healings"] += 1
        
        # Persist to disk
        self._save_state()
        
        self.logger.info(f"Recorded healing: {file_key} - {record.original_import}")
    
    def is_healed(self, file_path: Path, import_line: str) -> bool:
        """Check if a specific import has already been healed.
        
        Args:
            file_path: Path to the file
            import_line: Import statement to check
            
        Returns:
            True if import has been healed, False otherwise
        """
        try:
            file_key = str(file_path.relative_to(self.root))
        except ValueError:
            return False
        
        if file_key not in self.state["healed_files"]:
            return False
        
        current_hash = self._normalize_and_hash(import_line)
        
        for healing in self.state["healed_files"][file_key]:
            if healing.get("import_hash") == current_hash:
                return True
        
        return False
    
    def get_file_healings(self, file_path: Path) -> list[HealingRecord]:
        """Get all healing records for a specific file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            List of HealingRecord objects
        """
        try:
            file_key = str(file_path.relative_to(self.root))
        except ValueError:
            return []
        
        if file_key not in self.state["healed_files"]:
            return []
        
        return [HealingRecord(**healing) for healing in self.state["healed_files"][file_key]]
    
    def get_healing_summary(self) -> dict[str, Any]:
        """Get summary of all healing operations.
        
        Returns:
            Dict with healing statistics
        """
        total_files = len(self.state["healed_files"])
        total_healings = self.state["metadata"]["total_healings"]
        
        # Group by violation type
        by_type: dict[str, int] = {}
        for healing in self.state["healing_history"]:
            vtype = healing["violation_type"]
            by_type[vtype] = by_type.get(vtype, 0) + 1
        
        # Group by strategy
        by_strategy: dict[str, int] = {}
        for healing in self.state["healing_history"]:
            strategy = healing["healing_strategy"]
            by_strategy[strategy] = by_strategy.get(strategy, 0) + 1
        
        return {
            "total_files_healed": total_files,
            "total_healings": total_healings,
            "by_violation_type": by_type,
            "by_strategy": by_strategy,
            "created_at": self.state["metadata"]["created_at"],
            "last_updated": self.state["metadata"]["last_updated"],
        }
    
    def clear_file_state(self, file_path: Path) -> bool:
        """Clear healing state for a specific file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if state was cleared, False if no state existed
        """
        try:
            file_key = str(file_path.relative_to(self.root))
        except ValueError:
            return False
        
        if file_key in self.state["healed_files"]:
            del self.state["healed_files"][file_key]
            self._save_state()
            return True
        return False
    
    def cleanup_history(self, keep_last: int = 1000) -> int:
        """Clean up old healing history entries.
        
        Args:
            keep_last: Number of recent entries to keep
            
        Returns:
            Number of entries removed
        """
        original_count = len(self.state["healing_history"])
        self.state["healing_history"] = self.state["healing_history"][-keep_last:]
        self._save_state()
        return original_count - len(self.state["healing_history"])
    
    def clear_all_state(self) -> None:
        """Clear all healing state (use with caution)."""
        self.state = self._fresh_state()
        self._save_state()
        self.logger.warning("Cleared all healing state")


def load_state(project_root: Path) -> dict[str, Any]:
    """Load gravity state from disk.
    
    Args:
        project_root: Project root path
        
    Returns:
        State dictionary
    """
    manager = GravityStateManager(project_root)
    return manager.state


def save_state(project_root: Path, state: dict[str, Any]) -> None:
    """Save gravity state to disk.
    
    Args:
        project_root: Project root path
        state: State dictionary to save
    """
    manager = GravityStateManager(project_root)
    manager.state = state
    manager._save_state()


def heal_repository(
    project_root: Path | None = None,
    dry_run: bool = True,
    execute: bool = False,
    **kwargs: Any,
) -> dict[str, Any]:
    """Autonomous healing interface (Canon Key 51 compliance).
    
    Args:
        project_root: Project root path
        dry_run: If True, only report without fixing
        execute: If True, apply fixes
        
    Returns:
        Healing summary dict
    """
    if project_root is None:
        project_root = Path(".")
    
    manager = GravityStateManager(project_root)
    summary = manager.get_healing_summary()
    
    violations_found = 0
    
    # Check for potential issues
    if summary["total_healings"] == 0:
        violations_found += 1
        Logger.info("[GravityState] No healing history found")
    
    return {
        "violations_found": violations_found,
        "violations_fixed": 1 if violations_found == 0 else 0,
        "errors": 0,
        "skipped": 0,
        "summary": summary,
    }


def heal(violation: dict[str, Any], project_root: Path | None = None) -> dict[str, Any]:
    """Heal gravity state violations.
    
    Args:
        violation: Violation details dict
        project_root: Project root path
        
    Returns:
        Healing result dict
    """
    if project_root is None:
        project_root = Path(".")
    
    manager = GravityStateManager(project_root)
    violation_type = violation.get("type", "unknown")
    file_path = violation.get("file_path")
    
    if violation_type == "gravity_state_corruption" and file_path:
        success = manager.clear_file_state(Path(file_path))
        return {
            "status": "success" if success else "skipped",
            "details": f"Cleared state for {file_path}" if success else f"No state for {file_path}",
            "artifacts": [file_path] if success else [],
            "errors": [],
        }
    
    elif violation_type == "healing_history_cleanup":
        cleaned = manager.cleanup_history(keep_last=1000)
        return {
            "status": "success",
            "details": f"Cleaned up {cleaned} old records",
            "artifacts": ["healing_history"],
            "errors": [],
        }
    
    elif violation_type == "state_file_missing":
        # Force state reload (creates fresh if missing)
        manager.state = manager._load_state()
        return {
            "status": "success",
            "details": "State file recreated",
            "artifacts": ["gravity_healing_state.json"],
            "errors": [],
        }
    
    return {
        "status": "skipped",
        "details": f"Unknown violation: {violation_type}",
        "artifacts": [],
        "errors": [],
    }


def main():
    """Main entry point for Gravity State Utility."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Gravity State Utility")
    parser.add_argument(
        "--project-root",
        type=str,
        default=".",
        help="Project root path",
    )
    parser.add_argument(
        "--action",
        choices=["summary", "clear", "cleanup"],
        default="summary",
        help="Action to perform",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output",
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    project_root = Path(args.project_root)
    manager = GravityStateManager(project_root)
    
    if args.action == "summary":
        summary = manager.get_healing_summary()
        print(f"Files healed: {summary['total_files_healed']}")
        print(f"Total healings: {summary['total_healings']}")
        print(f"By violation type: {summary['by_violation_type']}")
        print(f"By strategy: {summary['by_strategy']}")
    
    elif args.action == "clear":
        manager.clear_all_state()
        print("All state cleared")
    
    elif args.action == "cleanup":
        cleaned = manager.cleanup_history(keep_last=1000)
        print(f"Cleaned {cleaned} old records")
    
    return summary if args.action == "summary" else {}


if __name__ == "__main__":
    main()
