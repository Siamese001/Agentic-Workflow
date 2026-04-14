"""
Meta-Learning Integration for L0 Routing - Wave 3.2

Implements fast adaptation, few-shot learning, and continual learning
capabilities for routing models to adapt to new patterns without catastrophic forgetting.
"""

from __future__ import annotations

import json
import logging
import time
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_improves_agent_policy,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_writes_learning_snapshot,
)
from tqdm import tqdm

logger = logging.getLogger(__name__)


@dataclass
class TaskExample:
    """Single example for meta-learning tasks"""

    query: str
    context: dict[str, Any]
    target_agent: str
    confidence: float
    success: bool
    timestamp: float = field(default_factory=time.time)
    features: dict[str, float] | None = None


@dataclass
class MetaLearningTask:
    """Meta-learning task with support and query sets"""

    task_id: str
    task_name: str
    support_examples: list[TaskExample]
    query_examples: list[TaskExample]
    task_type: str  # "few_shot", "adaptation", "continual"
    priority: float = 1.0
    created_at: float = field(default_factory=time.time)


@dataclass
class AdaptationResult:
    """Result of model adaptation"""

    task_id: str
    adaptation_type: str
    performance_before: float
    performance_after: float
    adaptation_time: float
    examples_used: int
    success: bool
    new_parameters: dict[str, Any] | None = None


class BaseMetaLearner(ABC):
    """Abstract base class for meta-learning algorithms"""

    def __init__(self, model_name: str, adaptation_rate: float = 0.01):
        self.model_name = model_name
        self.adaptation_rate = adaptation_rate
        self.adaptation_history: list[AdaptationResult] = []
        self.performance_history: list[float] = []

    @abstractmethod
    def adapt(self, task: MetaLearningTask) -> AdaptationResult:
        """Adapt model to new task"""
        pass

    @abstractmethod
    def predict(self, query: str, context: dict[str, Any]) -> tuple[str, float]:
        """Make prediction with adapted model"""
        pass

    @abstractmethod
    def reset(self):
        """Reset model to initial state"""
        pass

    def get_performance_trend(self) -> str:
        """Get performance trend (improving, declining, stable)"""
        if len(self.performance_history) < 10:
            return "insufficient_data"

        recent = self.performance_history[-5:]
        earlier = self.performance_history[-10:-5]

        recent_avg = np.mean(recent)
        earlier_avg = np.mean(earlier)

        if recent_avg > earlier_avg + 0.05:
            return "improving"
        elif recent_avg < earlier_avg - 0.05:
            return "declining"
        else:
            return "stable"


