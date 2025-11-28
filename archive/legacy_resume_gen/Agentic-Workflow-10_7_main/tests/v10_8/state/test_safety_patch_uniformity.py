import ast
import pathlib

TARGET_FILES = [
    "rag_execution_stack.py",
    "bullet_execution_stack.py",
    "drafting_execution_stack.py",
    "rag_orchestration.py",
    "draft_orchestration.py",
]

KEYS = ["safety_report", "policy_decision", "constitutional_review"]

def test_uniform_keys_present():
    for fname in TARGET_FILES:
        code = pathlib.Path(fname).read_text()
        for key in KEYS:
            assert key in code, f"{key} missing in {fname}"
