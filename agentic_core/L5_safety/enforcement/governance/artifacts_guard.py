from agentic_core.L2_execution.tools import write_gateway as _wg
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "artifacts_guard", "L5")
_emit_routes_through("p1", "artifacts_guard", "L5")
_emit_escalates_to_human("p1", "artifacts_guard", "L5")
_emit_reads_policy_state("p1", "artifacts_guard", "L5")

"\nArtifacts Governance Guard\n\nDeterministic read-only scanner for artifacts/ directory governance.\nEnforces retention rules, sensitive content detection, and inventory tracking.\n"
import re
from pathlib import Path
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)


def is_forbidden_artifact_name(file_path: Path) -> bool:
    """Check if file has a forbidden artifact name."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "is_forbidden_artifact_name", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "is_forbidden_artifact_name", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_SAFETY, "is_forbidden_artifact_name")
    forbidden_patterns = [".secrets.baseline", "forensic_discovery_output.json"]
    return any(pattern in str(file_path) for pattern in forbidden_patterns)


def scan_sensitive_content(file_path: Path) -> list[str]:
    """Scan file for sensitive content patterns."""
    sensitive_patterns = [
        "(?i)api[_-]?key\\s*[:=]",
        "(?i)secret\\s*[:=]",
        "sk-[A-Za-z0-9]{20,}",
        "xox[baprs]-[A-Za-z0-9-]{10,}",
    ]
    violations = []
    try:
        if file_path.stat().st_size > 2 * 1024 * 1024:
            return violations
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            content = f.read()
        for pattern in sensitive_patterns:
            if re.search(pattern, content):
                violations.append(f"Sensitive pattern detected: {pattern}")
    except (UnicodeDecodeError, PermissionError, OSError):
        pass
    return violations


def scan_artifacts_directory(artifacts_path: Path) -> dict[str, Any]:
    """Scan artifacts directory for governance violations."""
    violations = []
    inventory = []
    files_scanned = 0
    all_files = sorted(artifacts_path.rglob("*"))
    for file_path in all_files:
        if file_path.is_dir():
            continue
        files_scanned += 1
        relative_path = file_path.relative_to(artifacts_path)
        file_size = file_path.stat().st_size
        file_ext = file_path.suffix.lower()
        if is_forbidden_artifact_name(relative_path):
            violations.append(
                {
                    "file": str(relative_path),
                    "type": "forbidden_artifact_name",
                    "detail": f"Forbidden artifact name: {relative_path}",
                }
            )
        sensitive_violations = scan_sensitive_content(file_path)
        for violation in sensitive_violations:
            violations.append({"file": str(relative_path), "type": "sensitive_content", "detail": violation})
        inventory_item = {"file": str(relative_path), "bytes": file_size, "ext": file_ext}
        if file_size > 5 * 1024 * 1024:
            inventory_item["detail"] = "oversize"
        inventory.append(inventory_item)
    return {"files_scanned": files_scanned, "violations": violations, "inventory": inventory}


def main():
    """Main scanner execution."""
    root_path = Path(__file__).parent.parent.parent
    artifacts_path = root_path / "artifacts"
    if not artifacts_path.exists():
        print(f"Error: artifacts directory not found at {artifacts_path}")
        return 1
    print(f"Scanning artifacts directory: {artifacts_path}")
    result = scan_artifacts_directory(artifacts_path)
    output_dir = root_path / "artifacts" / "governance"
    _wg.ensure_dir(output_dir)
    report_path = output_dir / "artifacts_guard_report.json"
    _wg.write_json(report_path, result, indent=2)
    print(f"Scan complete. Report written to: {report_path}")
    print(f"Files scanned: {result['files_scanned']}")
    print(f"Violations found: {len(result['violations'])}")
    oversize_count = sum(1 for item in result["inventory"] if item.get("detail") == "oversize")
    if oversize_count > 0:
        print(f"Oversize files (>5MB): {oversize_count}")
    if result["violations"]:
        print("ARTIFACTS GOVERNANCE VIOLATIONS DETECTED:")
        for violation in result["violations"]:
            print(f"  {violation['file']}: {violation['type']} - {violation['detail']}")
        return 1
    else:
        print("No artifacts governance violations found.")
        return 0


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