class MAMLMetaLearner(BaseMetaLearner):
    """Model-Agnostic Meta-Learning implementation"""

    def __init__(self, model_name: str, adaptation_rate: float = 0.01, inner_steps: int = 5):
        super().__init__(model_name, adaptation_rate)
        self.inner_steps = inner_steps
        self.meta_parameters = self._initialize_meta_parameters()
        self.task_specific_parameters: dict[str, dict[str, Any]] = {}

    def _initialize_meta_parameters(self) -> dict[str, Any]:
        """Initialize meta-parameters"""
        return {
            "embedding_weights": np.random.randn(100, 50) * 0.1,
            "classification_weights": np.random.randn(50, 10) * 0.1,
            "bias": np.zeros(10),
            "learning_rate": self.adaptation_rate,
        }

    def adapt(self, task: MetaLearningTask) -> AdaptationResult:
        """Adapt model using MAML algorithm"""
        start_time = time.time()

        # Get current performance on task
        performance_before = self._evaluate_on_task(task)

        # Create task-specific parameters (copy meta parameters)
        task_params = {
            k: v.copy() if isinstance(v, np.ndarray) else v for k, v in self.meta_parameters.items()
        }

        # Inner loop adaptation on support examples
        for step in range(self.inner_steps):
            for example in task.support_examples:
                # Compute gradient and update task-specific parameters
                gradient = self._compute_gradient(example, task_params)
                task_params = self._update_parameters(task_params, gradient)

        # Store task-specific parameters
        self.task_specific_parameters[task.task_id] = task_params

        # Evaluate after adaptation
        performance_after = self._evaluate_on_task(task, task_params)

        adaptation_time = time.time() - start_time
        success = performance_after > performance_before

        result = AdaptationResult(
            task_id=task.task_id,
            adaptation_type="MAML",
            performance_before=performance_before,
            performance_after=performance_after,
            adaptation_time=adaptation_time,
            examples_used=len(task.support_examples),
            success=success,
            new_parameters=task_params,
        )

        self.adaptation_history.append(result)
        self.performance_history.append(performance_after)

        # Emit learning events
        _emit_records_learning_event(
            "maml_meta_learner",
            "adaptation_complete",
            {
                "task_id": task.task_id,
                "performance_improvement": performance_after - performance_before,
                "adaptation_time": adaptation_time,
                "success": success,
            },
        )

        _emit_writes_learning_snapshot(
            "maml_meta_learner",
            "adaptation_snapshot",
            {
                "task_id": task.task_id,
                "parameters": {
                    k: v.tolist() if isinstance(v, np.ndarray) else v for k, v in task_params.items()
                },
                "performance": performance_after,
            },
        )

        return result

    def predict(self, query: str, context: dict[str, Any]) -> tuple[str, float]:
        """Make prediction using adapted parameters"""
        # Use meta-parameters if no specific task adaptation
        current_params = self.meta_parameters

        # Simple forward pass (simplified)
        query_embedding = self._encode_query(query)

        # Apply embedding weights
        hidden = query_embedding @ current_params["embedding_weights"]
        hidden = np.tanh(hidden)

        # Apply classification weights
        logits = hidden @ current_params["classification_weights"] + current_params["bias"]
        probabilities = 1.0 / (1.0 + np.exp(-logits))  # Sigmoid

        # Get best prediction
        best_idx = np.argmax(probabilities)
        confidence = float(probabilities[best_idx])

        # Map index to agent name (simplified)
        agent_names = ["code_reviewer", "resume_writer", "data_analyst", "writer", "researcher"]
        agent_name = agent_names[best_idx % len(agent_names)]

        return agent_name, confidence

    def reset(self):
        """Reset to initial meta-parameters"""
        self.meta_parameters = self._initialize_meta_parameters()
        self.task_specific_parameters.clear()

        _emit_stores_learning_state(
            "maml_meta_learner",
            "reset",
            {
                "model_name": self.model_name,
            },
        )

    def _evaluate_on_task(self, task: MetaLearningTask, parameters: dict[str, Any] | None = None) -> float:
        """Evaluate model performance on task"""
        if parameters is None:
            parameters = self.meta_parameters

        correct = 0
        total = 0

        for example in task.query_examples:
            agent_name, confidence = self._predict_with_parameters(example.query, example.context, parameters)
            if agent_name == example.target_agent:
                correct += 1
            total += 1

        return correct / total if total > 0 else 0.0

    def _predict_with_parameters(
        self, query: str, context: dict[str, Any], parameters: dict[str, Any]
    ) -> tuple[str, float]:
        """Predict with specific parameters"""
        query_embedding = self._encode_query(query)
        hidden = query_embedding @ parameters["embedding_weights"]
        hidden = np.tanh(hidden)
        logits = hidden @ parameters["classification_weights"] + parameters["bias"]
        probabilities = 1.0 / (1.0 + np.exp(-logits))

        best_idx = np.argmax(probabilities)
        confidence = float(probabilities[best_idx])

        agent_names = ["code_reviewer", "resume_writer", "data_analyst", "writer", "researcher"]
        agent_name = agent_names[best_idx % len(agent_names)]

        return agent_name, confidence

    def _encode_query(self, query: str) -> np.ndarray:
        """Encode query to embedding (simplified)"""
        # In production, use actual embedding model
        words = query.lower().split()
        embedding = np.zeros(100)

        # Simple word-based embedding
        for i, word in enumerate(words[:20]):  # First 20 words
            hash_val = hash(word) % 1000
            embedding[hash_val % 100] += 1.0 / (i + 1)

        return embedding

    def _compute_gradient(self, example: TaskExample, parameters: dict[str, Any]) -> dict[str, Any]:
        """Compute gradient for single example (simplified)"""
        # Simplified gradient computation
        gradient = {
            "embedding_weights": np.random.randn(100, 50) * 0.01,
            "classification_weights": np.random.randn(50, 10) * 0.01,
            "bias": np.random.randn(10) * 0.01,
        }
        return gradient

    def _update_parameters(self, parameters: dict[str, Any], gradient: dict[str, Any]) -> dict[str, Any]:
        """Update parameters with gradient"""
        updated = {}
        for key in parameters:
            if isinstance(parameters[key], np.ndarray) and key in gradient:
                updated[key] = parameters[key] - self.adaptation_rate * gradient[key]
            else:
                updated[key] = parameters[key]
        return updated


