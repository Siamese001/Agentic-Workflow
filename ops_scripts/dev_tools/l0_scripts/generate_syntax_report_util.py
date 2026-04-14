"""Generate a syntax report by scanning Python files directly with ast.parse."""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path


def _find_project_root() -> Path:
    current = Path(__file__).resolve().parent
    for candidate in (current, *current.parents):
        if (candidate / "l0_scripts").exists() and (candidate / "L0_routing_scripts").exists():
            return candidate
    return Path(__file__).resolve().parents[1]


def _iter_python_files(project_root: Path):
    for path in project_root.rglob("*.py"):
        if "__pycache__" not in path.parts:
            yield path


def _classify_layer(path: Path) -> str:
    path_str = str(path).replace("\\", "/")
    if "L0_" in path_str or "/l0_scripts/" in path_str:
        return "L0"
    if "L1_" in path_str:
        return "L1"
    if "L2_" in path_str:
        return "L2"
    if "L3_" in path_str:
        return "L3"
    if "L4_" in path_str:
        return "L4"
    if "L5_" in path_str:
        return "L5"
    if "config" in path_str:
        return "Config"
    return "Other"


def build_report(project_root: Path) -> dict:
    errors_by_layer: dict[str, list[dict]] = {}
    total_files = 0
    for path in _iter_python_files(project_root):
        total_files += 1
        try:
            source = path.read_text(encoding="utf-8")
            ast.parse(source, filename=str(path))
        except SyntaxError as exc:
            layer = _classify_layer(path)
            errors_by_layer.setdefault(layer, []).append(
                {
                    "file": str(path.relative_to(project_root)),
                    "line": exc.lineno,
                    "offset": exc.offset,
                    "message": exc.msg,
                }
            )
        except OSError as exc:
            layer = _classify_layer(path)
            errors_by_layer.setdefault(layer, []).append(
                {
                    "file": str(path.relative_to(project_root)),
                    "line": None,
                    "offset": None,
                    "message": f"I/O error: {exc}",
                }
            )
    total_errors = sum(len(items) for items in errors_by_layer.values())
    return {
        "project_root": str(project_root),
        "total_files": total_files,
        "total_errors": total_errors,
        "by_layer": errors_by_layer,
    }


def _print_report(report: dict) -> None:
    print("Generating comprehensive syntax error report...")
    print()
    print(f"Total Python files scanned: {report['total_files']}")
    print(f"Total syntax errors: {report['total_errors']}")
    print()
    if report["total_errors"] == 0:
        print("SUCCESS: All files are syntactically valid!")
        return
    print("Errors by layer:")
    for layer in sorted(report["by_layer"]):
        items = report["by_layer"][layer]
        print(f"  {layer}: {len(items)}")
    print()
    for layer in sorted(report["by_layer"]):
        print(f"[{layer}]")
        for item in report["by_layer"][layer]:
            location = f":{item['line']}" if item["line"] else ""
            print(f"  - {item['file']}{location}: {item['message']}")
        print()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a syntax report by parsing Python files directly")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON instead of text")
    args = parser.parse_args(argv)

    project_root = _find_project_root()
    report = build_report(project_root)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        _print_report(report)
    return 0 if report["total_errors"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
