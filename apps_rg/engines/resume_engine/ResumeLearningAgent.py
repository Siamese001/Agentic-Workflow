from __future__ import annotations
"""
Learning & Intelligence Module - Phase 3 Implementation

This module provides advanced learning and intelligence capabilities:
- LearningLoop: Few-shot recall from vector store (Pinecone)
- ConfidenceScorer: Logprobs-based confidence scoring with retry logic
- InstructionInjector: Dynamic instruction injection for real-time steering
- MemoryPersistence: File hashing, skip logic, flapping detection
"""
from typing import Any, Optional, Protocol, Dict, List
from enum import Enum, auto


import asyncio
import hashlib
import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from .context import ResumeEngineContext
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L0_maintenance.mixins.subatomic_testing_mixin import SubatomicTestingMixin


class ConfidenceLevel(Enum):
    """Confidence levels for LLM responses."""
    HIGH = "high"  # >= 0.8
    MEDIUM = "medium"  # >= 0.5
    LOW = "low"  # < 0.5
    UNKNOWN = "unknown"


@dataclass
class LearningExample:
    """A single learning example for few-shot recall."""
    id: str
    TaskType: str
    input_context: str
    output_result: str
    success: bool
    confidence: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConfidenceResult:
    """Result of confidence scoring."""
    score: float
    level: ConfidenceLevel
    logprobs: Optional[List[float]] = None
    avg_logprob: Optional[float] = None
    should_retry: bool = False

    @classmethod
    def from_logprob(cls, avg_logprob: float, min_confidence: float = 0.7) -> "ConfidenceResult":
        """Create ConfidenceResult from average logprob."""
        # Normalize logprob (-2.0 to 0.0) to confidence (0.0 to 1.0)
        score = min(1.0, max(0.0, (avg_logprob + 2.0) / 2.0))

        if score >= 0.8:
            level = ConfidenceLevel.HIGH
        elif score >= 0.5:
            level = ConfidenceLevel.MEDIUM
        else:
            level = ConfidenceLevel.LOW

        return cls(
            score=score,
            level=level,
            avg_logprob=avg_logprob,
            should_retry=score < min_confidence
        )


@dataclass
class Instruction:
    """A dynamic instruction for agent steering."""
    id: str
    source: str  # Agent or user that injected the instruction
    content: str
    priority: int = 0  # Higher = more important
    target_agents: List[str] = field(default_factory=list)  # Empty = all agents
    expires_at: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class MemoryState:
    """Persistent memory state for resume validation."""
    file_hashes: Dict[str, str] = field(default_factory=dict)
    skip_files: Set[str] = field(default_factory=set)
    flapping_files: Set[str] = field(default_factory=set)
    validation_history: Dict[str, List[bool]] = field(default_factory=dict)
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())


