#!/usr/bin/env python3
"""
Wave State Manager - Ensures true idempotency across wave executions.

This module provides state persistence and checking to prevent
duplicate modifications and ensure waves are truly idempotent.
"""

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class WaveState:
    """State tracking for a specific wave execution."""
    wave_name: str
    execution_id: str
    timestamp: str
    files_modified: dict[str, str]  # file_path -> hash
    patterns_applied: dict[str, set[str]]  # pattern_type -> set of applied patterns
    metrics: dict[str, Any]
    is_complete: bool = False


class WaveStateManager:
    """Manages wave execution state for idempotency."""

    def __init__(self, state_file: str = "artifacts/wave_state.json"):
        self.state_file = Path(state_file)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.states: dict[str, WaveState] = self._load_states()

    def _load_states(self) -> dict[str, WaveState]:
        """Load existing wave states."""
        if self.state_file.exists():
            try:
                with open(self.state_file) as f:
                    data = json.load(f)
                    return {
                        wave_name: WaveState(**state_data)
                        for wave_name, state_data in data.items()
                    }
            except Exception as e:
                print(f"Warning: Could not load state file: {e}")
                return {}
        return {}

    def _save_states(self):
        """Save wave states to file."""
        data = {
            wave_name: asdict(state)
            for wave_name, state in self.states.items()
        }
        with open(self.state_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    def get_wave_state(self, wave_name: str) -> WaveState | None:
        """Get state for a specific wave."""
        return self.states.get(wave_name)

    def is_wave_complete(self, wave_name: str) -> bool:
        """Check if wave was previously completed."""
        state = self.get_wave_state(wave_name)
        return state.is_complete if state else False

    def was_file_modified(self, wave_name: str, file_path: str) -> bool:
        """Check if file was modified in previous wave execution."""
        state = self.get_wave_state(wave_name)
        if not state:
            return False
        return str(file_path) in state.files_modified

    def was_pattern_applied(self, wave_name: str, pattern_type: str, pattern: str) -> bool:
        """Check if pattern was applied in previous wave execution."""
        state = self.get_wave_state(wave_name)
        if not state:
            return False
        return pattern in state.patterns_applied.get(pattern_type, set())

    def start_wave_execution(self, wave_name: str) -> str:
        """Start tracking a new wave execution."""
        execution_id = hashlib.md5(f"{wave_name}_{datetime.now().isoformat()}".encode()).hexdigest()[:8]

        state = WaveState(
            wave_name=wave_name,
            execution_id=execution_id,
            timestamp=datetime.now().isoformat(),
            files_modified={},
            patterns_applied={},
            metrics={}
        )

        self.states[wave_name] = state
        self._save_states()

        return execution_id

    def record_file_modification(self, wave_name: str, file_path: str, content_hash: str):
        """Record a file modification."""
        state = self.states.get(wave_name)
        if state:
            state.files_modified[str(file_path)] = content_hash
            self._save_states()

    def record_pattern_application(self, wave_name: str, pattern_type: str, pattern: str):
        """Record a pattern application."""
        state = self.states.get(wave_name)
        if state:
            if pattern_type not in state.patterns_applied:
                state.patterns_applied[pattern_type] = set()
            state.patterns_applied[pattern_type].add(pattern)
            self._save_states()

    def record_metrics(self, wave_name: str, metrics: dict[str, Any]):
        """Record wave execution metrics."""
        state = self.states.get(wave_name)
        if state:
            state.metrics.update(metrics)
            self._save_states()

    def complete_wave(self, wave_name: str):
        """Mark wave as complete."""
        state = self.states.get(wave_name)
        if state:
            state.is_complete = True
            self._save_states()

    def get_file_hash(self, file_path: Path) -> str:
        """Calculate hash of file content."""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""

    def has_file_changed_since_wave(self, wave_name: str, file_path: Path) -> bool:
        """Check if file has changed since wave execution."""
        state = self.get_wave_state(wave_name)
        if not state or str(file_path) not in state.files_modified:
            return True  # File not tracked, assume changed

        previous_hash = state.files_modified[str(file_path)]
        current_hash = self.get_file_hash(file_path)

        return previous_hash != current_hash

    def reset_wave_state(self, wave_name: str):
        """Reset state for a wave (for forced re-execution)."""
        if wave_name in self.states:
            del self.states[wave_name]
            self._save_states()

    def get_execution_summary(self) -> dict[str, Any]:
        """Get summary of all wave states."""
        return {
            'total_waves': len(self.states),
            'completed_waves': len([s for s in self.states.values() if s.is_complete]),
            'waves': {
                name: {
                    'execution_id': state.execution_id,
                    'timestamp': state.timestamp,
                    'files_modified': len(state.files_modified),
                    'patterns_applied': sum(len(patterns) for patterns in state.patterns_applied.values()),
                    'is_complete': state.is_complete,
                    'metrics': state.metrics
                }
                for name, state in self.states.items()
            }
        }


# Global state manager instance
_state_manager = None

def get_state_manager() -> WaveStateManager:
    """Get global state manager instance."""
    global _state_manager
    if _state_manager is None:
        _state_manager = WaveStateManager()
    return _state_manager


def check_file_idempotency(wave_name: str, file_path: Path, modification_func) -> bool:
    """
    Check and apply file modification idempotently.

    Args:
        wave_name: Name of the wave
        file_path: Path to file to modify
        modification_func: Function that applies modifications

    Returns:
        True if modification was applied, False if already applied
    """
    state_manager = get_state_manager()

    # Check if file was already modified in this wave
    if state_manager.was_file_modified(wave_name, file_path):
        # Check if file has changed since modification
        if not state_manager.has_file_changed_since_wave(wave_name, file_path):
            print(f"⚪ {file_path}: Already modified, skipping (idempotent)")
            return False

    # Apply modification
    print(f"🔧 {file_path}: Applying modifications")
    modification_applied = modification_func()

    if modification_applied:
        # Record the modification
        content_hash = state_manager.get_file_hash(file_path)
        state_manager.record_file_modification(wave_name, file_path, content_hash)
        return True

    return False


def check_pattern_idempotency(wave_name: str, pattern_type: str, pattern: str, application_func) -> bool:
    """
    Check and apply pattern modification idempotently.

    Args:
        wave_name: Name of the wave
        pattern_type: Type of pattern (e.g., 'skip_pattern', 'assertion')
        pattern: The specific pattern to apply
        application_func: Function that applies the pattern

    Returns:
        True if pattern was applied, False if already applied
    """
    state_manager = get_state_manager()

    # Check if pattern was already applied in this wave
    if state_manager.was_pattern_applied(wave_name, pattern_type, pattern):
        print(f"⚪ Pattern '{pattern}' already applied, skipping (idempotent)")
        return False

    # Apply pattern
    print(f"🔧 Applying pattern: {pattern}")
    pattern_applied = application_func()

    if pattern_applied:
        # Record the pattern application
        state_manager.record_pattern_application(wave_name, pattern_type, pattern)
        return True

    return False


def start_wave(wave_name: str) -> str:
    """Start a wave execution with idempotency tracking."""
    state_manager = get_state_manager()

    # Check if wave was already completed
    if state_manager.is_wave_complete(wave_name):
        print(f"⚪ Wave {wave_name} already completed, skipping (idempotent)")
        return None

    print(f"🚀 Starting wave {wave_name}")
    execution_id = state_manager.start_wave_execution(wave_name)
    return execution_id


def complete_wave(wave_name: str, metrics: dict[str, Any] = None):
    """Complete a wave execution with metrics."""
    state_manager = get_state_manager()

    if metrics:
        state_manager.record_metrics(wave_name, metrics)

    state_manager.complete_wave(wave_name)
    print(f"✅ Wave {wave_name} completed")


def force_re_run_wave(wave_name: str):
    """Force re-run a wave by resetting its state."""
    state_manager = get_state_manager()
    state_manager.reset_wave_state(wave_name)
    print(f"🔄 Wave {wave_name} state reset, ready for re-execution")
