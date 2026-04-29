"""Analyze naming violations and emit rename proposals."""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config.path_constants import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
    get_validated_project_root,
)
from tqdm import tqdm


PROJECT_ROOT = get_validated_project_root()
EXCLUDE_DIRS = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES


def get_python_files_fast(root: Path) -> list[Path]:
    python_files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(directory for directory in dirnames if directory not in EXCLUDE_DIRS)
        for filename in sorted(filenames):
            if filename.endswith(".py"):
                python_files.append(Path(dirpath) / filename)
    return python_files


def classify_file(path: Path) -> str:
    from agentic_core.L5_safety.reasoning.core_kernel.classification_kernel import classify_file_standalone

    file_type = classify_file_standalone(path)
    if file_type in {
        "AGENT",
        "ORCHESTRATOR",
        "STRATEGY",
        "ADAPTER",
        "VALIDATOR",
        "EXCEPTION",
        "CONFIG",
        "FACTORY",
        "SERVICE",
        "ENGINE",
        "TYPES",
        "CLASS",
        "UTILITY",
        "STUB",
        "IGNORE",
    }:
        return "IGNORE"

    if file_type == "SCRIPT":
        return "SCRIPT" if re.match(r"^[A-Z]", path.stem) else "IGNORE"

    if file_type == "TEST":
        return "IGNORE" if path.name.startswith("test_") or path.name.endswith("_test.py") else "TEST"

    if file_type == "MIXIN":
        return "MIXIN" if re.match(r"^[A-Z]", path.stem) and not path.stem.islower() else "IGNORE"

    if file_type in {"PROTOCOL", "GATEWAY"}:
        return file_type

    return "IGNORE"


def get_compliant_name(path: Path, file_type: str) -> str | None:
    if file_type in {"IGNORE", "TYPES", "UTILITY", "PROTOCOL", "GATEWAY"}:
        return None

    if file_type == "SCRIPT":
        snake = re.sub(r"(?<!^)(?=[A-Z])", "_", path.stem).lower().replace("__", "_")
        target = f"{snake}.py"
        return None if target == path.name else target

    if file_type == "TEST":
        stem = path.stem
        s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", stem)
        clean = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
        target = f"test_{clean}.py"
        return None if target == path.name else target

    if file_type == "MIXIN":
        stem = path.stem
        s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", stem)
        clean = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
        if not clean.endswith("_mixin"):
            clean += "_mixin"
        target = f"{clean}.py"
        return None if target == path.name else target

    return None


def find_imports_to_update(project_root: Path, old_name: str, new_name: str) -> list[dict[str, Any]]:
    old_mod = old_name.removesuffix(".py")
    new_mod = new_name.removesuffix(".py")
    import_updates: list[dict[str, Any]] = []

    patterns = [
        re.compile(rf"from\s+[\w.]*{re.escape(old_mod)}\s+import"),
        re.compile(rf"import\s+[\w.]*{re.escape(old_mod)}"),
    ]

    for path in tqdm(get_python_files_fast(project_root), desc="Scanning imports", unit="file"):
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if old_mod not in content:
            continue
        if any(pattern.search(content) for pattern in patterns):
            import_updates.append(
                {
                    "file": str(path.relative_to(project_root)),
                    "old_module": old_mod,
                    "new_module": new_mod,
                }
            )
    return import_updates


def resolve_report_path(report_path: str | None) -> Path:
    if not report_path:
        return PROJECT_ROOT / "file_classification_report.json"
    candidate = Path(report_path)
    if not candidate.is_absolute():
        candidate = PROJECT_ROOT / candidate
    candidate = candidate.resolve()
    if PROJECT_ROOT not in candidate.parents and candidate != PROJECT_ROOT:
        raise ValueError("Report path must remain under the project root")
    return candidate


def main(report_path: str | None = None) -> int:
    print("=" * 80)
    print("FILE CLASSIFICATION ANALYSIS")
    print("=" * 80)

    python_files = get_python_files_fast(PROJECT_ROOT)
    stats: dict[str, Any] = {"analyzed": len(python_files), "compliant": 0, "violations": {}}
    proposals: list[dict[str, Any]] = []

    for path in tqdm(python_files, desc="Classifying files", unit="file"):
        if not path.exists():
            continue
        file_type = classify_file(path)
        if file_type == "IGNORE":
            continue

        new_name = get_compliant_name(path, file_type)
        if new_name and new_name != path.name:
            stats["violations"][file_type] = stats["violations"].get(file_type, 0) + 1
            import_updates = find_imports_to_update(PROJECT_ROOT, path.name, new_name)
            proposals.append(
                {
                    "current_path": str(path),
                    "current_name": path.name,
                    "proposed_name": new_name,
                    "file_type": file_type,
                    "relative_path": str(path.relative_to(PROJECT_ROOT)),
                    "import_updates": import_updates,
                    "import_count": len(import_updates),
                }
            )
        else:
            stats["compliant"] += 1

    total_violations = sum(stats["violations"].values())
    print(f"\nTotal files analyzed: {stats['analyzed']}")
    print(f"Compliant files: {stats['compliant']}")
    print(f"Total violations: {total_violations}")
    if total_violations:
        print("\nViolation breakdown:")
        for violation_type, count in sorted(
            stats["violations"].items(), key=lambda item: (-item[1], item[0])
        ):
            print(f"  {violation_type}: {count}")

    report = {
        "summary": stats,
        "proposals": proposals,
        "total_proposals": len(proposals),
        "phase1_agent_count": len([proposal for proposal in proposals if proposal["file_type"] == "AGENT"]),
        "phase2_mixin_count": len([proposal for proposal in proposals if proposal["file_type"] == "MIXIN"]),
        "phase3_test_count": len([proposal for proposal in proposals if proposal["file_type"] == "TEST"]),
    }

    target_report = resolve_report_path(report_path)
    target_report.parent.mkdir(parents=True, exist_ok=True)
    target_report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nDetailed report saved to: {target_report}")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze file naming violations and emit rename proposals.")
    parser.add_argument("--report-path", help="Optional report path under the project root.")
    raise SystemExit(main(report_path=parser.parse_args().report_path))