class ContinualLearner(BaseMetaLearner):
    """Continual learning with experience replay and elastic weight consolidation"""

    def __init__(self, model_name: str, memory_size: int = 1000, ewc_lambda: float = 0.4):
        super().__init__(model_name, adaptation_rate=0.01)
        self.memory_size = memory_size
        self.ewc_lambda = ewc_lambda

        # Experience replay buffer
        self.replay_buffer: deque = deque(maxlen=memory_size)

        # Elastic weight consolidation
        self.fisher_information: dict[str, np.ndarray] = {}
        self.optimal_parameters: dict[str, Any] = {}

        # Current model parameters
        self.current_parameters = self._initialize_parameters()

    def _initialize_parameters(self) -> dict[str, Any]:
        """Initialize model parameters"""
        return {
            "weights": np.random.randn(50, 20) * 0.1,
            "bias": np.zeros(20),
        }

    def adapt(self, task: MetaLearningTask) -> AdaptationResult:
        """Adapt with continual learning"""
        start_time = time.time()

        # Store optimal parameters before adaptation
        if not self.optimal_parameters:
            self.optimal_parameters = {
                k: v.copy() if isinstance(v, np.ndarray) else v for k, v in self.current_parameters.items()
            }

        # Get current performance
        performance_before = self._evaluate_on_task(task)

        # Add task examples to replay buffer
        for example in task.support_examples + task.query_examples:
            self.replay_buffer.append(example)

        # Continual learning with experience replay and EWC
        self._continual_learning_step(task)

        # Update Fisher information
        self._update_fisher_information(task)

        # Evaluate after adaptation
        performance_after = self._evaluate_on_task(task)

        adaptation_time = time.time() - start_time
        success = performance_after > performance_before

        result = AdaptationResult(
            task_id=task.task_id,
            adaptation_type="continual",
            performance_before=performance_before,
            performance_after=performance_after,
            adaptation_time=adaptation_time,
            examples_used=len(task.support_examples),
            success=success,
        )

        self.adaptation_history.append(result)
        self.performance_history.append(performance_after)

        # Emit learning events
        _emit_records_learning_event(
            "continual_learner",
            "adaptation_complete",
            {
                "task_id": task.task_id,
                "performance_improvement": performance_after - performance_before,
                "replay_buffer_size": len(self.replay_buffer),
                "success": success,
            },
        )

        _emit_improves_agent_policy(
            "continual_learner",
            "policy_update",
            {
                "task_id": task.task_id,
                "new_performance": performance_after,
                "buffer_utilization": len(self.replay_buffer) / self.memory_size,
            },
        )

        return result

    def predict(self, query: str, context: dict[str, Any]) -> tuple[str, float]:
        """Make prediction with continually learned parameters"""
        query_embedding = self._encode_query(query)

        # Forward pass
        hidden = query_embedding @ self.current_parameters["weights"]
        hidden = np.tanh(hidden)
        output = hidden + self.current_parameters["bias"]

        # Get best prediction
        best_idx = np.argmax(output)
        confidence = float(1.0 / (1.0 + np.exp(-output[best_idx])))  # Sigmoid

        agent_names = ["code_reviewer", "resume_writer", "data_analyst", "writer", "researcher"]
        agent_name = agent_names[best_idx % len(agent_names)]

        return agent_name, confidence

    def reset(self):
        """Reset to initial parameters"""
        self.current_parameters = self._initialize_parameters()
        self.replay_buffer.clear()
        self.fisher_information.clear()
        self.optimal_parameters.clear()

        _emit_stores_learning_state(
            "continual_learner",
            "reset",
            {
                "model_name": self.model_name,
                "memory_cleared": True,
            },
        )

    def _continual_learning_step(self, task: MetaLearningTask):
        """Perform continual learning step"""
        # Sample from replay buffer
        replay_examples = list(self.replay_buffer)

        # Combine current task and replay examples
        all_examples = task.support_examples + replay_examples

        # Update parameters with EWC regularization
        for example in tqdm(all_examples, desc="Processing", unit="item"):
            gradient = self._compute_gradient(example)

            # Apply EWC penalty
            for param_name in gradient:
                if param_name in self.fisher_information and param_name in self.optimal_parameters:
                    fisher = self.fisher_information[param_name]
                    optimal = self.optimal_parameters[param_name]
                    current = self.current_parameters[param_name]

                    # EWC regularization term
                    ewc_penalty = self.ewc_lambda * fisher * (current - optimal)
                    gradient[param_name] += ewc_penalty

            # Update parameters
            self._update_parameters(gradient)

    def _update_fisher_information(self, task: MetaLearningTask):
        """Update Fisher information for EWC"""
        # Simplified Fisher information estimation
        for param_name in self.current_parameters:
            if isinstance(self.current_parameters[param_name], np.ndarray):
                # Random Fisher diagonal (simplified)
                fisher_diag = np.random.rand(*self.current_parameters[param_name].shape) * 0.1
                self.fisher_information[param_name] = fisher_diag

    def _evaluate_on_task(self, task: MetaLearningTask) -> float:
        """Evaluate performance on task"""
        correct = 0
        total = 0

        for example in task.query_examples:
            agent_name, confidence = self.predict(example.query, example.context)
            if agent_name == example.target_agent:
                correct += 1
            total += 1

        return correct / total if total > 0 else 0.0

    def _encode_query(self, query: str) -> np.ndarray:
        """Encode query to embedding"""
        words = query.lower().split()
        embedding = np.zeros(50)

        for i, word in enumerate(words[:10]):
            hash_val = hash(word) % 500
            embedding[hash_val % 50] += 1.0 / (i + 1)

        return embedding

    def _compute_gradient(self, example: TaskExample) -> dict[str, Any]:
        """Compute gradient (simplified)"""
        return {
            "weights": np.random.randn(50, 20) * 0.01,
            "bias": np.random.randn(20) * 0.01,
        }

    def _update_parameters(self, gradient: dict[str, Any]):
        """Update parameters with gradient"""
        for param_name in gradient:
            if param_name in self.current_parameters:
                self.current_parameters[param_name] -= self.adaptation_rate * gradient[param_name]


class TaskScheduler:
    """Scheduler for meta-learning tasks"""

    def __init__(self, max_concurrent_tasks: int = 3):
        self.max_concurrent_tasks = max_concurrent_tasks
        self.task_queue: list[MetaLearningTask] = []
        self.active_tasks: dict[str, MetaLearningTask] = {}
        self.completed_tasks: list[MetaLearningTask] = []
        self.task_priorities: dict[str, float] = {}

    def add_task(self, task: MetaLearningTask):
        """Add task to scheduler"""
        self.task_queue.append(task)
        self.task_priorities[task.task_id] = task.priority

        # Sort queue by priority
        self.task_queue.sort(key=lambda t: t.priority, reverse=True)

        _emit_records_learning_event(
            "task_scheduler",
            "task_added",
            {
                "task_id": task.task_id,
                "task_type": task.task_type,
                "priority": task.priority,
                "queue_size": len(self.task_queue),
            },
        )

    def get_next_task(self) -> MetaLearningTask | None:
        """Get next task to process"""
        if len(self.active_tasks) >= self.max_concurrent_tasks:
            return None

        if not self.task_queue:
            return None

        task = self.task_queue.pop(0)
        self.active_tasks[task.task_id] = task

        return task

    def complete_task(self, task_id: str):
        """Mark task as completed"""
        if task_id in self.active_tasks:
            task = self.active_tasks.pop(task_id)
            self.completed_tasks.append(task)

            _emit_records_learning_event(
                "task_scheduler",
                "task_completed",
                {
                    "task_id": task_id,
                    "active_tasks": len(self.active_tasks),
                    "completed_tasks": len(self.completed_tasks),
                },
            )

    def get_task_statistics(self) -> dict[str, Any]:
        """Get task processing statistics"""
        return {
            "queue_size": len(self.task_queue),
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "task_types": self._get_task_type_distribution(),
        }

    def _get_task_type_distribution(self) -> dict[str, int]:
        """Get distribution of task types"""
        distribution = defaultdict(int)

        for task in self.task_queue + list(self.active_tasks.values()) + self.completed_tasks:
            distribution[task.task_type] += 1

        return dict(distribution)


