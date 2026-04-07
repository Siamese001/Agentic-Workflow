"""Batch-create evaluation package shims pointing to workflow_engines."""

import os

BASE = r"C:\Git\Agentic-Workflow\agentic_core\evaluation"
WE = "agentic_core.utils.workflow_engines"

# Mapping: (subpackage, module_name) -> source module in workflow_engines
shims = {
    ("chunking", "policies"): f"{WE}.policies",
    ("chunking", "validators"): f"{WE}.validators",
    ("feedback", "dpo_batch_builder"): f"{WE}.dpo_batch_builder",
    ("feedback", "proposer_bridge"): f"{WE}.proposer_bridge",
    ("feedback", "schemas"): f"{WE}.schemas",
    ("metrics", "answer_correctness"): f"{WE}.answer_correctness",
    ("metrics", "groundedness"): f"{WE}.groundedness",
    ("metrics", "ndcg"): f"{WE}.ndcg",
    ("metrics", "precision_at_k"): f"{WE}.precision_at_k",
    ("metrics", "recall_at_k"): f"{WE}.recall_at_k",
    ("metrics", "mrr"): f"{WE}.mrr",
    ("monitoring", "drift_monitor"): f"{WE}.drift_monitor",
    ("monitoring", "snapshots"): f"{WE}.snapshots",
    ("monitoring", "shadow_eval_runner"): f"{WE}.shadow_eval_runner",
    ("retrieval", "fusion"): f"{WE}.fusion",
    ("retrieval", "interfaces"): f"{WE}.interfaces",
    ("retrieval", "profiles"): f"{WE}.profiles",
    ("retrieval", "reranker"): f"{WE}.reranker",
    ("runners", "offline_eval_runner"): f"{WE}.offline_eval_runner",
    ("runners", "replay_eval_runner"): f"{WE}.replay_eval_runner",
    ("schemas", "evaluation_dataset_schema"): f"{WE}.evaluation_dataset_schema",
    ("schemas", "evaluation_report_schema"): f"{WE}.evaluation_report_schema",
    ("schemas", "evaluation_result_schema"): f"{WE}.evaluation_result_schema",
}

created = 0
for (subpkg, mod_name), source in shims.items():
    pkg_dir = os.path.join(BASE, subpkg)
    os.makedirs(pkg_dir, exist_ok=True)

    # Create __init__.py if missing
    init_path = os.path.join(pkg_dir, "__init__.py")
    if not os.path.exists(init_path):
        with open(init_path, "w", encoding="utf-8") as f:
            f.write(f'"""Evaluation {subpkg} package — shim re-exports."""\n')
        created += 1

    # Create shim module
    shim_path = os.path.join(pkg_dir, f"{mod_name}.py")
    if not os.path.exists(shim_path):
        content = f'"""Shim — re-exports from {source} for backward compatibility."""\n\n'
        content += f"from {source} import *  # noqa: F401,F403\n"
        with open(shim_path, "w", encoding="utf-8") as f:
            f.write(content)
        created += 1

print(f"Created {created} shim files")
