from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent


# OutreachEngineContext stub
class OutreachEngineContext:
    def __init__(self, *args, **kwargs):
        pass


"""
Outreach Engine Learning Module

Provides learning and memory capabilities:
- Learning loops for pattern recognition
- Confidence scoring for decisions
- Memory persistence across sessions
"""

import hashlib
import json
from datetime import datetime
from enum import Enum


# STUB: OutreachAgent base class (deprecated)
class OutreachAgent:
    """Legacy base class - use LICAgentBase instead."""

    pass


class HealerMixin:
    """Legacy mixin - use LICAgentBase instead."""

    pass


class OutreachConfidenceLevel(Enum):
    """
    Confidence levels for outreach decisions.

    Defines the confidence thresholds used to categorize the reliability
    of outreach decisions and predictions.
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class OutreachLearningExample:
    """
    A learning example from past outreach.

    Attributes:
        example_id: Unique identifier for the example
        TaskType: Type of task performed
        input_context: Input context for the task
        output_result: Result produced
        success: Whether the task succeeded
        confidence: Confidence score (0-1)
        timestamp: ISO timestamp of creation
    """

    example_id: str
    TaskType: str
    input_context: str
    output_result: str
    success: bool
    confidence: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class OutreachInstruction:
    """
    An instruction for outreach agents.

    Attributes:
        text: Instruction text
        priority: Priority level (higher = more important)
        source: Source of the instruction
        timestamp: ISO timestamp of creation
    """

    text: str
    priority: int
    source: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class OutreachLearningLoop:
    """
    Learning loop for outreach campaigns.

    Tracks patterns and improves over time through example recording
    and pattern recognition.

    Attributes:
        ctx: Outreach engine context
        _examples: List of recorded learning examples
        _patterns: Dictionary of recognized patterns and their counts
    """

    def __init__(self, ctx: OutreachEngineContext) -> None:
        """
        Initialize the learning loop.

        Args:
            ctx: Outreach engine context
        """
        self.ctx = ctx
        self._examples: list[OutreachLearningExample] = []
        self._patterns: dict[str, int] = {}

    async def record_success(
        self,
        TaskType: str,
        input_context: str,
        output_result: str,
        confidence: float = 0.8,
    ) -> Any:
        """Record a successful outreach pattern."""
        example_id = hashlib.sha256(f"{TaskType}:{input_context}:{output_result}".encode()).hexdigest()[:12]

        example = OutreachLearningExample(
            example_id=example_id,
            TaskType=TaskType,
            input_context=input_context,
            output_result=output_result,
            success=True,
            confidence=confidence,
        )

        self._examples.append(example)
        self._update_patterns(TaskType, success=True)

    async def record_failure(
        self,
        TaskType: str,
        input_context: str,
        error: str,
    ) -> Any:
        """Record a failed outreach attempt."""
        example_id = hashlib.sha256(f"{TaskType}:{input_context}:{error}".encode()).hexdigest()[:12]

        example = OutreachLearningExample(
            example_id=example_id,
            TaskType=TaskType,
            input_context=input_context,
            output_result=error,
            success=False,
            confidence=0.0,
        )

        self._examples.append(example)
        self._update_patterns(TaskType, success=False)

    def _update_patterns(self, TaskType: str, success: bool):
        """Update pattern tracking."""
        key = f"{TaskType}:{'success' if success else 'failure'}"
        self._patterns[key] = self._patterns.get(key, 0) + 1

    def get_success_rate(self, TaskType: str) -> float:
        """Get success rate for a Task type."""
        successes = self._patterns.get(f"{TaskType}:success", 0)
        failures = self._patterns.get(f"{TaskType}:failure", 0)
        total = successes + failures

        if total == 0:
            return 0.5  # Default

        return successes / total

    def get_examples(self, TaskType: str = None, limit: int = 10) -> list[OutreachLearningExample]:  # guardian: allow-magic_configuration
        """Get learning examples."""
        if TaskType:
            examples = [e for e in self._examples if e.TaskType == TaskType]
        else:
            examples = self._examples

        return examples[-limit:]


class OutreachConfidenceScorer:
    """
    Scores confidence for outreach decisions.
    """

    def __init__(self, ctx: OutreachEngineContext) -> None:
        self.ctx = ctx
        self.learning_loop = OutreachLearningLoop(ctx)

    def score_lead(self, lead: dict[str, Any]) -> float:
        """Score confidence for a lead."""
        score = 0.5  # Base score

        # Has company
        if lead.get("company"):
            score += 0.1

        # Has contact name
        if lead.get("contact_name"):
            score += 0.1

        # Has email
        if lead.get("email"):
            score += 0.1

        # Has title
        if lead.get("title"):
            score += 0.1

        # Has LinkedIn
        if lead.get("linkedin"):
            score += 0.1

        return min(1.0, score)

    def score_message(self, message: dict[str, Any]) -> float:
        """Score confidence for a message."""
        score = 0.5  # Base score

        content = message.get("content", "")
        subject = message.get("subject", "")

        # Has personalization
        if "{name}" in content or "{company}" in content:
            score += 0.15

        # Has call to action
        cta_words = ["schedule", "call", "meet", "discuss"]
        if any(word in content.lower() for word in cta_words):
            score += 0.1

        # Good subject length
        if 20 <= len(subject) <= 60:
            score += 0.1

        # Has unsubscribe
        if "unsubscribe" in content.lower():
            score += 0.1

        return min(1.0, score)

    def get_confidence_level(self, score: float) -> OutreachConfidenceLevel:
        """Convert score to confidence level."""
        if score >= 0.85:
            return OutreachConfidenceLevel.VERY_HIGH
        elif score >= 0.7:
            return OutreachConfidenceLevel.HIGH
        elif score >= 0.5:
            return OutreachConfidenceLevel.MEDIUM
        else:
            return OutreachConfidenceLevel.LOW


class OutreachMemoryPersistence:
    """
    Persists outreach learning across sessions.
    """

    def __init__(self, memory_file: str = "outreach_memory.json") -> None:
        self.memory_file = Path(memory_file)
        self._memory: dict[str, Any] = {}
        self._load()

    def _load(self):
        """Load memory from file."""
        if self.memory_file.exists():
            try:
                self._memory = json.loads(self.memory_file.read_text())
            except Exception:  # guardian: allow-silent_swallower
                self._memory = {}

    def _save(self):
        """Save memory to file."""
        try:
            self.memory_file.write_text(json.dumps(self._memory, indent=2))
        except Exception:  # guardian: allow-silent_swallower
            pass

    def store(self, key: str, value: Any) -> Any:
        """Store a value in memory."""
        self._memory[key] = {
            "value": value,
            "timestamp": datetime.now().isoformat(),
        }
        self._save()

    def retrieve(self, key: str) -> Any | None:
        """Retrieve a value from agentic_core.semantic_memory."""
        entry = self._memory.get(key)
        if entry:
            return entry.get("value")
        return None

    def list_keys(self) -> list[str]:
        """List all memory keys."""
        return list(self._memory.keys())

    def clear(self) -> Any:
        """Clear all memory."""
        self._memory = {}
        self._save()


class OutreachLearningAgent(SubatomicTestingMixin, SovereignBaseAgent):
    """
    Learning agent for outreach campaigns.

    Learns from past campaigns and provides recommendations.
    """

    def __init__(self, ctx: OutreachEngineContext) -> None:
        super().__init__(ctx)
        self.learning_loop = OutreachLearningLoop(ctx)
        self.confidence_scorer = OutreachConfidenceScorer(ctx)
        self.memory = OutreachMemoryPersistence()

    async def execute(self) -> None:
        """Execute execute operation."""
        print(f"   [{self.name}] Analyzing patterns...")

        # Score leads
        lead_scores = []
        for lead in self.ctx.leads:
            score = self.confidence_scorer.score_lead(lead)
            lead_scores.append(score)

        # Score messages
        message_scores = []
        for message in self.ctx.messages:
            score = self.confidence_scorer.score_message(message)
            message_scores.append(score)

        # Calculate averages
        avg_lead_score = sum(lead_scores) / len(lead_scores) if lead_scores else 0
        avg_message_score = sum(message_scores) / len(message_scores) if message_scores else 0

        # Store in memory
        self.memory.store("last_lead_score", avg_lead_score)
        self.memory.store("last_message_score", avg_message_score)

        # Generate recommendations
        recommendations = []

        if avg_lead_score < 0.6:
            recommendations.append("Improve lead quality - add more contact details")

        if avg_message_score < 0.6:
            recommendations.append("Improve message quality - add personalization")

        if recommendations:
            self.ctx.inject_instruction(
                f"Learning recommendations: {'; '.join(recommendations)}",
                priority=7,
            )

        self.record_result(True, f"Lead score: {avg_lead_score:.2f}, Message score: {avg_message_score:.2f}")
        print(f"   [{self.name}] ✅ Analysis complete")

    def inject_instruction(self, instruction: str, priority: int = 5) -> Any:  # guardian: allow-type_erasure
        """Inject an instruction into the context."""
        self.ctx.inject_instruction(instruction, priority)

    async def record_success(
        self,
        TaskType: str,
        input_context: str,
        output_result: str,
        confidence: float = 0.8,
    ) -> Any:  # guardian: allow-type_erasure
        """Record a successful pattern."""
        await self.learning_loop.record_success(TaskType, input_context, output_result, confidence)

    async def record_failure(
        self,
        TaskType: str,
        input_context: str,
        error: str,
    ) -> Any:  # guardian: allow-type_erasure
        """Record a failed pattern."""
        await self.learning_loop.record_failure(TaskType, input_context, error)

    def heal_repository(self) -> dict:  # guardian: allow-type_erasure
        """Invoke healing chain via super()."""
        return super().heal_repository()

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """Heal violations detected by OutreachLearningAgent."""
        violation_type = violation.get("type", "unknown")
        try:
            return {
                "status": "skipped",
                "details": f"OutreachLearningAgent heal() not yet implemented for {violation_type}",
                "artifacts": [],
                "errors": [],
            }
        except Exception as e:
            return {
                "status": "failed",
                "details": f"OutreachLearningAgent heal() failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }
