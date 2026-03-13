"""
Evaluation Dataset Schema

Defines the structure for evaluation examples and datasets.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class EvaluationExample:
    """Single evaluation example with query, ground truth, and expected answer."""

    query: str
    ground_truth_documents: list[str]
    expected_answer: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "query": self.query,
            "ground_truth_documents": self.ground_truth_documents,
            "expected_answer": self.expected_answer,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EvaluationExample":
        """Create from dictionary."""
        return cls(
            query=data["query"],
            ground_truth_documents=data["ground_truth_documents"],
            expected_answer=data["expected_answer"],
            metadata=data.get("metadata", {}),
        )


@dataclass
class EvaluationDataset:
    """Collection of evaluation examples."""

    examples: list[EvaluationExample]
    name: str
    version: str
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "examples": [example.to_dict() for example in self.examples],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EvaluationDataset":
        """Create from dictionary."""
        return cls(
            name=data["name"],
            version=data["version"],
            description=data.get("description", ""),
            examples=[EvaluationExample.from_dict(example) for example in data["examples"]],
        )

    def save_to_file(self, file_path: Path) -> None:
        """Save dataset to JSON file."""
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load_from_file(cls, file_path: Path) -> "EvaluationDataset":
        """Load dataset from JSON file."""
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def __len__(self) -> int:
        """Return number of examples."""
        return len(self.examples)
