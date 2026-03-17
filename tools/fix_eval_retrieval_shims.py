"""Create ALL missing evaluation.retrieval.* shims from workflow_engines modules."""

import os

ROOT = r"C:\Git\Agentic-Workflow"
WE = os.path.join(ROOT, "agentic_core", "utils", "workflow_engines")
EVAL_RET = os.path.join(ROOT, "agentic_core", "evaluation", "retrieval")

os.makedirs(EVAL_RET, exist_ok=True)

# Get all .py files in workflow_engines that could be retrieval-related
we_modules = [f[:-3] for f in os.listdir(WE) if f.endswith(".py") and f != "__init__.py"]

created = 0
for mod in we_modules:
    shim_path = os.path.join(EVAL_RET, f"{mod}.py")
    if not os.path.exists(shim_path):
        with open(shim_path, "w", encoding="utf-8") as f:
            f.write(f'"""Shim — re-exports from agentic_core.utils.workflow_engines.{mod}."""\n\n')
            f.write(f"from agentic_core.utils.workflow_engines.{mod} import *  # noqa: F401,F403\n")
        created += 1
        print(f"  Created: agentic_core/evaluation/retrieval/{mod}.py")

# Also ensure __init__.py exists
init_path = os.path.join(EVAL_RET, "__init__.py")
if not os.path.exists(init_path):
    with open(init_path, "w", encoding="utf-8") as f:
        f.write('"""Evaluation retrieval package."""\n')
    created += 1

print(f"\nCreated {created} shim files")
