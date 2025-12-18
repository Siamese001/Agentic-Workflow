"""
Validation Context - Shared Blackboard for L5+ Autonomous Systems.

Implements the Canon Validator ValidationContext pattern that serves as
the central blackboard for all agents to share state, signals, and memory.

This is the glue that connects all L5+ autonomy components.
"""

import copy
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

logger = logging.getLogger(__name__)

# Import L5+ components
from apps_shared.signal_bus import SignalBus, SignalType, get_signal_bus
from apps_shared.reflection_agent import ReflectionAgent, create_reflection_agent
from apps_shared.few_shot_library import FewShotLibrary


@dataclass
class ModifiedItem:
    """Track a modified item with metadata."""
    
    item_id: str
    item_type: str  # file, section, metric, etc.
    modification_type: str  # created, updated, deleted
    previous_value: Optional[Any] = None
    new_value: Optional[Any] = None
    modified_by: str = ""
    cycle: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)


class ValidationContext:
    """
    Central validation context implementing Canon Validator blackboard pattern.
    
    This class serves as the shared state container for all L5+ autonomous
    operations. It integrates:
    - SignalBus for inter-agent communication
    - ReflectionAgent for self-critique
    - FewShotLibrary for prompt enhancement
    - Modified items tracking
    - Execution history
    - Memory/embeddings storage
    
    Canon Validator Pattern:
        ctx = ValidationContext(workflow_id)
        ctx.signals  # Set of active signals
        ctx.modified_files  # Set of modified files
        ctx.signal_critical_failure(message)
        ctx.resilient_mutation(agent_name, prompt)
    """
    
    def __init__(
        self,
        workflow_id: str,
        workflow_type: str = "generic",
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize the validation context.
        
        Args:
            workflow_id: Unique identifier for this workflow
            workflow_type: Type of workflow (resume, outreach, etc.)
            config: Optional configuration overrides
        """
        self.workflow_id = workflow_id
        self.workflow_type = workflow_type
        self.config = config or {}
        
        # Core L5+ components
        self.signal_bus = get_signal_bus()
        self.reflection_agent = create_reflection_agent()
        self.few_shot_library = FewShotLibrary
        
        # State tracking
        self.current_cycle = 0
        self.modified_items: Dict[str, ModifiedItem] = {}
        self.execution_log: List[Dict[str, Any]] = []
        self.quality_scores: Dict[str, float] = {}
        
        # Memory and context
        self.accumulated_context: Dict[str, Any] = {}
        self.embeddings: Dict[str, List[float]] = {}
        self.memory: Dict[str, Any] = {}
        
        # Few-shot constants (Canon Validator pattern)
        self.FEW_SHOT_SHERLOCK = FewShotLibrary.SHERLOCK
        self.FEW_SHOT_GITOPS = FewShotLibrary.GITOPS
        self.FEW_SHOT_STRATEGIC = FewShotLibrary.STRATEGIC
        self.FEW_SHOT_REFLECTION = FewShotLibrary.REFLECTION_STRATEGY
        self.FEW_SHOT_RESUME_BULLETS = FewShotLibrary.RESUME_BULLETS
        self.FEW_SHOT_OUTREACH = FewShotLibrary.OUTREACH_PERSONALIZATION
        
        # Callbacks
        self._on_signal_callbacks: List[Callable] = []
        self._on_modification_callbacks: List[Callable] = []
        
        # Timestamps
        self.created_at = datetime.utcnow()
        self.last_modified_at = datetime.utcnow()
        
        logger.info(f"ValidationContext initialized: {workflow_id} ({workflow_type})")
    
    # =========================================================================
    # Signal System (Canon Validator API)
    # =========================================================================
    
    @property
    def signals(self) -> Set[SignalType]:
        """Get active signals (Canon Validator compatibility)."""
        return self.signal_bus.signals
    
    def signal_critical_failure(self, message: str, source: str = "") -> None:
        """Emit critical failure signal."""
        self.signal_bus.signal_critical_failure(message, source)
        self._notify_signal_callbacks(SignalType.CRITICAL_FAIL, message)
    
    def signal_test_failure(self, message: str = "", source: str = "") -> None:
        """Emit test failure signal."""
        self.signal_bus.signal_test_failure(message, source)
        self._notify_signal_callbacks(SignalType.TEST_FAILURE, message)
    
    def signal_high_risk(self, message: str, source: str = "") -> None:
        """Emit high risk signal."""
        self.signal_bus.signal_high_risk(message, source)
        self._notify_signal_callbacks(SignalType.HIGH_RISK, message)
    
    def signal_convergence(self, source: str = "") -> None:
        """Emit convergence signal."""
        self.signal_bus.signal_convergence(source)
        self._notify_signal_callbacks(SignalType.CONVERGED, "")
    
    def signal_needs_human_review(self, message: str, source: str = "") -> None:
        """Emit human review needed signal."""
        self.signal_bus.signal_needs_human_review(message, source)
        self._notify_signal_callbacks(SignalType.NEEDS_HUMAN_REVIEW, message)
    
    def has_signal(self, signal_type: SignalType) -> bool:
        """Check if a signal is active."""
        return self.signal_bus.has(signal_type)
    
    def clear_signals(self) -> None:
        """Clear all signals (typically at start of new cycle)."""
        self.signal_bus.clear()
    
    def _notify_signal_callbacks(self, signal_type: SignalType, message: str) -> None:
        """Notify registered signal callbacks."""
        for callback in self._on_signal_callbacks:
            try:
                callback(signal_type, message)
            except Exception as e:
                logger.error(f"Signal callback error: {e}")
    
    # =========================================================================
    # Modified Items Tracking
    # =========================================================================
    
    @property
    def modified_files(self) -> Set[str]:
        """Get modified file IDs (Canon Validator compatibility)."""
        return set(self.modified_items.keys())
    
    def track_modification(
        self,
        item_id: str,
        item_type: str,
        modification_type: str,
        previous_value: Any = None,
        new_value: Any = None,
        modified_by: str = "",
    ) -> None:
        """Track a modification to an item."""
        
        modification = ModifiedItem(
            item_id=item_id,
            item_type=item_type,
            modification_type=modification_type,
            previous_value=previous_value,
            new_value=new_value,
            modified_by=modified_by,
            cycle=self.current_cycle,
        )
        
        self.modified_items[item_id] = modification
        self.last_modified_at = datetime.utcnow()
        
        logger.debug(f"Tracked modification: {item_id} ({modification_type})")
        
        # Notify callbacks
        for callback in self._on_modification_callbacks:
            try:
                callback(modification)
            except Exception as e:
                logger.error(f"Modification callback error: {e}")
    
    def clear_modifications(self) -> None:
        """Clear modification tracking (typically at start of new cycle)."""
        self.modified_items.clear()
    
    def get_modifications_by_type(self, item_type: str) -> List[ModifiedItem]:
        """Get all modifications of a specific type."""
        return [m for m in self.modified_items.values() if m.item_type == item_type]
    
    # =========================================================================
    # Execution Logging
    # =========================================================================
    
    def log_execution(
        self,
        agent_name: str,
        action: str,
        success: bool,
        duration_ms: float = 0,
        input_summary: str = "",
        output_summary: str = "",
        quality_score: Optional[float] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log an execution event."""
        
        entry = {
            "agent": agent_name,
            "action": action,
            "success": success,
            "duration_ms": duration_ms,
            "input_summary": input_summary,
            "output_summary": output_summary,
            "quality_score": quality_score,
            "error": error,
            "cycle": self.current_cycle,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }
        
        self.execution_log.append(entry)
        
        if quality_score is not None:
            self.quality_scores[agent_name] = quality_score
        
        # Emit signal on failure
        if not success and error:
            self.signal_bus.emit(
                SignalType.VALIDATION_FAILURE,
                f"{agent_name}: {error}",
                source=agent_name,
                severity="error"
            )
    
    def get_recent_executions(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get most recent execution log entries."""
        return self.execution_log[-count:]
    
    def get_executions_by_agent(self, agent_name: str) -> List[Dict[str, Any]]:
        """Get all executions by a specific agent."""
        return [e for e in self.execution_log if e["agent"] == agent_name]
    
    # =========================================================================
    # Quality Tracking
    # =========================================================================
    
    def set_quality_score(self, component: str, score: float) -> None:
        """Set quality score for a component."""
        self.quality_scores[component] = score
        
        # Emit signal if below threshold
        threshold = self.config.get("quality_threshold", 0.7)
        if score < threshold:
            self.signal_bus.emit(
                SignalType.QUALITY_BELOW_THRESHOLD,
                f"{component} quality {score:.2f} below threshold {threshold}",
                source=component,
                severity="warning"
            )
    
    def get_average_quality(self) -> float:
        """Get average quality score across all components."""
        if not self.quality_scores:
            return 1.0
        return sum(self.quality_scores.values()) / len(self.quality_scores)
    
    # =========================================================================
    # Memory and Context
    # =========================================================================
    
    def store_memory(self, key: str, value: Any) -> None:
        """Store a value in memory."""
        self.memory[key] = value
    
    def get_memory(self, key: str, default: Any = None) -> Any:
        """Retrieve a value from memory."""
        return self.memory.get(key, default)
    
    def store_embedding(self, key: str, embedding: List[float]) -> None:
        """Store an embedding vector."""
        self.embeddings[key] = embedding
    
    def get_embedding(self, key: str) -> Optional[List[float]]:
        """Retrieve an embedding vector."""
        return self.embeddings.get(key)
    
    def update_accumulated_context(self, key: str, value: Any) -> None:
        """Update accumulated context."""
        self.accumulated_context[key] = value
    
    # =========================================================================
    # Cycle Management
    # =========================================================================
    
    def start_new_cycle(self) -> int:
        """Start a new convergence cycle."""
        self.current_cycle += 1
        self.clear_signals()
        self.clear_modifications()
        
        logger.info(f"Started cycle {self.current_cycle}")
        return self.current_cycle
    
    # =========================================================================
    # Reflection Integration
    # =========================================================================
    
    async def perform_reflection(self) -> Any:
        """Perform reflection on current cycle."""
        
        return await self.reflection_agent.reflect_on_execution(
            execution_log=self.execution_log,
            signals_summary=self.signal_bus.get_summary(),
            cycle=self.current_cycle,
            quality_scores=self.quality_scores,
        )
    
    # =========================================================================
    # Few-Shot Integration
    # =========================================================================
    
    def get_few_shot(self, pattern_name: str) -> Optional[str]:
        """Get a few-shot pattern by name."""
        return self.few_shot_library.get_all_patterns().get(pattern_name)
    
    def inject_few_shots(self, prompt: str, patterns: List[str]) -> str:
        """Inject few-shot patterns into a prompt."""
        return self.few_shot_library.inject_into_prompt(prompt, patterns)
    
    # =========================================================================
    # Serialization
    # =========================================================================
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize context to dictionary."""
        return {
            "workflow_id": self.workflow_id,
            "workflow_type": self.workflow_type,
            "current_cycle": self.current_cycle,
            "signals": [s.value for s in self.signals],
            "modified_items": [
                {
                    "item_id": m.item_id,
                    "item_type": m.item_type,
                    "modification_type": m.modification_type,
                    "modified_by": m.modified_by,
                    "cycle": m.cycle,
                }
                for m in self.modified_items.values()
            ],
            "quality_scores": self.quality_scores,
            "average_quality": self.get_average_quality(),
            "execution_log_count": len(self.execution_log),
            "memory_keys": list(self.memory.keys()),
            "embedding_keys": list(self.embeddings.keys()),
            "created_at": self.created_at.isoformat(),
            "last_modified_at": self.last_modified_at.isoformat(),
        }
    
    def save_to_file(self, path: Path) -> None:
        """Save context to JSON file."""
        path.write_text(json.dumps(self.to_dict(), indent=2, default=str))
        logger.info(f"Context saved to {path}")
    
    # =========================================================================
    # Callbacks
    # =========================================================================
    
    def on_signal(self, callback: Callable) -> None:
        """Register a callback for signal events."""
        self._on_signal_callbacks.append(callback)
    
    def on_modification(self, callback: Callable) -> None:
        """Register a callback for modification events."""
        self._on_modification_callbacks.append(callback)


def create_validation_context(
    workflow_id: str,
    workflow_type: str = "generic",
    config: Optional[Dict[str, Any]] = None,
) -> ValidationContext:
    """Factory function to create a ValidationContext."""
    return ValidationContext(
        workflow_id=workflow_id,
        workflow_type=workflow_type,
        config=config,
    )
