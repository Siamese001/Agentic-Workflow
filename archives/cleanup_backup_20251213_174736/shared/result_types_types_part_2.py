"""Split module 2 for result_types_types."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

@dataclass
class ExecutionResult(Result):
    """Result for workflow execution."""
    workflow_id: str = ''
    step_results: List[Result] = None
    total_steps: int = 0
    completed_steps: int = 0

    def __post_init__(self):
        if self.step_results is None:
            self.step_results = []
        self.completed_steps = len([r for r in self.step_results if r.is_success()])
        if self.completed_steps == self.total_steps and self.total_steps > 0:
            self.status = ResultStatus.SUCCESS
        elif self.completed_steps > 0:
            self.status = ResultStatus.PARTIAL
        else:
            self.status = ResultStatus.FAILURE

