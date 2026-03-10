"""Full scanner violation dump for all buckets."""
from pathlib import Path
from agentic_core.L5_safety.static_checks.system_invariant_scanner import scan_repository_for_bypasses

root = Path(__file__).resolve().parents[2]

for bucket_rel in [L2_EXECUTION_DIR, L5_SAFETY_DIR, "tests/sovereign_hardening"]:
    bucket = (root / bucket_rel).resolve()
    violations = scan_repository_for_bypasses(bucket)
    prefix = str(bucket)
    filtered = [v for v in violations if str(Path(v.file_path).resolve()).startswith(prefix)]
    py_files = [f for f in bucket.rglob("*.py") if "__pycache__" not in f.parts]
    print(f"\n=== {bucket_rel}: {len(py_files)} files, {len(filtered)} violations ===")
    for v in filtered:
        print(f"  {Path(v.file_path).name}:{v.line} [{v.rule_id}]")
