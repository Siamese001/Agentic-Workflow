"""Fix evaluation import chain issues.

The workflow_engines modules use relative imports like:
  from .base import GenerationMetric
  from ..metrics.base import EvaluationMetric
  from ..schemas.evaluation_dataset_schema import ...

These relative imports fail because workflow_engines/ is flat.
The actual package layout expected is under agentic_core/utils/ with
subpackages like metrics/, schemas/, runners/, monitoring/.

Strategy:
1. Create missing agentic_core/utils subpackages as shim re-exports
2. Create missing agentic_core/evaluation subpackages as shim re-exports
3. Fix the .base relative import in workflow_engines by creating base.py
"""

import os

ROOT = r"C:\Git\Agentic-Workflow"
WE = os.path.join(ROOT, "agentic_core", "utils", "workflow_engines")
EVAL = os.path.join(ROOT, "agentic_core", "evaluation")
UTILS = os.path.join(ROOT, "agentic_core", "utils")

created = 0


def create_file(path, content):
    global created
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        created += 1
        print(f"  Created: {os.path.relpath(path, ROOT)}")


# 1. Create base.py in workflow_engines (for from .base import)
# Check what's expected
with open(os.path.join(WE, "groundedness.py")) as f:
    content = f.read()

# groundedness imports from .base import GenerationMetric
# offline_eval_runner imports from ..metrics.base import EvaluationMetric
# Let's check what base classes are needed

base_content = '''"""Base metric classes for evaluation framework."""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any


class EvaluationMetric(ABC):
    """Abstract base class for all evaluation metrics."""

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def compute(self, **kwargs: Any) -> float:
        ...


class GenerationMetric(EvaluationMetric):
    """Base class for generation quality metrics (answer correctness, groundedness)."""
    pass


class RetrievalMetric(EvaluationMetric):
    """Base class for retrieval quality metrics (precision, recall, MRR, NDCG)."""
    pass
'''

create_file(os.path.join(WE, "base.py"), base_content)

# 2. Create agentic_core/utils/metrics/ as shim to workflow_engines
for pkg in ["metrics", "monitoring", "runners", "schemas"]:
    pkg_dir = os.path.join(UTILS, pkg)
    os.makedirs(pkg_dir, exist_ok=True)
    init_path = os.path.join(pkg_dir, "__init__.py")
    create_file(init_path, f'"""Shim package — agentic_core.utils.{pkg}"""\n')

# Map utils.metrics.* -> utils.workflow_engines.*
metrics_shims = {
    "answer_correctness": "agentic_core.utils.workflow_engines.answer_correctness",
    "groundedness": "agentic_core.utils.workflow_engines.groundedness",
    "ndcg": "agentic_core.utils.workflow_engines.ndcg",
    "precision_at_k": "agentic_core.utils.workflow_engines.precision_at_k",
    "recall_at_k": "agentic_core.utils.workflow_engines.recall_at_k",
    "mrr": "agentic_core.utils.workflow_engines.mrr",
    "base": "agentic_core.utils.workflow_engines.base",
}
for mod, source in metrics_shims.items():
    create_file(
        os.path.join(UTILS, "metrics", f"{mod}.py"),
        f'"""Shim — re-exports from {source}."""\nfrom {source} import *  # noqa: F401,F403\n',
    )

# Map utils.monitoring.* -> utils.workflow_engines.*
monitoring_shims = {
    "drift_monitor": "agentic_core.utils.workflow_engines.drift_monitor",
    "snapshots": "agentic_core.utils.workflow_engines.snapshots",
    "shadow_eval_runner": "agentic_core.utils.workflow_engines.shadow_eval_runner",
    "completeness_monitors": "agentic_core.utils.workflow_engines.completeness_monitors",
}
for mod, source in monitoring_shims.items():
    create_file(
        os.path.join(UTILS, "monitoring", f"{mod}.py"),
        f'"""Shim — re-exports from {source}."""\nfrom {source} import *  # noqa: F401,F403\n',
    )

# Map utils.runners.* -> utils.workflow_engines.*
runners_shims = {
    "offline_eval_runner": "agentic_core.utils.workflow_engines.offline_eval_runner",
    "replay_eval_runner": "agentic_core.utils.workflow_engines.replay_eval_runner",
}
for mod, source in runners_shims.items():
    create_file(
        os.path.join(UTILS, "runners", f"{mod}.py"),
        f'"""Shim — re-exports from {source}."""\nfrom {source} import *  # noqa: F401,F403\n',
    )

# Map utils.schemas.* -> utils.workflow_engines.*
schemas_shims = {
    "evaluation_dataset_schema": "agentic_core.utils.workflow_engines.evaluation_dataset_schema",
    "evaluation_report_schema": "agentic_core.utils.workflow_engines.evaluation_report_schema",
    "evaluation_result_schema": "agentic_core.utils.workflow_engines.evaluation_result_schema",
}
for mod, source in schemas_shims.items():
    create_file(
        os.path.join(UTILS, "schemas", f"{mod}.py"),
        f'"""Shim — re-exports from {source}."""\nfrom {source} import *  # noqa: F401,F403\n',
    )

# 3. Create missing evaluation shims
eval_extras = {
    ("monitoring", "completeness_monitors"): "agentic_core.utils.workflow_engines.completeness_monitors",
    ("retrieval", "answer_support"): "agentic_core.utils.workflow_engines.answer_support",
}
for (subpkg, mod), source in eval_extras.items():
    pkg_dir = os.path.join(EVAL, subpkg)
    os.makedirs(pkg_dir, exist_ok=True)
    create_file(
        os.path.join(pkg_dir, f"{mod}.py"),
        f'"""Shim — re-exports from {source}."""\nfrom {source} import *  # noqa: F401,F403\n',
    )

print(f"\nCreated {created} files total")