class LearningLoop:
    """
    Few-shot learning from past successful fixes.

    Uses vector store (Pinecone) for semantic search of similar past examples.
    Falls back to local storage if vector store unavailable.
    """

    def __init__(
        self,
        ctx: ResumeEngineContext,
        index_name: str = "resume-learning",
        local_fallback: bool = True,
    ):
        self.ctx = ctx
        self.index_name = index_name
        self.local_fallback = local_fallback

        # Local storage for fallback
        self._local_examples: List[LearningExample] = []
        self._local_file = Path(".memory/resume_learning.json")

        # Vector store connection (lazy init)
        self._pinecone_index = None
        self._pinecone_available = False

        self._load_local_examples()

    def _load_local_examples(self):
        """Load examples from local storage."""
        if self._local_file.exists():
            try:
                with open(self._local_file, "r") as f:
                    data = json.load(f)
                    self._local_examples = [
                        LearningExample(**ex) for ex in data.get("examples", [])
                    ]
            except Exception:
                self._local_examples = []

    def _save_local_examples(self):
        """Save examples to local storage."""
        try:
            self._local_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self._local_file, "w") as f:
                json.dump(
                    {"examples": [vars(ex) for ex in self._local_examples[-100:]]},  # Keep last 100
                    f,
                    indent=2,
                    default=str
                )
        except Exception:
            pass

    async def recall_similar(
        self,
        query: str,
        TaskType: Optional[str] = None,
        top_k: int = 3,
    ) -> List[LearningExample]:
        """
        Recall similar past examples for few-shot learning.

        Args:
            query: The current Task/problem description
            TaskType: Optional filter by Task type
            top_k: Number of examples to return

        Returns:
            List of similar LearningExample objects
        """
        # Try vector store first
        if self._pinecone_available and self._pinecone_index:
            try:
                results = await self._search_pinecone(query, TaskType, top_k)
                if results:
                    return results
            except Exception:
                pass

        # Fallback to local search
        return self._search_local(query, TaskType, top_k)

    async def _search_pinecone(
        self,
        query: str,
        TaskType: Optional[str],
        top_k: int,
    ) -> List[LearningExample]:
        """Search Pinecone for similar examples."""
        # This would use the actual Pinecone client
        # For now, return empty to use local fallback
        return []

    def _search_local(
        self,
        query: str,
        TaskType: Optional[str],
        top_k: int,
    ) -> List[LearningExample]:
        """Search local examples using simple text matching."""
        query_lower = query.lower()
        query_words = set(query_lower.split())

        scored_examples = []
        for ex in self._local_examples:
            if not ex.success:
                continue

            if TaskType and ex.TaskType != TaskType:
                continue

            # Simple word overlap scoring
            ex_words = set(ex.input_context.lower().split())
            overlap = len(query_words & ex_words)
            if overlap > 0:
                scored_examples.append((overlap, ex))

        # Sort by score descending
        scored_examples.sort(key=lambda x: x[0], reverse=True)

        return [ex for _, ex in scored_examples[:top_k]]

    async def record_success(
        self,
        TaskType: str,
        input_context: str,
        output_result: str,
        confidence: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Record a successful fix for future learning.

        Args:
            TaskType: Type of Task (e.g., "quality_fix", "ats_optimization")
            input_context: The input/problem that was solved
            output_result: The successful output/fix
            confidence: Confidence score of the fix
            metadata: Additional metadata
        """
        example = LearningExample(
            id=f"{TaskType}_{int(time.time())}_{hashlib.md5(input_context.encode()).hexdigest()[:8]}",
            TaskType=TaskType,
            input_context=input_context[:1000],  # Truncate
            output_result=output_result[:1000],
            success=True,
            confidence=confidence,
            metadata=metadata or {},
        )

        self._local_examples.append(example)
        self._save_local_examples()

        # Also upsert to vector store if available
        if self._pinecone_available:
            await self._upsert_pinecone(example)

    async def _upsert_pinecone(self, example: LearningExample):
        """Upsert example to Pinecone."""
        # Would use actual Pinecone client

    def get_stats(self) -> Dict[str, Any]:
        """Get learning statistics."""
        successful = [ex for ex in self._local_examples if ex.success]
        task_types = {}
        for ex in successful:
            task_types[ex.TaskType] = task_types.get(ex.TaskType, 0) + 1

        return {
            "total_examples": len(self._local_examples),
            "successful_examples": len(successful),
            "task_type_distribution": task_types,
            "pinecone_available": self._pinecone_available,
        }


class ConfidenceScorer:
    """
    Confidence scoring for LLM responses using logprobs.

    Provides retry logic when confidence is below threshold.
    """

    def __init__(
        self,
        min_confidence: float = 0.7,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        self.min_confidence = min_confidence
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # Statistics
        self.total_scores = 0
        self.high_confidence_count = 0
        self.retry_count = 0

    def score_response(
        self,
        response: Any,
        extract_logprobs: bool = True,
    ) -> ConfidenceResult:
        """
        Score the confidence of an LLM response.

        Args:
            response: The LLM response object
            extract_logprobs: Whether to extract logprobs from response

        Returns:
            ConfidenceResult with score and level
        """
        self.total_scores += 1

        # Try to extract logprobs from response
        avg_logprob = None
        if extract_logprobs and hasattr(response, 'candidates'):
            candidates = response.candidates
            if candidates and hasattr(candidates[0], 'avg_logprobs'):
                avg_logprob = candidates[0].avg_logprobs

        if avg_logprob is not None:
            result = ConfidenceResult.from_logprob(avg_logprob, self.min_confidence)
        else:
            # Default to medium confidence if no logprobs
            result = ConfidenceResult(
                score=0.6,
                level=ConfidenceLevel.MEDIUM,
                should_retry=False
            )

        if result.level == ConfidenceLevel.HIGH:
            self.high_confidence_count += 1

        if result.should_retry:
            self.retry_count += 1

        return result

    def score_from_logprob(self, avg_logprob: float) -> ConfidenceResult:
        """Score directly from a logprob value."""
        self.total_scores += 1
        result = ConfidenceResult.from_logprob(avg_logprob, self.min_confidence)

        if result.level == ConfidenceLevel.HIGH:
            self.high_confidence_count += 1

        return result

    def score_from_text(self, text: str) -> ConfidenceResult:
        """
        Heuristic confidence scoring based on text characteristics.

        Used when logprobs are not available.
        """
        self.total_scores += 1

        score = 0.5  # Base score

        # Positive indicators
        if len(text) > 100:
            score += 0.1
        if not any(phrase in text.lower() for phrase in ["i'm not sure", "maybe", "possibly"]):
            score += 0.1
        if any(phrase in text.lower() for phrase in ["specifically", "exactly", "precisely"]):
            score += 0.1

        # Negative indicators
        if "error" in text.lower() or "failed" in text.lower():
            score -= 0.2
        if text.count("?") > 2:
            score -= 0.1

        score = min(1.0, max(0.0, score))

        if score >= 0.8:
            level = ConfidenceLevel.HIGH
            self.high_confidence_count += 1
        elif score >= 0.5:
            level = ConfidenceLevel.MEDIUM
        else:
            level = ConfidenceLevel.LOW

        return ConfidenceResult(
            score=score,
            level=level,
            should_retry=score < self.min_confidence
        )

    async def retry_with_confidence(
        self,
        call_fn: Callable,
        *args,
        **kwargs,
    ) -> Tuple[Any, ConfidenceResult]:
        """
        Retry a function call until confidence threshold is met.

        Args:
            call_fn: Async function to call
            *args, **kwargs: Arguments to pass to call_fn

        Returns:
            Tuple of (result, confidence_result)
        """
        best_result = None
        best_confidence = ConfidenceResult(score=0.0, level=ConfidenceLevel.LOW)

        for attempt in range(self.max_retries):
            try:
                result = await call_fn(*args, **kwargs)

                # Score the result
                if hasattr(result, 'candidates'):
                    confidence = self.score_response(result)
                elif isinstance(result, str):
                    confidence = self.score_from_text(result)
                else:
                    confidence = ConfidenceResult(score=0.6, level=ConfidenceLevel.MEDIUM)

                # Keep best result
                if confidence.score > best_confidence.score:
                    best_result = result
                    best_confidence = confidence

                # Return if confidence is high enough
                if not confidence.should_retry:
                    return result, confidence

                # Wait before retry
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))

            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise e
                await asyncio.sleep(self.retry_delay)

        return best_result, best_confidence

    def get_stats(self) -> Dict[str, Any]:
        """Get scoring statistics."""
        return {
            "total_scores": self.total_scores,
            "high_confidence_count": self.high_confidence_count,
            "high_confidence_rate": self.high_confidence_count / max(1, self.total_scores),
            "retry_count": self.retry_count,
            "min_confidence_threshold": self.min_confidence,
        }


class InstructionInjector:
    """
    Dynamic instruction injection for real-time agent steering.

    Allows users or agents to inject instructions that guide
    downstream agent behavior.
    """

    def __init__(self, ctx: ResumeEngineContext) -> None:
        self.ctx = ctx
        self._instructions: List[Instruction] = []

    def inject(
        self,
        source: str,
        content: str,
        priority: int = 0,
        target_agents: Optional[List[str]] = None,
        ttl_seconds: Optional[int] = None,
    ) -> str:
        """
        Inject a new instruction.

        Args:
            source: Who is injecting (agent name or "user")
            content: The instruction content
            priority: Priority level (higher = more important)
            target_agents: List of agent names this applies to (None = all)
            ttl_seconds: Time-to-live in seconds (None = no expiry)

        Returns:
            Instruction ID
        """
        expires_at = None
        if ttl_seconds:
            expires_at = (
                datetime.now().timestamp() + ttl_seconds
            ).__str__()

        instruction = Instruction(
            id=f"inst_{int(time.time())}_{len(self._instructions)}",
            source=source,
            content=content,
            priority=priority,
            target_agents=target_agents or [],
            expires_at=expires_at,
        )

        self._instructions.append(instruction)

        # Also add to context for backward compatibility
        self.ctx.instructions.append(f"[{source}] {content}")

        return instruction.id

    def get_instructions(
        self,
        agent_name: Optional[str] = None,
        include_expired: bool = False,
    ) -> List[Instruction]:
        """
        Get active instructions, optionally filtered by agent.

        Args:
            agent_name: Filter by target agent (None = all)
            include_expired: Include expired instructions

        Returns:
            List of matching instructions, sorted by priority
        """
        now = datetime.now().timestamp()

        result = []
        for inst in self._instructions:
            # Check expiry
            if not include_expired and inst.expires_at:
                try:
                    if float(inst.expires_at) < now:
                        continue
                except ValueError:
                    pass

            # Check target
            if agent_name and inst.target_agents:
                if agent_name not in inst.target_agents:
                    continue

            result.append(inst)

        # Sort by priority (descending)
        result.sort(key=lambda x: x.priority, reverse=True)

        return result

    def get_instruction_text(
        self,
        agent_name: Optional[str] = None,
    ) -> str:
        """
        Get formatted instruction text for an agent.

        Args:
            agent_name: The agent requesting instructions

        Returns:
            Formatted string of all applicable instructions
        """
        instructions = self.get_instructions(agent_name)

        if not instructions:
            return ""

        lines = ["## Active Instructions:"]
        for inst in instructions:
            lines.append(f"- [{inst.source}] {inst.content}")

        return "\nimport logging\n\nLogger = logging.getLogger(__name__)\n".join(lines)

    def remove(self, instruction_id: str) -> bool:
        """Remove an instruction by ID."""
        for i, inst in enumerate(self._instructions):
            if inst.id == instruction_id:
                self._instructions.pop(i)
                return True
        return False

    def clear(self, source: Optional[str] = None) -> Any:
        """Clear instructions, optionally filtered by source."""
        if source:
            self._instructions = [
                inst for inst in self._instructions
                if inst.source != source
            ]
        else:
            self._instructions.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get instruction statistics."""
        by_source = {}
        for inst in self._instructions:
            by_source[inst.source] = by_source.get(inst.source, 0) + 1

        return {
            "total_instructions": len(self._instructions),
            "by_source": by_source,
            "active_count": len(self.get_instructions()),
        }


class MemoryPersistence:
    """
    Persistent memory for resume validation state.

    Tracks file hashes, skip logic, and flapping detection.
    """

    def __init__(
        self,
        memory_file: Optional[Path] = None,
        flapping_threshold: int = 3,
    ):
        self.memory_file = memory_file or Path(".memory/resume_memory.json")
        self.flapping_threshold = flapping_threshold

        self.state = MemoryState()
        self._load()

    def _load(self):
        """Load memory state from disk."""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, "r") as f:
                    data = json.load(f)
                    self.state = MemoryState(
                        file_hashes=data.get("file_hashes", {}),
                        skip_files=set(data.get("skip_files", [])),
                        flapping_files=set(data.get("flapping_files", [])),
                        validation_history=data.get("validation_history", {}),
                        last_updated=data.get("last_updated", datetime.now().isoformat()),
                    )
            except Exception:
                self.state = MemoryState()

    def _save(self):
        """Save memory state to disk."""
        try:
            self.memory_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.memory_file, "w") as f:
                json.dump(
                    {
                        "file_hashes": self.state.file_hashes,
                        "skip_files": list(self.state.skip_files),
                        "flapping_files": list(self.state.flapping_files),
                        "validation_history": self.state.validation_history,
                        "last_updated": datetime.now().isoformat(),
                    },
                    f,
                    indent=2,
                )
        except Exception:
            pass

    def calculate_hash(self, content: str) -> str:
        """Calculate SHA-256 hash of content."""
        return hashlib.sha256(content.encode()).hexdigest()

    def should_skip(self, file_id: str, content: str) -> bool:
        """
        Check if a file should be skipped based on memory.

        Args:
            file_id: Unique identifier for the file/section
            content: Current content

        Returns:
            True if file should be skipped
        """
        current_hash = self.calculate_hash(content)
        saved_hash = self.state.file_hashes.get(file_id)

        # If content has changed, don't skip
        if saved_hash and saved_hash != current_hash:
            return False

        # If content unchanged and in skip list, skip it
        if file_id in self.state.skip_files and saved_hash == current_hash:
            return True

        # If content unchanged, check validation history
        if saved_hash and saved_hash == current_hash:
            history = self.state.validation_history.get(file_id, [])
            if history and history[-1]:  # Last validation passed
                return True

        return False

    def record_validation(
        self,
        file_id: str,
        content: str,
        passed: bool,
    ) -> Any:
        """
        Record a validation result.

        Args:
            file_id: Unique identifier for the file/section
            content: Content that was validated
            passed: Whether validation passed
        """
        current_hash = self.calculate_hash(content)
        self.state.file_hashes[file_id] = current_hash

        # Update history
        if file_id not in self.state.validation_history:
            self.state.validation_history[file_id] = []

        history = self.state.validation_history[file_id]
        history.append(passed)

        # Keep only last N results
        if len(history) > 10:
            history = history[-10:]
            self.state.validation_history[file_id] = history

        # Detect flapping
        if len(history) >= self.flapping_threshold:
            recent = history[-self.flapping_threshold:]
            if len(set(recent)) > 1:  # Mixed results
                self.state.flapping_files.add(file_id)

        # Update skip list
        if passed:
            self.state.skip_files.add(file_id)
        else:
            self.state.skip_files.discard(file_id)

        self._save()

    def is_flapping(self, file_id: str) -> bool:
        """Check if a file is flapping (unstable validation)."""
        return file_id in self.state.flapping_files

    def clear_flapping(self, file_id: str) -> Any:
        """Clear flapping status for a file."""
        self.state.flapping_files.discard(file_id)
        self._save()

    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        return {
            "total_tracked": len(self.state.file_hashes),
            "skip_count": len(self.state.skip_files),
            "flapping_count": len(self.state.flapping_files),
            "last_updated": self.state.last_updated,
        }

    def reset(self) -> Any:
        """Reset all memory state."""
        self.state = MemoryState()
        self._save()


