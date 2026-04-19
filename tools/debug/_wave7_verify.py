import sqlite3

c = sqlite3.connect(r"artifacts/adg/adg_indexed_04192026_1251.sqlite")
h = c.execute(
    "SELECT COUNT(*) FROM violations WHERE severity='HIGH' AND category='antipattern'"
).fetchone()[0]
print(f"P1 HIGH: {h}")
SCOPE = [
    "system_learning/engines/hitl_decision_logger.py",
    "system_learning/engines/enhanced_rag_retrieval_cache.py",
    "agentic_core/utils/workflow_engines/offline_eval_runner.py",
    "agentic_core/utils/workflow_engines/dpo_batch_builder.py",
    "agentic_core/utils/meta_learning_engine_util.py",
    "agentic_core/utils/ast_fuzzy_util.py",
    "agentic_core/tracing/engines/distributed_tracing_coordinator.py",
    "agentic_core/seams/workflow_learning_bridge.py",
]
total = 0
for p in SCOPE:
    n = c.execute(
        "SELECT COUNT(*) FROM violations WHERE severity='HIGH' AND file_path=?",
        (p,),
    ).fetchone()[0]
    total += n
    print(f"  {n:3d}  {p}")
print(f"  Total: {total}")