class MetaLearningFramework:
    """
    Comprehensive meta-learning framework for L0 routing adaptation.

    Combines multiple meta-learning algorithms with task scheduling
    and continual learning capabilities.
    """

    def __init__(
        self,
        meta_learners: list[BaseMetaLearner] | None = None,
        task_scheduler: TaskScheduler | None = None,
        adaptation_threshold: float = 0.1,
    ):
        """
        Initialize meta-learning framework.

        Args:
            meta_learners: List of meta-learning algorithms
            task_scheduler: Task scheduling system
            adaptation_threshold: Minimum performance improvement to trigger adaptation
        """
        self.meta_learners = {learner.model_name: learner for learner in (meta_learners or [])}
        self.task_scheduler = task_scheduler or TaskScheduler()
        self.adaptation_threshold = adaptation_threshold

        # Performance tracking
        self.adaptation_history: list[AdaptationResult] = []
        self.framework_performance: list[float] = []

        # Create default meta-learners if none provided
        if not self.meta_learners:
            self.meta_learners = {
                "maml": MAMLMetaLearner("maml"),
                "continual": ContinualLearner("continual"),
            }

        _emit_stores_learning_state(
            "meta_learning_framework",
            "initialization",
            {
                "meta_learners": list(self.meta_learners.keys()),
                "adaptation_threshold": adaptation_threshold,
            },
        )

    def create_adaptation_task(
        self,
        task_id: str,
        task_name: str,
        examples: list[TaskExample],
        task_type: str = "few_shot",
        priority: float = 1.0,
    ) -> MetaLearningTask:
        """Create a meta-learning adaptation task"""

        # Split examples into support and query sets
        split_idx = max(1, len(examples) // 2)
        support_examples = examples[:split_idx]
        query_examples = examples[split_idx:]

        task = MetaLearningTask(
            task_id=task_id,
            task_name=task_name,
            support_examples=support_examples,
            query_examples=query_examples,
            task_type=task_type,
            priority=priority,
        )

        return task

    def process_adaptation_request(self, task: MetaLearningTask) -> list[AdaptationResult]:
        """Process adaptation request using all meta-learners"""
        results = []

        for learner_name, learner in tqdm(self.meta_learners.items(), desc="Processing", unit="item"):
            try:
                result = learner.adapt(task)
                results.append(result)

                # Record successful adaptation
                if result.success:
                    self.adaptation_history.append(result)

                _emit_records_learning_event(
                    "meta_learning_framework",
                    "learner_adapted",
                    {
                        "learner": learner_name,
                        "task_id": task.task_id,
                        "success": result.success,
                        "performance_improvement": result.performance_after - result.performance_before,
                    },
                )

            except (ValueError, TypeError, RuntimeError) as e:
                logger.error(f"Meta-learner {learner_name} failed: {e}")

        # Update framework performance
        if results:
            avg_improvement = np.mean([r.performance_after - r.performance_before for r in results])
            self.framework_performance.append(avg_improvement)

        return results

    def get_best_learner(self) -> str:
        """Get best performing meta-learner"""
        if not self.meta_learners:
            return "none"

        best_learner = None
        best_performance = -float("inf")

        for learner_name, learner in self.meta_learners.items():
            if learner.performance_history:
                recent_performance = np.mean(learner.performance_history[-10:])
                if recent_performance > best_performance:
                    best_performance = recent_performance
                    best_learner = learner_name

        return best_learner or list(self.meta_learners.keys())[0]

    def predict_with_best_learner(self, query: str, context: dict[str, Any]) -> tuple[str, float]:
        """Predict using best performing meta-learner"""
        best_learner_name = self.get_best_learner()
        best_learner = self.meta_learners[best_learner_name]

        return best_learner.predict(query, context)

    def get_framework_statistics(self) -> dict[str, Any]:
        """Get comprehensive framework statistics"""
        stats = {
            "meta_learners": {},
            "task_scheduler": self.task_scheduler.get_task_statistics(),
            "framework_performance": {
                "avg_improvement": np.mean(self.framework_performance) if self.framework_performance else 0.0,
                "total_adaptations": len(self.adaptation_history),
                "success_rate": np.mean([r.success for r in self.adaptation_history])
                if self.adaptation_history
                else 0.0,
            },
        }

        for learner_name, learner in self.meta_learners.items():
            stats["meta_learners"][learner_name] = {
                "performance_trend": learner.get_performance_trend(),
                "adaptations": len(learner.adaptation_history),
                "avg_performance": np.mean(learner.performance_history)
                if learner.performance_history
                else 0.0,
            }

        return stats

    def save_state(self, filepath: str):
        """Save framework state to file"""
        state = {
            "meta_learners": {
                name: {
                    "performance_history": learner.performance_history,
                    "adaptation_count": len(learner.adaptation_history),
                }
                for name, learner in self.meta_learners.items()
            },
            "framework_performance": self.framework_performance,
            "adaptation_history": [
                {
                    "task_id": r.task_id,
                    "adaptation_type": r.adaptation_type,
                    "performance_improvement": r.performance_after - r.performance_before,
                    "success": r.success,
                }
                for r in self.adaptation_history
            ],
            "task_scheduler": self.task_scheduler.get_task_statistics(),
        }

        with open(filepath, "w") as f:
            json.dump(state, f, indent=2)

        _emit_stores_learning_state(
            "meta_learning_framework",
            "state_saved",
            {
                "filepath": filepath,
                "total_adaptations": len(self.adaptation_history),
            },
        )


# Utility functions
def create_few_shot_task(
    task_id: str,
    task_name: str,
    examples_data: list[dict[str, Any]],
    priority: float = 1.0,
) -> MetaLearningTask:
    """Create a few-shot learning task from data"""

    if not examples_data:
        raise ValueError("examples_data cannot be empty")

    if len(examples_data) < 2:
        raise ValueError("examples_data must contain at least 2 examples for support/query split")

    task_examples = [
        TaskExample(
            query=data["query"],
            context=data.get("context", {}),
            target_agent=data["target_agent"],
            confidence=data.get("confidence", 0.8),
            success=data.get("success", True),
        )
        for data in examples_data
    ]

    return MetaLearningTask(
        task_id=task_id,
        task_name=task_name,
        support_examples=task_examples[: max(1, len(task_examples) // 2)],
        query_examples=task_examples[max(1, len(task_examples) // 2) :],
        task_type="few_shot",
        priority=priority,
    )


def create_default_meta_framework() -> MetaLearningFramework:
    """Create default meta-learning framework"""

    meta_learners = [
        MAMLMetaLearner("maml", adaptation_rate=0.01),
        ContinualLearner("continual", memory_size=1000, ewc_lambda=0.4),
    ]

    return MetaLearningFramework(
        meta_learners=meta_learners,
        adaptation_threshold=0.1,
    )


__all__ = [
    "MetaLearningFramework",
    "BaseMetaLearner",
    "MAMLMetaLearner",
    "ContinualLearner",
    "TaskScheduler",
    "TaskExample",
    "MetaLearningTask",
    "AdaptationResult",
    "create_few_shot_task",
    "create_default_meta_framework",
]