class ResumeLearningAgent(MCPHardenedMixin, HealerMixin, SubatomicTestingMixin):
    """
    Agent that combines all Phase 3 learning capabilities.

    Integrates:
    - Few-shot learning from past successes
    - Confidence scoring with retry logic
    - Dynamic instruction injection
    - Memory persistence
    """

    def __init__(self, ctx: ResumeEngineContext) -> None:
        self.ctx = ctx
        self.name = "ResumeLearningAgent"

        # Initialize components
        self.learning_loop = LearningLoop(ctx)
        self.confidence_scorer = ConfidenceScorer()
        self.instruction_injector = InstructionInjector(ctx)
        self.memory = MemoryPersistence()

    async def get_few_shot_context(
        self,
        task_description: str,
        TaskType: str = "general",
    ) -> str:
        """
        Get few-shot context from past successful fixes.

        Returns formatted string for prompt injection.
        """
        examples = await self.learning_loop.recall_similar(
            task_description,
            TaskType=TaskType,
            top_k=2,
        )

        if not examples:
            return ""

        lines = ["\n## Similar Past Successes:"]
        for i, ex in enumerate(examples, 1):
            lines.append(f"\n### Example {i} (confidence: {ex.confidence:.2f})")
            lines.append(f"Input: {ex.input_context[:200]}...")
            lines.append(f"Output: {ex.output_result[:200]}...")

        return "\n".join(lines)

    async def record_success(
        self,
        TaskType: str,
        input_context: str,
        output_result: str,
        confidence: float = 1.0,
    ) -> Any:
        """Record a successful operation for future learning."""
        await self.learning_loop.record_success(
            TaskType=TaskType,
            input_context=input_context,
            output_result=output_result,
            confidence=confidence,
        )

    def inject_instruction(
        self,
        content: str,
        priority: int = 0,
        target_agents: Optional[List[str]] = None,
    ) -> str:
        """Inject a dynamic instruction."""
        return self.instruction_injector.inject(
            source=self.name,
            content=content,
            priority=priority,
            target_agents=target_agents,
        )

    def get_instructions_for_agent(self, agent_name: str) -> str:
        """Get formatted instructions for an agent."""
        return self.instruction_injector.get_instruction_text(agent_name)

    def should_skip_section(self, section_id: str, content: str) -> bool:
        """Check if a section should be skipped."""
        return self.memory.should_skip(section_id, content)

    def record_section_validation(
        self,
        section_id: str,
        content: str,
        passed: bool,
    ) -> Any:
        """Record section validation result."""
        self.memory.record_validation(section_id, content, passed)

    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics from all components."""
        return {
            "learning": self.learning_loop.get_stats(),
            "confidence": self.confidence_scorer.get_stats(),
            "instructions": self.instruction_injector.get_stats(),
            "memory": self.memory.get_stats(),
        }

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()
